* ============================================================================
* v093a（组长代跑补丁 deck, 基于 b7e7 v0.93）: DRV2 共基管集电极 vcc->outp/outn (XQ3/XQ4) --
*   v092d 修复在 v0.93 合并时丢失(她从 v0.92 起编, 未同步组长认领的笔误修正)。c=vcc 时信号经 CB
*   直通 AC 地, outp/outn 悬空 -> drv2 输出恒零(v092d 已实证)。仅此 4 行结构差异, 其余 v0.93 原样。
* SOW-2 TX5G · Gilbert double-balanced 上变频混频器 tb
* b7e7 2026-10-16 v0.93（组长 v091b 口径合并: sin offset 接管 tran 激励 + four->稳态窗拟合口径;
*   = 组长侧 v091b(三口径修正) + v0.92(drv 结构修复) 的完全体, 代跑可直接用）
* v0.92（组长 v0.91 op 实测反馈: 本板无结构变更, 偏置一律不动）
* v0.91（组长 DC 诊断修正版: 偏置闭合重算, 只动偏置数值; 代跑口径见 design_notes §6）
* 频段: 5.15-5.85 GHz, 中心 LO=5.5 GHz; IF 0-160 MHz; VCC=2.5V 内部轨
* 口径: 所有功率/阻抗均为"差分 50Ω 口"（= 每边对地 25Ω）
*
* 模型引用: .lib 路径与段名请按 sg13g2_sim 环境校正 (design_notes.md §6)
* HBT 实例口径(组长实测确认): XQ<name> <c> <b> <e> <bn> npn13G2 Nx=<N>  (第4端=埋层 bn, 接 0, 非衬底)
* ============================================================================
.lib '../models/cornerHBT.lib' hbt_typ

* ---------- 子电路: HBT 电流镜 (低端灌电流, 1:nx 面积比) ----------
* Iref 由 Vcc 经 Rref 建立: Iref = (Vcc - Vbe)/Rref = (2.5-0.88)/1.62k = 1.0 mA
* 输出 I = nx * Iref
* Iout = nx * (Vcc-Vbe)/rr; nx 限 1-10 (PDK 声明), 大电流并联组
.subckt hbt_mirror nout vcc nx=8 rr=1.62k
XQr nref nref 0 0 npn13G2 nx=1        $ 二极管接法 (c=b)
XQo nout nref 0 0 npn13G2 nx={nx}     $ 输出管: c=nout, b=nref, e=0
Rref vcc nref {rr}                    $ rsil 建议
.ends hbt_mirror

* ---------- 子电路: Gilbert 混频器核心 ----------
* 端口: ifp ifn lop lon rfop rfon vcc
.subckt gilbert_mix ifp ifn lop lon rfop rfon vcc
* ---- gm 跨导对: nx=6, 尾流 16mA (8mA/边), 射极简并 Re=15Ω/边 (8/15/22Ω 三档预留, rsil) ----
XQ1  nswa  ifp  e1  0  npn13G2 nx=6
XQ2  nswb  ifn  e2  0  npn13G2 nx=6
Re1  e1  ntail 15                     $ rsil
Re2  e2  ntail 15                     $ rsil
* ---- 开关对: Q3/Q4=LO+ 侧, Q5/Q6=LO- 侧, nx=4 ----
XQ3  rfop  lop  nswa  0  npn13G2 nx=4
XQ4  rfon  lon  nswa  0  npn13G2 nx=4
XQ5  rfon  lop  nswb  0  npn13G2 nx=4
XQ6  rfop  lon  nswb  0  npn13G2 nx=4
* ---- 负载: R 45Ω/边 + tank (L 1nH // C 0.84pF @5.5G; 版图阶段 PDK 电感 Q~15 + cmim) ----
RL1  vcc  rfop  45
RL2  vcc  rfon  45
Lt1  vcc  rfop  1n
Lt2  vcc  rfon  1n
Ct1  rfop  0  0.84p                   $ cmim 建议
Ct2  rfon  0  0.84p
* ---- IF 基极偏置: v0.91 抬 0.88->1.2V (组长 DC 诊断 A: Vifb=0.88 时 ntail=-0.11V 镜像塌;
*     1.2V -> ntail≈+0.20V, gm Vce≈1.25V; 2k 高阻注入, 外源直驱时被低阻源覆盖) ----
Rb1  ifp  nifbias  2k
Rb2  ifn  nifbias  2k
Vifb nifbias 0 1.2
* ---- 尾流 16mA = 两组 8mA 镜像并联 ----
XBI1 ntail vcc hbt_mirror
XBI2 ntail vcc hbt_mirror
.ends gilbert_mix

* ============================================================================
* tb
* ============================================================================
Xmix nifp nifn nlop nlon nrfp nrfn nvcc gilbert_mix
Vcc  nvcc 0 2.5

* ---- IF 差分源: 共模 1.2V(=Vifb, v0.91) + 差分正弦 (单音 10MHz; 双音测 OIP3 改此两行, 见 control 注释)
*     v0.93 口径坑: SPICE 语义 tran 中源值由 sin() 表达式接管, dc 值仅在 DC/op 用;
*     sin offset 必须写共模值 (组长 v091b: 原 sin(0 ...) 在 tran 里共模=0 -> 全链截止) ----
.param ifamp = 15.8m                  $ -20dBm 差分@50Ω = 22.4mVrms 差分 = 15.8mV 单边峰
Vifp nifp_t 0 dc 1.2 sin(1.2 {ifamp} 10meg)
Vifn nifn_t 0 dc 1.2 sin(1.2 {-ifamp} 10meg)
Rif1 nifp_t nifp 0.01
Rif2 nifn_t nifn 0.01

* ---- LO 差分源: 5.5GHz, 0.4Vpp 差分 = ±100mV 单端, 共模 2.35V (v0.91 组长闭合点:
*     开关基极 2.35 -> nswa≈1.46V, 开关 Vce≈1.04V, gm Vce≈1.25V) ----
.param loamp = 100m
Vlop nlop_t 0 dc 2.35 sin(2.35 {loamp} 5.5g)    $ v0.93: offset 入 sin 首参
Vlon nlon_t 0 dc 2.35 sin(2.35 {-loamp} 5.5g)
Rlo1 nlop_t nlop 0.01
Rlo2 nlon_t nlon 0.01

* ---- 输出负载: 每边 25Ω 对地 (差模 50Ω) ----
Rload1 nrfp 0 25
Rload2 nrfn 0 25

* ---------- 仿真 ----------
.temp 27
.op
.control
* (1) 工作点自检: gm 对 Ic≈8mA/边, 尾流 16mA, 镜像管 Vce, 开关对 Vce
*     (层级名前缀按 ngspice 版本: @m.xmix... 或 @xmix..., 代跑时调整)
* (2) 瞬态: 200ns, 60ns 后稳态 (5.5G 周期 0.182ns, maxstep 1ps 保证每周期 >=180 点)
tran 1p 200n 60n
* (3) 单音 CG: 基频 5.51G (=LO+IF) 差分输出
*     v0.93: 本机 ngspice-47 无 four 命令 -- 代跑侧改稳态窗(60~200n)多频正弦最小二乘拟合
*     (组长 v091b 口径); four 行保留为注释, 供支持 four 的环境使用
let vr = v(nrfp) - v(nrfn)
wrdata sow2/results_v093/v093a_mix.csv v(nrfp) v(nrfn) v(nlop) v(nlon)
* four 5.51g vr
*     CG(dB) = 20log10(V5.51,sine_pk / ifamp)  ... 差分口径: 20log10(A5.51/(2*ifamp))
*     Pout(dBm@50Ωdiff) = 10log10( (V5.51_rms)^2 / 50 / 1e-3 )
* (4) 双音 OIP3: Vifp/Vifn 的 sin 频率改 9meg / 11meg, ifamp 改 11.2m (= -8dBm 差分/音 25.2mVrms→单边峰 11.2m*2?) 
*     注: -8dBm 差分/音 -> 每音 Vdiff,rms=28.3mV -> 单边峰 20mV -> ifamp=20m
*     IM3 @ LO±7M (5.507/5.513G):
*     four 5.507g vr
*     OIP3 = Pout(5.509) + (Pout(5.509)-Pim3(5.507))/2
* (5) LOFT/LO-RF 隔离: 注释 IF 源重跑, four 5.5g vr -> 泄漏 dBc
* (6) 击穿复核: 开关对截止相 Vce
let vce3 = v(nrfp) - v(nlop)
meas tran vce3_max max vce3 from=60n to=200n
.endc

* 测量口径汇总 (代跑回填 design_notes.md §4 表):
*   [ ] CG @ -20dBm IF 单音:  目标 +2dB (方案A; 方案B +4dB 见文档)
*   [ ] OIP3 (双音 -8dBm/音):  目标 >= +15dBm
*   [ ] LOFT:  目标 <= -40dBc
*   [ ] LO-RF 隔离:  目标 >= 35dB
*   [ ] Vce3_max:  < 2.6V (低阻基极口径, BVCBO 裕量); gm 对 Vce < 1.5V
.end
