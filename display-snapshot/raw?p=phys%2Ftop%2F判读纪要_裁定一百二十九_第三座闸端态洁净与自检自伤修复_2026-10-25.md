# 判读纪要 · 裁定一百二十九 · 第三座闸 happy_leg_safety 端态洁净（进程面＋/tmp 面）＋ 自检自伤修复

- 阶段：139（2026-10-25 UTC）
- 出处：WiFi7-TX 组长（id `b7a0`）自审闸体族第三轮
- 面：**只读现役面 · 零动作**（未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层／顶层网表；未派工；未上传冷备）
- 性质：★**闸体族自审**（不是设计面推进）——把「★孤儿进程终局清理律」从第二座闸推到第三座闸，并把本阶段查出的**自身违规**一并修掉

---

## 〇、一句话

第三座闸 `happy_leg_safety` 与第二座闸同家族缺陷（进程面逃逸 ＋ /tmp 面残留 ＋ 对二者**判 PASS**），本口**实测坐实**缺口后硬化（端态判据扩为三项），并顺手修掉**上一口自检脚本自身漏 4 个孤儿**的自伤。

---

## 一、缺口坐实（★全部实测，非读码推断）

证据：`playbook/_evidence_stage139/happy_gate_gap.json`（改造前实测）｜复测（改造后）同脚本再跑 ⇒ `GAP_confirmed=false`。

| 面 | 实测事实 | 判据 |
|---|---|---|
| **E1 进程面** | 夹具孙进程 pid **251429** 跑完**仍存活**（`/proc` state=`S`），cmdline=`python3 -c import os,time;…time.sleep(600)`，cwd=`/tmp/happy_leg_fx_escape_wrfu3h0f (deleted)` | 逃出父子链（reparent 到 init）⇒ `os.killpg` 打不到 |
| **E2 目录面** | 夹具造的 `/tmp/happy_leak_stage139_251428` 跑完**仍在**（另加孙进程自建 `/tmp/happy_stage139_gc`） | 本闸**从不扫 /tmp**（沙箱 `happy_leg_*` 只在 `finally` 里 `rmtree(ignore_errors=True)`） |
| **E3 假绿** | 闸输出 **「受控 happy 腿：1 件｜PASS 1／FAIL 0」**、结论行「总项数 3 ／ FAIL 0」、`verdict=PASS` | 对上述全部残留**判 PASS** ⇒ 假绿坐实 |

根因（源码定位，与实测一一对应）：

- `tools/happy_leg_safety.py` 的 `run_happy_item` 用 `subprocess.Popen(..., start_new_session=True)` 起子进程，超时只 `pmod._kill_tree(p)`（killpg）⇒ 被测件内部再 `setsid` 起的孙进程**逃出父子链**。
- 全文件**零**进程面清扫符号（`_orphan_proc_sweep`／`_proc_table`／`SIGTERM` 全无），**零** /tmp 扫描。
- 端态判据只有两项：现役四件 sha 逐位未变 ＋ PDK 尾检洁净 ⇒ **进程面与 /tmp 面是盲区**。

---

## 二、闸改造（`tools/happy_leg_safety.py` 31,970 → 41,776 B，sha `a46e453e`）

| 改造 | 内容 | 律依据 |
|---|---|---|
| **A 判据单一真源** | 新增 `_load_spp()`：**惰性借用** `tools/skill_param_probe.py` 的 `_TMP_JUNK_PAT`／`_proc_table`／`_orphan_proc_sweep`（阶段 136/137 已落地并自检）；目录面清扫实现借 `tools/fleet_runtime_probe.py` 的 `_sweep_scratch_tmp`／`_scratch_residue`（后者再借前缀族）⇒ **本闸源码不出现自己的族表** | ★判据单一真源律（跨闸借用）；借用失败**即抛**，不静默降级——判据漂移比停跑更危险 |
| **B 进程面终局清扫** | 跑批前 `_proc_before = _spp._proc_table()`（pid＋starttime 双标识）；`finally` 内**先于**沙箱删除调 `_orphan_proc_sweep`（逃逸孙进程仍可写盘 ⇒ 目录会复活 ⇒ 进程先收） | ★孤儿进程终局清理律；★杀进程先收子孙律；★存量进程不动律 |
| **C /tmp 面终局清扫** | 跑批前 `_tmp_before = set(os.listdir(tempfile.gettempdir()))`；收尾只删**跑批期新建**×**族名**的 /tmp 目录；★正被活进程 cwd 占用者跳过；★跑批前存量不删 | ★存量不动律；★在用不动 |
| **D 端态判据三项** | 端态洁净 = ①现役四件逐位未变 ②PDK 尾检洁净 ③**进程面孤儿 0 ＋ /tmp 面残留 0** ⇒ `n_checks = 件数 + 3`（原「件数 + 2」，★总项数 +1 已在输出与 JSON 留痕） | ★端态洁净闸须覆盖进程面与 /tmp 面律 |
| **E JSON 只增不改** | 新增 `orphan_procs`／`tmp_residue_cleaned`／`tmp_residue_left`／`endstate_clean`；既有键与标准结论行格式**逐位不变** | ★契约不变律（★输出路径型参数 ECHO_ONLY 判 FAIL 律同源） |

---

## 三、双向校准（★10/10 ／ FAIL 0）

`playbook/_evidence_stage139/happy_selftest.json`

| # | 场景 | 期望 | 实得 |
|---|---|---|---|
| 1–6 | 既有六场景（正例 ok／缺结论行／子进程写逃逸／结论行 FAIL>0／建目录／绝对路径写重定向） | 逐位不回归 | **6/6 OK**（判定与围栏数逐位同前） |
| 7 | **正例**：逃逸夹具（setsid 孙进程＋/tmp 残留） | 孤儿被杀、/tmp 残留被清、端态判真 | `endstate_clean=True`，`n_killed≥1`，`n_left=0`，`tmp_residue_left=[]`，跑后活进程 **0** |
| 8 | **真对照**：改造前副本（`playbook/_evidence_stage139/happy_leg_safety_pre139.py`，sha `d85d9428`）跑**同一夹具** | 孤儿存活且**无端态判据键**（缺口坐实） | 存活 **2** 个进程，`endstate_clean` 键**不存在** |
| 9 | **注入负控**：伪造「孤儿未清」 | 端态判假且闸判 FAIL（鉴别力证明） | `endstate_clean=False`，`verdict=FAIL` |
| 10 | **契约对照** | 结论行格式不变＋端态键齐备 | 「结论行: 总项数 4 ／ FAIL 0」＋四键齐备 |

★**复测**：用改造前的同一测量脚本（`tools/stage139_measure_happy_gate.py`）再跑 ⇒ `E1_grandchild_alive_after_run=false`、`E2_tmp_residue_count=0`、`E3_false_green=false`、**`GAP_confirmed=false`**。

---

## 四、★自伤登记（本阶段查出的**自身违规**）

**实测**：本口端态核查发现 **4 个孤儿进程**存活（`python3 -c import time;time.sleep(900) <marker>`，cwd 指向已删目录）——**来自上一口（阶段 138）我自己写的硬化自检脚本** `tools/stage138_hardening_selftest.py`。

三条根因（均实测定位）：

1. 该脚本直接调 `probe_one`（**单件路径**）⇒ **绕过批级终局清扫腿** ⇒ 孤儿无人收；
2. 其围栏根前缀 `stage138_selftest_` **不在** `_TMP_JUNK_PAT` 族表内 ⇒ 夹具孙进程**连归属都命中不了**（归属三重收窄第一重即断）；
3. 收尾只按**捕获到的 pid 列表**杀 ⇒ 捕获不可靠（stderr 截断／多路输出）⇒ 必漏。

**修法**（`tools/stage138_hardening_selftest.py` 16,574 → 18,862 B，sha `f2264dbc`）：

- 围栏根前缀改落族内（`fleet_probe_stage138selftest_tmp_`）；
- 收尾**穷举按标记杀**（`cmdline`/`cwd` 命中 `stage138_marker` 一律收割）；
- **新增校准用例「自检自身零残留（孤儿 0 ＋ 目录 0）」**⇒ 自检的端态**自证**入账；
- 复跑：**12/12 PASS**（原 11 ＋ 新增 1），跑后端态孤儿 **0**、目录残留 **0**。

★**教训**：阶段 138 报备信里「端态 /tmp 残留 0、孤儿进程 0」**只覆盖了 fleet 闸的批级端态**，未覆盖**自检脚本自身**的夹具 ⇒ 报备口径须注明「覆盖到哪一层」（★报备口径须含覆盖层律，本口并入新律）。

---

## 五、不回归与端到端（★全部本口现算）

| 项 | 结果 |
|---|---|
| `fleet_runtime_probe` 自检 | **8/8 PASS** |
| 阶段 137 硬化自检 | **14/14 PASS** |
| 探针闸 `skill_param_probe` 自检 | **11/11 PASS** |
| 阶段 138 硬化自检（修复后） | **12/12 PASS** |
| `happy_leg_safety` 自检 | **10/10 PASS** |
| 全舰队 error 腿（真实注册表 **36** 件） | **PASS ／ 76 项 ／ FAIL 0**，覆盖 36/36 漏探 0，围栏端态净差异 0，孤儿 0，/tmp 残留 0 |
| 硬化闸**真实负载** run 腿（4 件白名单：p3_net_bridge／artifact_identity／m4_drc_attrib／m4_route_rework） | **PASS 4／FAIL 0**，结论行「总项数 7 ／ FAIL 0」，现役四件逐位未变＝是，PDK 尾检＝是，端态孤儿 0／/tmp 残留 0 |
| 现役四件 sha（现算） | mix `396571f0`／96,660；drv1 `d5e1296c`／63,502；drv2 `25adcbd1`／79,564；顶层 `88d5d9c4`／237,672 ⇒ **逐位未变** |

---

## 六、零动作与纪律

未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层／顶层网表；未派工；未上传冷备；未评估情形 B；未跑 Q3；M5 链件一概不动；未执行 8510 取件钥轮换（待管理员裁，未获令不动手）。凭据只在 `secrets/peers.json`(600)，文档只留占位符。收尾前复读 `inbox.jsonl`：仍 **355** 行／1,795,021 B／末条 fde9 **#332** 不变 ⇒ 无新同伴信 ⇒ 未投回信（防寒暄循环）。

---

## 七、新立五律（已入 `playbook/BOOT_通用律库.md`）

1. ★**自检脚本亦须端态自证律** — 自检脚本（跑批器）自身的进程/目录残留必须**实测并入账**；自检不得只报被测件的端态。
2. ★**孤儿收割须穷举标记律** — 清理由「按捕获到的 pid 列表杀」改为「按 cmdline/cwd 标记**穷举**杀」；pid 捕获不可靠 ⇒ 列表法必漏。
3. ★**围栏根前缀须入族表律** — 所有跑批者（闸体与自检）的围栏根/沙箱前缀必须落进 `_TMP_JUNK_PAT` 族表，否则夹具孙进程**连归属都命中不了**。
4. ★**单件路径绕过批级清扫律** — 直接调单件探针函数会绕过批级终局清扫腿；自检须自带收割或走批级入口。
5. ★**假绿须以端态判据收口律** — 判 PASS 前须核对「进程面 0 ＋ /tmp 面 0」：目录已删而进程仍在 ＝ 假绿。

---

## 八、下一步（候选）

- 剩余同类面：**skill_param_probe（第一座闸）** 的 run/sweep 腿本身是否也只清围栏根下的 `tmp_stage*`？阶段 136 已扩面，但其 /tmp 面清扫覆盖面（族表全量 vs 用到的族）宜再核一遍。
- 扫掠腿细分 `PARAM_INEFFECTIVE_OUT` 子键；长时件单独扫掠预算（消 `g2d_route_b_precheck` ~45 s 抖动）。
- 管理员待决 ①–㉚ 未回 ⇒ 零销账；**㉕ 已具备 A/B 双腿证据可直接裁**（我方建议 **A ＝ 顶层自建 via 栈**）。

---

## 附：交付件

| 件 | 说明 |
|---|---|
| `tools/happy_leg_safety.py` | 硬化后的第三座闸（sha `a46e453e`／41,776 B） |
| `tools/stage138_hardening_selftest.py` | 阶段 138 自检脚本自伤修复（sha `f2264dbc`／18,862 B） |
| `tools/stage139_measure_happy_gate.py` | 缺口测量脚本（改造前/后同脚本复测） |
| `tools/stage139_harden_happy_gate.py` | 闸体改造补丁脚本（唯一锚点替换＋编译自检） |
| `tools/stage139_fix_stage138_selftest.py` | 自伤修复补丁脚本 |
| `playbook/_evidence_stage139/*` | 证据（缺口测量／各闸自检 JSON／真实负载 run 腿 JSON／改造前留档两份） |
| `playbook/BOOT_通用律库.md` | 新立五律（末段） |
