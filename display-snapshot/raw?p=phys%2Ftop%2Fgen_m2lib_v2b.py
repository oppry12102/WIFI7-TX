"""SOW-6 M1.5b · lib13g2 v2 guard_ring 双环分支专项冒烟（组长 b7a0 2026-10-17）
跑法：
    . /data/workspace/pdk/kl_env030.sh
    KLAYOUT_PATH=/data/workspace/pdk/ihp_open/ihp-sg13g2/libs.tech/klayout \
      klayout -zz -r phys/top/gen_m2lib_v2b.py
背景：gen_m2lib.py（v2a）已验 ptap 单环 + keepout → 官方 maximal DRC 零违规
      （phys/drc/final/m2lib_smoke_run/ ✅ 2026-10-17T03:55Z）。
      本件补两个未验缺口：
  A. guard_ring inner_ntap=True 双环（外 ptap + 内 ntap/nwell，inset 2.0µm）——
     风险面：nwell↔外环 p+（psub tap）间距、nwell↔npn bbox 间距、M1 双环分离。
  B. keepout 与 guard ring 邻接共存（tank 禁区贴驱动级岛的场景）。
验收：生成无错 + net_check（pg/ng 分簇、零短路）+ 官方 maximal DRC 零违规
"""
import sys
sys.path.insert(0, "/data/workspace/phys/top")
import lib13g2 as L

b = L.Board("TX5G_M2LIB_SMOKE_V2B")

# ── A. 双环 guard ring：外 ptap 环 (20,-8)~(60,8)，内 ntap 环 inset 2.0 ──────────
gr = b.guard_ring(20.0, -8.0, 60.0, 8.0, inner_ntap=True)
print(f"[A] 双环返回 {gr}")

# 环内放一颗 npn（Nx=1，bbox 半宽 3.35 → 36.65~43.35 × -3.56~3.56；
# npn bbox 上缘 3.56 ↔ ntap 内缘 5.61 → 2.05µm 间隙）+ 一颗 rsil（psub 器件，验无 nwell 干扰）
Q1 = b.mkpc_at("Q1", "npn13G2", {"Nx": 1}, (40.0, 0.0), "hbt")
RE1 = b.resistor("RE1", "rsil", 30.0, (28.0, -1.0))
print("  " + Q1.report())
print("  " + RE1.report())

# 接线（全 M1，w=0.8 盖头法）：out1 L 形从 RE.P2 到 C——两段均与端头/大板大面积重叠、
# 无暴露边缘对（v2b 两轮实证：w=0.5 竖擦 rsil 端头突出金属 0.13<0.18、横走 y=1.54 又在
# npn C 板上缘 1.25 留 0.04~0.14 窄缝——盖住=合并=无 space/notch 可言）；B 独立
b.wire_v("M1", RE1.p["P2"][0], RE1.p["P2"][1], Q1.p["C"][1], w=0.8)
b.wire_h("M1", Q1.p["C"][1], RE1.p["P2"][0], Q1.p["C"][0], w=0.8)
b.label("M1", Q1.p["C"][0], Q1.p["C"][1], "out1")
b.label("M1", Q1.p["B"][0], Q1.p["B"][1], "in1")
b.label("M1", RE1.p["P1"][0], RE1.p["P1"][1], "tail")

# ── B. keepout 与 guard ring 邻接共存 ─────────────────────────────────────────
b.keepout(64.0, -8.0, 78.0, 8.0, "KEEPOUT_tank_L1")       # 贴外环右缘（外缘 60.39）
b.keepout(14.0, 12.0, 30.0, 20.0, "KEEPOUT_digital_ph")   # 环外上方

# ── 自检：pg(外环)/ng(内环)/out1/in1/tail 分簇，零短路 ─────────────────────────
b.net_check("ALL", pad=1)
b.save("/data/workspace/phys/top/gds/m2lib_v2b.gds")
print("M2LIB V2B SMOKE OK", flush=True)
