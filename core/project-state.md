# 项目状态系统（project-state）

本文件是 AI 硬件开发 Skill V2 新增的"项目记忆"层。定位：**由 AI 主动维护的单一事实源（single source of truth）**——任何时刻打开 `project-memory.json`，AI 与用户都能立刻回答四件事：

1. **项目现在到哪了**（`current_stage`：12 个环节里推进到第几环）；
2. **已经定了什么**（`decisions_made`：每条决策都引用 `core/decision-record.md` 里的留痕）；
3. **还有什么没定、卡在哪**（`undecided`：未定项 + 阻塞在谁手里）；
4. **有什么风险、怎么缓解**（`risks`）+ **每一环验证到哪一级证据**（`verification_log`）。

它把 Skill 从"一次性的流程导航"升级为"可持续跟踪的项目执行系统"：换一天、换一个会话、换一个 AI 工具，只要读这一个 JSON 就能无缝接手，不用翻聊天记录。

> 与其他文件的关系：`product_contract` 指向 `docs/product-contract.md`（00 环节产物）；`board_contract` 指向 `references/board-contract.json`（见 `board-reference.md`）；`decisions_made` 里的每条都通过 `decision_id` 引用 `docs/decisions/` 下的决策记录（见 `core/decision-record.md`）。

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
    "01/12": "平台/芯片选型",
    "02/12": "环境搭建",
    "03/12": "原理图设计",
    "04/12": "PCB 布局布线",
    "05/12": "打样与元器件采购",
    "06/12": "焊接与硬件调试",
    "07/12": "固件开发（含 AI 推理）",
    "08/12": "烧录与调试",
    "09/12": "软硬件联调",
    "10/12": "产品化",
    "11/12": "故障排查（横向贯穿，非终点）"
  },
  "product_contract": "docs/product-contract.md",
  "board_contract": "references/board-contract.json",
  "decisions_made": [
    {
      "decision_id": "<如 DRV-001>",
      "summary": "<一句话结论>",
      "date": "<YYYY-MM-DD>",
      "record_path": "docs/decisions/<对应文件>.md"
    }
  ],
  "undecided": [
    {
      "item": "<未定项，如 麦克风选模拟 I2S 还是数字 PDM>",
      "blocked_on": "<user_decision / waiting_for_experiment / waiting_for_parts / blocked_by_stage_NN>",
      "owner": "<谁负责：用户 / AI 协助 / 第三方>",
      "needed_by_stage": "<必须在第几环之前定，如 03/12>"
    }
  ],
  "risks": [
    {
      "risk": "<风险描述>",
      "level": "<high / medium / low>",
      "mitigation": "<缓解措施>",
      "status": "<open / mitigated / closed>"
    }
  ],
  "verification_log": [
    {
      "stage": "<如 02/12>",
      "evidence_level": "<见下方证据级别定义>",
      "result": "<pass / fail / partial / not_started>",
      "note": "<证据简述，如 串口日志贴出 hello>",
      "date": "<YYYY-MM-DD>"
    }
  ]
}
```

**证据级别（`evidence_level` 字段取值，从低到高，禁止越级冒充）：**

| 级别 | 含义 | 例子 |
| --- | --- | --- |
| `doc_review` | 仅文档/静态检查通过，未动硬件 | ERC 零错误、DRC 零错误 |
| `compile_pass` | 编译/构建通过 | `idf.py build` 成功 |
| `flash_pass` | 固件成功烧录进板子 | esptool 报 hash 校验通过 |
| `log_observed` | 串口日志看到预期输出 | 日志打出 `hello board` |
| `real_machine_pass` | 真机上达到产品合同里的验收标准 | 真机能唤醒、能对话、能断电重开 |

> 纪律：写 `verification_log` 时必须说清是哪一级。编译通过 ≠ 烧录成功 ≠ 日志正常 ≠ 真机验收通过（沿用 SKILL.md 的证据分级纪律）。

### 第二步：每环验收后更新（AI 必须执行的纪律）

见下方"模板 B"的提示词。核心动作是**先更新 JSON，再在回复里列出本次差异**。

### 第三步：随时状态汇报

见下方"模板 C"。用户任何时候说"项目现在到哪了 / 当前状态"，都用模板 C。

## 可复制 AI 提示词模板

### 模板 A：初始化项目状态

```text
我要开始一个新的 AI 硬件项目，项目名是 <项目名>，一句话描述是 <做什么>。
请帮我在项目 docs/ 目录下创建 project-memory.json（完整路径 docs/project-memory.json）：
1. 按 core/project-state.md 里的完整模板生成 JSON；
2. product_contract 指向 docs/product-contract.md，board_contract 指向 references/board-contract.json；
3. current_stage 先填 "00/12"；
4. decisions_made / undecided / risks / verification_log 先放空数组，不要编造内容；
5. created_at 和 updated_at 都填今天日期；
6. 填完后告诉我还缺哪些信息、需要我补充什么。
注意：我不知道的字段就留空数组或写 "待补"，不要替我编决策、编风险、编验证结果。
```

### 模板 B：每完成一个环节就更新状态（含纪律原文）

> 把下面这段纪律原文贴给 AI，作为长期约定，每环验收后执行：

```text
【项目状态更新纪律，必须遵守】
每完成一个环节的验收清单后，你（AI）必须做两件事：
1. 更新 project-memory.json：
   - current_stage 推进到刚完成的环节号（如刚做完 03/12 原理图，就写成 "03/12"）；
   - 把本环节新做的关键决策追加进 decisions_made（每条要有 decision_id、一句话结论、日期、record_path 指向 docs/decisions/ 下的留痕）；
   - 把本环节已经定下来的项从 undecided 里删掉，把新冒出来的未定项加进去（必须标 blocked_on 和 owner）；
   - 把本环节新识别的风险追加进 risks（标 level 和 mitigation），已关闭的风险把 status 改成 closed；
   - 把本环节的验证结果追加进 verification_log（stage / evidence_level / result / note / date，证据级别不许越级）；
   - 同步更新 updated_at。
2. 在回复里明确列出"本次更新差异"：新增了哪几条决策、清掉了哪几个未定项、加了哪个风险、验证到了哪一级证据。
不要只改文件不汇报，也不要只在聊天里说而不落盘。
```

### 模板 C：状态汇报（"当前项目状态"查询模板）

```text
请读取项目 docs/project-memory.json，然后给我一份结构化的项目状态汇报，包含：
1. 当前进度：current_stage 是第几环、对应环节名是什么；
2. 已做决策：逐条列出 decisions_made（decision_id + 一句话结论 + 日期），并指出每条能在 docs/decisions/ 哪份文件里看到完整留痕；
3. 未决项：逐条列出 undecided，每条都要讲清"卡在哪、等谁、最晚哪一环之前要定"；
4. 风险：列出所有 status 为 open 的 risks，按 level 从高到低排；
5. 验证证据：列出 verification_log 里每个环节达到的最高证据级别，特别标出哪些环节还停留在 compile_pass 及以下、没有真机证据。
最后用 3 句话总结：下一步该干什么、最大的未决项是什么、最大的风险是什么。
只基于 project-memory.json 回答，不要凭聊天记忆补充；如果 JSON 里缺字段，直接说"状态文件缺该字段"。
```

## 常见坑

1. **现象**：`project-memory.json` 建好了，但两周后内容还是初始化那版，current_stage 纹丝不动。**原因**：把"建文件"当成了"上系统"，没有每环更新的纪律。**解决**：用模板 B 把更新动作写成硬纪律——每环验收清单一过就必须改 JSON 并汇报差异；AI 不更新就算该环节没闭环。
2. **现象**：decisions_made 里只写了"选了 N16R8"，没写为什么、比了哪些备选。**原因**：状态文件只记结论不记推理。**解决**：状态文件里的 decisions_made 只放一句话摘要 + record_path，完整的备选方案与取舍理由必须落到 `docs/decisions/` 下（见 `core/decision-record.md`）；没有 record_path 的决策不允许进 decisions_made。
3. **现象**：风险一直躺在脑子里，直到打样回来焊不上/模型跑不动才爆。**原因**：没有风险登记本，risks 数组空着。**解决**：每环结束强制过一遍 risks——选型风险、供应链风险、性能风险、认证风险；哪怕是 low 也要登记，爆雷时能溯源。
4. **现象**：undecided 里列了"麦克风选型待定"，但过了三周还在那，没人记得是在等谁。**原因**：未定项没标阻塞方和截止环节。**解决**：每条 undecided 必须有 `blocked_on`（user_decision / waiting_for_experiment / waiting_for_parts / blocked_by_stage_NN）和 `needed_by_stage`；到了截止环节还没定，AI 要主动在状态汇报里高亮提醒。
5. **现象**：同时开两个硬件项目，两个项目的进度混在一个 project-memory.json 里，current_stage 不知道在说哪个。**原因**：一个项目一个记忆文件的原则没守住。**解决**：每个项目一个独立文件夹、一个独立 `project-memory.json`，`project_id` 全局唯一；切换项目时先让 AI 读对应文件夹的 JSON，不允许跨项目合并。
6. **现象**：verification_log 里全写 "pass"，但一问是编译 pass 还是真机 pass，说不清。**原因**：证据级别没分级。**解决**：严格按五级证据（doc_review / compile_pass / flash_pass / log_observed / real_machine_pass）填写，没做到真机就不许写 real_machine_pass。

## 验收清单

- [ ] `docs/` 目录下存在 `project-memory.json`，且能被 JSON 解析器正常打开（无语法错误）
- [ ] `project_id`、`project_name`、`created_at`、`updated_at` 已填写
- [ ] `current_stage` 取值在 `00/12` 到 `11/12` 之间，且与 `stage_map` 里的环节名对得上
- [ ] `product_contract`、`board_contract` 指向的文件路径真实存在
- [ ] `decisions_made` 里每条都有 `decision_id`、`summary`、`date`、`record_path`，且 record_path 文件真实存在
- [ ] `undecided` 里每条都标了 `blocked_on`、`owner`、`needed_by_stage`，没有"裸待办"
- [ ] `risks` 里每条都标了 `level`（high/medium/low）和 `mitigation`，状态明确
- [ ] `verification_log` 里每条都有合法的 `evidence_level`，且没有越级冒充（如没真机证据就不写 real_machine_pass）
- [ ] 最近一次 `updated_at` 与刚完成的环节时间吻合，不是建文件后再没动过
- [ ] 对 AI 说"当前项目状态"，它能仅凭该 JSON 输出模板 C 的五段汇报

## 附：完整 project-memory.json 示例（虚构，仅示范字段填法）

> 以下为虚构项目"桌面 AI 语音助手 MVP"的示例，**不是真实项目记录**，仅示范每个字段怎么填。

```json
{
  "project_id": "va-desk-2026q3",
  "project_name": "桌面 AI 语音助手 MVP（离线唤醒 + 在线对话）",
  "created_at": "2026-09-01",
  "updated_at": "2026-09-28",
  "current_stage": "07/12",
  "stage_map": {
    "00/12": "方向确定与产品定义",
    "01/12": "平台/芯片选型",
    "02/12": "环境搭建",
    "03/12": "原理图设计",
    "04/12": "PCB 布局布线",
    "05/12": "打样与元器件采购",
    "06/12": "焊接与硬件调试",
    "07/12": "固件开发（含 AI 推理）",
    "08/12": "烧录与调试",
    "09/12": "软硬件联调",
    "10/12": "产品化",
    "11/12": "故障排查（横向贯穿，非终点）"
  },
  "product_contract": "docs/product-contract.md",
  "board_contract": "references/board-contract.json",
  "decisions_made": [
    {
      "decision_id": "DRV-001",
      "summary": "主控平台选 ESP32-S3 而非树莓派 Zero（零基础两周可完成）",
      "date": "2026-09-02",
      "record_path": "docs/decisions/DRV-001-esp32s3-vs-rpi.md"
    },
    {
      "decision_id": "DRV-002",
      "summary": "模组选 ESP32-S3-WROOM-1-N16R8（16MB Flash + 8MB 八线 PSRAM）而非 N8R2",
      "date": "2026-09-03",
      "record_path": "docs/decisions/DRV-002-module-n16r8-vs-n8r2.md"
    },
    {
      "decision_id": "DRV-003",
      "summary": "音频前端用 INMP441 数字 I2S 麦克风 + MAX98357A 功放，不用模拟 codec",
      "date": "2026-09-08",
      "record_path": "docs/decisions/DRV-003-audio-frontend.md"
    }
  ],
  "undecided": [
    {
      "item": "外壳用 3D 打印 PLA 还是现成亚克力壳",
      "blocked_on": "user_decision",
      "owner": "用户",
      "needed_by_stage": "10/12"
    },
    {
      "item": "电池容量选 500mAh 还是 1000mAh",
      "blocked_on": "waiting_for_experiment",
      "owner": "AI 协助测续航",
      "needed_by_stage": "10/12"
    },
    {
      "item": "是否在 MVP 里加物理静音按键",
      "blocked_on": "blocked_by_stage_09",
      "owner": "用户",
      "needed_by_stage": "09/12"
    }
  ],
  "risks": [
    {
      "risk": "ESP-SR 唤醒模型在 N16R8 上常驻后 RAM 占用接近上限，可能挤爆对话缓冲",
      "level": "high",
      "mitigation": "先在开发板上实测唤醒+录音并行的内存占用；若超限，砍掉离线指令词只保留唤醒词",
      "status": "open"
    },
    {
      "risk": "嘉立创 PCB 打样周期在月底可能排到 7 天",
      "level": "medium",
      "mitigation": "原理图一通过 ERC 就下单，不等 PCB 布局全部完成",
      "status": "mitigated"
    },
    {
      "risk": "INMP441 对电源纹波敏感，底噪可能偏大",
      "level": "low",
      "mitigation": "模拟电源单独加 LC 滤波，真机录一段底噪验证",
      "status": "open"
    }
  ],
  "verification_log": [
    {
      "stage": "00/12",
      "evidence_level": "doc_review",
      "result": "pass",
      "note": "product-contract.md 已写：一句话/场景/3 条功能/非目标/验收",
      "date": "2026-09-02"
    },
    {
      "stage": "01/12",
      "evidence_level": "doc_review",
      "result": "pass",
      "note": "选型对比表已做，结论 N16R8 模组",
      "date": "2026-09-03"
    },
    {
      "stage": "02/12",
      "evidence_level": "log_observed",
      "result": "pass",
      "note": "ESP-IDF 装好，blink 工程编译烧录，串口日志看到 hello",
      "date": "2026-09-05"
    },
    {
      "stage": "03/12",
      "evidence_level": "doc_review",
      "result": "pass",
      "note": "立创 ERC 零错误，BOM 已导出",
      "date": "2026-09-10"
    },
    {
      "stage": "04/12",
      "evidence_level": "doc_review",
      "result": "pass",
      "note": "DRC 零错误，Gerber 已导出待下单",
      "date": "2026-09-12"
    },
    {
      "stage": "05/12",
      "evidence_level": "real_machine_pass",
      "result": "pass",
      "note": "PCB 与元件已收到，BOM 逐颗核对无误",
      "date": "2026-09-20"
    },
    {
      "stage": "06/12",
      "evidence_level": "real_machine_pass",
      "result": "pass",
      "note": "3.3V/5V 电源轨实测正常，LED 与麦克风逐一验证",
      "date": "2026-09-24"
    },
    {
      "stage": "07/12",
      "evidence_level": "compile_pass",
      "result": "partial",
      "note": "I2S 麦克风驱动编译通过，ESP-SR 唤醒模型尚在移植，未到日志验证",
      "date": "2026-09-28"
    }
  ]
}
```
