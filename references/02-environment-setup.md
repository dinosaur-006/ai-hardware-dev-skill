# 02. 开发环境搭建（Development Environment Setup）

全流程的第 3 步。在选型（01 环节）确定为 ESP32-S3 主线后，把电脑上的编译/烧录/串口/前端工具链一次性装到位。**Windows 优先**，macOS/Linux 给出等价写法。输入：选型结论（ESP32-S3）；输出：一条能 `idf.py build` + 一条能 `pnpm dev` 的可用命令行环境。

## 目标与通过标准

- 目标：在 Windows 上装齐五件套——ESP-IDF 5.x、Arduino IDE、MicroPython（mpremote/Thonny）、PlatformIO（VSCode）、Node.js 24 + pnpm，并把串口驱动装好，让后面所有环节都能"复制命令即跑"。
- 通过标准：
  - 能在新开的 PowerShell 窗口里一行命令激活 ESP-IDF 5.x，并 `idf.py --version` 正常输出版本号。
  - 能在设备管理器里看到板子对应的 COM 口（CP210x 或 CH340 驱动已装）。
  - 能在纯英文路径（如 `D:\eb-build`）下完成一次 `idf.py build`，不报 ccache / gbk / ldgen 中文路径错误。
  - 能 `node -v` 显示 v24.x、`pnpm -v` 正常（WebSerial 等前端工具备用）。
  - 已为后续 AI 辅助开发准备好"纯英文工程目录 + 板级合同文件"。

## 可复制操作与命令

### 0. 通用原则（先读，避免后面所有坑）

- **工程一律放纯英文路径**：如 `D:\eb-build`、`D:\projects\my-device`。不要放在 `桌面\硬件\`、含中文/空格路径下做编译（详见"常见坑"1/2/3）。
- **每个新开的 PowerShell 窗口都要重新激活一次 ESP-IDF**——IDF 的环境变量只在当前窗口有效，不会全局持久化。
- 国内网络：IDF/工具链用 `dl.espressif.cn`，组件用 `components-file.espressif.cn`，Arduino 板包用 jihulab 镜像，不要硬刚 GitHub。

### 1. 串口驱动与 COM 口确认

1. 按板子上的串口芯片装驱动（看板子原理图或丝印）：
   - **CP210x**（Silabs）：装 CP210x Universal Windows Driver（见"资源与延伸"链接）。
   - **CH340/CH341**（沁恒）：运行 CH341SER.EXE 一键安装。
2. USB 线接板子（注意要用数据线，不是只能充电的线），打开"设备管理器 → 端口 (COM 和 LPT)"，记下 COM 号，例如 `COM4`。
3. PowerShell 里一行确认当前可见的串口：

```powershell
Get-CimInstance Win32_PnPEntity | Where-Object { $_.Name -match 'COM\d+' } | Select-Object Name, Status
```

macOS/Linux：macOS 看 `/dev/cu.usbserial-*` 或 `/dev/cu.usbmodem*`；Linux 看 `/dev/ttyUSB*` / `/dev/ttyACM*`（`ls /dev/ttyUSB*`）。

### 2. ESP-IDF 5.x 安装与多版本共存

**安装方式二选一**：

- **图形安装器 / EIM（推荐新手）**：从 `dl.espressif.cn` 下载 ESP-IDF 安装器（在线或离线包 zst），按向导选 ESP-IDF v5.4.x 或 v5.5.x，安装路径保持纯英文（如 `D:\esp`）。
- **离线包（本机已采用）**：把 `esp-idf-v5.4.1.zip` / `esp-idf-v5.5.5.zip` 解压到 `D:\esp\v5.4.1`、`D:\esp\v5.5.5`，工具统一放 `D:\esp\tools`（`IDF_TOOLS_PATH`），先在每个版本目录里跑一次 `install.ps1` 装工具链。

**激活脚本（关键，每个新 PowerShell 窗口先跑这段）**——v5.4.1 激活示例（路径换成你的实际安装目录）：

```powershell
# --- 激活 ESP-IDF v5.4.1（请在纯英文路径窗口中执行；<你的 IDF 安装路径> 替换为实际目录）---
$env:IDF_PATH = '<你的 IDF 安装路径>\v5.4.1'
$env:IDF_TOOLS_PATH = '<你的工具目录>'  # 如 D:\esp\tools
# 国内镜像：组件注册表与组件文件存储走乐鑫中国 CDN
$env:IDF_COMPONENT_REGISTRY_URL = 'https://components.espressif.cn'
$env:IDF_COMPONENT_STORAGE_URL = 'https://components-file.espressif.cn'
# 首选方案：把工程放纯英文路径（如 D:\eb-build\my-device），ccache 崩溃 / gbk 解码 / ldgen 乱码这类中文路径错误大多能直接避免。
# 下面三行是"兜底开关"——仅当工程路径已确认纯英文、仍出现 ccache 崩溃或 gbk 解码错误时，才取消注释启用：
#   - IDF_CCACHE_ENABLE=0 会关闭 ccache、牺牲增量编译加速（每次接近全量重编），非首选；
#   - PYTHONUTF8=1 / PYTHONIOENCODING=utf-8 强制 Python 用 UTF-8，可解决中文 Windows 控制台默认 gbk 读 config.env 报错。
# $env:PYTHONUTF8 = '1'
# $env:PYTHONIOENCODING = 'utf-8'
# $env:IDF_CCACHE_ENABLE = '0'
. $env:IDF_PATH\export.ps1
```

macOS/Linux 等价（激活脚本换成 export.sh，环境变量写法相同）：

```bash
export IDF_PATH=~/esp/v5.4.1
export IDF_TOOLS_PATH=~/esp/tools
# 首选：工程放纯英文路径。以下为兜底开关，仅在纯英文路径下仍报 ccache 崩溃 / gbk 解码错误时取消注释启用：
# export PYTHONUTF8=1
# export IDF_CCACHE_ENABLE=0
. $IDF_PATH/export.sh
```

**多版本切换**：本机同时装了 v5.4.1 与 v5.5.5。切版本只需换 `IDF_PATH` 再重新 source（tools 共用同一目录也可，互不覆盖）：

```powershell
# 从 v5.4.1 切到 v5.5.5：
$env:IDF_PATH = '<你的 IDF 安装路径>\v5.5.5'
. '<你的 IDF 安装路径>\v5.5.5\export.ps1'
```

**验证激活成功**：

```powershell
idf.py --version                       # 应输出 ESP-IDF v5.4.1 或 v5.5.5
(Get-Command xtensa-esp32s3-elf-gcc).Source   # 应指向 <你的工具目录>\...下的 gcc
```

**建工程与编译（务必在纯英文路径）**：

```powershell
mkdir D:\eb-build; cd D:\eb-build
idf.py set-target esp32s3
idf.py build
idf.py -p COM4 flash        # 把 COM4 换成你自己的口
idf.py -p COM4 monitor      # 看串口日志，Ctrl+] 退出
```

> EasyInput V2.0 板提示：开机状态下**短按一次 BOOT** 进入下载模式，退出需关机重开；它没有独立 RESET 键，不要按"按住 BOOT 再上电"那套老板子流程。（仅参考案例板提示；你自己的板以 `docs/board-contract.json` 的 `boot.enter`/`boot.exit` 为准。）

### 3. Arduino IDE（esp32 开发板包 + 国内加速）

1. 从 arduino.cc 装 Arduino IDE 2.x。
2. 文件 → 首选项 → "附加开发板管理器网址"填入 jihulab 国内镜像索引：

```text
https://jihulab.com/esp-mirror/espressif/arduino-esp32/-/raw/gh-pages/package_esp32_index_cn.json
```

3. 工具 → 开发板 → 开发板管理器，搜 `esp32`，安装；**国内用户请选带 `-cn` 后缀的包版本**（自动更新对国内包不生效，需要升级时手动换版本号）。
4. 工具 → 开发板 选你的板（如 ESP32S3 Dev Module），端口选设备管理器里的 COM 口。

### 4. MicroPython（烧录固件 + mpremote/Thonny）

```powershell
# 用系统 Python（已勾"Add to PATH"）装工具
pip install esptool mpremote
# 1) 擦除整片 Flash（MicroPython 首次烧录前通常需要；日常重烧用下面 write_flash 覆盖即可，不必反复擦）
esptool --port COM4 erase_flash
# 2) 烧录固件（.bin 从 micropython.org 下载页选 ESP32-S3 对应型号）
esptool --port COM4 --baud 460800 write_flash 0x1000 ESP32_GENERIC_S3-xxxx.bin
# 3) 进 REPL（Ctrl-] 退出）
mpremote
mpremote repl
# 直接跑本地脚本、传文件
mpremote run main.py
mpremote fs cp main.py :main.py
```

macOS/Linux：把 `COM4` 换成 `/dev/ttyUSB0`（Linux）或 `/dev/cu.usbserial-*`（macOS），其余相同。

Thonny（图形化 REPL/文件管理器，新手友好）：从 thonny.org 下载 Windows 安装包，装好后 运行 → 选择解释器 → MicroPython (ESP32) → 选 COM 口。

### 5. PlatformIO（VSCode 插件）

1. VSCode 扩展市场搜 `PlatformIO IDE` 安装，重启。
2. 新建 Project：Board 选 `Espressif ESP32-S3 Dev Module`（espressif32 平台），Framework 选 Arduino。
3. 生成的 `platformio.ini` 关键内容：

```ini
[env:esp32-s3-devkitc-1]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino
monitor_speed = 115200
```

4. 点底部工具栏的 →（Build）、插头（Upload）、小虫子旁的串口图标（Serial Monitor）。

### 6. Node.js 24 + pnpm（WebSerial/前端工具备用）

```powershell
# 1) 从 nodejs.org 下载 LTS 安装包（当前 LTS 为 v24 线），一路下一步
node -v      # 应输出 v24.x
npm -v
# 2) 装 pnpm（npm 方式，Windows 官方推荐）
npm install -g pnpm
pnpm -v
# 3) 新建一个 WebSerial/上位机小工具时：
mkdir D:\projects\webserial-tool; cd D:\projects\webserial-tool
pnpm init
```

macOS/Linux：Node 用 `nvm install 24` 或官网 pkg；pnpm 用 `curl -fsSL https://get.pnpm.io/install.sh | sh -`。

## 可复制 AI 提示词模板

模板 A：环境体检（装完照着跑）

```text
我在 Windows 11 上按下面这份清单装 ESP32-S3 开发环境，请帮我写一份"环境体检"PowerShell 脚本（.ps1），逐项检查并打印 PASS/FAIL：① node -v 是否 v24、pnpm -v 是否存在；② 在我指定的 IDF_PATH（<你的 IDF 安装路径>）下 export.ps1 后 idf.py --version 能否输出；③ xtensa-esp32s3-elf-gcc 是否在 PATH；④ 列出当前所有 COM 口；⑤ 检查是否误把工程放在含中文/空格的路径。脚本要求：纯英文输出、出错不中断、最后汇总未通过项和修复命令。
```

模板 B：编译报错回贴排查（最常用）

```text
我在用 ESP-IDF 5.4.1 编译一个 ESP32-S3 工程，工程路径是 <你的项目目录（纯英文路径、无空格无中文）>。我已经做了这些环境设置：PYTHONUTF8=1、IDF_CCACHE_ENABLE=0、组件镜像走 components.espressif.cn。下面是 idf.py build 的完整报错日志（含最后 80 行）：
<粘贴报错>
我的板级合同（引脚/PSRAM/Flash/外设）见 docs/board-contract.json：
<粘贴板级合同要点>
请按"错误根因 → 证据 → 最小修复命令"三步回答；不要一次改五个地方，先给最可能的那一条。
```

模板 C：多版本切换脚本

```text
我电脑上同时装了 ESP-IDF v5.4.1（<你的 IDF 安装路径>\v5.4.1）和 v5.5.5（<你的 IDF 安装路径>\v5.5.5），工具目录都是 <你的工具目录>。请帮我写两个 PowerShell 脚本：activate-idf541.ps1 和 activate-idf555.ps1，各自设置好 IDF_PATH/IDF_TOOLS_PATH/组件镜像环境变量；PYTHONUTF8=1 与关闭 ccache 作为可选兜底（默认注释掉，并在注释里说明"仅在纯英文路径下仍报 gbk/ccache 错误时才打开，关 ccache 会牺牲增量编译加速"），然后 source 对应 export.ps1，最后打印当前版本与 gcc 路径。脚本要能在新开窗口里直接 `. .\activate-idf541.ps1` 使用，并提醒我两个脚本不要在同一窗口里连着 source。
```

模板 D：让 AI 熟悉你的板子再写代码

```text
接下来我们要在这块板上写固件，请先阅读我的板级合同文件 docs/board-contract.json（里面写了 SoC、模组 N16R8、PSRAM、引出脚分配、按键/LED/音频引脚、串口下载方式）。在写任何代码之前，先复述你对"哪些脚已被占用、哪些脚空闲、下载模式怎么进"的理解，跟我确认无误后再开始。
```

## 常见坑

1. **现象**：`idf.py build` 中途 ccache 进程崩溃/闪退，或报 `ccache.exe has stopped working`。**原因**：ccache 4.x 在含中文/空格路径下 `std::filesystem` 处理非 ASCII 路径有 bug——**中文路径是根因**。**解决**：首选——把整个工程（连同 IDF 本体与 tools）移到纯英文路径（如 `D:\eb-build\my-device`）再编译，这是正解。若路径已确认纯英文仍偶发 ccache 崩溃，再兜底关闭 ccache：`$env:IDF_CCACHE_ENABLE='0'`；注意这会牺牲 ccache 增量编译加速，非首选。
2. **现象**：CMake/kconfgen 阶段报 `UnicodeDecodeError: 'gbk' codec can't decode byte ...`。**原因**：中文 Windows 控制台默认 gbk，而 IDF 的 config.env 是 UTF-8；若工程/IDF 路径含中文会放大此问题。**解决**：首选仍是保证工程与 IDF/tools 路径纯英文；若路径已纯英文仍报 gbk 解码错误，再兜底强制 UTF-8——`$env:PYTHONUTF8='1'; $env:PYTHONIOENCODING='utf-8'` 后再 source export.ps1。
3. **现象**：链接器/ldgen 阶段报奇怪的中文路径乱码、找不到组件，或明明文件存在却说 not found。**原因**：ldgen 等 Python 脚本在含中文路径下读写文件路径乱码。**解决**：工程目录一律纯英文（`D:\eb-build`），不要放在桌面/中文用户目录下；IDF 本体与 tools 也保持纯英文（如 `D:\esp`）。
4. **现象**：`idf.py build` 卡在下载组件、`git clone` GitHub 超时、或组件注册表连不上。**原因**：GitHub 直连不稳。**解决**：激活时设置 `$env:IDF_COMPONENT_REGISTRY_URL='https://components.espressif.cn'` 与 `$env:IDF_COMPONENT_STORAGE_URL='https://components-file.espressif.cn'`；IDF/工具链安装包从 `dl.espressif.cn` 下，不要从 GitHub Releases 硬下。
5. **现象**：插上板子，设备管理器里没有 COM 口，或 COM 口带黄色感叹号。**原因**：串口芯片驱动没装（CP210x / CH340），或用了只能充电的 USB 线。**解决**：装对应驱动（见"资源与延伸"），换一根确认能传数据的 USB 线，拔插一次再看设备管理器。
6. **现象**：Arduino IDE 开发板管理器装 esp32 板包一直转圈/失败。**原因**：默认从 GitHub 拉包，国内慢。**解决**：首选项里把附加开发板管理器网址换成 jihulab 的 `-cn` 索引（见上文命令），安装时选带 `-cn` 后缀的版本；自动更新对国内包无效，升级手动改版本号。
7. **现象**：新开 PowerShell 跑 `idf.py` 报"无法将 idf.py 识别为 cmdlet"。**原因**：IDF 环境变量只在激活过的那个窗口有效。**解决**：每个新窗口先跑一次第 2 节的激活脚本（或把它存成 `activate-idf541.ps1` 每次 `. .\activate-idf541.ps1`）。
8. **现象**：PowerShell 跑 `. .\export.ps1` 报"在此系统上禁止运行脚本"。**原因**：默认执行策略 Restricted。**解决**：本次会话临时放开——`Set-ExecutionPolicy -Scope Process Bypass`，或用 `powershell -ExecutionPolicy Bypass -File activate-idf541.ps1`。

## 验收清单

- [ ] 串口驱动已装，设备管理器能看到板子的 COM 口并记下编号
- [ ] ESP-IDF v5.4.1（及 v5.5.5）已解压到纯英文路径（如 `D:\esp\`），tools 在独立纯英文目录
- [ ] 新窗口跑激活脚本后，`idf.py --version` 正常输出版本号
- [ ] `xtensa-esp32s3-elf-gcc` 在 PATH 中能找到
- [ ] 组件国内镜像已设置；工程与 IDF/tools 均在纯英文路径下；`PYTHONUTF8=1` / `IDF_CCACHE_ENABLE=0` 仅在纯英文路径下仍报 gbk/ccache 错误时作为兜底启用（非默认开启）
- [ ] 在纯英文路径（如 `D:\eb-build`）下完成过一次 `idf.py set-target esp32s3 && idf.py build` 成功
- [ ] Arduino IDE 已通过 jihulab 镜像装好 esp32 板包（-cn 版本），能选到 ESP32S3 Dev Module
- [ ] MicroPython 已能 `mpremote` 进 REPL（或至少 esptool 能识别芯片）
- [ ] VSCode 已装 PlatformIO 插件，能创建 esp32-s3 工程
- [ ] `node -v` 为 v24.x、`pnpm -v` 正常，且已建立 `docs/board-contract.json`（板级合同）供后续 AI 辅助开发阅读

## 资源与延伸

- ESP-IDF Windows 安装指南（中文，官方）：https://docs.espressif.com/projects/esp-idf/zh_CN/latest/esp32s3/get-started/windows-setup.html （官方）
- 乐鑫国内下载站（IDF/工具链离线包）：https://dl.espressif.cn （官方镜像）
- ESP 组件注册表（国际站）：https://components.espressif.com/ （官方）
- IDF Component Manager 配置（含中国 storage_url 说明）：https://docs.espressif.com/projects/idf-component-manager/en/latest/use/how_to_configuration.html （官方）
- Arduino-ESP32 安装文档（含 jihulab 国内镜像与 -cn 包说明）：https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html （官方）
- MicroPython ESP32 固件下载（按板子型号选 .bin）：https://micropython.org/download/ESP32_GENERIC/ （官方）
- mpremote 命令行文档：https://docs.micropython.org/en/latest/reference/mpremote.html （官方）
- Thonny 官方下载（MicroPython 图形 IDE）：https://thonny.org/ （官方）
- PlatformIO 官网（VSCode 插件）：https://platformio.org/ （官方）
- Node.js 下载（选 v24 LTS）：https://nodejs.org/en/download （官方）
- pnpm 安装文档：https://pnpm.io/installation （官方）
- Silabs CP210x USB 转串口 VCP 驱动：https://www.silabs.com/developer-tools/usb-to-uart-bridge-vcp-drivers （官方）
- 沁恒 CH340/CH341 Windows 驱动 CH341SER.EXE：https://www.wch.cn/downloads/CH341SER_EXE.html （官方）
- esptool 文档（ESP32-S3 烧录/擦除）：https://docs.espressif.com/projects/esptool/en/latest/esp32s3/ （官方）
