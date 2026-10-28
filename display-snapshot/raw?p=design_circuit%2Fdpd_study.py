#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dpd_study.py — DPD 取舍量化研究（支撑任务书 OQ-4「DPD 是否纳入架构」）

不引入新的失真模型：所有数字都来自 budget_check.py 的同一套公式与同一份
params.csv（唯一数据源），只是换着问「DPD 拿掉会怎样、拿掉后有哪些替代
路线、各自要付多少 dB / 多少 mW / 是否还守得住规格」。

问的四个问题：
  表 A  DPD 三阶 IM3 对消量敏感性 —— 满功率下 DPD 要做多少 dB 才不击穿？
  表 B  无 DPD 的回退路线（两种机理差别巨大，必须分开建模）
        M1 驱动回退：降 VGA 驱动、PA 偏置不动 → OIP3 不变，每 1 dB 回退换 3 dB IM3
        M2 偏置回退：降 PA 偏置省电 → OIP3 随电流下降，回退换来的线性度很少
  表 C  无 DPD 无回退：把 PA 做大（OIP3 +Δ dB）要多少电流？能否守住功耗上限？
        电流标度指数 OIP3 ∝ I^exp 取 1.0 / 1.5 / 2.0 三档做敏感性（不押单一假设）
  表 D  若把 2.4G/6G 设计目标放回规范值（放弃自设裕量），无 DPD 的代价是什么

判定口径（与 budget_check.py 完全一致，避免自说自话）：
  EVM 判定 = 全链 EVM ≤ (设计目标 − 自设裕量)
  总体合格 = EVM 判定 且 每块 EVM 优于分配值 ≥ 裕量 且 功耗 ≤ 上限 且 输出功率 = 规格

用法：
    python3 dpd_study.py                 # 两条带全跑
    python3 dpd_study.py --band g24      # 只跑一条带
    python3 dpd_study.py --json dpd_study.json

显式假设（均为工程近似，输出中已标注）：
  * IM3 模型沿用 budget_check：P_IM3 = 0.75·(P/OIP3)³·P
    ⇒ IM3_dBc = −1.25 + 3·(P_dBm − OIP3_dBm)
  * M2（偏置回退）取 OIP3 ∝ I^1.5：偏置电流减半时 OIP3 掉 4.5 dB 而非 6 dB。
  * M1（驱动回退）PA 直流不变：线性度变好但功耗不省（效率下降）。
  * M2 中 PA 直流 ∝ 10^(−X/20)（输出功率与电流同比例）。
  * 回退只改驱动/VGA 增益，其余各级的 EVM 贡献与相噪项按参数表不变。
  * DPD 引擎为两带共用（同一时刻只有一个频带发射），故 60 mW 只计一次。
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import budget_check as bc  # noqa: E402

CSV = os.path.join(HERE, "params.csv")
CFG = "design"

# 表 C 电流标度指数敏感性（OIP3 ∝ I^exp）
UPSIZE_EXPONENTS = [1.0, 1.5, 2.0]
# 表 B 回退扫描网格（dB，步进 0.5）
BO_DB = [i / 2.0 for i in range(0, 25)]
# 表 A 的 DPD 对消量扫描（dB，步进 1）
DPD_SWEEP = list(range(0, 33))


def fresh(csv_path):
    return bc.Params(csv_path)


def bl(r, name):
    v = r["evm_blocks"].get(name)
    return v if v is not None else float("nan")


def head(title, label):
    print("=" * 96)
    print("%s    band=%s" % (title, label))
    print("=" * 96)


def fmt_p(pout_spec):
    return "规格✓" if abs(pout_spec[0] - pout_spec[1]) <= 0.5 else "规格✗"


# ---------------------------------------------------------------- 表 A
def table_a(P0, csv_path, band, label, target, margin):
    need = target - margin
    head("表 A  DPD 三阶 IM3 对消量敏感性（满功率，其余设计参数不动）", label)
    pa_alloc = float(P0.get("spec", band, "PA", "evm_alloc_db",
                            P0.get("arch", band, "PA", "evm_alloc_db")))
    print("  设计目标 %.1f dB，自设裕量 %.0f dB → EVM 判定线 %.1f dB；"
          "PA 分配 %.1f dB（须优于它 ≥%.0f dB）"
          % (target, margin, need, pa_alloc, margin))
    print("  %6s %10s %10s %10s %10s %6s %6s" %
          ("DPD_dB", "PA块EVM", "全链EVM", "PA裕量", "总功耗", "EVM", "总体"))
    min_evm = min_all = None
    for d in DPD_SWEEP:
        r = bc.compute(fresh(csv_path), CFG, band, margin, dpd_override=float(d))
        pa = bl(r, "PA")
        ok_evm = r["evm_total_db"] <= need
        ok_all = bool(r["overall_pass"])
        if ok_evm and min_evm is None:
            min_evm = d
        if ok_all and min_all is None:
            min_all = d
        print("  %6d %10.1f %10.1f %10.1f %10.0f %6s %6s" %
              (d, pa, r["evm_total_db"], pa_alloc - pa, r["pdc_total_mw"],
               "✓" if ok_evm else "✗", "✓" if ok_all else "✗"))
    print("  -> 满功率下所需最小 DPD 对消量：EVM 口径 %s / 总体口径（含逐块分配）%s"
          % (_fmt_d(min_evm), _fmt_d(min_all)))
    print("  （设计取值 %.0f dB，见 params.csv design/<band>/PA/dpd_im3_cancel_db）"
          % float(P0.get(CFG, band, "PA", "dpd_im3_cancel_db", 0.0)))
    print()
    return min_evm, min_all


def _fmt_d(x):
    return "%.0f dB" % x if x is not None else "30 dB 以内无解"


# ---------------------------------------------------------------- 表 B
def table_b(P0, csv_path, band, label, target, margin):
    need = target - margin
    head("表 B  无 DPD 的回退路线（两种机理必须分开看）", label)
    base = bc.compute(fresh(csv_path), CFG, band, margin, dpd_override=0.0)
    oip3_pa0 = base["stages"]["PA"]["oip3_db"]
    pa_dc0 = float(base["pdc_mw"]["PA"])
    g_vga0 = float(P0.get(CFG, band, "VGA", "gain_db", 0.0))
    pout0 = base["p_out_db"]
    pout_spec = float(P0.get("spec", band, "PA", "p_out_db"))
    print("  基线（无 DPD 满功率）：PA 块 %.1f dB，全链 %.1f dB，PA OIP3 %.1f dBm / "
          "直流 %.0f mW，总功耗 %.0f mW"
          % (bl(base, "PA"), base["evm_total_db"], oip3_pa0, pa_dc0,
             base["pdc_total_mw"]))
    print()
    print("  M1 驱动回退：PA 偏置不动 ⇒ OIP3 不变（每 1 dB 输出回退 ≈ 3 dB IM3 改善），"
          "直流不变 ⇒ 功耗不省")
    print("  %6s %8s %10s %10s %10s %10s %6s %6s" %
          ("回退dB", "Pout", "PA块EVM", "全链EVM", "PA直流", "总功耗", "EVM", "总体"))
    m1_evm = m1_all = None
    for x in BO_DB:
        P = fresh(csv_path)
        P.rows[(CFG, band, "VGA", "gain_db")] = g_vga0 - x
        r = bc.compute(P, CFG, band, margin, dpd_override=0.0)
        ok_evm = r["evm_total_db"] <= need
        ok_all = bool(r["overall_pass"])
        if ok_evm and m1_evm is None:
            m1_evm = (x, r["p_out_db"])
        if ok_all and m1_all is None:
            m1_all = (x, r["p_out_db"])
        print("  %6.1f %8.1f %10.1f %10.1f %10.0f %10.0f %6s %6s" %
              (x, r["p_out_db"], bl(r, "PA"), r["evm_total_db"],
               r["pdc_mw"]["PA"], r["pdc_total_mw"],
               "✓" if ok_evm else "✗", "✓" if ok_all else "✗"))
    print("  -> M1：EVM 口径最小回退 %s；总体口径（含输出功率规格）%s"
          % (_fmt_bo(m1_evm, pout0), _fmt_bo(m1_all, pout0)))
    print()

    print("  M2 偏置回退：降 PA 偏置省电，但 OIP3 随电流下降 ⇒ 线性度收益只有 M1 的 "
          "exp/3 = 0.5")
    print("  %6s %8s %10s %10s %10s %10s %10s %6s" %
          ("回退dB", "Pout", "PA直流", "OIP3", "PA块EVM", "全链EVM", "总功耗", "EVM"))
    m2_evm = None
    for x in BO_DB:
        P = fresh(csv_path)
        P.rows[(CFG, band, "VGA", "gain_db")] = g_vga0 - x
        P.rows[(CFG, band, "PA", "pdc_mw")] = pa_dc0 * bc.dB2W(-x / 2.0)
        # ΔOIP3_dB = 10·exp·log10(10^(−x/20)) = −0.5·exp·x（exp=1.5 ⇒ −0.75 dB / dB 回退）
        P.rows[(CFG, band, "PA", "oip3_db")] = oip3_pa0 - 0.5 * 1.5 * x
        r = bc.compute(P, CFG, band, margin, dpd_override=0.0)
        ok_evm = r["evm_total_db"] <= need
        if ok_evm and m2_evm is None:
            m2_evm = (x, r["p_out_db"], r["pdc_total_mw"])
        print("  %6.1f %8.1f %10.0f %10.1f %10.1f %10.1f %10.0f %6s" %
              (x, r["p_out_db"], r["pdc_mw"]["PA"], r["stages"]["PA"]["oip3_db"],
               bl(r, "PA"), r["evm_total_db"], r["pdc_total_mw"],
               "✓" if ok_evm else "✗"))
    print("  -> M2：EVM 口径最小回退 %s" % _fmt_bo(m2_evm, pout0))
    print("     （省下的电：回退 %.1f dB 时总功耗 %.0f mW，基线 %.0f mW）"
          % (m2_evm[0], m2_evm[2], base["pdc_total_mw"]) if m2_evm else "")
    print()
    return m1_evm, m2_evm


def _fmt_bo(t, pout0):
    if t is None:
        return "回退 12 dB 以内无解"
    return "%.1f dB（Pout %.1f dBm，规格 %.1f dBm → 降功率 %.1f dB）" % (
        t[0], t[1], pout0, pout0 - t[1])


# ---------------------------------------------------------------- 表 C
def table_c(P0, csv_path, band, label, target, margin):
    need = target - margin
    head("表 C  无 DPD 无回退：把 PA 做大（OIP3 +Δ，电流标度指数做敏感性）", label)
    base = bc.compute(fresh(csv_path), CFG, band, margin, dpd_override=0.0)
    oip3_pa0 = base["stages"]["PA"]["oip3_db"]
    pa_dc0 = float(base["pdc_mw"]["PA"])
    cap = float(base["pdc_max_mw"]) if base["pdc_max_mw"] else float("nan")
    pa_alloc = float(P0.get("spec", band, "PA", "evm_alloc_db",
                            P0.get("arch", band, "PA", "evm_alloc_db")))
    print("  PA 基线：OIP3 %.1f dBm，直流 %.0f mW；功耗上限 %.0f mW；PA 分配 %.1f dB"
          % (oip3_pa0, pa_dc0, cap, pa_alloc))
    for exp in UPSIZE_EXPONENTS:
        print("  OIP3 ∝ I^%.1f （ΔOIP3 %.0f dB ⇒ 电流 ×%.1f）："
              % (exp, 10.0, bc.dB2W(10.0) ** (1.0 / exp)))
        print("    %6s %10s %10s %10s %10s %6s %6s" %
              ("ΔOIP3", "电流倍数", "PA直流", "全链EVM", "总功耗", "EVM", "总体"))
        hit = None
        for d in [0, 2, 4, 6, 8, 10, 12, 15, 18, 21, 24]:
            ratio = bc.dB2W(d) ** (1.0 / exp)
            P = fresh(csv_path)
            P.rows[(CFG, band, "PA", "pdc_mw")] = pa_dc0 * ratio
            P.rows[(CFG, band, "PA", "oip3_db")] = oip3_pa0 + d
            r = bc.compute(P, CFG, band, margin, dpd_override=0.0)
            ok_evm = r["evm_total_db"] <= need
            ok_all = bool(r["overall_pass"])
            if ok_all and hit is None:
                hit = (d, ratio, r["pdc_total_mw"])
            print("    %6.1f %10.2f %10.0f %10.1f %10.0f %6s %6s" %
                  (d, ratio, r["pdc_mw"]["PA"], r["evm_total_db"],
                   r["pdc_total_mw"], "✓" if ok_evm else "✗",
                   "✓" if ok_all else "✗"))
        if hit:
            print("    -> 最小可过 OIP3 增量 %.0f dB（电流 ×%.1f，总功耗 %.0f mW "
                  "vs 上限 %.0f mW）" % (hit[0], hit[1], hit[2], cap))
        else:
            print("    -> ΔOIP3 扫描至 +24 dB 仍无法同时满足 EVM 与功耗上限")
        print()
    print("  注：并联合并（器件数量线性标度）对应 exp=1.0；提高单管过驱对应 exp≈1.5~2.0。")
    print("      两档结论一致：靠加大 PA 电流换线性度在本功耗预算内不成立。")
    print()


# ---------------------------------------------------------------- 表 D
def table_d(P0, csv_path, band, label, target, margin, norm):
    head("表 D  若把设计目标放回规范值：无 DPD 的代价", label)
    print("  规范值 %.1f dB，设计目标 %.1f dB（自设 %.0f dB 裕量）。"
          "下表给出每个目标下、无 DPD 时要满足它所需的最小驱动回退及其输出功率。"
          % (norm, target, margin))
    print("  %8s %10s %10s %10s %10s" %
          ("目标dB", "所需回退", "对应Pout", "规格差", "全链功耗"))
    rec = {}
    for t in [target, -40.0, norm]:
        hit = None
        g_vga0 = float(P0.get(CFG, band, "VGA", "gain_db", 0.0))
        for i in range(0, 121):
            x = i / 10.0
            P = fresh(csv_path)
            P.rows[(CFG, band, "VGA", "gain_db")] = g_vga0 - x
            r = bc.compute(P, CFG, band, 0.0, dpd_override=0.0)
            if r["evm_total_db"] <= t:
                hit = (x, r["p_out_db"], r["pdc_total_mw"])
                break
        if hit is None:
            print("  %8.1f %10s %10s %10s %10s" % (t, "无解(≤12dB)", "-", "-", "-"))
            rec[t] = None
        else:
            pout_spec = float(P0.get("spec", band, "PA", "p_out_db"))
            print("  %8.1f %10.1f %10.1f %10.1f %10.0f" %
                  (t, hit[0], hit[1], hit[1] - pout_spec, hit[2]))
            rec[t] = hit
    print()
    print("  注：表 D 的回退必然压低输出功率（与表 B 的规格判定一致），"
          "等于用链路余量换 EVM 裕量；是否可接受属规格裁决事项（回信请裁决）。")
    print()
    return rec


def main():
    ap = argparse.ArgumentParser(description="DPD 取舍量化研究")
    ap.add_argument("--csv", default=CSV)
    ap.add_argument("--band", default=None, choices=["g56", "g24"])
    ap.add_argument("--margin", type=float, default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    bands = [(a.band, dict(bc.BANDS)[a.band])] if a.band else bc.BANDS
    out = []
    for band, label in bands:
        P0 = bc.Params(a.csv)
        target = float(P0.get("spec", band, "SYS", "evm_target_db", -41))
        norm = float(P0.get("spec", band, "SYS", "evm_norm_db", -38))
        margin = a.margin if a.margin is not None else \
            float(P0.get("spec", "sys", "SYS", "evm_margin_min_db", 2))
        print("目标 EVM %.1f dB（规范 %.1f dB），自设裕量 %.0f dB\n" % (target, norm, margin))
        rec = {"band": band, "target_db": target, "norm_db": norm, "margin_db": margin}
        rec["min_dpd_evm_db"], rec["min_dpd_all_db"] = \
            table_a(P0, a.csv, band, label, target, margin)
        m1, m2 = table_b(P0, a.csv, band, label, target, margin)
        rec["m1_backoff_db"] = m1[0] if m1 else None
        rec["m2_backoff_db"] = m2[0] if m2 else None
        table_c(P0, a.csv, band, label, target, margin)
        rec["spec_target"] = {str(k): v for k, v in
                              table_d(P0, a.csv, band, label, target, margin, norm).items()}
        out.append(rec)

    print("=" * 96)
    print("结论速览（数字均可由本脚本复跑：python3 dpd_study.py）")
    print("=" * 96)
    for rec in out:
        print("  [%s] 满功率所需最小 DPD 对消：EVM 口径 %s / 总体口径 %s"
              % (rec["band"], _fmt_d(rec["min_dpd_evm_db"]), _fmt_d(rec["min_dpd_all_db"])))
        print("       无 DPD 替代：驱动回退 %s；偏置回退 %s；加大 PA 见表 C（三档指数均超功耗上限）"
              % ("%.1f dB" % rec["m1_backoff_db"] if rec["m1_backoff_db"] is not None else ">12 dB 无解",
                 "%.1f dB" % rec["m2_backoff_db"] if rec["m2_backoff_db"] is not None else ">12 dB 无解"))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print("JSON 已写出：%s" % a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
