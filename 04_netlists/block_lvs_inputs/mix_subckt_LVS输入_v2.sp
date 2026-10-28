* ============================================================================
* gilbert_mix 子电路 schematic（LVS schematic-vs-layout 对拍用）· v1（首版）
* ----------------------------------------------------------------------------
* 日期     : 2026-10-18 (b7e7)
* 口径来源 : b7a0 裁定二十三·五（mix LVS 前置件：补画 QX5/QX6 使两侧各 15 只逐件可对）
*            + 裁定二十四（LVS 输入对换源；D1-D4 形态判据适用 schematic 侧）
* 版图真值 : m2_mix_v29.gds（sha256 8f6da23dd5ec85bcc31f85ffe3887a25831b9761d7ff1065e415611ff93a9b34）
*            → pex_mix_v29.json（端子锚定版提取器）→ 换源件 pex_mix_v27.cdl（ce97750b03949593）
* 拓扑对齐 : 行序与换源 cdl 逐行对齐（行尾注释 = cdl 行名），器件 15Q/16R/6C，
*            网名对齐版图标注（datatype 25）。
* 形态口径 : D1 电阻 3T 位置式（`R名 n1 n2 0 model l= w=`，衬底=SPICE 全局 0，无阻值 token）；
*            D1-Q 四网位置式（`Q名 C B E 0 npn13G2 …`）；D2 衬底一律 0（地「轨网名」保留
*            版图标名 gnd——轨网与全局衬底 0 是两个网，layout 侧同构）；D3 网名禁 `/`
*            （版图双标签域 XBI1/nref+ntaila 取轨名 ntaila 单名，拓扑同一金属域）；
*            D4 we/le/Nx/m 四参全写（Nx=<N> m=1，对齐版图实测）。
* 器件名映射（sch 名 ↔ gen 实例 / cdl 行）:
*   QXQ1a↔XQ1a(Q1) QXQ1b↔XQ1b(Q2) QXQ2b↔XQ2b(Q3) QXQ2a↔XQ2a(Q4)
*   QXd3L↔d3L(Q5) QXd3R↔d3R(Q6)  ※ d3L/d3R=布局填充管·三端接地·Vbe=0 无正向偏置
*     （DUMMY_DEVICES 台账在册：design/sow6/DUMMY_DEVICES_台账_mix_Q5Q6_2026-10-18.md）
*   QXBI1_XQo↔XBI1.XQo(Q7,Nx10) QXBI1_XQr↔XBI1.XQr(Q8,Nx1) RXBI1_Rref↔XBI1.Rref(R5)
*   QXBI2_XQo↔XBI2.XQo(Q9,Nx10) QXBI2_XQr↔XBI2.XQr(Q10,Nx1) RXBI2_Rref↔XBI2.Rref(R6)
*     ※ XBI1 组版图实态：XQo/XQr 的 C=B 同落 ntaila 轨金属域（pex_mix_v29 域 M1:6
*       双标签 XBI1/nref+ntaila 实测，非提取合并产物）；XBI2 组为标准镜像
*       （XQo C=ntailb B=nref，XQr C=B=nref）。
*   QXQ3..QXQ6↔XQ3..XQ6(Q11..Q14)  RRd1/RRd2↔Rd1/Rd2(R7/R8)
*   RRba1/RRbb1/RRbb2/RRba2↔基极偏置馈入(R9..R12)  RRbin1/RRbin2↔nifbias 馈入(R13/R14)
*   RRL1/RRL2↔RL1/RL2(R15/R16)  CCca1/CCcb2/CCcb1/CCca2↔Cca1/Ccb2/Ccb1/Cca2(C1..C4)
*   CCt1/CCt2↔Ct1/Ct2(C5/C6)  QXQs↔XQs(Q15)
* 挂空节点备案（版图真值，deck 行为源 Bv*/Is0 不在版图）: nvtop(R5+R6 串对)、
*   nsens(Q15 二极管)、nifbias(R13+R14 对) 三节点在提取面无额外驱动——两侧同构即可。
* 组长侧跑法参数: --disable_tap_extraction --ignore_top_ports_mismatch
*   --no_series_res --no_parallel_res （同 drv2 v5 口径；如 mix 侧 H1 触发再议）
* ============================================================================
.subckt TX5G_M2_MIX_V32 ifp ifn lop lon rfop rfon vcc
* --- gm doublet 开关入对（nx=3） ---
QXQ1a nswa na1p e1a 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1        $ cdl Q1
QXQ1b nswa nb1p e1b 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1        $ cdl Q2
QXQ2b nswb nb2n e2b 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1        $ cdl Q3
QXQ2a nswb na2n e2a 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1        $ cdl Q4
* --- 布局填充管 d3L/d3R（裁定二十三·五 补画；台账在册；三端接地 Vbe=0） ---
QXd3L gnd gnd gnd 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1          $ cdl Q5
QXd3R gnd gnd gnd 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1          $ cdl Q6
* --- 尾阻 Re（rsil 30Ω 档） ---
RRe1a e1a ntaila 0 rsil l=4.286u w=1.000u                         $ cdl R1
RRe2a e2a ntaila 0 rsil l=4.286u w=1.000u                         $ cdl R2
RRe1b e1b ntailb 0 rsil l=4.286u w=1.000u                         $ cdl R3
RRe2b e2b ntailb 0 rsil l=4.286u w=1.000u                         $ cdl R4
* --- 镜像组 XBI1（ntaila 侧；XQo/XQr C=B 同落 ntaila 轨=版图实态） ---
QXBI1_XQo ntaila ntaila gnd 0 npn13G2 le=900.0n we=70.00n Nx=10 m=1   $ cdl Q7
QXBI1_XQr ntaila ntaila gnd 0 npn13G2 le=900.0n we=70.00n Nx=1 m=1    $ cdl Q8
RXBI1_Rref nvtop ntaila 0 rhigh l=1.000u w=2.000u                 $ cdl R5
* --- 镜像组 XBI2（ntailb 侧；标准镜像 XQr 基准 nref） ---
QXBI2_XQo ntailb nref gnd 0 npn13G2 le=900.0n we=70.00n Nx=10 m=1     $ cdl Q9
QXBI2_XQr nref nref gnd 0 npn13G2 le=900.0n we=70.00n Nx=1 m=1        $ cdl Q10
RXBI2_Rref nvtop nref 0 rhigh l=1.000u w=2.000u                   $ cdl R6
* --- 开关对（nx=6） ---
QXQ3 rfop lopd nswa 0 npn13G2 le=900.0n we=70.00n Nx=6 m=1        $ cdl Q11
QXQ4 rfon lond nswa 0 npn13G2 le=900.0n we=70.00n Nx=6 m=1        $ cdl Q12
QXQ5 rfon lopd nswb 0 npn13G2 le=900.0n we=70.00n Nx=6 m=1        $ cdl Q13
QXQ6 rfop lond nswb 0 npn13G2 le=900.0n we=70.00n Nx=6 m=1        $ cdl Q14
* --- C 臂 Rd（rsil 10Ω 档） ---
RRd1 lop lopd 0 rsil l=1.429u w=1.000u                            $ cdl R7
RRd2 lon lond 0 rsil l=1.429u w=1.000u                            $ cdl R8
* --- 基极偏置馈入（rhigh 2k 档） ---
RRba1 na1p nbiasL 0 rhigh l=1.470u w=1.000u                       $ cdl R9
RRbb1 nb1p nbiasH 0 rhigh l=1.470u w=1.000u                       $ cdl R10
RRbb2 nb2n nbiasL 0 rhigh l=1.470u w=1.000u                       $ cdl R11
RRba2 na2n nbiasH 0 rhigh l=1.470u w=1.000u                       $ cdl R12
* --- 输入偏置公共轨 nifbias ---
RRbin1 ifp nifbias 0 rhigh l=1.470u w=1.000u                      $ cdl R13
RRbin2 ifn nifbias 0 rhigh l=1.470u w=1.000u                      $ cdl R14
* --- 输入耦合电容（cmim 1n 档: area=514.382 perim=90.72） ---
CCca1 ifp na1p 0 cmim area=514.382 perim=90.72                    $ cdl C1
CCcb2 ifn nb2n 0 cmim area=514.382 perim=90.72                    $ cdl C2
CCcb1 ifp nb1p 0 cmim area=514.382 perim=90.72                    $ cdl C3
CCca2 ifn na2n 0 cmim area=514.382 perim=90.72                    $ cdl C4
* --- 负载 RL（rsil 45Ω 档） + 负载臂对地 Ct（0.84p 档） ---
RRL1 vcc rfop 0 rsil l=6.429u w=1.000u                            $ cdl R15
RRL2 vcc rfon 0 rsil l=6.429u w=1.000u                            $ cdl R16
CCt1 rfop gnd 0 cmim area=514.382 perim=90.72                     $ cdl C5
CCt2 rfon gnd 0 cmim area=514.382 perim=90.72                     $ cdl C6
* --- 敏感管 XQs（nx=1，C==B 二极管接法） ---
QXQs nsens nsens gnd 0 npn13G2 le=900.0n we=70.00n Nx=1 m=1       $ cdl Q15
.ends TX5G_M2_MIX_V32
* 器件统计: Q=15 R=16 C=6（与换源 cdl 逐行对齐；Q5/Q6=d3L/d3R 台账件）
