# 判读纪要 · drv1 衬底浮空根因定谳与 pwell 接地 tap 交办 —— **裁定二十七**

* 日期：2026-10-18（09:3x–09:5xZ）
* 签发：b7a0（WiFi7-TX-ASIC 组长）
* 触发：上口遗留未结项「drv1 对拍线 · 失配全收敛到衬底网单点」⇒ 本口按**先 dump 再判、禁盲试**的纪律做「region→端子」验尸
* 结论级别：**根因定谳（含机制链逐行定位 + 四跑因果对照 + 版图交办项）**

---

## 〇、一句话

**drv1 对拍 8 个 net / 4 个 device 失配的单根因＝衬底网**：
`npn13G2` 是**四端子**器件（`CustomBJT4`，第 4 端 S＝衬底），`rsil/rppd/rhigh` 是**三端子**器件（第 3 端子＝衬底）；
四只 HBT 与九只电阻的衬底端子**全部挂在同一张版图网 `$1`** 上，而该网**没有任何接地路径**（孤立）——
schematic 侧衬底按 D2 接 SPICE 全局 `0`（正确）⇒ 单边网双向失配 ⇒ 级联 8 net + 4 device。
**实证**：drv1 是现役三块中**唯一零 pwell 接地 tap** 的子块（`40/0 substrate_drw`＝0 多边形、无 `ptap1` 实例）；
且**偏置支路 XQo(Nx=8)/XQr(Nx=1) 的 pwell 岛浮空**，主差分对 Q2/Q3 的岛已接地。

---

## 一、机制链（deck 逐行定位，patched deckfix_v1）

| 环节 | 位置 | 原文/事实 |
|---|---|---|
| 器件是四端子 | `rule_decks/custom_bjt_extractor.lvs` `class CustomBJT4 < RBA::DeviceClassBJT4Transistor` | 参数仅 `we/le/Nx/m`；端子 C/B/E/S |
| S 与 tS 同层 | `bjt_extraction.lvs` L33-43 | `'S' => npn_sub, 'tC' =>…, 'tS' => npn_sub` —— **同一层** |
| S 端子必被定义 | `custom_bjt_extractor.lvs` `extract_devices` | 条件 `nx>0 && !collectors.is_empty? && !bases.is_empty? && !subs.is_empty?`（NPN 必查 subs）；`ts.interacting(device_region).merged.each { define_terminal(..., 'S', 8, poly) }` ⇒ **只要器件被提取，S 端子必然存在**（与 C/B/E 缺失行为不同） |
| 衬底并入 pwell | `bjt_connections.lvs` L31 | `connect(npn_sub, pwell)` |
| 电阻衬底并入 pwell | `res_connections.lvs` L28/34/40 | `connect(rsil_sub/rppd_sub/rhigh_sub, pwell)` |
| **接地链（唯一）** | `general_connections.lvs` L28/31/38 | `connect(pwell, ptap)` → `connect(ptap, cont_drw)` → `connect(cont_drw, metal1_con)` |
| ptap 的定义 | `general_derivations.lvs` L52/103-107 | `pactiv = activ.and(psd_drw)`；`ptap_all = pactiv.and(pwell).not(recog_diode).not(gatpoly)`；`ptap = ptap_all.not(ptap1_mk)`；`ptap1_mk = substrate_drw.and(pwell).interacting(ptap1_lbl)`，`ptap1_lbl = text_drw.texts("sub!")` |
| DISABLE_TAP_EXTRACTION 下仍通 | `tap_connections.lvs` 末段 | `if DISABLE_TAP_EXTRACTION: connect(ptap1_tie, ptap1_sub)` —— **器件不提取，但连通语句保留**（本轮四跑均带 `--disable_tap_extraction`） |
| **网名 label 层** | `layers_definitions.lvs` L185 | `metal1_text = labels(8, 25)`；`50/25 = metal4_text`；**`50/0` 不是任何网名层** |

⇒ **接地链完整表达**：`pwell ─ p+ 插塞(14/0∩1/0) ─ cont(6/0) ─ M1(8/0) ─(8/25 label 或几何并入既有 gnd 网)`。
**断链后果不是「器件不提取」，而是「S 端子挂孤立网」**——这正是本案的盲区形态。

---

## 二、pwell 分岛实证（现役 GDS，gdstk 逐层统计）

| 块 | GDS | 顶层 | `40/0 substrate_drw` | `46/0 pwell_drw` | `ptap1` 实例 | 衬底状态 |
|---|---|---|---|---|---|---|
| mix | `m2_mix_v29.gds`(8f6da23d) | TX5G_M2_MIX_V29 | **16** | 0 | **有** | 已接地 |
| drv2 | `m3_drv2_v20_v32.gds`(c9363888) | TX5G_M3_DRV2_V20 | **16** | 0 | **有（6 实例）** | 已接地（LVS PASS 之必要条件之一） |
| **drv1** | `m3_drv1_v20_v32.gds`(fe2ff903) | TX5G_M3_DRV1_V20 | **0** | 0 | **无** | **XQo/XQr 岛浮空** |

`pwell_drw(46/0)` 三块皆 0 ⇒ 正常：deck `pwell_allowed = CHIP.not(pwell_block)`，pwell 是**芯片级默认整面**，
分岛来自 `trans_drw/gatpoly/res_drw/salblock_drw/substrate_drw` 等 `npn_exclude` 的切割，**不来自 46/0 图形**。

---

## 三、四跑因果对照（唯一变量＝衬底接地；deck/网表/driving 几何全同）

配方：`bash run_lvs_v20_pass.sh <tag> <layout> drv1_subckt_LVS输入_v2b_topname.sp`
（deckfix_v1 + `--ignore_top_ports_mismatch --disable_tap_extraction --no_series_res --no_parallel_res`，~3.7s/跑）

| 跑 | 变量 | Status | net | device | 版图侧关键事实（`*_extracted.cir`） |
|---|---|---|---|---|---|
| **E0** | 基线（无 tap） | FAIL | **8 M / 8 X** | 13 对 / **4 非 Match** | `Q$1 ntail XBI/nref gnd \$1`、`R$5..R$13 … \$1` ⇒ **4 只 HBT + 9 只电阻的衬底全在 `$1`** |
| **E1** | +ptap1@(250,205)，label 打在 **50/0**（无效层） | FAIL | 8 M / 8 X | 4 非 Match | `$1` 依旧；log `substrate_drw has 1 polygons`（图形进来了） |
| **E2** | +ptap1@(250,205)，label 打在 **8/25**（`metal1_text`） | FAIL | 8 M / 8 X | 4 非 Match | **Q$1/Q$4 衬底＝`gnd$1`；Q$2/Q$3 衬底＝`gnd`** ⇒ ★**两岛判别成立，且浮空岛可被命名接地** |
| **E3** | +ptap1@(**−39.5,127.6**)＝ntail 汇集板上，label 8/25 | FAIL | **6 M / 10 X** | **6 非 Match** | **网名 `gnd|ntail`** ⇒ ★**ptap 落在 ntail 板上造成 gnd–ntail 短路**（禁区实测） |

* E2 的 `gnd$1` 是 klayout 对「同名不连通网」的自动改名 ⇒ **命名不能替代电学连接**（律，见 §五③）。
* E0→E2 的器件数不变（13/13）、提取指纹变化仅在衬底列 ⇒ **回改落点明确、不牵连其他网**。

---

## 四、错配「级联指纹」逐条解读（E0 `lvsdb_diff_dump`）

| layout | sch | 解读 |
|---|---|---|
| `$1` | `0` | ★根因：版图孤立的 pwell/衬底网 ↔ sch 全局地 |
| `gnd` | `?` | ★根因的反面：sch 侧**没有独立 gnd 网**（地就是 `0`），版图 gnd 无配对对象 |
| `inp` / `inn` | `?` / `INP` `INN` | 次因：sch 网名大写、版图 label 小写（与 drv2 的 `XBI<k>/nref ↔ NREF<k>` 同族，属 warning 族） |
| `ntail` | `NTAIL` | 同上（大小写） |
| `XBI/nref` | `NREF1` | 同上 + D3 改名遗留（`/` 被迫改名） |
| `$1`(dev) | `XBI_XQO`；`$4` | `XBI_XQR` | ★**衬底失配直接命中偏置支路两只 HBT** |
| `$9` `$10` | `RIN1` `RIN2` | 二级级联（衬底 + inp/inn 双因） |

---

## 五、裁定二十七（七项）

**① 衬底族根因定谳**：HBT 四端子（S）+ 电阻三端子（sub）的衬底网必须计入 LVS 网表比对。
只看 C/B/E 的对拍器会**系统性漏判**；本案的失配全部挂在 S/sub 上。

**② 机制链公开（可复现）**：`pwell ─ p+插塞 ─ cont ─ M1 ─(8/25 label 或并网)` 是唯一接地链；
`DISABLE_TAP_EXTRACTION` 只关器件、不关连通；**网名层＝`labels(8,25)`（M1）/ `labels(50,25)`（M4）**，`50/0` 无效。

**③ pwell 分岛律**：子块级 LVS 中，**pwell 是芯片级默认整面并被 `npn_exclude` 族切成多岛**；
「器件被提取」≠「衬底已接地」。**每岛各自需要接地通路**；命名（含重名自动改名）不能替代电学连接。

**④ 交办 b7e7（回改清单 v3 追加第 ①项）· drv1 偏置支路 pwell 接地**：
在 **XQo(x∈[−6.5,6.5],y≈106–110)/XQr(x≈34,y≈106–110) 所在 pwell 岛内**放 `ptap1`
（PCell 自带 `1/0 Activ + 14/0 pSD + 4×6/0 cont + 8/0 M1 tie + 40/0 substrate_drw`），
并以金属通路并入既有 **gnd 干线**（禁止依赖 label 命名）。
**禁区（E3 实测）**：`M1 (−39,121)–(39,136)`（面积 1170µm²）**ntail 汇集板及其压板带区**——ptap 落此造成 `gnd|ntail` 短路。
落点须过 DRC（M1.b/e、cont 密度）并给出 gnd 接入的 via 链证据。

**⑤ 对拍口径**：schematic 侧 D2（衬底接 SPICE 全局 `0`）**正确，维持不改**；
在④回改前 **drv1 LVS 不可能 PASS**——这是**版图事实缺口，不是 harness 缺陷**，不得为过对拍而改 sch。
drv2/mix 因已有 ptap1 不受影响（其 PASS 结论继续有效）。

**⑥ 单边网双向失配律（指纹）**：失配表若同时出现「layout 有 sch 无」与「sch 有 layout 无」的一对网，
**先查版图侧那张「只连器件端子、不连任何金属」的网**——它是单根因，其余是级联。

**⑦ 交办普查项（并行）**：现役三块接地 tap 普查已做（§二，drv1 独缺）；
请 b7e7 在后续轮次（v20 回改批）**把「每块每岛 pwell 均有接地 tap」列为自检断言**（零断言即停线）。

**附带**：本口**未动** M5/PEX 任何资产（判据器、suspicious、pipeline、回执、runbook、台账 json 一概未动）；
主闸门（换源重提取三件 cdl）口径不变——**b7e7 到件包第三次仍未到（8510 `.cdl` 仍 6 件、现役三名逐字未变）**。

---

## 六、测试件声明（禁止作交付）

| 件 | 说明 |
|---|---|
| `run_v2/lvs/drv1_v32_ptap_test.gds` | 上口 submark/ptap 试验件 |
| `run_v2/lvs/drv1_v32_submark_test.gds` | 上口试验件（顶层铺 40/0 ⇒ 器件归零） |
| **`run_v2/lvs/drv1_v32_ptapgnd_test.gds`** | **本口 E1/E2/E3 试验件**（每次覆盖重生成；`mk_drv1_ptap_test.py <x> <y>` 可复现任意落点） |
| `run_v2/lvs/drv1_subckt_LVS输入_v2b_topname.sp` | 上口派生件（仅改 2 行顶层名，正文逐字节同 b7e7 v2） |

以上四件**仅供机制验证**，不得进入交付面、不得作 b7e7 的回改参照版。

---

## 七、复现配方

```bash
cd /data/workspace/phys/sow6_run/run_v2/lvs
python3 mk_drv1_ptap_test.py 250 205      # E2（8/25 label）；改 -39.5 127.6 即 E3
bash run_lvs_v20_pass.sh E2tag "$PWD/drv1_v32_ptapgnd_test.gds" \
     "$PWD/drv1_subckt_LVS输入_v2b_topname.sp"
# 版图侧真值看 *_extracted.cir 的第 4 网列；逐项看 lvsdb_diff_dump.txt
. /data/workspace/pdk/kl_env030.sh && export KLAYOUT_PATH=$KLTECH
python3 lvsdb_nl_dump.py deckfix_v1/out_drv2v20_<tag> A /tmp/A.txt   # 两侧网表逐器件端子
```
