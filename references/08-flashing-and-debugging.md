# 08. 烧录与调试（Flashing & Debugging）

全流程的环节 08。固件编译通过（07 验收）后，把它烧进板子并确认真机行为。**铁律：烧录前必须过"烧录授权门禁"（人类在环确认），烧录不等于完成，日志正常才算数**。输入：`idf.py build` 通过的固件；输出：真机上跑起来的固件 + 一份烧录/启动日志证据。

> **证据分级：编译通过 ≠ 烧录成功 ≠ 日志正常 ≠ 真机验收。** 本环节完成的标准是：烧录成功 + monitor 日志正常（无 panic）+ 最小自检代码在真机通过。

## 目标与通过标准

- 目标：把 07 的固件安全地烧进板子，用串口 monitor 确认启动日志正常，并用最小自检代码验证外设真机行为。
- 通过标准：
  - 烧录前完成"烧录授权门禁"全部 6 项（见下），且获得用户对烧录目标（端口 + 芯片 + 完整 MAC）的原样确认。
  - `idf.py -p COMx flash` 成功，esptool 校验通过（Hash of data verified）。
  - `monitor` 启动日志正常：无 Guru Meditation / 无反复重启 / 无 bootloader panic；能看到自己的启动打印。
  - 最小自检代码（LED 闪 / 串口打印 / 按键响应）在真机通过。
  - 不默认执行 `erase_flash`：仅在"有理由才擦、且与用户再次确认后果"后执行。

## 可复制操作与命令

### 8.1 烧录授权门禁（硬性，6 项逐条）

> 为什么要有门禁：esptool/`idf.py flash` 会**写设备身份区（efuse 附近区域外的 flash 分区）、覆盖 NVS/校准数据**。烧错板子或烧错分区不可逆。训练营第 2 课也要求烧录前人工确认（见 `camp-notes.md` 模板 5）。**以下 6 项缺一不可，违反任一项 = 越权写入，立即作废重来。**

1. **烧录前完整展示**：端口（`COMx`）、芯片型号（esptool 读出的 chip 型号，如 ESP32-S3）、**完整 MAC 地址**、工程版本（`idf.py --version` + 工程 commit/版本）、产物路径（`build/my-device.bin` 等）、完整烧录命令。
2. **停下等用户确认**：展示后**必须停下**，等用户**原样输入"确认烧录到 XXXX"（XXXX = 完整 MAC 地址）**，一字不差才允许写入。
3. **不默认擦除**：无充分理由不执行 `erase_flash`；确需擦除（如改分区表）必须先向用户说明后果（NVS/校准/设备身份被清）并**再次确认**后才擦。不修改分区/偏移/设备身份。
4. **失败重试纪律**：烧录失败时，唯一允许的操作是"保持开机状态**短按一次 BOOT**（以板级合同 `boot.enter` 为准）"，最多重试一次；**不按住 BOOT+上电、不反复插拔、不改波特率**。仍失败则停下报障（见 11 排障）。
5. **MAC 隐私**：完整 MAC 只在当前对话中显示；任何落盘文件（日志、报告）只写**后四位**。
6. **记录留痕**：烧录完成后，在 `docs/flash-log.md` 记录：时间、端口、芯片、MAC 后四位、固件版本、命令、结果；不记录完整 MAC。

### 8.2 烧录（ESP-IDF）

```powershell
# 激活环境（02 环节激活脚本）后，进入工程目录（纯英文路径）
cd D:\eb-build\my-device
# 查看当前配置与目标
idf.py --version
idf.py set-target esp32s3
# 烧录（把 COMx 换成你的口；烧录前先过 8.1 门禁！）
idf.py -p COMx flash
# 只看烧录/启动日志（Ctrl+] 退出）
idf.py -p COMx monitor
# 编译+烧录+日志一条龙（日常用）
idf.py -p COMx flash monitor
```

**烧录失败常见输出**：`Connecting........_____.....` 卡住（下载模式没进对）、`A fatal error occurred: Failed to connect to ESP32-S3`（端口错/驱动/进错模式）、`Hash of data does not match`（flash 校验失败，重新烧）。

### 8.3 擦除（仅在"有理由才擦"时用，先过门禁第 3 条）

```powershell
# 整片擦除（会清 NVS/校准/设备身份；除非改分区表/全新板首次 MicroPython，否则不要用）
esptool -p COMx erase_flash
# 只擦某个分区（更保守，如只擦 NVS）：
# esptool -p COMx erase_region 0x9000 0x5000
```

### 8.4 串口 monitor 日志解读

| 日志特征 | 含义 | 下一步 |
| --- | --- | --- |
| `rst:0x1 (POWERON_RESET)` | 上电复位，正常 | 继续看启动 |
| `rst:0x5 (DEEPSLEEP_RESET)` / `rst:0x10 (RTCWDT)` | 深睡唤醒 / RTC 看门狗 | 查睡眠配置/看门狗 |
| `rst:0x6 (TG1WDT_SYS_RESET)` | 任务看门狗复位 | 查死循环/低优先级任务饿死 |
| `rst:0x9 (SW_CPU_RESET)` | 软件复位 | 查重启代码路径 |
| `Guru Meditation Error: Core 0 panic'ed` + backtrace | 运行时崩溃 | 按 11 环节模板 A 喂 AI 分析 backtrace |
| `E (xxx) spi_flash: ...` | flash 读写错误 | 查分区表/Flash 模式 |
| `W (xxx) boot: ...` | bootloader 警告 | 按警告内容查（如分区重叠） |
| 启动后**没有任何自己的打印** | 固件没跑起来/烧错分区 | 确认 flash 命令与分区表 |

### 8.5 最小自检代码（烧录后确认外设真机工作）

烧录 Hello World 后，逐步加：

1. LED 闪（点亮 500ms）→ 板上 LED 可见。
2. 串口每 2s 打印 `alive` + 当前 uptime → monitor 可见。
3. 按键按下打印 `btn pressed` → 触发成功。
4. 逐个外设（麦克风/功放/传感器）打印其读数 → 真机确认。

每加一个，烧录一次、真机验证一次；**证据分级如实记录：编译通过 / 烧录成功 / 日志正常 / 真机验收** 分别记到 `docs/flash-log.md` 与 `project-memory.json` 的 verification_log。

### 8.6 JTAG / USB-Serial-JTAG 排障入口

ESP32-S3 内置 USB-Serial/JTAG 控制器（原生 USB，D-/D+ 即 GPIO19/20）：

- 串口不可用时，可尝试用 JTAG 方式读取芯片：`idf.py -p COMx monitor` 失败时，检查是否被其它程序占用串口；
- OpenOCD 配 ESP32-S3 可做断点/单步调试（进阶），零基础先用串口日志即可；
- USB-Serial/JTAG 同时提供 CDC 串口，板子枚举出的 COM 口既是日志口也可烧录；驱动异常时先卸载/重装 USB 设备再枚举。

## 可复制 AI 提示词模板

模板 A：烧录失败诊断（T6 全模板）

```text
我在 Windows PowerShell 下用 <idf.py flash / esptool.py> 烧录 ESP32-S3，命令是：<粘贴完整命令>。
报错原文：
<粘贴 esptool 完整输出，尤其是 Connecting failed / A fatal error occurred / Hash of data does not match>
我的板子是 <板名>，下载模式进/退方式以板级合同为准：<粘贴 board-contract.json 的 boot.enter / boot.exit / independent_user_reset_button 字段>。
请按"端口/驱动 → 下载模式 → 供电/线 → 分区与 flash 模式 → 固件本身"的顺序，列出最可能的 3 个原因和对应验证命令，不要让我瞎试。
```

模板 B：串口日志解读（T3 全模板）

```text
我的 ESP32-S3 固件烧录成功了（esptool 校验通过），但 monitor 里看到的是：
<粘贴 monitor 日志，包括 Guru Meditation / Backtrace / panic / W (xxx) boot: 这些行>
请帮我判断：这是启动早期 panic（bootloader/分区/flash 配置问题）还是运行时崩溃（代码/内存问题）？根据 Backtrace 给出定位思路，并告诉我每条关键日志是什么意思。
```

模板 C：最小自检代码生成

```text
我的 ESP32-S3 固件已能烧录、monitor 能看到启动日志。请按"最小自检"顺序给我代码：① LED 闪烁；② 每 2 秒串口打印 alive+uptime；③ 按键按下打印事件；④ 逐个外设打印读数（麦克风/功放/传感器）。每段代码注释里标注"引脚以板级合同为准：<粘贴你的 board-contract 引脚>"，并说明每步烧录后应在 monitor 里看到什么。
```

## 常见坑

1. **现象**：`Connecting........_____` 永远连不上。**原因**：没进下载模式，或端口/线不对。**解决**：按板级合同 `boot.enter` 操作（参考板：开机状态短按一次 BOOT）；换数据线；看设备管理器端口。
2. **现象**：`Failed to connect`，但设备管理器有 COM 口。**原因**：驱动装错/端口被占用（monitor 没退出）。**解决**：关掉其它占用串口的程序；重新插拔；装对应驱动（02 环节）。
3. **现象**：烧录成功后 monitor 一直重启循环（rst 原因变化）。**原因**：固件 panic、看门狗、电源不稳（AI 负载时 LDO 瞬态不够会 brownout，见 11 环节）。**解决**：按 8.4 表查 rst 原因；喂 11 模板 A 给 AI；查电源/去耦。
4. **现象**：烧录成功但启动日志里没有任何自己的打印。**原因**：烧错分区/固件没运行/串口波特率错。**解决**：确认 flash 命令与分区表；`idf.py monitor` 用默认 115200；检查 app 起始分区。
5. **现象**：想擦除重烧却把 NVS/校准数据清了。**原因**：默认执行 erase_flash。**解决**：本包纪律：不默认擦除，有理由才擦且先确认（门禁第 3 条）；只擦目标分区更保守。
6. **现象**：MAC 地址出现在日志/报告文件里。**原因**：没守 MAC 隐私纪律。**解决**：落盘只写后四位（门禁第 5 条）。

## 验收清单

- [ ] 烧录前已过烧录授权门禁 6 项（展示端口/芯片/完整 MAC/版本/产物/命令 → 用户原样确认 → 不默认擦除 → 失败重试纪律 → MAC 隐私 → 记录留痕）
- [ ] `idf.py -p COMx flash` 成功，esptool 校验通过（Hash of data verified）
- [ ] `monitor` 启动日志正常：无 Guru Meditation、无反复重启、无 bootloader panic
- [ ] 最小自检代码 ①-④ 逐条真机通过（LED/打印/按键/外设读数）
- [ ] 未默认执行 erase_flash；确需擦除已先说明后果并获再次确认
- [ ] `docs/flash-log.md` 已记录（含 MAC 后四位，无完整 MAC）
- [ ] verification_log 已按证据分级回填（编译通过/烧录成功/日志正常/真机验收）

## 资源与延伸

- esptool 官方文档（烧录/擦除/排错）：https://docs.espressif.com/projects/esptool/ （官方）
- esptool ESP32-S3 专页（S3 烧录细节）：https://docs.espressif.com/projects/esptool/en/latest/esp32s3/ （官方）
- ESP-IDF 编程指南（分区表/monitor/错误处理）：https://docs.espressif.com/projects/esp-idf/zh_CN/stable/ （官方）
- ESP-IDF Fatal Errors 文档（Guru Meditation/backtrace 含义）：https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-guides/fatal-errors.html （官方）
- 训练营第 2 课（12 步烧录跑通 + 原文烧录授权提示词模板）：https://waytoagi.feishu.cn/wiki/OVQ5wz57uiFD0hkutgFcpasFntc （训练营）
