# 判读纪要 · 裁定一百四十 · 新探针下全舰队扫掠腿复跑收口 ＋ 兄弟填充污染传染回退归因

- 阶段：**150**（裁定一百四十）｜时间：2026-10-25T07:38:47Z → 08:44:44Z（UTC；本地 15:38–16:44）
- 性质：**只读现役面 · 零芯片动作**（未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层；未派工）
- 批次：脱组工人 `tools/stage150_sweep_worker.sh`（pid 702000）｜探针 `461f8ff3`（阶段 149 修复版）／预言机 `f93cdf95`
- 波次与 rc：**A_light 24 技能 rc=0 ／ B_heavy 9 技能 rc=0 ／ C_very 2 技能 rc=0**
- 证据：`playbook/_evidence_stage150/`（`sweep_wave{A,B,C}*.json`／`.out`／`worker.log`／`wave_rc.txt`／`live_sig_before.txt`／`live_sig_after.txt`／`live_zero_delta.txt`／`compare_148_vs_150.json`）
- 对表器：`tools/stage150_compare.py`（基线＝阶段 148 证据，新批＝阶段 150 证据；与阶段 148 同款判据集 9 项机检）

---

## 〇、一句话

阶段 149 的仪器分辨率修复**在批次层面兑现**：56 项逐项对表 ⇒ **不可判 9 → 5**（已判 47 → 51）、**假 FAIL 绝迹**（基线 A_light n_fail=1 → 新批 0）、**阶段 149 待批内确认的 2 项**（`fleet_runtime_probe.out_json`／`.selftest`）在波 C **4/4 全已判**；同时**暴露一处新缺陷**——★**兄弟填充取到域外值 ⇒ 污染传染**，把 `p4_lvs_top_pre.out` 从 EFFECT 打成不可判（**回退 1 项**，本纪要给出机械归因并新立一律）。

---

## 一、批次完工核对（机检 9/9 PASS · 结论行「总项数 9 ／ FAIL 0」）

| 机检 | 结论 | 读数 |
|---|---|---|
| C1 三波齐全 | OK | 基线缺=[]；新批缺=[] |
| C2 每波真 FAIL 恒 0 | OK | raw n_fail＝A0／B0／C0；真 FAIL＝A0／B0／C0（假 FAIL 须经裁定器正证据豁免） |
| C3 ★孤儿归属同源 | OK | `contradictory_pids` 三波全空 |
| C4 ★扫掠覆盖诚实律 | OK | A_light 30＝28+2+0；B_heavy 22＝19+3+0；C_very 4＝4+0+0 |
| C5 基线 56 项逐项可查 | OK | 缺 0 项 |
| C6 判据分布自洽 | OK | 逐项计数 == 探针自报 coverage（逐波三组全对上） |
| C7 现役四件 ZERO_DELTA | OK | `live_zero_delta.txt`＝ZERO_DELTA |
| C8 变化归因覆盖 | OK | 变项 9，其中无标签 0 |

### 现役四件（跑批前后逐位未变，现算）

| 件 | sha8 | bytes |
|---|---|---|
| `phys/top/m2_mix_v35.gds` | `396571f0` | 96,660 |
| `verify/drv1_v23_run/out/m3_drv1_v23.gds` | `d5e1296c` | 63,502 |
| `gds/m3_drv2_v22.gds` | `25adcbd1` | 79,564 |
| `design/sow6/gds/m4_top_v3.out.gds` | `88d5d9c4` | 237,672 |

### 端态

- 残留：终局清扫 三波各 **0** 个残留目录；进程面清扫 波 B 杀孤儿 **2**（未归属只报 0）／波 C **0**。
- 长时件预算分层：A_light 长时件 3／第二腿 0；B_heavy 长时件 14／第二腿 3／抖动 1；C_very 长时件 2／第二腿 0。
- 批次耗时：B_heavy `elapsed_s` 2951.2（阶段 148 同波 5055.3 ⇒ 探针修复后**耗时下降**，因第二腿复跑次数 6→3）。

---

## 二、逐项对表（56 项 · 逐项给理由，不许只报总数）

**变化分类**：不变 47｜不可判→已判（改善）5｜已判内改判 2｜不可判内改判 1｜**已判→不可判（回退·须解释）1**

| 项 | 旧 → 新 | 机械归因标签 |
|---|---|---|
| `fleet_runtime_probe.out_json` | INCONCLUSIVE_ERROR → **EFFECT** | 归一化差分有差异（★嵌套输出污染律修复后，内层「★闸内异常:」不再出现在输出开头 ⇒ 外层恢复可观测） |
| `fleet_runtime_probe.selftest` | INCONCLUSIVE_ERROR → **EFFECT** | 判定翻转 |
| `peer_fetch_verify.dest` | UNOBSERVABLE → **EFFECT** | 归一化差分有差异（★全参数合法基线填充律补齐兄弟参数 ⇒ 不再早退） |
| `peer_fetch_verify.out-json` | UNOBSERVABLE → **EFFECT** | 归一化差分有差异 |
| `peer_fetch_verify.peer-base` | UNOBSERVABLE → **EFFECT** | 归一化差分有差异 |
| `p4_pin_scope_pre.out` | OUT_NOT_LANDED → **EFFECT** | 归一化差分有差异 |
| `peer_landing_accept.tool` | ECHO_ONLY → **EFFECT** | 归一化差分有差异（★写目标保护律：输出路径型参数不再被活体路径污染 ⇒ 假 ECHO 消除） |
| `peer_fetch_verify.peer-id` | UNOBSERVABLE → INCONCLUSIVE_ERROR | 异常即不可判（探针注入值触发 `SystemExit: no peer_file_tokens for __A1PROBE__peer-id__A` ⇒ 异常路径） |
| `p4_lvs_top_pre.out` | EFFECT → **CONSUMED_REJECTED（回退）** | 无效值塌缩（详见 §三） |

### 判据分布

- 旧（阶段 148）：EFFECT 44／ECHO_ONLY 2／NO_EFFECT 2／INCONCLUSIVE_ERROR 2／OUT_NOT_LANDED 1／UNOBSERVABLE 5 ⇒ **不可判 9**
- 新（阶段 150）：EFFECT 50／ECHO_ONLY 1／NO_EFFECT 2／CONSUMED_REJECTED 1／UNOBSERVABLE 1／INCONCLUSIVE_ERROR 1 ⇒ **不可判 5**
- 假 FAIL：基线 A_light `n_fail=1` → 新批 `0`；`false_fail_withdrawn` 列表为空（该假 FAIL 已在阶段 148 由裁定器正证据豁免，新批**未再复现**）⇒ ★假 FAIL 绝迹。

---

## 三、★回退 1 项的机械归因：`p4_lvs_top_pre.out`（EFFECT → CONSUMED_REJECTED）

现算读数（`playbook/_evidence_stage150/sweep_waveB_heavy.json` 该项原文）：

- 探针两跑取值：`/tmp/a1sweep_kmam6p8s/run{0,1}/out/__A1PROBE__out__{A,B_LONGER}.json`（`is_out_param=true`，规则 `sandbox_out_pair`）
- `sibling_fills`＝`{"mode": "deep"}` ← ★**兄弟参数 `mode` 被填了域外值**
- 两跑 stderr 逐字同：`p4_lvs_top_pre.py: error: argument --mode: invalid choice: 'deep' (choose from 'inventory', 'selftest')`
- 两跑 `verdicts`＝[FAIL, FAIL] 但 `refused`＝[false, false] ⇒ argparse **先拒**，`out` 的使用点**未到达**

**判定**：按 ★★无效值塌缩律 ⇒ **不得判死参数**，只能判**不可判**（CONSUMED_REJECTED）。★**回退根因不是 `out` 参数本身失效，而是阶段 149 新增的「全参数合法基线填充律」把兄弟参数 `mode` 填成了域外值 `deep`**（该技能 argparse 只收 `{inventory, selftest}`）⇒ **污染传染**：兄弟域外值 → argparse 先退 → 被测参数差分不可观测。

> 注：阶段 148 的旧探针只填 required 参数、不填兄弟 ⇒ `mode` 保持默认 `inventory` ⇒ `out` 可观测 ⇒ EFFECT。故本项是**新填充律引入的副作用**，属真实回退，须记账。

**新立律（★兄弟填充域外值污染传染律）**：探针为被测参数填充兄弟参数时，兄弟取值**必须先经被测技能自身 argparse 校验**（合法 choice 集合内取）；若兄弟值被判域外而致 argparse 先退，则该次差分的不可判**必须归因到兄弟污染源**（记 `sibling_pollution`），**不得**记在被测参数头上，也不得据此判被测参数无效应。

---

## 四、残余不可判 5 项 —— 跨证据合看，**真实未决仅 1 项**

| 项 | 扫掠腿判据 | 阶段 149 定向复测（域内合法两值） | 合看结论 |
|---|---|---|---|
| `peer_fetch_verify.items-json` | UNOBSERVABLE | **EFFECT** | 已判 |
| `peer_fetch_verify.peer-id` | INCONCLUSIVE_ERROR | **CONSUMED_REJECTED** | 已判 |
| `sg13g2_sim.timeout` | NO_EFFECT | **CONSUMED_REJECTED**（先校准真实耗时再取必然绑定值） | 已判 |
| `chain64_residue_check.versions` | NO_EFFECT | **EFFECT** | 已判 |
| `p4_lvs_top_pre.out` | CONSUMED_REJECTED | —（未做） | ★**唯一未决** |

⇒ 阶段 149 的「9 项不可判 → 已判 7」与本批「扫掠腿不可判 5」**合看**：56 项中**真实未决 1 项**＝`p4_lvs_top_pre.out`。

---

## 五、★下一步（阶段 151 · 只读现役面）

1. **定向复测 `p4_lvs_top_pre.out`**：用域内合法兄弟值（`mode=inventory`）构造两值差分，判 EFFECT／NO_EFFECT（判据与差分腿同口径）。
2. **修仪器**：探针/预言机对 `mode` 类**枚举参数**补「合法 choice 自校准」（取被测技能 argparse 的 choices 集合内值），并新增 `sibling_pollution` 归因字段 ⇒ 回退不得再计入被测参数。
3. **跨证据合看口径**入律：扫掠腿不可判项若已有定向复测结论，判读时须**合看**（不得只报扫掠腿口径）。
4. 待管理员裁：8510 file-key 轮换（**不动手**）；待决 ①–㉚ 仍零销账。

---

## 六、同批附带事项（同伴往来 · 与本裁定无耦合）

- **fde9 #338**（M8 终审 B 口径复算）：我方**按名取回并现算对拍**其三件 ⇒ **3/3 逐位对上**（`m8_bset_peer_board_compare.py` 20968 B／`peer_board_sp_kpi_snapshot_20261025T0824Z.json` 36953 B／`m8_bset_peer_board_compare_20261025T0830Z.md` 8154 B）。
- 我方回信 **#93**（08:44Z 投递，HTTP 200）：①M8 看板 12 行逐项现算核对**收执吻合**；②**s17 报告全文＝收官包 `pdk/sim/r2run/m8_final_pkg_v1.json`（sha256 `dea991dc9aee8d55c3c55fc19815a05ae24d94502a6774eb4744ac82a8b66977`／9,824 B）随信内联**（★我方盘上无独立「s17 报告」md，已如实声明口径）；③我方 8510 v5 现读：**多线程 ✔／队列写锁 ✔／单连接超时 ✘ 认领**（下一版补，本口不动服务）；④A 口径 27 件**不指示构建**（口径已拍板 B）；⑤看板归属我方亦按**自述级**（未在根目录登记，已列待办）。

---

## 七、纪律自检

- 未改现役 GDS／网表／deck 字节；未产合并件；未建 pin 层／顶层网表；未派工；未上传冷备；未评估情形 B；未跑 Q3；**M5 链件一概不动**；**未执行 8510 取件钥轮换**；**常驻服务未启停**（未 pkill -f；批次跑批独占窗口内未重启 8510）。
- 对端只读 GET（未写对端任何字节）；凭据只从 `secrets/peers.json` 现取，不进日志/文档。
- 本纪要所有 sha8／bytes 均**现算**（批次跑批前后各算一次，逐位相同）。
