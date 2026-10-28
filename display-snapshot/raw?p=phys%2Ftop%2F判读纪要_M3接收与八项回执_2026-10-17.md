# 判读纪要 · M3 接收与八项回执（含 techlef 金属/过孔真值发现）

组长 b7a0 · 2026-10-17T05:3xZ · SOW-6 · 依据 inbox 117 行（b7e7 05:27Z）+ PDK 原件穷举

## 一、收讫（inbox 117）
- **M2 v2.0 作废 → v2.1 定稿候**：⑤b「同名分裂」新自检项抓出三处（gnd 散 5 分量 / ntailb 差 10µm /
  nvtop 两截）。组纪律升级：所有版图件自检台必含 ⑤b 连通分量级网名校验 + ⑦b 占位件核对。
- **M3 两件候代跑**：gen_M3_drv{1,2}_v1.py（自检 PASS，72/183 器件）+ emitpath.py + resgeom.py。
  **文件尚未投 8510 design/sow6/**——v8 回执已索（附 sha 要求），件到即代跑
  （kl_env030 + `-zz` → GDS → maximal DRC + net_check/LVS 预检 → 回执）。

## 二、两裁决（v8 回执全文：design/sow6/reply_v8_from_b7a0_2026-10-17.md，
sha 2b4a597a4ec8fb4f…，7404 B，回环核符）
- **裁决 A**：M2 回流**单层 M2**（做法 A 0.162Ω 进门）；`emit_return_spec(dual=True)` 留档，
  触发条件 PEX>0.2Ω。R-EMIT-02 注记升级随准则 v1.3。
- **备案 B**：drv2 四组 nref **按网表原文独立不并**；组间失配不进现有签核门；
  重议触发 = PVT/后仿级间偏置发散破门。已同步知会 fde9。

## 三、techlef 金属/过孔真值（本次新挖，开源 PDK 唯一金属 RC 出处）
`pdk/ihp_open/ihp-sg13g2/libs.ref/sg13g2_stdcell/lef/sg13g2_tech.lef`：
| 层 | RPERSQ Ω/□ | 厚 µm | | 层 | Ω/件 |
|---|---|---|---|---|---|
| Metal1 | 0.135 | 0.40 | | Cont | 22 |
| Metal2~5 | 0.103 | 0.45 | | Via1~4 | 20 |
| TopMetal1 | 0.021 | 2.0 | | TopVia1 | 4.0 |
| TopMetal2 | 0.0145 | 3.0 | | TopVia2 | 2.2 |

**对表**：准则 v1.2 R-VIA-01 的 **max 列 = techlef**（20/4.0/2.2/22）；
**target 列（9/2.2/1.1/17）= max×½ 设计降额**。b7e7 复现公式 9/0.06=150、2.2/0.06→37 成立
（0.06=60mΩ=0.2Ω×30%），**187 件/边维持**；techlef 全值口径需 334 件（max 列）。
最终裁决 = 执行条款① PEX ≤0.2Ω。金属 0.125 估值对账：M1 +8%/M2 −18%，drv2 总 ≈150mΩ，门不翻盘。

## 四、EXCLUTION 层穷举结论
开源 PDK **无 "EXCLUTION"/keeper 专层**（map 86 行/lyp 378 层/lyt/pycell/maximal decks 零命中）。
禁区口径：官方 inductor PCell 自带 nofill（x/23）排除；自画 tank 用 IND 27/0（+27/4 boundary 备案框）
+ NoMetFiller 160/0 + NoRCX 148/0。另：M1 deck（5_16）无器件禁区规则（npn/emit/poly 零引用），
金属压本体不属违例面，maximal DRC 兜底。

## 五、待办
1. b7e7 投件（v2.1+M3 六件+设计稿）→ 代跑全链 → 回执。
2. 准则 v1.3：R-VIA-01 拓扑注记（TV1 不串 e 链；无 M5→TM1 段则 TV1 整排不落、件数回填 150/边）+
   R-EMIT-02 单层 M2 注记 + Rsheet/techlef 真值表收编。
3. lib13g2 v2：guard_ring（+keepout）原语（真值表 §4 需求单⑤⑥，b7e7 明确划给我侧）。
4. 8445 通 → 发正式 inbox 信 v7/v8 摘要 + 删挂起文件 design/sow6/reply_v7_….md。
