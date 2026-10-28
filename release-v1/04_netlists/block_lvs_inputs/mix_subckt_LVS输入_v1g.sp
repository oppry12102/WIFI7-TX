* ============================================================================
* mix_subckt_LVS输入_v1g.sp —— **mix v35 面（v34 + M4.b 根修）的配套 LVS 网表**
* ============================================================================
* ★ v1g 相对 v1f 的变更（**只改顶层名，器件行/端口/参数一字未动**）：
*   `.subckt`/`.ends` 顶层名 TX5G_M2_MIX_V34 → **TX5G_M2_MIX_V35**（2 处）。
*   依据律 F14：面锚的 LVS 配套网表，其 `.subckt` 必须与所配那一版版图的顶层名
*   **逐字相同**（否则 KLayout 直接报 `Can't find a schematic counterpart for the
*   top cell`）——网表版本号不得在版图层之外单独漂移。
*   ⇒ v1g 配 **m2_mix_v35.gds**（gen_M2_mix_v35.py）；v1f 配 m2_mix_v34.gds。
*   两件**器件行逐字节相同**（10116B，仅顶层名 2 处不同）：v35 的 M4.b 修复只动
*   **M4 一层的 3 处 wire_v 调用**（× d3L/d3R 两只 = 6 段立管；假管 gnd 立管外移 δ=0.100µm），PCell 实例
*   一字不动 ⇒ 引脚坐标/C-B-E 的 M1 垫/hop 落柱/NET_DECL 全不变 ⇒ **LVS 侧零影响**，
*   故网表拓扑无需任何改动（自证：见 gen_M2_mix_v35.py 的 v3.5 四条断言 +
*   probe_m4b_fix_b7e7.py 的 δ 扫描实测）。
*
* ----------------------------------------------------------------------------
* 以下 v1f 相对 v1d 的变更说明（**四件事，拓扑一字未动**），v1g 全部继承：
*
*   ① 端口集合 8 → **29**（按官方提取 29 端口逐字对齐，裁定五十八 §五③）：
*      v1d 只声明 8 个（XBI1/nref ntaila gnd ifp ifn nifbias nvtop XBI2/nref），
*      而官方提取出 29 个（含 rfop/rfon/lop/lon/vcc/e1a/e2a/e1b/e2b/ntailb/nswa/nswb/
*      na1p/nb1p/nb2n/na2n/lond/lopd/nsens/nbiasL/nbiasH 等内部网被提升）。
*      差异纯是 `.subckt` 声明行少写 21 个端口——v1d 器件行网名（去 `0`）与官方
*      29 端口**逐字相同**（v1f 自证：见头注 §自证）。
*
*   ② 衬底端子 `0` → `gnd`（37 处，裁定五十八 §五④ + 组长 v1e 实证 Match 15→20）：
*      v1d 的 E 极写 `gnd`、衬底写 `0`——**同一行内混用两个地名**，reader 把 E 极
*      的 `gnd` 与版图 `gnd` 配对、把衬底的 `0` 与版图 `gnd` 配对 ⇒ 衬底那侧的器件
*      端子成对落单。v1f 统一写 `gnd`（与版图标注一致）。
*      ⚠ 与 drv1 v5 / drv2 v6（都 LVS PASS，衬底全写 `0`）不同——drv1/drv2 的 E 极
*      也写 `0`（统一），而 mix v1d 的 E 极写 `gnd`（混用）。统一写 `gnd` 是 mix 侧
*      的正确做法（与版图 `gnd` 标注一致；drv1/drv2 统一写 `0` 也与它们的版图一致）。
*
*   ③ 电容 6 只参数形态改写（裁定五十八 §五②）：
*      v1d: `CCca1 ifp na1p 0 cmim area=514.382 perim=90.72`（3 端子 + cmim + area/perim）
*      v1f: `CCca1 na1p ifp cap_cmim w=23.61u l=23.61u A=557.4321p P=94.44u m=1`
*           （2 端子 + cap_cmim + w/l/A/P/m）
*      差异：端子数（2 vs 3）、模型名（cap_cmim vs cmim）、参数集（w/l/A/P/m vs area/perim）、
*      口径（全板 557.4321 vs 净区 514.382）。
*      依据：官方提取器 `custom_mim_extractor.lvs` 的 `DeviceCustomMIM` 类定义 2 端子
*      （mim_top/mim_btm，无 sub）+ 参数 w/l/A/P/m（`capacitors_mod.lib` L64 `.subckt cap_cmim
*      PLUS MINUS` 证实 2 端子无 sub）。A=23.61²=557.4321 µm² / P=4×23.61=94.44 µm 自证
*      与官方提取 C$33 的 A=557.4321p / P=94.44u 逐位一致。
*      ⚠ 端子序：官方提取实证 C$33 `na1p ifp` ⇒ (n_hi, n_lo) = (TOPM1 上板, M5 下板)。
*      gen 里 `mkcmim(name, n_lo, n_hi, px, py)` ⇒ v1f 按 (n_hi, n_lo) 序写。
*
*   ④ D1-C 判据器升级（lvs_source_audit.py）：
*      v1d 的 3T 位置式（cmim 3T: 板1 板2 sub 位置式）是 ngspice_substitute reader 的契约，
*      不是 lvs_reader 的唯一合法形态。官方 cap_cmim 是 2 端子（mim_top/mim_btm，无 sub）+
*      w/l/A/P/m ⇒ lvs_reader 侧合法形态 = 2T 位置式（`C名 n_hi n_lo cap_cmim w= l= A= P= m=`）。
*      v1f 按此形态写。**D1-C 判据器已于 2026-10-19 升级完成**（skills/lvs_source_audit.py）：
*      现支持两种合法形态——① 官方提取 2T `cap_cmim`（lvs_reader 侧正解，本件用的就是它）；
*      ② cdl/代入器 3T `cmim`（ngspice_substitute 契约）。判法 = 按 (模型名, 模型位) 配对：
*      `cap_cmim`@idx3 = 2T 合法、`cmim`@idx4 = 3T 合法，其余组合 FAIL。
*      同批升级：D2 由「衬底写字面 gnd 一律 FAIL」改为**一致性判据**（真缺陷是**混用**两个
*      地名，不是「写了 gnd」）⇒ 本件（全表统一 `gnd`）判**合规**，误报 21→2（只剩 D3 已知
*      披露例外）；`pair` 模式加地网归一（`ground_equiv`）+ 电容端子序反转判定。
*      回归实测：drv1 v5 / drv2 v6（都 LVS PASS）仍 ok=true **零回退**；v1b/v1c/v1d 精确抓出
*      `D2-分裂` + 7 条 `D2-混用`（正是官方 FAIL 根因）。
*
* ============================================================================
* gilbert_mix 子电路 schematic（LVS schematic-vs-layout 对拍用）· v1g
* ----------------------------------------------------------------------------
* 日期     : 2026-10-19 (b7e7)
* 口径来源 : b7a0 裁定二十三·五（mix LVS 前置件）+ 裁定二十四（LVS 输入对换源）
*            + 裁定五十五（端口逐字对齐）+ 裁定五十六（XBI1 组 Activ 重叠根因）
*            + 裁定五十八（v1d→v1f 四件事：端口 29 + 衬底 gnd + 电容 2T + D1-C 升级）
*            + 裁定六十/六十补充（v34 代跑复核通过 + M4.b 镜像归因 ⇒ v1g 配 v35 面）
* 版图真值 : **m2_mix_v35.gds**（gen_M2_mix_v35.py = v34 + M4.b 根修：假管 gnd 立管外移
*            δ=0.100µm，QR_OFF=25.35 不变；Activ 足迹真值表 design/sow6/actgeom.py，
*            实测源自 m2_mix_v31.gds 的官方 GDS）
*            ⚠ v35 相对 v34 **只动 M4 一层的 3 处 wire_v 调用**（× d3L/d3R = 6 段；d3L/d3R 假管 gnd 立管 x：
*            ±50.000 → ±50.100），PCell 实例一字不动 ⇒ 引脚/焊盘/NET_DECL 全不变
*            ⇒ **本件拓扑与 v1f 逐字节相同**（仅顶层名 2 处不同）。
* 拓扑对齐 : 行序与 pex_mix_v31.cdl 逐行对齐（行尾注释 = cdl 行名），器件 15Q/16R/6C。
* 形态口径 : D1 电阻 3T 位置式（`R名 n1 n2 gnd model l= w=`，衬底=版图 gnd，无阻值 token）；
*            D1-Q 四网位置式（`Q名 C B E gnd npn13G2 …`，**端子序 = C B E 衬底**）；
*            D1-C **2T 位置式**（`C名 n_hi n_lo cap_cmim w= l= A= P= m=`，无 sub）；
*            D3 网名含 `/`（层次形端口名，逐字对齐版图标注）；
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
* §自证：v1f 器件行网名（去 `gnd`）与官方 29 端口逐字相同
*   v1f 器件行网名 = {XBI1/nref, XBI2/nref, e1a, e1b, e2a, e2b, ifn, ifp, lon, lond, lop,
*                    lopd, na1p, na2n, nb1p, nb2n, nbiasH, nbiasL, nifbias, nsens, nswa, nswb,
*                    ntaila, ntailb, nvtop, rfon, rfop, vcc, gnd} = 29 个
*   官方提取端口 = {gnd, ifp, ifn, nifbias, nvtop, XBI1/nref, ntaila, XBI2/nref, rfop, rfon,
*                  e1a, e2a, e1b, e2b, ntailb, nswa, nswb, na1p, nb1p, nb2n, na2n, lond, lopd,
*                  nsens, lop, lon, vcc, nbiasL, nbiasH} = 29 个
*   差集 = ∅ ✓
* ============================================================================
.subckt TX5G_M2_MIX_V35 gnd ifp ifn nifbias nvtop XBI1/nref ntaila XBI2/nref
+ rfop rfon e1a e2a e1b e2b ntailb nswa nswb na1p nb1p nb2n na2n lond lopd
+ nsens lop lon vcc nbiasL nbiasH
* --- gm doublet 开关入对（nx=3） ---
QXQ1a nswa na1p e1a gnd npn13G2 le=900.0n we=70.00n Nx=3 m=1
QXQ1b nswa nb1p e1b gnd npn13G2 le=900.0n we=70.00n Nx=3 m=1
QXQ2b nswb nb2n e2b gnd npn13G2 le=900.0n we=70.00n Nx=3 m=1
QXQ2a nswb na2n e2a gnd npn13G2 le=900.0n we=70.00n Nx=3 m=1
* --- 布局填充管 d3L/d3R（裁定二十三·五 补画；台账在册；三端接地 Vbe=0） ---
QXd3L gnd gnd gnd gnd npn13G2 le=900.0n we=70.00n Nx=3 m=1
QXd3R gnd gnd gnd gnd npn13G2 le=900.0n we=70.00n Nx=3 m=1
* --- 尾阻 Re（rsil 30Ω 档） ---
RRe1a e1a ntaila gnd rsil l=4.286u w=1.000u
RRe2a e2a ntaila gnd rsil l=4.286u w=1.000u
RRe1b e1b ntailb gnd rsil l=4.286u w=1.000u
RRe2b e2b ntailb gnd rsil l=4.286u w=1.000u
* --- 镜像组 XBI1（ntaila 侧；v3.4 起 XQo/XQr 的 Activ 足迹不再重叠，C 与 B 分网） ---
QXBI1_XQo ntaila XBI1/nref gnd gnd npn13G2 le=900.0n we=70.00n Nx=10 m=1
QXBI1_XQr XBI1/nref XBI1/nref gnd gnd npn13G2 le=900.0n we=70.00n Nx=1 m=1
RXBI1_Rref nvtop XBI1/nref gnd rhigh l=1.000u w=2.000u
* --- 镜像组 XBI2（ntailb 侧；标准镜像 XQr 基准 nref） ---
QXBI2_XQo ntailb XBI2/nref gnd gnd npn13G2 le=900.0n we=70.00n Nx=10 m=1
QXBI2_XQr XBI2/nref XBI2/nref gnd gnd npn13G2 le=900.0n we=70.00n Nx=1 m=1
RXBI2_Rref nvtop XBI2/nref gnd rhigh l=1.000u w=2.000u
* --- 开关对（nx=6） ---
QXQ3 rfop lopd nswa gnd npn13G2 le=900.0n we=70.00n Nx=6 m=1
QXQ4 rfon lond nswa gnd npn13G2 le=900.0n we=70.00n Nx=6 m=1
QXQ5 rfon lopd nswb gnd npn13G2 le=900.0n we=70.00n Nx=6 m=1
QXQ6 rfop lond nswb gnd npn13G2 le=900.0n we=70.00n Nx=6 m=1
* --- C 臂 Rd（rsil 10Ω 档） ---
RRd1 lop lopd gnd rsil l=1.429u w=1.000u
RRd2 lon lond gnd rsil l=1.429u w=1.000u
* --- 基极偏置馈入（rhigh 2k 档） ---
RRba1 na1p nbiasL gnd rhigh l=1.470u w=1.000u
RRbb1 nb1p nbiasH gnd rhigh l=1.470u w=1.000u
RRbb2 nb2n nbiasL gnd rhigh l=1.470u w=1.000u
RRba2 na2n nbiasH gnd rhigh l=1.470u w=1.000u
* --- 输入偏置公共轨 nifbias ---
RRbin1 ifp nifbias gnd rhigh l=1.470u w=1.000u
RRbin2 ifn nifbias gnd rhigh l=1.470u w=1.000u
* --- 输入耦合电容（cap_cmim 2T 位置式，w=l=23.61µm 见方，A=557.4321p P=94.44u） ---
CCca1 na1p ifp cap_cmim w=23.61u l=23.61u A=557.4321p P=94.44u m=1
CCcb2 nb2n ifn cap_cmim w=23.61u l=23.61u A=557.4321p P=94.44u m=1
CCcb1 nb1p ifp cap_cmim w=23.61u l=23.61u A=557.4321p P=94.44u m=1
CCca2 na2n ifn cap_cmim w=23.61u l=23.61u A=557.4321p P=94.44u m=1
* --- 负载 RL（rsil 45Ω 档） + 负载臂对地 Ct（cap_cmim 2T，0.84p 档） ---
RRL1 vcc rfop gnd rsil l=6.429u w=1.000u
RRL2 vcc rfon gnd rsil l=6.429u w=1.000u
CCt1 rfop gnd cap_cmim w=23.61u l=23.61u A=557.4321p P=94.44u m=1
CCt2 rfon gnd cap_cmim w=23.61u l=23.61u A=557.4321p P=94.44u m=1
* --- 敏感管 XQs（nx=1，C==B 二极管接法） ---
QXQs nsens nsens gnd gnd npn13G2 le=900.0n we=70.00n Nx=1 m=1
.ends TX5G_M2_MIX_V35
* 器件统计: Q=15 R=16 C=6（与 v1d 逐行同拓扑；v1f 四件事：端口 29 + 衬底 gnd + 电容 2T + D1-C 升级）
