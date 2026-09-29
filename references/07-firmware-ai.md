# 07. 固件开发（含 AI 推理）（Firmware & On-device AI Inference）

全流程的环节 07。硬件已能上电（见 06 环节），本环节用 ESP-IDF 把"板"变成"设备"：搭工程结构、写外设驱动、接入并跑起一个 INT8 量化的 AI 小模型。输入：`docs/product-contract.md`、板级合同（`board-reference.md`）、一块能上电的 ESP32-S3（优先 N16R8：16MB Flash + 8MB PSRAM）；输出：一个能编译、能烧录、能在真机上跑实时任务并完成一次 AI 推理的固件工程。

## 目标与通过标准

- 目标：在 ESP32-S3 上，用 ESP-IDF 搭出可维护的固件骨架，并把一个 AI 模型（关键词唤醒 / 音频分类 / 图像分类任选其一）以 INT8 量化形式跑起来。
- 通过标准：
  - 能在 `idf.py set-target esp32s3` 后，用 `idf.py build` 一次编译通过。
  - 能说出本工程的分区划分（app / model / nvs / spiffs）及各自大小。
  - 至少 2 个外设驱动（按键消抖、WS2812、旋转编码器、I2S 音频中任选）在真机上验证通过。
  - 能在真机上完成一次 AI 推理，并通过串口打印出推理结果类别。
  - 模型为 INT8 量化，且已记录内存预算（模型体积、Tensor Arena 占用、剩余 PSRAM）。

## 可复制操作与命令

> 前提：本机已有两套 ESP-IDF（版本号因机而异，下文用 `<你的 IDF 安装路径>` 变量表示；以本机 `D:\esp\v5.4.1` 与 `D:\esp\v5.5.5` 为例）。**先选版本再开终端**——多版本共存时，哪个版本的 export 脚本被 source，当前终端就是哪个版本，二者不能混用同一个 build 目录。

### 0. 选版本并激活工具链（PowerShell）

```powershell
# <你的 IDF 安装路径> 换成你本机对应版本的目录（以本机 D:\esp\v5.4.1 为例）
# 用 5.4.1（成熟稳定，多数老案例匹配）
<你的 IDF 安装路径>\esp-idf\export.ps1
# 或用另一版本（新特性/新组件支持更好），二选一，不要在同一窗口先后 source
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
# Name,   Type, SubType, Offset,   Size,     Flags
# 官方规则（来源：ESP-IDF 分区表文档，见本节末链接）：
#   - Offset 留空合法：gen_esp32part.py 自动排布，app 对齐 64KB(0x10000)、data 对齐 4KB(0x1000)；
#   - nvs(data,nvs) 官方建议 ≥ 0x3000；factory(app,factory) 留空会自动落到 0x10000；
#   - phy_init(data,phy) 可选（默认 PHY 初始化数据编进固件，不需要可省略）。
nvs,      data, nvs,     ,         0x4000,
factory,  app,  factory, ,         0x300000,
model,    data, spiffs,  ,         0x200000,
```

> 说明：上面 Offset 全部留空是官方支持的写法，工具会按对齐规则自动计算；改了 `CONFIG_PARTITION_TABLE_OFFSET` 时也不必手算偏移。规则出处：ESP-IDF 编程指南「分区表」章节（Type/SubType/Offset/Size 规则、data 子类型 nvs/spiffs 等），https://docs.espressif.com/projects/esp-idf/zh_CN/stable/esp32s3/api-guides/partition-tables.html 。

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
python -c "d=open('model.tflite','rb').read(); open('main/model_data.c','w').write('const unsigned char model_tflite['+str(len(d))+'] __attribute__((aligned(16))) = {'+','.join(str(b) for b in d)+'};\nconst unsigned int model_tflite_len = '+str(len(d))+' ;\n')"
```

> 模型较大（>1MB）时更建议烧进上面的 `model` 分区（spiffs），运行时 `esp_spiffs` 读出，而不是编进固件——可参考 AI 提示词模板 C。

### 5. 外设驱动：GPIO 按键消抖 / 旋转编码器 / WS2812 / I2S / NVS

不要手写寄存器，直接让 AI 基于板级合同生成，再真机验证。几个关键 API 约定（让 AI 照此风格写）：

- 按键消抖：`gpio_config()` 配输入 + 内部上拉，用 `esp_timer` 或 FreeRTOS 任务做 20ms 延时复测，不用 `vTaskDelay` 死等阻塞 UI 任务。
- WS2812：用 LED Strip 组件（`led_strip`，底层走 RMT 外设），**不要**用 bit-bang 软件模拟时序。
- 旋转编码器：A/B 两相中断 + 状态机判断方向，中断里只置标志/发队列，不做业务。
- I2S 音频：`i2s_driver_install()`，麦克风读、扬声器写用同一个 I2S 通道对，DMA 缓冲区交 FreeRTOS 队列传给推理任务。
- NVS 存配置（WiFi 凭据、阈值、校准值）：`nvs_flash_init()` → `nvs_open()` → `nvs_get_blob/set_blob()`。

### 6. 安全上电顺序（板级电源域，按合同）

> 板级事实去重：本节不写死具体 GPIO 编号与电平，一律以板级合同为准。引用位形如 `<board-contract:power.enable_gpio>`、`<board-contract:power.active_level>`、`<board-contract:power.shared_consumers>`、`<board-contract:power.power_up_settle_time_ms>`；**具体值以 `docs/board-contract.json` 为准，新板先建合同再开发**（建合同方法见 `board-reference.md` 第二部分）。

在 `app_main()` 最早期、**任何挂在该电源域下的外设初始化之前**：先把 `<board-contract:power.enable_gpio>`（共享电源域使能脚）配成输出并驱动到合同规定的 `<board-contract:power.active_level>` 安全电平；待电源稳定（等待合同里的 `power_up_settle_time_ms`，未写明则先实测、不要照抄别板延时）后，再去初始化 `<board-contract:power.shared_consumers>` 列出的外设（I2S/MIC/SPK 等）。顺序反了或使能脚悬空，会出现外设倒灌、欠压、反复重启。写驱动前先把板级合同里的"上电/下电顺序"读给 AI。

### 7. AI 推理接入

- 框架二选一：**TFLite Micro**（生态最大，配 ESP-NN 算子加速，关键词唤醒/音频分类/简单图像分类首选）或 **ESP-DL**（乐鑫自研，视觉/YOLO 类模型、ONNX 直接量化，性能更好）。
- 模型流水线：训练好的模型 → 导出 ONNX → 量化成 INT8（TFLite 用 PTQ；ESP-DL 用 esp-ppq）→ 上面第 4 小节转数组或烧 model 分区 → `interpreter->Invoke()` 推理。
- 内存预算：ESP32-S3 标称约 512KB 内部 SRAM，但**这个总数包含 cache、中断/栈、系统保留占用，运行时可用自由堆（free heap）远小于 512KB**，不要按 512KB 规划。另有 8MB PSRAM。权重放 Flash（只读）；Tensor Arena（激活内存）可放 PSRAM——**能跑，但要接受代价**：经验上 tensor arena 放在 PSRAM 后，首次访问 PSRAM 有明显冷启动延迟、单次推理延迟比放内部 RAM 显著增大（PSRAM 带宽低于内部 SRAM）。建议：小模型（关键词唤醒等）优先把 Tensor Arena 放内部 RAM 以换取低延迟；模型偏大塞不进内部 RAM 时再放 PSRAM，并实测记录延迟、接受该代价。INT8 后一个"关键词唤醒"模型通常几百 KB，"224×224 图像分类"约 1-3MB。先 `idf.py size` 看静态占用，推理时用 `esp_get_free_heap_size()` / `esp_get_free_internal_heap_size()` 分别打印内部与外部剩余堆。

### 8. 国内网络加速（GitHub 直连不稳时）

```powershell
# 组件仓库走国内镜像
$env:IDF_COMPONENT_REGISTRY_URL = "https://components.espressif.cn"
# 从 GitHub 拉工具/组件超时的，改用乐鑫下载站 https://dl.espressif.cn （装 IDF 时镜像选项里也有）
```

### 9. OTA 固件升级与版本管理

产品化阶段设备已分发出去，不可能再逐根 USB 线烧录，这时需要 OTA（Over The Air）。本小节讲固件侧要准备什么：分区表怎么从单 app 改成双 bank、HTTPS OTA 怎么跑、升级失败怎么自动回滚、设备身份与版本怎么管。**板级无关**：本节只讲 Flash 分区与固件逻辑，不涉及任何具体引脚。

> 落盘约定：OTA 的设计与灰度策略单独写 `docs/ota.md`（分区表版本、当前固件版本号、服务器地址/CDN、灰度批次、回滚预案都记在那里），不要散落在代码注释里。

#### 9.1 OTA 分区表设计（从单 factory 改双 bank）

第 2 小节的样例是单 `factory` 分区（无 OTA 能力）。要支持 OTA，必须把单 app 换成两个 OTA app 槽 `ota_0`/`ota_1`，再加一个 `otadata` 分区记录"下次启动哪个槽"。新的 `partitions.csv` 如下（Offset 仍全部留空，沿用第 2 小节官方自动对齐规则；app 子类型从 `factory` 改成 `ota_0`/`ota_1`）：

```csv
# Name,   Type, SubType, Offset,   Size,     Flags
# OTA 双 bank 分区表（替换第 2 小节的单 factory 样例后使用）：
#   - nvs(data,nvs)：存 WiFi 凭据/设备身份/配置，OTA 不擦它，建议 0x6000；
#   - otadata(data,ota)：OTA 状态区，官方固定 2 个扇区 = 0x2000（双扇区写，写坏一个还有另一个）；
#   - app0(app,ota_0) / app1(app,ota_1)：两个 app 槽，OTA 永远写"当前没在跑"的那个；
#     两个槽大小必须一致，且都 ≥ 最大固件 bin 体积（用 idf.py size 看，留余量）；
#   - model(data,spiffs)：模型/资源数据分区，OTA 不碰它（offset 留空自动排在 app 之后）。
# 官方规则同第 2 小节：Offset 留空合法，app 对齐 0x10000、data 对齐 0x1000。
nvs,      data, nvs,     ,         0x6000,
otadata,  data, ota,     ,         0x2000,
app0,     app,  ota_0,   ,         0x300000,
app1,     app,  ota_1,   ,         0x300000,
model,    data, spiffs,  ,         0x200000,
```

> 要点：① 两个 app 槽各 3MB 是示例，按你的固件实际体积定（`idf.py size` 看 app 占用，留约 20% 余量）；② 改成分区表后**第一次仍要 USB 烧录一次**（把新分区表 + 首版固件烧进 ota_0），之后才走 OTA；③ 数据分区（model/spiffs）的 offset 同样留空即可，工具自动排在两个 app 之后，**不要手填与 app 重叠的地址**。规则出处：ESP-IDF 编程指南「空中升级 (OTA)」章节（otadata 双扇区、ota_0/ota_1 双槽、回滚状态机），https://docs.espressif.com/projects/esp-idf/zh_CN/stable/esp32s3/api-reference/system/ota.html 。

#### 9.2 HTTPS OTA 流程（esp_https_ota）

核心是乐鑫自带的 `esp_https_ota` 组件：设备连 WiFi 后从服务器下载固件 bin，写进"非运行中"的那个 app 槽，校验通过后改 otadata 指向它，重启进新固件。流程要点（不是死记命令，是要保证每一步都做对）：

1. **服务器放固件**：把编译产物 `build/` 下生成的固件 `.bin`（或合并后的 all-in-one bin）放到 HTTPS 服务器/CDN 上，**同一个版本号只对应一个固定 URL**，别让设备每次下到不同文件。
2. **版本校验**：下载前先取服务器侧版本号（如一个 `version.json` 接口），和本机 `esp_app_desc` 里的版本比，服务器版本不更新就不下载，避免反复刷同一个 bin。
3. **镜像校验**：`esp_https_ota` 内部会校验镜像头/摘要；落盘前再对整包算 sha256 和服务器给的校验值比对，不一致就丢弃这个槽、不切启动分区。
4. **成功标记**：新固件第一次启动跑通自检后，必须调用 `esp_ota_mark_app_valid_cancel_rollback()` 把自己标成有效（见 9.4）；不标，下次重启会被 bootloader 自动回滚。
5. **失败回滚**：下载写坏/校验失败/新固件起不来，otadata 不动或回指旧槽，设备下次仍从旧版本启动——这就是双 bank 的意义。

最小可复制骨架（放到独立 FreeRTOS 任务里触发，别阻塞主任务）：

```c
#include "esp_https_ota.h"
#include "esp_app_desc.h"

static void ota_task(void *arg)
{
    const esp_app_desc_t *cur = esp_app_get_description();   // 编译期注入的当前固件版本
    esp_http_client_config_t cfg = {
        .url = "https://你的服务器/ota/firmware.bin",   // 占位，需替换为真实 HTTPS 地址（正式服务器/CDN 见 docs/ota.md）
        .timeout_ms = 10000,
        // .crt_bundle_attach = esp_crt_bundle_attach,   // 用系统根证书包校验服务器 HTTPS 证书
    };
    esp_https_ota_config_t ota_cfg = { .http_config = &cfg };
    ESP_LOGI(TAG, "当前版本=%s，开始 OTA 下载", cur->version);

    esp_https_ota_handle_t h = NULL;
    if (esp_https_ota_begin(&ota_cfg, &h) != ESP_OK) {
        ESP_LOGE(TAG, "begin 失败，放弃本次升级"); goto done;
    }
    while (esp_https_ota_perform(h) == ESP_ERR_HTTPS_OTA_IN_PROGRESS) {
        /* 流式下载中，可在此打印进度 */
    }
    if (esp_https_ota_is_complete_data_received(h) &&
        esp_https_ota_finish(h) == ESP_OK) {
        ESP_LOGI(TAG, "写入完成，5 秒后重启进新固件");
        vTaskDelay(pdMS_TO_TICKS(5000));
        esp_restart();
    } else {
        ESP_LOGE(TAG, "OTA 失败，不切分区，继续跑旧固件");
        esp_https_ota_abort(h);
    }
done:
    vTaskDelete(NULL);
}
```

> `menuconfig → Bootloader config → Enable app rollback support` 打开回滚；`Application manager` 里把固件版本号（`CONFIG_APP_PROJECT_VER`）设对，它就是 `esp_app_desc.version` 的来源。

#### 9.3 云 OTA 与国内镜像注意点（检查清单）

国内设备访问国外 OTA 服务器不稳定是常态。不要照抄某条命令，按这张清单逐项确认（具体服务器选型/CDN 由你定，记进 `docs/ota.md`）：

- [ ] **服务器/CDN 选址**：固件下载量大，优先选国内节点或国内云对象存储 + CDN 加速，不要让设备直连海外源站；海外用户单独走海外 CDN。
- [ ] **HTTPS 证书**：必须 HTTPS，设备端用官方 `crt_bundle` 校验服务器证书（别关校验裸跑 HTTP）；证书到期前在 `docs/ota.md` 里登记续期提醒。
- [ ] **带宽成本**：每个固件 bin 几 MB × 几万台设备 = 大量下载流量，用 CDN 回源 + 缓存，避免源站被打穿；灰度期间只放给小批次设备。
- [ ] **接口设计**：设备上报 `device_id + 当前版本 + 批次`，服务器返回"是否有新版本 + 下载地址 + 强制/可选升级"，按批次灰度下发，不要全员同时升级。
- [ ] **失败重试**：下载中断/失败不要立刻全量重刷（见 9.6）；连续失败 N 次后退回旧固件并上报失败日志，别把设备刷砖。

#### 9.4 升级回滚策略

- **交替写入**：OTA 永远写"当前没在跑"的那个槽（跑在 ota_0 就写 ota_1，反之亦然），写坏时运行中的旧固件不受影响。
- **启动后标记有效**：`menuconfig` 打开 `CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE` 后，新固件第一次启动处于待验证态；**跑通关键自检（能联网 / 能完成一次推理 / 关键外设正常）后立刻调用 `esp_ota_mark_app_valid_cancel_rollback()`**。
- **回滚触发**：新固件自检失败 → 调 `esp_ota_mark_app_invalid_rollback_and_reboot()` 主动回滚；或新固件直接崩溃/断电没来得及标记，bootloader 下次启动会把待验证态判为中止并自动跳回上一版本。
- **版本号比较**：服务器下发前比版本号，设备本机也比；只有服务器版本 > 本机版本才升级（配合 `esp_app_desc.version`），防止旧包把新设备刷回去。更严格的安全防回滚（`CONFIG_BOOTLOADER_APP_ANTI_ROLLBACK`）量产有安全要求时再开。

#### 9.5 设备身份与固件版本管理

- **NVS 存设备身份**：`device_id`（出厂烧录的唯一序列号）、当前固件版本、硬件批次号存在 NVS（`nvs_open("dev", ...)`），OTA 上报时一起带给服务器。
- **`esp_app_desc` 版本字段**：固件编译期自动生成 `esp_app_desc_t`，里面的 `version`/`secure_version`/`date` 就是当前镜像的版本来源，代码里直接读 `esp_app_get_description()`，**不要在业务代码里另写一份手填版本号**，容易和真实固件对不上。
- **服务器按批次下发**：服务器维护 `device_id → 批次/硬件型号/当前版本` 表，只给匹配的设备下发对应固件（不同硬件型号固件不通用），灰度批次先小后大。

#### 9.6 断点续传与断电安全

- **分块下载**：大固件分块（如每块 64KB~256KB）下载，记录已写进度到 NVS 或一个小 data 分区；断线后续传从断点继续，而不是整包重下（自己做断点要配合 HTTP Range 请求；`esp_https_ota` 默认是流式写槽）。
- **写入前校验**：每块/整包算 sha256，和服务器公布的校验值比对；镜像头、长度、摘要任一不符就丢弃这个槽，otadata 不切换。
- **断电在写入中间**：因为是写"另一个 bank"，写到一半断电，**运行中的旧 bank 完好**；下次上电 bootloader 看 otadata 仍指向旧 bank，旧固件照跑，那个没写完的槽下次 OTA 会被重新擦写。这就是双 bank + otadata 双扇区（0x2000）的兜底——断电不会变砖，前提是 9.4 的回滚/有效标记做齐。

## 可复制 AI 提示词模板

模板 A：生成外设驱动（先喂板级合同）

```text
我在做一个 ESP32-S3（ESP-IDF v<版本号>）固件，板级合同如下：<粘贴 board-reference.md 里的引脚表与上电顺序>。
请帮我写一个 main 组件，实现：<GPIO 按键消抖 / 旋转编码器 / WS2812 / I2S 麦克风+扬声器>。
要求：① 用 ESP-IDF 官方驱动（gpio/esp_timer/led_strip/i2s），不要软件 bit-bang WS2812；② 中断里只发 FreeRTOS 队列不做业务；③ 按板级合同遵守共享电源域使能脚（<board-contract:power.enable_gpio>）的上电顺序，先使能再初始化下游外设；④ 每段关键代码加中文注释；⑤ 同时给出该组件的 CMakeLists.txt。我会自己编译烧录验证，你负责代码我负责真机测试。
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

模板 E：OTA 分区与回滚设计

```text
我要给 ESP32-S3 设备做 OTA 升级。当前是单 factory 分区（partitions.csv 见下）：<粘贴现有 partitions.csv>。
请帮我：① 改成 ota_0/ota_1 双 bank + otadata 的分区表（nvs 0x6000、otadata 0x2000、两个 app 槽各留够、model/spiffs 数据分区保留），Offset 留空并沿用官方自动对齐的注释风格；② 写出 esp_https_ota 下载 + 新固件自检后 esp_ota_mark_app_valid_cancel_rollback 标记 + 失败自动回滚的完整任务代码；③ 说明 menuconfig 要打开哪几个 Kconfig（回滚使能 / 固件版本号）；④ 列出国内 CDN 选址 / HTTPS 证书 / 按 device_id 批次灰度下发的检查清单。我会自己烧录验证，你负责设计与代码，我负责真机升级测试。
```

## 常见坑

1. **现象**：`idf.py build` 在 ccache 或 ldgen 阶段崩溃 / 路径打印成乱码。**原因**：工程或构建目录在含中文的路径下（如 `C:\Users\明楚涵\...`）。**解决**：把构建工程放到纯英文路径，如 `D:\eb-build\my_device`；不要在用户中文目录里 build。
2. **现象**：编译过了，烧进去一推理就 Guru Meditation / 重启。**原因**：模型太大，Tensor Arena 超过可用 PSRAM，或模型数组没 16 字节对齐。**解决**：先 INT8 量化、缩小输入分辨率/帧率，确认数组 `__attribute__((aligned(16)))`，推理前打印 `esp_get_free_heap_size()`。
3. **现象**：板子上电后外设没反应，或反复重启、电流异常。**原因**：共享电源域使能脚（板级合同 `power.enable_gpio`）上电顺序错了（悬空/过早初始化挂在该域下的外设导致倒灌欠压）。**解决**：在 `app_main` 最前面先把 `<board-contract:power.enable_gpio>` 配成输出并给到合同规定的安全电平，再初始化 I2S/传感器；以板级合同 `docs/board-contract.json`（见 `board-reference.md`）的上电顺序为准，不要照抄别板引脚号。
4. **现象**：开了 WiFi 后音频爆音、按键丢触发。**原因**：WiFi 任务和实时音频/按键任务争抢同一核 CPU。**解决**：实时任务固定跑在核 0 并给高优先级，WiFi/LWIP 跑核 1 低优先级；推理任务用 `xTaskCreatePinnedToCore` 绑定核。
5. **现象**：换了个 IDF 版本编译就报一堆奇怪错误。**原因**：build 目录残留了上个版本的中间产物。**解决**：`idf.py fullclean`，确认当前窗口 source 的是哪个版本的 export.ps1；多版本建议各用独立 build 目录。
6. **现象**：Python 脚本报 `UnicodeDecodeError: 'gbk' codec can't decode...`。**原因**：Windows 下 Python 默认用 gbk 读文件。**解决**：构建前执行 `$env:PYTHONUTF8=1`，模型转数组脚本也在 UTF-8 模式下跑。
7. **现象**：`idf.py add-dependency` 拉组件超时 / GitHub clone 断连。**原因**：国内直连 GitHub 不稳。**解决**：组件走 `$env:IDF_COMPONENT_REGISTRY_URL="https://components.espressif.cn"`；IDF/工具二进制走 `https://dl.espressif.cn` 镜像。
8. **现象**：OTA 升级"成功"后设备重启变砖 / 反复 boot 进不了系统。**原因**：没开回滚、新固件启动后没调 `esp_ota_mark_app_valid_cancel_rollback()` 标记有效，或镜像 sha256 没校验就切了启动分区。**解决**：双 bank 写入 + 打开 `CONFIG_BOOTLOADER_APP_ROLLBACK_ENABLE`，新固件跑通自检后立刻标记有效；没标记的待验证固件重启会被 bootloader 自动回滚到旧版本，不会变砖。
9. **现象**：OTA 下载到一半报分区空间不足 / `esp_ota_begin` 失败。**原因**：ota_0/ota_1 两个 app 槽留小了（固件 bin 涨上去超过单槽），或没按双 bank 把两个槽配成等大。**解决**：`idf.py size` 看 app 实际占用，两个 app 槽都调到 ≥ 固件体积 + 约 20% 余量，重新分区（首次仍要 USB 烧一次新分区表）。

## 验收清单

- [ ] 已 source 正确版本的 ESP-IDF（5.4.1 或 5.5.5），终端 `idf.py --version` 对得上
- [ ] 工程放在纯英文路径（如 `D:\eb-build\my_device`），`idf.py set-target esp32s3` 成功
- [ ] `idf.py build` 一次编译通过，无 error
- [ ] `partitions.csv` 已划分 nvs / factory / model 分区并在 menuconfig 选中
- [ ] 至少 2 个外设驱动在真机验证通过（按键消抖 / WS2812 / 编码器 / I2S 任选）
- [ ] 共享电源域使能脚（`<board-contract:power.enable_gpio>`）的上电顺序已按板级合同写在 `app_main` 早期，且未在正文写死引脚号
- [ ] NVS 能读写一个配置项（重启后值保留）
- [ ] INT8 模型已嵌入（数组或 model 分区），真机推理能打印 top-1 结果
- [ ] 已记录内存预算（模型体积 / Tensor Arena / 剩余 PSRAM）
- [ ] 已按"先读板级合同 → AI 生成驱动 → 真机验证"的 vibecoding 流程跑通至少一个驱动
- [ ] 已把分区表改成 ota_0/ota_1 双 bank + otadata，两个 app 槽等大且留够固件体积余量
- [ ] OTA 升级失败或新固件起不来时，设备能自动回滚到上一可用版本（双 bank 兜底，不变砖）
- [ ] 新固件首次启动跑通自检后调用了 `esp_ota_mark_app_valid_cancel_rollback()`
- [ ] 设备身份 / 当前版本存在 NVS，服务器能按 device_id + 批次下发对应固件

## 资源与延伸

- ESP-IDF 编程指南（中文，官方文档）：https://docs.espressif.com/projects/esp-idf/zh_CN/stable/ （官方）
- TFLite for Microcontrollers（官方仓库）：https://github.com/tensorflow/tflite-micro （GitHub）
- ESP-DL 乐鑫深度学习库（ONNX 量化部署）：https://github.com/espressif/esp-dl （GitHub）
- ESP-NN ESP32-S3 向量指令加速算子库：https://github.com/espressif/esp-nn （GitHub）
- ESP-WHO 人脸检测/识别框架（基于 ESP-DL 的示例集）：https://github.com/espressif/esp-who （GitHub）
- Edge Impulse 边缘 AI 建模平台（数据采集→训练→部署一站式）：https://www.edgeimpulse.com/ （官方/平台）
- 小智 AI 语音助手（ESP32 端到端语音参考工程）：https://github.com/78/xiaozhi-esp32 （GitHub）
- 乐鑫国内下载站（GitHub 慢时的镜像）：https://dl.espressif.cn/ （官方镜像）
