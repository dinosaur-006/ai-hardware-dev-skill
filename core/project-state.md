# 项目状态系统（project-state）

本文件是 AI 硬件开发 Skill V2 新增的"项目记忆"层。定位：**由 AI 主动维护的单一事实源（single source of truth）**——任何时刻打开 `project-memory.json`，AI 与用户都能立刻回答四件事：

1. **项目现在到哪了**（`current_stage`：12 个环节里推进到第几环）；
2. **已经定了什么**（`decisions_made`：每条决策都引用 `core/decision-record.md` 里的留痕）；
3. **还有什么没定、卡在哪**（`undecided`：未定项 + 阻塞在谁手里）；
4. **有什么风险、怎么缓解**（`risks`）+ **每一环验证到哪一级证据**（`verification_log`）。

它把 Skill 从"一次性的流程导航"升级为"可持续跟踪的项目执行系统"：换一天、换一个会话、换一个 AI 工具，只要读这一个 JSON 就能无缝接手，不用翻聊天记录。

> 与其他文件的关系：`product_contract` 指向 `docs/product-contract.md`（00 环节产物）；`board_contract` 指向 `docs/board-contract.json`（见 `board-reference.md` 的建合同方法）；`decisions_made` 里的每条都通过 `decision_id` 引用 `docs/decisions/` 下的决策记录（见 `core/decision-record.md`）。项目目录布局以 SKILL.md「项目目录布局（唯一权威）」为准。

## 目标与通过标准

- 目标：让项目进度、决策、未决项、风险、验证证据**全部落盘**，不再依赖 AI 的上下文记忆或用户的聊天记录。
- 通过标准：
  - 项目开工第一天就有 `project-memory.json`，且字段齐全（未知项显式写 `null` 或 `"待补"`，不留空、不猜）。
  - 每完成一个环节的验收清单，`current_stage`、`decisions_made`、`undecided`、`risks`、`verification_log` 五个数组都被同步更新。
  - 任意时刻对 AI 说"当前项目状态"，AI 能在不翻聊天记录的情况下，仅凭 `project-memory.json` 给出结构化汇报。
  - 每条已做决策都能在 `docs/decisions/` 找到对应留痕（含备选方案与取舍理由），不靠"当时聊过"。
  - 每个未定项都标了阻塞方（等用户拍板 / 等实验结果 / 等物料到货），不会无限期挂起没人管。

## 可复制操作与命令

本系统没有命令行，核心产物是一个 JSON 文件。操作分三步。

### 第一步：建项目时初始化

在项目 `docs/` 目录下创建 `project-memory.json`（即 `docs/project-memory.json`，与 `product-contract.md` 同目录；目录结构见 `references/00-direction-and-definition.md`）。把下面模板整段复制进去，让 AI 按"模板 A 提示词"逐项填写。

> 路径约定：JSON 内部所有路径字段（`product_contract`、`board_contract`、`decisions_made[].record_path`）一律**相对项目根目录**书写（如 `docs/product-contract.md`、`docs/decisions/DRV-001-xxx.md`），不随本文件自身位于 `docs/` 而改成相对 `docs/` 的路径。

```json
{
  "project_id": "<短编号，如 va-desk-2026q3>",
  "project_name": "<一句话项目名>",
  "created_at": "<YYYY-MM-DD>",
  "updated_at": "<YYYY-MM-DD>",
  "current_stage": "00/12",
  "stage_map": {
    "00/12": "方向确定与产品定义",
    "00b/12": "需求翻译（人话→工程规格）",
    "01/12": "平台/芯片选型",
    "02/12": "环境搭建",
    "03/12": "原理图设计",
    "03a/12": "面包板原型验证（先验证再画板）",
    "04/12": "PCB 布局布线",
    "05/12": "打样与元器件采购",
    "06/12": "焊接与硬件调试",
    "07/12": "固件开发（含 AI 推理）",
    "08/12": "烧录与调试",
    "09/12": "软硬件联调",
    "10/12": "产品化",
    "11/12": "故障排查（横向贯穿全程的安全网）"
  },
  "product_contract": "docs/product-contract.md",
  "board_contract": "docs/board-contract.json",
  "decisions_made": [
    {
      "decision_id": "DRV-001",
      "summary": "<一句话决策>",
      "date": "<YYYY-MM-DD>",
      "record_path": "docs/decisions/DRV-001-xxx.md"
    }
  ],
  "undecided": [
    {
      "item": "<未定项>",
      "blocked_by": "等用户拍板 | 等实验结果 | 等物料到货",
      "notes": "<为什么卡住、缺什么信息>"
    }
  ],
  "risks": [
    {
      "risk": "<风险描述>",
      "level": "high|medium|low",
      "mitigation": "<缓解措施>"
    }
  ],
  "verification_log": [
    {
      "stage": "00/12",
      "date": "<YYYY-MM-DD>",
      "evidence_level": "编译通过|烧录成功|日志正常|真机验收",
      "items": ["<验收项>", "..."],
      "notes": "<说明>"
    }
  ]
}
```

### 第二步：每完成一个环节，更新一次（纪律核心）

完成某环节验收清单后，用"模板 B"让 AI 更新五个字段：

- `current_stage`：推进到下一个环节（如 `01/12` → `02/12`）。
- `decisions_made`：本环节新确定的决策追加进来，引用决策记录 id。
- `undecided`：本环节新出现的未定项（标阻塞方）。
- `risks`：新增/缓解的风险（缓解的可以移除或标 mitigated）。
- `verification_log`：本环节的验收结果（含证据级别）。

> 维护纪律：**AI 不得在没更新 project-memory.json 的情况下宣布"完成"某环节**；用户看到的状态永远以该文件为准。

### 第三步：任意时刻汇报状态

用"模板 C"让 AI 仅凭 `project-memory.json` 汇报：项目在哪、定了什么、卡在哪、下一步做什么。

## 可复制 AI 提示词模板

**模板 A：初始化项目状态（启动任何项目必用）**

```text
请按 core/project-state.md 的 project-memory.json 模板，为我的新项目 <项目名> 初始化项目状态文件：
1. 字段：project_name=<项目名>、current_stage="00/12"、product_contract、board_contract 指向对应文件路径；
2. decisions_made 初始为空，undecided 列出此刻所有未定项（含"谁决策"：等用户 / 等实验）；
3. risks 列出起步阶段我能预见的风险（如板级事实未确认、模型跑不动），每项给等级和缓解；
4. 把初始化结果写盘为 <项目目录>/docs/project-memory.json，并在回复里复述：项目现在在哪、定了什么、还有什么没定。
```

**模板 B：每完成一个环节就更新状态（纪律核心）**

```text
我刚完成 <环节名>（第 <N> 环节）的验收清单，结果：<各验收项 PASS/FAIL 摘要，FAIL 项写原因>。
请更新项目状态文件 docs/project-memory.json：current_stage 改为 "<N+1>/12"；把本环节确定的决策追加进 decisions_made（引用对应 decision-record 的 id）；把本环节新出现的未定项和风险同步进 undecided / risks；把本次验收结果追加进 verification_log（含证据级别：编译通过/烧录成功/日志正常/真机验收）。
更新后，用一句话列出"从上一次更新到这次"的差异（阶段变化、新增决策、新增风险），再给下一步建议。
```

**模板 C：状态汇报（"项目现在到哪了"）**

```text
请只读我的项目状态文件 docs/project-memory.json，按下面格式汇报：
1. 当前阶段（current_stage → stage_map 含义）+ 已完成环节；
2. 已定决策（decisions_made，引用 decision-record 的完整记录）；
3. 未定项（undecided：每条 + 阻塞方）；
4. 风险（risks：level + mitigation）；
5. 最近一次验收的证据级别（verification_log 最后一条）；
6. 下一步建议（按流程顺序给出 1-3 个动作）。
不要翻聊天记录，只以该文件为准。
```

## 常见坑

1. **现象**：AI 说"已完成 03 原理图"但 project-memory.json 还是 02。**原因**：没执行更新纪律。**解决**：验收完成必须更新状态文件，否则不算完成（纪律见上）。
2. **现象**：project-memory.json 里 decisions_made 引用了不存在的决策文件。**原因**：先写了状态、没落盘决策记录。**解决**：决策必须先落 `docs/decisions/` 再引用（见 decision-record.md）。
3. **现象**：换了一个 AI 工具（如 Trae 换豆包），新 AI 不知道项目进度。**原因**：只靠聊天记录。**解决**：新会话先读 project-memory.json（模板 C 汇报）。
4. **现象**：undecided 里的未定项长期没人管。**原因**：没标阻塞方。**解决**：每条必须标"等用户拍板 / 等实验结果 / 等物料到货"，谁该动谁一目了然。
5. **现象**：verification_log 全写"编译通过"。**原因**：把最弱证据当全部。**解决**：按证据级别如实写：编译通过 / 烧录成功 / 日志正常 / 真机验收，真机验收才等于"可用"。

## 验收清单

- [ ] 项目开工第一天已有 `docs/project-memory.json`，字段齐全
- [ ] `current_stage` 与真实进度一致（每完成一环节就更新）
- [ ] 每条 decisions_made 都能在 `docs/decisions/` 找到留痕
- [ ] 每个 undecided 项都标了阻塞方
- [ ] risks 有等级与缓解措施，缓解后已移除/标 mitigated
- [ ] verification_log 每项都有证据级别（编译通过/烧录成功/日志正常/真机验收）
- [ ] 任意时刻仅凭 project-memory.json 能回答"项目到哪了"

## 资源与延伸

- 决策留痕：`core/decision-record.md`
- 失败知识库：`core/failure-knowledge-base.md`
- 项目目录布局（唯一权威）：`SKILL.md`「项目目录布局」
