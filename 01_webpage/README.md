# WiFi7-TX 设计交付全景 WebUI

无鉴权、只读、服务端渲染的交付展示站。展示 SOW-1（系统/行为级）到 SOW-2（SG13G2 晶体管级）
全案：规格 / 架构 / 电路 / 版图规划 / 网表 / 晶体管级仿真 / 结项证据 / 数据下载。

- 对外：本地服务（`python3 server.py` 后访问 http://127.0.0.1:8600/）
- 端口：8600（壳服务名 `webui`，日志 /data/data/webui.out，pid /data/xuseek/data/webui.pid）
- 依赖：FastAPI + uvicorn + markdown + Pygments（均在 /data/xuseek/.venv 内），**零外链、离线可用**

## 运维

```sh
sh webui/ctl.sh restart|start|stop|status
python3 skills/webui_ctl.py        # 重建数据 + 重启 + 15 页冒烟（技能 webui_ctl）
python3 webui/sitebuild.py --force  # 只重建数据（~2s，产出 data/site.json）
```

## 代码结构

| 文件 | 职责 |
|------|------|
| `webui/sitebuild.py` | 数据管线：扫描 /data/workspace 全案 → `webui/data/site.json`（0.8MB） |
| `webui/server.py` | FastAPI 服务端渲染（14 个路由，无鉴权，取件白名单防穿越） |
| `webui/charts.py` | 纯 Python SVG 图表库（折线/柱/对数轴/阈值线/图例/热力表） |
| `webui/ctl.sh` | 启停（走 /data/ctl.sh 壳服务；先清端口再起，避免 bind 冲突） |
| `webui/data/site.json` | 数据快照（`meta.built_at` 为快照时间，服务按 mtime 自动热加载） |
| `skills/webui_ctl.py` | 已注册技能 `webui_ctl` |

## 路由

| 路由 | 内容 |
|------|------|
| `/` | 总览：KPI 卡、验证矩阵、SOW-2 迭代表、收敛轨迹图 |
| `/spec` | 系统规格 S1~S13 + spec.md 全文 |
| `/docs` `/docs/{slug}` | 文档库 23 篇（规格/架构/评审/电路/结项/判读纪要×5/口径拍板/调研） |
| `/circuit` | 电路参数表（params.csv 147 行）+ 6 张 SVG 图（版图/拓扑） |
| `/layout` | 版图规划：floorplan 大图 + layout_plan.md 全文 |
| `/phys` | **版图实证（SOW-3 + SOW-6）**：两块真实 GDS 的 DRC 轮次违规数 / LVS 状态与提取器件 / 逐网 PEX R·C / 前仿真 vs 后仿真增益，外加 TX5G_AMP2 寄生机理四张图 + 内嵌《HBT 级版图准则》全文；页顶横幅=SOW-6 全链版图实况（v19 收口中，纪要族 phys/top/） |
| `/netlist` `/netlist?p=…` | 34 份网表（v014 定稿 / **v013.1 定稿（v014 实际基线）** / v013 初版 / v011a-r2 投件 / 代跑主版），Pygments 高亮 |
| `/sim` | 仿真总览 |
| `/sim/op` | OP27 工作点：81 deck、锚/定标/i_vcc/温漂四步判据 + 全角矩阵 + 四版本对照 |
| `/sim/sp` `/sim/sp?deck=…` | sp 全 S 谱（27 角 × 61 频点，log 频轴）+ M8 终审统计 |
| `/sim/tran` `/sim/tran?which=mix\|chain&win=zoom\|full` | tran 时域波形（原始 1.4GB 波形定宽抽样 + 包络） |
| `/sim/device` `/sim/device?vce=…` | 器件 d1 corner 网格：fT / gm / β |
| `/sim/linearity` | B1 单板批次：线性度 HD2 / 噪声 PSD / S 参数 / CG |
| `/sim/iter` | v011a→v012→v013→v014 迭代与判读 |
| `/tree` | 全案文件树（交付白名单 221 个文件；凭据/信箱/缓存/deck/原始波形已排除） |
| `/data` | 交付物清单（28 项，sha256 + 下载） |
| `/raw?p=…` | 白名单目录取件（pdk/ design_circuit/ sim_report/ research/ outbox_files/ 及顶层 md） |

## 数据口径（与归档判读逐位一致）

- 迭代表 typ/bcs/wcs 三列 = 判据点 `mix.ntaila` 的 (t125−t27) 残差，**由 op27 CSV 现算**；
  v014 行的「预测」小字 = v013 收口时的线性外推值，仅留痕不参与裁决（2026-10-16 口径修正）。
- 对数轴刻度：`_log_ticks` 入参必须是原始值域（曾因传 log 域导致 log10 二次作用、左缘堆出
  1e-30…1e0 伪刻度，2026-10-16 修复）。
- OP27 判据域 = 5 测点（mix.ntaila / chain.mi.ntaila / chain.lb.ntaila / chain.lb.ntailb /
  lob.ntaila）× 3 corner = 15 点，判据轴 v2500，|Δ| ≤ 6.4mV；
  边角域 v2250/v2750 共 30 点按拍板划 dcvr 备案（v014 11/30 超线）。
- 站上所有数字均由 `sitebuild.py` 从原始 CSV/JSON 现算，不写死结论；
  版本对照（v011a-r2 / v012 / v013 / v014）同样由四份 op27_summary 现算。
