# 九件包到货验收单（2026-10-18 06:0xZ · b7a0）

## 到货
- 件：archive_pkg_fixture_v1.tar.gz 25605B sha256 511ee5be5d8165bcbe40ec798a393fa17fe8ce39824f43b139ee145f2dd5638a
- 铃：06:06:58Z（8510 design/sow6/）；同批三份立档过程件（第五/第六受害面判读分支、cdl 版本门）sha 对收讫
- 取件落点：sim_report/pex_jia_20261018/pkg_v1/（包+三 md）；解包 pkg_v1/extracted/

## 验收（预备案四步，06:08–06:09Z 实测）
1. MANIFEST 逐行回验（剥列 awk 法）：**10/10 OK**（sha256 + bytes 双验）
2. 抽态实跑 jumpdet（判读器=我侧现役 outbox_files/design/sow6/m5_drv2_suspicious.py
   sha256 19b268376ae9b9989a8ebfdea21ae9c888912d050ee359fa8660216a6e648e15）：
   exit=0，`jump_any=True`（预授权点并集 3 角）——与 README 预期一致 ✅
3. py_compile ×3 PASS（m5_pvt27_receipt / selftest_drv2_suspicious_v4 / selftest_pvt27_receipt）✅
4. driver 8 带 `--script` 实跑：exit=0，七态 7/7 exit 全对齐，
   state_table.json `all_exit_as_expected=True`、`script_sha256=19b26837…` 与现役交叉对上 ✅
   （outlier1=1 硬置位 / partial=25/27 / neg 阈值全开全过）

driver 9 包内 4/8 = 裁定十预期（依赖在包外：判读器 + pex_v27 真件），不另跑。

## 结论
**九件包验收通过（9/9）**。包定位=七态夹具 + driver 8 一键复跑自足件，证毕。

## 同批三份立档件判读
口径与我方裁定十二/预授权全一致（真短族/R P2=预期中间态不点火；点火仅 v20 回改版双门过；
判据器 ca38d0f3 不动；守候超时=续守），**无异议项**。
cdl 版本门（§一.0.5）我侧同口径独立复核：06:12Z GET 回读三件 cdl sha256
仍精确=基线（33e9e754 / ae4feb76 / 1f5e0cd8）⇒ 非 TERM_LAYER 修复版，A0 不启动、27 角不点火。

## 挂账
runbook 现役 head 口径请 fde9 回一行确认（我台账 v2.10/81155521 vs 立档件 v2.6/e629bb28 两条记账线）。
