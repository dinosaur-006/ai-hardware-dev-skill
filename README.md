# ai-hardware-dev — 零基础 AI 硬件开发 Skill（可在多种 Agent 中使用）

> 让 **Trae / 豆包 / Claude Code / Codex / DeepSeek Harness** 等任意 AI Agent 带你从零开发 AI 硬件：方向定义 → 需求翻译 → 选型 → 环境搭建 → 原理图 → 面包板原型 → PCB → 打样 → 焊接 → 固件（含 AI 推理）→ 烧录 → 联调 → 产品化 → 排障。

## 这是什么

一个**可移植的 Skill 包**：把"AI 辅助硬件开发"的完整方法论、操作命令（Windows 优先）、提示词模板、常见坑、验收清单固化下来。无论你在哪个 Agent 工具里，把本包路径指给它、让它按 `SKILL.md` 入口路由即可。**EasyInput V2.0 仅为参考案例板，本包板级无关**：任何新板先建板级知识合同（board-contract.json），Agent 再开发。

## 目录结构

```
ai-hardware-dev-skill/
├── SKILL.md                  # 入口：路由 + 纪律 + 完成标准（渐进披露）
├── board-reference.md        # 参考案例板事实 + 新板建合同方法
├── prompt-templates.md       # 高频提示词全文 + 全量索引
├── resources.md              # 官方/GitHub/社区/训练营资源清单
├── README.md                 # 本文件：安装与使用
├── CHANGELOG.md              # 版本记录（1.0.0 / 2.0.0 / 3.0.0）
├── LICENSE                   # 双授权声明（PolyForm NC 默认 + Apache-2.0 商业路径）
├── LICENSE-PolyForm-Noncommercial-1.0.0.txt
├── LICENSE-Apache-2.0.txt
├── NOTICE                    # 来源归属与隐私声明
├── core/                     # 项目执行系统（V2）
│   ├── project-state.md      #   项目状态：project-memory.json 模板 + 维护纪律
│   ├── decision-record.md    #   决策留痕：背景/备选/取舍/影响
│   ├── failure-knowledge-base.md  # 失败知识库：症状/概率原因/验证/解决/次数
│   └── ai-hardware-team.md   #   AI 团队多角色模式（PM→架构→电气→固件→QA→制造）
├── references/               # 各环节独立文件（渐进披露，按需读取）
│   ├── 00-direction-and-definition.md    # 方向确定与产品定义
│   ├── 00-product-translator.md          # 需求翻译：人话→工程规格
│   ├── 01-platform-selection.md          # 选型：MCU 级四级主线（Level1-4）
│   ├── 02-environment-setup.md           # 环境搭建
│   ├── 03-schematic-design.md            # 原理图设计
│   ├── 03a-breadboard-prototype.md       # 面包板原型验证（V3 新增，先验证再画板）
│   ├── 04-pcb-layout.md                  # PCB 布局布线
│   ├── 05-manufacturing-and-sourcing.md  # 打样与元器件采购
│   ├── 06-soldering-and-hardware-debug.md# 焊接与硬件调试
│   ├── 07-firmware-ai.md                 # 固件开发（含 AI 推理）
│   ├── 08-flashing-and-debugging.md      # 烧录与调试（含烧录授权门禁）
│   ├── 09-software-hardware-integration.md # 软硬件联调
│   ├── 10-productization.md              # 产品化
│   ├── 11-troubleshooting.md             # 故障排查（结构化失败知识库）
│   └── camp-notes.md                     # 训练营资料速览
└── scripts/                  # 可执行校验层（V3 新增，反幻觉）
    ├── check_board_contract.py   # 板级合同 JSON 校验
    ├── collect_pins.py           # 网表 vs 合同引脚 diff
    ├── power_budget.py           # 功耗预算求和 + 裕量
    ├── check_flash_budget.py     # 分区/内存预算
    ├── check_markdown_links.py   # Markdown 死链扫描
    ├── README.md                 # 脚本用法
    ├── skill-ci.yml.example      # CI 样例
    └── examples/                 # 样例输入文件
```

## 在各类 Agent 中安装使用

### 1. Trae（字节跳动的 AI IDE）

1. 克隆/下载本仓库到本地，如 `D:\ai-hardware-dev-skill`。
2. 在 Trae 中打开你的项目，把本包路径告诉 Trae（例如："请在 D:\ai-hardware-dev-skill 目录下按 SKILL.md 的入口路由工作"），或把 `SKILL.md` 内容粘贴进对话。
3. 让 Trae 先读 `SKILL.md` 的「入口路由」，再按你的目标（"我要做产品" / "只烧录" / "只画板"）选择环节文件。

### 2. 豆包（Doubao）

1. 在豆包中打开你的硬件项目会话。
2. 上传/粘贴本包关键文件（推荐至少：SKILL.md、board-reference.md），或把仓库路径给豆包让它按链接读取。
3. 让它从「入口路由」开始，按环节推进；启动项目时让它先建 `docs/project-memory.json`（见 `core/project-state.md`）。

### 3. Claude Code / Codex / DeepSeek Harness（命令行 Agent）

1. 克隆仓库到本地。
2. 在项目根目录放一个入口说明（或直接在提示里写）："请先读取 `SKILL.md`，按其「入口路由」表判断我的意图，然后只加载对应环节文件工作；涉及板级事实先读 `board-reference.md`；启动项目先初始化 `core/project-state.md` 的 project-memory.json。"
3. 关键纪律（可原样粘贴进 system prompt 或首条提示）：
   - 证据分级：编译通过 ≠ 烧录成功 ≠ 日志正常 ≠ 真机验收，回答时说明结论的证据级别。
   - 板级事实以 `docs/board-contract.json` 为准，不把 EasyInput V2.0 当通用事实。
   - 烧录前过「烧录授权门禁」（见 08 环节）：显示端口/芯片/完整 MAC/版本/产物/命令，等用户原样输入"确认烧录到 <完整 MAC>"才写入；不默认 erase_flash；失败唯一允许"保持开机短按一次 BOOT"重试一次。

### 4. 通用（任何 Agent）

- 直接读 `SKILL.md` 即可：它本身就是给 Agent 看的操作说明书。
- 涉及具体板子的引脚 / BOOT / 电源 / 外设事实时，先按 `board-reference.md` 的「新板建合同方法」为你的板建 `docs/board-contract.json`。

## 快速上手（零基础第一周）

1. 读 `references/00-direction-and-definition.md`，用模板 A/B/C 确定一个 2 周内能做完的 MVP 产品。
2. 读 `references/00-product-translator.md`，把想法翻译成工程规格。
3. 读 `references/01-platform-selection.md`，按四级主线选型（零基础默认 Level 1：ESP32-S3）。
4. 读 `references/02-environment-setup.md` 装环境（ESP-IDF 优先）。
5. 读 `references/03a-breadboard-prototype.md`：先在面包板上跑通 MVP，再决定自画板（03 原理图 → 04 PCB → 05 打样）。
6. 之后按 06 焊接 → 07 固件 → 08 烧录 → 09 联调 → 10 产品化推进，卡住就读 11。

## 验证与许可

- 本包自带 `scripts/` 校验层（板级合同、引脚 diff、功耗/分区预算、链接检查），详见 `scripts/README.md`。
- 双授权：默认 PolyForm Noncommercial 1.0.0（非商业使用，含专利条款）；商业使用需另行取得授权并按 Apache-2.0 条款。训练营资料仅限非商业使用（详见 LICENSE / NOTICE）。
