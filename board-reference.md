# 板级参考：EasyInput V2.0 参考案例 + 新板板级知识合同方法

本文件服务于"板级无关"原则：第一部分是参考案例板（EasyInput V2.0）的板级事实速览，仅作为示例；第二部分是"如何为任何新开发板建立板级知识合同"，让你和 Agent 拿到新板也能正确开发。

**铁律**：任何板的事实（引脚、BOOT、电源域、外设）以该板的板级合同为准；EasyInput 的事实**不是**通用 ESP32 事实，新板必须重新核对。

## 第一部分：参考案例板 EasyInput V2.0（板级事实速览）

> 权威副本与完整证据：`D:\硬件耍耍\Waytoagi\easyinput-board-cy\references\board-contract.json`（含字段级证据），配套 `easyinput-board-cy` Skill。以下为要点摘录，冲突时以权威副本为准。

### 身份

| 项 | 值 |
| --- | --- |
| 产品/课程名 | EasyInput V2.0 |
| 固件板型别名 | v2（大写 V2） |
| PCB 丝印 | AI Keyboard V2.1 |
| SoC | ESP32-S3R8（QFN56） |
| PSRAM | 8MB，八线 SPI（Octal），封装内 |
| Flash | 16MB（W25Q128 系列，片外） |
| 天线 | PCB 天线 |

以上三个名称指向同一块硬件基线，不是三套电气设计。

### 引脚合同（要点）

| 资源 | 引脚 | 说明 |
| --- | --- | --- |
| 按键 S1–S8 | GPIO 2, 47, 38, 41, 1, 6, 7, 48 | 低有效；GPIO0 不是 S5 |
| 编码器 A/B/按压 | GPIO 17 / 16 / 18 | 正交相位，不是两个普通按键 |
| LED/MIC/SPK 共享电源域 | GPIO8（高有效，PWR_EN） | 见"电源合同" |
| WS2812 ×5 | GPIO12（串联数据脚） | 5 颗共用一个数据脚 |
| 原生 USB | GPIO19 / 20 | |
| 麦克风（I2S） | GPIO9 / 10 / 11 | |
| 扬声器（I2S/MAX98357A） | GPIO14 / 13 / 15 | |
| UART0 调试 | GPIO44 / 43 | |
| 状态 LED | GPIO42 | |
| 电池检测 | GPIO5（使能）/ GPIO4（ADC，分压 2.0）/ GPIO40（外电检测）/ GPIO39（充电状态） | |
| 唤醒 | GPIO21 | 聚合唤醒，唤醒后重扫输入 |

### BOOT 操作（本板独有，勿照抄别的板）

- 开机状态下，**短按并松开一次 BOOT** 即进入下载模式。
- 不需要按住 BOOT，不需要配合重新上电；**不教"按住 BOOT + 上电"**。
- 退出下载模式只需关机重开；板上**没有**独立 RESET/EN 键。

### 电源合同（不可破坏）

- GPIO8 是高有效的 LED/MIC/SPK 共享电源域。先锁存下游安全状态，再拉高 GPIO8；使用外设前确认电源稳定。
- 已知未知项：统一最短稳定时间**未被证明**，需按器件规格或实测确认，不引用其他项目的延时值。
- 睡眠/关断共享电源域前，先让所有共享消费者停止并恢复安全引脚状态。

## 第二部分：新板板级知识合同方法（买到新板怎么用）

目标：花 30-60 分钟把新板的关键事实固化成 `board-contract.json`（+ 简述 md），让任何 Agent 开发前先读合同，而不是按通用 ESP32 教程猜。

### 建合同四步

1. **收集事实**，按优先级：
   - 板卡官方资料：产品页规格、官方原理图/引脚图、数据手册（芯片级）
   - 实物核对：PCB 丝印、板面走线、跳线/拨码
   - 实测验证：万用表量电源轨、实测 BOOT 行为、串口枚举
2. **填写合同模板**（见下节 JSON schema；也可让 AI 代填，用"提示词模板"）
3. **实测验证关键项**：电源轨电压、BOOT 进入/退出方式、关键外设引脚是否与文档一致——**以实测为准，写进 `verified_at` 与证据说明**
4. **版本化存放**：放入项目 `references/board-contract.json`，随项目走；后续新证据（勘误、批次差异）更新版本并记录被取代关系

### 合同模板（JSON，字段借鉴 EasyInput 合同）

```json
{
  "schema_version": 1,
  "contract_id": "<板名-日期>",
  "scope": "hardware_only_no_application_defaults",
  "verified_at": "<YYYY-MM-DD>",
  "aliases": {
    "product": "<产品名>",
    "firmware_board_alias": "<固件别名>",
    "pcb_silkscreen": "<丝印>"
  },
  "soc": { "model": "<如 ESP32-S3R8>", "package": "<封装>" },
  "psram": { "bytes": 8388608, "interface": "octal_spi", "voltage_v": 3.3 },
  "flash": { "family": "<如 W25Q128>", "bytes": 16777216 },
  "antenna": "pcb",
  "pins": {
    "<功能名>": { "gpio": <编号>, "active_level": 0, "signal": "<网络名>", "silkscreen": "<丝印>" }
  },
  "power": {
    "gpio": <电源使能脚>, "active_level": 1,
    "power_up_settle_time_ms": null,
    "power_up_settle_evidence": "unknown_requires_qualification",
    "shared_consumers": ["<共享该电源的外设列表>"]
  },
  "boot": {
    "gpio": 0,
    "enter": { "initial_state": "powered_on", "action": "<如 tap_boot_once>", "hold_required": false, "power_cycle_required": false },
    "exit": { "action": "<如 power_off_then_on>", "boot_press_required": false },
    "independent_user_reset_button": false,
    "legacy_hold_boot_during_power_on_forbidden": true
  },
  "usb": { "controller": "<esp32s3_native_usb 等>", "dn_gpio": <>, "dp_gpio": <> },
  "encoder": { "a_pin": "<名>", "b_pin": "<名>", "press_pin": "<名>" },
  "led": { "data_pin": "<名>", "pixel_count": <>, "color_order": "GRB" },
  "battery": { "sense_enable_pin": "<名>", "sense_adc_pin": "<名>", "voltage_divider": 2.0, "fuel_gauge_present": false },
  "audio": {
    "microphone": { "bclk_pin": "<名>", "ws_pin": "<名>", "data_in_pin": "<名>" },
    "speaker": { "bclk_pin": "<名>", "ws_pin": "<名>", "data_out_pin": "<名>" }
  },
  "debug_uart0": { "rx_pin": <>, "tx_pin": <> },
  "reserved": { "<保留脚>": "<原因，如 flash_psram_bus>" }
}
```

说明：`pins` 中的"名"是全文件统一的引用键（如 `KEY1`、`LED_DIN`），值里放 GPIO 编号；`power`/`boot` 这类安全关键项必须显式写清"已知/未知"，未知就写 `null` + 原因，**不猜**。

### 可复制 AI 提示词模板

模板 A：让 AI 起草新板合同

```text
我新买了一块开发板 <板名>，这是它的资料：
<粘贴产品页规格 / 引脚图 / 原理图要点 / 丝印照片描述>
请按以下 JSON schema 起草一份 board-contract.json（字段：schema_version/contract_id/aliases/soc/psram/flash/antenna/pins/power/boot/usb/led/battery/audio/debug_uart0/reserved），
要求：① 引脚用功能名做键、GPIO 编号做值；② 资料里没有的信息填 null 并在字段旁注明"资料缺失，需实测"；③ 不要用 EasyInput 或其他板的引脚替我猜测。
```

模板 B：新板实测验证清单

```text
我为 <板名> 建立板级合同后，需要实测验证。请给我一份实测清单：① 用万用表测哪些电源轨、期望电压多少；② BOOT/下载模式怎么实测进入与退出；③ 哪些外设引脚需要逐一验证、怎么验证（串口枚举/示波器/逻辑分析仪）；④ 每项实测结果应记入合同的哪个字段。
```

模板 C：冲突处理（文档与实物不符）

```text
<板名> 的板级合同里，<某引脚/某行为> 文档写的是 <A>，但我实测/看到的丝印是 <B>。请帮我判断：以哪个为准、为什么，以及是否需要更新合同并记录被取代关系（按证据优先级：硬件负责人确认 > 当前批次资料 > 打包原理图 > 合同文件 > 项目声明 > 通用教程）。
```

### 常见坑

1. **现象**：按通用 ESP32 教程猜新板引脚。**原因**：同一芯片不同板引脚天差地别。**解决**：先建合同，引脚一律查合同。
2. **现象**：BOOT 操作照抄 EasyInput（短按一次）。**原因**：EasyInput 是该板独有行为。**解决**：新板按自己的文档/实测确定 BOOT 流程，写入合同。
3. **现象**：忽略共享电源域/使能脚，外设上电顺序错。**原因**：只查了数据手册没查板级电源设计。**解决**：合同里必须有 `power` 段，外设使用前先满足电源合同。
4. **现象**：文档缺信息就按"最像 ESP32 常规做法"猜。**原因**：怕留空。**解决**：未知就写 `null` + "资料缺失，需实测"，绝不猜。
5. **现象**：合同建完不复测，后来实物与文档不符导致排查半天。**原因**：把文档当真值。**解决**：关键项（电源轨、BOOT、外设引脚）必须实测后写 `verified_at`。

### 验收清单

- [ ] 已收集该板官方资料（产品页/原理图/数据手册）
- [ ] `board-contract.json` 已按模板填写，缺失项显式标"需实测"
- [ ] 电源轨电压已用万用表实测并记录
- [ ] BOOT 进入/退出方式已实测并写入合同
- [ ] 关键外设引脚已核对（丝印/实测）
- [ ] 合同已放入项目 `references/board-contract.json` 并填写 `verified_at`
- [ ] 已知未知项（如电源稳定时间）已显式记录，未猜值
- [ ] Agent 开发前已按合同核对引脚与安全边界

## 参考来源

- EasyInput V2.0 板级权威副本：`D:\硬件耍耍\Waytoagi\easyinput-board-cy\references\board-contract.json`（本地，含字段级证据与验证日期）
- 配套 Skill：`D:\硬件耍耍\Waytoagi\easyinput-board-cy\SKILL.md`（身份/BOOT/电源合同/证据优先级/禁止事项）
