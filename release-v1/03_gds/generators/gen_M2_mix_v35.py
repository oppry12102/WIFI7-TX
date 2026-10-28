#!/usr/bin/env python3
"""
M2 gilbert_mix 版图生成脚本 v3.0（2026-10-18 · **合并版：QR_L 根修 + cmim 参数口径修正**，裁定四十 §二.1 令）
════════════════════════════════════════════════════════════════════════
  v3.0 = v2.9 底 ＋ cmim w 修正（两处几何正交：XBI1 摆位面 vs cmim 参数面，
         一次代跑到位——组长裁定四十「判读 A ⇒ 与回改合并一版 mix 出件」）。
  v2.9 已含：QR_L 8.7→12.0（XBI1 镜组真短根修，裁定四十 §一「法 A 采信定责版图」，
  修复=本 QR_L 改动；安全摆位律已立规，_qr_l_assert 运行时自证兜底）。

  ⑦ **cmim w 23.66→23.610：tank 选型公式补周边项**（裁定三十九 批准执行项；
     tank三判据实验报告 §五.3 / 判据②模型卡口径）。
     · 依据链：官方 LVS 识别层=MIM(36/0)=参数 w&l 全尺寸；模型卡
       C = CJ·w·l + CJSW·2(w+l)，CJ=1.5fF/µm²、CJSW=40aF/µm
       ⇒ 参数口径 840fF 精确解：1.5w²+0.16w=840 → w=23.611046。
     · 旧 w=23.66 系 lib mim_cap 面积口径（1.5w²=840→23.6643 相位 snap）的解，
       模型真值 843.479fF（+0.41% 良性——tank 落槌裁定「规格符合性 PASS」）；
       v3.0 换参数口径后真值 839.9257fF（−0.0088%），离名义近 47 倍。
     · **为何 23.610 不是 23.611046**：⑤ Offgrid 5nm——23611.046nm 与 %.3f 落库
       的 23.611µm（末位 1nm）均不在 5nm 制造网格上；落网格最近档 23.610
       （C=839.9257fF，Δ−0.074fF）。via 阵列相位核过：xanz=fix((23.610+0.12)/
       1.26)=18 不变（上板 22.68 零变化）、xoffset=GridFix(0.525)=0.525 干净。
     · 落库口径：mkcmim 不再走 lib mim_cap 面积口径解算，改直接按 w&l 传参
       （v2.6「相位规则由库持有」的前提已变——库解算口径=面积口径，与裁定
       三十九的参数口径不符，故 v3.0 把「参数→网格」这条规则收回交付件，
       推导全程留注释可审计）。先量后摆/落位自证/非致命回落全部保留。

M2 gilbert_mix 版图生成脚本 v2.9（2026-10-18 · **XBI1 镜组真短根修轮**）
════════════════════════════════════════════════════════════════════════
  v2.9 相对 v2.8 的全部变更（单点改动，其余逐字节同 v2.8）：

  ⑥ **QR_L 8.7→12.0：XBI1(ntaila 侧)镜参考网与尾轨 M1 真短根修**（fde9
     facediff_v34 静态对照发现 + 真 GDS m2_mix_v29.gds 连通域分析实锤，双源交叉）。
     · 病灶：npn13G2 的 C/B 带金属是横跨全管宽的长条（NX=10 实测 B 带半宽 9.30），
       旧 QR_L=8.7 令 XQr(NX=1) 管体整个落进 XQo(NX=10) 的 C/B 带金属投影 ⇒
       C_o=C_r、B_o=B_r，叠加 cb_tie(C_r=B_r) ⇒ XQo 二极管化 ⇒ ntaila 尾源从
       高阻电流镜塌成低阻二极管对（pex_mix_v27.cdl L25-26 Q7/Q8 C=B=ntaila）。
     · 实锤链：pex_mix_v29.json nets[0] = M1[6] area=49.18µm² 双标签
       [XBI1/nref, ntaila]（对照 XBI2/nref M1[67] 独立 19.77µm² 干净；ntaila 域
       面积 49.18 ≈ 19.77(镜链) + 29.4(ntaila 轨 M1 段) 并域）；桥接多边形 =
       XQo C/B 带金属（x[−29.25,−10.75] y[31.02,31.46] / x[−29.30,−10.70]
       y[28.74,28.98]）与 XQr 管带（x[−29.68,−27.72]）同层重叠。
     · 修：QR_L=12.0（XQr 管带左缘 gx−12.98，距 XQo B 带左端 gx−9.30 净空
       1.72µm ≥ M1 净距 0.63 富余）；Rref/cb_tie 逃逸列/y_join 汇横线/nvtop 出脚
       全部随 qr_x/rf_x 参数联动，零额外改动。XBI2 侧 QR_R=25.35 不动。
     · 自检盲区备案：preflight 二十项抓不到本类缺陷（e-pad 审计只查 E 指底座、
       ⑱ 只量自画矩形、器件 bbox 粗筛间距 1.0µm 时两 bbox 间隙 2.0µm 不报）。
       新律候裁：**镜像/邻管摆位必须按「邻件带金属实测半宽」验距，不得按
       PCell bbox 锚距**。本件新增 _qr_l_assert() 运行时断言兜底。
     · 电路影响（fde9 门1 A0′ FAIL 归因候选①）：ntaila 恢复高阻镜后尾电流
       偏置点改变 ⇒ CG 变化方向与量级待跑；修复后预期 pex cdl 的 XBI1 组
       Q7 ntaila <nref1> gnd NX=10 / Q8 <nref1> <nref1> gnd NX=1 / R5 nvtop
       <nref1>（与 ntailb 侧对称；内部网名按 label=XBI1/nref 层次形态）。

M2 gilbert_mix 版图生成脚本 v2.8（2026-10-18 · **真短 + 断路回改轮**）
════════════════════════════════════════════════════════════════════════
  v2.8 相对 v2.7 的全部变更（①②=回改清单内；③④⑤=清单外新发现，机检+真 GDS+bin
  pex 互证；新增 cbpath/resgeom 两道全板机检，全部零命中为自证判据）：

  ① **镜像组 XBI*.XQr 的 C=B 实连改绕 E 指列**（真短定谳 #1/#2，cbpath.cb_tie）。
     逃逸列选背离 XQo 一侧（XBI1 向左 / XBI2 向右），落点仍在原 y_join 横线覆盖内；
     C 带心 → y_join（climb 落点）的竖段保留 —— **C 带以上无 E 窗，无害段**。
  ② **XQs 的 C=B 实连改绕 E 指列**（真短定谳 #3，同 cb_tie，side=+1）；
     C → C+2.0（climb 落点）竖段保留，理由同上。
  ③ **rfop/rfon 竖轨通道 ∓15 → ∓16.2**（E 窗审计抓获）：旧 ∓15 正落在 XQ3/XQ4
     （Nx=6，锚 ∓9.975）的带列里 —— 横穿 B 带（rfop↔lopd/lond 真短，pex 42 域
     并域互证）+ 削最外指 E 窗 0.10µm（rfop↔nsw 真短）。16.2 处距带沿净距
     0.475µm。Ct 端子/TOPM1 竖轨/M1↔TM1 柱随参联动。
  ④ **ntaila 轨高改锚 P2 焊盘真值**（pad 审计抓获）：30Ω 落 rsil 长条 l=4.2857，
     lib 锚点在盘**下方** 0.236µm，旧轨（锚±0.15）顶边距盘底差 0.086µm ⇒
     Re1a/Re2a.P2（ntaila）直流断路。轨高 = 盘心 = RE_A_Y+l+0.40，并补
     锚点→焊盘短竖桩（⑫ 极性检查锚在 lib 标记点上，桩使标记/焊盘/轨三者连通）。
  ⑤ 事件性：`mkres` 登记 RES_DEVS、`mkhbt` 登记 HBT_DEVS；尾部新增
     `resgeom.audit_res_pads`（16 只电阻 ×P1/P2 焊盘金属覆盖）与
     `cbpath.audit_board_e_pads`（15 只 HBT ×全板 M1 对 E 指底座零重叠）。

  ⚠ 未动：DRC 基线指纹、器件摆位、其余布线。预期 gdsdiff delta =
    ①② 的 C=B 三段折线（各 +2 块 M1）、③ 的 rfop/rfon 竖轨/Ct/TOPM1 平移 1.2µm、
    ④ 的 ntaila 轨上移 0.366 + 2 根短竖桩。

M2 gilbert_mix 版图生成脚本 v2.7（2026-10-17）—— **v2.0~v2.6 全部作废，勿代跑**

v2.7 = v2.6 全部几何内容 + **Q8 代跑 v25 轮可修残留的代码落实**（2026-10-17 08:0xZ）。
逐条来源：组长 b7a0 inbox 第 59 行「Q8 代跑 v25 轮判读回执 · 战报 + 三问全答 +
可修残留三处」+ `design/sow6/DRC逐条坐标明细_v25轮_2026-10-17.md`（464 条全量）+ cell 名。

  ① 【TM1.a×4 / TM2.a×8 根治 —— 官方唯一抓到的「我画的」残留】全出在**自画 T 交
     半搭接**上（组长原话：「你的 drcgeom 只量矩形 minw，并集凹角是真盲区——建议补一条
     T 交检查」）：横轨端点正落在竖条中心，两条各自恰好等于该层最小宽（**逐矩形量
     ⑯ 全绿**），并集却在交界处留下一对相距半宽的**相向平行边**：
       · nbiasH（TOPM1，1.64）：官方逐条 (1.42,254.21;0.82,254.21)|(-0.6,255.03;0,255.03)
         与镜像组 @34.18 ⇒ 横轨两端外延 **0.82**（＝TOPM1 半宽）到竖条外缘。
       · nbiasL（TOPM2，2.0）：官方逐条 (-19,264.03)|(-20,265.03) 与镜像 (19,263.298)|
         (20,265.762) ⇒ 横轨两端外延 **1.0**（＝TOPM2 半宽）。
       · nvtop 横连（TOPM2）：官方逐条 (-38.2,9.268~10)|(-37.2,11.732~11) 与
         (55.582,10)|(53.118,11) ⇒ 两端外延 **1.0**。
     三处都只**外延横轨端点**，不挪网、不改拓扑、不动竖条；外延后并集只剩直角 L，
     无台阶、无小舌。净距核过：⑱ 间距 FAIL=0（外延端点离最近异网金属 >4µm）。
  ② 【自检台新增第 ⑳ 项（本轮真正的产出）】`drcgeom.facing_width_violations()`：
     把每个连通分量的并集边界抽出来（带「材料在哪一侧」），量**相向**平行边对的距离。
     **对着官方 v25 轮逐条坐标校准过，三个数字逐项对上**：
        M2  TOPM1 4 / TOPM2 8   drv1 0   drv2 TOPM2 8  ← 与官方 TM1.a/TM2.a 完全一致
     口径要点（两条都是踩过才知道的）：
       · 「相向」（材料分落两侧）才是判据 —— 官方对 drv1 的 vcc 直角拐角（两条**同侧**
         平行边相距 1.18µm）**不报**，同侧说明材料不在中间，那是台阶不是窄腰；
       · 形态学开运算（W×W 正方）那套把官方报的这些判成**合格**（本机实测三件全 0），
         口径与 deck 不符 ⇒ 留在 `morph_width_violations()` 里只作对照打印，**不判 FAIL**。
  ③ 【guard 环 / via 真值等其余残留】组长已裁：PCell 内部族（Offgrid 296 项、
     M1.b/M2.b/M4.b/V1.a/V1.b/CntB.* 九族）**备案接受，我无责**；guard 环零真几何违规。
     本件对此零改动。
  ④ 【答复三问】①via_stack 焊盘=阵列外推、档位即参数（线性律见下）；②逐条坐标已收，
     按 §三② 三处改（即上面 ①）；③lib 代跑解析 v2.2，与本件 ⓪ 闸钉的 sha 逐位一致。

  ⚠ 组长 08:0xZ 给的 TM1 平台线性律 **0.84(n−1)+1.26（n≥2）** 与他表里的 1×1=1.64
     不自洽（1×1 走 cut+2×0.61 的单孔规则）。本件顶层柱仍**全部钉 1×1**（唯一实测档），
     不外推 ⇒ 几何与 v2.5 实跑过的那份逐位相同。vcc 桶若要阵列需他点头。

v2.6 = v2.5 全部几何内容 + **组长 07:45Z 回执四裁的执行项**（lib v2.2 / mim_cap / TV1 钉档）。
逐条来源：组长 b7a0 07:45:29Z 回执信 + `probe_viastack_array_v22_2026-10-17.md`（sha e44d63e2…）。

  ⓪ 【库版本闸升 v2.2】sync_lib.py 的 CAND 已按裁定改成
     `design/sow6/lib13g2.py`（canonical，单层名）+ `top/lib13g2.py`（v2.1 历史快照），
     取行数多的那份 → 本脚本解析 **v2.2 / 539 行 / 27592B / sha 02ecbfb95b3b…**。
     变更仅 Board.via 的 vt1 透传，对本件器件/标注计数零影响（组长 07:45Z ①）。
  ① 【cmim 改用库原语 mim_cap —— 裁定②「确认，改」】v2.5 是我自己 create_cell + 手算
     23.66 见方；本版把 **W/L 解算与相位 snap 交给库**（mim_cap：官方密度
     cmim_caspec=1.5 fF/µm² → 840fF → 23.66 见方，且相位已固化在实现里，
     「23.665 → 内部 vmim 阵列 offgrid×1296、23.66 干净」的坑一并治掉）。
     摆放锚点口径 = `mkpc_at(kind="cap")` 把 **cell bbox 中心**落到 target，
     而两端引脚与 bbox 中心重合（组长实测：两 pin 同心于电容中心）⇒ target 直接给
     **顶层端子坐标**，端子零偏移落位。**先量后摆**（见 mkcmim 注释），
     落位后用 Dev.p 自证端子位置；对不上 → 占位回落，绝不猜。
  ② 【TopVia1 栈钉档 vt1=1×1】v2.2 起 `Board.via(t_layer="TopMetal1")` 会让
     **vt1 阵列档位继承 cols/rows**（v2.1 及更早硬编码 1×1）。若不显式钉档：
       · 本件 §7 的 rfop/rfon 顶层柱（`b.via(ch, Y_RF, "Metal1", "TopMetal1")`，
         默认 cols=2,rows=2）会从 1×1 静默变成 **2×2 阵列**；
       · 而 TM1 平台尺寸**非线性**（实测 1×1 = 1.64 见方、3×2 = 2.94×2.10，
         组长明令「按实测值取用，**勿自行外推**」）⇒ 2×2 无真值可依。
     故所有 t_layer=TopMetal1 的 via 显式 `vt1_cols=1, vt1_rows=1`：
     几何与 v2.5（v2.1 实跑过的那份）**逐位相同**，只用已实测的 1×1 平台。
     代价写在信里：这两处顶层馈电柱仍是**单颗 TopVia1**，EM 余量偏薄 ——
     若要阵列，需组长补测 (2×2)/(37×1) 的 TM1 平台真值。
  ③ 【口径勘误（组长 07:45Z ②）】cmim 的 pin shape 落 datatype **/2（pin purpose）**，
     **/1 是网名 label 层（METAL_LNUM）**。本脚本一直按 /2 取脚（`Board.pin_centers`
     = DT_PIN），口径本就正确；此处留痕以免下口再写「M5 pin 1」。

v2.5 = v2.4 全部内容 + **官方 DRC 两族的自侧落实** + 代跑补丁五条收编。逐条来源：
  组长 b7a0 07:29Z 回执信 + `判读纪要_M2M3代跑v24全链_2026-10-17.md`（sha 3c9bf6be…，8753B）。

  ① 【Offgrid 族（≈90% 项数）根治】官方制造网格 grid=0.005µm（纪要 §3.4）。
     病根单一：凡进 PCell 的几何参数、以及我画的所有顶点坐标，都可能是分数微米。
     两处治全族：
       · resgeom 侧：长度 l 量化到 **1/168µm** 晶格 —— 不是 1/200，是推出来的：
         电阻 P2 引脚高 = 0.72+0.84·l，要它落在 5nm 网格上 ⇒ 0.84·l=0.005k ⇒ l=k/168。
         取整到 1/168 即 0.84·l = k/200，恰好 5nm 整数倍。参数串改给足有效位
         （旧 `%.4g` 把 2000Ω 的 l=25/17 写成 "1.471u" → P2 落在 7.95564，离格）。
       · 本脚本侧：`b.rect / wire_h / wire_v / via / label` 五个入口全部过一层
         5nm 量化（**在交付件里改，不改库** —— 组长代跑解析的是他自己那份 lib13g2）。
  ② 【TM1.a×58 / TM2.a×31（要改图）】TopMetal1 最小宽 1.64µm、TopMetal2 2.0µm，
     而我全部顶层走线都用的库默认 W=0.30µm —— 顶层每根线都是违规。本版给
     TOPM1/TOPM2 的 wire_h/wire_v 设**每层最小宽下限**（顶层线一律 1.64/2.0）。
     ⚠ 由此引出一条新约束（我在 ⑨ 里踩到，见 bias rail 那段注释）：两条同层宽线
       若引脚相距 < 1.64+1.64，就会由「两条细线各自违规」变成「一条间距违规」。
       2k 电阻 P1→P2 只有 1.955µm，顶层加宽后 M1 插头与顶层立管的净距只剩 0.315µm
       → 改走「先在 M1 上把偏置轨拉高、离电阻远了再上顶层」。
  ③ 【cmim 落线（纪要 §3.2/§3.3 的 PDK 真值）】真引脚**分居两层**：
     Metal5.pin(67/2) 与 TopMetal1.pin(126/2)，每层恰 1 枚、同心于 cell 局部
     (11.83,11.83)，bbox 24.26 见方。旧 mkcmim 的「同层恰 2 pin」启发式**永不命中**
     → 六只全部回落占位。本版按真值取两层引脚，**标注加实例偏移**（旧版把 cell
     本地坐标当顶层绝对坐标落 label），并把六只的端子真正接到网上（§6/§7）。
  ④ 【ptap → ptap1】PDK 不认 `ptap`（真名 ptap1，ntap 同理）。`create_cell` 返 None
     被 assert 吞进 NOTES = **静默不落图**（纪要 §二.1）。本版改 ptap1 并保留
     try/except：名字再变也只是 PTAP_SKIPPED 记进 NOTES，不掐断全链。
  ⑤ 【bbox 双风格读取】真 klayout 的 Box 只有 left/bottom/right/top，仿真层 DBox
     只有 x1/y1/x2/y2 —— 原样一侧跑通另一侧必崩。本版统一走 _bb() 适配器。

v2.4 = v2.3 全部内容 + **⑭ 官方 label purpose /1 补打**（R-ANNO-01 ②：此前网名只打
     <金属>/25，而组长口径要求网名必须在官方 label purpose /1 层。/25 按 reply_v10
     §57-63 是次级 label 通道、不生幽灵网，故双打不撤。理由与取舍见 relabel_official）。

v2.3 = **路由返工 + 三处结构性勘误**。v2.2 自检台 ⑤c/⑤d 抓出 **15 处 FAIL**
（4 处跨层短路 + 11 处过孔柱压异网），本版全部清零，自检台 **12/12 PASS**。

  ① 【路由返工：三根引脚各走专属通道】病根一句话：npn13G2 的 C/B/E **同 x**
     （C y+1.13 / B y−1.14 / E 居中）。只要某条网的竖直干路还走在这个 x 上，
     它必然竖穿同器件的另外两只脚。v2.2 的 15 处 FAIL **无一例外**全是这一类。
     本版给三类脚各划一条通道：集电极向外折到 x=∓15（C 脚插头走 M1）、
     基极向岛心内折到 ∓3/±6（四条立管各一条通道，M1 插头）、
     发射极本就在 M2 竖线（nswa/nswb）保持不动。三条通道互不同 x，
     且 C/B 的插头在 M1、E 的干路在 M2 → 层与 x 双重错开。
  ② 【勘误：Rd1/Rd2 两端接反】网表 `Rd1 lop lopd 10` → P1=lop、P2=lopd；
     v2.2 把 lopd 的 M3 立管接在 P1、把 'lop' 标注画在 P2 的 M1 短脚上。
     既有检查全看不见：⑦ 比的是 DEV_NETS **声明**（声明是对的）、
     NET_DECL 只比网名**集合**、⑤b/⑤c 管的是连通与短路。已改回，并新增自检台
     第 ⑫ 项「引脚极性（几何取证）」当场复现。
  ③ 【勘误：RB_H 算式套错 → nbiasH/nbiasL 够不到竖条 P2】
     `RB_H = 0.72 + 0.84*res_params(...)["_geom"][0]`：_geom[0] 已经是**算式求出的
     长度**(112.69)，再套一次 0.72+0.84·L 得 95.38，而真实 P2 高度是
     0.72+0.84·**133.3** = 112.69。于是两条偏置网的立管从 y=330.38（电阻腰上）起，
     永远够不到 P2 引脚(347.692) —— **偏置网在版图上是断的**。本版一律用
     `res.p["P2"][1]` 真引脚 y。
  ④ 【勘误：ntailb 柱头被 e 网压住】柱原落在 Re1b/Re2b.P2 正下方 1.2µm（∓10,64.2），
     而 e1b/e2b 的 M2 竖引同列从 y=63 到 85 → 中间层压异网金属（2 处 FAIL）。
     改为 M1 上向岛心插 5µm 再落柱（∓5, 68）。
  ⑤ 【勘误：guard 环几何压在核内容上】RING_M=6 而环宽 4、M2 环又 inset=5
     → M2 环落在 x∈[CORE−1, CORE+3]，**骑在核 bbox 里**，于是 Rb1 的 M1→M3 柱脚
     整个踩在环上。改为环宽 2µm + RING_M 8µm，两环都退到核外 ≥3µm。

v2.2 的内容（仍然有效，v2.3 全部继承）：

v2.2 = **网名分裂勘误**（自检台 2026-10-17 新增的第 ⑤b 项「同名分裂」查出，v2.0 漏了三处）：
  ⑤ 【地网全断】v2.0 把每个发射极/假管脚各自落一块 M4 小岛就标 gnd，**岛与岛之间没有任何连线**
     —— 版图上 gnd 断成 ~8 段，LVS 必然判该网多段/浮空。本版加一条 M4 地轨把全部地脚串起来。
  ⑥ 【ntailb 断】v2.0 的 M3 轨只从 Re1b.P2 拉到 Re2b.P2（x∈[CX−10,CX+10]），
     而 XBI2.XQo.C 的引下点在 x=CX+20 —— **差 10µm 没接上**。本版把 M3 轨延到引下点。
  ⑦ 【nvtop 断】两组镜像的 Rref.P1 各自落一根 TOPM2 短脚就标 nvtop，**两根之间没连**。
     本版在 TOPM2 上补一条横向连接。
  根因与 v2.0 的 12 倍器件数同类：**自查台当时没有「一条网散在多个连通分量」这一项**，
  于是「标了名字就算接上了」。第 ⑤b 项补上后 v2.0 当场被抓出三处。

v2.0 的勘误内容（仍然有效，v2.2 全部继承）：v1.1 已作废（勿代跑）。四处实质错误，全部由前置自检台第⑦项
（网表↔版图交叉核对）查出，逐条可复现：

  ① 【器件数 12 倍】网表 `hbt_mirror` 逐字是
        XQr  nref nref 0 0 npn13G2 nx=1
        XQo  nout nref 0 0 npn13G2 nx={nx}
        Rref ntop nref {rr}
     —— `XQo` 是**一个** Nx 指器件。v1.1 的 gen 脚本按「环绕共质心」摆了
     **12 个 Nx=10** → 版图 120 指 vs 网表 10 指，尾流能力 12 倍 + LVS 实例数不符。
     根因：把「PDK PCell 内部的指阵列」误当成「版图要自己摆的阵列」。真值表 §4 的
     `hbtdiff_array 原语（ABBA/共质心+dummy）` 本就是**库 v2 原语**，阵列在库里面。
     正确落图：**Qr(nx=1) + XQo(nx=10) + Rref** 三件，无手工阵列、无 dummy。
  ② 【漏件】6 只 2k 电阻（Rba1/Rba2/Rbb1/Rbb2/Rb1/Rb2）v1.1 根本没落图；
     4 只 1n 耦合电容无占位；nbiasL/nbiasH/nifbias/nsens/nvtop 五个偏置口未端口化。
  ③ 【引脚极性】网表 `Re1a e1a ntaila 30` → P1=e1a、P2=ntaila；v1.1 的 NET_DECL
     写成 `ntaila = Re1a.P1`，上下颠倒。
  ④ 【阻值几何】v1.1 全部电阻都是 l=2u/w=1u 一档占位，不对应 30Ω/10Ω/45Ω/680Ω/2k。
     本版全部经 `resgeom.res_params()` / `res_auto()` 由阻值反算（**Q5 真值**：
     cornerRES 三档 rsil 6.02/7/7.98 · rppd 234/260/286 · rhigh 1160/1360/1560，
     几何取 typ 档；金属 M1 0.135 / M2-5 0.103 / TM1 0.021 / TM2 0.0145 Ω/□。
     回执给真值后只改 resgeom 一行，全岛几何自动重算）。

用法（组长侧）：
    . /data/workspace/pdk/kl_env030.sh
    KLAYOUT_PATH=$KLTECH klayout -zz -r gen_M2_mix_v26.py
用法（本机自检，无 klayout）：
    python design/sow6/dryrun/preflight.py design/sow6/gen_M2_mix_v26.py

输出：/data/workspace/gds/m2_mix_v35.gds

【2026-10-17 修订 · 文件名不变内容已变】按组长 reply_v12 的 Q5/Q6/Q7 落地：
  Q5 Rsheet 真值换算 + 高阻自动选型（res_auto）→ 三件电阻几何全部重算；
  Q6 cmim 真件（PCell `cmim`、w&l、23.610µm 见方（v3.0，见头注 ⑦），自适应引脚层 + 非致命回落）；
  Q7 guard 环定网 gnd（搭桥+落地柱，真接进 gnd 网）+ ptap 接触（PDK 默认参数，
     仿真层跳过、代跑落）。变更清单与逐项理由见 CHANGELOG_2026-10-17_Q5Q6Q7.md。
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (os.path.join(_HERE, "..", "..", "phys", "top"), _HERE):
    if os.path.isdir(_d):
        sys.path.insert(0, os.path.abspath(_d))
import lib13g2 as L
import resgeom as RG
import cbpath as CB

CX = 0.0                       # 岛几何中心 x；y 自下而上排布，岛框最后反推
# ── Q6 cmim 真件口径（reply_v12 §三 + 组长 07:45Z 裁定②）──
#   v2.6：W/L 交给库原语 `Board.mim_cap(name, C_fF, target)` 解（官方密度 1.5 fF/µm²
#   + 相位 snap，23.66 见方），本脚本只给**目标电容值**与**端子顶层坐标**。
#   CMIM_W/CMIM_L 保留为**自查基准**：库解出来的边长与之不符 → 记 NOTES 并占位回落
#   （官方密度或相位规则若变了，23.66 见方这块板的间距前提就不再成立，不能默跑）。
USE_CMIM = True
CMIM_C_FF = 840.0             # 四只耦合 840fF + 两只旁路 840fF（reply_v12 §三）
CMIM_W = CMIM_L = 23.610      # µm 见方（v3.0：参数口径精确解 23.611046 落 5nm 网格）
# ⚠ v3.0 口径变更（裁定三十九 批准 / 判据②模型卡）：840fF 的**参数口径**
#   （C=1.5w²+0.16w，官方模型卡 C=J·w·l+CJSW·2(w+l)）精确解 w=23.611046，
#   违反 ⑤ Offgrid 5nm（23611nm 非 5 的倍数；%.3f 落库 23.611 同样 offgrid）
#   ⇒ 落网格最近档 23.610：C_model=839.9257fF（−0.0088%）。via 相位自洽：
#   xanz=18（上板 22.68 零变化）、xoffset=GridFix((23.610−22.56)/2)=0.525 干净。
#   本值仍是**自查基准**：PCell 展开边长与之不符 → 记 NOTES 并占位回落。
# ⚠ v2.5（纪要 §3.2 PDK 真值）：cmim 两端**分居两层**——Metal5.pin(67/2) 与
#   TopMetal1.pin(126/2)，每层恰 1 枚，**同心**于 cell 局部 (11.83,11.83)，
#   bbox = (−0.6,−0.6 ; 24.26,24.26)（23.66 见方 + 0.3 边距），"23.66u" 被 PCell 吃下。
#   ⇒ 端子绝对坐标 = **摆放点 + (11.83, 11.83)**。
#   ⇒ v2.4 的「同层恰 2 pin」自适应**永不命中** → 六只全回落占位（纪要 §二.1 实锤）。
# ⚠ v2.6 勘误（组长 07:45Z ②）：pin shape 的 datatype 是 **/2 = pin purpose**；
#   **/1 是网名 label 层（METAL_LNUM）**，两者别混。`Board.pin_centers` 读的就是 /2。
CMIM_PIN_OFF = (11.83, 11.83)     # cell 局部引脚坐标（两端同心）
CMIM_PIN_LAYERS = ("M5", "TOPM1")  # n_lo 接 M5.pin、n_hi 接 TopMetal1.pin
CMIM_PINS = {}                    # 名 → 端子顶层坐标（真件落图时回填，占位件为空）

# ── v29（2026-10-18 · 裁定十七）：cb_tie 下横线 M1.e 自动退让（cbpath 内核升级）──
#    mix v28 真 GDS 定谳：cb_tie 下横线走 B 带心（顶 29.01）与 E 指底座（起
#    29.215）净距 0.205 < M1.e 0.22，短差 0.015µm。修法 = cbpath.cb_tie 内核
#    加自动退让（净距钳 0.225）+ assert_m1e_gap 间距断言（盲区第五例）+
#    audit_board_e_pads 全板 M1.e 间距桶。唯一几何 delta：XQr/XQs 下横线 y
#    −0.02（28.86→28.84），其余逐位不动。
b = L.Board("TX5G_M2_MIX_V35")

# v2.0 回改登记簿（与 drv1/drv2 v2.0 同款）
HBT_DEVS = []
RES_DEVS = []


def mkhbt(name, nx, x, y, mirror=False):
    inst = b.mkpc_at(name, "npn13G2", {"Nx": nx}, (x, y), "hbt", mirror=mirror)
    HBT_DEVS.append([name, (x, y), nx, mirror, []])
    return inst

# ══════════════════════════════════════════════════════════════════════════
# v2.5 官方 DRC 两族的**自侧落实**（纪要 §3.4 grid / §4.1 Offgrid / §4.2 真几何族）
# ──────────────────────────────────────────────────────────────────────────
# 口径纪律：改在**交付件**里，不改库 —— 组长代跑 `import lib13g2` 解析的是他自己那份，
# 我改本地副本对代跑毫无作用（只会制造「我这边已经改了」的假象）。
GRID = 0.005                          # 官方制造网格（sg13g2_tech_default.json drc_rules.grid）
# 顶层最小宽（TM1.a=1.64 / TM2.a=2.0，纪要 §4.2 实测规则值）。其余金属维持库默认
# 0.30µm：纪要里 M1~M5 **没有**最小宽违规项，说明它们的 minw ≤ 0.30，不动。
MINW = {"TOPM1": 1.64, "TOPM2": 2.0}


def _q(v):
    """量化到官方 5nm 网格（幂等；已对齐的值原样返回，故不引入新误差）。"""
    return round(v / GRID) * GRID


_rect0, _via0, _lab0 = b.rect, b.via, b.label
_wh0, _wv0 = b.wire_h, b.wire_v


def rect(lname, x1, y1, x2, y2):
    _rect0(lname, _q(x1), _q(y1), _q(x2), _q(y2))


def wire_h(lname, y, x1, x2, w=None):
    if abs(_q(x2) - _q(x1)) < GRID:          # 零长线 = 零面积框，官方 deck 与
        return                                  # 真 klayout 都会当退化图形；直接不画
    _wh0(lname, _q(y), _q(x1), _q(x2), w or MINW.get(lname))


def wire_v(lname, x, y1, y2, w=None):
    if abs(_q(y2) - _q(y1)) < GRID:
        return
    _wv0(lname, _q(x), _q(y1), _q(y2), w or MINW.get(lname))


def via(x, y, b_layer="Metal1", t_layer="Metal2", cols=2, rows=2,
        vt1_cols=None, vt1_rows=None, vt2_cols=None, vt2_rows=None):
    # v2.6：lib v2.2 起 TopVia1 阵列档位走 vt1_columns/vt1_rows，缺省继承 cols/rows。
    # v2.7（Q10 轮实测）：**lib v2.3 又给 TopVia2 加了同款继承**（vt2_columns/vt2_rows，
    #   t_layer=TopMetal2 时缺省继承 cols/rows）。本件有 5 处 t_layer=TopMetal2 的栈，
    #   在 v2.3 下实测 vt2 由 1×1 **静默变成 2×2**（`via_stack` 实例参数逐只统计可证）
    #   ⇒ 与「与你交付件零交集」的判断不符，故按同纪律**显式钉 vt2=1×1**，保持
    #   与已代跑（v25 轮 / lib v2.2）那份**逐位相同**的何。
    # 本封装**透传** vt1_*/vt2_*（否则钉档传不进来，报 unexpected kwarg），且**故意不给
    # 默认值**：None = 交给库按 cols/rows 继承 ⇒ 想钉 1×1 必须显式写出来。
    _via0(_q(x), _q(y), b_layer, t_layer, cols, rows, vt1_cols, vt1_rows,
          vt2_cols, vt2_rows)


def label(lname, x, y, text):
    _lab0(lname, _q(x), _q(y), text)


b.rect, b.wire_h, b.wire_v, b.via, b.label = rect, wire_h, wire_v, via, label


def _bb(cell):
    """top cell bbox 的**双风格**读取适配器（代跑补丁①）。

    真 klayout 0.30 的 Box/DBex 走 left/bottom/right/top；本机仿真层 DBox 走
    x1/y1/x2/y2。原样写一侧跑通、另一侧 AttributeError —— 「我这边全绿、他那边崩」
    的经典来源。统一走这里，两种风格都能读，读不到就**炸**（不猜）。
    """
    d = cell.dbbox()
    if d is None:
        return None
    if hasattr(d, "left") and hasattr(d, "x1"):
        return (min(d.left, d.x1), min(d.bottom, d.y1),
                max(d.right, d.x2), max(d.top, d.y2))
    if hasattr(d, "left"):
        return (d.left, d.bottom, d.right, d.top)
    if hasattr(d, "x1"):
        return (d.x1, d.y1, d.x2, d.y2)
    raise RuntimeError(f"无法读取 dbbox：{type(d)}")

# ── 真值表派生量（单元几何真值表_v1 §1/§2）────────────────────────────
HBT_H = 7.11

# ── 全局层分配（v2.0）──────────────────────────────────────────────
# 判据：同一层上各网的金属包围盒**互不相交**（自检台逐层合并判定，短路嫌疑为 0）。
# 远距离网靠「层 + y 带 + 专属 x 通道」三重分离；同层的网靠 x 区间或 y 带错开。
_M2NUM = {"M1": "Metal1", "M2": "Metal2", "M3": "Metal3", "M4": "Metal4",
          "M5": "Metal5", "TOPM1": "TopMetal1", "TOPM2": "TopMetal2"}
_ORDER = ["Metal1", "Metal2", "Metal3", "Metal4", "Metal5",
          "TopMetal1", "TopMetal2"]
GND_LAYER = "M4"        # 地专层

# 嵌套子电路内部网的版图网名形态（hbt_mirror 内部网 nref 是**每实例一条独立网**：
# XBI1.nref / XBI2.nref 两条，网表无 .global；标成裸 nref 或 {pfx}_nref 都对不上网表）
#   hier → xbi1/nref（默认）｜ flat_dot → xbi1.nref ｜ bare → nref（不可取）
NESTED_STYLE = "hier"
_NSEP = {"hier": "/", "flat_dot": ".", "bare": ""}[NESTED_STYLE]


def hnet(pfx, net):
    return net if _NSEP == "" else f"{pfx}{_NSEP}{net}"

LOPD_LAYER = "M3"       # lopd（Rd1 内口 + Q3.B + Q5.B）
LOND_LAYER = "M5"       # lond（Rd2 内口 + Q4.B + Q6.B）——与 lopd 分层避交叉
GMB_LAYER = "TOPM1"     # gm 基极四网 na1p/na2n/nb1p/nb2n（插列排布，平面无交叉）
BIASH_LAYER = "TOPM1"   # nbiasH 轨（与 GMB 同层但 y 带在上方，互不相交）
BIASL_LAYER = "TOPM2"   # nbiasL 轨（与 BIASH 分层 → x 交错也不相交）
NIFB_LAYER = "M3"       # nifbias（底部 y 带，与 lopd 的 y 带不重叠）
SENS_LAYER = "TOPM2"    # nsens
NVT_LAYER = "TOPM2"     # nvtop
GND_RAIL_Y = 18.0     # M4 地轨（v2.2 新增：v2.0 的 gnd 是碎岛，没有轨）


def climb(x, y, from_layer, to_layer):
    """from_layer → to_layer = **一个** via_stack（焊盘只在两端层）。

    2026-10-17 血泪：旧版「逐级 via 上跳」会在**每一层**留焊盘（M1→M3 = M1→M2 + M2→M3），
    压在别人的走线上就是真短路 —— 自检台 ⑤c 在本件抓出 5 处（rfop/nswa、nswb/lopd…）。
    自检台 ⑤d 对每根过孔柱加硬约束：中间层压到异网金属 = FAIL。
    ⚠ 真值表 §3 只实证过 M1↔M2；跨厚金属组合待组长回执（回执项 ②），退路见设计稿。
    """
    i = _ORDER.index(from_layer)
    tgt = _ORDER.index(_M2NUM[to_layer])
    assert i <= tgt, f"climb 方向错：{from_layer} → {to_layer}"
    if i == tgt:
        return
    if _ORDER[tgt] == "TopMetal1":
        # v2.6：lib v2.2 起 TopVia1 阵列档位**继承 cols/rows**（v2.1 硬编码 1×1）⇒
        # 本函数默认 cols=2,rows=2 会把顶层柱静默变成 2×2 阵列，而 TM1 平台非线性
        # （实测 1×1=1.64 见方 / 3×2=2.94×2.10，组长明令勿外推）⇒ 显式钉 1×1。
        b.via(x, y, b_layer=_ORDER[i], t_layer=_ORDER[tgt], vt1_cols=1, vt1_rows=1)
        return
    if _ORDER[tgt] == "TopMetal2":
        # v2.7：lib v2.3 起 TopVia2 档位**同样继承 cols/rows** ⇒ 本件 5 处 TM2 顶层柱
        # 在 v2.3 下会静默变 2×2（实测证实）。TopVia2 端头 2.00×2.00 压线合规是组长口径，
        # 但 2×2 的 TM2 平台**无实测值** ⇒ 与 vt1 同纪律显式钉 1×1，保持与 v25 轮逐位相同。
        b.via(x, y, b_layer=_ORDER[i], t_layer=_ORDER[tgt],
              vt1_cols=1, vt1_rows=1, vt2_cols=1, vt2_rows=1)
        return
    b.via(x, y, b_layer=_ORDER[i], t_layer=_ORDER[tgt])


def hop(x, y, from_layer="Metal1"):
    climb(x, y, from_layer, GND_LAYER)


# ═══════════════════════════════════════════════════════════════
# 0. 电阻几何助手（阻值 → (l,w)，假设 A1）
# ═══════════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════════════════
# 0b. cmim 真件（Q6）
# ═══════════════════════════════════════════════════════════════════════
def mkcmim(name, n_lo, n_hi, px, py):
    """放一只真 cmim：**走库原语 Board.mim_cap**（v2.6，组长 07:45Z 裁定②「确认，改」）。

    v2.6 改法与理由：
      ① W/L 交给库解：`mim_cap(name, C_fF, target)` 按官方密度 `cmim_caspec=1.5 fF/µm²`
         解方阵边长并做**相位 snap**（官方 cmim generateVias：n=fix((w+0.12)/1.26)、
         xoffset=(w−(n·1.26−0.12))/2 须落 0.005 网格，否则内部 Vmim 阵列全体 offgrid
         —— 组长实测 23.665 → offgrid×1296、23.66 干净）。我在 v2.5 手算 23.66 恰好
         落在干净相位，但**相位规则该由库持有**，不该由我在交付件里复刻一遍。
      ② 摆放锚点口径：`mkpc_at(kind="cap")` 把 **cell bbox 中心**落到 target，
         而两端引脚与 bbox 中心重合（组长实测「两 pin 同心于电容中心」）⇒
         **target 直接给顶层端子坐标**，端子零偏移落位（v2.5 是自己 create_cell 再插）。
      ③ **先量后摆**：插入前先造一只同名 cell 量出「bbox 中心 − 引脚中心」的真实偏移；
         万一将来两者不重合，用目标点反推 bbox 中心该落哪 → 仍是精确落位，
         而不是「插完发现偏了 30µm 再想办法」。绝不留下错位实例。
      ④ 落位后**自证**：`Dev.p` 给出两端顶层坐标，与目标差 > 1nm → 占位回落（不猜）。
      ⑤ 仍然**非致命**：任何一步不行 → 落占位矩形 + 记 CMIM_FALLBACK，不掐断全链。

    返回 (ok, (px, py))：成功时给出**顶层坐标**下的端子位置（两端同心，一个点）。
    """
    import pya as _pya
    if not USE_CMIM or hasattr(_pya, "WARN"):
        return False, None                     # 仿真层无 PDK → 走占位（自检台 ⑦b 会核对）
    # ── ③ 先量：bbox 中心 vs 引脚中心的真实偏移（未插入的临时 cell，不进版图）──
    try:
        probe = b.ly.create_cell("cmim", L._SG13,
                                 {"Calculate": "w&l", "w": f"{CMIM_W:.3f}u",
                                  "l": f"{CMIM_L:.3f}u"})
        bb = probe.dbbox()
        cen = ((bb.left + bb.right) / 2.0, (bb.bottom + bb.top) / 2.0)
        pin_loc = []
        for _ln in CMIM_PIN_LAYERS:
            _ps = b.pin_centers(probe, _ln)
            if len(_ps) != 1:
                NOTES.append(f"{name} CMIM_FALLBACK：{_ln} 上 pin 数={len(_ps)}"
                             f"（真值应为 1）—— PDK 版本或引脚层变了，人工核")
                return False, None
            pin_loc.append(_ps[0])
        if abs(pin_loc[0][0] - pin_loc[1][0]) > 1e-6 or abs(pin_loc[0][1] - pin_loc[1][1]) > 1e-6:
            NOTES.append(f"{name} CMIM_FALLBACK：两端不同心 M5{pin_loc[0]} vs "
                         f"TOPM1{pin_loc[1]} —— 同心假设失效，人工核")
            return False, None
        # 引脚中心相对 bbox 中心的偏移 → 目标点反推 bbox 中心落点
        tgt = (px - (pin_loc[0][0] - cen[0]), py - (pin_loc[0][1] - cen[1]))
    except Exception as e:
        NOTES.append(f"{name} CMIM_FALLBACK：锚点预检失败 {type(e).__name__}: {e}")
        return False, None
    # ── ① v3.0：**直接按 w&l 传参落位**（不再走 lib mim_cap 面积口径解算）──
    #    理由见头注 ⑦：裁定三十九 批准的是**参数口径**精确解（1.5w²+0.16w=840），
    #    而 lib mim_cap 按面积口径（1.5w²=C）解——两个口径不同解，必须绕开；
    #    「参数→网格」规则（23.611046→23.610，⑤ Offgrid）收回交付件并留推导。
    #    mkpc_at(kind="cap") 锚=bbox 中心 → target = ③ 反推出的 bbox 中心，语义不变。
    _p = {"Calculate": "w&l", "w": f"{CMIM_W:.3f}u", "l": f"{CMIM_L:.3f}u"}
    try:
        d = b.mkpc_at(name, "cmim", _p, tgt, "cap")
    except Exception as e:
        NOTES.append(f"{name} CMIM_FALLBACK：mkpc_at(cmim w&l) 失败 {type(e).__name__}: {e}")
        return False, None
    w = l = CMIM_W
    # 自查：PCell 展开边长必须等于基准（先量 probe 的 bb 已隐含一次，这里对 Dev 再验）
    try:
        _bb = d.cell.dbbox() if hasattr(d, "cell") and d.cell is not None else None
        if _bb is not None and (abs(_bb.width() - CMIM_W) > 1e-6
                                or abs(_bb.height() - CMIM_L) > 1e-6):
            NOTES.append(f"{name} CMIM_FALLBACK：PCell 展开 {_bb.width():.4f}×{_bb.height():.4f}"
                         f" ≠ 基准 {CMIM_W}×{CMIM_L}（官方 PCell 行为变了，人工核）")
            return False, None
    except Exception:
        pass                                   # Dev 无 cell 句柄时跳过该项（落位自证 ④ 仍兜底）
    c_nom = 1.5 * w * l + 0.08 * (w + l)       # 参数口径名义值（判据②模型卡，fF）
    # ── ④ 落位自证：Dev.p 是库自己换算的顶层端子坐标 ──
    pins = dict(d.p)
    if "BOT" not in pins or "TOP" not in pins:
        NOTES.append(f"{name} CMIM_FALLBACK：mim_cap 返回件缺 BOT/TOP 端 {sorted(pins)}")
        return False, None
    (bx, by), (tx, ty) = pins["BOT"], pins["TOP"]
    dev = max(abs(bx - px), abs(by - py), abs(tx - px), abs(ty - py))
    if dev > 1e-3:
        NOTES.append(f"{name} CMIM_FALLBACK：落位后端子 M5({bx:.3f},{by:.3f})/"
                     f"TOPM1({tx:.3f},{ty:.3f}) 偏离目标 ({px:.3f},{py:.3f}) {dev:.3f}µm")
        return False, None
    b.label("M5", px, py, n_lo)
    b.label("TOPM1", px, py, n_hi)
    CMIM_PINS[name] = (px, py)
    NOTES.append(f"{name} CMIM_REAL cmim(w&l={w}u 参数口径C_model={c_nom:.3f}fF"
                 f"[=1.5w²+0.16w，裁定三十九 批准] vs 面积口径{CMIM_C_FF:g}fF) 端子层=M5.pin(67/2)=[{n_lo}] + "
                 f"TopMetal1.pin(126/2)=[{n_hi}] 同心于顶层 ({px:.2f},{py:.2f})")
    return True, (px, py)


def mkres(name, R, model, x, y):
    """model="auto" = 让 resgeom.res_auto 在 rsil/rppd/rhigh 里挑面积最小的一档
    （Q5 真值落地后必须开：rsil 只 7Ω/□，1kΩ 会被拉成 142.9µm 长条）。
    选型结果逐件打印，型号即版图侧决策、随信报组长。"""
    p = RG.res_auto(R) if model == "auto" else RG.res_params(R, model)
    m = p["model"]
    _e = p.get("_griderr_pct", 0.0)
    print(f"  [res] {name:6s} {R:7g}Ω → {m:6s} l={p['_geom'][0]:10.6f} "
          f"w={p['_geom'][1]:7.3f} Rchk={p['_geom'][2]:9.4g}Ω "
          f"离格量化{_e:+6.3f}%  "
          f"P2pad顶 y={_q(y) + RG.res_pad2(m, p['_geom'][0])[1]:.3f}"
          f"（lib锚点 {_q(y) + RG.res_pin_anchor(p['_geom'][0]):.3f}"
          f"，高 {RG.res_pin_gap(m, p['_geom'][0]):+.3f}µm）", flush=True)
    assert abs(_e) < 5.0, f"{name} 离格量化误差 {_e}% 过大，检查 resgeom 晶格"
    RES_DEVS.append((name, (_q(x), _q(y)), m, p["_geom"][0], p["_geom"][1]))
    return b.mkpc_at(name, m, {"Calculate": "l", "l": p["l"], "w": p["w"]},
                     (_q(x), _q(y)), "res")


# ═══════════════════════════════════════════════════════════════
# 1. gm doublet：ABBA 四管（nx=3）+ 四只 30Ω Re
# ═══════════════════════════════════════════════════════════════
GM_COL = 20.0                  # 中心距 20µm → 相邻盒间空 9.6µm（容得下 2k 竖条）
GM_Y = 85.0
GM_X = {"XQ1a": CX - 1.5 * GM_COL, "XQ1b": CX - 0.5 * GM_COL,
        "XQ2b": CX + 0.5 * GM_COL, "XQ2a": CX + 1.5 * GM_COL}

# ABBA 序（网表：XQ1a nswa/na1p, XQ1b nswa/nb1p, XQ2b nswb/nb2n, XQ2a nswb/na2n）
XQ1a = mkhbt("XQ1a", 3, GM_X["XQ1a"], GM_Y)
XQ1b = mkhbt("XQ1b", 3, GM_X["XQ1b"], GM_Y)
XQ2b = mkhbt("XQ2b", 3, GM_X["XQ2b"], GM_Y)
XQ2a = mkhbt("XQ2a", 3, GM_X["XQ2a"], GM_Y)
d3L = mkhbt("d3L", 3, CX - 2.5 * GM_COL, GM_Y)
d3R = mkhbt("d3R", 3, CX + 2.5 * GM_COL, GM_Y)

# Re：a 对（ntaila）低一档、b 对（ntailb）高一档 —— 两组 P2 轨 y 不同，才谈得上分层
NOTES = []          # 占位件说明：只进 stdout 与设计稿，不落金属层
RE_A_Y, RE_B_Y = 55.0, 63.0
Re1a = mkres("Re1a", 30, "rsil", GM_X["XQ1a"], RE_A_Y)   # P1=e1a  P2=ntaila
Re2a = mkres("Re2a", 30, "rsil", GM_X["XQ2a"], RE_A_Y)   # P1=e2a  P2=ntaila
Re1b = mkres("Re1b", 30, "rsil", GM_X["XQ1b"], RE_B_Y)   # P1=e1b  P2=ntailb
Re2b = mkres("Re2b", 30, "rsil", GM_X["XQ2b"], RE_B_Y)   # P1=e2b  P2=ntailb

# gm 发射极 E(M2) → Re 的 P1(M1)：M2 竖直下引 + via_stack 落 M1
# ⚠ e1a/e1b/e2a/e2b 是**网表里的独立网**（XQ.E ↔ Re.P1 之间的那一段），
#   漏标 = LVS 取不到网名（自检台 ⑧「网名闭合」当场报漏标）。
for (q, r, enet) in ((XQ1a, Re1a, "e1a"), (XQ2a, Re2a, "e2a"),
                     (XQ1b, Re1b, "e1b"), (XQ2b, Re2b, "e2b")):
    ex, ey = q.p["E"]
    px, py = r.p["P1"]
    b.wire_v("M2", ex, ey, py)            # 竖直下引（E 本就在 M2，层路一致）
    b.via(ex, py)                         # M2 ↔ M1 落到 Re 的 P1
    b.label("M2", ex, (ey + py) / 2, enet)

# NTA 轨 y = **Re 的真实 P2 引脚 y**（不再用 +2.40 硬编码：Q5 真值下 rsil l=2u
# 那一档已不存在——30Ω 落成 l=4.2857，P1→P2 偏移 0.72+0.84·4.2857=4.32µm，
# 沿用旧常数会让尾流轨悬在电阻腰上，⑤b 会判同名分裂/悬空）。
NTA_Y_OLD = {"ntaila": Re1a.p["P2"][1], "ntailb": Re1b.p["P2"][1]}   # v2.0 前口径（仅对照）

# ═══════════════════════════════════════════════════════════════
# 2. 尾流镜像组 ×2 —— **修正 v1.1 的 12 倍错误**
# ═══════════════════════════════════════════════════════════════
MIR_Y = 30.0
# ══════════════════════════════════════════════════════════════════════
# v3.4（2026-10-19 · **XBI1 组器件 Activ 重叠根修**，裁定五十六 §四 甲案）
# ══════════════════════════════════════════════════════════════════════
# 病灶（官方 KLayout 精确布尔，裁定五十六 §三·4；我用 gdstk+shapely 独立复现，数值逐位相同）：
#   XBI1 组 Qr(Nx=1, 中心 −32.000) 与 Qo(Nx=10, 中心 −20.000) 的 **Activ 重叠**
#   （x 向重叠长度 **−2.6250 µm**；真交集面积 **2.8650 µm²** / 4 片 / 填充率 16.27%
#    —— 裁定五十五回信 §二 定谳：裁定五十六原文「2.6250 µm²」是量纲错，组长已自纠；
#    我首版探针同报 2.6250 但成因是口径错（只取各自最大一块域），probe v2 已修）。
#   两块 Activ 各自搭着两条轨的 Cont ⇒ 提取器把
#   `XBI1/nref` 与 `ntaila` 并成一个网。镜像的 XBI2 组同类净距 **+10.725µm**、官方提取分网 ✓。
#   ⇒ 病灶是**摆位参数**问题：QR_L=12.0 与 QR_R=25.35 不对称，是全板唯一的镜像例外。
# 修（单一动作）：
#   **QR_L / QR_R 并成一个 QR_OFF=25.35**，两侧完全镜像 ⇒ XBI1 的 Activ 净距变成
#   +10.725µm，与 XBI2 **逐位同构**，而那正是本面已被官方 DRC 判过的几何。
#   依赖链：qr_x / rf_x / nref 走线 / cb_tie 逃逸列 / nvtop 出脚全部随参数联动
#   （gen_mirror_group 内一律用器件**自报引脚坐标**，无手抄坐标）。
# ⚠ 为什么不用「最小位移」（14.625+0.63=15.255 就够）：
#   PDK 的 Activ 适用净距**本机查不到**（/data/pdk 不在，.lyt/drc deck 都没有）。
#   与其赌一个查不到的值，不如取**与 XBI2 完全相同的几何**——那一面零 Activ DRC 条目。
#   这就是本轮选型的理由，写在文件里备审（裁定五十六 §四·1「最终值必须过 DRC 的 Activ 净距」）。
QR_OFF, RF_OFF = 25.35, 8.0          # Qr 相对 Qo 的横向偏移（两侧同一值 = 真镜像）
# ⚠ v2.9（2026-10-18）：QR_L 8.7→12.0 —— XBI1 镜参考网(ntaila 侧)与尾轨 M1 真短根修。
#   根因（真 GDS m2_mix_v29.gds 连通域分析实锤，分量 M1[6] area=49.18µm² 同时携带
#   XBI1/nref 与 ntaila 两枚标签；fde9 facediff_v34 静态对照独立发现，交叉印证）：
#   npn13G2 的 C/B 带金属是**横跨全管宽的长条**（NX=10 实测 C 带 x∈[gx−9.25,gx+9.25]
#   w=18.5、B 带 x∈[gx−9.30,gx+9.30] w=18.6，中心=锚 x；来源：真 GDS 分量 6 原始多边形）。
#   旧 QR_L=8.7 < B 带半宽 9.30 ⇒ XQr(NX=1) 整个管体落在 XQo(NX=10) 的 C/B 带金属投影
#   内（XQr 管带 x∈[−29.68,−27.72] vs XQo B 带 x∈[−29.30,−10.70]，同层重叠）⇒
#   C_o=C_r、B_o=B_r，叠加 cb_tie 的 C_r=B_r ⇒ XQo 被接成二极管 ⇒ ntaila 尾源从
#   高阻电流镜塌成低阻二极管对（pex_mix_v27.cdl L25-26 Q7/Q8 C=B=ntaila 的来历）。
#   XBI2 侧 QR_R=25.35 ≫ 9.30+0.98 无此问题（M1[67] XBI2/nref 独立 19.77µm² 可证）。
#   新 QR_L=12.0：XQr 管带左缘 = gx−12−0.98，距 XQo B 带左端 gx−9.30 净空 1.72µm
#   （≥M1 同层净距 0.63 富余）。断言见下方 _qr_l_assert。
def _qr_l_assert():
    """自证：QR_OFF ≥ XQo B 带半宽 + XQr 管带半宽 + **自设保守间距 0.63**。
    ⚠ 数值真值入口唯一（裁定四十六 §五）：带半宽与间距都从 sow6/hbtgeom.py 取，
    不在本文件里另抄一份（2026-10-18 前的硬编码 9.30/0.98/0.63 就是"口径各写一份"
    的隐患：真值表一改，这里会静默留着旧数）。按**路径**加载，避开同名模块串味
    （phys/top 下也有 hbtgeom 系文件）；取不到则回落到同值常量并明确告警。
    ⚠ 0.63 = **自设保守项**（我的摆位裕度），PDK 适用值是 M1.b 0.18 —— 两者不可混写。"""
    _fallback = (9.30, 0.98, 0.63)
    _src = "sow6/hbtgeom.py"
    try:
        import importlib.util as _ilu
        _sp = _ilu.spec_from_file_location(
            "sow6_hbtgeom_truth", os.path.join(_HERE, "hbtgeom.py"))
        _hg = _ilu.module_from_spec(_sp)
        _sp.loader.exec_module(_hg)
        _b_half, _qr_half = _hg.band_half(10)[0], _hg.band_half(1)[0]
        _sp_v = _hg.M1_PLACING_SPACING_UM
    except Exception:                      # 取不到就回落，**但明确告警**
        _b_half, _qr_half, _sp_v = _fallback
        _src = "**回落常量**（未取到 sow6/hbtgeom.py）"
    # 断言写在 try 之外：绝不能让 except 顺手把真断言吞掉（那是最坏的一种静默）
    # v3.4：QR_L/QR_R 并成 QR_OFF（M1 带内缘这项它仍然要管，只是不再分左右）
    assert QR_OFF >= _b_half + _qr_half + _sp_v, \
        f"QR_OFF={QR_OFF} 不足：需 ≥ {_b_half}+{_qr_half}+{_sp_v}={_b_half+_qr_half+_sp_v}（XBI1 镜组真短根修律）"
    print(f"[_qr_l_assert] 触发 PASS：QR_OFF={QR_OFF} ≥ B带半宽{_b_half}+XQr带半宽{_qr_half}"
          f"+自设保守间距{_sp_v}={_b_half+_qr_half+_sp_v:.2f}"
          f"（内缘净空 {QR_OFF - _b_half - _qr_half - _sp_v:.2f}µm，真值源 {_src}）",
          flush=True)

_qr_l_assert()


# ── v3.4（2026-10-19）Activ 足迹净距断言 —— 裁定五十六 §四 甲案的真修守门 ──────────
# 为什么要有这道（QR_L=12.0 失效的同一个教训）：
#   `_qr_l_assert` 只管 **M1 带金属**的内缘净空，而短接发生在**器件 Activ**上。
#   几何层改了、连接层没改 —— 两道断言各管各的层，谁也替代不了谁。
#   故本断言管 Activ 框净距，真值从 **sow6/actgeom.py** 取（官方 GDS 实测的足迹宽度，
#   不是脚本反推、也不是纸面参数）；取不到就**大声失败**，不回落常量。
def _activ_gap_assert():
    _fallback = None                      # 故意不给回落：这一项回落等于没查
    _src = "sow6/actgeom.py"
    try:
        import importlib.util as _ilu
        _sp = _ilu.spec_from_file_location(
            "sow6_actgeom_truth", os.path.join(_HERE, "actgeom.py"))
        _ag = _ilu.module_from_spec(_sp)
        _sp.loader.exec_module(_ag)
    except Exception as _e:
        raise AssertionError(
            f"取不到 {_src}（{_e!r}）——Activ 足迹真值是**官方 GDS 实测**，"
            f"脚本里不留第二份；宁可停在这儿，也不拿猜的值放行") from _e
    # 组内两管的中心距：XQo 在 gx，Xr 在 gx ± QR_OFF
    need = _ag.min_center_gap(10, 1)
    for side, gx in ((-1, CX - 20.0), (+1, CX + 20.0)):
        qr_x = gx + side * QR_OFF
        gap = _ag.frame_gap(gx, 10, qr_x, 1)
        assert gap > 0, (f"XBI{1 if side < 0 else 2} 组 Activ 框**重叠** "
                        f"{gap:+.4f}µm（中心距 {abs(qr_x - gx):.3f} < 许可 {need:.3f}）——"
                        f"裁定五十六 §三·4 的 2.6250µm 就是这么来的")
        assert gap >= _ag.ACTIV_PLACING_SPACING_UM, \
            f"XBI{1 if side < 0 else 2} 组 Activ 净距 {gap:+.4f} < 自设保守项 {_ag.ACTIV_PLACING_SPACING_UM}"
    print(f"[_activ_gap_assert] PASS：QR_OFF={QR_OFF} ⇒ 两组 Activ 框净距均为 "
          f"{_ag.frame_gap(CX - 20.0, 10, CX - 20.0 - QR_OFF, 1):+.4f}µm"
          f"（≥ 自设保守项 {_ag.ACTIV_PLACING_SPACING_UM}；真值源 {_src}，"
          f"许可中心距 ≥ {need:.3f}µm）", flush=True)


_activ_gap_assert()

NVT_X = {}       # pfx → nvtop 顶层短脚的 (x, y)（v2.3：柱前先横插，见函数内注释）

def gen_mirror_group(gx, nout_net, pfx, side=-1):
    """一组 hbt_mirror = Qr(nx=1) + XQo(nx=10) + Rref(680Ω)，**三件，无阵列**。

    side=-1：Qr/Rref 落在 Qo 左侧；side=+1：落在右侧（须让开 Qo 右缘 20µm）。
    nref（M1）：Rref.P2 →(横) Qr.C →(竖) Qr.B →(横) XQo.B
    nout：XQo.C → ntail 轨（ntaila 走 M1 / ntailb 走 M3，见调用处）
    gnd（M4）：两管 E 经两级 via 上地专层
    """
    qo = mkhbt(f"{pfx}_XQo", 10, gx, MIR_Y)
    qr_x = gx + side * QR_OFF        # v3.4：两侧同一偏移 = 真镜像
    rf_x = qr_x + side * RF_OFF
    qr = mkhbt(f"{pfx}_XQr", 1, qr_x, MIR_Y)
    rf = mkres(f"{pfx}_Rref", 680, "rhigh", rf_x, MIR_Y - 16.0)

    # nref = Rref.P2 →(汇到 y_join) Qr.C ↓ Qr.B → XQo.B
    # ⚠ v2.4 勘误（Q5 真值落地实测）：v2.3 这里是「从 Rref.P2 的 y 画一条横线到
    #   Qr.C 的 x，再从 p2y 竖拉到 Qr.B」——它**默认 Rref.P2 高于 Qr.C**。旧口径
    #   Rref 680Ω 按 15Ω/□ 落成 l=45.33µm 长条，P2 在 y≈52.8，确实远高于 Qr.C(31.13)。
    #   Q5 真值下 680Ω 改落 rhigh l=1.0/w=2.0（面积 2µm²，长条 45µm 没有理由），
    #   P2 掉到 y≈15.6 —— **低于 Qr.C**，竖线从 15.6 拉到 27.8 够不到 Qr.C 的脚，
    #   nref 在版图上断成两截：引脚极性检查判「Qr.C 所在分量无标注」。
    #   修法：不再假设相对高低，显式取 y_join = max(p2y, Qr.C.y) + 余量。
    bref_y = qr.p["B"][1]
    cxr, cyr = qr.p["C"]
    p2x, p2y = rf.p["P2"]
    y_join = max(p2y, cyr) + 1.5
    b.wire_v("M1", p2x, p2y, y_join)                                # Rref.P2 ↑ 汇点
    b.wire_h("M1", y_join, min(p2x, cxr), max(p2x, cxr))            # 汇点 → Qr.C 列
    # ── v2.0（2026-10-18）C=B 实连改**绕 E 指列**（真短定谳 #1/#2）────────
    #    旧竖线从 B 带直拉 y_join 必穿 E 指底座（0.4665µm² 同层重叠）。cb_tie
    #    三段折线：B 带心 → 逃逸列(x±1.2，净距 0.70µm) → 上引 → C 列(y_join 高)。
    #    y_join 高度处已有 nref 汇横线（p2x~cxr），逃逸列选在**背离 XQo 一侧**，
    #    落点仍在既有横线覆盖范围内，不新增无主金属。
    CB.cb_tie(b, qr.p["C"], qr.p["B"], tag=f"mix.{pfx}_XQr",
              side=side, e_pad=CB.e_pad_rects(qr.p["B"][0], MIR_Y, 1))
    b.wire_v("M1", cxr, cyr, y_join)     # C 带心 → y_join（**C 带以上无 E 窗**，无害段）
    b.wire_h("M1", bref_y, min(qr.p["B"][0], qo.p["B"][0]),
             max(qr.p["B"][0], qo.p["B"][0]))                        # Qr.B → XQo.B
    b.label("M1", (qr.p["B"][0] + qo.p["B"][0]) / 2, bref_y, hnet(pfx, "nref"))
    b.label("M1", (p2x + cxr) / 2, y_join, hnet(pfx, "nref"))

    # nout = XQo.C → ntail 轨。ntailb 必须分层：ntaila 的 M1 轨在 y=57.4 横跨
    # [CX−30, CX+30]，而 ntailb 的引下点 x=CX+20 正在该区间内，同层必短。
    LAY = "M1" if nout_net == "ntaila" else "M3"
    if LAY != "M1":
        climb(qo.p["C"][0], qo.p["C"][1], "Metal1", LAY)   # 单柱 M1→M3（v2.2 多落一个
        #   M1→M2，两根柱叠在同一坐标 → 上面那根的 M2 焊盘被下面那根判成「无标注金属」）
    b.wire_v(LAY, qo.p["C"][0], qo.p["C"][1], NTA_Y[nout_net])
    b.label(LAY, qo.p["C"][0], qo.p["C"][1] + 2.5, nout_net)

    for d in (qo, qr):                                  # 发射极 → gnd 专层
        ex, ey = d.p["E"]
        # ⚠ npn13G2 的 E 脚与 C/B **同 x**。ntailb 的 M3 立管就沿这个 x（XBI2.XQo.C
        #   引下点 x=CX+20），若在 E 脚正下方落 M2→M4 柱，柱脚压住 ntailb 的 M3
        #   （⑤d keepout 偏紧）。解法同 drv1 v1.1：先在 M2 上外折 4µm 再落柱。
        gx = ex + 4.0 * (1 if ex >= 0 else -1)
        b.wire_h("M2", ey, ex, gx)
        hop(gx, ey, "Metal2")
        b.wire_v(GND_LAYER, gx, ey, GND_RAIL_Y)   # v2.2：一直落到 M4 地轨，不再是孤岛

    p1x, p1y = rf.p["P1"]                               # nvtop = Rref.P1 → 顶层端口
    # ⚠ v2.3 勘误之四：柱直接落在 Rref.P1 正下方 1.2µm（x=±53.35/±36.7）时，
    #   XBI2 那根的 M2 中间层只差 0.05µm 就压上 **M2 guard 环**右边那条。先横插
    #   1.5µm 再落柱，柱与环之间留 1.9µm。
    nx = p1x + 1.5 * (1 if p1x >= 0 else -1)
    b.wire_h("M1", p1y, p1x, nx)
    b.wire_v("M1", nx, p1y, p1y - 1.2)
    climb(nx, p1y - 1.2, "Metal1", NVT_LAYER)
    b.wire_v(NVT_LAYER, nx, p1y - 1.2, p1y - 4.0)
    b.label(NVT_LAYER, nx, p1y - 4.0, "nvtop")
    NVT_X[pfx] = (nx, p1y - 4.0)
    return qo, qr, rf


NTA_LAY = {"ntaila": "M1", "ntailb": "M3"}
# ── v2.0（2026-10-18）：ntaila 轨高改锚 **P2 焊盘真值**（pad-audit 抓获）────────
#   旧 NTA_Y = Re1a.p["P2"][1] = lib 锚点 = RE_A_Y + 0.72+0.84·l。30Ω 落 rsil
#   l=4.2857（长条档）：锚点在盘**下方** 0.236µm（盘 = 锚+[l+0.27, l+0.53]），
#   轨（锚±0.15）顶边距盘底还差 0.086µm ⇒ Re1a/Re2a 的 P2（ntaila）直流断路。
#   修：轨高 = 盘心 = RE_A_Y + l + c（rsil c=0.40，真值表 resgeom 模块头）。
_l_a = [d[3] for d in RES_DEVS if d[0] == "Re1a"][0]
NTA_Y = {"ntaila": RE_A_Y + _l_a + RG.RES_PAD2_C["rsil"],
         "ntailb": Re1b.p["P2"][1]}
print(f"  [pad-truth] ntaila 轨高 {NTA_Y['ntaila']:.3f}（旧锚点 {Re1a.p['P2'][1]:.3f}，"
      f"盘 [{RE_A_Y + _l_a + 0.27:.3f},{RE_A_Y + _l_a + 0.53:.3f}]）", flush=True)
b.wire_h("M1", NTA_Y["ntaila"], Re1a.p["P2"][0], Re2a.p["P2"][0])
# v2.0：锚点→焊盘短竖桩（⑫ 极性检查锚在 lib 标记点上；桩从锚点起、穿过真焊盘、
#   顶到轨 —— 标记盒、焊盘、轨三者一次连通，与 ntailb 的出脚模式同款）
for _r in (Re1a, Re2a):
    b.wire_v("M1", _r.p["P2"][0], _r.p["P2"][1], NTA_Y["ntaila"])
# ── v2.3 路由返工 ②：ntailb 的 M1→M3 柱**先向上出脚再横插 5µm**。
#   v2.2 把柱直接落在 Re1b/Re2b.P2 正下方 1.2µm 处（∓10, 64.2），而 e1b/e2b 的 M2
#   竖引正好在同一列从 y=63 一路到 85 → 柱的中间层 M2 压着异网金属（⑤d 2 处 FAIL）。
#   柱挪到 (∓5, 68.0)：那里 M2 空（M1 插头与 e 网竖线不同层）。
NTA_B_PILLAR_Y = 68.0
for r in (Re1b, Re2b):
    p2x, p2y = r.p["P2"]
    chx = p2x + 5.0 * (1 if p2x < 0 else -1)      # 向**岛心**插 5µm（必须在 M3 轨跨度内）
    b.wire_v("M1", p2x, p2y, NTA_B_PILLAR_Y)
    b.wire_h("M1", NTA_B_PILLAR_Y, p2x, chx)
    climb(chx, NTA_B_PILLAR_Y, "Metal1", NTA_LAY["ntailb"])
    b.wire_v(NTA_LAY["ntailb"], chx, NTA_B_PILLAR_Y, NTA_Y["ntailb"])
    b.label("M1", chx, NTA_B_PILLAR_Y, "ntailb")   # M1 插头上也标（否则该簇无网名）
b.wire_h(NTA_LAY["ntailb"], NTA_Y["ntailb"], Re1b.p["P2"][0], Re2b.p["P2"][0])
for r, net in ((Re1a, "ntaila"), (Re2a, "ntaila"),
               (Re1b, "ntailb"), (Re2b, "ntailb")):
    # v2.0：ntaila 的标落**轨高**（焊盘真值心）——锚点已不在金属上（轨已上移让盘）
    _ly = NTA_Y["ntaila"] if net == "ntaila" else r.p["P2"][1]
    b.label(NTA_LAY[net], r.p["P2"][0], _ly, net)

gen_mirror_group(CX - 20.0, "ntaila", "XBI1", side=-1)
gen_mirror_group(CX + 20.0, "ntailb", "XBI2", side=+1)

# ── v2.2 补线：两处「差一口气没接上」────────────────────────────────────
# ⑥ ntailb 的 M3 轨延到 XBI2.XQo.C 的引下点（v2.0 只拉到 CX+10，差 10µm 断着）
b.wire_h(NTA_LAY["ntailb"], NTA_Y["ntailb"], Re1b.p["P2"][0],
         b.devs["XBI2_XQo"].p["C"][0])
# ⑦ nvtop 两根短脚之间补 TOPM2 横连（v2.0 两根各自成岛）
# ⚠ v2.7 ①：横轨两端**外延** 1.0µm（＝TOPM2 半宽）到短脚的外缘 —— 原写法端点 = 短脚中心
#   ⇒ 半搭接，并集多出 1.0µm 宽的凸出小舌 < TM2.a 的 2.0µm（官方 v25 轮 TM2.a×8 逐条坐标：
#   (-38.2,9.268~10)|(-37.2,11.732~11)、(55.582,10)|(53.118,11) 两处）。逐矩形量全绿。
b.wire_h(NVT_LAYER, NVT_X["XBI1"][1], NVT_X["XBI1"][0] - 1.0, NVT_X["XBI2"][0] + 1.0)

# ═══════════════════════════════════════════════════════════════
# 3. 开关对 quad（nx=6）+ Rd（10Ω）
# ═══════════════════════════════════════════════════════════════
UNIT6_W = 1.85 * 6 + 4.85      # 15.95
QUAD_COL = UNIT6_W + 4.0       # 19.95
QUAD_ROW = HBT_H + 3.0         # 10.11
QX = QUAD_COL / 2
Q1_Y = 118.0                   # 下排（XQ5/XQ6）
Q0_Y = Q1_Y + QUAD_ROW         # 上排（XQ3/XQ4）

XQ3 = mkhbt("XQ3", 6, CX - QX, Q0_Y)   # rfop lopd nswa
XQ4 = mkhbt("XQ4", 6, CX + QX, Q0_Y)   # rfon lond nswa
XQ5 = mkhbt("XQ5", 6, CX + QX, Q1_Y)   # rfon lopd nswb
XQ6 = mkhbt("XQ6", 6, CX - QX, Q1_Y)   # rfop lond nswb

RD_Y = Q0_Y + 0.5 * HBT_H + 5.0
# Rd 外移 12µm：落在 quad 的**集电极列**正上方时，P1/P2 与 rfop/rfon 的竖引同列 → 必短
RD_XL, RD_XR = CX - QX - 12.0, CX + QX + 12.0
Rd1 = mkres("Rd1", 10, "rsil", RD_XL, RD_Y)    # P1=lopd P2=lop
Rd2 = mkres("Rd2", 10, "rsil", RD_XR, RD_Y)    # P1=lond P2=lon

# ══════════════════════════════════════════════════════════════════════
# v2.3 路由返工：**每根引脚先外折到专属通道，再上高金属层**
# ──────────────────────────────────────────────────────────────────────
# 病根一句话：npn13G2 的 C/B/E **同 x**（C y+1.13 / B y−1.14 / E 居中）。
# 只要某条网的竖直干路还走在这个 x 上，它就必然竖穿同器件的另外两只脚 ——
# 轻则过孔柱压住异网金属（⑤d），重则 M1/M2 直接短接（⑤c）。v2.2 的 15 处 FAIL
# **全部**是这一类，无一例外。故本版给三类脚各划一条专属通道：
#
#   集电极 C → 向**岛外**外折到 x=∓15（M1），rfop/rfon 的竖轨改走那里；
#   基极   B → 向**岛心**内折到各自通道（M1 插头），lopd/lond 的立管改走那里；
#   发射极 E → 已经在 M2 上（e 网/nsw 网），保持不动。
#
# 三条通道互不同 x，且 C/B 的插头都在 M1、E 的干路在 M2 → 层与 x 双重错开。
ESC_RF = 16.2                       # rfop/rfon 竖轨通道（Rd 竖条 ∓21.975 让开 5.775µm）
# ── v2.0（2026-10-18）15 → 16.2（E 窗审计抓获的真短，清单外）──────────────
#   旧 ∓15 正好落在 XQ3/XQ4（Nx=6，锚 ∓9.975）的**带列**里：B 带全局
#   x[−15.575,−4.375] ⇒ M1 竖轨从 Q1 排 C 高度直上 Y_RF 必横穿 B 带（rfop↔lopd
#   真短，真 GDS + pex 42 域并域互证）；且削进最外指 E 窗 0.10µm（rfop↔nsw/a 真短）。
#   16.2 处：竖轨右沿 −16.05，距 B 带左沿 −15.575 净距 0.475µm ≥ M1.b 0.18 ✓，
#   距 E 窗 1.1µm ✓。Ct 端子/TOPM1 竖轨/M1↔TM1 柱随本参数联动；M5 地线横段
#   本来就跨 x −35~−15 一段，外延 1.2µm 不进任何新板区。
ESC_B = {"XQ3": CX - 3.0, "XQ4": CX + 3.0,          # lopd / lond 四个立管专属通道
         "XQ5": CX + 6.0, "XQ6": CX - 6.0}

BASE_RAIL_Y = min(d.p["B"][1] for d in (XQ3, XQ4, XQ5, XQ6)) - 3.0
# ⚠ v2.3 勘误之二：**Rd1/Rd2 两端接反了**。网表 `Rd1 lop lopd 10` → P1=lop、P2=lopd；
#   v2.2 把 lopd 的 M3 立管接在 P1、把 'lop' 标注画在 P2 的 M1 短脚上 → 版图上叫
#   "lop" 的那条网其实是网表的 lopd。自检台第⑦项只比「该器件涉及的两条网的集合」，
#   **不比 pin 次序**，于是 P1/P2 上下颠倒照样 PASS。现已改回，并把次序核对补进自检台。
for net, LAY, rd, qlist in (("lopd", LOPD_LAYER, Rd1, (XQ3, XQ5)),
                            ("lond", LOND_LAYER, Rd2, (XQ4, XQ6))):
    p2x, p2y = rd.p["P2"]                           # 内口 = P2（上端）
    climb(p2x, p2y, "Metal1", LAY)                  # Rd 内口柱（在电阻自己的 x 上）
    b.wire_v(LAY, p2x, p2y, BASE_RAIL_Y)
    b.label(LAY, p2x, p2y, net)
    chs = []
    for d in qlist:
        bx, by = d.p["B"]
        ch = ESC_B[d.name]
        b.wire_h("M1", by, min(bx, ch), max(bx, ch))          # M1 插头（e 网在 M2，横穿无碍）
        climb(ch, by, "Metal1", LAY)                          # 柱只落在专属通道上
        b.wire_v(LAY, ch, by, BASE_RAIL_Y)
        b.label("M1", bx, by, net)
        chs.append(ch)
    b.wire_h(LAY, BASE_RAIL_Y, min(p2x, min(chs)), max(p2x, max(chs)))

# Rd 外口（lop/lon）= **P1**（下端）→ 直接向下出岛。
#   v2.2 从 P2 向下出岛 6µm，那条 M1 短脚正好从 P1 的过孔柱头上压过去，
#   ⑤c 判 ['lop'] vs ['lopd'] 跨层短接。改正极性后 P1 在下，向下即出岛，柱在 P2，互不干涉。
for rd, net in ((Rd1, "lop"), (Rd2, "lon")):
    p1x, p1y = rd.p["P1"]
    b.wire_v("M1", p1x, p1y, p1y - 6.0)
    b.label("M1", p1x, p1y - 6.0, net)


# ═══════════════════════════════════════════════════════════════
# 4. 发射极汇流 nswa / nswb（M2）→ via 落 gm 集电极轨（M1）
# ═══════════════════════════════════════════════════════════════
NSW_Y = {"nswa": Q0_Y - 4.0, "nswb": Q1_Y - 4.0}
# 传输点必须落在**各自 gm 集电极轨的 x 区间内**，否则竖引横穿另一条轨 → 短路。
NSW_TP = {"nswa": CX - 20.0, "nswb": CX + 20.0}
for devs_, net in (([XQ3, XQ4], "nswa"), ([XQ5, XQ6], "nswb")):
    eps = [d.p["E"] for d in devs_]
    ry, tp_x = NSW_Y[net], NSW_TP[net]
    for (ex, ey) in eps:
        b.wire_v("M2", ex, ey, ry)
    b.wire_h("M2", ry, min(min(e[0] for e in eps), tp_x),
             max(max(e[0] for e in eps), tp_x))
    b.via(tp_x, ry)
    b.label("M2", tp_x, ry, net)

for net, (qa, qb) in (("nswa", (XQ1a, XQ1b)), ("nswb", (XQ2b, XQ2a))):
    cpts = [qa.p["C"], qb.p["C"]]
    ry = max(p[1] for p in cpts) + 3.0
    tx = NSW_TP[net]
    for (cx_, cy_) in cpts:
        b.wire_v("M1", cx_, cy_, ry)
    b.wire_h("M1", ry, min(min(p[0] for p in cpts), tx), max(max(p[0] for p in cpts), tx))
    b.wire_v("M1", tx, ry, NSW_Y[net])
    b.label("M1", tx, ry, net)

# ═══════════════════════════════════════════════════════════════
# 5. gm 基极四网 → 2k 偏置电阻：**插列排布**是平面无交叉的关键
#    网表：Rba1 na1p nbiasL / Rba2 na2n nbiasH / Rbb1 nb1p nbiasH / Rbb2 nb2n nbiasL
#    四个源端（gm 基极）同 y、四个汇端（竖条 P1）同 y：任何**同序**排布在平面上
#    必交叉。唯一无交叉解是让汇端 x 插在源端 x 之间（X_res,i ∈ (X_gm,i, X_gm,i+1)），
#    于是「短竖段 + 一条 y 带横轨」互不穿越。GM_COL 因此从 12.4 放大到 20。
# ═══════════════════════════════════════════════════════════════
RB_Y = 235.0                   # 2k 竖条 P1（底端）y
# ⚠ v2.3 勘误：v2.2 的 `RB_H = 0.72 + 0.84*res_params(...)["_geom"][0]` **算错了** ——
#   _geom[0] 已经是「算式求出的长度」(112.69)，再套一次 0.72+0.84·L 得 95.38，
#   而 PCell 真实 P2 高度 = 0.72+0.84·**133.3** = 112.69。于是 nbiasH/nbiasL 的
#   TOPM1/TOPM2 立管从 y=330.38（电阻腰上）起，**够不到 P2 引脚 (347.692)** ——
#   两条偏置网在版图上是断的。⑤b「同名分裂」看不见（每条网只标了一个名字）。
#   本版一律用 `res.p["P2"][1]` 真引脚 y，不再用算式推。
RBA_X = {"Rba1": CX - 20.0, "Rbb1": CX + 0.0, "Rbb2": CX + 20.0, "Rba2": CX + 35.0}
BASE_MAP = (("XQ1a", "Rba1", "na1p"), ("XQ1b", "Rbb1", "nb1p"),
            ("XQ2b", "Rbb2", "nb2n"), ("XQ2a", "Rba2", "na2n"))
QB = {"XQ1a": XQ1a, "XQ1b": XQ1b, "XQ2b": XQ2b, "XQ2a": XQ2a}
RES2K = {}

for qn, rn, net in BASE_MAP:
    q = QB[qn]
    RES2K[rn] = mkres(rn, 2000, "rhigh", RBA_X[rn], RB_Y)
    by, bx = q.p["B"][1], q.p["B"][0]
    rx = RBA_X[rn]
    # ── v2.3 路由返工 ①：B 脚先在 **M1 上插头**到专属竖管通道，过孔柱只落在通道上。
    #   v2.2 把柱直接压在 B 脚（x=∓10/±30），而发射极竖线 e1a/e1b/e2a/e2b 也在
    #   同一列的 **M2** 上从 y=55 一路到 85 → 柱的中间层正压着异网金属
    #   （自检台 ⑤d 抓出 4 处）。插头走 M1、与 e 网竖线（M2）不同层，横穿无碍；
    #   柱脚落在 RBA_X（= 竖条自己的 x），M2/M3/M4/M5 在那里全空。
    b.wire_h("M1", by, min(bx, rx), max(bx, rx))
    climb(rx, by, "Metal1", GMB_LAYER)
    b.wire_v(GMB_LAYER, rx, by, RB_Y)
    b.label(GMB_LAYER, rx, RB_Y, net)
    b.label("M1", bx, by, net)                       # B 脚上也标（LVS 取名双保险）
    # 竖条两端是 M1 引脚 → 必须有 M1 金属 + 过孔相接，否则 LVS 判悬空
    # （下端这根柱 v2.3 首版被我改漏了，自检台新增的「⑫ 引脚极性」当场抓出来：
    #   Rba1.P1 所在连通分量「无标注」= 竖条底端根本没接上 na1p）
    b.wire_v("M1", rx, RB_Y, RB_Y - 1.2)
    climb(rx, RB_Y - 1.2, "Metal1", GMB_LAYER)
    p2y = RES2K[rn].p["P2"][1]                       # 真引脚，不是算式
    b.wire_v("M1", rx, p2y, p2y + 1.2)

RB_TOP = max(r.p["P2"][1] for r in RES2K.values())
# ⚠ v2.5 新增的硬约束（顶层加宽的**副作用**，不处理就是白改）：
#   顶层最小宽 1.64µm 之后，「细线直接压在电阻引脚上」的老写法自造间距违规 ——
#   2k 电阻 P1→P2 只有 0.72+0.84·l = **1.955µm**，两条 1.64µm 宽的顶层线各占 ±0.82，
#   净距只剩 1.955−1.64 = **0.315µm**，而 TM1.b/TM2.b 要 1.64。
#   （0.30µm 细线时净距 1.655µm 刚好合规 —— 顶层加宽把「宽度违规」换成了「间距违规」。）
#   改法：**偏置轨先在 M1 上离电阻远了再上顶层**。M1 与顶层不共面规则；M1 那段仍
#   0.30µm 宽，与 GMB 的 M1 插头净距 1.655µm ≥ M1.b 的 0.18。
BIAS_JUMP = 6.0                                   # P2 引脚之上留多少再上顶层
BIAS_Y = RB_TOP + BIAS_JUMP + 12.0
# ⚠ v2.7 ①：nbiasH 横轨两端**外延** 0.82µm（＝TOPM1 半宽）到两条竖条的外缘 ——
#   原写法 `wire_h(BIASH_LAYER, BIAS_Y, RBA_X["Rbb1"], RBA_X["Rba2"])` 的端点正好落在
#   竖条中心（竖条宽 1.64 = TM1 最小宽）⇒ 半搭接：并集留下相距 0.82µm 的相向平行边，
#   官方 v25 轮报 TM1.a×4（逐条坐标 (1.42,254.21;0.82,254.21)|(-0.6,255.03;0,255.03)
#   与镜像组 @34.18）。**⑯ 逐矩形量全绿**（两条各自都恰好 1.64），是新加的 ⑳ 项抓到的。
b.wire_h(BIASH_LAYER, BIAS_Y, RBA_X["Rbb1"] - MINW["TOPM1"] / 2,
         RBA_X["Rba2"] + MINW["TOPM1"] / 2)                          # nbiasH
for rn in ("Rbb1", "Rba2"):
    p2y = RES2K[rn].p["P2"][1]
    jy = _q(p2y + BIAS_JUMP)
    b.wire_v("M1", RBA_X[rn], p2y, jy)            # ← M1 先拉高（关键一步）
    climb(RBA_X[rn], jy, "Metal1", BIASH_LAYER)
    b.wire_v(BIASH_LAYER, RBA_X[rn], jy, BIAS_Y)
    b.label("M1", RBA_X[rn], jy, "nbiasH")
b.label(BIASH_LAYER, RBA_X["Rbb1"], BIAS_Y, "nbiasH")
BIASL_Y = BIAS_Y + 10.0
# ⚠ v2.7 ①：nbiasL 同样外延 1.0µm（＝TOPM2 半宽）；官方 v25 轮 TM2.a×8 的另两处逐条坐标
#   正是这一对竖条（(-19,264.03)|(-20,265.03) 与镜像 (19,263.298)|(20,265.762)）。
b.wire_h(BIASL_LAYER, BIASL_Y, RBA_X["Rba1"] - MINW["TOPM2"] / 2,
         RBA_X["Rbb2"] + MINW["TOPM2"] / 2)                          # nbiasL
for rn in ("Rba1", "Rbb2"):
    p2y = RES2K[rn].p["P2"][1]
    jy = _q(p2y + BIAS_JUMP)
    b.wire_v("M1", RBA_X[rn], p2y, jy)
    climb(RBA_X[rn], jy, "Metal1", BIASL_LAYER)
    b.wire_v(BIASL_LAYER, RBA_X[rn], jy, BIASL_Y)
    b.label("M1", RBA_X[rn], jy, "nbiasL")
b.label(BIASL_LAYER, RBA_X["Rba1"], BIASL_Y, "nbiasL")

# ═══════════════════════════════════════════════════════════════
# 6. IF 输入：Rb1/Rb2（2k → nifbias）+ 四只 1n 耦合电容**端子锚定落线**（v2.5）
# ═══════════════════════════════════════════════════════════════
IF_Y = 6.0
BIAS_NET = {"Rba1": "na1p", "Rbb1": "nb1p", "Rbb2": "nb2n", "Rba2": "na2n"}
# 2k 竖条高 113µm，摆在 gm 块**左侧之外**（d3L 盒左缘 CX−53.35）。
# ⚠ v2.3 勘误之三：Rb1 原在 x=−74，其 M1→M3 柱的 M2 中间层正压在 **M2 guard 环**
#   左边那条上（环占 x∈[−75.35,−71.35]）——柱脚踩环 = 与环那条网短接，而环**无标注**，
#   自检台只能报「无标注金属」无法定性。内移 4µm 到 x=−70 让柱完全出环。
Rb1 = mkres("Rb1", 2000, "rhigh", CX - 70.0, IF_Y)   # P1=ifp  P2=nifbias
Rb2 = mkres("Rb2", 2000, "rhigh", CX - 66.0, IF_Y)   # P1=ifn  P2=nifbias
NIF_Y = max(Rb1.p["P2"][1], Rb2.p["P2"][1]) + 14.0     # 真引脚顶上 14µm
for r in (Rb1, Rb2):
    p2x, p2y = r.p["P2"]
    b.wire_v("M1", p2x, p2y, p2y - 1.2)
    climb(p2x, p2y - 1.2, "Metal1", NIFB_LAYER)
    b.wire_v(NIFB_LAYER, p2x, p2y - 1.2, NIF_Y)
b.wire_h(NIFB_LAYER, NIF_Y, Rb1.p["P2"][0], Rb2.p["P2"][0])
b.label(NIFB_LAYER, Rb1.p["P2"][0], NIF_Y, "nifbias")
for r, net in ((Rb1, "ifp"), (Rb2, "ifn")):
    p1x, p1y = r.p["P1"]
    b.wire_v("M1", p1x, p1y, p1y - 4.0)
    b.label("M1", p1x, p1y - 4.0, net)

# ── v2.5 四只耦合电容：**端子锚定**（纪要 §3.2/§3.3 的 PDK 真值落线）──────────
# cmim 两端同心于 cell 局部 (11.83,11.83) ⇒ 顶层端子 = 摆放点 + (11.83,11.83)。
# 于是「把摆放点挪到 (通道x − 11.83, 端子y − 11.83)」就让 **TopMetal1.pin 正好落在
# 那条偏置通道上** —— 零额外走线、零短接可能、零拓扑改动。这是本轮最省事的一处落法：
# 起初想的是「给四只各画一段顶层引线」，画到第三只才发现四块 23.66µm 的板在 20µm 的
# 通道节距下**必然互相压**（板心距 < 板宽 = 同层短接）—— 于是反过来用摆放自由度解掉。
#
# 端子 y 取值受**四条**约束同时卡住（缺一条就是一处真违规，规则值全部来自纪要 §4.2）：
#   ① 必须落在通道 y 跨度内（GMB 立管 83.04~235.82），否则要另加顶层走线；
#   ② 同层两块 23.66µm 板心距 ≥ 23.66+1.64 = **25.30µm** ⇒ x 有交叠的两只用 y 错开 26；
#      （v3.0：w 缩至 23.610 后此约束更松（25.25µm）；上板 TOPM1 22.68 零变化，
#       26 错开维持——摆位不动，间距余量只增不减）
#   ③ cmim 的 **M5 板**（承载 if/ifn）不得压到 M5 上的 lond 干路（x∈[−3,6], y∈[123.8,127]）：
#      端子 x=0 那只的板 x∈[−12.13,12.13] 正压它 ⇒ 其 y 必须挪出 [111.67,139.13]；
#   ④ 旁路电容 rfop/rfon 的 TopMetal1 立管走 x=∓15（与通道净距 3.36µm），立管顶边
#      165.485 ⇒ 板底边须 ≥167.13 ⇒ 端子 y ≥ **179.26**。
#   180 / 180 / 206 / 206 同时满足 ①②③④。
CMIM_PIN_Y = {"Rba1": 180.0, "Rbb2": 180.0, "Rbb1": 206.0, "Rba2": 206.0}
for (nm, ifnet, chan) in (("Cca1", "ifp", "Rba1"), ("Ccb2", "ifn", "Rbb2"),
                          ("Ccb1", "ifp", "Rbb1"), ("Cca2", "ifn", "Rba2")):
    _px, _py = _q(RBA_X[chan]), _q(CMIM_PIN_Y[chan])
    # v2.6：mkcmim 的 target 就是**顶层端子坐标**（库按 bbox 中心锚点，端子=中心），
    # 不再由我算「摆放点 = 端子 − 局部引脚偏移」。
    _ok, _pin = mkcmim(nm, ifnet, BIAS_NET[chan], _px, _py)
    if _ok and _pin is not None:
        # 端子已落在偏置通道上 → 只补一个「同网双保险」标注，**不画线**（画了等于
        # 多一对同层图形去挤 1.64µm 间距，纯亏）。
        b.label(GMB_LAYER, _px, _py, BIAS_NET[chan])
        continue
    b.rect("M4", _px - 5.0, _py - 5.0, _px + 5.0, _py + 5.0)   # 回落占位（不掐断全链）
    NOTES.append(f"{nm}({ifnet},{BIAS_NET[chan]}) CMIM_PLACEHOLDER @({_px:.1f},{_py:.1f})")

# ── ifp / ifn 的 M5 侧落线（cmim 的 n_lo 端子在 M5.pin 上）────────────────────
# 四只耦合电容的 M5 端子分别在 (−20,180) ifp / (0,206) ifp / (20,180) ifn /
# (35,206) ifn。四块 M5 板与 RF 干路、与彼此的关系已在上面 CMIM_PIN_Y 的①②③④里
# 逐条核过。落法：M5 上把同 if 网的两只串起来，再单柱落 M1 接上 Rb1/Rb2 的 P1 短脚。
#   ifp 走 x=−45（四块板都在它右边，是块真正的空走廊）；ifn 走 x=52（岛右缘之外）。
#   ⚠ 两条 M1 落地线**必须错开 y**（4.0 / 2.0）：同 y 时 ifn 的 M1 横跨 x∈[−66,52]、
#   ifp 的横跨 x∈[−70,−45]，交叠段 x∈[−66,−45] 就是一条真短接。
# ⚠ 第一版（IFP_M1_Y=4.0 / IFN_M1_Y=2.0、IFN_M5_X=52.0）被自检台当场逮到三处真问题，
#   都不是玄学，逐条可复现：
#   ① ifp 的 M1 横轨 y=4 跨 x∈[−70,−45]，**横穿 ifn 的 Rb2.P1 短脚**（x=−66, y∈[2,6]）
#      → 5c 报 ifp/ifn 同簇。两网必须**错开 y**，且都要落在两条引脚桩**下方**（y<2）。
#   ② 两条 M1 落地线同 y 会交叠（x∈[−66,−45]），故 ifp 走 1.0、ifn 走 3.0。
#   ③ ifn 的 M5 走廊 x=52 **压住 nsens 的 M1→TOPM2 过孔柱**（XQs 在 x=52, 柱在
#      (52,121.13)，柱的中间层 M5 焊盘就在那儿）→ 5d 判「过孔柱压异网金属」。
#      走廊改 x=58（XQs 以东、guard 环以西的走廊），M5↔M1 柱同步挪。
IFP_M5_X, IFN_M5_X = -45.0, 58.0
IFP_M1_Y, IFN_M1_Y = 1.0, 3.0
for (net, xm5, ym1, pins, rstub) in (
        ("ifp", IFP_M5_X, IFP_M1_Y, [(-20.0, 180.0), (0.0, 206.0)], Rb1),
        ("ifn", IFN_M5_X, IFN_M1_Y, [(20.0, 180.0), (35.0, 206.0)], Rb2)):
    _y_lo = min(y for (_px_, y) in pins)
    _y_hi = max(y for (_px_, y) in pins) + 4.0      # 先升到最高端子之上再横插
    for (_px_, _py_) in pins:
        _ytop = _y_hi if _py_ == max(y for (_a, y) in pins) else _y_lo
        b.wire_v("M5", _px_, _py_, _ytop)
        b.wire_h("M5", _ytop, _px_, xm5)
    b.wire_v("M5", xm5, _y_lo, _y_hi)
    b.wire_v("M5", xm5, _y_lo, ym1)
    climb(xm5, ym1, "Metal1", "M5")
    b.wire_h("M1", ym1, xm5, rstub.p["P1"][0])
    if net == "ifp":   # ifp 的横轨止于 x=−45，够不到自己的引脚桩，需在桩列竖插
        # ⚠ 竖插**只能到 P1 的 y**（6.0）：再多 0.5µm 就压上 nifbias 的 M1→M3
        # 柱焊盘（y∈[6.44,7.06]），5c 当场报 ifp/nifbias 跨层短路。
        b.wire_v("M1", rstub.p["P1"][0], ym1, rstub.p["P1"][1])
    b.label("M5", xm5, _y_hi, net)

# ═══════════════════════════════════════════════════════════════
# 7. 输出级：RL（45Ω）+ Ct（0.84p 占位）+ rfop/rfon/vcc
#    RL 是两端同 x 的竖直器件，P1(vcc) 与 P2(rfop) 同列：vcc 若直上必与 rfop 的
#    竖引重叠 → 六网同簇短路（v1.1 的教训）。解法：rfop/rfon 轨走 RL **上方**；
#    vcc 先向下出 RL，再外折到 x=CX∓30 的专用通道上引，与 rfop/rfon 的 x 区间不交。
# ═══════════════════════════════════════════════════════════════
RL_Y = RD_Y + 16.0
RL1 = mkres("RL1", 45, "rsil", RD_XL, RL_Y)     # P1=vcc  P2=rfop
RL2 = mkres("RL2", 45, "rsil", RD_XR, RL_Y)     # P1=vcc  P2=rfon
CT_PIN_Y = 60.0      # 旁路电容端子 y —— 四条约束与耦合四只同源（见 CMIM_PIN_Y 注释①②③④）
for (nm, pin_x, net) in (("Ct1", CX - ESC_RF, "rfop"), ("Ct2", CX + ESC_RF, "rfon")):
    _px = _q(pin_x)                  # 端子锚到 rfop/rfon 的竖轨通道 x=∓15 上
    _py = _q(CT_PIN_Y)
    _ok, _pin = mkcmim(nm, "gnd", net, _px, _py)   # n_lo=M5.pin=gnd，n_hi=TOPM1.pin=rfop/rfon
    if _ok and _pin is not None:
        continue
    b.rect("M4", _px - 5.0, _py - 5.0, _px + 5.0, _py + 5.0)
    NOTES.append(f"{nm}(gnd,{net}) CMIM_PLACEHOLDER @({_px:.1f},{_py:.1f})")
# gnd 侧：两只旁路电容的 M5 端子（∓15, 60）串到 x=−35，再单柱 M4↔M5 落进 M4 地轨。
#   落点 (−35, 18) 在地轨矩形 x∈[−54,54], y∈[16,20] 内 ✓；x=−35 这条竖线两侧
#   四块耦合电容的 M5 板都在右边 7µm 外，lond 干路在 −3~6，都在板外 ✓。
for _px_ in (CX - ESC_RF, CX + ESC_RF):
    b.wire_h("M5", CT_PIN_Y, -35.0, _px_)
b.wire_v("M5", -35.0, CT_PIN_Y, GND_RAIL_Y)
b.via(-35.0, GND_RAIL_Y, "Metal4", "Metal5")          # M4 → M5 单柱（climb 只向上，故直调 via）
b.label("M5", -35.0, CT_PIN_Y, "gnd")

Y_RF = RL_Y + 12.0
# ── v2.3 路由返工 ③：集电极竖轨改走**外折通道** x=∓15。
#   v2.2 的 rfop 竖轨直接走 XQ3.C 的 x（=∓9.975），而同一列的 XQ3.B(lopd) 就在
#   y=126.97 → M1 上直接短接（⑤c 判 ['rfop'] vs ['lopd']），且基极过孔柱的 M2
#   中间层压着 nswa/2 处、nswb/2 处（⑤d 4 处）。外折后 C 脚与 B 脚各走各的列。
for devs_, net, ch, rl in (([XQ3, XQ6], "rfop", CX - ESC_RF, RL1),
                           ([XQ4, XQ5], "rfon", CX + ESC_RF, RL2)):
    for (cx_, cy_) in [d.p["C"] for d in devs_]:
        b.wire_h("M1", cy_, cx_, ch)                 # C 脚外折插头
    b.wire_v("M1", ch, min(p[1] for p in [d.p["C"] for d in devs_]), Y_RF)
    b.wire_h("M1", Y_RF, ch, rl.p["P2"][0])
    b.wire_v("M1", rl.p["P2"][0], rl.p["P2"][1], Y_RF)
    b.label("M1", (ch + rl.p["P2"][0]) / 2, Y_RF, net)
    b.label("M1", rl.p["P2"][0], rl.p["P2"][1], net)
    # ── v2.5：旁路电容 Ct 的 **TopMetal1.pin** 端子（x=ch 即本竖轨通道，y=CT_PIN_Y）
    #   落到 rf 网：顶层立管直下到 Y_RF 的 M1 轨，单柱 M1↔TOPM1 收口。
    #   顶层线宽自动取 1.64µm（MINW）⇒ 立管占 x∈[ch±0.82]，与四条偏置通道净距
    #   3.36µm ≥ TM1.b 的 1.64 ✓；顶端 165.485 与耦合电容板底边 168.17 净距 2.685 ✓。
    b.wire_v("TOPM1", ch, CT_PIN_Y, Y_RF)
    # v2.6：显式钉 TopVia1 档 1×1（v2.2 会继承 cols/rows 默认 2×2 → TM1 平台无实测值）。
    # 薄金属堆仍是默认 2×2（v2.2 对它逐位不变）。M5 端平台 = 阵列外沿+0.05/侧（实测规则）。
    b.via(ch, Y_RF, "Metal1", "TopMetal1", vt1_cols=1, vt1_rows=1)
    b.label("TOPM1", ch, CT_PIN_Y, net)

# v2.5：旁路电容端子搬走后，vcc 轨跟着挂在 **CT_PIN_Y** 上（原来挂 CT_Y）——
# CT_Y 那个「摆放 y」已不存在于本版，硬引用会 NameError（第一轮跑就崩在这）。
# vcc 轨的 y 有**硬下界**：M1 横轨不得压到 gm 器件的插头带（y∈[83.71,89.39]）——
# 本轮第一版挂在 CT_PIN_Y+14 = 74.0，正好落在插头带下方，⑤c 当场报 vcc 与
# e/nsw/na 整簇同网、⑬ 报 10 个引脚被异网横穿。上界则是四条 nbias 轨的 M1 立管
# （y∈[236.955,242.955]）与 GMB 插头（y∈[233.8,235]）。取 230 落在窗口正中。
Y_VCC_LO, VCC_Y = RL_Y - 6.0, 230.0
for rl, ch in ((RL1, CX - 30.0), (RL2, CX + 30.0)):
    p1x, p1y = rl.p["P1"]
    b.wire_v("M1", p1x, p1y, Y_VCC_LO)
    b.wire_h("M1", Y_VCC_LO, p1x, ch)
    b.wire_v("M1", ch, Y_VCC_LO, VCC_Y)
b.wire_h("M1", VCC_Y, CX - 30.0, CX + 30.0)
b.label("M1", CX, VCC_Y, "vcc")

# ═══════════════════════════════════════════════════════════════
# 8. Vbe 感测 XQs（c=b=nsens，e=gnd）+ nsens 端口；gm 两端 dummy 接地
# ═══════════════════════════════════════════════════════════════
XQs = mkhbt("XQs", 1, CX + 52.0, Q1_Y)
# ── v2.0（2026-10-18）C=B 实连改绕 E 指列（真短定谳 #3）：旧竖线从 B 带直拉
#    C+2.0 必穿 E 指底座（0.4665µm²）⇒ nsens↔gnd 真短。cb_tie 三段折线绕行，
#    上引高度仍 = C+2.0（climb 落点不动）；逃逸列向右（左侧 5µm 外是 E 回流跨桥）。
CB.cb_tie(b, XQs.p["C"], XQs.p["B"], tag="mix.XQs",
          side=+1, e_pad=CB.e_pad_rects(XQs.p["B"][0], Q1_Y, 1))
b.wire_v("M1", XQs.p["C"][0], XQs.p["C"][1], XQs.p["C"][1] + 2.0)   # C 带心 → climb 落点（C 带以上无害）
climb(XQs.p["C"][0], XQs.p["C"][1] + 2.0, "Metal1", SENS_LAYER)
b.wire_v(SENS_LAYER, XQs.p["C"][0], XQs.p["C"][1] + 2.0, Q1_Y + 40.0)
b.label(SENS_LAYER, XQs.p["C"][0], Q1_Y + 40.0, "nsens")
QS_E_X = XQs.p["E"][0] - 5.0            # 侧向让开 B/C 列
b.wire_h("M2", XQs.p["E"][1], XQs.p["E"][0], QS_E_X)
hop(QS_E_X, XQs.p["E"][1], "Metal2")
b.wire_v(GND_LAYER, QS_E_X, GND_RAIL_Y, XQs.p["E"][1])   # v2.2：落到地轨

DUM_GND_Y = GM_Y - 1.5 * HBT_H - 3.33 - 2.5
# ══════════════════════════════════════════════════════════════════════════
# v3.5（2026-10-19）★M4.b 根修：假管 gnd 立管外移 _DUM_RAIL_DX = 0.100 µm
# ──────────────────────────────────────────────────────────────────────────
# 缺陷（组长裁定六十补充 §〇 归因，我 probe_m4b_b7e7.py 独立复现逐位吻合）：
#   via_stack$2 的 M4 焊盘（XBI1 组管 E 脚 gnd 落柱，disp.x=±49.350、半宽 0.350
#   ⇒ 外边界 ±49.700）与 **d3L/d3R 假管的 gnd 立管**（引脚 x=±50.000、线宽 0.300
#   ⇒ 内边界 ±49.850）之间留出一条 **0.150 µm** 的同域窄缝（notch），
#   < M4.b **0.21**（官方原文 5.17；⚠ 我 drcgeom 表里原写 0.27 是凭同族类推编的错值，
#   已于本轮更正）⇒ 违规，余量 −0.060。
#   v31 只有右侧 1 条；v34 把 XBI1 组镜像到与 XBI2 对称后左侧也落到 ±49.350
#   ⇒ 同样 0.150 ⇒ **2 条**（MIRROR-OF-EXISTING，不是 v34 引入的新缺陷类型）。
# ⚠ 归属更正（我实测，组长 §〇.2 措辞为「顶层自画 M4 轨」——几何与净距全对，
#   但那条**不是轨**）：缝右边界那条立管是 **d3R 假管引脚直落的 gnd 立管**
#   （d3R = mkhbt("d3R", 3, CX + 2.5*GM_COL, GM_Y)，CX=0.0、GM_COL=20.0 ⇒ x=50.000），
#   由下面 3 次 wire_v（C/B/E 三引脚，npn13G2 三脚同 x）画出 **3 段重叠矩形**
#   （y 上界 83.860/84.990/86.240、下界同为 GND_RAIL_Y=18.000）⇒ 并集 = 一条立管。
#   **落码点因此是这 3 处 wire_v 的 x 参数**，不是某条轨的边界常量。
# 修法（组长 §〇.4 (a) 案，我 probe_m4b_fix_b7e7.py 量化）：
#   立管沿 |x| 增大方向外移 δ ⇒ 缝宽 = (49.850+δ) − 49.700。
#   · 最小合规 δ = 0.21 − 0.150 = **0.060**（缝宽恰 = 0.21，**零余量**，不可取）
#   · 连通性上界：立管内边界须 < 上焊盘外边界 50.350 ⇒ δ < 0.500；
#     立管**整条**落在焊盘跨度内（最稳）⇒ δ ≤ 50.350 − 50.150 = **0.200**
#   · **安全窗口 δ ∈ [0.060, 0.200]，取 δ = 0.100**：缝宽 0.250（余量 +0.040 ≈ 19%）、
#     立管 x∈[49.950,50.250] **完全落在**上焊盘跨度 [49.650,50.350] 内（重叠 = 全宽
#     0.300 ⇒ 搭接最稳）、离连通上界还有 0.400。
#   实测（真 v34 GDS 上做同款平移，probe_m4b_fix_b7e7.py §2）：
#     δ=0.100 ⇒ 官方缝 notch **2→0**、M4 域间 space **0→0**、立管-上焊盘同域 **3/3**
#     （地网连通不破）、M4 全域 bounds 不变、立管外边界右侧最近 M4 = via_stack$3
#     @x=51.650 净距 **+1.400** ⇒ **全绿，零副作用**。
# 为什么走 (a) 不走 (b)（(b) = 改 via_stack 落点，即 L771 的 `gx = ex + 4.0`）：
#   (a) 只动 **M4 一层的 3 处 wire_v 调用**（下面循环体，× d3L/d3R 两只 = **6 段立管**）；PCell 实例（d3L/d3R 的 disp）**一字不动**
#       ⇒ 引脚坐标、C/B/E 的 M1 垫、hop 落柱、NET_DECL/DUMMY_NET_DECL 全不变
#       ⇒ **LVS 侧零影响**（配套网表只需改顶层名，拓扑一字不动）；
#       立管长度/宽度不变、纯横向平移 ⇒ **gnd 回流电阻零变化**。
#   (b) 牵动 **M1/M2/M3/M4 四层**（hop→climb 是全栈柱），且 gx 同时决定 L772 的
#       M2 横线终点（实测 x∈[45.350,49.350] 宽 4.000）⇒ 须重验 ⑤d keepout、
#       M2 guard 环净距、⑲ 平台-走线间距、㉑ 落柱两端接上、⑱ 同层间距；
#       且 v34 的镜像动作正是靠 disp.x 参数化的，动 gx 会连带影响 XBI1/XBI2 对称性。
#   ⇒ (a) 副作用面明显更小，且「改一处即同时消两条」（左右对称，一个常量改两侧）。
_DUM_RAIL_DX = 0.100        # µm，假管 gnd 立管外移量（安全窗口 [0.060, 0.200] 的中段）


def _dum_rail_x(px):
    """假管 gnd 立管的 x：沿 |x| 增大方向外移 _DUM_RAIL_DX（左右对称）。
    落 5nm 制造网格（⑰ Offgrid）：0.100 与 50.000 都是 5nm 整数倍 ⇒ 结果 50.100 合规。"""
    return px + _DUM_RAIL_DX * (1 if px >= 0 else -1)


_DUM_RAIL_XS = []           # 自证用：收集实际落图的立管 x
for dd in (d3L, d3R):
    for pk in ("C", "B"):
        hop(dd.p[pk][0], dd.p[pk][1], "Metal1")
        _rx = _dum_rail_x(dd.p[pk][0])
        _DUM_RAIL_XS.append(_rx)
        b.wire_v(GND_LAYER, _rx, GND_RAIL_Y, dd.p[pk][1])
    hop(dd.p["E"][0], dd.p["E"][1], "Metal2")
    _rx = _dum_rail_x(dd.p["E"][0])
    _DUM_RAIL_XS.append(_rx)
    b.wire_v(GND_LAYER, _rx, GND_RAIL_Y, dd.p["E"][1])
# ── v3.5 自证断言（写在 try 之外，绝不让 except 顺手吞掉真断言）──────────────
# 判据：① 立管 x 必须是 ±(50.000+δ)；② 缝宽 = 内边界 − 49.700 ≥ M4.b 0.21 且留余量；
#       ③ 立管整条仍落在上焊盘跨度 [49.650, 50.350] 内（地网连通不破）。
_M4B_UM = 0.21                      # 官方原文 5.17（M2.b/M4.b 共用）
_PAD_OUT = 49.700                   # via_stack$2 M4 焊盘外边界（缝的另一侧）
_UPPAD_IN, _UPPAD_OUT = 49.650, 50.350   # y≈83.5–86.5 三个上焊盘 x 跨度
for _rx in _DUM_RAIL_XS:
    _sgn = 1 if _rx >= 0 else -1
    _in_edge = abs(_rx) - 0.150     # 立管半宽 0.300/2
    _out_edge = abs(_rx) + 0.150
    _seam = _in_edge - _PAD_OUT
    assert abs(abs(_rx) - (50.000 + _DUM_RAIL_DX)) < 1e-9, \
        f"v3.5 立管 x 应为 ±{50.000 + _DUM_RAIL_DX:.3f}，实得 {_rx}"
    assert _seam >= _M4B_UM + 0.020, \
        f"v3.5 M4.b 缝宽 {_seam:.4f} < 门限 {_M4B_UM} + 余量 0.020（立管 x={_rx}）"
    assert _in_edge >= _UPPAD_IN and _out_edge <= _UPPAD_OUT, \
        (f"v3.5 立管 [{_in_edge:.3f},{_out_edge:.3f}] 未整条落在上焊盘跨度 "
         f"[{_UPPAD_IN},{_UPPAD_OUT}] 内 ⇒ 地网连通可能破（立管 x={_rx}）")
    assert abs(_rx * 200 - round(_rx * 200)) < 1e-6, \
        f"v3.5 立管 x={_rx} 不在 5nm 制造网格上（⑰ Offgrid）"
print(f"[v3.5 M4.b 根修] 假管 gnd 立管外移 δ={_DUM_RAIL_DX:.3f}µm ⇒ x={sorted(set(abs(v) for v in _DUM_RAIL_XS))}"
      f"（{len(_DUM_RAIL_XS)} 段，左右各 {len(_DUM_RAIL_XS)//2}）；"
      f"缝宽 {_PAD_OUT}→{50.000 + _DUM_RAIL_DX - 0.150:.3f} = "
      f"{(50.000 + _DUM_RAIL_DX - 0.150) - _PAD_OUT:.4f}µm ≥ M4.b {_M4B_UM}"
      f"（余量 {(50.000 + _DUM_RAIL_DX - 0.150) - _PAD_OUT - _M4B_UM:+.4f}）；"
      f"立管整条落在上焊盘 [{_UPPAD_IN},{_UPPAD_OUT}] 内 ⇒ 地网连通 ✓；"
      f"4 条断言全过（x 值/缝宽余量/焊盘搭接/5nm 网格）", flush=True)
# M4 地轨（v2.2 新增）+ 单一 gnd 标注；上面各处不再各自标 gnd，避免同���分裂误报
b.rect(GND_LAYER, CX - 54.0, GND_RAIL_Y - 2.0, CX + 54.0, GND_RAIL_Y + 2.0)
b.label(GND_LAYER, CX, GND_RAIL_Y, "gnd")

# ═══════════════════════════════════════════════════════════════
# 9. 岛边界自适应（按真实内容反推）+ pad + guard ring
# ═══════════════════════════════════════════════════════════════
CORE_X0, CORE_Y0, CORE_X1, CORE_Y1 = _bb(b.top)      # ← 代跑补丁①：双风格读取
# ⚠ v2.3 勘误之五：guard 环的几何在 v2.0/v2.2 里是错的 ——
#   RING_M=6 而环宽 4，M2 环又用了 inset=ring_w+1=5 → M2 环落在
#   x∈[CORE_X0−1, CORE_X0+3]，**骑在核内容上**（环的 x 范围由核 bbox 定义，
#   所以最外侧那只器件必然被环压住）。实测两处真短：Rb1 的 M1→M3 柱脚
#   整个踩在 M2 环上（x=−74），XBI2 的 nvtop 柱差 0.05µm 压上。
#   修正：环宽收到 2µm、RING_M 提到 8µm，M1 环贴 guard 边、M2 环嵌在其内侧 1µm，
#   两环都在核外（离核 ≥3µm），任何核内过孔柱都不可能再碰到环。
RING_M = 8.0
GUARD_X0, GUARD_Y0 = CORE_X0 - RING_M, CORE_Y0 - RING_M
GUARD_X1, GUARD_Y1 = CORE_X1 + RING_M, CORE_Y1 + RING_M

# ── bondpad：**默认不放进块级岛**（2026-10-17 撤回理由之二）────────────
#   旧版在岛外侧摆两个 80µm octagon pad 并各打一个 PAD_IFP/PAD_IFN 标注，
#   但：① pad 与 ifp/ifn **没有任何连线**（浮空）；② 标注在 TOPM2 金属上，
#   LVS 会把 PAD_IFP 当成网名抽出**网表里不存在的网**；③ pad ring 是顶层拼接的事，
#   摆进块级岛里凭空把岛宽撑大 ~100µm。
#   待组长回执 Q3：若要求块级岛自带 pad，把 PADS_IN_ISLAND 置 True 并补 ifp/ifn 互连。
PADS_IN_ISLAND = False
if PADS_IN_ISLAND:
    PAD_HALF = 40.0
    PAD_Y = (CORE_Y0 + CORE_Y1) / 2
    PAD_X_L = GUARD_X0 - PAD_HALF - 4.0
    PAD_X_R = GUARD_X1 + PAD_HALF + 4.0
    b.bondpad(PAD_X_L, PAD_Y, 80.0, "octagon", name="PAD_IFP")
    b.bondpad(PAD_X_R, PAD_Y, 80.0, "octagon", name="PAD_IFN")
    b.label("TOPM2", PAD_X_L, PAD_Y, "ifp")      # 用**网表网名**，不用 PAD_IFP
    b.label("TOPM2", PAD_X_R, PAD_Y, "ifn")
    # ⚠ 置 True 时必须补 ifp/ifn 到 pad 的 TOPM2 互连，否则仍是浮空 pad（自检台 ⑥ 会报）
# 两 pad 之间不做顶层直连：那会把 ifp/ifn 两条网短在一起（v1.1 教训）。
# 1nF 片外耦合在 CDL 纪律 §3.1 已定为端口化，片上无需互连。

ring_w = 2.0
for (ly_name, inset) in (("M1", 0.0), ("M2", ring_w + 1.0)):
    a0, b0 = GUARD_X0 + inset, GUARD_Y0 + inset
    a1, b1 = GUARD_X1 - inset, GUARD_Y1 - inset
    b.rect(ly_name, a0, b0, a1, b0 + ring_w)
    b.rect(ly_name, a0, b1 - ring_w, a1, b1)
    b.rect(ly_name, a0, b0 + ring_w, a0 + ring_w, b1 - ring_w)
    b.rect(ly_name, a1 - ring_w, b0 + ring_w, a1, b1 - ring_w)

# ══════════════════════════════════════════════════════════════════════
# 9b Q7 裁决落地（reply_v12 §二）—— guard 环定网 + 补 tap
# ══════════════════════════════════════════════════════════════════════
# 先答组长点名要的那道**事实题**：v2.3 这个环是「M1 圈 + M2 圈」的**纯金属环、
# 环上没有任何 tap 接触**（全脚本只有 rect/wire_v，无扩散器件）。所以它按裁决
# 还不算 guard ring，只是一道屏蔽/回流环。裁决三条全部照办：
#   ① 环保留在块级岛内（不删、不上推 M4）；② 不许悬空 → 必须定网；
#   ③ 最简合规 = **ptap 接触 + 标 gnd**（ntap 双环是否升留给 M4 顶层决定）。
# 标注纪律（接 Q4）：datatype=25 的文本**只写网名本身**，写别的即幽灵网。
_ring_cx = (GUARD_X0 + GUARD_X1) / 2
_ring_cy = (GUARD_Y0 + GUARD_Y1) / 2
b.label("M1", _ring_cx, GUARD_Y0 + ring_w / 2, "gnd")          # 下边中点
b.label("M1", _ring_cx, GUARD_Y1 - ring_w / 2, "gnd")          # 上边中点
b.label("M1", GUARD_X0 + ring_w / 2, _ring_cy, "gnd")          # 左边中点
b.label("M1", GUARD_X1 - ring_w / 2, _ring_cy, "gnd")          # 右边中点
# M2 圈与 M1 圈本就是同一圈金属（一圈套一圈），同网再标一次便于 LVS 取名；
# 文本同样是纯网名，不加任何说明字。
b.label("M2", _ring_cx, GUARD_Y0 + ring_w + 1.0 + ring_w / 2, "gnd")
b.label("M2", _ring_cx, GUARD_Y1 - ring_w - 1.0 - ring_w / 2, "gnd")

# ── ptap 接触 ──────────────────────────────────────────────────────────
# ⚠ 真几何**本机无法验证**：这里没有 PDK 也没有 klayout，仿真层不建未知 PCell，
#   ptap 的确切参数名/是否带 M1 端口都无从查证。故三重防护：
#   ① TAP_ENABLE 开关（代跑若嫌多/嫌挤，一个数关掉即可）；
#   ② 参数留空走 PDK 默认（bondpad 的血泪：显式参数 dict 一律创建失败）；
#   ③ 非致命 try —— PDK 若不认 `ptap` 这个名字，只打印 PTAP_SKIPPED 并跳过，
#      **不影响其余全链跑完**（宁可少件不可断链）。
# 数量刻意取少（每边 2 只 = 8 只）：块级岛的衬底噪声主责在顶层 seal/guard，
#   这里只要证明「环不是浮空金属」；真要加密按 DRC 与噪声预算再加。
TAP_ENABLE = True
_tap_xy = []
for _t in (0.3, 0.7):
    _tap_xy += [(GUARD_X0 + _t * (GUARD_X1 - GUARD_X0), GUARD_Y0 + ring_w / 2),
                (GUARD_X0 + _t * (GUARD_X1 - GUARD_X0), GUARD_Y1 - ring_w / 2),
                (GUARD_X0 + ring_w / 2, GUARD_Y0 + _t * (GUARD_Y1 - GUARD_Y0)),
                (GUARD_X1 - ring_w / 2, GUARD_Y0 + _t * (GUARD_Y1 - GUARD_Y0))]
if TAP_ENABLE:
    import pya as _pya
    if hasattr(_pya, "WARN"):        # 仿真层：未知 PCell 会塞 10×10 假体，污染间距判定
        NOTES.append("PTAP_SKIPPED：本机仿真层不建未知 PCell —— ptap1 接触待代跑落")
    else:
        try:
            # ⚠ v2.5：**真名是 ptap1 不是 ptap**（纪要 §二.1，ntap 同理为 ntap1）。
            #   `b._pcell` 里 `assert cell is not None` —— PDK 不认这个名字时
            #   create_cell 返 None，异常被 assert 吞掉、再被我的 except 接住记
            #   PTAP_SKIPPED ⇒ **静默不落图**：上一轮我以为「落了 8 只 ptap」，其实
            #   GDS 里一只都没有。名字错 = 器件凭空消失，而日志里只有一行 SKIPPED。
            _pc = b._pcell("guard_ptap_default", "ptap1", {})
            for (_x, _y) in _tap_xy:
                b.top.insert(_pya.DCellInstArray(_pc, _pya.DTrans(_pya.DVector(_x, _y))))
            print(f"[guard] ptap ×{len(_tap_xy)} 已落环（PDK 默认参数）", flush=True)
        except Exception as _e:
            NOTES.append(f"PTAP_SKIPPED：{type(_e).__name__}: {_e}")

# ── 让「标了 gnd 的环」真的在 gnd 网上（裁决②「不许悬空」的硬要求）──────
# 三件事，缺一件环就还是一块浮空金属：
#   ① M2 内圈 ←M1 外圈：两圈同心但相距 3µm，via 焊盘才 0.3µm，够不着 →
#      先用一段 M1 搭桥把两圈拉到同一处，再落 M1→M2 柱。
#   ② M4 地轨向左延伸到环边。
#   ③ 环 → 地轨单柱（M1→M4）。柱位取 M1 圈中心线：那里 M2/M3 都是空的
#      （M2 内圈在 x 更内侧 3µm），中间层不会压到异网。
_bridge_x = GUARD_X0 + ring_w + 1.0 + ring_w / 2
for _yb in (GUARD_Y0 + ring_w + 1.0 + ring_w / 2, GUARD_Y1 - ring_w - 1.0 - ring_w / 2):
    b.wire_h("M1", _yb, GUARD_X0 + ring_w / 2, _bridge_x)
    b.via(_bridge_x, _yb, "Metal1", "Metal2")
b.rect(GND_LAYER, GUARD_X0 + ring_w / 2 - 1.5, GND_RAIL_Y - 2.0,
       CX + 54.0, GND_RAIL_Y + 2.0)
b.via(GUARD_X0 + ring_w / 2, GND_RAIL_Y, "Metal1", "Metal4")
b.label(GND_LAYER, GUARD_X0 + ring_w / 2, GND_RAIL_Y, "gnd")

ISLAND_X0, ISLAND_Y0, ISLAND_X1, ISLAND_Y1 = _bb(b.top)
ISLAND_W, ISLAND_H = ISLAND_X1 - ISLAND_X0, ISLAND_Y1 - ISLAND_Y0
print(f"[M2 v2.7] 核 bbox=[{CORE_X0:.1f},{CORE_Y0:.1f}~{CORE_X1:.1f},{CORE_Y1:.1f}]"
      f" → 岛 {ISLAND_W:.1f}×{ISLAND_H:.1f} µm", flush=True)

# ═══════════════════════════════════════════════════════════════
# 10. 网表锚 / 逐器件引脚↔网名声明（自检台第⑦项核对）
# ═══════════════════════════════════════════════════════════════
SP_ANCHOR = {"netlist": "/data/workspace/design/chain_top_tb_v015_1.sp",
             "subckt": "gilbert_mix"}
# ⚠ v3.3 维持排除，但**理由已查实并写死**（2026-10-19 实测，原注释只写"占位件"）：
#   ⑦ 的网表锚 SP_ANCHOR = design/chain_top_tb_v015_1.sp :: gilbert_mix，实测**只有 9 只
#   npn13G2**（4 只 gm + XQs + XQ3..XQ6），**既无 d3L/d3R、也无 XBI1/XBI2 镜像组**，
#   且 XQs 的 B/E 写 0（块级网表写 nsens/gnd）⇒ 这是一份**更早的网表视图**。
#   而组长真跑 LVS 用的块级网表 mix_subckt_LVS输入_v2.sp :: TX5G_M2_MIX_V32 有 **15 只**。
#   ⇒ 排除是**锚的局限**，不是声明缺失。v3.3 已把六只脚另行声明（见 DUMMY_NET_DECL），
#   并在 DUMMY_DECL_ASSERT 里拿块级网表逐字回查 —— **声明不再无人回查**。
#   （把 ⑦ 改锚到块级网表 = 一次自检台重构，且会把已收编的 nref/ntaila 命名分歧翻出来，
#    超出本轮范围 ⇒ 只作为**提案**报组长，不自行改。）
DUMMY_DEVICES = {"d3L", "d3R"}

# ── v3.3（2026-10-19）**假管声明网**（裁定五十一 §五② 的升级项，建议非门限）────────
# 升级前：那四条 gnd 补标的依据是「假管 C/B 落 M1 垫 → hop 到 M4 地轨」这句**人工判读**，
#         既不在 NET_DECL 里、也无任何机器可回查的出处 ⇒ 下一轮机械普查必把它当异类再挑一遍。
# 升级后：声明写进脚本，且出处是**网表逐字**——组长 2026-10-18 09:49Z 来信 §二已点名收编：
#         「15Q（含 `QXd3L/QXd3R gnd gnd gnd` **补画**）…37/37 逐器件拓扑+参数全等」。
#         D1-Q 四网位置式 = C B E 衬底 ⇒ d3L/d3R 三端全 gnd，与版图布线
#         （C/B 走 M1 垫 hop→M4 地轨、E 走 M2 竖线 hop→M4 地轨）逐条对得上。
# 单独成表（不并进 NET_DECL）的原因：并进去会让读表的人以为假管也在网表锚里可全量核对，
#         而实际上 ⑦ 的锚**没有**它们（见上）；分列＝声明可见、口径不混。
DUMMY_NET_DECL = {
    "gnd": [("d3L", "C"), ("d3L", "B"), ("d3L", "E"),
            ("d3R", "C"), ("d3R", "B"), ("d3R", "E")],
}

DEV_NETS = {
    "XQ1a": ("nswa", "na1p", "e1a"), "XQ2a": ("nswb", "na2n", "e2a"),
    "XQ1b": ("nswa", "nb1p", "e1b"), "XQ2b": ("nswb", "nb2n", "e2b"),
    "Re1a": ("e1a", "ntaila"), "Re2a": ("e2a", "ntaila"),
    "Re1b": ("e1b", "ntailb"), "Re2b": ("e2b", "ntailb"),
    "XQs": ("nsens", "nsens", "0"),
    "Rba1": ("na1p", "nbiasL"), "Rba2": ("na2n", "nbiasH"),
    "Rbb1": ("nb1p", "nbiasH"), "Rbb2": ("nb2n", "nbiasL"),
    "Rd1": ("lop", "lopd"), "Rd2": ("lon", "lond"),
    "XQ3": ("rfop", "lopd", "nswa"), "XQ4": ("rfon", "lond", "nswa"),
    "XQ5": ("rfon", "lopd", "nswb"), "XQ6": ("rfop", "lond", "nswb"),
    "RL1": ("vcc", "rfop"), "RL2": ("vcc", "rfon"),
    "Rb1": ("ifp", "nifbias"), "Rb2": ("ifn", "nifbias"),
    # 镜像组：网表实例路径 XBI1/XQr → 版图 XBI1_XQr（自检台统一分隔符）
    "XBI1_XQr": (hnet("XBI1", "nref"), hnet("XBI1", "nref"), "0"),
    "XBI1_XQo": ("ntaila", hnet("XBI1", "nref"), "0"),
    "XBI1_Rref": ("nvtop", hnet("XBI1", "nref")),
    "XBI2_XQr": (hnet("XBI2", "nref"), hnet("XBI2", "nref"), "0"),
    "XBI2_XQo": ("ntailb", hnet("XBI2", "nref"), "0"),
    "XBI2_Rref": ("nvtop", hnet("XBI2", "nref")),
    # ── v3.3 假管（占位 HBT）并入声明：三端全接地 ──────────────────────
    # 依据不是「人工判读」，而是**网表逐字**：`QXd3L gnd gnd gnd 0 npn13G2 … $ cdl Q5`
    # 与 `QXd3R gnd gnd gnd 0 npn13G2 … $ cdl Q6`（D1-Q 四网位置式 C B E 衬底）
    # ⇒ 版图侧的声明从此可被自检台 ⑦ 拿网表锚逐字回查（见 v3.3 说明与 DUMMY_DECL_ASSERT）。
    "d3L": ("gnd", "gnd", "gnd"), "d3R": ("gnd", "gnd", "gnd"),
}

NET_DECL = {
    "e1a": [("XQ1a", "E"), ("Re1a", "P1")],
    "e2a": [("XQ2a", "E"), ("Re2a", "P1")],
    "e1b": [("XQ1b", "E"), ("Re1b", "P1")],
    "e2b": [("XQ2b", "E"), ("Re2b", "P1")],
    hnet("XBI1", "nref"): [("XBI1_XQr", "C"), ("XBI1_XQr", "B"),
                           ("XBI1_XQo", "B"), ("XBI1_Rref", "P2")],
    hnet("XBI2", "nref"): [("XBI2_XQr", "C"), ("XBI2_XQr", "B"),
                           ("XBI2_XQo", "B"), ("XBI2_Rref", "P2")],
    "nswa": [("XQ1a", "C"), ("XQ1b", "C"), ("XQ3", "E"), ("XQ4", "E")],
    "nswb": [("XQ2a", "C"), ("XQ2b", "C"), ("XQ5", "E"), ("XQ6", "E")],
    "ntaila": [("Re1a", "P2"), ("Re2a", "P2"), ("XBI1_XQo", "C")],
    "ntailb": [("Re1b", "P2"), ("Re2b", "P2"), ("XBI2_XQo", "C")],
    "lopd": [("Rd1", "P2"), ("XQ3", "B"), ("XQ5", "B")],
    "lond": [("Rd2", "P2"), ("XQ4", "B"), ("XQ6", "B")],
    "na1p": [("XQ1a", "B"), ("Rba1", "P1")],
    "na2n": [("XQ2a", "B"), ("Rba2", "P1")],
    "nb1p": [("XQ1b", "B"), ("Rbb1", "P1")],
    "nb2n": [("XQ2b", "B"), ("Rbb2", "P1")],
    "nbiasL": [("Rba1", "P2"), ("Rbb2", "P2")],
    "nbiasH": [("Rba2", "P2"), ("Rbb1", "P2")],
    "nifbias": [("Rb1", "P2"), ("Rb2", "P2")],
    "rfop": [("XQ3", "C"), ("XQ6", "C"), ("RL1", "P2")],
    "rfon": [("XQ4", "C"), ("XQ5", "C"), ("RL2", "P2")],
    "lop": [("Rd1", "P1")], "lon": [("Rd2", "P1")],
    "vcc": [("RL1", "P1"), ("RL2", "P1")],
    "ifp": [("Rb1", "P1")], "ifn": [("Rb2", "P1")],
    "nsens": [("XQs", "C"), ("XQs", "B")],
    "nvtop": [("XBI1_Rref", "P1"), ("XBI2_Rref", "P1")],
    # ⚠ 已收编的命名分歧，**不要**在这里"修"：XBI1 组 XQo/XQr 的 C=B 在版图上与
    #   ntaila 同属一个 M1 域（域 M1:6 双标签），sch 按轨名单名转录 ntaila ＝ 组长
    #   2026-10-18 09:49Z §二「正确口径 · 不另开议题」；提取 cdl 取域内局部名 nref。
    #   两者指的是**同一物理域**，不是拓扑分歧 ⇒ 本表保持 ntaila，不动。
    "gnd": [("XBI1_XQo", "E"), ("XBI2_XQo", "E"), ("XQs", "E")],
}

# v3.3：假管声明**按键**并进 NET_DECL（键取自 DUMMY_NET_DECL 自己的键，不写死 gnd ——
#   写死过一次，负向测试立刻暴露「键被忽略」的坑：改 DUMMY_NET_DECL 的网名后，
#   两张表会各说各话，而断言只在其中一边响。见 纪要 §四·负向测试 N1）。
for _net, _ts in DUMMY_NET_DECL.items():
    NET_DECL.setdefault(_net, []).extend(_ts)

# ═══════════════════════════════════════════════════════════════
# 11. net_check + save
# ═══════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════
# ⑭ 官方 label purpose 补打（R-ANNO-01 ② 硬条款）
# ══════════════════════════════════════════════════════════════════════
# 口径原文（组长 R-ANNO-01 + reply_v9 §五 + probe_viastack_truth，三处同口径）：
#   「网名 label **一律打官方 label purpose /1 层**（Metal1.label=8/1、Metal2.label=10/1、
#     Activ.label=1/1……全表 pdk libs.tech/klayout/tech/sg13g2.lyp）——**禁止打 drawing /0 层**」。
# 本机无 PDK（/data/workspace/pdk/ 空）查不到 lyp 原表，只能按组长转述执行；
# 若代跑回报 lyp 实表与此不符，以 lyp 为准，改下面 METAL_LNUM 即可。
#
# 为什么补打写在**本脚本**里、而不是改 lib13g2.label()：
#   三件 `import lib13g2`，组长代跑时解析到的是**他那一份** phys/top/lib13g2.py；
#   我改自己 m1_lib/ 下的副本对代跑毫无作用 —— 那种改法只制造「我这边已经改了」的假象。
#   口径必须长在交付件里。
#
# /25 不撤：官方 LVS deck `connect(metal*_con, metal*_text)`（reply_v10 §57-63）把 /25 接进
#   金属网 = 次级 label 通道；两处同名 label 指向同一金属簇只是同名合并，不会多出网、
#   不会短路；且 /25 上全是纯网名，按 R-ANNO-01 本就不生幽灵网。
def relabel_official(b):
    """把每个 <metal>/25 的网名文本，在同层 <metal>/1 再打一份（官方 label purpose）。"""
    import pya
    METAL_LNUM = (8, 10, 30, 50, 67, 126, 134)   # M1 M2 M3 M4 M5 TOPM1 TOPM2
    n = 0
    for lnum in METAL_LNUM:
        for s in b.top.each_shape(b.ly.layer(lnum, 25)):
            if s.is_text():
                b.top.shapes(b.ly.layer(lnum, 1)).insert(
                    pya.Text(s.text.string, s.text.trans))
                n += 1
    print(f"[relabel] 官方 label purpose /1 补打 {n} 处（源：各金属 /25 网名文本）", flush=True)
    return n


# ── v2.0 新增两道机检（同 drv1/drv2 v2.0）────────────────────────────
RG.audit_res_pads(b, RES_DEVS, tag="mix_v35")
CB.audit_board_e_pads(b, HBT_DEVS, tag="mix_v35")

# ══════════════════════════════════════════════════════════════════════
# v3.2（2026-10-19）**无名 M1 簇补标** —— 纯网名文本，零金属图形改动
# ══════════════════════════════════════════════════════════════════════
# 为什么补：自检台第 ㉓ 项（带金属 × **顶层自画** M1 互压）靠「M1 连通簇上有没有
#   网名标注」判同网/异网。器件引脚落点那一小块 M1 焊盘历来**只有几何、没有网名**
#   ⇒ 带金属对着自己的焊盘全部落进「一侧无名 ⇒ 不可判」，㉓ 在 drv2 上可判率仅
#   **19.6%**（不可判 180/224），drv1 59%、mix 73%。可判率低 = 这一格基本是盲的。
# 为什么能机械补（不是猜）：每个无名簇里**所有**器件引脚的 NET_DECL 声明网**一致**
#   （探针逐簇核过：drv2 28 簇全 addable，**零「一簇多网」**）。声明网来自脚本
#   NET_DECL，且被自检台第 ⑦ 项与网表锚（SP_ANCHOR）交叉核对过 ⇒ 唯一解，不是推测。
# 补标后的效果（探针模拟 + 落地后实跑，数字一致）：
#   ㉓ 可判率 19.6% → **100%**（drv2）；59% → 100%（drv1）；73% → 100%（mix）
#   异网对全部 ≥ 自设保守项 0.63 ⇒ **零硬档、零软档**（原先报的 12 条负净距
#   「不可判」候选，全部落成**同网**——它们就是器件自己的引脚焊盘，本该相接）。
# ⚠ 口径不变：label 只**命名**，不代替电学连接（E2 的 gnd$1 教训）。地仍走
#   金属三环（M1 垫 → via_stack → M4 立管），本次一条金属都没动。
# 探针：design/sow6/dryrun/probe_nameless_m1.py（只读普查，不改任何件）
M1_CLUSTER_LABELS = [
    # v3.4：XBI1_Rref 随 Qr 左移 13.35µm（−40.325 → −53.675），**手抄坐标已失效**。
    #   两条 Rref 的 P1 补标一律从器件自报引脚取（与 v3.3 假管补标同一手法：零手抄）。
    (round(b.devs["XBI1_Rref"].p["P1"][0], 3), round(b.devs["XBI1_Rref"].p["P1"][1], 3),
     'nvtop', "XBI1_Rref.P1 → NET_DECL['nvtop']（坐标导出，v3.4）"),
    (round(b.devs["XBI2_Rref"].p["P1"][0], 3), round(b.devs["XBI2_Rref"].p["P1"][1], 3),
     'nvtop', "XBI2_Rref.P1 → NET_DECL['nvtop']（坐标导出，v3.4）"),
    (-20.00, +235.00, 'na1p', "Rba1.P1 → NET_DECL['na1p']"),
    (+0.00, +235.00, 'nb1p', "Rbb1.P1 → NET_DECL['nb1p']"),
    (+20.00, +235.00, 'nb2n', "Rbb2.P1 → NET_DECL['nb2n']"),
    (+35.00, +235.00, 'na2n', "Rba2.P1 → NET_DECL['na2n']"),
    (-70.00, +7.96, 'nifbias', "Rb1.P2 → NET_DECL['nifbias']"),
    (-66.00, +7.96, 'nifbias', "Rb2.P2 → NET_DECL['nifbias']"),
    (+52.00, +116.86, 'nsens', 'XQs.B/C 同簇，声明网唯一'),
    (+21.98, +138.59, 'lond', "Rd2.P2 → NET_DECL['lond']"),
    (-21.98, +138.59, 'lopd', "Rd1.P2 → NET_DECL['lopd']"),
    (+20.00, +31.24, 'ntailb', "XBI2_XQo.C → NET_DECL['ntailb']"),
    (+10.00, +63.00, 'e2b', "Re2b.P1 → NET_DECL['e2b']"),
    (-10.00, +63.00, 'e1b', "Re1b.P1 → NET_DECL['e1b']"),
    (+30.00, +55.00, 'e2a', "Re2a.P1 → NET_DECL['e2a']"),
    (-30.00, +55.00, 'e1a', "Re1a.P1 → NET_DECL['e1a']"),
]

# ══════════════════════════════════════════════════════════════════════
# v3.3（2026-10-19）**假管 gnd 补标：坐标与网名改为导出**（裁定五十一 §五② 的升级项）
# ══════════════════════════════════════════════════════════════════════
# v3.2 之前的四条是**手抄**的：坐标 (∓50.00, +83.87) / (∓50.00, +86.24)，
# 依据文本写「假管 d3L.C 落 M1 垫」「d3L.B 落 M1 垫」。实测（干跑 + 簇归属回查）：
#   器件自报真坐标 **C=(∓50, +86.240)、B=(∓50, +83.860)**
#   ⇒ 四条标注的 **依据文本 C/B 恰好互换**：83.87 那条其实落在 B 垫（Δ0.01µm），
#     86.24 那条落在 C 垫（Δ0.000）。标注本身仍在正确的 M1 簇上、网名仍是 gnd
#     （C/B 同为 gnd，由 `QXd3L gnd gnd gnd` 保证）⇒ **LVS/DRC 零影响，错的是「记录」**。
#   这正是「人工判读」会犯、而机械声明犯不了的错 —— 升级不是美化，是把这类错**根除**。
# 本版做法：坐标取 `dd.p[pk]`（器件对象自报）、网名取 NET_DECL 声明 ⇒ 结构上不可能互换。
def _dummy_m1_labels(devs=("d3L", "d3R"), pins=("C", "B")):
    """假管 C/B 的 M1 簇补标：坐标与网名**全导出**，零手抄。"""
    out = []
    for dn in devs:
        d = globals()[dn]
        for pk in pins:
            nets = sorted({n for n, ts in NET_DECL.items()
                           for (dd, pp) in ts if (dd, pp) == (dn, pk)})
            assert len(nets) == 1, f"{dn}.{pk} 声明网不唯一：{nets}"
            out.append((round(d.p[pk][0], 3), round(d.p[pk][1], 3), nets[0],
                        f"假管 {dn}.{pk} 落 M1 垫 → hop 到 M4 地轨 gnd"
                        f"（依据：网表 cdl Q5/Q6 = gnd gnd gnd，非人工判读）"))
    return out


_DUMMY_LABELS = _dummy_m1_labels()
M1_CLUSTER_LABELS = M1_CLUSTER_LABELS + _DUMMY_LABELS


def _dummy_decl_assert():
    """假管声明自证：①每脚声明网唯一 ②补标坐标＝器件自报引脚坐标 ③与块级网表逐字对上。

    为什么要有第③项：v3.2 那四条标注的依据是「人工判读」，机器无从回查；
    本版把依据钉到**块级 LVS 输入网表**（组长真跑那份），声明从此可被任何人复核。
    文件不在场时**大声报缺**并跳过——不静默（2026-10-19 静默兜底把错藏起来的血训）。
    """
    import re as _re
    import os as _os

    devs = {"d3L": d3L, "d3R": d3R}
    print(f"\n[_dummy_decl] 假管声明自证（{len(DUMMY_NET_DECL)} 网 / "
          f"{sum(len(v) for v in DUMMY_NET_DECL.values())} 脚）", flush=True)
    # ① + ②
    for net, terms in DUMMY_NET_DECL.items():
        for (dn, pk) in terms:
            nets = sorted({n for n, ts in NET_DECL.items()
                           for (d2, p2) in ts if (d2, p2) == (dn, pk)})
            assert nets == [net], f"{dn}.{pk} 声明网不唯一/与 NET_DECL 不一致：{nets}"
            px, py = devs[dn].p[pk]
            lab = [e for e in _DUMMY_LABELS if e[3].startswith(f"假管 {dn}.{pk} ")]
            if pk in ("C", "B"):
                assert lab, f"{dn}.{pk} 该补标却没补"
                assert (lab[0][0], lab[0][1]) == (round(px, 3), round(py, 3)), \
                    f"{dn}.{pk} 补标坐标 {lab[0][:2]} ≠ 引脚真坐标 {(px, py)}"
            print(f"  {dn}.{pk} 引脚({px:+.3f},{py:+.3f}) 声明网={net} "
                  f"补标={'有' if lab else '否(E 走 M2，由 M4 地轨单条 gnd 标注取名)'}", flush=True)
    # ③ 与块级网表逐字核对
    sub = "TX5G_M2_MIX_V35"
    here = _os.path.dirname(_os.path.abspath(__file__)) if "__file__" in globals() else "."
    cands = sorted(f for f in _os.listdir(here)
                   if f.startswith("mix_subckt_LVS") and f.endswith(".sp"))
    # 按**内容**挑（.subckt 行 == 本版顶层名），不按文件名猜：
    # 同目录并存 v1/v1b/v2/v3 四份，只认 .subckt 对得上的那一份。
    picked = None
    for c in cands:
        for ln in open(_os.path.join(here, c), encoding="utf-8"):
            t = ln.strip().split()
            if t and t[0].lower() == ".subckt" and len(t) > 1 and t[1] == sub:
                picked = c
                break
        if picked:
            break
    if not picked:
        print(f"  [WARN] 同目录 {cands} 内没有一份 .subckt == {sub} 的块级网表"
              f" ⇒ 跳过与网表的逐字核对（**声明仍在**，只是本机无从回查）", flush=True)
        return
    path = _os.path.join(here, picked)
    found, inside = {}, False
    for ln in open(path, encoding="utf-8"):
        s = ln.strip()
        if s.lower().startswith(".subckt"):
            inside = (s.split()[1] == sub)
            continue
        if inside and s.lower().startswith(".ends"):
            break
        if inside and "npn13G2" in s:
            t = s.split()
            nm = t[0][1:] if t[0].startswith("Q") else t[0]
            nm = next((c for c in (nm, nm[1:]) if c in devs), nm)
            if nm in devs:
                found[nm] = (t[1], t[2], t[3])
    for dn in ("d3L", "d3R"):
        assert dn in found, f"{picked} :: {sub} 内未找到 {dn} ⇒ 配套网表缺件"
        want = tuple(n for n, ts in DUMMY_NET_DECL.items()
                     for (d2, p2) in ts if d2 == dn)
        assert found[dn] == want, f"{dn} 与块级网表不符：网表 {found[dn]} vs 声明 {want}"
        print(f"  [OK] {dn} 网表 {found[dn]} == DUMMY_NET_DECL {want} ✓", flush=True)
    print(f"[_dummy_decl] 依据件：{picked} :: {sub}", flush=True)


_dummy_decl_assert()


def label_m1_clusters(b, tag="mix_v35"):
    for (x, y, net, why) in M1_CLUSTER_LABELS:
        b.label("M1", x, y, net)
    print(f"[m1-label] {tag}: 补 {len(M1_CLUSTER_LABELS)} 条顶层 M1 网名标注"
          f"（几何零改动）", flush=True)
    return len(M1_CLUSTER_LABELS)

n_clusters, shorts = b.net_check("ALL")
label_m1_clusters(b)
relabel_official(b)          # ⑭ R-ANNO-01 ②：官方 label purpose /1
# ⚠ net_check("ALL") 把 M1 与 M2 的图形丢进**同一个 Region** 合并，于是「M1 金属压到
#   M2 金属」也会被判成同一簇（跨层本就该压在一起）。它打印的「短路嫌疑」里绝大多数
#   是这种**层盲**假阳性，**不可当短路证据**。真判据是自检台第 ⑤ 项：逐层分簇 +
#   过孔桥接（M1/M2 分开判），零短路嫌疑。
print(f"[M2 mix v3.5] net_check(ALL) 簇={n_clusters} "
      f"（层盲，仅供参考）短路嫌疑={shorts if shorts else '无'}", flush=True)

os.makedirs("/data/workspace/gds", exist_ok=True)
b.save("/data/workspace/gds/m2_mix_v35.gds")
print("M2 MIX V3.4 OK", flush=True)
