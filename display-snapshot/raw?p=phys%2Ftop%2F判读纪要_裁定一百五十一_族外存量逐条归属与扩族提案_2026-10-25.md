# 判读纪要 · 裁定一百五十一 · 族外存量逐条归属 ＋ 扩族/清理提案（dry-run · 零删除）

- **主体**：WiFi7-TX 组长（b7a0）｜**时间**：2026-10-25 UTC 17:57–18:10Z（本地 2026-10-26 01:57–02:10）
- **性质**：仪器/判据面 · **只读现役面**（★零芯片动作、零删除、零仪器字节改动）
- **触发**：① 阶段 158 批次完工收口；② 阶段 159 实施（改仪器）后的**独立验证**；③ 阶段 160 归因结论的**可执行化**

---

## 〇、一句话

★阶段 158 批次**收口 PASS**（三波 rc 0/0/0、结论行 59／FAIL 0、收口闸 PASS）⇒ 阶段 159 **实施已落位**；★但实施器**自检从未真正跑过**（自检函数 `_load` 未定义 ⇒ 异常被 `except` 吞掉 ⇒ main() 仍返回 0）⇒ 本口补上**独立验证闸**（11 项全 PASS）并**修好实施器**（自检失败即非零退出）；同时把阶段 160 的「族外归因」升级为**逐条归属 + 扩族/清理提案（dry-run · 零删除）**。

---

## 一、阶段 158 收口（裁定一百四十八 §五 回填）

| 项 | 读数（现算） |
|---|---|
| 波次 | A_light(25)／B_heavy(9)／C_very(2)｜`wave_rc` = **0 / 0 / 0** |
| 结论行合计 | **总项数 59 ／ FAIL 0**（33+22+4） |
| 收口闸 | `batch_rerun_gate --mode check` ⇒ **rc=0／verdict=PASS／「总项数 10 ／ FAIL 0」** |
| 现役四件 | **ZERO_DELTA ✔**（mix `396571f0`/96,660；drv1 `d5e1296c`/63,502；drv2 `25adcbd1`/79,564；顶层 `88d5d9c4`/237,672） |
| 族外新增残留 | 修前 2（`_rsav_*`）→ **修后终局 0** ✔（波 C 期间出现的 2 条瞬时条目在批后已被其属主清掉） |

**逐字件**：`playbook/_evidence_stage159/stage158_batch_summary.json`｜`playbook/_evidence_stage158/worker.log`｜§五 草稿 `playbook/_evidence_stage159/stage158_sec5_draft.md`（已回填进裁定一百四十八纪要）。

---

## 二、★阶段 159 实施：自检从未跑过（**判据器自身的洞**）

- 实施时刻 **18:01:52Z**：census `25f115e6`→`c7ad815a`（28,351→32,128 B）；probe `287d22fc`→`d8ef438d`（137,607→138,124 B）；oracle `133b5499`／registry `43ef851a` **未动**；现役四件 ZERO_DELTA。
- ★实施器打印：`[自检] 异常：NameError("name '_load' is not defined")` ⇒ **自检函数 `_load` 在实施器里根本不存在** ⇒ 自检**从未执行** ⇒ 「落位是否正确」**无人验证**，而 `main()` 仍 `return 0` ⇒ **实施看起来成功了**。
- ★**这类洞的通用形状**：判据器自己的异常被 `except` 吞掉 ⇒ 只留一句打印、不影响退出码 ⇒ 「有自检」冒充「自检有齿」。

### 2.1 本口的修法（两处）

1. **补真实现**：`stage159_apply.py` 新增 `_load(path, tag)`（按路径 `importlib` 加载；两仪器均有 `__main__` 守卫 ⇒ 不执行 main）。
2. **不许静默吞**：自检异常或「字面写向族未被覆盖」⇒ **main() 返回 3（非零）**并打印「本次实施**未获验证**」⇒ 失败必现形。

### 2.2 ★独立验证闸（`tools/stage161_verify_stage159_patch.py` · 11 项全 PASS）

| 校验 | 内容 | 结果 |
|---|---|---|
| V1 | 两件仪器可按路径加载（主守卫未执行） | PASS |
| V2/V2b | census 侧 `_scan_literal_families` 在位、返回三元组 | PASS |
| V3 | C1 硬闸口径**只对写向族**（源码标记逐条核对） | PASS |
| **V4** | **字面写向族 10 个全部被现役族表覆盖（未覆盖 0）** | PASS |
| V5 | census 自检 rc=0「总项数 5 ／ FAIL 0」 | PASS |
| V6 | probe 自检 rc=0「总项数 17 ／ FAIL 0」 | PASS |
| V7 | 现役四件 ZERO_DELTA | PASS |
| V8 | 实施 manifest 与现役仪器字节一致（未被第三方改动） | PASS |
| V9 | probe 族表确含阶段 159 新增五族（`x_chain.md`／`rbmerge`／`inbox_dump.txt`／`ports_v20.json`／`probe2_v20.json`） | PASS |
| V10 | 验证前后 `/tmp` 条目数不变（验证未写 /tmp） | PASS |

★另实测：**我方新写的两件 stage161 工具自身不引入新的字面写向族**（扫描面 1,254 个文件，字面写向族仍为 10、未覆盖 0）⇒ 新工具不会污染族表与 C1 硬闸。

### 2.3 同口全批复跑（已起跑）

`sh tools/stage159_sweep_worker.sh`（脱离会话 · 完工有铃）· 起跑 **2026-10-25T18:04:26Z** · 仪器戳 probe `d8ef438d`／census `c7ad815a`／oracle `133b5499`／registry `43ef851a` · 与阶段 158 **逐项同口径**（A25／B9／C2 · 同预算 · 同负载闸）＋ **每批必跑面扩容**（批首/批尾各跑普查闸 selftest 含负控 N1 ＋探针 selftest ＋ `/tmp` 全量快照量化族外新增）。

---

## 三、★裁定一百五十一：族外存量**逐条归属**（`tools/stage161_tmp_family_expansion_proposal.py` · 21 项机检 FAIL 0）

读数（**本口现算**，`/tmp` 顶层 **619** 条目）：

| 归因类 | 条数 | 归属 | 说明 |
|---|---|---|---|
| K_OURS_INSTR | 197 | 我方仪器/工作区 | 内容指纹命中我方仪器标记 |
| K_OURS_PREFIX | 74 | 我方仪器 | **前缀学习回判**（前缀由高置信我方条目支撑） |
| K_OURS_CODE | 14 | 我方源码 | `.py/.sh` 字面命中 |
| K_WS_BACKUP | 5 | 我方工作区 | `*.bakNN` 备份件被写进 `/tmp` |
| **K_OURS 合计** | **290** | 我方 | ★**58.3% 的族外存量是我方自己的**（与阶段 160 结论一致） |
| K_EDA | 78 | PDK/EDA 工具 | 非我方仪器族 |
| K_KERNEL | 24 | **内核（xuseek 自身）** | ★**不得纳入我方族表**（BOOT 明示） |
| K_PEER_FACE / K_PEER | 5 / 12 | 对端 fde9 | ★不得纳入我方族表 |
| K_CRED_SUSPECT | 2 | **疑似凭据** | ★一律不删 |
| K_DOC_WEAK / K_UNKNOWN | 2 / 196 | 弱证据/来源不明 | 待人工判读 |

### 3.1 ★方法三件套（可复算）

1. **归因规则有序且确定**：凭据名 → 内核前缀 → 对端发布面同名 → 对端命名特征 → 备份件 → 内容指纹 → 源码字面 → EDA → 文档提及 → 不明。
2. **前缀学习**：从高置信我方条目学前缀族（**每个前缀 ≥1 条高置信支撑**），再回判未定条目（`K_OURS_PREFIX` 74 条）。
3. **★防自污染**：语料扫描**排除 `playbook/_evidence_*`**（★第一轮实测：上一轮证据 JSON 里逐条列着全部 `/tmp` 名 ⇒ 任何名字都会「被我方文档提及」⇒ 归属判据失效；实测 K_DOC_WEAK 从 272 降到 **2**）。

### 3.2 ★负控（注入模拟 · 走同一 `classify` ⇒ 判据器有齿）

| 负控 | 注入 | 结果 |
|---|---|---|
| NC-A | 内核名 `xuseek_selftest_injected_NC_A` | 分类＝K_KERNEL；前缀**未进** LOW/MID 提案 ✔ |
| NC-B | 对端发布面同名件 `peer_post_body_316_v3v4_candidates.md` | 分类＝K_PEER_FACE；前缀**未进** LOW/MID 提案 ✔ |
| NC-C | 提案覆盖数 vs 实测命中数 | 97 vs 97 ✔ |
| NC-D | 空提案假绿（族外非空却零提案） | 非假绿 ✔ |
| NC-E | **凭据名** `inbox_secret_NC_C.key` | 分类＝K_CRED_SUSPECT；前缀**未进** LOW/MID 提案 ✔ |

---

## 四、★扩族/清理提案（**dry-run · 零删除**）

**处置分布（族外 609 条）**：待令（可清·我方族）**290**｜待令（可清·非我方族表）**78**｜待令（移交）**41**｜待人工判读 **198**｜**不删（疑似凭据）2**。
**可回收字节**：我方族候选 **4,164,706 B**（4.0 MiB）；族外全体 14,827,274 B。

**扩族分级（按前缀干聚类）**：

- **LOW 76 干／97 条／1.42 MB**（可自动扩族，类纯度 100%）：`BOOT, gdsfp, a1chk, boot, apply, deliv, gate, judge, mirror, probe6, short, skill, stage142, wrap, __A1PROBE__r, __pycache__, actgeom, auth65, base0, census, cmim, d3435, drv2v17, gate2, gate3, gate4, last, libdensity, live, measure, measure2, measure3, opbackfill, oracle, ostest, outbox, p2fill, p2fill2, p4probe, part3, patch, polylist, probe2, probe3, probe4, probe5, rebuilt, rebuilt2, replace, rest, s149, shrink, shrink2, side, smoke6, spec, stage101, sweep, swnx5, tinyr, truth, upd10…upd12, upd3…upd9, v015, v5run, v5test, v6run, v7run`
- **MID 30 干／72 条／0.43 MB**（含弱证据或需人工确认）：`probe, mixv31, pitch, rhigh, drv1, _ck.bin, _nl.cir, _nl_lay.cir, cbpath, chainop13, cornerHBT, dcrc, devs, drv1ptap, fetch274, insp, klrel, klwheel, layermap, list, lobop13, lvstest, mixop13, ngspice, phys, pinmap, pubface, repro, upload, warn`
- **HIGH 234 干／440 条／12.97 MB**（泛前缀或跨类污染，**只列不采**）：`xuseek(内核), t, upd, lvs, g1, g2b, a1, dg, 8510, cdl, deck, f, r, x, chain, drc, mix, b7e7, fde9, sow6_…`

★**凭据件实测**：`/tmp/filekey`（20 B，2026-10-17T04:10:17Z）与 `/tmp/inbox.key`（20 B，同刻）——与**现役凭据真值逐条比对：均不相等**（**未命中现役凭据 ⇒ 无凭据外泄**；二者为旧调试截断件）⇒ 处置仍是**不删·人工确认**，★凭据值与指纹**一律不落文档、不落日志**。

---

## 五、★新发现：端态洁净缺口有**两条**（不是一条）

1. **族外存量 609 条**：清扫腿按族表匹配 ⇒ 删不掉。★阶段 159 补的是「**字面 /tmp 可派生面**」（C1 硬闸从「看不见」变「看得见」），**不覆盖历史存量** ⇒ 存量仍需**管理员令**＋扩族。
2. **族内存量（本批之前就存在的族内条目）**：`_sweep_residue_cleanup` 按**基线差集**只清「跑批期新建」⇒ 存量按设计留着（★存量不动律）。本批前实测**已有 10 条**：`a1ld_selftest_*` ×7（05:12–05:22Z）、`artifact_index.json`（03:26Z）、`g2d_timing.log`／`g2d_timing_probe.json`（03:33Z）。

⇒ 两者**都不是缺陷**（各守一条律），但**口径必须分开记**，否则会把「设计上不动」误读成「漏清」。★两条都需管理员令才能清（族外见 §四提案；族内存量属我方仪器产物，可同批清）。

---

## 六、纪律自检（本口）

- 未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层／顶层网表；未派工；未评估情形 B；未跑 Q3；**M5 链件未动**；**未执行 8510 取件钥轮换**（等管理员裁示）；跑批窗口内**未重启任何常驻服务**。
- ★本口改动的**仪器字节**：仅阶段 159 的 census `25f115e6`→`c7ad815a`、probe `287d22fc`→`d8ef438d`（**实施动作，已验证并已同口全批复跑**）；oracle/registry **未动**。**除此之外**本口未再动任何仪器字节。
- 现役四件**当口现算**逐位未变：mix `396571f0`/96,660；drv1 `d5e1296c`/63,502；drv2 `25adcbd1`/79,564；顶层 `88d5d9c4`/237,672。
- ★**零删除**：本口对 `/tmp` **只读**（提案件自证：跑前 619／跑后 619，差异 ∅）；未清任何存量（存量不动律）。
- 凭据：现取不打印；**未写入任何文档／纪要／信／发布面**；未索取对端 file-key；对端取件仅 GET。
- ★只读现役面：本口新增产物只写 `tools/`、`playbook/_evidence_stage161/`、`phys/top/`；★未在 `verify/`／`outbox_files/`／`phys/` 下新增 `.py`（避免改变 census 的 L1 扫描面）。

---

## 七、下口待办

1. **阶段 159 批次收口**（以铃为准，约 19:55Z）：三波读数＋必跑面（批首/批尾 selftest）＋族外新增残留（期望 0）＋四件 ZERO_DELTA ⇒ `batch_rerun_gate --mode check` 复判（**G2 应转 PASS**）。
2. **待管理员裁**（本口新增两项）：
   - ★**族外存量清理令**：按 §四 LOW（97 条／1.42 MB）先行，MID 需人工确认；内核族与对端族**移交**（41 条），凭据件**不删**；
   - ★**族内存量清理令**：10 条（设计上是「跑批期新建才清」，存量按设计留着）——是否一并清？
   - 原有：①–㉚（末封仍 26795；★㉕ 建议 **A ＝ 顶层自建 via 栈**）＋**8510 取件钥轮换**（我方**未动手**，凭据值不落盘）。
3. 治理日报：**2026-10-25 日报已发**（事实账 n=35586）⇒ 不重发。
