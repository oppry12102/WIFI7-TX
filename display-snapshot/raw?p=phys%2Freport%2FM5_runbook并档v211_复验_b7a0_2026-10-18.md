# M5 runbook 并档 v2.11 独立复验记录（b7a0 · 2026-10-18T06:3xZ）

**结论：独立复验五项全 PASS，裁定⑥销案条件达成。** 本记录为组长侧独立重跑，先跑后看 fde9 举证。

## 到货五件 sha 验收（8510 design/sow6/，06:22:33Z 到件铃×5）

| 件 | bytes | sha256 | 对拍 |
|---|---|---|---|
| sow6m5_pex_runbook.md（head v2.11） | 39920 | b4cc3efb01e58c9de4308588afc16d92fdadbd95b6b17cd2fdf3e0e359246aa5 | 信列一致 ✅ |
| sow6m5_pex_runbook_81155521_prev.md（A v2.10 归档） | 31740 | 8115552116c264de8f5fc963c2a5b6517b7eb0bee26a1af9aff5f0f4123ccf4d | =我台账 A v2.10 全串 ✅ |
| runbook_v2.5_e629bb28_prev.md（B v2.6 归档） | 23716 | e629bb283581bad3d2e6fbe0bc65bd0820aef1ac5c881d4779274cabc0c2cda1 | =B 线 v2.6 全串 ✅ |
| pex_jia_sha256.json（升版） | 24076 | 6a00e15da75e8725d7020729945f763cbaf8debb2cc6da5494235d9d4c02d6e4 | 信列一致 ✅ |
| M5_runbook并档v211_举证_2026-10-18.md | 8385 | 58780f3273f488cf2e6408a8aa9dfcc7e37165ca029ecb8ac43c10a1ffc65397 | 信列一致 ✅ |

②③ 为 cp -p 归档（非重生成）：与我台账既有基线 sha 逐位同串实证。

## 独立复验五项

1. **diff A_prev→v2.11**（diff -u）：**hunks=3、删 1 行（仅头部版本行 v2.10→v2.11+并档出处）、增 87 行**。
   行数口径自校：69（三段 9+19+41）+2（消歧注引用行+空行）+16（hunk1 版本行+CHANGELOG v2.11 条目）=87 ✅
   （首跑 grep 计 72 系漏计 15 个空增行，补空行后与 fde9 报数逐位吻合——零差异。）
2. **三段逐字对拍 B_prev**（我侧脚本切段逐行比）：cdl 版本门 9 行 / §3.1 19 行 / §3.2 41 行 **全等 ✅**（判据①独立重证）。
3. **锚点 grep 独立重跑**：sensitivity_jump_verdict 4→4｜m5_drv2_suspicious 6→6｜m5_pvt27_receipt 5→5｜m5_pex_pipeline.py 3→3｜m5_cdl_reship_check.py 4→4 **全不变 ✅**；§0.6 一键链、§4.1-A（×8）、§五 段全在。
4. **A 侧正文零删改**：hunks=3+删 1 数学保证 §〇/§0.6/A0 六判据/门1门2/§4.1-A·B/§五 逐字未动 ✅。
5. **pex_jia_sha256.json 结构核**：runbook_head=v2.11 b4cc3efb（39920B）、runbook_v211、runbook_v210=81155521…（**v2.10 历史行保留**）、runbook_v26=af71aa60…（**A 线键未动**）、runbook_v26_B_fork=e629bb28…（B 线单列+注）、changes 7→8 条末条含 not_merged；台账 20+ 已知锚（三 cdl 基线/suspicious 19b26837/判据器 ca38d0f3/pipeline 74c3e83a 等）交叉核全对 ✅。旧 json（513885d8）我侧无底，以锚核代 diff 接受。

## v2.11 版本行（台账订正依据）

`# SOW-6 M5 · PEX 代入执行手册（runbook v2.11；并档：并入 B v2.6 e629bb28… 三段增量＝§一.0.5 cdl 版本门 / §3.1 第五受害面 / §3.2 第六受害面·裁定十二，零口径/零门限/零判据器改动）`

## 本轮裁定（随回执下达）

- **裁定十三**（0.5 编号撞车）：维持 fde9 处置——B 段编号/正文一字未改+段末消歧注；新增条款：**今后引用一律带标题词**（「§一.0.5 cdl 版本门」/「§一.0.5 A0 判据」），禁裸引「§一.0.5」。
- **裁定十四**（§四 导航注）：**补，升 v2.12 单行微改**（§四 标题行照 B 原句追加「；点火版本门见 §3.2：仅 v20 回改版」）；增量举证即可（diff vs v2.11 预期 hunks=2：标题行 1删1增+CHANGELOG 条目），v2.11 已验收归档不动。
- **裁定十五**（B 线 CHANGELOG v2.5.1/v2.6-B 两条）：认可不搬运——引用+归档 ③ 可回读已足，重复搬运=制造两处真相。
- v2.6 双线版本号处置（B_fork 单列）认可；双方台账标注线别。
- 小账：`runbook_merge_v211_evidence.json` 信称同批落 design/sow6/ 但到货目录无此件，候补投。

## 状态（不变项重申）

主闸门仍候 b7e7 修复版三 cdl（fde9 06:22Z 复跑=基线 33e9e754/ae4feb76/1f5e0cd8，A0 不启动、27 角不点火、停线维持）；到货动线=§一.0.5 版本门→A0→E 一键链→我侧 deckfix_v3 LVS 对拍。并档收益：照 A 执行漏版本门的风险自本口起消失。

—— b7a0（组长）2026-10-18T06:3xZ · 复验工具 tools/verify_runbook_merge.py + 人工终判
