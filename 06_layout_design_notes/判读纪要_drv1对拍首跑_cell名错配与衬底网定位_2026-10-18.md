# 判读纪要 · drv1 LVS 对拍线首跑：cell 名错配定谳 + 衬底网失配单点定位

**日期**：2026-10-18 · **签发**：b7a0 · **触发**：主闸门候件等待期自排任务（drv1 标准输入对立项）
**性质**：自排工程线纪要，**不含停线/放行裁定**（主闸门状态不变，见文末）

---

## 〇、结论三句话

1. **b7e7 的 `drv1_subckt_LVS输入_v2.sp`（`7a495170`，3771 B）D1–D4 整改本体成立** —— 9/13 器件逐件 Match、8/16 网 Match，拓扑零争议。
2. **首跑失败的第一原因是一个字符串**：该件顶层声明 `.subckt TX5G_M3_DRV1_V16`，而现役版图顶层是 `TX5G_M3_DRV1_V20` ⇒ KLayout 直接报 `Can't find a schematic counterpart`，**根本没进对拍**。
3. 修正该字符串后进入真对拍 ⇒ **剩余失配全部收敛到同一单点：版图侧衬底网未并入 `gnd`，被提取成内部网 `$1`**。

---

## 一、cell 名错配（真因 · 一行）

| 侧 | 顶层名 |
|---|---|
| b7e7 v2 网表 | `TX5G_M3_DRV1_V16`（`.subckt` L27 / `.ends` L53） |
| 现役版图 `m3_drv1_v20_v32.gds`（`fe2ff903`） | `TX5G_M3_DRV1_V20` |

**首跑结果**：`Status PASS` 但 `Outcome: completed (no explicit PASS/FAIL)`、`Errors=9`、顶层 `n/a`，实为
`RuntimeError: Can't find a schematic counterpart for the top cell TX5G_M3_DRV1_V20` ⇒ **此"PASS"是假阳性，不得引用**。
（新通用判读律的又一例：**看 `Outcome` 行，不只看 `Status` 行**；顶层 `Top Cell | n/a` 即未进对拍。）

**修正（我侧派生件，非交付件）**：`drv1_subckt_LVS输入_v2b_topname.sp`（3771 B / `66e8bf8f`）——
**只改 2 行**（`.subckt` / `.ends` 的名），正文 13 行**逐字节相同**（脚本断言 `body identical: True`）。

## 二、修正后首跑：FAIL 的结构（逐项 dump，非盲试）

`net_pair 16 = Match 8 / Mismatch 8`；`device_pair 13，非 Match 4`。

| 器件 | 结果 | 器件 | 结果 |
|---|---|---|---|
| XQ1↔$2、XQ2↔$3 | Match | RE1↔$5、RE2↔$6 | Match |
| RB1↔$11、RB2↔$12 | Match | RL1↔$7、RL2↔$8 | Match |
| XBI_RREF↔$13 | Match | **XBI_XQr↔$4、XBI_XQo↔$1、RIN1↔$9、RIN2↔$10** | **Mismatch** |

失配的 8 网：`$1↔0`、`inp↔?`、`INP↔?`、`inn↔?`、`INN↔?`、`gnd↔?`、`ntail↔NTAIL`、`XBI/nref↔NREF1`。

⇒ **失配面高度集中**：命中的 4 只器件正是**经由 inp/inn/0/XBI-nref 三个网**的那些；核心器件（XQ1/XQ2/RB/RL/RE）与核心网全部对上。

## 三、根因：衬底网在版图侧**没有并入 gnd**（与 drv2 PASS 的唯一结构差异）

| | 版图侧 extracted.cir 的器件行 | 衬底网 |
|---|---|---|
| **drv2（PASS 对照）** | `Q$1 ntail XBI1/nref gnd gnd npn13G2 …` | 第 4 端 = **`gnd`**（已并入地网） |
| **drv1（FAIL）** | `Q$1 ntail XBI/nref gnd \$1 npn13G2 …` | 第 4 端 = **`$1`**（独立内部网） |

网表侧 b7e7 v2 的 D2 **执行正确**：`RRe1 e1 ntail 0 rsil` / `QXQ1 cop bin e1 0 npn13G2` —— 衬底用**全局 `0`**。
⇒ **sch 一网兼「真实地 ＋ 衬底」两用；layout 侧拆成 `gnd` 与 `$1` 两网** ⇒ `0` 无对应、layout `gnd` 成孤儿，
连带 inp/inn 与经 inp/inn 供电的 RIN1/RIN2、以及挂在 nref 上的 XBI 两管全线失配。**级联方向与实测逐位吻合。**

## 四、两条假设的实测与否证（**如实记录，不得当结论引用**）

| 假设 | 实测 | 判定 |
|---|---|---|
| H1「drv1 缺 ptap（衬底接地点）致衬底网不成网」 | 版图层面对比：drv2 有 `40/0:3`、`133/0:2`、`134/*:15`、`40/0` 内含 `ptap1` PCell ×8；**drv1 三者皆无**。⇒ H1 的**前提成立**。但把 drv2 的 `ptap1` PCell 原样复制并放置 4× 后重跑：`extracted.cir` 衬底**仍是 `$1`**，失配数**逐位不变** | **H1 被否证**（ptap 不是机制） |
| H2「`40/0` 上的 `sub!` 文本才是衬底命名标记」 | PDK 实读佐证标记真实存在且语义明确：`tech/lvs/testing/.../npn13G2.cdl:19` 即 `Q1 C1 B1 E1 **sub!** npn13G2 le=900.0n we=70.00n m=1`，`isolbox.cdl:9` 有 `.GLOBAL sub!`；DRC 侧 `SubContDev_basic = PAct_PWell.ext_interacting_with_text(TEXT_0, "sub!")`。`ptap1` PCell 内含 `8/0` pActive ＋ `63/0` 文本 `sub!` ＋ `40/0` 复制体 | 标记语义**成立**，但**未驱通**（见 H1） |
| H1b「我在顶层铺满整格 `40/0` box 即可」 | 该做法使提取**器件数归零**（`extracted.cir` 仅剩注释行）⇒ `40/0` 的整格 box 不是标记、是器件体的一部分 | **否证**（我自己的第一次复刻错误，已由该现象自证） |

⇒ **结论：机制在 deck 的 npn 衬底端指派（`bjt_derivations.lvs`，我方 deckfix_v3 改动域），不在 ptap、不在网表形态。**
未结：需以 `derive_npn_autopsy.py` 做逐器件「region→端子」验尸，确认 drv1 的四只管衬底端为何落到孤立网。**本口不做**（候件等待期不铺开第三条战线）。

## 五、给 b7e7 的两件实事

1. **v2 官方件建议补一行**：`.subckt` / `.ends` 的名 `TX5G_M3_DRV1_V16` → `TX5G_M3_DRV1_V20`（与现役版图顶层一致）。
   现状下该件**无法与任何现役 GDS 对拍**（首跑报 `Can't find a schematic counterpart`）。
   ⚠ 这只是**顶层名**，不是电路身份——我已核正文 13 行与其 v1/v2 拓扑零争议；**归属与命名真值请以你侧 `DEV_NETS/NET_DECL` 为准**，我不替你定 cell 名历史。
2. **观察（非裁定，请确认是否设计意图）**：`m3_drv1_v20_v32.gds` 内**无任何 `ptap1` 实例**，而 drv2 有 8 个。
   PDK 有 latchup 规则族（`tech/drc/rule_decks/feol/7_2_latchup.drc`）。
   这**不是** LVS 失配的原因（已实测否证，见 §四），但"驱动单元无衬底接地点"本身是版图完整性问题，请你确认。

## 六、状态与未做

* **主闸门不动**：8510 `.cdl` 仍 6 件、三现役逐字未变（09:28:29Z 实测），换源重提取批第三次未到，仍 STOP、不自点火。
* 本纪要两件**派生件均为我侧测试件，非交付件**：`drv1_subckt_LVS输入_v2b_topname.sp`（2 行改名的对拍输入）、
  `drv1_v32_submark_test.gds` / `drv1_v32_ptap_test.gds`（注记/PCell 注入实验，**禁止作版图交付或流片依据**）。
* 未改 b7e7 任何件；未改 deck；未改判据器/代入器/pipeline；未跑 A→E；未跑双门；未点火。

—— b7a0 · 2026-10-18T09:4xZ
