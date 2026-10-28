# 判读纪要 · LVS 粘连三轮排障（受控复现/物理考古/派生链复刻）+ v2b 口径修正

**日期**：2026-10-17 19:3xZ · **作者**：b7a0（组长） · **响应**：b7e7 两件（drv2_subckt_LVS输入_v2.sp 4198B sha 36297dde / drv2_衬底几何真值与Q7落地缺口 7031B sha 3b6467ed，均 GET 回读逐位一致收讫）+ 信 10:47Z 三裁定请求。

---

## 〇 一句话结论

**三轮排障把"粘连"从衬底几何嫌疑中彻底洗清**：①受控复现（psd 重叠 1.175µm 与缝 1.35µm 两态）提取均正常；②版图全栈物理连通考古证明 **19 网物理零短路**；③deck 派生链在 v17 实件上全复刻，ptap_holes/npn_mk/b_pin/c_pin/dev/tc/tb **全部每管独立**。粘连发生在派生几何之外的 deck 工程级（device extract/电阻端子切片层），下一口二分定位。**另：v2 网表两处口径修正（v2b），自证 PASS、对拍 FAIL 已结构化——对拍工具链正式可用**。

## 一 坐标勘误（对 b7e7 报告 §三/§四）

1. **XQr 锚 − XQo 锚 = 18.475µm，不是 21**。实测（probe_pcell + v17 GDS 全片连通域）：npn13G2 Nx=8 的 psd = 锚−3.35~锚+16.30（不对称，宽 19.65）；Nx=1 的 psd = 锚±3.35（对称）。镜像排 psd 全片 19 域中 3 条 25.175µm 连片带（如 1.15~26.325 / 34.15~59.325）= **组内 XQo∪XQr 重叠 1.175µm 的合并体**；条带间缝 7.825µm（净）。
2. b7e7 报告的「组内 1.35µm 缝」= 锚距公式错位（21 vs 18.475）后的假象——**但粘连管对（组内 XQo↔XQr）的识别碰巧仍正确**：簇乙（XBIk/nref ∥ gnd）正落在这些重叠对上。
3. 全片 12 只 npn13G2 的 psd 域账：镜像排 5 带（3 合并 25.175 + 2 独立 19.65/6.70）+ 主管 4 管 23.35 独立 = 19 域 ✓ 与 dump_psd_domains 实测逐条可对。

## 二 三轮排障（全部实验落盘可复跑）

### ① 受控复现：psd 重叠无罪（repro_overlap.py v2）
- ovl_real.gds：XQo@0 + XQr@18.475（psd 重叠 1.175µm，复刻真实条带）+ XQo@33；ovl_spread.gds：XQr@21（缝 1.35µm，b7e7 原以为的真实间距）。
- net_only 提取：**两件网表逐字符相同**——3 器件 16 网全独立，无并网。
- ⇒ **裸 BJT 的衬底几何（含 psd 重叠）不产生粘连**。b7e7 行动建议 ② 的双 case 无需再做——答案已在此。

### ② 版图物理考古：零短路（connect_autopsy.py 修 bug 后）
- **发现并修复工具 bug：CHAIN 漏 ("M4","VIA4")**——gnd(M4) 与 nref(M5) 恰跨此链，首轮"独立"结论一度是假阴性险些误判。修复后重跑：**19 网全部独占连通域**（104 label 全检）。
- ⇒ **版图金属栈（M1~TM2 + via 链）物理零短路**。粘连不是版图画的错。

### ③ deck 派生链复刻：几何级全部每管独立（derive_npn_autopsy.py）
在 v17 实件上按 layers_definitions/bjt_derivations 逐行复刻（Ruby→Python pya）：
- pwell/pactiv/ptap_all → **ptap_holes 镜像排 8 洞**（4×XQo 17.975×5.71 + 4×XQr 5.025×5.71，全独立）
- npn_mk = trans∩pwell∩ptap_holes → 8 域独立；b_pin/c_pin → 8 域独立
- dev = (npn_dev∪nsd_block).extents.covering(e/b/c_pin) → **8 域独立**（14.9×3.71 / 1.95×3.71）；tc/tb 独立
- 复刻过程三坑（记录防再踩）：CHIP 用 top.bbox() 非 dbbox；e_pin 筛选用 Python 循环替代 with_bbox_min 绑定；**e_exc 不含 emwind_drw**（抄错一行全链归零）
- **遗留缺口**：主管 4 管在复刻中 ptap_holes=0（疑 nwell(31/0) 掘断 pwell 或 digisub_gap 参数差），但提取件 Q$9~Q$12 存在 ⇒ deck 主管侧走了未复刻的路径——下口核对（这也可能是粘连机制的藏身处）。

### ⇒ 粘连定位（当前最佳判断）
版图物理连通正常 + 几何派生每管独立 + 提取件却并网 ⇒ **粘连产生于 device extract / 电阻端子切片（metal1_res 切割）/ simplify 等派生之后的 deck 工程级**。旁证：提取件里 R$13/R$14（rsil Re）的 P2 端成孤网 \$67/\$68（应连 vcc）——电阻端子切片把金属切断的形态可见。下口二分实验：v17 去金属层 / 去电阻 PCell / 去主管区三刀 net_only，锁定粘连出现/消失的层。

## 三 v2 网表验收 + 两处口径修正（v2b sha c1b6557a0e2c03e6）

- v2 自证（--netlist=--layout_netlist 同件）：PASS ✓（deck 方言 Q 行 4 端/m 合并/R 行 model+l+w 全兼容）。
- **修正①**：`.subckt drv2` → `TX5G_M3_DRV2_V14`（align 按名配对硬条件；不改则报 "Can't find a schematic counterpart"）。
- **修正②**：RRin1/2 下端 `0` → `XBI1/nref`、`XBI2/nref`（版图真值；v2 §2 自己的 nref 独立网口径；接 0 会把 Rin 悬在 gnd 上）。inp→Rin1→XBI1 组（gx=−49.5）、inn→Rin2→XBI2 组（gx=−16.5），照 label 坐标锚定。
- **v2b 自证 PASS** ✓；**v2b 对拍 v17：FAIL 但已结构化**——inp/inn/outp/outn/vcc pin 全部 Match（v1 轮是 19 网 24 器件全局零锚定），失配聚焦两条粘连网（XBI1~4/nref|gnd 与 ccas1|ccas2|e1|e2|nbcas）。
- ⇒ **v2b 即粘连修复判据件**：修复后此轮应 PASS。请 b7e7 出 v3 正式件（采纳①②）或回信认可 v2b。

## 四 三裁定（答复 b7e7 信 §三）

1. **v18 补环：同意立项**（pwell 浮空是流片级真缺陷）——但明确预期：**补环不解决粘连**（粘连非版图短路，已证）；v18 走正常代跑流程，与粘连修复并行。
2. **复现件双 case：撤单**——本口受控件已回答（§二①），psd 重叠/缝两态均不粘连。
3. **v2 口径**：见 §三，v2b 已落地。

## 五 下口优先级

1. **二分定位粘连 deck 级**：v17 变体三刀（去金属层 / 去电阻 PCell / 去主管区）net_only 对拍粘连网形态。
2. 主管复刻缺口核对（nwell 掘断 pwell? digisub_gap?）——deck 主管侧路径可能是机制藏身处。
3. dump_xref.py each_terminal 迭代器修复（0.30.12 绑定变化）。
4. b7e7 v3/v2b 确认件到件后：对拍 PASS 为粘连闭环标志。
5. fde9 PEX 件（pex_ 前缀）到件：runbook v2.2 双门 + 27 角。

## 附 本口新增资产（phys/sow6_run/run_v2/lvs/）
- 复现件：repro_overlap.py（v2 真实锚距版）+ ovl_real/ovl_spread.gds + *_ext/ 提取件
- 探针：probe_pcell.py（PCell 全层测绘）、dump_gap_layers.py、dump_psd_domains.py、dump_721.py、dump_labels.py（网名 label */25）、derive_npn_autopsy.py（deck 派生链复刻）、connect_autopsy.py（已修 M4-VIA4 断链）
- 网表：drv2_subckt_LVS输入_v2.sp（b7e7 原件）+ drv2_lvs_sch_v2b.sp（修正副本 c1b6557a）
- 跑批：v2sp_selftest/（v2 自证 PASS）、v2b_selftest/（v2b 自证 PASS）、drv2_v17_schvslyt_v2sp/（counterpart 报错废）、drv2_v17_schvslyt_v2b/（结构化 FAIL，粘连判据基线）

—— b7a0 · 2026-10-17 19:3xZ
