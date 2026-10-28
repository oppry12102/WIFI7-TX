# 判读纪要 · v18 补环代跑轮（Q14）· 2026-10-17

**组长 b7a0 代跑 · 到件验收 → 五关 → gdsdiff → DRC 对拍 → LVS×v3 结构化判读**
候件：b7e7 信 #143（11:53:38Z）交付①gen_M3_drv2_v18.py ②drv2_subckt_LVS输入_v3.sp；到件铃 facts#11306/11307。

---

## 一、到件验收（sha 对）

| 件 | sha256-16 | bytes | 判 |
|---|---|---|---|
| gen_M3_drv2_v18.py | c9f5f34a4b2a4d3d | 55766 | ✓ 与信逐字同 |
| drv2_subckt_LVS输入_v3.sp | e0fa170e5ad198dd | 5154 | ✓ |
| gen_M3_drv1_v18.py（Q12 旧件在盘） | 2a305b68f69cac60 | — | ✓ 复核无变化 |

## 二、b7e7 托办①：v2b ↔ v3 对拍 **PASS**

- 谜底先结：**v2b 从未投过 8510**（件一直在我侧 `run_v2/lvs/drv2_lvs_sch_v2b.sp`）——他侧两次 404 属正常（无件可取）。本口已补投 8510 design/sow6/（4458B sha **c1b6557a0e2c03e6**，与 v3 头注声称值一致）。
- `diff v2b v3`：**全部差异落 `*` 注释行**（头注释/变更史/口径来源/输入网络注），`.subckt/.ends`、RRin 两行、网络结构**零实质差异** —— 与 b7e7 预告「预期一致」逐字吻合。**v3 即 v2b 正式化，对拍面单一口径确立。**

## 三、代跑五关（我侧真 PDK 落图）

1. **preflight**：PASS · 器件 73 标注 59（v17 基线 70/52 + 桥×2+柱×1=+3 器件、gnd 标注 +7）· ⑲⑳ 双零 · ㉑ 落柱 **98 接 / 0 悬空**。
2. **teeth_v11**：**16/16 全有牙** ✓。
3. **gen stdout**：`[guard] ptap ×8 已落环（PDK 默认参数）`、环 (−81,−11)~(108,250) RING_M=8 RING_W=2、桥×2@x=104、落地柱@(107,100)、核 bbox=[−73,−3~100,242]、**岛框（含环）189×261** —— 与信逐字吻合（岛框含环口径已按新规读）。
4. **net_check 澄清（重要，防误读）**：我侧输出 `簇=34 短路嫌疑=[['bb1','bin','ccas1','ccas2','e1','e2','ntail']]`——比信中五关引的 5 网名多 ccas1/ccas2。**同口径重跑我侧 v17 gen：簇=33、嫌疑名单逐字符相同（7 网含 ccas）**，且 v13（Q8，无环时代）日志同名单 ⇒ **ccas 并簇是我环境层盲邻近审计（pad=2）的常态**，非 v18 引入；b7e7 的 5 网名系其无 PDK stub 口径。v18 净变化：簇 33→**34**（+1 = gnd 环独立簇）、悬空双零。
5. **过孔**：+3（桥×2+柱×1），46→49 ✓。

## 四、gdsdiff（v17 → v18）：**唯一差异=环族，器件 PCell 零变化**

CELL SET：only-B=`['ptap1']`（工具遇 cell 集差异早退，用 gdsdiff_full 变体续跑共同 cell）。
顶层 cell 逐层 delta（全部 B-only，A 侧零消失）：

| 层 | Δ件 | 内容 |
|---|---|---|
| 8/0 M1 | +6 | 外圈 4 边（GUARD 边、宽 2µm）+ 桥×2 M1 段 |
| 10/0 M2 | +4 | 内圈 4 边（inset3） |
| 50/0 M4 | +1 | 地轨右延搭接段 [88,108]×[98,102] |
| #insts | +11 | ptap1×8 + 过孔 3（桥×2+柱×1） |
| 8/1+10/1+50/1（及 /25 镜像） | +7 | 纯网名 `gnd` ×7（圈四边+M2 上下+落地柱） |

**判读：与 v1.8 设计意图逐位吻合，v1.7 几何零变化坐实，零意外 delta。**

## 五、DRC 对拍（基线 m3_drv2_v17_q13 → m3_drv2_v18_q14）：**162 → 162，Δ+0**

- 逐规则 M1.b 22 / M2.b 20 / V1.b 20 / cont·gatpoly·metal1·polyres Offgrid 族 / psd 2 / salblock 2 / extblock 14 —— **全 0 持平，消失 0 / 新增 0，指纹（规则+坐标）逐条相同**。
- **b7e7 托办终裁：tap 密度 / psd 间距条款 —— 整环（M1/M2 圈 + ptap×8 + 桥柱）落地后零新增违规，全绿。** ptap1 用 PDK 默认参数即合规，无需定制。

## 六、LVS（v18 × v3 正式件，COMPARE，--disable_tap_extraction）：**结构化 FAIL，与判据完全同构**

run_dir：`run_v2/lvs/drv2_v18_schvslyt_v3/`。extracted.cir 对拍 v17 基线（drv2_v17_schvslyt_v2b）：

1. **pwell 浮空已解（本轮主判定）**：全部器件 bulk/衬底端 `\$1` → `XBI1/nref|XBI2/nref|XBI3/nref|XBI4/nref|gnd`。v17 真 `$1` bulk 行 16 → **v18 残留 0**（grep 所余 11 行全为 Q$1x/R$1x 编号子串与 \$74/75 孤立标签，无一真 bulk）。guard 环 ptap 链经 deck 提取实证接通。
2. **粘连形态零变化**：两簇幻影焊合并名 `XBI…|gnd`（簇乙）与 `ccas1|ccas2|e1|e2|nbcas`（簇甲）原样保留 —— 幻影焊判决（deck `bjt_derivations.lvs` L59 covering-bbox）不受环影响，与 b7e7 预告逐字一致。
3. **R$13/14 孤立标签同案**：`\$67/\$68` → `\$74/\$75`，编号漂移、本质不变（rsil 远端标签缺失，与粘连无关旧案）。
4. 器件 15/15（12 HBT+12 R 展开面）；`.SUBCKT` 端口行 12 口一致。
5. **FAIL 归因单源化**：结构化 FAIL 唯一来源 = 两簇幻影焊（deck 工程级）+ bulk 挂合并网名（粘连的从属表现）；版图物理零短路（上口 flood_full 判决）、DRC 零新增（本轮）。

## 七、闭环判据（立此存照）

v18 结构化 FAIL 指纹 = ①两簇合并名 ②bulk 端挂 `XBI…|gnd` ③R$13/14 孤立标签。**deck（PDK/上游）修复版重跑：两簇合并名消散 + bulk 对上 v3 + R$13/14 归位 ⇒ 全绿 PASS = 粘连案闭环标志。** 在此前，v18+v3 即为 LVS 对拍的标准输入对（粘连指纹清单随附）。

## 八、状态与交棒

- v18 GDS 归位 `run_v2/gds/m3_drv2_v18.gds`；纪要同名投 8510 design/sow6/。
- SOW-6 M5 前仿基线（CG=+17.4465 dB）不受影响（网表口径零变化，DEV_NETS/NET_DECL 不动）。
- 候件：fde9 pex_ 件（runbook v2.2 双门）。M4 设计输入三件照旧（上环馈电预案 / cmim 独立电容区 / 骑体规避律）。

—— b7a0 · 2026-10-17T12:2xZ · 台账：部署 12:15Z / preflight+teeth 12:15~12:16Z / gen 12:16Z / gdsdiff 12:17Z / DRC 12:18Z / LVS 12:19Z / 纪要 12:2xZ
