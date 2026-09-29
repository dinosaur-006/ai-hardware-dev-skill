# 08. 烧录及调试（Flashing & Debugging）

全流程的环节 08。固件在本机编译通过后，本环节把它真正"灌"进 ESP32-S3 板子，并通过串口日志确认它**真的在跑**。输入：07 环节编译出的固件（`build/*.bin`）、一根能传数据的 USB 线、一块已上电的板子；输出：烧录成功 + 串口能看到自己写的日志 + 区分清楚"编译过/烧录过/真在跑"三件事。

> 关键心态：**编译成功 ≠ 烧录成功 ≠ 固件正常运行**。这是三段独立证据，缺一不可，见常见坑第 3 条。

## 目标与通过标准

- 目标：用最短路径把固件烧进板子，并会用串口日志定位问题。
- 通过标准：
  - 设备管理器里能看到板子对应的 COM 口（Linux/macOS 下 `/dev/ttyUSB0` 或 `/dev/tty.usbserial-*`）。
  - `esptool flash_id` 能读出芯片型号和 Flash 容量。
  - `idf.py flash` 烧录过程不报错、校验通过。
  - `idf.py monitor` 能看到自己代码里 `ESP_LOGI` 打印的输出。
  - 已按板级合同（`<board-contract:boot.enter>` / `<board-contract:boot.exit>`）掌握本板进入/退出下载模式的正确操作，不照抄别板。

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

### 3. 烧录授权门禁（硬性，V3 评审重点）

> 这是写入设备前的**硬门禁**，不是建议。烧录是不可逆地改写片上 Flash，写错设备/写错固件/误擦都会丢数据或让设备变砖。任何 Agent（包括 AI）在执行真正的写入前，都必须先过这道门。

**(1) 烧录前必须先完整显示以下信息，一条都不能少：**

- 端口（如 `COM3` / `/dev/ttyUSB0`）
- 芯片型号（`esptool flash_id` 读出，应为 ESP32-S3）
- **完整 MAC 地址**（如 `AA:BB:CC:11:22:33`）
- 工程版本（固件 version / git commit，来自当前 build）
- 产物路径（将写入的 `build/*.bin` 完整路径）
- **将要执行的完整烧录命令**（`idf.py -p <端口> flash` 或等价 esptool 命令）

**(2) 停下等用户确认**：把上面信息摆出来后**停止写入动作**，等用户**原样输入** `确认烧录到 XXXX`（`XXXX` 为刚显示的完整 MAC）。只有收到与完整 MAC 逐字一致的确认串，才允许执行写入；没收到、或对不上 MAC，一律不写。

**(3) 默认不擦 Flash**：**无理由不执行 `erase_flash`**；不改分区表、不改偏移、不改设备身份（MAC/efuse/NVS 身份数据不动）。只有当用户明确给出理由（如怀疑旧分区/OTA 残留导致固件跑不起来）时，才允许擦除——且擦除是破坏性动作，必须先向用户说明后果并再次确认。

**(4) 失败后的唯一重试方式**：自动连接/烧录失败时，**唯一允许的实体操作是"保持开发板开机，短按并松开一次 BOOT"**，随后**只重试一次**；不要"按住 BOOT 再上电"，不要反复插拔，不要自行改波特率/改分区去"碰运气"。仍失败就停下，按常见坑排查并回报。

**(5) MAC 隐私纪律**：完整 MAC 只在当前这一轮对话里显示用于核对；写入项目记录（flow/日志/文档）时**只保留 MAC 后四位**，不要把完整 MAC 落盘。

**(6) 违反后果**：跳过任一环节（未显示全信息就写、没等确认就写、默认 erase、把完整 MAC 写进记录）即视为越权写入，本次烧录作废、流程重来；并对照本文件「验收清单」逐项打勾，缺项不予通过。

### 4. 烧录 + 监视（最常用一条命令）

```powershell
# 确保当前窗口已 source 过对应版本的 export.ps1
# 且已通过上面第 3 节"烧录授权门禁"拿到用户对完整 MAC 的逐字确认
idf.py -p COM3 flash monitor
```

macOS/Linux：

```bash
idf.py -p /dev/ttyUSB0 flash monitor
```

退出监视：`Ctrl + ]`（Windows/Linux），macOS 同样 `Ctrl + ]`。

> 想提高烧录速度可加波特率：`idf.py -p COM3 -b 460800 flash`。
> **擦除 Flash（`idf.py erase-flash`）不是默认动作**：仅在怀疑分区/OTA 残留、且经用户确认后才用；日常重烧直接 `flash` 即可（见第 3 节门禁第 (3) 条）。

### 5. 进入下载模式的正确姿势（按板级合同，别照别板）

**通用 ESP32-S3 方法**：绝大多数开发板有 BOOT 和 RESET 两个键，通用做法是按住 BOOT 不放 → 点一下 RESET → 松开 BOOT，板子进入 ROM 下载模式，esptool 即可连上。

**但通用法未必适用你的板**：具体进入/退出下载模式的动作**以板级合同为准**——
- 进入方式看 `<board-contract:boot.enter>`（开机状态下做什么动作、是否需要按住、是否需要配合重新上电）；
- 退出方式看 `<board-contract:boot.exit>`；
- 板上有没有独立 RESET 键看 `<board-contract:boot.independent_user_reset_button>`；
- 合同里 `legacy_hold_boot_during_power_on_forbidden` 为 true 的板，**禁止教/用"按住 BOOT 再上电"**。

> 具体动作值（进入/退出下载模式的按键动作、是否需要配合上电、有无独立 RESET 键等）只存在于 `docs/board-contract.json` 与 `board-reference.md`，本文不写死，避免板级事实重复。新板先建合同再照合同操作。

如果 `esptool` 一直 `Connecting....` 连不上，先按本板合同确认它确实处在下载模式，再重试（失败重试方式见第 3 节门禁第 (4) 条）。

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

**JTAG 调试入口（ESP32-S3 内置）**：ESP32-S3 原生 USB（对应板级合同 `usb` 段）内置 **USB-Serial/JTAG**，无需外接调试器。当 USB 枚举时随 COM 口一起出现一个 JTAG 调试接口（设备管理器里的 "USB JTAG/serial debug unit"）时，即可作为排障入口：挂断点、单步、看异常地址与 backtrace。具体用法见 11《故障排查》的 JTAG 小节。

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

### 9. JTAG 调试（ESP32-S3 内置 USB-Serial/JTAG 接口）

前面几节讲的是"烧录 + 串口日志"。当设备卡死、崩溃、日志看不出原因时，需要真正的调试：打断点、单步、看变量、看调用栈。ESP32-S3 **原生 USB 已内置 USB-Serial/JTAG 外设，不用外接调试器**，同一根 USB 线同时承担烧录与调试。

#### 9.1 一根 USB 线，两个通道

ESP32-S3 的原生 USB（对应板级合同 `usb` 段，直连芯片 D+/D-，不是板上经 USB-UART 芯片的那一路）上电后会**同时枚举出两个设备**：

- **USB-Serial 通道**：就是一个 COM 口（Windows 设备管理器里 `COMx`），负责烧录（esptool / `idf.py flash`）和日志（`idf.py monitor`）——即本文件第 0~6 节走的通道。
- **JTAG 调试通道**：设备管理器里另一个设备，名称类似 `USB JTAG/serial debug unit`（不带 COM 号，常落在"通用串行总线设备 / 调试设备"类别下），这是 OpenOCD / GDB 调试用的通道。

> 两个通道共存于同一根 USB 线，互不冲突：烧录时 JTAG 通道闲着，调试时串口日志仍可另开一个 monitor 看。**能烧录（看到 COM 口）不等于能调试**——如果设备管理器里只有 COM 口、没有那个 JTAG 调试设备，说明 JTAG 通道没枚举出来（插错口 / 缺驱动 / menuconfig 没开），OpenOCD 是连不上的。

#### 9.2 起调试服务器 + 连 GDB（最小步骤）

前提：已 `idf.py build`，且板子用 USB 线接到 ESP32-S3 的**原生 USB 口**。

```powershell
# 终端 A：起 OpenOCD 调试服务器（内置 JTAG 配置文件）
idf.py openocd
# 等价底层命令：openocd -f board/esp32s3-builtin.cfg
# 看到 "Listening on port 3333 for gdb connections" 即就绪，这个窗口保持开着
```

另开一个终端 B（同样 source 过对应版本 export.ps1）：

```powershell
# 终端 B：连到 OpenOCD 起 GDB，自动连上目标并加载符号、复位
idf.py gdb
```

VSCode 用户：装 ESP-IDF 扩展后用扩展自带的「Debug」配置（`.vscode/launch.json` 选 ESP-IDF 调试配置），本质仍是自动跑 openocd + `xtensa-esp32s3-elf-gdb`，可图形化打断点。

#### 9.3 断点 / 单步 / 看变量（GDB 常用命令速查）

进入 GDB 后（`(gdb)` 提示符）常用命令：

```text
(gdb) break main.c:120      # 在 main.c 第 120 行下断点（也可 break 函数名）
(gdb) monitor reset          # 复位目标板
(gdb) continue               # 全速运行，跑到断点停下
(gdb) next                   # 单步（不进入函数）
(gdb) step                   # 单步（进入函数内部）
(gdb) print cls              # 停下时看变量 cls 的值
(gdb) print/x x              # 以十六进制看 x
(gdb) bt                     # backtrace：看当前调用栈（崩溃/卡死定位神器）
(gdb) info threads           # 看 FreeRTOS 任务（线程）列表
(gdb) thread 2               # 切到某个任务上下文，再 print 它的变量
(gdb) delete 1               # 删掉 1 号断点
(gdb) quit                   # 退出（提示时选 y）
```

程序停在断点那一行后，`print 变量名` 就能看到该时刻的真实值——这正是"打一堆 printf 才猜得到"的问题用 JTAG 一眼看穿的原因。

#### 9.4 排障用途：卡死 / 崩溃时看调用栈

设备"跑着跑着不动了、也不打印日志"时 attach 上 GDB：

- `bt` 看调用栈：卡在哪个函数、哪一层调用链，立刻知道是死循环、等信号量等不到、还是卡在某个驱动里。
- `info registers` / `print/x $pc` 看寄存器与程序指针，判断 CPU 到底停在哪。
- 配合 `info threads` 看哪个任务占着、谁被饿死——据此区分是**固件逻辑问题**（调用栈能指向你的代码）还是**硬件/供电/总线问题**（栈停在 ROM 下载态或读外设卡死、反复复位）。

#### 9.5 和烧录通道的区分（一句话记住）

| 动作 | 走哪个通道 | 命令 |
| --- | --- | --- |
| 烧录固件 | USB-Serial（COMx） | `idf.py -p COMx flash` / esptool |
| 看日志 | USB-Serial（COMx） | `idf.py -p COMx monitor` |
| 调试（断点/单步/看变量） | JTAG 调试通道 | `idf.py openocd` + `idf.py gdb` |

烧录与调试是同一根 USB 线上的**两个独立通道**：能 `flash` 成功说明 Serial 通道通，不代表 JTAG 通道也通；调试连不上先回 9.1 看设备管理器里那个 JTAG 设备在不在。官方文档：ESP-IDF 编程指南「JTAG 调试」（OpenOCD 安装、`esp32s3-builtin.cfg`、GDB 调试范例），https://docs.espressif.com/projects/esp-idf/zh_CN/stable/esp32s3/api-guides/jtag-debugging/index.html 。

## 可复制 AI 提示词模板

模板 A：烧录失败诊断（贴 esptool 输出）

```text
我在 Windows PowerShell 下用 <idf.py flash / esptool.py> 烧录 ESP32-S3，命令是：<粘贴完整命令>。
报错原文：
<粘贴 esptool 完整输出，尤其是 Connecting failed / A fatal error occurred / Hash of data does not match>
我的板子是 <板名>，下载模式进/退方式以板级合同为准：<粘贴 board-contract.json 的 boot.enter / boot.exit / independent_user_reset_button 字段>。
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

模板 D：JTAG 调试引导（贴 openocd/gdb 输出）

```text
我在 Windows 下用 ESP32-S3 原生 USB 调试：已经 idf.py build 成功，idf.py -p COMx flash 也能正常烧录。
现在跑 idf.py openocd 报错 / 或 idf.py gdb 连不上。报错原文：<粘贴 openocd / gdb 完整输出>。
设备管理器里看到的是：<是否只看到 COMx，有没有那个 "USB JTAG/serial debug unit" 设备>。
请按"JTAG 通道有没有枚举出来 → 驱动 → OpenOCD 配置文件 esp32s3-builtin.cfg → gdb 连 3333 端口"的顺序排查，并告诉我接下来在 (gdb) 里用哪几条命令看崩溃调用栈。注意：我知道能烧录不等于能调试，不要让我反复重烧。
```

## 常见坑

1. **现象**：插上板子没 COM 口，或设备管理器里带黄色感叹号。**原因**：没装 CP210x/CH340 驱动，或用了只能充电的 USB 线。**解决**：装对应串口驱动，换一根能传数据的线，插主板后置 USB 口。
2. **现象**：esptool 一直 `Connecting....____` 连不上、最终 timeout。**原因**：板子不在下载模式。**解决**：按本板板级合同 `<board-contract:boot.enter>` 进入下载模式（具体进/退动作以 `docs/board-contract.json` 为准，别板别照抄）；连不上时按门禁第 (4) 条只重试一次，不要"按住 BOOT 再上电"。
3. **现象**：`idf.py flash` 显示 hash 校验通过，但一上电就重启 / 乱码 / 没日志。**原因**：把"烧录成功"当成了"固件正常"。烧录只证明 bin 写进了 Flash，运行还取决于分区表、flash 模式、供电、代码本身。**解决**：按三段证据排查——编译（build 无 error）→ 烧录（esptool hash matched）→ 运行（monitor 有预期日志）。**不要默认 `erase-flash`**；仅在怀疑旧分区/OTA 残留时，先说明后果并经用户确认后再擦（见第 3 节门禁）。
4. **现象**：烧录中途报 `A fatal error occurred: Flash read failed` 或校验错误、写一半失败。**原因**：供电不足（USB 口带不动 PSRAM 全速烧写）或 flash 模式配错（qio/dio 与实际 Flash 不匹配）。**解决**：换主板后置 USB 口/短线；`menuconfig → Serial Flasher Config → Flash mode` 改 `DIO` 试一次。
5. **现象**：构建/烧录脚本报路径乱码、ccache 崩溃，或 Python 报 `UnicodeDecodeError: 'gbk'`。**原因**：工程在中文路径下；Windows Python 默认 gbk。**解决**：工程放到纯英文路径如 `D:\eb-build`；执行 `$env:PYTHONUTF8=1` 后再烧录。
6. **现象**：`add-dependency` / 拉 esptool / clone 仓库一直超时。**原因**：国内直连 GitHub 不稳。**解决**：组件用 `$env:IDF_COMPONENT_REGISTRY_URL="https://components.espressif.cn"`；IDF 二进制走 `https://dl.espressif.cn`。
7. **现象**：monitor 里全是乱码。**原因**：串口波特率与固件日志波特率不一致。**解决**：把 monitor 波特率设为 115200（menuconfig 里日志默认波特率），两边对齐。
8. **现象**：`idf.py openocd` 报找不到设备 / 连不上 JTAG，但 `idf.py flash` 烧录完全正常。**原因**：JTAG 通道没枚举出来——线插在了板上 USB-UART 口而非 ESP32-S3 原生 USB 口，或缺 JTAG 调试驱动，设备管理器里只有 COM 口、没有那个 `USB JTAG/serial debug unit`。**解决**：设备管理器确认同时有 `COMx` 和一个 JTAG 调试设备；USB 线要插在 ESP32-S3 原生 USB 口（直连 D+/D-），别插经 USB-UART 芯片的那一路；装齐 IDF 自带驱动后拔插一次。
9. **现象**：GDB 里 `break main.c:行号` 下了断点，但程序不停在断点。**原因**：固件编译优化级别太高把行号 / 函数内联掉了；或烧录走的 Serial 通道和调试目标对不上（gdb 加载的 elf 与刚烧的 bin 不是同一次 build）。**解决**：`menuconfig → Compiler options` 把优化调到 `-Og`（调试期）后重新 build + flash；确认 gdb 加载的是本次 `build/` 下同一个 elf，别混着旧 build 目录。

## 验收清单

- [ ] 设备管理器（或 `/dev`）里能看到板子对应的串口
- [ ] CP210x/CH340 驱动已装，换过数据线确认不是充电线问题
- [ ] `esptool.py --port COMx flash_id` 能读出 ESP32-S3 型号与 Flash 容量
- [ ] 已按板级合同（`<board-contract:boot.enter>`/`<board-contract:boot.exit>`）掌握本板下载模式进/退操作，未照抄别板
- [ ] **已过烧录授权门禁**：烧录前显示了端口/芯片/完整 MAC/工程版本/产物路径/完整命令，并等到用户逐字输入"确认烧录到 <完整 MAC>"才写入
- [ ] 本次烧录**未执行 erase_flash**（除非有用户确认的理由），未改分区/偏移/设备身份
- [ ] 项目记录里 MAC 只留了后四位，完整 MAC 未落盘
- [ ] `idf.py -p COMx flash` 烧录校验通过（hash matched）
- [ ] `idf.py monitor` 能看到自己代码里 `ESP_LOGI` 打印的预期日志
- [ ] 能区分编译成功 / 烧录成功 / 运行正常三段证据，并用它定位过一次问题
- [ ] 工程在纯英文路径、`$env:PYTHONUTF8=1` 已设，国内镜像已配置
- [ ] 知道 monitor 退出键是 `Ctrl + ]`
- [ ] 设备管理器里能同时看到 `COMx`（烧录/日志）和 `USB JTAG/serial debug unit`（JTAG 调试）两个设备
- [ ] `idf.py openocd` 能看到 "Listening on port 3333 for gdb connections"，`idf.py gdb` 能连上目标
- [ ] 已用 JTAG 在自己代码里设过一次断点、用 `print` 看过一次变量值、用 `bt` 看过一次调用栈
- [ ] 清楚烧录走 USB-Serial（COMx）、调试走 JTAG，且能烧录 ≠ 能调试

## 资源与延伸

- ESP-IDF 编程指南（烧录、分区表、monitor 章节，中文官方文档）：https://docs.espressif.com/projects/esp-idf/zh_CN/stable/ （官方）
- esptool 官方文档（擦除/烧录/下载模式/排错）：https://docs.espressif.com/projects/esptool/ （官方）
- 乐鑫国内下载站（GitHub 慢时镜像）：https://dl.espressif.cn/ （官方镜像）
- 小智 AI 语音助手（含新手免环境烧录固件指南，可对照参考）：https://github.com/78/xiaozhi-esp32 （GitHub）
