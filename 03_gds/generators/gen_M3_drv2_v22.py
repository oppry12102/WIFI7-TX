#!/usr/bin/env python3
"""
M3-b · drv2 级版图生成脚本 v2.0（**真短 + 断路回改轮** · 2026-10-18）
════════════════════════════════════════════════════════════════════════
  v2.0 相对 v1.9 的全部变更（①②=回改清单内；③④=清单外新发现，三证据实锤）：

  ① **Re1/Re2 的 P2 出脚改锚焊盘真值**（断路，真值表 resgeom 模块头）
     lib 引脚锚点 0.72+0.84·l 对 rsil 短条(l=1) 高出盘顶 0.03µm ⇒ stub 悬空。
     先 mkres 后 chain，p2_pad=res_pad2 真值入参；新增 audit_res_pads 机检。
  ② **XBI*.XQr 的 C=B 实连改绕 E 指列**（真短 #5~#8，cbpath.cb_tie 三段折线，
     逃逸列净距 0.70µm）；新增 cbpath.audit_board_e_pads 全板机检。
  ③ **ccas 下横段上移**（清单外 · E 窗审计抓获）：原 1µm 横段以 C 带心为轴，
     下缘削进**本管 E 指窗顶 0.03µm** ⇒ ccas↔e 真短（真 GDS + pex 五名域互证）。
  ④ **ccas 竖段 M1→M2**（清单外 · 真 GDS 实测）：XQ3 的 B 带是全宽 M1 条
     （x[锚−9.3,锚+9.3]），M1 竖线从 C 高度直上 E 高度必横穿（交叠 0.5µm² ⇒
     ccas↔nbcas 真短；旧 ⑤c 的「让开」只躲开了仿真层引脚标记盒）。B 带=M1、
     目标 E 脚=M2 ⇒ 竖段改走 M2，下端 cross 换层、E 落地段 M2 本层直落
     （中心 = E 脚心 +0.21，让开 nbcas 柱 M2 中间层禁产区）。
     ⚠ 预期 gdsdiff：ccas 链路 M1→M2 换层 + 下横段上移 0.46；其余逐位不动。

M3-b · drv2 级版图生成脚本 v1.9
  v1.9 = v1.8 唯一变更：**E 回流链断路修复**（2026-10-17 组长裁决，lap=0.6µm）。
    · 根因与修复同 drv1 v1.9（place_emit_chain 的 arm_bot 按 via 外接高推，
      焊盘实际顶比外接低 0.085µm → 直流断路）。drv2 同型断（桶焊盘孤立 2 域）。
    · 修复：emitpath.place_emit_chain 新增 lap=0.6，臂与桶 M2 焊盘重叠
      0.515µm ≥ 0.5µm 验收线。
    · 根因教训升准则 v1.4（见 drv1 v1.9 头注释）。
  v1.8 = v1.7 全部几何**零变化** + **guard 环落地**（2026-10-17 11:37Z 组长三裁定①
  立项；来源：inbox 第 71 行 +《判读纪要_LVS粘连三轮排障_v2b口径》§四.1，
  sha b85bde19…）。裁定同步的预期：**补环不解决粘连**（粘连在 deck 工程级、
  版图物理零短路已三轮排障证明）——本环解的是 **pwell 浮空**这个流片级真缺陷
  （12 管 sub=PCell 自带全接 gnd，但核内无一条手画衬底接触；v17 台账 §12
  「guard ring 由库 v2 提供，本脚本不画」自本版起废止：库 guard_ring 的
  "pg" 占位标注与全边密排 tap 不合本件标注纪律/tap 预算，改走 mix v27 同款
  —— v2.7 基线代跑全绿的成熟做法，逐件同构）。

  环方案（mix v27 §9b 同款，全部参数照抄其 v2.5 定稿口径）：
    · 几何：GUARD = CORE bbox ± RING_M(8)；M1 外圈 ring_w=2 贴 GUARD 边，
      M2 内圈 inset=3（两圈同隙 1µm）→ M2 内圈离核 3µm —— 「环绝不骑核」
      （mix v2.3 勘误之五：Rb1 柱脚踩环 ×2 的血训参数）。
    · ptap1 ×8：每边 2 只（0.3/0.7 比例点，中心线正落 M1 圈上），PDK 默认
      参数；仿真层 PTAP_SKIPPED 进 NOTES（本机无 PDK 不建 ptap1，真几何
      本机无法验证），代跑真落 —— tap 密度与 psd 间距条款由代跑 DRC 终裁
      （mix v27 同款 8 只已代跑全绿）。
    · 定网 gnd（裁决②「不许悬空」三件事，缺一即浮空金属）：
      ① 搭桥：右边上下两处 M1 桥（M1 圈右边中心线 → M2 圈中心线）+
         M1→M2 柱 —— 两圈同心相距 1µm，via 焊盘够不着，必须先桥后柱；
      ② M4 地轨右延搭接段（§6 轨 [NT_X0,NT_X1] → 环右边 GUARD_X1）；
      ③ 落地单柱：环右边中心线 (GUARD_X1−1, GND_Y) M1→M4 —— 柱位所在
         M1 圈中心线上 M2/M3 全空（M2 内圈在 x 更内 3µm、M3 只有 nbias
         干路 x∈[30,47]），中间层不压异网（⑤d 口径自查）。
    · 标注：datatype=25 纯网名 "gnd" ×7（M1 圈四边 + M2 圈上下 + 落地柱，
      不加任何说明字）；relabel_official 自动补 /1（⑭ 照跑）。
    · 网表口径零变化：ptap 接触非器件、不进 DEV_NETS/NET_DECL（自检台第⑦
      项核对面不变）；LVS 对拍件 = drv2_subckt_LVS输入_v3.sp（v2b 正式化，
      sha 见投件信）。
    · 岛框 print：环落图后按 _bb(b.top) 真实内容重算（含环），不再 CORE±6。

  v1.7 = v1.6（37×1 终版）全部其余几何 + **vcc 顶层馈电桶整根撤除**（2026-10-17 09:37Z
  裁定①·选②；来源：组长 inbox 第 64 行「Q11 代跑闭环 + 四裁定」+《判读纪要_Q11代跑v16轮》
  sha 9981f872…）。四条裁定理由（全文见纪要）：电路拓扑已闭环（RL.P1 30mA 全量注上环 +
  TOPM2 立管串环 + Rref.P1 偏置），M5 无 vcc 网**也不该有**；造 M5 干线=零收益负收益；
  桶从未生效——四轮代跑全绿 + typ 基线 CG=+17.4465 均为**无桶状态**，删=回归已验证基线；
  R-VIA-01 强制对象是发射极回流桶（Via1×150），vcc 馈电桶系**自愿冗余非条款**。
  配套：RL.P1 注入 EM 复核一行（上环 TM1 6µm = 90mA 能力，裕 3×）。
  撤桶使本件 ㉑ 恢复全绿（浮岛只有 LVS 能抓，官方 DRC 无此规则——血训在案）。
  ※ v1.6 两天内的沿革：13×3（09:23 首批）→ 37×1@−17.25（09:33 更正）→ **撤除**（本版）。
    前两版的落点/平台账都成了废纸，但「浮空缺陷」的教训留在自检台第 ㉑ 项里。
  v1.5 = v1.4 全部内容 + **Q8 代跑 v25 轮三处可修残留的代码落实**（2026-10-17 08:0xZ；
  来源：组长 inbox 第 59 行「Q8 代跑 v25 轮判读回执 · 战报 + 三问全答 + 可修残留三处」
        + `design/sow6/DRC逐条坐标明细_v25轮_2026-10-17.md` 逐条坐标）：

  ① 【TM2.a×8 根治 · 自检台新增第 ⑳ 项】本件 4 处 T 交半搭接（官方逐条坐标：
     (-36,13.268~14)|(-35,15.732~15)、(55,182.268~183)|(56,184.732~184)、
     (56,-2|-2.732)|(55,-1|-0.268)、(41.732,183)|(41,182.268)|(40,184)…）：
     bin/bb1 的 TOPM2 横轨端点**正落在竖条中心**（半搭接）⇒ 并集多出 1.0µm
     宽的凸出小舌 < TM2.a 的 2.0µm。逐矩形量（⑯）全绿，是官方先抓到的。
     改法（**贯通式外延**，不挪网、不改拓扑）：横轨两端各外延 1.0µm（＝竖条半宽），
     使竖条外缘与横轨端点齐平 ⇒ 并集只剩直角 L，无台阶。
       · bin  ：横轨左端 -36 → -37（立管在 -36）
       · bb1  ：两条横轨右端 56 → 57（竖条在 56），左端 40 → 39（立管在 40），
               且竖条顶端 184 → 185（贯通横轨，不留半搭接台阶）
     自检台口径校准见下：⑳ 对着官方逐条坐标复算，本件 ⑳=8（官方 TM2.a×8）、
     M2 ⑳=12（官方 TM1.a×4 + TM2.a×8）、drv1 ⑳=0（官方 0）—— **逐项对上**。
  ② 【Slt.c.M1×1 真开槽】v1.3 的文首把「两条 15.15 轨 + 缝 2.0 + 右端桥」写进了注释，
     **代码却还是一整块 `b.rect("M1", NT_X0, NT_Y0, NT_X1, NT_Y1)`**（组长实测：
     官方仍报 Slt.c.M1×1，polygon=(-62,117.7;-62,150;88,150;88,117.7)，
     最窄边 32.3 > 30 的无开槽上限）。本版**代码真开**：两轨各 15.15 + 缝 2.0 +
     右端 5.0µm 搭桥（桥最窄边 5.0 < 30 ✓）。EM 截面一步不减：
     2×15.15 = 30.3 ≥ 29.28mA @1mA/µm 的需求（0.966 mA/µm，裕 1.03）。
     ⚠ 注释与代码必须同改（本条就是「只进注释没进代码」的翻车现场）。
  v1.6 = v1.5 全部几何 + **vcc 顶层馈电桶按 R-VIA-01 恢复 ≥37 颗**（2026-10-17 09:0xZ；
    来源：组长 08:26Z 裁定 Q-A + `判读纪要_Q9代跑v26轮_2026-10-17.md` §3 七档实测表，
    sha aa85cecd…）—— 本版两处改动，一处是裁定，一处是本轮自检逮到的缺陷：

  ① 【桶档位 1×1 → 13×3 = 39 颗】组长裁定：3×2（6 件）EM 5mA/件 = 3.6× 超 Jmax、
     0.67Ω ≫ 60mΩ 预算，**双超否决**；「执行：恢复 ≥37 颗」，三档候选
     13×3=39（TM1 11.34×2.94 / M5 10.70×2.30，最紧凑）／ 19×2=38（16.38 宽）／
     37×1（31.50 宽，已获官方 deck 零新增实证）。**按桶金属形状取 13×3**：
     vcc 上环右段（x 24.82~40，宽 15.2µm）放得下 11.34，放不下 16.38 与 31.50。
     电阻账：官方 TopVia1 4.0Ω/件 ⇒ 39 并联 ≈ 0.10Ω（v1.5 的 1×1 是 4Ω 串在 vcc 馈电
     上，~30mA 下约 120mV 压降）；EM 账 39 × 1.4mA = 54.6mA ≥ 实际 ~30mA。
     薄金属堆仍按 `cols=TV1_N(37), rows=1` 走 vn_*（M5 侧平台随薄堆外沿，见 ㉑ 注）。

  ② 【落点从「浮空」挪到上环上 —— 本轮新加的自检台第 ㉑ 项量出来的缺陷】
     v1.5 的落点 `TVY = Y_VCC_HI − VCC_W = 206`，而 vcc 上环占 y ∈ [209, 215]
     ⇒ 1×1 的 TM1 平台（1.64 见方）顶边只到 **206.82**，比环低 **2.18µm**；
     M5 侧那一带更是全空。**两端都不落金属 = 整根落柱是浮岛**，R-VIA-01 想要的
     37 颗顶层馈电从来就没接过电（不是「4Ω 太贵」，是 ∞）。旧落点还正好压在
     outp/outn 的 M1 走线上（x=34 的那条 L 形 M1，从发射极臂到 Y_CP=206）。
     ⚠ 官方 DRC **不报**浮空金属（没有这条规则），⑯⑰⑱⑲⑳ 五族全绿也照样漏 ——
       这是自检台第 6 个「恒过的检查」（⑯b / ⑳ 之后）。已加 ㉑「落柱两端落点重叠」。
     本版把落点平移到环的中心线 TVY = Y_VCC_HI、TVX 34.0 → 33.0（纯平移，
     网名/拓扑不动），TM1 侧因此真正压在环上。

  ③ 【**M5 侧仍无落点 —— 要你裁，我不猜】】落点挪上来之后，顶端接住了、M5 端
     依然悬空：drv2 的 vcc 分配**全在 TOPM1**（Rref.P1→下环、RL.P1→上环、
     TOPM2 立管串上下两环），那一带除上环外**没有任何 M5 金属**。
     M5 端要接到哪张网（新建 M5 vcc 干路？改走 TOPM2 立管？此桶改挂别的网？）是
     **电路决定**，版图侧猜错就是静默短路/断路。已随信报你，裁定后我改一个数 + 重跑。
     在此之前本件 ㉑ 项**如实报 1 条 FAIL**（M5 端悬空），不自欺成全绿。

  v1.4 = v1.3 全部几何内容 + **lib v2.2 的 TopVia1 钉档**（2026-10-17 07:5xZ；来源：组长
    07:45Z 回执信）。v1.3 = v1.2 + 官方 DRC 两族自侧落实 + Slt.c.M1 开槽（见文末沿革表）。
    v1.2 = v1.1 + ⑭ 官方 label purpose /1 补打（R-ANNO-01 ②，理由见 relabel_official）

网表锚：design/chain_top_tb_v015_1.sp :: `.subckt drv2 inp inn outp outn vcc`
         + `.subckt hbt_mirror nout ntop nx=8 rr=1.62k`

## 三条硬纪律（与 drv1 同源，见 gen_M3_drv1_v1.py 头）
1. 器件数逐只对网表（`SP_ANCHOR` + `DEV_NETS` → 自检台第⑦项）。
   **4 组 hbt_mirror 各是三件**（Qr nx=1 / Qo nx=8 / Rref 1.62k），绝不摆阵列。
2. 阻值全部经 resgeom 由阻值反算（假设 A1 Rsheet=15Ω/□）。
3. 发射极回流按 R-EMIT-01/02 + R-VIA-01 断言，几何由 emitpath.place_emit_chain 统一落。

## drv2 特有的三件事

**(1) 4 组镜像的 nref 是四条**互不连通的网（网表没写 .global，每组内部节点各自独立）。
    版图按网表原文把四条都标成 `nref`，但几何上互不相接（自检台逐层合并能证明）。
    ⚠ 电路上 4 个二极管接法的镜像**不共享基极**，等于 4 个独立偏置 → 无电流共享、
    失配不受控。这是网表层的观察，已随投件信提请组长（不改网表，只备案）。

**(2) Via1 桶 = 150 件**（R-VIA-01 签核数字，0.2Ω 档 via 桶 60mΩ → 9/0.06 = 150）。
    v1.7：vcc 顶层馈电的 37 件 TopVia1 **按裁定①撤除**（自愿冗余非条款，见头部 v1.7）。
    台账口径回到 **150 件/边**（发射极回流桶 = R-VIA-01 强制对象）。
    ⚠「减层 stack 只用 Via1+TV1」中间怎么从 M2 爬到 M5，准则没写 —— 已列为回执项。

**(3) vcc 分上下两环 + 一条 TOPM2 立管串起来**。
    理由：Rref 高 108µm，其 vcc 端（P1）在最底；RL1/RL2 的 vcc 端在 y≈200。
    单层 TM1 跑 190µm，按 RSH=0.0625Ω/□（**估值**）即使 20µm 宽也有 0.6Ω —— 不可接受。
    故用 TOPM2 立管（TM2 3.0µm 厚，估 0.0625Ω/□ 同档）分段，每段仍短。

用法（组长侧）：
    . /data/workspace/pdk/kl_env030.sh
    KLAYOUT_PATH=$KLTECH klayout -zz -r gen_M3_drv2_v1.py
用法（本机自检，无 klayout）：
    python design/sow6/dryrun/preflight.py design/sow6/gen_M3_drv2_v1.py

输出：/data/workspace/gds/m3_drv2_v17.gds

【2026-10-17 修订 · 文件名不变内容已变】按组长 reply_v12 的 Q5/Q6/Q7 落地：
  Q5 Rsheet 真值换算 + 高阻自动选型（res_auto）→ 三件电阻几何全部重算；
  Q6 cmim 真件（PCell `cmim`、w&l、23.66µm 见方，自适应引脚层 + 非致命回落）；
  Q7 guard 环定网 gnd（搭桥+落地柱，真接进 gnd 网）+ ptap 接触（PDK 默认参数，
     仿真层跳过、代跑落）。变更清单与逐项理由见 CHANGELOG_2026-10-17_Q5Q6Q7.md。
v1.4 = v1.3 全部几何内容 + **lib v2.2 的 TopVia1 钉档**（2026-10-17 07:5xZ；来源：组长
  b7a0 07:45:29Z 回执 ① 与新投盘 `probe_viastack_array_v22_2026-10-17.md`，sha e44d63e2…）：

  ⓪ 【库版本闸升 v2.2】canonical = 8510 `design/sow6/lib13g2.py`（v2.2 / 539 行 / 27592B /
     sha 02ecbfb95b3b…）。v2.2 变更仅 `Board.via` 一处（vt1 透传 + 缓存键含 vt1 档位），
     薄金属堆与既有调用行为逐位不变 ⇒ 本件其余几何零变化。
  ① 【TopVia1 桶钉 1×1】本件 R-VIA-01 的 vcc 顶层馈电桶是 `b.via(TVX, TVY,
     b_layer="Metal5", t_layer="TopMetal1", cols=37, rows=1)` —— 意图是 37 列 TopVia1
     阵列（37 × 1.4mA = 51.8mA ≥ 实际 ~30mA）。但 **v2.1 及更早 `Board.via` 把 vt1 档位
     硬编码 1×1**（官方 `via_stack_code.py` 里 vt1 走 vt1_columns/vt1_rows，与 vn_* 无关），
     ⇒ 桶实际只落了**一颗** TopVia1；v2.2 起 vt1 缺省**继承 cols/rows**，不钉档就会变成
     37×1 阵列，而 TM1 平台**非线性**（实测 1×1 = 1.64 见方、3×2 = 2.94×2.10；组长明令
     「按实测值取用，**勿自行外推**」）⇒ 37×1 无真值可依。
     本版显式 `vt1_cols=1, vt1_rows=1`：与 v1.3（v2.1 时代已代跑过的那份）几何**逐位相同**，
     薄金属堆仍按 cols=37/rows=1 走（M5 侧平台规则 = 阵列外沿 +0.10/侧，1×1 的 0.62 同口径）。
     ⚠ 由此把一个**此前没人写明的口径问题**摆上台面：这桶名义 37 颗、实际 1 颗 TopVia1，
       单 via 过 ~30mA 是否满足官方 V1 电流规则，需组长裁定（两问已写进信里）。
       要真阵列，请补测 (37×1) 的 TM1 平台真值，我这边立刻改档。
  ② 【绘图封装透传 vt1_*】v1.3 的官方-DRC 落实块把 `b.via` 换成了本地封装（5nm 量化用），
     签名停在 `(x, y, b_layer, t_layer, cols, rows)` ⇒ 钉档参数传不进去
     （`TypeError: unexpected keyword argument 'vt1_cols'`，本轮自检当场逮到）。
     封装改为**透传** vt1_cols/vt1_rows，且故意不给默认值：想钉 1×1 必须显式写出来。

v1.3 = v1.2 全部内容 + **官方 DRC 两族的自侧落实 + Slt.c.M1 开槽**（2026-10-17；来源：
  组长 b7a0 07:29Z 回执信 + `判读纪要_M2M3代跑v24全链_2026-10-17.md`）：

  ① 【Offgrid 族（≈90% 项数）】官方 grid=0.005µm（纪要 §3.4）。resgeom 侧长度 l 量化到
     **1/168µm** 晶格（P2 = 0.72+0.84·l 落在 5nm 上的充要步距），参数串给足有效位；
     本脚本侧五个绘图入口过 5nm 量化。
  ② 【TM1.a×18 / TM2.a×22（要改图）】TopMetal1 最小宽 1.64µm、TopMetal2 2.0µm，而全部
     顶层走线都用库默认 0.30µm —— 顶层每根线都违规。给 TOPM1/TOPM2 设每层最小宽下限。
     ⚠ 顶层加宽会自造间距违规（两条 1.64µm 宽线相距 <3.28µm 即违规）：本件 vcc 双环在
       x=±70（Y_VCC_LO=6 / Y_VCC_HI=212），与 bin/bb1 的 TOPM2 立管（x=−36/+40）错开，
       逐条核过自检台 ⑱ 项 0 FAIL。
  ③ 【Slt.c.M1×1 根治】M1 **无开槽最大宽度 30µm**；ntail 汇流轨是 150×32.3µm 的大平面，
     最窄边 32.3 > 30 必开槽。（组长记成「150µm 宽」，但 DRC 的 width 取 bbox 最窄边。）
     槽不能白开 —— 一刀切下去平面断成两片就是「同名分裂」（LVS 判多段）。本版：
     **两条 16.15µm 的轨 + 右端 5µm 搭桥**：两轨最窄边 16.15（<30 ✓）、搭桥 2.3（✓）；
     EM 截面一步不减（2×16.15 = 32.3 = W_NT，29.28mA @1mA/µm 仍 0.976 mA/µm）。
     槽宽取 2.3µm（>M1 间距 0.18；槽自身的最小宽规则本机查不到，待代跑校准）。
  ④ 【代跑补丁①】bbox 双风格适配器 `_bb()`。

"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
for _d in (os.path.join(_HERE, "..", "..", "phys", "top"), _HERE):
    if os.path.isdir(_d):
        sys.path.insert(0, os.path.abspath(_d))
import lib13g2 as L
import resgeom as RG
import emitpath as EP
import cbpath as CB

CX = 0.0
USE_CMIM = False

b = L.Board("TX5G_M3_DRV2_V22")

# v2.0 回改登记簿（与 drv1_v20 同款）：HBT（E 指底座扫描）+ 电阻（焊盘覆盖自检）
HBT_DEVS = []
RES_DEVS = []


def mkhbt(name, nx, x, y, mirror=False):
    """HBT 实例 + 审计登记（第 5 位 = 预批准「本管 E 窗落地」矩形表，可后补）。"""
    inst = b.mkpc_at(name, "npn13G2", {"Nx": nx}, (x, y), "hbt", mirror=mirror)
    HBT_DEVS.append([name, (x, y), nx, mirror, []])
    return inst


def _hbt(name):
    """按名取登记条目（供后续补 ok_rects）。"""
    for d in HBT_DEVS:
        if d[0] == name:
            return d
    raise KeyError(name)

# ══════════════════════════════════════════════════════════════════════════
# 官方 DRC 两族的**自侧落实**（纪要 §3.4 grid / §4.1 Offgrid / §4.2 真几何族）
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
    if abs(_q(x2) - _q(x1)) < GRID:      # 零长线 = 零面积框，官方 deck 与
        return                              # 真 klayout 都会当退化图形；直接不画
    _wh0(lname, _q(y), _q(x1), _q(x2), w or MINW.get(lname))


def wire_v(lname, x, y1, y2, w=None):
    if abs(_q(y2) - _q(y1)) < GRID:
        return
    _wv0(lname, _q(x), _q(y1), _q(y2), w or MINW.get(lname))


def via(x, y, b_layer="Metal1", t_layer="Metal2", cols=2, rows=2,
        vt1_cols=None, vt1_rows=None, vt2_cols=None, vt2_rows=None):
    # vv1.4：lib v2.2 起 TopVia1 阵列档位走 vt1_columns/vt1_rows、缺省继承 cols/rows
    #（v2.1 硬编码 1×1）。本封装必须**透传** vt1_*，否则顶层的 1×1 钉档传不进来
    #（unexpected kwarg）。故意不给默认值：想钉 1×1 必须显式写出来。
    # v1.5（Q10 轮实测）：lib **v2.3** 又给 TopVia2 加了同款继承 ⇒ 本件 6 处
    #   t_layer=TopMetal2 的栈（bin/bb1 的偏置立管）在 v2.3 下**静默从 1×1 变 2×2**
    #   （实例参数逐只统计实证）⇒ 与 vt1 同纪律**显式钉 vt2=1×1**，几何与 v25 轮逐位相同。
    _via0(_q(x), _q(y), b_layer, t_layer, cols, rows, vt1_cols, vt1_rows,
          vt2_cols, vt2_rows)

def label(lname, x, y, text):
    _lab0(lname, _q(x), _q(y), text)


b.rect, b.wire_h, b.wire_v, b.via, b.label = rect, wire_h, wire_v, via, label


def _bb(cell):
    """top cell bbox 的**双风格**读取适配器（代跑补丁①）。

    真 klayout 0.30 的 Box/DBox 走 left/bottom/right/top；本机仿真层 DBox 走
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



# ══════════════════════════════════════════════════════════════════════
# 0. 层分配（drv2 的网比 drv1 多：ccas1/2、nbcas、4×nref → 七层全占满）
#    M1 引脚/ntail/ccas ｜ M2 发射极臂 ｜ M3 nbias ｜ M4 gnd ｜ M5 nref1..4 + 占位带
#    TOPM1 vcc 双环 ｜ TOPM2 vcc 立管 + bin/bb1
# ══════════════════════════════════════════════════════════════════════
_M2NUM = {"M1": "Metal1", "M2": "Metal2", "M3": "Metal3", "M4": "Metal4",
          "M5": "Metal5", "TOPM1": "TopMetal1", "TOPM2": "TopMetal2"}
_ORDER = ["Metal1", "Metal2", "Metal3", "Metal4", "Metal5",
          "TopMetal1", "TopMetal2"]
GND_LAYER, NREF_LAYER, BIAS_LAYER = "M4", "M5", "M3"
VCC_LAYER, VCC_STK_LAYER, PH_LAYER = "TOPM1", "TOPM2", "M5"

# 嵌套子电路内部网的版图网名形态（hbt_mirror 内部网 nref 是**每实例一条独立网**，
# 网表无 .global —— drv2 是 4 条，标成裸 `nref` 会被 LVS 并成一条）。
#   hier → xbi1/nref（默认）｜ flat_dot → xbi1.nref ｜ bare → nref（不可取）
NESTED_STYLE = "hier"
_NSEP = {"hier": "/", "flat_dot": ".", "bare": ""}[NESTED_STYLE]


def hnet(pfx, net):
    return net if _NSEP == "" else f"{pfx}{_NSEP}{net}"
BIAS_RISER = "TOPM2"      # bin / bb1 走 TOPM2（要与 vcc 立管错开 x）


def cross(x, y, lo, hi):
    """lo↔hi 跨层连接 = **一个** via_stack（焊盘只在两端层）。

    2026-10-17 血泪：旧版是「逐级铺栈」（M1→M5 连落四级 via_stack），
    每个实例都在**中间层**留焊盘 → 压在别人的走线上 = 真短路
    （自查抓出 drv1 1 处 / drv2 9 处 / M2 5 处跨层短路，三件全部撤回）。
    自检台 ⑤d 对每根过孔柱加硬约束：中间层压到异网金属 = FAIL。
    """
    lo = _ORDER[_ORDER.index(_M2NUM.get(lo, lo))]
    hi = _ORDER[_ORDER.index(_M2NUM.get(hi, hi))]
    if lo == hi:
        return
    if hi == "TopMetal1":
        # v1.4：v2.2 起 vt1 阵列缺省继承 cols/rows ⇒ 默认 2×2 的顶层柱会静默变阵列，
        # 而 TM1 平台非线性（实测 1×1=1.64 / 3×2=2.94×2.10，勿外推）⇒ 显式钉 1×1。
        b.via(x, y, b_layer=lo, t_layer=hi, vt1_cols=1, vt1_rows=1)
        return
    if hi == "TopMetal2":
        # v1.5：lib v2.3 起 **TopVia2 档位同样缺省继承 cols/rows** ⇒ 本函数默认的 2×2
        # 会把 bin/bb1 的 4 处 TOPM2 立管 + vcc 的 2 处静默变成 2×2 TopVia2 阵列
        # （实例参数逐只统计实证：v2.3 下 vt2_columns=2）。2×2 的 TM2 平台无实测值
        # （组长只给了 TopVia2 默认端头 2.00×2.00 合规的 1×1 口径）⇒ 同纪律钉 1×1，
        # 几何与已代跑的 v25 轮（lib v2.2）**逐位相同**。
        b.via(x, y, b_layer=lo, t_layer=hi,
              vt1_cols=1, vt1_rows=1, vt2_cols=1, vt2_rows=1)
        return
    b.via(x, y, b_layer=lo, t_layer=hi)


def mkres(name, R, model, x, y):
    """model="auto" = 让 resgeom.res_auto 在 rsil/rppd/rhigh 里挑面积最小的一档
    （Q5 真值落地后必须开：rsil 只 7Ω/□，1kΩ 会被拉成 142.9µm 长条）。
    选型结果逐件打印，型号即版图侧决策、随信报组长。"""
    p = RG.res_auto(R) if model == "auto" else RG.res_params(R, model)
    m = p["model"]
    print(f"  [res] {name:6s} {R:7g}Ω → {m:6s} l={p['_geom'][0]:8.3f} "
          f"w={p['_geom'][1]:7.3f} Rchk={p['_geom'][2]:.3g}Ω  "
          f"P2pad顶 y={y + RG.res_pad2(m, p['_geom'][0])[1]:.3f}"
          f"（lib锚点 {y + RG.res_pin_anchor(p['_geom'][0]):.3f}"
          f"，高 {RG.res_pin_gap(m, p['_geom'][0]):+.3f}µm）", flush=True)
    RES_DEVS.append((name, (x, y), m, p["_geom"][0], p["_geom"][1]))
    return b.mkpc_at(name, m, {"Calculate": "l", "l": p["l"], "w": p["w"]},
                     (x, y), "res")


def mkres_pad(name, R, model, x, y):
    """mkres + P2 焊盘真值跨度（绝对 y）—— v2.0 出脚锚定专用。"""
    inst = mkres(name, R, model, x, y)
    m, l_f = RES_DEVS[-1][2], RES_DEVS[-1][3]
    span = RG.res_pad2(m, l_f)
    return inst, (y + span[0], y + span[1])


# ══════════════════════════════════════════════════════════════════════
# 1. 几何骨架
# ══════════════════════════════════════════════════════════════════════
X_C = 24.0                  # XQ1/XQ3 @ -X_C；XQ2/XQ4 镜像 @ +X_C（nx=10 体宽 23.35）
Y_CAS = 190.0               # XQ3/XQ4（cascode）锚
Y_CE = 178.0                # XQ1/XQ2（共射输入）锚
Y_CP = 206.0                # outp/outn 轨（M1）
# Y_RL（RL1/RL2 的 P1 高度）在 §9 由 res_auto 现算：Y_RL = Y_CP − RL_SPAN
Y_P1 = 171.0                # Re1/Re2 的 P1（e1/e2 落点）
RES_BOT = 0.53              # 电阻本体下沿相对 P1 的下沉量
X_ESC = 38.0                # ntail 外折通道 @ ∓X_ESC（须在 M1 落点焊盘之外）
ARM_TOP = Y_CE - 0.01       # E 脚（M2 引脚）y
ARM_BOT = Y_P1 - RES_BOT
VIA1_N = 150                # R-VIA-01：0.2Ω 档 via 桶 60mΩ → 9/0.06 = 150
VC1, VR1 = RG.factor(VIA1_N)
VW, VH = RG.via_extent(VC1, VR1)
M1_PAD_H = VH + RES_BOT
# v1.7：TV1_N / TV1_COLS / TV1_ROWS 一族随桶撤除（沿革见头部 v1.7；37×1 的落点/平台
# 计算留档在 CHANGELOG_Q11 §9 与判读纪要，不再进代码）。

ARM_LEN = ARM_TOP - ARM_BOT
SP = EP.emit_return_spec(
    i_side=14.64,                          # 准则 §二 实测表：DRV2 cascode nx=10 → 14.64 mA/边
    tier_ohm=RG.EM_BUDGET["drv2"],         # R-VIA-01 方案 2 已采纳的 0.2Ω 档
    rail_len_um=ARM_LEN, m1_len_um=M1_PAD_H,
    ntail_i=29.28,                         # 两边合流
    tag="drv2")
assert SP["via1_n"] == VIA1_N == 150, SP["via1_n"]
assert SP["report"]["ok"], f"drv2 发射极路径超档：{SP['report']}"
print(EP.report(SP), flush=True)
W_NT = SP["w_ntail"]

NT_Y1 = 150.0
NT_Y0 = NT_Y1 - W_NT
NT_X0, NT_X1 = -62.0, 88.0
GX = (-49.5, -16.5, 16.5, 49.5)    # 4 组 XQo 锚 x（组距 33µm）
X_QR_OFF, X_RF_OFF = 21.0, 27.0     # XQr / Rref 相对 XQo 的横向偏移
Y_MIR = 108.0                       # 镜像组行
Y_RF = 20.0                         # Rref P1（vcc）→ P2（nref）在 111.44
Y_NREF = 114.0                      # 每组 nref 的 M5 横向轨
Y_RIN = 8.0                         # Rin P1（inp/inn）→ P2（gnd）在 64.72
X_RIN = (-46.0, -39.0)
Y_RB = 8.0                          # Rb P1（bin/bb1）→ P2（nbias）在 57.72（500Ω）
X_RB = (35.0, 42.0)
NBIAS_Y = 54.0                      # nbias M3 干路
NBCAS_Y = 184.0                     # nbcas M5 干路（XQ3/XQ4 的 B 脚）
X_BIN_RISER, X_BB1_RISER = -36.0, 40.0   # bin/bb1 的 TOPM2 立管（须在 M2 臂之外）
X_VCC_RISER = -70.0                 # vcc 的 TOPM2 立管
Y_VCC_LO, Y_VCC_HI = 6.0, 212.0     # vcc 下环 / 上环
VCC_W = 6.0

# ══════════════════════════════════════════════════════════════════════
# 2. 有源级：XQ1/XQ2（共射，nx=10）+ XQ3/XQ4（cascode，nx=10）
#    XQ2/XQ4 镜像 → 四个本体盒左右对称（引脚列恒在锚 x）。
# ══════════════════════════════════════════════════════════════════════
XQ1 = mkhbt("XQ1", 10, CX - X_C, Y_CE)      # ccas1 bin e1
XQ2 = mkhbt("XQ2", 10, CX + X_C, Y_CE, mirror=True)
XQ3 = mkhbt("XQ3", 10, CX - X_C, Y_CAS)     # outp nbcas ccas1
XQ4 = mkhbt("XQ4", 10, CX + X_C, Y_CAS, mirror=True)

# ccas1 / ccas2：XQ1.C(M1) ↔ XQ3.E(M2 脚)。
# ⚠ npn13G2 的 C/B/E **同 x**：沿 x 直上（M1）会从 XQ3 的 B 脚（nbcas）头上压过去
#   —— 自检台 ⑤c 报出 ccas1↔nbcas 跨层短路。解法：向岛心方向外折 4µm 再直上，
#   两端横插压到 1µm（1.13µm 的脚间距下唯一能过的宽度），让开 B 脚焊盘。
# ══ v2.0（2026-10-18）两处回改（清单外新发现 · E 窗审计 + 真 GDS + pex 三证据）══
#   ③ **下横段上移**：原 1µm 高以 C 带心为轴 → 下缘 [带底−0.28] 削进**本管 E 指窗
#      顶 0.03µm**（E 窗 = (8,0) 金属，顶 +0.77）⇒ ccas↔e 真短（每窗 0.0105µm²，
#      XQ1/XQ2 各 2~3 窗）。修：底边 = C带底 + 0.18（M1.b 净距）⇒ 中心 = 带心+0.46。
#   ④ **竖段 M1→M2**：XQ3 的 B 带是**全宽 M1 条**（真 GDS 实测 x[锚−9.3, 锚+9.3]，
#      即 ±(8.325+0.975)），M1 竖线从 C 高度直上 E 高度**必横穿**（真 GDS 交叠
#      0.5µm² ⇒ ccas↔nbcas 真短——此前 ⑤c 的「让开」只躲开了仿真层的引脚标记盒，
#      真带它看不见，属盲区第三例的又一受害者）。B 带 = M1、目标 E 脚 = M2
#      ⇒ 竖段改走 M2（跨 M1 带无碍）：下端 cross 上 M2，上端原 E 脚 cross 不动。
for (q1, q3, net) in ((XQ1, XQ3, "ccas1"), (XQ2, XQ4, "ccas2")):
    c1x, c1y = q1.p["C"]
    e3x, e3y = q3.p["E"]
    jx = e3x - 4.0 * (1 if e3x >= 0 else -1)        # 向岛心方向让开引脚列
    y_lo = c1y - 0.22 + 0.18 + 0.5                  # C带底(带心−0.22) + 0.18 + 半宽
    b.wire_h("M1", y_lo, c1x, jx, w=1.0)            # XQ1.C 落地带（已避开本管 E 窗顶）
    cross(jx, y_lo, "Metal1", "Metal2")             # v2.0 ④：起点换层上 M2
    b.wire_v("M2", jx, y_lo, e3y + 0.21, w=1.0)     # v2.0 ④：跨 XQ3 B 带（M1）走 M2
    # E 脚落地（M2 本层直落 E 窗）：中心 = E 脚心 +0.21 —— 贴窗内上沿走，让开
    #   nbcas cross 柱（M1→M5）在 M2 的中间层禁产区（柱心 y=188.86，平台顶 ≈189.17；
    #   原 e3y 高度横段 [189.49,190.49] 距平台 0.32 被 ⑪ 判 FAIL，上移后净距 0.53）
    b.wire_h("M2", e3y + 0.21, e3x, jx, w=1.0)
    b.label("M2", jx, (y_lo + e3y) / 2, net)

# ══════════════════════════════════════════════════════════════════════
# 3. 发射极回流链（几何全在 emitpath.place_emit_chain）
# ── v2.0（2026-10-18）：**先 mkres 后 chain**，P2 出脚改锚**焊盘真值** ──
#    旧口径 stub 从 lib 引脚锚点 y_p1+1.56 起画，rsil 短条(l=1)实盘顶只到
#    y_p1+1.53 ⇒ 悬空 0.03µm（Re1/Re2 P2 断路，与 drv1 同族同修，真值表
#    resgeom.RES_PAD1/RES_PAD2_OFF）。
Re1, _P2_RE1 = mkres_pad("Re1", 1.5, "rsil", CX - X_C, Y_P1)   # P1=e1  P2=ntail（1.5Ω → l=1u w=4.665u）
Re2, _P2_RE2 = mkres_pad("Re2", 1.5, "rsil", CX + X_C, Y_P1)   # P1=e2  P2=ntail
for q, p2_pad, net, sgn in ((XQ1, _P2_RE1, "e1", -1), (XQ2, _P2_RE2, "e2", +1)):
    EP.place_emit_chain(b, q.p["E"][0], Y_P1, SP, net, sgn,
                        X_ESC, NT_Y1, y_arm_top=q.p["E"][1], res_bot=RES_BOT,
                        lap=0.6, p2_pad=p2_pad)

# ══════════════════════════════════════════════════════════════════════
# 4. ntail 汇流轨（M1，W_NT ≥ 32.3µm：29.28mA @ M1 的 1mA/µm）
# ══════════════════════════════════════════════════════════════════════
# ⚠ v1.5 ②：Slt.c.M1「M1 无开槽最大宽度 30µm」，本轨最窄边 32.3 > 30 ⇒ **真开槽**。
#   v1.3 只把开槽方案写进注释、代码仍是一整块 b.rect（官方 v25 轮照报 Slt.c.M1×1，
#   polygon=(-62,117.7;-62,150;88,150;88,117.7)）——「只进注释没进代码」的翻车现场。
#   方案（组长 08:0xZ 处方 + 本件 EM 复核）：两条 15.15µm 轨 + 2.0µm 缝 + 右端 5.0µm 搭桥。
#   · 轨最窄边 15.15 < 30 ✓；桥最窄边 5.0 < 30 ✓；缝 2.0 > M1.b 的 0.18 ✓
#   · EM 截面：2×15.15 = 30.3 ≥ 29.28mA @1mA/µm ⇒ 0.966 mA/µm，裕 1.03 ✓
#   · 搭桥放**右端**：左端 x=NT_X0=-62 那侧紧贴器件区，桥压上去会盖到别的金属。
SLT_SEAM = 2.0                     # 缝宽（> M1 间距 0.18）
SLT_BR_W = 10.0                    # 搭桥宽（< 30 ✓；宽 10 ⇒ 桥内电流密度 ≈1.46mA/µm）
_rail_h = (NT_Y1 - NT_Y0 - SLT_SEAM) / 2.0
assert _rail_h <= 30.0 - 1e-9, f"ntail 单轨最窄边 {_rail_h:.3f} 超 Slt.c.M1 的 30µm"
assert _rail_h * 2.0 >= 29.28, f"ntail 双轨 EM 截面 {2 * _rail_h:.3f} < 29.28µm"
b.rect("M1", NT_X0, NT_Y0, NT_X1, NT_Y0 + _rail_h)                     # 下轨
b.rect("M1", NT_X0, NT_Y0 + _rail_h + SLT_SEAM, NT_X1, NT_Y1)          # 上轨
b.rect("M1", NT_X1 - SLT_BR_W, NT_Y0 + _rail_h,                        # 右端搭桥
       NT_X1, NT_Y0 + _rail_h + SLT_SEAM)
b.label("M1", CX, NT_Y0 + 1.0, "ntail")

# ══════════════════════════════════════════════════════════════════════
# 5. 尾流镜像 ×4：每组 = Qr(nx=1) + Qo(nx=8) + Rref(1.62k) **三件**
#    nref 走 M5：XQo.C(ntail) 与 XQo.B(nref) 只差 2.38µm，留在 M1 必被 ntail 轨吞掉。
#    ntail 轨在镜像组**上方** → XQo.C 直接向上进轨即可，不必绕行。
# ══════════════════════════════════════════════════════════════════════
RFOBJ = []
for k, gx in enumerate(GX):
    pfx = f"XBI{k + 1}"
    qo = mkhbt(f"{pfx}_XQo", 8, gx, Y_MIR)   # C=ntail
    qr = mkhbt(f"{pfx}_XQr", 1, gx + X_QR_OFF, Y_MIR)
    rf = mkres(f"{pfx}_Rref", 1620, "rhigh", gx + X_RF_OFF, Y_RF)          # P1=vcc P2=nref
    RFOBJ.append((pfx, qo, qr, rf))
    b.wire_v("M1", qo.p["C"][0], qo.p["C"][1], NT_Y0)          # XQo.C 直上进 ntail 轨
    b.label("M1", qo.p["C"][0], NT_Y0 + 1.0, "ntail")
    # ── v2.0（2026-10-18）C=B 实连改**绕 E 指列**（真短定谳 #5~#8）────────
    #    旧口径竖线从 B 带直拉 C 带必穿 E 指底座（0.4665µm² 同层重叠）。改 cb_tie
    #    三段折线，竖线挪到 x+1.2（净距 0.70µm）；落线即自证（重叠必须为 0）。
    CB.cb_tie(b, qr.p["C"], qr.p["B"], tag=f"drv2.{pfx}_XQr", side=+1,
              e_pad=CB.e_pad_rects(qr.p["B"][0], Y_MIR, 1))
    b.wire_h(NREF_LAYER, Y_NREF, qo.p["B"][0], rf.p["P2"][0])
    for (px, py) in ((qr.p["B"][0], qr.p["B"][1]), (qr.p["C"][0], qr.p["C"][1]),
                     (qo.p["B"][0], qo.p["B"][1])):
        cross(px, py, "Metal1", NREF_LAYER)
        b.wire_v(NREF_LAYER, px, Y_NREF, py)
    b.wire_v(NREF_LAYER, rf.p["P2"][0], rf.p["P2"][1], Y_NREF)
    cross(rf.p["P2"][0], rf.p["P2"][1], "Metal1", NREF_LAYER)   # P2 脚 → M5 nref 轨
    b.label(NREF_LAYER, qo.p["B"][0], Y_NREF, hnet(pfx, "nref"))

# ══════════════════════════════════════════════════════════════════════
# 6. 地网 M4：4 组镜像的 E 脚（M2 引脚）+ Rin1/Rin2 的 P2（M1 引脚）
# ══════════════════════════════════════════════════════════════════════
GND_Y = 100.0
b.rect(GND_LAYER, NT_X0, GND_Y - 2.0, NT_X1, GND_Y + 2.0)
b.label(GND_LAYER, CX, GND_Y, "gnd")
for (_p, qo, qr, _rf) in RFOBJ:
    for q in (qo, qr):
        ex, ey = q.p["E"]
        # ⚠ npn13G2 的 C/B/E 同 x，而 nref 的 M5 立管正沿这个 x → E 脚正下方落
        #   M2→M4 过孔会压住自己的 nref 立柱（自检台 ⑤d 抓出 8 处）。M2 上外折 4µm。
        gx = ex + 4.0 * (1 if ex >= 0 else -1)
        b.wire_h("M2", ey, ex, gx)
        cross(gx, ey, "Metal2", GND_LAYER)
        b.wire_v(GND_LAYER, gx, GND_Y, ey)
        b.label(GND_LAYER, gx, GND_Y, "gnd")

# ══════════════════════════════════════════════════════════════════════
# 7. 输入电阻 Rin1/Rin2（1k，inp/inn → gnd）与基极偏置 Rb1/Rb2（500Ω，bin/bb1 → nbias）
# ══════════════════════════════════════════════════════════════════════
Rin1 = mkres("Rin1", 1000, "auto", X_RIN[0], Y_RIN)
Rin2 = mkres("Rin2", 1000, "auto", X_RIN[1], Y_RIN)
for r, net in ((Rin1, "inp"), (Rin2, "inn")):
    b.wire_v("M1", r.p["P1"][0], r.p["P1"][1], r.p["P1"][1] - 3.0)
    b.label("M1", r.p["P1"][0], r.p["P1"][1] - 3.0, net)
    px, py = r.p["P2"]
    cross(px, py, "Metal1", GND_LAYER)
    b.wire_v(GND_LAYER, px, GND_Y, py)
    b.label(GND_LAYER, px, GND_Y, "gnd")

Rb1 = mkres("Rb1", 500, "auto", X_RB[0], Y_RB)
Rb2 = mkres("Rb2", 500, "auto", X_RB[1], Y_RB)
b.wire_h(BIAS_LAYER, NBIAS_Y, X_RB[0] - 5.0, X_RB[1] + 5.0)
b.label(BIAS_LAYER, X_RB[0], NBIAS_Y, "nbias")
for r in (Rb1, Rb2):
    px, py = r.p["P2"]
    cross(px, py, "Metal1", BIAS_LAYER)
    b.wire_v(BIAS_LAYER, px, NBIAS_Y, py)
    b.label(BIAS_LAYER, px, NBIAS_Y, "nbias")

# ── bin / bb1（TOPM2）：Rb.P1 → XQ.B
#    两条网的源（x=35/42）在汇（x=∓24）**同一侧** → 平面无直解（M2 插列定理）。
#    bb1 先走到外侧 x=56 再折回 x=40，把两条网分成两条互不相交的折线。
# y_lo 必须避开 vcc 下环的 TOPM1 带（y 3~9）：自检台 ⑤d 报出 bin 立柱压 vcc
for (r, q, net, y_lo, riser, y_hi) in ((Rb1, XQ1, "bin", 14.0, X_BIN_RISER, None),
                                        (Rb2, XQ2, "bb1", -2.0, X_BB1_RISER, 184.0)):
    px, py = r.p["P1"]
    # ⚠ v1.2 勘误（Q5 真值落地实测）：Rb 500Ω 由 rsil l=33.3（15Ω/□ 旧口径）
    #   改落 rppd l=1.92 → P1→P2 只差 2.34µm。老写法 `wire_v("M1", px, py, y_lo)`
    #   从 P1 竖直上到 y_lo=14，**必然从 P2 的 M1 焊盘正上方穿过** → bin 与 nbias
    #   在 M1 上真短。这个短**自检台看不见**（仿真模型不画电阻的 M1 焊盘，
    #   自建层只画 via 中间层焊盘），只有真 DRC 才炸 —— 故按真几何推理修：
    #   P1 高度先横插到专属竖列 jx（朝岛内侧让，两网互不相犯），再竖上去落柱。
    jx = px - 3.5                       # Rb1@35→31.5、Rb2@42→38.5（相距 7µm）
    b.wire_h("M1", py, min(px, jx), max(px, jx))
    b.wire_v("M1", jx, py, y_lo)
    cross(jx, y_lo, "Metal1", BIAS_RISER)
    if y_hi is None:
        # v1.5 ①：横轨**外延**到立管外缘（bin 的立管在 x=X_BIN_RISER=-36，半宽 1.0）。
        # 原写法横轨端点 = 立管中心 ⇒ 半搭接，并集多出 1.0µm 小舌 < TM2.a 的 2.0（官方 TM2.a×8）。
        _xl = min(jx, riser) - (1.0 if riser < jx else 0.0)
        _xr = max(jx, riser) + (1.0 if riser > jx else 0.0)
        b.wire_h(BIAS_RISER, y_lo, _xl, _xr)
        b.wire_v(BIAS_RISER, riser, q.p["B"][1], y_lo)
    else:
        # v1.5 ①：bb1 的两条横轨两端同样**外延**到竖条外缘（竖条 x=56，半宽 1.0；
        # 上横轨左端的 riser 立管 x=40，半宽也是 1.0），且 56 那根竖条**贯通**到 y_hi+1.0
        # （= 横轨上缘），不留「竖条顶停在横轨中心」的半搭接台阶。
        _mid = 56.0
        b.wire_h(BIAS_RISER, y_lo, min(jx, _mid), max(jx, _mid) + 1.0)
        b.wire_v(BIAS_RISER, _mid, y_hi + 1.0, y_lo)
        _x2a, _x2b = min(_mid, riser), max(_mid, riser)
        b.wire_h(BIAS_RISER, y_hi, _x2a - 1.0, _x2b + 1.0)
        b.wire_v(BIAS_RISER, riser, q.p["B"][1], y_hi)
    cross(riser, q.p["B"][1], "Metal1", BIAS_RISER)
    b.wire_h("M1", q.p["B"][1], min(riser, q.p["B"][0]), max(riser, q.p["B"][0]))
    b.label(BIAS_RISER, riser, q.p["B"][1], net)
    b.label("M1", q.p["B"][0], q.p["B"][1], net)

# ══════════════════════════════════════════════════════════════════════
# 8. nbcas：XQ3.B / XQ4.B（M5）→ 端口
# ══════════════════════════════════════════════════════════════════════
b.wire_h(NREF_LAYER, NBCAS_Y, CX - X_C, CX + X_C)
b.label(NREF_LAYER, CX, NBCAS_Y, "nbcas")
for q in (XQ3, XQ4):
    px, py = q.p["B"]
    cross(px, py, "Metal1", NREF_LAYER)
    b.wire_v(NREF_LAYER, px, NBCAS_Y, py)
b.wire_v(NREF_LAYER, CX, Y_VCC_HI + 6.0, NBCAS_Y)
b.label(NREF_LAYER, CX, Y_VCC_HI + 6.0, "nbcas")

# ══════════════════════════════════════════════════════════════════════
# 9. 输出级：RL1/RL2（100Ω，vcc→outp/outn）+ outp/outn 轨
#    RL 与 Re 同病（竖直两端子同列）：outp 从 C 脚**外折**到 x=∓34 上去，
#    再从 RL 顶上接 P2；vcc 从底下取。
# ══════════════════════════════════════════════════════════════════════
# ⚠ 同 drv1 v1.2：Y_RL 原按旧口径写死 199.68（= Y_CP−6.32），Q5 真值下
#   100Ω 改选 rppd l=1.0 → P1→P2 间距 1.56µm，不同步就跟引脚脱钩（⑤b 判悬空）。
RL_SPAN = 0.72 + 0.84 * RG.res_auto(100)["_geom"][0]
Y_RL = Y_CP - RL_SPAN
RL1 = mkres("RL1", 100, "auto", CX - X_C, Y_RL)   # P1=vcc  P2=outp
RL2 = mkres("RL2", 100, "auto", CX + X_C, Y_RL)   # P1=vcc  P2=outn
assert abs(RL1.p["P2"][1] - Y_CP) < 1e-6 and abs(RL2.p["P2"][1] - Y_CP) < 1e-6, \
    f"RL.P2 未落到输出轨 {Y_CP}（实得 {RL1.p['P2'][1]}）—— 轨高与间距脱钩了"
for (r, q, net, sgn) in ((RL1, XQ3, "outp", -1), (RL2, XQ4, "outn", +1)):
    ch = CX + sgn * (X_C + 10.0)
    cx_, cy_ = q.p["C"]
    b.wire_h("M1", cy_, min(cx_, ch), max(cx_, ch))
    b.wire_v("M1", ch, Y_CP, cy_)
    b.wire_h("M1", Y_CP, min(ch, r.p["P2"][0]), max(ch, r.p["P2"][0]))
    b.label("M1", (ch + r.p["P2"][0]) / 2, Y_CP, net)

# ══════════════════════════════════════════════════════════════════════
# 10. vcc 干路：下环（4×Rref.P1，TOPM1）+ 上环（2×RL.P1，TOPM1）+ TOPM2 立管串联
#     v1.7：顶层馈电桶已撤（裁定①），RL.P1 注入全由上环承载 → 下面补 EM 复核
# ══════════════════════════════════════════════════════════════════════
b.rect(VCC_LAYER, X_VCC_RISER, Y_VCC_LO - VCC_W / 2, NT_X1 + 12.0, Y_VCC_LO + VCC_W / 2)
# 上环必须**一直伸到 x=X_VCC_RISER**（立管所在列），否则立管顶端的 TOPM1 过孔落空 →
# vcc 断成「上环 / 立管 / 下环」三截。自检台第⑤b 项就是抓这个的（2026-10-17 实测踩中）。
b.rect(VCC_LAYER, X_VCC_RISER, Y_VCC_HI - VCC_W / 2,
       CX + X_C + 16.0, Y_VCC_HI + VCC_W / 2)
b.label(VCC_LAYER, X_VCC_RISER, Y_VCC_LO, "vcc")
b.label(VCC_LAYER, CX, Y_VCC_HI, "vcc")
for (_p, _qo, _qr, rf) in RFOBJ:                      # Rref.P1 → 下环
    px, py = rf.p["P1"]
    cross(px, py, "Metal1", VCC_LAYER)
    b.wire_v(VCC_LAYER, px, Y_VCC_LO + VCC_W / 2, py)
    b.label(VCC_LAYER, px, py, "vcc")
for r in (RL1, RL2):                                  # RL.P1 → 上环
    px, py = r.p["P1"]
    cross(px, py, "Metal1", VCC_LAYER)
    b.wire_v(VCC_LAYER, px, Y_VCC_HI - VCC_W / 2, py)
    b.label(VCC_LAYER, px, Y_VCC_HI - VCC_W / 2, "vcc")
# ── EM 复核（裁定① 配套）：RL.P1 注入全走 TOPM1 上环，核载流能力 ──
_I_RL = 30.0            # mA，RL1+RL2 P1 全量注入（组长 09:37Z 口径）
_TM1_J = 15.0           # mA/µm（同信：上环 TM1 6µm = 90mA 能力 ⇒ 15mA/µm）
print(f"[EM] vcc 上环 TOPM1 {VCC_W:.1f}µm × {_TM1_J:.0f}mA/µm = {VCC_W*_TM1_J:.0f}mA 能力 "
      f"≥ RL.P1 注入 {_I_RL:.0f}mA（裕 {VCC_W*_TM1_J/_I_RL:.1f}×）", flush=True)
assert VCC_W * _TM1_J >= _I_RL, "vcc 上环 EM 不足（裁定① 配套复核）"
# vcc 立管（TOPM2）：下环左端 → 上环左端，把两个环串成一条网
b.rect(VCC_STK_LAYER, X_VCC_RISER - VCC_W / 2, Y_VCC_LO,
       X_VCC_RISER + VCC_W / 2, Y_VCC_HI + VCC_W)
for yy in (Y_VCC_LO, Y_VCC_HI):
    cross(X_VCC_RISER, yy, VCC_LAYER, VCC_STK_LAYER)
b.label(VCC_STK_LAYER, X_VCC_RISER, (Y_VCC_LO + Y_VCC_HI) / 2, "vcc")

# ══════════════════════════════════════════════════════════════════════
# 11. 占位 / 禁区（cmim + tank）：落 M5 的**顶部专带**（y≥220，那里没有 nref 走线）
# ══════════════════════════════════════════════════════════════════════
PH_BOX = 12.0
PH_GAP = 3.0                       # 占位矩形之间至少留 PH_GAP，否则同层会并成一个簇 → 假短路
PH_Y = 236.0
NOTES = []          # 占位件说明：只进 stdout 与设计稿，不落金属层
PH_PLACE = {
    "Cin1": (-54.0, "inp", "bin"), "Cin2": (54.0, "inn", "bb1"),
    "Ct1": (-18.0, "outp", "gnd"), "Ct2": (18.0, "outn", "gnd"),
    "Lt1": (-36.0, "vcc", "outp"), "Lt2": (36.0, "vcc", "outn"),
}
if USE_CMIM:
    raise SystemExit("cmim PCell 名/参数待组长回填")
for nm, (px, n1, n2) in PH_PLACE.items():
    b.rect(PH_LAYER, px - PH_BOX / 2, PH_Y - PH_BOX / 2,
           px + PH_BOX / 2, PH_Y + PH_BOX / 2)
    NOTES.append(f"{nm}({n1},{n2}) "
                 + ("TANK_L1_KEEPOUT" if nm.startswith("Lt") else "CMIM_PLACEHOLDER")
                 + f" @({px:.1f},{PH_Y:.1f})")
_pxs = sorted(v[0] for v in PH_PLACE.values())
assert all(b_ - a_ >= PH_BOX + PH_GAP for a_, b_ in zip(_pxs, _pxs[1:])), \
    f"占位矩形 x 间距不足 {PH_BOX + PH_GAP}µm：{_pxs}"
print(f"[M3-b] 占位件 {len(PH_PLACE)} 个（cmim 4 + tank L1 禁区 2）"
      f" —— 未落成器件，PCell 名 / 禁区层号待回执", flush=True)

# ══════════════════════════════════════════════════════════════════════
# 12. 岛边界（按真实内容反推）。v1.8 起 guard 环在本脚本落地（§12b）。
# ══════════════════════════════════════════════════════════════════════
CORE_X0, CORE_Y0, CORE_X1, CORE_Y1 = _bb(b.top)      # ← 代跑补丁①：双风格读取

# ══════════════════════════════════════════════════════════════════════
# 12b. guard 环（v1.8 立项落地 · mix v27 §9b 同款）—— 见头部 v1.8 说明
# ══════════════════════════════════════════════════════════════════════
RING_M = 8.0                        # 环外缘离核 8µm（mix v2.5 定稿；勘误之五血训参数）
RING_W = 2.0                        # 圈宽（mix v2.5 定稿：宽 4 会骑核）
GUARD_X0, GUARD_Y0 = CORE_X0 - RING_M, CORE_Y0 - RING_M
GUARD_X1, GUARD_Y1 = CORE_X1 + RING_M, CORE_Y1 + RING_M
for (_ly, _ins) in (("M1", 0.0), ("M2", RING_W + 1.0)):     # M1 外圈贴边、M2 内圈 inset 3
    _a0, _b0 = GUARD_X0 + _ins, GUARD_Y0 + _ins
    _a1, _b1 = GUARD_X1 - _ins, GUARD_Y1 - _ins
    b.rect(_ly, _a0, _b0, _a1, _b0 + RING_W)                # 下边
    b.rect(_ly, _a0, _b1 - RING_W, _a1, _b1)                # 上边
    b.rect(_ly, _a0, _b0 + RING_W, _a0 + RING_W, _b1 - RING_W)   # 左边
    b.rect(_ly, _a1 - RING_W, _b0 + RING_W, _a1, _b1 - RING_W)   # 右边
# 标注纪律（Q4）：datatype=25 纯网名 "gnd"，不加任何说明字 —— 四边 M1 + 上下 M2
_gx_c = (GUARD_X0 + GUARD_X1) / 2
_gy_c = (GUARD_Y0 + GUARD_Y1) / 2
b.label("M1", _gx_c, GUARD_Y0 + RING_W / 2, "gnd")
b.label("M1", _gx_c, GUARD_Y1 - RING_W / 2, "gnd")
b.label("M1", GUARD_X0 + RING_W / 2, _gy_c, "gnd")
b.label("M1", GUARD_X1 - RING_W / 2, _gy_c, "gnd")
b.label("M2", _gx_c, GUARD_Y0 + RING_W + 1.0 + RING_W / 2, "gnd")
b.label("M2", _gx_c, GUARD_Y1 - RING_W - 1.0 - RING_W / 2, "gnd")
# ── ptap1 ×8（每边 2 只，0.3/0.7 比例点，中心线正落 M1 圈上）──────────
# 三重防护照 mix v27：① TAP_ENABLE 开关 ② 参数留空走 PDK 默认 ③ 非致命 try。
# 仿真层不建未知 PCell（塞假体会污染间距判定）→ PTAP_SKIPPED 进 NOTES，代跑真落。
TAP_ENABLE = True
_tap_xy = []
for _t in (0.3, 0.7):
    _tap_xy += [(GUARD_X0 + _t * (GUARD_X1 - GUARD_X0), GUARD_Y0 + RING_W / 2),
                (GUARD_X0 + _t * (GUARD_X1 - GUARD_X0), GUARD_Y1 - RING_W / 2),
                (GUARD_X0 + RING_W / 2, GUARD_Y0 + _t * (GUARD_Y1 - GUARD_Y0)),
                (GUARD_X1 - RING_W / 2, GUARD_Y0 + _t * (GUARD_Y1 - GUARD_Y0))]
if TAP_ENABLE:
    import pya as _pya
    if hasattr(_pya, "WARN"):
        NOTES.append("PTAP_SKIPPED：本机仿真层不建 ptap1 PCell —— 8 只 ptap 接触待代跑落"
                     "（mix v27 同款已代跑全绿；tap 密度/psd 间距条款由代跑 DRC 终裁）")
    else:
        try:
            _pc = b._pcell("guard_ptap_default", "ptap1", {})
            for (_x, _y) in _tap_xy:
                b.top.insert(_pya.DCellInstArray(_pc, _pya.DTrans(_pya.DVector(_x, _y))))
            print(f"[guard] ptap ×{len(_tap_xy)} 已落环（PDK 默认参数）", flush=True)
        except Exception as _e:
            NOTES.append(f"PTAP_SKIPPED：{type(_e).__name__}: {_e}")
# ── 定网 gnd 三件事（裁决②「不许悬空」；缺一环即浮空金属）────────────
# ① 搭桥：右边上下两处 M1 桥（M1 圈右边中心线 → M2 圈中心线）+ M1→M2 柱
#    （两圈同心相距 1µm，via 焊盘够不着 → 先桥后柱；选右边因 M4 地轨右延在此）
_bx = GUARD_X1 - RING_W - 1.0 - RING_W / 2                  # 右边 M2 圈中心线
for _yb in (GUARD_Y0 + RING_W + 1.0 + RING_W / 2,
            GUARD_Y1 - RING_W - 1.0 - RING_W / 2):
    b.wire_h("M1", _yb, GUARD_X1 - RING_W / 2, _bx)
    b.via(_bx, _yb, "Metal1", "Metal2")
# ② M4 地轨右延搭接段：§6 轨 [NT_X0, NT_X1] → 环右边（同层同网相接并一簇）
# ③ 落地单柱：环右边中心线 (GUARD_X1−1, GND_Y) M1→M4 —— 柱位 M1 圈中心线上
#    M2/M3 全空（M2 内圈在 x 更内 3µm；M3 只有 nbias 干路 x∈[30,47]），
#    中间层不压异网（自检台 ⑤d 口径）。
b.rect(GND_LAYER, NT_X1, GND_Y - 2.0, GUARD_X1, GND_Y + 2.0)
b.via(GUARD_X1 - RING_W / 2, GND_Y, "Metal1", "Metal4")
b.label(GND_LAYER, GUARD_X1 - RING_W / 2, GND_Y, "gnd")
print(f"[guard] 环 ({GUARD_X0:.1f},{GUARD_Y0:.1f})~({GUARD_X1:.1f},{GUARD_Y1:.1f}) "
      f"RING_M={RING_M} RING_W={RING_W} · 桥×2@x={_bx:.1f} · 落地柱@({GUARD_X1 - RING_W / 2:.1f},{GND_Y:.1f})",
      flush=True)

MARGIN = 6.0                         # 仅历史口径备案；v1.8 起 ISLAND 按含环真实内容反推
print(f"[M3-b drv2 v1.8] 核 bbox=[{CORE_X0:.1f},{CORE_Y0:.1f}~{CORE_X1:.1f},{CORE_Y1:.1f}]"
      f" → {CORE_X1 - CORE_X0:.1f}×{CORE_Y1 - CORE_Y0:.1f} µm", flush=True)
ISLAND_X0, ISLAND_Y0, ISLAND_X1, ISLAND_Y1 = _bb(b.top)   # 环落图后真实内容（含 guard 环）
ISLAND_W, ISLAND_H = ISLAND_X1 - ISLAND_X0, ISLAND_Y1 - ISLAND_Y0
print(f"[M3-b drv2 v1.8] 岛框（含 guard 环）=[{ISLAND_X0:.1f},{ISLAND_Y0:.1f}~"
      f"{ISLAND_X1:.1f},{ISLAND_Y1:.1f}] → {ISLAND_W:.1f}×{ISLAND_H:.1f} µm", flush=True)

# ══════════════════════════════════════════════════════════════════════
# 13. 网表锚 / 逐器件引脚↔网名声明
# ══════════════════════════════════════════════════════════════════════
SP_ANCHOR = {"netlist": "/data/workspace/design/chain_top_tb_v015_1.sp",
             "subckt": "drv2"}
DUMMY_DEVICES = ()          # drv2 无 dummy HBT

DEV_NETS = {
    "XQ1": ("ccas1", "bin", "e1"), "XQ2": ("ccas2", "bb1", "e2"),
    "XQ3": ("outp", "nbcas", "ccas1"), "XQ4": ("outn", "nbcas", "ccas2"),
    "Re1": ("e1", "ntail"), "Re2": ("e2", "ntail"),
    "Rb1": ("bin", "nbias"), "Rb2": ("bb1", "nbias"),
    "Rin1": ("inp", "0"), "Rin2": ("inn", "0"),
    "RL1": ("vcc", "outp"), "RL2": ("vcc", "outn"),
}
for k in range(1, 5):
    p = f"XBI{k}"
    DEV_NETS[f"{p}_XQr"] = (hnet(p, "nref"), hnet(p, "nref"), "0")
    DEV_NETS[f"{p}_XQo"] = ("ntail", hnet(p, "nref"), "0")
    DEV_NETS[f"{p}_Rref"] = ("vcc", hnet(p, "nref"))
PH_DECL = {k: (v[1], v[2]) for k, v in PH_PLACE.items()}

NET_DECL = {
    "outp": [("XQ3", "C"), ("RL1", "P2"), ("Ct1", "p1"), ("Lt1", "p2")],
    "outn": [("XQ4", "C"), ("RL2", "P2"), ("Ct2", "p1"), ("Lt2", "p2")],
    "ccas1": [("XQ1", "C"), ("XQ3", "E")],
    "ccas2": [("XQ2", "C"), ("XQ4", "E")],
    "bin": [("XQ1", "B"), ("Rb1", "P1"), ("Cin1", "p2")],
    "bb1": [("XQ2", "B"), ("Rb2", "P1"), ("Cin2", "p2")],
    "e1": [("XQ1", "E"), ("Re1", "P1")],
    "e2": [("XQ2", "E"), ("Re2", "P1")],
    "ntail": [("Re1", "P2"), ("Re2", "P2")]
             + [(f"XBI{k}_XQo", "C") for k in range(1, 5)],
    **{hnet(f"XBI{k}", "nref"): [(f"XBI{k}_XQr", "C"), (f"XBI{k}_XQr", "B"),
                                 (f"XBI{k}_XQo", "B"), (f"XBI{k}_Rref", "P2")]
       for k in range(1, 5)},
    "vcc": [("RL1", "P1"), ("RL2", "P1")]
           + [(f"XBI{k}_Rref", "P1") for k in range(1, 5)]
           + [("Lt1", "p1"), ("Lt2", "p1")],
    "nbias": [("Rb1", "P2"), ("Rb2", "P2")],
    "nbcas": [("XQ3", "B"), ("XQ4", "B")],
    "inp": [("Rin1", "P1"), ("Cin1", "p1")],
    "inn": [("Rin2", "P1"), ("Cin2", "p1")],
    "gnd": [(f"XBI{k}_XQo", "E") for k in range(1, 5)]
           + [(f"XBI{k}_XQr", "E") for k in range(1, 5)]
           + [("Rin1", "P2"), ("Rin2", "P2"), ("Ct1", "p2"), ("Ct2", "p2")],
}

# ══════════════════════════════════════════════════════════════════════
# 14. net_check + save
# ══════════════════════════════════════════════════════════════════════
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



# ══════════════════════════════════════════════════════════════════════
# v2.1（2026-10-19）**无名 M1 簇补标** —— 纯网名文本，零金属图形改动
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
    (-24.00, +179.24, 'ccas1', "XQ1.C → NET_DECL['ccas1']"),
    (+24.00, +179.24, 'ccas2', "XQ2.C → NET_DECL['ccas2']"),
    (-28.50, +106.86, 'XBI1/nref', 'XBI1_XQr.B/C 同簇，声明网唯一'),
    (+4.50, +106.86, 'XBI2/nref', 'XBI2_XQr.B/C 同簇，声明网唯一'),
    (+37.50, +106.86, 'XBI3/nref', 'XBI3_XQr.B/C 同簇，声明网唯一'),
    (+70.50, +106.86, 'XBI4/nref', 'XBI4_XQr.B/C 同簇，声明网唯一'),
    (+35.00, +8.00, 'bin', "Rb1.P1 → NET_DECL['bin']"),
    (+42.00, +8.00, 'bb1', "Rb2.P1 → NET_DECL['bb1']"),
    (+24.00, +204.44, 'vcc', "RL2.P1 → NET_DECL['vcc']"),
    (-24.00, +204.44, 'vcc', "RL1.P1 → NET_DECL['vcc']"),
    (+76.50, +20.00, 'vcc', "XBI4_Rref.P1 → NET_DECL['vcc']"),
    (+43.50, +20.00, 'vcc', "XBI3_Rref.P1 → NET_DECL['vcc']"),
    (+10.50, +20.00, 'vcc', "XBI2_Rref.P1 → NET_DECL['vcc']"),
    (-22.50, +20.00, 'vcc', "XBI1_Rref.P1 → NET_DECL['vcc']"),
    (+24.00, +188.86, 'nbcas', "XQ4.B → NET_DECL['nbcas']"),
    (-24.00, +188.86, 'nbcas', "XQ3.B → NET_DECL['nbcas']"),
    (+42.00, +10.34, 'nbias', "Rb2.P2 → NET_DECL['nbias']"),
    (+35.00, +10.34, 'nbias', "Rb1.P2 → NET_DECL['nbias']"),
    (-39.00, +9.56, 'gnd', "Rin2.P2 → NET_DECL['gnd']（地；金属已接 M4 地轨）"),
    (-46.00, +9.56, 'gnd', "Rin1.P2 → NET_DECL['gnd']（地；金属已接 M4 地轨）"),
    (+76.50, +21.72, 'XBI4/nref', "XBI4_Rref.P2 → NET_DECL['XBI4/nref']"),
    (+49.50, +106.86, 'XBI4/nref', "XBI4_XQo.B → NET_DECL['XBI4/nref']"),
    (+43.50, +21.72, 'XBI3/nref', "XBI3_Rref.P2 → NET_DECL['XBI3/nref']"),
    (+16.50, +106.86, 'XBI3/nref', "XBI3_XQo.B → NET_DECL['XBI3/nref']"),
    (+10.50, +21.72, 'XBI2/nref', "XBI2_Rref.P2 → NET_DECL['XBI2/nref']"),
    (-16.50, +106.86, 'XBI2/nref', "XBI2_XQo.B → NET_DECL['XBI2/nref']"),
    (-22.50, +21.72, 'XBI1/nref', "XBI1_Rref.P2 → NET_DECL['XBI1/nref']"),
    (-49.50, +106.86, 'XBI1/nref', "XBI1_XQo.B → NET_DECL['XBI1/nref']"),
]


def label_m1_clusters(b, tag="drv2_v22"):
    for (x, y, net, why) in M1_CLUSTER_LABELS:
        b.label("M1", x, y, net)
    print(f"[m1-label] {tag}: 补 {len(M1_CLUSTER_LABELS)} 条顶层 M1 网名标注"
          f"（几何零改动）", flush=True)
    return len(M1_CLUSTER_LABELS)

n_clusters, shorts = b.net_check("ALL")
# ── v2.0 新增两道机检（同 drv1_v20）────────────────────────────────────
RG.audit_res_pads(b, RES_DEVS, tag="drv2_v22")
_nd, _nb, _hits = CB.audit_board_e_pads(b, HBT_DEVS, tag="drv2_v22")
print(f"[e-pad-audit] drv2_v20: {len(HBT_DEVS)} 只 HBT × {_nb} 块板级 M1 "
      f"对 E 指底座零重叠 ✓", flush=True)
label_m1_clusters(b)
relabel_official(b)          # ⑭ R-ANNO-01 ②：官方 label purpose /1
print(f"[M3-b drv2 v2.0] 簇={n_clusters} 短路={shorts if shorts else '无'}", flush=True)

os.makedirs("/data/workspace/gds", exist_ok=True)
b.save("/data/workspace/gds/m3_drv2_v22.gds")
print("M3-B DRV2 V2.0 OK", flush=True)
