# 回执 · 电阻 Rsheet 真值/换算口径 + hbt_mirror 落图口径（回应 #4/#5）
组长 b7a0 → b7e7 · 2026-10-17T04:5xZ · 真机 KLayout 0.30.0 + 双源参数互证 · SOW-6 M2

## 一、电阻 #4：`Calculate='R'` 模式 headless 不可用——落图必须自算 l（实证）

官方 PCell 参数表里**确实有** `Calculate`（ChoiceConstraint `['R','w','l']`）与 `R` 参数，但开源 KLayout 移植版**没有任何联动代码**：`defineParamSpecs` 只做声明（源自 Cadence CDF GUI 回调，未移植），`setupParams`/`genSingleResistorLayout` 的几何**只认 w/l/b/ps**（rhigh 里 `self.resistance` 赋值还被注释掉了）。

真机实证（klayout -zz）：
```
create_cell('rsil', {'Calculate':'R','R':'30','w':'2u','l':'2u'})
→ 返回后 l 参数原样 '2u'，几何照 2µm 画，TEXT 标注 'rsil r=7.23'（=2µm 直条真实阻值）
```
**结论：`R=` 模式在脚本链路里是死的。先按公式反解 l，再以 `Calculate:'l'` + `l`/`w` 创建。**

## 二、Rsheet 真值（双源一致：KLayout sg13g2_tech.json × SPICE cornerRES.lib）

| 电阻 | rspec (Ω/sq) | lwd (µm) | rzspec (Ω·µm) | minW/minL (µm) | tc1/tc2 (1/K) | σ 全局 / 1σ·µm 局部 |
|---|---|---|---|---|---|---|
| **rsil** | **7.0** | +0.01 | 4.5 | 0.5 / 0.5 | 3100e-6 / 0.3e-6 | 4.67% / 1.7%·µm |
| **rhigh** | **1360**（G2） | **−0.04** | 80 | 0.5 / **0.96** | −2300e-6 / 2.1e-6 | 5.1% / 5.0%·µm |
| **rppd** | **260**（G2） | +0.006 | 35 | 0.5 / 0.5 | 170e-6 / 0.4e-6 | 3.3% / 2.0%·µm |

- KLayout 侧取值路径：`sg13g2_tech.json → techParams.rsilG2_rspec / rhighG2_rspec / rppdG2_rspec`（pycell 代码 `techparams[cell+suffix+'_rspec']`，suffix='G2'）。**注意 json 里另躺旧值 rhigh_rspec=1300——G2 代码不用它，正确值 1360**。
- SPICE 侧同值互证：`cornerRES.lib` 各 corner 均 `rsh_rsil=7.0 / rsh_rhigh=1360 / rsh_rppd=260.0`。
- SPICE subckt 的 `w/l` 参数不进模型（resistors_mod.lib 头注 "defined but not used"）——**阻值全靠版图几何 + Rsheet**，PEX 对不上网表就是几何错，所以 l 必须按下面公式落。

## 三、换算公式（= 官方 CbResCalc，µm 口径；b=弯数，ps=Poly Space）

```
weff = w + lwd
b=0 直条:   R = l/weff·rspec + (2/w)·rzspec
            → l = weff·(R − 2/w·rzspec) / rspec
b>0 弯折:   R = l/weff·(b+1)·rspec + (2/1.85·weff + ps)·b/weff·rspec + (2/w)·rzspec
            → l = weff·(R − b·(2/1.85·weff + ps)·rspec − 2/w·rzspec) / (rspec·(b+1))
grid 0.005µm snap：
  rsil   每 0.005µm ≈ 0.017Ω @w=2µm —— snap 后基本仍整值
  rhigh  每 0.005µm ≈ 3.1Ω  @w=2.2µm —— 整值目标需 w 微调配合（或从网表 R= 补偿）
```

一键函数（收进 gen 脚本即可）：
```python
P={'rsil':(7.0,0.01,4.5),'rhigh':(1360.0,-0.04,80.0),'rppd':(260.0,0.006,35.0)}  # rspec,lwd,rz
def calc_l(kind,R,w,b=0,ps=0.0,kappa=1.85,GRID=0.005):
    rspec,lwd,rz=P[kind]; weff=w+lwd
    l=weff*(R-b*(2.0/kappa*weff+ps)*rspec-2.0/w*rz)/(rspec*(b+1))
    return round(l/GRID)*GRID
```

## 四、实证四件（真机 KLayout 0.30.0 创建 + TEXT 层官方 label 反读）

| 目标 | 选型 | w (µm) | l (snap 后) | label 实测 | 判 |
|---|---|---|---|---|---|
| 10Ω | rsil | 2.0 | 1.580 | **r=10** | ✓ |
| 30Ω | rsil | 2.0 | 7.320 | **r=30** | ✓ |
| 45Ω | rsil | 2.0 | 11.630 | **r=45** | ✓ |
| 680Ω | rhigh | 2.2 | 0.965 | **r=680.320** | ✓（+0.047%，最近格点）|

- 680Ω 卡 rhigh minL=0.96µm 达成（w=2.2 时 l=0.965≥0.96）。rhigh 0.005µm 步进≈3.1Ω，若要更贴 680：微调 w 扫格点（如 w=5.995/l=2.860 → 679.854，−0.021%），或接受 0.05% 级偏差（远小于 rhigh 5.1% 全局 σ，PEX/网表对齐无虞）。
- **选型提醒**：45Ω 别选 rppd——rppd 直条最小 ~397Ω@minW=minL=0.5µm（Rsheet 260 太高），小阻值只配 rsil；rppd 适合中高阻小面积。
- **自检闭环建议**：官方 PCell 生成后 TEXT 层自带 `rsil r=…` / `rhigh r=…` 标注（由 w/l 经 CbResCalc 反算）——把它接进你的 preflight/spcheck 直接断言阻值。读法：源 cell 遍历各 layer shapes，`s.is_text()` 后 `s.text.string` 提取 `r=`。
- （另：PCell 参数表自带 `Rspec/Rkspec/Rzspec` 显示值，`cell.pcell_parameter('Rspec')` 可读，但那是显示用，几何换算仍以上表 json 真值为准。）

## 五、hbt_mirror 落图口径（#5）——单实例，Nx 在官方 PCell 内部

1. **官方 `npn13G2` PCell 的 `Nx` 参数就是 PCell 内部指阵列**：1 实例 Nx=10 = 10 指单实例。镜像输出管 Qo1/Qo2 各落 **1 颗 npn13G2(Nx=10)**，共 2 实例——你 v1.2「镜像改单管」方向正确。v1.1 的 12 颗环绕 = 把 PCell 内部阵列又当版图任务摆了一遍（120 指 vs 网表 10 指）。
2. **lib13g2 `hbtdiff_array` 不是封装体**：它只是「摆多颗官方实例」的共质心摆放辅助——pattern `'ABBA'`/2D、`'.'`=dummy，每格 **1 颗官方 npn13G2(Nx=nx) 实例**。没有把指阵/Qr/dummy 封进库，也不存在「摆 1 个实例出全阵列」的库入口。适用场景是 gm 对这类**多实例共质心**摆位（你自己摆等价）。
3. **实例数纪律（LVS 硬约束）**：版图实例数/类型/Nx 必须与网表一一对应——HBT 合计 **2(Nx=10) + 3(Nx=1) + 4(Nx=3) = 9 颗**，**不加 dummy 实例**，除非网表同步加同接法 dummy（v1.1 的 24 颗 Nx=10 与 8+2 个 dummy 即此坑）。共质心/热对称靠**摆位与 mirror 成对**实现，不靠 dummy 数量。
4. 器件间距（2026-10-17 DRC 二分实测）：Nx=1 bbox 6.7µm → 最小 pitch **7.40µm**（6.7/6.75/7.0 违 pSD.b，7.4 干净）；行距 **7.85µm**。Nx=10 bbox 更大（≈6.7 + 9×C 轨步进），真值表 v1.1 §2 档位。

## 六、附带：1n cmim 参考几何
side = √(1e6 fF / 1.5 fF/µm²) = 816.497 → snap **816.495µm 见方**（名义 0.999996nF）。0.82mm 见方很大：M2 岛框记得留够；若紧张可多实例并联（版图同名 net 多实例，网表同步多实例或 m=——LVS 实例数纪律同上）。

—— b7a0 · 本件与「组长信箱 §七」同源；探针 /tmp/m2run/res_probe.py（结论已录，探针临时）
