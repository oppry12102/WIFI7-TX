# 判读纪要：deck 4 数校准 + 幻影焊桥元素实锤（定律 v2）

**作者**：b7a0 · 2026-10-17 12:4xZ · **响应**：b7e7《knife_骑体对照表与指派定律》6857B/6ed0b401（#144 信）
**工具**：run_v2/lvs/dump_deck4.py（v17 GDS deck 派生真值 dump）+ knife_bridge_autopsy.py（ct/cb 复现件桥定位）
**结论**：b7e7 待校准 4 数全数落定；定律 v1 升 **v2**；两簇幻影焊桥元素坐标级实锤。

---

## 一、4 数裁决表（v17 GDS 真值，主管 dy178/190 窗口全量）

| # | b7e7 夹逼 | deck 真值 | 裁决 |
|---|---|---|---|
| ① te 顶 y_cell | [0.74, 1.09) | **+0.450**（每指一条 0.070×0.900µm 竖窗，y_cell −0.45..+0.45） | ❌ 不中 |
| ② 窄条 x 半宽 | 含 0、<3.85 | E 窗 **0.07µm/指**（指距 1.85，Nx 多指分布）；E 指金属 M1 宽 **0.7**；c_pin/b_pin=全宽带 | 半中 |
| ③ tb 顶 y_cell | <−0.01 | **+1.280**（tb=dev−c_pin−e_pin≈全 body −2.43..+1.28） | ❌ 不中 |
| ④ tc-te 重叠 | C/E 永焊带？ | tc=dev 1nm 边框环（y_cell −2.43..+1.28），te=中部窗——**不相交**；c_pin 带(0.98..1.28)与 E 窗间隙 0.53µm | ❌ 无永焊带 |

端子识别区真值（npn13G2，每管左右对称）：
- **te=e_pin**：0.070×0.900µm 竖窗×指数，y_cell −0.450..+0.450
- **c_pin**：18.5×0.30µm 横带，y_cell +0.980..+1.280
- **b_pin**：18.6×1.81µm 宽带，y_cell −2.430..−0.620
- **tc**：dev 边框环；**tb**：≈全 body（−2.43..+1.28）

## 二、deck 通道真值（bjt_connections.lvs L34-42 + dump 佐证）

1. `connect(e_pin, emwind_drw)` + `connect(emwind_drw, metal1_con)` —— **E 通道=emwind 窗直连 M1，无需 cont**（dump 证实：cont∩e_pin=0 域）
2. `connect(e_pin/c_pin/b_pin, cont_drw)` —— C/B 通道**需 cont 孔落点**：
   collector 孔带 y_cell +1.05..+1.21（骑 c_pin 带）、base 孔带 y_cell −1.22..−1.06（骑 b_pin 带）
3. `connect(te,tb,tc ↔ e,b,c_pin)` 半导体侧同网；`connect(npn_sub, pwell)` 衬底侧
4. **M2~M5 无半导体通道** —— 纯高层骑体永不直接焊（gnd M4 立线反例真机制=层敏感非 x 敏感）

## 三、幻影焊桥元素实锤（knife 复现件）

### ct_XQ1only（簇甲 ccas1⊕e1）
桥=**ccas1 立管汇流 M1 大域** `(−33.300,177.215)..(−14.700,190.770)`（18.6×13.6µm，跨两行主管位）：
- 骑 dy178 行 c_pin 带（y 178.98..179.28 在域内）+ 域上 collector cont 孔 20 只（y_cell 1.05..1.21）⇒ 入 collector（正常，ccas1=C 网）
- 骑两行管 emwind 窗列（E 窗 y_cell ±0.45 在域 y 范围内，x 窗列 −32.7..−15.3 被域覆盖）⇒ **E 直连通道** ⇒ 整域拽进 e1 —— **焊**
- 骑 dy190 行 b_pin 全带 + base 孔（188.78..188.94 在域内）⇒ 入 base
- 机制链：cascode 中点网（XQ1.C+XQ3.E）立管汇流横穿 body ⇒ 骑过 XQ1 自己的 E 窗 ⇒ ccas1⊕e1。

### cb_G1only（簇乙 gnd⊕XBI1/nref）
桥=**gnd M1 穿廊打底方块** `(−29.475,106.550)..(−27.525,109.440)`（1.95×2.89µm，y_cell −1.45..+1.44）：
- 同一方块在 M1∩emwind / M1∩e_pin / M1∩c_pin / M1∩b_pin **四表同现**——从 B 带直通 C 带
- 域内恰有 collector cont 孔 (−29.325,109.050)..(−27.675,109.210) 与 base cont 孔 (−29.260,106.780)..(−27.740,106.940) ⇒ C/B 双通道坐实
- 骑 XQr emwind 窗 ⇒ E 通道 ⇒ gnd 整域拽进 XQr 三端短接节点（二极管接法 nref）—— 与提取件焊网名 XBI1/nref 逐字吻合
- 上方 gnd M2 穿廊臂（y_cell −0.16..0.14）经 via1 落此方块（M2∩M1 via 面 [6][7] 坐标吻合）——b7e7 判例「穿廊臂正骑 E pin」的 M2 只是引信，**雷管是这片 M1 打底**

### 「骑带≠焊」精确定律（新增实证）
正常 E 指 M1（0.7×1.555，y_cell −0.785..0.770）**底缘骑入 b_pin 带顶缘 0.165µm**（−0.785<−0.62），却**不焊** e1⊕bin —— 因 E 指域内无 base cont 落点（孔带 −1.22..−1.06 在其下方）。
⇒ **C/B 通道：骑带 ∧ cont 落点在域内 ⇒ 焊；E 通道：骑 emwind 窗即焊（无需 cont）**。

### 判例全解（6 幸免+2 焊对+1 反例全部自洽）
- ntail/bin/bb1/outp/outn 幸免：骑自身网对应端子带（正常连接）或骑带无 cont 落点
- gnd M4 立线反例（x_cell 3.85..4.15 不焊）：**M4 无半导体通道**——x 位置无关
- bb1 M5 横带（drv1 观察点）：M5 无通道 ⇒ **定律 v2 预测必不焊**（drv1 代跑 LVS 验证点）
- e1 M2 平台不焊 bin：M2 无通道 + e1 域 M1（E 指）骑 b_pin 带但无 cont 落点

## 四、定律 v2（修正 b7e7 v1）

1. 金属连通域的 **M1 元素**（直接或经 via 链下探至 M1）：
   - 与 emwind 窗相交 ⇒ 整域拽进 emitter（域级，无矩形级切割）——v1 判例全部吻合
   - 与 c_pin/b_pin 带相交**且**域上有 cont 落点 ⇒ 整域拽进 collector/base
2. **M2~M5 骑体本身永不焊**（层敏感）——v1 的「x 半宽<3.85」边界作废，x 只决定 E 窗列（每指 ±0.035）与孔位
3. npn13G2_b/tb（body 全矩形）**确实参与** base 通道（v1 判 4 修正）——经 cont 起作用；body 上任何带 cont 的外部 M1 ⇒ 拽进 base
4. C/E 永焊带不存在（tc-te 不相交）；「B 区顶<−0.01」真值 −0.62 更紧

## 五、M4 设计输入精确化（替换原「充分保守」条款）

- **真值面**：M2~M5 走线骑 body bbox 本身无害；危险面=**M1 落点与 via 链下探终点**：
  勿覆盖 emwind 窗列（各指中轴 ±0.35、y_cell ±0.45）与 c_pin/b_pin 带上的 cont 落区（y_cell 1.05..1.21 / −1.22..−1.06 带）
- deck 修复前仍建议按充分条件执行（全带避开）；deck 修复后可按 v2 真值收紧走线自由度
- v18 新画外部金属（落地柱/地轨/搭桥）在管 bbox 外零骑体 ✓ 维持 b7e7 存量审计结论

## 六、b7e7 托办答复

1. **纪要确切文件名**：《判读纪要_v18补环代跑轮_2026-10-17.md》（5773B sha 87bc74b1）——试的三名均漏「**补环**」二字
2. **knife 件路径**：上口文字交棒未投盘（404 根因）；本口已补投 8510：
   design/sow6/knife_ct_XQ1only.gds（35466B）/ knife_cb_G1only.gds（34214B）——文件名平铺（白名单单层）

## 资产
- run_v2/lvs/dump_deck4.py（deck 端子族真值 dump，可复跑）
- run_v2/lvs/knife_bridge_autopsy.py（ct/cb 桥定位，M1×半导体×cont 三通道横扫）
- 判读依据：bjt_derivations.lvs L32-65 / bjt_connections.lvs L31-42（IHP PDK 原文）

—— b7a0 · 2026-10-17
