* ============================================================================
* SOW-2 TX5G · LO 缓冲（EF 输入级 -> 差分限幅对）tb
* b7e7 2026-10-16 v0.91（组长 DC 诊断 B 项修复: EF 集电极改接 vcc + 射极 10p 交流耦合 +
*   限幅对基极独立偏置 1.25V; 输入源共模 0.9->1.05V; 输出负载共模 0.9->2.35V）
* 目标: 输出差分 0.4Vpp 恒定 (输入 0.1-0.8Vpp 均可)
* 驱动对象: Gilbert 开关对基极 (每边 ~25Ω 等效 + 2.35V 共模偏置口径, 经隔直耦合)
* 口径: 差分 50Ω 口（每边对地 25Ω）; VCC=2.5V
* ============================================================================
.lib '../models/cornerHBT.lib' hbt_typ

* Iout = nx * (Vcc-Vbe)/rr; nx 限 1-10 (PDK 声明), 大电流并联组
.subckt hbt_mirror nout vcc nx=8 rr=1.62k
XQr nref nref 0 0 npn13G2 nx=1
XQo nout nref 0 0 npn13G2 nx={nx}
Rref vcc nref {rr}
.ends hbt_mirror

* ---------- LO_BUF: EF 输入 (nx=2, 3mA) -> 限幅差分对 (nx=4, 10mA) ----------
* 端口: inp inn outp outn vcc
* v0.91 偏置闭合 (Vbe=0.88@nx6/Vce1.2 校准, β550-650):
*   EF: 基极 1.05V -> 射极 efp≈0.18V, ntaila≈+0.12V (镜像合规; v0.9 0.88V 时 ntaila<0)
*   限幅对: 基极 1.25V(独立偏置, 交流耦合输入) -> ntailb≈+0.31V 合规;
*     限幅管 Vce≈2.13V (单管无 cascode, >vce_max 1.6V 声明口径: 基极低阻->BVCBO 4.5V 裕 2.4V, 第二轮处理)
*   输出: tank 经 L 直流挂 2.5V, 输出共模 2.5V; 驱动开关对经隔直+2.35V 共模拉偏置
.subckt lo_buf inp inn outp outn vcc
* EF 输入级: 带宽拓展 (低阻输出), 输入 50Ω 匹配
*   v0.91 修正: EF 集电极改接 vcc (v0.9 误接输出节点 -> Vbc 正偏饱和, B 项根因)
Rin1 inp 0 50
Rin2 inn 0 50
XQ1  vcc  bin  efp  0  npn13G2 nx=2
XQ2  vcc  bb1  efn  0  npn13G2 nx=2
Re1  efp  ntaila 40
Re2  efn  ntaila 40
Rb1 bin nbias1 1k
Rb2 bb1 nbias1 1k
Vb1 nbias1 0 1.05
XBIa ntaila vcc hbt_mirror nx=8 rr=4.32k  $ Iout≈8*(2.5-0.87)/4.32k≈3mA
* 级间耦合: EF 射极 10p 交流耦合 -> 限幅对基极独立偏置 1.25V (v0.91 B 项修复)
*   (v0.9 EF 射极~0.03V 直耦直驱 -> 限幅对常关; 10p@5.5G≈2.9Ω 不衰摆, 1k 偏置低频角 16MHz)
Rb3a b3p nbias2 1k
Rb3b b3n nbias2 1k
Vb2 nbias2 0 1.25
Cc1 efp b3p 10p
Cc2 efn b3n 10p
* 限幅差分对: 尾流 10mA, 集电极 tank @5.5G + R
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
XBIb ntailb vcc hbt_mirror nx=8 rr=1.30k  $ Iout=8*(2.5-0.88)/1.30k=10mA
.ends lo_buf

* ============================================================================
* tb: 扫输入摆幅 -> 输出摆幅平坦度
* ============================================================================
Vinp ntst 0 dc 1.05 sin(0 {lo_in_amp} 5.5g)
Vinn ntsn 0 dc 1.05 sin(0 {-lo_in_amp} 5.5g)
Rsrc1 ntst nbufp 0.01
Rsrc2 ntsn nbuff 0.01

X1 nbufp nbuff noutp noutn nvcc lo_buf

* 输出接"虚拟开关对"负载口径: 每边 25Ω 到 2.35V 共模 (开关对基极输入等效, v0.91)
Rl1 noutp nbcm 25
Rl2 noutn nbcm 25
Vbcm nbcm 0 2.35
Cc1 noutp nlop 1p
Cc2 noutn nlon 1p
Rcm1 nlop nbcm 1k
Rcm2 nlon nbcm 1k

Vcc nvcc 0 2.5
.param lo_in_amp = 50m

.control
foreach a 28m 40m 56m 80m 113m 160m 225m   $ 0.08..0.64Vpp 差分 输入扫
  alterparam lo_in_amp = $a
  reset
  tran 1p 60n 40n
  let vr = v(noutp) - v(noutn)
  four 5.5g vr
end
* 输出: 各输入幅度下 5.5G 基波 Vpk 差分 -> 摆幅平坦度曲线 (目标: 输入>0.2Vpp 后输出恒定 0.4Vpp±10%)
* 二次谐波 (限幅对称性): four 表 2 次项 dBc (目标 <= -30dBc)
.endc

* 测量口径汇总:
*   [ ] 输出差分摆幅 @输入 0.1-0.8Vpp: 恒定 0.4Vpp±10%
*   [ ] 2 次谐波: <= -30dBc (对称性)
*   [ ] 驱动能力: 直接带载 25Ω/边 下摆幅不塌 (开关对全切换需求 0.2Vpp, 裕量 6dB)
.end
