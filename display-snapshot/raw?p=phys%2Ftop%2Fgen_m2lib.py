"""SOW-6 M1.5 · lib13g2 v2 新原语冒烟 v2（组长 b7a0 2026-10-17）
跑法：
    . /data/workspace/pdk/kl_env030.sh
    KLAYOUT_PATH=/data/workspace/pdk/ihp_open/ihp-sg13g2/libs.tech/klayout \
      klayout -zz -r phys/top/gen_m2lib.py
内容（b7e7 M2 需求单 8 项中 v2 新增 5 项 + 镜像校验）：
  ① hbtdiff_array 'ABBA'（nx=1，两端 dummy×1，pitch=7.40 官方合法间距）
  ② hbtdiff_array quad 2×2 ['AB','BA'] + 对角 label + sym_pairs 镜像校验
    （冒烟不接 C 竖条——sym 校验只依赖 label 坐标，避免简化接线引入挤压违规）
  ③ via_bucket 124 件减层 stack（Via1 + TopVia1，M2 汇流）——DRC 销点件
  ④ resistor rsil 30Ω（Re 口径）/ rhigh 2k（Rb 口径），grid snap 后名义值回报
  ⑤ mim_cap 0.84pF（Ct 口径，官方密度 1.5fF/µm²，grid snap）
  ⑥ guard_ring ptap 环包 gm 阵列（内缘离 npn bbox ≥0.7µm）
  ⑦ keepout tank 禁区标注
验收：生成无错 + net_check 零短路 + sym OK + 官方 DRC maximal 零违规
"""
import sys
sys.path.insert(0, "/data/workspace/phys/top")
import lib13g2 as L

b = L.Board("TX5G_M2LIB_SMOKE")

# ① gm ABBA 共质心（nx=1 演示口径；实际 gm nx=3 由 b7e7 M2 v1.0 坐标化定）宽 4×7.4=29.6
g, gm_cen = b.hbtdiff_array("ABBA", (45.0, 0.0), nx=1, dummies=1)
print(f"[hbtdiff] ABBA+dummy → {sorted((k, len(v)) for k, v in g.items())} 中心={gm_cen}")
print("  " + g["A"][0].report())

# ⑥ guard_ring 包住 gm 阵列（阵列整体 bbox 23.15~66.85 × -3.33~3.78——Nx=1 bbox 半宽 3.35；
#    两轮实证：环 tap 不得进入 npn substrate-tie 环带（LU.d1/npnG2.c/pSD.b 连锁），内缘离 bbox ≥1.5µm）
gr = b.guard_ring(21.0, -5.7, 69.0, 5.7)

# ② quad 2×2（['AB','BA']，同向摆放，pitch=7.40 / 行距 7.85）+ 对角 label（不接线）
q, quad_cen = b.hbtdiff_array(["AB", "BA"], (30.0, 25.0), nx=1, mirror=False)
print(f"[hbtdiff] quad 2×2 → {sorted((k, len(v)) for k, v in q.items())} 中心={quad_cen}")
AXIS = quad_cen[0]
# A = 左上 + 右下（对角），B = 右上 + 左下；label 只标注坐标供 sym 校验
b.label("M1", q["A"][0].p["C"][0], q["A"][0].p["C"][1] + 1.0, "lopd")
b.label("M1", q["A"][1].p["C"][0], q["A"][1].p["C"][1] + 1.0, "lopd")
b.label("M1", q["B"][0].p["C"][0], q["B"][0].p["C"][1] + 1.0, "lond")
b.label("M1", q["B"][1].p["C"][0], q["B"][1].p["C"][1] + 1.0, "lond")

# ③ via_bucket 124 件减层 stack（mix 级发射极回流口径；drv2 同原语 n=187）
vb = b.via_bucket(12.0, -12.0, 124, tag="mix_emit")

# ④ 电阻（官方 rspec 真值自动解 W/L + grid snap）
RE1 = b.resistor("RE1", "rsil", 30.0, (6.0, -14.0))
RB1 = b.resistor("RB1", "rhigh", 2000.0, (75.0, -14.0))
print("  " + RE1.report())
print("  " + RB1.report())

# ⑤ cmim 0.84pF（Ct 口径；官方密度 1.5fF/µm²，grid snap 后名义值回报）
CT1, wh, cn = b.mim_cap("CT1", 840.0, (52.0, 18.0))
print("  CT1 pins:", {k: (round(v[0], 3), round(v[1], 3)) for k, v in CT1.p.items()})

# ⑦ keepout（tank/L1 备案禁区块示意）
b.keepout(8.0, 8.0, 18.0, 20.0, "KEEPOUT_tank_L1")

# 自检：连通 + quad 对角镜像互换校验（轴=quad 中心 x；lopd/lond 悬空 label 属预期）
b.net_check("ALL", pad=1, sym_pairs=[("lopd", "lond")], axis_x=AXIS)
b.save("/data/workspace/phys/top/gds/m2lib_smoke.gds")
print("M2LIB SMOKE OK", flush=True)
