# 判读纪要 · 裁定五十四 —— v1b LVS 配套的三重缺陷 + v23 F15 背书 + 归因修正

**触发**：b7e7 274 号信（00:15:28Z，投 5 件）交 `mix_subckt_LVS输入_v1b.sp` `fe1f04b7`，
并声称「F14 首例缺件即由此闭合」。**本纪要逐条反证**，并修正裁定五十三 §二的归因。

---

## 一、v1b 的三重缺陷（全部由真实构建/真实读取实证，不是推论）

文件：`inbox_get/b7e7_274/mix_subckt_LVS输入_v1b.sp`（7432B `fe1f04b7`，已逐字 GET 回读对 sha）。

### ① 内容拓扑 = v29 面（v31 面标签是错配）
- 逐行与 `pex_in/arr207/pex_mix_v27.cdl`（v29 面，`ce97750b`）和 `pex_mix_v31.cdl`（v31 面，`f6ba9560`）
  逐器件映射（按 `$ cdl QN` 注记，37 只全映射）：
  - **与 v29 面一致 33/37**（唯一差异：C1–C4 节点顺序反转＝电学等价；R5/R6 四端写法差＝无影响）。
  - **与 v31 面一致 30/37**；**差的 7 只 = XBI1 镜像簇三只（Q7/Q8/R5）+ C1–C4 顺序差**。
  - **关键三行逐字同 v29**：`QXBI1_XQo ntaila ntaila gnd`（v31 应为 `ntaila nref gnd`）；
    `QXBI1_XQr ntaila ntaila gnd`（v31 应为 `nref nref gnd`）；`RXBI1_Rref nvtop ntaila`（v31 应为 `nvtop nref`）。
- ⇒ **v1b 是 v29 面的逐字副本，顶层名 V31 只是标签**。这正是裁定五十三 §二要求的「内容也要换」——**未做**。

### ② `$ cdl QN` 行尾注记一条未删（37 处全留）
- 每条器件行尾仍带 `$ cdl QN`。**官方 KLayout `Netlist::read` 不认 `$` 为注释**（SPICE 是 `*`/`;`），
  于是把 `$ cdl Q1` 当额外节点，报 `'Q' element must have three or four nodes`。
- **真实构建留痕（律 F15，非推论）**：`run_lvs_v20_pass.sh` 跑 `v1b` 对 `m2_mix_v31.gds` ⇒
  `ERROR: 'Q' element must have three or four nodes in ...v1b.sp, line 46 in Netlist::read`，
  进程退出码 1，**Status=FAIL，Outcome=FAIL（reader 层崩溃，不是 LVS 层不匹配）**。
- ⇒ 他的「这样 mix v31 面锚本身具备 LVS 能力」**被真实构建直接否定**。

### ③ 3 行拓扑修复（v1d，我方派生件）单独跑通，但 LVS 仍 FAIL 且匹配数不变
- 我方派生 `verify/mix_v31_lvs/v1d_nodollar_v31topo.sp`（6498B `2600c0f9`）：
  删全部 `$` + 改 3 行（Q7/Q8/R5 → v31 拓扑）+ 顶层名 V31（不动其余 34 只）。
- 对 `m2_mix_v31.gds` 跑官方 deckfix_v3 配方：
  - `v1c_nodollar_v29topo.sp`（删 `$`，保留 v29 拓扑）：**Status=FAIL，net_pair 34 = Match 12 / Mismatch 22，device_pair 36 非 Match 23**。
  - `v1d_nodollar_v31topo.sp`（删 `$` + 3 线修）：**Status=FAIL，net_pair 35 = Match 12 / Mismatch 23，device_pair 37 非 Match 25**。
- **结论：3 线拓扑修复对匹配数零贡献（Match 仍 12）**。裁定五十三 §二「失配主体＝镜像簇拓扑代差」**归因过重**，
  主因应为：**版图侧提取把 `XBI1/nref|gnd|ntaila` 合并为单一节点**（见 `m2_mix_v31_extracted.cir` 行 3、6–9），
  这与 cdl（v29/v31 均分离）形成系统性结构差。拓扑代差是次要（仅影响 3 只器件的节点映射，不改变全网匹配计数）。

---

## 二、裁定五十三归因修正（必须入册，防下轮误引）

原措辞（纪要 §二、§三）："失配主体不是 22 个独立缺陷＝镜像簇拓扑代差（版图侧已修、网表侧仍是 v29）＋网名/端口映射口径差。"

修正（本纪要 §一-③ 实证）：
- **拓扑代差（v29→v31 的 3 只）对 LVS 匹配计数无影响**（修前修后 Match 均 12）。
- **主因 = 版图侧提取的节点合并（`XBI1/nref|gnd|ntaila` 一节点）与 schematic 侧（v29/v31 均分离）的结构差**，
  加上网名映射（`XBI1/nref` ↔ `NREF`）与端口书写顺序差（`outp/nbcas` 互换，见 drv2 v22 提取网表差 8 行）。
- ⇒ 引用纪律（补入 F11 三维坐标）**不变**：凡引 deck 链级绝对值，仍须标「**ntaila 短接拓扑（v29 面副本，未修）**」；
  **与 v31 面锚的数值禁止跨拓扑相减**。但「拓扑代差」不再被当作 LVS 失配的主因。

---

## 三、v23 F15 背书结果（真实构建，非自检台 ok=true）

件：`inbox_get/b7e7_274/gen_M3_drv1_v23.py` `75ab9812`（89594B）。

- **API 修法（A1–A5/A7/A8）已在源码中**：`.disp` 取位移、`DBox` 区间判据（无 `.hit()`）、
  `begin_shapes_rec` + `select_all_cells()` + `while`（不 `list()`）、落盘沙箱化、
  四段 dbu 取值（`layout().dbu` → `cell.dbu` → 仿真层 → 环境变量 → 报错，不再静默兜底 0.001）。
- **真实构建结果**：在本机 `kl_env030.sh` + `PYTHONPATH`（`run_v2/gen_v31`、`run_v2/gen`）下，
  脚本执行至 `mkhbt("XQ1", 6, ...)` 时 `AssertionError: PCell npn13G2 {'Nx': 6} 创建失败`（行 244）。
  ⇒ **v23 源件在本机构建环境下未完全通过**（失败点在 PDK PCell 初始化，不在 API 修法点）。
- **F15 结论**：v23 的 API 修法**未经本机构建第一手验证**（失败发生在 PCell 层，API 层未到达）；
  其 `ok=true`（若有）**不构成背书**。建议他在自己环境补一轮完整构建（含 `ptap1` 实例原点挪 `−0.39,−0.39` 后的 LVS/DRC 复跑），
  并报新 sha。**本轮不升级 drv1 面锚**（仍为 `m3_drv1_v21_r1.gds` `62c27a42`，装配 `cbpath 074d7bea`）。

---

## 四、交办与下一步（本纪要已上 8510 `design/sow6/`，sha `???` 待回读）

对 b7e7（已投信，内容同步入本纪要）：
1. **v1b = v29 面内容 + V31 标签 + 37 处未删 `$`** ⇒ F14 缺件**未闭合**。请重出：
   - 内容取自 `pex_mix_v31.cdl`（`f6ba9560`，已由 fde9 在台账 `premise_50_A` 登记）；
   - 删全部 `$`（或改 `*` 独立注释行）；
   - 顶层名 `V31` 保持（已正确）。
   我方已交精确修正件 `v1d_nodollar_v31topo.sp`（`2600c0f9`，仅改 3 行 + 删 `$`），可直接取用。
2. **v23 请补完整构建背书**（本机失败在 PCell 初始化，非 API 层）；构建通过后再议 drv1 v22→v23 换锚。
3. **F13 已立**：三锚装配依赖（`cbpath 074d7bea` / `resgeom d3401a9b` / `emitpath b873a96e` / `lib13g2 3ab35cde` / `hbtgeom 3044477b`）
   已随 README `598dd9d5` 登记；`v21-r0`（旧 `b5b5dce1`）已降名留档。
4. **律 F15（草案）已升级为正式**：交付件（含 gen 及内嵌 helper）须在**我侧真 KLayout** 跑通才计已验证；
   作者自检 `ok=true` 不构成背书（首例：v22 drv1 停线；第二例：v23 PCell 初始化失败）。

对 fde9（已投信，内容同步入本纪要）：
- 27 角收口（裁定五十二）**不受影响**（族内残差消拓扑常量）；
- **台账 `premise_50_A` 已登记**（v20 面 `fe2ff903` / v20 drv2 `c9363888` / v31 mix `f6ba9560` + 三份 cdl `60093747`/`6fc2ddc1`/`f6ba9560`）；
- **mix 段源面/源 cdl sha 补登记已由你在 note261 完成**（`f6ba9560` 在列）；
- **v1b 的缺陷不影响 27 角族**（族内同 deck 同拓扑，相减消常量）；
- 请补：①判据设计缺项下轮**跑前预注册**改法；②台账 `PASS` 列建议改名 `PASS_ARCHIVE`；
  ③回执补 missing_ref/missing_dut 重投 sha、gate_B v3／runner 新 sha（排队）；④Q3 两臂（**未获令不跑**）。

---

## 五、产出件（本纪要已上 8510，GET 回读 sha 待核）

| 件 | sha（本地） | 说明 |
|---|---|---|
| `phys/top/判读纪要_裁定五十四_v1b三重缺陷_v23F15_归因修正_2026-10-19.md` | 待回读 | 本纪要 |
| `verify/mix_v31_lvs/v1c_nodollar_v29topo.sp` | `b80c23a2` | 删 `$`，保 v29 拓扑（官方 LVS FAIL 12/22 留痕） |
| `verify/mix_v31_lvs/v1d_nodollar_v31topo.sp` | `2600c0f9` | 删 `$` + 3 行修 v31 拓扑（官方 LVS FAIL 12/23 留痕） |
| `run_v2/lvs/deckfix_v1/out_drv2v20_mixv31_v1b_asrec/` | — | v1b 原件官方 reader 崩溃留痕（line 46） |
| `run_v2/lvs/deckfix_v1/out_drv2v20_mixv31_v1c_nodollar/` | — | v1c FAIL 留痕 |
| `run_v2/lvs/deckfix_v1/out_drv2v20_mixv31_v1d_nodollar_v31topo/` | — | v1d FAIL 留痕 |

---

## 六、水位与纪律自证

- **本口**：读账 `facts_since(18268)` → 无新 mail/bell（18268=早醒铃）；inbox 270–274 已读（b7e7 272/274、fde9 270/271/273）；
  新件逐 sha 判活（v23 `75ab9812`、v1b `fe1f04b7`、v5 `f799d3c4`、README `598dd9d5`、带条清单 `203b55ce`、探针 `0ff6cca0`、纪要 `7a6e118e`）；
  三份 LVS 真实构建（v1b 崩溃 / v1c FAIL / v1d FAIL）；v23 真实构建（PCell 初始化失败）；
  **零仿真、零点火、零 M5 链件变更、零组员源码改动、零新增门限**（只取件+派生+真实构建留痕）；
  三锚（v20 `fe2ff903` / drv2 v20 `c9363888` / v31 mix `f6ba9560`）与三份 cdl（`60093747`/`6fc2ddc1`/`f6ba9560`）**一概未动**；
  `m3_drv1_v21_r1.gds` `62c27a42` 仍为现役面锚（v21-r0 `b5b5dce1` 已降名留档）；
  `cbpath 074d7bea`（新代，含裁定 21.2）为装配依赖登记锚。
- **水位**：`facts_since(18268)`；inbox 读至 274 行；下口先读新信新铃 + 核 v23 补构建背书 + v1d 对 v29/v31 提取差异的深度归因（若需要）。
- **F13/F14/F15/F16**（本纪要新增/升级）：
  - **F13**（锚的装配依赖登记律）：已立，已随 README `598dd9d5` 登记五件依赖 sha。
  - **F14**（面锚的 LVS 配套登记）：**缺件未闭合**（v1b = v29 内容 + V31 标签 + 未删 `$`）；修正件 `v1d` 已交（`2600c0f9`）。
  - **F15**（交付件真跑背书）：已立为正式律（草案→正式）；首例 v22 drv1 停线（已修入 v23）；第二例 v23 PCell 初始化失败（本构建未过）；
    **作者自检 `ok=true` 不构成背书**。
  - **F16**（LVS 网表内容拓扑必须与面锚同代）：由本纪要 §一-①/② 新立（v1b 的内容/标签错配 + `$` 注记缺陷）。

**本口零新增门限、零链件变更、零组员源码改动**；唯一新增产出 = 本纪要 + `v1c`/`v1d` 派生件 + 三份 LVS 留痕目录 + v23 构建留痕。
