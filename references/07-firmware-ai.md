# 07. 固件开发（含 AI 推理）（Firmware Development & AI Inference）

全流程的环节 07。板子能通电（06 验收）后，开始写固件：从最小系统跑通，到外设驱动，到本地 AI 推理。**主线：ESP-IDF（C）跑 TFLite Micro / ESP-DL / ESP-NN 做 TinyML；备用：Arduino / MicroPython**。输入：板级合同 + 已验证的硬件；输出：能完成产品核心功能的固件（编译通过 + 烧录成功 + 真机验收）。

> 本环节与 08（烧录调试）配合：07 负责"写对"，08 负责"烧上并确认"。**证据分级：编译通过 ≠ 烧录成功 ≠ 日志正常 ≠ 真机验收**——本环节验收只到"编译通过 + 逻辑审查"，烧录与真机验收在 08。

## 目标与通过标准

- 目标：写出一份能编译、能烧录、能在真机上完成产品核心功能的 ESP-IDF 固件，并把 AI 推理（如语音唤醒/关键词识别/图像分类）跑起来。
- 通过标准：
  - `idf.py build` 编译通过，无 Error（Warning 已知晓）。
  - 固件能按板级合同正确操作引脚（LED/按键/编码器/麦克风/功放/传感器），不猜引脚。
  - 用 TFLite Micro 或 ESP-DL 完成一次本地 AI 推理：模型已转成 C 数组/分区，interpreter 初始化成功，能输出 top-1 结果。
  - 内存预算表（堆/PSRAM/Tensor Arena）已算清并留档（可跑 `scripts/check_flash_budget.py` 校验分区/内存）。
  - 真机验收（与 08 配合）：功能按 product-contract 验收清单逐条通过。

## 可复制操作与命令

### 7.1 工程结构与 Hello World（ESP-IDF）

```powershell
# 建工程（在纯英文路径；<你的 IDF 安装路径> 已激活的前提下）
cd D:\eb-build
idf.py create-project my-device
cd my-device
idf.py set-target esp32s3
# 首次：先确认最小系统能跑（GPIO 点亮板上 LED）
idf.py build
```

> 每次新开 PowerShell 窗口先跑激活脚本（见 02 环节）；`idf.py flash`/`monitor` 的下载模式操作以板级合同的 `boot.enter`/`boot.exit` 为准。

最小系统代码（`main/main.c`，点亮板载 LED；引脚以你的 `docs/board-contract.json` 为准）：

```c
#include <stdio.h>
#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define LED_GPIO   <LED 引脚，如 GPIO2；以板级合同为准>

void app_main(void)
{
    gpio_set_direction(LED_GPIO, GPIO_MODE_OUTPUT);
    while (1) {
        gpio_set_level(LED_GPIO, 1);
        vTaskDelay(pdMS_TO_TICKS(500));
        gpio_set_level(LED_GPIO, 0);
        vTaskDelay(pdMS_TO_TICKS(500));
    }
}
```

### 7.2 读板级合同再写驱动（防幻觉关键）

写任何外设驱动前，先用 02 环节模板 D 让 AI 复述板级合同：哪些脚占用、哪些空闲、下载模式怎么进。**绝不凭记忆猜 GPIO 编号**——不同板（含 EasyInput V2.0 与你的新板）引脚完全不同，一律以 `docs/board-contract.json` 为准（详见 `board-reference.md` 板级合同方法与常见坑 3）。

### 7.3 外设驱动骨架（按键/编码器/I2S 音频/I2C 传感器）

**按键（GPIO 读 + 软件消抖 ≥20ms；与 03 硬件 100nF 消抖对齐）**：

```c
// 按键：按下=低电平（以板级合同为准）；软件消抖 20ms 与硬件 100nF 消抖配合
#define BTN_GPIO <按键引脚>
#define DEBOUNCE_MS 20
static bool btn_read_debounced(void) {
    static uint32_t last_t = 0;
    static bool last_stable = true;
    uint32_t now = esp_timer_get_time() / 1000; // ms
    bool raw = gpio_get_level(BTN_GPIO);
    if (now - last_t >= DEBOUNCE_MS) {
        last_t = now;
        last_stable = raw;
    }
    return last_stable;
}
```

**旋转编码器（EC11，A/B 相 + 内部上拉）**：见训练营第 3 课鼓机工程（`camp-notes.md`），核心是边沿检测 + 方向判定；A/B 相接反只是方向反，不致命。

**I2S 麦克风 INMP441（I2S 输入）与功放 MAX98357A（I2S 输出）**：

```c
#include "driver/i2s_std.h"
// 配置两路 I2S：麦克风（RX）、功放（TX）。引脚以板级合同为准（SCK/WS/SD）。
// 注意：INMP441 需在初始化后留 >10ms 稳定；MAX98357A 输出前先让 BCLK/LRC 跑起来。
```

**I2C 传感器（SDA/SCL，各 4.7kΩ 上拉已在原理图配好）**：

```c
#include "driver/i2c_master.h"
// i2c_master_bus_add_device 注册设备；读取用 i2c_master_transmit_receive。
```

### 7.4 本地 AI 推理（TinyML 主线）

**路线选择**：

| 需求 | 用哪个 | 说明 |
| --- | --- | --- |
| 通用 CNN（关键词/图像分类） | TFLite Micro + ESP-NN | 生态最全、教程最多；ESP-NN 加速 S3 向量指令 |
| 图像分类/检测（乐鑫全家桶） | ESP-DL | ONNX 转 C 数组部署，官方维护，性能好 |
| 不想写 C（原型） | MicroPython（tflite-micro 或 mpy 的 ml 模块） | 慢但上手快，原型够用 |
| 云端/大模型 | ESP32 只做端侧唤醒 + 音频上传 | 模型跑在服务端，见 09 联调 |

**TFLite Micro 接入步骤（ESP-IDF）**：

1. 模型转 INT8 量化（训练营方法 / Edge Impulse 导出 / 本地 ONNX→TFLite）：
   - Edge Impulse 导出：EON Tuner 选 INT8，下载 C 数组版 `.tflite`。
   - 本地转换：`onnx→tflite`（tf.lite.TFLiteConverter，representative_dataset 做 INT8 校准）。
2. 把 `.tflite` 转成 C 数组（`xxd -i model.tflite > model.cc`）或放入自定义分区（data 分区，见 7.5）。
3. 工程引入组件：

```powershell
idf.py add-dependency "espressif/esp-nn"
idf.py add-dependency "espressif/tflite-micro"
```

4. 推理代码骨架（Tensor Arena 放 PSRAM；首次推理用 PSRAM 可行，但 PSRAM 访问延迟高于内部 SRAM，**持续跑推理时优先把热数据/arena 留在内部 SRAM**，性能差异明显）：

```c
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"

// 模型 C 数组（extern）
extern const unsigned char model_tflite[];
extern const unsigned int model_tflite_len;

// Tensor Arena 放 PSRAM（首次可行；注意 PSRAM 延迟，持续推理优先内部 SRAM）
static uint8_t tensor_arena[<arena 大小，如 256 * 1024>] __attribute__((section(".dram2_0")));

void ai_run_once(float* input, int input_len, float* out_top1) {
    static tflite::MicroInterpreter* interpreter = nullptr;
    if (!interpreter) {
        static tflite::MicroMutableOpResolver<10> resolver;
        // 注册需要的算子：resolver.AddConv2D(); resolver.AddFullyConnected(); ...
        static tflite::MicroInterpreter static_interp(
            tflite::GetModel(model_tflite), resolver, tensor_arena, sizeof(tensor_arena));
        interpreter = &static_interp;
        if (interpreter->AllocateTensors() != kTfLiteOk) { /* 内存不够，缩小 arena/降模型 */ }
    }
    memcpy(interpreter->input(0)->data.f, input, input_len * sizeof(float));
    interpreter->Invoke();
    // 读 output(0)->data.f 取 top-1（此处省略 argmax）
}
```

> **内存预算铁律**：模型大小、Tensor Arena、堆余量三者**必须在写代码前算清并留档**（用 `scripts/check_flash_budget.py` + 分区表校验），不然推理时直接 OOM 重启。参考量级：INT8 关键词唤醒模型 50–200KB、TFLite Micro 运行时 + arena 200–500KB；N16R8 的 8MB PSRAM 装得下 1MB 内模型，但延迟与功耗要实测。

### 7.5 分区表与 Flash 预算（防幻觉重点）

ESP32-S3 16MB Flash 用默认 4MB 分区表会浪费空间。自定义分区表（`partitions.csv`，放工程根目录）示例——**注意按官方 CSV 语法写，offset 可空但分区类型必须合法；data 分区用 `spiffs` 类型或显式 offset 才不会报错**：

```csv
# Name,   Type, SubType, Offset,  Size, Flags
nvs,      data, nvs,     ,        0x4000,
otadata,  data, ota,     ,        0x4000,
phy,      data, phy,     ,        0x1000,
factory,  app,  factory, ,        0x300000,
model,    data, spiffs,  ,        0x200000,
storage,  data, spiffs,  ,        0x800000,
```

（语法要点：逗号分隔六列；`Offset` 留空表示自动分配，但 `data` 分区建议显式给 offset 或用 `spiffs` 子类型 + 自动分配，两者都要在 `idf.py menuconfig` 的 "Partition Table → Custom partition CSV" 里启用；`factory` 用 `app, factory` 子类型占住首分区。**把分区表喂给 `scripts/check_flash_budget.py` 校验各段求和 ≤ Flash 容量。**）

CMake 里指定分区表：

```cmake
# CMakeLists.txt（工程根）
# 默认用 4MB 分区表；自定义时取消注释：
# set(PARTITION_TABLE_CUSTOM "partitions.csv")
```

### 7.6 固件内存与性能常识（避免幻觉）

- ESP32-S3 有 **512KB 内部 SRAM（总数，含 cache）**：其中相当一部分被 cache/系统占用，**可自由使用的堆远小于 512KB**；不要把"512KB"当成"可用堆 512KB"。
- PSRAM（N16R8 的 8MB）可放模型与大数据，但访问延迟高于内部 SRAM，**推理热路径优先内部 SRAM**。
- WiFi 开启后堆使用明显上升（WiFi 驱动 + LWIP 缓冲），AI 推理与 WiFi 同时跑时先算好预算（WiFi TX 峰值 400mA+ 是功耗不是内存，但两者都要预算）。
- 常见分配策略：模型数组放 Flash 分区（不占 RAM），Tensor Arena 放 PSRAM 或内部 SRAM，音频帧缓冲放内部 SRAM（延迟敏感）。

## 可复制 AI 提示词模板

模板 A：生成外设驱动（喂板级合同）

```text
我的板级合同 docs/board-contract.json 内容如下：<粘贴 pins/power/boot/led/audio 字段>。我要驱动这些外设：<按键/旋转编码器/WS2812/INMP441 麦克风/MAX98357A 功放/I2C 传感器>。请用 ESP-IDF 5.4（C 语言）为我生成对应外设驱动代码骨架：每个外设一个 .c/.h，包含初始化、读写/触发、错误处理；引脚一律从合同取，不得自己猜；代码里注释注明"引脚以板级合同为准"；最后给出 main.c 里如何组合调用。
```

模板 B：接入 TFLite Micro INT8 推理（T10 全模板）

```text
我要在 ESP32-S3（8MB PSRAM / 16MB Flash）上做 <关键词唤醒 / 音频分类 / 手势图像分类>。已训练好模型 <模型名>。
请帮我：① 评估用 TFLite Micro + ESP-NN 还是 ESP-DL 更合适；② 给出 INT8 量化后模型体积、Tensor Arena 大小、推理延迟量级的估算；③ 写出在 ESP-IDF 里初始化 interpreter、分配 tensor arena（放 PSRAM）、喂入 <音频帧/图像帧>、调用 Invoke 并打印 top-1 类别的完整示例代码；④ 提醒内存不够时如何降配。
```

模板 C：模型转换流水线（ONNX→TFLite→C 数组）

```text
我有 <ONNX / PyTorch / Keras> 格式的 <语音唤醒/图像分类> 模型，目标部署到 ESP32-S3（INT8 量化）。请给我一条完整的转换流水线命令：① 转 TFLite（含 representative dataset 做 INT8 校准）；② 量化后模型大小评估与剪枝/降采样建议；③ 转 C 数组或自定义分区两种方式的命令与工程改动；④ 转换后如何在固件里加载。给出每步命令与预期输出，我是 Windows 11 + Python 3.14。
```

模板 D：WiFi 与实时任务共存（任务划分设计）

```text
我的 ESP32-S3 固件要同时做：<实时音频采样/推理> 和 <WiFi 上传结果/OTA>。请帮我设计 FreeRTOS 任务划分：① 哪些放高优先级实时任务（音频/推理），哪些放低优先级（WiFi/网络）；② 共享数据怎么保护（队列/互斥锁/环形缓冲），给出代码骨架；③ WiFi 开启后内存与功耗预算怎么调整（WiFi TX 峰值 400mA+）；④ 常见"卡顿/掉线/内存不足"坑怎么避免。
```

## 常见坑

1. **现象**：GPIO 编号对不上，点不亮 LED 或驱动错外设。**原因**：AI/自己凭记忆写 GPIO，没读板级合同。**解决**：写驱动前先跑 02 模板 D；EasyInput 的 GPIO8/GPIO0 不是通用事实（见 board-reference.md 常见坑 1）。
2. **现象**：`idf.py build` 报分区表错误 / model 分区不识别。**原因**：partitions.csv 语法错（offset 缺失、类型写错）。**解决**：按 7.5 官方语法写，data 分区用 `spiffs` 子类型或显式 offset；用 `scripts/check_flash_budget.py` 校验。
3. **现象**：推理时 OOM / 反复重启。**原因**：Tensor Arena 或堆预算没算清，模型太大。**解决**：先跑 `scripts/check_flash_budget.py` 算清（分区 vs Flash、arena vs PSRAM）；降模型/降采样率/缩 arena。
4. **现象**：TFLite Micro 初始化报 `AllocateTensors` 失败。**原因**：arena 不够或算子没注册全。**解决**：增大 arena（放 PSRAM）、按模型用到的算子补齐 resolver、确认模型是 INT8。
5. **现象**：按键不响应或连跳。**原因**：没消抖或硬件/软件消抖阈值不一致。**解决**：软件消抖 20ms 与 03 环节硬件 100nF 对齐；边沿检测用中断+任务。
6. **现象**：I2S 音频初始化成功但麦克风无声。**原因**：INMP441 上电后稳定时间不够、BCLK/WS/SD 接错。**解决**：初始化后延时 >10ms 再读；对照板级合同核 SCK/WS/SD 引脚。
7. **现象**：WiFi 一连接，音频/推理卡顿或掉线。**原因**：任务优先级没分好、共享缓冲无保护。**解决**：按模板 D 划分任务；WiFi 事件回调与数据处理分离。
8. **现象**：模型推理结果永远同一个类别。**原因**：输入喂的格式不对（未做 INT8 量化缩放 / 帧格式不对）。**解决**：核对输入张量的 scale/zero_point，按训练时的预处理一致喂入。

## 验收清单

- [ ] `idf.py build` 编译通过，无 Error
- [ ] 所有 GPIO/外设引脚来自 `docs/board-contract.json`（无凭记忆猜脚）
- [ ] 板载 LED/按键最小系统在真机点亮/响应（烧录在 08 完成）
- [ ] 外设驱动（麦克风/功放/传感器等）已编译并逻辑审查通过
- [ ] 模型已转 INT8 并加载成功（C 数组或分区），推理能输出 top-1
- [ ] Tensor Arena 大小、分区表已跑 `scripts/check_flash_budget.py` 校验通过（分区求和 ≤ Flash、arena ≤ PSRAM 预算）
- [ ] WiFi/实时任务划分符合模板 D 设计，共享数据有保护
- [ ] 内存预算表（模型/arena/堆余量）已留档到 `docs/firmware-memory-budget.md`
- [ ] 证据分级如实记录：本环节验收为"编译通过 + 逻辑审查"；烧录/真机在 08 完成后回填

## 资源与延伸

- ESP-IDF 编程指南（中文，分区表/FreeRTOS/组件）：https://docs.espressif.com/projects/esp-idf/zh_CN/stable/ （官方）
- TensorFlow TFLite Micro（MCU 推理框架）：https://github.com/tensorflow/tflite-micro （GitHub）
- ESP-DL（乐鑫深度学习库，ONNX 部署）：https://github.com/espressif/esp-dl （GitHub）
- ESP-NN（向量指令加速算子）：https://github.com/espressif/esp-nn （GitHub）
- ESP-WHO（人脸检测/识别框架）：https://github.com/espressif/esp-who （GitHub）
- Edge Impulse（边缘 AI 建模平台）：https://www.edgeimpulse.com/ （官方）
- 训练营第 3 课（EasyInput 实时鼓机，含外设驱动与工程结构）：https://waytoagi.feishu.cn/wiki/F9f5wkfF5ibo3sku3Ppc6u5Tnnf （训练营）
