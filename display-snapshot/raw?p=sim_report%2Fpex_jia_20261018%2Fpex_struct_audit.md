# M5 口径甲代入前静态结构审计（deck vs cdl）

生成：m5_pex_struct_audit.py（fde9）｜输入：v015.1 前仿 deck + b7e7 cdl 三件（sha 见回执）

> 口径：b7a0《M5 PEX 口径裁定（组长四裁）》2026-10-18 裁定一（口径甲：cdl 只替换 L0 实物器件行，deck 理想件逐字保留）。本审计在**进网表前**逐件比对 cdl 与 deck 的拓扑差，用于会诊定位「这批 cdl 能否直接进双门」。

## 阶段 gilbert_mix（cdl：pex_mix_v27.cdl）

**cdl 自带 WARNING（提取侧声明的合并域）**：
- `* WARNING merged-domain: names=['gnd', 'nsens', 'ntaila'] chosen=ntaila pending-deck-fix-re-extract`
- `* WARNING merged-domain: names=['lond', 'lopd', 'nswa', 'rfon', 'rfop'] chosen=lond pending-deck-fix-re-extract`

| 检查项 | 计数 | 明细 |
|---|---|---|
| Q 件 b==e（基极/发射极同名=粘连） | 15/15 | Q1(lond)、Q2(lond)、Q3(nswb)、Q4(nswb)、Q5(ntaila)、Q6(ntaila)、Q7(ntaila)、Q8(ntaila)、Q9(ntailb)、Q10(ntaila)、Q11(lond)、Q12(lond)、Q13(lond)、Q14(lond)、Q15(ntaila) |
| R 件两节点同名（自环=远端被并入） | 4 | R1(e1a)、R2(e2a)、R3(e1b)、R4(e2b) |
| cdl 网名（deck 中无对应） | 0 | — |
| deck 网名（cdl 中消失=被并没） | 8 | hbt_mirror、lopd、nsens、nswa、nswb、ntailb、rfon、rfop |

**cdl 器件清单（原始行）**：

- `Q1 lond e1a e1a npn13G2 we=70n le=900n NX=3 M=1 sub=0`
- `Q2 lond e1b e1b npn13G2 we=70n le=900n NX=3 M=1 sub=0`
- `Q3 nswb e2b e2b npn13G2 we=70n le=900n NX=3 M=1 sub=0`
- `Q4 nswb e2a e2a npn13G2 we=70n le=900n NX=3 M=1 sub=0`
- `Q5 ntaila ntaila ntaila npn13G2 we=70n le=900n NX=3 M=1 sub=0`
- `Q6 ntaila ntaila ntaila npn13G2 we=70n le=900n NX=3 M=1 sub=0`
- `R1 e1a e1a rsil l=4.286u w=1.0u sub=0`
- `R2 e2a e2a rsil l=4.286u w=1.0u sub=0`
- `R3 e1b e1b rsil l=4.286u w=1.0u sub=0`
- `R4 e2b e2b rsil l=4.286u w=1.0u sub=0`
- `Q7 ntaila ntaila ntaila npn13G2 we=70n le=900n NX=10 M=1 sub=0`
- `Q8 ntaila ntaila ntaila npn13G2 we=70n le=900n NX=1 M=1 sub=0`
- `R5 nvtop ntaila rhigh l=1.0u w=2.0u sub=0`
- `Q9 ntailb ntaila ntaila npn13G2 we=70n le=900n NX=10 M=1 sub=0`
- `Q10 ntaila ntaila ntaila npn13G2 we=70n le=900n NX=1 M=1 sub=0`
- `R6 nvtop ntaila rhigh l=1.0u w=2.0u sub=0`
- `Q11 lond lond lond npn13G2 we=70n le=900n NX=6 M=1 sub=0`
- `Q12 lond lond lond npn13G2 we=70n le=900n NX=6 M=1 sub=0`
- `Q13 lond nswb nswb npn13G2 we=70n le=900n NX=6 M=1 sub=0`
- `Q14 lond nswb nswb npn13G2 we=70n le=900n NX=6 M=1 sub=0`
- `R7 lop lond rsil l=1.429u w=1.0u sub=0`
- `R8 lon lond rsil l=1.429u w=1.0u sub=0`
- `R9 na1p nbiasL rhigh l=1.47u w=1.0u sub=0`
- `R10 nb1p nbiasH rhigh l=1.47u w=1.0u sub=0`
- `R11 nb2n nbiasL rhigh l=1.47u w=1.0u sub=0`
- `R12 na2n nbiasH rhigh l=1.47u w=1.0u sub=0`
- `R13 ifp nifbias rhigh l=1.47u w=1.0u sub=0`
- `R14 ifn nifbias rhigh l=1.47u w=1.0u sub=0`
- `C1 ifp ifp cmim area=514.382 sub=0`
- `C2 ifn ifn cmim area=514.382 sub=0`
- `C3 ifp ifp cmim area=514.382 sub=0`
- `C4 ifn ifn cmim area=514.382 sub=0`
- `R15 vcc lond rsil l=6.429u w=1.0u sub=0`
- `R16 vcc lond rsil l=6.429u w=1.0u sub=0`
- `C5 ntaila ntaila cmim area=514.382 sub=0`
- `C6 ntaila ntaila cmim area=514.382 sub=0`
- `Q15 ntaila ntaila ntaila npn13G2 we=70n le=900n NX=1 M=1 sub=0`

## 阶段 drv1（cdl：pex_drv1_v19.cdl）

| 检查项 | 计数 | 明细 |
|---|---|---|
| Q 件 b==e（基极/发射极同名=粘连） | 4/4 | Q1(cop)、Q2(con)、Q3(ntail)、Q4(nref) |
| R 件两节点同名（自环=远端被并入） | 2 | R1(e1)、R2(e2) |
| cdl 网名（deck 中无对应） | 1 | nref |
| deck 网名（cdl 中消失=被并没） | 2 | hbt_mirror、ntail |

**cdl 器件清单（原始行）**：

- `Q1 cop e1 e1 npn13G2 we=70n le=900n NX=6 M=1 sub=0`
- `Q2 con e2 e2 npn13G2 we=70n le=900n NX=6 M=1 sub=0`
- `R1 e1 e1 rsil l=1.0u w=1.75u sub=0`
- `R2 e2 e2 rsil l=1.0u w=1.75u sub=0`
- `Q3 ntail nref nref npn13G2 we=70n le=900n NX=8 M=1 sub=0`
- `Q4 nref nref nref npn13G2 we=70n le=900n NX=1 M=1 sub=0`
- `R3 vcc nref rhigh l=1.19u w=1.0u sub=0`
- `R4 inp nref rhigh l=1.0u w=1.36u sub=0`
- `R5 inn nref rhigh l=1.0u w=1.36u sub=0`
- `R6 bin nbias rhigh l=1.0u w=1.36u sub=0`
- `R7 bb1 nbias rhigh l=1.0u w=1.36u sub=0`
- `R8 vcc cop rppd l=1.0u w=2.6u sub=0`
- `R9 vcc con rppd l=1.0u w=2.6u sub=0`

## 阶段 drv2（cdl：pex_drv2_v19.cdl）

| 检查项 | 计数 | 明细 |
|---|---|---|
| Q 件 b==e（基极/发射极同名=粘连） | 12/12 | Q1(ccas1)、Q2(ccas1)、Q3(outp)、Q4(outn)、Q5(ntail)、Q6(nref)、Q7(ntail)、Q8(nref)、Q9(ntail)、Q10(nref)、Q11(ntail)、Q12(nref) |
| R 件两节点同名（自环=远端被并入） | 2 | R1(ccas1)、R2(ccas1) |
| cdl 网名（deck 中无对应） | 1 | nref |
| deck 网名（cdl 中消失=被并没） | 4 | ccas2、hbt_mirror、nbcas、ntail |

**cdl 器件清单（原始行）**：

- `Q1 ccas1 ccas1 ccas1 npn13G2 we=70n le=900n NX=10 M=1 sub=0`
- `Q2 ccas1 ccas1 ccas1 npn13G2 we=70n le=900n NX=10 M=1 sub=0`
- `Q3 outp ccas1 ccas1 npn13G2 we=70n le=900n NX=10 M=1 sub=0`
- `Q4 outn ccas1 ccas1 npn13G2 we=70n le=900n NX=10 M=1 sub=0`
- `R1 ccas1 ccas1 rsil l=1.0u w=4.665u sub=0`
- `R2 ccas1 ccas1 rsil l=1.0u w=4.665u sub=0`
- `Q5 ntail nref nref npn13G2 we=70n le=900n NX=8 M=1 sub=0`
- `Q6 nref nref nref npn13G2 we=70n le=900n NX=1 M=1 sub=0`
- `R3 vcc nref rhigh l=1.19u w=1.0u sub=0`
- `Q7 ntail nref nref npn13G2 we=70n le=900n NX=8 M=1 sub=0`
- `Q8 nref nref nref npn13G2 we=70n le=900n NX=1 M=1 sub=0`
- `R4 vcc nref rhigh l=1.19u w=1.0u sub=0`
- `Q9 ntail nref nref npn13G2 we=70n le=900n NX=8 M=1 sub=0`
- `Q10 nref nref nref npn13G2 we=70n le=900n NX=1 M=1 sub=0`
- `R5 vcc nref rhigh l=1.19u w=1.0u sub=0`
- `Q11 ntail nref nref npn13G2 we=70n le=900n NX=8 M=1 sub=0`
- `Q12 nref nref nref npn13G2 we=70n le=900n NX=1 M=1 sub=0`
- `R6 vcc nref rhigh l=1.19u w=1.0u sub=0`
- `R7 inp nref rhigh l=1.0u w=1.36u sub=0`
- `R8 inn nref rhigh l=1.0u w=1.36u sub=0`
- `R9 bin nbias rppd l=1.923u w=1.0u sub=0`
- `R10 bb1 nbias rppd l=1.923u w=1.0u sub=0`
- `R11 vcc outp rppd l=1.0u w=2.6u sub=0`
- `R12 vcc outn rppd l=1.0u w=2.6u sub=0`

## 汇总

- cdl 三件 HBT 总数 **31**，其中 **b==e 粘连 31**（占 100%）
- R 件自环（远端并入）共 **8** 件

**判读**：这批 cdl 的**标称值与前仿 deck 逐件一致**（派生层自测 9/9 机器精度复核，见 pex_devmodels_selftest.log），但**拓扑级存在系统性粘连**：HBT 基极与发射极同名、发射极电阻变自环、感测/尾网/LO 域被并名。⇒ 属提取 deck 侧「幻影焊」未解（b7a0 主闸门：候 deck 修复版 LVS 重提），不是代入器或派生层的建模问题。

