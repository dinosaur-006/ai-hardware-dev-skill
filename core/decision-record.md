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

最终拍板选了什么。一句话说清。

## 备选方案（alternatives）

| 备选 | 优点 | 缺点 |
| --- | --- | --- |
| 方案 A |  |  |
| 方案 B |  |  |

## 取舍理由（why）

为什么选结论这个、为什么不选其他备选。把当时的权衡写透，包括哪些因素权重高、哪些是硬约束。

## 影响面（impact）

这条决策影响了下游哪些设计 / BOM / 固件 / 成本 / 周期；如果以后要推翻它，返工代价有多大。

## 后续验证（follow-up）

计划怎么验证这条决策是对的（在哪一环节、用什么证据级别验收）。
```

### 配套 JSON 片段（用于 project-memory.json 的 decisions_made）

```json
{
  "decision_id": "DRV-NNN",
  "summary": "<一句话结论>",
  "date": "YYYY-MM-DD",
  "record_path": "docs/decisions/DRV-NNN-<短描述>.md"
}
```

### 操作步骤

1. 讨论中出现"选 A 还是 B"、"要不要加这个模块"、"用云还是本地"这类问题时，不要口头过完就翻篇。
2. 用下面"模板 A"让 AI 把讨论固化成一份 `docs/decisions/DRV-NNN-*.md`。
3. 用户拍板后把 status 从 `proposed` 改成 `accepted`，并在 `project-memory.json` 追加 `decisions_made` 条目。
4. 后来决策被推翻时，旧文件 status 改 `superseded`、填 `superseded_by`，**不删除旧文件**（保留推理历史）。

## 可复制 AI 提示词模板

### 模板 A：把一次选型/方案讨论固化成决策记录

```text
我们刚刚讨论了一个硬件方案问题：<用两三句话把问题、讨论过程、各方案说清楚>。
请帮我把它固化成一份决策记录，存到 docs/decisions/ 下：
1. 分配下一个决策编号（先看 docs/decisions/ 里最大的 DRV-NNN，加 1）；
2. 按 core/decision-record.md 的 Markdown 模板写全八个字段：背景 / 结论 / 备选方案（至少 2 个，列表格列优缺点）/ 取舍理由 / 影响面 / 后续验证；
3. 结论先写 "待用户拍板"，status 设为 proposed；
4. 写完后告诉我文件路径，并提醒我：拍板后要把 status 改成 accepted，还要在 project-memory.json 的 decisions_made 里追加一条引用。
注意：不要替我拍板，备选方案要客观写优缺点，不要因为我倾向某方案就把别的备选写得一无是处。
```

### 模板 B：决策回顾（项目中途检查关键决策是否仍成立）

```text
请读取 docs/decisions/ 目录下所有 status 为 accepted 的决策记录，结合 project-memory.json 当前的 current_stage（现在是第 <NN/12> 环），给我一份决策回顾：
1. 逐条列出每条决策（id + 一句话结论 + 拍板日期）；
2. 针对每条，结合当前阶段出现的新事实（如实测性能、供应链变化、成本变化、需求变化），判断它现在是：仍然成立 / 需要补充验证 / 可能已不成立；
3. 对"可能已不成立"的决策，说明触发它动摇的新事实是什么、推翻它的返工代价（看 impact 字段）有多大、建议现在就开新决策取代它还是继续观察；
4. 最后给出建议：哪几条决策值得现在就重新评估。
只基于已落盘的决策记录和 project-memory.json 回答，不要凭印象补细节。
```

## 常见坑

1. **现象**：决策记录里只有"结论：选 N16R8"，没有备选、没有理由。**原因**：把决策记录当成了结论便签。**解决**：模板强制 alternatives 至少 2 个方案、why 必须写取舍；只有结论没有备选的记录打回重写——那不是决策，是公告。
2. **现象**：决策做了，但没人跟踪 impact，等 PCB 都打样了才发现"当初选的芯片功耗比预估高 3 倍，电池方案要重做"。**原因**：决策时没写影响面，事后没人复盘。**解决**：每条决策必须写 impact（影响了哪些下游设计、推翻代价多大）；到了相关环节，用模板 B 回顾一次。
3. **现象**：会上/聊天里口头定了"就用这个吧"，没写下来，两周后换个会话谁都不记得。**原因**：口头决策不落盘。**解决**：任何"拍板"动作发生的当场，就用模板 A 生成记录；`project-memory.json` 的 decisions_made 只认落盘文件，不认聊天记录。
4. **现象**：把"教程里默认这么接"当成了自己做过决策，写进决策记录。**原因**：没真正比较过备选，只是照抄惯例。**解决**：决策记录的门槛是"至少比较过 2 个备选"；照抄惯例的不算决策，直接写进 `board-contract.json` 或原理图注释即可，不要占用 DRV 编号。
5. **现象**：决策被推翻后直接删旧文件，未来看到新决策不知道它是怎么演进来的。**原因**：把记录当草稿纸。**解决**：旧记录永不删除，status 改 `superseded` 并填 `superseded_by`，保留完整推理链。

## 验收清单

- [ ] `docs/decisions/` 目录存在，且每条关键决策单独一个 `DRV-NNN-*.md` 文件
- [ ] 每条记录八字段齐全：id / date / context / decision / alternatives / why / impact / status
- [ ] alternatives 至少列了 2 个备选，并各有优缺点
- [ ] why 字段写清了取舍理由与硬约束，不只是"感觉这个好"
- [ ] impact 字段说明了影响的下游设计与返工代价
- [ ] status 取值合法（proposed / accepted / superseded），superseded 记录填了 superseded_by
- [ ] `project-memory.json` 的 `decisions_made` 里每条都能在 `docs/decisions/` 找到对应文件（record_path 真实存在）
- [ ] 没有把"默认选择/照抄惯例"包装成决策记录
- [ ] 项目进行到 07/12 之后至少做过一次决策回顾（模板 B），或明确记录"尚未回顾"
- [ ] 旧决策被取代时原文件保留、未删除

## 附：示例决策记录（虚构，仅示范字段填法）

> 以下两条为示例，**不是真实项目记录**，仅示范八字段怎么填。

### 示例 1：DRV-001 主控平台（ESP32-S3 vs 树莓派 Zero）

- id: DRV-001
- date: 2026-09-02
- status: accepted

#### 背景（context）

用户零基础，第一次做硬件，希望两周内能点亮并跑通语音交互；预算有限，不熟悉 Linux 与驱动开发；产品形态是常插桌面的小设备，希望低功耗。

#### 结论（decision）

选 ESP32-S3 单片机路线，不用树莓派。

#### 备选方案（alternatives）

| 备选 | 优点 | 缺点 |
| --- | --- | --- |
| ESP32-S3（MCU + FreeRTOS） | 上电即跑、无操作系统；功耗低；开发生态对新手友好（Arduino/ESP-IDF）；板载 Wi-Fi/BLE；训练营主线就是它 | 算力有限，不能跑大模型，AI 推理只能走轻量本地模型 + 云端 |
| 树莓派 Zero 2W（Linux） | 算力强，能直接跑 Python 大模型 SDK；生态成熟 | 功耗高、开机慢（数十秒）；需要 Linux 驱动与音频调试；成本高（约 80 元 + 外设）；零基础者排障门槛高 |
| K210 / 其他 NPU 板子 | 本地视觉算力强 | 资料少、社区小、新手遇到问题难查；与语音助手方向不匹配 |

#### 取舍理由（why）

本项目核心交互是"唤醒 + 云端对话"，真正的 AI 在云端，本地只需要录音、唤醒、播放——这正好是 ESP32-S3 的甜区。树莓派的算力优势用不上，反而背上 Linux 调试、功耗、开机慢三座山。两周周期内，ESP32-S3 路线的可完成性远高于树莓派。

#### 影响面（impact）

- 整条技术栈锁定在 ESP-IDF / Arduino：固件语言是 C/C++ 或 MicroPython，不能直接跑 Python 大模型 SDK。
- 所有音频处理必须走 I2S 外设驱动，不能依赖 Linux ALSA。
- 产品化阶段要考虑低功耗睡眠设计（ESP32-S3 原生支持），这是树莓派做不到的。
- 推翻代价：换平台等于重新画板、重新写固件，几乎是推倒重来——所以这条决策必须在 01/12 环节定死，不然后面全白做。

#### 后续验证（follow-up）

在 02/12 环境搭建环节确认 Windows 上 ESP-IDF 能顺利编译烧录；若环境装不上再回头评估树莓派路线（但概率低，因为训练营主线就是 ESP32-S3）。

---

### 示例 2：DRV-002 主控模组选型（N16R8 vs N8R2）

- id: DRV-002
- date: 2026-09-03
- status: accepted

#### 背景（context）

项目要做一个桌面语音助手，需要常驻唤醒模型 + 录音缓冲 + Wi-Fi。手头预算 60 元以内，希望一次打样成功，不想因为内存不够返工 PCB。

#### 结论（decision）

选 ESP32-S3-WROOM-1-**N16R8**（16MB Flash + 8MB 八线 PSRAM）。

#### 备选方案（alternatives）

| 备选 | 优点 | 缺点 |
| --- | --- | --- |
| N16R8（16MB Flash / 8MB PSRAM） | PSRAM 充裕，能塞下 ESP-SR 唤醒模型 + 对话缓冲；社区资料多 | 单价比 N8R2 贵约 8 元；Flash 用不满 |
| N8R2（8MB Flash / 2MB PSRAM） | 便宜约 8 元； footprint 相同，PCB 不用改 | 2MB PSRAM 跑 ESP-SR 后余量紧张，唤醒+录音并行可能 OOM；后期要换芯片就得重打样 |
| N16R2（16MB Flash / 2MB PSRAM） | Flash 够大 | PSRAM 仍是 2MB，没解决内存瓶颈，价格优势不明显 |

#### 取舍理由（why）

这是第一个硬件项目，最大风险不是省 8 元，而是"模型跑不动 → 换芯片 → 重打样"的返工。PSRAM 是硬约束（ESP-SR 官方推荐 Octal PSRAM），Flash 8MB 其实也够用，但 N8R2 与 N16R8 引脚兼容，多花 8 元买内存余量，比赌一把划算。

#### 影响面（impact）

- BOM：模组单价 +8 元，整板 BOM 约 42 元。
- PCB：N16R8 与 N8R2 封装相同，PCB 不用为这条决策改布局。
- 固件：可以按 PSRAM 充裕来规划内存，不必一开始就裁剪模型。
- 推翻代价：若将来要降级到 N8R2，PCB 不用改，只改固件内存配置，返工代价低——这也是选封装兼容模组的原因。

#### 后续验证（follow-up）

在 07/12 固件环节，实测 ESP-SR 唤醒 + I2S 录音并行时的 PSRAM 占用；若占用超过 6MB 说明决策正确，若远低于预期则下次可考虑 N8R2 降本。
