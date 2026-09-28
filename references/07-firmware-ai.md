# 07. 固件开发（含 AI 推理）（Firmware & On-device AI Inference）

全流程的第 8 步。硬件已能上电（见 06 环节），本环节用 ESP-IDF 把"板"变成"设备"：搭工程结构、写外设驱动、接入并跑起一个 INT8 量化的 AI 小模型。输入：`docs/product-contract.md`、板级合同（`board-reference.md`）、一块能上电的 ESP32-S3（优先 N16R8：16MB Flash + 8MB PSRAM）；输出：一个能编译、能烧录、能在真机上跑实时任务并完成一次 AI 推理的固件工程。

## 目标与通过标准

- 目标：在 ESP32-S3 上，用 ESP-IDF 搭出可维护的固件骨架，并把一个 AI 模型（关键词唤醒 / 音频分类 / 图像分类任选其一）以 INT8 量化形式跑起来。
- 通过标准：
  - 能在 `idf.py set-target esp32s3` 后，用 `idf.py build` 一次编译通过。
  - 能说出本工程的分区划分（app / model / nvs / spiffs）及各自大小。
  - 至少 2 个外设驱动（按键消抖、WS2812、旋转编码器、I2S 音频中任选）在真机上验证通过。
  - 能在真机上完成一次 AI 推理，并通过串口打印出推理结果类别。
  - 模型为 INT8 量化，且已记录内存预算（模型体积、Tensor Arena 占用、剩余 PSRAM）。

## 可复制操作与命令

> 前提：本机已有两套 ESP-IDF（`D:\esp\v5.4.1` 与 `D:\esp\v5.5.5`）。**先选版本再开终端**——多版本共存时，哪个版本的 export 脚本被 source，当前终端就是哪个版本，二者不能混用同一个 build 目录。

### 0. 选版本并激活工具链（PowerShell）

```powershell
# 用 5.4.1（成熟稳定，多数老案例匹配）
D:\esp\v5.4.1\esp-idf\export.ps1
# 或用 5.5.5（新特性/新组件支持更好）
D:\esp\v5.5.5\esp-idf\export.ps1
```

macOS/Linux：

```bash
. ~/esp/esp-idf/export.sh   # 路径换成你本机 IDF 的实际位置
```

> 每次新开 PowerShell 窗口都要重新 source 一次对应版本的 export.ps1。不要两个版本在同一个窗口里先后 source。

### 1. 新建工程并指定目标芯片

```powershell
cd D:\eb-build                      # 纯英文路径构建目录（中文路径会让 ccache/ldgen 崩溃，见常见坑）
idf.py create-project my_device
cd my_device
idf.py set-target esp32s3
```

工程骨架（ESP-IDF）长这样，对照 Arduino 工程理解差异：

```text
my_device/
├── main/
│   ├── main.c              # app_main() 入口
│   ├── model_data.c        # INT8 模型的 C 数组（自动生成）
│   └── CMakeLists.txt      # 本组件源文件清单
├── partitions.csv          # 自定义分区表
├── sdkconfig               # menuconfig 生成（勿手改，用 menuconfig 改）
├── sdkconfig.defaults      # 想固化的默认配置写这里
└── CMakeLists.txt          # 顶层工程文件
```

| 对比项 | ESP-IDF（本主线） | Arduino（速览分支） |
| --- | --- | --- |
| 入口 | `app_main()`（C，FreeRTOS 任务里跑） | `setup()` / `loop()`（C++） |
| 配置 | `menuconfig` 图形化，分区表精细 | 板子菜单选型号，分区较粗 |
| AI/PSRAM | 原生支持 PSRAM、双核、ESP-NN 加速 | 封装简单，但复杂模型/PSRAM 调优受限 |
| 适合 | 本主线：音频/AI/产品化固件 | 极快 demo、简单外设 |

### 2. 配置分区表（partitions.csv）

在工程根目录建 `partitions.csv`，把模型单独放一个分区，避免和 app 挤在一起：

```csv
# Name,   Type, SubType, Offset,   Size,    Flags
nvs,      data, nvs,     ,         0x4000,
factory,  app,  factory, ,         0x300000,
model,    data, spiffs,  ,         0x200000,
```

`idf.py menuconfig` → `Partition Table` 选 "Custom partition table CSV" 并指向 `partitions.csv`；`Serial Flasher Config` 里确认 Flash 大小为 16MB、PSRAM 模式按板子选（N16R8 选 80MHz 8-line）。

### 3. 编译 / 清理 / 重配

```powershell
idf.py build
idf.py fullclean     # 换 IDF 版本或报奇怪错时先 fullclean
idf.py menuconfig
```

macOS/Linux：命令完全相同（`idf.py build` 等）。

### 4. 把 INT8 模型转成 C 数组嵌进固件

假设模型文件是 `model.tflite`（已 INT8 量化）：

```powershell
python -c "d=open('model.tflite','rb').read(); open('main/model_data.c','w').write('const unsigned char model_tflite['+str(len(d))+'] __attribute__((aligned(16))) = {'+','.join(str(b) for b in d)+'};\nconst unsigned int model_tflite_len = '+str(len(d))+';\n')"
```

> 模型较大（>1MB）时更建议烧进上面的 `model` 分区（spiffs），运行时 `esp_spiffs` 读出，而不是编进固件——可参考 AI 提示词模板 C。

### 5. 外设驱动：GPIO 按键消抖 / 旋转编码器 / WS2812 / I2S / NVS

不要手写寄存器，直接让 AI 基于板级合同生成，再真机验证。几个关键 API 约定（让 AI 照此风格写）：

- 按键消抖：`gpio_config()` 配输入 + 内部上拉，用 `esp_timer` 或 FreeRTOS 任务做 20ms 延时复测，不用 `vTaskDelay` 死等阻塞 UI 任务。
- WS2812：用 LED Strip 组件（`led_strip`，底层走 RMT 外设），**不要**用 bit-bang 软件模拟时序。
- 旋转编码器：A/B 两相中断 + 状态机判断方向，中断里只置标志/发队列，不做业务。
- I2S 音频：`i2s_driver_install()`，麦克风读、扬声器写用同一个 I2S 通道对，DMA 缓冲区交 FreeRTOS 队列传给推理任务。
- NVS 存配置（WiFi 凭据、阈值、校准值）：`nvs_flash_init()` → `nvs_open()` → `nvs_get_blob/set_blob()`。

### 6. 安全上电顺序（EasyInput V2.0 板特别注意）

EasyInput V2.0 上 **GPIO8 是外设共享电源域的使能脚**（详见 `board-reference.md`）。在 `app_main()` 最早期、**任何 I2S/传感器初始化之前**，先把 GPIO8 配成输出并驱动到板级合同规定的安全电平；再去初始化挂在该电源域下的外设。顺序反了或引脚悬空，会出现外设倒灌、欠压、反复重启。写驱动前先把板级合同里的"上电/下电顺序"读给 AI。

### 7. AI 推理接入

- 框架二选一：**TFLite Micro**（生态最大，配 ESP-NN 算子加速，关键词唤醒/音频分类/简单图像分类首选）或 **ESP-DL**（乐鑫自研，视觉/YOLO 类模型、ONNX 直接量化，性能更好）。
- 模型流水线：训练好的模型 → 导出 ONNX → 量化成 INT8（TFLite 用 PTQ；ESP-DL 用 esp-ppq）→ 上面第 4 步转数组或烧 model 分区 → `interpreter->Invoke()` 推理。
- 内存预算：ESP32-S3 有 512KB 内部 SRAM + 8MB PSRAM。权重放 Flash（只读），Tensor Arena（激活内存）放 PSRAM；INT8 后一个"关键词唤醒"模型通常几百 KB，"224×224 图像分类"约 1-3MB。先 `idf.py size` 看静态占用，推理时用 `esp_get_free_heap_size()` 打印剩余堆。

### 8. 国内网络加速（GitHub 直连不稳时）

```powershell
# 组件仓库走国内镜像
$env:IDF_COMPONENT_REGISTRY_URL = "https://components.espressif.cn"
# 从 GitHub 拉工具/组件超时的，改用乐鑫下载站 https://dl.espressif.cn （装 IDF 时镜像选项里也有）
```

## 可复制 AI 提示词模板

模板 A：生成外设驱动（先喂板级合同）

```text
我在做一个 ESP32-S3（ESP-IDF v<版本号>）固件，板级合同如下：<粘贴 board-reference.md 里的引脚表与上电顺序>。
请帮我写一个 main 组件，实现：<GPIO 按键消抖 / 旋转编码器 / WS2812 / I2S 麦克风+扬声器>。
要求：① 用 ESP-IDF 官方驱动（gpio/esp_timer/led_strip/i2s），不要软件 bit-bang WS2812；② 中断里只发 FreeRTOS 队列不做业务；③ 遵守 GPIO8 共享电源域的上电顺序；④ 每段关键代码加中文注释；⑤ 同时给出该组件的 CMakeLists.txt。我会自己编译烧录验证，你负责代码我负责真机测试。
```

模板 B：评估并接入 TFLite Micro INT8 推理

```text
我要在 ESP32-S3（8MB PSRAM / 16MB Flash）上做 <关键词唤醒 / 音频分类 / 手势图像分类>。已训练好模型 <模型名>。
请帮我：① 评估用 TFLite Micro + ESP-NN 还是 ESP-DL 更合适；② 给出 INT8 量化后模型体积、Tensor Arena 大小、推理延迟量级的估算；③ 写出在 ESP-IDF 里初始化 interpreter、分配 tensor arena（放 PSRAM）、喂入 <音频帧/图像帧>、调用 Invoke 并打印 top-1 类别的完整示例代码；④ 提醒内存不够时如何降配。
```

模板 C：模型转换流水线脚本（ONNX → TFLite INT8 → C 数组）

```text
请帮我写一份 Python 脚本，完成：把 onnx 模型用 onnx-tf/或 tf2onnx 等价路径转成 TFLite，再用代表数据集做 INT8 全整数量化，最后把 .tflite 转成 ESP-IDF 可直接编译的 C 数组（aligned(16)，含长度常量）。每一步给 pip 依赖、可运行命令和报错处理建议。我是 Windows PowerShell 环境，注意 Python 默认编码问题。
```

模板 D：WiFi 与实时任务共存设计

```text
我的设备既要连 WiFi 上传数据，又要实时做 <按键/音频节拍/电机>。请帮我设计 FreeRTOS 任务划分：哪些任务跑在哪个核、优先级如何、WiFi 事件循环放哪个核、如何避免 WiFi 断线重连时影响实时音频（爆音/丢键）。给出任务创建代码和优先级数值表，并说明为什么这样分。
```

## 常见坑

1. **现象**：`idf.py build` 在 ccache 或 ldgen 阶段崩溃 / 路径打印成乱码。**原因**：工程或构建目录在含中文的路径下（如 `C:\Users\明楚涵\...`）。**解决**：把构建工程放到纯英文路径，如 `D:\eb-build\my_device`；不要在用户中文目录里 build。
2. **现象**：编译过了，烧进去一推理就 Guru Meditation / 重启。**原因**：模型太大，Tensor Arena 超过可用 PSRAM，或模型数组没 16 字节对齐。**解决**：先 INT8 量化、缩小输入分辨率/帧率，确认数组 `__attribute__((aligned(16)))`，推理前打印 `esp_get_free_heap_size()`。
3. **现象**：板子上电后外设没反应，或反复重启、电流异常。**原因**：GPIO8 共享电源域上电顺序错了（悬空/过早初始化挂在该域下的外设导致倒灌欠压）。**解决**：在 `app_main` 最前面先把 GPIO8 配成输出并给安全电平，再初始化 I2S/传感器；以 `board-reference.md` 的上电顺序为准。
4. **现象**：开了 WiFi 后音频爆音、按键丢触发。**原因**：WiFi 任务和实时音频/按键任务争抢同一核 CPU。**解决**：实时任务固定跑在核 0 并给高优先级，WiFi/LWIP 跑核 1 低优先级；推理任务用 `xTaskCreatePinnedToCore` 绑定核。
5. **现象**：换了个 IDF 版本编译就报一堆奇怪错误。**原因**：build 目录残留了上个版本的中间产物。**解决**：`idf.py fullclean`，确认当前窗口 source 的是哪个版本的 export.ps1；多版本建议各用独立 build 目录。
6. **现象**：Python 脚本报 `UnicodeDecodeError: 'gbk' codec can't decode...`。**原因**：Windows 下 Python 默认用 gbk 读文件。**解决**：构建前执行 `$env:PYTHONUTF8=1`，模型转数组脚本也在 UTF-8 模式下跑。
7. **现象**：`idf.py add-dependency` 拉组件超时 / GitHub clone 断连。**原因**：国内直连 GitHub 不稳。**解决**：组件走 `$env:IDF_COMPONENT_REGISTRY_URL="https://components.espressif.cn"`；IDF/工具二进制走 `https://dl.espressif.cn` 镜像。

## 验收清单

- [ ] 已 source 正确版本的 ESP-IDF（5.4.1 或 5.5.5），终端 `idf.py --version` 对得上
- [ ] 工程放在纯英文路径（如 `D:\eb-build\my_device`），`idf.py set-target esp32s3` 成功
- [ ] `idf.py build` 一次编译通过，无 error
- [ ] `partitions.csv` 已划分 nvs / factory / model 分区并在 menuconfig 选中
- [ ] 至少 2 个外设驱动在真机验证通过（按键消抖 / WS2812 / 编码器 / I2S 任选）
- [ ] GPIO8 共享电源域的上电顺序已按板级合同写在 `app_main` 早期
- [ ] NVS 能读写一个配置项（重启后值保留）
- [ ] INT8 模型已嵌入（数组或 model 分区），真机推理能打印 top-1 结果
- [ ] 已记录内存预算（模型体积 / Tensor Arena / 剩余 PSRAM）
- [ ] 已按"先读板级合同 → AI 生成驱动 → 真机验证"的 vibecoding 流程跑通至少一个驱动

## 资源与延伸

- ESP-IDF 编程指南（中文，官方文档）：https://docs.espressif.com/projects/esp-idf/zh_CN/stable/ （官方）
- TFLite for Microcontrollers（官方仓库）：https://github.com/tensorflow/tflite-micro （GitHub）
- ESP-DL 乐鑫深度学习库（ONNX 量化部署）：https://github.com/espressif/esp-dl （GitHub）
- ESP-NN ESP32-S3 向量指令加速算子库：https://github.com/espressif/esp-nn （GitHub）
- ESP-WHO 人脸检测/识别框架（基于 ESP-DL 的示例集）：https://github.com/espressif/esp-who （GitHub）
- Edge Impulse 边缘 AI 建模平台（数据采集→训练→部署一站式）：https://www.edgeimpulse.com/ （官方/平台）
- 小智 AI 语音助手（ESP32 端到端语音参考工程）：https://github.com/78/xiaozhi-esp32 （GitHub）
- 乐鑫国内下载站（GitHub 慢时的镜像）：https://dl.espressif.cn/ （官方镜像）
