# 11. 故障排查（Troubleshooting）

全流程的"安全网"。前面任何环节（硬件焊接 / 固件逻辑 / 软硬件联调）出现"不亮 / 不响 / 连不上 / 一直重启"时，回到本环节用分层法定位。输入：一个具体症状 + 串口日志；输出：定位结论 + 修复 + 一条沉淀进故障库的"现象→原因→解决"。

## 目标与通过标准

- 目标：建立"分层排查 + 日志驱动 + 证据纪律"的排障习惯，而不是瞎猜瞎换。
- 通过标准：
  - 遇到问题能按"电源→时钟/复位→引脚/外设→固件逻辑→协议/网络"逐层排查，知道每层用什么手段。
  - 能看懂串口日志的关键行：`rst:0x...` 复位原因、`Guru Meditation Error`、`Backtrace`。
  - 能区分"编译通过 / 烧录成功 / 日志正常 / 真机表现对"四件事，不互相冒充。
  - 每次排障结论沉淀成一条"现象→原因→解决"。

## 可复制操作与命令

### 分层排查法（从硬到软，逐层排除）

| 层 | 怀疑什么 | 怎么查 |
| --- | --- | --- |
| 1 电源 | 没供电 / 电压不对 / USB 线只充电不传数据 | 万用表测 3V3-GND；换一根数据线；看设备管理器有没有新串口 |
| 2 时钟/复位 | BOOT 状态错、boot loop、brownout | 上电第一行日志的 `rst:0x...` / `boot:0x...`；EN 引脚 |
| 3 引脚/外设 | 接错脚、电平不匹配、虚焊 | 万用表测 GPIO 静态电平；对照板子丝印；换个脚试 |
| 4 固件逻辑 | 空指针、栈溢出、死循环、看门狗 | IDF Monitor 看 Guru Meditation / backtrace；二分注释代码 |
| 5 协议/网络 | 串口乱码、WiFi 2.4G/BLE 连不上 | 核对波特率；连手机热点排除路由；看串口有没有数据 |

### 第一步永远是：插串口看日志

PowerShell（ESP-IDF 终端环境里）：

```powershell
idf.py -p COM3 monitor
```

macOS/Linux：

```bash
idf.py -p /dev/ttyUSB0 monitor
```

上电瞬间前几行最关键：

```text
rst:0x1 (POWERON_RESET),boot:0x8 (SPI_FAST_FLASH_BOOT)
...
cpu_start: ESP-IDF v5.x
```

- `rst:0x...` 是复位原因；`Guru Meditation Error` 后面括号里是异常类型；`Backtrace:` 下一行 `app_main at xxx.c:行号` 通常就是元凶。
- 看到崩溃后无限重启，先在 menuconfig 里把 panic 行为改成"打印后暂停"，让日志停下来。

### 二分法定位固件问题

怀疑某段代码导致崩溃/卡死时：

1. 把 `app_main` 后半段注释掉，只留点灯 + 串口打印，烧录看是否正常。
2. 一半一半地恢复代码，直到崩——bug 就在刚恢复的那一半里。

PowerShell 里快速看最近改了什么：

```powershell
git diff --stat
git log --oneline -5
git diff HEAD~1
```

macOS/Linux 相同。**新现象先怀疑自己最近的改动**：上一个 commit 能不能跑？能就是这次引入的。

### 日志级别与关键点打印

```powershell
idf.py menuconfig
# Component config -> Log output -> Default log verbosity -> Debug
```

关键路径加打印（ESP-IDF 自带时间戳）：

```c
ESP_LOGI(TAG, "btn pressed i=%d v=%d", i, v);
ESP_LOGW(TAG, "wifi retry %d", retry_count);
ESP_LOGE(TAG, "i2s write failed: %d", err);
```

怀疑两个模块之间卡住时，在中间插 `ESP_LOGI(TAG, "reach A")` / `"reach B"`，看日志停在哪一行。

### 把日志喂给 AI

不要只截图。复制**从上电到复现问题之间的完整文本日志**，连同下面"模板 A"一起贴给 AI；只贴最后一行它无从下手。

### 串口乱码时先核对波特率与串口号

```powershell
Get-PnpDevice -Class Ports | Where-Object {$_.Status -eq 'OK'} | Select-Object FriendlyName
```

板子默认日志 115200；板子改了波特率而 monitor 没改，就是乱码。

## 可复制 AI 提示词模板

模板 A：日志喂 AI（最常用）

```text
我在做一个 ESP32-S3（ESP-IDF）硬件项目，串口 monitor 输出如下，设备在 <描述现象，如：开机 3 秒后自动重启>。请帮我分析：
1. rst 复位原因是什么、属于哪一类（上电/看门狗/异常/软复位）；
2. Guru Meditation Error 的类型和大概在哪一行；
3. backtrace 里哪个函数最可疑；
4. 给出下一步排查建议（具体到加哪条日志/查哪个配置）。
先给结论和假设，不要直接改代码。
日志原文：
"""
<粘贴从上电到复现的完整日志>
"""
我最近的改动：<git diff 或口头描述>
```

模板 B：现象描述模板（硬件类问题）

```text
我遇到这个硬件症状：
- 板子型号：<EasyInput V2.0 / 其他，SoC=ESP32-S3>
- 现象：<上电后灯不亮 / 设备管理器没有串口 / GPIO 量出来是 0V 而我期望 3.3V / 等>
- 已经试过：<换数据线 / 换 USB 口 / 重新烧录 / 万用表量过 3V3=X.XV>
- 本来期望：<它应该怎样>
请按"电源→时钟复位→引脚→固件→协议"五层，每层列出检查清单，写明"怎么测、测出来说明什么"。我是新手，<有/没有>示波器，请标注哪些需要示波器。
```

模板 C：硬件 vs 软件二分（不知道是哪边的问题）

```text
我的设备出现：<如：WS2812 不亮 / I2S 无声 / 按键按了没反应>。我不确定是硬件接线问题还是固件代码问题。请给我一个"二分法"排查方案：
1. 怎么用最小固件（不依赖我的业务逻辑）单独验证硬件本身好坏；
2. 怎么用 PC 端 mock 数据 / 串口手动发命令单独验证固件逻辑；
3. 两个测试分别过了/没过的四种组合，各自说明问题在哪、下一步做什么。
```

## 常见坑

1. **现象**：上电完全没反应，灯不亮、设备管理器也没串口。**原因**：USB 线是充电线（无数据芯）、只接了 5V 没接 GND、电源开关没开。**解决**：换一根确定能传数据的 USB 线；量 3V3 对 GND 电压；EasyInput V2.0 确认开关拨到 ON。
2. **现象**：USB 插电脑出现未知设备 / 黄色感叹号，或串口时有时无。**原因**：外挂串口芯片（CH340/CP210x）驱动没装；前置 USB 口供电不稳。**解决**：在设备管理器看硬件 ID 装对应驱动；换主板后置 USB 口。
3. **现象**：`idf.py flash` 一直失败，报 "Failed to connect to ESP32-S3"。**原因**：没进下载模式；串口被占；波特率太高。**解决**：EasyInput V2.0 开机状态下短按一次 BOOT 进入下载模式（退出需关机重开，不要"按住 BOOT+上电"）；关掉其他占串口的程序；降低烧录波特率。
4. **现象**：GPIO 量出来一直是 0V 或 3.3V 不动。**原因**：脚没配成输出、被其他外设占用、量错脚。**解决**：先 `gpio_set_direction` + `gpio_set_level` 翻转，用最小例程验证；对照板子丝印和引脚图。
5. **现象**：按键按下去串口完全没事件。**原因**：没开内部上拉/下拉、消抖缺失。**解决**：`gpio_pullup_en` 内部上拉，代码加 20ms 消抖；万用表量按下/松开时引脚电平是否在 0/3.3V 间跳。
6. **现象**：WS2812 不亮，或颜色红绿蓝错位。**原因**：数据线接错脚、WS2812 是 5V 信号 3.3V 识别不了、RGB 顺序配错。**解决**：换确认过的 GPIO；确认供电；把 LED 顺序在 GRB/RGB 之间切换试。
7. **现象**：I2S 没声音，或有爆音/杂音。**原因**：BCLK/LRCK/DIN 三线接错、采样率不匹配、音量为 0、DMA buffer 太小。**解决**：对照解码板丝印三线逐一核对；采样率用 16000/44100 试；先烧官方 i2s 例程确认硬件。
8. **现象**：I2S 麦克风（INMP441 类）读出来全是 0 或固定值。**原因**：SCK/WS/SD 接错、L/R 使能脚拉错、时钟没出来。**解决**：量 SCK 引脚有没有跳变；确认 SD 接对、使能脚电平正确。
9. **现象**：WiFi 连不上一直失败。**原因**：路由是 5GHz（ESP32-S3 只支持 2.4GHz）、密码错、路由开了 MAC 过滤、信号弱。**解决**：连 2.4GHz 热点；核对密码；先用手机热点排除路由问题。
10. **现象**：BLE 手机扫不到 / 连不上。**原因**：广播没开、手机蓝牙缓存、被其他 App 占着。**解决**：代码确认 `esp_ble_gap_start_advertising`；重启手机蓝牙；在系统蓝牙里"忽略此设备"再重连。
11. **现象**：开机后反复重启（boot loop），日志无限循环打印 boot。**原因**：panic 后自动重启、app 分区损坏、电源带不动 brownout。**解决**：menuconfig 把 panic 改成"打印后暂停"，让日志停下来看 backtrace；查日志里有没有 brownout 提示。
12. **现象**：日志出现 `Task watchdog got triggered` / 看门狗复位。**原因**：某任务循环跑太久没喂狗、在 ISR 里做长事。**解决**：找出挂死任务；长循环里 `vTaskDelay(1)` 让出 CPU；ISR 只做最少事。
13. **现象**：串口打印全是乱码。**原因**：波特率不匹配（最常见）、日志走了错误 UART。**解决**：两边都设 115200；确认 monitor 的波特率参数。
14. **现象**：浏览器 WebSerial 连不上板子（弹窗没设备 / 报错）。**原因**：串口被其他工具占用、浏览器不是 Chrome/Edge、页面不是 https/localhost。**解决**：关掉 IDF Monitor/Serial Studio；用 Chrome/Edge；本地用 localhost 打开页面。

## 验收清单

- [ ] 遇到问题时第一反应是插串口看日志，而不是瞎换线/瞎重烧
- [ ] 能看懂上电前几行的 `rst:0x...` 复位原因
- [ ] 遇到 Guru Meditation 能指出 backtrace 第一行对应的函数/文件/行号
- [ ] 能用二分法把崩溃定位到"刚加的那一半代码"
- [ ] 能用 `git diff` / `git log` 定位"上一个能跑"的版本
- [ ] 清楚区分：编译通过 ≠ 烧录成功 ≠ 日志正常 ≠ 真机表现对
- [ ] 日志级别能调到 Debug，关键路径加了 `ESP_LOGx` 打印
- [ ] 至少沉淀了 3 条自己遇到的"现象→原因→解决"进故障库
- [ ] 硬件类问题先用最小例程验证硬件，再怀疑业务代码

## 资源与延伸

- ESP-IDF Fatal Errors 官方文档（Guru Meditation / backtrace / 看门狗含义）：https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-guides/fatal-errors.html （官方）
- Web Serial API（MDN，英文，WebSerial 排障对照）：https://developer.mozilla.org/en-US/docs/Web/API/Web_Serial_API （官方文档）
- Web Bluetooth API（MDN，中文，BLE 排障对照）：https://developer.mozilla.org/zh-CN/docs/Web/API/Web_Bluetooth_API （官方文档）
- Serial Studio（看日志/波形工具）：https://github.com/Serial-Studio/Serial-Studio （GitHub）
