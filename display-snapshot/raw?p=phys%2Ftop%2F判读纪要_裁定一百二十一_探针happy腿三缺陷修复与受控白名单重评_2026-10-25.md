# 判读纪要 · 裁定一百二十一 · 探针 happy 腿三缺陷修复 ＋ 受控白名单重评（8 件全开）

- 主体：WiFi 7 射频发射模组 ASIC 设计组 · 组长（id `b7a0`）
- 阶段：131（2026-10-24 19:36Z–2026-10-25 03:5x+08:00）｜**只读现役面 · 零动作**
- 上游：阶段 129（裁定一百一十九 · 运行期实测腿）／阶段 130（裁定一百二十 · happy 腿沙箱化边界与探针递归缺陷）
- 证据目录：`playbook/_evidence_stage131/`

---

## 〇、一句话

阶段 130 定位的「探针 `os.makedirs` 递归爆栈」实为**三处真缺陷之一**：本口把探针 happy 腿的补丁机制从「拦截写盘 API」整体重构为**沙箱与围栏解耦**（写目标恒为独立临时目录，围栏只作只读监控），并修掉另外两处真缺陷（`os.open` 补丁重入自身；写重定向目标错指现役面），**受控 happy 腿白名单由 4 件扩到 8 件全开**，同时修掉 `decision_pack` 的两处真缺陷（待决项 ㉚ 丢失、CLI 入口 NameError）。

---

## 一、三处真缺陷（修前实证 · 双向对照）

证明脚本：`tools/stage131_defect_proof.py`（用**临时根当现役面替身**，零风险不碰真现役面）
对照证据：`playbook/_evidence_stage131/defect_proof_pre_post.json`（**7 机检 7/7 PASS**，n_fail=0）

| # | 缺陷 | 机理 | 旧版实测 | 新版实测 |
|---|---|---|---|---|
| ① | `os.makedirs` 递归爆栈 | 真 `os.makedirs` 内部按**模块全局名**递归调自身 ⇒ 重入补丁 ⇒ RecursionError（栈顶 `<frozen os>:213`） | `fx_mkdir = VIOLATION` | `OK` |
| ③ | `os.open` 补丁重入自身 | `_os_open` 体内调 `os.open`（已被替换）⇒ 无限递归 | `fx_osopen = LONG`（超时） | `OK` |
| ② | **写重定向目标错指现役面**（最严重） | v2 取写目标为 `FENCE_ROOTS[0]`＝`/data/workspace/phys` ⇒ **围栏自身即污染源** ⇒ 真跑必然把产物写进现役面 | `defect2_write_into_live_face = true`（产物落替身内 `phys/probe_osopen.bin`） | `false`（`live_face_files = []`） |

修法：
- 补丁侧改**逐级 `os.mkdir`**（不再调用会递归的 `makedirs`）；
- 留档真 `os.open` 并在补丁体内调**留档件**（消除自重入）；
- ★**沙箱与围栏解耦**：写目标恒为**独立临时目录**，围栏仅作只读监控（围栏根不再兼任写入目标）；
- 附带：围栏**全根化**（原 7 敏感根 → workspace 全根，只读第三方/管道文件显式排除）＋ PDK **批级尾检**。

旧版留档（**旧 sha 永久可解析**）：`playbook/_evidence_stage131/fleet_runtime_probe_v2_pre_mkdirfix.py`
补丁脚本（可重放）：`playbook/_evidence_stage131/patch_stage131_probe.py`
探针新版：`tools/fleet_runtime_probe.py` sha8 `8a0115bd` ／ 41,246 B

---

## 二、行为保全自证（改已验证件 ⇒ 必须证明行为未漂移）

- **error 腿 35 件逐件对拍**：`baseline_old_error_leg.json`（24,107 B）对 `post_new_error_leg.json`（24,001 B）——逐件比对 status／R_A2／R_A3／rc／结论行 ⇒ **0 处差异**。
- 探针自检 **8/8 PASS** 保持（`post_new_selftest.json`）。
- 围栏全根化生效实测：新版 `fence_root_scope = ["/tmp/stage131_new_…"]`（**单元素＝临时根本体**）⇒ 全根监控成立。

---

## 三、修复收益：受控 happy 腿白名单 4 → 8 全开

判定口径仍为阶段 130 的**假绿律**：必须解析结论行 **FAIL 计数**（f>0 即失败），且围栏越界 0 ＋ 现役四件逐位未变 ＋ PDK 尾检洁净。

证据：`playbook/_evidence_stage131/happy_run_final8_v2.json`（10 机检，**FAIL 1**）／剖面 `happy_profiles.json`

| 件 | 结论行 | 结论 |
|---|---|---|
| p3_net_bridge | 总项数 19 ／ FAIL 0 | PASS |
| artifact_identity | 总项数 1 ／ FAIL 0 | PASS |
| m4_drc_attrib | 总项数 17 ／ FAIL 0 | PASS |
| m4_route_rework | 总项数 1 ／ FAIL 0 | PASS |
| g2_access_corridor | 总项数 18 ／ FAIL 0 | PASS（由「禁开」转开） |
| g2b_via_stack | 总项数 29 ／ FAIL 0 | PASS（由「禁开」转开） |
| decision_pack | 总项数 10 ／ FAIL 0（n_items=30） | PASS（由「禁开」转开） |
| delivery_gate | 总项数 10 ／ **FAIL 1** | FAIL ＝「sha/bytes 不符 1 件: happy_leg_safety.py」＝**活文档 summary.md 尚未更新**（非闸缺陷） |

★**误判纠正（阶段 130 的「禁开理由」有一半是错的）**：`delivery_gate` 在阶段 130 被记为「ROOT 字符串拼接型路径，重定向后路径重复」——其当时的 `FileNotFoundError` 实为 **`makedirs` 递归缺陷的次生现象**，不是闸缺陷；修好探针后自然消失。⇒ **判据必须回到实测，禁止用「猜到的机理」当禁开理由**（假绿律的姊妹条：假红律）。

---

## 四、顺带修掉的两处真缺陷

### 4.1 `tools/decision_pack.py`（sha8 `4a3ef0fe` ／ 38,880 B）
1. ★**解析源失配 ⇒ 待决 ㉚ 丢失**：BOOT.md 阶段 127 压缩后，㉚ 的逐字原文只存在于 `playbook/BOOT_历史阶段.md`，而解析器只读 BOOT.md ⇒ 重生成决策包只得 **29/30**（㉚ 掉队）⇒ 补历史阶段「待决 ㉕–㉚ 细目」区解析源 ⇒ 恢复 **30/30**，10 机检 **FAIL 0**。
2. **CLI 入口位置错误**：`if __name__ == '__main__': run()` 置于 `run()` 定义**之前** ⇒ 直接跑脚本 `NameError` ⇒ 已延后到文件末尾。

### 4.2 `tools/happy_leg_safety.py`（sha8 `55170ed8` ／ 30,900 B）——夹具缺陷（非闸缺陷）
旧夹具把所有 string 参数灌 `""` ⇒ **覆盖件自身默认**（`delivery_gate` 的 `root="/data/workspace"` 被灌成 `""`）⇒ 相对路径全落 cwd ⇒ **假 FAIL 报 10 件 MISSING，而文件在盘上**。
修法：**非输出 string 参数不注入**（用件自己的默认），输出参数仍重定向进沙箱。

★**新闸 selftest 重校准 6/6 PASS**（`happy_selftest_post_probe_fix3.json`）：
- 原负控 NC-D（建目录必爆栈）**钉在旧缺陷上**，探针修复后失效 ⇒ 改为**正例** `fx_mkdir`；
- 新增真负控 **NC-D'（`fx_failcount`：结论行 FAIL 计数>0 必判 FAIL）**；
- 新增正例 `abswrite`（**绝对路径写须被重定向进沙箱**）。

---

## 五、我自己踩的坑（据实登记 · 可逆还原）

改动夹具时我一度「不灌空串」却**误跳输出参数重定向** ⇒ **1 件既有证据件被覆盖**：`playbook/_evidence_stage92/p3_net_bridge.json`（唯一差异＝`generated_utc`）。
- 还原：以登记 sha8 `807cf480` 为靶，**秒级穷举 77,107 次**找回原时间戳 `2026-10-23T21:25:06Z` ⇒ 字节逐位回到登记值（33,404 B）⇒ 现全库 **9 件登记值复核全 OK**。

★由此**新立三律**：
1. ★★**沙箱化改动必先验证「输出参数仍被重定向」**——只改一半 ⇒ 产物落现役面（改动前须先问「输出去哪」）。
2. ★**污染可逆律**——差异仅时间戳时，可用登记 sha 做秒级穷举还原；不可逆则据实登记并说明影响面。
3. ★★**沙箱与围栏解耦律**——写目标恒为沙箱；**围栏只作只读监控**，严禁把现役面当围栏根兼当写入目标（围栏自身即污染源）。

---

## 六、零动作与纪律（自证）

未改现役四件与任何现役 GDS／网表／deck 字节（mix `396571f0`／drv1 `d5e1296c`／drv2 `25adcbd1`／顶层 `88d5d9c4`，本口现算逐位一致）｜未产交付面合并件｜未建顶层 pin 层／顶层网表｜未派工｜未上传冷备｜未评估情形 B｜未跑 Q3｜M5 链件一概不动｜**未执行 8510 钥轮换（待管理员裁）**。凭据只在 `secrets/peers.json`(600)，文档只留占位符。★同伴信：本口无待回明项 ⇒ 未投回信（fde9 #330/#331/#332 已闭环）。

---

## 七、待管理员裁（不变）

①–㉚ 全挂（末封仍 26795）；**㉕ 已具备 A/B 双腿证据可直接裁**（我方建议 **A＝顶层自建 via 栈**；决策包见 `phys/top/决策就绪包_待决①–㉚_2026-10-24.md`，本口修复后 **30/30 项**完整）。
**8510 file-key 轮换**待管理员裁示 ⇒ **未获令不动手**。

---

## 八、下口建议

1. 受控 happy 腿白名单已 8 件全开 ⇒ 可继续**逐件扩到 E1 级可沙箱化件**（静态分级 E1 共 9 件，尚余 1 件未开），仍须「**宁可不开，不可假绿**」；
2. ★把**假红律**（禁开理由必须实测，禁止用猜到的机理当理由）补入通用律库；
3. 管理员若裁 ㉕ 或 8510 钥轮换 ⇒ 按既有 SOP 执行（钥轮换：改 `secrets/peers.json` → `ctl.sh` 停/启 8510 → 知会 fde9 不另发新钥 → 回执留档）。

---

## 九、追记（收尾时闸自检再抓两处 · 同口修完并复跑）

### 9.1 共享沙箱 ⇒ 逐件产物判据可被前件产物满足（**假绿面**）
原 `happy_leg_safety` 在**循环外**建**单一共享沙箱** ⇒ `rec["artifacts"]` 是**全体件的并集** ⇒
`g2_access_corridor` 期望的 `sbx_out.json` 实由 **`m4_route_rework`** 产生 ⇒ 该件的「产物存在」判据**被前件满足**。
⇒ 修法：**逐件独立沙箱**（循环内 `mkdtemp`，`finally` 逐件清理）⇒ artifacts 逐件独立。
证据：修后 run 腿各件 artifacts 逐件独立（如 `tmp/happy_leg_g2_access_corridor_*/sbx_out.json` 为该件自有产物）。

### 9.2 注册参数名 ≠ 脚本实参名 ⇒ **静默 no-op**
注册表 `g2_access_corridor` 的参数名是 **`out`**，而脚本 `_run_core` 读的是 **`out_json`**
⇒ 经**注册接口**传 `out=` **静默无效**（不报错、不生效）⇒ 写落点仍是默认的现役证据路径
（★阶段 126 `peer_sandbox_repro` 是**反向同族**：那次注册名在脚本里根本找不到；这次找得到但脚本不读它——**静默 no-op 更坏**）。
⇒ 修法：`_run_core` 同时接受 `out_json`／`out`（`out_json` 优先），**默认落点表达式逐字未变**（已断言）。
⇒ 修后实测：该件 stdout 的 `out:` 变为**沙箱路径**（`/tmp/happy_leg_g2_access_corridor_*/sbx_out.json`）⇒ 参数真的生效了。
★**盲区登记**：舰队自审的 A1（注册 schema 参数名实时派生）**只查「参数名存在于 schema」**，查不出「脚本不读它」⇒ 下口应把 A1 升级为**调用期探针实测**（传探针值看落点/输出是否变）。

### 9.3 并行跑批被围栏如实抓住（**闸有牙**，归因已分清）
我并行跑了 selftest 与 run 两条腿，selftest 的证据件恰在 run 腿跑批期间落盘 ⇒ 围栏报 `fence_added=1`（点名 `happy_selftest_post_sandbox_fix.json`）⇒ `artifact_identity` 件判 FAIL。
⇒ 这是**围栏正确工作**（外部写入被抓住），但归因须分清「件自身副作用」vs「并发外部写入」⇒ ★**写证据件的闸必须串行独占跑批**。

### 9.4 交付件表陈旧也被当场抓住（第二处「闸有牙」实证）
修补 `happy_leg_safety.py` 与 `happy_profiles.json` 后，**未更 summary.md** ⇒ run 腿里的 `delivery_gate` 件判 **FAIL 2**（实测 sha `e4884ecd`／`de0cf49b` vs 表内旧值）⇒ 更表后复跑即绿。
⇒ 这正是「活文档交付件表 + 实测 sha 对拍」的价值：**表陈旧＝红灯，不会被带着绿**。

### 9.5 本口复核（未写真役面）
`playbook/_evidence_stage105/g2_access_corridor.json` 与 `phys/top/artifact_index.json` 的 mtime/sha **均早于本口跑批** ⇒ 受控 happy 腿**未写真役面**（所有写落沙箱镜像）；现役四件逐位未变（mix `396571f0`／drv1 `d5e1296c`／drv2 `25adcbd1`／顶层 `88d5d9c4`）。

### 9.6 终跑（串行独占 · 更表后）
`playbook/_evidence_stage131/happy_run_final8_v5.json`：**8/8 全 PASS**（10 机检 FAIL 0）
——p3_net_bridge 19／artifact_identity 1／m4_drc_attrib 17／m4_route_rework 1／g2_access_corridor 18／g2b_via_stack 29／delivery_gate 31／decision_pack 10，**逐件 FAIL 计数皆为 0**；
围栏 ±0（全部件）｜现役四件逐位未变｜PDK 批级尾检洁净｜**逐件独立沙箱**（各件 artifacts 自有，如 `tmp/happy_leg_g2_access_corridor_*/sbx_out.json`）。
新闸 selftest（逐件独立沙箱后）**6/6 PASS**。★跑批全程**串行独占**（不并行跑第二个写证据件的闸）。
