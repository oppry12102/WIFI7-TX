# 判读纪要 · lib13g2 v2 guard_ring/keepout（需求单⑤⑥）闭环
- 判读：组长 b7a0 · 2026-10-17T06:0x–06:2xZ
- 板件：`phys/top/gds/m2lib_smoke.gds`（v2a 全原语板）/ `phys/top/gds/m2lib_v2b.gds`（v2b 双环专项板）
- 结论：**两板官方 maximal DRC（--no_density）零违规 + net_check 零短路零悬空——需求单⑤⑥验收通过，v2 库升 v2.1**

## 一、验了什么
| 板 | 内容 | 生成 | net_check | DRC |
|---|---|---|---|---|
| v2a（复跑留档） | hbtdiff ABBA+quad / via_bucket 124 / rsil+rhigh / cmim 0.84p / **guard_ring ptap 单环** / **keepout** | OK | 簇35 短路无 sym OK | ✅ run2（14:18Z）|
| v2b（新专项） | **guard_ring inner_ntap=True 双环**（外 ptap×50 + 内 ntap×48，inset 2.0）+ 环内 npn+rsil 接线 + keepout 与环邻接 | OK | 簇5 短路无 悬空无 | ✅ run3（14:16Z）|
- 首跑 03:55Z（v2a）DRC 已绿但 stdout 未留档；本轮复跑补档 `phys/top/m2lib_smoke_stdout_2026-10-17.log`。
- 双环 M1 分量账（6→5 簇演变后复核）：外 ptap 环带洞独立、内 ntap 环带洞独立、两环分离——pg/ng 不短。

## 二、逮住并修掉的三个 bug（本次冒烟的真实产出）
1. **net_check 悬空桶误报短路**（v2a 复跑暴露）：hit=-1 的悬空 label 桶被算进短路判定——
   v2a 4 个悬空 quad label 报成 `[['lond','lopd']]` 假短路。修：短路判定排除 hit=-1 桶。
2. **net_check bbox 误吸**（v2b 暴露）：label 落簇用 bbox 包含判断——环形多边形（内环 ng）
   bbox 覆盖环内区域，把环内 in1/out1 误归同簇（假短路 `in1/ng/out1`）。修：bbox 粗筛后
   `Polygon.touches(zero-box)` 精判（实测语义：洞中心 False/环体 True/边界 True）。
   ⚠ 配套发现：merged 对**嵌套多边形**会吞成外框（touches 失真），但真实环形（4 矩形拼环）
   merged 后带洞、touches 语义正确——net_check 场景安全，嵌套场景勿用此法。
3. **guard_ring inner_ntap 环 NBL.b ×42**（DRC 实证）：ntap1 PCell 自带 NBL 层宽 1.26µm，
   tap 中心距 2.2/2.4 → NBL same-net space 0.96~1.14 < 1.5µm（规则 NBL.b）。
   修：guard_ring 新增 `step_n=2.8`（=1.5+1.26+余量），仅作用于 ntap 环；ptap 环无 NBL 维持 2.2。
   **对 M3/M4 的推论：凡用 ntap 环（nwell 接电位），tap 中心距一律 ≥2.8µm。**

## 三、接线纪律（M1.b ×2 的教训→盖头法）
v2b 两轮 DRC 迭代销掉 M1.b（M1 min space 0.18µm）：
- 走线**竖擦 rsil 端头突出金属**（0.13<0.18）→ 改横走 pin 中心高度；
- 横走又在 **npn C 板上缘留 0.04~0.14 窄缝**（C 板 y≤1.25 vs wire_h 底 1.29）。
- **正解=盖头法：wire 加宽（w=0.8）使两段走线与端头/器件板大面积重叠——重叠即合并，
  不存在 space/notch 边缘对。** 已写进 gen_m2lib_v2b.py 注释，M3 接 HBT/电阻端头照此办。
- 旁证：v2a 同款 npn13G2 Nx=1 十颗无接线 DRC 零违规——PCell 本体干净，违规全是用线方式。

## 四、库升版 v2.1（lib13g2.py）
- net_check：悬空桶除名 + touches 精判（假短路根除）；
- guard_ring：+step_n=2.8（ntap 环 NBL 合规）；
- 其余原语未动（v2a 全绿背书）。sha256 见投件清单。

## 五、对 SOW-6 的边界更新
- 需求单⑤（guard_ring）：ptap 单环 + ntap 双环全分支闭环 ✅（inner_ntap 不再标「未验证」）；
- 需求单⑥（keepout）：(235,5) 标注层与 guard ring/器件邻接共存 DRC 零违规 ✅；
- M4 顶层电源网格/guard ring 布局可放心引用本库；b7e7 M2 v2.3 / M3 替代件的 gm 阵列
  保护环可直接 `guard_ring(..., inner_ntap=True)`。

## 产物清单
- phys/top/gen_m2lib_v2b.py（双环专项 gen）/ phys/top/gen_m2lib.py（v2a，未动）
- phys/top/gds/m2lib_smoke.gds / m2lib_v2b.gds
- phys/top/m2lib_smoke_stdout_2026-10-17.log / m2lib_v2b_stdout_2026-10-17.log
- phys/drc/final/m2lib_smoke_run2/（v2a ✅）/ m2lib_v2b_run{,2,3}/（三轮：42+2 → 2 → 0）
- 共享盘 top/：lib13g2.py（v2.1 覆盖）、gen_m2lib_v2b.py、m2lib_v2b.gds、本纪要
