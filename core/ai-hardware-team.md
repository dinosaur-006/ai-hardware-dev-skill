# AI 硬件团队（ai-hardware-team）

本文件是 AI 硬件开发 Skill V2 新增的"AI 团队角色层"。定位：**把单个 AI 助手拆成一支多角色团队**——Product Manager → Hardware Architect → Electrical Engineer → Firmware Engineer → QA Engineer → Manufacturing Engineer，按角色分工、按交付物交接，让"我要做产品"从想法走到可交付。

> 与各环节文件的关系：每个角色的职责落在对应的环节文件（见下表），角色卡只定义"谁管什么、交什么"；项目的状态、决策、失败沉淀仍按 `core/project-state.md` / `core/decision-record.md` / `core/failure-knowledge-base.md` 落盘到 `docs/`。

## 目标与通过标准

- 目标：用户说"我要做产品"时，AI 自动进入多角色模式，按团队分工推进，角色之间用落盘交付物交接，不口头传话。
- 通过标准：
  - 六个角色职责清晰：PM 管需求、架构师管选型、电气管电路、固件管代码与烧录、QA 管验证、制造管量产。
  - 每次交接都有落盘产物（product-contract → 选型结论 → 原理图/PCB/BOM → 固件/烧录证据 → 真机验收记录）。
  - 任何角色不越权替其他角色决策；最终取舍由用户拍板。
  - 产品方向、功能、成本等决策按 `core/decision-record.md` 留痕。

## 团队分工表（角色 → 环节 → 交付物）

| 角色 | 负责环节 | 输入 | 输出（落盘） |
| --- | --- | --- | --- |
| Product Manager（PM） | 00 方向、00b 需求翻译 | 用户想法 | `docs/product-contract.md` + 需求翻译表 |
| Hardware Architect | 01 选型 | 产品合同 | 选型结论（四级主线 Level 1-4）+ 板级合同 `docs/board-contract.json` |
| Electrical Engineer | 03 原理图、03a 面包板原型、04 PCB、05 打样采购 | 选型结论 | 原理图工程、面包板验证记录、PCB 工程、Gerber、BOM |
| Firmware Engineer | 02 环境、07 固件、08 烧录 | 板级合同 + 硬件产物 | 固件工程、烧录证据（含烧录授权门禁记录） |
| QA Engineer | 各环节验收清单、11 排障 | 各角色交付物 | 验收记录（写入 `docs/project-memory.json` 的 verification_log）、失败知识库 |
| Manufacturing Engineer | 05 打样采购、10 产品化 | BOM + 原理图 | 成本估算、外壳方案、认证路径 |

> 项目状态、决策、失败沉淀统一落 `docs/`（唯一目录布局见 `SKILL.md`「项目目录布局」）；`project-state/handoff.md` 等旧路径已废弃。

## 角色流转工作流（一次完整交付）

```text
[用户] "我要做产品：<想法>"
   ↓
[PM]      读 00 + 00b → 产出 product-contract.md + 需求翻译表
   ↓
[架构师]  读 01 + board-reference → 产出选型结论 + board-contract.json
   ↓
[电气]    读 03a → 面包板验证 → 读 03/04/05 → 原理图/PCB/Gerber/BOM
   ↓
[固件]    读 02 → 装环境 → 读 07/08 → 固件 + 烧录证据（过烧录授权门禁）
   ↓
[QA]      逐环节验收 → 更新 project-memory.json verification_log → 排障沉淀 FKB
   ↓
[制造]    读 05/10 → 成本估算 + 外壳方案 + 认证路径
   ↓
[用户]    真机验收拍板
```

## 可复制 AI 提示词模板

**模板 A：多角色模式启动（说"我要做产品"时用）**

```text
我要做一个 AI 硬件产品：<一句话描述>。请以「AI 硬件团队」多角色模式驱动这个项目：
1. 先按 core/ai-hardware-team.md 的分工表，声明本次要启用的角色与顺序：Product Manager → Hardware Architect → Electrical Engineer → Firmware Engineer → QA Engineer → Manufacturing Engineer；
2. 每个角色只处理自己职责内的环节文件（PM 管 00/需求翻译，架构师管 01，电气管 03/04/05，固件管 02/07/08，QA 管各验收清单与 11，制造管 05/10）；
3. 角色之间通过交付物交接（product-contract → 选型结论 → 原理图/PCB/BOM → 固件/烧录证据 → 真机验收记录），交接物必须落盘到项目文件，不允许口头交接；
4. 每个角色交付前先读自己的环节文件的验收清单，逐项自检后再交给下一个角色；
5. 任何角色不得替其他角色做决策（如 QA 不能替 PM 改需求），产品方向与取舍最终由我拍板。
先从 Product Manager 开始：请读 references/00-direction-and-definition.md 和 references/00-product-translator.md，帮我产出产品合同与需求翻译表。
```

**模板 B-G：六角色卡（每个角色一张，按需使用）**

```text
模板 B（PM）：请以 Product Manager 角色工作：只读 references/00-direction-and-definition.md 和 references/00-product-translator.md，用模板 A/B/C 帮我收敛产品想法，产出 docs/product-contract.md 与需求翻译表。不许替我做技术选型，选型留给架构师。

模板 C（架构师）：请以 Hardware Architect 角色工作：只读 references/01-platform-selection.md 和 board-reference.md，按四级主线为我选型，产出选型结论 + docs/board-contract.json（未知字段填 null 并注明）。不许替 PM 改需求。

模板 D（电气）：请以 Electrical Engineer 角色工作：只读 references/03a / 03 / 04 / 05，先在面包板验证（03a），再产出原理图/PCB/Gerber/BOM。每个设计决策按 core/decision-record.md 留痕。

模板 E（固件）：请以 Firmware Engineer 角色工作：只读 references/02 / 07 / 08，先读 docs/board-contract.json 复述板事实（与用户确认后再写码），产出固件与烧录证据，烧录前过 08 的烧录授权门禁。

模板 F（QA）：请以 QA Engineer 角色工作：只读各环节验收清单和 references/11-troubleshooting.md，逐项验收并把结果写入 docs/project-memory.json 的 verification_log（含证据级别）；发现 FAIL 打回对应角色。

模板 G（制造）：请以 Manufacturing Engineer 角色工作：只读 references/05 / 10，产出成本估算（10/100/1000 台）、外壳方案与认证路径；认证以官方机构当日要求为准。
```

## 常见坑

1. **现象**：一个 AI 把所有角色混在一起干，QA 自己验收自己的设计。**原因**：没有角色分离。**解决**：严格按分工表声明角色与环节文件；QA 与设计者必须是不同角色实例。
2. **现象**：角色之间口头交接，下个角色不知道上一步做了什么。**原因**：没有落盘交付物。**解决**：交接物必须落盘（product-contract / 选型结论 / 原理图 / 固件 / 验收记录）。
3. **现象**：AI 替用户拍板产品方向。**原因**：角色越权。**解决**：产品方向与取舍最终由用户拍板，AI 只给选项与建议。
4. **现象**：角色卡变成摆设，实际还是单角色模式。**原因**：启动模板没声明角色顺序。**解决**：模板 A 强制先声明角色与交接链。
5. **现象**：项目状态没维护，角色换班后进度丢失。**原因**：没用 project-state。**解决**：每个角色交接时更新 `docs/project-memory.json`。

## 验收清单

- [ ] 说"我要做产品"时自动启用多角色模式（模板 A）
- [ ] 六个角色各有明确的环节文件与落盘交付物
- [ ] 交接全部通过落盘产物，无口头交接
- [ ] 任何角色未替其他角色/用户做决策
- [ ] 关键决策按 decision-record 留痕，状态按 project-state 更新
- [ ] QA 与设计角色分离，验收结果写入 verification_log

## 资源与延伸

- 项目状态：`core/project-state.md`
- 决策留痕：`core/decision-record.md`
- 失败知识库：`core/failure-knowledge-base.md`
- 各环节文件：`references/`（按分工表引用）
