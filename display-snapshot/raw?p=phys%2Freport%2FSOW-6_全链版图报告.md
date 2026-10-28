# SOW-6 · 全链完整版图（GDS）结项报告

- 版本：**v0.3（现况校准升版）** · 组长 b7a0 · 2026-10-23T15:34Z（v0.2 正文一字未删，只加 §0-bis 并更新状态行）
- 任务书：`phys/SOW-6_全链版图立项书_2026-10-17.md`（v1.0，管理员 2026-10-17T00:40Z 立项）
- 状态：**M1 ✅ / M2 v2.4 + M3 v1.3/v1.2 已代跑闭环候 b7e7 v25 轮 / M4 未启动 / M5 前仿基线已备案**
  → **块级现况（面锚与签核状态）见 §0-bis（2026-10-23 现算）**；本状态行为 2026-10-17 候件期快照。
- 本稿性质：候件期预填骨架——M1 章节已按终稿口径写就；M2/M3/M5 填现状锚点，到件代跑后升版补全；M4 占位。
- 库版本注记（2026-10-17T07:44Z）：lib13g2 升 **v2.2**（538行/27592B，sha 02ecbfb9…，canonical=design/sow6/lib13g2.py）
  ——Board.via 增 TopVia1 阵列透传（修官方 vt1_* 硬编码坑）；阵列外推真值见 phys/top/probe_viastack_阵列外推_v22_2026-10-17.md；
  b7e7 自检台升 v25（⓪ 库版本闸 + ⑮ HBT 间距项），其 15/15 PASS 与我代跑同验 v2.1，版本面对齐。

---

## 0. 进展一览

> 本表为 2026-10-17 候件期快照；M2/M3 的现役面锚与签核状态以 **§0-bis** 为准。

| 里程碑 | 内容 | 主责 | 状态 | 关键产物 |
|---|---|---|---|---|
| **M1** | 共享版图库 + 冒烟件 | 组长 | ✅ **闭环（v2.1）** | `phys/top/lib13g2.py` v2.1（26,221 B，sha b0583f69…）；v2a/v2b 双板 maximal DRC 零违规 |
| **M2** | mix 级（Gilbert 共质心 + gm 对 + 尾流 + Rd/tank） | b7e7 设计 / 组长代跑 | ⏳ **v2.4 代跑闭环 07:2xZ**：preflight 14×3 PASS、cmim×6+ptap1×8 实落、环零真几何违规；DRC 剩 Offgrid+核内间距/线宽族候 v25 | 判读纪要 phys/top/判读纪要_M2M3代跑v24全链_2026-10-17.md（投盘 sha 3c9bf6be…） |
| **M3** | drv1 + drv2 功率级（R-EMIT-02 + R-VIA-01 实做） | b7e7 设计 / 组长代跑 | ⏳ **v1.3/v1.2 代跑闭环 07:2xZ**（teeth 11/11）；待修：TM1.a/TM2.a 线宽族 + Slt.c.M1 开槽（drv2 大平面 150µm） | 同上纪要 §4.2 逐条坐标 |
| **M4** | 顶层拼接 + pad ring + ESD + 电源网格 + seal ring | 组长 | ⬜ 未启动 | 依赖 M2/M3 定稿 |
| **M5** | 全链 PEX 后仿对拍 + 判读 | fde9 主判 / 组长复核 | ⏳ 前仿基线已备案 | typ CG=+17.4465 dB（§7） |

### 0-bis 现况校准（2026-10-23T15:34Z 现算；组长 b7a0）

本报告 v0.2 正文写于 2026-10-17（候件期）。此后 M2/M3 的面锚与签核状态已推进，按**当日现算**校准如下；
**v0.2 既有正文一字未删**，只加本节并更新状态行。

| 块 | 现役面锚 | sha8（本地＋8510 GET 双核） | bytes | DRC | LVS |
|---|---|---|---|---|---|
| M2 mix | `phys/top/m2_mix_v35.gds`（top=TX5G_M2_MIX_V35） | `396571f0` | 96,660 | 219 | PASS 29/29 |
| M3 drv1 | `verify/drv1_v23_run/out/m3_drv1_v23.gds` | `d5e1296c` | 63,502 | 18（对 v21_r1 ZERO-DELTA） | PASS 13/13 |
| M3 drv2 | `gds/m3_drv2_v22.gds` | `25adcbd1` | 79,564 | 147（对 v20 ZERO-DELTA） | PASS |

- **双核口径**：本地 sha256 现算 ＋ 按名 GET 8510 `/files` 回读现算，三件**全部 BYTE-IDENTICAL**（第九轮零漂移）。
- **M4 顶层**：**仍未启动**（顶层 floorplan 与 LO_BUF 仍规划级）⇒ **全链 GDS 未出、全链一致性检查未做**（§0 表 M4 行与 §8 判据不变）。
- **M5**：主基线**未升面**；三块面锚的提取网表/链件（cdl、pex）**一概未动**（cbpath 冻结 `25190557`）⇒ 本节不构成"后仿已按新面对拍"。
- **旧锚处置**：mix v31 `ef034d51`／v34 `0fc902ec`／drv1 v21_r1 `62c27a42`／drv2 v20 `c9363888` **一律留档不删**（旧面基准）。
- 证据件：`phys/top/判读纪要_裁定六十五_b7e7v35批验收_v35×v1g_LVS_PASS_M4b根修闭环_组长自纠027溯源_2026-10-19.md`（`9bc29d5b`）、
  `phys/top/判读纪要_裁定六十七_src分流三待裁_AST律边界_两处面锚分叉_2026-10-19.md`（`b2aff83c`）、
  `phys/top/判读纪要_裁定七十四_真GDS带条清单与43338对表_2026-10-20.md`（`4706e7ab`）。

---

## 1. 任务与范围（对齐立项书 §1）

四级核心版图（lo_buf / gilbert_mix / drv1 / drv2，对应 v015.1 chain 子电路）+ 顶层拼接 +
pad/ESD，全管线 DRC / LVS / PEX / 后仿对拍收口。保真度分级：L0 全真实（HBT/R/MIM/金属/pad/ESD）、
**L1 备案不实做（tank 电感 EM 项）**——版图留禁区 + 占位标注（IND 27/0 + nofill x/23 +
NoMetFiller 160/0 + NoRCX 148/0），网表沿用理想 Lt 口径，结项显式声明。不做 PLL/数字基带（隔离占位区标注）。

## 2. 基线锚（零漂移）

| 锚 | 文件 | 状态 |
|---|---|---|
| 网表 | `pdk/sim/v015_1/chain_top_tb_v015_1.sp`（27/27 PASS 基线） | 冻结 |
| 版图准则 | `design_circuit/HBT级版图准则_v1.2_b7e7.md` + **v1.3 组长注记版**（R-VIA-01 拓扑 / R-EMIT-02 金属 Rsheet 真值 / R-RES-01 poly 三档 / R-ANNO-01 注记纪律） | v1.3 注记版已投 8510 design/sow6/（sha 3c1842c8…，18,912 B） |
| 管线 | SOW-3 两轮实证（gen → DRC maximal → LVS → PEX 几何法 → 后仿对拍） | 沿用 |
| 工具链 | pdk/kl_env.sh（KLayout 0.30.12，`-zz` + PYTHONPATH venv site-packages）+ pdk/ihp_open/ | 固化 |

## 3. M1 · 共享版图库（✅ 闭环）

### 3.1 交付物
- **`phys/top/lib13g2.py` v2.1**（26,221 B，sha b0583f69…）：全原语库——via_stack / guard_ring（双环）/
  bondpad / HBT·R·MIM 封装 / net_check（v2.1 两修复）。
- 冒烟板双绿：`top/m2lib_smoke.gds`（全原语板，v2a 同批）+ `top/m2lib_v2b.gds`（双环专项板），
  SG13G2 maximal deck `--no_density` **零违规**（stdout 两份留档 2026-10-17）。
- 共享盘 `top/` 七件全套（库 + 两 gen 脚本 + 两 GDS + 两 stdout + 纪要）。

### 3.2 真值与裁决（组长判读，纪要见 phys/top/）
1. **via_stack 六组合全通**（probe 实测 + 官方 maximal deck）：
   M2↔M3 / M3↔M4 = 0.70×0.61；M4/M5↔TM1 = 1.64×1.64 大环档。
   **Q1 裁决：全栈单颗、中间层焊盘全留**——柱下 keepout 为必需（非保守），R-VIA-01 max 列 = techlef 真值，
   target = max×½ 降额（最终 PEX ≤0.2 Ω 门，187 件/边维持）。
   金属 Rsheet 真值（libs.ref techlef，开源 PDK 唯一金属 RC 出处）：
   M1 0.135 / M2–M5 0.103 / TM1 0.021 / TM2 0.0145 Ω/□（厚 0.40/0.45/2.0/3.0 µm）；
   Cont 22 / Via1–4 20 / TopVia1 4.0 / TopVia2 2.2 Ω/件。**A1「15 Ω/□」作废。**
2. **镜像语义**：库无缺陷零改动——`Trans(2,True,0,0)` ≡ 左右镜像；b7e7 判别式把 mirror 参数记反（已澄清）。
3. **cmim 实装**：PCell 名 `"cmim"`，参数 = w & l；0.84 pF → 23.66 µm 见方。
4. **R-RES-01 poly 真值**：cornerRES 三档 rhigh 1160/1360/1560、rppd 234/260/286、rsil 6.02/7.0/7.98 Ω/□
   （1σ 5/2/1.7%）；2 kΩ 电阻 = rhigh 1360 typ。
5. **R-ANNO-01 注记纪律**：/25 被 connect 进金属网 = 次级 label（写非网名必生幽灵网）；
   63/0 被器件模式匹配（varicap/ntap/isolbox/rfnmos）；占位说明不回 GDS；254/0 私有层默认不用
   （官方穷举零命中，Q4 裁决：**无自由注释层**）。
6. **LVS 口径**：层次网表 NAMES_SEP="/"（Q2）；块级岛不放 bondpad（Q3，M2 两浮空 pad 已撤）。
7. **guard_ring 双环 + keepout**（需求单⑤⑥）：外 ptap×50 + 内 ntap×48（inset 2.0）；
   **NBL.b 真值**：ntap 环 NBL 宽 1.26 µm + space 1.5 → 中心距 ≥2.76，库定 step_n=2.8；
   **M1.b 真值**：min space/notch 0.18 µm → **接线盖头法纪律**（wire 加宽与端头大面积重叠合并=无边缘对，禁擦边）。
8. **net_check v2.1 两修复**：①悬空桶（hit=−1）误入短路判定→除名；②bbox 包含误吸环形多边形环内
   label → bbox 粗筛 + `Polygon.touches(zero-box)` 精判（merged 对嵌套多边形吞成外框，勿用此法，真环形安全）。
   ⚠ 代跑口径：M2/M3 件若依赖旧版 net_check 语义（假短路放行），判读以 v2.1 严口径为准。

### 3.3 KLayout 铁坑（复述防坑）
`-b` batch 不加载 pycell 宏包（create_cell 全返 None）→ 必 `-zz` + PYTHONPATH 追加 venv site-packages
（SOW-3 报告 §3 配方）。

## 4. M2 · mix 级（⏳ v2.3 已交付候投件，b7e7 主笔）｜**块级现况见 §0-bis**

- 现状：v2.0 自查作废（⑤b 同名分裂）；v2.2 撤回（4 跨层短路 + 11 柱压异网）。
- **v2.3（2026-10-17 06:29Z 文字交付收讫，自检 12/12，岛 143.4×383.8 µm，网名 29/29 闭合）**：
  15 FAIL 清零——病根 = npn13G2 C/B/E 同 x，竖直干路必竖穿同器件另两脚；修法 = 三类脚专属通道
  （C→M1 外折 ∓15 竖轨 / B→岛心内折 ∓3/±6 通道 / E 居 M2 不动），柱头只落自己通道。
  顺带修三结构 bug：Rd1/Rd2 两端接反改正、偏置网 `_geom[0]` 双重计算改真引脚、guard 环压核改
  环宽 2 µm + RING_M 8 退核外 ≥3 µm。发射极回流不变（drv1 196.1 / drv2 155.9 / drv2 双层 108.7 mΩ）。
- **自检台升 12 项**：新增 ⑫ 引脚极性几何取证（过孔感知并查集、按几何不按声明）——**立为代跑验收硬门**。
  b7e7 自纠「7 注入 7 FAIL 假通过」（探针 import 崩出非真抓）→ 修正为 11 真 FAIL + 逐条先验原件 PASS，
  教训立组级纪律：**判 FAIL 前证「机制在跑」，判 PASS 前证「机制能抓」**。
- **Q7 裁决（组长，2026-10-17T06:4xZ，reply_v12 §二）**：guard 环（器件隔离环）≠ pad/seal ring（M4），
  **环保留岛内、不删不推 M4、不许悬空**。ptap 环标 gnd；ntap 环标岛内正电源网（禁接 nbias 偏置网 /
  lop 交流节点；tap 中心距 ≥2.8 µm）；最简合规 = ptap 单环标 gnd（v2a 口径 DRC 背书）；ntap 双环升不升
  留 M4 按噪声预算定。datatype=25 标注文本只写网名本身（写别的=幽灵网）。定网后 5 处「柱下无标注金属」
  注记应清零。
- 组侧硬门（代跑必查）：⑤b / ⑤c / ⑤d / ⑦b / ⑧ / ⑫ + preflight 12 项 + teeth 11 注入。

## 5. M3 · drv1 + drv2（⏳ drv2 v1.1 + drv1 v1.2 候投件代跑）｜**块级现况见 §0-bis**

- b7e7 05:46Z 信报 v1.1（自检 11/11）；**06:29Z 撤回 drv1 v1.1**（自查出 bb1 电气断线：
  底段画到 ch=24 而回流竖管在 x=50，差 8 µm 没接上；一行修 land_x=50.0）→ 改交 **v1.2**（自检 12/12）。
  **drv2 v1.1 用新检查复跑仍 PASS，不撤。**
- 投件卡点根因（06:3xZ 判定）：v10/v11 催办信只写「token=filekey」未给值——**配方含糊非通道故障**。
  reply_v12 §四已给全文（POST 8510 /files，token=<redacted>…（与 GET 同把）、name=design/sow6/<名>、
  中文名 URL quote、逐件投+贴 sha）。
- 组侧待办：到件铃 → 取件 → sha 对账 → `kl_env030 -zz` gen → GDS → maximal DRC（--no_density）
  → net_check v2.1 → preflight 12 项 → teeth 11 注入 → 回执。三件齐一次跑完。
- 验收锚（立项书 §5）：drv2 发射极回流 PEX 回读 ≤0.14 Ω/边；via 规模 ≥ 方案 2 档（187 件/边）。

## 6. M4 · 顶层 + pad/ESD（⬜ 未启动）

依赖 M2/M3 定稿。范围：floorplan 岛式布局（对齐 layout_plan.md §2）、级间走线、电源网格、
guard ring、bondpad（PDK 官方 PCell）、ESD 二极管族（diodevdd/vss 2kV/4kV）、seal ring；
顶层 maximal DRC + 6_9_pad.drc 单跑。 tank 禁区标注（L1）。

## 7. M5 · PEX 后仿对拍（⏳ 前仿基线已备案，fde9 主判）

- **typ 前仿基线（2026-10-17 05:2xZ 备案）：CG = +17.4465 dB**（sanity PASS，Δ=−0.0235，门 ±0.05）——
  PEX 对拍唯一锚。纪要 `pdk/sim/r2run/判读纪要_sow6m5_typ基线_2026-10-17.md`（已投共享盘）。
- 口令已下：PEX 代入先过 **A0′ ≤1e-5 门** → 门内进 27 角 PVT（后仿 deck）。
- 验收门：链级 CG 退化 ≤0.5 dB（相干 bin 直读口径）；ACPR/EVM 观察项备案不设门槛。
- fde9 联动：①偏置全联动（常数项×k，runner 由 rail-only 改）已批候回执；②C 层（27 角扩 save）不做、
  维持 A/B 分层（置位角≥3 或 typ 置位再议）。候其 runbook 投 8510 design/sow6/。
- PEX 件未产出（时序在 M3 替代件之后）。

## 8. 验收判据对照（立项书 §5）

| # | 判据 | 现状 |
|---|---|---|
| 1 | DRC maximal 零违规（四级+顶层）+ 6_9_pad.drc | M1 冒烟板双绿；M2/M3 候件；M4 未启动 |
| 2 | LVS Netlists match（对 v015.1 subckt，CDL 纪律沿用） | 候 M2 v2.3 / M3 代跑 |
| 3 | drv2 回流 ≤0.14 Ω/边 + via ≥方案 2 档 | M3 到件后代跑量测 |
| 4 | 全链 PEX 后仿 CG 退化 ≤0.5 dB | typ 前仿锚已备案；PEX 候 M5 |
| 5 | ACPR/EVM 备案 + L1 显式声明 | 本稿 §1 已声明；后仿读数候 M5 |

## 9. 风险台账（滚动）

| 风险 | 状态/预案 |
|---|---|
| M2 迭代轮次 | v2.3 返工方向已定（x 通道），若再一轮不达线则组长侧介入布线 |
| 投件通道（8445 死） | 8510 /files 投件口通道本身正常（自投回环多轮验证）；四轮零到件根因=催办信配方含糊（token 未给值）——reply_v12 已补全配方候改投 |
| tank EM 缺位 | L1 备案维持；管理员若给 EM 工具任务书另立升版 |
| net_check 口径差 | v2.1 严口径为唯一判读标准（旧版假短路语义作废） |

## 10. 文件索引（本报告引用）

- 纪要：`phys/top/判读纪要_{M3接收与八项回执,Q4注释层与Rsheet真值,lib13g2v2_guardring_keepout}_2026-10-17.md`、
  `phys/top/回执判定_via_cmim_镜像_2026-10-17.md`、`phys/top/回执_电阻Rsheet与hbt落图_2026-10-17.md`、
  `phys/top/probe_viastack_truth_2026-10-17.md`、`pdk/sim/r2run/判读纪要_sow6m5_typ基线_2026-10-17.md`
- 库/板：`phys/top/lib13g2.py`、`gen_m2lib.py`、`gen_m2lib_v2b.py`、两 GDS + 两 stdout
- 回执：`design/sow6/reply_v7~v12_from_b7a0_2026-10-17.md`（8510 在册；v12=Q7 裁决+Q1–Q6 重申+投件配方全文）、
  准则注记版、probe 真值
- 共享盘 `top/` 七件 + `pdk/sim/r2run/` 判读全链
- **§0-bis 现役面锚三件**：`phys/top/m2_mix_v35.gds`（`396571f0`）、`verify/drv1_v23_run/out/m3_drv1_v23.gds`（`d5e1296c`）、
  `gds/m3_drv2_v22.gds`（`25adcbd1`）＋判读纪要 裁定六十五（`9bc29d5b`）／裁定六十七（`b2aff83c`）／裁定七十四（`4706e7ab`）

---
变更史：v0.3（2026-10-23T15:34Z）块级签核现况校准（新增 §0-bis；MIX v35／DRV1 v23／DRV2 v22 双核实测，M4 仍未启动）；
v0.2（2026-10-17T06:4xZ）M2 v2.3 收讫+Q7 裁决落文+M3 撤换与投件根因更新；
v0.1 骨架预填（2026-10-17T06:2xZ，候件期组长预填；M2/M3/M5 到件代跑后升版）。
