# 决策记录（decision-record）

本文件是 AI 硬件开发 Skill V2 新增的"决策留痕"层。定位：**把"为什么选这个芯片、为什么用这个方案"落成书面记录，关键决策不靠聊天记录回忆**。

硬件项目周期长、换会话多，一个月后再问"当初为什么选 N16R8 而不是 N8R2"，没人记得。决策记录就是为了回答这类问题：当时的背景是什么、比了哪几个备选、为什么这么取舍、影响了哪些下游设计、现在这条决策还成不成立。

> 与其他文件的关系：`project-memory.json` 的 `decisions_made` 数组里每条都通过 `decision_id` 引用本系统里的一条决策记录，`record_path` 指向 `docs/decisions/<id>.md`。**没有落盘留痕的决策，不允许写进 `decisions_made`。**

## 目标与通过标准

- 目标：每个影响成本、周期、硬件设计、架构走向的关键决策都有一份留痕，包含背景、备选、取舍理由、影响面，可被未来任意时刻回溯。
- 通过标准：
  - 每条关键决策单独一个 Markdown 文件，存放在 `docs/decisions/` 目录，文件名即决策 ID（如 `DRV-001-chip-choice.md`）。
  - 记录至少包含八个字段：id、date、context（背景）、decision（结论）、alternatives（备选方案）、why（取舍理由）、impact（影响面）、status（proposed/accepted/superseded）。
  - 结论必须至少比较过 2 个备选；没比较过备选的"默认选择"不算决策，不许走决策记录流程。
  - 决策被推翻时，旧记录不删除，把 status 改成 `superseded`，并指向取代它的新决策 ID。
  - 项目中途做一次"决策回顾"，检查关键决策在当前阶段是否仍成立。

## 可复制操作与命令

### 存放约定

- 目录：项目 `docs/decisions/`（若不存在则创建）。
- 命名：`DRV-NNN-<短描述>.md`，`NNN` 从 001 开始递增，不复用。
- 一条决策一个文件；不要把多条决策塞进一个文件。
- 与 `project-memory.json` 的对接：决策被用户拍板后，立刻在 `project-memory.json` 的 `decisions_made` 里追加一条 `{decision_id, summary, date, record_path}`。

### 决策记录 Markdown 模板（直接复制）

```markdown
# DRV-NNN：<一句话决策标题>

- id: DRV-NNN
- date: YYYY-MM-DD
- status: proposed | accepted | superseded
- superseded_by: <若 status=superseded，填新决策 ID，否则留空>

## 背景（context）

当时面临什么问题、约束是什么（成本 / 周期 / 性能 / 功耗 / 团队能力 / 已有物料）。

## 结论（decision）

最终选择是什么，一句话说清。

## 备选方案（alternatives）

| 方案 | 优点 | 缺点 | 为什么没选 |
| --- | --- | --- | --- |
| A | | | |
| B | | | |

## 取舍理由（why）

权衡了什么：成本 / 周期 / 性能 / 功耗 / 生态 / 学习成本 / 供应链。

## 影响面（impact）

影响哪些后续环节：原理图电源方案、PCB 层数、固件内存预算、外壳尺寸、认证范围……

## 回顾（review，可选）

在哪个环节回头看这条决策是否仍成立；若不成立，指向新决策 ID。
```

### 决策记录 JSON 片段（同步给 project-memory.json）

```json
{
  "decision_id": "DRV-001",
  "summary": "选 ESP32-S3-WROOM-1-N16R8 模组（16MB Flash + 8MB PSRAM）",
  "date": "2026-09-29",
  "record_path": "docs/decisions/DRV-001-chip-choice.md"
}
```

> 路径约定：`record_path` 等 JSON 内部路径一律相对项目根目录书写（如 `docs/decisions/DRV-001-xxx.md`），与 `core/project-state.md` 一致。

## 可复制 AI 提示词模板

**模板 A：生成决策记录（关键选型/方案决策后留痕）**

```text
我们刚才决定：<结论，如：选 ESP32-S3 N16R8 模组>。
背景：<为什么走到这个选择，如：需要 8MB PSRAM 跑 1MB 内模型、16MB Flash 装固件+模型>。
备选方案：<列出认真比较过的备选与理由，如：N8R2（内存不够跑该模型）、树莓派（功耗与成本过高、启动慢）>。
取舍理由：<权衡点，如：成本/功耗/生态/学习成本>。
影响面：<这个决策影响哪些后续环节，如：03 原理图电源方案、07 固件内存预算、10 外壳尺寸>。
请按 core/decision-record.md 的模板把这条决策固化写入 docs/decisions/ 目录，并同步到 project-memory.json 的 decisions_made。
```

**模板 B：决策回顾（中途回顾关键决策是否仍成立）**

```text
项目进行到 <环节 N>。请只读 docs/decisions/ 下的所有决策记录和 docs/project-memory.json，逐条回顾每条决策：① 当时选择的前提现在是否仍成立；② 有没有新信息（实测/成本/生态变化）使原决策不再最优；③ 是否需要新建决策或标记 superseded。输出一张表：决策 ID / 原结论 / 当前是否成立 / 建议动作。
```

## 常见坑

1. **现象**：project-memory.json 里写了决策，但 docs/decisions/ 没有对应文件。**原因**：跳过留痕直接写状态。**解决**：决策必须先落盘再引用（见目标与通过标准）。
2. **现象**：一条记录塞了三个决策，回溯时分不清。**原因**：没有一决策一文件。**解决**：按存放约定拆分。
3. **现象**："默认选择"也走了决策流程，记录了"没比较过备选"的伪决策。**原因**：把不假思索的默认当决策。**解决**：至少比较 2 个备选才算决策；没比较的写"沿用默认，未做正式决策"。
4. **现象**：决策被推翻后旧记录被删除。**原因**：想保持目录干净。**解决**：保留旧记录、status 改 superseded、指向新决策——历史是资产。
5. **现象**：记录只写了结论没写背景和备选，一个月后看不懂"为什么"。**原因**：省略了最重要的部分。**解决**：背景与备选是必须字段，宁可多写。

## 验收清单

- [ ] 每条关键决策在 `docs/decisions/` 有独立文件，文件名即决策 ID
- [ ] 八字段齐全：id/date/context/decision/alternatives/why/impact/status
- [ ] 至少比较过 2 个备选方案
- [ ] `project-memory.json` 的 decisions_made 已同步（引用 id + record_path）
- [ ] 被推翻的决策标记 superseded 并指向新决策
- [ ] 中途做过一次决策回顾

## 资源与延伸

- 项目状态：`core/project-state.md`
- 失败知识库：`core/failure-knowledge-base.md`
- 项目目录布局（唯一权威）：`SKILL.md`「项目目录布局」
