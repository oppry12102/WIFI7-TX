# 判读纪要：Q4 注释层裁决 + Rsheet 真值回执（SOW-6）
日期：2026-10-17 05:5xZ · 记录人：组长 b7a0
触发：b7e7 inbox 121（M3 v1.1 交付，回执清单 Q4+Rsheet）· fde9 inbox 120（跑前确认句两项）

## 一、Q4「有无 deck 认可的注释层号」——官方 deck 掏穿实证

**结论：官方无自由注释层。占位件说明维持「只进 stdout+设计稿、不回 GDS」（b7e7 v1.1 现行做法=正确）。**

证据（pdk/ihp_open/ihp-sg13g2/libs.tech/klayout/tech/）：
1. `lvs/rule_decks/layers_definitions.lvs`：
   - metal1_text=labels(8,25)、metal2_text=labels(10,25)、metal3_text=labels(30,25)、
     metal4_text=labels(50,25)、metal5_text=labels(67,25)、topmetal1_text=labels(126,25)、
     topmetal2_text=labels(134,25)、ind_text=labels(27,25)、nwell_text=labels(31,25)、
     substrate_text=labels(40,25)、backmetal1_text=labels(20,25)、**text_drw=labels(63,0)**
   - exchange0-3_text=labels(190-193,25)（交换层族）
2. `lvs/rule_decks/general_connections.lvs:57-63`：**connect(metal*_con, metal*_text)**
   → /25 文本层被 connect 进金属网络 = 等同 label 通道，写非网名文本照样产生幽灵网名
   （与 v1.0 占位件标注落 M2 同构且更隐蔽——它就是官方 label 通道之一）。
3. 63/0（lyp 中名 TEXT.drawing）被器件模式匹配使用：
   - `cap_connections.lvs:38` connect(varicap_ports, text_drw)
   - `general_derivations.lvs:98-99` ntap1/ptap1_lbl = text_drw.texts(well_patt/sub_patt)
   - `cap_derivations` nmoscap_patt、"G*/SUB*/NW*" 匹配；`diode_derivations` isolbox；
     `esd_derivations` nmoscl；`ind_derivations` IND LA/LB；`mos_derivations` rfnmos
   → 任意注释撞 glob 模式即误识别器件。
4. **254/0 私有注释层通道**：官方 lyp + LVS rule_decks 全库穷举 254 零命中
   （三不读：lyp 不显 / LVS 不提 / DRC 不查）。组约定：254/0 无任何语义仅人看；冒烟不过即撤。默认不用。

## 二、Rsheet 真值回执（15Ω/□ A1 作废）

出处 `pdk/sim/models/cornerRES.lib`（IHP 官方库原件；8510 sim/models/ 同源可取）：

| 类型 | bcs | typ | wcs | 局部 1σ |
|---|---|---|---|---|
| rhigh | 1160 | **1360** | 1560 | 5.0% |
| rppd | 234 | 260 | 286 | 2.0% |
| rsil | 6.02 | 7.0 | 7.98 | 1.7% |

- 2k 器件电阻一律 rhigh typ 1360 Ω/□（既有口径正式化）。
- 金属互连 Rsheet 用 techlef 真值：M1 0.135 / M2-M5 0.103 / TM1 0.021 / TM2 0.0145 Ω/□；
  过孔 Cont 22 / Via1-4 20 / TopVia1 4.0 / TopVia2 2.2 Ω/件。
- b7e7「Rsheet=15Ω/□（A1）」两头皆非 → 作废；发射极回流按金属真值重算归档
  （方向安全：真值≪15，199.3/162.0 mΩ 系大幅保守高估，门 250/200 不动）。
- cmim：PCell 名 "cmim"+Calculate=w&l；0.84pF→23.66µm 见方（M2 回执判定重引）。

## 三、fde9 跑前确认句两项批复（已回 8425，200 ok）

1. 偏置联动=**全联动**：vcc 换轨时 Vbcm 2.35/Vb 1.25/Vbcas 2.05 全随 vdd 常数项×k（k=vdd/2.5）；
   runner rail-only → 全联动，改完回执。
2. C 层拍板=**不做**：维持 A 层第一判据+B 层事后归因（runbook §4.1 批准）；
   再议触发：drv2_suspicious 置位角≥3 或 typ 角置位，届时事后诊断 deck，不入第一轮 27 角。
3. 请其把 sow6m5_pex_runbook.md（sha 40c8813d…）投 8510 design/sow6/ 归档。

## 四、M3 v1.1 候代跑状态

- b7e7 交付信（05:46:06Z）：gen_M3_drv1_v11.py / gen_M3_drv2_v11.py / 设计稿 v1.1，
  自检 11/11；v1.0/v2.0/v2.1 弃跑。
- **截至 05:57Z 三件未到 8510 design/sow6/ → reply_v10 已催办（信附逐件 sha 要求）**。
- 到件流程：取件→算 sha 回贴对账→代跑全链（kl_env030 `-zz` gen→GDS→maximal DRC+net_check/LVS
  预检→回执；WARN 两条以过孔感知连通分量+⑤d 逐柱点名复核）。
- M2 v2.3 方向认可（发射极竖线专用 x 通道）；⑤c/⑤d/⑧ 全绿是硬门。
- reply_v10 已投 8510：sha256=2d7180c2e607daf615ad3d6c2538e5775eab6a63444a9a0e012ac590bd244883（5514B，回环核符）。
