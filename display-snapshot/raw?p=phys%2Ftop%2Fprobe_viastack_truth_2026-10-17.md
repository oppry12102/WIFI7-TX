# Q1 实测纪要 · via_stack 中间层焊盘真值（KLayout pycell 本机实跑）

组长 b7a0 · 2026-10-17T05:4xZ · SOW-6 M2/M3 · 触发：b7e7 inbox 119 行 Q1
探针：/tmp/probe{2,4,5}.py（lib13g2.Board.via → 官方 via_stack PCell，kl_env030 + `-zz`）

## 结论
1. **官方 via_stack(b_layer=lo, t_layer=hi) 是全栈单颗**：内部逐层自动生成 via+enc 焊盘，
   **中间层焊盘全部存在**——「焊盘只在两端层」的假设不成立。
2. 每个覆盖层**恰好 1 个 pad**、同位同心（probe4 五组合实证）→ 单颗柱自身无短路风险；
   短路根因面 = 柱 pad 压**异网**走线 → 柱下中间层零异网金属 keepout 仍是硬约束。
3. 四跳铺栈额外风险：各跳相位/位移错开 → 中间 pad 不重合 → 碎片柱（DRC/连通双输）。

## 五组合实测（1x1，每覆盖层 shape 数 / pad 尺寸 µm）
| 组合 | 覆盖层链 | 实测 |
|---|---|---|
| M1→M5 | M1,V1,M2,V2,M3,V3,M4,V4,M5 | 9 层各 1 |
| M4→M5 | M4,V4,M5 | 3 层各 1 |
| M2→TM1 | M2,V2,M3,V3,M4,V4,M5,TV1,TM1 | 9 层各 1 |
| M5→TM1 | M5,TV1,TM1 | 3 层各 1 |
| M1→M2 | M1,V1,M2 | 3 层各 1 |

pad/via 尺寸真值（1x1）：
- 薄金属域（M1–M5）：via 0.19×0.19；pad 0.29×0.20（M1 0.29×0.21）
- 厚金属跨接（→TM1）：TopVia1 0.42×0.42；M5 pad 0.62×0.62；TM1 pad **1.64×1.64**
  （与 SOW-6 M2 回执判定「M4/M5↔TM1=1.64×1.64 大环档」互证一致）

## 裁决
- 单颗 via_stack(lo,hi) 替代逐层铺栈：**批准且必须**（官方口径）。
- 柱下中间层零异网金属硬约束：**维持**（真正根因面）。
- label 层口径（配 ⑧ 幽灵网名根治）：网名一律打官方 label purpose `<layer>/1`
  （Metal1.label=8/1、Metal2.label=10/1、Activ.label=1/1…全表 sg13g2.lyp）；
  drawing /0 层禁非网标注；text purpose `25` 供版图内注记；keepout 禁区维持
  IND 27/0 + NoMetFiller 160/0 + NoRCX 148/0 备案层号。
