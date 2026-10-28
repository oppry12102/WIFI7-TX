# 判读纪要 · 裁定一百二十八 · 跨闸端态洁净统一（进程面 ＋ /tmp 面）

- 时点：2026-10-25（本地 10:12–10:29，UTC 02:12–02:29）
- 阶段：**138**（承阶段 137 · 裁定一百二十七）
- 性质：**只读现役面 · 零动作**（未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层；未派工）
- 产物：`tools/fleet_runtime_probe.py` 改造（41,309 → 45,720 B）＋ `tools/stage138_hardening_selftest.py` ＋ `tools/stage138_escape_repro.py`（坐实实验）＋ 证据 `playbook/_evidence_stage138/*`

---

## 一、缘起：两条都是**实测坐实**的缺口（不是读码推断）

上口（阶段 137）留下的下口步骤第 1 条只给了两个低优先加固项；本口顺着「上一阶段刚立的新律
『★孤儿进程终局清理律』是否覆盖到其它闸」这个问题往下查，查出**第二座闸的同类缺口**。

### E1 进程面缺口（坐实实验，`tools/stage138_escape_repro.py`）

`tools/fleet_runtime_probe.py` 的 `probe_one()` 用 `subprocess.Popen(..., start_new_session=True)`
起被测技能子进程 ⇒ 该子进程自成一会话；超时分支只 `os.killpg(os.getpgid(p.pid), SIGKILL)`
⇒ **只能杀到同一进程组**。被测技能若在内部再 `setsid` 起孙进程 ⇒ 孙进程**逃出父子链**
（reparent 到 init）⇒ `killpg` 打不到。

坐实结果（实测，非推断）：

| 观测项 | 实测值 |
|---|---|
| 夹具孙进程 pid | 250407（`stage138_escape_repro.json`） |
| probe 跑完后存活？ | **是**，`/proc/250407/stat` state = `S`（sleeping） |
| cmdline | `python3 -c import time;time.sleep(900) /tmp/a1probe_stage138_*/stage138_marker` |
| cmdline 是否命中 scratch 族？ | **是**（`a1probe_` 前缀）⇒ 归属判据本可命中，只是本闸**没有进程面清扫腿** |
| fleet 源码中的进程面符号 | **零**（`orphan_proc_sweep` / `_proc_table` / `SIGTERM` 全无） |

⇒ 阶段 136 坐实的「目录洁净 ≠ 端态洁净」在**第二座闸**上同样成立。

### E2 目录面缺口（坐实实验）

`fleet_runtime_probe.sweep_tmp_dirs()` 只删「**围栏根下**名字匹配 `tmp_stage*` 的目录」
（`TMPDIR_PATTERNS = ("tmp_stage",)`），**从不扫 `/tmp`**。

坐实结果：造 `/tmp/g1drc_stage138_residue_*` 目录 → 跑 `sweep_tmp_dirs([ROOT])`
→ `n_swept = 0`，该目录**仍在**。⇒ 被测技能在 `/tmp` 造的 scratch 残留**不被清**。

---

## 二、改造（`tools/fleet_runtime_probe.py`，41,309 → 45,720 B，sha8 `af78c0ac`）

### A 判据不另立表 —— 惰性借用 `skill_param_probe` 的真源

新增 `_load_spp()`：**惰性**加载 `tools/skill_param_probe.py`（阶段 136/137 已落地并自检通过的
进程面实现），取其 `_TMP_JUNK_PAT`（前缀族真源）／`_proc_table`（进程快照）／
`_orphan_proc_sweep`（归属三重收窄 ＋ 深度优先 TERM→KILL）。

★借用失败**即抛**（`RuntimeError`），**不静默降级到另一张表** —— 判据漂移比停跑更危险。
★本闸源码中**不出现**自己的 `_TMP_JUNK_PAT = re.compile(...)`（自检 P4 逐条断言）。

### B 进程面终局清扫腿

跑批前取 `_proc_before = _spp._proc_table()`（pid+starttime 双标识快照）；
收尾 `finally` 内**先于**沙箱删除调用 `_spp._orphan_proc_sweep(_proc_before)`
（子进程在 rmtree 之后仍可能写盘 ⇒ 目录会复活 ⇒ 进程先收）。
归属三重收窄（沿用阶段 137 判据）：① 跑批期新生 ② scratch 归属 ③ 非自身/祖先/pid1；
无归属者**只报不杀**。

### C `/tmp` 目录面终局清扫腿

新增 `_sweep_scratch_tmp()` / `_scratch_residue()`：只删**跑批期新建**（`/tmp` 前后快照差集）
且命中 scratch 族名的**目录**；★正被活进程 cwd 占用的目录**跳过**（防误删并行作业现场）；
★跑批**前**存量目录**不删**（存量不动律）。

### D 端态洁净判据并入 + JSON 新键（★契约不变）

- 端态洁净判据从「围栏根目录面」扩到「围栏根 ＋ `/tmp` 面 ＋ 进程面」**三项同时归零**；
- JSON **只增不改**：`orphan_procs` / `tmp_residue_cleaned` / `tmp_residue_left`；
- `n_fail` 语义、标准结论行、`verdict`、`coverage` **逐位不变**（自检 C1/C2 用改造前备份件逐位对照）。

---

## 三、★自伤登记（2 处，均已修，且被律自己抓到）

1. **自检 P1 首跑 FAIL**：自检把围栏根建在 `/tmp/stage138_selftest_*`（**不属 scratch 族**）
   ⇒ 进程归属三重收窄必然不命中 ⇒ 把「归属不中」误读成「清扫腿失效」。
   ⇒ 修法：围栏根改用族内命名 `fleet_probe_stage138selftest_*`（复刻真实跑批的 `fence_dir` 口径）。
   ⇒ 由此立 ★**围栏路径须落 scratch 族内律**（否则测的是错的语义）。
2. **自检自身留残留**：自检 `finally` 只删了 `tmpd`，漏删落在 `/tmp` 的围栏根与存量负控目录
   ⇒ 端态检出 3 个残留。⇒ 修法：`finally` 内一并清（立 ★**闸内自测亦须零残留律**）。

另：一次 `tail -c` 读中文文件触发 UnicodeDecodeError（★工具输出别用 `tail -c` 律，已改 `tail -n`）。

---

## 四、实测锚

| 项 | 结果 |
|---|---|
| 缺口坐实实验 E1 | 逃逸孙进程 **存活**（pid 250407，state S）⇒ **GAP** |
| 缺口坐实实验 E2 | `/tmp` 残留 **不被清**（`n_swept=0`）⇒ **GAP** |
| 阶段 138 硬化自检 | **11/11 ／ FAIL 0**（正例 5 ＋ 负控 4 ＋ 契约对照 2） |
| fleet 既有自检（阶段 129 八场景） | **8/8 ／ FAIL 0** 不回归 |
| 阶段 137 硬化自检 | **14/14 ／ FAIL 0** 不回归 |
| 探针闸自检（阶段 133/135） | **11/11 ／ FAIL 0** 不回归 |
| 端到端全舰队 error 腿（真实注册表 36 件） | **PASS ／ 76 项 ／ FAIL 0**；覆盖 36/36 漏探 0 |
| 端态（跑批后） | `/tmp` scratch 残留 **0**；孤儿进程 **0** |
| 现役四件 sha（本口现算） | mix `396571f0`/96,660、drv1 `d5e1296c`/63,502、drv2 `25adcbd1`/79,564、顶层 `88d5d9c4`/237,672 —— **逐位未变** |

---

## 五、★新立四律（入 `playbook/BOOT_通用律库.md` 末段）

★**端态洁净闸须覆盖进程面与 /tmp 面律**｜★**判据单一真源律（跨闸借用）**｜
★**闸内自测亦须零残留律**｜★**围栏路径须落 scratch 族内律**。

---

## 六、零动作与纪律

未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层／顶层网表；未派工；未上传冷备；
未评估情形 B；未跑 Q3；M5 链件一概不动；未执行 8510 取件钥轮换（待管理员裁，未获令不动手）。
凭据只在 `secrets/peers.json`(600)，文档只留占位符。沙箱写系统临时目录并即删。
