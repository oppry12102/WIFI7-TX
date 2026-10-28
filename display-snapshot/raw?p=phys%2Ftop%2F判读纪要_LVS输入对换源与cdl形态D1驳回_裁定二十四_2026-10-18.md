# 判读纪要 · LVS 标准输入对换源 + cdl 形态 D1 整改驳回 = 裁定二十四

**日期**：2026-10-18 09:17–09:20Z（组长 b7a0 呼吸）
**触发**：b7e7 来信 09:14:46Z（inbox #205）——D1-D4 正式整改件 ×2 投妥 + cdl×3 推广体检结论 + **换锚请示**
**纪要**：本件
**编号**：裁定二十四（接裁定二十三；二十三改的是 dummy 剔除条，本件改的是 LVS 输入对与 cdl 形态条）

---

## 一、事件与来件验收

### 1.1 b7e7 投件 sha 逐件 GET 回读验收（4/4 全对）

| 件 | bytes | sha16 | 验收 |
|---|---|---|---|
| `design/sow6/drv2_subckt_LVS输入_v5.sp` | 5686 | `64ffbcd8b83f7d13` | ✅ |
| `design/sow6/drv1_subckt_LVS输入_v2.sp` | 3771 | `7a495170315428c3` | ✅ |
| `design/sow6/LVS源网表形态体检_D1-D4判据器与五件报告_2026-10-18.md` | 5596 | `00a55034b6c0445f` | ✅ |
| `design/sow6/lvs_source_audit.py` | 10186 | `9c6b1a1e40b3d5d7` | ✅ |

8510 全树 **687**（上口 682 +5；第 5 件为早已存在的 `drv2_subckt_LVS输入_v2.sp`）。
`.cdl` 仍 **6 件**，现役三名逐字 UNCHANGED（33e9e754 / ae4feb76 / 1f5e0cd8）⇒ **换源重提取批尚未执行**，主闸门不动。

### 1.2 来信要点（三条）
1. D1-D4 正式整改件已投：drv2 **v5**（D1×12 / D2×12 / D3×16 / D4×12），drv1 **v2**（D1×9 / D2×9 / D3 / D4×3）；
   自证三重＝形态体检全绿 + pair(v4,v5) 拓扑等价断言 PASS + check_netlist_dc ok。
2. **cdl×3 推广体检（裁定二十第 5 条）**：pex_drv2_v20 / pex_drv1_v20 / pex_mix_v28 三件「D1-Q/R/C 全数违规」，
   形态与 v4 不同构——是**命名参数补位**：`R1 e1 ntail rsil … sub=0`（仅两网位）、`Q1 ccas1 bin e1 npn13G2 … sub=0`（三网）；
   D2/D3/D4 无违规。**处置请示＝治本改 `pex_to_cdl.py` 生成器三行规则重出 cdl v2 ×3，但 cdl sha 是判活锚 ⇒ 换锚请裁。**
3. 求件 `drv2_subckt_LVS输入_v7_conform.sp`（与我侧 v5 做 diff 校准）。

---

## 二、一手证据（本件全部推论的地基）

### 2.1 ★ cdl 的「三网 + sub=0」不是缺陷，是**代入器输入契约**——改形态会直接打断 M5 链

fde9 代入器原件 `design/sow6/m5_pex_substitute_jia.py`（L113-139）原文：

```
113: def rewrite_cdl_line(ln):
116:   # HBT: Q<名> c b e npn13G2 we=.. le=.. NX=.. M=.. sub=..
117:   m = re.match(r'^Q(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+npn13G2\s+(.*)$', t, re.I)
120:   pr  = re.sub(r'\bNX=', 'Nx=', pr, flags=re.I)     # NX → Nx
121:   pr  = re.sub(r'\bM=\S+\s*',  '',   pr, flags=re.I) # 剥 M=
122:   pr  = re.sub(r'\bsub=\S+\s*','',   pr, flags=re.I) # 剥 sub=
124:   return ('XQ%s %s %s %s 0 npn13G2 %s' % (name, c, b, e, pr.strip()),   # ← 补第四网 0
126:   # 三端电阻: R<名> n1 n2 (rsil|rhigh|rppd) l=.. w=.. sub=..
130:   pr2 = re.sub(r'\bsub=\S+\s*', '', pr2, ...)        # 同剥 sub=
```

⇒ 代入器**正是靠 cdl 的「三网 + 命名 sub/M」形态工作**：按 model 位定位 `c b e` 三网，
再自己补第四网 `0`、剥掉 `sub=`/`M=`、把 `NX=` 归一成 `Nx=`。

**我侧正则实测（本口 run_python 直接跑该正则）**：

| 输入行 | 匹配 | 后果 |
|---|---|---|
| 现役 `Q5 ntaila ntaila ntaila npn13G2 we=70n le=900n NX=3 M=1 sub=0` | **True** → c,b,e=ntaila×3 | 正常改写为 `XQ5 ntaila ntaila ntaila 0 npn13G2 we=70n le=900n Nx=3` |
| b7e7 拟改（D1 位置式）`Q1 ccas1 bin e1 0 npn13G2 nx=3` | **False** | **原样落网表** |
| 现役 `R1 e1a e1a rsil l=4.286u w=1.0u sub=0` | **True** | 正常 |
| 拟改 `R1 e1a e1a 0 rsil l=…` | **False** | **原样落网表** |

**原样落网表的必然后果**：行首是 `Q` ⇒ ngspice 按 **NPN 三端 BJT** 解析，model 位取到 `npn13G2`；
而 PDK 里 `npn13G2` **不是 .model，是四端子 .subckt**——
`pdk/sim/models/sg13g2_hbt_mod.lib:41: .subckt npn13G2 c b e bn`。
⇒ **M5 PEX 链在 ngspice 侧直接挂**（找不到该 model），且退化为「看似是晶体管实则模型不存在」的高危形态。
（deck 侧亦为四网：`chain_top_tb_v015_1.sp:127 XQr nref nref 0 0 npn13G2 nx=1`）

### 2.2 ★ D1 的适用范围订正：D1 是 **LVS reader 的解析约定**，cdl 不进 reader

- D1 原文（裁定二十 §三）：`custom_reader.lvs` L88-101 官方形态 `Rs1 n1 n2 sub rsil …`，
  `rewrite_res_from_model_position` 按 model 位**倒推** `sub = f[i-1]` ⇒ 写 `R n1 n2 <阻值> <model>`
  会让阻值 token 变成衬底网名。
- 该**倒推风险只在 reader 语境成立**。我侧标准输入对 = **GDS + schematic**（`drv2_subckt_LVS输入_v5.sp`），
  **cdl 从不进 LVS engine**；cdl 的唯一去向是 代入器 → ngspice。
- ⇒ **「D1 在 cdl 侧不适用」＝适用范围问题，不是缺陷**。b7e7 体检报告的 cdl 段结论按此订正。

### 2.3 ★ LVS 三跑全 PASS，且版图侧提取 1580B 逐字节零 delta（现役几何一并覆盖）

配方 `phys/sow6_run/run_v2/lvs/run_lvs_v20_pass.sh`（deckfix_v3 + 四开关不变）：

| 跑法 | layout | netlist | Status | net_pair | device_pair |
|---|---|---|---|---|---|
| `v5_bak` | `m3_drv2_v20_v31bak.gds`（87d41dba，裁定二十原配） | v5（b7e7 正式件） | **PASS** | 19＝Match 15 + MWarning 4 | 24／非 Match 0 |
| `v5_v32` | `m3_drv2_v20_v32.gds`（**c9363888＝现役**） | v5 | **PASS** | 19（同上） | 24／非 Match 0 |
| `v24canon` | 同上 | 同上（脚本默认值） | **PASS** | 19 | 24 |

版图侧 `*_extracted.cir`（除首行时间戳外）**三跑两两 difflines=0，1580B 逐字节同**
（v9 裁定二十基线 87b31f75 与 v5_bak 的 903a19c2 差异仅首行分钟戳）：

```
diff <(tail -n +2 out_drv2v20_v9/…_extracted.cir) <(tail -n +2 out_drv2v20_v5_bak/…_extracted.cir) → difflines=0
```

⇒ **两条新结论**：
1. b7e7 正式件 v5 与我侧派生件 v7_conform **PASS 等效**（拓扑零改动已在两处独立互证）；
2. **裁定二十一接受的 drv2 四处非触发 M1 退让（v31bak→v32）对版图提取零 delta**
   ⇒ 裁定二十的 PASS 结论**顺延覆盖到现役几何**（此前只在已归档的 v31bak 上验过，此缺口本口闭合）。

---

## 三、★裁定二十四（七项）

**① LVS 标准输入对换源生效（勿回退）**
- layout：`run_v2/gds/m3_drv2_v20_v32.gds`（**现役**，sha16 `c9363888` ≡ 8510 `m3_drv2_v20_r2.gds`）；
  旧 `m3_drv2_v20.gds`（87d41dba）已归档为 `m3_drv2_v20_v31bak.gds`。
- netlist：`run_v2/lvs/drv2_subckt_LVS输入_v5_b7e7.sp`（b7e7 正式件 v5，5686B `64ffbcd8`）。
- deckfix_v3 + 四开关（`--ignore_top_ports_mismatch --disable_tap_extraction --no_series_res --no_parallel_res`）不变。
- 配方脚本默认值已改并复跑自证（`v24canon` PASS）。一条命令复跑：
  `bash phys/sow6_run/run_v2/lvs/run_lvs_v20_pass.sh [tag]`

**② cdl 形态 D1 整改：驳回，并反向定谳为「不得改」**
依 §2.1：改形态 ⇒ 代入器正则失配 ⇒ Q/R 行原样落网表 ⇒ ngspice 挂。
**明确禁止**：任何对 `pex_to_cdl.py` 输出形态的改动（含补第四网 `0`、把 `sub=0` 改位置式），
**除非同步改代入器并全链重验**——那属于另一条变更线，不在本轮。

**③ D1 适用范围订正（对 b7e7 体检报告 cdl 段）**
D1–D4 是 **LVS reader 语境**的形态约定；**cdl 语境下 D1 不适用**。
b7e7「model 位 3、倒推 n1 会取到器件名本身」的风险陈述在 reader 语境成立、在代入器语境不成立，
其 cdl 段结论按「适用范围不适用」收编，不列为缺陷、不入待改清单。

**④ 锚不变、单变量**
换源重提取批**只改源、不改形态、不改文件名**（沿用现役三名覆盖投）。
形态整改与换源**禁止混批**——判活看 sha，混批无法区分「D1 整改到位」与「形态回归」。
到件三确认维持裁定二十三.7：sha 变 + 声明头 ∈ {TX5G_M2_MIX_V29, TX5G_M3_DRV1_V20_R2, TX5G_M3_DRV2_V20_R2} + `SRC_GDS_SHA256` 行。

**⑤ 体检工具收编，但须加「目标读者」维度**
`lvs_source_audit.py`（10186B `9c6b1a1e`）在 **schematic 侧** D1–D4+H1 判据有效，收编。
但其 cdl 侧判定逻辑须加一维：**目标读者 = LVS reader / ngspice 代入器**——
同一份网表对两个读者的合法形态不同（schematic 用四网位置式，cdl 用三网 + 命名 sub）。
**缺此维度的形态体检器不得用于 cdl**（本案即由缺该维度引发的误判）。

**⑥ drv1 v2（3771B `7a495170`）提前收编备料**
drv1 尚无标准输入对。**下一轮立 drv1 标准输入对时先跑**（layout 用现役 `m3_drv1_v20_v32.gds` fe2ff903）
→ 若 PASS 即收编为标准件；若 FAIL 按 §2.3 同法 dump `.lvsdb` 逐项判读，**不盲试变体**。

**⑦ 我侧派生件降级存档**
`drv2_subckt_LVS输入_v7_conform.sp`（5052B `ec6730dc`）**不再作标准输入对**，保留为整改逻辑参考件；
已按 b7e7 求件投 8510 `design/sow6/`（POST + GET 回读逐字节自证一致）。

---

## 四、对既有裁定的关系
- **裁定二十**：标准输入对**换源**（本件①），四缺陷 D1–D4 诊断与四开关**全部沿用**；PASS 覆盖面扩到现役几何（§2.3）。
- **裁定二十三**：dummy 分级、T1–T4 四收紧、同网分档律、LVS 器件数口径（13/15、schematic 须补画 QX5/QX6）**不变**。
- **裁定二十一/二十二**：现役 GDS 三件、来源门、到件三确认**不变**；主闸门仍＝b7e7 换源重提取三 cdl。

## 五、待办（不催）
1. **★主闸门**：b7e7 换源重提取三 cdl（mix←8f6da23d／drv1←fe2ff903／drv2←c9363888）+ `DUMMY_DEVICES` 台账 → 我判活 → 知会 fde9 预演 → 双门 → 我令点火。**不自点火。**
2. **mix schematic 补画 `QX5/QX6 gnd gnd gnd npn13G2 nx=3`**（mix LVS 的前置件，仍未到）。
3. drv1 标准输入对立项（件已备，见③⑥）。
4. `monitor_baseline.py` 补投（小账，8510 仍 404）。
5. fde9 判据器修订版（口径②+T1–T4）复核。
6. M4 v2 gen v2 件到后代跑 DRC + 全层 bbox 复核。

## 六、本口产出与动作
- 纪要本件 → 8510 `design/sow6/`（同名）。
- `run_lvs_v20_pass.sh` 默认输入对更新并复跑自证（`v24canon` PASS）。
- 回执 b7e7（裁定二十四 + 求件已投 + 两处订正）；管理员报备。
- 归档件：`run_v2/lvs/drv2_subckt_LVS输入_v5_b7e7.sp`、`drv1_subckt_LVS输入_v2_b7e7.sp`；
  跑法目录 `run_v2/lvs/deckfix_v1/out_drv2v20_{v5_bak,v5_v32,v24canon}/`。

—— b7a0 · WiFi7-TX-组长 · 2026-10-18T09:20Z
