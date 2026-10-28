# 判读纪要 · 裁定一百二十五 · 差分扫掠腿判据硬化（假 FAIL 归零）

- **阶段**：135（承接 134 · 裁定一百二十四）
- **日期**：2026-10-25（UTC 2026-10-24T23:51Z 起）
- **范围**：只读现役面 · 零动作（未改现役四件 GDS/网表/deck 字节；未产交付面合并件；未建 pin 层／顶层网表；未派工；未上传冷备）
- **主人**：b7a0（WiFi7-TX 组长）

---

## 一、缘起：波二的 3 项 FAIL 全是假 FAIL

阶段 134 波二（21 件／36 项）实测结论行「总项数 36 ／ FAIL 3」，判据为 `NO_EFFECT`：

| # | 技能.参数 | 波二判据 | 源码复核（人工定向） | 真相 |
|---|---|---|---|---|
| 1 | `sg13g2_sim.timeout` | NO_EFFECT（FAIL） | `skills/sg13g2_sim.py` L11 `timeout = int(kwargs.get("timeout", 120))`、L26 `subprocess.run(..., timeout=timeout)`、L34 错误文案含 timeout | **参数确被读取**；但 `netlist` 是必填、探针未注入 ⇒ 技能在 L13 `if not netlist:` 处**早退** ⇒ 参数使用点**根本没到达** ⇒ 差分无差异只说明「没走到那一步」 |
| 2 | `g1_short_locator.out` | NO_EFFECT（FAIL） | `tools/g1_short_locator.py` L790 `outp = ROOT / args.out`、L819-820 `_skill_argv` 转发 `--out` | **参数确被读取**；但探针超时（`_ProbeTimeout`）被技能**内部 except 吞掉**（L859 打印「★闸内异常: _ProbeTimeout:」并返回失败 dict）⇒ 探针层 `raised=None` ⇒ 差分无差异是「两跑同早退」 |
| 3 | `g1_drc_precheck.keep_tmp` | NO_EFFECT（FAIL） | `tools/g1_drc_precheck.py` L538 `if getattr(args, "keep_tmp", False)`、L597 `if kw.get("keep_tmp")` | 同上：参数确被读取，探针超时被吞 ⇒ 假 FAIL |

**判据缺陷的性质**：「两跑无差异 ⇒ 参数被丢弃」是**过强推论**。差分腿是**观测工具**，
它的阴性结果**不构成「参数无效」的证据**（★类比：阴性只说明没测到）。此前把阴性当阳性，
造成 3 起假 FAIL。

同时复核出另外 3 项 `ECHO_ONLY`（`m4_drc_rerun.mode`、`p4_lvs_top_pre.mode`、`g1_short_locator.sweep`）
实为 **argparse 域外拒绝**（`invalid choice`）——按阶段 134 已立的「无效值塌缩律」应记
`CONSUMED_REJECTED`（不可判），误记 `ECHO_ONLY` 会暗示「只回显不使用」，与事实相反。

---

## 二、判据硬化（六处改动 · 补丁 `tools/stage135_sweep_harden_patch.py`，幂等）

| 改动 | 内容 | 对应新律 |
|---|---|---|
| ① 差分不证死 | `NO_EFFECT` 由判死降为**不可判（INFO）**；差分腿仅保留**正证据**判死 `OUT_NOT_LANDED`（输出路径型两跑均未落地） | ★★差分不证死律 |
| ② 早退识别 | 两跑返回体含 `error` ⇒ `UNOBSERVABLE`（不可判） | ★早退不可观测律 |
| ③ 吞异常识别 | 输出含「★闸内异常:」⇒ `INCONCLUSIVE_ERROR`（不可判） | ★闸内吞异常不可观测律 |
| ④ argparse 归类 | `usage:`／`invalid choice:` ⇒ `CONSUMED_REJECTED`（不可判） | ★argparse 域外拒绝归类律 |
| ⑤ 超时收割 | 超时点 `SIGKILL` 自己的子进程（`/proc` 扫 PPid） | ★差分腿超时收割子进程律 |
| ⑥ 沙箱早退泄漏 | 沙箱**登记** ＋ 扫掠腿每项跑完**统一二次清扫**（含重试） | ★扫掠沙箱早退泄漏律 |

另：`BaseException` 兜底（argparse 的 `SystemExit` 属 `BaseException`，旧 `except Exception` 抓不到 ⇒ 会掀翻整条腿）；
覆盖口径改三分解互斥同屏（★★扫掠覆盖诚实律 135 版）。

**判据集定稿（九项）**：`EFFECT`／`ECHO_ONLY`／`OUT_NOT_LANDED`（唯一正证据判死）／
`NO_EFFECT`（不可判·INFO）／`CONSUMED_REJECTED`／`UNOBSERVABLE`／`INCONCLUSIVE_ERROR`／`TIMEOUT`／`ERROR`／`NOT_RUN`。

---

## 三、实测

| 项 | 结果 |
|---|---|
| 闸自检（阶段 133 六项 ＋ **阶段 135 新增扫掠腿五项校准**） | **11/11 PASS**（结论行「总项数 11 ／ FAIL 0」） |
| 扫掠腿标定（新腿） | **6/6 PASS**：dead_transit→NO_EFFECT／alive_transit→EFFECT／echo→ECHO_ONLY／early_exit→UNOBSERVABLE／swallowed→INCONCLUSIVE_ERROR／argparse_reject→CONSUMED_REJECTED |
| 阶段 133 差分标定（旧腿未改动，回归） | **3/3 PASS** |
| 静态全量回归 | 36 件／125 参数 **FAIL 0**；腿T 覆盖同前：可判 73（alive 73／dead 0）／不可判 37／未涉及 15 |
| 舰队自审 live | **36/36 PASS**（硬闸缺 0；覆盖 36/36；A1=0 A2=0 A3=0 A4=0） |
| 波三重测（重件 13 件／长预算） | 见 `playbook/_evidence_stage135/sweep_wave3.json` |

★**自伤登记（据实）**：闸自检首轮 **10/11**（负控 `sweep_argparse_reject` 判 ERROR 而非 CONSUMED_REJECTED）
—— 根因是**夹具自身的转义缺陷**（`\\n` 写入夹具后成为真实换行 ⇒ 夹具语法错 ⇒ 模块加载失败），
非闸缺陷；修夹具后 11/11。★该次失败被闸自检自身抓到（未外溢）。

---

## 四、副作用与残留（本口实测）

- 阶段 134 波二遗留：`/tmp/a1sweep_*` **12 个残留**（5 个含产物）＋ `phys/drc/tmp_stage97_b_hvrhl2` 15 个文件
  ＋**孤儿 klayout 进程**（PID 70326，存活 1675 s，持续占 CPU）—— 根因分别是
  早退不经 `rmtree` 与超时后子进程成孤儿（见新律⑤⑥）。**本口已清扫归零**。
- 清理动作：SIGKILL 孤儿进程链（69908/69912/70325/70326）＋ `rm -rf` 上述两处残留；
  现役四件与 PDK **零改动**（字节未动）。

---

## 五、零动作与纪律

未改现役四件与任何现役 GDS／网表／deck 字节；未产交付面合并件；未建顶层 pin 层／顶层网表；
未派工；未上传冷备；未评估情形 B；未跑 Q3；M5 链件一概不动；**未执行 8510 取件钥轮换（待管理员裁）**。
凭据只在 `secrets/peers.json`(600)；文档只留占位符；沙箱写系统临时目录并即删。
