# 09. 软硬件联调（Software-Hardware Integration）

全流程的第 10 步。在固件能单独跑、板端外设单独验证之后（见 `07-firmware-ai.md` / `08-flashing-and-debugging.md`），把"板端事件 → 电脑/手机端可视化"和"电脑/手机命令 → 板端执行"两条链路打通。输入：可烧录固件 + 一个空白联调面板项目；输出：双向通的串口/BLE 链路 + 一份协议文档 + 一份真机验收记录。

## 目标与通过标准

- 目标：建立板端与上位机（电脑浏览器 / Node 面板 / 手机）之间稳定、可观测、可双向命令的通信链路。
- 通过标准：
  - 板端能把按键/传感器/音频事件以 JSON 行协议发到上位机，上位机实时显示。
  - 上位机能发命令（如 `{"t":"led","v":1}`），板端正确执行并回 `ack`。
  - 断线重连后无需重新烧录即可恢复通信。
  - 协议有版本号，新增字段不破坏老客户端。

## 可复制操作与命令

### 联调架构总览

```text
板端 ESP32-S3  <--USB 串口（主信道）-->  电脑 Chrome/Edge（WebSerial）或 Node 面板
板端 ESP32-S3  <--BLE GATT（无线）---->  手机/电脑浏览器（WebBluetooth）
```

- **主信道**：USB 串口（ESP32-S3 原生 USB-Serial/JTAG）。烧录、日志、命令都走它，最稳；先把这条跑通再考虑无线。
- **无线信道**：BLE。做无线演示 / 手机控制时再上，用 GATT 一个 notify 特征上报事件、一个 write 特征收命令。

### 串口协议设计（JSON 行协议）

设计原则（领域事件 JSON、双向开关、状态查询、版本化）：

- UTF-8，一行一条 JSON，`\n` 结尾；非 `{` 开头的行当日志忽略（板端 log 混在流里不崩解析器）。
- 每条消息带 `t`（type）字段区分事件/命令；设备上电先发 `hello`（含协议版本 `v`），再发一次完整 `state`。
- 双向同构：板端→上位机叫"事件"（`key`/`state`/`tick`），上位机→板端叫"命令"（`led`/`ping`）；命令必须回 `ack` 或 `error`。
- 状态查询：上位机连上先发 `{"t":"ping"}`，板端回 `hello` + 全量 `state`。
- 版本化：只加字段、不改老字段语义；要破坏性改动就升 `v`，老客户端忽略它不认识的字段。

示例（板端 → 上位机）：

```json
{"t":"hello","v":1,"name":"my-ai-device"}
{"t":"state","led":0,"vol":100,"btn":0}
{"t":"btn","i":0,"v":1}
```

示例（上位机 → 板端）：

```json
{"t":"led","v":1}
{"t":"ping"}
```

板端回应：

```json
{"t":"ack","cmd":"led","ok":1}
{"t":"error","cmd":"led","msg":"bad value"}
```

### 板端自检：串口打印回环

联调第一步永远是"让板子自己吐数据"。在主循环里加：

```c
printf("{\"t\":\"tick\",\"ms\":%llu}\n",
       (unsigned long long)esp_timer_get_time() / 1000);
```

用串口助手能稳定看到逐行 JSON，就算板端 OK。

### 打开 IDF Monitor（看日志 + 自动解析 backtrace）

PowerShell（在 ESP-IDF 终端环境里）：

```powershell
idf.py -p COM3 monitor
```

macOS/Linux：

```bash
idf.py -p /dev/ttyUSB0 monitor
```

退出 monitor：`Ctrl + ]`（Windows / macOS 相同）。注意：monitor 会占用串口，和 WebSerial / Serial Studio 同时连会失败，**二选一**。

### 查串口号（Windows）

```powershell
Get-PnpDevice -Class Ports | Where-Object {$_.Status -eq 'OK'} | Select-Object FriendlyName
```

macOS/Linux：

```bash
ls /dev/tty.*                      # macOS
ls /dev/ttyUSB* /dev/ttyACM*      # Linux
```

### PC 端假数据注入（板端没好，先跑通上位机）

板子还没好时，用脚本伪造事件喂给 UI。新建目录（**路径用纯英文**，如 `D:\eb-build\host-panel`）：

```powershell
mkdir D:\eb-build\host-panel
cd D:\eb-build\host-panel
npm init -y
```

macOS/Linux 相同命令。写 `mock-ticker.mjs`：

```js
let i = 0;
setInterval(() => {
  process.stdout.write(JSON.stringify({ t: "btn", i: i++ % 4, v: 1 }) + "\n");
}, 500);
```

运行：

```powershell
node mock-ticker.mjs
```

把输出接进同一个解析函数，上位机 UI 没板子也能调。

### 回环测试 + WebSerial 最小连接

在 Chrome/Edge 地址栏打开 `http://localhost` 或任意 https 页面，F12 控制台跑：

```js
const port = await navigator.serial.requestPort();
await port.open({ baudRate: 115200 });

const decoder = new TextDecoderStream();
port.readable.pipeTo(decoder.writable);
const reader = decoder.readable.getReader();
while (true) {
  const { value, done } = await reader.read();
  if (done) break;
  console.log(value); // 板端打印
}
```

发命令：

```js
const encoder = new TextEncoderStream();
encoder.readable.pipeTo(port.writable);
const writer = encoder.writable.getWriter();
await writer.write('{"t":"ping"}\n');
```

断线重连：`navigator.serial.getPorts()` 能拿到之前授权过的端口，插回板子后直接 `port.open()`，不用再弹窗选。

### WebBluetooth（BLE GATT，无线信道）

板端定义一个自定义 Service UUID，内含一个 notify 特征（板端→手机事件）和一个 write 特征（手机→板端命令）。浏览器里：

```js
const device = await navigator.bluetooth.requestDevice({
  filters: [{ services: ['你的服务UUID'] }],
});
const server = await device.gatt.connect();
const service = await server.getPrimaryService('你的服务UUID');

const txChar = await service.getCharacteristic('notify特征UUID');
await txChar.startNotifications();
txChar.addEventListener('characteristicvaluechanged', e => {
  console.log(new TextDecoder().decode(e.target.value));
});

const rxChar = await service.getCharacteristic('write特征UUID');
await rxChar.writeValue(new TextEncoder().encode('{"t":"ping"}\n'));
```

注意：WebBluetooth 只在 Chrome/Edge、且必须 https（或 localhost）下可用；Firefox / Safari 不支持。

### Node.js v24 + pnpm 建联调面板

PowerShell：

```powershell
npm install -g pnpm
cd D:\eb-build
pnpm create vite host-panel --template vanilla
cd host-panel
pnpm install
pnpm dev
```

macOS/Linux：

```bash
npm install -g pnpm
pnpm create vite host-panel --template vanilla
cd host-panel && pnpm install && pnpm dev
```

把上面 WebSerial 代码包成"连接 / 断开 / 发送命令"三个按钮 + 一个事件日志区即可。

### 联调工具与方法论

- **工具**：串口助手推荐 Serial Studio（开源、跨平台、能画曲线、记录 CSV）；临时看日志用 Arduino IDE 串口监视器也行。
- **时间戳对齐**：板端 `printf` 带毫秒时间戳；上位机收到事件也打本地时间，两边对比即知延迟。
- **回环测试**：发 `ping` 等 `ack`，500ms 没回算失败。
- **先各自验证再对接**：① 板端不接上位机，printf 自检事件格式；② 上位机用 mock 数据跑通 UI；③ 再插线对接，发 `ping` 收到 `hello`+`state` 才算 `synced`。

## 可复制 AI 提示词模板

模板 A：设计 JSON 行协议

```text
我在做一个 ESP32-S3 硬件项目，需要设计板端（设备）与电脑浏览器上位机之间的串口通信协议。板端会上报：按键按下/抬起、传感器数值、节拍 tick、电量；上位机会下发：LED 开关、音量、开始/停止。请帮我设计一个"一行一条 JSON、UTF-8、\n 结尾"的文本协议，要求：
1. 每条消息有 "t" 字段区分类型；
2. 设备上电先发 hello（含协议版本 v）和一次完整 state；
3. 上位机命令要有 ack/error 回应；
4. 预留版本扩展方式（只加字段不破坏老客户端）；
5. 给我列出 Device→Host 和 Host→Device 两张消息表，每条配一个 JSON 示例。
用我自己的领域事件命名，不要照搬 MIDI 语义。
```

模板 B：写 WebSerial 连接 / 断线重连代码

```text
用原生 WebSerial API（不依赖第三方库）帮我写一段浏览器代码，实现：
1. 点击按钮请求串口（requestPort），波特率 115200；
2. 持续读取串口流，按 \n 切分，逐行 JSON.parse，解析失败的行（日志）打印到 console 但不崩溃；
3. 提供 send(obj) 方法把对象 JSON.stringify 后加 \n 写出；
4. 监听 disconnect 事件，插回设备时用 navigator.serial.getPorts() 自动重连；
5. 用 TypeScript，带中文注释。
```

模板 C：PC 端 mock 假数据跑通上位机

```text
板端固件还没写完，但我想先把浏览器上位机 UI 跑通。请用 Node.js（ESM，.mjs）写一个 mock 脚本，每隔 300-800ms 随机往 stdout 打印一行 JSON 事件，模拟：按键 {"t":"btn","i":0..3,"v":0/1}、传感器 {"t":"sensor","a":<0-4095>}、心跳 {"t":"tick","ms":<uptime>}。再写一个最小 HTML 页面，用 WebSerial 读真实板子；同时支持一个"mock 模式"开关，开了就用这个脚本/setInterval 的假数据喂同一个解析函数。目标：板子没插也能把 UI 布局调完。
```

## 常见坑

1. **现象**：串口助手能看到碎片，但板端 `printf` 明明是正常字符串。**原因**：波特率不匹配（板子 115200、助手开 9600），或日志行和 JSON 行混在一起没按行切。**解决**：两边统一 115200；上位机按 `\n` 切行，非 `{` 开头的行忽略。
2. **现象**：WebSerial 点"连接"弹窗里看不到板子。**原因**：串口被 IDF Monitor / Serial Studio 占用；或浏览器不是 Chrome/Edge；或页面不是 https/localhost。**解决**：关掉其他占串口的工具；用 Chrome/Edge；本地开发用 localhost。
3. **现象**：板子一插电脑就被 IDF Monitor 抢口，WebSerial 永远连不上。**原因**：`idf.py monitor` 是阻塞占用。**解决**：联调 Web 面板时 `Ctrl+]` 退出 monitor；串口二选一。
4. **现象**：上位机能收板端事件，但发命令板端没反应。**原因**：命令末尾没加 `\n`，板端一直在等行结束；或板端没注册 UART 接收回调。**解决**：写命令必须 `...\n`；板端用行缓冲收满一行再 parse。
5. **现象**：JSON 解析偶尔整个崩、UI 卡死。**原因**：板端 log（如 `I (123) cpu_start:...`）和 JSON 半行切进来。**解决**：`try/catch` 包住 `JSON.parse`，失败行丢弃并计数；板端日志最好走另一个 UART。
6. **现象**：BLE 能扫描到设备，但连接几秒就断。**原因**：没监听 `gattserverdisconnected`、连接后没立刻 `startNotifications`、手机休眠杀后台。**解决**：监听断开事件自动重连；连接成功后第一时间订阅 notify。
7. **现象**：协议加了新字段，老手机 App 全崩。**原因**：老客户端严格解析、遇未知字段报错。**解决**：约定"未知字段忽略"；只加字段不删不改；破坏性改动升 `v` 并在 `hello` 里声明。

## 验收清单

- [ ] 板端每秒 `printf` 一行 JSON 事件，串口助手能稳定看到
- [ ] 上位机（浏览器或 Node 面板）能连上串口，按 `\n` 切行并 `JSON.parse`
- [ ] 上位机发 `{"t":"ping"}`，板端回 `hello` + 完整 `state`
- [ ] 上位机发一个控制命令（如 LED 开关），板端真实执行并回 `ack`
- [ ] 拔掉 USB 再插回，无需重新烧录即可重连（自动或手动点一下连接）
- [ ] 板端 log 行与 JSON 行混在一起时，上位机不崩（try/catch + 忽略非 JSON 行）
- [ ] 协议文档（消息表）已写进 `docs/protocol.md`，含版本号 `v`
- [ ] 没插板子时，mock 数据能跑通上位机 UI
- [ ] BLE 信道（如需要）能 notify 事件、能写命令

## 资源与延伸

- Web Serial API（MDN，英文）：https://developer.mozilla.org/en-US/docs/Web/API/Web_Serial_API （官方文档）
- Web Bluetooth API（MDN，中文）：https://developer.mozilla.org/zh-CN/docs/Web/API/Web_Bluetooth_API （官方文档）
- Serial Studio（开源串口/遥测仪表）：https://github.com/Serial-Studio/Serial-Studio （GitHub）
- Node.js 官网：https://nodejs.org/en （官方）
- pnpm 官网：https://pnpm.io/ （官方）
