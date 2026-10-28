# 判读纪要 · 裁定一百二十 · happy 腿沙箱化边界与探针递归缺陷（阶段 130）

- 日期：2026-10-24（本地 2026-10-25 凌晨）｜作者：b7a0（WiFi7-TX 组长）｜性质：只读现役面 · 零动作
- 承接：阶段 129（裁定一百一十九）留下「happy 腿（真实逻辑腿）默认路径覆盖残余风险 ⇒ 默认只跑 error」。
- 本阶段任务：把该残余风险**量化并机器化**，回答「哪些件可安全开 happy 腿」。

## 一、静态腿：逃逸风险五级分级（注册表 34 件全覆盖）

| 级 | 判据 | 件数 |
|---|---|---|
| E0 | 无写调用检出 | 0 |
| E1 | 写仅经 open/os.open ⇒ 可被补丁重定向 | 9 |
| E2 | 起子进程（subprocess/os.system）⇒ 写逃逸不经补丁 | 11 |
| E3 | 含危险写（os.remove/unlink/replace、shutil.copy/move/rmtree）⇒ 不经补丁，能真删真覆盖 | 14 |
| E4 | 外部库写（KLayout/sqlite）⇒ 绕开 Python 层补丁 | 0 |

**★结论：34 件中仅 9 件候选可开 happy 腿**；E2/E3 共 25 件一律不开（子进程写逃逸与危险写是真能改现役面的路径）。
**★围栏盲区**：阶段 129 探针围栏只覆盖 7 个根（phys/verify/gds/design/tools/playbook/outbox_files）⇒ workspace 其余目录是盲区 ⇒ 本阶段新闸改**全根围栏**（仅排除 PDK/会话等只读第三方，并对 PDK 做批级尾检）。

## 二、实跑腿：白名单 4 件真跑通（结论行 FAIL=0、围栏越界 0、现役四件逐位未变、PDK 尾检洁净）

白名单：**p3_net_bridge / artifact_identity / m4_drc_attrib / m4_route_rework**（实测 PASS 4/4）。
禁开 4 件（逐条理由与证据见 `playbook/_evidence_stage130/excluded.json`）：decision_pack、delivery_gate、g2_access_corridor、g2b_via_stack。

## 三、★最高价值发现：探针 happy 腿的 `os.makedirs` 递归缺陷（阶段 129 探针本体）

- 现象：凡 happy 腿中**需新建目录**的件 ⇒ `RecursionError: maximum recursion depth exceeded`（栈顶 `<frozen os>:213`）。
- 根因：探针 CHILD 把 `os.makedirs` 换成补丁函数，而**真 makedirs 内部递归调用的是模块全局名** ⇒ 递归重入补丁 ⇒ 无限递归；
  且补丁 `_open` 自己在建父目录时调用真 makedirs ⇒ 任何写到「尚不存在目录」的文件必炸。
- 影响面：happy 腿**从未被真验证过**（阶段 129 默认只跑 error 腿 ⇒ 缺陷未暴露）。「默认只跑 error」这个保守默认**保护了我方**。
- 修法（下口执行，动探针本体须留档＋行为保全自证）：补丁侧改用**逐级 `os.mkdir`**（真 mkdir 不递归）替代真 makedirs，并禁止补丁内部调用会递归的 makedirs。

## 四、★三形态沙箱化的硬约束（本阶段实测归纳）

1. **monkeypatch open**：对多数件可行，但与需建目录/需重入的件不兼容 ⇒ 假 FAIL。
2. **输出参数重定向**：对「os.path.join(ROOT, …)」型**部分**有效，对「ROOT+字符串拼接」型**无效**（路径重复）；且对**输入语义参数**（md/file/dest）盲目重定向会造**假 FAIL**（阶段 129 探针的 `md` 即在输出名集合内）。
3. **专根真跑**：产物受控但**覆盖既有交付件后不可回滚** ⇒ 会覆盖既有件者一律禁开。
⇒ 综合结论：**happy 腿只能对「写入仅落在受控新增路径、且与补丁兼容」的件开启；否则宁可不开（假绿律）。**

## 五、判定口径自纠（★假绿律）

只看「有结论行」**不算通过**：必须解析结论行里的 FAIL 计数（`总项数 N ／ FAIL f`），f>0 即判该件失败。
本阶段据此把 delivery_gate／g2_* 的「有结论行」从假绿纠正为真 FAIL。

## 六、零动作与纪律

未改现役四件与任何现役 GDS／网表／deck 字节（逐位 sha 现算未变）｜未产交付面合并件｜未建顶层 pin 层／顶层网表｜未派工｜未上传冷备｜未评估情形 B｜未跑 Q3｜未动 M5 链件｜★未轮换 8510 file-key（待管理员裁）。
★副作用自证：负控 NC-A（子进程写 workspace）**被围栏检出**（新增=1）且跑后**清零**（残留复检为空）；PDK 尾检洁净。

## 七、下口待办（按优先级）

1. **修探针 happy 腿的 makedirs 递归缺陷**（改已验证件 ⇒ 留档＋编译自检＋行为保全自证＋自检复跑），顺带把围栏扩为全根。
2. 修 delivery_gate 的 ROOT 字符串拼接（改前留档＋行为保全自证）。
3. 在探针修好后，把 4 件禁开件按「白名单＋逐件例外」重新评估（decision_pack 仍禁：会覆盖既有交付件）。
