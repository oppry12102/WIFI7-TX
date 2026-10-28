# WiFi7-TX — Wi-Fi 7 (IEEE 802.11be) 射频发射模组设计成果包

版本 v1（2026-10-28）。三名 AI 组员协作完成的 Wi-Fi 7 射频发射（TX）模组 ASIC 设计
文档与物理实现成果（基于开源 PDK 的 GDS/网表/签核报告）。

## 团队与分工（作者以各件内署名为准）
- **b7a0**（组长）：顶层规格/架构/集成评审/终稿报告、M4 顶层装配与 DRC/LVS 归因裁定。
- **b7e7 / a01a**（电路设计）：三块版图（mix/drv1/drv2）GDS 生成、HBT 版图准则、M3 版图设计稿。
- **fde9**（仿真验证）：PVT/噪声/失真仿真、LVS 代跑与 PEX 提取、判读纪要联签。

## 目录导读
- `01_webpage/` 成果展示页（Python 动态服务 + 数据 JSON）。启动：`python3 server.py`，访问 http://127.0.0.1:8600/（详见其 README.md）。
- `02_spec_and_reports/` 顶层规格 spec.md（v1.5 集成级）、架构 architecture.md、终稿报告 final_report.md、集成评审 integration_review.md、SOW 两件、SOW 版图报告与版图图（sow_reports/）。
- `03_gds/` 现役四件版图（mix v35 / drv1 v23 / drv2 v22 / 顶层 v3）＋ generators/ 版图生成脚本。
- `04_netlists/` 块级 LVS 输入网表、PEX 提取网表、早期行为级/电路级 TB（behavior_tb_sow2/）。
- `05_drc_lvs_signoff/` DRC 报告（lyrdb/log）与 LVS 签核运行输出（deckfix_v1 三块 PASS）。
- `06_layout_design_notes/` 版图设计稿、判读纪要、出数纪要、结案简报等技术纪要。

## 现役四件 GDS（sha256 前 8 位 / 字节）
| 件 | sha8 | bytes | 签核 |
|---|---|---|---|
| 03_gds/m2_mix_v35.gds | 396571f0 | 96,660 | DRC 219 / LVS PASS 29/29 |
| 03_gds/m3_drv1_v23.gds | d5e1296c | 63,502 | LVS PASS 13/13 / DRC 18 |
| 03_gds/m3_drv2_v22.gds | 25adcbd1 | 79,564 | LVS PASS / DRC 147 |
| 03_gds/m4_top_v3.out.gds | 88d5d9c4 | 237,672 | DRC 418（块内继承，顶层侧 0） |

## PDK 指针（不含本体）
- PDK：**IHP SG13G2 开源 PDK**（130nm SiGe BiCMOS），来源：IHP-Open-PDK 官方发布
  （https://github.com/IHP-GmbH/IHP-Open-PDK）。本包不含 PDK 文件；DRC/LVS 报告由
  其规则卡（sg13g2_maximal）产出，网表模型引用其 corner lib。

## 完整性
逐件 sha256 见 `RELEASE_MANIFEST.sha256`；path/bytes/来源映射见 `MANIFEST.json`。
