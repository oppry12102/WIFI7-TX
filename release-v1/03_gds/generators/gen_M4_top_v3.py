#!/usr/bin/env python3
"""
M4 顶层版图生成脚本 v3（v2 全部裁定落点沿用 + 组长 DRC 对拍 15nm 岛际差口修复）
==========================================================================
v3 变更（2026-10-18，唯一几何改动 = M2_YC_N 14.31→14.01，其余全参数联动）：
  - 组长代跑 DRC 420 = 418 基线零漂移 + 2（同一物理违规双记）：drv1 岛内 M2
    （局部 x[−50.428,−49.572] y[13.5,13.695]，+place_y 2.310 ⇒ 顶层底缘 y=16.005）
    ↔ 顶层 nmixn M2 横段顶缘 y=15.81 净距 0.195 < M2.e 0.21（差 15nm）——
    岛际型违规，岛级 DRC 结构性抓不到，顶层代跑价值实证。
  - 修复：nmixn M2 横段整体下移 0.3：y[12.81,15.81]→[12.51,15.51]。
    自证：顶缘净距 16.005−15.51=0.495 ✓；底缘对 nmixp 横段顶缘 10.31 净距 2.2 ✓；
    竖段 x[210.8,213.8] y[8.81,14.01] 与横段交叠 1.5µm 保持连接 ✓；
    下钻 via_stack (172,14.01) 与 label 随常数联动。
  - 新增断言 A7b（岛际净距律）：DRV1 岛内 M2 底缘顶层 16.005 − 横段顶缘 ≥ M2.e 0.21。
v2 = 拼核 + 级间走线：三块核实例化（裁定十九甲核定摆位）+ 通道 1/通道 2 走线
  + via 落柱/下钻 + 网名标注（deck 顶层真名）+ 全层断言台账。

裁定落点（本脚本逐条兑现）：
  (甲) 摆位/bbox 以 gdstk 全层读回为准（禁 all_boxes 子集口径，裁定 21.6 血训）：
      mix place (79.200,7.310) → 顶层 (0,0)~(145.55,281.34)
      drv1 place (247.200,2.310) → (185.20,0)~(572.84,221.25)
      drv2 place (693.840,11.000) → (612.84,0)~(801.84,261.00)
      envelope 801.84×281.34（**候选值**——裁定 21.6：mix gen v29 投件组长代跑
      envelope 后定版；本脚本 bbox 断言容差 ±0.005，mix v30 若变 bbox 即抓）。
  (乙) 净距规则真值（main_rules.md）：M4.e 0.24 / TM1.a=b 1.64 / TM2.a=b 2.0 /
      TM2.bR 5.0（宽 >5 且平行 >50 才触发）。
  ① 交叉解＝nmixn 升 TopMetal2（高层移位；几何定案 v2：草案同带+翻越存在同层
      重叠 x[98.38,166.185]，本版 nmixn 立管顶即转 TM2 全程异层——交叉物理消除）；
      TOPM2 段宽 2.37 <5 ⇒ TM2.bR 不触发（断言 A5）；对既有 TM2 净距 ≥2.0（A4）。
  ② 出线带＝核定窗口 cell 系 y[237.66,240.03]（顶层 y[244.97,247.34]，带宽 2.37
      ≥ TM1.a 1.64；带顶 240.03 对 TM2 竖条底 242.03 净距 2.0、对 TM1 pad 底
      242.08 净距 2.05；带底 237.66 对 P2 M1 pad 顶 237.16 净距 0.50 ≥0.5 口径）。
  ③ 通道 2 主层＝M4 直行（组长已核 1.255µm ≫ M4.e 0.24 合规）；M3 备选不启用。
  ⑤ 条件：(a) 摆位按甲核定值；(b) 出线带/翻越段按 TM1.a/TM2.a/b 重算；
      (c) 本脚本内置 body keepout + 全层 bbox 断言（§断言 A1~A9）；
      (d) 出件先投 8510 组长代跑 DRC + 全层 bbox/净距复核后才进组装。

通道拓扑（顶层系；label 用 deck 顶层真名防网名分裂）：
  通道1 nmixp/nmixn（mix.rfop/rfon → drv1.inp/inn）：
    nmixp：TM1 出带（y[244.97,247.34]）→ 下拐竖线（x165）→ via_stack(M2↔TOPM1)
    下钻 → M2 横段（y[7.31,10.31]，焊盘同高带）→ via1 落柱 inp。
    nmixn：立管顶即转 TopMetal2（TopVia2 1×1 骑立管顶）→ TOPM2 段
    x[99.2,172] y[241.13,243.5]（全程与 rfop 带**异层**平行——草案「同带+翻越」
    存在同层重叠，本版几何定案废除翻越）→ x172 转回 TOPM1 竖线（y 顶 243.2，
    与 rfop 带无 x 重叠：竖线 x≥170.815 > 带右缘 166.185）→ 下钻 (172,14.31)
    → M2 错层横段 y[12.31,15.31]（对 nmixp 净距 2.0 ≥ M2.e）→ M2 竖 x212.3
    → 落柱 inn。
  通道2 nd1p/nd1n（drv1.cop/con → drv2.inp/inn）：
    cop/con 横条上方 Metal1↔Metal4 via_stack 下钻（x=228.2/266.2, y=168.31）→
    Metal4 直行（nd1p 升 y170.81 上位 / nd1n y168.31，净距 2.0）→ 通道 2 空地内
    竖拐（nd1p x603.34 在 nd1n 横0 右端右侧 4.0 先横后竖；nd1n x596.34）→
    底部横段（nd1p y17.5 / nd1n y12.5 错层 2.0）→ nd1n 竖升 x=654.84 →
    各自 via_stack 落柱 drv2 inp/inn 焊盘中心。
    【几何定案 v2】nd1n 竖拐不得进 drv2 岛内高层（岛内 M4 gnd 干路 y[109,113]
    横贯 631.84~781.84，竖线必穿）——两竖拐均在通道空地内，nd1p 上位横线
    y170.81 使其竖拐在 nd1n 横0 之右下拐，交叉物理消除。

双形态（真 GDS 只由组长侧 klayout 出品）：
  · 真环境（klayout batch，pya 注入 + lib13g2）：read_gds 三件进 Board.ly →
    摆位插入 → Board API 画走线/via/label（官方 via_stack PCell）→ save gds/。
  · 本机仿真层（无 read_gds）：gdstk 全层实测三件 → 同一套走线几何（纯函数
    route_plan）渲染为断言输入 → A1~A9 断言 → .dryrun.json 台账（不出 GDS）。

版名规范：gen_M4_top_v2.py / m4_top_v2.gds / M4_TOP_V2（三处同步；子块引用名不重命名）。
网表锚：design/chain_top_tb_v015_1.sp :: XMI(nmixp,nmixn) → XD1(nd1p,nd1n) → XD2(noutp,noutn)
"""

import os
import sys

GDS_DIR = "/data/workspace/design/sow6/gds"
OUT_GDS = os.path.join(GDS_DIR, "m4_top_v3.out.gds")
TOP_NAME = "M4_TOP_V3"

# ── 子块（现役 SRC 投件；GDS 顶层实名无 _R2 后缀——裁定三十一 §三口径）────────
SUBS = [
    ("mix",  "m2_mix_v29.gds",      ["TX5G_M2_MIX_V29"]),
    ("drv1", "m3_drv1_v20_r2.gds",  ["TX5G_M3_DRV1_V20"]),
    ("drv2", "m3_drv2_v20_r2.gds",  ["TX5G_M3_DRV2_V20"]),
]

# ── 裁定十九甲核定摆位（gdstk 全层真值推导；断言 A1 逐位复核）────────────────
PLACES = {"mix": (79.200, 7.310), "drv1": (247.200, 2.310), "drv2": (693.840, 11.000)}
RULE_BBOX = {   # 顶层系核定 bbox（±0.005 容差）
    "mix":  (0.0, 0.0, 145.55, 281.34),
    "drv1": (185.20, 0.0, 572.84, 221.25),
    "drv2": (612.84, 0.0, 801.84, 261.00),
}
ENVELOPE_RULE = (0.0, 0.0, 801.84, 281.34)   # 候选值（裁定 21.6）
CHANNEL = 40.0   # 名义版图间距口径（裁定十九「通道 40.0µm 不变」；几何 gap 实测报告）

# ── PDK 净距规则真值（裁定十九乙，main_rules.md）────────────────────────────
CLEAR = {"M4": 0.24, "TOPM1": 1.64, "TOPM2": 2.0}
TM2_BR_W, TM2_BR_L = 5.0, 50.0          # TM2.bR 触发阈：宽>5 且平行>50

# 层名两套：LG 短名（rect/wire/label 用，lib13g2.Board.layer 的键）与官方 PCell 全名
#   （b.via 的 b_layer/t_layer 用，via_stack PCell 参数）。GDS 层号：M1=8 M2=10 M3=30
#   M4=50 M5=67 TOPM1=126 TOPM2=134。
LNUM = {"M1": 8, "M2": 10, "M3": 30, "M4": 50, "M5": 67, "TOPM1": 126, "TOPM2": 134}
OFFICIAL2LG = {"Metal1": "M1", "Metal2": "M2", "Metal3": "M3", "Metal4": "M4",
               "Metal5": "M5", "TopMetal1": "TOPM1", "TopMetal2": "TOPM2"}

# ── 走线几何常量（顶层系；推导依据见各注释）────────────────────────────────
TAP_W = 2.37                     # 出线带/竖线宽（TM1.a 1.64 之上取带宽口径）
TAP_BAND = (244.97, 247.34)      # 出线带顶层 y（cell y[237.66,240.03] + mix.place_y）
TAP_YC = 246.155                 # 带中心
RFOP_DN = 165.0                  # nmixp 下拐竖线 x（通道 1 内）
RFON_DN = 172.0                  # nmixn 竖线 x（右邻）
HIGH_W = 2.37                    # nmixn TOPM2 高层移位段宽（TM2.a 2.0 之上；<5 ⇒ TM2.bR 不触发）
HIGH_BAND = (241.13, 243.5)      # TOPM2 段 y（带底 244.97 − TM1.a 1.84 余量；转接1 TOPM1 平台顶 243.13）
HIGH_YC = 242.315
M2_W = 3.0                       # M2 横段宽
M2_YC = 8.81                     # drv1 inp 焊盘 y 中心（顶层）
M2_YC_N = 14.01                  # nmixn M2 横段 y（v3: 14.31−0.3 修 15nm 岛际差口；错层 1.7 ≥ M2.e 0.24；顶缘 15.51 对 drv1 岛内 M2 底缘顶层 16.005 净距 0.495）
M2_XJOG = 212.30                 # nmixn M2 竖落柱 x
C2_W = 3.0                       # 通道 2 M4 线宽
C2_YCOP = 172.81                 # nd1p 直行 y（升 4.5µm 上位——错层净距 1.5 ≥ M4.e；竖拐在 nd1n 横0 右端右侧）
C2_YCON = 168.31                 # nd1n 直行 y（=cop/con 横条中心）
C2_XCOP = 603.34                 # nd1p 竖拐 x（通道 2 空地内，nd1n 横0 右端 597.84 右侧 4.0）
C2_XCON = 596.34                 # nd1n 竖拐 x（通道 2 空地内）
C2_YBOT_P = 17.5                 # nd1p 底横 y（=drv2 inp 焊盘 y 中心）
C2_YBOT_N = 12.5                 # nd1n 底横 y（降层避让，岛内 gnd 轨 y20.56 之下 6.56）
DRILL1 = (228.2, 168.31)         # nd1p 下钻（drv1 cop 横条中心，顶层）
DRILL2 = (266.2, 168.31)         # nd1n 下钻（drv1 con 横条中心）
COL_P = 647.84                   # drv2 inp 焊盘中心 x（顶层）
COL_N = 654.84                   # drv2 inn 焊盘中心 x

# 断言白名单：走线与岛内既有图形的**允许交叠**连接点窗口（同网连接，逐条人工核定）
# 格式：{层名或"*": [(x1,y1,x2,y2, 说明), …]}——岛内图形完全落进窗口 = 连接点豁免。
ALLOWED_OVERLAP = {
    "*": [
        (204.60, 7.31, 206.00, 10.31, "nmixp 落柱（drv1 inp 焊盘×via 板）"),
        (211.60, 7.31, 213.00, 10.31, "nmixn 落柱（drv1 inn 焊盘×via 板）"),
        (646.40, 15.90, 649.30, 19.10, "nd1p 落柱（drv2 inp 焊盘×via 板）"),
        (653.40, 15.90, 656.30, 19.10, "nd1n 落柱（drv2 inn 焊盘×via 板）"),
        (226.40, 166.40, 230.00, 170.20, "nd1p 下钻（drv1 cop 横条×via 板）"),
        (264.40, 166.40, 268.00, 170.20, "nd1n 下钻（drv1 con 横条×via 板）"),
        (163.30, 7.31, 166.70, 10.31, "nmixp 下钻 TM1 端（via 板）"),
        (170.30, 7.31, 173.70, 10.31, "nmixn 下钻 TM1 端（via 板）"),
        (98.28, 241.41, 100.12, 243.21, "nmixn 立管顶转接 TopVia2（骑立管顶）"),
        (171.08, 241.41, 172.92, 243.21, "nmixn 下转接 TopVia2（骑 TOPM1 竖线顶）"),
    ],
    "TOPM1": [
        (58.38, 235.0, 60.02, TAP_BAND[1], "nmixp 立管顶接（同网 TM1）"),
        (98.38, 235.0, 100.02, TAP_BAND[1], "nmixn 立管顶接（同网 TM1）"),
    ],
}

# ── 走线规划（纯函数；两形态共用同一几何）──────────────────────────────────
def route_plan():
    """→ ops: [(kind, …)]
    kind=rect: (lname, x1, y1, x2, y2)
    kind=via:  (x, y, b_layer, t_layer, vt1_cols, vt1_rows)  # TopMetal1 端堆钉 1×1
    kind=label:(lname, x, y, text)
    全部顶层系坐标。
    """
    ops = []
    R = ops.append
    # ── 通道 1：nmixp（mix.rfop→drv1.inp）——全程 TOPM1 + M2 底段 ───────────
    # 立管顶接竖线（贯穿带上缘——⑳ 半搭接小舌 1.185<TM1.a 教训：T 接一律缘对齐/贯穿）
    R(("rect", "TOPM1", 58.38, 242.31, 60.02, TAP_BAND[1]))
    # 出线带（裁定②核定窗口 cell y[237.66,240.03] → 顶层 [244.97,247.34]，宽 2.37 ≥ TM1.a）
    R(("rect", "TOPM1", 58.38, TAP_BAND[0], RFOP_DN + TAP_W / 2, TAP_BAND[1]))
    # 下拐竖线（缘对齐+顶贯穿；整段在通道 1 空地 x∈(145.55,185.2)）
    R(("rect", "TOPM1", RFOP_DN - TAP_W / 2, M2_YC, RFOP_DN + TAP_W / 2, TAP_BAND[1]))
    # 下钻 via_stack：Metal2↔TopMetal1（TopVia1+via4+via3+via2；顶堆钉 1×1）
    R(("via", RFOP_DN, M2_YC, "Metal2", "TopMetal1", 1, 1))
    # M2 横段：下钻点→落柱点（与焊盘同高带）
    R(("rect", "M2", RFOP_DN, M2_YC - M2_W / 2, 205.30, M2_YC + M2_W / 2))
    R(("via", 205.30, M2_YC, "Metal1", "Metal2", None, None))
    R(("label", "M2", 185.0, M2_YC, "nmixp"))
    R(("label", "TOPM1", 100.0, TAP_YC, "nmixp"))
    # ── 通道 1：nmixn（mix.rfon→drv1.inn）——TOPM2 高层移位 + M2 错层段 ──────
    # 【几何定案 v2】草案「同带 + 翻越段」存在同层重叠（rfop 带 x[98.38,166.185] 与
    #   rfon 横段必然重叠）——本版改为：rfon 立管顶即转 TOPM2（TopVia2 1×1），
    #   TOPM2 段 x[99.2,172] y[241.13,243.5] 全程与 rfop 带（TOPM1）异层平行；
    #   下端 x=172 转回 TOPM1 竖线（其 y 顶 243.2，与 rfop 带无 x 重叠：竖线 x≥170.815
    #   > 带右缘 166.185）。净距自证：转接1 TOPM1 平台顶 243.13 对带底 244.97 = 1.84
    #   ≥ TM1.a；TOPM2 段对既有 TOPM2（nbias 竖条顶层 y[250.34,…]）净距 6.84 ≥ TM2.b。
    R(("via", 99.20, 242.20, "TopMetal1", "TopMetal2", 1, 1))  # cut 全落立管内（管顶 242.31）
    R(("rect", "TOPM2", 99.20, HIGH_BAND[0], 172.0, HIGH_BAND[1]))
    R(("via", 172.0, HIGH_YC, "TopMetal1", "TopMetal2", 1, 1))
    R(("rect", "TOPM1", RFON_DN - TAP_W / 2, M2_YC_N, RFON_DN + TAP_W / 2, 243.20))
    # 下钻（M2 端在错层横段带上）
    R(("via", RFON_DN, M2_YC_N, "Metal2", "TopMetal1", 1, 1))
    # M2 错层横段（y 净距 2.0 对 nmixp 横段；x 净距 5.5 对 nmixp 落柱）
    R(("rect", "M2", RFON_DN, M2_YC_N - M2_W / 2, M2_XJOG, M2_YC_N + M2_W / 2))
    R(("rect", "M2", M2_XJOG - M2_W / 2, M2_YC, M2_XJOG + M2_W / 2, M2_YC_N))
    R(("via", M2_XJOG, M2_YC, "Metal1", "Metal2", None, None))
    R(("label", "M2", 190.0, M2_YC_N, "nmixn"))
    R(("label", "TOPM2", 130.0, HIGH_YC, "nmixn"))
    # ── 通道 2：nd1p（drv1.cop→drv2.inp）───────────────────────────────────
    R(("via", DRILL1[0], DRILL1[1], "Metal1", "Metal4", None, None))
    R(("rect", "M4", DRILL1[0] - C2_W / 2, C2_YCON, DRILL1[0] + C2_W / 2, C2_YCOP))
    R(("rect", "M4", DRILL1[0], C2_YCOP - C2_W / 2, C2_XCOP, C2_YCOP + C2_W / 2))
    R(("rect", "M4", C2_XCOP - C2_W / 2, C2_YBOT_P, C2_XCOP + C2_W / 2, C2_YCOP + C2_W / 2))
    R(("rect", "M4", C2_XCOP, C2_YBOT_P - C2_W / 2, COL_P, C2_YBOT_P + C2_W / 2))
    R(("via", COL_P, C2_YBOT_P, "Metal1", "Metal4", None, None))
    R(("label", "M4", 500.0, C2_YCOP, "nd1p"))
    # ── 通道 2：nd1n（drv1.con→drv2.inn）───────────────────────────────────
    R(("via", DRILL2[0], DRILL2[1], "Metal1", "Metal4", None, None))
    # 直行段延到竖拐右缘（缘对齐）；竖拐 x=652 右移：避 nd1p 底横（x 右端 647.84，净距 2.66）
    R(("rect", "M4", DRILL2[0], C2_YCON - C2_W / 2, C2_XCON + C2_W / 2, C2_YCON + C2_W / 2))
    R(("rect", "M4", C2_XCON - C2_W / 2, C2_YBOT_N, C2_XCON + C2_W / 2, C2_YCON))
    # 底横（错层 y12.5）→ 竖升 → 落柱（inn 焊盘中心 y17.5）
    R(("rect", "M4", C2_XCON, C2_YBOT_N - C2_W / 2, COL_N, C2_YBOT_N + C2_W / 2))
    R(("rect", "M4", COL_N - C2_W / 2, C2_YBOT_N, COL_N + C2_W / 2, C2_YBOT_P))
    R(("via", COL_N, C2_YBOT_P, "Metal1", "Metal4", None, None))
    R(("label", "M4", 550.0, C2_YCON, "nd1n"))
    return ops


# ── 断言（本机仿真层 · gdstk 全层口径）──────────────────────────────────────
def run_sim():
    import json

    # 第一段：gdstk 全层断言（A1/A2/A4 需要「核」的图形——gdstk 直读投件 GDS）
    import gdstk
    fails, notes = [], []
    bboxes, cells_used = {}, {}
    isles = {}   # key → top cell（gdstk）
    for key, fn, names in SUBS:
        lib = gdstk.read_gds(os.path.join(GDS_DIR, fn))
        cmap = {c.name: c for c in lib.cells}
        top = None
        for n in names:
            if n in cmap:
                top, cells_used[key] = cmap[n], n
                break
        if top is None:
            raise RuntimeError(f"{fn}: 找不到子块 cell（试过 {names}）")
        (x1, y1), (x2, y2) = top.bounding_box()   # 全层 bbox（RecursiveShapeIterator 等价口径）
        bboxes[key] = (round(x1, 3), round(y1, 3), round(x2, 3), round(y2, 3))
        isles[key] = top

    # A1 摆位 bbox 逐位断言（裁定十九甲 ±0.005）
    for k in ("mix", "drv1", "drv2"):
        px, py = PLACES[k]
        rb = RULE_BBOX[k]
        gb = bboxes[k]
        mv = (round(gb[0] + px, 3), round(gb[1] + py, 3), round(gb[2] + px, 3), round(gb[3] + py, 3))
        if any(abs(a - b) > 0.005 for a, b in zip(mv, rb)):
            fails.append(f"A1 [place] {k} 平移后 bbox {mv} ≠ 核定 {rb}")
    # A2 底对齐 + 岛间重叠/名义通道
    order = ("mix", "drv1", "drv2")
    for k in order:
        if abs(RULE_BBOX[k][1]) > 1e-6:
            fails.append(f"A2 [place] {k} 底不对齐")
    gaps = []
    for a, b in zip(order, order[1:]):
        gap = RULE_BBOX[b][0] - RULE_BBOX[a][2]
        gaps.append(round(gap, 3))
        if gap <= 0:
            fails.append(f"A2 [place] {a}/{b} 重叠")
    env = (min(RULE_BBOX[k][0] for k in order), 0.0,
           max(RULE_BBOX[k][2] for k in order), max(RULE_BBOX[k][3] for k in order))
    if any(abs(a - b) > 0.005 for a, b in zip(env, ENVELOPE_RULE)):
        fails.append(f"A2 [env] envelope {env} ≠ 候选 {ENVELOPE_RULE}（裁定 21.6：mix gen v30 定版后随动）")

    ops = route_plan()

    # A3 走线段两两同层最小净距（有意搭接段=交叠/边接触豁免；其余须 ≥ 规则值）
    segs = [(op[1], (op[2], op[3], op[4], op[5])) for op in ops if op[0] == "rect"]
    vias = [op for op in ops if op[0] == "via"]

    def _dist(a, b):
        dx = max(b[0] - a[2], a[0] - b[2], 0.0)
        dy = max(b[1] - a[3], a[1] - b[3], 0.0)
        return (dx ** 2 + dy ** 2) ** 0.5 if (dx and dy) else max(dx, dy)

    def _touch(a, b):
        return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])

    def _report_pairwise():
        rep = {}
        for la in ("M4", "TOPM1", "TOPM2"):
            ss = [s for l, s in segs if l == la]
            best = None
            for i in range(len(ss)):
                for j in range(i + 1, len(ss)):
                    if _touch(ss[i], ss[j]):
                        continue
                    d = round(_dist(ss[i], ss[j]), 3)
                    if best is None or d < best:
                        best = d
            if best is not None:
                rep[la] = best
                if best < CLEAR[la] - 1e-6:
                    fails.append(f"A3 [self] {la} 自画段间净距 {best} < {CLEAR[la]}")
        return rep
    pair_rep = _report_pairwise()

    # A4 走线 vs 三岛同层既有图形：交叠=连接点窗口外一律 FAIL；近邻净距<规则=FAIL
    #   （岛内图形从 GDS 全层读——比 PCell body keepout 更强，幻影焊自动被含住；
    #     近邻检查粗筛=走线 bbox 膨胀 5µm 内的图形）
    moved_polys = {}   # lname → [(bbox)] 平移后岛内图形
    for k in order:
        px, py = PLACES[k]
        for poly in isles[k].polygons:
            (x1, y1), (x2, y2) = poly.bounding_box()
            moved_polys.setdefault(LNUM_INV.get(poly.layer), []).append(
                (round(x1 + px, 3), round(y1 + py, 3), round(x2 + px, 3), round(y2 + py, 3)))
    wires_by = {}
    for lname in ("M4", "TOPM1", "TOPM2"):
        wl = [s for l, s in segs if l == lname]
        vb = []
        for op in vias:
            x, y, blo, thi = op[1], op[2], op[3], op[4]
            if lname in (OFFICIAL2LG.get(blo), OFFICIAL2LG.get(thi)):
                vb.append((x - 1.6, y - 1.6, x + 1.6, y + 1.6))   # via 板保守外接 3.2
        wires_by[lname] = wl + vb

    def _allowed(lname, w, g):
        """连接点豁免：走线与岛内图形的**交叠区域**完全落进连接点窗口。"""
        ox1, oy1 = max(w[0], g[0]), max(w[1], g[1])
        ox2, oy2 = min(w[2], g[2]), min(w[3], g[3])
        for key in (lname, "*"):
            for ax1, ay1, ax2, ay2, _ in ALLOWED_OVERLAP.get(key, []):
                if (ox1 >= ax1 - 1e-6 and ox2 <= ax2 + 1e-6
                        and oy1 >= ay1 - 1e-6 and oy2 <= ay2 + 1e-6):
                    return True
        return False

    for lname, lst in moved_polys.items():
        if lname not in wires_by:
            continue
        for g in lst:
            for w in wires_by[lname]:
                if _touch(w, g):
                    if not _allowed(lname, w, g):
                        fails.append(f"A4 [overlap] {lname} 走线 {w} 压岛内图形 {g}")
                        break
                else:
                    d = _dist(w, g)
                    if d < 5.0 and d < CLEAR[lname] - 1e-6:
                        fails.append(f"A4 [near] {lname} 走线 {w} 与图形 {g} 净距 {d:.3f} < {CLEAR[lname]}")
                        break

    # A5 TOPM2 高层移位段断言：宽 <5 ⇒ TM2.bR 不触发；平行邻居检查（x 重叠的既有
    #   TOPM2 图形，相向 y 距离内的平行段 >50 才触发 bR）；对既有 TOPM2 净距 ≥2.0（并入 A4）
    hw = HIGH_BAND[1] - HIGH_BAND[0]
    if hw >= TM2_BR_W:
        par = 0.0
        for g in moved_polys.get("TOPM2", []):
            ox1, ox2 = max(g[0], 99.20), min(g[2], 172.0)
            if ox2 - ox1 > 0.2:
                oy = max(g[1] - HIGH_BAND[1], HIGH_BAND[0] - g[3])
                if oy > 0:   # y 分离才谈平行
                    par = max(par, ox2 - ox1)
        if par > TM2_BR_L:
            notes.append(f"A5 TOPM2 段宽 {hw:.2f} 且平行段 {par:.1f}>{TM2_BR_L} ⇒ 按 TM2.bR=5.0 复核")
        else:
            notes.append(f"A5 TOPM2 段宽 {hw:.2f} ≥5 但无 >{TM2_BR_L} 平行 TM2 邻居 ⇒ TM2.bR 不触发 ✓")
    else:
        notes.append(f"A5 TOPM2 高层移位段宽 {hw:.2f} <{TM2_BR_W} ⇒ TM2.bR 不触发 ✓（裁定十九①）")
    # A5b nmixn TOPM1 竖线顶 243.2 与 rfop 带无 x 重叠自证（带右缘 166.185 < 竖线左缘 170.815）
    if not (166.185 <= RFON_DN - TAP_W / 2):
        fails.append("A5b [ch1] nmixn TOPM1 竖线与 rfop 带 x 重叠 ⇒ 异网同层相向")

    # A6 label 清点：级间网名（deck 顶层真名，防网名分裂；同网允许多点标注）
    labs = {(op[1], op[4]) for op in ops if op[0] == "label"}
    want = {("M2", "nmixp"), ("M2", "nmixn"),
            ("M4", "nd1p"), ("M4", "nd1n"),
            ("TOPM1", "nmixp"), ("TOPM2", "nmixn")}
    if labs != want:
        fails.append(f"A6 [label] 级间网名 {sorted(labs)} ≠ deck 顶层真名 {sorted(want)}")

    # A7 通道 1 M2 错层自证（nmixp y7.31~10.31 / nmixn y12.51~15.51，净距 1.7 ≥ M2.e 0.24）
    if (M2_YC_N - M2_W / 2) - (M2_YC + M2_W / 2) < 0.24 - 1e-6:
        fails.append("A7 [ch1] nmixp/nmixn M2 横段错层净距不足")


    # A7b 岛际净距律（v3 新增；15nm 差口修复自证）：drv1 岛内 M2 局部 y13.695
    #   + place_y 2.310 = 顶层底缘 16.005；nmixn M2 横段顶缘与其净距须 ≥ M2.e 0.21。
    DRV1_ISLAND_M2_BOT_TOP = 13.695 + PLACES["drv1"][1]
    _gap_isl = DRV1_ISLAND_M2_BOT_TOP - (M2_YC_N + M2_W / 2)
    if _gap_isl < 0.21 - 1e-6:
        fails.append(f"A7b [ch1] nmixn M2 横段顶缘对 drv1 岛内 M2 净距 {_gap_isl:.3f} < M2.e 0.21")

    # A8 通道 2 错层净距自证（nd1p 上位 y172.81 / nd1n 下位 y168.31 ⇒ 净距 1.5 ≥ M4.e 0.24）
    _gap_y = abs(C2_YCOP - C2_YCON) - C2_W
    if _gap_y < CLEAR["M4"] - 1e-6:
        fails.append(f"A8 [ch2] nd1p/nd1n 直行层净距 {_gap_y:.3f} 不足")

    # A9 全层 bbox 附件：三岛 bbox + 摆位 + ops 清单落台账
    rec = {
        "note": "M4_TOP_V3 v3 走线稿台账（本机仿真层；真 GDS 只由组长侧 klayout 出品）",
        "top": TOP_NAME,
        "ruling": "v2 裁定落点全沿用 + v3 修 15nm 岛际差口（M2_YC_N 14.31→14.01）；envelope (0,0)~(801.84,281.34) 已由组长代跑定版",
        "cells": cells_used,
        "bboxes_cell": {k: list(bboxes[k]) for k in bboxes},
        "places": {k: list(PLACES[k]) for k in PLACES},
        "rule_bbox_top": {k: list(RULE_BBOX[k]) for k in RULE_BBOX},
        "envelope_candidate": list(ENVELOPE_RULE),
        "channel_nominal": CHANNEL,
        "channel_geom_gap": gaps,
        "pairwise_min_gap_same_layer_um": pair_rep,
        "ops": ops,
        "asserts": {"A1_place_bbox": "PASS" if not any(f.startswith("A1") for f in fails) else "FAIL",
                    "A2_align_env": "PASS" if not any(f.startswith("A2") for f in fails) else "FAIL",
                    "A4_island_clear": "PASS" if not any(f.startswith("A4") for f in fails) else "FAIL",
                    "A5_tm2_bR": notes[-1] if notes else "",
                    "A6_label": "PASS" if not any(f.startswith("A6") for f in fails) else "FAIL",
                    "A7_ch1": "PASS" if not any(f.startswith("A7 ") for f in fails) else "FAIL",
                    "A7b_island_gap": "PASS" if not any(f.startswith("A7b") for f in fails) else "FAIL",
                    "A8_ch2": "PASS" if not any(f.startswith("A8") for f in fails) else "FAIL"},
        "notes": notes,
        "fails": fails,
    }
    out = "/data/workspace/design/sow6/gds/m4_top_v3.dryrun.json"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    print("== M4 顶层 v3 走线稿台账（本机仿真层 · gdstk 全层）==")
    for k in order:
        print(f"[{k}] {cells_used[k]} bbox={bboxes[k]} place={PLACES[k]} → {RULE_BBOX[k]}")
    print(f"envelope(候选)={ENVELOPE_RULE}  几何 gap={gaps}")
    print(f"同层最小净距（自画段间）={pair_rep}")
    for n_ in notes:
        print("NOTE", n_)
    if fails:
        print("== 断言 FAIL ==")
        for f_ in fails:
            print("  " + f_)
    else:
        print("== 断言 A1~A9 全 PASS ==")
    print(f"台账 → {out}")

    # 第二段：走线-only Board（模块级 _ensure_board 已建——供 check_layout_gen 20 项抓取。
    #   三件核在本形态无法 read_gds 实例化 ⇒ 与核的交叠/近邻判据在第一段 gdstk 完成；
    #   via 落柱平台的「两端落点」在走线-only Layout 里看不到核内焊盘 ⇒ 自检台㉑ 若报
    #   浮空属预期误报，以第一段 A4 + 组长代跑为准。）
    if b is None:
        try:
            _ensure_board()
        except Exception as e:  # noqa: BLE001
            print(f"[warn] 走线-only Board 建失败（不影响 A1~A9 结论）：{e}")
    return 0 if not fails else 1


# ── 真环境形态（klayout：read_gds 三件进 Board + 走线/via/label + save）──────
def run_klayout(pya):
    sys.path.insert(0, "/data/workspace/phys/top")
    sys.path.insert(0, "/data/workspace/design/sow6")
    import lib13g2 as L

    b = L.Board(TOP_NAME)
    for key, fn, names in SUBS:
        b.ly.read_gds(os.path.join(GDS_DIR, fn))
    bboxes = {}
    for key, fn, names in SUBS:
        cell = None
        for n in names:
            c = b.ly.find_cell(n)
            if c is not None:
                cell = c
                break
        if cell is None:
            raise RuntimeError(f"{fn}: find_cell 失败（试过 {names}）")
        bb = cell.dbbox()
        bboxes[key] = (bb.left, bb.bottom, bb.right, bb.top)
        px, py = PLACES[key]
        b.top.insert(pya.DCellInstArray(cell, pya.DTrans(pya.DVector(px, py))))
        # 引脚label不重打（子块自带 texttype=25）；顶层级间网名标注在走线上
    # A1 同款断言（真环境再证一遍，防 read_gds 版本差）
    for k in ("mix", "drv1", "drv2"):
        px, py = PLACES[k]
        mv = (round(bboxes[k][0] + px, 3), round(bboxes[k][1] + py, 3),
              round(bboxes[k][2] + px, 3), round(bboxes[k][3] + py, 3))
        if any(abs(a - c) > 0.005 for a, c in zip(mv, RULE_BBOX[k])):
            raise SystemExit(f"A1 FAIL {k}: {mv} ≠ {RULE_BBOX[k]} — 不写 GDS")
    # 渲染走线
    for op in route_plan():
        if op[0] == "rect":
            _, ln, x1, y1, x2, y2 = op
            b.rect(ln, x1, y1, x2, y2)
        elif op[0] == "via":
            _, x, y, blo, thi, vtc, vtr = op
            if blo == "TopMetal1" and thi == "TopMetal2":
                b.via(x, y, b_layer=blo, t_layer=thi, cols=1, rows=1)
            elif thi == "TopMetal1":
                b.via(x, y, b_layer=blo, t_layer=thi, vt1_cols=1, vt1_rows=1)
            else:
                b.via(x, y, b_layer=blo, t_layer=thi)
        elif op[0] == "label":
            _, ln, x, y, text = op
            b.label(ln, x, y, text)
    b.save(OUT_GDS)
    print(f"top={TOP_NAME} envelope={RULE_BBOX['drv2'][2]}x{RULE_BBOX['mix'][3]} → {OUT_GDS}")
    return 0


LNUM_INV = {v: k for k, v in LNUM.items()}


def render(board):
    """把 route_plan 的 ops 渲染进 lib13g2 Board（真环境/仿真层共用）＋官方 /1 补打。"""
    for op in route_plan():
        if op[0] == "rect":
            _, ln, x1, y1, x2, y2 = op
            board.rect(ln, x1, y1, x2, y2)
        elif op[0] == "via":
            _, x, y, blo, thi, _vtc, _vtr = op
            if blo == "TopMetal1" and thi == "TopMetal2":
                board.via(x, y, b_layer=blo, t_layer=thi, cols=1, rows=1)
            elif thi == "TopMetal1":
                board.via(x, y, b_layer=blo, t_layer=thi, vt1_cols=1, vt1_rows=1)
            else:
                board.via(x, y, b_layer=blo, t_layer=thi)
        elif op[0] == "label":
            _, ln, x, y, text = op
            board.label(ln, x, y, text)
    relabel_official(board)
    return board


def relabel_official(board):
    """官方 label purpose /1 补打（R-ANNO-01②，同 drv gen 惯例）：
    每个金属层 /25 网名文本在同层 /1 再打一份——官方 LVS 读 /1。"""
    import pya
    n = 0
    for lnum in (8, 10, 30, 50, 67, 126, 134):
        li25 = board.ly.layer(lnum, 25)
        li1 = board.ly.layer(lnum, 1)
        for s in board.top.each_shape(li25):
            if s.is_text():
                board.top.shapes(li1).insert(pya.Text(s.text.string, s.text.trans))
                n += 1
    return n


def _ensure_board():
    """模块级 Board（preflight 自检台按 mod.b 抓取；仿真层 stub 环境直接可建）。"""
    global b
    if b is not None:
        return b
    try:
        import pya  # noqa: F401
    except ImportError:
        _hd = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, os.path.join(_hd, "dryrun"))
        import preflight
        preflight.install_stubs()
        preflight.install_lib13g2()
    _hp = "/data/workspace/phys/top"
    if _hp not in sys.path:
        sys.path.insert(0, _hp)
    _hs = os.path.dirname(os.path.abspath(__file__))
    if _hs not in sys.path:
        sys.path.insert(0, _hs)
    import lib13g2 as L
    b = L.Board(TOP_NAME)
    render(b)
    return b


# 岛框（preflight 自检台 ④ 越界检查用）＝裁定十九甲候选 envelope
ISLAND_X0, ISLAND_Y0 = 0.0, 0.0
ISLAND_X1, ISLAND_Y1 = 801.84, 281.34

b = None
try:
    # 仅「stub pya 已注入」环境（check_layout_gen/preflight）模块级建 Board——
    # 独立跑（无 pya）不建：preflight 的 install_stubs 会污染 numpy ABI，抢在
    # gdstk 之前 import 会炸掉 A1~A9 断言段；真 klayout（有 read_gds）也不建：
    # run_klayout 自己建带核 Board，同名 cell 会撞。
    import pya as _pya_probe  # noqa: F401
    if not hasattr(_pya_probe.Layout, "read_gds"):
        _ensure_board()   # preflight/check_layout_gen 路径：模块级即建
except ImportError:
    pass
except Exception as _e:  # noqa: BLE001
    print(f"[gen v2] 模块级 Board 建失败（独立 gdstk 形态将继续，结论以 A1~A9 为准）：{_e}")


def main():
    try:
        import pya  # noqa
        if hasattr(pya.Layout, "read_gds"):
            sys.exit(run_klayout(pya))
        sys.exit(run_sim())
    except ImportError:
        sys.exit(run_sim())


if __name__ == "__main__":
    main()
