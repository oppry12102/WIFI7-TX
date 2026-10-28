# 判读纪要 · 裁定一百四十九（拟）· 阶段 159 · L1「字面 /tmp」派生规则 —— 实施器落地与实施前验证

- 时间：2026-10-25T17:08Z–17:16Z（UTC；本地 2026-10-26 01:08–01:16）｜作者：b7a0（WiFi7-TX 组长）
- 性质：**仪器/判据面**（只读现役面 · **零芯片动作**）｜★**本口未改任何仪器字节**（census `25f115e6`／probe `287d22fc`／oracle `133b5499`／registry `43ef851a` 四件与在跑批次一致）
- 前置：阶段 158 批次**在跑**（波 B heavy，pid 1586940，17:15Z 实测 53 min）⇒ ★**未完成前不得实施**（否则收口闸 G2 必红）
- 依据：`playbook/_stage159_design_L1字面tmp派生规则.md`（R1–R6）｜`playbook/_stage159_精确改点与验收口径.md`（定位单）｜`playbook/_evidence_stage158/stage159_l1_literal_proto.json`（L1 字面派生原型）

---

## 一、缘起（阶段 158 收口登记的派生面缺口）

L1 静态族派生**只认** `mkdtemp(prefix=…)` 与 `os.path.join(tempfile.gettempdir(), 'X')` ⇒ **不认「字面 `/tmp/<名>`」常量**（对端件脚本写死 `/tmp/_rsav_base_b1.py`、我方预言机 `tools/a1_domain_oracle.py` 写死 `/tmp/x_chain.md` 等即属此类）⇒ 该族**只能人工增补**进族表 ⇒ ★C1 族表覆盖完备性硬闸**看不见**它（派生面不全 ⇒ 差集恒空）。

原型实测（阶段 158 末）：全扫描面 **1,250 文件 / 70 命中 / 27 字面族** ⇒ 写向 10、只读 17 ⇒ ★写向侧缺口恰 **5 族**：`inbox_dump.txt`／`ports_v20.json`／`probe2_v20.json`／`rbmerge`／`x_chain.md`。

## 二、本口做了什么（三件，全部**只读**）

### 1. 实施器 `playbook/_stage159_patch/stage159_apply.py`（apply-ready · 带前置门）

- **改点仅两处仪器**（与定位单一致）：
  - **A `tools/fleet_hygiene_census.py`**：新增 `_PFX_LITERAL_TMP`／`_WRITE_HINTS`／`_NEGCTL_LIT` ＋ `_scan_literal_families()`；`static_families()` 把**字面写向族并入 live**（进 C1 硬闸）、**只读族并入 declared**（INFO 层，不进硬闸）；C1 口径文案**显式**改为「C1 口径**只对写向族**」；`data` 增 `literal_write_families`／`literal_readonly_families`／`n_literal_write_families`／`n_literal_readonly_families`（★覆盖诚实律：同屏）。
  - **B `tools/skill_param_probe.py`**：`_TMP_JUNK_PAT` 增补 5 个字面族。
- ★**前置门**（`_preconditions()`）：阶段 158 `batch_end.txt` 存在 ＋ 收口闸 `stage154_batch_rerun_gate.py --mode check` ⇒ **verdict PASS** ⇒ 否则**拒绝执行**（不改任何仪器字节）。
- ★幂等：已含标记则跳过；改前备份到 `playbook/_stage159_patch/backup/`；**编译自检通过才落位**（★批量改写必编译自检律）；落盘后现算 sha8/bytes ＋ 现役四件 ZERO_DELTA 自检。

### 2. ★实施器 dry-run 端到端验证 `playbook/_stage159_patch/dryrun_verify.py` ⇒ **结论行 16 ／ FAIL 0**

**零仪器改动**（内存替换 ⇒ 产物只写工作区 `dryrun/` 目录；★**全程不写 `/tmp`** ⇒ 不破阶段 158 的「族外新增残留 0」验收）。

| # | 校验 | 结果 |
|---|---|---|
| 1–5 | 五处锚点唯一（count==1） | 5/5 |
| 6 | 内存替换完成（★单一真源函数 `_patch_census_src`／`_patch_probe_src`，apply 与 dryrun 共用 ⇒ 无两份实现漂移） | PASS |
| 7 | 编译自检（★批量改写必编译自检律） | 两件通过 |
| 8 | L1 字面族派生有命中 | hits=**71**／写向 **10**／只读 **22** |
| 9 | 新族表覆盖字面写向族 | 缺口 **0**（旧表缺 5 ⇒ 新表补齐） |
| 10 | 候选 live 族缺口（新族表） | live=**85**，缺口 **0** |
| 11 | 候选 live 族缺口（旧族表）>0 ⇒ ★新规则**确有牙** | 旧表缺口 **5**：`inbox_dump.txt`／`ports_v20.json`／`probe2_v20.json`／`rbmerge`／`x_chain.md` |
| 12 | 负控 N1：注入族外族 ⇒ 仍报出 | `gap=['zzzcensus_injected_family_']` |
| 13 | 只读族不进 C1 硬闸（INFO 列） | 只读 22（例：`__g2_no_such_auth__.txt`／`_nl_lay.cir`） |
| 14 | 覆盖诚实：派生面同屏 | 总族 29 ＝ 写向 10 ＋ 只读 22；命中 71 |
| 15 | probe 清扫腿/孤儿归属**自动**覆盖五族（单一真源） | 5/5 命中 |
| 16 | 零仪器改动：现役 census/probe 字节未变 | `25f115e6`／`287d22fc` 未变 |

### 3. 跑批器 v2 ＋ 一体化 prep

- `tools/stage159_sweep_worker.sh`：与阶段 158 批次**逐项同口径**（同一技能集合 LIGHT 25／HEAVY 9／VERY 2、同一预算）⇒ 判据可比、覆盖不缩水；★**每批必跑面扩容**（裁定一百四十八 §五-4 待办）—— 批首＋批尾各跑一次**普查闸 selftest（含负控 N1）＋ 探针 selftest**，记 rc 与标准结论行（FAIL 计数），任一 FAIL 即不算完工；另加 **/tmp 全量条目快照** ⇒ 量化「族外新增残留数」。
- `tools/stage159_prep.py`：①阶段 158 完工判定 ②批次摘要＋纪要 §五 回填草稿（机器提取）③收口闸复判（**必须 PASS**）④阶段 159 实施 ⇒ 打印起跑命令。★当前 `--status` 实测**正确拒绝实施**（`batch_end.txt` 缺失／波 B·C 未记 rc）。

## 三、★★四项实测修正（相对定位单）—— ★引用数字前必实测律

1. **probe 侧「清扫腿／孤儿归属」无需另改**：实测 `skill_param_probe.py` 的清扫腿（L1216／L1246／L2653／L2658／L2668／L2725）与孤儿归属（L1381）**已统一用 `_TMP_JUNK_PAT.match()`** ⇒ 族表一改即自动覆盖 ⇒ 定位单所列该两处改动**自然生效**，实施**只改族表一处**；dry-run 第 15 项已实测自证 5/5 命中。
2. **锚点转义层数**：文件内字符类写作 `['\"]`（引号前带反斜杠），Python 字面量转义层数不同 ⇒ 早期锚定 `_PFX_TMPVAR` 整行实测 **count=0** ⇒ 改用无歧义锚点 `def _scan_families(path):`（★锚点未命中即中止，**绝不做半改**）。
3. **probe 族表末行 `)` 必须在引号内**（与原文件同构：`b7a0_s1")`）：写成引号外 ⇒ `re.compile` 报 `missing ), unterminated subpattern`。
4. ★★**负控 N1 抓到「我本口引入的回归」**：新族表末项一度写成 `...probe2_v20\.json|)` ⇒ **尾随 `|` ⇒ 空替代分支** ⇒ 正则**匹配一切** ⇒ C1 差集**恒空** ＝ ★阶段 158 刚修掉的「族表硬闸假绿」**复发**。⇒ 去掉尾随 `|` 后负控转绿（`gap=['zzzcensus_injected_family_']`）。★**判据器有齿、当场咬住作者本人**——此即阶段 159 负控设计的价值所在。

## 四、★下一步（阶段 158 收口后）

1. 阶段 158 批次完工（**以铃为准**）⇒ `python3 tools/stage159_prep.py`（自动：摘要＋§五 草稿＋收口闸复判＋实施）；
2. 起跑同口全批复跑（跨会话后台，**完工有铃**）：`sh tools/stage159_sweep_worker.sh`；
3. 新批次完工 ⇒ 收口闸复判（G2 转 PASS）＋ 终局洁净（孤儿 0／残留 0／族外新增 0／现役四件 ZERO_DELTA）＋ 纪要 §五 回填；
4. 待管理员裁：①–㉚（末封仍 26795；★㉕ 建议 **A ＝ 顶层自建 via 栈**）＋**8510 取件钥轮换**（我方**未动手**，凭据值不落盘）。

## 五、纪律自检（本口）

未改现役 GDS／网表／deck 字节；未产合并件；未建 pin 层／顶层网表；未派工；未评估情形 B；未跑 Q3；**M5 链件未动**；**未执行 8510 取件钥轮换**；跑批窗口内**未重启**任何常驻服务；**未改任何仪器字节**（四件与在跑批次一致）。
本口新增文件**全部落在发布面之外**（`playbook/_stage159_patch/`、`tools/`、`phys/top/`）⇒ **交付面字节零变化**。
凭据现取不打印；未索取对端 file-key；我方 8510 取件钥继续停用。
