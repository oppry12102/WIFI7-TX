* ============================================================================
* v093a（组长代跑补丁 deck, 基于 b7e7 v0.93）: DRV2 CB 集电极 vcc->outp/outn (v092d 修复在 v0.93 丢失)
*   口径: IF -5dBm 差分 = 15.8m*10^(15/20) (链出绝对电平定衰减档); CB 补丁外与 v0.93 原样。
* SOW-2 TX5G · 链级联 top: LO_BUF -> Gilbert MIX -> DRV1 -> DRV2
* b7e7 2026-10-16 v0.93（组长 v091b 口径合并: ① 源 sin offset(4 源); ② lo_buf EF 基极耦合 Cin1/Cin2 1p
*   (同 lobuf_tb v0.93); ③ four->稳态窗拟合口径; ④ drv 结构修复保持 v0.92 = 组长侧 v091b 的完全体）
* v0.92（drv 结构修复同步: DRV2 补共基管 XQ3/XQ4, DRV1 端口直改 cop/con -- 与 drv_tb v0.92 一致）
* v0.91（组长 DC 诊断修正同步版）| 验证: 全链转换增益 / 级间衔接 / 级联 OP1dB 趋势
* 链路口径（v0.93 修订）: mixer CG 实测 -9.1dB（组长 v091b tran; 原预算 +2 建立在无简并理想开关口径），
*   IF -20dBm 单音进 -> RF 预期约 -29dBm; 链预算重排（方案 B）见 design_notes §0.3: 若 IF -5dBm 进、
*   drv 链 +14~16dB -> 链出约 +0.5~+2dBm, 恰配 PA 输入 +1dBm -> 原计划级间衰减 ~10dB 预计删除（等实测定稿）
* 所有子电路与单模块 tb 完全一致 (自包含, 便于代跑)
* ============================================================================
.lib '../models/cornerHBT.lib' hbt_typ

* ---------- 公共: 参数化 HBT 电流镜 ----------
.subckt hbt_mirror nout vcc nx=8 rr=1.62k
XQr nref nref 0 0 npn13G2 nx=1
XQo nout nref 0 0 npn13G2 nx={nx}
Rref vcc nref {rr}
.ends hbt_mirror

* ---------- LO_BUF (同 lobuf_tb.sp v0.91: EF 集电极接轨 + 10p 交流耦合 + 限幅对基极独立偏置) ----------
.subckt lo_buf inp inn outp outn vcc
Rin1 inp 0 50
Rin2 inn 0 50
* v0.93 结构修复(组长 v091b 案, 同 lobuf_tb): EF 基极输入耦合 1p, 信号到得了 EF (偏置不动)
Cin1 inp bin 1p
Cin2 inn bb1 1p
XQ1  vcc  bin  efp  0  npn13G2 nx=2
XQ2  vcc  bb1  efn  0  npn13G2 nx=2
Re1  efp  ntaila 40
Re2  efn  ntaila 40
Rb1 bin nbias1 1k
Rb2 bb1 nbias1 1k
Vb1 nbias1 0 1.05
XBIa ntaila vcc hbt_mirror nx=8 rr=4.32k
Rb3a b3p nbias2 1k
Rb3b b3n nbias2 1k
Vb2 nbias2 0 1.25
Cc1 efp b3p 10p
Cc2 efn b3n 10p
XQ3  outp  b3p  t1  0  npn13G2 nx=4
XQ4  outn  b3n  t2  0  npn13G2 nx=4
Re3  t1  ntailb 12
Re4  t2  ntailb 12
RL1 vcc outp 60
RL2 vcc outn 60
Lt1 vcc outp 1n
Lt2 vcc outn 1n
Ct1 outp 0 0.84p
Ct2 outn 0 0.84p
XBIb ntailb vcc hbt_mirror nx=8 rr=1.30k
.ends lo_buf

* ---------- Gilbert MIX (同 mixer_tb.sp) ----------
.subckt gilbert_mix ifp ifn lop lon rfop rfon vcc
XQ1  nswa  ifp  e1  0  npn13G2 nx=6
XQ2  nswb  ifn  e2  0  npn13G2 nx=6
Re1  e1  ntail 15
Re2  e2  ntail 15
XQ3  rfop  lop  nswa  0  npn13G2 nx=4
XQ4  rfon  lon  nswa  0  npn13G2 nx=4
XQ5  rfon  lop  nswb  0  npn13G2 nx=4
XQ6  rfop  lon  nswb  0  npn13G2 nx=4
RL1  vcc  rfop  45
RL2  vcc  rfon  45
Lt1  vcc  rfop  1n
Lt2  vcc  rfon  1n
Ct1  rfop  0  0.84p
Ct2  rfon  0  0.84p
Rb1  ifp  nifbias  2k
Rb2  ifn  nifbias  2k
Vifb nifbias 0 1.2
XBI1 ntail vcc hbt_mirror
XBI2 ntail vcc hbt_mirror
.ends gilbert_mix

* ---------- DRV1 (同 drv_tb.sp v0.92: 端口直改 cop/con, tank 即端口) ----------
.subckt drv1 inp inn cop con vcc
Rin1 inp 0 50
Rin2 inn 0 50
Cin1 inp bin 1p
Cin2 inn bb1 1p
XQ1  cop  bin  e1  0  npn13G2 nx=6
XQ2  con  bb1  e2  0  npn13G2 nx=6
Re1  e1  ntail 4
Re2  e2  ntail 4
Rb1 bin nbias 1k
Rb2 bb1 nbias 1k
Vb nbias 0 0.95
RL1 vcc cop 25
RL2 vcc con 25
Lt1 vcc cop 1n
Lt2 vcc con 1n
Ct1 cop 0 0.84p
Ct2 con 0 0.84p
XBI ntail vcc hbt_mirror
.ends drv1

* ---------- DRV2 (同 drv_tb.sp) ----------
.subckt drv2 inp inn outp outn vcc
Rin1 inp 0 50
Rin2 inn 0 50
Cin1 inp bin 1p
Cin2 inn bb1 1p
XQ1  ccas1  bin  e1  0  npn13G2 nx=10
XQ2  ccas2  bb1  e2  0  npn13G2 nx=10
XQ3  outp  nbcas  ccas1  0  npn13G2 nx=10      $ v0.92 补漏共基 CB 管 (同 drv_tb v0.92)
XQ4  outn  nbcas  ccas2  0  npn13G2 nx=10
Re1  e1  ntail 1.5
Re2  e2  ntail 1.5
Rb1 bin nbias 500
Rb2 bb1 nbias 500
Vb nbias 0 0.95
Vbcas nbcas 0 2.05
Cbc1 ccas1 nbcas 10p
Cbc2 ccas2 nbcas 10p
RL1 vcc outp 25
RL2 vcc outn 25
Lt1 vcc outp 0.7n
Lt2 vcc outn 0.7n
Ct1 outp 0 1.2p
Ct2 outn 0 1.2p
XBI1 ntail vcc hbt_mirror
XBI2 ntail vcc hbt_mirror
XBI3 ntail vcc hbt_mirror
XBI4 ntail vcc hbt_mirror      $ 4 组 = 32mA (目标 30, +2mA 标定余量)
.ends drv2

* ============================================================================
* top 级联
* ============================================================================
Vcc nvcc 0 2.5

* IF 差分源 (单音 10MHz, -20dBm 差分; 共模 1.2V=Vifb, v0.91)
* v0.93: sin offset 接管 tran 激励 (共模入 sin 首参, dc 仅 op 用)
.param ifamp = 88.9m
Vifp nifp_t 0 dc 1.2 sin(1.2 {ifamp} 10meg)
Vifn nifn_t 0 dc 1.2 sin(1.2 {-ifamp} 10meg)

* LO 源 (VCO 口径: 0.3Vpp 差分 -> LO_BUF 限幅; 共模 1.05V=EF 基极偏置, v0.91)
.param loin = 106m
Vlop nlop_t 0 dc 1.05 sin(1.05 {loin} 5.5g)
Vlon nlon_t 0 dc 1.05 sin(1.05 {-loin} 5.5g)

* 级 1: LO_BUF (输出经 1p 隔直耦合 mix lop/lon, 共模拉 2.35V=v0.91 开关对基极闭合点)
XLB nlop_t nlon_t nblop nblon nvcc lo_buf
Rcm1 nblop nbcm 1k
Rcm2 nblon nbcm 1k
Vbcm nbcm 0 2.35
Cc1 nblop nlop 1p
Cc2 nblon nlon 1p
Rloin1 nlop nbcm 2k
Rloin2 nlon nbcm 2k

* 级 2: MIX
XMI nifp_t nifn_t nlop nlon nmixp nmixn nvcc gilbert_mix

* 级间: mix RF 输出 (对地 25Ω 虚拟负载口径改直驱) -> 隔直 -> drv1
Rtap1 nmixp ntap1 0.01
Rtap2 nmixn ntap2 0.01
Rdc1 ntap1 0 1meg     $ 高阻探针路径 (不加载), 实际耦合由 Cin1 完成
Rdc2 ntap2 0 1meg
XD1 nmixp nmixn nd1p nd1n nvcc drv1

* 级 3: DRV2 (drv1 输出 tank 内阻 25Ω/边 已是 50Ω 口, 直接接)
XD2 nd1p nd1n noutp noutn nvcc drv2
Rload1 noutp 0 25
Rload2 noutn 0 25

* ---------- 仿真 ----------
.temp 27
.op
.control
tran 1p 200n 60n
let vr = v(noutp) - v(noutn)
* v0.93: ngspice-47 无 four -> 代跑侧稳态窗(60~200n)拟合; three four 行保留注释
* four 5.51g vr
* 全链 CG = 20log10( A5.51差分 / (2*ifamp) )
* 级间探针 (同法 four): nmixp-nmixn (mix CG), nd1p-nd1n (drv1 输出)
let vmix = v(nmixp) - v(nmixn)
* four 5.51g vmix
let vd1 = v(nd1p) - v(nd1n)
wrdata sow2/results_v093/v093a_chain_m5.csv v(noutp) v(noutn) v(nmixp) v(nmixn) v(nd1p) v(nd1n) v(nlop) v(nlon) v(nblop) v(nblon)
* four 5.51g vd1
* 稳定性初查: 8-12G 级间波形无振荡 (目测 tran 尾段规则性; k 因子第二轮)
.endc

* 测量口径汇总 (代跑回填):
*   [ ] 全链 CG @-20dBm IF: v0.93 预期 = -9.1(mix 实测) + drv1 + drv2（drv 链待实测; 旧预算 +15~19dB 作废）
*   [ ] 级间摆幅衔接: mix 输出 tank 摆幅 vs drv1 输入压摆需求 (无削顶)
*   [ ] LO 链: mix lop/lon 实际摆幅 >= 0.3Vpp 差分 (限幅输出经 1pF 耦合后)
*   [ ] 各级 Vce_max 击穿复核
*   [ ] 尾段波形规则 (无寄生振荡)
* 满功率推算 (v0.93 方案 B 口径, 组长 v091b 实测 mix CG=-9.1dB 回填):
*   IF -5dBm 进 -> mix 出 -14.1dBm -> drv1+drv2 (+14~16dB 待实测) -> 链出 ~+0.5~+2dBm,
*   恰配 PA 输入 +1dBm -> 原 ~10dB 级间衰减预计删除（若 drv 实测增益高于预算, 按
*   链出 +1dBm 反推衰减档, 数据说话）; 链 IM3 预估 ~-33dBc vs WLAN -45dBc 缺口见 §0.3 决策
.end
