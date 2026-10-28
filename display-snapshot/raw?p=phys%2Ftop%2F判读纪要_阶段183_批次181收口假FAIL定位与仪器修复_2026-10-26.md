# 判读纪要 · 阶段 183（2026-10-26）

**主题**：批次 181 收口判定（4 项 FAIL）→ 定位「假 FAIL」根因 → 修仪器（探针形态 B ＋ 被测脚本三处加固）→ 注册 pin 层闸（㉔ 两缺口全闭）→ 起批次 183（修仪器必批次级复跑）
**性质**：只读现役面 · 零芯片动作 · 未改任何现役 GDS/网表/deck 字节 · 未建 pin 层 · 未派工 · 未重启常驻服务

---

## 一、开局

- 本口：2026-10-26 06:34:03Z–07:0xZ（本地 14:34–15:0x）｜触发：`stall_eye`（到点唤醒）⇒ **无新信、无新铃**。
- ★水位：上口交出 39691 ⇒ 本口起自 39692；账本末行 **39704**（收尾时读）。
- 同伴信箱：`inbox.jsonl` **381 行**（二进制读＋逐行 decode）**零新增**（末条仍是 8902 #8902-b7a0-2，00:44:21Z）⇒ 无待回明项。

---

## 二、批次 181 收口（实测）

批次 181 于 **2026-10-26T06:13:50Z** 收口（跑批器 pid 2747788 已退出）：

| 波 | rc | 结论 |
|---|---|---|
| A_light(29) | 0 | 42 项 FAIL 0 |
| **B_heavy(9)** | **1** | 22 项 FAIL 1 |
| C_very(2) | 0 | 4 项 FAIL 0 |

- 批尾必跑面：census/post **5/5 PASS**、probe/post **19/19 PASS**；现役四件 **ZERO_DELTA**；/tmp 新增 **0**（族内 0 族外 0）。

**收口闸 `batch_rerun_gate`（check）＝ FAIL（总项数 10 ／ FAIL 4）**：

| 判据 | 判定 | 事实 |
|---|---|---|
| G1/G2/G3/G8/G10 | PASS | 批次件完整、仪器字节现役、registry 现役、现役四件零变化、端态终局洁净 |
| **G4** | FAIL | 非零波＝B_heavy(1) |
| **G5** | FAIL | 回退 B_heavy: 0→1（相对上一批 167） |
| **G7** | FAIL | 回退 2（未声明 2）：`p4_lvs_leg/mode: EFFECT→NO_EFFECT`；`m4_assemble_drill/out: EFFECT→OUT_NOT_LANDED` |
| **G9** | FAIL | 探针自报 n_fail=1 |

★**上口「普查闸 C2/C3 既存回归」已证伪并最终取证**：本口在**干净窗口**（无批次在跑）跑 `fleet_hygiene_census census` ⇒ **3/3 PASS**（C1 族表 87 写向族全覆盖／C2 留残留 0 闸／C3 孤儿 0）⇒ 上口那次红是**跑批窗口内并发污染假警报**，**不存在该回归**。

---

## 三、★两项「回退」的真实成因（本口实测，逐一归因）

### 3.1 `m4_assemble_drill/out`＝OUT_NOT_LANDED（**假判死参数**）

扫掠 JSON 明细：两跑各 **16.7s / 14.1s**（**未超时**），`raised=[None,None]`，但两跑 stdout 均含**技能自身未捕获异常**的裸 traceback：

```
File "/data/workspace/tools/m4_assemble_drill.py", line 350, in main
    new_items = parse_items(Path(r1["lyrdb"]))
TypeError: argument should be a str or an os.PathLike object ... not 'NoneType'
```

根因链（三层）：

1. **被测脚本层**：候选件 DRC 跑批失败 ⇒ `r1["lyrdb"]` 为 None ⇒ 脚本虽有 `chk("K11", …, False, det)` 判据，却**继续下坠**执行 `Path(None)` ⇒ TypeError ⇒ **崩在落盘之前** ⇒ 输出路径型参数「未落地」。
2. **cwd 依赖层**：DRC 跑批按**工作根相对路径**取 PDK/规则文件 ⇒ 闸在任意 cwd（差分腿沙箱 `/tmp/a1sweep_*`）下跑必失败 ⇒ 上项在沙箱里必然触发。
3. **探针判据层**：探针的「技能自身崩溃」识别只认形态 A（`[FAIL] 闸内部异常`，即技能自己 catch 后打印的兜底）⇒ **裸 traceback 形态漏检** ⇒ 两跑都崩时漏到「输出路径未落地」分支 ⇒ 判「死参数」＝**假 FAIL**（违反★★异常即不可判律）。

⇒ **不是**「参数无效」，而是**技能自身崩了、差分腿根本没观测到正常路径**。

### 3.2 `p4_lvs_leg/mode`＝NO_EFFECT（不可判，判据正确）

`sweep_waveA_light.json` 的 `pairs_tried` 显示：探针只试了 **`sandbox_path_pair`**（域外哨兵路径对），**未构造域内枚举对**。根因：参数描述 `inventory=只读盘点（默认）｜rerun=加临时目录重跑…｜selftest=只跑负控` 含「**目录**」二字 ⇒ 被 `pathish` 判定误认成路径型 ⇒ 走路径兜底；两跑拿路径当 mode ⇒ 技能**静默回落 inventory** ⇒ 两跑无差异 ⇒ NO_EFFECT。
★该判定**本身正确**（★差分不证死律：不可判、不计 FAIL），但相对上一批 EFFECT 构成 G7「证据强度下降」。

---

## 四、本口修仪器（三处，只改工具字节，不碰芯片）

| # | 件 | 改动 | 依据 |
|---|---|---|---|
| 1 | `tools/skill_param_probe.py` | **新增形态 B 识别**：子进程非零退出 ＋ 输出含裸 `Traceback (most recent call last)` ⇒ 判 `INCONCLUSIVE_ERROR`（不可判、不计 FAIL）；判据链新增两条分支 | ★★异常即不可判律 ＋ ★技能自身崩溃不可观测律 |
| 2 | 同上 | **新增自检负控 6**（`sweep_self_uncaught`：裸 traceback 形态 ⇒ 期望 INCONCLUSIVE_ERROR） | ★双向校准律（闸有牙） |
| 3 | `tools/m4_assemble_drill.py` | ①`main()` 开头 **chdir 工作根**（消除 cwd 依赖，退出时恢复）②lyrdb 缺失 ⇒ **优雅降级**：不再 `Path(None)` 崩，K13/K14 记「未执行」，仍走零动作复核与**落盘**（报告文件照落地）③重复的 K11 编号改 K11b | ★闸自身不崩律 ＋ ★输出路径型参数无论成败都应落地 |

**探针自检（改后）＝ 19/19 PASS**（新增 `SWEEP_SELF_UNCAUGHT` 命中 INCONCLUSIVE_ERROR）⇒ 探针可进批次。

★**手工定向复测**（`/tmp` cwd 下，模拟差分腿沙箱）：修后 DRC 正常（K11b/K12/K13 PASS）、**报告落地**（11980 B）⇒ 沙箱可观测 ✔。

★**⚠ 另发现一处独立信号（不在本口修，已立项）**：`m4_assemble_drill` 的 **K14 负控失效** —— 今日实跑 K14 FAIL（负控件「drv1 故意平移 −200µm」对拍 added=0），而**阶段 97 归档证据 `playbook/_evidence_stage97/m4_assemble_drill.json` K14＝PASS**（added=24、added_top_side=12，18/18 全 PASS）⇒ **闸「有牙」相对归档出现回归**。已排除 cwd 假象（修 chdir 后仍 FAIL）⇒ 根因待查（平移量是否已不足、PDK 规则集变化、现役块版次几何余量），**下一批立项专项**。

---

## 五、㉔ 两缺口全闭（注册 + 覆盖度闸同步）

- **注册 `pin_layer_accept`**（registry 43→44；描述含 token `pin_accept`／`pin_layer_gate`／「pin 层验收」）。
- **覆盖度闸 `tools/m4_chain_gate_coverage.py` 同步编辑**（该闸**不在**批次仪器清单 ⇒ 编辑不破坏 G2；registry 变更则**必破坏** G3 ⇒ 注册严格排在批次收口后）：
  - `COVERING['pin 层']` 增列 `('pin_layer_accept', ['pad_rect','min_s','min_w','bbox','decision_table','pin_metal'])`；
  - `GAP_CLAIMS['pin 层']` 标 `closed: True`；K03 语义由「缺口存活」改为「**缺口面闭合验证**」（已关闭缺口须**命中在册专项闸**，否则声明与实况不符）；负控 NC-B 期望改为「推翻式扫描仍能命中（机制不因缺口关闭而失效）」。
- **覆盖度闸实跑＝7/7 PASS**（K01 现算 44 件；K02 命中 8 闸含 `pin_layer_accept`（脚本 23052 B，token 全中）；K03 缺口面闭合；K04/K05 负控仍咬；K06 现役四件 ZERO_DELTA；K07 残余诚实同屏）。

⇒ **待决 ㉔ 的两处缺口（顶层网表／pin 层）全部关闭**：顶层 v4 侧 4 面现成闸 ＋ 顶层网表闸（阶段 181）＋ pin 层闸（阶段 182 建、阶段 183 在册）＝ **三件均有显式专项验收闸**。

---

## 六、批次 183（修仪器必批次级复跑律 ⇒ 已起跑）

- 跑批器：`tools/stage183_sweep_worker.sh`（自 `stage181_sweep_worker.sh` 逐字派生，仅输出目录 `_evidence_stage183` ＋ LIGHT 29→**30**（增列 `pin_layer_accept`））。
- **pid 2929917**，2026-10-26T06:41:01Z 起跑；probe=`17d4839f`、census=`c7ad815a`、oracle=`133b5499`、**registry=`dab3c879`**（注册后的新值）。
- ★**G7 声明**：`playbook/_evidence_stage183/declared_changes.json` 声明 `m4_assemble_drill/out` 一项 —— 理由：阶段 181 的 OUT_NOT_LANDED 是**探针漏检技能自身未捕获异常**造成的假判死；修后落到「不可判」档属**修正误判**，非证据强度真实下降。`p4_lvs_leg/mode` 无需声明（与上一批同为 NO_EFFECT，无变化）。
- ★**跑批窗口内冻结**：不再改 registry／仪器字节（改则 G2/G3 当场暴露）。

---

## 七、结论

1. ★批次 181 的 4 项 FAIL 中，**G4/G5/G9 同源**（wave B 那 1 项假 FAIL：技能自身崩 ⇒ 探针漏检 ⇒ 误判死参数），**G7** 由两项档位变化构成（其一为假判死被修正、其一为域外取值塌缩的诚实不可判）。
2. ★**假 FAIL 已消除**（探针形态 B + 被测脚本优雅降级 + 消除 cwd 依赖）；探针自检 19/19；覆盖度闸 7/7；㉔ 两缺口全闭。
3. ★**新发现独立信号**：K14 负控相对阶段 97 归档失效（闸「有牙」回归），已排除 cwd 假象 ⇒ 下一批专项立项。
4. ★**零芯片动作**：现役四件现算 396571f0/96660、d5e1296c/63502、25adcbd1/79564、88d5d9c4/237672 ⇒ ZERO_DELTA；未建 pin 层、未新建顶层网表、未派工、未重启常驻服务。

## 八、下口待办（顺序不可颠倒）

1. **查批次 183 活**（pid 2929917；detach ⇒ 完工**自动按铃**；亦可查 `playbook/_evidence_stage183/worker.log` 的 `batch done` 与 `batch_end.txt`）。收口后：①干净窗口跑 `fleet_hygiene_census census`（C2/C3 终态取证，预期全绿）②跑 `batch_rerun_gate`（check）取收口 verdict（预期 10/10；G7 靠 declared_changes 豁免）。
2. **重生决策包 ＋ 复跑断言实测闸**（K02 须绿）⇒ 交付**有效裁点**（舰队 44 件、批次 183 有效）。★批次产物会重写各闸证据 JSON ⇒ 证据 sha 只在最后一次批次收口后稳定。
3. **K14 负控失效专项立项**（相对阶段 97 归档回归的根因：平移量/PDK 规则集/现役块几何余量三查）。
4. **待管理员裁 ①–㉚**（末封 26795 未回）；★**㉕ 可直接裁**（建议 A ＝ 顶层自建 via 栈）；★**㉔ 采 A 的第一批动作（建 pin 层闸）已就位并在册**；清理令等一句「是否一并清」。
