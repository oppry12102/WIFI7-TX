* ============================================================================
* drv1 子电路 schematic（LVS schematic-vs-layout 对拍用）· v1（首件）
* ----------------------------------------------------------------------------
* 日期     : 2026-10-17 (b7a0 组长代造，bb1 M5 验证点立照专用)
* 口径来源 : drv2_subckt_LVS输入_v3.sp 形态学（Q 行 4 端 / R 行带 model+l/w /
*            器件名映射 Q|R 前缀+版图实例名 / 测试台件剥离）
* 版图真值 : gen_M3_drv1_v18.py (2a305b68) DEV_NETS/NET_DECL + v18 重跑 gen stdout
*            [res] 行（本口 13:29Z 重跑，gdsdiff vs 现役 353e5a56 = IDENTICAL）
* ----------------------------------------------------------------------------
* 与 drv2 v3 的结构差异（drv1 真值）:
*   1. 主管 2 只 XQ1/XQ2 Nx=6（drv2 四管 Nx=10）；XQ2 B=bb1
*   2. 镜像组仅 1 组（XBI/nref，_NSEP=/ 无组号）
*   3. R 选型不同: Re=rsil 1.000/1.750（drv2 为 4.665）、Rb=1k rhigh 1.000/1.360
*      （drv2 为 500 rppd 1.923/1.000）、Rin=1k rhigh、RL=100 rppd 1.000/2.600
*   4. Rin1/2 下端 = 0（版图真值接 gnd 网，gen §8 注释"inp/inn → gnd"；
*      schematic 侧 0 ↔ 版图 gnd 经 ptap 拓扑同构，照 drv2 v3 的 E=0 同一口径）
*   5. 剥离: Cin1/Cin2/Ct1/Ct2（cmim 外置预留 235/5 非制造层，v18 无真件）、
*      Lt1/Lt2（tank L 禁区占位）、Vb/Vbcas（测试台理想源）
*   6. bb1 网 = XQ2.B + Rb2.P1（v2 §五预测: bb1 M5 横带骑 XQr body 必不焊，
*      本轮立照 = extracted.cir 里 bb1 应保持独立二件网）
* 组长侧跑法: run_lvs.py --disable_tap_extraction --ignore_top_ports_mismatch（0.30.0）
* ============================================================================
.subckt TX5G_M3_DRV1_V16 inp inn cop con vcc
* --- 输入网络: Rin1/2 1k rhigh（P2=gnd 真值→0） ---
RRin1 inp 0 1000 rhigh l=1.000u w=1.360u
RRin2 inn 0 1000 rhigh l=1.000u w=1.360u
* --- 主两管 npn13G2 Nx=6 -> m=6（sub 经衬底接 0；C/B/E 照 DEV_NETS） ---
QXQ1 cop bin e1 0 npn13G2 le=900.0n we=70.00n m=6
QXQ2 con bb1 e2 0 npn13G2 le=900.0n we=70.00n m=6
* --- 发射极负反馈 Re1/2 4R rsil（v18 stdout 真值 w=1.750） ---
RRe1 e1 ntail 4 rsil l=1.000u w=1.750u
RRe2 e2 ntail 4 rsil l=1.000u w=1.750u
* --- 基极偏置 Rb1/2 1k rhigh（Vb 源已剥离: nbias=Rb1.P2/Rb2.P2 公共金属网） ---
RRb1 bin nbias 1000 rhigh l=1.000u w=1.360u
RRb2 bb1 nbias 1000 rhigh l=1.000u w=1.360u
* --- 输出负载 RL1/2 100R rppd（版图真画件） ---
RRL1 vcc cop 100 rppd l=1.000u w=2.600u
RRL2 vcc con 100 rppd l=1.000u w=2.600u
* --- 尾流镜像 hbt_mirror 单组展开内联（Qr Nx=1 + Qo Nx=8 + Rref 1.62k rhigh;
*     nref 独立网 XBI/nref，照版图 NESTED_STYLE=hier 网名形态） ---
QXBI_XQr XBI/nref XBI/nref 0 0 npn13G2 le=900.0n we=70.00n m=1
QXBI_XQo ntail XBI/nref 0 0 npn13G2 le=900.0n we=70.00n m=8
RXBI_Rref vcc XBI/nref 1620 rhigh l=1.190u w=1.000u
* --- 已剥离件备案（版图仅 235/5 预留/测试台专有，不在本件） ---
*   Cin1 inp bin 10p / Cin2 inn bb1 10p   （cmim 外置预留 16+16 只）
*   Ct1 cop 0 0.84p / Ct2 con 0 0.84p     （cmim 外置预留，p2 侧真接 gnd）
*   Lt1 vcc cop 0.7n / Lt2 vcc con 0.7n   （tank L 禁区占位）
*   Vb nbias 0 1.25 / Vbcas nbcas 0 2.05  （测试台理想源；drv1 无 nbcas 网）
.ends TX5G_M3_DRV1_V16
