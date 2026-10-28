"""SOW-6 M1 冒烟 · lib13g2 共享库 v1 验证件
跑法：
    . /data/workspace/pdk/kl_env.sh
    KLAYOUT_PATH=/data/workspace/pdk/ihp_open/ihp-sg13g2/libs.tech/klayout \
      klayout -zz -r phys/top/gen_smoke6.py
内容：HBT 差分对（镜像）+ rsil 退化对 + via_stack 发射极下落 + M1 tail + 2×bondpad
验收：生成无错 + net_check 零短路 + bbox 合理（bondpad PCell 首次入库冒烟）
"""
import sys
sys.path.insert(0, "/data/workspace/phys/top")
import lib13g2 as L

b = L.Board("TX5G_SMOKE6")

# 差分对（对称轴 x=6，同 SOW-3 口径）
XD = 0.925
Q1 = b.mkpc_at("Q1", "npn13G2", {"Nx": 2}, (XD, 0.0), "hbt")
Q2 = b.mkpc_at("Q2", "npn13G2", {"Nx": 2}, (12.0 - XD, 0.0), "hbt", mirror=True)
RE1 = b.mkpc_at("RE1", "rsil", {"Calculate": "l", "l": "2u", "w": "1u"}, (XD, -7.5), "res")
RE2 = b.mkpc_at("RE2", "rsil", {"Calculate": "l", "l": "2u", "w": "1u"}, (12.0 - XD, -7.5), "res", mirror=True)
for d in (Q1, Q2, RE1, RE2):
    print("  " + d.report(), flush=True)

# 发射极(M2) -> via_stack -> M1 -> RE 上端（SOW-3 已验证走法）
VIA_M1M2 = b.via  # 方法引用，参数组合缓存内置
def emit_to_re(Q, RE, net):
    ex, ey = Q.p["E"]
    rx, ry = RE.p["P2"]
    via_y = ry + 1.2
    b.via(rx, via_y)
    b.wire_v("M2", ex, ey, via_y + 0.2)
    b.wire_h("M2", via_y + 0.2, ex, rx)
    b.path("M1", [(rx, via_y - 0.2), (rx, ry)])
    b.label("M2", ex, (ey + via_y) / 2, net)

emit_to_re(Q1, RE1, "et1")
emit_to_re(Q2, RE2, "et2")

# tail（M1）
Y_TAIL = RE1.p["P1"][1]
b.wire_h("M1", Y_TAIL, RE1.p["P1"][0], RE2.p["P1"][0])
b.label("M1", 6.0, Y_TAIL, "tail")

# bondpad 冒烟 ×2（官方 PCell 首次入库；shape 必须用 octagon——square 分支 evaluate OOM，PDK pycell bug，2026-10-17 实证）
b.bondpad(-25.0, 0.0, 70.0, "octagon", name="PAD_IN")
b.bondpad(37.0, 0.0, 70.0, "octagon", name="PAD_OUT")
b.label("TOPM2", -25.0, 0.0, "pad_in")

b.net_check("ALL")
b.save("/data/workspace/phys/top/gds/smoke6.gds")
print("SMOKE6 OK", flush=True)
