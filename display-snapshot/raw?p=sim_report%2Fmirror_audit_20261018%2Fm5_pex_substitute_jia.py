#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m5_pex_substitute_jia.py — 口径甲代入器（b7a0 2026-10-18 02:2xZ《M5 PEX 口径裁定（组长四裁）》裁定一/二）

裁定一（阻塞 A）→ 口径甲：**cdl 只替换 L0 实物器件行，deck 理想件逐字保留。**
  实现（= b7a0「实现按 fde9 案：器件名白名单逐条替换 L0 实物件，deck 偏置源/B 源/tank/PAD 耦合逐字保留；
  白名单清单入代入器运行日志备审计」）：
    · deck 侧：白名单内的行逐字保留（理想件/偏置源/耦合件/参数）；白名单外的器件行一律剔除
      （它们是 L0 实物件，由 cdl 接管）。
    · cdl 侧：全部 L0 实物器件行（Q/R/C）改写为 X 行后进入网表；
      但凡某 cdl 件是「deck 保留件」的实物孪生（同位置同标称值），则剔除该 cdl 件，
      避免与 deck 保留件重复计入（重复计入=把 45Ω 变成 22.5Ω 这类硬错），剔除项全部入日志备案。
    · 子电路端口序以 deck 为准并逐字核对（不一致即停）。
  裁定二护栏：
    1) 逐件「原行 → X 行」映射日志留档（本脚本写 pex_subst_audit_*.log / .md）；
    2) 门 1 回归 Δ=0 继续作为改写正确性机器闸（m5_pex_op_gate.py）。

用法：
  python3 m5_pex_substitute_jia.py --deck <deck.sp> --cdldir <dir> --out <out.sp>
                                 [--op-only] [--audit <audit.md>]
"""
import argparse
import os
import re
import sys

# ── 阶段 → cdl 文件 ───────────────────────────────────────────────────────────
STAGES = {
    'gilbert_mix': 'pex_mix_v27.cdl',
    'drv1':        'pex_drv1_v19.cdl',
    'drv2':        'pex_drv2_v19.cdl',
}

# ── 裁定一白名单：deck 侧逐字保留的理想件/偏置源/耦合件 ─────────────────────────
# 依据：b7a0 裁定一正文列明的理想件清单（Bvbl/Bvbh/Bvifb/Bvt/Is0/RL1/RL2/Lt1/Lt2/Cca1,2/Ccb1,2）
#       + 各阶段 deck 中「cdl 侧没有对应实物件」的其余行（激励/耦合/偏置电压源/参数）。
KEEP = {
    'gilbert_mix': ['Is0', 'Bvbl', 'Bvbh', 'Bvifb', 'Bvt',
                    'Cca1', 'Cca2', 'Ccb1', 'Ccb2',     # PAD 片外耦合 1nF（CDL 纪律 §3.1）
                    'RL1', 'RL2',                        # 45Ω tank 负载（CDL 纪律 §3.2）
                    'Lt1', 'Lt2',                        # 理想 tank L 1nH
                    'Ct1', 'Ct2'],                       # 理想 tank 谐振电容
    'drv1': ['Cin1', 'Cin2',                          # 10p 级间耦合
             'Vb',                                    # 尾流偏置电压源 1.20
             'RL1', 'RL2', 'Lt1', 'Lt2', 'Ct1', 'Ct2'],
    'drv2': ['Cin1', 'Cin2', 'Vb', 'Vbcas',
             'RL1', 'RL2', 'Lt1', 'Lt2', 'Ct1', 'Ct2'],
}

# ── cdl 侧剔除项：deck 保留件的「实物孪生」（同位置同标称值）→ 剔除防重复计入 ──
CDL_DROP = {
    'gilbert_mix': {
        'R15': 'deck RL1 45Ω tank 负载的实物孪生（vcc-lond 45Ω=RSIL×6.429/1.0）→ 裁定一保留 deck 侧',
        'R16': 'deck RL2 45Ω tank 负载的实物孪生（vcc-lond 45Ω）→ 裁定一保留 deck 侧',
    },
    'drv1': {
        'R8':  'deck RL1 100Ω tank 负载的实物孪生（vcc-cop RPPD×1.0/2.6=100Ω）→ 裁定一保留 deck 侧',
        'R9':  'deck RL2 100Ω tank 负载的实物孪生（vcc-con 100Ω）→ 裁定一保留 deck 侧',
    },
    'drv2': {
        'R11': 'deck RL1 100Ω tank 负载的实物孪生（vcc-outp RPPD×1.0/2.6=100Ω）→ 裁定一保留 deck 侧',
        'R12': 'deck RL2 100Ω tank 负载的实物孪生（vcc-outn 100Ω）→ 裁定一保留 deck 侧',
    },
}

# 派生层 RSH / MIM 面密度（仅用于日志备案的标称值复算，不参与电路计算）
RSH = {'rsil': 7.0, 'rhigh': 1360.0, 'rppd': 260.0}
CMIMA = 1.5e-15      # F/µm²


def load_cdl_body(path):
    """取 cdl 的 .subckt ... .ends 段（去掉头部注释与 .lib 行）"""
    body, inside, name = [], False, None
    for ln in open(path, encoding='utf-8'):
        s = ln.rstrip('\n')
        t = s.strip()
        m = re.match(r'^\.subckt\s+(\S+)', t, re.I)
        if m:
            inside, name = True, m.group(1)
            body.append(s)
            continue
        if inside and re.match(r'^\.ends\b', t, re.I):
            body.append(s)
            break
        if inside and t and not t.startswith('*') and not t.lower().startswith('.lib'):
            body.append(s)
    if not inside:
        raise SystemExit('cdl 无 .subckt 段：%s' % path)
    return name, body


def _f(v):
    """'4.286u' → 4.286e-06"""
    v = v.strip()
    if v.lower().endswith('u'):
        return float(v[:-1]) * 1e-6
    if v.lower().endswith('n'):
        return float(v[:-1]) * 1e-9
    if v.lower().endswith('p'):
        return float(v[:-1]) * 1e-12
    if v.lower().endswith('k'):
        return float(v[:-1]) * 1e3
    if v.lower().endswith('meg'):
        return float(v[:-3]) * 1e6
    return float(v)


def _param(params, key, default=None):
    m = re.search(r'\b%s\s*=\s*(\S+)' % re.escape(key), params, re.I)
    return m.group(1) if m else default


def rewrite_cdl_line(ln):
    """cdl 器件行 → X 行（不改数值与拓扑）。返回 (新行, 元件名, 标称值说明)"""
    t = ln.strip()
    # HBT: Q<名> c b e npn13G2 we=.. le=.. NX=.. M=.. sub=..
    m = re.match(r'^Q(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+npn13G2\s+(.*)$', t, re.I)
    if m:
        name, c, b, e, pr = m.groups()
        pr = re.sub(r'\bNX=', 'Nx=', pr, flags=re.I)
        pr = re.sub(r'\bM=\S+\s*', '', pr, flags=re.I)
        pr = re.sub(r'\bsub=\S+\s*', '', pr, flags=re.I)
        nx = _param(pr, 'Nx', '?')
        return ('XQ%s %s %s %s 0 npn13G2 %s' % (name, c, b, e, pr.strip()),
                'XQ' + name, 'HBT npn13G2 Nx=%s（we/le 原样透传）' % nx)
    # 三端电阻: R<名> n1 n2 (rsil|rhigh|rppd) l=.. w=.. sub=..
    m = re.match(r'^R(\S+)\s+(\S+)\s+(\S+)\s+(rsil|rhigh|rppd)\s+(.*)$', t, re.I)
    if m:
        name, n1, n2, mdl, pr = m.groups()
        pr2 = re.sub(r'\bsub=\S+\s*', '', pr, flags=re.I)
        l = _f(_param(pr2, 'l', '1u')); w = _f(_param(pr2, 'w', '1u'))
        r = RSH[mdl.lower()] * l / w
        return ('XR%s %s %s %s %s' % (name, n1, n2, mdl.lower(), pr2.strip()),
                'XR' + name, 'R=%s×%.6g/%.6g=%.6g Ω' % (RSH[mdl.lower()], l, w, r))
    # MIM 电容: C<名> n1 n2 cmim area=.. sub=..
    m = re.match(r'^C(\S+)\s+(\S+)\s+(\S+)\s+cmim\s+(.*)$', t, re.I)
    if m:
        name, n1, n2, pr = m.groups()
        pr2 = re.sub(r'\bsub=\S+\s*', '', pr, flags=re.I)
        a = _f(_param(pr2, 'area', '1.0'))
        return ('XC%s %s %s cmim %s' % (name, n1, n2, pr2.strip()),
                'XC' + name, 'C=area×1.5fF/µm²=%.6g fF（面项，裁定四）' % (a * 1.5e3))
    return None


def split_deck_body(body):
    """deck .subckt 体 → (保留行, 剔除行[(名字,原行)], 未知行)"""
    keep, drop, unknown = [], [], []
    for ln in body:
        t = ln.strip()
        if not t or t.startswith('*') or t.startswith('.'):
            keep.append((None, ln))            # 注释与 .param 等点命令：逐字保留
            continue
        nm = t.split()[0]
        keep.append((nm, ln))
    return keep


def build_stage_body(deck_body, cdl_body, stage, audit):
    """口径甲：deck 白名单保留 + cdl L0 实物器件行（X 改写）"""
    keepnames = KEEP[stage]
    drops = CDL_DROP[stage]

    # ---- deck 侧分类 ----
    deck_keep, deck_drop = [], []
    for ln in deck_body:
        t = ln.strip()
        if not t or t.startswith('*'):
            deck_keep.append((None, ln))
            continue
        if t.startswith('.'):
            deck_keep.append((None, ln))       # .param 等
            continue
        nm = t.split()[0]
        if nm in keepnames:
            deck_keep.append((nm, ln))
        else:
            deck_drop.append((nm, ln))

    # ---- cdl 侧 ----
    cdl_keep, cdl_drop = [], []
    for ln in cdl_body:
        t = ln.strip()
        if not t or t.startswith('*') or t.startswith('.') and not t.lower().startswith('.subckt'):
            continue
        if t.lower().startswith('.subckt') or t.lower().startswith('.ends'):
            continue
        nm = t.split()[0]
        if nm in drops:
            cdl_drop.append((nm, ln, drops[nm]))
            continue
        r = rewrite_cdl_line(t)
        if r is None:
            raise SystemExit('cdl 未知器件行（%s/%s）：%s' % (stage, nm, t))
        newline, xname, nominal = r
        cdl_keep.append((nm, ln, newline, xname, nominal))

    out = []
    out.append('* ---------- [%s] 口径甲代入：deck 保留件（白名单·逐字保留）----------' % stage)
    out.extend(ln for _nm, ln in deck_keep)
    out.append('* ---------- [%s] 口径甲代入：cdl L0 实物器件行（Q/R/C→X 改写·数值拓扑不动）----------' % stage)
    out.extend(x[2] for x in cdl_keep)

    audit.append('### 阶段 %s' % stage)
    audit.append('')
    audit.append('**deck 侧保留（%d 行）**：%s' % (len(deck_keep),
                 '、'.join(sorted({n for n, _ in deck_keep if n}) or ['（仅注释/参数）'])))
    audit.append('')
    audit.append('**deck 侧剔除（%d 行，L0 实物件→由 cdl 接管）**：' % len(deck_drop))
    audit.append('')
    audit.append('| deck 行 | 处理 |')
    audit.append('|---|---|')
    for nm, ln in deck_drop:
        audit.append('| `%s` | 剔除（L0 实物件，cdl 接管） |' % ln.strip()[:120])
    audit.append('')
    audit.append('**cdl 侧剔除（重复计入防护）**：')
    audit.append('')
    if cdl_drop:
        audit.append('| cdl 行 | 原因 |')
        audit.append('|---|---|')
        for nm, ln, why in cdl_drop:
            audit.append('| `%s` | %s |' % (ln.strip()[:120], why))
    else:
        audit.append('（无）')
    audit.append('')
    audit.append('**cdl 侧逐件映射（原行 → X 行，裁定二护栏 1）**：')
    audit.append('')
    audit.append('| 原 cdl 行 | 代入后 X 行 | 派生标称值 |')
    audit.append('|---|---|---|')
    for nm, o, nw, xname, nominal in cdl_keep:
        audit.append('| `%s` | `%s` | %s |' % (o.strip()[:110], nw.strip()[:110], nominal))
    audit.append('')
    return out


def find_subckt(src, name):
    a = None
    for i, ln in enumerate(src):
        m = re.match(r'^\s*\.subckt\s+(\S+)', ln, re.I)
        if m and m.group(1) == name:
            a = i
            break
    if a is None:
        raise SystemExit('deck 缺 .subckt %s' % name)
    b = a
    while not re.match(r'^\s*\.ends\b', src[b], re.I):
        b += 1
    return a, b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--deck', required=True)
    ap.add_argument('--cdldir', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--op-only', action='store_true',
                    help='产出只跑 .op 的快筛 deck（门1 秒级预筛，不做 tran）')
    ap.add_argument('--tran-raw', default='', help='tran 记录集导出路径（写进 deck 的 write 行）')
    ap.add_argument('--audit', default='', help='审计 md 落盘路径')
    a = ap.parse_args()

    src = open(a.deck, encoding='utf-8').read().split('\n')
    audit = ['# M5 口径甲代入审计（b7a0 四裁·裁定一/二）', '',
             '生成：m5_pex_substitute_jia.py（fde9）', '']

    cdl_map = {k: os.path.join(a.cdldir, v) for k, v in STAGES.items()}
    for k, p in cdl_map.items():
        if not os.path.exists(p):
            raise SystemExit('缺 cdl: %s' % p)

    new = list(src)
    # 先在原始 src 上算好三段行号，再**从后往前**替换（避免行号漂移）
    spans = {}
    for stage in ('gilbert_mix', 'drv1', 'drv2'):
        a0, b0 = find_subckt(src, stage)
        spans[stage] = (a0, b0)
    for stage in sorted(spans, key=lambda k: -spans[k][0]):
        a0, b0 = spans[stage]
        cdl_name, cdl_body = load_cdl_body(cdl_map[stage])
        if cdl_name != stage:
            raise SystemExit('cdl .subckt 名 %s ≠ deck 名 %s' % (cdl_name, stage))
        pa = src[a0].split()[2:]
        pb = [l for l in cdl_body if l.strip().lower().startswith('.subckt')][0].split()[2:]
        if [x.lower() for x in pa] != [x.lower() for x in pb]:
            raise SystemExit('端口序不一致 %s:\n  deck=%s\n  cdl =%s' % (stage, pa, pb))
        body = build_stage_body(src[a0+1:b0], cdl_body, stage, audit)
        new[a0+1:b0] = body
        # 段内自检：不得出现另一个 .subckt 头
        for ln in new[a0+1:b0]:
            if re.match(r'^\s*\.subckt\b', ln, re.I):
                raise SystemExit('段界错误：%s 体内混入 .subckt 头：%s' % (stage, ln))

    # 派生层 include（不改 cdl 一字，只是把 cdl 器件名接到 ngspice 可解模型）
    if not any('pex_devmodels.lib' in l for l in new):
        for i, ln in enumerate(new):
            if ln.strip().lower().startswith('.lib') and 'cornerhbt' in ln.lower():
                new.insert(i+1, '.include /data/workspace/sow6/m5/pex_devmodels.lib   $ fde9: PDK 器件模型派生层（rsil/rhigh/rppd/cmim）')
                break

    # .control：save（tran 前）+ tran + write
    if not a.op_only:
        ci = next((i for i, l in enumerate(new) if l.strip().lower() == '.control'), None)
        if ci is None:
            raise SystemExit('deck 缺 .control')
        tj = next((i for i in range(ci, len(new)) if new[i].strip().lower().startswith('tran ')), None)
        if tj is None:
            raise SystemExit('deck .control 内缺 tran')
        if not any('save noutp' in l for l in new[ci:tj]):
            new.insert(tj, 'save noutp noutn nmixp nmixn nd1p nd1n   $ fde9: save 须在 tran 之前（2GB 内存墙）')
            tj += 1
        if a.tran_raw and not any('write ' in l for l in new[ci:tj+3]):
            new.insert(tj+1, 'write %s   $ fde9: 导出 tran 记录集' % a.tran_raw)
    else:
        # 快筛：去掉 .control 整块，只留 deck 级 .op
        ci = next((i for i, l in enumerate(new) if l.strip().lower() == '.control'), None)
        if ci is not None:
            ei = next(i for i in range(ci, len(new)) if new[i].strip().lower() == '.endc')
            new[ci:ei+1] = ['* (口径甲快筛：.control 已摘除，只跑 deck 级 .op)']

    open(a.out, 'w', encoding='utf-8').write('\n'.join(new))
    if a.audit:
        open(a.audit, 'w', encoding='utf-8').write('\n'.join(audit) + '\n')
    print('out   : %s (%d B)' % (a.out, os.path.getsize(a.out)))
    print('audit : %s' % (a.audit or '(未指定)'))


if __name__ == '__main__':
    main()
