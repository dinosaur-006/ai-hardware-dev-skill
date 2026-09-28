# 01. 平台/芯片选型（Platform & Chip Selection）

全流程的第 2 步。根据产品合同选择芯片平台。**主线：ESP32-S3**（AI 硬件入门的默认第一选择）；树莓派 / K210 / STM32 / Jetson 作为速览分支，只在明确需求下切换。输入：`docs/product-contract.md`；输出：一行选型结论 + 采购板型确认。

## 目标与通过标准

- 目标：用"算力、外设、AI 能力、成本、功耗、生态"六维对比，为产品选到够用且不后悔的平台。
- 通过标准：
  - 能说出选型结论与一句话理由。
  - 主线程项目明确落在 ESP32-S3，并确认板子内存/Flash/引脚余量够跑 MVP。
  - 特殊需求（重算力视觉 / 工业强实时 / 超低功耗视觉唤醒）能正确转到速览分支。
  - 已确认采购渠道有现货（见 `05-manufacturing-and-sourcing.md`）。

## 选型决策树（条件路由）

1. 产品需要 WiFi/BLE 联网 + 音频/按键/传感器类实时交互（语音助手、鼓机、传感器盒子、桌面小机器人）→ **ESP32-S3（主线）**
2. 要跑 Linux 全栈 + Python AI（大模型对话、复杂摄像头视觉、多进程服务）→ **树莓派（Pi 4/5）**
3. 要电池供电的超低功耗视觉唤醒（关键词/图像唤醒、一次性拍照识别）→ **K210**
4. 工业级、强实时控制、特殊外设接口（PLC、电机、汽车电子）→ **STM32**
5. 重算力机器人 / 自动驾驶原型（目标检测、SLAM）→ **Jetson**

主线 ESP32-S3 的选择理由：双核 240MHz 带向量指令（SIMD，加速神经网络与信号处理）、内置 2.4GHz WiFi + BLE、原生 USB、TinyML 生态成熟（TFLite Micro / ESP-DL / ESP-NN）、板级成本约 ¥30-80、社区与中文教程量最大、且是训练营教具（EasyInput V2.0 即 ESP32-S3）。

## 六维对比表

| 维度 | ESP32-S3（主线） | 树莓派 | K210 | STM32 | Jetson |
| --- | --- | --- | --- | --- | --- |
| 定位 | MCU + WiFi/BLE | 微型 Linux 电脑 | 视觉 MCU | 工业 MCU | AI 边缘计算板 |
| 算力 | 双核 240MHz + 向量指令 | 四核 1.5-2.4GHz | 双核 400MHz + KPU | 按系列（Cortex-M 等） | GPU 数百 GFLOPS 级 |
| AI 方式 | TinyML：TFLite Micro / ESP-DL，KB-MB 级模型 | TensorFlow / PyTorch，MB 级 | KPU 硬件加速量化 CNN | ST Edge AI / Cube.AI | 完整 AI 框架 |
| 联网 | 内置 WiFi/BLE | 网口/外接 | 无（需外接） | 无（需外接） | 内置 WiFi |
| 典型推理功耗 | <300mW | 3-5W+ | mW 级 | 低 | 5-15W+ |
| 板级成本 | ¥30-80 | ¥300-700 | ¥40-100 | ¥30-150 | ¥1000+ |
| 开发难度（AI 辅助） | 低：生态大、教程多、训练营教具 | 中：Linux 环境 | 中：生态较窄 | 中高：工具链重 | 高：环境复杂 |
| 适合场景 | 语音/传感/按键类实时硬件 | Python 全栈原型、摄像头 | 电池视觉唤醒 | 工业/强实时 | 视觉机器人原型 |

## 可复制操作与命令

本环节没有命令，操作是"填一张选型自检表"：

1. 打开上面的六维对比表，按产品合同逐维打勾。
2. 确认 ESP32-S3 模组规格：优先选 **N16R8**（16MB Flash + 8MB PSRAM，八线 PSRAM），TinyML 模型才放得下；预算受限时至少 N8R8/N8R2。
3. 确认板子引脚余量：列出现需外设（按键、编码器、LED、麦克风、扬声器、传感器……），对照板子引出脚（新板建合同方法见 `board-reference.md`）。
4. 把结论写进 `docs/product-contract.md` 的"平台"一节。

## 可复制 AI 提示词模板

模板 A：帮我选型（主模板）

```text
我正在做一个 <产品描述>。我是零基础、AI 辅助开发。请按"算力、外设需求、AI 能力、成本、功耗、生态"六个维度，帮我对比 ESP32-S3 / 树莓派 / K210 / STM32 / Jetson，给出明确推荐和理由；如果推荐 ESP32-S3，请说明该选哪个模组（如 N16R8）和理由。
```

模板 B：评估模型能否在 ESP32-S3 上跑

```text
我要在 ESP32-S3（<8MB PSRAM / 16MB Flash>）上跑 <模型或任务描述>。请评估：需要什么量级的模型、是否需要 INT8 量化、用 TFLite Micro 还是 ESP-DL 更合适、预计推理延迟量级、内存是否够，并给出结论与替代方案（如降采样率、缩小模型、改树莓派）。
```

模板 C：板级核对（买板前后都能用）

```text
我用的开发板是 <板名>，规格：<粘贴板子规格，如 SoC/内存/Flash/引出脚>。我要做的产品是 <描述>，需要这些外设：<清单>。请核对：① 内存/Flash 是否够跑 MVP（含 <模型/音频缓冲区等>）；② 引脚是否够用、有没有复用冲突；③ 有无明显不合适之处。请给出"够/不够/注意事项"三列结论。
```

## 常见坑

1. **现象**：只看"算力大"选了 Jetson。**原因**：被宣传吸引，忽略价格、功耗、环境复杂度。**解决**：第一个项目用 ESP32-S3；真需要重算力时，先树莓派做原型，再考虑 Jetson。
2. **现象**：选了 ESP32 老型号（原版 ESP32 / ESP32-C3）跑 AI。**原因**：以为"ESP32 都一样"。**解决**：选 ESP32-S3——带向量指令，且 N 系列模组有大 PSRAM。
3. **现象**：忽略 PSRAM/Flash 容量，模型放不下。**原因**：只关注芯片不关注模组后缀。**解决**：选 N16R8（16MB Flash + 8MB PSRAM）；模型大小见模板 B。
4. **现象**：被"AI 加速器/KPU"宣传迷惑，买回生态差的板子没教程。**原因**：硬件能力 ≠ 可开发性。**解决**：优先生态大、中文资料多的平台；K210 只在明确电池视觉唤醒场景使用。
5. **现象**：把树莓派当 MCU 用（做实时按键、音频节拍）。**原因**：Linux 非实时、功耗高、上电慢。**解决**：实时交互/低功耗任务给 ESP32-S3，Linux 全栈任务给树莓派，两者可用串口/BLE 配合。
6. **现象**：不查库存与价格就下单。**原因**：忽略供应链。**解决**：选型时顺手查嘉立创/淘宝现货与价格（见 `05-manufacturing-and-sourcing.md`）。

## 验收清单

- [ ] 已按六维对比表完成选型
- [ ] 选型结论一句话已写入 `docs/product-contract.md`（如"选 ESP32-S3：WiFi/BLE 内置、TinyML 生态成熟、约 ¥50、训练营教具"）
- [ ] 已确认模组规格（优先 N16R8）够放 MVP 模型
- [ ] 已确认板子引脚余量（外设清单 vs 引出脚）
- [ ] 已检查特殊需求是否需要切换分支（树莓派/K210/STM32/Jetson）
- [ ] 已确认采购渠道有现货
- [ ] 已为当前板建立/引用板级知识合同（见 `board-reference.md`）

## 资源与延伸

- ESP32-S3 官方产品页（规格与特性）：https://www.espressif.com/products/socs/esp32-s3 （官方）
- ESP32-S3 中文数据手册（V2.1）：https://documentation.espressif.com/api/resource/doc/file/AyK0PQ1l/FILE/esp32-s3_datasheet_cn.pdf （官方）
- ESP32-S3 产品概述（ESP 硬件设计指南，中文）：https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/product-overview.html （官方）
- ESP32 vs 树莓派：IoT/AI/嵌入式与 PCB 项目平台对比（含 TinyML vs Edge AI 对比表）：https://jlcpcb.com/blog/esp32-vs-raspberry-pi （社区/英文）
- ESP32 与 STM32 上运行 TinyML 的区别与选择（中文）：https://www.eet-china.com/mp/a495207.html （社区/中文）
- 训练营第 1 课（教具 EasyInput V2.0 即 ESP32-S3）：https://waytoagi.feishu.cn/wiki/YUfhwbwdUiYXtYkCru7cfKaGnWb （训练营）
