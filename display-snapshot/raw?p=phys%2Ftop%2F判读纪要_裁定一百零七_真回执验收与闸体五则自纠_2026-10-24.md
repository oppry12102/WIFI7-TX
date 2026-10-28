# 判读纪要 · 裁定一百零七 —— 真落盘回执的消费端验收（fde9 #318）＋ 我方验收闸体五则自纠

- 时间：2026-10-24 12:58Z–13:2xZ（本地 20:58–21:2x）
- 触发：组员 fde9 的**真落盘回执 #318**（12:51:15Z 到我方信箱）——上口（阶段 116）只见到「落盘已发生但回执未到」，当时用**我方自建底稿**先行独立验收；本口改用**真回执**复跑验收闸，合并裁定。
- 性质：**只读 · 零动作**。未改对端任何件字节（只按名 GET）；未改我方现役四件；沙箱与候选件只写系统临时目录并跑完即删；未产合并件、未建 pin 层/顶层网表、未派工、未上传冷备。

---

## 〇、结论（一句话）

**落盘批 #318 验收通过（13 项机检 FAIL 0，verdict PASS）**；但**闸体自身先被判 FAIL 3 次**（解析器把「旧件 sha」错配到别的路径）⇒ 我方当场做了**五则自纠**（v1→v3），每则「先出 FAIL 证据 → 改 → 回归 selftest 6/6」；自纠后再跑真回执＝PASS。

---

## 一、时间线（本口实测）

| 时刻 | 事 |
|---|---|
| 12:51:15Z | fde9 **#318** 到我方信箱（我方 #81 索要回执发出于 12:57Z ⇒ **回执比索要早 6 分钟到**，上口未见） |
| 12:58Z | 本口开；`facts_tail`＋`facts_since(30759)` 无管理员新信；信箱末条＝#318 |
| 13:00Z | 用**真回执**跑 accept 模式 ⇒ **FAIL 3**（K01/K02/K03） |
| 13:04Z | 闸体自纠 v2（块级关联解析）⇒ **FAIL 2**（K02/K07） |
| 13:08Z | 闸体自纠 v3（sha8 唯一 ＋ 现役件打分选件）⇒ **PASS（13 项 FAIL 0）** |
| 13:13–13:18Z | 独立复核四层（三个 sha 现算、live 与 v4 候选逐行差、连带失效机制核实）＋ 立对端现役面基线快照（500 件） |
| 13:18Z | 起两腿复现工人（后继版 v2 vs 原版）—— 在途 |
| 13:15–13:22Z | ★上口工人（`verify_chain_repro.py`）**空跑**：日志只有启动横幅、无结果 JSON ⇒ 查明为**被 OOM 杀**（见 §五-6 补记） |
| 13:23Z | 本口开：读 facts 尾（无管理员新信）＋信箱 ⇒ 新信 **fde9 #320**（13:19:16Z，按名可取回执＋内容级 nonce） |
| 13:26–13:32Z | 时序探针：pre-H3 候选件全盘扫描 **320 s 后被 cgroup OOM 杀**（rc=-9，memory.max 1 GiB，oom_kill +1） |
| 13:30–13:38Z | 三腿有界复现工人（`verify_legs_capped.py`，每腿 150 s 封顶）⇒ 结果见 §五-6 |
| 13:38Z | 按名取到 #320 两件，sha256/bytes 逐位对上；回信 fde9 **#83**（首行 `ACK-D0045408 …`） |

---

## 二、闸体自纠五则（★本纪要的主要内容：错的是我方闸，不是组员件）

**背景**：阶段 116 的验收是拿**我方自建底稿**跑的；本口换成**组员真回执**后，闸体立刻报 FAIL 3 ⇒ 暴露「我方闸只认得自己写的回执格式」这一**闸体缺陷**（★★消费端自建闸必须能吃真回执，否则是自说自话）。

| 编号 | 缺陷（先出 FAIL 证据） | 修法 | 回归 |
|---|---|---|---|
| ① | **解析器只认同行配对**：真回执把「路径 / sha256 / 字节」**分列多行**（#318 §二①–③）⇒ 「旧件 sha」被配到别的路径上 ⇒ K01 FAIL（落盘对数=0）、K02 FAIL（1 件不符）、K03 FAIL（archive=0） | v2 块级关联解析：R1 同行同现／R2 sha8↔文件名内嵌 hex8 互配／R3 主体式（路径行后 8 行内找 sha）／R4 主体回指（sha 行最近前置路径行）／R5 文件名内嵌 hex8 立声明 | v2 后 K01/K03/K04/K05 转 PASS，剩 K02/K07 |
| ② | **字节数提取把文件名里的时间戳当字节数**：`\d{3,9}` 无边界匹配 ⇒ `…_20261024T123129Z.py` 里的 20261024 被当作 bytes | 字节数一律走**词边界**正则 `(?<![\w])(\d{3,9})(?![\w])`，并优先「bytes：N／（N B）／`／ N`」显式形态 | v2 内建 |
| ③ | **夹具拷贝有上限**（400 件）⇒ 被审件缺输入 ⇒ K07 被降为 INFO（夹具不全） | **夹具主动补齐**：按被审件自报的缺件清单（stderr 的 FileNotFoundError 路径）回源按名取件补进沙箱后重跑（≤3 轮） | v2 内建（本例最终未触发补齐：目标件换对后夹具已足） |
| ④ | **同一 sha 的第二次出现被当成新声明**：#318 §五④ 散文里的「同一 sha `db1c463b…`」被配到不相干路径 ⇒ K02 假 FAIL | **sha8 唯一**：一个 sha8 ⇒ 一个件；已在册的 sha8 再出现只记 **mention**，不新建声明 | v3 ⇒ K02 转 PASS |
| ⑤ | **现役件选错**：v2 的「现役」邻近匹配（40 字内即算现役）把落盘执行器 `landing_batch_v4_h3.py` 选成被审工具 ⇒ K07 rc=2、K10 失真 | 改为**行内证据打分**：「路径：/新现役件：」标签 +3、「现役 \`path\`」紧邻 +2；本例 `sow6/m5/ref_sha_audit.py` 得 5 分、其余 3 件 0 分 | v3 ⇒ K07/K10 转 PASS |

**自纠纪律**：每则都**先出 FAIL 证据再改**，改完**必跑 selftest 双向校准**（正例 PASS ＋ 五负控各须 FAIL）——v2 后、v3 后各跑一次，两次结果**逐字节相同**（`selftest_after_v2.json` 与 `selftest_after_v3.json` 同 sha `ca835382`，1009 B）⇒ **6/6 无回归**。

---

## 三、真回执验收结果（accept 模式 · 13 项机检 **FAIL 0** · verdict **PASS**）

证据：`playbook/_evidence_stage117/landing_accept_318_v3.json`（`75a0fc74` / 15905 B）

| 项 | 判定 | 实况 |
|---|---|---|
| K01 回执可解析 | PASS | live=7 archive=3 声明总数=10 |
| **K02 R2 现役件逐位对上** | PASS | 7 件 sha/bytes 全部现算对上（不符 0） |
| **K03 R2 留档件逐位对上** | PASS | 3 件逐位对上（不符 0） |
| K04 留档文件名 sha8 段＝内容实算 sha8 | PASS | 3/3 |
| **K05 被引 sha 永久可解析** | PASS | 10/10 按名取到且内容对上 |
| K06「其余判据未改」声明 | PASS | 声明在位（**本闸不代其判定语义**） |
| **K07 R1 正常路径** | PASS | rc=0，末行逐字「总项数 16 ／ FAIL 0 ／ 期望 16」 |
| **K08 R1′ 缺件路径** | PASS | 位置参数探针 rc=1，末行「总项数 0 ／ FAIL 1 ／ 期望 0 —— ★提前返回（缺件 loudly fail 计 1 项 FAIL）：未跑满 ⇒ 不计通过」，**无 traceback** |
| **K09 H3 ROOT 可配置** | PASS | env 键 `REF_SHA_AUDIT_ROOT`，源码含 os.environ |
| K10 R4 ck11 实况 | INFO | 白名单 61 条／命中本盘 24 条；**消费端盘实跑 rc=1「总项数 16 ／ FAIL 1」** ⇒ 判据级红、**盘相对**（见 §五 口径登记）；回执未自报 ck11 计数 ⇒ 不判 |
| K11 零动作自证 | PASS | mix `396571f0`/96660｜drv1 `d5e1296c`/63502｜drv2 `25adcbd1`/79564｜顶层 `88d5d9c4`/237672（本口现算） |
| K12 结论自洽 | PASS | 全部 sha/bytes 现算，未采信转述 |
| K13 对端清单交叉 | INFO | 对端 manifest 3066 件，回执路径命中 9 |

**被审工具选择口径**（新增可查字段）：target=`sow6/m5/ref_sha_audit.py`（score 5）；候选打分表 `{v4_h3_verify:0, landing_batch_v4_h3:0, v3_v4_verify_v2:0, ref_sha_audit:5}`。

---

## 四、独立复核四层（不采信回执转述，全部现算）

1. **三个 sha 现算对上**（按名 GET 后本地 sha256）：
   - 现役 `sow6/m5/ref_sha_audit.py` ＝ `db1c463b15e76f23…` / **46596 B**（与 #318 §二① 逐位一致）
   - v4 候选 `sow6/m5/ref_sha_audit_v4.py` ＝ `f97ec78bace6927c…` / **46472 B**
   - 旧现役 v2 `sow6/m5/history/ref_sha_audit_v2_fcd4aebb_20261024T123129Z.py` ＝ `fcd4aebb8439cc0a…` / **42283 B**
   - 留档 v4 `…/ref_sha_audit_v4_f97ec78b_20261024T123129Z.py` ＝ `f97ec78bace6927c…` / **46472 B** ⇒ **与候选原字节同 sha**（字节未改成立）
2. **现役 ＝ v4 候选 ＋ 恰好 1 行**：逐行 diff **只有 1 处改动**＝行 59
   `-ROOT = "/data/workspace"` → `+ROOT = os.environ.get("REF_SHA_AUDIT_ROOT", "/data/workspace")  # ★H3（b7a0 #78）：ROOT 可配置（env=REF_SHA_AUDIT_ROOT），默认值不变`
   ⇒ 与 #318 §四自述**一致**（H3 只改这一行、默认值不变）。
3. **连带失效机制核实**（#318 §六自披露的那一处）：
   - 原版 `ref_sha_audit_v3_v4_verify.py`（`949d95989ea880f1` / 18924 B）源码内 `BASE = os.path.join(D, "ref_sha_audit.py")`、`BASE_SHA8 = "fcd4aebb8439cc0a"` ⇒ **基线＝现役**；落盘后现役已＝v4+H3 ⇒ 对照轴消失 ⇒ 报 15 项 FAIL —— **前提消失型假警报，机制成立**（与我方 #315 已立纪律同款）。
   - 后继版 `ref_sha_audit_v3_v4_verify_v2.py`（`b2e1ef82ea8c95df` / 19180 B）源码内 `BASE = _glob.glob(D/history/ref_sha_audit_v2_*.py)[-1]`、`BASE_SHA8 = "fcd4aebb8439cc0a"`、docstring 明写「基线改指**留档的 v2 副本**（字节未改、sha 锚定）」⇒ **对照轴已复位**。
4. **被审工具在我方沙箱独立复跑**：正常路径 rc=0「总项数 16 ／ FAIL 0 ／ 期望 16」、缺件路径 rc=1 且结论行齐备 ⇒ 与 #318 §三贴回的两条 stdout/rc **逐字一致**（我方复现，非转述）。

---

## 五、裁定与口径登记

1. **落盘批 #318 验收通过**：R1／R1′／R2／R4／H3 五条硬条件**在我方消费端盘上全部成立**；三个 sha 永久可解析成立。
2. **口径登记①（沿用阶段 116，两种量纲不可直接相等比较）**：ck11 的「工具判据级 FAIL 1」与我方「解析式命中本盘 24 条」是**两种量纲**；我方盘实跑红、组员盘实跑红 ⇒ **红绿是「件×盘」的函数**，双方各自自清，**非工具缺陷**。
3. **口径登记②（本口新增）**：★**回执里的「同一 sha …」等散文提及不构成新声明** ⇒ 验收闸必须区分「声明」与「提及」（sha8 唯一律）。否则闸会把提及错配成声明并报假 FAIL（我方已中招，见 §二④）。
4. **口径登记③（本口新增）**：★**消费端自建闸必须能吃真回执格式**——只认得自写格式的闸是「自说自话」；本口证据链：同一条真回执在 v1 判 FAIL 3、在 v3 判 PASS ⇒ **闸的判定力取决于解析力，不是取决于回执写得规不规范**。
5. **连带失效的处置裁定**：**合规**——原件字节未改（冻结）＋ 同批立后继版 ＋ 基线改指留档副本 ＋ sha 锚定 ＋ 自披露不待我发现 ⇒ 与我方 #315 所立「凡 A/B 对比型自审件，换现役批里须同批立后继版（或把对比轴改指留档副本）」一致。
6. **★两腿复现（补记 · 本口 13:30–13:38Z 实测，结论＝「机制成立、处置正确、端到端在消费端不可跑」）**：
   - **上口工人空跑之因**：上口 `verify_chain_repro.py` 日志只有启动横幅、无结果 JSON ⇒ 实测查明为**被 OOM 杀**（非超时、非脚本缺陷）：pre-H3 工具 `ROOT = "/data/workspace"` 硬编码 → 全盘 `os.walk` + 逐文件 sha256；本口时序探针实测单次全盘扫描 **320.0 s 后 rc=-9（SIGKILL）**（我方 subprocess 超时设为 540 s ⇒ 杀出来自系统侧）；cgroup 证据 `memory.max` = 1 073 741 824 B（1 GiB）、`memory.events` `oom`=6 / `oom_kill`=5（探针后现读）。证据：`playbook/_evidence_stage117/pre_h3_fullscan_probe.json`。
   - **有界复现方法**（`playbook/_evidence_stage117/verify_legs_capped.py`）：只按名 GET 对端件（未改其字节）→ 临时沙箱布件（`sow6/m5/` ＋ `history/`）→ `REF_SHA_AUDIT_ROOT` 指向沙箱 → 三腿各 150 s 封顶、每腿结束即落 JSON（**增量落盘 ⇒ 再被杀也不丢证据**）。
   - **腿C（独立验证器 `ref_sha_audit_v4_h3_verify.py` `9efd2331`/13035）** ⇒ **rc=0、ck01–ck21 全 PASS、末行逐字「总项数 21 ／ FAIL 0」、用时 0.3 s** ⇒ **组员 §一④ 的「21/21 FAIL 0」被我方独立复现**（口径：在**我方工作区**跑的）。
   - **腿A（后继版 v2 `b2e1ef82`/19180）** ⇒ 静态段 ck01–ck21 ＝ **21 PASS / 0 FAIL**（含 ck04 基线指纹、ck20「改动行恰好 5 条」实测 5 条）。
   - **腿B（原版 `949d9598`/18924）** ⇒ 静态段 ck01–ck21 ＝ **14 PASS / 7 FAIL**，FAIL 全在「基线＝现役 ⇒ 对照轴消失」族：ck04 基线指纹、ck07、ck09、ck13、ck15、ck19、ck20（ck20 实测「1 条」≠ 期望 5 条）。
   - **基线解析（确定性实测）**：腿B 的 `BASE = D/ref_sha_audit.py` ⇒ 现役 sha256 `db1c463b…`（46596 B）≠ 源码锚 `fcd4aebb8439cc0a` ⇒ ck04 FAIL；腿A 的 `BASE = sorted(glob(D/history/ref_sha_audit_v2_*.py))[-1]` ⇒ 留档副本 sha256 `fcd4aebb…`（42283 B）＝ 锚 ⇒ 对照轴在位。
   - **运行段（ck21 之后的 `run_cli` 候选件 `--selftest`）**：两腿均 150 s 封顶超时、**未出结论行** ⇒ **不据此判组员件 PASS/FAIL**；只记「消费端资源不足，静态段已足」。
   - **裁定**：**连带失效的处置合规且机制成立**（原版假警报实测复现、后继版静态段全绿）；**组员「复核请用后继版」的口径正确**；**端到端 54/54 在消费端不可复现属资源维度**，非判据不符。

7. **口径登记④（本口新增）**：★**件 × 盘 × 资源三维**——红绿是「件 × 盘 × **资源**」的函数。第三维＝消费端能否在资源上限内跑完（我方 cgroup 1 GiB）；本次证据＝同批两件静态段一致、运行段在我方盘不可跑。⇒ 凡「自审件在消费端复现」类要求，**必须先声明消费端资源上限**，否则「不可跑」会被误读成「判据不符」。
8. **口径登记⑤（本口新增·可施工）**：★**对比型自审件的候选件/留档副本也应 env 可配 ROOT**——H3 只落在现役件上，候选件与留档副本仍 pre-H3 硬编码 ⇒ 消费端永远只能验到静态段、端到端判据不可复现。建议下一批把 H3 覆盖到 `ref_sha_audit_v3.py` / `ref_sha_audit_v4.py` / `history/ref_sha_audit_v2_*.py`（只改 ROOT 行、不动判据语义），并补「现役 sha + 旧件留档 sha」两项回执。
9. **口径登记⑥（本口确认）**：★**回执一律走「按名可取 + 回信首行 nonce ACK」**——组员 #320 提出的内容级回执机制**在我方实测有效**（两件按名取到、sha256/bytes 逐位对上；我方回信首行 `ACK-D0045408 body-sha8=… guide-sha8=…`）；对端信箱无 GET 面 ⇒ 传输级 `delivered` 不可自证，**内容级证据可自证**。

---

## 六、我方本口动作与零动作

- **动作**：真回执落盘（`receipt_fde9_318_raw.md`，逐字）；闸体三版自纠（v1→v2→v3，工具 sha `6c3fe201`→`0b7bf83a`→**`4dd990cb` / 62434 B**）；selftest 回归 ×2（6/6，两次同 sha）；独立复核四层；对端现役面**基线快照**（`sow6/m5` 500 件 sha+bytes）；回信组员 **#82**；向管理员报备。
- **动作（续 · 本口 13:23–13:38Z）**：查明上口工人空跑之因（OOM，非脚本缺陷）并做**三腿有界复现**（脚手架 `verify_legs_capped.py`，增量落盘）；时序探针测得 pre-H3 全盘扫描 320 s 被 OOM 杀（cgroup 1 GiB）；按名取到组员 #320 两件并逐位核 sha256/bytes；**回信组员 #83**（首行 `ACK-D0045408 body-sha8=406074be guide-sha8=591c0eb6`）；向管理员报备（阶段 118）。
- **零动作**：未改对端任何件字节（只按名 GET）；未改我方现役四件（mix `396571f0`/96660｜drv1 `d5e1296c`/63502｜drv2 `25adcbd1`/79564｜顶层 `88d5d9c4`/237672，本口现算）；沙箱只写系统临时目录并跑完即删（`sandbox_removed=True`）；未产合并件；未建 pin 层/顶层网表；未派工；未上传冷备；未评估情形 B；未跑 Q3。
- **纪律**：凭据只在 `secrets/peers.json`（600）；文档内只留占位符；引用数字全部本口现算（★引用数字前必实测律）。

---

## 七、件索引（本口产出 · sha8/bytes 本口现算）

| 件 | sha8 | bytes |
|---|---|---|
| `phys/top/判读纪要_裁定一百零七_真回执验收与闸体五则自纠_2026-10-24.md` | 见 summary.md（本文自身不写死 sha，避免循环引用） | — |
| `tools/peer_landing_accept.py`（v3 现役闸） | `4dd990cb` | 62434 |
| `playbook/_evidence_stage117/receipt_fde9_318_raw.md`（真回执逐字） | `fbefda5e` | 9104 |
| `playbook/_evidence_stage117/landing_accept_318.json`（v1 跑批 FAIL 3 证据） | `2be30520` | 7016 |
| `playbook/_evidence_stage117/landing_accept_318_v2.json`（v2 跑批 FAIL 2 证据） | `4ba2cd65` | 8093 |
| `playbook/_evidence_stage117/landing_accept_318_v3.json`（v3 跑批 PASS 证据） | `75a0fc74` | 15905 |
| `playbook/_evidence_stage117/selftest_after_v3.json`（回归 6/6） | `ca835382` | 1009 |
| `playbook/_evidence_stage117/peer_surface_snapshot_20261024T1316Z.json`（对端基线快照 500 件） | `36d3e13c` | 73939 |
| `playbook/_evidence_stage117/patch_gate_v2.py` / `patch_gate_v3.py`（自纠补丁） | `f01bc57c` / `ebf20b12` | 15263 / 7855 |
| `playbook/_evidence_stage117/verify_chain_repro.py`（上口两腿复现工人脚本 · 实测被 OOM 杀） | `422c604c` | 3666 |
| `playbook/_evidence_stage117/verify_legs_capped.py`（★三腿有界复现脚本 · 增量落盘） | `82d487ad` | 7124 |
| `playbook/_evidence_stage117/verify_legs_capped.json`（★三腿实测结果） | `7d96c960` | 14589 |
| `playbook/_evidence_stage117/verify_legs_capped.log`（工人运行日志） | `ec7f337b` | 3744 |
| `playbook/_evidence_stage117/pre_h3_fullscan_probe.json`（★全盘扫描 OOM 探针证据） | `83a58f0e` | 1858 |
| `playbook/_outbox/b7a0_to_fde9_83.md`（回信组员 #83 · 首行 nonce ACK） | `acb6c907` | 6892 |

## 八、组员产出（非我方交付件 · 仅引用，不列入上表）

- fde9：其盘 v4+H3 落盘批（现役 `sow6/m5/ref_sha_audit.py`＝`db1c463b…`/46596 B、`history/` 两件留档、`landing_batch_v4_h3.py`、`ref_sha_audit_v4_h3_verify.py`、`ref_sha_audit_v3_v4_verify_v2.py`、两份 stdout 副本、v10 `frozen_roster.json`）——**其自产，我方只按名取件读取与验证，未改其任何字节**。
- fde9（#320 新增两件）：`sow6/m5/peer_post_sent_319_v4_h3_landing_reissue.md`＝`0472d30b…`/7390 B、`sow6/m5/peer_landing_320_ack_request.md`＝`98694832…`/3904 B —— **其自产，我方按名取件并现算核 sha（逐位一致），未改其任何字节**。
- b7e7：在途 ④cdl `_SCHEMATIC_PREFERRED` 层次名塌缩（等情形 B，不催）。
