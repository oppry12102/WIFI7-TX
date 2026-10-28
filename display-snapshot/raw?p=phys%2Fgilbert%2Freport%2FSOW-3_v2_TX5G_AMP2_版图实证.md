# SOW-3 v2.0 · TX5G_AMP2（两级 HBT 放大级）版图实证 —— 从版图到后仿真的全链记录

> ⚠️ **2026-10-16 11:37Z 组长增补更正（详见 `SOW-3_v2.1_TX5G_AMP2_机理判定.md`）**：
> 1. **本文所有「A0 (dB)」是绝对电平 dBV**（激励 `AC 0.05`），不是电压增益。
>    同口径**电压增益 = A0 + 26.02 dB**：前仿真 +4.41 dBV = **+30.43 dB 增益**，
>    后仿真 −29.06 dBV = **−3.04 dB 增益**，落差 33.47 dB（落差不变，前后同参）。
> 2. **本文 §7 的处方「要么加大退化电阻」在固定 Vbe 偏置下是错的**（实测 Re×2/×4/×8 使增益
>    单调变差 −8.36/−9.13/−11.77 dB，Ic1 从 2.45 掉到 0.90 mA）。唯一有效处方是**降低回流路径电阻**。
> 3. 机理已判定为**小信号发射极阻抗失配**（非直流偏置漂移）；并且**各网贡献不可相加**，
>    归零 rc/vcc 反而再掉 5dB（非单调）。
> 4. 本文归因表为手工跑出，v2.1 已脚本化（`phys/gilbert/sim/attrib_amp2.py`）并加入 f3dB 有效性判定。
> 本文其余内容（DRC/LVS/PEX 提取、复现步骤、边界声明）仍然有效。

> 缘起：管理员 2026-10-16 09:55Z 问「真实版图/DRC-LVS/PEX/后仿真能做吗」。v1.0（`phys/`）用单级
> HBT 差分级跑通了全链，结论是「22×32µm 的小走线只吃 0.4dB」。本 v2.0 换一个**版图更吃互连**的块，
> 并把 v1.0 暴露出来的口径坑全部填掉。

## 0. 一句话结论

**两级 HBT 放大级 TX5G_AMP2 全链跑通：真实 GDS → DRC 零违规 → LVS Netlists match →
第一阶 PEX → 后仿真。结论有两层：**

1. **器件几何口径**（v1.0 的隐含问题）：LVS 从版图实测的 HBT 发射极几何是 `le=0.9µm, we=0.07µm`，
   而模型卡 `npn13G2` 的默认几何是 `le=0.96µm, we=0.12µm` —— 版图实际发射极面积比模型默认小
   **1.8 倍**。前/后仿真必须显式声明用哪一套（`DEV_GEOM` 开关）。
2. **互连寄生**：本块标称 RSH/C 估值下，版图寄生把中频增益从 **+4.41dB 打到 −29.1dB**，
   主要来自 **vss 地轨串联电阻（3.8Ω×2）** 与 **发射极 M2 走线（1.75Ω×2）+ M1 短桩 + via**。
   根因是**发射极退化电阻（45.8Ω）只有 ~5×1/gm，发射极节点的小信号阻抗只有几欧姆**，
   加上地轨电流造成的几十 mV 直流偏置漂移，两者叠加把增益打崩。

---

## 1. 目标块：TX5G_AMP2（两级 HBT 放大级）

选它的理由：这是 TX 链里**版图最吃互连**的一段——级间节点 `cb2` 同时连着驱动管基极、输出管基极、
耦合电阻 RC 和走线；发射极要经 `via_stack` 从 M2 落到 M1 再走到退化电阻；地轨要横贯全块。

```
Vcc 3.3
Q1 npn13G2 Nx=4   B=bin(片外驱动源 DC 0.98)  E=e1--RS1(45.8)-->vss   C=rc--RL1(793.7)-->vcc
RC  rsil l=2u(22.9)   rc -> cb2       级间耦合（同时给 Q2 基极提供直流通路）
Q2 npn13G2 Nx=4   B=cb2  E=e2--RE2(45.8)-->vss   C=out--RL2(406)-->vcc
片外：Cblk 1nF 隔直 + 50Ω（AC 主测不挂 50Ω，否则 50Ω 把输出节点压到 33Ω、版图寄生看不出来）
```

| 参数 | 值 | 来源 |
|---|---|---|
| I_C1 / I_C2 | 2.6 / 7.4 mA | ngspice op 实测 |
| 增益 A0 | +4.41 dB（输出开路口径） | `phys/gilbert/pre/amp2_pre.sp` |
| f_3dB | 1.585 GHz | 同上 |
| A(3GHz) / A(6.8GHz) | −2.20 / −8.53 dB | 同上 |

---

## 2. 工具链（与 v1.0 同一套）

KLayout 0.30.0（debian 免 root 解包，`pdk/kl_env030.sh`）+ IHP-Open-PDK 官方 DRC/LVS deck
+ ngspice-47（`pdk/ngroot`）。

## 3. 真实 GDS（`phys/gilbert/gds/amp2.gds`）

`phys/gilbert/layout/gen_amp2.py` 生成，7 个 PDK PCell（2×npn13G2 Nx=4、2×rsil l=4u、
1×rsil l=2u、2×rppd）+ 1 个 via_stack，M1/M2 两层手工布线，39 × 21 µm。

**布线阶段 net_check.py 抓到的坑（都已修）**：

1. M2 发射极走线直接向右拐，会和 M1 的 bin/cb2 走线**跨层重叠**（HBT 的 C/B/E 同列，
   M1 基极引脚在正下方）→ 改成先**向上**拐 1.2µm 再横走。
2. 发射极网络被 via_stack 分成 M2 段和 M1 段，PEX 要分别提 R/C → 两段各标一个网名
   （`et1m1` / `et1m2`），再用显式 via 电阻串起来。

## 4. DRC（官方 maximal deck，`--no_density`）

**最终零违规**（`phys/gilbert/drc/final4/`，63.7s；LVS 同步 PASS，`phys/gilbert/lvs/run4/`）。v2.0 迭代中抓到的**真实违规**：

| 规则 | 现象 | 修法 |
|---|---|---|
| `metal2_drw_Offgrid` | 发射极拐点 `ey+1.2 = 6.192µm` 越过 5nm 栅格 | 所有自算坐标统一 `g(v)=round(v/0.005)*0.005` |
| `M1.b`（M1 同网小间距 0.18µm） | rc 横线 0.3µm 宽，顶边 13.15 与 RC 顶部引脚焊盘下沿 13.27 只差 **0.12µm** | 贴引脚那段加宽到 0.96µm（与 rsil/rppd 焊盘同宽） |
| `M1.b` | 输出线竖段左边 30.85 贴着 Q2 集电极大焊盘右边 30.7，差 **0.15µm** | 输出线右移到 x=32 再上拉 |
| `EXTB.c`（EXTBlock–pSD 间距 0.31） | 退化电阻 cell 挪到 y=−3.1 时触发 | 继续下移到 y=−4.0（**final4 通过**）|

## 5. LVS（官方 deck，`--run_mode=flat --ignore_top_ports_mismatch`）

**Netlists match / PASS**（`phys/gilbert/lvs/run4/amp2_extracted.cir`，7 个器件全识别）。

踩到的最大一个坑：**发射极退化电阻 rsil l=4u 一开始完全提取不出来**
（`rsil device terminals don't touch device marker` / `No. of ports exist for rsil is 1`）。
根因：SG13G2 LVS deck 的 rsil 识别层是
`rsil_res = polyres_mk ∩ res_drw − (pSD ∪ SalBlock ∪ nSD ∪ nSD_block)`，
**只要 rsil 的 cell bbox 与 HBT cell 的 bbox 有交叠**，就可能被这些层排除掉。
把 RS1/RE2 整体挪到 HBT bbox（y≥1.67）以下即解决。

## 6. PEX（第一阶几何法，`phys/gilbert/pex/extract_pex_amp2.py`）

| 网 | 层 | 走线长度 µm | R_total Ω | C_total fF | 引脚数 |
|---|---|---|---|---|---|
| rc | M1 | 60.1 | 7.51 | 3.46 | 3 |
| cb2 | M1 | 46.0 | 5.75 | 1.31 | 2 |
| out | M1 | 34.5 | 4.31 | 1.27 | 2 |
| vcc | M1 | 84.2 | 10.53 | 2.51 | 2 |
| vss | M1 | 61.2 | 7.65 | 1.81 | 4 |
| et1m2 / et2m2 | M2 | 28.0 | 3.50 | 2.19 | 2 |
| et1m1 / et2m1 | M1 | 7.4 | 0.93 | 0.26 | 2 |
| via_stack ×2 | — | — | 0.15 | — | — |

**PEX 网表生成踩到的三个坑（都影响结果，必须记）**：

1. **零值元件不能发**：ngspice 会把 `0Ω` 电阻改写成 `1e-12Ω`、把 `0fF` 电容留在电路里，
   两者都会**改变直流解**（实测 Vrc 差 89mV）。对拍时零寄生网表必须**直接短接**（不生成
   p_/hub 拆分），否则「零寄生基线」和前仿真对不上。
2. **模型卡必须前后一致**：后仿真一度用了 PDK 原卡（`selft=1` 自热开），前仿真用等温卡
   （`selft=0`），仅此一项就差 6dB。HBT VBIC 的自热在开关瞬态下会让 ngspice 的 thermal node
   出 NaN（`Timestep too small`，已复现），所以瞬态统一用等温卡，自热另做直流点单测。
3. **器件几何口径**：见 §0 第 1 条。`DEV_GEOM=1` 时后仿真带 `le=0.9u we=0.07u`，
   对本模型的 npn13G2 **无影响**（le/we 只进入 l/v 变体��� rcx 公式），所以两行结果相同——
   这本身也说明「模型卡的 Nx 与版图 Nx 不是同一件事」。

## 7. 前/后对拍（`phys/gilbert/sim/pre_post_amp2.md`）

| 情形 | A0 (dB) | f3dB | A(6.8GHz) |
|---|---|---|---|
| 前仿真（零寄生） | **+4.41** | **1.585 GHz** | −8.53 |
| 后仿真（标称 RSH/C/via） | **−29.06** | 单调下降，无 3dB 点 | −30.28 |
| RSH×4 | −35.93 | — | −31.06 |
| RSH×16 | −35.66 | — | −33.48 |
| C×4 | −29.06 | — | −30.46 |
| RSH×16 & C×16 | −35.66 | — | −37.11 |
| via=1.0Ω | −31.67 | — | −30.32 |

**逐网归因（把某网的串联电阻归零，其余保留）**：

| 归零的网 | A0 (dB) | 相对标称 |
|---|---|---|
| 标称（全寄生） | −29.06 | — |
| vss 地轨 | −16.85 | **+12.2dB** |
| vss + 两个 M2 发射极走线 | −2.26 | +26.8dB |
| vss + 全部发射极网络 | +10.97 | +40.0dB |
| 全部串联 R（只剩 C 和 via） | +2.47 | +31.5dB |

**怎么读这张表**：

- 主导项是**发射极路径**（M2 走线 1.75Ω×2 + M1 短桩 0.46Ω×2 + via 0.15Ω ≈ 4.6Ω）
  和 **vss 地轨**（3.8Ω×2，承载约 9mA → 35mV 直流抬升）。
- 根因是**这一级的发射极退化只有 45.8Ω，约 5×1/gm（1/gm ≈ 3.5~10Ω）**，
  发射极节点的小信号阻抗就是几欧姆量级，几欧姆的金属电阻不是「小寄生」，而是**直接进分母**；
  地轨的直流压降又会整体抬高发射极电位、改变工作点。两者叠加 → 增益塌。
- 工程含义：**HBT 共射级要么把退化电阻加大到 ≫ 金属 R 的几十倍，要么把发射极路径
  （含地轨回流）当成 RF 大电流走线来布**（加宽、走 TopMetal1/2、缩短到 via）。这正是
  `design_circuit/layout_plan.md` 里「衬底耦合 / 走线长度差决定 LOFT 与正交误差」的同类问题。

## 8. 口径与边界（务必随结果引用）

1. **这是设计闭环级实证，不替代流片签核**：DRC 用了 `--no_density`（子块无 filler），
   LVS 用了 `--ignore_top_ports_mismatch`（KLayout 0.30.0 缺 `flag_missing_ports`）。
2. **金属层 RSH/C 是工程估值**（PDK 未随附金属层 R/C 数据）→ 给了 ×4/×16 扫描；
   结论对 RSH 不敏感（因为主导项是 vss/发射极路径的**直流**与**低阻**效应）。
3. **via 电阻 0.15Ω 是按 2×2 单 via 阵列估的**，扫描到 1.0Ω 时增益再掉 2.6dB。
4. **PEX 是一阶集总**：每网一个 hub + 每引脚 R/2、C/2；没有做耦合矩阵、没有 EM/IR/天线规则。
5. **AC 主测口径不挂 50Ω**（输出开路），因为 50Ω 会把输出节点阻抗压到 33Ω，
   版图寄生就看不出来；功率/P1dB 那套另加 Cblk+50Ω。

## 9. 复现步骤

```bash
. /data/workspace/pdk/kl_env030.sh
export PYTHONPATH="$PYTHONPATH:/data/xuseek/.venv/lib/python3.13/site-packages"
# 1) 出 GDS
KLAYOUT_PATH=$KLTECH klayout -zz -r phys/gilbert/layout/gen_amp2.py
# 2) 布线自检（短路/悬空）
python3 phys/layout/net_check.py phys/gilbert/gds/amp2.gds M1
python3 phys/layout/net_check.py phys/gilbert/gds/amp2.gds M2
# 3) DRC
cd $KLTECH/tech/drc && python3 run_drc.py --path=/data/workspace/phys/gilbert/gds/amp2.gds \
     --run_dir=/data/workspace/phys/gilbert/drc/final4 --mp=2 --no_density
# 4) LVS
cd $KLTECH/tech/lvs && python3 run_lvs.py --layout=/data/workspace/phys/gilbert/gds/amp2.gds \
     --netlist=/data/workspace/phys/gilbert/lvs/amp2.cdl \
     --run_dir=/data/workspace/phys/gilbert/lvs/run3 --run_mode=flat --ignore_top_ports_mismatch
# 5) PEX + 后仿真 + 对拍
python3 phys/gilbert/pex/extract_pex_amp2.py
python3 phys/gilbert/sim/compare_amp2.py
```
