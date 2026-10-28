# M5 口径甲代入审计（b7a0 四裁·裁定一/二）

生成：m5_pex_substitute_jia.py（fde9）

### 阶段 drv2

**deck 侧保留（15 行）**：Cin1、Cin2、Ct1、Ct2、Lt1、Lt2、RL1、RL2、Vb、Vbcas

**deck 侧剔除（14 行，L0 实物件→由 cdl 接管）**：

| deck 行 | 处理 |
|---|---|
| `Rin1 inp 0 1k      $ v015[2]` | 剔除（L0 实物件，cdl 接管） |
| `Rin2 inn 0 1k      $ v015[2]` | 剔除（L0 实物件，cdl 接管） |
| `XQ1  ccas1  bin  e1  0  npn13G2 nx=10` | 剔除（L0 实物件，cdl 接管） |
| `XQ2  ccas2  bb1  e2  0  npn13G2 nx=10` | 剔除（L0 实物件，cdl 接管） |
| `XQ3  outp nbcas  ccas1  0  npn13G2 nx=10` | 剔除（L0 实物件，cdl 接管） |
| `XQ4  outn nbcas  ccas2  0  npn13G2 nx=10` | 剔除（L0 实物件，cdl 接管） |
| `Re1  e1  ntail 1.5` | 剔除（L0 实物件，cdl 接管） |
| `Re2  e2  ntail 1.5` | 剔除（L0 实物件，cdl 接管） |
| `Rb1 bin nbias 500` | 剔除（L0 实物件，cdl 接管） |
| `Rb2 bb1 nbias 500` | 剔除（L0 实物件，cdl 接管） |
| `XBI1 ntail vcc hbt_mirror` | 剔除（L0 实物件，cdl 接管） |
| `XBI2 ntail vcc hbt_mirror` | 剔除（L0 实物件，cdl 接管） |
| `XBI3 ntail vcc hbt_mirror` | 剔除（L0 实物件，cdl 接管） |
| `XBI4 ntail vcc hbt_mirror   $ 4 组 = 32mA (目标 30, +2mA 标定余量)` | 剔除（L0 实物件，cdl 接管） |

**cdl 侧剔除（重复计入防护）**：

| cdl 行 | 原因 |
|---|---|
| `R11 vcc outp rppd l=1.0u w=2.6u sub=0` | deck RL1 100Ω tank 负载的实物孪生（vcc-outp RPPD×1.0/2.6=100Ω）→ 裁定一保留 deck 侧 |
| `R12 vcc outn rppd l=1.0u w=2.6u sub=0` | deck RL2 100Ω tank 负载的实物孪生（vcc-outn 100Ω）→ 裁定一保留 deck 侧 |

**cdl 侧逐件映射（原行 → X 行，裁定二护栏 1）**：

| 原 cdl 行 | 代入后 X 行 | 派生标称值 |
|---|---|---|
| `Q1 ccas1 ccas1 ccas1 npn13G2 we=70n le=900n NX=10 M=1 sub=0` | `XQ1 ccas1 ccas1 ccas1 0 npn13G2 we=70n le=900n Nx=10` | HBT npn13G2 Nx=10（we/le 原样透传） |
| `Q2 ccas1 ccas1 ccas1 npn13G2 we=70n le=900n NX=10 M=1 sub=0` | `XQ2 ccas1 ccas1 ccas1 0 npn13G2 we=70n le=900n Nx=10` | HBT npn13G2 Nx=10（we/le 原样透传） |
| `Q3 outp ccas1 ccas1 npn13G2 we=70n le=900n NX=10 M=1 sub=0` | `XQ3 outp ccas1 ccas1 0 npn13G2 we=70n le=900n Nx=10` | HBT npn13G2 Nx=10（we/le 原样透传） |
| `Q4 outn ccas1 ccas1 npn13G2 we=70n le=900n NX=10 M=1 sub=0` | `XQ4 outn ccas1 ccas1 0 npn13G2 we=70n le=900n Nx=10` | HBT npn13G2 Nx=10（we/le 原样透传） |
| `R1 ccas1 ccas1 rsil l=1.0u w=4.665u sub=0` | `XR1 ccas1 ccas1 rsil l=1.0u w=4.665u` | R=7.0×1e-06/4.665e-06=1.50054 Ω |
| `R2 ccas1 ccas1 rsil l=1.0u w=4.665u sub=0` | `XR2 ccas1 ccas1 rsil l=1.0u w=4.665u` | R=7.0×1e-06/4.665e-06=1.50054 Ω |
| `Q5 ntail nref nref npn13G2 we=70n le=900n NX=8 M=1 sub=0` | `XQ5 ntail nref nref 0 npn13G2 we=70n le=900n Nx=8` | HBT npn13G2 Nx=8（we/le 原样透传） |
| `Q6 nref nref nref npn13G2 we=70n le=900n NX=1 M=1 sub=0` | `XQ6 nref nref nref 0 npn13G2 we=70n le=900n Nx=1` | HBT npn13G2 Nx=1（we/le 原样透传） |
| `R3 vcc nref rhigh l=1.19u w=1.0u sub=0` | `XR3 vcc nref rhigh l=1.19u w=1.0u` | R=1360.0×1.19e-06/1e-06=1618.4 Ω |
| `Q7 ntail nref nref npn13G2 we=70n le=900n NX=8 M=1 sub=0` | `XQ7 ntail nref nref 0 npn13G2 we=70n le=900n Nx=8` | HBT npn13G2 Nx=8（we/le 原样透传） |
| `Q8 nref nref nref npn13G2 we=70n le=900n NX=1 M=1 sub=0` | `XQ8 nref nref nref 0 npn13G2 we=70n le=900n Nx=1` | HBT npn13G2 Nx=1（we/le 原样透传） |
| `R4 vcc nref rhigh l=1.19u w=1.0u sub=0` | `XR4 vcc nref rhigh l=1.19u w=1.0u` | R=1360.0×1.19e-06/1e-06=1618.4 Ω |
| `Q9 ntail nref nref npn13G2 we=70n le=900n NX=8 M=1 sub=0` | `XQ9 ntail nref nref 0 npn13G2 we=70n le=900n Nx=8` | HBT npn13G2 Nx=8（we/le 原样透传） |
| `Q10 nref nref nref npn13G2 we=70n le=900n NX=1 M=1 sub=0` | `XQ10 nref nref nref 0 npn13G2 we=70n le=900n Nx=1` | HBT npn13G2 Nx=1（we/le 原样透传） |
| `R5 vcc nref rhigh l=1.19u w=1.0u sub=0` | `XR5 vcc nref rhigh l=1.19u w=1.0u` | R=1360.0×1.19e-06/1e-06=1618.4 Ω |
| `Q11 ntail nref nref npn13G2 we=70n le=900n NX=8 M=1 sub=0` | `XQ11 ntail nref nref 0 npn13G2 we=70n le=900n Nx=8` | HBT npn13G2 Nx=8（we/le 原样透传） |
| `Q12 nref nref nref npn13G2 we=70n le=900n NX=1 M=1 sub=0` | `XQ12 nref nref nref 0 npn13G2 we=70n le=900n Nx=1` | HBT npn13G2 Nx=1（we/le 原样透传） |
| `R6 vcc nref rhigh l=1.19u w=1.0u sub=0` | `XR6 vcc nref rhigh l=1.19u w=1.0u` | R=1360.0×1.19e-06/1e-06=1618.4 Ω |
| `R7 inp nref rhigh l=1.0u w=1.36u sub=0` | `XR7 inp nref rhigh l=1.0u w=1.36u` | R=1360.0×1e-06/1.36e-06=1000 Ω |
| `R8 inn nref rhigh l=1.0u w=1.36u sub=0` | `XR8 inn nref rhigh l=1.0u w=1.36u` | R=1360.0×1e-06/1.36e-06=1000 Ω |
| `R9 bin nbias rppd l=1.923u w=1.0u sub=0` | `XR9 bin nbias rppd l=1.923u w=1.0u` | R=260.0×1.923e-06/1e-06=499.98 Ω |
| `R10 bb1 nbias rppd l=1.923u w=1.0u sub=0` | `XR10 bb1 nbias rppd l=1.923u w=1.0u` | R=260.0×1.923e-06/1e-06=499.98 Ω |

### 阶段 drv1

**deck 侧保留（10 行）**：Cin1、Cin2、Ct1、Ct2、Lt1、Lt2、RL1、RL2、Vb

**deck 侧剔除（9 行，L0 实物件→由 cdl 接管）**：

| deck 行 | 处理 |
|---|---|
| `Rin1 inp 0 1k      $ v015[2]: 50->1k (M1 实测锚; 隐藏 DC 负载 50mA->2.5mA)` | 剔除（L0 实物件，cdl 接管） |
| `Rin2 inn 0 1k      $ v015[2]` | 剔除（L0 实物件，cdl 接管） |
| `XQ1  cop  bin  e1  0  npn13G2 nx=6` | 剔除（L0 实物件，cdl 接管） |
| `XQ2  con  bb1  e2  0  npn13G2 nx=6` | 剔除（L0 实物件，cdl 接管） |
| `Re1  e1  ntail 4` | 剔除（L0 实物件，cdl 接管） |
| `Re2  e2  ntail 4` | 剔除（L0 实物件，cdl 接管） |
| `Rb1 bin nbias 1k` | 剔除（L0 实物件，cdl 接管） |
| `Rb2 bb1 nbias 1k` | 剔除（L0 实物件，cdl 接管） |
| `XBI ntail vcc hbt_mirror` | 剔除（L0 实物件，cdl 接管） |

**cdl 侧剔除（重复计入防护）**：

| cdl 行 | 原因 |
|---|---|
| `R8 vcc cop rppd l=1.0u w=2.6u sub=0` | deck RL1 100Ω tank 负载的实物孪生（vcc-cop RPPD×1.0/2.6=100Ω）→ 裁定一保留 deck 侧 |
| `R9 vcc con rppd l=1.0u w=2.6u sub=0` | deck RL2 100Ω tank 负载的实物孪生（vcc-con 100Ω）→ 裁定一保留 deck 侧 |

**cdl 侧逐件映射（原行 → X 行，裁定二护栏 1）**：

| 原 cdl 行 | 代入后 X 行 | 派生标称值 |
|---|---|---|
| `Q1 cop e1 e1 npn13G2 we=70n le=900n NX=6 M=1 sub=0` | `XQ1 cop e1 e1 0 npn13G2 we=70n le=900n Nx=6` | HBT npn13G2 Nx=6（we/le 原样透传） |
| `Q2 con e2 e2 npn13G2 we=70n le=900n NX=6 M=1 sub=0` | `XQ2 con e2 e2 0 npn13G2 we=70n le=900n Nx=6` | HBT npn13G2 Nx=6（we/le 原样透传） |
| `R1 e1 e1 rsil l=1.0u w=1.75u sub=0` | `XR1 e1 e1 rsil l=1.0u w=1.75u` | R=7.0×1e-06/1.75e-06=4 Ω |
| `R2 e2 e2 rsil l=1.0u w=1.75u sub=0` | `XR2 e2 e2 rsil l=1.0u w=1.75u` | R=7.0×1e-06/1.75e-06=4 Ω |
| `Q3 ntail nref nref npn13G2 we=70n le=900n NX=8 M=1 sub=0` | `XQ3 ntail nref nref 0 npn13G2 we=70n le=900n Nx=8` | HBT npn13G2 Nx=8（we/le 原样透传） |
| `Q4 nref nref nref npn13G2 we=70n le=900n NX=1 M=1 sub=0` | `XQ4 nref nref nref 0 npn13G2 we=70n le=900n Nx=1` | HBT npn13G2 Nx=1（we/le 原样透传） |
| `R3 vcc nref rhigh l=1.19u w=1.0u sub=0` | `XR3 vcc nref rhigh l=1.19u w=1.0u` | R=1360.0×1.19e-06/1e-06=1618.4 Ω |
| `R4 inp nref rhigh l=1.0u w=1.36u sub=0` | `XR4 inp nref rhigh l=1.0u w=1.36u` | R=1360.0×1e-06/1.36e-06=1000 Ω |
| `R5 inn nref rhigh l=1.0u w=1.36u sub=0` | `XR5 inn nref rhigh l=1.0u w=1.36u` | R=1360.0×1e-06/1.36e-06=1000 Ω |
| `R6 bin nbias rhigh l=1.0u w=1.36u sub=0` | `XR6 bin nbias rhigh l=1.0u w=1.36u` | R=1360.0×1e-06/1.36e-06=1000 Ω |
| `R7 bb1 nbias rhigh l=1.0u w=1.36u sub=0` | `XR7 bb1 nbias rhigh l=1.0u w=1.36u` | R=1360.0×1e-06/1.36e-06=1000 Ω |

### 阶段 gilbert_mix

**deck 侧保留（21 行）**：Bvbh、Bvbl、Bvifb、Bvt、Cca1、Cca2、Ccb1、Ccb2、Ct1、Ct2、Is0、Lt1、Lt2、RL1、RL2

**deck 侧剔除（23 行，L0 实物件→由 cdl 接管）**：

| deck 行 | 处理 |
|---|---|
| `XQ1a  nswa  na1p  e1a  0  npn13G2 nx=3` | 剔除（L0 实物件，cdl 接管） |
| `XQ2a  nswb  na2n  e2a  0  npn13G2 nx=3` | 剔除（L0 实物件，cdl 接管） |
| `Re1a  e1a  ntaila 30   $ v015.1[1]: 15->30 (ACPR 处方推荐档)` | 剔除（L0 实物件，cdl 接管） |
| `Re2a  e2a  ntaila 30   $ v015.1[1]: 15->30 (ACPR 处方推荐档)` | 剔除（L0 实物件，cdl 接管） |
| `XQ1b  nswa  nb1p  e1b  0  npn13G2 nx=3` | 剔除（L0 实物件，cdl 接管） |
| `XQ2b  nswb  nb2n  e2b  0  npn13G2 nx=3` | 剔除（L0 实物件，cdl 接管） |
| `Re1b  e1b  ntailb 30   $ v015.1[1]: 15->30 (ACPR 处方推荐档)` | 剔除（L0 实物件，cdl 接管） |
| `Re2b  e2b  ntailb 30   $ v015.1[1]: 15->30 (ACPR 处方推荐档)` | 剔除（L0 实物件，cdl 接管） |
| `XQs  nsens nsens 0 0 npn13G2 nx=1` | 剔除（L0 实物件，cdl 接管） |
| `Rba1 na1p nbiasL 2k` | 剔除（L0 实物件，cdl 接管） |
| `Rba2 na2n nbiasH 2k` | 剔除（L0 实物件，cdl 接管） |
| `Rbb1 nb1p nbiasH 2k` | 剔除（L0 实物件，cdl 接管） |
| `Rbb2 nb2n nbiasL 2k` | 剔除（L0 实物件，cdl 接管） |
| `Rd1  lop  lopd 10` | 剔除（L0 实物件，cdl 接管） |
| `Rd2  lon  lond 10` | 剔除（L0 实物件，cdl 接管） |
| `XQ3  rfop  lopd nswa  0  npn13G2 nx=6   $ v015.1[2]: 4->6 (ACPR 处方推荐档; Vce_sw 观察条件见头注)` | 剔除（L0 实物件，cdl 接管） |
| `XQ4  rfon  lond nswa  0  npn13G2 nx=6   $ v015.1[2]: 4->6 (ACPR 处方推荐档; Vce_sw 观察条件见头注)` | 剔除（L0 实物件，cdl 接管） |
| `XQ5  rfon  lopd nswb  0  npn13G2 nx=6   $ v015.1[2]: 4->6 (ACPR 处方推荐档; Vce_sw 观察条件见头注)` | 剔除（L0 实物件，cdl 接管） |
| `XQ6  rfop  lond nswb  0  npn13G2 nx=6   $ v015.1[2]: 4->6 (ACPR 处方推荐档; Vce_sw 观察条件见头注)` | 剔除（L0 实物件，cdl 接管） |
| `Rb1  ifp  nifbias  2k` | 剔除（L0 实物件，cdl 接管） |
| `Rb2  ifn  nifbias  2k` | 剔除（L0 实物件，cdl 接管） |
| `XBI1 ntaila nvtop hbt_mirror nx=10 rr=680   $ v013: 672->680 (同 mix 板裁决)` | 剔除（L0 实物件，cdl 接管） |
| `XBI2 ntailb nvtop hbt_mirror nx=10 rr=680   $ v013: 672->680 (同 mix 板裁决)` | 剔除（L0 实物件，cdl 接管） |

**cdl 侧剔除（重复计入防护）**：

| cdl 行 | 原因 |
|---|---|
| `R15 vcc lond rsil l=6.429u w=1.0u sub=0` | deck RL1 45Ω tank 负载的实物孪生（vcc-lond 45Ω=RSIL×6.429/1.0）→ 裁定一保留 deck 侧 |
| `R16 vcc lond rsil l=6.429u w=1.0u sub=0` | deck RL2 45Ω tank 负载的实物孪生（vcc-lond 45Ω）→ 裁定一保留 deck 侧 |

**cdl 侧逐件映射（原行 → X 行，裁定二护栏 1）**：

| 原 cdl 行 | 代入后 X 行 | 派生标称值 |
|---|---|---|
| `Q1 lond e1a e1a npn13G2 we=70n le=900n NX=3 M=1 sub=0` | `XQ1 lond e1a e1a 0 npn13G2 we=70n le=900n Nx=3` | HBT npn13G2 Nx=3（we/le 原样透传） |
| `Q2 lond e1b e1b npn13G2 we=70n le=900n NX=3 M=1 sub=0` | `XQ2 lond e1b e1b 0 npn13G2 we=70n le=900n Nx=3` | HBT npn13G2 Nx=3（we/le 原样透传） |
| `Q3 nswb e2b e2b npn13G2 we=70n le=900n NX=3 M=1 sub=0` | `XQ3 nswb e2b e2b 0 npn13G2 we=70n le=900n Nx=3` | HBT npn13G2 Nx=3（we/le 原样透传） |
| `Q4 nswb e2a e2a npn13G2 we=70n le=900n NX=3 M=1 sub=0` | `XQ4 nswb e2a e2a 0 npn13G2 we=70n le=900n Nx=3` | HBT npn13G2 Nx=3（we/le 原样透传） |
| `Q5 ntaila ntaila ntaila npn13G2 we=70n le=900n NX=3 M=1 sub=0` | `XQ5 ntaila ntaila ntaila 0 npn13G2 we=70n le=900n Nx=3` | HBT npn13G2 Nx=3（we/le 原样透传） |
| `Q6 ntaila ntaila ntaila npn13G2 we=70n le=900n NX=3 M=1 sub=0` | `XQ6 ntaila ntaila ntaila 0 npn13G2 we=70n le=900n Nx=3` | HBT npn13G2 Nx=3（we/le 原样透传） |
| `R1 e1a e1a rsil l=4.286u w=1.0u sub=0` | `XR1 e1a e1a rsil l=4.286u w=1.0u` | R=7.0×4.286e-06/1e-06=30.002 Ω |
| `R2 e2a e2a rsil l=4.286u w=1.0u sub=0` | `XR2 e2a e2a rsil l=4.286u w=1.0u` | R=7.0×4.286e-06/1e-06=30.002 Ω |
| `R3 e1b e1b rsil l=4.286u w=1.0u sub=0` | `XR3 e1b e1b rsil l=4.286u w=1.0u` | R=7.0×4.286e-06/1e-06=30.002 Ω |
| `R4 e2b e2b rsil l=4.286u w=1.0u sub=0` | `XR4 e2b e2b rsil l=4.286u w=1.0u` | R=7.0×4.286e-06/1e-06=30.002 Ω |
| `Q7 ntaila ntaila ntaila npn13G2 we=70n le=900n NX=10 M=1 sub=0` | `XQ7 ntaila ntaila ntaila 0 npn13G2 we=70n le=900n Nx=10` | HBT npn13G2 Nx=10（we/le 原样透传） |
| `Q8 ntaila ntaila ntaila npn13G2 we=70n le=900n NX=1 M=1 sub=0` | `XQ8 ntaila ntaila ntaila 0 npn13G2 we=70n le=900n Nx=1` | HBT npn13G2 Nx=1（we/le 原样透传） |
| `R5 nvtop ntaila rhigh l=1.0u w=2.0u sub=0` | `XR5 nvtop ntaila rhigh l=1.0u w=2.0u` | R=1360.0×1e-06/2e-06=680 Ω |
| `Q9 ntailb ntaila ntaila npn13G2 we=70n le=900n NX=10 M=1 sub=0` | `XQ9 ntailb ntaila ntaila 0 npn13G2 we=70n le=900n Nx=10` | HBT npn13G2 Nx=10（we/le 原样透传） |
| `Q10 ntaila ntaila ntaila npn13G2 we=70n le=900n NX=1 M=1 sub=0` | `XQ10 ntaila ntaila ntaila 0 npn13G2 we=70n le=900n Nx=1` | HBT npn13G2 Nx=1（we/le 原样透传） |
| `R6 nvtop ntaila rhigh l=1.0u w=2.0u sub=0` | `XR6 nvtop ntaila rhigh l=1.0u w=2.0u` | R=1360.0×1e-06/2e-06=680 Ω |
| `Q11 lond lond lond npn13G2 we=70n le=900n NX=6 M=1 sub=0` | `XQ11 lond lond lond 0 npn13G2 we=70n le=900n Nx=6` | HBT npn13G2 Nx=6（we/le 原样透传） |
| `Q12 lond lond lond npn13G2 we=70n le=900n NX=6 M=1 sub=0` | `XQ12 lond lond lond 0 npn13G2 we=70n le=900n Nx=6` | HBT npn13G2 Nx=6（we/le 原样透传） |
| `Q13 lond nswb nswb npn13G2 we=70n le=900n NX=6 M=1 sub=0` | `XQ13 lond nswb nswb 0 npn13G2 we=70n le=900n Nx=6` | HBT npn13G2 Nx=6（we/le 原样透传） |
| `Q14 lond nswb nswb npn13G2 we=70n le=900n NX=6 M=1 sub=0` | `XQ14 lond nswb nswb 0 npn13G2 we=70n le=900n Nx=6` | HBT npn13G2 Nx=6（we/le 原样透传） |
| `R7 lop lond rsil l=1.429u w=1.0u sub=0` | `XR7 lop lond rsil l=1.429u w=1.0u` | R=7.0×1.429e-06/1e-06=10.003 Ω |
| `R8 lon lond rsil l=1.429u w=1.0u sub=0` | `XR8 lon lond rsil l=1.429u w=1.0u` | R=7.0×1.429e-06/1e-06=10.003 Ω |
| `R9 na1p nbiasL rhigh l=1.47u w=1.0u sub=0` | `XR9 na1p nbiasL rhigh l=1.47u w=1.0u` | R=1360.0×1.47e-06/1e-06=1999.2 Ω |
| `R10 nb1p nbiasH rhigh l=1.47u w=1.0u sub=0` | `XR10 nb1p nbiasH rhigh l=1.47u w=1.0u` | R=1360.0×1.47e-06/1e-06=1999.2 Ω |
| `R11 nb2n nbiasL rhigh l=1.47u w=1.0u sub=0` | `XR11 nb2n nbiasL rhigh l=1.47u w=1.0u` | R=1360.0×1.47e-06/1e-06=1999.2 Ω |
| `R12 na2n nbiasH rhigh l=1.47u w=1.0u sub=0` | `XR12 na2n nbiasH rhigh l=1.47u w=1.0u` | R=1360.0×1.47e-06/1e-06=1999.2 Ω |
| `R13 ifp nifbias rhigh l=1.47u w=1.0u sub=0` | `XR13 ifp nifbias rhigh l=1.47u w=1.0u` | R=1360.0×1.47e-06/1e-06=1999.2 Ω |
| `R14 ifn nifbias rhigh l=1.47u w=1.0u sub=0` | `XR14 ifn nifbias rhigh l=1.47u w=1.0u` | R=1360.0×1.47e-06/1e-06=1999.2 Ω |
| `C1 ifp ifp cmim area=514.382 sub=0` | `XC1 ifp ifp cmim area=514.382` | C=area×1.5fF/µm²=771573 fF（面项，裁定四） |
| `C2 ifn ifn cmim area=514.382 sub=0` | `XC2 ifn ifn cmim area=514.382` | C=area×1.5fF/µm²=771573 fF（面项，裁定四） |
| `C3 ifp ifp cmim area=514.382 sub=0` | `XC3 ifp ifp cmim area=514.382` | C=area×1.5fF/µm²=771573 fF（面项，裁定四） |
| `C4 ifn ifn cmim area=514.382 sub=0` | `XC4 ifn ifn cmim area=514.382` | C=area×1.5fF/µm²=771573 fF（面项，裁定四） |
| `C5 ntaila ntaila cmim area=514.382 sub=0` | `XC5 ntaila ntaila cmim area=514.382` | C=area×1.5fF/µm²=771573 fF（面项，裁定四） |
| `C6 ntaila ntaila cmim area=514.382 sub=0` | `XC6 ntaila ntaila cmim area=514.382` | C=area×1.5fF/µm²=771573 fF（面项，裁定四） |
| `Q15 ntaila ntaila ntaila npn13G2 we=70n le=900n NX=1 M=1 sub=0` | `XQ15 ntaila ntaila ntaila 0 npn13G2 we=70n le=900n Nx=1` | HBT npn13G2 Nx=1（we/le 原样透传） |

