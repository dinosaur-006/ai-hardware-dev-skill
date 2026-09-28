# 01. 平台/芯片选型（Platform & Chip Selection）

全流程的第 2 步。根据产品合同选择芯片平台。**主线：MCU 级 AI 硬件开发主线（四级分级）**——从零基础入门到重算力边缘，按"算力量级 / 系统形态"分 Level 1–4 逐级升级，**不要把"AI 硬件"等同于"ESP32"**：ESP32-S3 只是入门第一站（Level 1）。输入：`docs/product-contract.md`；输出：一行选型结论（含 Level 等级）+ 采购板型确认。

## 目标与通过标准

- 目标：用"算力、外设、AI 能力、成本、功耗、生态"六维对比，为产品选到够用且不后悔的平台。
- 通过标准：
  - 能说出选型结论与一句话理由，并说清本项目落在四级主线的哪一级（Level 1–4）。
  - 零基础 / 无明确重算力需求的项目默认落在 Level 1（ESP32-S3），并确认板子内存/Flash/引脚余量够跑 MVP。
  - 选型结论附带功耗预算数字（峰值电流、电源裕量 ≥30%、bulk 电容、热设计），并跑 `scripts/power_budget.py` / `scripts/check_flash_budget.py` 留证据。
  - 需求超出 Level 1 时，能正确路由到 Level 2（STM32+NPU）/ Level 3（树莓派 Linux）/ Level 4（Jetson）；特殊需求（超低功耗视觉唤醒）知道备注 K210。
  - 已确认采购渠道有现货（见 `05-manufacturing-and-sourcing.md`）。

## MCU 级 AI 硬件开发主线（四级分级）

AI 硬件不是"只有 ESP32"一条路，而是一条按算力量级与系统形态逐级上升的四级主线。**零基础一律从 Level 1 起步**，需求涨上来再按本节末尾的"升级路线"上跳，不要一上来就买最贵的板。

| 级别 | 平台 | 定位 | AI 能力形态 | 一句话场景 |
| --- | --- | --- | --- | --- |
| **Level 1（入门主线）** | ESP32-S3 | MCU + WiFi/BLE，零基础第一选择 | MCU 级 TinyML：TFLite Micro / ESP-DL / ESP-NN（KB–MB 级量化模型） | 语音助手、鼓机、传感器盒子、桌面小机器人 |
| **Level 2（MCU 升级）** | STM32 + NPU（如 STM32N6 系列） | 从 MCU 往上一步：带 NPU 的工业 MCU | NPU 硬件视觉加速 + ST Edge AI / Cube.AI，工业生态强 | 需要更强视觉/AI 加速、又要工业级实时与生态 |
| **Level 3（Linux 全栈）** | Raspberry Pi（Pi 4/5） | 微型 Linux 电脑 | Python AI 全栈：TensorFlow / PyTorch、摄像头视觉、大模型对话 | 复杂摄像头视觉、多进程服务、LLM 对话原型 |
| **Level 4（重算力边缘）** | Jetson | AI 边缘计算模组/开发板 | 完整 AI 框架，GPU 数十~数百 TOPS 级 | 机器人 / 自动驾驶原型、目标检测、SLAM |

> 特殊需求备注：超低功耗电池视觉唤醒（关键词/图像唤醒、一次性拍照识别）可看 K210，但生态较窄、中文资料少，非该场景不要选。

**Level 1 为什么是零基础第一站**：ESP32-S3 双核 240MHz 带向量指令（SIMD，加速神经网络与信号处理）、内置 2.4GHz WiFi + BLE、原生 USB、TinyML 生态成熟（TFLite Micro / ESP-DL / ESP-NN）、板级成本约 ¥30-80、社区与中文教程量最大、且是训练营教具（EasyInput V2.0 即 ESP32-S3）。

## 选型四级路由（先问量级，再落 Level）

先回答两个问题：**① 需要什么算力量级？② 需要裸 MCU 实时系统，还是 Linux 全栈系统？** 再按下表落到 Level：

1. WiFi/BLE 联网 + 音频/按键/传感器类实时交互，模型在 KB–MB 级（语音唤醒、关键词识别、传感器分类、鼓机）→ **Level 1：ESP32-S3**
2. MCU 级实时，但视觉/AI 推理需要硬件 NPU 加速，或要工业级生态（STM32 工具链、工业外设）→ **Level 2：STM32N6 等 STM32+NPU**
3. 要跑 Linux 全栈 + Python AI（大模型对话、复杂摄像头视觉、多进程服务、需要 pip 装库）→ **Level 3：树莓派（Pi 4/5）**
4. 重算力机器人 / 自动驾驶原型（实时目标检测、SLAM、多路摄像头）→ **Level 4：Jetson**

## 升级路线：从 Level 1 起步，按需上跳

主线用法是 **Level 1 起步 → 需求升级时按 Level 2 / 3 / 4 迁移**，不是一次选到底。判定"何时升级"：

- 模型体积 **> 1MB**，或需要 Linux 生态（Python / pip / 多进程 / 大模型对话）→ 升到 **Level 3（树莓派）**。
- 需要 **NPU 视觉加速**（图像推理帧率/精度要求明显超出 ESP32-S3 软件向量指令），但仍要 MCU 级实时与工业生态 → 升到 **Level 2（STM32+NPU）**。
- 需要 **重算力**（多路视觉、SLAM、机器人实时感知）→ 升到 **Level 4（Jetson）**。
- 不要反过来：把树莓派当 MCU 用（实时按键/音频节拍）；实时交互仍应留给 Level 1/2，Linux 板可用串口/BLE 与 MCU 板配合。

## 六维对比表（按四级主线重排）

| 维度 | Level 1：ESP32-S3 | Level 2：STM32+NPU（STM32N6） | Level 3：树莓派 Pi 4/5 | Level 4：Jetson |
| --- | --- | --- | --- | --- |
| 定位 | MCU + WiFi/BLE（入门主线） | 带 NPU 的工业 MCU | 微型 Linux 电脑 | AI 边缘计算板 |
| 算力 | 双核 240MHz + 向量指令 | Cortex-M 级 MCU + 片上 NPU | 四核 1.5-2.4GHz | GPU/加速器，数十~数百 TOPS 级 |
| AI 方式 | TinyML：TFLite Micro / ESP-DL / ESP-NN，KB-MB 级模型 | NPU 硬件加速视觉，ST Edge AI / Cube.AI | TensorFlow / PyTorch，MB–十 MB 级 | 完整 AI 框架（CUDA 生态） |
| 联网 | 内置 WiFi/BLE | 无（需外接模块） | 网口/外接 WiFi | 内置 WiFi |
| 典型推理功耗 | <300mW | mW~低功耗 | 3-5W+ | 5-15W+ |
| 板级成本 | ¥30-80 | ¥100-300 级（按 NPU 系列） | ¥300-700 | ¥1000+ |
| 开发难度（AI 辅助） | 低：生态大、教程多、训练营教具 | 中高：STM32 工具链 + NPU 部署 | 中：Linux 环境 | 高：环境复杂、需散热 |
| 适合场景 | 语音/传感/按键类实时硬件 | 工业视觉加速、强实时控制 | Python 全栈原型、摄像头、LLM 对话 | 视觉机器人原型、SLAM |

> K210 不进四级主表：仅"超低功耗电池视觉唤醒"这一特殊需求可用（KPU 硬件加速量化 CNN、mW 级功耗、板级约 ¥40-100），但生态较窄、中文资料少，非该场景不要选。

## 可复制操作与命令

本环节没有命令，操作是"填一张选型自检表"：

1. 打开上面的六维对比表，按产品合同逐维打勾。
2. 确认 ESP32-S3 模组规格：优先选 **ESP32-S3-WROOM-1-N16R8**（乐鑫真实全称；后缀 N16R8 = 16MB Flash + 8MB PSRAM，八线 PSRAM），TinyML 模型才放得下；预算受限时至少 N8R8/N8R2（与 N16R8 封装兼容，PCB 不用改）。
3. **功耗预算前置（选型时就算，不要等画板/打样才算）**：选型结论必须附带功耗预算数字——
   - 峰值电流：WiFi TX（ESP32-S3 约 400mA+ 量级）、AI 推理 burst、麦克风+功放同时工作时的瞬时峰值；
   - 电源额定与裕量：LDO/充电管理额定电流 ≥ 峰值，并留 ≥30% 裕量（或按电池/USB 能力按需）；
   - 电容容量：电源入口放足够 bulk 电容应对瞬态峰值，防止 WiFi 一发射就掉压复位；
   - 热设计：持续大电流（如线性充电、LDO 压差大）时算散热，必要时换开关方案。
   - 用脚本留证据：`scripts/power_budget.py`（把 BOM 电流列求和、检查电源裕量）、`scripts/check_flash_budget.py`（分区/内存预算）。**选型结论里要写清峰值电流与裕量数字，并跑脚本留证据**，不要只写"够用"。
4. 确认板子引脚余量：列出现需外设（按键、编码器、LED、麦克风、扬声器、传感器……），对照板子引出脚（新板建合同方法见 `board-reference.md`）。
5. 把结论写进 `docs/product-contract.md` 的"平台"一节（含功耗预算数字）。

## 可复制 AI 提示词模板

模板 A：帮我选型（主模板，按四级路由）

```text
我正在做一个 <产品描述>。我是零基础、AI 辅助开发。请先判断两个问题：① 需要什么算力量级（KB-MB 级 TinyML / 需要 NPU 视觉加速 / Linux Python 全栈 / 重算力机器人）；② 需要裸 MCU 实时系统还是 Linux 全栈。然后按"MCU 级 AI 硬件开发四级主线"（Level 1 ESP32-S3 / Level 2 STM32+NPU 如 STM32N6 / Level 3 树莓派 / Level 4 Jetson）推荐我该落在哪一级，并按"算力、外设需求、AI 能力、成本、功耗、生态"六维说明理由；如果落在 Level 1（ESP32-S3），请说明该选哪个模组（如 N16R8）和理由。
```

模板 B：评估模型能否在 ESP32-S3 上跑

```text
我要在 ESP32-S3（<8MB PSRAM / 16MB Flash>）上跑 <模型或任务描述>。请评估：需要什么量级的模型、是否需要 INT8 量化、用 TFLite Micro 还是 ESP-DL 更合适、预计推理延迟量级、内存是否够，并给出结论与替代方案（如降采样率、缩小模型、改树莓派）。
```

模板 C：板级核对（买板前后都能用）

```text
我用的开发板是 <板名>，规格：<粘贴板子规格，如 SoC/内存/Flash/引出脚>。我要做的产品是 <描述>，需要这些外设：<清单>。请核对：① 内存/Flash 是否够跑 MVP（含 <模型/音频缓冲区等>）；② 引脚是否够用、有没有复用冲突；③ 有无明显不合适之处。请给出"够/不够/注意事项"三列结论。
```

模板 D：选型时做功耗预算（功耗预算前置）

```text
我在为 <产品名> 选平台（初步定 ESP32-S3-WROOM-1-N16R8），外设包括：<WiFi 联网、I2S 麦克风、MAX98357A 功放、WS2812、I2C 传感器、按键>，供电方式是 <USB 5V / 锂电池 + TP4056>。请帮我做一份功耗预算：① 估算各外设稳态电流与峰值电流（特别列出 WiFi TX 400mA+ 量级、AI 推理 burst、麦克风+功放同时工作的峰值）；② 汇总整机峰值与稳态；③ 所选 LDO/充电管理额定电流是否 ≥ 峰值、裕量是否 ≥30%；④ 电源入口需要多大 bulk 电容应对瞬态、防止 WiFi 发射掉压；⑤ 持续大电流时 LDO/充电管理的散热要不要换开关方案。最后用表格给出"器件/典型电流/峰值电流/备注"，并给出结论：现有电源方案够不够、要改什么。这份数字会写进选型结论并跑 scripts/power_budget.py 留证据。
```

## 常见坑

1. **现象**：只看"算力大"选了 Jetson。**原因**：被宣传吸引，忽略价格、功耗、环境复杂度。**解决**：第一个项目用 ESP32-S3；真需要重算力时，先树莓派做原型，再考虑 Jetson。
2. **现象**：选了 ESP32 老型号（原版 ESP32 / ESP32-C3）跑 AI。**原因**：以为"ESP32 都一样"。**解决**：选 ESP32-S3——带向量指令，且 N 系列模组有大 PSRAM。
3. **现象**：忽略 PSRAM/Flash 容量，模型放不下。**原因**：只关注芯片不关注模组后缀。**解决**：选 ESP32-S3-WROOM-1-N16R8（16MB Flash + 8MB PSRAM）；模型大小见模板 B。
4. **现象**：被"AI 加速器/KPU"宣传迷惑，买回生态差的板子没教程。**原因**：硬件能力 ≠ 可开发性。**解决**：优先生态大、中文资料多的平台；K210 只在明确电池视觉唤醒场景使用。
5. **现象**：把树莓派当 MCU 用（做实时按键、音频节拍）。**原因**：Linux 非实时、功耗高、上电慢。**解决**：实时交互/低功耗任务给 ESP32-S3，Linux 全栈任务给树莓派，两者可用串口/BLE 配合。
6. **现象**：不查库存与价格就下单。**原因**：忽略供应链。**解决**：选型时顺手查嘉立创/淘宝现货与价格（见 `05-manufacturing-and-sourcing.md`）。

## 验收清单

- [ ] 已按六维对比表完成选型，并写明本项目落在四级主线的哪一级（Level 1–4）
- [ ] 选型结论一句话已写入 `docs/product-contract.md`（如"Level 1 选 ESP32-S3：WiFi/BLE 内置、TinyML 生态成熟、约 ¥50、训练营教具"）
- [ ] 若落在 Level 1，已确认模组规格（优先 ESP32-S3-WROOM-1-N16R8）够放 MVP 模型
- [ ] 已确认板子引脚余量（外设清单 vs 引出脚）
- [ ] **已做功耗预算前置**：峰值电流（WiFi TX 400mA+、AI burst、外设同时工作）、电源额定与 ≥30% 裕量、bulk 电容、热设计已算清并写入选型结论
- [ ] 已跑 `scripts/power_budget.py`（BOM 电流求和+裕量）与 `scripts/check_flash_budget.py`（分区/内存）留证据
- [ ] 已按"何时升级"判定自查：模型 >1MB / 需要 Linux 生态是否该升 Level 3；需要 NPU 视觉加速是否该升 Level 2；需要重算力是否该升 Level 4
- [ ] 已确认超低功耗视觉唤醒等特殊需求是否需备注 K210
- [ ] 已确认采购渠道有现货
- [ ] 已为当前板建立/引用板级知识合同（见 `board-reference.md`）

## 资源与延伸

- ESP32-S3 官方产品页（规格与特性）：https://www.espressif.com/products/socs/esp32-s3 （官方）
- ESP32-S3 中文数据手册（V2.1）：https://documentation.espressif.com/api/resource/doc/file/AyK0PQ1l/FILE/esp32-s3_datasheet_cn.pdf （官方）
- ESP32-S3 产品概述（ESP 硬件设计指南，中文）：https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/product-overview.html （官方）
- ESP32 vs 树莓派：IoT/AI/嵌入式与 PCB 项目平台对比（含 TinyML vs Edge AI 对比表）：https://jlcpcb.com/blog/esp32-vs-raspberry-pi （社区/英文）
- ESP32 与 STM32 上运行 TinyML 的区别与选择（中文）：https://www.eet-china.com/mp/a495207.html （社区/中文）
- STM32N6 产品页（Level 2：带 NPU 的 STM32，官方）：https://www.st.com/en/microcontrollers-microprocessors/stm32n6-series.html （官方）
- Raspberry Pi 官网（Level 3：Pi 4/5 产品页）：https://www.raspberrypi.com/ （官方）
- NVIDIA Jetson 官网（Level 4：边缘 AI 模组）：https://developer.nvidia.com/embedded/jetson-modules （官方）
- 训练营第 1 课（教具 EasyInput V2.0 即 ESP32-S3）：https://waytoagi.feishu.cn/wiki/YUfhwbwdUiYXtYkCru7cfKaGnWb （训练营）
