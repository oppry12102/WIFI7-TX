# 判读纪要 · 裁定一百二十七 · 扫掠腿「结论可读性」双键加固 ＋ 孤儿进程终局清理腿（进程面）

- 时点：2026-10-25 01:03–01:11 UTC（本地 09:03–10:11 Asia/Shanghai）
- 阶段：**137**（上口 136 收口）｜**只读现役面 · 零动作**（未改任何现役 GDS/网表/deck 字节；未产合并件；未建 pin 层/顶层网表；未派工）
- 闸件：`tools/skill_param_probe.py`（69,053 → **76,686 B**，sha `7edc1bdc…`）｜补丁 `tools/stage137_sweep_readability_patch.py`（**幂等**）｜自检 `tools/stage137_hardening_selftest.py`（新增）

## 〇、缘起（两条，都是上口留下的实测缺口）

1. ★**可读性缺口**（上口 summary 下口步骤 1）：扫掠腿 JSON 的 `fails` 键**同时装「真 FAIL」与「不可判·INFO」两类** ⇒ `n_fail` 计数正确、结论行正确，但**键名与内容语义不符** ⇒ 读 JSON 的人会把「19 条不可判」误读成「19 条失败」。
2. ★**进程面缺口**（阶段 136 实测坐实）：阶段 136 的终局清扫只清**目录**（`/tmp` 12 个残留已清零），但跑批派生的 `run_drc.py → sh → klayout` 链**逃出父子链**（setsid ⇒ 被 reparent 到 init）⇒ 目录清掉后**进程仍在**，存活 16 分钟持续占 CPU。★**目录洁净 ≠ 端态洁净**。

## 一、闸改造（2 处 · 1 个文件）

`tools/skill_param_probe.py`：补丁 `tools/stage137_sweep_readability_patch.py`（**幂等**：标记串 `# ★STAGE137_PATCH_V1`／`# ★STAGE137_PATCH_V2`，V1 11 处 ＋ V2 1 处；复跑两次均 `[noop] 无改动（幂等）`；写回前**语法自检**）。

### 改造 A · 双键拆分（★结论键语义单一律）

- `fails` **只装真 FAIL**（当前唯一来源：`OUT_NOT_LANDED` ⇒ `PARAM_INEFFECTIVE_OUT`、输出路径型 `ECHO_ONLY` ⇒ `PARAM_INEFFECTIVE_OUT`）；
- 新增 `needs_review` 键装**不可判/INFO**（`NO_EFFECT_INFO`／`CONSUMED_REJECTED_INFO`／`ECHO_ONLY_INFO`／`TIMEOUT`／`ERROR`／`INCONCLUSIVE_ERROR`／`UNOBSERVABLE`／`NOT_RUN`），新增 `n_needs_review` 计数；
- **契约不变**：`n_fail` 计数、`verdict`、标准结论行「结论行: 总项数 N ／ FAIL n」、`coverage` 全部逐位不变（见 §二 契约对照）；
- 标准输出分行标注：`[真FAIL]…` 与 `[待人工判读]…`（原为同一列表、无区分 ⇒ 误读源）。

### 改造 B · 孤儿进程终局清理腿（进程面）

- 新增 `_proc_table()`（/proc 快照：pid → starttime/ppid/cmd/cwd）、`_scratch_path()`（**复用 `_TMP_JUNK_PAT` 单一真源**，且额外要求落在 `/tmp/` 或 `phys/drc/` 下 ⇒ 不误伤同名正式件名如 `m4_*.gds`）、`_scratch_tokens()`（逐 token 判，不跨 token 误配）、`_ancestor_pids()`、`_orphan_proc_sweep()`；
- **归属三重收窄**：① **跑批期间新生**（pid+starttime 不在跑批前快照）⇒ 跑批前的存量进程一律不碰；② cmdline 或 cwd 命中本舰队 scratch 前缀；③ 排除 pid 1 / 自己 / 自己的祖先；
- 命中者连**子孙**一起收（深度优先，先 TERM 后 KILL）；无 scratch 归属但名字像 `klayout`／`run_drc.py`／`ngspice`／`netgen` 的 ⇒ **只报不杀**（`unattributed`）⇒ 宁可漏杀不可误杀；
- JSON 新增 `orphan_procs` 键（`n_killed`／`killed`／`n_left`／`left`／`n_unattributed`／`unattributed`）＋ 标准输出加行「★进程面终局清扫: 杀孤儿 N 个 ／ 未归属只报 N」；
- ★V2 小修：`_alive()` 原按 `kill(pid,0)` 判活 ⇒ **僵尸态（Z）会被误判为「残留」** ⇒ 改判 `/proc/<pid>/stat` 的 state，Z 视为已死。

## 二、校准与实测（14 道机检 · 全 PASS）

`tools/stage137_hardening_selftest.py`（标准结论行「结论行: 总项数 N ／ FAIL n」，rc 0/1）：

| 类别 | 用例 | 结果 |
|---|---|---|
| 正例 | `ORPHAN_CWD_KILLED`（cwd 在 scratch 面的跑批期新生进程） | OK（被杀并记录） |
| 正例 | `ORPHAN_CMDLINE_KILLED`（cmdline 含 scratch 路径） | OK |
| 负控 | `ORPHAN_PREEXIST_UNTOUCHED`（跑批前存量，cwd 在 scratch 面） | OK（未杀、仍活） |
| 负控 | `ORPHAN_UNRELATED_UNTOUCHED`（跑批期新生但与 scratch 无关） | OK（未杀、仍活） |
| 负控 | `ORPHAN_SELF_SAFE`（自己/父进程不在击杀集） | OK |
| 正例 | `KEYS_FAILS_ONLY_TRUE`（`fails` 全为真 FAIL 且 `len(fails)==n_fail==1`） | OK |
| 正例 | `KEYS_NEEDS_REVIEW_ONLY_INFO`（`needs_review` 全为 `_INFO` 且 `n_needs_review==1`） | OK |
| 正例 | `KEYS_VERDICT_CONSISTENT`／`KEYS_CONCLUSION_LINE` | OK |
| 对照 | `CONTRACT_N_FAIL_SAME`／`CONTRACT_VERDICT_SAME`／`CONTRACT_COVERAGE_SAME`／`CONTRACT_CONCLUSION_SAME`（**改造前备份件** vs 改造后，同一夹具跑同一 sweep ⇒ 逐位一致） | OK |
| 正例 | `CONTRACT_ORPHAN_KEY_PRESENT` | OK |

★**结论行: 总项数 14 ／ FAIL 0**；证据 `playbook/_evidence_stage137/stage137_hardening_selftest.json`。

## 三、回归与端到端

- 探针闸自检（阶段 133 六项 ＋ 阶段 135 五项）**11/11 ／ FAIL 0**（不回归）⇒ `playbook/_evidence_stage137/probe_selftest_regression.json`。
- 端到端 mini sweep（**真实注册表** · `g2d_route_b_precheck` · 2 项）：**FAIL 0 ／ PASS**；新键生效（`fails` 0 条、`needs_review` 1 条、`n_needs_review` 1）；输出出现 `[待人工判读][UNOBSERVABLE]…` 标注；`★终局清扫: 清除残留目录 0 个`；`★进程面终局清扫: 杀孤儿 0 个 ／ 未归属只报 0` ⇒ `playbook/_evidence_stage137/sweep_mini.json`。
- ⚠ **口径说明（非闸缺陷）**：本次 mini sweep 的 `g2d_route_b_precheck.out` 判 `UNOBSERVABLE`（早退不可观测），而阶段 136 同款 mini sweep 判 `EFFECT` —— 根因是**该技能单跑耗时 ~45 s，恰在探针逐项超时线上**（第二跑被技能内部 guard 吞掉超时 ⇒ 走早退分支）⇒ 属**耗时边界抖动**；两种判据**都不计 FAIL**（★超时≠违例律）⇒ 闸结论同为 PASS。消抖须给长时件单独加预算（与阶段 135「长预算第二腿」同思路），**本阶段未动**。
- 端态：**`/tmp` 舰队残留 0**（`a1sweep_`／`a1probe_`／`g1drc_`／`g2d_`／`g2c_`／`m4_` 全族 0）｜工作区 `phys/drc/tmp_stage*` **0**｜**孤儿进程 0**（无 klayout／run_drc 残留）。
- 现役四件 sha 本口现算**逐位未变**：mix `396571f0`/96,660、drv1 `d5e1296c`/63,502、drv2 `25adcbd1`/79,564、顶层 `88d5d9c4`/237,672。

## 四、★自伤登记（一处，被补丁幂等判据自身抓到）

- **补丁 V2 首版缺标记串**：V2 新文本未带 `# ★STAGE137_PATCH_V2` ⇒ 复跑时锚点已不存在 ⇒ 脚本报 `[abort] 锚点命中 0 次`（**幸未落位**）。处置：**从 pre137 备份还原 ⇒ 一次重施 V1+V2** ⇒ 复跑两次均 `[noop]`。⇒ 印证 ★幂等判据须用标记串律（**每个补丁阶段都要有独立标记串**，不能只给首版打标记）。
- 另：一次 `tail -c` 读文件输出触发 UnicodeDecodeError（★工具输出别用 `tail -c` 律的已知纪律，本口自伤一处，已改 `tail -n`）。

## 五、新立四律（入 `playbook/BOOT_通用律库.md` 末段）

1. ★**结论键语义单一律**：`fails` 类键只装真 FAIL；不可判/INFO 走独立键＋独立计数；改键不得改 `n_fail` 计数、结论行与 `verdict`（契约不变）。
2. ★**孤儿进程终局清理律**：终局清扫必须兼扫进程面（目录洁净 ≠ 端态洁净）；归属三重收窄；无归属者只报不杀。
3. ★**存量进程不动律**：只对跑批期间新生（pid+starttime 双标识）的进程生效。
4. ★**杀进程先收子孙律**：深度优先（先子孙后父）＋ TERM→KILL 两段；判活看 state（Z 视为已死）。

## 六、零动作与纪律

未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层／顶层网表；未派工；未上传冷备；未评估情形 B；未跑 Q3；M5 链件一概不动；**未执行 8510 取件钥轮换（待管理员裁）**。凭据只在 `secrets/peers.json`(600)，文档只留占位符。沙箱写系统临时目录并即删。

## 七、证据清单

- `playbook/_evidence_stage137/stage137_hardening_selftest.json`（14 项）
- `playbook/_evidence_stage137/probe_selftest_regression.json`（11 项）
- `playbook/_evidence_stage137/sweep_mini.json`（端到端 mini sweep · 新键）
- `playbook/_evidence_stage137/skill_param_probe_pre137.py`（改造前备份 · 契约对照用）
- 补丁 `tools/stage137_sweep_readability_patch.py`（幂等）｜自检 `tools/stage137_hardening_selftest.py`
