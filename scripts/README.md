# scripts/ — 可执行校验层（Anti-Hallucination Tooling）

V3 引入。目的：把「AI 说它检查过了」变成「脚本跑出来是这样」——板级事实外置到 `docs/board-contract.json`，用脚本机器校验，而不是让 LLM 对着自己写的文字喊 PASS。

## 脚本清单

| 脚本 | 作用 | 输入 | 退出码 |
| --- | --- | --- | --- |
| `check_board_contract.py` | 校验板级合同 JSON：必填/必未知断言 + 安全断言（`legacy_hold_boot_during_power_on_forbidden` 必须 true 等） | `docs/board-contract.json` | 0=PASS / 1=FAIL / 2=输入错误 |
| `collect_pins.py` | 从 EDA 网表 CSV **机器提取**真实引脚分配，与板级合同 diff（反 AI 读文字自证） | 网表 CSV + 板级合同 JSON | 0=PASS / 1=有冲突 / 2=输入错误 |
| `power_budget.py` | BOM 电流列求和 + 电源裕量检查（`--margin` 默认 30%） | BOM CSV + `--rated-ma` | 0=PASS / 1=FAIL / 2=输入错误 |
| `check_flash_budget.py` | 分区表求和 vs Flash 容量；Tensor Arena vs PSRAM 余量（默认 25% 余量） | partitions CSV + `--flash-bytes/--psram-bytes/--tensor-arena-bytes` | 0=PASS / 1=FAIL / 2=输入错误 |
| `check_markdown_links.py` | Markdown 死链扫描（本地 + 远程 HEAD；跳过占位符；`--skip-hosts` 跳过需登录域名） | `.md` 文件列表 | 0=PASS / 1=有死链 / 2=输入错误 |

## 快速开始（Windows PowerShell）

```powershell
cd scripts
python check_board_contract.py examples\board-contract.good.json        # PASS=95 FAIL=0, exit 0
python check_board_contract.py examples\board-contract.bad.json          # FAIL=9, exit 1
python collect_pins.py examples\pins.netlist.good.csv examples\board-contract.good.json   # PASS, exit 0
python collect_pins.py examples\pins.netlist.bad.csv examples\board-contract.good.json    # CONFLICT, exit 1
python power_budget.py examples\bom.example.csv --rated-ma 1000          # PASS, exit 0
python check_flash_budget.py examples\partitions.example.csv --flash-bytes 16M --psram-bytes 8M --tensor-arena-bytes 2M  # PASS, exit 0
python check_flash_budget.py examples\partitions.overflow.csv --flash-bytes 16M --psram-bytes 8M --tensor-arena-bytes 2M # FAIL, exit 1
python check_markdown_links.py README.md --skip-hosts waytoagi.feishu.cn # 0=全绿
```

## 与各环节的对接

- **01 选型 / 03 原理图 / 04 PCB**：功耗预算与分区/内存预算用 `power_budget.py` / `check_flash_budget.py` 留证据（见 01 环节「功耗预算前置」）。
- **03b 原理图 → 04 PCB**：用 `collect_pins.py` 对 EDA 导出的网表与板级合同做引脚 diff，替代「AI 读文字后口头 PASS」。
- **任何环节开始前**：先跑 `check_board_contract.py` 确认板级合同自洽；`check_markdown_links.py` 用于本仓库自检（CI 样例见 `skill-ci.yml.example`）。

## CI 接入（可选）

参考 `skill-ci.yml.example`：GitHub Actions 里每次提交跑 `check_board_contract.py examples/board-contract.good.json` 与 `check_markdown_links.py`，保证 Skill 包自身不坏。

## 注意

- 脚本只依赖 Python 标准库，无需 pip 安装（Python 3.8+）。
- 远程链接检查用 GET + 10s 超时；`robots.txt` 禁止自动抓取的站点（如 jihulab 的 JSON）请用 `--skip-hosts` 跳过，人工浏览器复核。
