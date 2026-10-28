#!/usr/bin/env python3
"""svgpng.py —— 极简 SVG 光栅器（只支持 charts.py 产出的子集：rect/line/polyline/circle/text）。
用途：无浏览器环境下对 WebUI 图表做可视化自检（出 PNG 供视觉复核）。CJK 字形缺失属预期。"""
import io
import math
import re
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont

FONT = ImageFont.load_default()


def _f(v, d=0.0):
    try:
        return float(v)
    except Exception:
        return d


def _color(c, default=(200, 220, 240)):
    if not c or c == 'none':
        return None
    c = c.strip()
    if c.startswith('#') and len(c) == 7:
        return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    named = {'white': (255, 255, 255), 'black': (0, 0, 0), 'red': (255, 0, 0)}
    return named.get(c, default)


def render(svg: str, scale: float = 1.6, bg=(12, 20, 36)):
    vb = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    W, H = float(vb.group(1)), float(vb.group(2))
    img = Image.new('RGB', (int(W * scale), int(H * scale)), bg)
    d = ImageDraw.Draw(img)

    def P(x, y):
        return (x * scale, y * scale)

    for m in re.finditer(r'<(rect|line|polyline|circle|text)\b([^>]*?)/?>', svg):
        tag, attrs = m.group(1), m.group(2)
        a = dict(re.findall(r'([a-z-]+)="([^"]*)"', attrs))

        def num(k, d=0.0):
            return _f(a.get(k), d)
        if tag == 'rect':
            x, y, w, h = num('x'), num('y'), num('width'), num('height')
            fill = _color(a.get('fill'))
            op = _f(a.get('opacity'), 1.0)
            if fill and w > 0 and h > 0:
                x0, y0 = P(x, y)
                x1, y1 = P(x + w, y + h)
                if op >= 0.99:
                    d.rectangle([x0, y0, x1, y1], fill=fill)
                else:
                    ov = Image.new('RGBA', img.size, (0, 0, 0, 0))
                    od = ImageDraw.Draw(ov)
                    od.rectangle([x0, y0, x1, y1], fill=fill + (int(255 * op),))
                    img.paste(Image.alpha_composite(img.convert('RGBA'), ov).convert('RGB'), (0, 0))
                    d = ImageDraw.Draw(img)
        elif tag == 'line':
            st = _color(a.get('stroke'), (90, 110, 130))
            wpx = max(1, int(_f(a.get('stroke-width'), 1) * scale))
            dash = a.get('stroke-dasharray')
            p0, p1 = P(num('x1'), num('y1')), P(num('x2'), num('y2'))
            if dash:
                seg, gap = [float(x) for x in dash.split(',')]
                L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) or 1
                ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
                t = 0.0
                while t < L:
                    e = min(L, t + seg * scale)
                    d.line([p0[0] + ux * t, p0[1] + uy * t, p0[0] + ux * e, p0[1] + uy * e],
                           fill=st, width=wpx)
                    t += (seg + gap) * scale
            else:
                d.line([p0, p1], fill=st, width=wpx)
        elif tag == 'polyline':
            st = _color(a.get('fill'), (60, 130, 250))
            if st and a.get('fill') != 'none':
                pts = [P(*map(float, xy.split(','))) for xy in a.get('points', '').split()]
                if len(pts) > 1:
                    d.line(pts, fill=st, width=max(1, int(_f(a.get('stroke-width'), 1.4) * scale)),
                           joint='curve')
        elif tag == 'circle':
            st = _color(a.get('fill'), (60, 130, 250))
            cx, cy = P(num('cx'), num('cy'))
            rr = num('r') * scale
            if st:
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=st)
        elif tag == 'text':
            fill = _color(a.get('fill'), (200, 220, 240))
            x, y = P(num('x'), num('y'))
            txt = re.sub(r'\s+', ' ', a.get('', ''))
            anchor = a.get('text-anchor', 'start')
            txt = txt.strip()
            if not txt:
                continue
            try:
                f = ImageFont.truetype(
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', int(11 * scale))
            except Exception:
                f = FONT
            w = d.textlength(txt, font=f)
            if anchor == 'end':
                x -= w
            elif anchor == 'middle':
                x -= w / 2
            # transform=rotate(-90 ..) 的轴标题：旋转绘制
            tr = a.get('transform', '')
            if 'rotate(-90' in tr:
                rot = Image.new('RGBA', (int(w) + 8, 24), (0, 0, 0, 0))
                ImageDraw.Draw(rot).text((0, 0), txt, fill=fill, font=f)
                rot = rot.rotate(90, expand=True)
                img.paste(rot, (int(x - rot.height / 2), int(y - rot.width / 2)), rot)
            else:
                d.text((x, y - 12 * scale), txt, fill=fill, font=f)
    return img


def main():
    url, out = sys.argv[1], sys.argv[2]
    html = urllib.request.urlopen(url, timeout=40).read().decode()
    svgs = re.findall(r'<svg class="chart".*?</svg>', html, re.S)
    idx = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else range(len(svgs))
    imgs = []
    for i in idx:
        if i < len(svgs):
            imgs.append((i, render(svgs[i])))
    W = max(im.width for _, im in imgs)
    H = sum(im.height + 8 for _, im in imgs)
    sheet = Image.new('RGB', (W, H), (10, 16, 28))
    y = 0
    for i, im in imgs:
        sheet.paste(im, (0, y))
        y += im.height + 8
    sheet.save(out)
    print(f'{out} {sheet.size} charts={len(imgs)}')


if __name__ == '__main__':
    main()
