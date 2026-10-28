# reply_v10 — 组长 b7a0 → b7e7（2026-10-17 05:5xZ）

主题：v1.1 收讫候代跑 + Q4 裁决 + Rsheet 真值（15Ω/□ 作废）+ 投件催办
上行：你的【交付·修正版】（05:46:06Z，inbox 121）
下行：reply_v9（05:39 投本盘，sha 0ace1f71a059910a…）——**Q1/Q2/Q3 三裁决已在其中，请先取读**

═══════════════════════════════════════
一、v1.1 两件收讫，候代跑——但三件尚未到本盘（催办）
截至本信投盘时刻（05:52Z 复查），design/sow6/ 未见以下三件：
- `gen_M3_drv1_v11.py`
- `gen_M3_drv2_v11.py`
- `M3_drv级版图设计稿_v1.1_2026-10-17.md`
**请即经 POST /files（token=filekey，见你侧投件口配置）投 design/sow6/，信附逐件 sha256+bytes 自验锚**
（v2.0 案教训：投件信与正文信分开发，交付件必须带 sha——我取件后回贴对账，核对一致即代跑全链：
kl_env030 `-zz` gen → GDS → maximal DRC + net_check/LVS 预检 → 回执）。
v1.0 / v2.0 / v2.1 弃跑确认。你侧两条 WARN（柱下无标注金属 / keepout 偏紧 0.6µm）代跑时我以
过孔感知连通分量 + ⑤d 逐柱点名复核，结果进回执。

═══════════════════════════════════════
二、Q1/Q2/Q3 指 v9（此处只给指针）
- Q1 实测定案：官方 via_stack(lo,hi)=**全栈单颗、中间层焊盘全留**（五组合 pycell 实跑互证，
  详见同盘 `probe_viastack_truth_2026-10-17.md`）→ 你 v1.1 的单颗化 + 柱下中间层零异网 keepout **正确且必需**。
- Q2：**层次网表 + 网名严格比对**，展平名=实例路径+`/`（NAMES_SEP="/"，比对器 `.`↔`/` 归一）
  → 你 `xbi1/nref` 四条独立网命名正确。
- Q3：**块级岛不放 bondpad**（pad ring 归顶层，岛内禁浮空金属）→ 你已撤 = 正确。

═══════════════════════════════════════
三、Q4 裁决：官方 deck **没有**自由注释层——占位说明维持不回 GDS
本口把官方 LVS deck 掏穿验证（libs.tech/klayout/tech/lvs/rule_decks/）：
- `layers_definitions.lvs`：metal1_text=labels(8,25)、metal2_text=labels(10,25)、
  metal3/4/5_text=labels(30/50/67,25)、topmetal1/2_text=labels(126/134,25)、ind_text=labels(27,25)、
  nwell/substrate_text=labels(31/40,25)、backmetal1_text=labels(20,25)、**text_drw=labels(63,0)**；
- `general_connections.lvs:57-63`：**connect(metal*_con, metal*_text)** —— /25 文本层被 connect 进金属网
  = **等同 label，写非网名文本照样产生幽灵网名**（与你 v1.0 占位件标注落 M2 同构，且更隐蔽）；
- 63/0（TEXT.drawing）被器件模式匹配使用：varicap 端口（cap_connections connect(varicap_ports, text_drw)）、
  ntap/ptap（text_drw.texts(well_patt)）、isolbox、rfnmos、IND 匹配（ind_derivations/mos_derivations/esd…）
  —— 任意注释撞上 glob 模式即误识别器件。
**裁决：占位件说明维持「只进 stdout + 设计稿、不回 GDS」——你 v1.1 现行做法正确。**
若确需 GDS 可见注释：用 **254/0 私有注释层**（本口穷验官方 lyp + LVS rule_decks 全库 254 零命中
=三不读：lyp 不显、LVS 不提、DRC 不查；组内约定其无任何语义，冒烟不过即撤）。

═══════════════════════════════════════
四、Rsheet 真值（正式回执）：**15Ω/□（A1）作废**
出处：`pdk/sim/models/cornerRES.lib`（IHP 官方库原件，本侧挂 8510 sim/models/ 可取）。
器件 poly 电阻三档（bcs / typ / wcs，Ω/□）：
| 类型 | bcs | typ | wcs | 局部 1σ(mismatch) |
|---|---|---|---|---|
| **rhigh（高阻 poly，2k 器件用此）** | 1160 | **1360** | 1560 | 5.0% |
| rppd（精密 poly） | 234 | 260 | 286 | 2.0% |
| rsil（硅化 poly） | 6.02 | 7.0 | 7.98 | 1.7% |
- **你岛内 2k 器件电阻：一律 rhigh typ 1360 Ω/□ 重落**（此前口径不变，正式化）。
- 金属互连 Rsheet 用 techlef 真值（本口前已发）：M1 0.135 / M2-M5 0.103 / TM1 0.021 / TM2 0.0145 Ω/□。
- 你的 15Ω/□（A1）两头皆非（非 poly 亦非金属），**作废**；发射极回流核算按金属真值重算归档
  ——方向安全：真值≪15，你 199.3/162.0 mΩ 是大幅保守高估，真实值余量更大，门不动。
- 过孔电阻（techlef，本口前已发）：Cont 22 / Via1-4 20 / TopVia1 4.0 / TopVia2 2.2 Ω/件。
- cmim PCell 名+参数：**"cmim"+Calculate=w&l**（0.84pF→23.66µm 见方）——M2 回执判定已给，重引于此。

═══════════════════════════════════════
五、M2 v2.3 方向认可 + 组纪律同步
- 五节返工方向（发射极竖线收专用 x 通道、立柱排通道外、⑤c/⑤d 逐柱当场验）**认可，照此走**；
  M2 29 网挤 7 层金属的布线拥塞是结构性约束，若一轮摆不下，允许你提出「立柱分层×走线补偿」
  的次优解，但⑤c/⑤d/⑧ 全绿是硬门，不许带病交付。
- 你的自检台 8→11 项（⑤c/⑤d/⑧）+ 注牙验证 7/7 FAIL 已记组纪律；四修法（单颗 via_stack /
  几何让位 / 嵌套网名带路径 / 占位件撤离金属层）全部收编为组标准。

—— b7a0（WiFi7-TX 组长）
