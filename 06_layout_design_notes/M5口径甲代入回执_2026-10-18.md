# M5 口径甲代入回执 —— 双门判定（门1 FAIL·未进动态·未点火 27 角）

- 回件：`M5口径甲代入回执_2026-10-18.md`
- 收件：b7a0（WiFi7-TX-组长）｜抄送：b7e7（电路设计）
- 时间：2026-10-18 02:5xZ（UTC）｜提交：fde9（WiFi7-TX-仿真验证）
- 口径依据：**《M5 PEX 口径裁定（组长四裁）》**（8510 `design/sow6/M5口径裁定_b7a0四裁_2026-10-18.md`，2818 B，sha `2859c0ec99bb07ad…`）——四裁已全部执行到位。
- 结果一句话：**口径甲代入器按裁定一实现并落档；门1 在 `.op` 阶段即无解（OP 无解，singular at `xmi.nsens`），**
  **门2 未评、27 角未点火；根因经静态审计定位为「提取侧幻影焊未解（cdl 31/31 HBT 基极与发射极同名）」，
  不是代入器/派生层的建模问题。**

---

## 一、裁定执行对账（四裁逐条）

| 裁定 | 要求 | 本方执行 | 状态 |
|---|---|---|---|
| 一（阻塞A） | 口径甲：cdl 只替换 L0 实物器件行，deck 理想件逐字保留 | 新建 `m5_pex_substitute_jia.py`：按器件名白名单逐条替换；deck 侧 `Bvbl/Bvbh/Bvifb/Bvt/Is0/RL1/RL2/Lt1/Lt2/Cca1,2/Ccb1,2`（+ 各阶段 `Cin/Vb/Vbcas/Ct/.param`）逐字保留；端口序逐字核对，不一致即停 | ✅ 已实现并落档 |
| 二·护栏1 | 逐件「原行 → X 行」映射日志留档 | `pex_subst_audit_jia.md`（15.9 KB）：逐阶段列 deck 保留/剔除行、cdl 剔除行及原因、逐件映射表 + 派生标称值 | ✅ |
| 二·护栏2 | 门1 回归 Δ=0 继续作改写正确性机器闸 | 前仿 `.op` 重跑复现 **A0′ = 0.000000 PASS**（ref `typ_v015_1.raw` vs dut `base_probe.raw`） | ✅ |
| 三（双门锚） | 0.05 dB 操作门 + 0.5 dB 工程门（27 角） | 门限脚本按 0.05 dB 实现（`m5_parse_pex_tran.py`）；0.5 dB 判据在 27 角判读段；**本次门1 未过 → 两门均未进** | ⏸ 门1 未过 |
| 四（cmim） | 按 area 面项 771.573 fF 点火，-0.44% 备案 | 派生层 `cmim` 子电路按 `C = area×1.5fF/µm²` 实现 = 771.573 fF（面项，无周长外推） | ✅（备案待落 27 角报告首页） |

## 二、门1 判定：FAIL（OP 无解）

跑件：`sow6/pdk/sim/v015_1/chain_top_tb_v015_1_pex_jia_op.sp`（口径甲代入后的**只跑 .op 快筛件**，与全 tran 件同一电路）
原始日志：`sow6/m5/pex_jia_op_screen.log`（14129 B，sha `56f4eb8b51f724f5…`）

```
Warning: singular matrix:  check node xmi.nsens      （×5）
Note: Starting dynamic gmin stepping → Dynamic gmin stepping failed
Note: Starting true gmin stepping  → True gmin stepping failed
Note: source stepping failed
Error: Transient op failed, timestep too small
Error: The operating point could not be simulated successfully.
```

- A0′：**不可测（无 OP 解）**，非「超门」。
- 门2 / 27 角：按口令②「任一不过：停线报我，带原始数据」——**未进动态、未点火**。

## 三、根因定位：静态结构审计（会诊第一输入）

`pex_struct_audit.md`（6677 B）+ `m5_pex_struct_audit.py`（可重跑）：

| 阶段 | HBT 件数 | **b==e（基极/发射极同名）** | R 自环 | deck 网被并没 | cdl 新增网名 | cdl 自带 WARNING |
|---|---|---|---|---|---|---|
| gilbert_mix | 15 | **15 / 15** | 4 | lopd、nsens、nswa、nswb、ntailb、rfon、rfop | — | merged-domain `['gnd','nsens','ntaila']→ntaila`；`['lond','lopd','nswa','rfon','rfop']→lond` |
| drv1 | 4 | **4 / 4** | 2 | ntail（→cdl 改名 nref）、hbt_mirror 实例 | nref | — |
| drv2 | 12 | **12 / 12** | 2 | ntail、ccas2、nbcas、hbt_mirror 实例 | nref | — |
| **合计** | **31** | **31 / 31（100%）** | **8** | | | |

判读（与《判读纪要_mix_cdl网名策略裁定》《…幻影焊判决…》同一框架）：

1. **标称值层面：全对**。派生层自测 9/9 机器精度（误差 ~1e-16）逐件复现前仿网表标称值
   （drv1 Re=4.0000 / RL=100.0000 / XBI=1618.4 / Rb=1000.0；drv2 Re=1.5005 / Rb=499.98；mix Re=30.002；cmim=771.573fF），
   日志 `pex_devmodels_selftest.log`。**⇒ 这批 cdl 是「值全对、拓扑全错」的件。**
2. **拓扑层面：系统性粘连**。三件 31 个 HBT **无一例外**基极与发射极同名（等价于把 B-E 结焊死），
   发射极电阻退化为自环（R1 e1a e1a …），感测/尾网/LO 域被并名。`nsens` 被并入 `ntaila` 后，
   deck 保留的 `Is0 vcc nsens` 与 `Bvbl/Bvifb/Bvt` 表达式失去参考节点 → **`xmi.nsens` 悬空 → OP 无解**。
3. 归属：**提取 deck 侧「幻影焊」未解**（b7a0 20:35:54Z 已交待：候 deck 修复版 LVS 重提 = 主闸门），
   **不是**代入器、派生层或口径甲实现的问题。
4. 判读纪要已给的二分：**deck 修复后若 b==e 仍在 = 版图真短 → 走回改流程，不许改名掩盖**。

## 四、口径甲实现要点（供复核）

1. **deck 侧**：白名单内逐字保留；白名单外器件行一律剔除（L0 实物件由 cdl 接管）。
2. **cdl 侧**：Q/R/C → X 改写（Q/R/C 三类共 37 件全转，`R n1 n2 name` 只查 `.model`、子电路只能 `X` 实例化；
   `npn13G2` 是四端 `.subckt c b e bn`，cdl 的 `sub=0` → 补第 4 端 `0`）。
3. **重复计入防护（请备案确认）**：凡 cdl 件是「deck 保留件」的**实物孪生**（同位置同标称值）则剔除，
   已剔 5 件并入审计日志：

   | cdl 件 | 孪生的 deck 保留件 | 标称值核对 |
   |---|---|---|
   | mix R15 / R16 | deck `RL1/RL2` 45Ω tank 负载 | RSIL×6.429/1.0 = 45.0Ω ✓ |
   | drv1 R8 / R9 | deck `RL1/RL2` 100Ω tank 负载 | RPPD×1.0/2.6 = 100.0Ω ✓ |
   | drv2 R11 / R12 | deck `RL1/RL2` 100Ω tank 负载 | RPPD×1.0/2.6 = 100.0Ω ✓ |

   不剔除则 45Ω 变 22.5Ω、100Ω 变 50Ω（硬错），故按裁定一「deck 理想件逐字保留」只能取 deck 侧。
   mix 的 `C1~C4`（ifp/ifn 对地 MIM 771.573fF）与 deck 的 `Cca1,2/Ccb1,2`（ifp/ifn→na1p/nb1p **片外串联**耦合 1nF）
   **不是同一元件**（对地寄生 vs 片外串联耦合），故两者并存，不属重复计入。
4. 端口序：三阶段 `.subckt` 头逐字核对通过（mix ifp ifn lop lon rfop rfon vcc / drv1 inp inn cop con vcc / drv2 inp inn outp outn vcc）。
5. 派生层接入：`.include /data/workspace/sow6/m5/pex_devmodels.lib`（不改 cdl 一字）。

## 五、门限有效性背书（0.05 dB 是不是在噪声里？）

前仿 typ 同 deck **重跑复现**（02:12–02:27Z 重跑件，195.2 MB）：

- 全链 CG = **17.446489113733694 dB**（与 10-17 首跑**逐位一致**），Δ vs 锚 17.4465 = **−1.09e-05 dB**
- 前仿 `.op` 六探针重跑 **A0′ = 0.000000**（六点全 2.5 V，差分 ≤ 8.9e-16 V）
- ⇒ ngspice-47 同 deck 重跑噪声底 ≈ **1e-5 dB**，**0.05 dB 操作门 ≈ 4600× 噪声底**；
  修复版 cdl 到货后，|ΔCG| 只要超过 0.05 dB 就必是物理量，不会是数值抖动。
- 派生物：`sow6/m5/typ_v015_1_tran.raw`（sha `76f047746a6af1b8…`）、`base_probe.raw`（sha `d5c09b80f8e8300e…`）

## 六、请求裁决 / 交付事项

| # | 事项 | 收件 | 状态 |
|---|---|---|---|
| R1 | **deck 修复版 cdl（解体=归位）到货即刻重跑门1/门2**：代入器、派生层、双门脚本、27 角 runner 均已就位，**无需再请示**（沿用 20:35:54Z 预授权） | b7e7 → b7a0 | 待件 |
| R2 | 若 deck 修复后 b==e 粘连仍在（=版图真短），按《…幻影焊判决…》走**回改流程**，不以改名掩盖 | b7a0 | 请确认 |
| R3 | 第四节「实物孪生件剔除」5 件规则**请备案确认**（不确认则下轮仍按此执行，异动即报） | b7a0 | 请确认 |
| R4 | 裁定四的 −0.44% cmim 系统偏差，**27 角报告首页注记**已排版待落（27 角未点火，暂不落） | b7a0 | 备案 |

## 七、四件套（runbook v2.5 §五 格式）

1. **判读结果 JSON**：`M5门1判定与结构审计_2026-10-18.json`（6384 B）
   — 含门1 判定与原始报错行、静态结构审计逐阶段计数、裁定执行对账、噪声底、请求项、全部 sha256。
2. **关键数值**：A0′ = 不可测（OP 无解，singular `xmi.nsens`）｜CG_PEX = 未评｜Δ vs 锚 = 未评｜
   噪声底 = 1e-5 dB（CG 重跑逐位一致）｜b==e 粘连 = 31/31。
3. **跑件/deck/raw sha256**（全表见 JSON）：
   cdl mix `33e9e754…`／drv1 `ae4feb76…`／drv2 `1f5e0cd8…`；
   口径甲 deck `77b26e5c1c82596f…`（全 tran 件）／`e1f475e6fab1a3b4…`（.op 快筛件）；
   派生层 `90174e7e3dec69b9…`；前仿 typ tran `76f047746a6af1b8…`；op 重跑 `d5c09b80f8e8300e…`。
4. **偏差归因与请求裁决项**：见第三节归因 + 第六节 R1–R4。
5. **drv2 四组偏置同漂判读**：**不适用**——门1 未过，未进动态/B 层（无 drv2 静态点表可出）。

## 八、附：随件清单

| 文件 | 内容 |
|---|---|
| `M5口径甲代入回执_2026-10-18.md` | 本件 |
| `M5门1判定与结构审计_2026-10-18.json` | 判读结果 JSON（四件套 1、3） |
| `pex_struct_audit.md` | 静态结构审计（deck vs cdl 逐件） |
| `pex_subst_audit_jia.md` | 口径甲逐件映射日志（裁定二护栏1） |
| `pex_jia_op_screen.log` | 门1 原始 ngspice 日志 |
| `m5_pex_substitute_jia.py` | 口径甲代入器 |
| `m5_pex_struct_audit.py` | 静态结构审计脚本 |

—— fde9（WiFi7-TX 仿真验证）2026-10-18
