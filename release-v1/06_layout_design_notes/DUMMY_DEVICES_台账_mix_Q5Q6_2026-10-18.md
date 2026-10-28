# DUMMY_DEVICES 台账 v1.2 — gilbert_mix 填充管 d3L/d3R（编号 5/6）

b7e7 · 2026-10-18 · schema v1.1（组长裁定二十五 §三发布 / 裁定二十六 §三升级：坐标与域号取自与 cdl 同批 SRC 的提取 json，禁沿用上一轮）
**v1.2 变更（裁定三十一 §二）**：标题与「数量口径」小节去器件编号字面写法（范围表述会被编号全文扫成假进册；本注记自身亦不出现该字面）。「## + 编号」块首两行与块内证据行为判据器锚点与证据窗口，**保留编号字面**——全文件合法命中仅此两块。
适用 cdl 件：`pex_mix_v27.cdl`（现役槽位名，sha ce97750b…，SRC_GDS_SHA256: 8f6da23d…）
同源证据件：`pex_mix_v29.json`（同批 v29 源提取产物，与 cdl 同一 SRC_GDS_SHA256）——本台账全部坐标/域号系该 json 2026-10-18 实读，非沿用 v28 轮正例。
台账性质：档C 阳性认定要件（裁定二十三·三 / 二十五 §三），不是免责通道。只覆盖「三端同地」填充管族；
骑体真短族（XBI1/2.XQr nref↔gnd）不在本台账，仍走零豁免 FAIL。

## Q5

Q5 d3L pex_mix_v27.cdl:L18
x=-50.0 y=86.24 Nx=3 we=70n le=900n m=1
domain C=M1[11] B=M1[7] E=M2[9]
gnd connect: pex_mix_v29.json dnode_net 实读 M1:11→['gnd'] M1:7→['gnd'] M2:9→['gnd']（同批 SRC 8f6da23d）；cdl 行 `Q5 gnd gnd gnd npn13G2 we=70n le=900n NX=3 M=1 sub=0`；gen L1022-1029 三端 wire_v(GND_LAYER,…) 落 y=GND_RAIL_Y 唯一 gnd 标注地轨（L1030-1032）。

补证：json devices[4] terms C/B/E 坐标 (−50.0, 86.24/83.86/84.993)，node=[M1,11]/[M1,7]/[M2,9] 逐位与块内域号一致。

## Q6

Q6 d3R pex_mix_v27.cdl:L19
x=+50.0 y=86.24 Nx=3 we=70n le=900n m=1
domain C=M1[107] B=M1[103] E=M2[42]
gnd connect: pex_mix_v29.json dnode_net 实读 M1:107→['gnd'] M1:103→['gnd'] M2:42→['gnd']（同批 SRC 8f6da23d）；cdl 行 `Q6 gnd gnd gnd npn13G2 we=70n le=900n NX=3 M=1 sub=0`；gen L1022-1029 三端 wire_v 落同一地轨（L1030-1032）。

补证：json devices[5] terms C/B/E 坐标 (+50.0, 86.24/83.86/84.993)，node=[M1,107]/[M1,103]/[M2,42] 逐位与块内域号一致。

## 数量口径（15 = 13 + 2，裁定二十三·五不变）

- 版图提取面 15 只 HBT：电路 13（编号 1–4、7–15）+ 台账 2（d3L/d3R＝编号 5/6）。
- deck 电路面 13 只（9 直接 + 2×hbt_mirror×2；XQr/XQs 为 C==B 二极管接法且 B≠E ⇒ b==e 件数 0）。
- mix schematic 侧补画 QX5/QX6 使两侧各 15 只逐件可对（mix_subckt_LVS输入_v1.sp f03737b7 已投）。
- 对称性：d3L/d3R 以 CX∓2.5*GM_COL 布放（gen L505-506），gm 匹配管同档（Nx=3 we=70n le=900n）。
- 电气含义：三端同网 ⇒ Vbe=Vce=0 ⇒ 无正向偏置 ⇒ 对 CG 基线零影响。

## 证据自检表（schema v1 逐条命中行号）

| 器件 | 块首行（含 Q\d+） | 证据① 坐标行 | 证据② 域行 | 证据③ gnd+连接词行 |
|---|---|---|---|---|
| Q5 | `## Q5` 下第 1 行 | 第 2 行（x=/y=） | 第 3 行（M1[/M2[） | 第 4 行（gnd + connect/接地） |
| Q6 | `## Q6` 下第 1 行 | 第 2 行 | 第 3 行 | 第 4 行 |
台账件数 = 2 = cdl 件内三端同地件数 ✓（全树无其他三端同地填充管，Q=15 逐行核对）。

## 维护纪律（T2，v1.1 增补）

- 台账坐标/域号**必须**取自与 cdl 同批 SRC_GDS_SHA256 的提取 json；换源/换批 ⇒ 本台账同批重读重投，禁沿用旧轮数字。
- 唯一来源：gen `DUMMY_DEVICES = {"d3L","d3R"}`；gen 改动涉及填充管增删 ⇒ 同批更新台账并重投。
- 不在册的三端同地器件一律 FAIL；两族（填充管/骑体真短）不得互相借用台账。
