# 判读纪要 · 裁定一百一十七 · 技能舰队 A2/A3/A4 backlog 清零 ＋ 三个 advisory 当场转正硬闸 ＋ 行为保全自证

- **时间**：2026-10-24 15:33–16:0xZ（UTC；本地 23:33–次日 0:0x）
- **范围**：我方**注册为一等工具的 33 件脚本**（技能舰队）＋ 我方自审器 `tools/skill_fleet_audit.py`
- **性质**：**只读现役面**——未改任何现役 GDS／网表／deck 字节；未产合并件；未建顶层 pin 层／顶层网表；未派工；未上传冷备；未执行 8510 钥轮换（待管理员裁）；未评估情形 B；未跑 Q3；M5 链件一概不动
- **外部输入**：无新管理员信（待决 ①–㉚ 全挂，末封仍 **26795**）；inbox 无新同伴信（末条仍 #332，15:29:30Z）；本口由 `early_wake(by=bell)` 唤醒（事实 32020）

---

## 〇、一句话结论

阶段 126 立的 **A5 覆盖完备性律**把舰队自审的「盲区」打开后，露出一个更隐蔽的问题：**A2/A3/A4 三条律当时只是 advisory**——实测 **A2 缺 3、A3 缺 8、A4 缺 5（共 16 项）**，而舰队自审报告照样写 **PASS**。这与 A5 同族：**盲区里的全绿不构成证据**。本口把 16 项**逐件整改**（共触及 **16 件**技能脚本 ＋ 审计器 1 件）、把 **A2/A3/A4 由 advisory 转正为硬闸**、并用**双向校准（1 正例 ＋ 7 负控）＋ 16 件逐件实跑的行为保全自证**证明「转正有牙、整改零回归」。

---

## 一、为什么做这件事（背景）

阶段 126 实测：旧版自审器花名册硬编码 27 项 vs 注册表现况 **33** 项 ⇒ 漏审 6 ⇒ 旧版「硬闸 27/27 PASS」是**假全绿**。立 A5 后花名册改为注册表派生，覆盖补齐，但**报告里仍留着 16 项 backlog 提醒**（A2=3／A3=8／A4=5），且这三项**不参与判定**——即：**整改未做、报告仍 PASS**。若就此收口，等于把「没查」写成「查过且合格」。故本口主动做整改 ＋ 转正。

**本口新增律（入 `playbook/BOOT_通用律库.md`）**

| 律 | 内容 | 由来 |
|---|---|---|
| ★★**整改转正律（A6）** | backlog 清零后**必须把该项转正为硬闸**；否则整改成果会退回「提醒」状态，自审照样判 PASS | 本口实测 |
| ★★**标准结论行律（A3 口径升级）** | 结论行必须是「**结论行**: 总项数 N ／ FAIL n」（**带前缀**）；判据由「源码含『总项数』与『FAIL』两词」升级为「源码含标准结论行字面量」 | 本口实测漏检 5 件 |
| ★★**闸套律（A2 ＋ A3 的统一实现）** | 异常兜底 ＋ 末行标准结论行，用**同一套闸套**实现（改写 `run` 为 `_run_core` ＋ 外层 `run(*args, **kw)` 兜底） | 本口整改 |
| ★★**路径可移植律（A4 转正）** | 源码内不得出现机器相关绝对路径字面量（如 `/tmp/…`）；改走 `tempfile`（**本机取值须与改前完全一致 ⇒ 语义零漂移**） | 本口整改 |
| ★★**静态判据不等于行为证据** | 源码里有关键词 ≠ 运行时真落了那一行 ⇒ 静态闸只能判「能不能」，**「落没落」必须实跑取证** | 本口实测（见 §四） |

---

## 二、实测缺口（整改前 · 逐件）

| 律 | 缺口 | 技能（括号内为根因） |
|---|---|---|
| A2 闸自身不崩（无 try/except 兜底） | **3** | `gate_hardening_selftest`、`m4_drc_attrib`、`p1_scope_map` |
| A3 报告完整性（无标准结论行） | **8** | `artifact_identity`、`m4_drc_attrib`、`m4_route_rework`、`m4_top_reconcile`、`p1_scope_map`、`p2_place_table`、`sg13g2_sim`、`webui_ctl` |
| A4 路径可移植（机器相关绝对路径字面量） | **5** | `artifact_identity`（`IDX_TMP='/tmp/…'`）、`g2_access_corridor`（`TMP='/tmp/g2_access_corridor/'`）、`g2b_via_stack`（`TMP='/tmp/g2b_via_stack/'`）、`peer_landing_accept`（缺件探针路径写死）、`peer_sandbox_repro`（`sbx="/tmp/peer_sbx_%d"`） |

去重后**唯一技能 14 个**、共 **16 项**缺口。

---

## 三、整改动作（两批 · 技能脚本 16 件 ＋ 审计器 1 件）

### 第一批（13 件）— `playbook/_evidence_stage127/patch_stage127.py`

1. **闸套（A2＋A3）** 9 件：`artifact_identity`、`m4_drc_attrib`、`m4_route_rework`、`m4_top_reconcile`、`p1_scope_map`、`p2_place_table`、`sg13g2_sim`、`webui_ctl`、`gate_hardening_selftest`
   - 实现：模块级 `def run(` → `def _run_core(`；在 `__main__` 块**之前**插入统一闸套（异常 ⇒ 结构化 FAIL ＋ 失败态落盘 ＋ 结论行；正常 ⇒ 末尾追加标准结论行）。
   - ★闸套**只追加、不改写**：既有输出行逐字节不变（见 §五实测）。
   - ★计数**取各工具真实字段**（`summary.n_checks/n_fail`、`checks` 清单、`exit_code`、`smoke` 坏页数等），**不臆造**。
   - `gate_hardening_selftest` 自带结论行 ⇒ 闸套**不重复打印**（`_GATE_CORE_HAS_CONCL=True`）。
2. **A4 字面量** 5 件：改为 `os.path.join(tempfile.gettempdir(), …)`；`peer_landing_accept` 的缺件探针改用沙箱内不存在路径（`os.path.join(sandbox, '__pla_missing_probe__.txt')`）⇒ 仍是「缺件」负控且不再写死机器路径。
   - ★**本机取值与改前完全一致**（`/tmp` ⇒ `tempfile.gettempdir()` 在本机同值）⇒ **语义零漂移**。

### 第二批（6 件）— `playbook/_evidence_stage127/patch_stage127_phase2.py`

★**A3 判据强化后才暴露的二次缺口**（这正是「静态词面判据不等于行为证据」的实证）：

- **5 件**源码里**根本没有标准结论行**（原判据因源码别处含「总项数」「FAIL」而误判合格）：`g2_access_corridor`、`g2b_via_stack`、`g2d_route_b_precheck`、`p4_pin_scope_pre`、`peer_fetch_verify` ⇒ 补闸套（末行落标准结论行）。
- **1 件**`peer_sandbox_repro` 自印「总项数 17 ／ FAIL 0」但**缺「结论行:」前缀** ⇒ 补前缀（标准形）；其**解析对端**输出的 `CONCL_RE` 不变（对端仍用旧形）。

### 审计器自身（`tools/skill_fleet_audit.py`）

- **A2/A3/A4 由 advisory 转正为硬闸**：`hard_ok = A1 ∧ A2 ∧ A3 ∧ A4`；`gaps_hard` 改按 `hard_ok` 计；报告口径与 note 同步改写。
- **A3 判据升级**：由「含『总项数』与『FAIL』」⇒「含**标准结论行**字面量」。
- **selftest 扩到 8 场景**：新增 **S6 无异常兜底(A2)**、**S7 无标准结论行(A3)**、**S8 机器相关路径字面量(A4)** 三个负控。
- ★**自指自证**：转正瞬间审计器**自己**被判 A4 不合规——因为新增的 S8 负控样例里写了 `"/tmp/x"` 字面量 ⇒ 改为**运行时拼接**（源码不落字面量、样例仍带字面量）⇒ 审计器自身零违规；**这条自指缺陷本身即「转正有牙」的证据**。

---

## 四、纪律（旧版留档 · 零回归护栏）

- ★★**改写活文件前先留档旧版（承阶段 126 律）**：本口共留档 **20 件**旧版于 `playbook/_archive/stage127/`（含审计器阶段 126 版 `fb74365b`／18,985 B——**该 sha 已被阶段 126 纪要与 summary 引用**⇒ 永久可解析）。
  - ★诚实记录：审计器在本口的**两个中间版本**（`a8d7ea89`、`08b0618e`）**未被任何文档引用**，其字节未留档。
- ★**路径零漂移**：`/tmp/…` ⇒ `tempfile.gettempdir()` 在本机**同值**；`peer_landing_accept` 探针路径由「机器绝对路径」改「沙箱内不存在路径」⇒ **负控语义不变**。
- ★**既有行逐字节不变**：闸套只**追加**末行；不改任何既有输出行的内容与次序。
  - ★例外一（有意的口径变更）：`peer_sandbox_repro` 的末行由「总项数 17 ／ FAIL 0」标准化为「**结论行:** 总项数 17 ／ FAIL 0」。
  - ★例外二（不动其行序）：`peer_landing_accept` 的结论行在**行内**而非末行——其下游解析器取「末行」（`last_nonempty_line`）⇒ **改行序会破坏契约**，故保留原位并在报告口径中标注。

---

## 五、自证结果（三层）

### 5.1 舰队自审（转正后）

```
判定: PASS  硬闸缺 0/33；覆盖完备性: 注册 33／审到 33／缺 0／多余 0；逐律缺口 A1=0 A2=0 A3=0 A4=0
结论行: 总项数 33 ／ FAIL 0
```

### 5.2 双向校准（selftest 8 场景 · **0 FAIL**）

| 场景 | 期望 | 实测 |
|---|---|---|
| S1 正例·注册表现况全覆盖 | PASS | PASS（33／33，硬闸缺 0） |
| S2 负控·历史硬编码花名册漏审 | FAIL | FAIL（漏审 6） |
| S3 负控·注册项脚本缺失 | FAIL | FAIL（硬闸缺 1） |
| S4 负控·注册 schema 与 run 不兼容 | FAIL | FAIL |
| S5 负控·注册表不可读不静默降级 | FAIL | FAIL |
| **S6 负控·闸无异常兜底(A2)** | FAIL | **FAIL**（A2 缺口 1） |
| **S7 负控·闸无标准结论行(A3)** | FAIL | **FAIL**（A3 缺口 1） |
| **S8 负控·机器相关路径字面量(A4)** | FAIL | **FAIL**（A4 缺口 1） |

临时目录残留＝**无**。

### 5.3 行为保全自证（16 件逐件实跑 · `behavior_equivalence.json`）

判据：① stdout 须含标准结论行「结论行: 总项数 N ／ FAIL n」且 FAIL ≤ 总项数；② **既有输出行逐字节不变**（与改前留档件同参数实跑逐行比对）；③ 无 traceback／无未捕获异常。

- **16／16** 落了标准结论行；**15／16** 既有行逐字节不变；
- 唯一差异件 `peer_sandbox_repro`：差异行仅两处——① **我方工作区件数**（28075 vs 28074，**两次运行之间的环境动态量**，非行为回归）；② 结论行**前缀标准化**（本次有意变更）。
- 计数诚实性抽样：`m4_drc_attrib` **17／0**、`m4_top_reconcile` **18／1**、`g2_access_corridor` **18／0**、`g2b_via_stack` **29／0**、`webui_ctl` **23／0**（23 页冒烟全通）、`gate_hardening_selftest` **40／4**、`p4_pin_scope_pre` **3／0**、`peer_fetch_verify` **2／0**（对端取件逐件对拍 0 不符）、`peer_sandbox_repro` **17／0**。

---

## 六、遗留与口径边界（诚实登记，均为**既有**事实，非本口引入）

1. `m4_top_reconcile` **FAIL 1**＝顶层基座仍内嵌**陈旧块版次**（mix v29／drv1 v20／drv2 v20）——与阶段 93/88 结论一致，**既有**。
2. `sg13g2_sim` **FAIL 1**＝本次实跑的 `t_min.sp` 仿真**非零退出**（工具如实报 FAIL；换网表即换计数）。
3. `gate_hardening_selftest` **FAIL 4**＝其「D/C1 正例」直接取**当前 `summary.md`** 作夹具，而上口 summary 的交付件表里 `tools/skill_fleet_audit.py`、`tools/peer_sandbox_repro.py` 两行 sha **已被本口改动**⇒ 交付件闸判 2 件不符 ⇒ 连带 4 项检查失败。
   ⇒ ★**本口收尾重写 `summary.md`（写入改后真实 sha）后，该闸回落**——收尾实测复跑确认（见下条）。
4. ★**「活文档型 golden 基线」过期 ⇒ 假警报（本口新发现并处置）**：重写 summary 后复跑，该闸仍报 **FAIL 1**，细项＝`D/C1 既有行逐字节不变`（`before_lines=12` vs `after_existing_lines=36`）。查因：该检查的基线 `verify/gate_hardening_109/before/delivery_gate.normal.txt` 是**阶段 109 捕获的 `delivery_gate` 对 `summary.md` 的输出**（当时交付件表 **9 行**）⇒ **`summary.md` 是活文件，一改行数基线必不等** ⇒ 属**夹具基线过期**，**非 delivery_gate 行为回归**（同口其余 D/C1 三项「verdict=PASS／结论行 FAIL=0／rc=0」均 PASS）。
   ⇒ ★**处置**：按「golden file 随活输入刷新」常规做法——**旧基线先留档**（`before/history/`，sha `c6aeb218`／2,011 B），再以当前 PASS 输出重捕获（**剔除末行结论行**，保持「补丁前输出形态」语义；v1 误含结论行亦留档）；并写 `before/README_refresh.md` 登记刷新缘由与sha。⇒ 复跑 **该闸 PASS 40／40**、交付件闸 PASS 33／33。
   ⇒ ★**登记为已知耦合**：该检查通过**依赖基线与 `summary.md` 同步**；日后 summary 交付件表增删行须同样刷新基线并追加说明，否则又会出现同型假警报（★宁可假警报也不静默放过，故保留 FAIL 呈现 ＋ 显式说明，不做「自动降级为 INFO」）。
4. 静态 A3 判据仍**只能判「能不能」**；「落没落」目前靠本口的行为保全自证覆盖 ⇒ ★**尚未**做成常设回归闸（候选：把 `smoke_stage127.py` 升为注册技能并在阶段收尾跑）。

---

## 七、我方交付件（本口产出 · sha8／bytes 本口现算）

| 件 | sha8 | bytes |
|---|---|---|
| ★**本件自身**（`phys/top/判读纪要_裁定一百一十七_…_2026-10-24.md`） | 自身 sha8/bytes **不写死**（循环引用）⇒ 见 `playbook/BOOT_交付物索引.md` 或 `artifact_identity whois` 现算 | — |
| `tools/skill_fleet_audit.py` | `b4f60ce2` | 23024 |
| `playbook/_evidence_stage127/patch_stage127.py` | `2bc5273d` | 11982 |
| `playbook/_evidence_stage127/patch_stage127_phase2.py` | `3a527503` | 5968 |
| `playbook/_evidence_stage127/smoke_stage127.py` | `3168738b` | 9386 |
| `playbook/_evidence_stage127/patch_applied.json` | `a2d04600` | 8073 |
| `playbook/_evidence_stage127/patch_applied_phase2.json` | `fb0a90db` | 3484 |
| `playbook/_evidence_stage127/skill_fleet_audit_final.json` | `f193e8b7` | 17598 |
| `playbook/_evidence_stage127/skill_fleet_audit_selftest.json` | `696378c6` | 1564 |
| `playbook/_evidence_stage127/behavior_equivalence.json` | `e0807431` | `11234` |
| `playbook/_evidence_stage127/delivery_gate_summary_stage126.json` | `157e1c32` | 4072 |

★被改的 16 件技能脚本（＋审计器 1 件）逐件 sha8／bytes 见 `playbook/_evidence_stage127/patch_applied.json` 与 `patch_applied_phase2.json`；旧版留档 20 件见 `playbook/_archive/stage127/`。

## 八、组员产出（非我方交付件 · 仅引用，不列入上表）
- **fde9**（`sow6/m5/`，本口只按名 GET，未改其任何字节）：#330／#331／#332 三信已闭环（面 A 3/3 内容级闭环、收信端上限 v1.3＝262,144 字符＋队列预算 64 MiB、ck05 双方同口径、v3 维持不出、8510 file-key 继续停用不索取新钥）。
- **b7e7**：在途 ④cdl `_SCHEMATIC_PREFERRED` 层次名塌缩（等情形 B，不催）。

---

## 九、下一步（未获授权不动手）

1. **管理员待决 ①–㉚** 到即按 `phys/top/决策就绪包_待决①–㉚_2026-10-24.md` §0 速览表逐号销账（末封仍 26795）；**㉕ 已具备 A/B 双腿证据可直接裁**（我方建议 A：顶层自建 via 栈）。
2. ★**8510 file-key 轮换**仍待管理员裁示（我方未动手；对方已确认继续停用、不索取新钥）。
3. 收尾自洽性检查：重写 `summary.md` 后复跑 `gate_hardening_selftest`（期望 40／0）与 `delivery_gate`（期望 PASS）。
4. 可选（只读、无需授权）：把 `smoke_stage127.py` 升为注册技能（行为保全回归闸），使「落没落」常态化；并把 A3 静态判据再收紧为「print 语句含标准结论行」。
