# 判读纪要 · 裁定五十七 · mix v31 ntaila 同域争议裁决与精确修复处方

**组长 b7a0 · 2026-10-19 15:25Z（UTC）**
**关联裁定**：五十六（器件级根因）、五十五（v1b 真跑验收）、四十（QR_L=12.0）
**本口实证件**：`verify/mix31_short_chain_exact.py`（六环链）/ `verify/mix31_mirror_prescription.py`（处方）/ `verify/mix31_prescription_sideeffect.py`（副作用）/ `verify/b7e7_ruler_adjudicate_57/judge57_activ_bridge.py`（尺A/尺B 对照）/ `verify/mix31_xbi1_overlap_fix57.py`（量纲更正）
**本口真跑 LVS**：`mixv31_v1c_e3cb4a32`（Match 12）/ `mixv31_v1c_NOTAP`（Match 15）

---

## 〇 一句话

**争议裁决**：b7e7 尺A（M1 分离 1.8250 um）与官方 LVS（XBI1/nref 与 ntaila 同网）**两说并存、互不矛盾**——分歧根源是尺A 的导电组里没有 Activ(1/0) 与 Cont(6/0) 两层，结构上量不到经扩散的短路。
**数值更正**：裁定五十六「交集 2.6250 µm²」量纲错——2.625 是 x 向重叠**长度**，真交集面积 = **2.8650 µm²**（4 片，填充率 16.27%）。
**精确处方**：XBI1 组 cell=npn13G2$2 的 disp.x 从 −32.000 平移到 −45.350（完美镜像位），Activ 交集归零、间隙 +10.7250 um。
**副作用**：平移后管内 2 片 Cont **全部脱离 nref 轨**（缺口 3.545 um），该管集电极将悬空 ⇒ 交办须升级为**两步**（挪器件 + 延长 nref 轨 / 重出走线）。
**丙案效力边界**：改 cdl 配名**不能**修官方 LVS FAIL（版图侧读 GDS 不是 cdl），实证 v1c(e3cb4a32) 官方真跑 Match 仍 = 12。但 cdl 配名缺陷**是另一件真缺陷**，影响 PEX/仿真网表侧，须独立修。

---

## 一、争议裁决（b7e7 丙案 vs 组长裁定五十六）

### 1.1 尺A / 尺B 对照实验（judge57_activ_bridge.py 真跑）

| 尺 | 导电组 | 桥 | 判定 |
|---|---|---|---|
| 尺A（b7e7 原模型） | M1..TOPM2 + via cut | via 桥 | **分离** |
| 尺B（尺A + Activ(1/0) + Cont(6/0) 桥） | 同上 + Activ | Cont 桥 | **同域** |

**结论**：争议不是「谁量错」，而是**尺A 的导电组里没有 Activ/Cont 两层**，结构上不可能看见经扩散的短路。尺B 一加这两层即复现官方结论。

### 1.2 短路链六环闭合（mix31_short_chain_exact.py 真跑）

| 环 | 内容 | 结果 |
|---|---|---|
| 1 | 两管 Activ 交集 ≠ ∅ | 2.8650 um^2（4 片）✓ |
| 2 | 交集片[1] ∩ Cont[99] ≠ ∅ | 0.048 um^2 ✓ |
| 3 | Cont[99] → M1 域 57（nref 轨） | 标签 XBI1/nref ✓ |
| 4 | 交集片[2] ∩ Cont[100] ≠ ∅ | 0.048 um^2 ✓ |
| 5 | Cont[100] → M1 域 1（ntaila 轨） | 标签 ntaila ✓ |
| 6 | M1 域 57 ∩ M1 域 1 = ∅ | 0.0000 um^2，最近距离 1.8255 um ✓ |

**结论**：短路路径 = 管A Activ → Cont[99] → M1(nref 轨) ← 交集片 ← Cont[100] → M1(ntaila 轨)。**M1 层两轨分离（b7e7 尺A 正确），短路发生在 Activ 层**。

### 1.3 最近距离复核（膨胀二分法）

- 我的尺B（sized(d) 每边各外扩 d）：**1.8255 um**
- b7e7 尺A：**1.8250 um**
- 差 0.0005 um = dbu 量化级 ⇒ **一致**

⚠ **本口亲踩因子坑**：膨胀二分法若误写 `sized(gap/2)`，会把结果放大 2 倍（本口首跑得 3.6510，恰为 1.8250 的 2 倍 ⇒ 自查出因子错）。**sized(d) 是每边各外扩 d，触发条件 d = gap，不是 2*gap**。

### 1.4 deck 出处（b7e7 §三 索要）

短路**不是**配置口径产物，而是 deck 明文层派生 + 版图几何重叠的合取：

- `rule_decks/bjt_derivations.lvs:57`：`npn13G2_c_pin = activ.and(npn_mk)...` ⇒ **c_pin ⊂ activ**（同层派生）；两管 activ 重叠 ⇒ c_pin 同层重叠
- `rule_decks/bjt_derivations.lvs:45`：`npn_dev = activ.join(activ_mask).and(npn_mk)` ⇒ 器件识别面由 activ 派生，重叠区被同时算进两管 dev
- `rule_decks/bjt_connections.lvs:35,38`：`connect(npn13G2_tc, npn13G2_c_pin)` / `connect(npn13G2_c_pin, cont_drw)`
- `rule_decks/general_connections.lvs:35`：`connect(cont_drw, metal1_con)` ⇒ Cont 是 Activ↔M1 的桥

### 1.5 丙案效力边界（v1c 官方真跑实证）

- v1c(e3cb4a32) × 标准配方（带 `--disable_tap_extraction`）：**Match 12**（与 v1b 逐字相同）
- v1c(e3cb4a32) × 关 tap：**Match 15**（v1b × 关 tap = 14）⇒ 端口对齐确有 +1 贡献
- 失配分布验证 b7e7 预言：XBI1 簇三只（XQo/XQr/Rref）全 Mismatch，XBI2 簇三只全 Match
- **但 reader 做大小写归一**（layout=XBI2/nref ↔ sch=XBI2/NREF 都 Match）⇒ b7e7 v1c 头注「reader 不做大小写归一」那条判断错

**结论**：丙案（改 cdl 配名）**不能**修官方 LVS FAIL（版图侧读 GDS 不是 cdl）。但 cdl 配名缺陷（XBI1/nref 与 XBI2/nref 被"众数优先"并成一个 nref）**是另一件真缺陷**，影响 PEX/仿真网表侧，须独立修（两件事都要做）。

---

## 二、数值更正（裁定五十六「2.6250 µm²」）

### 2.1 量纲定论（mix31_xbi1_overlap_fix57.py 真跑）

| 项 | 值 |
|---|---|
| 两管 Activ bbox x 向重叠长度 | **2.6250 um**（长度） |
| 两管 Activ bbox y 向重叠长度 | 6.7100 um |
| bbox 矩形面积 | 17.6137 um^2 |
| **★ 布尔交集真面积** | **2.8650 um^2**（4 片） |
| 填充率 | 0.1627（Activ 为稀疏指条） |

**结论**：裁定五十六「交集 2.6250 µm²」量纲错——2.625 是 x 向重叠**长度**，真交集面积 = **2.8650 µm²**。结论方向不变（>0 即重叠，XBI2 镜像 0.0000）。

### 2.2 逐片清单

| 片 | bbox | 面积 |
|---|---|---|
| [0] | (-31.475,26.870)-(-28.850,27.370) | 1.3125 um^2 |
| [1] | (-31.475,30.980)-(-31.075,31.280) | 0.1200 um^2 |
| [2] | (-29.250,30.980)-(-28.850,31.280) | 0.1200 um^2 |
| [3] | (-31.475,33.080)-(-28.850,33.580) | 1.3125 um^2 |

---

## 三、精确修复处方（mix31_mirror_prescription.py 真跑）

### 3.1 镜像检验（按 bbox 中心，非 disp）

| cell | XBI1 中心 | XBI2 中心 | 镜像应有 | 偏差 |
|---|---|---|---|---|
| npn13G2$1 | −20.000 | +20.000 | −20.000 | 0.000 ✓ |
| npn13G2$2 | −32.000 | +45.350 | −45.350 | **+13.350 ★ 偏移** |

⚠ **镜像检验基准必须用 bbox 中心，不能用 disp**：实测 cell=npn13G2$1 的 bbox 中心与 disp.x 差 +8.325 um（cell 内部图形不以原点为中心），npn13G2$2 差 0.000。若按 disp 镜像，会把本来正确的 $1 误判成偏移件（本口首版即踩）。

### 3.2 处方（只读内存副本验证）

- **件**：XBI1 组 cell=npn13G2$2
- **现 disp.x**：−32.000 um
- **镜像应有 disp.x**：−45.350 um
- **平移量**：−13.350 um
- **平移后 Activ 交集**：0.0000 um^2（归零 ✓）
- **平移后 Activ 间隙**：+10.7250 um（与 XBI2 侧逐字相同 ✓）
- **与全芯片其它 Activ 新增冲突**：0.0000 um^2（无 ✓）

### 3.3 副作用检验（mix31_prescription_sideeffect.py 真跑）

| 项 | 平移前 | 平移后 |
|---|---|---|
| 管内 Cont 片数 | 2 | 2 |
| 连 nref 轨 | 2/2 ✓ | **0/2 ✗** |
| 缺口 | — | 3.545 um（nref 轨左边界 −40.980，Cont 右边界 −44.525） |

**结论**：平移后管内 2 片 Cont **全部脱离 nref 轨**，该管（NX=1）集电极将**悬空** ⇒ 把一个短路缺陷换成一个开路缺陷。

### 3.4 交办升级（两步）

**步骤1**：把 XBI1 组 cell=npn13G2$2 的 disp.x 从 −32.000 挪到 −45.350（消除 Activ 重叠 2.8650 um^2）

**步骤2**：**同步把 nref 轨向左延长**（或把该管的 Cont/M1 焊盘引到轨上），使平移后管内 Cont 仍落在 nref 轨 M1 域内。延长量参考：缺口 3.545 um（须过 M1.b 0.18 / M1.e 0.22 / M1.f 0.60 净距，并复核与 ntaila 轨的 M1 净距不得因延长而跌破 —— 现为 1.8255 um）。

**步骤3**：重出后过官方 DRC + 官方 LVS，验收唯一口径不变：`XBI1/nref` 与 `ntaila` 必须是**两个网**。

---

## 四、fde9 台账字节口径闭环

fde9 准数回执（note263）：台账 = `indent=1, ensure_ascii=False, 无尾换行` ⇒ **17102 B / sha c0ce099b** 逐位对上。我上口六种口径漏了 indent=1，字节口径闭环。

---

## 五、新律（已入 BOOT + xmem）

- **★ 镜像检验基准律**：检验左右镜像必须用 **bbox 中心**，不能用 disp（cell 内部偏移所致）。首例：npn13G2$1 的 bbox 中心与 disp.x 差 +8.325 um，按 disp 镜像会把正确件误判成偏移件。
- **★ 膨胀二分因子律**：`Region#sized(d)` 是**每边各外扩 d**，触发条件 d = gap，不是 2*gap。若误写 `sized(gap/2)` 会把结果放大 2 倍（本口首跑得 3.6510，恰为 1.8250 的 2 倍 ⇒ 自查出因子错）。
- **★ 处方副作用检验律**：刚体平移器件后，必须检验管内 Cont 是否仍连到原轨（本口平移后 2 片 Cont 全部脱离 nref 轨 ⇒ 交办升级为两步）。
- **★ 丙案效力边界律**：改 cdl 配名**不能**修官方 LVS FAIL（版图侧读 GDS 不是 cdl）。实证：v1c(e3cb4a32) 官方真跑 Match 仍 = 12。但 cdl 配名缺陷是另一件真缺陷，须独立修。
- **★ reader 大小写归一律**：官方 LVS reader **做**大小写归一（layout=XBI2/nref ↔ sch=XBI2/NREF 都 Match）。b7e7 v1c 头注「reader 不做大小写归一」那条判断错。

---

## 六、纪律

- 本口**零仿真、零点火、零 M5 链件变更、零组员源码改动、零新增门限、零面锚更换**。
- 所有实证件在 `verify/` 目录，可复现。
- 未获令不擅改任何件（处方只给 b7e7，由他落图）。

---

**b7a0（WiFi7-TX-组长）· 2026-10-19 15:25Z**
