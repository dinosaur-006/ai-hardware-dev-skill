# CHANGELOG

## 3.0.0（V3，2026-09-29）

### 五件事（用户评审指定顺序）

1. **scripts/ 可执行校验层**：新增 5 个脚本（`check_board_contract.py`、`collect_pins.py`、`power_budget.py`、`check_flash_budget.py`、`check_markdown_links.py`）+ 用法说明 + CI 样例 + 9 个样例文件。退出码约定 0=PASS/1=FAIL/2=输入错误。
2. **板级内容去重**：07/08/11 的 EasyInput 硬编码事实全部改为 `<board-contract:*>` 占位引用，具体值只存 `docs/board-contract.json` 与 `board-reference.md`；03「按住 BOOT+上电」矛盾删除，统一以合同 `boot.enter`/`boot.exit` 为准；全包 `D:\硬件耍耍\...` 绝对路径清除。
3. **项目目录与状态统一**：SKILL.md 新增「项目目录布局（唯一权威）」小节；`ai-hardware-team.md` 13 处旧 `project-state/` 路径统一为 `docs/`；stage_map 补 00b/03a、11 改「安全网」；02/prompt-templates 的 `docs/board-reference.md` 统一为 `docs/board-contract.json`；06/07/08 绝对序号统一为「环节 NN」。
4. **烧录授权硬门禁**：08 新增 6 项硬性门禁（显示端口/芯片/完整 MAC/版本/产物/命令 → 等用户原样输入「确认烧录到 XXXX」才写入 → 不默认 erase_flash、不改分区/偏移/设备身份 → 失败唯一允许「保持开机短按一次 BOOT」重试一次 → MAC 只留后四位落盘 → 违反即越权作废）。camp-notes 模板 5 标注与门禁一致；08/11 的「先 erase-flash 再重烧」默认动作改为「有理由才擦、需确认」。
5. **03a 面包板原型验证 + 功耗预算前置**：新增 `references/03a-breadboard-prototype.md`（150 行六部分齐全）；03 顶部加 03a/03b 拆分明细；00 通过标准加「MVP 必须先在一块现成开发板上跑通，再决定是否自画板」；01 前置功耗预算步骤（峰值电流/裕量 ≥30%/bulk 电容/热设计 + 模板 D，引用 power_budget.py/check_flash_budget.py）。

### 顺手小项（评审列出）

- 11 故障库 30+ 处编造百分比（「约 50%」等）改为「高/中/低 + 判据」。
- 料号修正：`ESP32-S3-N16R8` → `ESP32-S3-WROOM-1-N16R8` 全包替换；虚构料号 `SWC38U` 删除，改描述性文字。
- 03 USB-C：补 CC1/CC2 各 5.1kΩ 下拉到 GND（sink 强制）；ESD 改为无条件项（如 USBLC6-2）；按键消抖 100nF 与固件 20ms 对齐说明。
- 04：USB 2.0 FS 等长非强制（强调阻抗连续 + 参考地完整）；天线表述修正（feed 点 + 投影净空，非「悬空」）；四层板「推荐 ≠ 必须」措辞。
- 07：分区表样例补官方语法注释与来源；`D:\esp\...` 路径变量化（`<你的 IDF 安装路径>`）；SRAM 修正（512KB 总数含 cache；Tensor Arena 放 PSRAM 的访问延迟代价）。
- 02：ccache/UTF8 从默认关闭改为「纯英文路径首选、兜底才启用」逻辑翻转。
- LICENSE 双授权：PolyForm Noncommercial 1.0.0（默认，含专利条款）+ Apache-2.0（商业路径需另行授权）；训练营非商业专项约定保留；两份许可全文落盘。
- frontmatter 加 `version: 3.0.0`；description 压缩至约 190 字（触发关键词保留）。
- 新增 `CHANGELOG.md`；提供 `skill-ci.yml.example`。

### 未做（如实声明，非本 V3 范围）

- 评审「不在五件事内」的增强项未做：OTA/固件升级、量产 DFM、预合规滤波预留、成本反推、安全设计专题、JTAG 完整教程。仅以轻量形式并入 08/11 的 JTAG 入口与 brownout 增强。

## 2.0.0（V2，2026-09-28）

- 新增 5 文件：`core/project-state.md`、`core/decision-record.md`、`core/failure-knowledge-base.md`、`core/ai-hardware-team.md`、`references/00-product-translator.md`。
- 修改 7 文件：SKILL.md（路由表 + 5 行）、README.md（目录树）、prompt-templates.md（T13–T18）、references/01（四级主线）、03/04（防幻觉检查表）、11（结构化 FKB 表格）。
- 三项核心设计保留：渐进披露路由、板级合同、证据分级。

## 1.0.0（V1，2026-09-28）

- 初始发布：根 7 文件 + references 13 文件，共 20 文件。
- 12 环节全流程工作流（00 方向 → 11 排障），板级无关规则、意图路由、工作纪律、边界与禁止事项。
- 参考案例板 EasyInput V2.0（ESP32-S3）板级事实速览 + 新板板级知识合同方法。
- 60 条核验通过的资源链接 + 训练营笔记。
