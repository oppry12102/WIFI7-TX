# 判读纪要 · 裁定一百三十四／一百三十六（WiFi7-TX 组长 b7a0）

- 时间：2026-10-25 UTC 04:54–05:30（本地 12:54–13:30）
- 性质：**只读现役面 · 零芯片动作**（未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层；未派工）
- 本纪要合并两件事：**阶段 144 收口**（全舰队扫掠腿三波跑批完成）与**阶段 146**（不可判根因定域＋探针三修＋域内合法值发现器）

---

## 〇、一句话

阶段 144 的 56 项扫掠腿跑批**全部跑完**（FAIL 0／未跑 0／抖动 1），留下 **18 项不可判**；本阶段把其中 **11 项**逐条定域到根因，用 **4 处补丁**（探针自身）＋ **1 个新工具**（域内合法值发现器）把轻量子集的可判率从 **2/10 → 5/10**，并**坐实 2 类判据器自身缺陷**（早退假阳性 / 域外取值）。

---

## 一、阶段 144 收口（裁定一百三十四）：三波跑批实况

跑批：后台工人 `tools/stage144_sweep_worker.sh`（pid 367409），串行三波（★跑批独占窗口律：并发＝假 FAIL），
**2026-10-25T03:54:56Z 起 · 05:16:30Z 完**（waveA rc=0 / waveB rc=0 / waveC rc=0 / batch done）。

| 波 | 技能/项 | 判据分布 | 不可判 | 抖动 | 未跑 | 终局 |
|---|---|---|---|---|---|---|
| A 轻件 24 技能 | 30 项 | EFFECT 22／NO_EFFECT 1 | **8**（UNOBSERVABLE 4／INCONCLUSIVE 3／NO_EFFECT 1） | 0 | 0 | 残留 0／孤儿 0 |
| B 重件 9 技能 | 22 项 | EFFECT 14／CONSUMED_REJECTED 3／UNOBSERVABLE 5 | **8** | 1（`g1_drc_precheck.keep_tmp`） | 0 | 孤儿杀 2（KLayout DRC，TERM）／未归属只报 2 |
| C 超重件 2 技能 | 4 项 | EFFECT 2／INCONCLUSIVE 2 | **2** | 0 | 0 | 残留 0／孤儿 0 |
| **合计** | **38 技能／56 项** | **EFFECT 38** | **18** | 1 | **0** | 残留 0 |

- 历史三态抖动（`g2d_route_b_precheck`）**收敛为单一 EFFECT**（profile 自动把单项预算抬到 82 s，实测 83.8/82.6 s）⇒ 阶段 143 的长时件预算分层律在**全舰队**层面生效。
- ★**波 B 孤儿面的一处观察**：KLayout DRC 子进程被探针按 scratch 归属杀掉 2 个，但同时又被记进「未归属只报」清单（同一 pid 出现在 killed 与 unattributed 两表）⇒ 探针的归属判据与报告口径有一处**自相矛盾**（非致命；孤儿终局数 0 正确）。留待下阶段修（★归属判据与报告须同源律）。

---

## 二、阶段 146（裁定一百三十六）：18 项不可判的**逐条根因**

### 2.1 三类根因（实测坐实，非推断）

| 类 | 机理 | 实测证据 | 波及项数 |
|---|---|---|---|
| **R1 域外取值** | 扫掠腿固定用**域外哨兵**（number → `-987654321`；枚举串 → `__A1PROBE__…`）⇒ 工具早退/抛异常 ⇒ **参数使用点未到达** | `service_liveness_gate.mode` → `KeyError: 'n_cases'`；`peer_landing_accept.mode` → `SystemExit: accept 模式须给 receipt_md`；`m4_drc_rerun.mode` / `p4_lvs_top_pre.mode` / `g1_short_locator.sweep` → argparse 拒绝（CONSUMED_REJECTED） | **11** |
| **R2 早退假阳性** | 早退判据 `_ERRKEY_PAT` 只要返回值里**出现** `'error':` 就判早退——哪怕值是 `None` ⇒ **正常路径被误判不可观测** | `skill_fleet_audit.json_out`（实测 0.5/0.6 s、结论行 FAIL 0）被判 UNOBSERVABLE；`.selftest`（0.5/1.4 s）同 | **2**（同族波及面更大） |
| **R3 兄弟参数缺合法基线** | 无 default 的**必填**兄弟参数被塞类型哑值（string → `""`）⇒ 前置校验失败 ⇒ 早退 | `sg13g2_sim.timeout`（netlist="" ⇒ 网表找不到）；`peer_fetch_verify.*` 5 项（items-json/peer-base 缺失） | **6+** |

### 2.2 四处补丁（探针自身，`tools/skill_param_probe.py`）

| 补丁 | 内容 | 对应根因 |
|---|---|---|
| **P1** | 早退判据要求 error **值非 None**（`(?!None\b)`） | R2 |
| **P2** | 扫掠腿改为**候选配对**制：①输出路径型沙箱对 ②**域内合法对**（静态发现）③域外哨兵对（兜底）；**逐对试跑**，取第一对「两跑都走到正常路径」的配对 | R1 |
| **P3** | 兄弟参数**合法基线**：脚本形参默认值 → 域内发现值 → 类型哑值（兜底） | R3 |
| **P4** | 早退判定改看**顶层**失败（顶层 error 非空／`verdict=FAIL` 且 `n_fail`）；嵌套子项 error 不算早退；配对搜索同步用顶层判定 | R2 深层 |

★补丁**可重放**：`tools/_stage146_probe_patch.py`（幂等；`A1_PATCH_TARGET` 可指向副本）。
★**重放等价实测**：从补丁前备份（`/tmp/skill_param_probe.py.bak_stage146`）重放 ⇒ 与现役文件**逐字节相同**（sha `34198f05…`／100,980 B）⇒ 补丁可复现，非手改不可追溯。
★P4-b（描述里点名的目录 ⇒ 列目录取既有文件名）落在新工具 `tools/a1_legal_domain.py`。

### 2.3 新工具：`tools/a1_legal_domain.py`（域内合法值与合法基线程序化发现器）

只读现役面：**只解析脚本源码（ast）＋注册表 JSON，不执行任何技能、不写任何现役件**。

- 发现源优先级：argparse `choices` ＞ 枚举字典/赋值 ＞ 字符串比较（`== "x"` / `in (...)`）＞ argparse/形参默认值 ＞ **描述枚举词**（「census（默认）｜selftest」）＞ 描述示例路径 ＞ **描述点名目录下的既有文件名** ＞ 脚本内绝对路径常量。
- 附带 **M3 注册名×形参核对**：FORMAL／KW_READ／KW_FORWARD（`**kw` 转发或动态键，**不判缺陷**）／KWARGS_SWALLOW（**静默无效**，高危）／MISSING（调用期 TypeError）。
- 全舰队实测：**38 技能／131 参数**，域内两值可发现 **78（59.5%）**；**KWARGS_SWALLOW 0**、**MISSING 0** ⇒ **无「注册参数被静默吞掉」的实证缺陷**（此前的 115 项告警经细化全部降为 KW_FORWARD 噪声：`**kw` 转发／`kwargs.items()` 动态消费）。
- 自检 **8/8**（正例 4：argparse choices／数值相邻两值／形参默认值可作基线／调用计划无阻塞；负控 4：域外参数名发现不到两值／`**kw` 吞名判 KWARGS_SWALLOW／缺形参判 MISSING／不可解兄弟参数记入 `blocked_by`）。

### 2.4 打补丁后的复测（轻件子集 5 技能／10 残余项）

| 项 | 补丁前（波 A） | 补丁后 | 变化 |
|---|---|---|---|
| `skill_fleet_audit.json_out` | UNOBSERVABLE | **EFFECT** | ✔ R2 修掉 |
| `skill_fleet_audit.selftest` | UNOBSERVABLE | **EFFECT** | ✔ R2 修掉 |
| `peer_landing_accept.mode` | INCONCLUSIVE_ERROR | **EFFECT** | ✔ 配对搜索（accept→probe→snapshot 三对后取到可跑对） |
| `service_liveness_gate.mode` | INCONCLUSIVE_ERROR | **EFFECT** | ✔ 域内对（census／selftest） |
| `chain64_residue_check.verifier_items` | EFFECT | UNOBSERVABLE | ✖ **回退**（P4-b 给兄弟参数补了合法基线 ⇒ 工具走得更远后暴露自身失败）⇒ 记为**回退项**，须下阶段定域 |
| `sg13g2_sim.timeout` | UNOBSERVABLE | UNOBSERVABLE | ✖ netlist 域内值仍不可发现（描述点名目录的既有文件名未命中 netlist 口径） |
| `chain64_residue_check.versions` | INCONCLUSIVE_ERROR | INCONCLUSIVE_ERROR | ✖ 域格式为 `letter=sha`，静态发现不到 |
| `skill_fleet_audit.registry` | UNOBSERVABLE | UNOBSERVABLE | ✖ 路径型：需「注册表副本」作第二合法值（未做） |
| `peer_landing_accept.tool` | NO_EFFECT | NO_EFFECT | ✖ 需与 `mode=probe` 配对使用（参数间依赖未建模） |
| **小计** | 已判 2／不可判 8 | **已判 5／不可判 5** | **不可判 8→5（−37.5%）** |

### 2.5 ★仍待下阶段（诚实列名，不假装已判）

- **域格式感知**：参数域不是枚举而是**格式**时（`versions`＝`letter=sha`），静态发现不到域内值 ⇒ 需「失败驱动的格式自举」（读异常信息里的「expected 2, got 1」推字段数）或人工定向复测。
- **参数间依赖**：`tool` 只有在 `mode=probe` 下才有意义 ⇒ 差分腿需建模「同族参数联动」。
- **路径型参数的第二合法值**：如 `registry` 需「同内容副本」才既合法又可区分。
- **回退项** `chain64_residue_check.verifier_items`：P4-b 引入的兄弟基线使其走得更远后暴露自身失败 ⇒ 须定域是「工具缺陷」还是「参数缺陷」。
- **孤儿面自相矛盾**：波 B 里同一 pid 既记 killed 又记 unattributed（探针归属判据与报告不同源）。

---

## 三、★新立五律（入 `playbook/BOOT_通用律库.md` 末段）

1. ★**域内合法取值律** —— 差分/探针的取值必须**落在参数域内**；域外取值会把「工具早退」误读成「参数无效应」（R1）。
2. ★**合法基线律** —— 探针调用必须给兄弟参数**域内合法值**（脚本形参默认值 → 域内发现值），否则参数使用点未到达，差分不可观测（R3）。
3. ★**早退须看顶层律** —— 判「早退」只看技能**自己返回的顶层失败**；嵌套结果里的子项 error／空值 error 不得触发早退（R2）。
4. ★**配对搜索律** —— 取值域不唯一时，按证据强度**逐对试跑**，取第一对「两跑都走到正常路径」的配对；试了几对须披露。
5. ★**注册名×形参须同源核律** —— 判「注册参数被静默吞掉」须区分「字面读取／`**kw` 转发／动态消费」三态；只有**既非形参、又无任何读取面**才可判缺陷（否则 131 参数里会假报 115 项）。

---

## 四、实测锚（本口现算）

- 探针自检 **13/13 PASS**；阶段 137 硬化自检 **14/14 PASS**；域内发现器自检 **8/8 PASS**。
- 补丁重放等价：备份重放 ⇒ 与现役文件**逐字节相同**（`34198f05…`／100,980 B）。
- 全舰队域内发现器报告：38 技能／131 参数／域内两值可发现 78（59.5%）／静默吞名 **0**／缺形参 **0**。
- 复测（轻件 5 技能）：残余 10 ＝ **已判 5 ＋ 不可判 5 ＋ 未跑 0**；FAIL 0；抖动 0；终局残留 0／孤儿 0。
- 现役四件 sha 逐位未变：mix `396571f0`／96,660；drv1 `d5e1296c`／63,502；drv2 `25adcbd1`／79,564；顶层 `88d5d9c4`／237,672。
- 收尾复读 `inbox.jsonl`：**360 行**，末条＝**fde9 #337**（回我 #92：其 5 条陈述 5/5 吻合、其 8425 已升 v1.4 多线程＋30 s 超时＋队列锁、并发 8/16 与 16/16 全 PASS、470 MB 波形备选关闭）⇒ **无待回明项，未投回信**（防寒暄循环）。

---

## 五、零动作与纪律

未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层／顶层网表；未派工；未上传冷备；未评估情形 B；未跑 Q3；**M5 链件一概不动**；**未执行 8510 取件钥轮换**（待管理员裁，未获令不动手）。
本阶段唯一改动＝**我方自有工具**（探针 + 新发现器 + 补丁脚本）；未触碰任何现役芯片件。

---

## 六、证据

- `playbook/_evidence_stage144/`：三波扫掠 JSON（waveA/B/C）＋ worker.log ＋ 盘点 inventory_fullfleet.json
- `playbook/_evidence_stage146/`：`a1_legal_domain_report.json`（全舰队域内发现＋M3 核对）｜`sweep_recheck_light.json`（P1–P3 后）｜`sweep_recheck_light2.json`（P1–P4 后）
- 补丁脚本 `tools/_stage146_probe_patch.py`（幂等可重放；`A1_PATCH_TARGET` 覆盖目标）
