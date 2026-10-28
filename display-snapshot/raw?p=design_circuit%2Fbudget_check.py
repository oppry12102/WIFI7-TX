#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
budget_check.py — WiFi7-TX 电路级预算复算（任务书 SOW-1 第 2/3 项）

复算四件事：
  (1) 级联增益 / 级联 OP1dB / 级联 OIP3（简化级联公式）
  (2) 各 EVM 贡献块 → RSS 合成全链 EVM
  (3) 与 architecture.md 预算表逐项对账（对比表）
  (4) EVM 分配对账：每块是否优于分配值 ≥ margin（默认 2 dB）

全部数值来自同目录 params.csv，脚本内不写死设计值。
口径与假设见 design_circuit.md §1.3（EVM_dB = 10log10(Perr/Psig)）。

用法：
    python3 budget_check.py                       # 默认：design 配置，6G+2.4G
    python3 budget_check.py --config arch         # 用架构给定值复算
    python3 budget_check.py --band g56            # 只跑一条带
    python3 budget_check.py --margin 3            # 提高 EVM 裕量门槛
    python3 budget_check.py --pa-sweep            # 扫 PA 直流 -> 可达全链 EVM
    python3 budget_check.py --csv my.csv --json out.json
"""

import argparse
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(HERE, "params.csv")

# ---- 信号链顺序（结构定义，非设计数值）----
CHAIN = ["DAC", "LPF", "VGA", "MIX", "DRV", "PA"]
POWER_ONLY = ["PLL", "AUX", "DPD"]
BANDS = [("g56", "5-6G (320MHz@4096QAM)"), ("g24", "2.4G")]


# ---------------------------------------------------------------- 参数装载
class Params:
    def __init__(self, path):
        self.rows = {}
        self.note = {}
        with open(path, newline="", encoding="utf-8") as f:
            lines = [ln for ln in f if not ln.lstrip().startswith("#")]
        for r in csv.DictReader(lines):
                if not r.get("config"):
                    continue
                k = (r["config"].strip(), r["band"].strip(),
                     r["stage"].strip(), r["param"].strip())
                v = r["value"].strip()
                try:
                    v = float(v)
                except ValueError:
                    pass
                self.rows[k] = v
                self.note[k] = (r.get("unit", "").strip(), r.get("note", "").strip())

    def raw(self, cfg, band, stage, param, default=None):
        return self.rows.get((cfg, band, stage, param), default)

    def get(self, cfg, band, stage, param, default=None):
        """当前配置取值；缺失时回退到架构配置，再回退默认。"""
        for c in (cfg, "arch"):
            v = self.rows.get((c, band, stage, param))
            if v is not None:
                return v
        return default


# ---------------------------------------------------------------- 小工具
def dB2W(db):
    return 10.0 ** (db / 10.0)


def W2dB(w):
    return 10.0 * math.log10(w)


def pm2dB(x):
    """幅度 -> dB"""
    return 20.0 * math.log10(x)


def dB2pm(db):
    return 10.0 ** (db / 20.0)


def w_to_dbm(w):
    """线性功率（任意同量纲）-> dBm"""
    return W2dB(w) + 30.0


# ---------------------------------------------------------------- 相位噪声
def _l_ref(f, l100k, slope_dbdec):
    """参考振荡器单边带相噪 dBc/Hz：f<100k 按 slope 下降，f>100k 持平。"""
    if f < 1e5:
        return l100k + slope_dbdec * math.log10(1e5 / f)
    return l100k


def _l_vco(f, l100k, f_flicker, slope_below):
    """VCO 开环相噪：f<转折按 slope_below，f>转折按 20dB/dec。"""
    if f_flicker > 0:
        l_c = l100k + 20.0 * math.log10(f_flicker / 1e5) if f_flicker > 1e5 else \
              l100k - slope_below * math.log10(1e5 / f_flicker)
    else:
        l_c = l100k
    if f < f_flicker:
        return l_c + slope_below * math.log10(f_flicker / f)
    return l_c - 20.0 * math.log10(f / f_flicker)


def _l_total(f, P, band, override=None):
    """总单边带相噪 L(f) dBc/Hz（开环口径；环路内 VCO 项被抑制）"""
    ov = override or {}
    f0 = ov.get("f0_hz", P.get("design", band, "LO_IPN", "f0_hz"))
    fvco = ov.get("vco_f_hz", P.get("design", band, "LO_IPN", "vco_f_hz"))
    fref = ov.get("f_ref_hz", P.get("design", band, "LO_IPN", "f_ref_hz"))
    bw = ov.get("pll_bw_hz", P.get("design", band, "LO_IPN", "pll_bw_hz"))
    l_ref100 = ov.get("ref_l_100k_dbchz", P.get("design", band, "LO_IPN", "ref_l_100k_dbchz"))
    ref_slope = ov.get("ref_slope_dbdec", P.get("design", band, "LO_IPN", "ref_slope_dbdec", 20))
    l_vco100 = ov.get("vco_l_100k_dbchz", P.get("design", band, "LO_IPN", "vco_l_100k_dbchz"))
    f_fl = ov.get("vco_flicker_hz", P.get("design", band, "LO_IPN", "vco_flicker_hz"))
    v_slope = ov.get("vco_slope_below_dbdec", P.get("design", band, "LO_IPN", "vco_slope_below_dbdec", 30))
    nd = ov.get("divider_n", P.get("design", band, "LO_IPN", "divider_n", 1))
    l_div = ov.get("divider_l_dbchz", P.get("design", band, "LO_IPN", "divider_l_dbchz", -140))

    # 参考倍频项（环路内）：参考相噪 x (fvco/fref)^2
    l_floor = _l_ref(f, l_ref100, ref_slope) + pm2dB(fvco / fref)
    # VCO 项：环路内被二阶环压制（(f_bw/f)^2）；环路外直通，另加分频器自身底噪
    l_v = _l_vco(f, l_vco100, f_fl, v_slope)
    l_div_floor = l_div                        # 分频器自身 1/f 底噪
    if f < bw:
        l_v_sup = l_v - 40.0 * math.log10(bw / f)   # 二阶环压制
        return max(l_floor, l_div_floor, l_v_sup)
    # 理想 1/N 分频保持 dBc/Hz 相噪不变；仅叠加分频器自身噪声
    return max(l_v, l_div_floor)


_PN_CACHE = {}


def phase_noise(P, band, override=None):
    """返回 (L_int_dBc, EVM_dB, sigma_rad, fs_t, region)"""
    ov = override or {}
    key = (band, tuple(sorted((k, repr(v)) for k, v in ov.items() if k != "steps")))
    if key in _PN_CACHE:
        return _PN_CACHE[key]
    ov = override or {}
    f_lo = ov.get("int_f_lo", P.get("design", band, "LO_IPN", "int_f_lo", 1e3))
    f_hi = ov.get("int_f_hi", P.get("design", band, "LO_IPN", "int_f_hi", 1e8))
    n = int(ov.get("steps", 400000))
    # 对数扫描积分 sigma^2 = 2*integral L(f) df
    lin = [f_lo * (f_hi / f_lo) ** (i / n) for i in range(n + 1)]
    lin[0], lin[-1] = f_lo, f_hi
    tot = 0.0
    region = {}
    for a, b in zip(lin, lin[1:]):
        mid = math.sqrt(a * b)
        l = _l_total(mid, P, band, ov)
        tot += dB2W(l) * (b - a)
    sigma = math.sqrt(2.0 * tot)              # rad rms
    l_int = W2dB(tot) + 3.0103                # 积分相噪 dBc（单边带定义）
    # 相噪→EVM：误差/信号 = sqrt(sigma^2/2)
    evm = W2dB(sigma ** 2 / 2.0)
    fs_t = sigma / (2 * math.pi * (ov.get("f0_hz", P.get("design", band, "LO_IPN", "f0_hz"))))
    region["bw"] = ov.get("pll_bw_hz", P.get("design", band, "LO_IPN", "pll_bw_hz"))
    out = (l_int, evm, sigma, fs_t, region)
    _PN_CACHE[key] = out
    return out


# ---------------------------------------------------------------- 主计算
def compute(P, cfg, band, margin_db=2.0, dpd_override=None):
    S = P.get("spec", band, "SYS", None)
    k = P.get("spec", "sys", "SYS", "im3_k", 0.75)
    target = P.get("spec", band, "SYS", "evm_target_db",
                   P.get("spec", "sys", "SYS", "evm_target_db", -41))
    p_in = P.get(cfg, band, "SYS", "chain_in_db", -5.0)
    p_out_spec = P.get("spec", band, "PA", "p_out_db")

    out = {"config": cfg, "band": band, "k_im3": k, "target_db": target,
           "margin_db": margin_db, "stages": {}, "errors": []}

    # ---- (1) 增益级联与各级电平 ----
    p = p_in
    for st in CHAIN:
        g = float(P.get(cfg, band, st, "gain_db", 0.0) or 0.0)
        oip3 = P.get(cfg, band, st, "oip3_db")
        pdc = P.get(cfg, band, st, "pdc_mw")
        pae = P.get(cfg, band, st, "pae_at_p1db")
        oo = float(P.get(cfg, band, st, "oip3_over_p1db", 0.0) or 0.0)
        p1db = P.get(cfg, band, st, "op1db_db")
        if p1db is None and pae and pdc:      # 由 PA 直流 + P1dB 处效率推出
            p1db = w_to_dbm((float(pdc) / 1000.0) * float(pae))
        if oip3 is None and p1db is not None and oo:   # OIP3 = P1dB + 经验余量
            oip3 = float(p1db) + float(oo)
        out["stages"][st] = {"gain_db": g, "p_in_db": p, "p_out_db": p + g,
                             "oip3_db": oip3, "op1db_db": p1db, "pdc_mw": pdc,
                             "oip3_over_p1db": oo}
        p += g
    out["gain_total_db"] = p - p_in
    out["p_out_db"] = p
    out["p_out_spec_db"] = p_out_spec
    out["p_in_db"] = p_in

    p_final_w = dB2W(out["p_out_db"])
    out["p_final_w"] = p_final_w

    # ---- (2) OIP3 级联（dB 域倒数相加：1/OIP3_tot = sum 10^(2*prefixGain - OIP3_i)/10）----
    prefix = 0.0
    s_oip3 = 0.0
    for st in CHAIN:
        o = out["stages"][st]["oip3_db"]
        if o is None:
            prefix += out["stages"][st]["gain_db"]
            continue
        # 1/IIP3_tot = Σ_i G_prefix_i^2 / OIP3_i  （dB 域：10^((2*prefix-OIP3_i)/10)）
        s_oip3 += dB2W(2 * prefix - float(o))
        prefix += out["stages"][st]["gain_db"]
    iip3_cas = -W2dB(s_oip3) if s_oip3 > 0 else None
    oip3_cas = (iip3_cas + out["gain_total_db"]) if iip3_cas is not None else None
    out["iip3_cascade_db"] = iip3_cas
    out["oip3_cascade_db"] = oip3_cas

    # ---- (3) OP1dB 级联（简化式：min_i[ P1dB_i - 后续级总增益 ]）----
    best, who = None, None
    suffix = {}
    for st in CHAIN:
        suffix[st] = sum(out["stages"][x]["gain_db"] for x in CHAIN[CHAIN.index(st) + 1:])
    for st in CHAIN:
        v = out["stages"][st]["op1db_db"]
        if v is None:
            continue
        cand = float(v) + suffix[st]   # 折算到链输出：P1dB_i + 其后各级增益
        if best is None or cand < best:
            best, who = cand, st
    out["op1db_cascade_db"] = best
    out["op1db_limited_by"] = who

    # ---- (4) 各块 EVM ----
    # 4a. 由 OIP3 推导的模拟级块
    dpd_db = P.get(cfg, band, "PA", "dpd_im3_cancel_db", 0.0)
    if dpd_override is not None:
        dpd_db = dpd_override
    out["dpd_db"] = float(dpd_db)

    blocks = {}
    per_stage_im3 = {}
    for st in CHAIN:
        blk = P.get(cfg, band, st, "evm_block")
        o = out["stages"][st]["oip3_db"]
        if not blk or o is None:
            continue
        po = dB2W(out["stages"][st]["p_out_db"])
        o3 = dB2W(float(o))
        im3 = k * (po / o3) ** 3 * po            # 该级输出端 IM3 功率
        im3 *= dB2W(suffix[st])                # 折算到链输出
        per_stage_im3[st] = im3
        blocks[blk] = blocks.get(blk, 0.0) + im3
    out["im3_per_stage_w"] = per_stage_im3

    # 4b. 直接给定的块（DAC/LPF/IQ/LOFT/LO_IPN）
    for blk, stage in [("DAC", "DAC"), ("LPF", "LPF"), ("IQ_MM", "IQ_MM"), ("LOFT", "LOFT")]:
        v = P.get(cfg, band, stage, "evm_direct_db")
        if v is None:
            continue
        blocks[blk] = blocks.get(blk, 0.0) + dB2W(float(v)) * p_final_w

    # 4c. LO 相噪块
    l_int, evm_lpn, sigma, fs_t, _ = phase_noise(P, band)
    out["lo_lint_dbc"] = l_int
    out["lo_evm_db"] = evm_lpn
    out["lo_sigma_rad"] = sigma
    out["lo_jitter_s"] = fs_t
    blocks["LO_IPN"] = blocks.get("LO_IPN", 0.0) + dB2W(evm_lpn) * p_final_w

    # 4d. DPD 收益（仅作用于 PA 块：线性功率按 10^(-dpd/10) 缩减）
    if "PA" in blocks and out["dpd_db"] > 0:
        blocks["PA"] *= dB2W(-out["dpd_db"])
        out["dpd_applied"] = True

    evm_tbl = {}
    for blk, d in sorted(blocks.items()):
        evm_tbl[blk] = W2dB(d / p_final_w) if d > 0 else -300.0
    out["evm_blocks"] = evm_tbl

    # ---- (5) 全链 RSS ----
    tot = sum(blocks.values())
    out["evm_total_db"] = W2dB(tot / p_final_w)
    out["evm_total_margin_db"] = out["evm_total_db"] - target   # 负值=优于目标

    # ---- (6) 分配对账（每块 margin ≥ margin_db）----
    alloc_rows = []
    missing = []
    all_blocks = set(evm_tbl.keys())
    for blk in ["DAC", "LPF", "VGAMIX", "LO_IPN", "IQ_MM", "LOFT", "PA"]:
        if blk not in all_blocks:
            alloc_rows.append({"block": blk, "alloc_db": None, "design_db": None,
                               "margin_db": None, "pass": None,
                               "why": "未建模（架构未给该级线性度参数）"})
            missing.append(blk)
            continue
        alloc = P.get("spec", band, blk, "evm_alloc_db",
                      P.get("arch", band, blk, "evm_alloc_db"))
        dv = evm_tbl[blk]
        if alloc is None:
            alloc_rows.append({"block": blk, "alloc_db": None, "design_db": dv,
                               "margin_db": None, "pass": False, "why": "无分配值"})
            continue
        m = float(alloc) - dv              # 正值 = 优于分配
        alloc_rows.append({"block": blk, "alloc_db": float(alloc), "design_db": dv,
                           "margin_db": m, "pass": m >= margin_db,
                           "why": "" if m >= margin_db else "裕量不足"})
    out["evm_reconcile"] = alloc_rows
    out["evm_missing"] = missing
    out["evm_reconcile_pass"] = (not missing) and all(
        r["pass"] for r in alloc_rows if r["pass"] is not None)

    # ---- (7) 功耗 ----
    pd = {}
    for st in CHAIN + POWER_ONLY:
        v = P.get(cfg, band, st, "pdc_mw")
        if v is not None:
            pd[st] = float(v)
    out["pdc_mw"] = pd
    out["pdc_total_mw"] = sum(pd.values())
    arch_tot = 0.0
    for st in CHAIN + POWER_ONLY:
        v = P.get("arch", band, st, "pdc_mw")
        if v is not None:
            arch_tot += float(v)
    out["pdc_arch_mw"] = arch_tot
    pmax = P.get("spec", band, "SYS", "pdc_max_mw")
    out["pdc_max_mw"] = pmax
    out["pdc_pass"] = (pmax is None) or (out["pdc_total_mw"] <= float(pmax))
    pa_dc = pd.get("PA", 0.0)
    if pa_dc:
        out["pae_pct"] = 100.0 * dB2W(out["p_out_db"]) / pa_dc   # mW/mW
    else:
        out["pae_pct"] = None

    # 输出功率核对
    out["pout_pass"] = (p_out_spec is None) or \
        abs(out["p_out_db"] - float(p_out_spec)) <= 0.5
    out["overall_pass"] = bool(out["evm_reconcile_pass"] and out["pdc_pass"]
                               and out["pout_pass"])
    return out


# ---------------------------------------------------------------- PA 扫描
def pa_sweep(P, cfg, band, margin_db=2.0):
    """PA 直流 -> 全链 EVM；找满足 EVM 目标+裕量的最小 PA 直流"""
    target = float(P.get("spec", band, "SYS", "evm_target_db",
                         P.get("spec", "sys", "SYS", "evm_target_db", -41)))
    need = target - margin_db          # 各块都要优于它
    alloc_pa = P.get("arch", band, "PA", "evm_alloc_db", -46)
    rows = []
    for dc in [200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000, 1200, 1500, 2000]:
        # 以覆盖写临时参数：PA 直流 + 反推 OIP3
        pae = float(P.get("design", band, "PA", "pae_at_p1db", 0.25))
        oo = float(P.get("design", band, "PA", "oip3_over_p1db", 8.0))
        p1db = w_to_dbm((dc / 1000.0) * pae)
        oip3 = p1db + oo
        save = P.rows.get((cfg, band, "PA", "pdc_mw"))
        save_o = P.rows.get((cfg, band, "PA", "oip3_db"))
        P.rows[(cfg, band, "PA", "pdc_mw")] = float(dc)
        P.rows[(cfg, band, "PA", "oip3_db")] = oip3
        r = compute(P, cfg, band, margin_db)
        if save is not None:
            P.rows[(cfg, band, "PA", "pdc_mw")] = save
        else:
            P.rows.pop((cfg, band, "PA", "pdc_mw"), None)
        if save_o is not None:
            P.rows[(cfg, band, "PA", "oip3_db")] = save_o
        else:
            P.rows.pop((cfg, band, "PA", "oip3_db"), None)
        rows.append({"pa_dc_mw": dc, "p1db_db": p1db, "oip3_db": oip3,
                     "pa_block_db": r["evm_blocks"].get("PA"),
                     "evm_total_db": r["evm_total_db"],
                     "pdc_total_mw": r["pdc_total_mw"],
                     "pass": r["evm_total_db"] <= need and r["pdc_pass"]})
    return rows, need, float(alloc_pa)


# ---------------------------------------------------------------- 打印
def f(x, w=8, p=2):
    if x is None:
        return "-".rjust(w)
    return ("%.*f" % (p, x)).rjust(w)


def fi(x, w=6):
    if x is None:
        return "-".rjust(w)
    return ("%d" % round(x)).rjust(w)


def print_report(P, res, margin_db):
    cfg, band = res["config"], res["band"]
    print("=" * 78)
    print("config=%s  band=%s   (EVM_dB = 10log10(Perr/Psig), k_IM3=%.2f, 裕量门槛 %.1f dB)"
          % (cfg, band, res["k_im3"], margin_db))
    print("=" * 78)

    print("\n[1] 增益/电平/线性度级联")
    print("  %-5s %8s %8s %8s %9s %9s %8s" %
          ("stage", "G(dB)", "Pin", "Pout", "OIP3", "OP1dB", "Pdc(mW)"))
    for st in CHAIN:
        s = res["stages"][st]
        print("  %-5s %8.2f %8.2f %8.2f %9s %9s %8s" %
              (st, s["gain_db"], s["p_in_db"], s["p_out_db"],
               f(s["oip3_db"], 9, 1), f(s["op1db_db"], 9, 1), fi(s["pdc_mw"], 8)))
    print("  %-5s %8.2f %8.2f %8.2f %9s %9s %8s" %
          ("合计", res["gain_total_db"], res["p_in_db"], res["p_out_db"],
           f(res["oip3_cascade_db"], 9, 1), f(res["op1db_cascade_db"], 9, 1),
           fi(res["pdc_total_mw"], 8)))
    print("  规格输出功率 %.1f dBm  ->  %s   |  级联 OIP3 = %.1f dBm (IIP3 %.1f dBm)"
          % (res["p_out_spec_db"] or 0, "PASS" if res["pout_pass"] else "FAIL",
             res["oip3_cascade_db"] if res["oip3_cascade_db"] else float("nan"),
             res["iip3_cascade_db"] if res["iip3_cascade_db"] else float("nan")))
    if res["oip3_cascade_db"]:
        print("  级联 OIP3 距输出 %.1f dB（OP1dB 限制级：%s）"
              % (res["oip3_cascade_db"] - res["p_out_db"], res["op1db_limited_by"]))
    if res["dpd_db"]:
        print("  DPD IM3 对消假设：%.1f dB（仅作用于 PA 块）" % res["dpd_db"])

    print("\n[2] 各块 EVM 与分配对账")
    print("  %-8s %10s %10s %9s %7s  %s" %
          ("block", "分配(dB)", "设计(dB)", "裕量(dB)", "判定", "备注"))
    for r in res["evm_reconcile"]:
        if r["alloc_db"] is None and r["design_db"] is None:
            print("  %-8s %10s %10s %9s %7s  %s" %
                  (r["block"], "-", "-", "-", "n/a", r["why"]))
            continue
        print("  %-8s %10s %10s %9s %7s  %s" %
              (r["block"], f(r["alloc_db"], 10, 1), f(r["design_db"], 10, 1),
               f(r["margin_db"], 9, 1), "PASS" if r["pass"] else "FAIL", r["why"]))
    print("  %-8s %10s %10.2f %9.2f %7s  (目标 %.1f dB)" %
          ("全链RSS", "-", res["evm_total_db"], res["evm_total_margin_db"],
           "PASS" if res["evm_total_db"] <= res["target_db"] else "FAIL", res["target_db"]))
    if res.get("evm_missing"):
        print("  注意：%s 未建模，上行 RSS 仅含已建模块" % ",".join(res["evm_missing"]))
    print("  LO 相噪：积分 L_int=%.1f dBc  ->  EVM=%.1f dB  (sigma=%.3e rad, t_rms=%.1f fs)"
          % (res["lo_lint_dbc"], res["lo_evm_db"], res["lo_sigma_rad"],
             res["lo_jitter_s"] * 1e15))

    print("\n[3] 功耗对账")
    print("  %-8s %10s %10s" % ("stage", "本设计", "架构"))
    for st in CHAIN + POWER_ONLY:
        d = res["pdc_mw"].get(st)
        a = P.get("arch", band, st, "pdc_mw")
        if d is None and a is None:
            continue
        print("  %-8s %10s %10s" % (st, fi(d, 10), fi(a, 10)))
    print("  %-8s %10s %10s   规格上限 %s  -> %s" %
          ("合计", fi(res["pdc_total_mw"], 10), fi(res["pdc_arch_mw"], 10),
           fi(res["pdc_max_mw"], 8), "PASS" if res["pdc_pass"] else "FAIL"))
    if res["pae_pct"]:
        print("  PA 效率 @工作点：%.1f%%  (Pout=%.1f dBm / Pdc=%.0f mW)"
              % (res["pae_pct"], res["p_out_db"], res["pdc_mw"].get("PA", 0)))
    if res.get("evm_missing"):
        verdict = "部分建模：仅已建模块参与判定"
    else:
        verdict = "PASS" if res["overall_pass"] else "FAIL（详见上表 FAIL 行）"
    print("\n  总判定：%s" % verdict)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="WiFi7-TX 电路预算复算")
    ap.add_argument("--csv", default=DEFAULT_CSV)
    ap.add_argument("--config", default="design", choices=["design", "arch"])
    ap.add_argument("--band", default=None, choices=["g56", "g24"])
    ap.add_argument("--margin", type=float, default=None, help="EVM 裕量门槛 dB")
    ap.add_argument("--dpd", type=float, default=None, help="覆盖 DPD IM3 对消 dB")
    ap.add_argument("--pa-sweep", action="store_true")
    ap.add_argument("--ref-compare", action="store_true", help="比较不同参考振荡器")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    if not os.path.exists(a.csv):
        sys.exit("找不到参数表：%s" % a.csv)
    P = Params(a.csv)
    margin_db = a.margin if a.margin is not None else \
        float(P.get("spec", "sys", "SYS", "evm_margin_min_db", 2))
    bands = [(a.band, dict(BANDS)[a.band])] if a.band else BANDS

    results = []
    for band, label in bands:
        if a.pa_sweep:
            rows, need, alloc = pa_sweep(P, a.config, band, margin_db)
            print("=" * 78)
            print("PA 直流扫描  band=%s  (需全链 EVM <= %.1f dB, PA 分配 %.1f dB)"
                  % (band, need, alloc))
            print("=" * 78)
            print("  %8s %9s %9s %12s %12s %10s %7s" %
                  ("PA_dc", "P1dB", "OIP3", "PA块EVM", "全链EVM", "总功耗", "判定"))
            for r in rows:
                print("  %8d %9.1f %9.1f %12.1f %12.1f %10d %7s" %
                      (r["pa_dc_mw"], r["p1db_db"], r["oip3_db"],
                       r["pa_block_db"], r["evm_total_db"], r["pdc_total_mw"],
                       "PASS" if r["pass"] else "-"))
            ok = [r for r in rows if r["pass"]]
            if ok:
                print("\n  -> 满足条件的最小 PA 直流：%.0f mW（全链 %.0f mW）"
                      % (ok[0]["pa_dc_mw"], ok[0]["pdc_total_mw"]))
            else:
                print("\n  -> 当前参数下无解（扫描至 2000 mW）")
            continue

        if a.ref_compare:
            print("=" * 78)
            print("参考振荡器对 LO IPN 的影响  band=%s" % band)
            print("=" * 78)
            print("  %-34s %10s %10s %10s" % ("参考", "L_int(dBc)", "EVM(dB)", "t_rms(fs)"))
            for key in ["alt_ref_1", "alt_ref_2", "alt_ref_3"]:
                spec = P.raw("ref", "sys", "LO_IPN", key)
                if not spec:
                    continue
                fref, lref = [float(x) for x in str(spec).split("|")[:2]]
                li, ev, sg, ts, _ = phase_noise(
                    P, band, {"f_ref_hz": fref, "ref_l_100k_dbchz": lref})
                print("  %-34s %10.1f %10.1f %10.1f" %
                      ("%.0f Hz @ %.0f dBc/Hz@100k" % (fref, lref), li, ev, ts * 1e15))
            print()

        r = compute(P, a.config, band, margin_db, dpd_override=a.dpd)
        r["band_label"] = label
        print_report(P, r, margin_db)
        print()
        results.append(r)

    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=1)
        print("JSON 已写出：%s" % a.json)
    return 0 if all(r.get("overall_pass", False) for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
