* ============================================================================
* drv2 子电路 schematic（LVS schematic-vs-layout 对拍用）· v2
* ----------------------------------------------------------------------------
* 日期     : 2026-10-17 (b7e7)
* 口径来源 : b7a0《判读纪要_LVS首跑net_only_BJT端子粘连排查_2026-10-17.md》§四
*            + b7a0 信 2026-10-17T10:32Z（schematic 件格式口径）
* 源锚     : design/chain_top_tb_v015_1.sp :: .subckt drv2 (行 241~271)
*            + .subckt hbt_mirror (行 126~130, nx=8 rr=1.62k 默认)
* 版图真值 : gen_M3_drv2_v17.py DEV_NETS/NET_DECL + stdout [res] 行（v17 五关全绿基线）
* ----------------------------------------------------------------------------
* v2 变更（vs v1，按组长新口径）:
*   1. HBT 全部 X 行 -> Q 行 4 端（KLayout reader 的 X 行不建器件）:
*      Q<名> C B E <sub> npn13G2 le=900.0n we=70.00n m=<Nx>（官方样例形，nx->m）
*   2. hbt_mirror 展开 4 实例内联（版图本就扁平画在顶层 cell）；
*      内部网 nref 每实例独立: XBI<k>/nref（照版图 NESTED_STYLE=hier 网名形态）
*   3. 剥离版图不存在件: Vb、Vbcas、Cin1/2、Ct1/2（cmim 仅占位）、Lt1/2（禁区占位）
*      —— 剥离后 nbias=Rb1/Rb2 公共网、nbcas=XQ3.B/XQ4.B 公共网，与版图金属网一致
*   4. R 行带 model + l/w（照 gen stdout [res] 行实选，res_auto 现算值）:
*      Re=rsil 1.000/4.665 · Rref=rhigh 1.190/1.000 · Rin=rhigh 1.000/1.360
*      Rb=rppd 1.923/1.000 · RL=rppd 1.000/2.600（单位 µm）
*   5. RL 保留（版图真画，勿当测试台剥离）
* 器件名映射: QXQ1<->版图 XQ1、QXBI1_XQo<->XBI1_XQo、RRe1<->Re1 …（Q/R 前缀 + 版图实例名）
* 组长侧首跑参数: --disable_tap_extraction --ignore_top_ports_mismatch（0.30.0 回退环境）
* ============================================================================
.subckt drv2 inp inn outp outn vcc
* --- 输入网络: Rin1/2 1k rhigh（Cin 占位已剥离，inp/inn 为子ckt端口） ---
RRin1 inp 0 1000 rhigh l=1.000u w=1.360u
RRin2 inn 0 1000 rhigh l=1.000u w=1.360u
* --- 主四管 npn13G2 Nx=10 -> m=10（sub 经衬底接 0；C/B/E 照 DEV_NETS） ---
QXQ1 ccas1 bin  e1 0 npn13G2 le=900.0n we=70.00n m=10
QXQ2 ccas2 bb1  e2 0 npn13G2 le=900.0n we=70.00n m=10
QXQ3 outp  nbcas ccas1 0 npn13G2 le=900.0n we=70.00n m=10
QXQ4 outn  nbcas ccas2 0 npn13G2 le=900.0n we=70.00n m=10
* --- 发射极负反馈 Re1/2 1.5R rsil ---
RRe1 e1 ntail 1.5 rsil l=1.000u w=4.665u
RRe2 e2 ntail 1.5 rsil l=1.000u w=4.665u
* --- 基极偏置 Rb1/2 500R rppd（Vb 源已剥离: nbias=Rb1.P2/Rb2.P2 公共金属网） ---
RRb1 bin nbias 500 rppd l=1.923u w=1.000u
RRb2 bb1 nbias 500 rppd l=1.923u w=1.000u
* --- 输出负载 RL1/2 100R rppd（版图真画件） ---
RRL1 vcc outp 100 rppd l=1.000u w=2.600u
RRL2 vcc outn 100 rppd l=1.000u w=2.600u
* --- 尾流镜像 hbt_mirror x4 展开内联（每组 = Qr Nx=1 + Qo Nx=8 + Rref 1.62k rhigh;
*     nref 每实例独立网 XBI<k>/nref，四条互不连通，照版图扁平形态） ---
QXBI1_XQr XBI1/nref XBI1/nref 0 0 npn13G2 le=900.0n we=70.00n m=1
QXBI1_XQo ntail XBI1/nref 0 0 npn13G2 le=900.0n we=70.00n m=8
RXBI1_Rref vcc XBI1/nref 1620 rhigh l=1.190u w=1.000u
QXBI2_XQr XBI2/nref XBI2/nref 0 0 npn13G2 le=900.0n we=70.00n m=1
QXBI2_XQo ntail XBI2/nref 0 0 npn13G2 le=900.0n we=70.00n m=8
RXBI2_Rref vcc XBI2/nref 1620 rhigh l=1.190u w=1.000u
QXBI3_XQr XBI3/nref XBI3/nref 0 0 npn13G2 le=900.0n we=70.00n m=1
QXBI3_XQo ntail XBI3/nref 0 0 npn13G2 le=900.0n we=70.00n m=8
RXBI3_Rref vcc XBI3/nref 1620 rhigh l=1.190u w=1.000u
QXBI4_XQr XBI4/nref XBI4/nref 0 0 npn13G2 le=900.0n we=70.00n m=1
QXBI4_XQo ntail XBI4/nref 0 0 npn13G2 le=900.0n we=70.00n m=8
RXBI4_Rref vcc XBI4/nref 1620 rhigh l=1.190u w=1.000u
* --- 已剥离件备案（版图仅 PH_PLACE 占位/测试台专有，不在本件） ---
*   Vb nbias 0 1.25 / Vbcas nbcas 0 2.05   （测试台理想源）
*   Cin1 inp bin 10p / Cin2 inn bb1 10p    （cmim 占位）
*   Ct1 outp 0 1.2p / Ct2 outn 0 1.2p      （cmim 占位）
*   Lt1 vcc outp 0.7n / Lt2 vcc outn 0.7n  （tank L 禁区占位）
.ends drv2
