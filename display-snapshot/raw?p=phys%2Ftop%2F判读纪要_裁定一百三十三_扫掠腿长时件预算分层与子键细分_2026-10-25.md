# 判读纪要 · 裁定一百三十三 · 扫掠腿长时件预算分层与 `PARAM_INEFFECTIVE_OUT` 子键细分

- 阶段：**143**（裁定一百三十三）｜时间：2026-10-25 UTC 03:32–03:52（本地 11:32–11:52）
- 性质：**只读现役面 · 零芯片动作**（未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层；未派工）
- 上口遗留项：扫掠腿细分 `PARAM_INEFFECTIVE_OUT` 子键 ＋ 长时件单独扫掠预算（消 `g2d_route_b_precheck` 抖动）——本口**已做**。

---

## 一、缘起与★实测根因（不靠推断）

上口在裁定一百二十九纪要里点名「`g2d_route_b_precheck` ~45 s 抖动」，但**未定位根因**。本口现算坐实：

| 实测项 | 数值 | 证据 |
|---|---|---|
| `g2d_route_b_precheck.run()` **单跑**实耗 | **41.0–41.2 s**（两次独立调用：42.7 s／41.0 s／41.2 s） | 本口现场计时（`/tmp/g2d_timing.log`）＋扫掠腿 `runs_elapsed` |
| 扫掠腿**默认单项预算** | **45 s** | `A1_SWEEP_ITEM_TIMEOUT` 默认 45 |
| 余量 | **~9 %**（41.2 s vs 45 s） | 同上 |
| 该件注册 timeout | 600 s | `$XUSEEK_HOME/data/skills.json` |

⇒ **根因一（预算撞线）**：用**统一 45 s 默认预算**去撞**实耗 41 s 的长时件** ⇒ 机器稍忙即越线 ⇒ 跨批判据在两态间跳。
历史三批实测即为三态：阶段 134 波三＝`EFFECT`／阶段 137 mini＝`UNOBSERVABLE`／阶段 134 heavy＝`NOT_RUN`。

⇒ **根因二（超时被吞）**：该件 `run()` 内部把 DRC/LVS 失败吞成 `{"verdict":"FAIL","error":…}` 并**返回**（不抛）。
探针的 SIGALRM 超时被这层 `except Exception` 吃掉 ⇒ 探针**看不到超时**，只看到「返回值含 `'error':`」⇒
判为 `UNOBSERVABLE`（早退不可观测）而非 `TIMEOUT` ⇒ 又一抖动源。

⇒ **根因三（全局预算饿死）**：长时件吃满**全局预算**后，后续项一律 `NOT_RUN`（不可判），长时件与短时件**共用一批预算**。

## 二、★三处修改（工具化，`tools/skill_param_probe.py`）

1. **★判据族子键细分**（`PARAM_INEFFECTIVE_OUT` 拆两子键，**族名/计数不变、消费端按前缀兼容**）：
   - `PARAM_INEFFECTIVE_OUT_NOT_LANDED` —— **正证据判死**：两跑均未落地指定输出文件；
   - `PARAM_INEFFECTIVE_OUT_ECHO_ONLY` —— **只回显判死**：输出路径型参数只回显未落地。
   ⇒ 原先把**两种不同证据强度**的判死压在同一 verdict 里，读的人无法区分来源。
2. **★长时件预算分层**：
   - **计量基准**：新增**单跑耗时**记录（`cap["elapsed_s"]` ⇒ `runs_elapsed`），profile 存**单跑最坏耗时**
     （不是整项两跑之和 —— 否则预算被放大一倍）；
   - **profile**：`playbook/_long_skill_profile.json`（每技能保留 8 个样本）⇒ 单项预算 = `p90 × 2.0`，
     下限 60 s、上限 600 s；长时件不再与短时件共用 45 s 默认预算；
   - **第二腿**：不可判项（`TIMEOUT`／`NOT_RUN`／`UNOBSERVABLE`／`INCONCLUSIVE_ERROR`／`ERROR`）**自动转第二腿**
     （长预算 240 s ＋ **独立预算池** 900 s，`A1_SWEEP_LEG2_ITEM_TIMEOUT`／`A1_SWEEP_LEG2_BUDGET`）
     ⇒ 长时件不再被全局预算饿死。
3. **★抖动显式披露**：结果项带 `legs`（两腿的判据/耗时/单项预算）与 `jitter` 布尔；两腿同判 ⇒ 记「判据跨批稳定」
   的正面证据；两腿异判 ⇒ `jitter=true` 并在 `detail` 里点名腿1/腿2。

**配套（消费端）**：`tools/stage137_hardening_selftest.py` 的 `KEYS_FAILS_ONLY_TRUE` 断言改为**族前缀匹配**
（`startswith("PARAM_INEFFECTIVE_OUT")` ＋ `family` 字段）；`CONTRACT_COVERAGE_SAME` 改为
「**旧键逐位不变** ＋ **新增键白名单**」两条（新增 `leg2_item_timeout_s`／`leg2_budget_s`／`leg2_run`／`jitter`／`long_items`）。

## 三、★实测四腿（`g2d_route_b_precheck` 两项：out／keep）

| 腿 | 设置 | 腿1判据 | 腿2判据 | 最终 | jitter |
|---|---|---|---|---|---|
| **legA**（冷 profile） | 默认 45 s 单项预算 | — | — | **EFFECT 2/2** | 0 |
| **legB**（暖 profile） | profile 预算 82 s | — | — | **EFFECT 2/2** | 0 |
| **legC**（负控·紧预算） | 20 s 单项预算 | `UNOBSERVABLE`（超时被吞） | `EFFECT` | **EFFECT 2/2** | **1**（已披露） |
| **legD**（负控·全局预算） | `A1_SWEEP_BUDGET=1` | `NOT_RUN` | `EFFECT` | **EFFECT 2/2** | **1**（已披露） |

- legA/legB 的 `runs_elapsed` 实测：41.0/41.2、41.1/40.9、41.0/40.9、40.7/41.0 ⇒ profile 样本 41.2/41.1/41.0/41.0。
- legB `long_items=2`（两项均按 profile 给 82 s 预算）⇒ **余量从 ~9 % 提到 ~100 %** ⇒ 撞线抖动消除。
- legC/legD 是**负控**：证明第二腿真能兜住「不可判」态，且**抖动被披露而非隐藏**。
- 四腿 `n_fail=0`；每腿覆盖诚实律：残余 2 ＝ 已判 2 ＋ 不可判 0 ＋ 未跑 0；终局清扫 0 残留／0 孤儿。

## 四、自检与回归

- 探针自检（`mode=selftest`）：**13/13 PASS**（静态 6 ＋ 扫掠 5 ＋ 端态 2）。
- 阶段 137 硬化自检：**14/14 PASS**（含 `KEYS_FAILS_ONLY_TRUE`（新子键）、`CONTRACT_COVERAGE_SAME`（旧键逐位不变＋新增键白名单））。
- `python3 -m py_compile` 通过；补丁脚本 `tools/stage143_sweep_harden_patch.py` **可重放**（改前版本已归档 `playbook/_archive/stage143/`）。

## 五、★自伤与工具事故（各 1 处，已当场消）

1. **★BOOT.md 阶段条目重复三次**：`cut -c` 在 C locale 下按**字节**截断 ⇒ 多字节字符被切断 ⇒ 工具输出 UTF-8
   解码失败 ⇒ **命令被重试** ⇒ 写文件的脚本被跑了两遍 ⇒ 143 条目重复 3 次。
   ⇒ 已用 `tools/stage143_boot_dedupe.py` 去重（143 行数=1、142 行数=1，chars 9336 ≤ 自设 12000）；
   ⇒ **教训两条**：①★工具输出截断须按**字符**（`cut -c` 与 `tail -c` 同族，扩展既有律）；
   ②★写文件的脚本必须**幂等**（命令可能被重试）。
2. **★探针超时被技能吞掉**（见根因二）：技能自身 `except Exception` 把 `_ProbeTimeout` 吃掉 ⇒ 探针判
   `UNOBSERVABLE` 而非 `TIMEOUT`。本口未改该技能（不代改他人口径/不改成员交付件），改为在扫掠腿侧
   以**第二腿**兜住并在 detail 里披露。

## 六、零动作与现役锚（本口现算）

- 现役四件 sha/bytes 逐位未变：mix `396571f0`/96,660｜drv1 `d5e1296c`/63,502｜drv2 `25adcbd1`/79,564｜顶层 `88d5d9c4`/237,672。
- 未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层／顶层网表；未派工；未上传冷备；未评估情形 B；未跑 Q3；
  M5 链件一概不动；**未执行 8510 取件钥轮换**（待管理员裁，未获令不动手）。
- 开跑首步核服务存活：**8510/8600 均 OK**（`service_liveness_gate` census PASS 4/0：件 476／一致 476／不符 0）。
- 收尾复读 `inbox.jsonl`：仍 **355 行／1,795,021 B** ⇒ 无新同伴信 ⇒ 未投回信。

## 七、★新立三律（已入 `playbook/BOOT_通用律库.md`）

1. **★长时件预算分层律** —— 统一默认预算撞长时件 ⇒ 跨批判据抖动；长时件须按**实测运行期**给单独单项预算，
   不可判项须**自动转第二腿**（长预算＋独立预算池），长时件不得与短时件共用一批预算。
2. **★抖动须显式披露律** —— 判据可能跨批不稳定时必须记录两腿判据（`legs`/`jitter`），不得只采一次结果；
   抖动未消解也要报告。
3. **★判据族须可分子键律** —— 同一 verdict 族内并存不同**证据强度**的判死 ⇒ 必须拆子键（族名不变、计数不变、
   消费端按前缀兼容）。

（另附两条工具纪律：★工具输出截断须按字符律（`cut -c`/`tail -c` 同族）；★写文件脚本须幂等律。）

## 八、下一步

1. ★**全舰队扫掠腿**在新预算分层下复跑一次（29 项残余面），取「抖动项数」与「第二腿触发项数」的**全量分布**——
   本口只对 `g2d_route_b_precheck` 两项做了四腿实测。
2. `PARAM_INEFFECTIVE_OUT_ECHO_ONLY` 子键在**全舰队**是否真的出现（此前波三只有 `ECHO_ONLY` 3 项）⇒ 需全量跑批确认。
3. 待管理员裁：①–㉚ 仍未回（末封仍 26795）⇒ 零销账；★㉕ 仍建议 **A ＝ 顶层自建 via 栈**。
   8510 file-key 轮换等令（不动手）。b7e7 在途 ④cdl 等情形 B（不催）。

---

**证据**：`playbook/_evidence_stage143/`（`sweep_g2d_legA.json`／`legB`／`legC_tight`／`legD_budget1` ＋各自 `.out`／
`skill_param_probe_selftest.json`／`stage137_hardening_selftest.json`／`service_liveness_gate.json`）；
**profile**：`playbook/_long_skill_profile.json`；**补丁**：`tools/stage143_sweep_harden_patch.py`（可重放）。
