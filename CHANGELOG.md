# CHANGELOG（版本变更记录）

本包版本号见 `SKILL.md` frontmatter 的 `version` 字段。所有版本均遵循三项核心设计：渐进披露路由、板级知识合同（board-contract.json 字段级诚实）、证据分级（编译通过 ≠ 烧录成功 ≠ 日志正常 ≠ 真机验收）。

## 3.1.0（当前版）— 第二轮评审内容缺口增强（六项落地）

### 新增（对应评审"内容缺口"表格六项）

- **OTA / 固件升级与设备管理**：07 新增「### 9. OTA 固件升级与版本管理」（otadata/app0/app1 双 bank 分区表、esp_https_ota 要点、升级回滚策略、设备身份与固件版本管理、断点续传与断电安全）；10 新增「### 11. 固件升级与设备管理（产品化视角）」（发布管道/灰度/回滚预案/设备清单/状态上报）
- **量产可制造性（DFM）与测试工装**：04 新增「### 4.8 可制造性设计」（拼版与工艺边、Mark 点、测试点 TP 阵列、ICT/烧录治具、一次通过率目标、10 项自查清单）；05 新增「### 8. DFM 与下单衔接」（下单选项对照 + 收货 DFM 核对）
- **预合规（pre-compliance）**：04 新增「### 4.9 预合规预留」（电源入口 π 型滤波与磁珠位、USB 共模电感/串阻位、天线匹配位、默认贴 0Ω 先手）；10 新增「### 10.1 预合规摸底（送测前先自测）」（摸底动作清单、六类整改手段表：展频/削峰/磁珠/屏蔽等）
- **成本反推（目标售价→选型约束）**：01 新增「## 成本反推（目标售价 → BOM 目标价 → 选型约束）」（反推模板、器件大类预算表、量级折扣/MOQ、落盘 docs/bom-target.md）；10 新增「### 12. 成本反推在量产阶段的应用」
- **安全设计专题**：03 新增「### 3.7 电路安全设计」（反接保护/过流保护/ESD 系统防护/锂电池热失控/看门狗策略 + 轻量 FMEA 表模板）；06 新增「### 3.1 锂电池安全与热失控处置（FMEA 化）」；11 故障库新增安全类条目 #15–18（看门狗循环复位/过流烧保险/PTC 断开/ESD 损 GPIO/锂电池保护板锁定）
- **JTAG 调试完整教程**：08 新增「### 9. JTAG 调试（ESP32-S3 内置 USB-Serial/JTAG 接口）」（OpenOCD/gdb 流程、断点/单步/变量查看、与烧录通道区分）；11 的 JTAG 排障小节补 08 教程指引

### 变更

- SKILL.md `version` 升至 3.1.0；文件清单注释同步标注各环节新增增强小节；frontmatter description 保持精简不加长
- 各增强小节均配「可复制 AI 提示词模板」（01/03/04/07/08/10/11 模板编号续接既有 A/B/C/D），常见坑与验收清单同步增补
- 新增外部链接均经 web.fetch 验证后写入（ESP-IDF OTA 官方文档、JTAG 调试官方文档）

## 3.0.0 — 从"教程"到"可被机器验证的执行系统"

### 新增
- `scripts/` 校验脚本层：`check_board_contract.py`（板级合同 JSON Schema 校验 + 必填/必未知断言）、`collect_pins.py`（EDA 网表提取与合同 diff）、`power_budget.py`（BOM 电流求和 + 裕量检查）、`check_flash_budget.py`（分区表 vs Flash、Tensor Arena vs PSRAM）、`check_markdown_links.py`（链接存活检查）+ `scripts/README.md` 用法说明
- `references/03a-breadboard-prototype.md`：面包板原型验证环节（03 拆分为 03a「面包板原型验证」新文件 + 03b「原理图设计」即原 03-schematic-design.md）
- `CHANGELOG.md`、`LICENSE-PolyForm-Noncommercial-1.0.0.txt`、`LICENSE-Apache-2.0.txt`

### 变更
- 板级内容去重：07/08/11 中硬编码 EasyInput 事实改为 `<board-contract:*>` 占位引用，具体值只存于 board-contract.json
- 项目目录布局统一为唯一权威（docs/ 体系：project-memory.json、board-contract.json、product-contract.md、failure-knowledge-base.md、decisions/），SKILL.md 新增「项目目录布局（唯一权威）」小节
- 烧录授权硬门禁：烧录前必须显示端口/芯片/完整 MAC/版本/产物/命令，等用户原样确认"确认烧录到 XXXX"后才写入；不默认 erase；MAC 只留后四位入档
- LICENSE 由 CC BY-NC 4.0 改为双授权：PolyForm Noncommercial 1.0.0（默认，非商业）+ Apache-2.0（商业路径，需另行授权）
- SKILL.md frontmatter 增加 `version: 3.0.0`；description 压短为触发匹配用
- 00 通过标准增加"MVP 必须先在一块现成开发板上跑通，再决定是否自画板"
- 01 选型前置功耗预算（峰值电流/电源裕量/电容/热设计），引用 power_budget.py / check_flash_budget.py

### 修复（评审 14 条技术错误）
- 03 的"按住 BOOT + 上电"表述与 board-reference 矛盾 → 统一为"以 boot.enter/exit 合同为准"（EasyInput 为短按 BOOT 进下载、关机重开退出、无 RESET 键）
- 03 补 USB-C CC1/CC2 各 5.1kΩ 下拉到 GND（sink 强制）；ESD 保护改为无条件项；按键消抖 100nF 与 07 固件 20ms 消抖对齐
- 04 删除"USB 需等长"伪精确（USB 2.0 FS 无等长要求，强调阻抗连续性/不跨分割/参考地完整）；天线表述改为"feed 点伸出板边、投影区及外侧留净空"；"官方推荐四层板"防放大为"必须 4 层"
- 07 分区表样例修正；D:\esp\v5.4.1 等本机路径改为"你的 IDF 安装路径"变量；512KB SRAM 表述修正（总数含 cache、自由堆远小于此，PSRAM 首次推理延迟显著需写明经验）
- 08 烧录授权硬门禁（见上）；JTAG 调试入口（ESP32-S3 内置 USB-Serial/JTAG）
- 11 故障库删除编造百分比（约 50%/55% → 高/中/低 + 判据）；"先 erase-flash 再重烧"默认动作改为"有理由才擦"；brownout 增强（AI 负载大电流为"反复重启"头号嫌疑：WiFi TX 400mA+、NPU burst、LDO 瞬态）；新增 JTAG 排障小节
- 02 的 IDF_CCACHE_ENABLE=0 / PYTHONUTF8=1 从"默认开"改为"先保证路径纯英文、路径不合法才启用兜底"的逻辑
- 料号修正：ESP32-S3-N16R8 → ESP32-S3-WROOM-1-N16R8 / -WROOM-2-N16R8（SWC38U 查证后处理）
- 清除 resources.md / core/failure-knowledge-base.md / NOTICE 中硬编码本机绝对路径（D:\硬件耍耍\...）
- stage 编号统一（stage_map 与 00b/03a 新环节一致；11 定位为安全网环节而非"非终点"）

## 2.0.0 — 项目执行系统

### 新增
- `core/project-state.md`：项目状态系统（project-memory.json 模板 + 每环节更新纪律）
- `core/decision-record.md`：决策记录（关键选型/方案取舍留痕）
- `core/failure-knowledge-base.md`：失败知识库模板（症状/概率原因/验证/解决/次数）
- `core/ai-hardware-team.md`：AI 硬件团队多角色模式（PM→硬件架构→电气→固件→QA→制造）
- `references/00-product-translator.md`：需求翻译层（人话→工程规格）

### 变更
- 01 平台选型升级为 MCU 级 AI 硬件主线四级分级（Level1 ESP32-S3 入门 → Level2 STM32+NPU → Level3 树莓派 → Level4 Jetson）
- 03/04 增加「AI 必须逐项检查清单（防幻觉）」："ERC/DRC 通过 ≠ 正确"，逐条 PASS/FAIL
- 11 故障库升级为结构化 Failure Knowledge Base 表格
- SKILL.md 路由表、README、prompt-templates 同步扩展

## 1.0.0 — 初始版本

- 全流程 12 环节闭环：方向定义 → 选型 → 环境 → 原理图 → PCB → 打样采购 → 焊接调试 → 固件（含 AI 推理）→ 烧录 → 软硬件联调 → 产品化 → 故障排查
- 三项核心设计：渐进披露路由、板级知识合同（board-reference.md + 新板建合同方法）、证据分级
- 每环节文件含：目标与通过标准 / 可复制操作与命令（Windows 优先）/ 可复制 AI 提示词模板 / 常见坑 / 验收清单
- 板级无关：EasyInput V2.0 仅作参考案例
- 训练营资料引用（WaytoAGI 第七期，非商业约定）见 NOTICE
