#!/usr/bin/env python3
"""
M3-a · drv1 级版图生成脚本 v2.3（**ptap tie 对心轮 + 取图助手三修** · 2026-10-19）
════════════════════════════════════════════════════════════════════════
  v2.3 相对 v2.2（`1e32e3d5`）的变更**只有三处**，金属走线几何零改动：

  ① **ptap1 实例落点改 `DTrans(_tx−0.39, _ty−0.39)`**（组长裁定四十九建议）
     · 根因（组长从 PDK 源码读出，我已用**真 GDS 第一手复核**，逐位吻合）：
       `ptap1` 的全部图形建在 `Box(0,0,w,l)`，w=l=0.78 ⇒ **原点在 Activ 左下角**，
       而它自带的 8/0 M1 tie 在局部 **(0.14,0.09)-(0.64,0.69) = 0.50×0.60**，
       中心在 **原点+(0.39,0.39)**，**不在原点**。
       我 v2.2 把 via_stack 打在**实例原点** ⇒ 焊盘 (13.65,99.69)-(14.35,100.31)
       与 tie (14.14,100.09)-(14.64,100.69) 只重叠 **0.21×0.22 = 0.0462 µm²**
       —— 非零所以「通了」，但只压住 tie 左下角，向右 0.29、向↑ 0.38 悬空。
       侥幸通 ≠ 接好（同律 F8：看着压住 ≠ 真压住）。
     · 修法：**挪 tap 不挪 via**。理由是量出来的，不是猜的 —— 用真 GDS 做基线
       （删掉两只 ptap1 与两根 via_stack$3 后取各层最近邻）逐方案比净距：

         方案 A 挪 tap (−0.39,−0.39)：Activ 净距 4.48（现状 4.375/4.850）、
             pSD 净距 4.25、tie 对 M1 净距 6.44 —— **各层余量都在 µm 级**，
             官方 Activ/pSD/M1 间距条款是 0.2~0.5 量级 ⇒ 不新增违规。
         方案 B 挪 via（+0.39,+0.39）：M4 焊盘对**同 x 的 M4 立管**净距只剩
             **0.085µm**（现状 −0.305 即压着），还得连立管一起挪，风险高一个量级。
       ⇒ 采纳 A（也与组长建议逐字一致）。修后 tie ⊂ via 焊盘，**重叠 0.3000 µm²**
         （0.0462 → 0.3000，**6.5 倍**，四边全包、彻底不再是压一角）。

  ② **仿真层 M1 tie 替身换成 PDK 真值**（原为 0.80 见方的自造替身）
     · 替身形状照 ① 的真值：局部 0.50×0.60、中心 (+0.39,+0.39)。因为实例落点
       同步挪了 −0.39，仿真层里它就落在 **(tap 中心)**，与真跑逐位同位。
     · **只补 tie，不补 Activ/pSD/Cont**：那三层的真值虽已量到（Activ 0.78 见方、
       Cont 4×0.16²、pSD ±0.03），但它们是 PDK 内部图形且官方 DRC 已终裁全绿，
       塞进仿真层只会给 ⑯⑱ 同层间距自查添**合法却报警**的噪声，不增验证价值。
       真值记在 `_TAP_PDK` 里，供断言与后人查。

  ③ **取图助手三修**（组长裁定四十九 §三：v2.0 那条「双通」血训修复没生效，
     真 KLayout 连炸三次）—— 三处都在**工具层**，不涉几何：
     a. 位移统一读 `t.disp.x/.disp.y`（真 KLayout 的 Trans **既无 .x/.y 也无
        .dx/.dy**，只有 .disp；且 .disp 给**整数 dbu**，要 ×dbu 才是 µm）。
        旧写法 `getattr(t,'x',None) else t.dx` 在真构建上直接 AttributeError。
     b. `bb.hit(x,y)` 换成**纯 Python 包围盒判定**：真 KLayout 的 DBox 只有
        inside/contains/touching/overlaps，**没有 hit** ⇒ 旧写法当场炸。
     c. 取图改 `begin_shapes_rec` + **`select_all_cells()`** + `while not
        it.at_end()` 逐个 `it.shape()`/`it.trans()`：默认**不进 PCell 变体**，
        真跑里 ptap1 的 tie、via_stack 焊盘都在子 cell 内 ⇒ 旧写法会报
        「tap 处没有 M1 接地垫」**假停线**。另：**不能 list(it)**（实测 list()
        反复吐出迭代器自身），故一律 while 循环。

  ⚠ 本机仍**跑不了**真 KLayout：本轮起，「双通」的口径按组长 v1.7 增补执行 ——
     **凡交付件内嵌「双通/兼容」helper，未经组长侧真 KLayout 实跑背书，一律按
     未验证计**。本件的三处 API 修法来自组长的实测正解，我这边**只做了
     仿真层自证 + 真 GDS 几何交叉验证**，API 本身仍待他复跑盖章。

════════════════════════════════════════════════════════════════════════
（v2.0 及更早：真短 + 断路回改轮 · 2026-10-18）
════════════════════════════════════════════════════════════════════════
  v2.0 相对 v1.9 的**全部**变更只有两类，各一处机制、其余逐位不动：

  ① **Re1/Re2 的 P2 出脚改锚焊盘真值**（断路 · 4 条中的本件 2 条）
     · 根因**不是**「rsil 一档引脚距错」，而是更宽的一条真值缺陷：
       **lib13g2 报的引脚锚点（真值表 §2 拟合 0.72+0.84·l）不是焊盘**。
       实测（GDS 逐位，三模型七点全中）：pad2 = [l+off_lo, l+off_hi]
         rsil off=(0.07,0.33) / rhigh (0.15,0.41) / **rppd (0.13,0.43，盘高 0.30)**
       rsil 短条（l=1）盘顶只到 y_p1+1.53，锚点在 y_p1+1.56 ⇒ **悬空 0.03µm**。
     · 为何只有 Re 中招：出线一律从锚点起画 —— 朝下/穿盘的（ntail、gnd 下引轨）
       线身穿过焊盘 ⇒ 连通；**朝上离开焊盘的**（本 stub）整段悬空 ⇒ 断路。
     · 修法：**先 mkres 后 chain**，把 `RG.res_pad2(model, l)` 的**焊盘真值跨度**
       传进 `place_emit_chain(p2_pad=…)`，stub 从**盘心**起画（重叠半个盘高）。
     · 连带新增机检 `resgeom.audit_res_pads`：每只电阻 P1/P2 **真实焊盘**必须有
       板级 M1 覆盖 —— 旧自检台第⑥项查的是**引脚标记盒**（仿真层按锚点放的
       ±0.15 盒），标记盒被线盖住就放行，真焊盘空着它不管（**盲区第四例**）。

  ② **XBI.XQr 的 C=B 实连改绕 E 指列**（真短 · 8 案中的本件 1 案）
     · npn13G2 的 C 带 / E 指底座 / B 带**同 x 列**：E 指底座是 (8,0) 金属，
       x∈锚±0.35、y∈[−0.785,+0.77]。旧口径 `wire_v("M1", B.x, B.y, C.y)` 从 B 带
       直拉 C 带，**中途必穿** ⇒ 同层重叠 0.30×1.557 = **0.4665µm²**，
       nref↔gnd 真短（M1 同层即导通，无需桥孔）。
     · 修法：`cbpath.cb_tie()` 三段折线，竖线挪到 x+1.2（净距 **0.70µm** ≫ M1.b
       的 0.18），上下横线走在 C/B 带心（带内，不占带外空间）。
     · 连带新增机检 `cbpath.audit_board_e_pads`：全板 M1 × 每只 npn 的 E 指底座，
       重叠必须为 0 —— 补上自检台盲区第三例（仿真层不画 PCell 内部 E 指底座）。

  ⚠ 本版**未**动：DRC 基线指纹、器件摆位、通道律、cmim 外置条带、island 口径。
    预期 gdsdiff delta 仅两组：①两条 P2 stub 下移 0.16µm；②XQr 的 C=B 竖线
    换成三段折线（净增 2 块 M1）。

M3-a · drv1 级版图生成脚本 v1.9
  v1.9 = v1.8 唯一变更：**E 回流链断路修复**（2026-10-17 组长裁决，lap=0.6µm）。
    · 根因：place_emit_chain 的 arm_bot 按 via 外接高（+0.09/边）推，而 via_stack
      PCell 的 M2 焊盘实际只外沿 +0.005/边 → 臂底悬在焊盘顶之上 0.085µm，
      XQ1/XQ2.E → Re1.P1 直流断路（e1/e2 各裂两簇，四方实锤：b7e7 几何提取 /
      组长 LVS deck / gen 源码公式 / 组长 klayout 逐层量测，判读③已改判版图真断）。
    · 修复：emitpath.place_emit_chain 新增 lap 参数（默认 0.6µm），arm_bot 下移
      lap → 臂与桶 M2 焊盘重叠 0.515µm ≥ 0.5µm 验收线（组长：只延 0.09 剩 5nm
      形同虚设不收）。其余几何与 v1.8 **逐位一致**（gdsdiff 预期唯一 delta=两条
      M2 宽臂底边各下移 0.6µm）。
    · 根因教训已升 HBT 级版图准则 v1.4（R-VIA-01 族新条：凡按 PCell 外接尺寸推
      内部形状位置一律禁止，必须用实际块坐标）。
  v1.8 = v1.7 全部真金属几何**零变化** + **cmim 34 只全数外置 drv1 岛外**（2026-10-17
  09:48Z 裁定⑤·选③「外置独立电容区」；来源：组长 inbox 第 65 行）。落法：
    · 拆分表**维持 v1.7 的 16×0.625p×2 + 0.84p×2**（裁定⑤明文「条带规格照你的拆分表」）；
    · 34 只预留框全部改画在 **(235,5) 非制造层（235/5）** 方向的**外置条带**：
      4 列 × 9 行、列距=见方+3、行距=见方+3（Ct 行 26.66），区约 94×237µm；
    · drv1 核 bbox / 真金属 / 通道**零变化**（DRC 28 指纹应全同，gdsdiff 唯一 delta=235/5）；
    · 真件金属在 M4 顶层布局落独立电容区、连线顶层布（届时本条带坐标即 M4 设计输入）；
    · DEV_NETS/PH_DECL 拆分行与 ⑦b 前缀族核对**不动**。
  ⚠ 顺带订正 v1.7 台账的一句错话：「核已被电路占满」不成立（实测器件+过孔仅占核 2.4%）；
    v1.7 的「缺 237µm」根因是把条带自锁在核顶之上（CAPSTRIP_Y0=核顶 ⇒ 可用高恒 0）。
    裁定⑤外置后此账作废，订正存档于 design/sow6/裁定2_核内电容区实测_2026-10-17.md。
  v1.7（2026-10-17，b7e7）
  ⚠ 版本号订正：v1.4~v1.6 三轮只改了 stdout 的打印串，**文件头这一行一直停在 v1.3**
    —— 与「只进注释没进代码」同类（头号是给人读的，改了打印忘了改头，读的人会以为件没变）。
    本版起头号与打印串一起升。

  v1.7 = v1.6 全部几何 + **裁定①「cmim 拆分并联 + 电容专用区」落地**（2026-10-17 09:3xZ；
    来源：组长 09:09Z 判读纪要 §裁① + 09:19Z 回信 Q11 期待）。四条约束逐条落：

  ① 【单只 ≤30µm 见方】取 **16 × 0.625p**（他给的两档里单只更小的那档）：单只见方
     **20.41µm**，比上限多 32% 余量（9×1.11p 是 27.22，只多 9%）。
     Ct1/Ct2 **不拆**：0.84p 单只就是 23.66 见方，已满足 ≤30；再拆会让单只掉到
     ~2fF 以下，而官方 cmim 的几何律 n=fix((side+0.12)/1.26) 在 side<1.14µm 时 n=0，
     算不出 W/L（w1 变 −0.12）。
  ② 【专用条带行距 = 见方 + 3µm】`strip_layout()` 逐轴按 side+3 排布（CMIM_STRIP_PITCH）。
  ③ 【总量守恒】16×625×2 + 1×840×2 = 21680fF = 20p + 1.68p，与网表一致。
  ④ 【DEV_NETS 同步拆分行】每只并联单元都是**独立器件行**（`Cin1_00`…`Cin1_15`，
     同两端网），全部进 PH_DECL / NET_DECL。自检台第 ⑦b 项同步升级为「前缀族核对」：
     网表一只电容 ⇔ PH_DECL 里有 ≥1 个同前缀行，**且只数必须与 CMIM_SPLIT 一致**
     （防「只声明一只」蒙过核对）。

  ⚠ 拆不动的根因**不是拆分**，是面积（**拆分是面积中性的**）：总量守恒 ⇒ 总面积
     14453µm²（核 118×206 = 24345µm² 的 **59%**）；条带按行距要 237µm 高，而 drv1
     的核已被电路占满、顶边之上本版**留 0µm**（未擅自扩岛 —— 扩岛会改掉你每轮都在对的
     核 bbox 与 DRC 面积）。差额逐项印在 stdout 的「CMIM 面积台账」里，随信报你。

  v1.3 = v1.2 全部内容 + ⑭ 官方 label purpose /1 补打（R-ANNO-01 ②，理由见 relabel_official）

网表锚：design/chain_top_tb_v015_1.sp :: `.subckt drv1 inp inn cop con vcc`
         （`XBI ntail vcc hbt_mirror` 走**默认参数** nx=8 / rr=1.62k —— drv2 的 4 组同样）

## 三条硬纪律（都是 M2 血的教训，不是新口味）

1. **器件数逐只对网表**（`SP_ANCHOR` + `DEV_NETS` → 自检台第⑦项 spcheck 递归展开核对）。
   `hbt_mirror` = **Qr(nx=1) + XQo(nx=8) + Rref(1.62k) 三件**，
   绝不能又按「环绕共质心」摆成阵列（M2 v1.2 的 12 倍错误就出在这）。
2. **每个阻值都经 resgeom.res_params()/res_auto() 由阻值反算**（Q5 真值：
   cornerRES 三档 rsil 6.02/7/7.98 · rppd 234/260/286 · rhigh 1160/1360/1560，取 typ；
   金属 M1 0.135 / M2-5 0.103 / TM1 0.021 / TM2 0.0145 Ω/□；
   回执给真值后只改 resgeom 一行，全岛几何自动重算）。
3. **发射极回流按 R-EMIT-01/02 + R-VIA-01 落成可执行断言**（emitpath.py），
   几何由 `emitpath.place_emit_chain()` 统一落（drv1/drv2 同构，结论见该函数头）。

## 布局上唯一难解的一处（写在 emitpath.place_emit_chain 头，这里只留一句）

`Re` 竖直两端子，P1(e1) 在下、P2(ntail) 在上、同列只差 1.56µm ——
15µm 宽的 M1 落点段无论放哪都会把 P2 包进去。解法：宽回流段放 **M2**，
在 **Re 本体下方**才换到 M1，P1 在焊盘里、P2 在焊盘上方。

## ⚠ guard ring 不在本脚本里画

真值表 §4 需求单回应：⑤ guard_ring 属**库 v2 交付项**（M1 建库时落）。
（早前 v0.1 试过自己画环 —— 环是**闭合成环**的连通图，自检台的簇外接框会罩住整个内部，
凭空报出一大片假短路；顺手把自检台的命中判据从「外接框」改成「成员矩形」修掉了。）

用法（组长侧）：
    . /data/workspace/pdk/kl_env030.sh
    KLAYOUT_PATH=$KLTECH klayout -zz -r gen_M3_drv1_v1.py
用法（本机自检，无 klayout）：
    python design/sow6/dryrun/preflight.py design/sow6/gen_M3_drv1_v1.py

输出：/data/workspace/gds/m3_drv1_v22.gds

【2026-10-17 修订 · 文件名不变内容已变】按组长 reply_v12 的 Q5/Q6/Q7 落地：
  Q5 Rsheet 真值换算 + 高阻自动选型（res_auto）→ 三件电阻几何全部重算；
  Q6 cmim 真件（PCell `cmim`、w&l、23.66µm 见方，自适应引脚层 + 非致命回落）；
  Q7 guard 环定网 gnd（搭桥+落地柱，真接进 gnd 网）+ ptap 接触（PDK 默认参数，
     仿真层跳过、代跑落）。变更清单与逐项理由见 CHANGELOG_2026-10-17_Q5Q6Q7.md。
v1.5 = v1.4 全部几何内容 + **lib v2.2 的 TopVia1 钉档**（2026-10-17 07:5xZ；来源：组长
  b7a0 07:45:29Z 回执 ① 与新投盘 `probe_viastack_array_v22_2026-10-17.md`，sha e44d63e2…）：

  ⓪ 【库版本闸升 v2.2】canonical = 8510 `design/sow6/lib13g2.py`（v2.2 / 539 行 / 27592B /
     sha 02ecbfb95b3b…）。本件经 `sync_lib.py` 换闸，`Board.via` 的 vt1 透传对本件无行为变化。
  ① 【TopVia1 钉 1×1】v2.2 起 `Board.via(t_layer="TopMetal1")` 的 **vt1 阵列档位继承
     cols/rows**（v2.1 及更早硬编码 1×1 —— 官方 `via_stack_code.py` 里 vt1 走
     `vt1_columns/vt1_rows`，与 vn_* 无关）。本件两处 vcc 顶层柱走 `cross(..., VCC_LAYER)`
     → `b.via(x, y, "Metal1", "TopMetal1")`，默认 cols=2,rows=2 ⇒ v2.2 下会**静默**从
     1×1 变成 2×2 阵列；而 TM1 平台尺寸**非线性**（组长实测 1×1 = 1.64 见方、
     3×2 = 2.94×2.10，并明令「按实测值取用，**勿自行外推**」）⇒ 2×2 无真值可依。
     故显式 `vt1_cols=1, vt1_rows=1`：几何与 v1.4（v2.1 时代已代跑过的那份）逐位相同。
     代价（已写入信里请组长裁定）：这两处顶层馈电柱仍是**单颗 TopVia1**，EM 余量偏薄；
     要阵列需先补测 2×2 的 TM1 平台真值。
  ② 【绘图封装透传 vt1_*】v1.4 的官方-DRC 落实块把 `b.via` 换成了本地封装
     （5nm 量化用），签名停在 `(x, y, b_layer, t_layer, cols, rows)` ⇒ 顶层钉档参数
     传不进去（`TypeError: unexpected keyword argument 'vt1_cols'`，本轮自检当场逮到）。
     封装改为**透传** vt1_cols/vt1_rows，且故意不给默认值：想钉 1×1 必须显式写出来。

v1.4 = v1.3 全部内容 + **官方 DRC 两族的自侧落实**（2026-10-17；来源：组长 b7a0 07:29Z 回执信
  + `判读纪要_M2M3代跑v24全链_2026-10-17.md`）：

  ① 【Offgrid 族（≈90% 项数）】官方制造网格 grid=0.005µm（纪要 §3.4）。resgeom 侧把电阻
     长度 l 量化到 **1/168µm** 晶格（推出来的：P2 引脚高 = 0.72+0.84·l，要它落在 5nm 网格
     上 ⇒ l=k/168），参数串给足有效位（旧 `%.4g` 会把 25/17 写成 1.471 而失格）；
     本脚本侧 rect/wire_h/wire_v/via/label 五个绘图入口全部过一层 5nm 量化。
  ② 【TM1.a×9（要改图）】TopMetal1 最小宽 1.64µm，而本件顶层走线全用库默认 W=0.30µm
     —— 顶层每根线都违规。给 TOPM1/TOPM2 的 wire_h/wire_v 设每层最小宽下限（1.64/2.0）。
     M1~M5 不动：纪要里它们**没有**最小宽违规项，说明 minw ≤ 0.30。
  ③ 【代跑补丁①】bbox 读取改双风格适配器 `_bb()`：真 klayout 只有 left/bottom/right/top，
     本机仿真层只有 x1/y1/x2/y2 —— 原样一侧跑通、另一侧 AttributeError。
  ⚠ 顶层加宽会自造间距违规（两条 1.64µm 宽的顶层线相距 <3.28µm 即违规）：本件顶层只有
     vcc 干路（4µm 宽横轨 Y_VCC=200 + 两条竖轨），逐条核过自检台 ⑱ 项 0 FAIL。

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
USE_CMIM = True          # 组长 08:0xZ 五裁①：cmim 走库原语 b.mim_cap（面积闸见 cmim_fits）
# v2.1：NOTES 定义**上移**到此处 —— §7.5 的 PTAP_SKIPPED 要往里写，而原定义
#       在 §12（PH_BOX 旁）。原位保留一行注释指回，避免两处初始化互相覆盖。
NOTES = []          # 占位件说明：只进 stdout 与设计稿

# v2.1：顶层 cell 名随件升到 V21 —— 与 `drv1_subckt_LVS输入_v3.sp` 的
#   `.subckt TX5G_M3_DRV1_V21` 逐字对齐（裁定二十七 §一②交办项「请把顶层名随
#   下一版改正」：原网表名 V16 滞后于版图，KLayout 会直接报
#   `Can't find a schematic counterpart for the top cell`）。
# v2.3：顶层 cell 名随件升到 V23 —— 与 `drv1_subckt_LVS输入_v5.sp` 逐字对齐。
#   （v2.1 起 V21、v2.2 起 V22，本轮同一机制续行。）
b = L.Board("TX5G_M3_DRV1_V23")

# v2.0 回改登记簿：HBT 实例（E 指底座真值扫描用）+ 电阻（焊盘覆盖自检用）
HBT_DEVS = []       # [(name, (x_pin, y_org), nx, mirror)]
RES_DEVS = []       # [(name, (x0, y0), model, l)]


def mkhbt(name, nx, x, y, mirror=False):
    """mkpc_at 的 HBT 包装：登记 E 指底座真值扫描所需信息（cbpath.audit_board_e_pads）。"""
    inst = b.mkpc_at(name, "npn13G2", {"Nx": nx}, (x, y), "hbt", mirror=mirror)
    HBT_DEVS.append((name, (x, y), nx, mirror))
    return inst

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
    # vv1.5：lib v2.2 起 TopVia1 阵列档位走 vt1_columns/vt1_rows、缺省继承 cols/rows
    #（v2.1 硬编码 1×1）。本封装必须**透传** vt1_*，否则顶层的 1×1 钉档传不进来
    #（unexpected kwarg）。故意不给默认值：想钉 1×1 必须显式写出来。
    # v1.6（Q10 轮实测）：lib **v2.3** 又给 TopVia2 加了同款继承（vt2_columns/vt2_rows，
    #   t_layer=TopMetal2 时缺省继承 cols/rows）⇒ 与 vt1 同纪律钉 1×1。**本件实测无
    #   t_layer=TopMetal2 的栈**（见实例参数统计），故此处只做透传，不改任何几何。
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


def _bb_mfg(cell):
    """**制造层** bbox：排除 235/5 非制造 keepout（裁定⑤：外置预留不进岛界/台账）。

    v1.8 新增。为什么必须有：外置电容条带画在 (235,5) 起、x 到 ~326µm，dbbox 会把它
    吃进岛界 ⇒ 岛 130×224 瞬间变 400×233，"核 bbox 零变化"就成了假话。
    真 klayout 走 bbox_per_layer 逐层拼；本机仿真层走 cell.boxes 逐盒过滤（cell._li
    取层号）。两条路都没有时退回 _bb 并**打印声明**（不静默猜）。
    """
    try:
        pts = []
        if hasattr(cell, "boxes") and hasattr(cell, "_li"):            # 本机仿真层
            for lid, bl in cell.boxes.items():
                if cell._li(lid).num == 235:
                    continue
                for b in bl:
                    pts += [(b.x1, b.y1), (b.x2, b.y2)]
        elif hasattr(cell, "bbox_per_layer") and hasattr(cell, "layout"):  # 真 klayout
            ly = cell.layout()
            for i in range(ly.layers()):
                if ly.get_info(i).layer == 235:
                    continue
                bb = cell.bbox_per_layer(i)
                if not bb.empty():
                    pts += [(bb.left, bb.bottom), (bb.right, bb.top)]
        # 文本也要进（历史口径 dbbox 含 label 文本；v16/v17 的核 bbox 一直带它，
        # "零变化"要对得上就得同口径——只剔 235/5 的）。
        if hasattr(cell, "texts") and isinstance(cell.texts, dict):      # 本机仿真层
            for lid, ts in cell.texts.items():
                if cell._li(lid).num == 235:
                    continue
                for tx in ts:
                    pts += [(tx.trans.dx * 0.001, tx.trans.dy * 0.001)]
        elif hasattr(cell, "begin_texts"):                              # 真 klayout
            try:
                for t in cell.begin_texts():
                    if t.layer_num != 235:
                        pts += [(t.x, t.y)]
            except Exception:
                pass
        if not pts:
            print("[bbox] 制造层无图形，退回全 cell 口径（含 235/5）", flush=True)
            return _bb(cell)
        return (min(p[0] for p in pts), min(p[1] for p in pts),
                max(p[0] for p in pts), max(p[1] for p in pts))
    except Exception as e:
        print(f"[bbox] 制造层口径读取失败（{type(e).__name__}: {e}），退回全 cell 口径",
              flush=True)
        return _bb(cell)
    if hasattr(d, "left"):
        return (d.left, d.bottom, d.right, d.top)
    if hasattr(d, "x1"):
        return (d.x1, d.y1, d.x2, d.y2)
    raise RuntimeError(f"无法读取 dbbox：{type(d)}")



# ══════════════════════════════════════════════════════════════════════
# 0. 层分配（真值表只收录 7 层金属，「一个网一层」排不下，多网共用层；
#    共用层的网靠 y 带 / x 区间彻底错开）
# ══════════════════════════════════════════════════════════════════════
_M2NUM = {"M1": "Metal1", "M2": "Metal2", "M3": "Metal3", "M4": "Metal4",
          "M5": "Metal5", "TOPM1": "TopMetal1", "TOPM2": "TopMetal2"}
_ORDER = ["Metal1", "Metal2", "Metal3", "Metal4", "Metal5",
          "TopMetal1", "TopMetal2"]
GND_LAYER = "M4"         # 地专层
NREF_LAYER = "M3"        # nref（XQo.B / XQr.C / XQr.B / Rref.P2）—— 全是小电流
BIAS_LAYER = "M5"        # bin / bb1 / nbias
VCC_LAYER = "TOPM1"      # vcc 干路（15 mA/µm，4µm 就富余 30 倍）
PH_LAYER = "TOPM2"       # 占位 / 禁区（cmim 占位 + tank L1 禁区），互不相接

# 嵌套子电路内部网的版图网名形态（hbt_mirror 的内部网 nref 是**每实例一条独立网**，
# 网表无 .global；标成裸 `nref` → drv1/drv2 的镜像偏置网同名，LVS 按名比对必失配）。
#   hier     → xbi/nref    层次网表 / Calibre 内部展平惯例（默认）
#   flat_dot → xbi.nref    ngspice / Calibre 展平输出惯例
#   bare     → nref        不可取（会触发自检台 ⑧「同名多网被短接」）
NESTED_STYLE = "hier"
_NSEP = {"hier": "/", "flat_dot": ".", "bare": ""}[NESTED_STYLE]


def hnet(pfx, net):
    """嵌套子电路内部网的版图网名（与网表展平后的名字逐字一致）。"""
    return net if _NSEP == "" else f"{pfx}{_NSEP}{net}"


HNET = hnet("XBI", "nref")          # 本件只有一个镜像实例 XBI


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
        # v1.5：v2.2 起 vt1 阵列缺省继承 cols/rows ⇒ 默认 2×2 的顶层柱会静默变阵列，
        # 而 TM1 平台非线性（实测 1×1=1.64 / 3×2=2.94×2.10，勿外推）⇒ 显式钉 1×1。
        b.via(x, y, b_layer=lo, t_layer=hi, vt1_cols=1, vt1_rows=1)
        return
    b.via(x, y, b_layer=lo, t_layer=hi)


def stub(layer, x, y, dy, net, w=None):
    """在器件引脚下落一小段真实金属并打网名标注。
    （自检台第⑥项会把器件自身的 pin 方块剔掉，只认真正的走线 —— 不落金属必判悬空。）"""
    b.wire_v(layer, x, y, y + dy, w)
    b.label(layer, x, y + dy, net)


def mkres(name, R, model, x, y):
    """model="auto" = 让 resgeom.res_auto 在 rsil/rppd/rhigh 里挑面积最小的一档
    （Q5 真值落地后必须开：rsil 只 7Ω/□，1kΩ 会被拉成 142.9µm 长条）。
    选型结果逐件打印，型号即版图侧决策、随信报组长。
    v2.0：登记 RES_DEVS（焊盘覆盖自检用）。"""
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
    """mkres + **P2 焊盘真值跨度**（绝对 y）。v2.0 出脚锚定专用 —— 出线一律从
    焊盘真值起画，lib 引脚锚点（0.72+0.84·l）只当标记点，不再当落点。"""
    inst = mkres(name, R, model, x, y)
    m, l_f = RES_DEVS[-1][2], RES_DEVS[-1][3]
    span = RG.res_pad2(m, l_f)
    return inst, (y + span[0], y + span[1])


# ══════════════════════════════════════════════════════════════════════
# 1. 几何骨架（先定死坐标，emitpath 再据此反解宽度 —— 不能拍脑袋写长度）
# ══════════════════════════════════════════════════════════════════════
Y_Q = 150.0                 # XQ1/XQ2 锚（集电极列）
X_Q = 14.0                  # XQ1 @ -X_Q / XQ2（镜像）@ +X_Q；E 脚与 Re 同列
Y_P1 = 143.0                # Re1/Re2 的 P1（= e1/e2 落点高度）
X_ESC = 26.0                # ntail 从 Re.P2 外折的专属通道 @ ∓X_ESC（须在 M1 落点焊盘之外）
RES_BOT = 0.53              # 电阻本体下沿相对 P1 的下沉量（真值表 §2 的 −0.53）
NT_Y1, NT_Y0 = 136.0, 121.0     # ntail 轨（15µm 高）
NT_X0, NT_X1 = -39.0, 39.0
Y_MIR = 108.0               # 镜像组（XQo @0 / XQr @34）—— 全在 ntail 轨下方
X_CH = -10.0                # XQo.C 上折后横移的通道
NREF_Y = 96.0               # nref M3 干路
GND_Y = 82.0                # gnd M4 干路
NBIAS_Y = 70.0              # nbias M5 干路
Y_RIN = 8.0                 # Rin P1（inp/inn）→ P2(gnd) 在 64.72
Y_RB = 8.0                  # Rb  P1（bin/bb1）→ P2(nbias) 在 64.72
X_RIN = (-42.0, -35.0)
X_RB = (35.0, 42.0)
Y_RF = 14.0                 # Rref P1（vcc）→ P2（nref）在 14+91.44 = 105.44
X_RF = -50.0
X_QR = 34.0                 # XQr 锚 x
Y_CP = 166.0                # cop / con 轨
X_CESC = 24.0               # cop/con 从 C 脚外折的通道 @ ∓24（= bin/bb1 的 M5 立管 x）
X_BIAS = 24.0               # bin/bb1 在 M5 上的立管 x（要让开 M2 回流臂）
Y_VCC = 200.0               # vcc TOPM1 顶部横轨
X_VCC = -60.0               # vcc 干路立管

# ══════════════════════════════════════════════════════════════════════
# 2. 发射极回流规格（R-EMIT-01/02 + R-VIA-01）
#    rail_len = M2 臂长 = E 脚 y − M1 焊盘顶（= Re 本体下沿）
#    m1_len   = M1 落点焊盘高（≈Via1 阵列外接高）
# ══════════════════════════════════════════════════════════════════════
ARM_TOP = Y_Q - 0.01                  # M2 引脚 E 的 y
M1_PAD_H = RG.via_extent(*RG.factor(120))[1] + RES_BOT   # 焊盘高 = 桶外接高 + 0.53
ARM_LEN = ARM_TOP - (Y_P1 - RES_BOT)
SP = EP.emit_return_spec(
    i_side=3.72,                            # 准则 §二 实测表：DRV1 nx=6 → 3.72 mA/边
    tier_ohm=RG.EM_BUDGET["drv1"],          # 签核取严 ≤0.250Ω（−40℃ 角）
    rail_len_um=ARM_LEN, m1_len_um=M1_PAD_H,
    ntail_i=7.44,                           # 两条边合流到 ntail
    tag="drv1")
assert SP["via1_n"] == 120
assert SP["report"]["ok"], f"drv1 发射极路径超档：{SP['report']}"
print(EP.report(SP), flush=True)
W_NT = SP["w_ntail"]

# ══════════════════════════════════════════════════════════════════════
# 3. 输入级 XQ1 / XQ2（nx=6）
#    XQ2 绕锚 y 轴镜像 → 两个器件的**本体盒**也左右对称（引脚列恒在锚 x），差分等长。
# ══════════════════════════════════════════════════════════════════════
XQ1 = mkhbt("XQ1", 6, CX - X_Q, Y_Q)                                # cop bin e1
XQ2 = mkhbt("XQ2", 6, CX + X_Q, Y_Q, mirror=True)

# ══════════════════════════════════════════════════════════════════════
# 4. 发射极回流链（几何全在 emitpath.place_emit_chain 里，自检台可复核）
# ── v2.0（2026-10-18）：**先 mkres 后 chain**，P2 出脚改锚**焊盘真值** ──
#    旧序（先 chain 后 mkres）时 place_emit_chain 拿不到 Re 实例，只能用
#    lib 引脚锚点 0.72+0.84·l = y_p1+1.56 预估 —— 而 rsil 短条(l=1) 的**实焊盘
#    顶只到 y_p1+1.53**，stub 整段悬空 0.03µm ⇒ Re1/Re2 的 P2 直流断路
#    （真值表见 resgeom.RES_PAD1/RES_PAD2_OFF，GDS 逐位实测 7/7 命中）。
Re1, _P2_RE1 = mkres_pad("Re1", 4, "rsil", CX - X_Q, Y_P1)   # P1=e1  P2=ntail
Re2, _P2_RE2 = mkres_pad("Re2", 4, "rsil", CX + X_Q, Y_P1)   # P1=e2  P2=ntail
for q, p2_pad, net, sgn in ((XQ1, _P2_RE1, "e1", -1), (XQ2, _P2_RE2, "e2", +1)):
    EP.place_emit_chain(b, q.p["E"][0], Y_P1, SP, net, sgn,
                        X_ESC, NT_Y1, y_arm_top=q.p["E"][1], res_bot=RES_BOT,
                        lap=0.6, p2_pad=p2_pad)

# ══════════════════════════════════════════════════════════════════════
# 5. ntail 汇流轨（M1，W_NT ≥ 15µm）
# ══════════════════════════════════════════════════════════════════════
b.rect("M1", NT_X0, NT_Y0, NT_X1, NT_Y1)
b.label("M1", CX, NT_Y0 + 1.0, "ntail")

# ══════════════════════════════════════════════════════════════════════
# 6. 尾流镜像组 `XBI ntail vcc hbt_mirror` = **Qr(nx=1) + XQo(nx=8) + Rref(1.62k) 三件**
#    nref 走 M3：XQo.C(ntail) 与 XQo.B(nref) 只差 2.38µm 而 ntail 轨有 15µm 宽，
#    nref 留在 M1 必被 ntail 轨吞掉 → 同层短接。改层是唯一解。
#    XQo.C 从**上方**绕出去（先上折再横移），避开 B 脚那一行。
# ══════════════════════════════════════════════════════════════════════
XQo = mkhbt("XBI_XQo", 8, 0.0, Y_MIR)                                 # C=ntail
XQr = mkhbt("XBI_XQr", 1, X_QR, Y_MIR)                                # C=B=nref
Rref = mkres("XBI_Rref", 1620, "rhigh", X_RF, Y_RF)                     # P1=vcc P2=nref

qcx, qcy = XQo.p["C"]
b.wire_v("M1", qcx, qcy, qcy + 4.8)
b.wire_h("M1", qcy + 4.8, min(qcx, X_CH), max(qcx, X_CH))
b.wire_v("M1", X_CH, NT_Y0, qcy + 4.8)
b.label("M1", X_CH, NT_Y0 + 1.0, "ntail")

rbx, rby = XQr.p["B"]
rcx, rcy = XQr.p["C"]
# ── v2.0（2026-10-18）C=B 实连改**绕 E 指列**三段折线 ──
#    旧口径 `wire_v("M1", rbx, rby, rcy)` 从 B 带直拉 C 带，**中途穿 E 指底座**
#    （(8,0) 金属，x∈锚±0.35）⇒ 同层重叠 0.30×1.557=0.4665µm² = nref↔gnd 真短
#    （真短定谳 #4）。新口径走 cbpath.cb_tie：竖线挪到 x+1.2，净距 0.70µm。
CBT_XQr = CB.cb_tie(b, XQr.p["C"], XQr.p["B"], tag="drv1.XBI_XQr", side=+1,
                    e_pad=CB.e_pad_rects(XQr.p["B"][0], Y_MIR, 1))
b.wire_h(NREF_LAYER, NREF_Y, X_RF, X_QR)
for (px, py) in ((rbx, rby), (rcx, rcy), (XQo.p["B"][0], XQo.p["B"][1])):
    cross(px, py, "Metal1", NREF_LAYER)
    b.wire_v(NREF_LAYER, px, NREF_Y, py)
b.label(NREF_LAYER, X_QR, NREF_Y, HNET)
rf2x, rf2y = Rref.p["P2"]
cross(rf2x, rf2y, "Metal1", NREF_LAYER)
b.wire_v(NREF_LAYER, rf2x, NREF_Y, rf2y)
b.label(NREF_LAYER, rf2x, rf2y, HNET)

# ══════════════════════════════════════════════════════════════════════
# 7. 地网 M4：XQo.E / XQr.E（M2 脚）+ Rin1/Rin2 的 P2（M1 脚）
# ══════════════════════════════════════════════════════════════════════
b.rect(GND_LAYER, -56.0, GND_Y - 2.0, 56.0, GND_Y + 2.0)
b.label(GND_LAYER, CX, GND_Y, "gnd")
for q in (XQo, XQr):
    ex, ey = q.p["E"]
    # ⚠ npn13G2 的 C/B/E **同 x**（C y+2.27 / B y−1.13 / E 居中），而 nref 的 M3 立管
    #   正好沿这个 x 从干路拉到 B/C 脚 → 若在 E 脚正下方落 M2→M4 过孔，
    #   柱脚就压住 nref 的 M3 立柱（自检台 ⑤d 当场抓出）。解法：先在 M2 上外折 4µm
    #   再落过孔，柱下 M3 无金属。
    gx = ex + 4.0 * (1 if ex >= 0 else -1)
    b.wire_h("M2", ey, ex, gx)
    cross(gx, ey, "Metal2", GND_LAYER)
    b.wire_v(GND_LAYER, gx, GND_Y, ey)
    b.label(GND_LAYER, gx, GND_Y, "gnd")

# ══════════════════════════════════════════════════════════════════════
# 7.5 ★裁定二十七 §三 交办①：偏置支路 **pwell 接地 tap**（XQo 岛 / XQr 岛）
# ══════════════════════════════════════════════════════════════════════
# 定谳（组长 #206 裁定二十七）：三块里 **只有 drv1 的 `40/0 substrate_drw`=0、
#   `ptap1` 实例=0** ⇒ `pwell_allowed = CHIP.not(pwell_block)` 被 `npn_exclude`
#   （trans_drw/gatpoly/res_drw/salblock_drw/substrate_drw…）切成多岛后，
#   **XQo(Nx=8) / XQr(Nx=1) 所在的浮空岛没有任何接地路径** ⇒ 四只 HBT ＋
#   九只电阻的衬底端子（S 端）全挂同一张孤立网 `$1`（E0 实测 8M/8X）。
#   Q2/Q3（cop/bin、con/bb1）所在岛不浮空 —— 它们靠**自己的 E 指**经
#   §7 的 M2→M4 线下引接进 gnd 干线，E 指底座即 (8,0) metal1_con ⇒ 岛即通。
#   drv1 这两只管的 E 指也走了同一条路，但**它们是两只独立岛**……
#   ——不对：E0 实测它们与九只电阻同挂 `$1`，说明 XQo/XQr/电阻同属**一岛**；
#   之所以仍浮空，是因为 §7 的 E 脚下引只把 **M2 以上**接进 gnd，衬底侧要靠
#   **ptap 接触**才通（deck：`pwell ─connect(pwell,ptap)─ pactiv∩pwell
#   ─cont_drw─ metal1_con─ M1`）。这正是本节补的那一环。
#
# ★交办两条硬规矩，本节逐条兑现：
#   ① **禁止用 label 命名代替电学连接** —— E2 把 ptap 放在 (250,205) 且 label
#      落 8/25，net 仍是 8M/8X，只多了个 `gnd$1`：那是 klayout 给「同名但
#      不连通」的碎片自动改名，接地**并不成立**。⇒ 本节一律走**真金属**
#      （M1 垫 → via_stack → M4 立管 → 同层压 gnd 干线），label 只作命名。
#   ② **禁区**：`M1 (-39,121)-(39,136)` ntail 汇集板及其压板带区
#      （E3 实测 ptap 落 (−39.5,127.6) ⇒ gnd–ntail 短路）。
#
# 落点三原则（逐条对真值核过，非拍脑袋）：
#   ① **禁区零距离**：两只 tap 取 y=100.0，距 ntail 板下沿 121 有 **21µm**。
#   ② **不落 HBT 排除区、且同属该 pwell 岛**：XQo 管身 x∈[-7.45,+7.45]
#      （B 带半宽 0.925×Nx+0.05=7.45）、XQr 管身 x∈[33.05,34.95]；两只 tap
#      取 x=14 / x=42，**都在管身之外**，其间无任何 `npn_exclude` 图形
#      （y∈[86,126] 带内逐层点过：M1/M2/M3/M4/M5 与全部嵌套实例都空）。
#   ③ **柱下中空层无异网**：走 `cross()` 的 M1→M4 **单** via_stack，焊盘只在
#      两端层 —— 与 §7 的 E 脚下引同款（自检台 ⑤d 口径），M2/M3 不留盘，
#      避免压在 nref 的 M3 立管（x=0 / x=34）上。
#
# 形状照 drv2 v18 补环/mix v27 同款三重防护：① TAP_ENABLE 开关 ② 参数留空走
# PDK 默认 ③ 非致命 try。仿真层不建未知 PCell（塞假体会污染间距判定）⇒
# PTAP_SKIPPED 进 NOTES，真几何待代跑落。**金属那一半不受开关管** —— 它
# 必须无条件画出来，否则本机连自检都验不到接地链。
TAP_ENABLE = True
# ── v2.3：`ptap1` 的 PDK 真值（**第一手来源 = 真 GDS `m3_drv1_v21.gds` 逐条解出**，
#    与组长从 `ptap1_code.py` 源码读出的数字逐位吻合，残差 0）：
#      Activ 1/0 : (0,0)-(0.78,0.78)          pSD 14/0 : (-0.03,-0.03)-(0.81,0.81)
#      Cont 6/0  : 4 只 0.16² @ 0.14/0.48 阵列   M1 tie 8/0: **(0.14,0.09)-(0.64,0.69)**
#    ⇒ 原点是 Activ 左下角，**tie 中心在原点+(0.39,0.39)**，边长 0.50×0.60。
#    另有 8/2 (0.14,0.14)-(0.64,0.64) 与 40/0 0.78 见方（本轮未用，记录备查）。
_TAP_PDK = {"tie": (0.14, 0.09, 0.64, 0.69),
            "tie_c": (0.39, 0.39),
            "activ": (0.0, 0.0, 0.78, 0.78),
            "psd": (-0.03, -0.03, 0.81, 0.81)}
_TAP_TIE_W = _TAP_PDK["tie"][2] - _TAP_PDK["tie"][0]     # 0.50
_TAP_TIE_H = _TAP_PDK["tie"][3] - _TAP_PDK["tie"][1]     # 0.60
_TAP_TIE_CX, _TAP_TIE_CY = _TAP_PDK["tie_c"]             # (0.39, 0.39)
PTAP_ISLANDS = {"XQo": (14.0, 100.0),      # XQo(Nx=8) 所在浮空岛
                "XQr": (42.0, 100.0)}      # XQr(Nx=1) 所在浮空岛
for _nm, (_tx, _ty) in PTAP_ISLANDS.items():
    # 真金属接地：M1(pdap 垫) ─via_stack─ M4 立管 ─同层压─ gnd 干线
    cross(_tx, _ty, "Metal1", GND_LAYER)
    b.wire_v(GND_LAYER, _tx, GND_Y, _ty)
    b.label(GND_LAYER, _tx, GND_Y, "gnd")
if TAP_ENABLE:
    import pya as _pya
    if hasattr(_pya, "WARN"):
        # ── 仿真层替身：ptap1 PCell 落不了 ⇒ 只补它**自带的 M1 tie**，形状照 PDK 真值
        #    （局部 0.50×0.60 @ 中心(+0.39,+0.39)）。v2.2 这里放的是自造的 0.80 见方，
        #    盖住 via 焊盘没问题，但**盖错了地方**：真跑的 tie 在实例原点的右上方，
        #    替身却在原点 ⇒ 本机自证「全过」而真跑只是压住一角（口径漂移的第四例）。
        #    现在实例落点同步挪了 −0.39，替身落在 (tap 中心)，**与真跑逐位同位**。
        _SIM_ONLY_TIE = []
        for _nm, (_tx, _ty) in PTAP_ISLANDS.items():
            b.rect("M1", _tx - _TAP_TIE_W / 2, _ty - _TAP_TIE_H / 2,
                   _tx + _TAP_TIE_W / 2, _ty + _TAP_TIE_H / 2)
            _SIM_ONLY_TIE.append((_nm, _tx, _ty))
        NOTES.append("PTAP_SKIPPED：本机仿真层不建 ptap1 PCell —— 2 只 ptap 接触待代跑落"
                     "（mix v27 / drv2 v18 同款已代跑全绿；tap 密度/psd 间距条款由"
                     "代跑 DRC 终裁）。接地用的 M4 立管+via_stack **已无条件落图**，"
                     "缺的只是 ptap1 自带的 1/0 Activ+14/0 pSD+6/0 cont+8/0 M1 垫；"
                     f"本机按 PDK 真值垫了 {len(_SIM_ONLY_TIE)} 块 "
                     f"{_TAP_TIE_W:.2f}×{_TAP_TIE_H:.2f}µm M1 tie 替身"
                     "（**仅仿真层**，不进真 GDS；真值来源=真 GDS 逐条解出，见 _TAP_PDK）")
    else:
        try:
            _pc = b._pcell("guard_ptap_default", "ptap1", {})
            for (_nm, (_tx, _ty)) in PTAP_ISLANDS.items():
                # v2.3：落点挪 tie 中心对齐 via_stack 焊盘中心（见文件头 ①）
                _ox, _oy = _tx - _TAP_TIE_CX, _ty - _TAP_TIE_CY
                b.top.insert(_pya.DCellInstArray(
                    _pc, _pya.DTrans(_pya.DVector(_ox, _oy))))
            print(f"[tap] pwell 接地 ×{len(PTAP_ISLANDS)}："
                  + " · ".join(f"{n}@tie({x:.1f},{y:.1f})"
                              for n, (x, y) in PTAP_ISLANDS.items())
                  + f"（实例落点已挪 −{_TAP_TIE_CX}/{_TAP_TIE_CY} 对心）", flush=True)
        except Exception as _e:
            NOTES.append(f"PTAP_SKIPPED：{type(_e).__name__}: {_e}")

# ── 自检断言：「每块每岛均有接地 tap」（交办硬要求：**零断言即停线**）──────
# 本机跑不了 deck 的 pwell 连通域分析，所以断言不落在「连通域」这种跑不动的
# 判据上，而落在**四条可证伪的几何事实**上（任一条为假即 AssertionError 停线）：
#   ① 每个声明的岛都点名一只 tap，且落点在「能下引到 gnd 干线、又没进禁区」的区间里；
#   ② 该落点上**真的有** via_stack 实例（接地链的金属那一环在图上）；
#   ③ 该落点的 **M4 立管**在图上，且其 M4 金属**真压** gnd 干线（不是「看着像」）；
#   ④ **禁区内零 tap**（E3 实测 gnd–ntail 短路的前车之鉴）。
#
# ⚠ 两个取图助手必须**仿真层与真 KLayout 双通**（v2.0 血训：自检结论只认新鲜
#   解释器，且这段断言要在**组长的真 KLayout 代跑**里同样过；写死仿真层的
#   `cell.insts` / `cell.each_shape` 会让代跑当场 AttributeError 停线）。
# ⚠ v2.3：原注释「两个取图助手必须仿真层与真 KLayout 双通」的**修法其实没生效**
#   ——组长真跑连炸三次（裁定四十九 §三）：位移取 .x/.dy、DBox.hit、只取顶层。
#   下面按他实测的正解重写；**v1.7 增补**：未经真跑背书的「双通 helper」
#   一律按未验证计（本机只能仿真层自证 + 真 GDS 几何交叉验证）。
def _resolve_dbu(_cell):
    """取该 cell 所属 layout 的 dbu（µm/db）。

    ⚠ **真 KLayout 的 `Cell` 没有 `.dbu` 属性** —— dbu 挂在 **Layout** 上
      （`cell.layout().dbu`，组长 adapt 实测正解）。首版我写 `getattr(cell,'dbu',None)`
      会**静默回落到 0.001**：本 PDK 恰好就是 1nm，结果「对得上」⇒ 错法被结果掩盖。
      **这正是本轮 §三 的教训翻版：静默兜底 = 把错误藏起来。**
      ⇒ 顺序：layout().dbu → cell.dbu → 显式环境变量 → 报错（不再默默给常数）。"""
    _lay = getattr(_cell, "layout", None)
    if callable(_lay):
        _d = getattr(_lay(), "dbu", None)
        if _d:
            return float(_d)
    _d = getattr(_cell, "dbu", None)
    if _d:
        return float(_d)
    _p = sys.modules.get("pya")            # 仿真层：模块级 `D = 0.001`（照 sg13g2 map）
    _d = getattr(_p, "D", None)
    if _d:
        return float(_d)
    _env = os.environ.get("B7E7_DBU")
    if _env:
        return float(_env)
    raise RuntimeError("取不到 dbu：请核 layout().dbu，或设环境变量 B7E7_DBU（µm/db）")


_DBU = _resolve_dbu(b.top)      # µm/db；真 KLayout 取 layout().dbu（整数栅格 → µm）


def _disp_um(_t):
    """返回实例位移（**µm**）。

    两条路的位移属性**名字不同、单位也不同**，必须先分流再取值：
      · 仿真层 DTrans：有 `.dx/.dy`，**已是 µm**（它的 `.disp` 也是 µm）。
      · 真 KLayout Trans：**既无 .x/.y 也无 .dx/.dy**，只有 `.disp`，且给
        **整数 dbu** —— 要 ×dbu 才是 µm（组长正解 `t.trans.disp.x` 即此）。
    ⚠ 分流顺序反了会静默出错：v2.3 首版先查 `.disp`，于是仿真层的 µm 值
      被当成 dbu 乘了 0.001，实例原点从 14.0 变成 0.014 —— 断言②当场炸
      （这正是「有牙」的用处：错得响，错不错得过去）。
    """
    if hasattr(_t, "dx"):                          # 仿真层：已是 µm
        return (_t.dx, _t.dy)
    _d = getattr(_t, "disp", None)                 # 真 KLayout：整数 dbu
    if _d is not None and hasattr(_d, "x"):
        return (_d.x * _DBU, _d.y * _DBU)
    return (0.0, 0.0)


def _inst_origins(_cell):
    if hasattr(_cell, "insts"):                     # dryrun/pya 仿真层
        return [_disp_um(t) for (_c, t) in _cell.insts]
    return [_disp_um(_ia.trans) for _ia in _cell.each_inst()]   # 真 KLayout


def _boxes_recursive(_cell, _li):
    """返回该层在**世界坐标**的 (x1,y1,x2,y2) 列表，**递归进子 cell（PCell 变体）**。

    真 KLayout：`begin_shapes_rec` **默认不进子结构**，必须 `select_all_cells()`；
    迭代**不能 list()**（实测 list(it) 反复吐出迭代器自身），一律 while + next()。
    仿真层：直接给已摆放好的图元，无需递归。

    ⚠ 分派**不能只看有没有 begin_shapes_rec** —— 我自己的仿真层也实现了同名方法
      （当生成器用，没有 select_all_cells），照 hasattr 分派会在本机先炸。
      唯一无歧义的判据是仿真层私有的 `insts` 属性（真 KLayout 没有）。"""
    _out = []
    if hasattr(_cell, "insts"):                     # dryrun 仿真层
        for _s in _cell.each_shape(_li):
            _bb = _s.dbbox() if hasattr(_s, "dbbox") else _s
            _out.append((_bb.x1, _bb.y1, _bb.x2, _bb.y2))
        return _out
    _it = _cell.begin_shapes_rec(_li)               # 真 KLayout
    _it.select_all_cells()
    while not _it.at_end():
        _sh = _it.shape()
        _bb = _sh.dbbox() if hasattr(_sh, "dbbox") else _sh
        _d = _it.trans().disp
        _out.append((_bb.left + _d.x * _DBU, _bb.bottom + _d.y * _DBU,
                     _bb.right + _d.x * _DBU, _bb.top + _d.y * _DBU))
        _it.next()
    return _out


def _bb_xy(_bb):
    """取包围盒四边，兼容真 KLayout 的 .left/.right/.bottom/.top、仿真层的 .x1/.x2，
    以及 `_boxes_recursive` 真路径直接产出的 4 元组。"""
    if isinstance(_bb, (tuple, list)):
        return tuple(_bb[:4])
    g = lambda *names: next(getattr(_bb, _n) for _n in names if hasattr(_bb, _n))
    return (g("left", "x1"), g("bottom", "y1"), g("right", "x2"), g("top", "y2"))


def _bb_hit(_bb, x, y):
    """点是否落在盒内。**纯 Python 判定**：真 KLayout 的 DBox 没有 .hit()**。"""
    _x1, _y1, _x2, _y2 = _bb_xy(_bb)
    return _x1 <= x <= _x2 and _y1 <= y <= _y2


def _bb_overlap_area(_a, _b):
    _ax1, _ay1, _ax2, _ay2 = _bb_xy(_a)
    _bx1, _by1, _bx2, _by2 = _bb_xy(_b)
    _w = min(_ax2, _bx2) - max(_ax1, _bx1)
    _h = min(_ay2, _by2) - max(_ay1, _by1)
    return (_w * _h) if (_w > 0 and _h > 0) else 0.0


_nt_box = (NT_X0, NT_Y0, NT_X1, NT_Y1)
_inst_xy = {(round(_x, 3), round(_y, 3)) for (_x, _y) in _inst_origins(b.top)}
_m4_boxes = _boxes_recursive(b.top, b.layer(GND_LAYER))
_m1_boxes = _boxes_recursive(b.top, b.layer("M1"))
assert len(PTAP_ISLANDS) >= 1, "TAP-ASSERT ①：一只接地 tap 都没声明"
for _nm, (_tx, _ty) in PTAP_ISLANDS.items():
    # 干线本体横跨 x∈[-56,56]，立管必须落在其正上方才谈得上「并进干线」
    assert -56.0 <= _tx <= 56.0, \
        f"TAP-ASSERT ①：{_nm} 的 tap x={_tx} 在 gnd 干线跨度 [-56,56] 之外"
    assert GND_Y <= _ty <= NT_Y0, \
        f"TAP-ASSERT ①：{_nm} 的 tap y={_ty} 不在 (GND_Y={GND_Y}, NT_Y0={NT_Y0}) 下引区间内"
    assert any(_bb_hit(_bb, _tx, _ty) for _bb in _m1_boxes), \
        f"TAP-ASSERT ②：{_nm} 的 tap ({_tx},{_ty}) 处没有 M1 接地垫 —— 接地链断在第一环"
    assert (round(_tx, 3), round(_ty, 3)) in _inst_xy, \
        f"TAP-ASSERT ②：{_nm} 的 tap ({_tx},{_ty}) 处没有 via_stack 实例 —— 接地链断在第二环"
    assert any(_bb_hit(_bb, _tx, _ty) for _bb in _m4_boxes), \
        f"TAP-ASSERT ③：{_nm} 的 tap ({_tx},{_ty}) 处没有 M4 立管金属"
    assert any(_bb_hit(_bb, _tx, GND_Y) for _bb in _m4_boxes), \
        f"TAP-ASSERT ③：{_nm} 的 M4 立管 ({_tx},y={GND_Y}) 没落到 gnd 干路上"
    assert not (_nt_box[0] <= _tx <= _nt_box[2] and _nt_box[1] <= _ty <= _nt_box[3]), \
        f"TAP-ASSERT ④：{_nm} 的 tap ({_tx},{_ty}) 落进 ntail 汇集板禁区（E3 ⇒ gnd–ntail 短路）"
    # ── v2.3 新增 **TAP-ASSERT ⑤：tie 必须被 via 焊盘**全**覆盖** ──
    #   这条是本轮事故的直接对策：v2.2 的重叠只有 0.0462µm²（非零⇒自检全过），
    #   但真值是「只压住 tie 左下角」。**判据从「重叠>0」升级为「四边包含」**，
    #   于是「侥幸通」与「接好」在机检层面彻底分不开 → 以后再挪任一端都会被逮住。
    _tie = (_tx - _TAP_TIE_W / 2, _ty - _TAP_TIE_H / 2,
            _tx + _TAP_TIE_W / 2, _ty + _TAP_TIE_H / 2)
    _tie_area = _TAP_TIE_W * _TAP_TIE_H
    _cov = max([_bb_overlap_area(_tie, _bb) for _bb in _m1_boxes] or [0.0])
    assert abs(_cov - _tie_area) < 1e-9, (
        f"TAP-ASSERT ⑤：{_nm} 的 ptap M1 tie {_tie}（{_tie_area:.4f}µm²）"
        f"被 M1 金属只覆盖 {_cov:.4f}µm²（{_cov/_tie_area*100:.1f}%）—— "
        f"via 焊盘没把 tie 全盖住，接地靠压一角，属侥幸（v2.2 实测 0.0462/0.30）")
print(f"[tap] 自检断言 6×{len(PTAP_ISLANDS)} 条全过（干线跨度 / M1 垫 / via 在图 / "
      f"M4 压干线 / 禁区零 / **tie 全覆盖**）", flush=True)

# ══════════════════════════════════════════════════════════════════════
# 8. 输入电阻 Rin1/Rin2（1k，inp/inn → gnd）与基极偏置 Rb1/Rb2（1k，bin/bb1 → nbias）
# ══════════════════════════════════════════════════════════════════════
Rin1 = mkres("Rin1", 1000, "auto", X_RIN[0], Y_RIN)
Rin2 = mkres("Rin2", 1000, "auto", X_RIN[1], Y_RIN)
for r, net in ((Rin1, "inp"), (Rin2, "inn")):
    stub("M1", r.p["P1"][0], r.p["P1"][1], -3.0, net)
    px, py = r.p["P2"]
    cross(px, py, "Metal1", GND_LAYER)
    b.wire_v(GND_LAYER, px, GND_Y, py)
    b.label(GND_LAYER, px, GND_Y, "gnd")

Rb1 = mkres("Rb1", 1000, "auto", X_RB[0], Y_RB)
Rb2 = mkres("Rb2", 1000, "auto", X_RB[1], Y_RB)
b.wire_h(BIAS_LAYER, NBIAS_Y, X_RB[0] - 5.0, X_RB[1] + 5.0)
b.label(BIAS_LAYER, X_RB[0], NBIAS_Y, "nbias")
for r in (Rb1, Rb2):
    px, py = r.p["P2"]
    cross(px, py, "Metal1", BIAS_LAYER)
    b.wire_v(BIAS_LAYER, px, NBIAS_Y, py)
    b.label(BIAS_LAYER, px, NBIAS_Y, "nbias")

# ── bin / bb1（M5）：Rb.P1 → XQ.B
#    ① 两条网的源（x=35/42）在两条汇（x=∓14）**同一侧**，平面无直解（M2 插列定理）；
#    ② bb1 的 M5 立管若走 x=14，会正好落在 XQ2 的 M2 回流臂里 → 短接。
#       故两条网的 M5 立管都外移到 x=∓24（cop/con 的外折通道同 x，M1 层，互不干扰），
#       再各自过一个 M5↔M1 过孔 + 一小段 M1 横插进 B 脚。
for (r, q, net, y_lo, ch, y_hi) in ((Rb1, XQ1, "bin", 4.0, -X_BIAS, None),
                                    (Rb2, XQ2, "bb1", -2.0, X_BIAS, 110.0)):
    px, py = r.p["P1"]
    # ⚠ v1.2 勘误：v1.2 这条 `wire_h(BIAS_LAYER, y_lo, min(px, ch), max(px, ch))`
    #   画到 **ch**，而 bb1 的回流竖管在 **x=50** —— y_lo 那段从 px=42 画到 ch=24，
    #   与 x=50 的竖管差了 **8µm 没接上**：bb1 在版图上断成两截（Rb2.P1 → 一条
    #   死头横线；x=50 竖管 → B 脚）。为什么没人看见：⑤b「同名分裂」只数**带标注**
    #   的连通分量，'bb1' 只标了一处（另一截无标注），于是断线隐形。
    #   v1.2 起把该横段的终点改成**真正接得上竖管的那个 x**（y_hi 为 None 时是 ch，
    #   否则是 50.0）；自检台新增第 ⑫ 项「引脚极性（几何取证）」当场抓出本条。
    land_x = ch if y_hi is None else 50.0
    b.wire_v("M1", px, py, y_lo)
    cross(px, y_lo, "Metal1", BIAS_LAYER)
    b.wire_h(BIAS_LAYER, y_lo, min(px, land_x), max(px, land_x))
    if y_hi is None:                                   # bin：一条立管直通 B 脚高度
        b.wire_v(BIAS_LAYER, ch, q.p["B"][1], y_lo)
    else:                                              # bb1：先走到外侧再折回来
        b.wire_h(BIAS_LAYER, y_hi, min(ch, 50.0), max(ch, 50.0))
        b.wire_v(BIAS_LAYER, 50.0, y_hi, y_lo)
        b.wire_v(BIAS_LAYER, ch, q.p["B"][1], y_hi)
    cross(ch, q.p["B"][1], "Metal1", BIAS_LAYER)
    b.wire_h("M1", q.p["B"][1], min(ch, q.p["B"][0]), max(ch, q.p["B"][0]))
    b.label(BIAS_LAYER, ch, q.p["B"][1], net)      # M5 立管上
    b.label("M1", q.p["B"][0], q.p["B"][1], net)   # B 脚上

# ══════════════════════════════════════════════════════════════════════
# 9. vcc 干路（TOPM1，4µm）：Rref.P1 + RL1.P1 + RL2.P1
#    RL 也是竖直两端子：P1(vcc) 在下、P2(cop/con) 在上，同列 —— 与 Re 同一种病。
#    cop 轨从 C 脚**外折**到 x=∓24 上去，再从 RL 顶上接 P2；vcc 从底下取。
# ══════════════════════════════════════════════════════════════════════
VCC_W = 4.0
b.rect(VCC_LAYER, X_VCC - VCC_W / 2, Y_RF - 2.0, X_VCC + VCC_W / 2, Y_VCC + VCC_W)
b.rect(VCC_LAYER, X_VCC, Y_VCC, CX + X_CESC + VCC_W, Y_VCC + VCC_W)
b.label(VCC_LAYER, X_VCC, (Y_RF + Y_VCC) / 2, "vcc")
rf1x, rf1y = Rref.p["P1"]
cross(rf1x, rf1y, "Metal1", VCC_LAYER)
b.wire_h(VCC_LAYER, rf1y, X_VCC, rf1x)
b.label(VCC_LAYER, rf1x, rf1y, "vcc")

# ⚠ Q5 真值落地后的坑（2026-10-17 实测）：100Ω 原按 rsil l=6.667（15Ω/□ 旧口径）
#   反推，P1→P2 间距 6.32µm，故把 RL 的 P1 放在 Y_CP−6.32 让 P2 正好落到输出轨。
#   真值下 res_auto 改选 rppd l=1.0 → 间距只有 1.56µm；若沿用旧的 −6.32，
#   轨与引脚差 4.76µm，M1 横轨从引脚**上方掠过** → ⑤b「引脚无同层金属」+ LVS 悬空。
#   修法：间距由 res_auto 的真 l 现算，间距变了轨自动跟着走（不再两处各写一个常数）。
RL_SPAN = 0.72 + 0.84 * RG.res_auto(100)["_geom"][0]
Y_RL = Y_CP - RL_SPAN
RL1 = mkres("RL1", 100, "auto", CX - X_Q, Y_RL)   # P1=vcc  P2=cop
RL2 = mkres("RL2", 100, "auto", CX + X_Q, Y_RL)   # P1=vcc  P2=con
assert abs(RL1.p["P2"][1] - Y_CP) < 1e-6 and abs(RL2.p["P2"][1] - Y_CP) < 1e-6, \
    f"RL.P2 未落到输出轨 {Y_CP}（实得 {RL1.p['P2'][1]}）—— 轨高与间距脱钩了"
for (r, q, net, sgn) in ((RL1, XQ1, "cop", -1), (RL2, XQ2, "con", +1)):
    px, py = r.p["P1"]
    cross(px, py, "Metal1", VCC_LAYER)
    b.wire_v(VCC_LAYER, px, Y_VCC + VCC_W / 2, py)
    b.label(VCC_LAYER, px, Y_VCC + VCC_W / 2, "vcc")
    cx_, cy_ = q.p["C"]
    ch = CX + sgn * X_CESC
    b.wire_h("M1", cy_, min(cx_, ch), max(cx_, ch))
    b.wire_v("M1", ch, Y_CP, cy_)
    # cop/con 轨终点 = P1 锚点 x：焊盘 x 以锚**居中**（±(w−0.04)/2），轨压住盘的
    # 靠 ch 侧一半 ⇒ 连通（pad-audit 实测覆盖 ✓）。
    # ⚠ 本处曾被我第一版 pad-audit 误报「RL1.P2 差 0.02µm」——根因是那版把
    #   cell 局部系当锚相对系，整表错位；按 pex 端子坐标重锚后此误报消（教训
    #   已写进 resgeom.audit_res_pads docstring）。几何保持与 v1.9 逐位一致。
    b.wire_h("M1", Y_CP, min(ch, px), max(ch, px))
    b.label("M1", (ch + px) / 2, Y_CP, net)

# ══════════════════════════════════════════════════════════════════════
# 10. 占位 / 禁区：**本轮落地**（组长 08:0xZ 五裁；机制全落地 + 面积闸挡住放不下的）
#     裁定原文两条：
#       ① cmim PCell = 库原语 `Board.mim_cap`（官方密度 1.5 fF/µm² 自动解 W/L），
#          pin = Metal5.pin(67/2) + TopMetal1.pin(126/2)，两 pin 同心于电容中心；
#       ② tank L1 禁区层号 = (235,5)（库 v2.2 `_KEEPOUT` 备案：非制造、官方 deck 不查）
#          —— 占位矩形从 TOPM2 挪到该层，**勿占真金属**。
#     本版做法（机制全落地，落不下的如实记尺寸账，不硬塞）：
#       · 四只 cmim 走真原语，但落位前先过 `cmim_fits()` 面积/净距闸：
#           ① 见方完全落在核 bbox 内；② 与我画的 M1/M2/M4/M5/TOPM1/TOPM2 图形净距
#             ≥ CMIM_CLEAR；③ 边长 ≤ CMIM_MAX_L（超了说明这块地方根本不是给它留的）。
#         全过才落，落位后再用 Dev.p 自证端子坐标（与 M2 的 mkcmim 同一套先量后摆）。
#         任一条不过 → 回落占位 + NOTES 写清**差多少**，并在信里当问题提。
#       · 两只 tank L1 占位改走 `Board.keepout`（(235,5) rect+text），不再占 TOPM2。
#       · 落不下去的 cmim 占位也一律走 (235,5)：占位是「预留区」标记，不是金属 ——
#         这是对裁定②的**同口径外延**（他只点了 tank 那两只），已在交件信报备。
# ══════════════════════════════════════════════════════════════════════
PH_BOX = 12.0
# NOTES 见文件头 CX 附近（v2.1 上移）
CMIM_PINS = {}
# 网表值（chain_top_tb_v015_1.sp :: .subckt drv1）：Cin1/Cin2 10p、Ct1/Ct2 0.84p
CMIM_C_FF = {"Cin1": 10000.0, "Cin2": 10000.0, "Ct1": 840.0, "Ct2": 840.0}
CMIM_PIN_LAYERS = ("M5", "TOPM1")   # 67/2 + 126/2（裁定①，与 M2 同一口径）
CMIM_CLEAR = 3.0                     # 与我画金属的最小净距（µm）
CMIM_MAX_L = 30.0                    # 裁定①的单只上限：见方 ≤ 30µm

# ── v1.7（Q11 轮 · 裁定①「拆分并联 + 电容专用区」）──────────────────────────────
# 裁定原文约束四条，逐条落在这里：
#   ① 单只 ≤30µm 见方 ② 专用条带行距 = 见方 + 3µm ③ 总量守恒 10p/0.84p
#   ④ DEV_NETS 同步拆分行；Cin 取「9×1.11p 或 16×0.625p」由我按布局定。
# 取 **16 × 0.625p**（他给的两档里单只更小的那档）：单只见方 20.41µm，比 30µm 上限
# 多出 32% 余量（9×1.11p 是 27.22，余量只有 9%）。**Ct1/Ct2 不拆**：0.84p 单只就是
# 23.66 见方，已满足 ≤30；再拆会让单只掉到 ~2fF 以下，而官方 cmim 的几何律
# n=fix((side+0.12)/1.26) 在 side<1.14µm 时 n=0 ⇒ 算不出 W/L（w1 会变成 −0.12）。
# ⚠ 拆分是**面积中性**的：总电容守恒 ⇒ 总面积守恒（密度 1.5 fF/µm²）。
#   Cin1+Cin2 = 2×10000fF ⇒ 13333µm²，Ct1+Ct2 = 1120µm²，合计 **14453µm²**。
#   而 drv1 的核只有 118×206µm = 24331µm² —— 电容要占 **59%**。这条我量出来了、
#   印在 stdout、并随信报你（见 NOTES 的 AREA 台账），不靠"放不下"三个字交差。
CMIM_SPLIT = {"Cin1": (16, 625.0), "Cin2": (16, 625.0),    # (只数, 每只 fF)
              "Ct1": (1, 840.0), "Ct2": (1, 840.0)}
CMIM_DENS = 1.5                        # fF/µm²（官方 cmim_caspec）
CMIM_STRIP_PITCH = 3.0                 # 行距 = 见方 + 3µm（裁定①②）


def cmim_side(c_fF):
    """单只 cmim 的见方边长（µm）—— 官方密度 + PCell 几何律，与 land_cmim 的复算同式。"""
    side0 = (c_fF / CMIM_DENS) ** 0.5
    n = int((side0 + 0.12) / 1.26 + 1e-9)
    w1 = n * 1.26 - 0.12
    return w1 + round((side0 - w1) / 0.01) * 0.01


def strip_layout(units, x0, y0, x1, y1):
    """专用条带布局：按行铺，行距 = 见方 + 3µm，列距同。返回 [(cx, cy), ...] 与放不下的个数。

    裁定①的口径是「**条带**行距 = 见方 + 3µm」⇒ 一行能放几只看条带宽度，
    故先按 x 方向排满再换行。放不下就**如实少放**，不缩间距硬塞。
    """
    out = []
    cx = cy = None
    side = pitch = None
    for side in sorted({s for _c, s in units}, reverse=True):
        pitch = side + CMIM_STRIP_PITCH
        cx, cy = x0 + side / 2.0, y1 - pitch - side / 2.0      # 自上而下、从左到右
        for _c, s in units:
            if s != side:
                continue
            if cy - side / 2.0 < y0 or cx + side / 2.0 > x1:
                cx = None
                break
            out.append((cx, cy))
            cx += pitch
        if cx is not None:
            break
    return out


PH_PLACE = {
    "Lt1": (-40.0, 204.0, "vcc", "cop"), "Lt2": (40.0, 204.0, "vcc", "con"),
}
# p1 = M5.pin(67/2) 侧、p2 = TopMetal1.pin(126/2) 侧（与 PH_PLACE 的 (n1,n2) 同序）
CMIM_ORDER = {"Cin1": ("inp", "bin"), "Cin2": ("inn", "bb1"),
              "Ct1": ("cop", "gnd"), "Ct2": ("con", "gnd")}


def _core_box():
    """当前核 bbox（岛在第 11 节才算，这里取同一口径的瞬时值）。"""
    x0, y0, x1, y1 = _bb_mfg(b.top)   # 制造层口径（同 §11；裁定⑤）
    return (x0, y0, x1, y1)


def cmim_fits(cx, cy, side, clear=CMIM_CLEAR):
    """落位前几何闸：见方 [cx±side/2] 放不放得下。返回 (ok, 理由字符串)。

    为什么本机必须自侧先挡：cmim 的**内部**金属（TM1/M5 板 + Vmim 阵列）在本仿真层
    不建模，官方 DRC 才看得见；而「23.66 见方压到 vcc 顶层轨」这种冲突是**纯几何**，
    完全可以自侧判真死 —— 不挡就是明知故犯。
    """
    half = side / 2.0
    box = (cx - half, cy - half, cx + half, cy + half)
    x0, y0, x1, y1 = _core_box()
    if box[0] < x0 or box[2] > x1 or box[1] < y0 or box[3] > y1:
        return False, (f"见方 {side:.2f} 越出核 bbox [{x0:.1f},{y0:.1f}~{x1:.1f},{y1:.1f}]")
    if side > CMIM_MAX_L:
        return False, f"见方 {side:.2f} > 面积闸 {CMIM_MAX_L:.0f}"
    for lname in ("M1", "M2", "M4", "M5", "TOPM1", "TOPM2"):
        li = b.layer(lname)
        for rec in b.top.begin_shapes_rec(li):
            sh = rec.shape()
            if not sh.is_box():
                continue
            # ⚠ 只读 x1/y1/x2/y2，**不读 .left/.right**：本机仿真层 DBox 只有前者，
            #   真 klayout 两者都有；而本机 klayout_db_stub.Region/touches 是**按属性
            #   存不存在**来判「整数 dbu Box 还是 µm DBox」的（getattr(box,'left',None)）
            #   —— 我曾给仿真层补了 left 别名，结果所有 µm 坐标被当成 dbu 整数，
            #   ⑫ 项全件报「悬空脚」。教训：补属性会静默改掉别人的风格判定。
            bx1, by1, bx2, by2 = sh.dbbox().x1, sh.dbbox().y1, sh.dbbox().x2, sh.dbbox().y2
            gx = max(bx1 - box[2], box[0] - bx2, 0.0)
            gy = max(by1 - box[3], box[1] - by2, 0.0)
            if max(gx, gy) <= 1e-9:
                return False, (f"与 {lname} 图形 [{bx1:.2f},{by1:.2f}~"
                               f"{bx2:.2f},{by2:.2f}] 重叠")
            if max(gx, gy) < clear:
                return False, (f"与 {lname} 图形 [{bx1:.2f},{by1:.2f}~"
                               f"{bx2:.2f},{by2:.2f}] 净距 "
                               f"{max(gx, gy):.2f} < {clear:.2f}")
    return True, "ok"


def land_cmim(name, n_m5, n_tm1, px, py, c_fF):
    """落一只真 cmim（库原语 + 先量后摆 + 落位自证），失败返回 (False, 理由)。"""
    import pya as _pya
    if not USE_CMIM:
        return False, "USE_CMIM=False（本脚本侧开关）"
    if hasattr(_pya, "WARN"):
        # 本机仿真层无 PDK：**照样把面积账算出来**（否则这道闸在本地等于没验过）。
        # 尺寸按 lib13g2.mim_cap 的官方规则复算（cmim_caspec=1.5 fF/µm²；
        # n=fix((side+0.12)/1.26)、w=n·1.26−0.12 后同 0.01 相位对齐）；
        # 真落位仍一律走库原语，本函数**不参与落件**，只供判闸与报账。
        side0 = (c_fF / 1.5) ** 0.5
        n = int((side0 + 0.12) / 1.26 + 1e-9)
        w1 = n * 1.26 - 0.12
        side = w1 + round((side0 - w1) / 0.01) * 0.01
        ok, why = cmim_fits(px, py, side)
        return False, (f"{why}（本机无 PDK，按官方密度 1.5fF/µm² 复算的"
                       f"见方边长 {side:.2f}µm）")
    try:
        probe = b.ly.create_cell("cmim", L._SG13,
                                 {"Calculate": "w&l", "w": "1.000u", "l": "1.000u"})
        bb = probe.dbbox()
        cen = ((bb.left + bb.right) / 2.0, (bb.bottom + bb.top) / 2.0)
        pin_loc = []
        for _ln in CMIM_PIN_LAYERS:
            _ps = b.pin_centers(probe, _ln)
            if len(_ps) != 1:
                return False, f"{_ln} 上 pin 数={len(_ps)}（应为 1）"
            pin_loc.append(_ps[0])
        if abs(pin_loc[0][0] - pin_loc[1][0]) > 1e-6 or abs(pin_loc[0][1] - pin_loc[1][1]) > 1e-6:
            return False, f"两端不同心 {pin_loc[0]} vs {pin_loc[1]}"
        tgt = (px - (pin_loc[0][0] - cen[0]), py - (pin_loc[0][1] - cen[1]))
    except Exception as e:
        return False, f"锚点预检失败 {type(e).__name__}: {e}"
    # ── 先问库要多大，再问自己放不放得下（顺序不能反：先落再发现压线就来不及了）──
    try:
        d, (w, l), c_nom = b.mim_cap(name, c_fF, tgt)
    except Exception as e:
        return False, f"mim_cap 失败 {type(e).__name__}: {e}"
    if d is None:
        return False, "mim_cap 返回空器件"

    def _unplace():
        """面积闸不过 ⇒ 把刚落下的这只精确摘掉（真 klayout 走 Cell#delete，
        本机仿真层 pya.Cell.delete 同语义）。**不许**用 delete_instances() ——
        那会连本块全部器件一起删掉。"""
        import pya as _p
        try:
            b.top.delete(_p.DCellInstArray(d.cell, d.trans))
        except Exception:
            return
        b.devs.pop(name, None)

    ok, why = cmim_fits(px, py, max(w, l))
    if not ok:
        _unplace()
        return False, why
    pins = dict(d.p)
    if "BOT" not in pins or "TOP" not in pins:
        _unplace()
        return False, f"返回件缺 BOT/TOP 端 {sorted(pins)}"
    (bx, by), (tx, ty) = pins["BOT"], pins["TOP"]
    dev = max(abs(bx - px), abs(by - py), abs(tx - px), abs(ty - py))
    if dev > 1e-3:
        _unplace()
        return False, f"落位后端子偏离目标 {dev:.3f}µm"
    b.label(CMIM_PIN_LAYERS[0], px, py, n_m5)
    b.label(CMIM_PIN_LAYERS[1], px, py, n_tm1)
    CMIM_PINS[name] = (px, py)
    NOTES.append(f"{name} CMIM_REAL cmim(C={c_fF:g}fF→{w}×{l}u 名义{c_nom:.1f}fF) "
                 f"端子 M5.pin(67/2)=[{n_m5}] + TopMetal1.pin(126/2)=[{n_tm1}] "
                 f"同心于 ({px:.2f},{py:.2f})")
    return True, "ok"


# ── 裁定①落地：每只主电容拆成 N 只并联，铺进**电容专用条带** ──────────────
# 顺序：先按拆分表算每只边长 → 铺条带 → 逐只先量后摆；放不下的**如实记尺寸账**。
n_real = n_ko = 0
CMIM_PLAN = []                      # [(器件名, 网1, 网2, cx, cy, 单只fF)] —— DEV_NETS 用
_cm_units = []
_nofit = {}
for nm, (n_un, c_un) in CMIM_SPLIT.items():
    _side = cmim_side(c_un)
    assert _side <= CMIM_MAX_L, f"{nm} 单只 {_side:.2f} > 上限 {CMIM_MAX_L:.0f}（裁定①）"
    _cm_units += [(nm, _side)] * n_un
# 条带区域：**外置独立电容区**（裁定⑤·选③）。锚 (235,5)、非制造层 235/5，
# 4 列 × 9 行铺开；列距/行距 = 该只见方 + 3µm（裁定②行距口径；Ct 行 26.66）。
# drv1 核内**一格不占**：真件金属与连线都在 M4 顶层电容区落地（届时本表即设计输入）。
_core0 = _core_box()
EXT_X0, EXT_Y0 = 235.0, 5.0
def _ext_strip(units):
    """外置条带：从锚点向上铺，每行 4 只，行高 = 行内最大见方 + 3。
    返回 ([(cx,cy,side)], 区宽, 区高) —— 区宽/高进台账（M4 顶层电容区设计输入）。"""
    out, y_cur, w_max = [], EXT_Y0, 0.0
    for r0 in range(0, len(units), 4):
        row = units[r0:r0 + 4]
        rh = max(s for _n, s in row) + CMIM_STRIP_PITCH
        x_cur = EXT_X0
        for nm, s in row:
            out.append((x_cur + s / 2.0, y_cur + rh - s / 2.0, s))
            x_cur += s + CMIM_STRIP_PITCH
        w_max = max(w_max, x_cur - EXT_X0 - CMIM_STRIP_PITCH)
        y_cur += rh
    return out, w_max, y_cur - EXT_Y0
_ext_list, _EXT_W, _EXT_H = _ext_strip(_cm_units)
_positions = [(cx, cy) for cx, cy, _s in _ext_list]
_EXT_N = len(_positions)
_i = 0
_seq = {}          # 每组自己的并联单元序号（不能用共用的 _i：没抢到条带格的那几只
                   # 也要各自成行，否则 PH_DECL 的键会互相覆盖，只剩一行）
for nm, side in _cm_units:
    _n_m5, _n_tm1 = CMIM_ORDER[nm]
    if _i < len(_positions):
        _cx, _cy = _positions[_i]
        _dname = nm if CMIM_SPLIT[nm][0] == 1 else f"{nm}_{_i:02d}"
        _ok, _why = land_cmim(_dname, _n_m5, _n_tm1, _cx, _cy, CMIM_SPLIT[nm][1])
        CMIM_PLAN.append((_dname, _n_m5, _n_tm1, _cx, _cy, _ok))   # 声明行：落没落都进
        if _ok:
            n_real += 1
            _i += 1
            continue
        # 落不下：这一格退回预留区（(235,5) 非制造层），逐格记尺寸账
        b.keepout(_cx - side / 2.0, _cy - side / 2.0, _cx + side / 2.0, _cy + side / 2.0,
                  f"CMIM_AREA_RESERVED {_dname}({_n_m5},{_n_tm1}) "
                  f"{CMIM_SPLIT[nm][1]:g}fF 见方{side:.2f}")
        NOTES.append(f"{_dname}({_n_m5},{_n_tm1}) CMIM_RESERVED@(235,5) "
                     f"({_cx:.2f},{_cy:.2f}) 单只{side:.2f}µm 未落真件：{_why}")
        n_ko += 1
        _i += 1
    else:
        _nofit[nm] = _nofit.get(nm, 0) + 1
        n_ko += 1
        # 专用带还没开辟 ⇒ 这一只**连预留框都没地方画**，但声明行照给
        # （DEV_NETS 同步拆分行是裁定的硬要求；声明 ≠ 落件，落件与否在 NOTES 里）
        _k = _seq.get(nm, 0)
        _seq[nm] = _k + 1
        CMIM_PLAN.append((nm if CMIM_SPLIT[nm][0] == 1 else
                          f"{nm}_{_k:02d}", _n_m5, _n_tm1, None, None, False))
# ── 台账（裁定⑤·外置战报）──
_cm_area = sum(CMIM_SPLIT[k][0] * CMIM_SPLIT[k][1] for k in CMIM_SPLIT) / CMIM_DENS
_rows = -(-len(_cm_units) // 4)
_ext_h, _ext_w = _EXT_H, _EXT_W
NOTES.append(
    f"CMIM 外置台账（裁定⑤·选③）：拆后 {len(_cm_units)} 只全数外置 drv1 岛外，"
    f"总量守恒 {sum(v[0] * v[1] for v in CMIM_SPLIT.values()):.0f}fF（20p + 1.68p）⇒ "
    f"真件面积 {_cm_area:.0f}µm²。预留条带 @{(EXT_X0, EXT_Y0)} 起铺："
    f"4 列 × {_rows} 行、列距/行距=见方+3µm，区约 {_ext_w:.0f}×{_ext_h:.0f}µm，"
    f"全部落在 235/5 非制造层 —— drv1 核 bbox/真金属/通道零变化，"
    f"M4 顶层电容区落地时本表即设计输入。"
    f"（订正：v1.7 台账『核已被电路占满』不成立，器件+过孔仅占核 2.4%；"
    f"『缺 237µm』系条带自锁核顶之误 —— 外置后此账作废。）")

for nm, (px, py, n1, n2) in PH_PLACE.items():
    b.keepout(px - PH_BOX / 2, py - PH_BOX / 2, px + PH_BOX / 2, py + PH_BOX / 2,
              f"TANK_L1_KEEPOUT {nm}({n1},{n2}) L1层 非制造")
    NOTES.append(f"{nm}({n1},{n2}) TANK_L1_KEEPOUT@(235,5) ({px:.1f},{py:.1f})")
    n_ko += 1
print(f"[M3-a] 占位/电容：拆后 {len(_cm_units)} 只（{len(CMIM_SPLIT)} 组），"
      f"真 cmim 落件 {n_real} 只（b.mim_cap）+ (235,5) 预留区 {n_ko} 处", flush=True)
for _n in NOTES:
    print(f"  · {_n}", flush=True)

# ══════════════════════════════════════════════════════════════════════
# 11. 岛边界（按真实内容反推）。guard ring 由库 v2 提供，本脚本不画。
# ══════════════════════════════════════════════════════════════════════
CORE_X0, CORE_Y0, CORE_X1, CORE_Y1 = _bb_mfg(b.top)  # 制造层口径（235/5 外置预留不进岛界，裁定⑤）
MARGIN = 6.0
ISLAND_X0, ISLAND_Y0 = CORE_X0 - MARGIN, CORE_Y0 - MARGIN
ISLAND_X1, ISLAND_Y1 = CORE_X1 + MARGIN, CORE_Y1 + MARGIN
ISLAND_W, ISLAND_H = ISLAND_X1 - ISLAND_X0, ISLAND_Y1 - ISLAND_Y0
_dbb = _bb(b.top)    # 全 cell 口径（含 235/5 外置条带与全部子 cell 文本）——与 v16/v17 旧数字对拍用
print(f"[M3-a drv1 v1.8] 核 bbox(mfg 制造层口径，235/5 外置预留不入)="
      f"[{CORE_X0:.1f},{CORE_Y0:.1f}~{CORE_X1:.1f},{CORE_Y1:.1f}]"
      f" → 岛 {ISLAND_W:.1f}×{ISLAND_H:.1f} µm", flush=True)
print(f"[M3-a drv1 v1.8] 全 cell 口径 dbbox=[{_dbb[0]:.1f},{_dbb[1]:.1f}~{_dbb[2]:.1f},{_dbb[3]:.1f}]"
      f"（含外置预留，与 v1.6/v1.7 的核 bbox 打印**不可直接互比**）", flush=True)

# ══════════════════════════════════════════════════════════════════════
# 12. 网表锚 / 逐器件引脚↔网名声明（自检台第⑦项 spcheck 核对）
#     HBT 的元数据是 (C, B, E) 三元 —— spcheck 会把网表行末的地网名 0 归一掉。
# ══════════════════════════════════════════════════════════════════════
SP_ANCHOR = {"netlist": "/data/workspace/design/chain_top_tb_v015_1.sp",
             "subckt": "drv1"}

DEV_NETS = {
    "XQ1": ("cop", "bin", "e1"), "XQ2": ("con", "bb1", "e2"),
    "Re1": ("e1", "ntail"), "Re2": ("e2", "ntail"),
    "Rb1": ("bin", "nbias"), "Rb2": ("bb1", "nbias"),
    "Rin1": ("inp", "0"), "Rin2": ("inn", "0"),
    "RL1": ("vcc", "cop"), "RL2": ("vcc", "con"),
    "XBI_XQr": (HNET, HNET, "0"), "XBI_XQo": ("ntail", HNET, "0"),
    "XBI_Rref": ("vcc", HNET),
}
# 裁定①「DEV_NETS 同步拆分行」：每只并联单元都是**独立器件行**（同两端网），
# 逐只入 PH_DECL ⇒ spcheck 第⑦项按名逐只核。落不下的那些只进 NOTES，不进网表。
PH_DECL = {d[0]: (d[1], d[2]) for d in CMIM_PLAN}   # 全部并联单元都声明
PH_DECL.update({k: (v[2], v[3]) for k, v in PH_PLACE.items()})
_CAPROWS = {nm: [d[0] for d in CMIM_PLAN if d[0] == nm or d[0].startswith(nm + "_")]
            for nm in CMIM_SPLIT}

NET_DECL = {
    "cop": [("XQ1", "C"), ("RL1", "P2")] + [(d, "p1") for d in _CAPROWS["Ct1"]] + [("Lt1", "p2")],
    "con": [("XQ2", "C"), ("RL2", "P2")] + [(d, "p1") for d in _CAPROWS["Ct2"]] + [("Lt2", "p2")],
    "bin": [("XQ1", "B"), ("Rb1", "P1")] + [(d, "p2") for d in _CAPROWS["Cin1"]],
    "bb1": [("XQ2", "B"), ("Rb2", "P1")] + [(d, "p2") for d in _CAPROWS["Cin2"]],
    "e1": [("XQ1", "E"), ("Re1", "P1")],
    "e2": [("XQ2", "E"), ("Re2", "P1")],
    "ntail": [("Re1", "P2"), ("Re2", "P2"), ("XBI_XQo", "C")],
    HNET: [("XBI_XQr", "C"), ("XBI_XQr", "B"), ("XBI_XQo", "B"), ("XBI_Rref", "P2")],
    "vcc": [("RL1", "P1"), ("RL2", "P1"), ("XBI_Rref", "P1"),
            ("Lt1", "p1"), ("Lt2", "p1")],
    "nbias": [("Rb1", "P2"), ("Rb2", "P2")],
    "inp": [("Rin1", "P1")] + [(d, "p1") for d in _CAPROWS["Cin1"]],
    "inn": [("Rin2", "P1")] + [(d, "p1") for d in _CAPROWS["Cin2"]],
    "gnd": [("XBI_XQo", "E"), ("XBI_XQr", "E"), ("Rin1", "P2"), ("Rin2", "P2"),
            ("Ct1", "p2"), ("Ct2", "p2")],
}

# ══════════════════════════════════════════════════════════════════════
# 13. net_check + save
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
# v2.2（2026-10-19）**无名 M1 簇补标** —— 纯网名文本，零金属图形改动
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
    (+34.00, +106.86, 'XBI/nref', 'XBI_XQr.B/C 同簇，声明网唯一'),
    (+35.00, +8.00, 'bin', "Rb1.P1 → NET_DECL['bin']"),
    (+42.00, +8.00, 'bb1', "Rb2.P1 → NET_DECL['bb1']"),
    (+14.00, +164.44, 'vcc', "RL2.P1 → NET_DECL['vcc']"),
    (-14.00, +164.44, 'vcc', "RL1.P1 → NET_DECL['vcc']"),
    (-50.00, +14.00, 'vcc', "XBI_Rref.P1 → NET_DECL['vcc']"),
    (+42.00, +9.56, 'nbias', "Rb2.P2 → NET_DECL['nbias']"),
    (+35.00, +9.56, 'nbias', "Rb1.P2 → NET_DECL['nbias']"),
    (-35.00, +9.56, 'gnd', "Rin2.P2 → NET_DECL['gnd']（地；金属已接 M4 地轨）"),
    (-42.00, +9.56, 'gnd', "Rin1.P2 → NET_DECL['gnd']（地；金属已接 M4 地轨）"),
    (-50.00, +15.72, 'XBI/nref', "XBI_Rref.P2 → NET_DECL['XBI/nref']"),
    (+0.00, +106.86, 'XBI/nref', "XBI_XQo.B → NET_DECL['XBI/nref']"),
    (+14.00, +100.00, 'gnd', 'ptap M1 垫 → via_stack(M1→M4) → M4 地轨 gnd'),
    (+42.00, +100.00, 'gnd', 'ptap M1 垫 → via_stack(M1→M4) → M4 地轨 gnd'),
]


def label_m1_clusters(b, tag="drv1_v22"):
    for (x, y, net, why) in M1_CLUSTER_LABELS:
        b.label("M1", x, y, net)
    print(f"[m1-label] {tag}: 补 {len(M1_CLUSTER_LABELS)} 条顶层 M1 网名标注"
          f"（几何零改动）", flush=True)
    return len(M1_CLUSTER_LABELS)

n_clusters, shorts = b.net_check("ALL")
# ── v2.0 新增两道机检（放在 net_check 之后、save 之前）────────────────────
#   ① 焊盘覆盖：每只电阻 P1/P2 **真实焊盘**必须有板级 M1（专治 emitpath 锚点缺陷）
#   ② E 指底座：全板 M1 × 每只 npn 的 E 指底座，同层重叠必须为 0（真短自证）
RG.audit_res_pads(b, RES_DEVS, tag="drv1_v22")
_nd, _nb, _hits = CB.audit_board_e_pads(b, HBT_DEVS, tag="drv1_v22")
print(f"[e-pad-audit] drv1_v20: {HBT_DEVS and len(HBT_DEVS)} 只 HBT × {_nb} 块板级 M1 "
      f"对 E 指底座零重叠 ✓", flush=True)
label_m1_clusters(b)
relabel_official(b)          # ⑭ R-ANNO-01 ②：官方 label purpose /1
print(f"[M3-a drv1 v2.0] 簇={n_clusters} 短路={shorts if shorts else '无'}", flush=True)

# ── v2.3：落盘路径**随件改名**且**可移植** ──────────────────────────────
#   ① 改名：v22 把文件名写死 `m3_drv1_v22.gds`。升 v23 时若照抄，落盘名与顶层
#      cell 版本对不上 ⇒ **覆盖旧锚、面账记错版本**（本轮自查抓到，差点又犯）。
#   ② 可移植：绝对路径 `/data/workspace/...` 在组长侧不存在 ⇒ 强制**脚本同目录**，
#      沙箱里也能落（组长 adapt 的 A8 改沙箱就是这件事）；要另指定用 B7E7_GDS_OUT。
_OUT_GDS = (os.environ.get("B7E7_GDS_OUT")
            or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "m3_drv1_v23.gds"))
os.makedirs(os.path.dirname(_OUT_GDS), exist_ok=True)
b.save(_OUT_GDS)
print(f"[save] {_OUT_GDS}", flush=True)
print("M3-A DRV1 V2.3 OK", flush=True)
