* ============================================================================
* SOW-2 TX5G · PA 驱动级（2 级: CE+简并 -> CASCODE）tb
* b7e7 2026-10-16 v0.92（组长 v0.91 op 实测反馈·结构修复: DRV2 补共基管 XQ3/XQ4, DRV1 端口直改 cop/con;
*   偏置一律不动, 尾流 quasi-sat 税 -6%~-30% 第二轮随全链数据统一标定）
* v0.91（组长 DC 诊断修正: Vbcas 1.7->2.05V; CE 基极偏置 0.88->0.95V 修尾流镜像余量; 只动偏置数值）
* 目标: DRV2 输出 OP1dB >= +10dBm @50Ω差分, 5.5G
* 口径: 差分 50Ω 口（每边对地 25Ω）; VCC=2.5V
* 无源理想元件, 版图阶段: 电感->PDK 电感, 电阻->rsil/rppd, 电容->cmim
* ============================================================================
.lib '../models/cornerHBT.lib' hbt_typ

* ---------- 子电路: HBT 电流镜（低端灌电流, 同 mixer_tb） ----------
* Iout = nx * (Vcc-Vbe)/rr; nx 限 1-10 (PDK 声明), 大电流并联组
.subckt hbt_mirror nout vcc nx=8 rr=1.62k
XQr nref nref 0 0 npn13G2 nx=1
XQo nout nref 0 0 npn13G2 nx={nx}
Rref vcc nref {rr}
.ends hbt_mirror

* ---------- DRV1: CE + 射极简并, 8mA, tank 负载 ----------
* 端口: inp inn cop con vcc   (输入输出均差分, 50Ω 口)
*   v0.92 结构修复(组长案 a): 原 outp/outn 端口内部零引用(tank 挂 cop/con) -> 级联断;
*   端口直改 cop/con, tank 即端口; tb 侧调用按位置映射, 不变
.subckt drv1 inp inn cop con vcc
* 输入并联匹配粗糙版: 每边 50Ω 对地 (增益让 3dB, 第二轮换 L 型匹配)
Rin1 inp 0 50
Rin2 inn 0 50
Cin1 inp bin 1p                          $ cmim, 隔直
Cin2 inn bb1 1p
XQ1  cop  bin  e1  0  npn13G2 nx=6
XQ2  con  bb1  e2  0  npn13G2 nx=6
Re1  e1  ntail 4                         $ rsil
Re2  e2  ntail 4
* 基极偏置: v0.91 抬 0.88->0.95V (尾流镜像余量: 8mA 尾/Re4Ω 下 0.88V 时 ntail≈0 贴地;
*   0.95V -> ntail≈+0.07V 合规。CE 单管 Vce≈2.4V>1.6V 声明口径, 组长已批带声明跑, 第二轮 cascode)
Rb1 bin nbias 1k
Rb2 bb1 nbias 1k
Vb nbias 0 0.95
* 负载 tank: L 1nH // C 0.84pF, 并 R 25Ω/边 (差模 50Ω 工作阻抗)
RL1 vcc cop 25
RL2 vcc con 25
Lt1 vcc cop 1n
Lt2 vcc con 1n
Ct1 cop 0 0.84p
Ct2 con 0 0.84p
XBI ntail vcc hbt_mirror                 $ 8mA
.ends drv1

* ---------- DRV2: CASCODE 输出级, 30mA, tank 负载 ----------
* 端口: inp inn outp outn vcc
.subckt drv2 inp inn outp outn vcc
Rin1 inp 0 50
Rin2 inn 0 50
Cin1 inp bin 1p
Cin2 inn bb1 1p
* 主管 CE (nx=10) + 共基 CB (nx=10), 射极简并 1.5Ω/边
XQ1  ccas1  bin  e1  0  npn13G2 nx=10
XQ2  ccas2  bb1  e2  0  npn13G2 nx=10
* v0.92 结构修复(组长四行案): v0.91 绘制遗漏共基管 -> ccas 直流悬空(实测 0.015V), 主管 vbc=+0.884 深饱和;
*   补 XQ3/XQ4 后 ccas≈2.05-Vbe≈1.16V, 主管 Vbc≈-0.2V 反偏, CB Vcb≈-0.45V/Vce≈1.34V, 与闭合表一致
XQ3  vcc  nbcas  ccas1  0  npn13G2 nx=10
XQ4  vcc  nbcas  ccas2  0  npn13G2 nx=10
Re1  e1  ntail 1.5
Re2  e2  ntail 1.5
* cascode 管基极偏置: v0.91 抬 1.7->2.05V (组长 DC 诊断 C: 原 ccas≈0.85V<CE 基极 -> CE 饱和;
*   2.05V -> ccas≈1.16V, CE Vbc 反偏≈-0.2V, CB Vcb≈0.45V, CB Vce≈1.34V ✓)
Rb1 bin nbias 500
Rb2 bb1 nbias 500
* CE 主管基极偏置: v0.91 抬 0.88->0.95V (尾流镜像余量, 32mA/Re1.5Ω 下 0.88V 时 ntail≈-0.03V 贴地)
Vb nbias 0 0.95
Vbcas nbcas 0 2.05
Cbc1 ccas1 nbcas 10p                     $ cascode 基极高频旁路 (cmim)
Cbc2 ccas2 nbcas 10p
* 输出 tank: L 0.7nH // C 1.2pF @5.5G + R 25Ω/边
RL1 vcc outp 25
RL2 vcc outn 25
Lt1 vcc outp 0.7n
Lt2 vcc outn 0.7n
Ct1 outp 0 1.2p
Ct2 outn 0 1.2p
XBI  ntail vcc hbt_mirror
XBI2 ntail vcc hbt_mirror
XBI3 ntail vcc hbt_mirror
XBI4 ntail vcc hbt_mirror                $ 4 组 nx=8 并联 = 32mA 名义 (目标 30, +2mA 标定余量)
* 尾流口径 v0.92 备案: CE 基极 0.95V 下 ntail≈+0.05V 贴地, 镜像输出管 Vce 极低 quasi-sat 税
*   -> 实测或仅 20-25mA (组长预测), 第二轮随全链统一标定 (同 mixer -12% 口径)
.ends drv2

* ============================================================================
* tb: ac 扫增益 + foreach 幅度扫描测 OP1dB
* ============================================================================
* 激励: 差分理想源 (共模 0.95V=v0.91 基极偏置口径; 经 Cin 隔直, 仅名义值), 经 0.01Ω 接 drv 链
Vinp ntst 0 dc 0.95 ac 0.5 sin(0 {drv_amp} 5.5g)
Vinn ntsn 0 dc 0.95 ac -0.5 sin(0 {-drv_amp} 5.5g)

X1 ntst ntsn na nan nvcc drv1
Ccou1 na nbin2 1p
Ccou2 nan nbin3 1p
Rinb1 nbin2 0 50
Rinb2 nbin3 0 50
X2 nbin2 nbin3 noutp noutn nvcc drv2
Rload1 noutp 0 25
Rload2 noutn 0 25

Vcc nvcc 0 2.5

.param drv_amp = 20m

.control
* (1) AC: 增益/带宽/稳定性 (drv1, drv2, 以及级联)
ac dec 200 0.1g 20g
let g_tot = db(v(noutp)-v(noutn))
let g_in  = db(v(ntst)-v(ntsn))
let s21_est = g_tot - g_in
plot s21_est
* (2) OP1dB 扫描 @5.5G: foreach 输入幅度, tran+four 提基波功率
*     幅度列表覆盖 -30..+8 dBm 差分 (15.6uV..0.56V 单边峰):
foreach a 15.6u 31m 44m 62m 88m 125m 176m 250m 350m 500m
  alterparam drv_amp = $a
  reset
  tran 1p 60n 40n
  let vr = v(noutp) - v(noutn)
  four 5.5g vr
end
*     输出: 各幅度下 5.5G 基波 Vpk -> Pout(dBm)=10log10((Vpk/sqrt(2))^2/50/1m)
*     OP1dB = Pout 满足 Pout = Pout_linear - 1 的输入点 (线性外推由小幅度两点定)
* (3) 击穿复核:
let vce_q1 = v(noutp) - v(nbin2)
meas tran vce_max max vce_q1 from=40n to=60n
.endc

* 测量口径汇总 (代跑回填):
*   [ ] DRV1 增益 @5.5G: 目标 +8dB (含输入并联 50Ω 的 -3dB)
*   [ ] DRV2 增益 @5.5G: 目标 +6~8dB
*   [ ] 级联总增益 (drv1->drv2, 级间直接 50Ω 粗匹配): 目标 +12~16dB
*   [ ] 链 OP1dB @50Ω 差分输出: 目标 >= +10dBm
*   [ ] Vce_max (v0.92 cascode 口径): 主管 Vce≈ccas-e≈1.1V (摆幅被 CB 屏蔽, 不落在主管);
*       CB 管 Vce≈1.34V+输出摆幅/2, 基极 Vbcas 理想源低阻 -> BVCBO 4.5V 口径, BVCEO 1.6V 双保险
*   [ ] 稳定性: ac 曲线 8-12G 无峰值异常 (k 因子第二轮)
* 注: XBI2/XBI3/XBI4 四组并联 = 32mA (目标 30, +2mA 标定余量, 第二版改 nx 阵列精确配流)
.end
