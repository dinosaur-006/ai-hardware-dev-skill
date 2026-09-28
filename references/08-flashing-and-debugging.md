# 08. 烧录及调试（Flashing & Debugging）

全流程的第 9 步。固件在本机编译通过后，本环节把它真正"灌"进 ESP32-S3 板子，并通过串口日志确认它**真的在跑**。输入：07 环节编译出的固件（`build/*.bin`）、一根能传数据的 USB 线、一块已上电的板子；输出：烧录成功 + 串口能看到自己写的日志 + 区分清楚"编译过/烧录过/真在跑"三件事。

> 关键心态：**编译成功 ≠ 烧录成功 ≠ 固件正常运行**。这是三段独立证据，缺一不可，见常见坑第 3 条。

## 目标与通过标准

- 目标：用最短路径把固件烧进板子，并会用串口日志定位问题。
- 通过标准：
  - 设备管理器里能看到板子对应的 COM 口（Linux/macOS 下 `/dev/ttyUSB0` 或 `/dev/tty.usbserial-*`）。
  - `esptool flash_id` 能读出芯片型号和 Flash 容量。
  - `idf.py flash` 烧录过程不报错、校验通过。
  - `idf.py monitor` 能看到自己代码里 `ESP_LOGI` 打印的输出。
  - 已掌握参考板 EasyInput V2.0 进入/退出下载模式的正确操作。

## 可复制操作与命令

### 0. 先认端口（Windows PowerShell）

```powershell
# 列出当前串口，确认板子插上后新增了哪个 COM
[System.IO.Ports.SerialPort]::GetPortNames()
```

macOS/Linux：

```bash
ls /dev/ttyUSB* /dev/tty.usbserial* /dev/tty.usbmodem* 2>/dev/null
```

> 插上板子前先记一次端口列表，插上后对比新增项，就是板子的口（Windows 下通常是 `COM3`、`COM4`……）。

### 1. 装 USB 串口驱动（第一次必做）

板子的串口芯片常见为 **CP210x** 或 **CH340**。设备管理器里如果 COM 口带黄色感叹号，或根本不出现，就是没装驱动：

- CP210x：到 Silicon Labs 官网下载 CP210x VCP 驱动。
- CH340：下载 CH341SER 驱动。
- 装完拔插一次 USB。**优先用主板后置 USB 口和能传数据的线**——很多线只能充电不能传数据，这是新手第一大坑。

### 2. 读芯片信息（先确认链路通）

```powershell
# 把 COM3 换成你实际的端口
esptool.py --chip esp32s3 --port COM3 flash_id
```

macOS/Linux：

```bash
esptool.py --chip esp32s3 --port /dev/ttyUSB0 flash_id
```

能看到 `Chip is ESP32-S3` 和 Flash ID，说明驱动、线、下载链路都通了。卡在这里就别往下走，先按常见坑排查。

### 3. 擦除 Flash（换新固件/分区表对不上时先擦）

```powershell
idf.py erase-flash
# 或直接用 esptool：
esptool.py --chip esp32s3 --port COM3 erase-flash
```

### 4. 烧录 + 监视（最常用一条命令）

```powershell
# 确保当前窗口已 source 过对应版本的 export.ps1
idf.py -p COM3 flash monitor
```

macOS/Linux：

```bash
idf.py -p /dev/ttyUSB0 flash monitor
```

退出监视：`Ctrl + ]`（Windows/Linux），macOS 同样 `Ctrl + ]`。

> 想提高烧录速度可加波特率：`idf.py -p COM3 -b 460800 flash`。

### 5. 进入下载模式的正确姿势

**通用 ESP32-S3 方法**：绝大多数开发板有 BOOT 和 RESET 两个键，通用做法是按住 BOOT 不放 → 点一下 RESET → 松开 BOOT，板子进入 ROM 下载模式，esptool 即可连上。

**EasyInput V2.0（本训练营参考板，真实操作，不要套用上面的通用法）**：

- 该板**没有独立 RESET 键**，且 USB 串口桥支持自动复位。
- 板子处于**开机运行状态**时，**短按一次 BOOT 键**即进入下载模式。
- **退出下载模式必须关机再重新上电**（拔插 USB / 关电源重开），按一下不会自己跑起来。
- **不要教、不要用"按住 BOOT 再上电"这套**——在这块板上不适用，按真实操作来。

如果 `esptool` 一直 `Connecting....` 连不上，先按上面 EasyInput 的方式确认板子确实处在下载模式，再重试。

### 6. 串口日志与日志级别

代码里用 ESP-IDF 日志宏分级打印，monitor 里才能按级别过滤：

```c
ESP_LOGE("main", "错误：%d", err);   // 错误
ESP_LOGW("main", "警告");
ESP_LOGI("main", "推理结果类别=%d", cls);  // 信息（最常用）
ESP_LOGD("main", "调试细节");
ESP_LOGV("main", "最啰嗦的 trace");
```

`idf.py menuconfig` → `Component config` → `Log output` 可设置默认显示级别。调试期把级别调到 Debug，稳定后调回 Info 省 Flash、省流量。

其他串口工具（任选其一，`idf.py monitor` 够用就不用装）：

- Arduino IDE：`工具 → 串口监视器`，波特率 115200。
- Windows：PuTTY（Serial，选 COM 口、115200）或任意"串口助手"。
- 命令行：`arduino-cli monitor -p COM3 -c baudrate=115200`。

### 7. Arduino IDE / PlatformIO 上传（速览分支）

- Arduino IDE：选好 ESP32S3 板型与 PSRAM 配置 → 点上传 → 串口监视器看日志。
- PlatformIO：`pio run -t upload`，`pio device monitor`。
- 本主线推荐 `idf.py`，Arduino/PIO 只在已有现成 Arduino 库时使用。

### 8. 国内网络 / 编码兜底

```powershell
# Python 默认 gbk 报 UnicodeDecodeError 时
$env:PYTHONUTF8=1
# 组件拉取走国内镜像
$env:IDF_COMPONENT_REGISTRY_URL = "https://components.espressif.cn"
# GitHub 直连不稳时，工具/二进制走 https://dl.espressif.cn
```

## 可复制 AI 提示词模板

模板 A：烧录失败诊断（贴 esptool 输出）

```text
我在 Windows PowerShell 下用 <idf.py flash / esptool.py> 烧录 ESP32-S3，命令是：<粘贴完整命令>。
报错原文：
<粘贴 esptool 完整输出，尤其是 Connecting failed / A fatal error occurred / Hash of data does not match>
我的板子是 EasyInput V2.0（无 RESET 键，开机状态短按 BOOT 进入下载模式，退出要重上电）。
请按"端口/驱动 → 下载模式 → 供电/线 → 分区与 flash 模式 → 固件本身"的顺序，列出最可能的 3 个原因和对应验证命令，不要让我瞎试。
```

模板 B：串口日志解读（贴 monitor 输出）

```text
我的 ESP32-S3 固件烧录成功了（esptool 校验通过），但 monitor 里看到的是：
<粘贴 monitor 日志，包括 Guru Meditation / Backtrace / panic / W (xxx) boot: 这些行>
请帮我判断：这是启动早期 panic（bootloader/分区/flash 配置问题）还是运行时崩溃（代码/内存问题）？根据 Backtrace 给出定位思路，并告诉我每条关键日志是什么意思。
```

模板 C：让 AI 生成驱动/串口联调代码（配合烧录验证）

```text
我刚烧录了一个新外设驱动（<按键/WS2812/I2S>），引脚定义：<粘贴板级引脚表>。请帮我在 main.c 里加一段最小自检代码：上电后通过 ESP_LOGI 周期性打印 <按键状态 / LED 闪烁计数 / I2S 采样值>，这样我烧进去看串口就能确认外设是否真的工作。同时告诉我：正常时日志应该长什么样，不正常时可能长什么样。
```

## 常见坑

1. **现象**：插上板子没 COM 口，或设备管理器里带黄色感叹号。**原因**：没装 CP210x/CH340 驱动，或用了只能充电的 USB 线。**解决**：装对应串口驱动，换一根能传数据的线，插主板后置 USB 口。
2. **现象**：esptool 一直 `Connecting....____` 连不上、最终 timeout。**原因**：板子不在下载模式。**解决**：EasyInput V2.0 在开机状态下短按一次 BOOT 进入下载模式；连不上时关机重开再试，不要用"按住 BOOT 再上电"那套。
3. **现象**：`idf.py flash` 显示 hash 校验通过，但一上电就重启 / 乱码 / 没日志。**原因**：把"烧录成功"当成了"固件正常"。烧录只证明 bin 写进了 Flash，运行还取决于分区表、flash 模式、供电、代码本身。**解决**：按三段证据排查——编译（build 无 error）→ 烧录（esptool hash matched）→ 运行（monitor 有预期日志）；先 `idf.py erase-flash` 再重烧一次，排除旧分区残留。
4. **现象**：烧录中途报 `A fatal error occurred: Flash read failed` 或校验错误、写一半失败。**原因**：供电不足（USB 口带不动 PSRAM 全速烧写）或 flash 模式配错（qio/dio 与实际 Flash 不匹配）。**解决**：换主板后置 USB 口/短线；`menuconfig → Serial Flasher Config → Flash mode` 改 `DIO` 试一次。
5. **现象**：构建/烧录脚本报路径乱码、ccache 崩溃，或 Python 报 `UnicodeDecodeError: 'gbk'`。**原因**：工程在中文路径下；Windows Python 默认 gbk。**解决**：工程放到纯英文路径如 `D:\eb-build`；执行 `$env:PYTHONUTF8=1` 后再烧录。
6. **现象**：`add-dependency` / 拉 esptool / clone 仓库一直超时。**原因**：国内直连 GitHub 不稳。**解决**：组件用 `$env:IDF_COMPONENT_REGISTRY_URL="https://components.espressif.cn"`；IDF 二进制走 `https://dl.espressif.cn`。
7. **现象**：monitor 里全是乱码。**原因**：串口波特率与固件日志波特率不一致。**解决**：把 monitor 波特率设为 115200（menuconfig 里日志默认波特率），两边对齐。

## 验收清单

- [ ] 设备管理器（或 `/dev`）里能看到板子对应的串口
- [ ] CP210x/CH340 驱动已装，换过数据线确认不是充电线问题
- [ ] `esptool.py --port COMx flash_id` 能读出 ESP32-S3 型号与 Flash 容量
- [ ] 知道 EasyInput V2.0 的正确下载模式操作（开机短按 BOOT 进入，重上电退出）
- [ ] `idf.py erase-flash` 成功执行过一次
- [ ] `idf.py -p COMx flash` 烧录校验通过（hash matched）
- [ ] `idf.py monitor` 能看到自己代码里 `ESP_LOGI` 打印的预期日志
- [ ] 能区分编译成功 / 烧录成功 / 运行正常三段证据，并用它定位过一次问题
- [ ] 工程在纯英文路径、`$env:PYTHONUTF8=1` 已设，国内镜像已配置
- [ ] 知道 monitor 退出键是 `Ctrl + ]`

## 资源与延伸

- ESP-IDF 编程指南（烧录、分区表、monitor 章节，中文官方文档）：https://docs.espressif.com/projects/esp-idf/zh_CN/stable/ （官方）
- esptool 官方文档（擦除/烧录/下载模式/排错）：https://docs.espressif.com/projects/esptool/ （官方）
- 乐鑫国内下载站（GitHub 慢时镜像）：https://dl.espressif.cn/ （官方镜像）
- 小智 AI 语音助手（含新手免环境烧录固件指南，可对照参考）：https://github.com/78/xiaozhi-esp32 （GitHub）
