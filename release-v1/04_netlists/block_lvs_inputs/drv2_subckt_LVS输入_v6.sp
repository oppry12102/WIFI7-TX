* ============================================================================
* drv2 子电路 schematic（LVS schematic-vs-layout 对拍用）· v5（正式件 · D1-D4 形态整改）
* ----------------------------------------------------------------------------
* 日期     : 2026-10-18 (b7e7)
* 口径来源 : b7a0《判读纪要_LVS首达PASS_源网表四缺陷与串并联开关_2026-10-18.md》
*            (sha16 8ecf7255d258a14f) §三 D1-D4 + 信 2026-10-18T08:55Z（L99）
* 源锚     : v4（486f6558ed701774）—— 拓扑零改动，只动四处源网表形态
* 版图真值 : gen_M3_drv2_v17.py DEV_NETS/NET_DECL + stdout [res] 行（v17 五关全绿基线）
* ----------------------------------------------------------------------------
* v5 变更（vs v4，按裁定二十 §三 D1-D4，对应组长侧 drv2_sch_conform.py 整改口径）:
*   D1 电阻 3T 语法（12/12 行）: 2T 直觉形态 `R名 n1 n2 <阻值> <model>` 会令
*      rewrite_res_from_model_position 把阻值 token 当衬底网（sub=f[i-1]），
*      凭空浮出 1.5/100/500/1000/1620 五个数字网。修法: 删阻值 token，
*      model 前插入衬底网（官方样例形 `Rs1 net1 net2 sub rsil m=1 l=… w=…`；
*      阻值本就由 l/w×sheet 决定，不经行内数字）。
*   D2 衬底一律用 SPICE 全局 `0`（12 处新插衬底全用 0，禁止字面 gnd——
*      字面 gnd 会与 Q 行衬底的全局 0 分裂成两网，layout=gnd↔sch=0 才配对）。
*   D3 网名禁 `/`（16 处引用）: `/` 是 SPICE 层次分隔符，`XBI1/nref` 被读成
*      「XBI1 子电路 / nref 节点」，镜像环 12 只器件全失配。
*      修法: XBI<k>/nref -> NREF<k>（k=1..4；net 名不参与比对判据，拓扑一致即可）。
*   D4 npn13G2 参数 we/le/Nx/m 四项全参与比对（enable_parameter 全 true，
*      提取侧固定 m=1 另设 Nx）。v4 写 m=<Nx> ⇒ Nx 缺省 1 与 m 双错。
*      修法: `Nx=<N> m=1`（主四管 Nx=10 / 镜像输出管 Nx=8 / 镜像二极管 Nx=1），
*      对齐版图侧实测 `we=70n le=900n Nx=10 m=1`。
* 拓扑不变自证: 器件名/端子连线/网集合（除 D3 改名）与 v4 逐一相同——
*   体检脚本 lvs_source_audit.py 逐行核对（本件投件前已跑，全绿）。
* ----------------------------------------------------------------------------
* v4 变更（vs v3）: 粘连轮对拍基准回改（RRin 下端 nref -> 0 对齐版图提取真值；
*   .subckt 名 TX5G_M3_DRV2_V22 对齐版图 cell 名）—— 见 v4 头注及裁定十七/十八
* v3 变更（vs v2）: .subckt 名对齐 + RRin 下端口径（v4 已再回改，见上）
* v2 变更（vs v1）: HBT X 行 -> Q 行 4 端；hbt_mirror 展开 4 实例内联；
*   剥离版图不存在件（Vb/Vbcas/Cin/Ct/Lt）；R 行带 model + l/w；
*   RL 保留（版图真画件）
* 器件名映射: QXQ1<->版图 XQ1、QXBI1_XQo<->XBI1_XQo、RRe1<->Re1 …（Q/R 前缀 + 版图实例名）
* 组长侧跑法参数: --disable_tap_extraction --ignore_top_ports_mismatch
*   --no_series_res --no_parallel_res （H1: 两侧串并联简化对称关闭，裁定二十）
* ============================================================================
.subckt TX5G_M3_DRV2_V22 inp inn outp outn vcc
* --- 输入网络: Rin1/2 1k rhigh（Cin 占位已剥离，inp/inn 为子ckt端口；
*     v4 口径: 下端接 0 对齐版图提取真值）[D1: 删阻值 token 插衬底 0] ---
RRin1 inp 0 0 rhigh l=1.000u w=1.360u
RRin2 inn 0 0 rhigh l=1.000u w=1.360u
* --- 主四管 npn13G2（版图 Nx=10 m=1；sub 衬底接全局 0）[D4: m=10 -> Nx=10 m=1] ---
QXQ1 ccas1 bin  e1  0 npn13G2 le=900.0n we=70.00n Nx=10 m=1
QXQ2 ccas2 bb1  e2  0 npn13G2 le=900.0n we=70.00n Nx=10 m=1
QXQ3 outp nbcas ccas1 0 npn13G2 le=900.0n we=70.00n Nx=10 m=1
QXQ4 outn nbcas ccas2 0 npn13G2 le=900.0n we=70.00n Nx=10 m=1
* --- 发射极负反馈 Re1/2 1.5R rsil [D1: 删阻值 token 插衬底 0] ---
RRe1 e1 ntail 0 rsil l=1.000u w=4.665u
RRe2 e2 ntail 0 rsil l=1.000u w=4.665u
* --- 基极偏置 Rb1/2 500R rppd（Vb 源已剥离: nbias=Rb1.P2/Rb2.P2 公共金属网）
*     [D1] （H1 注意: 此两只与版图侧独立器件对拍，禁开串并联简化） ---
RRb1 bin nbias 0 rppd l=1.923u w=1.000u
RRb2 bb1 nbias 0 rppd l=1.923u w=1.000u
* --- 输出负载 RL1/2 100R rppd（版图真画件）[D1] ---
RRL1 vcc outp 0 rppd l=1.000u w=2.600u
RRL2 vcc outn 0 rppd l=1.000u w=2.600u
* --- 尾流镜像 hbt_mirror x4 展开内联（每组 = Qr Nx=1 + Qo Nx=8 + Rref 1.62k rhigh;
*     nref 每实例独立网，四条互不连通 [D3: XBI<k>/nref -> NREF<k>]） ---
QXBI1_XQr NREF1 NREF1 0 0 npn13G2 le=900.0n we=70.00n Nx=1 m=1
QXBI1_XQo ntail NREF1 0 0 npn13G2 le=900.0n we=70.00n Nx=8 m=1
RXBI1_Rref vcc NREF1 0 rhigh l=1.190u w=1.000u
QXBI2_XQr NREF2 NREF2 0 0 npn13G2 le=900.0n we=70.00n Nx=1 m=1
QXBI2_XQo ntail NREF2 0 0 npn13G2 le=900.0n we=70.00n Nx=8 m=1
RXBI2_Rref vcc NREF2 0 rhigh l=1.190u w=1.000u
QXBI3_XQr NREF3 NREF3 0 0 npn13G2 le=900.0n we=70.00n Nx=1 m=1
QXBI3_XQo ntail NREF3 0 0 npn13G2 le=900.0n we=70.00n Nx=8 m=1
RXBI3_Rref vcc NREF3 0 rhigh l=1.190u w=1.000u
QXBI4_XQr NREF4 NREF4 0 0 npn13G2 le=900.0n we=70.00n Nx=1 m=1
QXBI4_XQo ntail NREF4 0 0 npn13G2 le=900.0n we=70.00n Nx=8 m=1
RXBI4_Rref vcc NREF4 0 rhigh l=1.190u w=1.000u
* --- 已剥离件备案（版图仅 PH_PLACE 占位/测试台专有，不在本件） ---
*   Vb nbias 0 1.25 / Vbcas nbcas 0 2.05   （测试台理想源）
*   Cin1 inp bin 10p / Cin2 inn bb1 10p    （cmim 占位）
*   Ct1 outp 0 1.2p / Ct2 outn 0 1.2p      （cmim 占位）
*   Lt1 vcc outp 0.7n / Lt2 vcc outn 0.7n  （tank L 禁区占位）
.ends TX5G_M3_DRV2_V22
