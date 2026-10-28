# 判读纪要：M5 口径甲代入首轮 · 门1 OP 无解 · cdl 31/31 粘连（deck bug 第三受害面）

- 时间：2026-10-18 02:55~03:05Z（UTC）
- 与会：b7a0（组长判读/裁决）｜fde9（仿真验证，口径甲代入与双门执行）｜b7e7（电路设计，deck 修复责任侧，本口通报）
- 触发：fde9 五件到（8510 design/sow6/，02:55:07Z 铃×5）+ inbox #170 回执信

## 一、到件验收（sha 全对）

| 件 | B | sha256 前 16 |
|---|---|---|
| M5口径甲代入回执_2026-10-18.md | 9456 | 2442261f926ec791 |
| M5门1判定与结构审计_2026-10-18.json | 6384 | 10edbacba522398c |
| pex_struct_audit.md | 6677 | 7ff51e7602706fa8 |
| pex_subst_audit_jia.md | 15869 | d4b920e5e9310dea |
| pex_jia_op_screen.log | 14129 | 56f4eb8b51f724f5 |

本地落盘：sim_report/pex_jia_20261018/。

## 二、四裁执行对账（fde9 全 ✅）

一（口径甲白名单替换 L0 实物件）✅；二护栏1（映射日志 pex_subst_audit_jia.md）✅；二护栏2（门1 Δ=0 机器闸：前仿 .op 重跑 A0′=0.000000）✅；三（双门按 0.05/0.5 dB 实现，本次未进）✅；四（cmim 面项 771.573 fF）✅。

## 三、门1 判定：FAIL（OP 无解，非超门）

`.op` 快筛件 singular matrix at **xmi.nsens**（×6）→ dynamic/true gmin stepping、source stepping 依次全败 → "The operating point could not be simulated successfully"。A0′ 不可测；门2 未评、27 角未点火（口令②停线带原始数据 ✅）。

## 四、根因（静态结构审计，三阶段 31/31）

- **31/31 HBT 基极=发射极同名**（mix 15/15、drv1 4/4、drv2 12/12）= B-E 结全焊死；
- 8 R 自环（mix e1a/e2a/e1b/e2b×4、drv1 e1/e2、drv2 ccas1×2）；
- merged-domain WARNING：`['gnd','nsens','ntaila']→ntaila`、`['lond','lopd','nswa','rfon','rfop']→lond`（**gnd 也被并没**，提取侧自带 pending-deck-fix-re-extract 声明）；
- 被并没 deck 网共 14：mix 8（hbt_mirror/lopd/nsens/nswa/nswb/ntailb/rfon/rfop）+ drv1 2 + drv2 4；
- 标称值层全对：派生层自测 9/9 机器精度（~1e-16）复现前仿网表值 ⇒ **「值全对、拓扑全错」**。

**归属：提取 deck 幻影焊（bjt_derivations.lvs L59 covering-bbox 端子识别 bug）同源第三受害面**：
①LVS 报告假 FAIL → ②LVS 幻影焊（版图无罪已判决，判读纪要 20:0xZ）→ ③PEX cdl 网名粘连 → 仿真 OP 无解（真伤：cdl 是交付网表）。
非代入器/派生层/口径甲实现问题。

## 五、组长裁决（R1~R4 + 新增裁定五）

- **R1 确认**：deck 修复版 cdl 到货即重跑门1/门2（预授权有效，无需请示）；双门过即点火 27 角。
- **R2 确认＋先验**：修复后 b==e 仍在 = 版图真短 → 回改流程，不以改名掩盖。先验：flood_full 验尸案发现场零短路 + GDS 无 31/0/60/0 + nwell 假说死 ⇒ 版图真短概率极低。
- **R3 备案确认**：实物孪生剔除 5 件（mix R15/R16→deck RL 45Ω、drv1 R8/R9、drv2 R11/R12→deck RL 100Ω）正确（不剔则阻值减半硬错）；规则固化代入器常驻白名单 + 27 角回执续列（异动即报）。C1~C4 与 Cca/Ccb 并存非重复计入（对地 vs 片外串联耦合）亦认可。
- **R4 备案同意**：−0.44% 注记 27 角点火后落报告首页；v1.1 perim 窗归零时刷注记。
- **裁定五（新增）：cdl 重提验收六判据**——①31/31 b≠e ②R 零自环 ③merged-domain WARNING 清零（gnd 独立专项核）④14 被并没网全回归 ⑤nref 网须附提取器来源映射（疑=hbt_mirror 改名，不得无名新增）⑥端口序复核。全过 → 直接跑门；任一不过 → 停线带原始数据。

## 六、门限有效性背书（收讫备案）

同 deck 重跑 CG=17.446489113733694 dB 与 10-17 首跑逐位一致（Δ=−1.09e-05 dB vs 锚 17.4465）⇒ 噪声底 1e-5 dB，0.05 dB 操作门 ≈ 4600× 噪声底。修复版到货后 |ΔCG|>0.05 dB 必为物理量。

## 七、下一步

1. **主闸门（不变，双线）**：候 b7e7 deck 修复版 → LVS×v3 对拍闭环（b7a0）+ cdl 重提六判据→门1/门2→27 角（fde9）。
2. 本纪要 + 两信底稿（fde9 裁决 / b7e7 通报）投 8510 design/sow6/ 与两 inbox。
3. 通报管理员一句（阶段报备）。

—— b7a0 · 2026-10-18T03:05Z
