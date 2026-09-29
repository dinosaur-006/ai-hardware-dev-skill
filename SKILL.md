---
name: ai-hardware-dev
version: 3.1.0
description: 零基础 AI 硬件开发全流程指引 + 项目执行系统（AI 辅助开发/vibecoding）。覆盖选型、画板、烧录、联调、排障到产品化闭环，含需求翻译、项目状态、决策留痕、失败知识库与多角色团队模式。用于自制 AI 硬件（"我要做产品"）、从零画板、烧录、软硬件联调、硬件排障、选型、查项目进度、决策留痕、失败沉淀；可单独调用子环节（只烧录/只联调/只画板）。EasyInput V2.0 仅为参考案例板。
---

# ai-hardware-dev：零基础 AI 硬件开发全流程指引

## 定位

面向"零基础 + AI 辅助开发（vibecoding）"用户与 AI Agent 的硬件开发导航包：让 Agent 在用户用 Trae / 豆包 / Claude Code / Codex / DeepSeek Harness 等工具写代码的前提下，按正确顺序、用正确事实、走完整流程开发 AI 硬件产品。

- **板级无关**：本 Skill 主体是通用方法论 + MCU 级 AI 硬件主线知识（Level1 ESP32-S3 入门 → Level2 STM32+NPU → Level3 树莓派 → Level4 Jetson）。`board-reference.md` 提供参考案例板（EasyInput V2.0）的完整事实，以及"给新开发板建立板级知识合同"的方法——买到任何新板都先建合同，Agent 再开发。
- **全流程闭环**：12+ 个环节各有一份独立参考文件（见"文件清单"），每份都含：目标与通过标准、可复制命令/操作（Windows 优先）、可复制 AI 提示词模板、常见坑、验收清单。
- **可单独调用**：每个环节文件自包含，用户只烧录、只联调、只画板时，直接读对应文件即可，不必走完全程。
- **项目执行系统**（V2）：`core/` 目录提供跨环节系统能力——项目状态（`core/project-state.md`，AI 主动维护 project-memory.json）、决策记录（`core/decision-record.md`）、失败知识库（`core/failure-knowledge-base.md`）、AI 团队多角色模式（`core/ai-hardware-team.md`）；需求翻译层（`references/00-product-translator.md`）负责"人话→工程规格"。

## 入口路由

先判断用户意图，再只读所需文件（不要一次全读）：

| 用户意图（示例表述） | 读这些文件 |
| --- | --- |
| "想做个 AI 硬件 / 帮我定方向 / 从哪开始" | `references/00-direction-and-definition.md` |
| "我有个想法但不清楚要什么硬件 / 人话转工程规格" | `references/00-product-translator.md`（需求翻译层） |
| "选开发板 / 选芯片 / 这个模型跑不跑得动" | `references/01-platform-selection.md` + `board-reference.md` |
| "我要做产品"（从想法到交付全程） | `core/ai-hardware-team.md`（多角色团队模式）+ 按环节推进 |
| "装环境 / 装不上 / 报错了" | `references/02-environment-setup.md` |
| "画原理图 / 帮我画板 / 改电路" | `references/03-schematic-design.md` |
| "先在面包板试试 / 画板前先搭原型 / 接线方案行不行" | `references/03a-breadboard-prototype.md` |
| "PCB 布局 / 布线 / 打样前检查" | `references/04-pcb-layout.md` |
| "打样 / 买元器件 / BOM" | `references/05-manufacturing-and-sourcing.md` |
| "焊接 / 焊完上电没反应" | `references/06-soldering-and-hardware-debug.md` |
| "写固件 / 跑 AI 模型 / 推理 / 驱动外设" | `references/07-firmware-ai.md` + `board-reference.md` |
| "烧录 / 下载固件 / 烧不进去" | `references/08-flashing-and-debugging.md` |
| "电脑和板子通信 / 联调 / WebSerial / BLE" | `references/09-software-hardware-integration.md` |
| "做外壳 / 电池 / 认证 / 产品化" | `references/10-productization.md` |
| "板子出问题了 / 排查 / 不工作" | `references/11-troubleshooting.md` + `core/failure-knowledge-base.md`（排障后沉淀） |
| "现在项目到哪了 / 当前状态 / 下一步做什么" | `core/project-state.md`（project-memory.json） |
| "为什么选这个芯片 / 这个方案怎么定的 / 决策留痕" | `core/decision-record.md` |
| "训练营资料 / 课程内容" | `references/camp-notes.md` |
| "不知道从哪开始" | 从 `references/00` 开始，按流程顺序推进；遇到哪一步卡住就读哪一步的文件 |
| 任何涉及具体板的引脚 / BOOT / 电源 / 外设事实 | 先读 `board-reference.md`（含新板建合同方法） |

**执行顺序约定**：完整流程建议按 00→（需求翻译 00b）→01→02→03→（03a 面包板原型）→04→…→11 推进，但每一环都可单独进入；进入任何涉及硬件的环节前，先确认板级事实（`board-reference.md`）。启动任何项目时，先按 `core/project-state.md` 初始化 project-memory.json 并持续维护。

## 项目目录布局（唯一权威）

本 Skill 全包所有落盘约定一律以本节为准；其他文件若出现不同的项目路径写法（如早期版本的 `project-state/`），以本节为准并回头更新对应文件。你的项目根目录下采用如下标准结构：

```
你的项目目录/
├── docs/
│   ├── project-memory.json        # 项目状态（唯一）
│   ├── product-contract.md        # 产品合同（00 产出）
│   ├── board-contract.json        # 板级知识合同（唯一事实源）
│   ├── failure-knowledge-base.md  # 失败知识库（跨项目沉淀）
│   └── decisions/                 # 决策记录（DRV-*.md，唯一）
├── firmware/                      # 固件工程
├── hardware/                      # 原理图/PCB/打样文件
└── scripts/                        # 校验脚本（ai-hardware-dev/scripts/ 复制或引用）
```

- 项目状态、决策、板级合同、失败知识库全部落在 `docs/` 下，不存在第二套状态目录；`project-state/handoff.md`、`project-state/decision-record.md` 等旧写法已废弃——流转进度与验收更新进 `docs/project-memory.json`，关键决策落 `docs/decisions/DRV-*.md`。
- 固件工程落 `firmware/`，原理图 / PCB / BOM / 打样文件落 `hardware/`，可复用的校验、激活脚本放 `scripts/`（从本 Skill 包的 `scripts/` 目录复制或直接引用）。
- JSON 内部所有路径字段一律相对项目根目录书写（如 `docs/product-contract.md`、`docs/decisions/DRV-001-xxx.md`）。

## 全流程工作流（12 环节 + 需求翻译总览）

| 环节 | 文件 | 通过标准（该环节验收） |
| --- | --- | --- |
| 00 方向确定与产品定义 | `references/00-direction-and-definition.md` | 有 product-contract.md：一句话、场景、功能、非目标、可检验验收 |
| 00b 需求翻译（人话→工程规格） | `references/00-product-translator.md` | 需求翻译表：功能拆解、硬件映射、优先级、未确定项 |
| 01 平台/芯片选型 | `references/01-platform-selection.md` | 一行选型结论（四级分级 Level 1-4）+ 板子内存/Flash/引脚够跑 MVP |
| 02 环境搭建 | `references/02-environment-setup.md` | 能在 Windows 上编译并烧录一个 hello/blink 工程 |
| 03 原理图设计 | `references/03-schematic-design.md` | 原理图通过 ERC，AI 防幻觉检查表逐项 PASS，BOM 可导出 |
| 03a 面包板原型验证（先验证再画板） | `references/03a-breadboard-prototype.md` | 最小接线方案在面包板上跑通核心功能，迁移清单核对后再进 PCB |
| 04 PCB 布局布线 | `references/04-pcb-layout.md` | DRC 零错误，AI 防幻觉检查表逐项 PASS，Gerber 可导出 |
| 05 打样与元器件采购 | `references/05-manufacturing-and-sourcing.md` | 下单并收到 PCB 与元件，BOM 核对无误 |
| 06 焊接与硬件调试 | `references/06-soldering-and-hardware-debug.md` | 上电各电源轨正常，外设逐一验证 |
| 07 固件开发（含 AI 推理） | `references/07-firmware-ai.md` | 外设驱动可用；模型量化后能推理出预期结果 |
| 08 烧录与调试 | `references/08-flashing-and-debugging.md` | 固件烧录成功并能在日志中看到运行证据 |
| 09 软硬件联调 | `references/09-software-hardware-integration.md` | 板端事件能到电脑端、电脑命令能控制板端 |
| 10 产品化 | `references/10-productization.md` | 有外壳方案、电源方案、认证路径与成本估算 |
| 11 故障排查 | `references/11-troubleshooting.md` | 按分层法定位到根因并修复 |

## 板级无关规则（Agent 必须遵守）

1. **开发任何板之前，先拿到该板的板级事实**：参考案例板直接读 `board-reference.md`；新板先按其中"新板板级知识合同方法"建立合同（引脚、BOOT、电源域、外设）。
2. **不把 EasyInput V2.0 的事实当通用事实**：EasyInput 只是参考案例；GPIO 编号、BOOT 操作、电源域设计在新板上必须重新核对（合同为准）。
3. **不把其他项目/教程的默认值当该板真值**：引脚、BOOT 流程、电源顺序以板级合同为准，通用教程只作线索。

## 通用工作纪律（Agent 必须遵守）

- **证据分级，禁止冒充**：编译通过 ≠ 烧录成功 ≠ 日志正常 ≠ 真机验收通过。回答与交付时必须说清结论属于哪一级证据。
- **真机验收优先**：硬件行为最终以真机表现为准；静态检查通过只说明"未见已建模冲突"。
- **涉及动作先确认**：擦除 Flash、批量改文件、发布等动作先向用户说明影响再执行。
- **命令与链接要真实**：命令以各环节文件为准；链接必须是官方/已验证来源，不编造 URL。
- **AI 辅助开发分工**：Agent 负责按文件执行、把报错与日志喂给自己排查；产品方向、功能取舍等决策由用户拍板。
- **项目状态维护纪律**：启动项目即按 `core/project-state.md` 创建 project-memory.json；每完成一个环节的验收清单后，AI 必须更新 current_stage、decisions_made、undecided、risks、verification_log，并在回复里列出本次更新的差异。关键选型/方案决策按 `core/decision-record.md` 留痕；每次排障后按 `core/failure-knowledge-base.md` 结构化沉淀。

## 边界（本 Skill 不负责）

- 不替用户做产品方向与功能取舍决策（00 环节只提供方法与模板）。
- 不保证认证合规：认证以官方机构当日要求为准（见 10 环节）。
- 不代替真机验证：所有"验收"都要用户实际执行并反馈结果。
- 不维护 EasyInput 板级事实的第二真相源：EasyInput V2.0 的板级合同以其参考仓库的 `board-contract.json` 为权威副本（本机绝对路径不写入本包），本包 `board-reference.md` 只摘录要点。

## 禁止事项

- 对 EasyInput V2.0：不教"按住 BOOT + 上电"；不把 GPIO8 当成只控制灯带的普通 IO；不把 GPIO0 当成普通按键。
- 不在本包内复制 easyinput-board-cy / easyinput-drum-machine 的正文（引用其路径即可）。
- 不编造芯片规格、命令、提示词模板或链接；写不出的写"以官方文档为准"。
- 不写入隐私信息（open_id、手机号、微信号、个人地址）。

## 完成标准（一次完整开发交付前确认）

- 12 个环节各自的验收清单已逐项通过或明确记录未过项。
- 板级事实来自板级合同而非猜测；新板已建立合同。
- project-memory.json 已存在且当前阶段、决策、风险、验证记录为最新；关键决策有 decision-record 留痕。
- 最终交付物（固件/板子/外壳/文档）有真机验证证据或明确标注"未真机验证"。
- 产物含 LICENSE / NOTICE 声明（训练营资料仅限非商业使用）。

## 文件清单与加载指引（渐进披露）

只加载当前任务需要的文件；每个文件 150-400 行，可整读或用关键词定位。

- `board-reference.md` — 参考案例板 EasyInput V2.0 事实 + 新板建合同方法（涉及任何板的事实前必读）
- `prompt-templates.md` — 各环节可复制 AI 提示词模板汇总（找提示词时读）
- `resources.md` — 分类资源清单：官方文档 / GitHub / 中文社区 / 训练营（找资料时读）
- `scripts/` — 可复用校验脚本（环境体检、多版本切换等）；使用时复制或引用到项目的 `scripts/` 目录
- `core/project-state.md` — 项目状态系统：project-memory.json 模板 + 每环节更新纪律（启动项目必读）
- `core/decision-record.md` — 决策记录：关键选型/方案取舍留痕模板（做决策时读）
- `core/failure-knowledge-base.md` — 失败知识库模板：症状/概率原因/验证/解决/次数（排障后沉淀时读）
- `core/ai-hardware-team.md` — AI 硬件团队多角色模式：PM→硬件架构→电气→固件→QA→制造（"我要做产品"时读）
- `references/00-direction-and-definition.md` — 方向确定与产品定义
- `references/00-product-translator.md` — 需求翻译层：人话→工程规格（00 之后、01 之前）
- `references/01-platform-selection.md` — MCU 级 AI 硬件主线选型（Level1 ESP32-S3 入门 → Level2 STM32+NPU → Level3 树莓派 → Level4 Jetson；含成本反推：目标售价→BOM 目标价→选型约束）
- `references/02-environment-setup.md` — 环境搭建（ESP-IDF / Arduino / MicroPython / PlatformIO / Node.js）
- `references/03-schematic-design.md` — 原理图设计（立创EDA / KiCad；含电路安全设计：反接/过流/ESD/看门狗 + 轻量 FMEA）
- `references/03a-breadboard-prototype.md` — 面包板原型：先在面包板验证最小接线方案，再画 PCB（V3 新增）
- `references/04-pcb-layout.md` — PCB 布局布线（含 DFM 可制造性设计 + 预合规滤波预留）
- `references/05-manufacturing-and-sourcing.md` — 打样与元器件采购（嘉立创等；含 DFM 下单衔接）
- `references/06-soldering-and-hardware-debug.md` — 焊接与硬件调试（含锂电池安全与热失控 FMEA）
- `references/07-firmware-ai.md` — 固件开发（含 TFLite Micro / ESP-DL / Edge Impulse AI 推理；含 OTA 固件升级与版本管理）
- `references/08-flashing-and-debugging.md` — 烧录与调试（esptool / idf.py / Arduino / WebSerial；含 JTAG 调试：内置 USB-Serial/JTAG + OpenOCD/gdb）
- `references/09-software-hardware-integration.md` — 软硬件联调（WebSerial / WebBluetooth / 协议）
- `references/10-productization.md` — 产品化（3D 打印外壳 / 电源 / 认证；含 OTA 设备管理 / 预合规摸底 / 量产成本反推）
- `references/11-troubleshooting.md` — 故障排查（分层排查 + 故障库；含安全类故障：看门狗/过流/ESD/锂电池）
- `references/camp-notes.md` — 训练营资料速览（WaytoAGI 第七期 AI 硬件基础训练营）
