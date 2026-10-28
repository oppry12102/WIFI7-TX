#!/usr/bin/env python3
"""AST 逻辑指纹比对器 —— 判「两个 .py 件逻辑是否等价」，不靠 diff 行数/字节数。

由来（裁定六十六 ★AST 逻辑指纹判等价律）：
  8510 现役 `actgeom.py` `bd0e5e25`(5426B) vs 我方代跑部署 `7a42cc23`(4683B)
  字节差 743B / diff 20 行，但**逻辑指纹完全相同**——差异全在注释（组员把我方量纲更正固化进件）。
  ⇒ 若只看字节差就会误判「要重跑整条 v35 链」。

判法（三层，逐层收紧）：
  L1 raw      = 文件字节 sha256（最严；任何空白/注释差都不同）
  L2 ast      = ast.dump(parse(src)) 的 sha256（剥掉全部注释与格式；**保留 docstring 与字符串常量**）
  L3 ast_nodoc= 在 L2 基础上再把所有 docstring 与字符串常量归一为 ''（只留控制流/名字/数值/结构）
                 ⇒ 用于「差异只在文档措辞」的判定

★★L3 的硬边界（裁定六十七立，本工具首版撞出来的假阴性）：
  **字符串常量可能是「判据的输入数据」，不是「文档措辞」。**
  归一字符串会把这类语义变化**掩盖成 IDENTICAL**（＝假阴性，比假阳性更危险）。
  实证（2026-10-19 23:0xZ）：`drcgeom_b7e7.py` 我方部署副本 `10e05734`(42475B) vs 8510 现役 `400f9117`(46618B)
    L3 ast_nodoc = **IDENTICAL `3eb60e18ba9f`**，但 `RULES["M3"]["src"]`/`RULES["M5"]["src"]`
    由 `"assumed"` 改为 `"官方 main_rules.md L66/L82"` —— 而 `src` 正是 hard/soft **分流判据的输入**
    （`pad_spacing_violations()` 末行 `hard if RULES[lname]["src"] == "纪要" else soft`；
      preflight ⑳ `_hard20 = [x for x in _n20 if x[4] == "纪要"]`）
    ⇒ L3 说「逻辑等价」，**判据语义其实变了**（虽然本例分流结果不变，因两者都 ≠"纪要"）。
  ⇒ **用本工具判等价，必须同时跑 `--rules`（值级对比）**；本工具已把 `--rules` 设为**默认开启**，
     并在 L3 判 IDENTICAL 而值级有 DIFF 时**显式打 ★SEMANTIC-DATA-CHANGED 警告**。
  ⇒ 律：**判据输入数据（RULES/门限/映射表/白名单）不得被字符串归一掩盖，必须值级对比。**

用法：
  python3 phys/top/ast_fingerprint.py A.py B.py [C.py ...]          # 默认含值级对比
  python3 phys/top/ast_fingerprint.py --no-rules A.py B.py          # 只看三层指纹
  python3 phys/top/ast_fingerprint.py --rules-names RULES,FOO A.py B.py   # 指定要值级对比的顶层字典名
退出码：0=全部 L3 等价且值级无 DIFF；1=存在逻辑差异或值级 DIFF；2=用法/解析错
"""
import ast
import hashlib
import json
import os
import sys


def _sha(b):
    if isinstance(b, str):
        b = b.encode("utf-8")
    return hashlib.sha256(b).hexdigest()


class _StrNorm(ast.NodeTransformer):
    """把字符串常量（含 docstring）归一为 ''；数值/名字/结构全保留。"""

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return ast.copy_location(ast.Constant(value=""), node)
        return node


def fingerprint(path):
    src = open(path, encoding="utf-8").read()
    raw = _sha(open(path, "rb").read())
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return {"path": path, "error": "SyntaxError: %s" % e, "raw": raw}
    l2 = _sha(ast.dump(tree))
    tree3 = _StrNorm().visit(ast.parse(src))
    l3 = _sha(ast.dump(tree3))
    # 结构统计（便于人读差异在哪）
    kinds = {}
    for n in ast.walk(tree):
        k = type(n).__name__
        kinds[k] = kinds.get(k, 0) + 1
    return {
        "path": path,
        "bytes": os.path.getsize(path),
        "raw": raw,
        "ast": l2,
        "ast_nodoc": l3,
        "n_nodes": sum(kinds.values()),
        "n_func": kinds.get("FunctionDef", 0),
        "n_call": kinds.get("Call", 0),
        "n_num": kinds.get("Constant", 0),
        "top_funcs": sorted(
            n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ),
        "top_assigns": sorted(
            t.id
            for n in tree.body
            if isinstance(n, ast.Assign)
            for t in n.targets
            if isinstance(t, ast.Name)
        ),
    }


def _lit(node):
    """尽力把 AST 节点还原成可 JSON 化的字面值（用于 RULES 值级对比）。"""
    try:
        return ast.literal_eval(node)
    except Exception:
        return "<non-literal:%s>" % type(node).__name__


def rules_dump(path, names=("RULES", "LNUM", "V1STACK_TRUTH", "SLIT_MAXW")):
    """抽顶层字典常量的**值级**快照（判「门限值有没有真变」）。"""
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    out = {}
    for n in tree.body:
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id in names:
                    out[t.id] = _lit(n.value)
    return out


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    if len(args) < 2:
        print(__doc__)
        return 2
    want_rules = "--no-rules" not in flags          # ★默认开启（裁定六十七）
    names = ("RULES", "LNUM", "V1STACK_TRUTH", "SLIT_MAXW")
    for f in flags:
        if f.startswith("--rules-names"):
            if "=" in f:
                names = tuple(x for x in f.split("=", 1)[1].split(",") if x)
    fps = [fingerprint(p) for p in args]
    for f in fps:
        if "error" in f:
            print("PARSE-ERROR", f["path"], f["error"])
            return 2
    print("=" * 78)
    print("AST 逻辑指纹比对（L1 raw / L2 ast / L3 ast_nodoc）＋值级对比（默认开）")
    print("=" * 78)
    for f in fps:
        print(
            "%-58s %7d B  raw=%s  ast=%s  nodoc=%s"
            % (os.path.relpath(f["path"]), f["bytes"], f["raw"][:8], f["ast"][:8], f["ast_nodoc"][:12])
        )
    print("-" * 78)
    base = fps[0]
    rc = 0
    l3_same_all = True
    for f in fps[1:]:
        for lvl, key in (("L1 raw", "raw"), ("L2 ast", "ast"), ("L3 ast_nodoc", "ast_nodoc")):
            same = base[key] == f[key]
            print("  %-11s %s  %s" % (lvl, "IDENTICAL" if same else "DIFFERENT",
                                      "" if same else "(%s vs %s)" % (base[key][:8], f[key][:8])))
        if base["ast_nodoc"] != f["ast_nodoc"]:
            rc = 1
            l3_same_all = False
            print("  ⇒ ★逻辑不同（控制流/名字/数值有差异）")
            # 定位差异
            for k in ("n_nodes", "n_func", "n_call", "n_num"):
                if base[k] != f[k]:
                    print("     %s: %s vs %s" % (k, base[k], f[k]))
            fa, fb = set(base["top_funcs"]), set(f["top_funcs"])
            if fa != fb:
                print("     仅A有的函数:", sorted(fa - fb))
                print("     仅B有的函数:", sorted(fb - fa))
            aa, ab = set(base["top_assigns"]), set(f["top_assigns"])
            if aa != ab:
                print("     仅A有的顶层赋值:", sorted(aa - ab))
                print("     仅B有的顶层赋值:", sorted(ab - aa))
        elif base["ast"] != f["ast"]:
            print("  ⇒ 逻辑等价（差异仅在 docstring/字符串常量）")
        elif base["raw"] != f["raw"]:
            print("  ⇒ 逻辑等价（差异仅在注释/空白/格式）")
        else:
            print("  ⇒ 逐字节相同")
        print("-" * 78)
    if want_rules:
        print("值级快照对比（%s）" % "/".join(names))
        dumps = [rules_dump(f["path"], names) for f in fps]
        keys = sorted({k for d in dumps for k in d})
        val_diff = False
        for k in keys:
            vals = [json.dumps(d.get(k), sort_keys=True, ensure_ascii=False, default=str) for d in dumps]
            tag = "SAME" if len(set(vals)) == 1 else "★DIFF"
            if tag != "SAME":
                val_diff = True
            print("  %-16s %s" % (k, tag))
            if tag == "★DIFF":
                for f, v in zip(fps, vals):
                    print("      %s: %s" % (os.path.relpath(f["path"]), v[:400]))
        # 逐层逐键值对比（定位到「哪个字典的哪个键的哪个字段」变了）
        for k in keys:
            if all(isinstance(d.get(k), dict) for d in dumps):
                sub = sorted({sk for d in dumps for sk in d[k]})
                for sk in sub:
                    rows = [d[k].get(sk, {}) for d in dumps]
                    fields = sorted({fk for r in rows if isinstance(r, dict) for fk in r})
                    for fld in fields:
                        vs = [r.get(fld) if isinstance(r, dict) else None for r in rows]
                        if len({json.dumps(v, ensure_ascii=False, default=str) for v in vs}) > 1:
                            val_diff = True
                            print("    ★ %s[%r].%s:" % (k, sk, fld))
                            for f, v in zip(fps, vs):
                                print("        %s = %r" % (os.path.relpath(f["path"]), v)[:200])
        # ★★裁定六十七：L3 说等价但值级有 DIFF ⇒ 假阴性警告
        if l3_same_all and val_diff:
            rc = 1
            print("=" * 78)
            print("★★SEMANTIC-DATA-CHANGED（假阴性警告）")
            print("  L3 ast_nodoc 判 IDENTICAL，但**判据输入数据（字典值）有差异**。")
            print("  ⇒ 字符串常量归一**掩盖了语义变化**：这些字符串可能是判据的输入数据，不是文档措辞。")
            print("  ⇒ 不得据 L3 IDENTICAL 判「无需重跑/无影响」；必须逐键核该数据是否参与判据分流。")
            print("  实证首例：drcgeom RULES[*]['src'] 参与 hard/soft 分流（裁定六十七）。")
            print("=" * 78)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
