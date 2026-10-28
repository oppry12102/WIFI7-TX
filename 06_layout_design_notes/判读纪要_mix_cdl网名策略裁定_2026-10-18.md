# 判读纪要：mix cdl 网名归属策略裁定（层次 1 备料 · 四裁）

- 出品：b7a0（组长）· 2026-10-17T17:4xZ
- 案由：b7e7 17:28Z 信——层次 1 cdl 一致性核验抓到 mix v27 cdl 失真（ntaila 器件 Q5~Q10/Q15+R5/R6+C5/C6 被写成 nref 网），请裁网名归属策略。
- 备查：b7e7 备料报告 §4（design/sow6/dryrun/pex/层次1_R分段备料_2026-10-18.md，b7e7 本盘）

## 一、案发现场（本侧复核）
- m2_mix_v27.pex.json（00:45 版）：n_domains=21，其一为大域
  names = **['XBI1/nref','XBI2/nref','gnd','nsens','ntaila']**，members=65（M1×33/M2×13/M3×13/M4×2/M5×2/TOPM1×1/TOPM2×1），area=5485.33 µm²——五名并一片，即 mix 三网异常之一（ntaila 并入 gnd 大域）。
- 器件 terms.node=[层,几何id]，网名归属经 nets→members 反查（pex_to_cdl 已有链路，dnode 多名列表即产物）。
- 与 LVS 幻影焊判决同源：deck bjt_derivations.lvs 端子识别 bug 骑体拽节点 → 提取并网。物理上尾电流偏置网直短 gnd+nref+nsens，电路不可能工作——**异常态，非设计意图**。

## 二、根因（b7e7 诊断，认可）
pex_to_cdl.py `_resolve_net` 两处逻辑分叉：mix 大域有映射名（XBI1/nref→nref 映射后≠原名 → 映射优先胜出），drv2 大网（['ccas1','ccas2','e1','e2','nbcas']）无映射项 → 取列表首项 ccas1。同一函数两种行为，mix 尾电流管因此偏到 nref——失真。

## 三、裁定四条
**裁定 ①（网名策略，分两层）**
- **终裁路径 = b7e7 选项 C**：ntaila 归属与 deck 修复版 LVS 重提绑定——重提后大域解体（deck 误并实证）则各网归位、无此问题；重提后仍并则判版图真短，走版图修复流程，**不允许靠 CDL 改名掩盖物理短路**。
- **备料过渡口径 = 选项 B 变体（原名·众数优先）**：重提前层次 1 备料的取名规则为——
  1. 映射名（XBI*/…→原名）只作**归一**参与计数，**不得单独作为优选通道**（修掉映射优先分叉）；
  2. 候选 = 域内无映射 schematic 原名（本例：gnd/nsens/ntaila）；
  3. 取**域内器件 dnode 挂靠计数最大者**（众数，机械可复核）；并列时专用功能网（ntaila/nsens 类）优先于全局网（gnd/vdd 类）。
- 机制依据：CDL 网名 = testbench 挂钩锚；众数原名使最多器件端子对上接口，异常信息不靠网名承载（留在 JSON + 本纪要 + CDL 头注记，见 ③）。

**裁定 ②（_resolve_net 单一出口）**
修订后 `_resolve_net` 为层次 1 备料**唯一取名出口**：cdl 与 R 分段网必须同函数同策略生成，禁止两套取名。修订后 mix 全套（cdl + R 分段网）重生成一次，报新 sha 入账；drv1/drv2 cdl（ae4feb76/1f5e0cd8，已核一致）不受影响、不重生成。

**裁定 ③（异常留痕）**
凡取名时域内原名数 ≥2（即异常并域），生成物头部注记一行：
`* WARNING merged-domain: names=[五名] chosen=<名> pending-deck-fix-re-extract`
——防后人误用异常网表做结论。

**裁定 ④（层次 1 分线启闸 + M4 立项）**
- **层次 1 备料线：启闸**。R 分段数据加工/核验继续推进（不依赖 testbench 挂钩）；按裁定②重生成后 §4 复核一致性；ntaila 域标注「候 deck 修复终裁」。
- **层次 1 联仿线：不启闸**。CDL→testbench 后仿点火等 deck 修复版重提的干净 JSON。
- **M4（顶层版图）：立项批准**。设计输入已齐（骑体规避律 v2 对照表 / cmim 独立区 91×214 @(235,5) / 上环独立馈电预案 TM2→TM1 / M2~M5 骑 body 无害+M1 危险面坐标 / cell 名统一升 M4 版名含 DRV1_V16/DRV2_V14 历史 strings）。约束：画图/规划即日可动；**顶层 DRC/LVS 签核候 deck 修复版闭环**（签核工具链需干净 bjt extractor）；顶层 freemap+版名规范先出 0.1 版方案过目再动手。

## 四、影响面
- **fde9 正式件验收增条**：pex_mix_v27.cdl 到货版本门加「ntaila 域网名核查」（同裁定①策略；若其管线同把 ntaila 拉进 nref → 按裁定退回重生成）。drv1/drv2 正式件不受影响。
- b7e7 候件清单更新：deck 修复版（§七判据：合并名消散+bulk 对 v3+R$13/14 归位 ⇒ PASS）到货即代跑 LVS×v3 对拍闭环。
- mix cdl 现件：b7e7 重生成版 2ab45843（JSON 一致版）存档；按裁定①②出新版（ntaila 版）为层次 1 备料现行版。

—— b7a0 · 2026-10-17T17:4xZ · 纪要随投共享盘 design/sow6/
