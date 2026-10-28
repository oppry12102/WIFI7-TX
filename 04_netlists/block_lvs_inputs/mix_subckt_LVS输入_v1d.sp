* ============================================================================
* mix_subckt_LVS输入_v1d.sp —— **mix v34 面（XBI1 组 Activ 重叠根修件）的配套 LVS 网表**
* ============================================================================
* v1d 相对 v1c 的变更（**只改端口名与 XBI1 簇的三处网名，拓扑一字未动**）：
*
*   ① 端口集合 7 → **8**：
*      v1c 端口第 1 项是 **`XBI1/nref|ntaila`** —— 那是官方提取器把两个网**并成一个**
*      之后给出的网名（`|` 是它的并网写法）。本轮甲案把并网拆掉，版图应当导出
*      **`XBI1/nref`** 与 **`ntaila`** 两个独立端口 ⇒ v1d 按 8 端口写。
*      ⚠ 这是**预期**，不是既成事实：拆分后的端口名以官方跑出来的那份为准。
*        若官方仍给 `XBI1/nref|ntaila`（并网仍在），本件会在 XBI1 簇上失配 ——
*        那就说明**器件重叠没拆干净**，而不是网表写错。失配范围可预期地局限在
*        QXBI1_XQo / QXBI1_XQr / RXBI1_Rref 三只 + 两条尾阻 Re1a/Re2a。
*
*   ② XBI1 簇网名按**设计意图**写（与 v1c 的 `nrefa` 同一拓扑，只是改成真端口名）：
*        QXBI1_XQo : C=ntaila   B=XBI1/nref  E=gnd
*        QXBI1_XQr : C=XBI1/nref B=XBI1/nref E=gnd
*        RXBI1_Rref: nvtop  XBI1/nref
*        RRe1a/RRe2a: e1a/e2a → ntaila
*      —— 这正是版图 NET_DECL 声明的拓扑（gen_M2_mix_v34.py 里 XBI1_XQo 一行
*      `("ntaila", hnet("XBI1","nref"), "0")`），也是 v29 之前的老网表口径。
*      v1c 用内部名 `nrefa` 是为了**不预判**并网与否（裁定五十五 §四①）；本轮甲案
*      已把「并网是不是缺陷」从争议变成事实（裁定五十六 §三：Activ 重叠 2.6250 µm²），
*      故可以按意图直写。
*
*   ③ 版图真值锚换新面：m2_mix_v31.gds(ef034d51) → **m2_mix_v34.gds**（QR_OFF 25.35，
*      XBI1 组 Activ 净距 −2.625 → **+10.725 µm**，与 XBI2 组逐位同构）。
*
* ============================================================================
* gilbert_mix 子电路 schematic（LVS schematic-vs-layout 对拍用）· v1d
* ----------------------------------------------------------------------------
* 日期     : 2026-10-19 (b7e7)
* 口径来源 : b7a0 裁定二十三·五（mix LVS 前置件）+ 裁定二十四（LVS 输入对换源）
*            + 裁定五十五（端口逐字对齐）+ 裁定五十六（XBI1 组 Activ 重叠根因）
* 版图真值 : **m2_mix_v34.gds**（gen_M2_mix_v34.py，QR_OFF=25.35；Activ 足迹真值表
*            design/sow6/actgeom.py，实测源自 m2_mix_v31.gds 的官方 GDS）
* 拓扑对齐 : 行序与 pex_mix_v31.cdl 逐行对齐（行尾注释 = cdl 行名），器件 15Q/16R/6C。
* 形态口径 : D1 电阻 3T 位置式（`R名 n1 n2 0 model l= w=`，衬底=SPICE 全局 0，无阻值 token）；
*            D1-Q 四网位置式（`Q名 C B E 0 npn13G2 …`，**端子序 = C B E 衬底**）；
*            D2 衬底一律 0；D3 网名含 `/`（层次形端口名，逐字对齐版图标注）；
*            D4 we/le/Nx/m 四参全写（Nx=<N> m=1）。
*            ⚠ v1c 头注勘误（裁定五十五回信 §三，组长官方真跑实证）：我原写「reader 不做
*              大小写/分隔符归一」——**错**。官方 reader **做大小写归一**（layout=XBI2/nref ↔
*              sch=XBI2/NREF 判 Match）。故 D3 的 `/` 不是失配风险源，本件端口名照写即可。
* 器件名映射（sch 名 ↔ gen 实例 / cdl 行）:
*   QXQ1a↔XQ1a(Q1) QXQ1b↔XQ1b(Q2) QXQ2b↔XQ2b(Q3) QXQ2a↔XQ2a(Q4)
*   QXd3L↔d3L(Q5) QXd3R↔d3R(Q6)  ※ 布局填充管·三端接地·Vbe=0（DUMMY_DEVICES 台账在册）
*   QXBI1_XQo↔XBI1.XQo(Q7,Nx10) QXBI1_XQr↔XBI1.XQr(Q8,Nx1) RXBI1_Rref↔XBI1.Rref(R5)
*   QXBI2_XQo↔XBI2.XQo(Q9,Nx10) QXBI2_XQr↔XBI2.XQr(Q10,Nx1) RXBI2_Rref↔XBI2.Rref(R6)
*   QXQ3..QXQ6↔XQ3..XQ6(Q11..Q14)  RRd1/RRd2↔Rd1/Rd2(R7/R8)
*   RRba1/RRbb1/RRbb2/RRba2↔基极偏置馈入(R9..R12)  RRbin1/RRbin2↔nifbias 馈入(R13/R14)
*   RRL1/RRL2↔RL1/RL2(R15/R16)  CCca1/CCcb2/CCcb1/CCca2↔Cca1/Ccb2/Ccb1/Cca2(C1..C4)
*   CCt1/CCt2↔Ct1/Ct2(C5/C6)  QXQs↔XQs(Q15)
*   ※ **v1b 注释勘误（裁定五十六 §五）**：XBI1 组 XQo 的 C 是 **ntaila**（ntailb 是
*     XBI2 那侧），B 是 XBI1/nref —— 本件按正确口径写。
* 挂空节点备案（版图真值，deck 行为源 Bv*/Is0 不在版图）: nvtop(R5+R6 串对)、
*   nsens(Q15 二极管)、nifbias(R13+R14 对) 三节点在提取面无额外驱动——两侧同构即可。
* 组长侧跑法参数: --disable_tap_extraction --ignore_top_ports_mismatch
*   --no_series_res --no_parallel_res （同 drv2 v5 口径；如 mix 侧 H1 触发再议）
* ============================================================================
.subckt TX5G_M2_MIX_V34 XBI1/nref ntaila gnd ifp ifn nifbias nvtop XBI2/nref
* --- gm doublet 开关入对（nx=3） ---
QXQ1a nswa na1p e1a 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1
QXQ1b nswa nb1p e1b 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1
QXQ2b nswb nb2n e2b 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1
QXQ2a nswb na2n e2a 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1
* --- 布局填充管 d3L/d3R（裁定二十三·五 补画；台账在册；三端接地 Vbe=0） ---
QXd3L gnd gnd gnd 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1
QXd3R gnd gnd gnd 0 npn13G2 le=900.0n we=70.00n Nx=3 m=1
* --- 尾阻 Re（rsil 30Ω 档） ---
RRe1a e1a ntaila 0 rsil l=4.286u w=1.000u
RRe2a e2a ntaila 0 rsil l=4.286u w=1.000u
RRe1b e1b ntailb 0 rsil l=4.286u w=1.000u
RRe2b e2b ntailb 0 rsil l=4.286u w=1.000u
* --- 镜像组 XBI1（ntaila 侧；v3.4 起 XQo/XQr 的 Activ 足迹不再重叠，C 与 B 分网） ---
QXBI1_XQo ntaila XBI1/nref gnd 0 npn13G2 le=900.0n we=70.00n Nx=10 m=1
QXBI1_XQr XBI1/nref XBI1/nref gnd 0 npn13G2 le=900.0n we=70.00n Nx=1 m=1
RXBI1_Rref nvtop XBI1/nref 0 rhigh l=1.000u w=2.000u
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
.ends TX5G_M2_MIX_V34
* 器件统计: Q=15 R=16 C=6（与 v1c 逐行同拓扑；XBI1 簇改用真端口名 nref）
