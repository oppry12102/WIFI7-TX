# 变更面留档 · 裁定五 cdl 重提验收六判据器（fde9 2026-10-18T03:1xZ）

## 触发
b7a0（组长）2026-10-18T03:00:38Z《M5 口径甲回执收讫，R1~R4 裁决如下（新增裁定五：cdl 重提验收六判据）》
——「重提件到货先对表再跑门；六判据全过 → 门1/门2 直接跑；任一不过 → 停线带原始数据报我」。

## 新增（不动任何既有标称值/裁定口径/门限/b7e7 件）
| 件 | 作用 |
|---|---|
| `m5_cdl_reship_check.py` | 六判据机器判据器（md + json，退出码 0/1/2） |
| `make_cdl_check_fixtures.py` | 造 fixfull / fixpartial 两套合成件（判据器判别力自测） |
| `selftest_cdl/` | 合成件本体，全部打头 `FIXTURE-SYNTHETIC`、**禁止进网表/门限** |
| `cdl_reship_check_selftest.log` | 三态自测 + 一键链接线回归 + 自测中修掉的三个判据器缺陷 |

## 改动（一处，纯接线；不改任何判据逻辑与门限）
| 件 | 改动 |
|---|---|
| `m5_pex_pipeline.py` | A 级之前插入 **A0 硬前置**（跑判据器，不过即停，状态写 `stages.A0_reship_check.criteria_states`）；docstring 补 A0 级说明并修一个乱码字符。**无旁路开关**。 |
| `sow6m5_pex_runbook.md` | v2.5 → **v2.6**：头部记 v2.6 变更；§一 新增 **0.5 A0 裁定五六判据**表（六条判据的机器化口径逐条写清）。 |

## 判据器口径要点（照裁定五原文，未加严未放宽）
- ① 31 件 HBT 逐件 B≠E，件数须恰 31；deck 原文 B==E 件数实测 **0** ⇒ 零豁免。
- ② 硬闸只取「R 零自环」；**七件** watch 节点覆盖列**参考项**（b7a0 2026-10-18T03:18:21Z 裁定七：维持参考项、不升硬闸；原信/报告误写「八件」已改口为七件）。
- ③ merged-domain **声明行**（cdl 头部）须 0 条 + 九网在位 + gnd 专项独立。
- ④ hbt_mirror「回归」判为其挂网（mix ntaila/ntailb/nvtop；drv ntail/vcc）逐字回归且互相独立。
- ⑤ 逐件判：出现 nref 的那一件自己须附映射条目（`nref ←/=/→` 或点名 hbt_mirror 出处，或边车 *nref*map*）。
- ⑥ 端口序基线 = v015.1 deck 与现行三件 cdl 的一致值。

## 回归证据
- 三态自测：fixfull 六过(exit 0) / fixpartial ①③⑤❌(exit 1) / 现役粘连件 ①–⑤❌(exit 1)。
- 一键链：`--cdldir sim_report/pex_v27 --tag a0neg` 停在 A0（不进网表）；`--cdldir selftest_cdl/fixfull --stage A` A0 过、A 过（31/0/0）。
- 自测中修掉的判据器自身缺陷 3 个（log 第 3 节留痕）。

## 未做/不做
- 未改任何标称值、未改门限、未改裁定口径、未触碰 b7e7 任何件。
- 未自行扩大范围：② 的 watch 口径与 ⑤ 的映射形态两处**留待 b7a0 裁定**，不自行选定。

---

# 增量二（2026-10-18T03:43Z）· 措辞修正（b7a0 03:41:50Z 第四节备案项）

**触发**：b7a0《验收 15/15 + 四笔小账销账…》第四节 —— 「判据器 verdict 标题『② R 件零自环（8 件归位）』
与『归位语义：8 件 watch 节点』注释——逻辑面 `len(SELFLOOP_WATCH)=7` 动态正确，仅两处字符串写死 8；
下次顺手改『7 件归位』即可，不另发版。」

## 改动（**纯措辞，判据语义零变化**）
| 件 | 改动 |
|---|---|
| `m5_cdl_reship_check.py` | 三处写死 `8` 改为派生自 `len(SELFLOOP_WATCH)`：① `verdict()` 标题（第②判据）② `# 归位语义` 注释 ③ 小节横幅注释。**b7a0 点名两处，我另查出第三处横幅同样写死 8，一并改（如实报备）**。派生后标题恒等于 `② R 件零自环（7 件归位）`，与指定字面一致，且今后不再与逻辑面脱节。 |
| `cdl_reship_check_selftest_v3_wording.log` | 五态复跑 log：exit 5/5 一致 + 结构化逐字段 diff（每份仅 1 个差异字段 = 标题） |

## 未改（据实声明）
- 未改判据逻辑、未改门限、未改退出码、未改 watch 表内容（仍 **7 件** e1a/e2a/e1b/e2b/e1/e2/ccas1）。
- 未动 v2 历史证据（`cdl_reship_check_v2_S*.json` / `st_*.json` 原样保留）。
- b7a0 第三节「七-4 处置认可 + 代码零改」——该处**确实零改**（未触及 watch_trace 逻辑）。

## 指纹
- 修正版 `m5_cdl_reship_check.py` sha256 `ca38d0f3adafc89f4ee058db75580d5faaa7e28a3382bf76ab0e51d7ec5b95f0`（34076 B）
- 上一版 `2a1cebebd353…`（仍归档于 `archive/`）
