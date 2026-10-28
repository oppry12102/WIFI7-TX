# 裁定六十四 · 27 角族 deck 实际 CDL 溯源与换锚前置 3/3 裁定

**时间**：2026-10-19 19:40Z（UTC）  
**触发**：fde9 19:20Z 来信（inbox #290，8350B）交来「27 角族/PEX/M5 谱系影响评估（换锚前置 3/3）· 修订版」  
**裁定人**：b7a0（WiFi7-TX-组长）  
**实测链**：本口独立复跑（19:21–19:40Z），逐件 sha + 器件行 diff + 几何指纹对拍，全链闭合

---

## 〇、核心结论（先读这条）

**fde9 核心主张成立**：27 角族 deck（`cb694761`，wu_gate2 帽）实际代入的 mix CDL 是 **V29 面 `ce97750b`**（头注 `GDS: TX5G_M2_MIX_V29` / SRC_GDS_SHA256 `8f6da23d`），**不是** premise_50_A 登记的 v31 面 CDL `f6ba9560`。

**根因**：代入器 `m5_pex_substitute_jia.py`（~~`ca74fd53`~~ **fde9 现役 `2cd712ba`**，裁定六十五更正——`ca74fd53` 是我方滞后镜像件）的 ~~`STAGE_CDL`~~ **`STAGES`** 映射**写死文件名** `'gilbert_mix': 'pex_mix_v27.cdl'`——而该文件名下的内容是 V29 面 CDL（`ce97750b`），v31 面的 CDL 存在**另一个文件名** `pex_mix_v31.cdl`（`f6ba9560`）下，代入器根本不会读它。**（此实质结论 fde9 在其现役件上独立复现成立，不受上述 sha/变量名更正影响。）**

**裁定**：
1. **换锚前置三条全达成**（情形 A：只改 GDS 面锚登记，deck 不动）
2. **premise_50_A 在册冲突坐实**（mix GDS 面锚 = v31 `ef034d51`，deck 实际 CDL 产物 = V29 面 `ce97750b`）
3. **命名纪律立律**（引用 v3x 时必须写明层次——`装配代 v3x` / `mix GDS 面 v3x` / `CDL 产物 v3x`，禁裸写 v3x）
4. **当前阶段不升 v34 面**（情形 B 成本-收益不对称，待 fde9 评估后再议）

---

## 一、实测链（逐项附出处，可复现）

### 1.1 代入器结构性锁死（写死文件名）

**代入器**：`sim_report/mirror_audit_20261018/m5_pex_substitute_jia.py`（`ca74fd53`，14895B）  
**关键代码**（L27-33）：
```python
STAGES = {
    'gilbert_mix': 'pex_mix_v27.cdl',
    'drv1':        'pex_drv1_v19.cdl',
    'drv2':        'pex_drv2_v19.cdl',
}
```

**代入器 `--cdldir design/sow6` 时，三件 CDL sha**：
| 阶段 | 文件名 | sha | 头注声明的源 GDS |
|---|---|---|---|
| gilbert_mix | `pex_mix_v27.cdl` | `ce97750b` | `TX5G_M2_MIX_V29` / `8f6da23d` |
| drv1 | `pex_drv1_v19.cdl` | `60093747` | （未标 SRC_GDS_SHA256） |
| drv2 | `pex_drv2_v19.cdl` | `6fc2ddc1` | （未标 SRC_GDS_SHA256） |

**与 runbook L483-485 逐字对上**：mix `ce97750b` / drv1 `60093747` / drv2 `6fc2ddc1` ✓

### 1.2 两份 `pex_mix_v27.cdl` 的器件行 diff

**V29 面 CDL**（`pex_in/arr207/pex_mix_v27.cdl`，`ce97750b`，2384B）：
```
Q7 ntaila ntaila gnd npn13G2 we=70n le=900n NX=10 M=1 sub=0
Q8 ntaila ntaila gnd npn13G2 we=70n le=900n NX=1 M=1 sub=0
R5 nvtop ntaila rhigh l=1.0u w=2.0u sub=0
```

**v31 面 CDL**（`outbox_files/design/sow6/pex_mix_v31.cdl`，`f6ba9560`，2475B）：
```
Q7 ntaila nref gnd npn13G2 we=70n le=900n NX=10 M=1 sub=0
Q8 nref nref gnd npn13G2 we=70n le=900n NX=1 M=1 sub=0
R5 nvtop nref rhigh l=1.0u w=2.0u sub=0
```

**差异**：3 行（Q7/Q8/R5），`ntaila` → `nref`（ntaila 分网修复）  
**节点集合**：两份 CDL 的 28 个节点名**逐字相同**（含 `nref`/`ntaila`/`ntailb` 等），差异纯在**器件连接拓扑**（Q7/Q8 的 B 极从 `ntaila` 改 `nref`，R5 从 `ntaila` 改 `nref`）  
**网数**：V29 面 28 网 / v31 面 35 网（差 7 = 6 匿名网 + 1 ntaila/nref 分网）

### 1.3 两份 `m2_mix_v29.gds` 的几何指纹对拍

**两份 sha**：
- `gds/m2_mix_v29.gds`：`c9bc8d98`（95924B，mtime 2026-10-18 18:39:51）
- `design/sow6/gds/m2_mix_v29.gds`：`8f6da23d`（95924B，mtime 2026-10-18 19:51:03）

**几何指纹对拍**（gdstk 逐 cell 的 polygon/reference/label 计数 + sha）：
- cells 数：21 vs 21 ✓
- cell 名集合：逐字相同（含顶层 `TX5G_M2_MIX_V29`）✓
- 几何指纹不同的 cell 数：**0** ✓

**结论**：几何层 IDENTICAL（字节差纯 BGNLIB 时间戳，132 字节位置全在 GDS 头部的 modification/access date 字段）  
**CDL 头注声明的源 GDS sha = `8f6da23d`** ⇒ 对上 `design/sow6/gds/m2_mix_v29.gds`，不是 `gds/m2_mix_v29.gds`

### 1.4 两份 `pex_drv2_v19.cdl` 的器件行 diff

**两份 sha**：
- `pex_in/arr207/pex_drv2_v19.cdl`：`ebe7d9d7`（1616B）
- `outbox_files/design/sow6/pex_drv2_v19.cdl`：`6fc2ddc1`（2018B）

**器件行 diff**：IDENTICAL（24 行逐字相同）  
**差异纯头注**：提取层次声明从 `R-only` 改 `R + cmim`（v5 起 MIM 面入提取）

### 1.5 代入器 sha 与 BOOT.md 记载不符

> ⛔⛔ **本节结论已由裁定六十五（2026-10-19 20:5xZ）撤销——本节是错的，原文留档不删。**
> **错在：我把「我方 8510 滞后镜像件」的 sha 当成了「fde9 现役件」的 sha，据此判 BOOT.md 记载过期。**
> 真相：**BOOT.md 原记的 `2cd712ba` 是对的**（fde9 现役代入器，31933B，他用它逐位复现了现役 deck `99307f45`）；
> 我实测的 `ca74fd53`（14895B）是**我方镜像件**，且**我自己 10-18 的 `MIRROR_HEAD_LEDGER_2026-10-18.md` 早已登记它为「滞后一版 · 只读参考」**
> （源侧现役 head 当时记 `a93c0d2f`，现已推进到 `2cd712ba`）。
> **⇒ BOOT.md 的更正已回滚**（`ca74fd53` → 恢复 `2cd712ba`，并注明镜像件身份）。详见裁定六十五 §六。

~~**BOOT.md 记载**：「代入器=**2cd712ba**」~~
~~**实测**：`ca74fd53`（14895B，mtime 2026-10-18 10:55:07）~~
~~**grep `2cd712ba` 全盘**：仅出现在旧纪要（裁定三十七/三十八/四十七），未找到对应实体文件~~
~~**结论**：BOOT.md 记载的 sha 已过期，须更正为 `ca74fd53`~~

**更正后的事实**：
- **fde9 现役代入器 = `2cd712ba`（31933B）**，在他侧 `sow6/m5/m5_pex_substitute_jia.py`；
  他 runbook L493 记「head `2cd712ba`（未动一字节）」**正确，不需改**。
  **决定性证据（他提供，我采信并登记）**：用该件在 `/tmp/t_sub` 隔离目录重跑档甲 ⇒ 产出 23861B、
  sha `99307f45…cfb4f`，与现役 deck `chain_top_tb_v015_1_pex_v34.sp` **`cmp` BYTE-IDENTICAL** ⇒ 现役 deck 确由 `2cd712ba` 产出。
- **我方 `ca74fd53`（14895B）= 8510 滞后镜像件**（我方 `sim_report/mirror_audit_20261018/` 与 `outbox_files/design/sow6/` 两处同 sha），
  差面 = **仅 MIM 电容支路**（缺 `CMIMP_F_PER_UM` 40 aF/µm、`PERIM_KEYS`、`_SCALE`/`_norm_um()`）——
  **按我方 MIRROR_HEAD_LEDGER §二.2「滞后镜像不得作停线/放行/判据器复核依据」，本不该拿它下「记载过期」的结论。**
- **grep `2cd712ba` 在我方盘找不到实体，是必然的**——那是**他侧**的件，我方只有镜像。我把「我方盘无实体」误读成「记载过期」。
- **变量名亦是我转述错**：我 §〇/§1.1 写 `STAGE_CDL`，**两侧实体都是 `STAGES`**（我方镜像 L28、他现役 L28-32）。
  **实质结论一致且不受影响**：`STAGES['gilbert_mix'] = 'pex_mix_v27.cdl'` 写死文件名 ⇒ 只读该名下的件（V29 面 CDL `ce97750b`），
  **不会读 `pex_mix_v31.cdl`（`f6ba9560`）** ⇒ 结构性锁死成立。**这条 fde9 在他现役件上独立复现、完全成立**（他 §四.1 末）。

### 1.6 gdsfp.py 路径更正

**BOOT.md 记载**：「几何指纹对拍 `python3 run_v2/gdsfp.py A.gds B.gds`」  
**实测**：`run_v2/gdsfp.py` 不存在，真路径 = `phys/sow6_run/run_v2/gdsfp.py`  
**结论**：BOOT.md 路径须更正

---

## 二、换锚前置三条裁定

### 2.1 情形 A：只改 GDS 面锚登记（v31 `ef034d51` → v34 `0fc902ec`），deck 不动

**谱系影响**：
- **27 角族**：不需要重跑（deck 不动 ⇒ 数值链零影响）
- **PEX**：不需要重提（deck 不动 ⇒ 寄生参数不变）
- **M5**：不需要重跑（与 27 角族同一 deck、同一跑批）

**换锚前置三条达成情况**：
1. ✓ LVS PASS（v34×v1f，裁定六十二）
2. ✓ DRC 新增项处置（M4.b 不构成换锚障碍，裁定六十）
3. ✓ **谱系影响评估 = 零影响**（本裁定）

**裁定**：**可以换锚**（情形 A），但须同时处置 premise_50_A 在册冲突（见 §三）

### 2.2 情形 B：用 v34 GDS 重新提取 CDL 并代入 deck

**谱系影响**：
- **27 角族**：需要重跑（v34 GDS 有实质布局变更：ntaila 分域 2.8650→0.0000 µm² + M4.b 镜像 + QR_OFF=25.35 真镜像）
- **PEX**：需要重提（v34 布局变更直接改变寄生拓扑）
- **M5**：需要重跑（与 27 角族同一跑批）

**预估工作量**：~5-8h（含等待）  
- v34 CDL 提取（b7e7 侧）：~1h
- deck 代入 + 审计：~0.5h
- 27 角族全跑（27 corners，detach 后台）：~2-4h
- 后处理 + 与 V29 面基线对拍 + 判据基线重建：~1-2h

**裁定**：**当前阶段不建议**（情形 B）  
**理由**：
1. **破坏数值连续性**：ntaila 分域 + M4.b 镜像是实质几何变更，换 CDL 后 27 角族结果与 V29 面基线不可直接比对 ⇒ 裁定五十九已收口的判据体系需重建基线
2. **成本-收益不对称**：~5-8h 全链重跑 + 基线重建 + 判据重定；v34 的收益（ntaila 同域消除、DRC −4）在当前阶段不构成紧急需求
3. **前置件未到位**：v34 CDL 尚未提取、v1f 网表未在 fde9 workspace ⇒ 无法独立复核

---

## 三、premise_50_A 在册冲突处置

**冲突**：premise_50_A 登记「mix v31 `ef034d51`」为冻结锚 + 「三份 cdl（…/`f6ba9560`）与本族全链建自这三面」；但 deck 实际代入 mix CDL = `ce97750b`（V29 面），**不是** `f6ba9560`。

**处置**：**(a) 补注 premise_50_A**（fde9 提议的三择一中的 (a) 案）  
**补注内容**：
```
mix GDS 面锚 = v31 ef034d51；但 deck 实际代入的 CDL 提取产物 = V29 面 ce97750b（件名 pex_mix_v27.cdl，源 GDS TX5G_M2_MIX_V29 sha 8f6da23d）。两者为不同层次，勿混读。
```

**授权 fde9 改台账**：
- 改 `premise_50_A` 补注（上述内容）
- 三步收尾法（写入前副本 + 锚点校验 + 新 sha 回报）
- corners/deck/verdict_55/verdict_59_registration 一字不碰

---

## 四、命名纪律立律

**新律**：**引用 v3x 时必须写明层次——`装配代 v3x` / `mix GDS 面 v3x` / `CDL 产物 v3x`，禁裸写 v3x**

**理由**：本轮混淆（fde9 信里的 PEX 前提、premise_50_A 的表述、「v34 代跑件」这个件名）三处同源，都是裸写 v3x 造成的。

**实例**：
- ✗ 「v34 代跑件」
- ✓ 「mix GDS 面 v34 代跑件 `0fc902ec`（装配代 v34，CDL 产物 V29 面 `ce97750b`）」

**生效**：即刻生效，fde9/b7e7 后续所有纪要/台账/投信一律遵守。

---

## 五、fde9 七条待裁定逐项回复

### ① 「换锚」语义澄清
**裁定**：情形 A（只改 GDS 面锚登记，deck 不动）

### ② 本评估是否满足换锚前置第三条？
**裁定**：是（情形 A ⇒ 三条全达成）

### ③ 在册冲突处置
**裁定**：(a) 补注 premise_50_A（见 §三）

### ④ v1f 网表 + v34 CDL 是否需 b7e7 移交至 fde9 workspace？
**裁定**：不需要（情形 A 下 deck 不动，无需独立复核 LVS PASS 或出情形 B 定量预估）

### ⑤ 裁定六十一 v2 预注册文复核进度？
**裁定**：已由裁定六十三（阶段 66）全段背书、即刻生效（D1/D2/D3 三项修订全对）

### ⑥ 台账二择一
**裁定**：已由裁定六十三裁 (a) 授权改，等回执新 sha

### ⑦ 命名纪律建议
**裁定**：采纳，立律（见 §四）

---

## 六、新律与更正

### 6.1 新律 1 条
- **★★命名层次律**（裁定六十四立）：引用 v3x 时必须写明层次——`装配代 v3x` / `mix GDS 面 v3x` / `CDL 产物 v3x`，禁裸写 v3x

### 6.2 BOOT.md 更正 2 处
- ~~代入器 sha：`2cd712ba` → `ca74fd53`~~ **⛔ 本条已回滚（裁定六十五）**：BOOT.md 原记 `2cd712ba` 是**对的**（fde9 现役件）；
  我实测的 `ca74fd53` 是**我方 8510 滞后镜像件**（我方 `MIRROR_HEAD_LEDGER_2026-10-18.md` 早已登记「滞后一版 · 只读参考」）。
  BOOT.md 已恢复 `2cd712ba` 并加注镜像件身份与差面。
- gdsfp.py 路径：`run_v2/gdsfp.py` → `phys/sow6_run/run_v2/gdsfp.py` **（本条成立，fde9 §四.2 亦确认；他侧纪要 L116 早已写完整路径，无需改）**

### 6.3 ⛔ §一.3/§一.4「fde9 未报但我查出的两处」——表述须限定（裁定六十五补）
我报的两处同名不同件（`m2_mix_v29.gds` `c9bc8d98` vs `8f6da23d`；`pex_drv2_v19.cdl` `ebe7d9d7` vs `6fc2ddc1`）
**是「我方盘内 / 我方 8510 与他侧之间」的差异，不是他盘内差异**——fde9 全盘搜 sha 均未找到我报的那两个件（他 §五.1），
他盘内 `m2_mix_v29.gds` 只有 1 个（`8f6da23d`，正是 CDL 头注声明的源 GDS，对上）。
**⇒ 结论不变（谱系可溯性要求 sha 唯一、引用须标 sha），但「fde9 未报」的措辞不当**：他没报是因为**他盘上不存在**。
**他另主动补报了他盘内更严重的同类问题**（`pex_mix_v27.cdl` 17 件/8 种 sha、`pex_drv2_v19.cdl` 16 件/8 种、`pex_drv1_v19.cdl` 16 件/7 种，
噪声源＝`selftest_cdl/` 夹具与 `rehearsal_*/` 演练件），并据此提议立**★★件引用双标识律**（件名 + sha 前 8 位，同名多件须加目录）
⇒ **裁定六十五采纳立律**（见裁定六十五 §四）。

---

## 七、纪律确认

- **零仿真、零点火、零 M5 链件变更、零面锚更换（仍 = v31 `ef034d51`）、零组员源码改动、零新增门限**
- 本裁定只做：谱系影响评估裁定 + premise_50_A 在册冲突处置 + 命名纪律立律 + BOOT.md 更正
- **未代定任何数值**（谱系影响 = 零影响，无需重跑/重提）
- **未改 fde9 的任何件**（一律只读 + 授权改台账）
- **未改 b7e7 的任何件**（一律只读）

---

## 八、产出

- **纪要**：本件（`判读纪要_裁定六十四_27角族deck实际CDL溯源与换锚前置33_2026-10-19.md`）
- **信 fde9**：`outbox_draft/reply_fde9_裁定六十四_谱系评估裁定与命名纪律.md`
- **信管理员**：裁定六十四报备
- **BOOT.md 更新**：阶段 67（裁定六十四）+ 代入器 sha 更正 + gdsfp.py 路径更正

---

## 九、下一步

1. **等 fde9 回执**：台账 premise_50_A 补注的新 sha
2. **等 b7e7 回**：在途 5 项（M4.b 统一处置／cdl 层次名塌缩／真 GDS 带条清单／v1.7-1.8 加 F15 条款／preflight ㉔㉓）
3. **当前阶段不升 v34 面**（情形 B 待 fde9 评估后再议）
4. **命名纪律即刻生效**：后续所有纪要/台账/投信一律遵守

—— b7a0（WiFi7-TX-组长）
