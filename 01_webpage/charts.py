#!/usr/bin/env python3
# charts.py —— 纯服务端 SVG 图表（无外部依赖、无 CDN；WiFi7-TX WebUI 专用）
# 线性/对数双轴、网格、图例、阈值线、分组柱。输出 SVG 字符串。
import math

PALETTE = ['#3b82f6', '#f97316', '#10b981', '#a855f7', '#ef4444', '#14b8a6',
           '#eab308', '#ec4899', '#6366f1', '#84cc16']
GRID = '#223047'
AXIS = '#5b6b82'
TEXT = '#c9d6e8'


def _nice_ticks(lo, hi, n=5):
    if hi <= lo:
        hi = lo + 1.0
    span = hi - lo
    raw = span / max(1, n)
    mag = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw / mag <= m:
            step = m * mag
            break
    else:
        step = 10 * mag
    start = math.floor(lo / step) * step
    ticks = []
    v = start
    while v <= hi + step * 0.5:
        if v >= lo - step * 0.001:
            ticks.append(round(v, 12))
        v += step
    return ticks


def _log_lab(v):
    """对数刻度标签：m=1 用 1e<n>，m=2/5 用 2e<n>/5e<n>（旧写法把 2e-1 与 5e-1 都标成 1e-1，三点重合读不出）"""
    e = int(math.floor(math.log10(v)))
    m = v / 10 ** e
    if abs(m - 1.0) < 1e-9:
        return f'1e{e}'
    return f'{m:g}e{e}'


def _log_ticks(lo, hi):
    # 口径：入参必须是【原始值域】(不是 log10 后的域)。line_chart 里 fx/fy 已把值映到 log 域，
    # 若把 log 域再喂进来 = log10 二次作用：负下界被 max(lo,1e-30) 悄悄夹到 1e-30，
    # 于是生成 1e-30…1e0 共 31 个十进刻度、且全被 fx 的 clamp 压到左缘同一 x → 整排伪刻度文本。
    if lo <= 0 or hi <= 0:
        raise ValueError(f'_log_ticks 需要正数原始值域，收到 lo={lo} hi={hi}')
    lo = max(lo, 1e-30)
    ticks = []
    e0, e1 = math.floor(math.log10(lo)), math.ceil(math.log10(hi))
    d = max(1e-9, 1.0)
    for e in range(int(e0), int(e1) + 1):
        for m in (1, 2, 5):
            v = m * 10 ** e
            if lo / d <= v <= hi * d:
                ticks.append(v)
    return ticks or [lo, hi]


def _fmt(v):
    if v == 0:
        return '0'
    a = abs(v)
    if a >= 1e5 or a < 1e-3:
        return f'{v:.2e}'
    if a >= 100:
        return f'{v:.1f}'
    if a >= 10:
        return f'{v:.2f}'
    if a >= 1:
        return f'{v:.3f}'
    return f'{v:.4g}'


def _scale(lo, hi, log):
    if log:
        lo = max(lo, 1e-30)
        hi = max(hi, lo * 10)
        def f(v):
            return math.log10(max(v, lo * 0.999))
        return f, (math.log10(lo), math.log10(hi))
    if hi <= lo:
        hi = lo + 1.0
    def f(v):
        return v
    return f, (lo, hi)


def line_chart(series, *, width=900, height=380, title='', xlabel='', ylabel='',
               xlog=False, ylog=False, hlines=(), vlines=(), ymin=None, ymax=None,
               xmin=None, xmax=None, markers=True, legend=True, pad=(58, 22, 44, 74),
               xtick_fmt=None, ypad=0.06):
    """series: [{name, x:[], y:[], color, dash, width}]；hlines=[(y,label)]"""
    xs, ys = [], []
    for s in series:
        for x, y in zip(s['x'], s['y']):
            if x is None or y is None:
                continue
            xs.append(x)
            ys.append(y)
    if not xs:
        return f'<div class="chart-empty">无数据</div>'
    xlo = xmin if xmin is not None else min(xs)
    xhi = xmax if xmax is not None else max(xs)
    ylo = ymin if ymin is not None else min(ys + [h[0] for h in hlines])
    yhi = ymax if ymax is not None else max(ys + [h[0] for h in hlines])
    if ylo == yhi:
        ylo, yhi = ylo - 1, yhi + 1
    elif ypad and not ylog:
        # 读图打磨（fde9 建议②）：数据极值不贴顶/底边，默认留 6% 余量（显式给 ymin/ymax 时不干预）
        span0 = yhi - ylo
        if ymin is None:
            ylo -= span0 * ypad
        if ymax is None:
            yhi += span0 * ypad * 1.15
    fx, (xlo_, xhi_) = _scale(xlo, xhi, xlog)
    fy, (ylo_, yhi_) = _scale(ylo, yhi, ylog)
    if ylog and ypad and ymin is None and ymax is None:
        dlog = yhi_ - ylo_
        if ymin is None:
            ylo_ -= dlog * ypad
        if ymax is None:
            yhi_ += dlog * ypad
    if xhi_ == xlo_:
        xhi_ = xlo_ + 1
    if yhi_ == ylo_:
        yhi_ = ylo_ + 1
    pt, pr, pb, pl = pad
    W, H = width, height
    iw = W - pl - pr
    ih = H - pt - pb

    def X(v):
        return pl + (fx(v) - xlo_) / (xhi_ - xlo_) * iw

    def Y(v):
        return pt + ih - (fy(v) - ylo_) / (yhi_ - ylo_) * ih

    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" '
           f'role="img" xmlns="http://www.w3.org/2000/svg">']
    if title:
        out.append(f'<text x="{pl}" y="18" class="ct">{title}</text>')
    yt = _log_ticks(max(ylo, 1e-30), max(yhi, 1e-30)) if ylog else _nice_ticks(ylo, yhi, 5)
    xt = _log_ticks(max(xlo, 1e-30), max(xhi, 1e-30)) if xlog else _nice_ticks(xlo, xhi, 6)
    def _xfmt(t):
        if xtick_fmt is None:
            return _fmt(t)
        try:
            return xtick_fmt.format(t)
        except Exception:
            return _fmt(t)
    for t in yt:
        y = Y(t)
        if y < pt - 1 or y > pt + ih + 1:
            continue
        out.append(f'<line x1="{pl}" y1="{y:.1f}" x2="{pl+iw}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        lab = _fmt(t) if not ylog else _log_lab(t)
        out.append(f'<text x="{pl-8}" y="{y+4:.1f}" class="ca" text-anchor="end">{lab}</text>')
    for t in xt:
        x = X(t)
        if x < pl - 1 or x > pl + iw + 1:
            continue
        out.append(f'<line x1="{x:.1f}" y1="{pt}" x2="{x:.1f}" y2="{pt+ih}" stroke="{GRID}" stroke-width="1"/>')
        lab = _xfmt(t) if not xlog else _log_lab(t)
        out.append(f'<text x="{x:.1f}" y="{pt+ih+18:.1f}" class="ca" text-anchor="middle">{lab}</text>')
    out.append(f'<line x1="{pl}" y1="{pt+ih}" x2="{pl+iw}" y2="{pt+ih}" stroke="{AXIS}"/>')
    out.append(f'<line x1="{pl}" y1="{pt}" x2="{pl}" y2="{pt+ih}" stroke="{AXIS}"/>')
    for y, lab in hlines:
        if ylo_ <= (math.log10(y) if ylog else y) <= yhi_:
            yy = Y(y)
            out.append(f'<line x1="{pl}" y1="{yy:.1f}" x2="{pl+iw}" y2="{yy:.1f}" stroke="#ef4444" '
                       f'stroke-width="1.4" stroke-dasharray="7,4"/>')
            out.append(f'<text x="{pl+iw-4}" y="{yy-5:.1f}" class="chl" text-anchor="end">{lab}</text>')
    for x, lab in vlines:
        if xlo_ <= (math.log10(x) if xlog else x) <= xhi_:
            xx = X(x)
            out.append(f'<line x1="{xx:.1f}" y1="{pt}" x2="{xx:.1f}" y2="{pt+ih}" stroke="#f59e0b" '
                       f'stroke-width="1.2" stroke-dasharray="5,4"/>')
            out.append(f'<text x="{xx+4:.1f}" y="{pt+12:.1f}" class="chl">{lab}</text>')
    for i, s in enumerate(series):
        col = s.get('color') or PALETTE[i % len(PALETTE)]
        da = f' stroke-dasharray="{s["dash"]}"' if s.get('dash') else ''
        segs, cur = [], []
        for x, y in zip(s['x'], s['y']):
            if x is None or y is None:
                if cur:
                    segs.append(cur)
                cur = []
                continue
            px, py = X(x), Y(y)
            cur.append((px, py))
            if markers and len(s['x']) <= 40:
                out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{col}"/>')
        if cur:
            segs.append(cur)
        for seg in segs:
            if len(seg) > 1:
                pl_pts = ' '.join(f'{a:.1f},{b:.1f}' for a, b in seg)
                out.append(f'<polyline points="{pl_pts}" fill="none" stroke="{col}" '
                           f'stroke-width="{s.get("width",1.8)}" stroke-linejoin="round"{da}/>')
            elif seg:
                out.append(f'<circle cx="{seg[0][0]:.1f}" cy="{seg[0][1]:.1f}" r="3.5" fill="{col}"/>')
    if xlabel:
        out.append(f'<text x="{pl+iw/2:.0f}" y="{H-8}" class="ca" text-anchor="middle">{xlabel}</text>')
    if ylabel:
        out.append(f'<text x="14" y="{pt+ih/2:.0f}" class="ca" text-anchor="middle" '
                   f'transform="rotate(-90 14 {pt+ih/2:.0f})">{ylabel}</text>')
    if legend:
        lx, ly = pl, H - 26
        for i, s in enumerate(series):
            col = s.get('color') or PALETTE[i % len(PALETTE)]
            out.append(f'<rect x="{lx}" y="{ly-9}" width="11" height="11" rx="2" fill="{col}"/>')
            out.append(f'<text x="{lx+16}" y="{ly}" class="ca">{s.get("name","")}</text>')
            lx += 20 + 7.2 * len(s.get('name', ''))
    out.append('</svg>')
    return ''.join(out)


def bar_chart(cats, groups, *, width=900, height=380, title='', ylabel='', hlines=(),
              ymin=None, ymax=None, pad=(58, 22, 60, 74), value_fmt='{:.2f}', ylabel2=''):
    """groups: [{name, values:[], color, axis}]；cats 为类目标签。
    axis=2 的组走右轴（量纲不同的多轴共图，fde9 建议①），右轴独立标度、独立刻度。"""
    g1 = [g for g in groups if g.get('axis', 1) != 2]
    g2 = [g for g in groups if g.get('axis', 1) == 2]
    vals = [v for g in g1 for v in g['values'] if v is not None]
    if not vals and not g2:
        return '<div class="chart-empty">无数据</div>'
    pt, pr, pb, pl = pad
    has2 = bool(g2) and bool(vals)
    if has2:
        pr = max(pr, 56)
    W, H = width, height
    iw = W - pl - pr
    ih = H - pt - pb
    if vals:
        lo = ymin if ymin is not None else min(vals + [h[0] for h in hlines])
        hi = ymax if ymax is not None else max(vals + [h[0] for h in hlines])
        if lo > 0 and lo / (hi - lo if hi != lo else 1) > 2:
            lo = 0
        if hi == lo:
            hi = lo + 1
        span = hi - lo
        hi += span * 0.08
        lo -= span * 0.12 if lo < 0 else span * 0.02
    else:
        lo, hi = 0.0, 1.0
    vals2 = [v for g in g2 for v in g['values'] if v is not None]
    if vals2:
        lo2, hi2 = min(vals2), max(vals2)
        if lo2 > 0:
            lo2 = 0
        if hi2 == lo2:
            hi2 = lo2 + 1
        span2 = hi2 - lo2
        hi2 += span2 * 0.08
        lo2 -= span2 * 0.02

    def Y(v):
        return pt + ih - (v - lo) / (hi - lo) * ih

    def Y2(v):
        return pt + ih - (v - lo2) / (hi2 - lo2) * ih

    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" '
           f'role="img" xmlns="http://www.w3.org/2000/svg">']
    if title:
        out.append(f'<text x="{pl}" y="18" class="ct">{title}</text>')
    zero = Y(0)
    for t in _nice_ticks(lo, hi, 5):
        y = Y(t)
        if y < pt - 1 or y > pt + ih + 1:
            continue
        out.append(f'<line x1="{pl}" y1="{y:.1f}" x2="{pl+iw}" y2="{y:.1f}" stroke="{GRID}"/>')
        out.append(f'<text x="{pl-8}" y="{y+4:.1f}" class="ca" text-anchor="end">{_fmt(t)}</text>')
    if vals2:
        for t in _nice_ticks(lo2, hi2, 5):
            y = Y2(t)
            if y < pt - 1 or y > pt + ih + 1:
                continue
            out.append(f'<text x="{pl+iw+8}" y="{y+4:.1f}" class="ca">{_fmt(t)}</text>')
        out.append(f'<line x1="{pl+iw}" y1="{pt}" x2="{pl+iw}" y2="{pt+ih}" stroke="{AXIS}"/>')
        if ylabel2:
            out.append(f'<text x="{W-10}" y="{pt+ih/2:.0f}" class="ca" text-anchor="middle" '
                       f'transform="rotate(90 {W-10} {pt+ih/2:.0f})">{ylabel2}</text>')
    n, g = len(cats), len(groups)
    slot = iw / max(1, n)
    bw = slot * 0.72 / max(1, g)
    for gi, grp in enumerate(groups):
        col = grp.get('color') or PALETTE[gi % len(PALETTE)]
        sc = Y2 if grp.get('axis', 1) == 2 else Y
        z = sc(0) if vals2 and grp.get('axis', 1) == 2 else zero
        for ci, v in enumerate(grp['values']):
            if v is None:
                continue
            x = pl + ci * slot + slot * 0.14 + gi * bw
            y = sc(v)
            h = abs(z - y)
            y0 = min(z, y)
            out.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{bw*0.9:.1f}" height="{max(0.6,h):.1f}" '
                       f'fill="{col}" rx="1.5" opacity="0.88"><title>{cats[ci]} · {grp.get("name","")} = '
                       f'{value_fmt.format(v)}</title></rect>')
    for y, lab in hlines:
        if lo <= y <= hi:
            yy = Y(y)
            out.append(f'<line x1="{pl}" y1="{yy:.1f}" x2="{pl+iw}" y2="{yy:.1f}" stroke="#ef4444" '
                       f'stroke-width="1.4" stroke-dasharray="7,4"/>')
            out.append(f'<text x="{pl+iw-4}" y="{yy-5:.1f}" class="chl" text-anchor="end">{lab}</text>')
    out.append(f'<line x1="{pl}" y1="{zero:.1f}" x2="{pl+iw}" y2="{zero:.1f}" stroke="{AXIS}"/>')
    step = 1 if n <= 24 else (2 if n <= 60 else 3)
    for ci, c in enumerate(cats):
        if ci % step:
            continue
        out.append(f'<text x="{pl+ci*slot+slot/2:.1f}" y="{pt+ih+17:.1f}" class="ca" '
                   f'text-anchor="middle">{c}</text>')
    if ylabel:
        out.append(f'<text x="14" y="{pt+ih/2:.0f}" class="ca" text-anchor="middle" '
                   f'transform="rotate(-90 14 {pt+ih/2:.0f})">{ylabel}</text>')
    lx, ly = pl, H - 22
    for i, grp in enumerate(groups):
        col = grp.get('color') or PALETTE[i % len(PALETTE)]
        nm = grp.get('name', '')
        if grp.get('axis', 1) == 2 and ylabel2:
            nm = f'{nm}（右轴）'
        out.append(f'<rect x="{lx}" y="{ly-9}" width="11" height="11" rx="2" fill="{col}"/>')
        out.append(f'<text x="{lx+16}" y="{ly}" class="ca">{nm}</text>')
        lx += 20 + 7.2 * len(nm)
    out.append('</svg>')
    return ''.join(out)


def heat_table(rows, cols, values, *, thresholds=(), fmt='{:.2f}', caption=''):
    """小热力表：values[r][c]（None=缺）；thresholds=((上界, 绿), ...) 逐格判色。"""
    out = ['<table class="ht"><caption>' + caption + '</caption><tr><th></th>']
    out += [f'<th>{c}</th>' for c in cols]
    out.append('</tr>')
    for ri, rname in enumerate(rows):
        out.append(f'<tr><th>{rname}</th>')
        for ci in range(len(cols)):
            v = values[ri][ci]
            if v is None:
                out.append('<td class="na">—</td>')
                continue
            cls = ''
            for th, cname in thresholds:
                if v <= th:
                    cls = cname
                    break
            out.append(f'<td class="{cls}">{fmt.format(v)}</td>')
        out.append('</tr>')
    out.append('</table>')
    return ''.join(out)
