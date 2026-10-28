# 判读纪要 · SOW-6 M2/M3 代跑（v24/v13/v12 现行件全链）· 组长 b7a0 · 2026-10-17

## 0. 一句话结论
三件现行件（gen_M2_mix_v24 / gen_M3_drv1_v13 / gen_M3_drv2_v12）**全链代跑闭环**：
gen×3 OK → maximal DRC×3（违规见 §4，两族）→ net_check ✓ → preflight 14 项×3 **全 PASS** →
teeth 11/11 + label teeth 3/3 **全部有牙**。**几何接线/极性/短路零 FAIL**；剩余工作全部集中在
①Offgrid（res_auto 分数几何 vs 5nm 网格）②核内真几何间距/线宽族（§4.2）。**guard 环（Q7）落图零真几何违规。**

## 1. 到件与 sha 对账（两轮，逐位一致）
- v23 轮七件（06:56:25Z 信，后升版作废）：gen_M2_mix_v23 51594B 46b6b81d… / drv1_v12 26337B baba8f8e… /
  drv2_v11 28732B d0e901e0… / 两设计稿 13081B 83c3d4fb… 4988B ab730116… / CHANGELOG 8927B 32ded539… /
  dryrun_v23.tar.gz 52902B b8cc71e1… —— **已按作废指令停用**（我恰在其间跑完一轮，产出并入本纪要 §3/§4）
- v24 轮六件（07:09:49Z 信，**现行**）：v24 54263B bc5cf43f… / v13 28790B 7a72290a… / v12 31185B 059ac75d… /
  dryrun_v24 85573B bba08f2b… / README_交付清单 8427B e1fcb13d… / CHANGELOG 10841B 4b25cddb… 全对上。
- v24 相对 v23 唯一改动 = relabel_official()（/1 补打，纯文本层）→ **两轮 DRC 逐规则计数完全一致**
  （1280/177/825），v23 轮的 DRC 基线对 v24 继续有效。

## 2. 代跑环境与产物
- 真 klayout 0.30.0（pdk/kl_env030.sh 铁律）+ IHP SG13G2 官方 maximal deck `--no_density`（run_drc.py，
  deep mode）；preflight/teeth 走 dryrun 仿真层（每件独立跑）；GDS 出品即权威件。
- 产物（run_v2/）：gds/m2_mix_v24.gds（f7996a8f…）/ m3_drv1_v13.gds（efd5c84b…）/ m3_drv2_v12.gds（ade2c58f…）；
  drc/<件>/（逐规则 log + lyrdb）；logs/（gen/pf/drc/teeth 全套）。
- GDS 实例取证：M2 = npn13G2×15 + rsil×8 + rhigh×8 + via_stack×46 + **cmim×6 + ptap1×8**；
  drv1 = npn×4+via19+rsil2+rhigh5+rppd2；drv2 = npn×12+via47+rsil2+rhigh6+rppd4。
- ⑭ 验证：三件 /1 与 /25 **逐层同数**（M2：8/1=32=8/25、10/1=8、30/1=5、50/1=2、67/1=7、126/1=11、134/1=4；
  drv1 32/32；drv2 53/53）。lyp 实表核对：8/1 等 label purpose 全在册，**METAL_LNUM (8,10,30,50,67,126,134)/1 口径正确，无需改**。

## 3. PDK 真值新发现（代跑第一价值，请上游同步）
1. **`ptap` 不存在，真名 `ptap1`**（ihp/ptap1_code.py；ntap 同理为 `ntap1`）。b._pcell("…","ptap",{})
   → create_cell 返 None → assert 进 NOTES 被吞 = 静默不落图。改 ptap1 后 8 只全落（PDK 默认参数）。
2. **cmim 引脚真值**：两端各在 **Metal5.pin (67/2)** 与 **TopMetal1.pin (126/2)**，每层恰 1 枚 pin、
   **同心**于 cell 局部 (11.83,11.83)；bbox=(−0.6,−0.6;24.26,24.26)（23.66 见方 + 0.3 边距）。
   w/l 参数字符串 "23.66u" 被 PCell 吃下 ✓。「同层恰 2 pin」启发式永不命中——已代改为跨层收集。
3. **M2 六只 cmim 端子绝对坐标**（落线用；M5 端与 TOPM1 端同心）：
   (−8.170,122.830) (−8.170,140.830) (31.830,122.830) (31.830,140.830) (−10.145,190.495) (33.805,190.495)
   落线建议：TM1 端直接在 TM1 走（**TM1 线宽 ≥1.64µm**，见 §4.2）；M5 端在 TM1 正下方，
   需 TopVia1 上引错位走或 Via4 下引——注意 TopVia1 4.0Ω/件与柱下 keepout。
4. 制造网格 **grid=0.005µm（5nm）**（sg13g2_tech_default.json drc_rules.grid）——Offgrid 族根源。

## 4. DRC 判读（maximal deck --no_density；M2 1280 / drv1 177 / drv2 825 项）
### 4.1 Offgrid 族（系统性，≈90% 项数）
金属/via/cont/activ/psd/polyres 等全层 `*_drw_Offgrid`。根因单一：**res_auto 的 l/w 是分数微米**
（l=4.286/1.429/1.471/1.923、w=2.6、0.84·l 派生腰高、ptap1 的 0.3/0.7 环向分点），
5nm 网格下不整。修法（一处治全族）：res_auto 出值后 **l/w 与一切派生坐标 snap 到 5nm**
（电阻阻值误差 ≤0.35%，远小于 corner ±14%）；ptap1 环向分点同样取整。
环带内的 Offgrid（activ/cont/psd/substrate×24、cont×96、metal1×6）全是 ptap1 分数位所致，随全局 snap 消。

### 4.2 真几何族（要改版图的，按件列）
| 件 | 规则×数 | 定义（deck 值） | 样本坐标 |
|---|---|---|---|
| M2 | TM1.a×58 | TopMetal1 最小宽度 1.64µm | (−0.15~0.82, 237.0)（nvtop 顶联区，0.97µm 细线） |
| M2 | TM2.a×31 | TopMetal2 最小宽度 2.0µm | (−38.2, 9.85~11.8) |
| M2 | TM1.b×6 | TopMetal1 最小间距 1.64µm | (20.15 vs 20.49, 110~154)（rfop/rfon 顶线） |
| M2 | M1.b×8 / M2.b×7 / M4.b×1 | M1 间距 0.18 / M2 间距 0.27 / M4 间距 | (−9.85,67.8) 等 / (5.65,117.2) / (49.85,29.5~30.4)（M4 地轨端头 vs 柱） |
| M2 | V1.a×4 / V1.b×16 | Via1 宽 0.19 / 间距 0.22 | (−28.625,29.28)（XBI1 区） |
| M2 | CntB.h1×19 / CntB.g2×2 | ContBar 的 M1 包边 0.05 / pSD 重叠 0.09 | (−10.85~−12.54,31.0) / (−25.35,31.05~31.21)（均在 XBI 镜像区 y≈31） |
| drv1 | M1.b×11 / M2.b×9 / TM1.a×9 / V1.b×8 | 同上 | (13.67,144.5) / (−16.8,142.4) / (13.18,163.9~166.6) / (33.7,107.16) |
| drv2 | M1.b×22 / M2.b×20 / TM1.a×18 / TM2.a×22 / V1.b×20 | 同上 | (−24.3,172.5) / (20.5~27.7,170.4) / (−22.65,17.9~20.5) / (30.5~−36,13.85) / (70.2,107.16) |
| drv2 | **Slt.c.M1 ×1** | M1 无开槽最大宽度 30µm | (−62,117.7;88,150) —— 发射极回流大平面 150µm 宽，须开槽（slit） |

归因：**guard 环 + ptap 带 = 零真几何违规**（环带内仅 §4.1 Offgrid）；真几何违规全部在核内，
多为真值换算后几何重排的连带（细顶线/间距挤紧/大平面），逐条坐标已列，inspect.py 可复核。

## 5. preflight 14 项 ×3 = 全 PASS（含 kit 补丁后）
- v24 kit 两处**上游已自修**：netaudit.NAME2NUM 已带 M1 风格别名（TOPM1/TOPM2 拼写）✓；
  preflight 自身 sys.path 加固 ✓；新增 ⑭ 三判据 ✓。
- 我侧仍需补丁的 kit 内伤 ×1：`klayout_db_stub.Polygon` 缺 `touches()`（lib13g2 **v2.1** net_check 的
  标注精判调用）——已补（见 §6）。注意 b7e7 本地 m1_lib/lib13g2.py 是 **v1**（无 touches 调用），
  故其侧从未崩——**kit 里的库副本比 M1 正式版 v2.1 旧一档**，请同步。
- gen 脚本 bbox 读取改为双风格（真 klayout `left/bottom/right/top`；仿真层 `x1/y1/x2/y2`），
  消除「一侧跑通另一侧必崩」的 API 偏斜。

## 6. 代跑补丁全清单（上游同步项，均带「【代跑补丁 b7a0】」标记）
| # | 文件 | 补丁 | 性质 |
|---|---|---|---|
| 1 | gen_M2_mix_v24.py | bbox 双风格读取（_bb/_bb2） | 真 API 兼容（三件同改） |
| 2 | gen_M2_mix_v24.py | `"ptap"` → `"ptap1"` | **PDK 真名**（原样静默不落图） |
| 3 | gen_M2_mix_v24.py | mkcmim 跨层引脚收集 + 标注加实例偏移 (x,y) + NOTES 引用同步 | **PDK 真值**（原样六只全回落占位） |
| 4 | dryrun/klayout_db_stub.py | Polygon.touches() | 仿真层缺真 API 方法 |
| 5 | dryrun/teeth_v11.py | CASES 文件名 v11/v12/v23 → v13/v12/v24 | kit 版本偏斜（旧名已作废） |

## 7. preflight/teeth 战报
- preflight 14 项：三件 **PASS**（器件 77/32/71，标注 57/32/53；⑫ 引脚极性逐脚核对 29/16/30 件零 FAIL）。
- teeth 11/11 真 FAIL（原件各自身 PASS 为前提）；teeth_label 3/3（A 撤补打/B 金属/0 文本/C /1 凭空名）。

## 8. 对 b7e7 三问的正式回答（07:09:49Z 信 §六）
1. **CMIM_FALLBACK / PTAP_SKIPPED**：原样两处都触发——PDK 不认 `ptap`（真名 `ptap1`），
   cmim 的「同层恰 2 pin」自适应永不命中（真引脚分居 M5/TM1）。两处均已代修，修后零 FALLBACK/SKIPPED，
   cmim×6 + ptap1×8 全部实落。
2. **cmim 真实引脚坐标**：§3.3 六只全列；两端同心，M5 端与 TOPM1 端同 (x,y)，分属 67/2 与 126/2。
3. **官方 DRC 对环/ptap 判定**：环定网 gnd + 搭桥柱 + M4 单柱 + ptap1×8（PDK 默认参数）落图后，
   **环带零真几何违规**；唯一环内项是 ptap 分数坐标的 Offgrid（§4.1 随 snap 消）。Q7 三条裁决落图验收**通过**。

## 9. 口令与下一步
- b7e7：①按 §4.2 修真几何族 + §4.1 snap 5nm（res_auto 一处）+ §6 上游同步 → 升 v25/v14/v13 重投；
  ②cmim 落线（§3.3 数据齐）→ 六只电容出占位；③Slt.c.M1 的 drv2 大平面开槽方案进设计稿。
- fde9：runner 全联动/runbook v2.1 收讫；M5 等我这侧 M2/M3 定稿后 PEX 件（顺序不变）。
- 组长侧：M4 顶层等 M2/M3 定稿；回执信随本纪要投 8445。
