#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""delivery_gate.py — ★★交接文档交付件归属实测律 的机器闸（裁定六十八立）

用途：扫交接文档（summary.md 或任意 md）的「我方交付件」表，逐行实测
      ①文件是否存在（MISSING 一律 FAIL）②sha 现算是否与表内记载一致 ③bytes 是否一致。
      并核「组员产出」段列的件**不得同时出现在我方交付件表**（归属混淆＝真串面）。

立律缘由（活标本，裁定六十八 §五）：上口 summary「我方交付件（本口新增/修改）」表
  7 件中 **4 件在我方盘 MISSING**，全是组员信里自述的**他们自己的**产出
  （fde9: ledger_lineage_chain_64.md §八 / lineage_scope_patch_66.py / ref_sha_audit.py；
   b7e7: state/件身份索引_F16.md），上口以第一人称「我方」记入 ⇒ 串面家族第五例。
  根因：组员信里的 sha/bytes/工具名与我方产出**形态完全相同**，
        按「本口处理过的事」回忆 ⇒ 凡读过并复述过的都被记成本口产出的。

★本器自身也受「工具首版必自审假阳性律」约束：
  - 首版正则过严（12 行只匹配 2 行、其余静默「解析跳过」）⇒ **全绿也可能是失效**。
    已修：宽松解析 + **表行数与判定行数必须相等**（解析跳过 > 0 即 FAIL，不许静默降覆盖）。
  - v2（2026-10-23 维护轮，b7a0——首版对当前维护轮 summary 假阳性实录修正）：
    「零表行」判据区分「声明空」与「沉默空表」——维护轮段内**显式声明**
    「无新产件/零交付件」等＝显式信号 → 放行（记 none_declared）；
    **有表头无数据行**、或段内散文连声明都没有 → 仍 FAIL。
    家族律依据：「报 0 须区分『结构上不可能』与『量过了没有』」（裁定六十九入律）——
    声明空＝明确报了 0（量过了）；沉默空表＝什么都没说（没量）。
  - v2 新增 --selftest：夹具自身有效性断言（裁定六十八第五封我方承诺项）——
    不只验负例「会红」，还验「红在预定机制上」（MISSING／不符／归属混淆／零表行 逐夹具点名），
    防夹具因依赖文件消失/改名而静默变哑（红错地方也算哑）。
  - v3（2026-10-24 维护轮，b7a0——内部待办㉛ P0-A，裁定一百）：
    **闸门自身在早退路径上崩成 traceback**（v2「文档不存在」早退只返回两键 dict ⇒ render() KeyError
    ⇒ 无结论行 ⇒ 最该响的场景没响）。v3 修：①所有早退路径统一走 `_blank_result()` 全键骨架
    ＋显式 reasons；②render() 全程 .get 兜底（残缺 dict 不得崩）；③**报告恒有结论行**
    「结论行: 总项数 N ／ FAIL n」（★★验证器报告完整性律）；④退出码收敛 {0,1}
    （原「未给文档」路径 rc=2 越界）；⑤run()/CLI 双层 try/except ⇒ 异常也有结论行；
    ⑥selftest 增两例（无「我方交付件」段／文档不存在早退）并**逐例断言结论行存在**。
    ★正常路径**既有行逐字节不变**，只在末尾追加一行结论行。

用法：
  python3 delivery_gate.py <md 路径> [--root /data/workspace] [--json out.json]
  python3 delivery_gate.py --selftest [--root /data/workspace]
技能入口：run(md=..., root=..., json_out=..., selftest=False)
"""
import hashlib
import json
import os
import re
import sys

# 「我方交付件」段与「组员产出」段的标题识别（宽松：含关键词即可）
MINE_KEYS = ("我方交付件", "本口新增", "交付件（本口")
FOREIGN_KEYS = ("组员产出", "不入我方交付件表")

# 「零产件显式声明」识别（v2）：段内出现任一短语＝维护轮明确报了 0（量过了）→ 放行。
# 只认「明确说没有」的措辞，不认泛泛的「无」/「零」单字（避免误放行沉默空段）。
NONE_DECL_RE = re.compile(
    r"无新产件|零新产件|零交付件|无交付件|零新增|本口无|无（维护|无新交付|本口零|零产件"
)


def _sha_bytes(fp):
    b = open(fp, "rb").read()
    return hashlib.sha256(b).hexdigest(), len(b)


def _find_section(lines, keys, stop_prefix="## "):
    """返回 (start_idx, end_idx) 半开区间；找不到返回 (None, None)。"""
    start = None
    for i, l in enumerate(lines):
        if l.startswith(stop_prefix) and any(k in l for k in keys):
            start = i
            break
    if start is None:
        return None, None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith(stop_prefix):
            end = j
            break
    return start, end


def _has_table_header(seg_lines):
    """段内是否出现 markdown 表头（含 sha 列的 |…| 行）。用于区分「有表头无数据」vs「无表」。"""
    for l in seg_lines:
        if not l.startswith("|"):
            continue
        if l.startswith("|---") or set(l.replace("|", "").strip()) <= set("-: "):
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cells) >= 2 and ("sha" in cells[0].lower() or "sha" in cells[1].lower()):
            return True
    return False


def _table_rows(seg_lines):
    """抽 markdown 表体行（跳过表头与分隔行）。返回 rows。"""
    rows = []
    for l in seg_lines:
        if not l.startswith("|"):
            continue
        if l.startswith("|---") or set(l.replace("|", "").strip()) <= set("-: "):
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        # 表头行识别：首列含「件」/「path」/「文件」且第二列含 sha
        if ("sha" in cells[1].lower() or "sha" in cells[0].lower()) and not re.search(r"[0-9a-f]{8}", " ".join(cells)):
            continue
        rows.append(cells)
    return rows


def _blank_result(md_path, root):
    """完整键集的结果骨架（v3 · 裁定一百 · 内部待办㉛ P0-A）。

    为什么要有骨架：v2 在「文档不存在」路径上早退时只返回 {"verdict","reason"} 两个键，
    下游 render() 读 res['doc'] ⇒ KeyError ⇒ **闸门自身崩成 traceback（无结论行）**
    ⇒ 最该响的场景没响（本人方自审 F7 所出）。v3：任何早退路径都返回全键 dict
    ＋ 显式 reasons ＋ 可渲染的结论行。
    """
    return {"doc": md_path, "root": root, "mine": [], "foreign": [],
            "n_rows_seen": 0, "n_rows_judged": 0, "n_items": 0, "n_fail": 1,
            "missing": [], "mismatch": [], "foreign_has_local": [],
            "none_declared": False, "verdict": "FAIL",
            "reasons": [], "reason": None}


def gate(md_path, root="/data/workspace"):
    """主闸。返回 dict（verdict + 明细）。"""
    if not os.path.isfile(md_path):
        res = _blank_result(md_path, root)
        res["reason"] = f"文档不存在: {md_path}"
        res["reasons"] = [res["reason"]]
        return res
    text = open(md_path, encoding="utf-8", errors="replace").read()
    lines = text.split("\n")

    out = {"doc": md_path, "root": root, "mine": [], "foreign": [],
           "n_rows_seen": 0, "n_rows_judged": 0, "missing": [], "mismatch": [],
           "foreign_has_local": [], "none_declared": False, "verdict": "PASS"}

    # ── 一、我方交付件表：逐行实测 ──
    s, e = _find_section(lines, MINE_KEYS)
    if s is None:
        out["verdict"] = "FAIL"
        out["reason"] = "未找到「我方交付件」段（标题须含: %s）" % "/".join(MINE_KEYS)
        out["reasons"] = [out["reason"]]
        out["n_items"] = 0
        out["n_fail"] = 1
        return out
    seg = lines[s:e]
    rows = _table_rows(seg)
    out["n_rows_seen"] = len(rows)
    for cells in rows:
        path = cells[0].strip("`").strip()
        # 首列可能带说明文字，取第一个像路径的 token
        if not re.match(r"^[\w./\u4e00-\u9fff-]+$", path):
            m = re.search(r"`([^`]+)`", cells[0])
            path = m.group(1) if m else path
        sha_cell = cells[1] if len(cells) > 1 else ""
        b_cell = cells[2] if len(cells) > 2 else ""
        m = re.search(r"([0-9a-f]{8,64})", sha_cell)
        claim_sha = m.group(1) if m else None
        mb = re.search(r"(\d+)", b_cell)
        claim_b = int(mb.group(1)) if mb else None
        fp = os.path.join(root, path) if not path.startswith("/") else path
        rec = {"path": path, "claim_sha": claim_sha, "claim_bytes": claim_b}
        if not os.path.isfile(fp):
            rec["status"] = "MISSING"
            out["missing"].append(rec)
        else:
            s256, nb = _sha_bytes(fp)
            rec["actual_sha"] = s256[:16]
            rec["actual_bytes"] = nb
            sha_ok = (claim_sha is None) or s256.startswith(claim_sha[:8])
            b_ok = (claim_b is None) or (claim_b == nb)
            rec["status"] = "OK" if (sha_ok and b_ok) else "MISMATCH"
            if rec["status"] == "MISMATCH":
                out["mismatch"].append(rec)
        out["mine"].append(rec)
        out["n_rows_judged"] += 1

    # ── 一·补（v2）：零表行时区分「声明空」vs「沉默空表」 ──
    #   声明空＝段内显式写了「无新产件/零交付件」等＝明确报了 0（量过了）→ 放行；
    #   沉默空表＝有表头没数据、或连声明都没有＝没量 → FAIL。
    if out["n_rows_seen"] == 0:
        out["none_declared"] = bool(NONE_DECL_RE.search("\n".join(seg)))

    # ── 二、组员产出段：★真判据＝「不得同时出现在我方交付件表」（归属混淆）──
    #   为什么不用「我方盘无实体」当 FAIL 判据（首版假阳性，裁定六十八当场撞到）：
    #   组员**投到我方发布面**的件（如 b7e7 投 8510 `design/sow6/preflight_b7e7.py`）
    #   我方盘**当然有实体**（`outbox_files/design/sow6/` 就是 8510 的根），
    #   但它**不是我方产出** ⇒ 「有实体」不等于「归属标错」。
    #   ⇒ 「我方盘有无实体」降为 INFO；FAIL 判据＝**同名件同时出现在两张表**（那才是真串面）。
    mine_basenames = {os.path.basename(x["path"]) for x in out["mine"]}
    fs, fe = _find_section(lines, FOREIGN_KEYS)
    if fs is not None:
        names = set()
        for l in lines[fs:fe]:
            for m in re.finditer(r"`([^`]+\.(?:md|py|json|gds|cdl|sp|lib|txt))`", l):
                names.add(os.path.basename(m.group(1)))
        for n in sorted(names):
            hits = []
            for r2, dirs, files in os.walk(root):
                dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "node_modules")]
                if n in files:
                    hits.append(os.path.join(r2, n).replace(root + os.sep, ""))
            in_mine = n in mine_basenames
            rec = {"name": n, "local_hits": hits, "in_mine_table": in_mine,
                   "status": "★DUP-IN-MINE" if in_mine else ("INFO-HAS-LOCAL" if hits else "OK-NO-LOCAL")}
            out["foreign"].append(rec)
            if in_mine:
                out["foreign_has_local"].append(rec)

    # ── 三、判定（含「不许静默降覆盖」+ v2 声明空/沉默空表分界）──
    reasons = []
    n_fail = 0
    if out["missing"]:
        reasons.append(f"MISSING {len(out['missing'])} 件（不得入表）: "
                       + ", ".join(x["path"].split("/")[-1] for x in out["missing"]))
        n_fail += len(out["missing"])
    if out["mismatch"]:
        reasons.append(f"sha/bytes 不符 {len(out['mismatch'])} 件: "
                       + ", ".join(x["path"].split("/")[-1] for x in out["mismatch"]))
        n_fail += len(out["mismatch"])
    if out["foreign_has_local"]:
        reasons.append(f"★归属混淆 {len(out['foreign_has_local'])} 件（同时出现在两张表）: "
                       + ", ".join(x["name"] for x in out["foreign_has_local"]))
        n_fail += len(out["foreign_has_local"])
    if out["n_rows_judged"] != out["n_rows_seen"]:
        reasons.append(f"★覆盖降级：表行 {out['n_rows_seen']} 但判定 {out['n_rows_judged']}"
                       "（解析跳过 > 0，不许静默）")
        n_fail += 1
    if out["n_rows_seen"] == 0 and not out["none_declared"]:
        if _has_table_header(seg):
            reasons.append("「我方交付件」段有表头但零数据行（空表＝没信号，同「全绿≠全跑」）")
        else:
            reasons.append("「我方交付件」段既无表行也无零产件声明（沉默＝没信号，须显式声明或列表）")
        n_fail += 1
    out["verdict"] = "FAIL" if reasons else "PASS"
    out["reasons"] = reasons
    # v3：结论行所需的两个数（★总项数＝被判定项数；★FAIL 数＝失败项数，结构性问题各记 1）
    out["n_items"] = out["n_rows_judged"]
    out["n_fail"] = n_fail
    return out


def render(res):
    """渲染报告。v3：全程 .get 兜底（残缺 dict 不得崩）＋ 末尾恒有结论行。"""
    L = []
    L.append(f"=== delivery_gate: {res.get('doc', '?')} ===")
    L.append(f"判定: {res.get('verdict', 'FAIL')}")
    rs = list(res.get("reasons") or [])
    if not rs and res.get("reason"):
        rs = [res["reason"]]
    for r in rs:
        L.append(f"  ★ {r}")
    if res.get("none_declared") and res.get("n_rows_seen", 0) == 0:
        L.append("  ✓ 零产件显式声明（维护轮明确报了 0，量过了）→ 放行")
    if res.get("mine"):
        L.append(f"-- 我方交付件（表行 {res['n_rows_seen']} / 判定 {res['n_rows_judged']}）--")
        for x in res["mine"]:
            if x["status"] == "MISSING":
                L.append(f"  ★MISSING  {x['path']}")
            elif x["status"] == "MISMATCH":
                L.append(f"  ★不符  实测 {x.get('actual_sha')} {x.get('actual_bytes')}B "
                         f"vs 表内 {x['claim_sha']} {x['claim_bytes']}  {x['path']}")
            else:
                L.append(f"  ✓ {x['actual_sha']} {x['actual_bytes']:>7}B  {x['path'].split('/')[-1][:56]}")
    if res.get("foreign"):
        L.append("-- 组员产出（★判据＝不得同时出现在我方交付件表；「我方盘有无实体」仅 INFO）--")
        for x in res["foreign"]:
            tag = {"OK-NO-LOCAL": "✓", "INFO-HAS-LOCAL": "i", "★DUP-IN-MINE": "★"}[x["status"]]
            detail = {"OK-NO-LOCAL": "我方盘无实体",
                      "INFO-HAS-LOCAL": f"我方盘有实体（＝组员投我方发布面/我方留档副本，非我方产出）{len(x['local_hits'])} 份",
                      "★DUP-IN-MINE": "★同时出现在我方交付件表＝归属混淆"}[x["status"]]
            L.append(f"  {tag} {x['name']}: {detail}")
    # ── 结论行（★★验证器报告完整性律 · 裁定一百）：**任何路径都必须有**，下游按此正则读 ──
    n_items = res.get("n_items", res.get("n_rows_judged", 0))
    n_fail = res.get("n_fail", 0)
    suffix = "（显式声明零产件）" if res.get("none_declared") and n_items == 0 else ""
    L.append(f"结论行: 总项数 {n_items} ／ FAIL {n_fail}{suffix}")
    return "\n".join(L)


# ── selftest（v2）：夹具自身有效性断言 ──
# 每个负例夹具不仅须「会红」（verdict=FAIL），还须「红在预定机制上」——
# 逐夹具点名它应触发的那一条 reason 关键词。若夹具因依赖文件消失/改名而
# 红错地方（或变 PASS），selftest 即 FAIL（夹具变哑被当场抓住）。
# 正例夹具须 PASS（真件、真 sha/bytes、归属清晰）。
SELFTEST_CASES = [
    # (夹具名, 期望 verdict, 必须出现的 reason 关键词列表（全部命中才算「红在预定机制」）)
    ("neg_missing.md", "FAIL", ["MISSING"]),
    ("neg_mismatch.md", "FAIL", ["不符"]),
    ("neg_dup.md", "FAIL", ["归属混淆"]),
    ("neg_empty.md", "FAIL", ["零数据行"]),
    # v3 新增两例（裁定一百 · 内部待办㉛ P0-A）：
    ("neg_nosection.md", "FAIL", ["未找到"]),          # 有文档但无「我方交付件」段 → 须有原因行
    ("ABS:/tmp/xuseek_no_such_delivery_gate_doc.md", "FAIL", ["文档不存在"]),  # 早退路径不得崩
    ("pos_ok.md", "PASS", []),
]


def selftest(root="/data/workspace"):
    """跑全部夹具，逐条断言 verdict + 预定机制 + 结论行存在。返回 dict。"""
    fx_dir = os.path.join(root, "verify", "delivery_gate_selftest_68")
    lines = []
    all_ok = True
    n_cases = 0
    n_fail = 0
    for name, want_verdict, want_reasons in SELFTEST_CASES:
        # "ABS:" 前缀＝绝对路径（用于「文档不存在」早退路径，v3 新增）
        fp = name[4:] if name.startswith("ABS:") else os.path.join(fx_dir, name)
        if not os.path.isfile(fp) and not name.startswith("ABS:"):
            all_ok = False
            lines.append(f"  ★夹具缺失  {name}（{fp} 不存在——夹具自身失效）")
            continue
        res = gate(fp, root)
        got_verdict = res.get("verdict")
        got_reasons = res.get("reasons", [])
        # 0) 闸门自身不得崩：render() 必须能出报告（v2 在此崩成 KeyError ⇒ P0）
        try:
            rendered = render(res)
            render_ok = True
        except Exception as e:
            rendered = ""
            render_ok = False
            all_ok = False
            lines.append(f"  ★{name}: render() 崩了 {type(e).__name__}: {e}（闸门自身不得崩）")
        # 1) verdict 对
        v_ok = (got_verdict == want_verdict)
        # 2) 预定机制全命中（reason 文本里须出现每个关键词）
        r_ok = all(any(k in r for r in got_reasons) for k in want_reasons) if want_reasons else True
        # 3) 结论行必须存在（★★验证器报告完整性律）
        c_ok = ("结论行: 总项数" in rendered)
        if not c_ok:
            all_ok = False
            lines.append(f"  ★{name}: 报告里没有结论行（下游读不到 ⇒ 判 FAIL）")
        case_ok = v_ok and r_ok and render_ok and c_ok
        all_ok = all_ok and case_ok
        n_cases += 1
        if not case_ok:
            n_fail += 1
        tag = "✓" if case_ok else "★"
        mech = "、".join(want_reasons) if want_reasons else "（正例，无预定负机制）"
        lines.append(f"  {tag} {name}: 期望 {want_verdict} / 机制[{mech}] → 实得 {got_verdict}"
                     f"（结论行 {'有' if c_ok else '★无'}）")
        if not v_ok:
            lines.append(f"      ★verdict 不符：期望 {want_verdict} 实得 {got_verdict}（夹具变哑/红错地方）")
        if not r_ok:
            miss = [k for k in want_reasons if not any(k in r for r in got_reasons)]
            lines.append(f"      ★机制未命中：{miss}（实得 reasons={got_reasons}）")
    return {"ok": all_ok, "lines": lines, "n_cases": n_cases, "n_fail": n_fail}


def _fail_report(md, root, msg, json_out=None):
    """统一失败出口：任何异常/早退都落「结论行 + FAIL≥1 + rc=1」（★★验证器报告完整性律）。"""
    res = _blank_result(md, root)
    res["reason"] = msg
    res["reasons"] = [msg]
    res["n_items"] = 0
    res["n_fail"] = 1
    txt = render(res)
    if json_out:
        try:
            with open(json_out, "w", encoding="utf-8") as f:
                json.dump(res, f, ensure_ascii=False, indent=1)
            txt += f"\n[json] {json_out}"
        except Exception:
            pass
    print(txt)
    return {"verdict": "FAIL", "reasons": [msg], "n_items": 0, "n_fail": 1,
            "n_rows_seen": 0, "n_rows_judged": 0, "none_declared": False,
            "missing": [], "mismatch": [], "text": txt}


def run(md="/data/workspace/summary.md", root="/data/workspace", json_out=None, selftest=False, **kw):
    """技能入口。selftest=True 跑夹具有效性断言（不读 md）。

    v3（裁定一百 · 内部待办㉛）：**闸内任何异常都被兜住** ⇒ 报告（stdout）恒有结论行，
    返回值恒含 verdict/n_items/n_fail；绝不把 traceback 当报告。
    """
    try:
        if selftest:
            st = selftest(root)
            txt = "=== delivery_gate --selftest（夹具自身有效性断言）===\n" + "\n".join(st["lines"])
            txt += f"\n判定: {'PASS' if st['ok'] else 'FAIL'}"
            txt += f"\n结论行: 总项数 {st['n_cases']} ／ FAIL {st['n_fail']}"
            print(txt)
            return {"verdict": "PASS" if st["ok"] else "FAIL", "selftest": True,
                    "n_items": st["n_cases"], "n_fail": st["n_fail"], "text": txt}
        res = gate(md, root)
        txt = render(res)
        if json_out:
            with open(json_out, "w", encoding="utf-8") as f:
                json.dump(res, f, ensure_ascii=False, indent=1)
            txt += f"\n[json] {json_out}"
        print(txt)
        return {"verdict": res.get("verdict", "FAIL"), "reasons": res.get("reasons", []),
                "n_rows_seen": res.get("n_rows_seen"), "n_rows_judged": res.get("n_rows_judged"),
                "n_items": res.get("n_items", res.get("n_rows_judged", 0)),
                "n_fail": res.get("n_fail", 0),
                "none_declared": res.get("none_declared", False),
                "missing": [x["path"] for x in res.get("missing", [])],
                "mismatch": [x["path"] for x in res.get("mismatch", [])],
                "text": txt}
    except Exception as e:
        import traceback
        traceback.print_exc()   # 细节走 stderr；报告本体（stdout）仍须有结论行
        return _fail_report(md, root, f"★闸内异常: {type(e).__name__}: {e}", json_out)


if __name__ == "__main__":
    a = sys.argv[1:]
    root = "/data/workspace"
    jo = None
    if not a:
        print(__doc__)
        print("结论行: 总项数 0 ／ FAIL 1（未给待闸文档路径＝没跑＝不得读成 PASS）")
        sys.exit(1)
    if "--root" in a:
        root = a[a.index("--root") + 1]
    if "--json" in a:
        jo = a[a.index("--json") + 1]
    try:
        if a[0] == "--selftest":
            st = selftest(root)
            print("=== delivery_gate --selftest（夹具自身有效性断言）===")
            print("\n".join(st["lines"]))
            print(f"判定: {'PASS' if st['ok'] else 'FAIL'}")
            print(f"结论行: 总项数 {st['n_cases']} ／ FAIL {st['n_fail']}")
            sys.exit(0 if st["ok"] else 1)
        md = a[0]
        r = gate(md, root)
        print(render(r))
        if jo:
            json.dump(r, open(jo, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print(f"[json] {jo}")
        sys.exit(0 if r.get("verdict") == "PASS" else 1)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"结论行: 总项数 0 ／ FAIL 1（★闸内异常 {type(e).__name__}: {e}）")
        sys.exit(1)
