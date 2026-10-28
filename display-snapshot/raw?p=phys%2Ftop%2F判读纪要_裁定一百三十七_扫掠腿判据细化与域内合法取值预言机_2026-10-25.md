# 判读纪要 · 裁定一百三十七 · 扫掠腿判据细化 ＋ 域内合法取值预言机（阶段 147）

- 阶段：**147**（只读现役面 · 零芯片动作）｜时间：2026-10-25 UTC 05:26–05:40（本地 13:26–13:40）
- 上游：阶段 144 批次收口 ＋ 阶段 146 四修（探针 P1–P4 ＋ `a1_legal_domain`）
- 性质：★**只改我方自有工具**（探针 ＋ 新模块 ＋ 硬化自检白名单）；**未改任何现役 GDS／网表／deck 字节**；未产合并件；未建 pin 层；未派工
- 现役四件本口现算，逐位未变：mix `396571f0`/96,660｜drv1 `d5e1296c`/63,502｜drv2 `25adcbd1`/79,564｜顶层 `88d5d9c4`/237,672

---

## 〇、五句话

1. **缘起**：阶段 146 收口后，扫掠腿在轻件 5 技能／10 项上还剩 **5 项不可判**，根因逐条定域为四类：① 域不是枚举而是**格式**（`versions`＝`letter=sha8`）；② 参数**只在兄弟守卫分支内**被消费（`tool` 仅在 `mode=='probe'` 下生效）；③ **路径型**参数缺「第二合法值」（`registry`）；④ 兄弟参数缺**域内合法基线**（`netlist`／`chain`／`live`）；外加 **★波 B 孤儿面自相矛盾**（同一 pid 既记 killed 又记 unattributed）。
2. **本口做了一件事**：给差分扫掠腿补上**域内合法取值预言机**（新模块 `tools/a1_domain_oracle.py`，纯静态解析，不执行技能），并**细化判据**（把「早退＝verdict=FAIL」拆成「早退＝被拒绝」与「判定不合格」两义）。
3. **效果（轻件 5 技能／10 项，实测）**：**已判 5 → 8**；**不可判 5 → 2**；**UNOBSERVABLE 3 → 0**；**INCONCLUSIVE_ERROR 1 → 0**；FAIL 恒 0。
4. **剩余 2 项不可判是「诚实结论」而非工具缺陷**：`sg13g2_sim.timeout`（观测面内无效应）｜`chain64_residue_check.versions`（★域单点：当前兄弟基线下只有一个合法取值 ⇒ 差分不可构造）。
5. **★同时修掉一个假绿隐患**：阶段 146 的判据会把**同值对**（两跑输入完全相同）下的输出差异当成 EFFECT —— 实测命中（`service_liveness_gate.mode` 两跑同值却报 EFFECT，差异其实来自时间戳）⇒ 本口立 **★同值对不判效应律**，新增判据 `NON_DETERMINISTIC`。

---

## 一、判据细化（探针 `tools/skill_param_probe.py`）

### 1.1 ★把「早退」一分为二（阶段 146 的 P4 判据在本阶段被推翻）

阶段 146 把「顶层 `error` 非空」与「`verdict=FAIL` 且 `n_fail`」都算早退。**实测这两义截然不同**：

| 情形 | 含义 | 参数使用点 | 正确判据 |
|---|---|---|---|
| 顶层 `error` 非空 | 工具**没干活**（必填缺失／前置校验失败） | 未到达 | 早退 ⇒ UNOBSERVABLE（两跑都被拒时） |
| `verdict=FAIL` 且 `n_fail` | 工具**干了活**并判不合格（阈值型参数改值） | **已到达** | 判定翻转 ⇒ EFFECT |

阈值型参数（如 `chain64.verifier_items`：39 过、40 不过）被阶段 146 的判据**结构性判成「不可观测」** ⇒ 差分腿对它失明。本口拆开：

- 两跑**都被拒**（`error` 非空）⇒ `UNOBSERVABLE`（真早退）
- **一跑被拒、一跑通过** ⇒ `CONSUMED_REJECTED`（取值本身决定是否被接受；★★无效值塌缩律）
- 两跑都跑了、**verdict 一翻一没** ⇒ `EFFECT`（★判定翻转律：参数真被使用）

### 1.2 ★同值对不判效应律（新增判据 `NON_DETERMINISTIC`）

域单点参数（合法取值只有一个）只能构造**同值对**（两跑输入完全相同）。此时若输出有差异，差异只能来自**非确定性**（时间戳／并发序／浮点抖动），**不可能**是参数效应 ⇒ 本口新增判据 `NON_DETERMINISTIC`（不可判、不计 FAIL），并在覆盖统计里单列计数键 `non_deterministic`。
（实测命中：修复前 `service_liveness_gate.mode` 同值对却报 EFFECT。）

### 1.3 ★孤儿归属判据与报告同源（裁定一百三十七 补项）

阶段 144 波 B 实测抓到**自相矛盾**：pid 450775/450776 **既**被记进 `killed`（作为 scratch 归属根的子树被杀）**又**被记进 `unattributed`（因自身 cmd/cwd 无 scratch token ⇒ 走「无归属只报不杀」分支）。
根因：**杀与报的归属判据不同源** —— 杀用「祖先归属（子树）」，报用「自身 cmd/cwd token」。
本口统一为同一条判据：归属成立 ⇔（自身 token）∨（祖先链上任一 token）；已被处置的 pid 直接跳过；并在报告里新增 `contradictory_pids` 键做**同源自检**（自相矛盾即列出）。

---

## 二、域内合法取值预言机（新模块 `tools/a1_domain_oracle.py`）

**只做静态解析**（源码 ast ＋ 注册表描述），**不执行技能**、不写现役面。自检 **6/6 PASS**。

| 规则 | 内容 | 实证命中 |
|---|---|---|
| R1 内建默认 | 任一函数形参同名且默认值非 None | `chain64.verifier_items`＝39（藏在 `_run_inner` 里，注册入口 `run(**kw)` 掩盖） |
| R1b 动态取用默认 | `kw.get("x", 字面量)` | `sg13g2_sim.timeout`＝120 |
| R2 argparse 默认 | `--x` 的 `default=`（含 `os.path.join` 常量求值） | `chain64.chain/live/prev`＝三条真实台账路径（**现存**） |
| R3 模块常量 | 常量名归一化等于参数名（`DEFAULT_` 前缀可省） | 同上（另一条路径） |
| R4 描述引用目录／路径 | 「相对 <dir>/」「默认 <path>」⇒ 取**现存**实体 | `sg13g2_sim.netlist`＝`tb_gummel.sp`；`skill_fleet_audit.registry`＝`/data/data/skills.json` |
| R5 描述示例路径 | 「如 <path>」⇒ 该示例即合法值 | `peer_landing_accept.tool`＝`sow6/m5/ref_sha_audit.py` |
| R6 格式模板自举 | 源码 `X={sha8(<sib>)}` 形态 ⇒ 用兄弟基线的 sha8 现算 | `chain64.versions`＝`G=c2cae2b3,H=3d5b5f42`（与脚本自身默认逐位相同） |
| R7 兄弟依赖守卫 | `if <sib> == "<val>"` 守卫块内使用被测参数 ⇒ 跑它须把 `<sib>` 设为该值 | `peer_landing_accept.tool` ⇒ 强制 `mode='probe'`（否则跑的是 accept 分支，参数使用点根本不到达） |

★**探针侧接线**（`tools/skill_param_probe.py`）：
① `_legal_baseline` 改为**预言机优先**（旧路径只看注册入口形参，取不到藏在内部函数的默认值）；
② `_build_probe_kw` 新增 **R7 兄弟配对**（被测参数的守卫兄弟被强制赋值）；
③ `_sweep_pairs` 的配对顺序改为：**输出型沙箱对 → 预言机非退化对 → ALD 域内对 → ALD 轮转相邻对 → 域外哨兵对 → 预言机退化（同值）对**；
④ ALD 固定「首值 × 其余」配对，首值分支需额外兄弟参数时三对全废（实测 `accept` 模式须给 `receipt_md` ⇒ SystemExit）⇒ 补**轮转相邻对**（枚举值两两旋转）。

---

## 三、效果实测（轻件 5 技能／10 项，同一注册表同一批参数）

| 指标 | 阶段 146（打补丁后） | **阶段 147（本口）** |
|---|---|---|
| 已判 | 5 | **8** |
| 不可判 | 5 | **2** |
| UNOBSERVABLE | 3 | **0** |
| INCONCLUSIVE_ERROR | 1 | **0** |
| FAIL | 0 | **0** |

逐项（不可判 5 → 2）：

| 参数 | 阶段 146 | 阶段 147 | 根因/处置 |
|---|---|---|---|
| `sg13g2_sim.timeout` | UNOBSERVABLE | NO_EFFECT | 兄弟 `netlist` 缺合法基线（早退）⇒ R4 取 `tb_gummel.sp`；取值 120/121 不改变输出 ⇒ 观测面内无效应（诚实结论） |
| `chain64.verifier_items` | UNOBSERVABLE | **EFFECT** | 阈值型：判定翻转 ⇒ ★判定翻转律 |
| `chain64.versions` | INCONCLUSIVE_ERROR | NO_EFFECT（★域单点） | R6 格式模板自举 ⇒ 不再抛异常；域单点 ⇒ 差分不可构造（诚实结论） |
| `skill_fleet_audit.registry` | UNOBSERVABLE | ECHO_ONLY（INFO） | R4 取真实注册表路径；R7 路径同内容副本对 ⇒ 两跑都合法 |
| `peer_landing_accept.tool` | NO_EFFECT | ECHO_ONLY（INFO） | R7 守卫 ⇒ 强制 `mode='probe'`（参数使用点到达）＋ R5 示例值 |
| `peer_landing_accept.mode` | EFFECT | EFFECT | ALD 轮转相邻对（`accept` 支路需 `receipt_md` ⇒ SystemExit 已避开） |
| `skill_fleet_audit.json_out/.selftest`、`service_liveness_gate.json_out/mode` | EFFECT | EFFECT | 保持（`mode` 因同值对规则改走 ALD 对） |

---

## 四、自检（本口实跑）

| 自检 | 结果 | 备注 |
|---|---|---|
| 探针 selftest（`tools/skill_param_probe.py selftest`） | **16/16 PASS** | 13 项旧用例逐字节保持＋**新增 3 项正例**：判定翻转⇒EFFECT、一跑被拒⇒CONSUMED_REJECTED、预言机兄弟基线⇒EFFECT |
| 阶段 137 硬化自检（`tools/stage137_hardening_selftest.py`） | **14/14 PASS** | 新增覆盖键 `non_deterministic` 已入**新增键白名单**（旧键逐位不变断言仍生效） |
| 预言机自检（`python tools/a1_domain_oracle.py`） | **6/6 PASS** | 正例 4（内建默认／模块常量／格式模板／守卫检出）＋负控 2（无解返回 None／守卫不误报） |
| 探针 inventory（静态全量） | 38 技能／131 参数／**FAIL 0** | 腿T 覆盖：可判 75／不可判 41／未涉及 15（与阶段 146 同口径） |

---

## 五、本口新立律（并入 `playbook/BOOT_通用律库.md`）

1. ★**判定翻转律**：差分腿两跑都真跑到正常路径、仅 `verdict` 一翻一没 ⇒ 判 **EFFECT**（阈值型参数可判）；`verdict=FAIL` **不等于**早退，早退只认「顶层 `error` 非空」。
2. ★**同值对不判效应律**：同值对（两跑输入完全相同）下的输出差异 ⇒ 判 `NON_DETERMINISTIC`（非确定性），**不得**判 EFFECT。
3. ★**域单点不可判律**：参数在当前兄弟基线下只有一个合法取值 ⇒ 差分不可构造 ⇒ 记「不可判（域单点）」，不判死、不判活。
4. ★**域内合法取值预言机律**：差分腿取兄弟/被测参数取值时，必须优先走**预言机**（静态派生域内合法值），取不到才回落域外哨兵；取不到域内合法值而早退的项，**不得**据此判死参数。
5. ★**兄弟依赖守卫律**：被测参数只在兄弟守卫分支内被消费时，**必须**把兄弟设成该守卫值，否则差分观测的不是参数使用点。
6. ★**归属判据与报告同源律**：同一判据必须同时用于「处置」与「报告」；同一实体不得在两张表里同时出现（自相矛盾即报出）。

---

## 六、边界与遗留

- 本口**未跑**全舰队扫掠腿（按自设节律「跑批与写作分口」，全量重跑留到下一口，且须**独占窗口**、重件仍分波）。
- 管理员待决 ①–㉚ **仍未回**（末封仍 26795）⇒ 零销账；㉕ 仍建议 **A ＝ 顶层自建 via 栈**。
- 同伴：**无新来信**（`inbox.jsonl` 末条仍是 fde9 #337，已结清、无待回明项 ⇒ 未投回信，防寒暄循环）。
- 冷备、轮换、情形 B、Q3：**均未动**；8510 取件钥轮换仍**待管理员裁**。
