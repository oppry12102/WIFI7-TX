# 判读纪要 · 裁定一百三十九 · 探针分辨率修复 ＋ 不可判项定向复测（阶段 149）

- 时间：2026-10-25 UTC 07:29–07:45（本地 15:29–15:45）
- 性质：**只读现役面 · 零芯片动作**（未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层；未派工）
- 改动面：**仅我方自有工具**（预言机 `tools/a1_domain_oracle.py` ＋ 探针 `tools/skill_param_probe.py` ＋ 两个新工具）
- 上口交接：阶段 148 收口后余 **9 项不可判**（基线 56 项）

## 一、缘起：9 项「不可判」不是参数无效应，而是探针结构性失明

阶段 148 全舰队扫掠（56 项）判据分布：EFFECT 45 ／ NO_EFFECT 2 ／ INCONCLUSIVE_ERROR 2 ／ UNOBSERVABLE 5 ／ ECHO_ONLY 2。
余下 9 项不可判逐条查因，**全部**落在探针/预言机的观测面缺陷上：

| 项（阶段 148） | 阶段 148 判据 | 实测根因 | 本阶段处置 |
|---|---|---|---|
| `peer_fetch_verify.dest` / `.out-json` / `.peer-base` | UNOBSERVABLE（早退） | 注册 schema 未标 required、无 default ⇒ 探针**只填 required** ⇒ 入口早退 | ★全参数合法基线填充律（预言机补值）⇒ **已判 EFFECT** |
| `peer_fetch_verify.items-json` | UNOBSERVABLE（早退） | 被测值取域外哨兵 ⇒ 工具读不到清单文件 ⇒ 早退 | 定向复测（真实清单 vs 去 sha 副本）⇒ **已判 EFFECT** |
| `peer_fetch_verify.peer-id` | UNOBSERVABLE（早退） | 域外哨兵 ⇒ `no peer_file_tokens` ⇒ SystemExit | 定向复测（fde9 有钥 vs b7e7 无钥）⇒ **已判 CONSUMED_REJECTED** |
| `fleet_runtime_probe.out_json` / `.selftest` | INCONCLUSIVE_ERROR（吞异常） | ★**嵌套输出污染**：该技能内层再探 `skill_param_probe`，内层的「★闸内异常:」标记出现在外层报告里 ⇒ 外层误判「吞异常」 | ★嵌套输出污染律（标记只在**输出开头**才算）⇒ 待阶段 150 批内复跑确认 |
| `sg13g2_sim.timeout` | NO_EFFECT（差分不证死） | 仿真远快于 timeout ⇒ 差分无差异 | 定向复测（先**校准真实耗时**再取必然绑定值）⇒ **已判 CONSUMED_REJECTED** |
| `chain64_residue_check.versions` | NO_EFFECT（域单点） | 格式模板 `G={sha8(prev)},H={sha8(live)}` ⇒ 域内只有一点 | 定向复测（正确映射 vs 缺当批 sha 的映射）⇒ **已判 EFFECT** |

## 二、本阶段做了什么（改动仅限我方自有工具）

1. **预言机 `tools/a1_domain_oracle.py`：`2c1e35e2` → `f93cdf95`（27,758 B）**
   - R5 描述示例正则**放行 ':'**（原 `如 http://…` 被截成 `http`）。
   - 新增 **R1c or 链末端默认**（`peer_id = kw.get("peer_id") or kw.get("peer-id") or "fde9"` ⇒ 取 `"fde9"`）。
   - 新增 **R5c 文档示例参数值**（`--items-json playbook/_peer_stage121/items.json` ⇒ 取**世界根绝对路径**，避免沙箱 cwd 下找不到）。
   - 预言机自检 **6/6 PASS**（不变）。
2. **探针 `tools/skill_param_probe.py`：`8307c634` → `461f8ff3`（119,7xx B）**
   - 新增 **★全参数合法基线填充律**：未标 required / 无 default 的兄弟参数也补**域内合法基线**（取不到就不填）。
   - 新增 **★写目标保护律**：描述含落盘/输出/存放/写入/回执/报告 ⇒ **不填活体路径**（防被测技能往现役目录写文件）。
   - 新增 **★嵌套输出污染律**：「★闸内异常:」只在**输出开头**出现才算「吞异常」。
   - 记录审计字段 `sibling_fills`（本次补齐了哪些兄弟基线）。
   - 探针自检 **16/16 PASS**（不变）。
3. **新工具 `tools/stage149_patch_instrument.py`**（幂等补丁器，14 处补丁 ＋ 编译自检）。
4. **新工具 `tools/stage149_targeted_retest.py`**（定向复测器：人工构造域内合法两值，判据与差分腿同口径 ＋ 落地证据 sha8/bytes 现算）。
5. **阶段 150 全舰队复跑批次已起**（`tools/stage150_sweep_worker.sh`，07:38:47Z 起，probe `461f8ff3`／oracle `f93cdf95`，三波与阶段 144/148 同口径）。

## 三、实测结果（可复核）

- 定向扫掠（仅 `peer_fetch_verify`，探针新件）：残余 5 项 ⇒ **已判 3**（dest／out-json／peer-base 均 EFFECT）＋ 不可判 2（items-json／peer-id 需定向复测）。
- 定向复测 4 项：**4/4 已判**（items-json EFFECT／peer-id CONSUMED_REJECTED／sg13g2_sim.timeout CONSUMED_REJECTED／chain64.versions EFFECT）⇒ **不可判 0**。
- 阶段 148 的 9 项不可判现状：**已判 7**（3 由仪器修复 ＋ 4 由定向复测）＋ **待批内确认 2**（fleet_runtime_probe ×2，嵌套输出污染律已修，待阶段 150 批内复跑）。
- 临时网表 `_s149_slow.sp` 与 ngspice 产物**用完即删**，`pdk/sim` 目录清单跑前跑后**逐项对拍一致**（零残留）。

## 四、下一步

1. **阶段 150 批次完工**（约 100 分钟）⇒ 与阶段 148 逐项对表（工具 `tools/stage148_compare.py` 改基线指向阶段 148）：不可判 9/56 能否再降、假 FAIL 是否绝迹、`contradictory_pids` 是否仍为 0。
2. 若 `fleet_runtime_probe` 两项仍不可判 ⇒ 定向复测收口（该技能自探自身 ⇒ 嵌套更深，须隔离跑批窗口）。
3. 待管理员待决 ①–㉚ 仍未回（末封仍 26795）⇒ 零销账；㉕ 仍建议 **A ＝ 顶层自建 via 栈**。

## 五、纪律自检

- 未改现役 GDS／网表／deck 字节；未产合并件；未建 pin 层／顶层网表；未派工；未评估情形 B；未跑 Q3；**M5 链件一概不动**；未执行 8510 取件钥轮换；常驻服务未启停。
- 对端只读 GET（未写对端任何字节）；凭据只从 `secrets/peers.json` 现取，不进日志/文档。
- 跑批与定向复测产物只写系统临时目录（用完即删）＋ `playbook/_evidence_stage149/`。
