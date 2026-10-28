# 判读纪要 · 裁定一百二十六 · 扫掠腿残留清扫硬化与波三收口

- 阶段：136（承阶段 135 · 裁定一百二十五）
- 日期：2026-10-25（本地 Asia/Shanghai；内部 UTC）
- 范围：**只读现役面 · 零动作**——未改任何现役 GDS／网表／deck 字节；未产合并件；未建 pin 层／顶层网表；未派工；未上传冷备；未评估情形 B；未跑 Q3；M5 链件一概不动；**未执行 8510 取件钥轮换（待管理员裁）**。
- 前置：本口开场无新管理员信（待决 ①–㉚ 全挂，末封仍 **26795**）；无新同伴信（`inbox.jsonl` 355 行全部解码成功，末条 fde9 2026-10-24T15:29:30Z）⇒ 未投回信。

---

## 一、波三收口（阶段 134 扫掠腿重件 21 件/36 项中的 13 件/29 项）

命令：`python3 tools/stage134_sweep_run.py --only '<13 件>' --item-timeout 150 --budget 3000 --out playbook/_evidence_stage135/sweep_wave3.json`
（detach 工人 pid 90143/90146/90147；完工 exit 0 门铃自醒；实测 elapsed **2846.8 s**）

**判据分布（29 项）**

| 判据 | 计数 | 含义 |
|---|---|---|
| EFFECT | 10 | 两值差分观测到输出变化 ⇒ 参数**确实被读取并起作用** |
| INCONCLUSIVE_ERROR | 9 | 闸内吞异常（输出含「★闸内异常:」）⇒ 不可判 |
| UNOBSERVABLE | 6 | 两跑均 `error` 早退 ⇒ 参数使用点未到达 ⇒ 不可判 |
| CONSUMED_REJECTED | 3 | argparse 域外取值被消费后拒绝（`invalid choice:`）⇒ 不可判 |
| NO_EFFECT | 1 | 观测面内无差异 ⇒ **不可判·INFO**（★差分不证死律，不再判死） |
| ECHO_ONLY / OUT_NOT_LANDED / TIMEOUT / ERROR / NOT_RUN | 0 | — |

- **覆盖自洽（★扫掠覆盖诚实律）**：残余 **29 ＝ 已判 10 ＋ 不可判 19 ＋ 未跑 0** ✔
- **n_fail 0 ／ verdict PASS**——阶段 134 波二的 **3 项假 FAIL 全部归零**（原先被判死/判 FAIL 的 6 项现分别归 UNOBSERVABLE 3 项、INCONCLUSIVE_ERROR 3 项、CONSUMED_REJECTED 3 项）。
- 逐项复核唯一 `NO_EFFECT` 项：`peer_landing_accept.tool`——其输出实为**双向校准（selftest）**路径，`tool` 参数在该路径本就不被读取 ⇒ 差分无差异属**观测面限制**，判「不可判」正确（判死即为假 FAIL）。
- 复核 `OUT_NOT_LANDED`（唯一保留的差分腿判死类）：**0 项** ⇒ 本轮无任何参数被判死。

## 二、围栏复跑（并发重叠假 FAIL 的 ±0 确认）

`python3 tools/fleet_runtime_probe.py --legs error --json playbook/_evidence_stage135/fleet_runtime_probe_error36_rerun.json`

- 判定 **PASS（76/76）**，结论行「总项数 76 ／ FAIL **0**」
- 围栏端态：跑批期间副作用事件 **0**（新增 0／变更 0）｜端态净差异 **0**（新增 0／变更 0／消失 0）｜已清扫临时目录 0
- ⇒ 上口记录的「FAIL 1＝围栏并发重叠（波三在跑写 `phys/drc/rerun_stage96/…`）」为**并发造成的假 FAIL**，波三收口后复跑**归零**（±0 确认）。

## 三、★波三实测暴露的真实缺口：扫掠腿残留清扫不完备

**实测残留（波三收口后）**

- `/tmp` 侧残留 **12 个目录**：`g1drc_*` 3、`g1lvs_*` 4、`g2c_dbg_*` 3、`g2d_route_b_*` 2（其中 5 个含产物）
- 工作区侧 `phys/drc/tmp_stage*` **0**（技能自身 tmp_stage107_* 已被登记清扫 ✔）
- **孤儿进程链 1 条**：`run_drc.py` → `sh` → `klayout`（存活 16 分钟持续占 CPU，父进程已随 worker 退出）

**两条根因（读源码坐实）**

1. **★残留前缀表不完备**：`tools/skill_param_probe.py` 的 `_TMP_JUNK_PAT` 只覆盖 `g1drc_|g1loc_|g2c_|m4_|a1sweep_|a1probe_|a1diff_` 五族 ⇒ `g1lvs_`／`g2d_route_b_`／`g2csup_`／`p4_` 等**技能自身 scratch 前缀**根本不在表内 ⇒ 漏清。
2. **★终局清扫覆盖面窄**：跑批末只扫 `a1sweep_*`（探针自己的沙箱），而**技能自身的 /tmp 目录**在「子进程在 rmtree 之后仍在写盘」时会**复活** ⇒ 必须按前缀表在收尾再扫（且扫两遍：早复活＋晚复活）。

**闸改造三处**（补丁 `tools/stage136_sweep_residue_patch.py`，幂等；`tools/skill_param_probe.py` 67,259 → **69,053 B**，sha256 `9a958c38…`）

- A. 扩 `_TMP_JUNK_PAT` 为**全舰队 scratch 前缀表**（新增 `g1lvs_`／`g2csup_`／`g2d_`／`p4_`／`_p4_`／`p3_`／`p2_`／`p1map_`／`mfp_`／`happy_`／`gate128_`／`fleet_probe_`／`chain64_`／`skillfleet_`／`stage131_`／`tmp_stage97_`／`b7a0_shard_`／`a1s135_` 等族）
- B. 抽出 `_terminal_residue_sweep(tmp_before, passes=2, gap=1.0)`：**两遍**清扫（间隔 sleep）+ 只删**跑批期间新建**的名字（快照差集）⇒ 不越界、不误删他人生存目录
- C. 残留清单入证据：JSON 新增 `terminal_residue_cleaned` 字段 ＋ 标准输出加「★终局清扫: 清除残留目录 N 个」行

## 四、★新立三条律（入 `playbook/BOOT_通用律库.md` 末段）

1. **★残留前缀表完备律**：跑批清扫的**前缀表必须覆盖全舰队 scratch 前缀**（含技能自身前缀），否则端态不洁净；前缀表缺项＝闸缺陷，不得靠事后手工补。
2. **★终局清扫扩面律**：跑批收尾必须**按前缀表再扫一遍**（至少两遍、间隔 sleep），因为子进程在 rmtree 之后仍在写盘会让目录**复活**；只扫探针自己的沙箱＝端态不洁净。
3. **★残留清单入证据律**：清扫结果必须**逐条落进 JSON 与标准输出**（可核），不得只做不记。

（另附通用元律，见下节自伤登记。）

## 五、★自伤登记（本口两处，均被自检自身抓到）

1. **补丁幂等判据写错**：首版以「NEW 含 OLD 且 OLD 不在文件中」判幂等——而 NEW_C1/C2/C3 **以 OLD 为前缀** ⇒ `old not in src` 永假 ⇒ 复跑把 helper／JSON 键／打印行**重复插入**。处置：**从备份回滚**（`/tmp/spp_backup_stage136.py`，还原 67,259 B / `964fff42…`）⇒ 改用**标记串**判幂等（`★幂等判据须用标记串律`：判据不得依赖「谁包含谁」的前缀关系）。复跑三次 ⇒ `[noop] 无改动（幂等）`，helper/JSON 键/打印行各恰 1 份。
2. **夹具形态缺陷**：残留自检首版用**符号链接**指向 `/tmp` 同名条目 ⇒ `shutil.rmtree` 对符号链接抛错且被 `ignore_errors=True` 吞掉 ⇒ 目录未被清 ⇒ 正例**假 FAIL**。处置：夹具改**真实目录**（与真实残留形态一致）⇒ 5/5 PASS。
   ★该假 FAIL 被**闸自检自身**抓到（未外溢到结论）。

## 六、实测与校准

| 项 | 结果 |
|---|---|
| 波三扫掠（13 件/29 项） | **n_fail 0 ／ PASS**；29 ＝ 10 ＋ 19 ＋ 0 ✔ |
| 探针 error 腿复跑（36 件） | **76/76 PASS ／ FAIL 0**；围栏净差异 0 ✔ |
| 残留清扫自检（新） | **5/5 PASS**（正例 1 ＋ 负控 NC-A 越界／NC-B 误删跑批前目录／NC-C 复活／NC-D 清单可核） |
| 探针闸自检（回归） | **11/11 ／ FAIL 0**（阶段 133 六项 ＋ 阶段 135 扫掠五项，不回归） |
| 端到端 mini sweep（`g2d_route_b_precheck`，2 项） | EFFECT 2 ／ FAIL 0；**终局清扫 0 残留**；`/tmp` 零残留；**无孤儿 klayout** ✔ |
| 现役四件 sha 现算 | mix `396571f0`/96,660、drv1 `d5e1296c`/63,502、drv2 `25adcbd1`/79,564、顶层 `88d5d9c4`/237,672 ⇒ **逐位未变** ✔ |

## 七、遗留与下口

- 管理员待决 ①–㉚ **未回**（末封仍 26795）⇒ 零销账动作；**㉕ 已具备 A/B 双腿证据可直接裁**（我方建议 **A ＝ 顶层自建 via 栈**；路线 B 牵动 5 件基线与 119 处引用）。
- **8510 file-key 轮换待管理员裁，未获令不动手**（凭据值不落盘）。
- 待清理项：**无**（`/tmp` 残留 0、`phys/drc/tmp_stage*` 0、孤儿 klayout 0）。
