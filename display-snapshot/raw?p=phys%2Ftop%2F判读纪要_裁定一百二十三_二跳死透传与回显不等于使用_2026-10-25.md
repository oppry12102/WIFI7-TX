# 判读纪要 · 裁定一百二十三 · 二跳死透传与「回显≠使用」· 2026-10-25

> 范围：**只读现役面 · 零动作**（未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层／顶层网表；未派工；未上传冷备）。
> 闸体：`tools/skill_param_probe.py`（阶段 132 新建）——本阶段**在闸自身上抓到真缺陷并当口修**。

## 一、起因：闸自身中了它要抓的病

阶段 132 的 `skill_param_probe` 用来抓「注册参数静默 no-op」。阶段 133 复读该闸源码时实测到：

| 事实 | 实测依据 |
|---|---|
| `dynamic_timeout` 注册参数 → `dynamic_probe(timeout_default=…)` | 代码路径唯一 |
| `timeout_default` 在 `dynamic_probe` 函数体内**从未被 Load**（只出现在形参声明处） | 全文检索：`timeout_default` 在该函数体出现 **1** 次＝声明行 |
| 全文件 `signal` / `alarm` / `Thread` 计数 **0 / 0 / 0** | ⇒ **根本没有超时强制** |

⇒ **注册参数 `dynamic_timeout` 传下去即被丢弃（真·二跳死透传）**：经注册接口传 `dynamic_timeout=1` 对行为**零影响**，
且**探针可无限期挂住整闸**（跑一个长时技能即整闸卡死）。
★该缺陷**阶段 132 的静态腿查不出**：腿U 判「形参在所属函数体内从未被 Load」——而 `dynamic_timeout` 在 `run()` 体内**确实被 Load**
（只是作为**实参**传给被调函数）。⇒ 腿U 的判据只覆盖「一跳」，**对「透传到子函数后在子函数被忽略」结构性失明**。

## 二、三条新律（本阶段立，已入 `playbook/BOOT_通用律库.md`）

1. **★★二跳死透传律（透传即丢弃＝静默 no-op）**
   注册参数的值若**只**流向被调函数的形参、而该形参在被调函数体内**再不被读取** ⇒ 该参数**静默无效**。
   静态**可判定**（不依赖运行期），故列为 FAIL 级；不可判定者（属性调用／`**kwargs` 下传／`locals()` 反射／来源不唯一）⇒ 一律记「不可判」，**不得据以判缺陷**。
2. **★★回显≠使用律（echo ≠ use）**
   「参数值出现在 stdout／产物里」**不等于**「参数被使用」——哨兵回显会让单点探针误判为「被读」。
   机器判据＝**两值差分实测**：同参数注入两个**长度不同**的探针值各跑一次，
   归一化后比对 ⇒ `EFFECT`（有可观测效应）／`ECHO_ONLY`（只回显）／`NO_EFFECT`（传下去即丢弃）。
   ★两探针值必须**长度不同**：等长时「按长度/按数量使用」的行为在两跑间无差异 ⇒ 差分腿会把「真使用」误判成 `ECHO_ONLY`（本阶段实测踩中并修）。
3. **★★闸自身度量诚实律（覆盖不得掩盖盲区）**
   闸输出「FAIL 0」时**必须同时给出覆盖度量**：可判／不可判／未涉及各多少。
   「判不了」**不得**被记成「未涉及」——否则「全绿」是**度量层面**的假绿。本阶段实测：未涉及 44 项（多因 `v = kw.get('out') or DEFAULT` 这类**间接绑定**）⇒ 如实改记「不可判」37 项。

（另沿用并强化 **★超时≠违例律**：探针超时判 `TIMEOUT`＝不可判，不计 FAIL，须点名转第二腿长预算复跑。）

## 三、闸的四处改造（`tools/skill_param_probe.py` 25,509 → 43,107 B）

| # | 改造 | 作用 |
|---|---|---|
| ① | `_run_with_timeout()`：`signal.setitimer(ITIMER_REAL)` 真强制超时 | 令 `dynamic_timeout` **真正生效**；超时判 `TIMEOUT`（不可判，不计 FAIL） |
| ② | **腿T 二跳传递静态分析**（`_load_contexts` / `_follow` / `_dyn_keys_in`） | 新增 `DEAD_TRANSIT` 判据；带 `unprovable` 保守边界 |
| ③ | **差分实测腿** `differential_probe()` | 三判据可区分 `EFFECT`／`ECHO_ONLY`／`NO_EFFECT`；两值长度不同 |
| ④ | **覆盖度量行** | 「腿T 覆盖: 可判 N（alive／dead）／不可判／本地未读／未涉及」 |

补丁链（可审、幂等、每处断言 old 唯一命中）：
`tools/stage133_patch_probe.py` → `tools/stage133b_patch_coverage.py` → `tools/stage133c_patch_difffix.py`（三者均自带「已应用则跳过」判定）。

## 四、双向校准（四组，全部实测）

| 组 | 内容 | 结果 |
|---|---|---|
| 闸自检 | 6 例：OK／NOOP_NAME／UNUSED／OVERWRITTEN／**DEAD_TRANSIT（新增负控）**／**ALIVE_TRANSIT（新增同形反向对照）** | **6/6 PASS** |
| 差分标定 | 3 只夹具必须给出**三个不同判据**：死透传⇒`NO_EFFECT`／真使用⇒`EFFECT`／只回显⇒`ECHO_ONLY` | **3/3 PASS**（首轮 alive 夹具误判 `ECHO_ONLY` ⇒ 据实改夹具为真「使用」并拉长第二探针值，修正后通过） |
| 端到端负控 | 留档旧版 `playbook/_archive/stage133/skill_param_probe_pre_stage133.py`（**含真缺陷**）注册为夹具 | 判 **`DEAD_TRANSIT`**（FAIL 1）✔ 闸对真缺陷有牙 |
| 端到端正控 | 同一 schema 指向修复后现役版 | **FAIL 0** ✔ |
| 假红防护 | 同形结构（值传到被调函数）但被调函数**真读** ⇒ 不得报；只回显 ⇒ 不得报 | 均**未报** ✔ |

## 五、舰队复跑（改闸后回归）

- `skill_fleet_audit`（live，注册表派生花名册）：**36/36 PASS**，A1–A4 缺口 **0**，覆盖完备性 36/36。
- `fleet_runtime_probe` error 腿：**76/76 PASS**，围栏副作用 **±0**（新增/变更/消失全 0），PDK 尾检洁净，覆盖 36/36。
- 我方闸自检：**36 件 / 125 个注册参数** ⇒ 腿T 覆盖：**可判 73（alive 73／dead 0）／不可判 37／本地未读 0／未涉及 15**
  ⇒ **另 52 项静态不可判 ⇒ 须由动态差分腿覆盖（阶段 134 的全量动态扫掠）**。
  ★即：静态腿已证**现役 36 件无二跳死透传**，但覆盖仅 73/125，残余面待动态腿穷举。

## 六、零动作与纪律

未改现役四件与任何现役 GDS／网表／deck 字节；未产交付面合并件；未建顶层 pin 层／顶层网表；未派工；未上传冷备；
未评估情形 B；未跑 Q3；M5 链件一概不动；**未执行 8510 取件钥轮换（待管理员裁）**。
凭据只在 `secrets/peers.json`(600)；文档只留占位符。夹具与证据只写 `playbook/_fixtures/`、`playbook/_evidence_stage133/`、`playbook/_archive/stage133/`。

## 七、下一步（阶段 134 候选）

1. **全量动态差分扫掠**：125 个注册参数逐个两值差分（现闸已有 `differential_probe`；需补 `sweep` 模式入口）⇒ 覆盖腿T 的 52 项残余面。
2. 腿T 不可判的 37 项逐个点名（`p1_scope_map.variant`／`p2_place_table.json_out`／`chain64_residue_check.verifier_items`／`chain64_residue_check.versions`／`peer_sandbox_repro.out`／`happy_leg_safety.registry`），逐个手工核对是否真生效。
3. 受控 happy 腿白名单第 9 件 E1 逐件评估（宁可不开，不可假绿）。
