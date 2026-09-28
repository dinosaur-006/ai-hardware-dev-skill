# ai-hardware-dev — 零基础 AI 硬件开发全流程 Skill

一个跨 Agent 可用的 Skill 包：让 AI Agent 引导你（零基础、AI 辅助开发 / vibecoding）完成 AI 硬件产品的完整开发闭环——方向定义、芯片选型、环境搭建、原理图、PCB、打样、焊接、固件（含边缘 AI 推理）、烧录、软硬件联调、产品化与故障排查。

- **板级无关**：主体是通用方法论 + MCU 级 AI 硬件主线知识（Level1 ESP32-S3 入门 → Level2 STM32+NPU → Level3 树莓派 → Level4 Jetson）；EasyInput V2.0 只是参考案例，任何开发板都适用（见 `board-reference.md` 的新板建合同方法）。
- **单环节可用**：只想烧录、只想联调、只想画板时，直接读对应环节文件即可。
- **项目执行系统**（V2）：项目状态（project-memory.json）、决策记录、失败知识库、AI 硬件团队多角色模式，让 Skill 不只是"流程导航"而是"项目执行系统"。
- **每环节自带**：目标与通过标准、可复制命令（Windows 优先）、可复制 AI 提示词模板、常见坑、验收清单。

## 目录结构

```
ai-hardware-dev/
├── SKILL.md                          # 入口：触发描述、意图路由、工作流、边界、禁止事项、完成标准
├── README.md                         # 本文件：各 Agent 安装与使用方法
├── LICENSE / NOTICE                  # 非商业使用与来源归属声明
├── board-reference.md                # 参考案例板 EasyInput V2.0 + 新板建板级知识合同方法
├── prompt-templates.md               # 各环节可复制 AI 提示词模板汇总
├── resources.md                      # 分类资源清单（官方/GitHub/中文社区/训练营，链接已核验）
├── core/                             # V2 项目执行系统
│   ├── project-state.md              # 项目状态：project-memory.json 模板 + 每环节更新纪律
│   ├── decision-record.md            # 决策记录：关键选型/方案取舍留痕模板
│   ├── failure-knowledge-base.md     # 失败知识库：症状/概率原因/验证/解决/次数
│   └── ai-hardware-team.md           # AI 硬件团队多角色模式（PM→架构→电气→固件→QA→制造）
└── references/
    ├── 00-direction-and-definition.md     # 方向确定与产品定义
    ├── 00-product-translator.md           # 需求翻译层：人话→工程规格（V2 新增）
    ├── 01-platform-selection.md           # MCU 级 AI 硬件主线选型（Level1-4 四级分级）
    ├── 02-environment-setup.md            # 环境搭建
    ├── 03-schematic-design.md             # 原理图设计（含 AI 防幻觉检查表）
    ├── 04-pcb-layout.md                   # PCB 布局布线（含 AI 防幻觉检查表）
    ├── 05-manufacturing-and-sourcing.md   # 打样与元器件采购
    ├── 06-soldering-and-hardware-debug.md # 焊接与硬件调试
    ├── 07-firmware-ai.md                  # 固件开发（含 AI 推理）
    ├── 08-flashing-and-debugging.md       # 烧录与调试
    ├── 09-software-hardware-integration.md# 软硬件联调
    ├── 10-productization.md               # 产品化
    ├── 11-troubleshooting.md              # 故障排查（结构化失败知识库）
    └── camp-notes.md                      # 训练营资料速览（WaytoAGI 第七期）
```

## 在各 Agent 中安装使用

本包遵循标准 SKILL.md 格式（YAML frontmatter + Markdown 正文 + references 渐进披露），不依赖任何特定 Agent 的私有工具。各 Agent 的挂载方式如下（具体路径以各工具当日文档为准）：

| Agent | 安装/使用方式 |
| --- | --- |
| **Claude Code** | 将本文件夹放入项目 `.claude/skills/ai-hardware-dev/` 或用户级 skills 目录，SKILL.md 会被自动识别；在对话中描述硬件开发需求即可触发。 |
| **Codex** | 将本文件夹放入项目 `.codex/skills/ai-hardware-dev/`；或在项目 `AGENTS.md` 中写一行"硬件开发任务请阅读 `ai-hardware-dev/SKILL.md`"并给出路径。 |
| **Trae** | 在项目设置/自定义规则中引用 `SKILL.md` 的绝对路径或粘贴其内容；开发时提示"参考 ai-hardware-dev skill"。 |
| **DeepSeek Harness / 通用 Agent** | 把 `SKILL.md` 全文作为上下文/系统提示注入，或写入项目的 AGENTS.md/.cursorrules 等约定文件；需要哪个环节就再加载对应的 references 文件。 |
| **豆包 / 其他对话式 Agent** | 直接粘贴 `SKILL.md` 并说明"按其中路由读取 references 下对应文件"。 |

通用原则：任何 Agent 使用前先读 `SKILL.md`；涉及具体板的开发先读 `board-reference.md`。

## 使用前必读

1. **新板先建板级知识合同**：买到新开发板后，按 `board-reference.md` 第二部分花 30-60 分钟建立 `board-contract.json`（可让 AI 代填，有模板），后续所有开发都以合同为准，避免按通用教程猜引脚。
2. **启动项目先建项目状态**：按 `core/project-state.md` 初始化 `project-memory.json`（项目名、当前阶段、已定决策、未定项、风险、验证记录）；每完成一个环节的验收清单后让 AI 更新状态并列出差异。
3. **从 00 开始走一遍全流程**：第一个项目建议按 00（→需求翻译）→01→11 顺序推进，每环节验收清单打勾后再进入下一环节。
4. **单独调用**：只想做某个环节（如烧录）时，直接读对应文件，无需走完全程。
5. **证据分级**：编译通过 ≠ 烧录成功 ≠ 真机验收。每步以真机表现为准。
6. **说"我要做产品"**：读 `core/ai-hardware-team.md`，让 AI 以多角色团队模式（PM→硬件架构→电气→固件→QA→制造）驱动全程。

## 许可

- 本包：CC BY-NC 4.0（署名-非商业性使用），详见 `LICENSE`。
- 引用内容与来源归属：详见 `NOTICE`（训练营资料仅限非商业使用）。
- 价格/交期/认证等动态信息以官方当日为准。
