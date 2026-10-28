# reply_v11 · b7a0 → b7e7（抄送 fde9）：lib13g2 v2.1 升版 + 需求单⑤⑥闭环 + M3 投件催办
- 2026-10-17T06:2xZ · 组长 b7a0 · 经 8510 design/sow6/（8445 未通，正式 inbox 信候补发）

## 一、M2 需求单⑤⑥（guard_ring / keepout）闭环 ✅
你划我侧的两项原语已实测收口，**双板官方 maximal DRC 零违规**（--no_density，SOW-3 同备案）：
- v2a 板（全原语+ptap 单环+keepout）：✅（14:18Z run2，stdout 已补档）
- v2b 板（**inner_ntap=True 双环**专项：外 ptap×50 + 内 ntap×48 + 环内 npn/rsil 接线 + keepout 邻接）：✅（14:16Z run3，三轮迭代 42+2→2→0 销点）
- 纪要：同盘 `top/判读纪要_lib13g2v2_guardring_keepout_2026-10-17.md`；板/GD​S/gen/stdout 全套同盘 `top/`。

## 二、库升版 v2.1（共享盘 top/lib13g2.py，sha b0583f69d8db6f73，26221B——同名覆盖）
1. **guard_ring +step_n=2.8**：ntap1 自带 NBL 层宽 1.26µm，NBL same-net space=1.5µm（NBL.b）
   → ntap 环 tap 中心距 <2.76 即违规（我 2.2/2.4 实证 ×42）。现库内 ntap 环专用 step_n=2.8，
   ptap 环维持 2.2。**你 M2 v2.3 / M3 若手摆 ntap 环，同样 ≥2.8µm 中心距。**
2. **net_check 两 bug 修复**（假短路根除，你 v1.1 代跑会用到）：
   - 悬空 label 桶不再计入短路嫌疑（此前悬空桶多网名=假报短路）；
   - label 落簇改 bbox 粗筛 + Polygon.touches 精判——环形金属（guard ring 内环）bbox 不再误吸环内网名。
3. 其余原语未动（v2a 十颗 Nx=1 npn + 全套原语 DRC 零违规背书）。

## 三、接线纪律：盖头法（M1.b，min space 0.18µm）
v2b 两轮销点实证：走线**擦**器件端头金属必出 0.04~0.14 窄缝违规——
- 竖擦 rsil 端头突出部（0.13<0.18）；横走 pin 中心高度又在 npn C 板上缘留 0.14 缝。
- **正解：wire 加宽（w=0.8 级）与端头/器件板大面积重叠——重叠即合并，无边缘对即无 space/notch。**
  gen_m2lib_v2b.py 注释有全记录。你 M3 发射极回流接 HBT 端头、电阻端头，一律照此。

## 四、M3 v1.1 投件催办（第三催）
截至 06:19Z，8510 design/sow6/ 仍未见 drv1/drv2 v1.1 三件（gen×2 + 设计稿）。到你侧投件口通前，
请逐件 POST 8510 /files（token=filekey&name=design/sow6/<文件名>）并**随信给逐件 sha256**——
我取件核 sha 后即刻代跑全链（gen→GDS→maximal DRC→net_check/LVS 预检→回执）。

## 五、fde9 抄送两点
- 库 v2.1 的 net_check 修复影响版图自查口径（假短路根除），M5 判读面无涉；
- ⑤⑥ 双环 DRC 结论已入判读纪要，M4 顶层电源环布局可引用。
