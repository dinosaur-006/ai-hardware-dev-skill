# 板级参考（board-reference）

本文件有两部分：**① 参考案例板 EasyInput V2.0 的板级事实速览**；**② 新开发板板级知识合同（board-contract）方法**——后者是本包的真正核心：买到任何新板，先按下面的 JSON 模板建一份 `docs/board-contract.json`，AI 才有一份可靠的"该板事实源"可用。

> ⚠️ 重要：**EasyInput V2.0 只是参考案例板**。GPIO 编号、BOOT 操作、电源域设计在新板上必须重新核对，以你自己板的 `docs/board-contract.json` 为准，不要照抄本文件（本文件第 3 条坑也专门强调）。

## 一、参考案例板：EasyInput V2.0 板级事实速览

以下事实来自 EasyInput 参考仓库的 `board-contract.json`（权威副本，本文件只摘录要点）。**这些不是 ESP32-S3 的通用事实。**

| 项目 | 值 | 说明 |
| --- | --- | --- |
| SoC | ESP32-S3（双核 240MHz，向量指令 SIMD） | 通用 ESP32-S3 能力 |
| 模组 | ESP32-S3-WROOM-1 **N16R8**（16MB Flash + 8MB PSRAM，八线） | 通用模组规格；GPIO 引出以合同为准 |
| 原生 USB | 有：D- = GPIO19，D+ = GPIO20（USB-Serial/JTAG） | 通用 ESP32-S3 原生 USB 引脚 |
| 下载模式进入 | 开机状态下**短按一次 BOOT**（板上无独立 RESET 键） | **本板特定**，新板以合同 `boot.enter` 为准 |
| 下载模式退出 | 关机重开 | **本板特定**，新板以合同 `boot.exit` 为准 |
| GPIO8 | 5V/3.3V 电源域共享开关（控制 WS2812 灯带等 5V 外设供电） | **本板特定**，不是普通 GPIO；新板以合同 `pins` 为准 |
| GPIO0 | BOOT 键（下载模式切换） | **本板特定**，不是普通按键；新板以合同 `boot` 为准 |
| Strapping | GPIO3/GPIO45/GPIO46 保留（上下拉已按手册处理） | 通用规则：Strapping 引脚不接普通外设 |
| 串口 | USB-Serial/JTAG 枚举出 COM 口（115200 默认日志） | 通用 ESP32-S3 |
| 供电 | USB 5V / 锂电池 + TP4056 充电管理 | 本板方案 |

## 二、新板板级知识合同方法（给任何新开发板建合同）

### 为什么必须有合同

AI 最容易犯的错是**一本正经地错**：问"GPIO0 怎么接"，普通 AI 会说"GPIO0 通常是 boot"然后直接输出。但不同板（ESP32 / ESP32-S3 / ESP32-C3 / 自研板）的 BOOT 操作、引脚分配、电源域完全不同。**板级合同就是把"该板事实"外置成结构化 JSON，AI 只读合同，不猜。**

### 合同 JSON 模板（复制到 `docs/board-contract.json`）

```json
{
  "schema_version": 1,
  "board_name": "<板名，如 EasyInput V2.0>",
  "aliases": ["<别名，如训练营叫法>"],
  "soc": "<SoC，如 ESP32-S3>",
  "module": "<模组，如 ESP32-S3-WROOM-1-N16R8>",
  "psram": "<PSRAM 容量，如 8MB>",
  "flash": "<Flash 容量，如 16MB>",
  "antenna": {
    "type": "<PCB 天线 / 外置天线>",
    "keepout_note": "<天线净空要求，按模组手册>"
  },
  "pins": {
    "<功能名>": "<GPIO 编号，如 GPIO8>",
    "...": "..."
  },
  "power": {
    "input": "<供电方式，如 USB 5V / 锂电池 + TP4056>",
    "vcc_3v3_regulator": "<LDO 型号>",
    "power_up_settle_time_ms": null,
    "power_up_settle_time_ms_evidence": "unknown_requires_qualification"
  },
  "boot": {
    "enter": "<进入下载模式操作，如 power_on_short_press_boot_once>",
    "exit": "<退出下载模式操作>",
    "independent_user_reset_button": <true/false>,
    "legacy_hold_boot_during_power_on_forbidden": true
  },
  "usb": {
    "dplus_gpio": "GPIO20",
    "dminus_gpio": "GPIO19",
    "native_usb_serial_jtag": true
  },
  "led": {
    "<LED 功能名>": "<GPIO 编号>"
  },
  "battery": {
    "type": "<无 / 锂电池 + TP4056 等>",
    "charging_ic": "<充电管理 IC，如 TP4056>"
  },
  "audio": {
    "mic": "<麦克风型号/接口>",
    "amp": "<功放型号/接口>",
    "speaker": "<喇叭规格>"
  },
  "debug_uart0": "<串口引脚与波特率，如 GPIO43/44 115200>",
  "reserved": ["<保留引脚列表>"]
}
```

**填写规则（防幻觉）**：

1. **引脚用功能名做键、GPIO 编号做值**：如 `"boot_button": "GPIO0"`，不要用 GPIO 编号做键。
2. **资料里没有的信息填 `null`**，并在字段旁注明原因（如 `"unknown_requires_qualification"`）；**绝不猜**。
3. **不要用 EasyInput 或其他板的引脚替你猜测**——新板必须从产品页、原理图、丝印照片实测得来。
4. `legacy_hold_boot_during_power_on_forbidden` 必须为 `true`（现代板一律禁止"按住 BOOT 再上电"旧操作），除非你确认你的板确实需要旧操作。
5. 建完合同后，跑 `scripts/check_board_contract.py` 校验（见 scripts/README.md）。

### 建合同四步

1. **收集资料**：产品页规格、引脚图、原理图要点、丝印照片描述。
2. **让 AI 起草**：用下方"模板 A"让 AI 按上面 JSON schema 起草合同。
3. **实测核对**：上电后逐项核对（BOOT 进/退操作、LED 引脚、串口枚举），把实测结果写回合同（见"模板 B"）。
4. **跑校验脚本**：`python scripts/check_board_contract.py docs/board-contract.json`，PASS 后再让 AI 开发。

## 三、可复制 AI 提示词模板

**模板 A：起草新板合同**

```text
我新买了一块开发板 <板名>，这是它的资料：
<粘贴产品页规格 / 引脚图 / 原理图要点 / 丝印照片描述>
请按以下 JSON schema 起草一份 board-contract.json（字段：schema_version/contract_id/aliases/soc/psram/flash/antenna/pins/power/boot/usb/led/battery/audio/debug_uart0/reserved），
要求：① 引脚用功能名做键、GPIO 编号做值；② 资料里没有的信息填 null 并在字段旁注明"资料缺失，需实测"；③ 不要用 EasyInput 或其他板的引脚替我猜测。
```

**模板 B：实测验证清单**

```text
我已为 <板名> 起草了 docs/board-contract.json。请给我一份"实测验证清单"：上电后我要逐项测并回填哪些字段（BOOT 进/退、LED/按键引脚、串口枚举、供电方式），每项怎么写进 JSON。我按清单实测后回来更新合同。
```

**模板 C：合同与文档冲突处理**

```text
我的板级合同 docs/board-contract.json 写着 <字段>，但我实际测试发现 <现象>，两者不符。请帮我：① 判断哪个更可信（实测为准）；② 给出合同更新建议；③ 检查是否还有其他字段可能受影响。
```

## 四、常见坑

1. **现象**：AI 写代码时把 GPIO8 当普通 GPIO 用。**原因**：没读合同，把 EasyInput 事实当通用事实。**解决**：写任何代码前让 AI 先读 `docs/board-contract.json`（模板见 02 环节 D）。
2. **现象**：新板 BOOT 操作按旧教程"按住 BOOT 再上电"，死活进不了下载模式。**原因**：不同板 BOOT 操作不同。**解决**：以合同 `boot.enter` 为准；合同没写就先实测补上再开发。
3. **现象**：AI 问 GPIO0 怎么接，直接回答"GPIO0 通常是 boot"。**原因**：模型把旧知识当事实。**解决**：AI 必须先读合同；合同没有的字段，答案是"该板合同未记录，需实测"，不是猜。
4. **现象**：合同里字段全是猜的值，板上电后对不上。**原因**：起草时没遵守"未知填 null"规则。**解决**：严格按填写规则 2/3；实测后再把 null 替换成真值。
5. **现象**：把 EasyInput 的电源域设计（GPIO8 开关）抄到自研板。**原因**：参考案例被当成了模板。**解决**：自研板的电源域按自己的原理图设计，合同如实记录；EasyInput 只作思想参考。

## 五、验收清单

- [ ] 新板已建 `docs/board-contract.json`（字段齐全、未知填 null 并注明原因）
- [ ] 已跑 `scripts/check_board_contract.py` 校验 PASS
- [ ] BOOT 进/退操作已实测并写入合同
- [ ] 引脚分配已与原理图/丝印核对
- [ ] 未把 EasyInput V2.0 的事实当通用事实（全包可检索验证）

## 六、资源与延伸

- EasyInput 参考仓库（board-contract.json 权威副本）：本地参考素材（easyinput-board-cy 仓库），本机绝对路径不写入本包
- ESP32-S3 引脚分配表（官方数据手册）：https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf （官方）
- 乐鑫 ESP32-S3 硬件设计指南（引脚/电源/天线）：https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/ （官方）
