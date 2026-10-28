# 判读纪要 · 裁定一百三十八 · 全舰队扫掠腿复跑 · 逐项对表 · 假 FAIL 机械裁定与守卫方向修复

- 日期：2026-10-25（UTC 05:41–07:26；本地 13:41–15:26）
- 阶段：**148**（承接阶段 144 基线、阶段 147 判据细化）
- 性质：**只读现役面 · 零芯片动作**（未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层；未派工）
- 改动面：**仅我方自有工具**（跑批脚本／对表器／裁定器／探针／预言机）
- 证据面：`playbook/_evidence_stage148/`（证据目录，非现役芯片面）

---

## 〇、三句话

1. **复跑完成并逐项对表**：阶段 144 基线 56 项 → 新批 56 项，**不可判 18/56 → 9/56**（−9，全部为改善），**真 FAIL 恒 0**，`contradictory_pids` 三波全空，现役四件跑批前后 **ZERO_DELTA**；56 项中 44 项不变、12 项变，**12 项全部有机械归因**（C8 由「只报数」升级为「无标签即 FAIL」后仍全绿）。
2. **抓到并撤销 1 条假 FAIL**：`p4_pin_scope_pre.out` 被探针判「输出路径未落地 ⇒ 判死参数」，实为**兄弟守卫方向反转**造成的观测面失真；机械反证＝守卫关闭后 2/2 跑落地（sha8 `77e05fa3`／`a8d59bbb`，各 41,620 B）⇒ 该参数**真被使用** ⇒ 原 FAIL 撤销，判据恢复「已判」。
3. **根因已修并定向复测**：预言机 `ast.walk` 把 `orelse`（互补分支）也算进守卫分支 ⇒ 方向反转；改为 body／orelse 分账 + `where=branch|complement` + 探针按方向取兄弟值 ⇒ 自检 **预言机 6/6 ／ 探针 16/16**，定向复测 `p4_pin_scope_pre` ⇒ **EFFECT、FAIL 0**（假 FAIL 不再复现）。

---

## 一、跑批口径（与阶段 144 逐项同口径，保证判据可比）

| 项 | 值 |
|---|---|
| 探针 | `tools/skill_param_probe.py`，批次用 sha `59f93b0f`（阶段 147 打补丁后那份，已核） |
| 波划分 | A_light 24 技能／B_heavy 9／C_very 2（与阶段 144 **同一集合**，同口径） |
| 单项超时 | 45 s ／ 900 s ／ 2400 s（**与基线同值**⇒ 判据可比） |
| 全局预算 | 3600／14400／28800 s，第二腿池 2400／10800／21600 s（**×1.5／×2 上调**⇒ 新判据多腿不被预算截断） |
| 起止 | 2026-10-25T05:41:23Z 起 → 07:20:03Z 止（波 A 3m59s／波 B 84m16s／波 C 10m25s） |
| 波退出码 | A=1／B=0／C=0（A 的 1＝批内 1 条 FAIL，已由裁定器撤销为假 FAIL） |
| 现役四件 | 跑批前后各现算一次 sha/bytes ⇒ **ZERO_DELTA**（`live_zero_delta.txt`） |

**跑批期运行观察（运维向）**：脱组工人（pid 533361）完工**未见事实账 bell 行**（`facts_since` 全类型扫描无 worker 行）⇒ ★**不能只等铃**，下口须轮询 `playbook/_evidence_stage148/worker.log` 与 `wave_rc.txt` 判完工（本口即如此取得完工信号）。

---

## 二、逐项对表（阶段 144 基线 vs 阶段 148 新批）

**判据分布**

| | EFFECT | ECHO_ONLY | NO_EFFECT | UNOBSERVABLE | INCONCLUSIVE_ERROR | CONSUMED_REJECTED | OUT_NOT_LANDED |
|---|---|---|---|---|---|---|---|
| 基线 144 | 38 | 0 | 1 | 9 | 5 | 3 | 0 |
| 新批 148（原始） | 44 | 2 | 2 | 5 | 2 | 0 | 1 |
| 新批 148（**裁定后生效**） | **45** | 2 | 2 | 5 | 2 | 0 | **0** |

⇒ **不可判 18/56 → 9/56（32.1% → 16.1%）**；**真 FAIL 0**（原始 1 条已撤销）。

**12 个变项逐条归因（全部机械标签，无「无标签·须人工」）**

| 项 | 旧 → 新 | 归因（探针原文标签） |
|---|---|---|
| `g1_short_locator.sweep` | CONSUMED_REJECTED → EFFECT | 归一化差分有差异 |
| `m4_drc_rerun.mode` | CONSUMED_REJECTED → EFFECT | 判定翻转 |
| `p4_lvs_top_pre.mode` | CONSUMED_REJECTED → EFFECT | 归一化差分有差异 |
| `peer_landing_accept.mode` | INCONCLUSIVE_ERROR → EFFECT | 归一化差分有差异 |
| `peer_landing_accept.tool` | NO_EFFECT → ECHO_ONLY | 回显≠使用 |
| `service_liveness_gate.mode` | INCONCLUSIVE_ERROR → EFFECT | 归一化差分有差异 |
| `skill_fleet_audit.json_out` | UNOBSERVABLE → EFFECT | 归一化差分有差异 |
| `skill_fleet_audit.registry` | UNOBSERVABLE → ECHO_ONLY | 回显≠使用 |
| `skill_fleet_audit.selftest` | UNOBSERVABLE → EFFECT | 归一化差分有差异 |
| `chain64_residue_check.versions` | INCONCLUSIVE_ERROR → NO_EFFECT | 域单点不可判（诚实结论） |
| `sg13g2_sim.timeout` | UNOBSERVABLE → NO_EFFECT | 差分不证死（诚实结论） |
| `p4_pin_scope_pre.out` | EFFECT → OUT_NOT_LANDED ⇒ **撤销，恢复 EFFECT** | 假 FAIL 撤销·守卫方向反转 |

**九道机器校验（全绿）**：C1 三波齐全｜C2 每波**真** FAIL 恒 0（假 FAIL 须裁定器正证据豁免）｜**C9 守卫方向反转项在批内逐条有裁定记录**｜C3 `contradictory_pids` 三波全空｜C4 扫掠覆盖诚实律（30=28+2、22=17+5、4=2+2）｜C5 基线 56 项逐项可查（缺 0）｜C6 判据分布自洽｜C7 现役四件 ZERO_DELTA｜**C8 变项逐条命中机械归因标签（无标签即 FAIL）**。

---

## 三、★假 FAIL 的发现与机械裁定

### 3.1 现象

波 A 报出 1 条：

```
[真FAIL][PARAM_INEFFECTIVE_OUT_NOT_LANDED] p4_pin_scope_pre.out
  两值差分无差异，且指定输出路径在两跑均未落地 ⇒ 输出路径型参数确未生效（正证据）⇒ 判死参数
```

两跑 stdout 均为 `结论行: 总项数 3 ／ FAIL 0`（**3 项**＝技能 selftest 路径的负控项数），而该技能正常口径应为 **33 项校验**。

### 3.2 根因（静态定位，机械可复现）

预言机 `tools/a1_domain_oracle.py` 的 `visit_If` 用 `ast.walk(node)` 收「守卫分支内被使用的参数名」——而 `ast.walk` 对 `If` 节点**同时遍历 `body` 与 `orelse`** ⇒

> 「参数其实在**互补分支**被消费」被误判成「参数只在**守卫分支内**被消费」。

`p4_pin_scope_pre.py` 的实际结构：

```python
out = kw.get('out') or (EV + 'p4_pin_scope_pre.json')
if mode == 'selftest':
    return selftest()          # ← 守卫分支：**不**消费 out
R = inventory(out_json=out)    # ← 互补分支：消费 out
```

⇒ 探针据「守卫=mode:'selftest'」把 `mode` 设成 `selftest` ⇒ **out 的消费点不可达** ⇒ 两跑都不落盘 ⇒ 「未落地」信号**由兄弟守卫产生，与 `out` 无关** ⇒ 假 FAIL。

全注册表守卫方向审计：**17 条守卫应用中 3 条方向反转**——`p4_pin_scope_pre.out`（mode='selftest'）、`merge_fingerprint.gds`（mode='baseline'，实际消费点在 `check` 分支）、`fleet_hygiene_census.only`（mode='selftest'，消费点在 census 路径）。

### 3.3 机械裁定（正证据）

新工具 `tools/stage148_fail_adjudicator.py`：对每个 FAIL 项做**四跑**对照——① 历史口径复现（兄弟＝守卫值）② 守卫关闭（兄弟去掉 / 取域内合法非守卫值），各跑两个探针值 ⇒ 落地与否**现算 sha256/bytes**。

| 跑法 | 落地 | stdout 尾 | 结论 |
|---|---|---|---|
| 历史口径（`mode='selftest'`） | **0/2** | `结论行: 总项数 3 ／ FAIL 0` | 消费点不可达（退化分支） |
| 守卫关闭（`mode` 去掉 → 技能自身默认 `inventory`） | **2/2** | `校验 33 项：PASS 33 / FAIL 0；负控 3 项 PASS 3 … 结论行: 总项数 33 ／ FAIL 0` | **参数真被使用** |

落地件 sha8/bytes：`77e05fa3`／41,620 B、`a8d59bbb`／41,620 B ⇒ **判 FALSE_FAIL_GUARD_DIRECTION（假 FAIL）⇒ 撤销**，真 FAIL 计 0。

---

## 四、修复与定向复测

### 4.1 修复（两处，均为我方自有工具）

1. **预言机 `tools/a1_domain_oracle.py`**：`visit_If` 改为 **body（守卫分支）与 orelse（互补分支）分开记账**；`sibling_guard()` 返回 `where=branch|complement`，**优先 branch 候选**（更贴近「参数在哪被消费」），无 branch 才用 complement。
2. **探针 `tools/skill_param_probe.py`**：`_build_probe_kw` 按 `where` 取兄弟值——`branch` ⇒ 取守卫值；`complement` ⇒ 取**域内合法非守卫值**（注册 schema 默认 → 预言机合法基线），取不到则去掉该键让技能走自身默认；决策记入 `guard_note`／`guard` 字段（审计可追）。

### 4.2 复测

| 复测项 | 结果 |
|---|---|
| 预言机自检 | **6/6 PASS**（`ORACLE_R7_SIBLING_GUARD` 现返回 `where=branch`） |
| 探针自检 | **16/16 PASS**（含 `SWEEP_ORACLE_SIBLING`） |
| 定向重跑 `p4_pin_scope_pre` | **EFFECT ／ FAIL 0**（假 FAIL 不再复现） |
| 修复后守卫表 | 17 条：15 条 `branch`、2 条 `complement`（`p4_pin_scope_pre.out`、`fleet_hygiene_census.only` ⇒ 探针改取 `mode='inventory'`／`mode='census'`） |

### 4.3 未动的两处（诚实记录）

- 探针 `sweep` 的**输出路径型 FAIL 规则本身**未改（仍保留「未落地 ⇒ 判死」），因为修的是**观测面失真的成因**（守卫方向），且加了独立裁定器做后手闸；下一批将不再触发假 FAIL。
- `fleet_hygiene_census.only` 的动态腿在 census 口径下较重，本口**未**对其做动态复测（该项不在本批残余集内）；已在守卫表中标注方向，下批自动按 `mode='census'` 测。

---

## 五、新立四律（入 `playbook/BOOT_通用律库.md`）

1. **★守卫方向反转律** —— 静态判定「参数在守卫分支内被消费」时，**必须把 `orelse`（互补分支）与 `body` 分账**（`ast.walk` 会把两者混同）；否则探针会把兄弟设成守卫值而**关掉**消费点 ⇒ 差分观测不到参数 ⇒ 假 FAIL。
2. **★兄弟守卫方向取值律** —— 守卫方向＝互补时，兄弟参数必须取**域内合法且非守卫值**；不得用守卫值（那等于关掉消费点）。
3. **★假 FAIL 正证据撤销律** —— 凡报「输出路径未落地 ⇒ 判死参数」，须有**正证据**方可定案：守卫关闭后落地（sha/bytes 现算）⇒ 判**假 FAIL**并撤销；两态皆不落地 ⇒ 才是真 FAIL。撤销须逐条留证，不得口头豁免。
4. **★机械归因标签须穷尽律** —— 变化项若无任何机械归因标签 ⇒ **判 FAIL**（不得以「已显式标无标签」放行）；标签表须穷尽探针自述的判据原文（本次补入「归一化差分有差异」后，6 项「无标签」归零）。

---

## 六、纪律自检

- 现役四件本口现算逐位未变：mix `396571f0`/96,660｜drv1 `d5e1296c`/63,502｜drv2 `25adcbd1`/79,564｜顶层 `88d5d9c4`/237,672（跑批前后各一次，`live_zero_delta.txt`＝ZERO_DELTA）。
- 未改现役 GDS／网表／deck 字节；未产合并件；未建 pin 层／顶层网表；未派工；未上传冷备；未评估情形 B；未跑 Q3；**M5 链件一概不动**；**未执行 8510 取件钥轮换**；常驻服务未启停（未 pkill -f）。
- 裁定器与对表器的临时跑批件只写系统临时目录并即删（残留清扫：波 A/B/C 均「清除残留目录 0 个」）。
- ★待决零销账：管理员 ①–㉚ 仍未回（末封仍 26795）；㉕ 仍建议 **A ＝ 顶层自建 via 栈**；8510 file-key 轮换待管理员裁（我方未动手）。

---

## 七、遗留与下口

1. **下批（新探针 sha `8307c634`／预言机 sha `2c1e35e2`）全舰队复跑**：验证「不可判 9/56」能否进一步下降、假 FAIL 是否绝迹、`contradictory_pids` 仍为 0。
2. **`fleet_hygiene_census.only` 动态复测**（census 口径较重 ⇒ 单项跑，不并入整批）。
3. **归因标签表仍可能漏项**：下批若再出现「无标签·须人工」，须当场补标签或点名转人工（C8 已改为「无标签即 FAIL」）。
4. **跑批完工信号**：脱组工人完工**未见 bell 行** ⇒ 下口不得只等铃，须轮询 `worker.log`／`wave_rc.txt`。
