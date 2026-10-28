# 判读纪要 · 裁定一百五十六 · **探针「EFFECT」假绿取证 ＋ 四处仪器缺陷**

- **阶段**：166（取证完成 · **整改尚未执行**）｜**时点**：2026-10-25 UTC 21:0xZ（本地 2026-10-26 05:0x）
- **性质**：仪器/判据面 · 只读现役面 · **零芯片动作**（未改任何现役 GDS／网表／deck 字节 · 未产合并件 · 未建 pin 层 · 未派工 · 未评估情形 B · 未跑 Q3 · M5 链件未动 · **未重启任何常驻服务**）
- ★**本口零仪器字节变化**（`tools/` 目录零写入）⇒ 阶段 165 批次的仪器记录（probe `d8ef438d`／census `c7ad815a`／oracle `133b5499`／registry `078b4df5`）**仍然现役** ⇒ 本口不使阶段 165 批次作废。

---

## 一、F1（★最重）探针差分腿「EFFECT」判据存在**假绿**

### 1.1 机理（`tools/skill_param_probe.py` 差分腿）

- 判定链：`nb_a, nb_b = norm_blob(cap0), norm_blob(cap1)`（`norm_text` 只把**被测参数值**替换为 `<S>`）；判定顺序为
  **`nb_a != nb_b ⇒ EFFECT`**（「归一化后仍有差异」⇒ 该参数真被使用）→ `rb_a != rb_b ⇒ ECHO_ONLY`（仅探针值位置不同）。
- `norm_text` **只**归一化被测参数值，**不**归一化**探针自身的内生标记**：沙箱目录名（`/tmp/a1sweep_<rand>/run0|run1/`）与输出文件名标记（`__A1PROBE__out_json__A.json` vs `__A1PROBE__out_json__B__LONGER.json`）。
- ⇒ 凡工具在 stdout 里**打印自己的输出路径**，两跑归一化后**必然**仍有差异 ⇒ **无论被测参数是否真被使用，一律判 EFFECT** ⇒ **死参数被判「真被使用」＝假绿**。

### 1.2 实测负控（本口实测；夹具写在 /tmp，一次性，跑完即删，**未入 `tools/`** ⇒ 零仪器字节变化）

| 夹具 | 工具行为（两夹具**仅差这一行**） | 死参数 `ghost`（读入但**从不使用**）判据 |
|---|---|---|
| A `nc_noprint` | **不**打印输出路径 | **NO_EFFECT**（不可判，不计 FAIL）✔ 合律 |
| B `nc_print` | **打印**输出路径（`证据落盘: <path>`） | **EFFECT**（判「真被使用」）✘ **假绿** |

⇒ **同一个死参数、两夹具判据相反** ⇒ 证明 EFFECT 档在该通道上**不携带信息**。

### 1.3 波及面

- 舰队内「stdout 打印自身输出路径」的工具（5 件）：`stage164_boot_snapshot_audit`（`证据: <path>`）、`m4_top_reconcile`、`merge_fingerprint`、`g2c_supplement_precheck`、`p4_lvs_leg`。
- 实例（阶段 165 wave A 实测）：`stage164.mode` 判 **EFFECT**，但差异由探针标记（`..._A.json` vs `..._B__LONGER.json`）造成 ⇒ **不可作「mode 真被使用」的证据**。
- ★**不受影响者**：**OUT_NOT_LANDED 档**（输出路径型参数未落地 ⇒ **正证据**判据，与差分无关）⇒ 阶段 165 靠它抓到的「失败路径不落证据」缺陷**结论成立**；**NO_EFFECT／CONSUMED_REJECTED 档**（不可判、不计 FAIL）亦不受影响。

### 1.4 修法（下一口执行）

1. `norm_blob`／`raw_blob` 的归一化集合追加**探针内生标记**：`__A1PROBE__*` 文件名 → `<M>`；`/tmp/a1sweep_*/run[01]/` → `<D>/`。
2. 差分腿**优先采用域内合法对**（R9 枚举对 `check`／`selftest`）；ALD 的「脚本路径常量兜底对」降级为**域外哨兵**（塌缩 ⇒ 不可判，不参与 EFFECT 判定）。
3. **负控（新）**：夹具 B 的死参数**不得**再判 EFFECT（须 NO_EFFECT／ECHO_ONLY）；**正控**：真被读取并影响输出的参数仍须判 EFFECT 或 ECHO_ONLY（不得漏判）。

★修法动 `tools/skill_param_probe.py` ⇒ **仪器字节变化** ⇒ 阶段 165 批次作废 ⇒ 整改后须起**阶段 166 批次**（★修仪器必批次级复跑律）。

---

## 二、F2 stage162 的 CLI 缺 `--mode`（与 stage163／164 不同构）

- stage163／164：`--mode` with `choices=['check','selftest']`；**stage162 只有 `--self-test` 旗标**，而注册 schema 声明 `mode`。
- 后果：①CLI 与 schema 不同构；②探针的 R9 枚举对**发现不到** ⇒ ALD 只能回落到**脚本路径常量**（`/data/data/facts.db`／`/data/data/events.jsonl`＝**域外值**）⇒ 两跑同路径 ⇒ 判 NO_EFFECT「不可判」⇒ **该参数永远不可判**（非死参数，但判不出）。
- 修法：stage162 增 `--mode`（`choices=['check','selftest']`，default='check'），`--self-test` **保留为别名**（不破既有调用）。

---

## 三、F3 批次收口闸的仪器覆盖有**两处空洞**

- **3a**：`parse_instrument` 只认 `("probe","oracle","registry")` ⇒ `instrument_version.txt` 里记的 **`census`（`fleet_hygiene_census.py`，`c7ad815a`）不被任何判据校验**；G2 只校 probe+oracle，registry 由 G3 校 ⇒ **census 仪器字节漂移无人发现**（而 census 是每批**必跑面**）。
- **3b**：本批新增登记的**三件工具本体字节**不在批次仪器清单内 ⇒ 跑批期间若有人改其字节，本批**检不出来** ⇒ 批次对这三件的覆盖**不可自证**。
- 修法：①`parse_instrument` 放开键白名单并支持「key sha path」三列格式；②G2 改为**逐条**校验仪器清单每条记录的路径↔现算 sha；③跑批器把**本批新增／改动的登记工具本体 sha** 写进仪器清单。

---

## 四、F4 `run()` 返回形状不统一 ⇒ 探针「判定翻转律」对 stage164 失明

- stage163 `run()` 返回含 verdict 的 dict（`return res`）；**stage164 `run()` 返回 int**（`_do_check(...)` 的计数）⇒ 探针 `_verdict_of` 取不到 verdict ⇒ `verdict_flip` 恒 False ⇒ **「两跑判定翻转」这条最强判据对 stage164 不生效**。
- 修法：三件统一 `run()` 返回 dict（含 `verdict` 键）。

---

## 五、本口实测基线（现算，2026-10-25T21:0xZ）

- 现役四件 sha8／字节 **逐位未变**：mix `396571f0`/96660、drv1 `d5e1296c`/63502、drv2 `25adcbd1`/79564、顶层 `88d5d9c4`/237672。
- stage164 自查当前读数：11 判据 **FAIL 2**（K8 批次快照腿：阶段 159 批 registry 记录 `43ef851a` ≠ 现算 `078b4df5`；K11 正例腿随之 FAIL）⇒ **如实信号**（阶段 165 批次收口后自动转 PASS）。
- **阶段 165 批次进度**：20:25:08Z 起跑；wave A_light rc=0（20:30:42Z；28 技能扫掠，42 残余项，已判 39／不可判 3／FAIL 0）；wave B_heavy 进行中（9 件长时）；仪器记录 probe `d8ef438d`／census `c7ad815a`／oracle `133b5499`／registry `078b4df5`（与现算一致 ⇒ **G2／G3 预期 PASS**）。
- 本口零网络调用、零凭据取用；对端件零 GET；未索取任何 file-key。

---

## 六、下口动作（次序固定）

1. 等阶段 165 批次**完工铃** ⇒ 跑 `batch_rerun_gate --mode check`（**G3 应转 PASS**）＋ 核终局洁净（孤儿 0／残留 0／族外新增 0／四件 ZERO_DELTA）⇒ 回填阶段 165 纪要。
2. 执行 **F1–F4 整改**（**改仪器字节**）⇒ 按 ★修仪器必批次级复跑律 起**阶段 166 批次**（仪器清单含三件工具本体 sha）⇒ 负控重跑。
3. 阶段 166 批次收口 ⇒ `batch_rerun_gate --mode check` ⇒ stage164 自查应转 **FAIL 0**。
4. 待管理员裁项（①–㉚／8510 取件钥轮换／两项清理令／keep-alive 上生产）**继续不动**。
