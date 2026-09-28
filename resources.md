# 资源清单（resources）

本文件汇总 ai-hardware-dev 全包引用的外部资源，按来源类型分类。**所有链接均已在起草时经 web_fetch / 搜索实际验证**（标记 ⚠️ 的为飞书文档内给出、本次未单独浏览器抓取，使用前按需打开确认）。动态信息（价格、交期、认证要求）一律以官方当日为准。

## 一、官方文档（乐鑫 Espressif 与其他官方机构）

| 资源 | 链接 | 用途 | 验证 |
| --- | --- | --- | --- |
| ESP32-S3 官方产品页 | https://www.espressif.com/products/socs/esp32-s3 | 规格、特性、选型（01） | ✅ |
| ESP32-S3 中文数据手册 V2.1 | https://documentation.espressif.com/api/resource/doc/file/AyK0PQ1l/FILE/esp32-s3_datasheet_cn.pdf | 引脚、电气参数（01/03） | ✅ |
| ESP32-S3 产品概述（硬件设计指南·中文） | https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/product-overview.html | 芯片特性、最小系统（01/03/04） | ✅ |
| ESP32-S3 PCB 版图布局（硬件设计指南·中文） | https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/pcb-layout-design.html | 天线净空、叠层、去耦规范（04） | ✅ |
| ESP32-S3 硬件设计指南中文 PDF | https://docs.espressif.com/projects/esp-hardware-design-guidelines/zh_CN/latest/esp32s3/esp-hardware-design-guidelines-zh_CN-master-esp32s3.pdf | 完整硬件设计参考（04） | ✅ |
| ESP-IDF 编程指南（中文） | https://docs.espressif.com/projects/esp-idf/zh_CN/stable/ | 开发、烧录、分区、monitor（07/08） | ✅ |
| ESP-IDF Windows 安装指南（中文） | https://docs.espressif.com/projects/esp-idf/zh_CN/latest/esp32s3/get-started/windows-setup.html | 环境搭建（02） | ✅ |
| esptool 官方文档 | https://docs.espressif.com/projects/esptool/ | 擦除/烧录/下载模式/排错（08） | ✅ |
| esptool ESP32-S3 专页 | https://docs.espressif.com/projects/esptool/en/latest/esp32s3/ | S3 烧录细节（02） | ✅ |
| 乐鑫国内下载站（镜像） | https://dl.espressif.cn/ | GitHub 慢时下载 IDF/工具链（02/07/08） | ✅ |
| ESP 组件注册表（国际站） | https://components.espressif.com/ | 组件搜索（02） | ✅ |
| IDF Component Manager 配置（含中国 storage_url 说明） | https://docs.espressif.com/projects/idf-component-manager/en/latest/use/how_to_configuration.html | 国内组件镜像配置（02） | ✅ |
| Arduino-ESP32 安装文档（含 jihulab 国内镜像） | https://docs.espressif.com/projects/arduino-esp32/en/latest/installing.html | Arduino 环境（02） | ✅ |
| ESP-IDF Fatal Errors 文档 | https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-guides/fatal-errors.html | Guru Meditation/backtrace/看门狗含义（11） | ✅ |
| ESP-IDF Power Management 文档 | https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/system/power_management.html | Light-sleep/Deep-sleep（10） | ✅ |
| MicroPython ESP32 固件下载 | https://micropython.org/download/ESP32_GENERIC/ | MicroPython 固件（02） | ✅ |
| mpremote 命令行文档 | https://docs.micropython.org/en/latest/reference/mpremote.html | MicroPython 工具（02） | ✅ |
| Thonny | https://thonny.org/ | MicroPython 图形 IDE（02） | ✅ |
| PlatformIO | https://platformio.org/ | VSCode 插件与平台（02） | ✅ |
| Node.js 下载（v24 LTS） | https://nodejs.org/en/download | 前端/联调工具（02/09） | ✅ |
| pnpm 安装文档 | https://pnpm.io/installation | 包管理（02/09） | ✅ |
| Silabs CP210x USB 转串口驱动 | https://www.silabs.com/developer-tools/usb-to-uart-bridge-vcp-drivers | 串口驱动（02） | ✅ |
| 沁恒 CH340/CH341 驱动 | https://www.wch.cn/downloads/CH341SER_EXE.html | 串口驱动（02） | ✅ |
| 立创 EDA 专业版 | https://pro.easyeda.com/ | 原理图/PCB/一键下单（03/04/05/06） | ✅ |
| 嘉立创 EDA 专业版用户指南（中文） | https://prodocs.lceda.cn/cn/ | 原理图/PCB 教程（03/04） | ✅ |
| 嘉立创 EDA 专业版快速入门 | https://prodocs.lceda.cn/cn/quick-start.html | 新建工程、导出 Gerber（03） | ✅ |
| 嘉立创 EDA 标准版用户指南 | https://docs.lceda.cn/cn | 标准版教程（03） | ✅ |
| KiCad 官网 | https://www.kicad.org/ | 开源 EDA（03/04） | ✅ |
| KiCad 下载页 | https://www.kicad.org/download/ | 安装（03/04） | ✅ |
| 嘉立创 PCB 打样官网 | https://www.jlc.com/ | 打样下单/工艺/报价（05/06） | ✅ |
| 立创商城 | https://www.szlcsc.com/ | 元器件采购（05/06） | ✅ |
| TP4056 立创商城商品页（含手册） | https://item.szlcsc.com/354934.html | 充电管理选型（10） | ✅ |
| TP4056 原厂数据手册（南京拓微·中文 PDF） | http://www.tp-asic.com/res/tp-asic/pdres/202206/TP4056_42.pdf | 充电参数与公式（10） | ✅ |
| Autodesk Fusion 个人版 | https://www.autodesk.com/products/fusion-360/personal | 外壳建模（10） | ✅ |
| FreeCAD | https://www.freecad.org/ | 开源参数化建模（10） | ✅ |
| Tinkercad | https://www.tinkercad.com/ | 网页版入门建模（10） | ✅ |
| Blender | https://www.blender.org/ | 开源 3D 造型（10） | ✅ |
| Edge Impulse | https://www.edgeimpulse.com/ | 边缘 AI 建模平台（07） | ✅ |
| MDN Web Serial API（英文） | https://developer.mozilla.org/en-US/docs/Web/API/Web_Serial_API | 浏览器串口（09/11） | ✅ |
| MDN Web Bluetooth API（中文） | https://developer.mozilla.org/zh-CN/docs/Web/API/Web_Bluetooth_API | 浏览器 BLE（09/11） | ✅ |

> 说明：`https://components.espressif.cn/`（国内组件镜像）直连返回空（前端渲染），但已由官方组件管理文档与本机激活脚本双重佐证，正文中以环境变量形式使用，不单列资源链接。

## 二、GitHub 开源项目

| 项目 | 链接 | 用途 | 验证 |
| --- | --- | --- | --- |
| TensorFlow TFLite Micro | https://github.com/tensorflow/tflite-micro | MCU 端推理框架（07） | ✅ |
| ESP-DL（乐鑫深度学习库） | https://github.com/espressif/esp-dl | ONNX 量化部署（07） | ✅ |
| ESP-NN（向量指令加速算子） | https://github.com/espressif/esp-nn | S3 推理加速（07） | ✅ |
| ESP-WHO（人脸检测/识别框架） | https://github.com/espressif/esp-who | 视觉示例集（07） | ✅ |
| 小智 AI 语音助手（xiaozhi-esp32） | https://github.com/78/xiaozhi-esp32 | 端到端语音参考工程/复刻对象（00/07/08） | ✅ |
| Serial Studio | https://github.com/Serial-Studio/Serial-Studio | 串口/遥测仪表（09/11） | ✅ |
| CY-CHENYUE 仓库列表 | https://github.com/CY-CHENYUE?tab=repositories | 训练营配套固件与 Skill 源码 | ⚠️ 飞书文档给出，未单独抓取 |
| esp-idf-cy（ESP-IDF 环境 Skill） | https://github.com/CY-CHENYUE/esp-idf-cy | 训练营配套环境搭建 Skill | ⚠️ 飞书文档给出，未单独抓取 |

## 三、中文社区与教程

| 资源 | 链接 | 用途 | 验证 |
| --- | --- | --- | --- |
| 柴火创客学园 M0 零基础智能硬件入门 | https://opc.chaihuo.org/courses/m0 | 用中文让 AI 做硬件的入门课（00） | ✅ |
| 电子工程专辑：ESP32 与 STM32 上运行 TinyML 的区别 | https://www.eet-china.com/mp/a495207.html | 选型参考（01） | ✅ |
| JLCPCB Blog：ESP32 vs Raspberry Pi | https://jlcpcb.com/blog/esp32-vs-raspberry-pi | TinyML vs Edge AI 对比（01） | ✅ |

## 四、训练营（WaytoAGI 第七期 AI 硬件基础训练营）

| 文档 | 链接 | 用途 | 验证 |
| --- | --- | --- | --- |
| 训练营主页 | https://waytoagi.feishu.cn/wiki/YUfhwbwdUiYXtYkCru7cfKaGnWb | 课程总入口（00/01/camp） | ✅ 已抓取 |
| 社区首页（通往 AGI 之路） | https://waytoagi.feishu.cn/wiki/QPe5w5g7UisbEkkow8XcDmOpn8e | 社区门户 | ✅ 已抓取 |
| 第 1 课：从想法到开工：AI 硬件起步指南 | https://waytoagi.feishu.cn/wiki/CvYQwzu4ViaxIgkSEw5cFezBnje | 方向定位、开工四环节 | ✅ 已抓取 |
| 第 2 课：跑通第一条 AI 硬件开发链路 | https://waytoagi.feishu.cn/wiki/OVQ5wz57uiFD0hkutgFcpasFntc | 12 步烧录跑通、原文提示词 | ✅ 已抓取 |
| 第 3 课：AI 键盘哄我上工 & EasyInput 上的实时鼓机 | https://waytoagi.feishu.cn/wiki/F9f5wkfF5ibo3sku3Ppc6u5Tnnf | 鼓机制作指南、复刻+改造作业 | ✅ 已抓取 |

> 训练营资料默认可公开、仅限非商业使用；使用约定与逐字提示词详见 `references/camp-notes.md`。

## 五、本地可复用素材（非链接）

| 路径 | 用途 |
| --- | --- |
| `D:\esp\v5.4.1`（含 activate-idf541.ps1）与 `D:\esp\v5.5.5` | 本机已装的 ESP-IDF 双版本；激活与镜像配置见 02 环节 |
| `D:\硬件耍耍\Waytoagi\easyinput-board-cy\references\board-contract.json` | EasyInput V2.0 板级合同权威副本（board-reference.md 的数据来源） |
| `D:\硬件耍耍\Waytoagi\easyinput-beatbox\docs\course\` | 第 3 课讲义与 PPT 分页稿（camp-notes.md 补充素材） |
| `D:\硬件耍耍\Waytoagi\easyinput-beatbox\docs\host-protocol.md` / `midi-protocol.md` | 串口/协议设计思想参考（09 环节借鉴，不复制正文） |

## 使用注意

- **认证类**（FCC/CE/RoHS/SRRC）：本包不附链接，一律"以机构官网当日要求为准"（见 10 环节）。
- **价格/交期类**：以嘉立创/立创商城官网当日为准。
- **淘宝**：仅作渠道文字说明，未附商品 URL。
- 需要更多提示词与资料时，先读 `prompt-templates.md` 与各环节文件的「资源与延伸」。
