# AI 提示词模板汇总（prompt-templates）

本文件把 ai-hardware-dev 各环节文件里的可复制 AI 提示词模板汇总在一起，分两部分：

- **第一部分：高频通用模板（全文可直接复制）**——跨环节反复使用、最值得先存的 18 个（含 V2 项目执行系统模板）。
- **第二部分：全量模板索引**——按环节列出全部模板名与使用场景，完整全文在各环节文件（`references/NN-*.md`）的「可复制 AI 提示词模板」一节。
- **训练营原文模板**（7 条，逐字摘录自第 1/2 课）见 `references/camp-notes.md`「训练营可复用提示词模板」。

用法：给 Trae / 豆包 / Claude Code / Codex / DeepSeek Harness 等任一种 agent 直接粘贴即可；`<占位符>` 替换成你的真实信息。所有模板都站在"AI 干活、你判断"的 vibecoding 视角。

## 第一部分：高频通用模板（全文）

### 通用排查类

**T1. 日志喂 AI 排查（故障排查 11 环节，最常用）**

```text
我在做一个 ESP32-S3（ESP-IDF）硬件项目，串口 monitor 输出如下，设备在 <描述现象，如：开机 3 秒后自动重启>。请帮我分析：
1. rst 复位原因是什么、属于哪一类（上电/看门狗/异常/软复位）；
2. Guru Meditation Error 的类型和大概在哪一行；
3. backtrace 里哪个函数最可疑；
4. 给出下一步排查建议（具体到加哪条日志/查哪个配置）。
先给结论和假设，不要直接改代码。
日志原文：
"""
<粘贴从上电到复现的完整日志>
"""
我最近的改动：<git diff 或口头描述>
```

**T2. 编译报错回贴排查（环境搭建 02 环节）**

```text
我在用 ESP-IDF 5.4.1 编译一个 ESP32-S3 工程，工程路径是 D:\eb-build\my-device（纯英文）。我已经做了这些环境设置：PYTHONUTF8=1、IDF_CCACHE_ENABLE=0、组件镜像走 components.espressif.cn。下面是 idf.py build 的完整报错日志（含最后 80 行）：
<粘贴报错>
我的板级合同（引脚/PSRAM/Flash/外设）见 docs/board-reference.md：
<粘贴板级合同要点>
请按"错误根因 → 证据 → 最小修复命令"三步回答；不要一次改五个地方，先给最可能的那一条。
```

**T3. 串口日志解读（烧录调试 08 环节）**

```text
我的 ESP32-S3 固件烧录成功了（esptool 校验通过），但 monitor 里看到的是：
<粘贴 monitor 日志，包括 Guru Meditation / Backtrace / panic / W (xxx) boot: 这些行>
请帮我判断：这是启动早期 panic（bootloader/分区/flash 配置问题）还是运行时崩溃（代码/内存问题）？根据 Backtrace 给出定位思路，并告诉我每条关键日志是什么意思。
```

### 板级事实类

**T4. 让 AI 先读板级合同再写代码（环境搭建 02 环节）**

```text
接下来我们要在这块板上写固件，请先阅读我的板级合同文件 docs/board-reference.md（里面写了 SoC、模组 N16R8、PSRAM、引出脚分配、按键/LED/音频引脚、串口下载方式）。在写任何代码之前，先复述你对"哪些脚已被占用、哪些脚空闲、下载模式怎么进"的理解，跟我确认无误后再开始。
```

**T5. 为新板建板级知识合同（board-reference.md）**

```text
我新买了一块开发板 <板名>，这是它的资料：
<粘贴产品页规格 / 引脚图 / 原理图要点 / 丝印照片描述>
请按以下 JSON schema 起草一份 board-contract.json（字段：schema_version/contract_id/aliases/soc/psram/flash/antenna/pins/power/boot/usb/led/battery/audio/debug_uart0/reserved），
要求：① 引脚用功能名做键、GPIO 编号做值；② 资料里没有的信息填 null 并在字段旁注明"资料缺失，需实测"；③ 不要用 EasyInput 或其他板的引脚替我猜测。
```

### 硬件动作类

**T6. 烧录失败诊断（烧录调试 08 环节）**

```text
我在 Windows PowerShell 下用 <idf.py flash / esptool.py> 烧录 ESP32-S3，命令是：<粘贴完整命令>。
报错原文：
<粘贴 esptool 完整输出，尤其是 Connecting failed / A fatal error occurred / Hash of data does not match>
我的板子是 EasyInput V2.0（无 RESET 键，开机状态短按 BOOT 进入下载模式，退出要重上电）。
请按"端口/驱动 → 下载模式 → 供电/线 → 分区与 flash 模式 → 固件本身"的顺序，列出最可能的 3 个原因和对应验证命令，不要让我瞎试。
```

**T7. 上电调试 SOP 陪跑（焊接调试 06 环节，第一次通电必用）**

```text
我准备第一次给这块新板上电。请你扮演一位严格的硬件老师，一步步带我走完上电 SOP，每一步我回报现象你再让我下一步：
板子：<2 层 ESP32-S3，5V USB 供电，板上有 TP4056 锂电池充电、MAX98357A 功放、INMP441 麦克风>
我手里有：万用表、可调电源（可限流）、USB 线。
请从「目检 → 不通电测电源对地 → 限流上电 → 测电压轨 → 逐外设」逐步骤问我，告诉我每一步正常读数应该是多少、超过多少就该断电。
```

**T8. 焊接质量自查（焊接调试 06 环节）**

```text
我刚焊完一块 ESP32-S3 板。请你当我的焊接质检助手，根据我下面的描述，帮我判断焊点是否合格、漏了哪些检查：
- 我焊了哪些件：<列一下：阻容/排针/USB/主控/麦克风模块/功放…>
- 烙铁温度：<约 350°C>，用的是 <刀头/尖头>，焊锡 <有铅 0.8mm>
- 我看到的可疑点：<举例：U1 第 4 脚旁边有点亮、R12 看起来发暗…>
请给我：① 按元件类型的检查要点清单；② 哪些现象一定是虚焊/桥连；③ 下一步该用万用表哪一档、测哪两个点。
```

### 联调与选型类

**T9. WebSerial 连接/断线重连代码（软硬件联调 09 环节）**

```text
用原生 WebSerial API（不依赖第三方库）帮我写一段浏览器代码，实现：
1. 点击按钮请求串口（requestPort），波特率 115200；
2. 持续读取串口流，按 \n 切分，逐行 JSON.parse，解析失败的行（日志）打印到 console 但不崩溃；
3. 提供 send(obj) 方法把对象 JSON.stringify 后加 \n 写出；
4. 监听 disconnect 事件，插回设备时用 navigator.serial.getPorts() 自动重连；
5. 用 TypeScript，带中文注释。
```

**T10. 评估并接入 TFLite Micro INT8 推理（固件 AI 07 环节）**

```text
我要在 ESP32-S3（8MB PSRAM / 16MB Flash）上做 <关键词唤醒 / 音频分类 / 手势图像分类>。已训练好模型 <模型名>。
请帮我：① 评估用 TFLite Micro + ESP-NN 还是 ESP-DL 更合适；② 给出 INT8 量化后模型体积、Tensor Arena 大小、推理延迟量级的估算；③ 写出在 ESP-IDF 里初始化 interpreter、分配 tensor arena（放 PSRAM）、喂入 <音频帧/图像帧>、调用 Invoke 并打印 top-1 类别的完整示例代码；④ 提醒内存不够时如何降配。
```

**T11. 外壳建模需求描述（产品化 10 环节）**

```text
我是零基础、用 AI 辅助做硬件的新手。我要给我的产品做一个 3D 打印外壳，请把下面这段模糊描述转成一份可以在 Fusion 360 里照着做的建模步骤清单（含尺寸、公差、分件方式）：
产品：<一句话产品描述>
主板尺寸：<长×宽×高 mm，如 51×27×8mm>，安装孔距：<如 M3，孔距 40×20mm>
需要开的口：<Type-C 口、电源按键、音量键、麦克风孔、扬声器网孔、天线开窗>
电池：<1 节 18650 / 具体 LiPo 尺寸 mm>
目标：<桌面摆放 / 手持 / 挂绳>
材料：<PLA / PETG>
请给出：1) 整体外形尺寸建议；2) 上盖/底壳分件与固定方式；3) 每个开口的位置与留量；4) 容易被我漏掉的结构（散热、防误触、电池固定）。
```

**T12. 评估产品想法（方向定义 00 环节，起步必用）**

```text
我是一个零基础、用 AI 辅助开发（vibecoding）的硬件新手，只有一块 <开发板名>（<板子规格>）。请帮我评估下面这个产品想法，并从"开发难度、元器件成本、能否用 MCU 实现、最快可验证的最小版本"四个维度给出建议和改造方案：
产品想法：<一句话描述>
目标用户：<谁>
核心功能：<3-5 条>
```

### 项目执行系统类（V2）

**T13. 多角色模式启动（AI 硬件团队，说"我要做产品"时用）**

```text
我要做一个 AI 硬件产品：<一句话描述>。请以「AI 硬件团队」多角色模式驱动这个项目：
1. 先按 core/ai-hardware-team.md 的分工表，声明本次要启用的角色与顺序：Product Manager → Hardware Architect → Electrical Engineer → Firmware Engineer → QA Engineer → Manufacturing Engineer；
2. 每个角色只处理自己职责内的环节文件（PM 管 00/需求翻译，架构师管 01，电气管 03/04/05，固件管 02/07/08，QA 管各验收清单与 11，制造管 05/10）；
3. 角色之间通过交付物交接（product-contract → 选型结论 → 原理图/PCB/BOM → 固件/烧录证据 → 真机验收记录），交接物必须落盘到项目文件，不允许口头交接；
4. 每个角色交付前先读自己的环节文件的验收清单，逐项自检后再交给下一个角色；
5. 任何角色不得替其他角色做决策（如 QA 不能替 PM 改需求），产品方向与取舍最终由我拍板。
先从 Product Manager 开始：请读 references/00-direction-and-definition.md 和 references/00-product-translator.md，帮我产出产品合同与需求翻译表。
```

**T14. 初始化项目状态（project-state，启动任何项目必用）**

```text
请按 core/project-state.md 的 project-memory.json 模板，为我的新项目 <项目名> 初始化项目状态文件：
1. 字段：project_name=<项目名>、current_stage="00/12"、product_contract、board_contract 指向对应文件路径；
2. decisions_made 初始为空，undecided 列出此刻所有未定项（含"谁决策"：等用户 / 等实验）；
3. risks 列出起步阶段我能预见的风险（如板级事实未确认、模型跑不动），每项给等级和缓解；
4. 把初始化结果写盘为 <项目目录>/docs/project-memory.json，并在回复里复述：项目现在在哪、定了什么、还有什么没定。
```

**T15. 每完成一个环节就更新状态（project-state，纪律核心）**

```text
我刚完成 <环节名>（第 <N> 环节）的验收清单，结果：<各验收项 PASS/FAIL 摘要，FAIL 项写原因>。
请更新项目状态文件 docs/project-memory.json：current_stage 改为 "<N+1>/12"；把本环节确定的决策追加进 decisions_made（引用对应 decision-record 的 id）；把本环节新出现的未定项和风险同步进 undecided / risks；把本次验收结果追加进 verification_log（含证据级别：编译通过/烧录成功/日志正常/真机验收）。
更新后，用一句话列出"从上一次更新到这次"的差异（阶段变化、新增决策、新增风险），再给下一步建议。
```

**T16. 需求翻译（人话→工程规格，00 之后 01 之前）**

```text
我要做一个 <一句话产品描述>。请按 references/00-product-translator.md 的需求翻译表模板，把这句话翻译成工程规格：
1. 逐条拆解功能（输入/处理/输出/交互/通信/供电/状态反馈）；
2. 每个功能给技术需求与硬件映射（如"语音输入 → 麦克风 → 模拟 MEMS+ADC 或数字 I2S 麦克风"）；
3. 每行标优先级（P0 必需 / P1 想要 / P2 以后），并列出"未确定项"（如：本地 AI 还是云端 AI？电源用 USB 还是锂电池？）；
4. 不要直接跳到具体芯片/开发板——选型留给下一环节（01）；
5. 翻译完用一段话复述你的工程理解，把"需要我决策的未确定项"单独列出来问我。
```

**T17. 生成决策记录（decision-record，关键选型/方案决策后留痕）**

```text
我们刚才决定：<结论，如：选 ESP32-S3 N16R8 模组>。
背景：<为什么走到这个选择，如：需要 8MB PSRAM 跑 1MB 内模型、16MB Flash 装固件+模型>。
备选方案：<列出认真比较过的备选与理由，如：N8R2（内存不够跑该模型）、树莓派（功耗与成本过高、启动慢）>。
取舍理由：<权衡点，如：成本/功耗/生态/学习成本>。
影响面：<这个决策影响哪些后续环节，如：03 原理图电源方案、07 固件内存预算、10 外壳尺寸>。
请按 core/decision-record.md 的模板把这条决策固化写入 docs/decisions/ 目录，并同步到 project-memory.json 的 decisions_made。
```

**T18. 排障后沉淀失败知识库（failure-knowledge-base，每次排障后必用）**

```text
刚解决了一个硬件问题，请按 core/failure-knowledge-base.md 的条目格式把它结构化沉淀：
症状：<一句话，可检索>
可能原因（带概率估计与依据）：<如：供电不足 60%（曾 3 次复现）；虚焊 30%（目检可疑）；固件 bug 10%（日志未见）>
验证方法：<可操作步骤，如：万用表测 3.3V 对 GND、示波器看波形>
解决：<最终修复方式>
已发生次数：<本次是第几次>
相关环节：<如：06 焊接调试 / 08 烧录>
请写入 docs/failure-knowledge-base.md（与 core 模板同格式），并在 project-memory.json 的 risks 里把已缓解的风险勾掉。
```

## 第二部分：全量模板索引

| 环节 | 模板 | 使用场景 | 完整全文 |
| --- | --- | --- | --- |
| 00 方向定义 | A 评估产品想法 | 起步：评估想法可行性 | `references/00-direction-and-definition.md` |
| 00 | B 生成产品合同 | 把想法写成 product-contract.md | 同上 |
| 00 | C 砍 MVP 边界 | 防止范围失控 | 同上 |
| 00b 需求翻译 | A 人话→规格翻译 | 想法转工程规格（T16） | `references/00-product-translator.md` |
| 00b | B 反向确认 | AI 复述工程理解待确认 | 同上 |
| 00b | C 缺口提问 | 未确定项补齐 | 同上 |
| 01 选型 | A 帮我选型（四级分级） | MCU 级 AI 硬件主线 Level1-4 选型 | `references/01-platform-selection.md` |
| 01 | B 评估模型能否跑 | 模型 vs PSRAM/Flash 预算 | 同上 |
| 01 | C 板级核对 | 买板前后核对规格 | 同上 |
| 02 环境 | A 环境体检 | 装完环境逐项自检 | `references/02-environment-setup.md` |
| 02 | B 编译报错回贴排查 | 编译报错（高频） | 同上（T2） |
| 02 | C 多版本切换脚本 | IDF 5.4.1/5.5.5 并存 | 同上 |
| 02 | D 让 AI 先读板级合同 | 写代码前对齐板事实 | 同上（T4） |
| 03 原理图 | A 最小系统原理图清单 | 生成必装模块清单 | `references/03-schematic-design.md` |
| 03 | B 外设接线表 | 生成接线核对表 | 同上 |
| 03 | C 原理图审查员 | 画完自查 ERC 风险 | 同上 |
| 03 | D 读数据手册辅助 | 看芯片手册重点 | 同上 |
| 03 | E 原理图防幻觉检查 | 逐项检查（电源/LDO/去耦/晶振/USB/天线/地） | 同上 |
| 04 PCB | A 布局分区方案 | 生成布局分区 | `references/04-pcb-layout.md` |
| 04 | B 设计规则参数表 | 填 EDA 规则 | 同上 |
| 04 | C PCB 审查 | 走线完自查 | 同上 |
| 04 | D 发厂前检查清单 | 导出 Gerber 前核对 | 同上 |
| 04 | E PCB 防幻觉检查 | 逐项检查（DRC 通过≠正确） | 同上 |
| 05 打样采购 | A BOM 拆分工 | SMT 贴 vs 手贴 | `references/05-manufacturing-and-sourcing.md` |
| 05 | B 阻容取值审查 | 核对被动元件取值 | 同上 |
| 05 | C 下单前自检 | 防止拍错板 | 同上 |
| 06 焊接调试 | A 焊接质量自查 | 焊完质检 | `references/06-soldering-and-hardware-debug.md`（T8） |
| 06 | B 上电 SOP 陪跑 | 第一次通电 | 同上（T7） |
| 06 | C 故障定位引导 | 板不工作时排查树 | 同上 |
| 07 固件 AI | A 生成外设驱动 | 喂板级合同写驱动 | `references/07-firmware-ai.md` |
| 07 | B 接入 TFLite Micro INT8 | AI 推理接入 | 同上（T10） |
| 07 | C 模型转换流水线 | ONNX→TFLite→C 数组 | 同上 |
| 07 | D WiFi 与实时任务共存 | 任务划分设计 | 同上 |
| 08 烧录调试 | A 烧录失败诊断 | 贴 esptool 输出 | `references/08-flashing-and-debugging.md`（T6） |
| 08 | B 串口日志解读 | 贴 monitor 输出 | 同上（T3） |
| 08 | C 最小自检代码 | 烧录后确认外设工作 | 同上 |
| 09 联调 | A 设计 JSON 行协议 | 协议设计 | `references/09-software-hardware-integration.md` |
| 09 | B WebSerial 连接代码 | 浏览器连串口 | 同上（T9） |
| 09 | C PC 端 mock 假数据 | 板子没到先调 UI | 同上 |
| 10 产品化 | A 外壳建模需求 | 生成建模步骤 | `references/10-productization.md`（T11） |
| 10 | B 电池续航选型计算 | 电池与续航估算 | 同上 |
| 10 | C 认证路径咨询 | 自用/售卖认证路线 | 同上 |
| 10 | D 量产成本估算 | 10/100/1000 台成本 | 同上 |
| 11 排障 | A 日志喂 AI | 贴日志分析（最高频） | `references/11-troubleshooting.md`（T1） |
| 11 | B 现象描述模板 | 硬件症状五层排查 | 同上 |
| 11 | C 硬件 vs 软件二分 | 不知道哪边问题 | 同上 |
| 11 | D 排障后沉淀 FKB | 把排障结论结构化沉淀（T18） | 同上 + `core/failure-knowledge-base.md` |
| 项目状态 | A 初始化项目状态 | 启动项目建 project-memory.json（T14） | `core/project-state.md` |
| 项目状态 | B 每环节后更新状态 | 完成验收后更新+列差异（T15） | 同上 |
| 项目状态 | C 状态汇报 | "项目现在到哪了" | 同上 |
| 决策记录 | A 生成决策记录 | 选型/方案决策留痕（T17） | `core/decision-record.md` |
| 决策记录 | B 决策回顾 | 中途回顾关键决策是否仍成立 | 同上 |
| 失败知识库 | A 排障后沉淀 | 症状/概率原因/验证/解决/次数（T18） | `core/failure-knowledge-base.md` |
| 失败知识库 | B 查询匹配 | 新症状先查 FKB 按概率排序 | 同上 |
| 失败知识库 | C 概率校准 | 新证据后更新概率与次数 | 同上 |
| AI 团队 | A 多角色模式启动 | "我要做产品"时启用（T13） | `core/ai-hardware-team.md` |
| AI 团队 | B-G 六角色卡 | PM/架构/电气/固件/QA/制造各一卡 | 同上 |
| 板级合同 | A 起草新板合同 | 新板建 contract.json | `board-reference.md`（T5） |
| 板级合同 | B 实测验证清单 | 建合同后实测 | 同上 |
| 板级合同 | C 冲突处理 | 文档与实物不符 | 同上 |
| 训练营 | 模板 1-7（7 条） | 训练营原文提示词（含烧录前人工确认授权流程） | `references/camp-notes.md` |

## 训练营原文模板说明

训练营第 1/2 课课件里有多条逐字可用的提示词（共 7 条，全部保留在 `references/camp-notes.md`），与本包各环节模板互补，重点推荐：

- **模板 1 / 2（第 1 课）**：开工前让 AI"只读对齐"——通读资料、识别板型与工具链、复述理解后再动手。与本包 T4 同源，更严格。
- **模板 3–6（第 2 课）**：把"只读验身 → 人工确认 → 写入 → 正常重启 → 功能验收"固化成流程模板，含烧录前显示端口/芯片/MAC、等用户原样确认"确认烧录到 XXXX"再写入的安全纪律。
- **模板 7**：按训练营方法整理的可复用框架，适用于任何板型的"只读对齐 → 最小改动 → 真机验收"流程。
