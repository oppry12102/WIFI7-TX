* ----------------------------------------------------------------------------
* v1c 变更（vs v1b，**只动 .subckt 端口行 + 8 条器件行的网名**，共 9 行）:
*   起因（裁定五十五 §四②）：**端口集合根本不是同一组**。
*   · 版图实际导出 7 个顶层端口:
*       `XBI1/nref|ntaila` `gnd` `ifp` `ifn` `nifbias` `nvtop` `XBI2/nref`
*   · v1b `.subckt` 声明 7 个:
*       `ifp ifn lop lon rfop rfon vcc`
*     ⇒ IFN/IFP/RFOP/RFON/NTAILA/NVTOP/NREF 一律成对 `layout=? ↔ sch=?` 翻车。
*   本件把端口改成**版图实际导出的逐字拼写**（含 `/`、`|` 与混合大小写）——
*   因为 **reader 不做大小写归一**（`layout=gnd ↔ sch=GND` 也失配），
*   能对齐的唯一口径就是逐字照抄，故不取「统一大写/统一小写」任一方案。
*   体内网名随之改写，使每个端口在 body 内**真被引用**（否则 check_netlist_dc
*   判「端口零引用」FATAL）：
*     `XBI1/nref|ntaila` ← 原 `ntaila`（RRe1a/RRe2a/QXBI1_XQo）
*     `XBI2/nref`         ← 原 XBI2 簇的 `nref`（QXBI2_XQo/XQr/RXBI2_Rref）
*   v1b 的 `lop`/`lon`/`vcc` 在 v31 版图**未导出** ⇒ 降为**内部网**（不动器件连接）
*
*   ★ **本件不是乙案**（刻意不预判裁定五十五 §四①）：
*     XBI1 簇的参考网仍写成**独立内部网 `nrefa`**（QXBI1_XQo.B / QXBI1_XQr.C,B /
*     RXBI1_Rref 上端），即保留「镜像参考网独立」的设计意图。
*     ⇒ 若官方提取真把 XBI1 的 C/B 并到端口那个网上，跑 v1c 会在**这一簇**
*       （Q7/Q8/R5 三只）上失配，把 §四① 的分歧**单独隔离**出来；
*       若失配消失，则官方并网是提取口径产物。
*     真要按现状对齐（同网），那是另一件（可叫 v1d = 乙案），本件不做。
*
*   若 reader 拒收含 `/`、`|` 的端口名，退路 = 保留现行配方已带的
*   `--ignore_top_ports_mismatch`，并另出端口改名对照表。
* ----------------------------------------------------------------------------

* ============================================================================
* gilbert_mix 子电路 schematic（LVS schematic-vs-layout 对拍用）· v1b（首版）
* ----------------------------------------------------------------------------
* 日期     : 2026-10-18 (b7e7)
* 口径来源 : b7a0 裁定二十三·五（mix LVS 前置件：补画 QX5/QX6 使两侧各 15 只逐件可对）
*            + 裁定二十四（LVS 输入对换源；D1-D4 形态判据适用 schematic 侧）
* 版图真值 : m2_mix_v31.gds（sha256 ef034d51202c2db8ebc8f78c74c798c55b90f984870181839d885d39985837c1）
*            → pex_mix_v31.json（端子锚定版提取器）→ 换源件 pex_mix_v31.cdl（f6ba956041d9...）
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
*     ※ XBI1 组版图实态：XQo/XQr 的 C=B 同落 nref 轨金属域（pex_mix_v31 域 M1:6
*       双标签 XBI1/nref+ntaila 实测，非提取合并产物）；XBI2 组为标准镜像
*       （XQo C=ntailb B=nref，XQr C=B=nref）。
*     ※ v31 面修复：Q7/Q8/R5 节点从 v29 面 ntaila 短接拓扑改为 nref 独立成网
*       （裁定五十三：ntaila 短接解除，镜像簇拓扑与 v31 面锚一致）。
*   QXQ3..QXQ6↔XQ3..XQ6(Q11..Q14)  RRd1/RRd2↔Rd1/Rd2(R7/R8)
*   RRba1/RRbb1/RRbb2/RRba2↔基极偏置馈入(R9..R12)  RRbin1/RRbin2↔nifbias 馈入(R13/R14)
*   RRL1/RRL2↔RL1/RL2(R15/R16)  CCca1/CCcb2/CCcb1/CCca2↔Cca1/Ccb2/Ccb1/Cca2(C1..C4)
*   CCt1/CCt2↔Ct1/Ct2(C5/C6)  QXQs↔XQs(Q15)
* 挂空节点备案（版图真值，deck 行为源 Bv*/Is0 不在版图）: nvtop(R5+R6 串对)、
*   nsens(Q15 二极管)、nifbias(R13+R14 对) 三节点在提取面无额外驱动——两侧同构即可。
* 组长侧跑法参数: --disable_tap_extraction --ignore_top_ports_mismatch
*   --no_series_res --no_parallel_res （同 drv2 v5 口径；如 mix 侧 H1 触发再议）
* ============================================================================
.subckt TX5G_M2_MIX_V31 XBI1/nref|ntaila gnd ifp ifn nifbias nvtop XBI2/nref
* --- gm doublet 开关入对（nx=3） ---
QXQ1a nswa na1p e1a 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1
QXQ1b nswa nb1p e1b 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1
QXQ2b nswb nb2n e2b 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1
QXQ2a nswb na2n e2a 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1
* --- 布局填充管 d3L/d3R（裁定二十三·五 补画；台账在册；三端接地 Vbe=0） ---
QXd3L gnd gnd gnd 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1
QXd3R gnd gnd gnd 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1
* --- 尾阻 Re（rsil 30Ω 档） ---
RRe1a e1a XBI1/nref|ntaila 0 rsil l=4.286u w=1.000u
RRe2a e2a XBI1/nref|ntaila 0 rsil l=4.286u w=1.000u
RRe1b e1b ntailb 0 rsil l=4.286u w=1.000u
RRe2b e2b ntailb 0 rsil l=4.286u w=1.000u
* --- 镜像组 XBI1（ntaila 侧；XQo/XQr C=B 同落 ntaila 轨=版图实态） ---
QXBI1_XQo XBI1/nref|ntaila nrefa gnd 0 npn13G2 le=900.0n we=70.00n Nx=10 m=1
QXBI1_XQr nrefa nrefa gnd 0 npn13G2 le=900.0n we=70.00n Nx=1 m=1
RXBI1_Rref nvtop nrefa 0 rhigh l=1.000u w=2.000u
* --- 镜像组 XBI2（ntailb 侧；标准镜像 XQr 基准 nref） ---
QXBI2_XQo ntailb XBI2/nref gnd 0 npn13G2 le=900.0n we=70.00n Nx=10 m=1
QXBI2_XQr XBI2/nref XBI2/nref gnd 0 npn13G2 le=900.0n we=70.00n Nx=1 m=1
RXBI2_Rref nvtop XBI2/nref 0 rhigh l=1.000u w=2.000u
* --- 开关对（nx=6） ---
QXQ3 rfop lopd nswa 0 npn13G2 le=900.0n we=70.00n Nx=6 m=1
QXQ4 rfon lond nswa 0 npn13G2 le=900.0n we=70.00n Nx=6 m=1
QXQ5 rfon lopd nswb 0 npn13G2 le=900.0n we=70.00n Nx=6 m=1
QXQ6 rfop lond nswb 0 npn13G2 le=900.0n we=70.00n Nx=6 m=1
* --- C 臂 Rd（rsil 10Ω 档） ---
RRd1 lop lopd 0 rsil l=1.429u w=1.000u
RRd2 lon lond 0 rsil l=1.429u w=1.000u
* --- 基极偏置馈入（rhigh 2k 档） ---
RRba1 na1p nbiasL 0 rhigh l=1.470u w=1.000u
RRbb1 nb1p nbiasH 0 rhigh l=1.470u w=1.000u
RRbb2 nb2n nbiasL 0 rhigh l=1.470u w=1.000u
RRba2 na2n nbiasH 0 rhigh l=1.470u w=1.000u
* --- 输入偏置公共轨 nifbias ---
RRbin1 ifp nifbias 0 rhigh l=1.470u w=1.000u
RRbin2 ifn nifbias 0 rhigh l=1.470u w=1.000u
* --- 输入耦合电容（cmim 1n 档: area=514.382 perim=90.72） ---
CCca1 ifp na1p 0 cmim area=514.382 perim=90.72
CCcb2 ifn nb2n 0 cmim area=514.382 perim=90.72
CCcb1 ifp nb1p 0 cmim area=514.382 perim=90.72
CCca2 ifn na2n 0 cmim area=514.382 perim=90.72
* --- 负载 RL（rsil 45Ω 档） + 负载臂对地 Ct（0.84p 档） ---
RRL1 vcc rfop 0 rsil l=6.429u w=1.000u
RRL2 vcc rfon 0 rsil l=6.429u w=1.000u
CCt1 rfop gnd 0 cmim area=514.382 perim=90.72
CCt2 rfon gnd 0 cmim area=514.382 perim=90.72
* --- 敏感管 XQs（nx=1，C==B 二极管接法） ---
QXQs nsens nsens gnd 0 npn13G2 le=900.0n we=70.00n Nx=1 m=1
.ends TX5G_M2_MIX_V31
* 器件统计: Q=15 R=16 C=6（与 v31 面 cdl 逐行对齐；Q7/Q8/R5 已改为 nref 独立拓扑；Q5/Q6=d3L/d3R 台账件）
