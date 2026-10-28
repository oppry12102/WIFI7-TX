#!/usr/bin/env python3
# server.py —— WiFi7-TX 设计交付全景 WebUI（FastAPI，无鉴权，只读静态数据）
# 端口 8600。启动: python3 webui/server.py
import html
from urllib.parse import quote
import json
import math
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import charts  # noqa: E402

WS = '/data/workspace'
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data', 'site.json')

try:
    import markdown
except ImportError:
    markdown = None
try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name
    from pygments.formatters import HtmlFormatter
    _PYG = True
except Exception:
    _PYG = False

from fastapi import FastAPI, Query, HTTPException          # noqa: E402
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse  # noqa: E402

app = FastAPI(title='WiFi7-TX WebUI', docs_url=None, redoc_url=None)

_STATE = {'mtime': 0, 'data': None}
_MD_CACHE = {}


def S():
    if _STATE['data'] is None or os.path.getmtime(DATA) != _STATE['mtime']:
        with open(DATA, encoding='utf-8') as f:
            _STATE['data'] = json.load(f)
        _STATE['mtime'] = os.path.getmtime(DATA)
    return _STATE['data']


def safe_path(rel, roots):
    """白名单目录内取件，防穿越。"""
    p = os.path.realpath(os.path.join(WS, rel))
    if not any(p == r or p.startswith(r + os.sep) for r in
               [os.path.realpath(os.path.join(WS, x)) for x in roots]):
        raise HTTPException(404, 'path not allowed')
    return p


# ---------------------------------------------------------------- 壳
NAV = [('/', '总览'), ('/spec', '规格'), ('/docs/architecture-md', '架构'), ('/docs', '文档'), ('/circuit', '电路'), ('/layout', '版图'), ('/phys', '版图实证'),
       ('/dyn', '动态指标'), ('/scan', 'ACPR 扫描'), ('/netlist', '网表'), ('/sim', '仿真'), ('/tree', '文件树'), ('/data', '数据')]

CSS = """
*{box-sizing:border-box}
body{margin:0;background:#0b1220;color:#c9d6e8;
 font:15px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans CJK SC','PingFang SC',sans-serif}
a{color:#7cc4ff;text-decoration:none}a:hover{text-decoration:underline}
header{position:sticky;top:0;z-index:20;background:#0d1524f0;backdrop-filter:blur(6px);
 border-bottom:1px solid #1e2a3d;padding:10px 22px;display:flex;align-items:center;gap:22px;flex-wrap:wrap}
header .brand{font-weight:700;color:#eaf2ff;letter-spacing:.3px}
header nav a{margin-right:14px;font-size:14px;color:#9fb6d4;padding:3px 2px}
header nav a.on{color:#fff;border-bottom:2px solid #3b82f6}
header .sp{flex:1}
header .tag{font-size:12px;color:#7d93b0;border:1px solid #24334a;border-radius:20px;padding:2px 10px}
main{max-width:1180px;margin:0 auto;padding:22px}
h1{font-size:24px;margin:6px 0 4px}h2{font-size:19px;margin:26px 0 10px;color:#eaf2ff;
 border-left:3px solid #3b82f6;padding-left:9px}h3{font-size:16px;margin:18px 0 8px;color:#dbe7f7}
.card{background:#101a2b;border:1px solid #1e2a3d;border-radius:10px;padding:14px 16px;margin:10px 0}
.grid{display:grid;gap:12px}.g2{grid-template-columns:repeat(auto-fit,minmax(340px,1fr))}
.g3{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}.g4{grid-template-columns:repeat(auto-fit,minmax(190px,1fr))}
.kpi{background:#101a2b;border:1px solid #1e2a3d;border-radius:10px;padding:12px 14px}
.kpi .v{font-size:22px;font-weight:700;color:#7cc4ff}.kpi .l{font-size:12.5px;color:#8fa6c2}
.kpi .n{font-size:11.5px;color:#6d84a3;margin-top:3px}
.ok{color:#34d399}.no{color:#f87171}.warn{color:#fbbf24}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:8px 0}
th,td{border:1px solid #1e2a3d;padding:5px 8px;text-align:left;vertical-align:top}
th{background:#13203a;color:#bcd2ee;font-weight:600}
tr:hover td{background:#142033}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
code,pre{font-family:ui-monospace,Menlo,Consolas,monospace}
code{background:#142033;padding:1px 5px;border-radius:4px;font-size:12.5px;color:#9ad7ff}
pre{background:#0a1120;border:1px solid #1e2a3d;border-radius:8px;padding:10px 12px;overflow:auto;
 font-size:12px;line-height:1.5}
pre code{background:none;padding:0}
.chart{width:100%;height:auto;background:#0c1424;border:1px solid #1a2436;border-radius:8px}
.ct{fill:#dbe7f7;font-size:14px;font-weight:600}.ca{fill:#8296b2;font-size:10.5px}
.chl{fill:#f87171;font-size:10.5px}
.chart-empty{padding:20px;color:#6d84a3}
.badge{display:inline-block;padding:2px 9px;border-radius:12px;font-size:12px;border:1px solid}
.b-ok{color:#34d399;border-color:#14532d;background:#0d2b1e}
.b-no{color:#f87171;border-color:#7f1d1d;background:#2b0d0d}
.b-warn{color:#fbbf24;border-color:#78350f;background:#2b1f0d}
.b-info{color:#7cc4ff;border-color:#1e3a8a;background:#0d1c33}
.fig{background:#0c1424;border:1px solid #1e2a3d;border-radius:10px;padding:10px}
.fig svg{width:100%;height:auto;background:#fff;border-radius:6px}
.fig .cap{font-size:12.5px;color:#8fa6c2;margin-top:7px}
.fig .cap b{color:#dbe7f7}
.muted{color:#8296b2;font-size:12.5px}
.pill{display:inline-block;background:#13203a;border:1px solid #24354f;border-radius:14px;
 padding:2px 10px;margin:2px 4px 2px 0;font-size:12px}
.toc{columns:2;font-size:13px}
.small{font-size:12.5px}
hr{border:0;border-top:1px solid #1e2a3d;margin:18px 0}
"""


def page(title, body, active='', sub=''):
    nav = ''.join(f'<a href="{u}" class="{"on" if u == active else ""}">{n}</a>' for u, n in NAV)
    return HTMLResponse(f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · WiFi7-TX 设计交付全景</title><style>{CSS}</style></head><body>
<header><span class="brand">WiFi7-TX · 交付全景</span><nav>{nav}</nav><span class="sp"></span>
<span class="tag">SOW-2 结项 · v014 终态</span><span class="tag">无鉴权 · 只读</span></header>
<main>{('<p class="muted">'+sub+'</p>' if sub else '')}{body}</main></body></html>""")


def tbl(headers, rows, cls=''):
    h = ''.join(f'<th class="{cls}">{x}</th>' for x in headers)
    body = ''
    for r in rows:
        body += '<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>'
    return f'<table><tr>{h}</tr>{body}</table>'


def kpi(v, label, note='', cls=''):
    return (f'<div class="kpi"><div class="v {cls}">{v}</div><div class="l">{label}</div>'
            f'<div class="n">{note}</div></div>')


def badge(ok, text_ok, text_no):
    return f'<span class="badge {"b-ok" if ok else "b-no"}">{text_ok if ok else text_no}</span>'


def md_html(rel):
    p = os.path.join(WS, rel)
    key = (rel, os.path.getmtime(p))
    if key in _MD_CACHE:
        return _MD_CACHE[key]
    txt = open(p, encoding='utf-8').read()
    if markdown is None:
        out = '<pre>' + html.escape(txt) + '</pre>'
    else:
        exts = ['tables', 'fenced_code', 'toc', 'sane_lists', 'attr_list']
        if _PYG:
            exts.append('codehilite')
        out = markdown.markdown(txt, extensions=exts, extension_configs={
            'codehilite': {'guess_lang': False, 'css_class': 'codehilite'},
            'toc': {'permalink': False}})
        if _PYG:
            out += '<style>' + HtmlFormatter(style='monokai', noclasses=True).get_style_defs('.codehilite') \
                + '.codehilite{background:#0a1120;border:1px solid #1e2a3d;border-radius:8px;padding:8px 10px}</style>'
    if len(_MD_CACHE) > 64:
        _MD_CACHE.clear()
    _MD_CACHE[key] = out
    return out


def highlight_code(text, lang='spice'):
    if _PYG:
        try:
            return highlight(text, get_lexer_by_name(lang), HtmlFormatter(style='monokai', noclasses=True))
        except Exception:
            pass
    return '<pre>' + html.escape(text) + '</pre>'


# ---------------------------------------------------------------- 总览
@app.get('/', response_class=HTMLResponse)
def home():
    d = S()
    op, sp, ext, meta = d['op27'], d['sp'], d['tran']['ext'], d['meta']
    m8h = sp.get('stats') or {}
    mix = ext.get('mix', {})
    rows = []
    rows.append((f'<b>SOW-1 系统/行为级</b>', 'spec v1.3 冻结 + architecture v1.2 + 终稿报告 v1.2 + 集成评审 R-01~R-09',
                 '<span class="badge b-ok">已交付</span>', 'final_report.md / spec.md'))
    rows.append(('<b>SOW-2 晶体管级</b>', 'SG13G2 PDK + ngspice-47，三板（Gilbert 混频器 / LO BUF / 链级联）',
                 '<span class="badge b-ok">已结项</span>', 'pdk/sim/v014/ 定稿板'))
    rows.append(('<b>OP27 工作点</b>', f'27 角全扫（3 corner × 3 温 × 3 vdd）× 3 板 = 81 deck，判据域 '
                 f'{op["axis_pass"]}/{op["axis_total"]} 全过',
                 badge(op['axis_pass'] == op['axis_total'], 'PASS', 'FAIL'),
                 f'results_r2_v014/op27_summary_v014.csv'))
    rows.append(('<b>sp 频域</b>', f'27 角 × 61 频点（0.1G~100G）全 S 谱，混合模 Sdd 3 对 1647 点零 fail',
                 '<span class="badge b-ok">PASS</span>', f"eig 带内 max {m8h.get('eig_wb_max')}"))
    rows.append(('<b>tran 时域</b>', '2.5µs 双音（IF 9/11MHz，LO 5.5GHz）+ 链级，原始波形 1.4GB 全量归档',
                 '<span class="badge b-ok">PASS</span>', f"mix OIP3 {mix.get('OIP3_dBm')} dBm"))
    rows.append(('<b>SOW-6 全链版图</b>', 'lib13g2 v2.3 单元库 → M2/M3 代跑 → DRV1/DRV2 全链 GDS（v19 E 断路修复版）；'
                 'DRC 残留全 PCell 备案族零新增；LVS 粘连案判决 = deck 端子识别 bug（版图三次无罪），修复重跑收口中',
                 '<span class="badge b-warn">收口中</span>', 'phys/report/SOW-6_全链版图报告.md'))
    chain_out = ext.get('chain', {}).get('chain_out', {})
    kpis = ''.join([
        kpi(f'{op["axis_pass"]}/{op["axis_total"]}', 't125 温漂判据域（|Δ|≤6.4mV）',
            f'最差 {op["axis_worst"]["d_mV"]:+}mV @ {op["axis_worst"]["corner"]}', 'ok'),
        kpi(f'{op["spec_iv"]}mA', 'i_vcc 规格点本体电流', '45mA 判据线内（mix typ/t27/v2500）'),
        kpi(f'kptat {op["kptat"]}', 'PTAT 补偿系数（v014 收口）', 'η 实测 typ .670 / bcs .815 / wcs .552'),
        kpi(f'{mix.get("CG_dB_per_tone")}dB', '混频器转换增益（每音）',
            f'Pout {mix.get("pout_per_band_dBm")}dBm · OIP3 {mix.get("OIP3_dBm")}dBm'),
        kpi(f'{m8h.get("n_files")}', 'sp 数据集（27 角 × 2 口径）',
            f'single-fails {m8h.get("single_fails_total")} · Sdd fail {m8h.get("sdd_fails")}'),
        kpi(f'{len(d["docs"])}', '文档（规格/架构/评审/结项/纪要）', '全量 Markdown 渲染可读'),
        kpi(f'{sum(len(g["items"]) for g in d["netlists"])}', '网表文件（可在线阅读/下载）',
            'v014 定稿 / v013 / v011a-r2 投件 / 代跑主版'),
        kpi(f'{len(d["figures"])}', '图形（版图规划 + 电路拓扑）', 'SVG 内嵌，零外链'),
    ])
    def _n(x):
        return '—' if x is None else f'{x:+.2f}'
    def _cell(v, k):
        """实测（CSV 现算）+ 预测另注。口径纪律：三列只放实测，预测必须带『预测』字样。"""
        s = _n(v[k])
        p = v.get('pred')
        if p:
            s += f'<br><span class="muted small">预测 {p[{"typ":0,"bcs":1,"wcs":2}[k]]:+.2f}</span>'
        return s

    # ---- SOW-6 全链版图区块（数字全部来自 sitebuild 现算，叙述为内容编组）----
    sw = d.get('sow6', {})
    sw_drc1 = (sw.get('drc', {}).get('drv1_v23') or {}).get('violations')
    sw_drc2 = (sw.get('drc', {}).get('drv2_v22') or {}).get('violations')
    sw_drcmix = (sw.get('drc', {}).get('mix_v35') or {}).get('violations')

    def _slug(rel):
        return re.sub(r'[^0-9A-Za-z一-鿿]+', '-', rel).strip('-')
    sw_miles = [
        ('M1 规划与单元库', 'lib13g2 v2.1→v2.3 定版：guard_ring / keepout 零违规；via/cmim 镜像判定 + 单元几何真值表',
         'phys/top/判读纪要_lib13g2v2_guardring_keepout_2026-10-17.md', 'done'),
        ('M2/M3 器件库与代跑', 'M2 v2.3 交付收讫 · M2/M3 代跑 v24 全链 · M3 接收八项回执',
         'phys/top/判读纪要_M2M3代跑v24全链_2026-10-17.md', 'done'),
        ('Q8~Q12 五轮代跑闭环', 'DRC 三口径持平 + gdsdiff 唯一 delta 逐字吻合；cmim 拆分并联、发射极回流桶 187 件/边等裁定逐轮落地',
         'phys/top/判读纪要_Q12代跑v17轮_2026-10-17.md', 'done'),
        ('v18 补环代跑', 'ptap×8 落环 + 岛框逐字对；器件 PCell 零变化、DRC Δ+0 指纹全同；pwell 浮空实证已解',
         'phys/top/判读纪要_v18补环代跑轮_2026-10-17.md', 'done'),
        ('LVS 粘连案 · 幻影焊判决', '12 变体刀阵三刀二分：案发现场零短路 ⇒ deck npn 端子识别 bug，版图三次无罪；骑体对照表 v2 + 指派定律收编',
         'outbox_files/design/sow6/knife_骑体对照表与指派定律_v2_2026-10-17.md', 'done'),
        ('E 回流链断路 · v19 修复', '四方实锤（断缝 0.085µm）→ lap 0.6µm 修复三轮实证：几何 assert / LVS e1$1 消散 / DRC −3−3 新增 0',
         'phys/top/判读纪要_v19修复代跑轮_2026-10-17.md', 'done'),
        ('deck 修复与 LVS 闭环', 'b7e7 修复端子指派后重跑：合并名消散 + bulk 对上 v3 + R$13/14 归位 ⇒ PASS 即粘连案闭环（判据已立）',
         'phys/top/判读纪要_deck4数校准_桥元素实锤_2026-10-17.md', 'run'),
        ('PEX 后仿 27 角', 'fde9 正式 pex_ 三件到货即启：runbook v2.5 版本门 → 双门（A0′≤1e-5 + |CG−17.4465|≤0.05）→ 口令②',
         'pdk/sim/r2run/判读纪要_sow6m5_typ基线_2026-10-17.md', 'done'),
        ('ntaila 真短 · 根因六环闭合', '短路在<b>器件扩散块重叠</b>（真交集 2.8650µm²，非 2.6250——那是 bbox 重叠<b>长度</b>）；'
         'M1 上两轨本不相接（域 57 vs 域 1，最近 1.8255µm）⇒ QR_L=12.0 修的是 M1 间距、修不到扩散重叠。'
         '立<b>量连接层从半导体层起算律</b>（尺必须含 Activ+Cont，只有金属+via 结构上量不到经扩散的短路）',
         'phys/top/判读纪要_裁定五十六_mix_v31_ntaila同域器件级根因_2026-10-19.md', 'done'),
        ('v34 甲案 · 镜像真拉开', 'QR_L/QR_R 并成 QR_OFF=25.35 真镜像 ⇒ 官方提取 XBI1/nref 与 ntaila <b>两网独立</b>、并网写法 0 次；'
         'Activ 交集 2.8650→<b>0.0000</b>µm²。立<b>镜像动作缺陷倍增律</b>（M4.b 新增 1 条＝既有缺陷镜像复制，非新缺陷）',
         'phys/top/判读纪要_裁定五十八_mix_v34甲案代跑验收_ntaila同域已消除_2026-10-19.md', 'done'),
        ('27 角族收口 + 判据缺项闭合', 'fde9 全 27 角收口成立（带三条限定）；判据缺项经裁定五十九/六十一/六十三闭合 ⇒ '
         '预注册文 v2 <b>全段背书生效</b>（臂A/臂B 废止，主判据＝<b>结构性序关系·零阈值</b>）。'
         '立<b>门限出身场合律</b>（0.05dB 出身复现精度被移植到族内离散 ⇒ 量级错配 252 倍）',
         'phys/top/判读纪要_裁定六十三_fde9预注册文v2复核背书_全段通过_2026-10-19.md', 'done'),
        ('★v35 M4.b 根修 · 面锚换锚', 'mix GDS 面 v35 = v34 + 假管 gnd 立管外移 δ=0.100（一个常量改两侧 6 段）⇒ '
         '<b>M4.b 2→0、DRC 219、新增 0</b>；<b>LVS PASS</b>（net_pair 29 Match 29）；'
         '版图侧提取件与 v34×v1f <b>除时间戳外逐字节相同</b> ⇒ 对提取零影响。'
         '换锚前置三条全达成（情形 A：只改面锚登记、deck 不动 ⇒ 27 角族/PEX/M5 谱系零影响）',
         'phys/top/判读纪要_裁定六十五_b7e7v35批验收_v35×v1g_LVS_PASS_M4b根修闭环_组长自纠027溯源_2026-10-19.md', 'done'),
    ]
    sw_rows = [(f'<b>{t}</b>', desc, f'<a href="/docs/{_slug(pth)}">纪要/报告</a>',
                '<span class="badge b-ok">完成</span>' if st == 'done' else
                ('<span class="badge b-warn">进行中</span>' if st == 'run'
                 else '<span class="badge b-info">候件</span>'))
               for t, desc, pth, st in sw_miles]
    sw_kpis = ''.join([
        kpi(f'{sw_drcmix} / {sw_drc1} / {sw_drc2}', 'MIX v35 / DRV1 v23 / DRV2 v22 DRC 残留（现算）',
            '现役面锚轮（裁定六十五换锚）：mix v35 = v34 + M4.b 根修（δ=0.100，假管 gnd 立管外移）⇒ M4.b 2→0、新增 0；'
            'drv1 v23 = 现役面锚（pwell 接地 tap 轮之后续锚）；drv2 v22。残留全 PCell 备案族'
            '（mix 侧 M1.b 8 条经独立布尔复现 8/8 落 PCell 实例内、0/8 落顶层自画 M1 域内 ⇒ 归器件内部账，不归摆位）', 'ok'),
        kpi(f'{sw.get("n_runs", "—")}', '代跑闭环轮次（M2M3 v24 → Q8~Q12 → v18 → v19 → v29 M1.e 清零 → v31 ntaila 修复 → v34 镜像 → v35 M4.b 根修）',
            '每轮 sha 收讫 + preflight/teeth/DRC 坐标级 diff（含镜像归因）/几何指纹全链自证'),
        kpi(f'{sw.get("n_memos", "—")}', 'SOW-6 纪要/回执/真值表（phys/top）',
            '全部 Markdown 全文渲染于文档库'),
        kpi('×3', '三面 LVS 官方真跑 PASS', 'mix v35×v1g（net_pair 29 Match 29）／drv1 v23（13/13）／drv2 v22；'
            '粘连案判决 = deck 端子识别 bug，版图无罪', 'ok'),
    ])
    sw_report_slug = _slug('phys/report/SOW-6_全链版图报告.md')

    tl = [(f'<b>{v["ver"]}</b>', v['change'], _cell(v, 'typ'), _cell(v, 'bcs'), _cell(v, 'wcs'),
           f'<span class="badge {"b-ok" if "全过" in v["verdict"] else "b-no"}">'
           f'{"PASS" if "全过" in v["verdict"] else "FAIL"}</span> '
           + re.sub(r'^(全过|FAIL)（?', '', v['verdict']))
          for v in d['iteration']]
    vs = op['versions']
    cats = [v['ver'] for v in vs]
    ch_iter = charts.bar_chart(
        cats, [{'name': '判据轴最大 |残差|',
                'values': [abs(v['axis_worst']['d_mV']) if v['axis_worst'] else None for v in vs],
                'color': '#f97316'}],
        title='四轮迭代：判据轴最大温漂残差（v014 单参数收口 kptat=3.98 后全过 6.4mV 判据线）',
        ylabel='|Δ| (mV)', hlines=[(6.4, '判据线 6.4mV')], height=300)
    crit_nodes = ['mix.ntaila', 'chain.mi.ntaila', 'chain.lb.ntaila', 'chain.lb.ntailb', 'lob.ntaila']
    gser = []
    for i, seg in enumerate(('typ', 'bcs', 'wcs')):
        gser.append({'name': seg, 'color': charts.PALETTE[i],
                     'values': [next((x['d_mV'] for x in op['axis'] if x['node'] == nm
                                      and x['corner'] == seg), None) for nm in crit_nodes]})
    ch_axis = charts.bar_chart(crit_nodes, gser, title='v014 终态：判据域 15/15 点温漂残差（5 测点 × 3 corner）',
                               ylabel='mV', hlines=[(6.4, '+6.4'), (-6.4, '−6.4')], value_fmt='{:+.2f}',
                               height=320)
    body = f"""
<div class="card">
  <h1>{meta['title']}</h1>
  <p class="muted">{meta['sub']}　·　{meta['team']}</p>
  <p><span class="badge b-ok">● {meta['status']}</span>　<span class="badge b-info">{meta['tool']}</span></p>
</div>
<div class="grid g4">{kpis}</div>
<h2>验证矩阵</h2>
{tbl(['工作包', '内容', '状态', '证据'], rows)}
<h2>SOW-6 全链版图 · 最新进展 <span class="badge b-warn">2026-10-17 一日战果</span></h2>
<p class="muted">单元库定版（lib13g2 v2.3）→ M2/M3 代跑 → Q8~Q12 五轮代跑闭环 → v18 补环 → LVS 粘连案幻影焊判决
→ E 回流链断路 v19 修复。全程组长代跑 + sha 收讫对账，判读纪要逐轮归档（<a href="/docs">文档库 · SOW-6 组</a>）。
收口两件：deck 修复重跑（LVS）、fde9 PEX 27 角（后仿对拍 typ 基线）。
结项报告：<a href="/docs/{sw_report_slug}">SOW-6 全链版图报告 v0.3</a>。</p>
<div class="grid g4">{sw_kpis}</div>
{tbl(['里程碑', '内容', '证据', '状态'], sw_rows)}
<h2>SOW-2 迭代路径（OP27 t125 温漂残差，mV）</h2>
<p class="muted">判据线 |Δ| ≤ 6.4mV，判据轴 = v2500；v014 单参数收口后判据域全过，边角域（v2250/v2750）
按拍板划 dcvr 备案、不阻塞结项。<b>typ/bcs/wcs 三列为判据点 mix.ntaila 的 (t125−t27) 残差、由 op27 CSV 现算</b>
（与判读纪要各版表格、<a href="/sim/op">/sim/op</a>、<a href="/sim/iter">/sim/iter</a> 同源）；
v014 行小字「预测」= v013 收口时的线性外推预测，仅作留痕、不参与裁决；裁决按判据域 5 节点全域
（15 点），各版最差点见 /sim/op。</p>
{tbl(['版本', '改动', 'typ', 'bcs', 'wcs', '裁决'], tl, 'num')}
<h2>迭代收敛轨迹（判据轴 v2500 · t125−t27 残差）</h2>
{ch_iter}{ch_axis}
<h2>快速入口</h2>
<div class="grid g3">
 <div class="card"><b>设计</b><br><a href="/docs">文档库</a> · <a href="/circuit">电路与参数表</a> ·
   <a href="/layout">版图规划</a> · <a href="/netlist">网表浏览器</a><br>
   <a href="/docs/{sw_report_slug}">SOW-6 全链版图报告</a> ·
   <a href="/phys">版图实证（SOW-3/SOW-6）</a></div>
 <div class="card"><b>仿真</b><br><a href="/sim/op">OP27 工作点</a> · <a href="/sim/sp">sp 频域</a> ·
   <a href="/sim/tran">tran 时域波形</a> · <a href="/sim/device">器件特性</a> ·
   <a href="/sim/linearity">线性度/噪声</a>
   <a href="/dyn">动态指标 ACPR/EVM/LOFT</a> · <a href="/scan">混频器 ACPR 参数扫描</a></div>
 <div class="card"><b>数据</b><br><a href="/data">交付物清单与下载</a> ·
   <span class="muted">全部数据来自本机 /data/workspace，只读挂载，无鉴权</span></div>
</div>
<p class="muted small">数据快照 {meta['built_at']} · 端口 8600 · 服务端渲染，零外部依赖（离线可用）</p>
"""
    return page('总览', body, '/', '一页看完：从规格、架构、电路、版图到晶体管级仿真与结项证据。')


@app.get('/spec', response_class=HTMLResponse)
def spec_page():
    d = S()
    sp = d['spec_table']
    rows = [(f'<b>{r["id"]}</b>', r['metric'], r['req'], r['goal'], r['note']) for r in sp['rows']]
    body = f"""<h1>系统规格（spec v1.3 · 预算与口径冻结）</h1>
<p class="muted">范围：2.4 / 5 / 6 GHz 三频段射频发射通路（基带 I/Q → DAC → 重构滤波 → VGA → 上变频 →
驱动 → PA → 天线口）。不含接收通路、数字基带 MAC/PHY 上层与完整电源方案。方法论：SOW-1 行为级建模，
SOW-2 已在 IHP SG13G2 PDK 晶体管级验证。版本：<b>{sp['version']}</b></p>
<h2>关键系统指标（{sp['n']} 项）</h2>
{tbl(['#', '指标', '规范要求（802.11be）', '本设计目标', '备注'], rows)}
<h2>完整规格原文</h2><div class="card">{md_html('spec.md')}</div>"""
    return page('规格', body, '/spec')


# ---------------------------------------------------------------- 文档
@app.get('/docs', response_class=HTMLResponse)
def docs_index(q: str = Query('')):
    d = S()
    groups = {}
    for doc in d['docs']:
        if q and q not in doc['title'] and q not in doc['name'] and q not in doc['group']:
            continue
        groups.setdefault(doc['group'], []).append(doc)
    body = ['<h1>文档库</h1><p class="muted">全案 Markdown 原文（在线渲染）· 检索：'
            '<input id="q" placeholder="输入关键词回车" value="%s" '
            'oninput="location.href=\'/docs?q=\'+encodeURIComponent(this.value)" '
            'style="background:#101a2b;border:1px solid #24354f;color:#c9d6e8;border-radius:6px;padding:5px 9px">'
            % html.escape(q)]
    for g, items in groups.items():
        body.append(f'<h2>{g}</h2>')
        rows = [(f'<a href="/docs/{it["slug"]}">{it["title"]}</a>',
                 f'<span class="muted small">{it["path"]}</span>',
                 f'{it["head"]} 行', f'{it["chars"]/1024:.1f} KB', it['sha'], it['mtime']) for it in items]
        body.append(tbl(['文档', '路径', '行数', '大小', 'sha256', '更新'], rows))
    return page('文档库', ''.join(body), '/docs')


@app.get('/docs/{slug}', response_class=HTMLResponse)
def doc_page(slug: str):
    d = S()
    doc = next((x for x in d['docs'] if x['slug'] == slug), None)
    if not doc:
        raise HTTPException(404, 'doc not found')
    body = (f'<p class="muted"><a href="/docs">← 文档库</a> · {doc["group"]} · '
            f'{doc["path"]} · {doc["head"]} 行 · sha256 {doc["sha"]}… · {doc["mtime"]} · '
            f'<a href="/raw?p={doc["path"]}">下载原文</a></p>'
            f'<div class="card">{md_html(doc["path"])}</div>')
    return page(doc['title'], body, '/docs')


# ---------------------------------------------------------------- 电路 / 版图
@app.get('/circuit', response_class=HTMLResponse)
def circuit():
    d = S()
    figs = ''.join(
        f'<div class="fig"><a href="/raw?p={f["path"]}" target="_blank">{f["file_svg"]}</a>'
        for f in [])
    gal = ''
    for f in d['figures']:
        gal += (f'<div class="fig"><div>{f["svg_inline"]}</div>'
                f'<div class="cap"><b>{f["title"]}</b> — {f["desc"]}<br>'
                f'<span class="muted small">{f["path"]} · {f["size"]/1024:.1f} KB · '
                f'<a href="/raw?p={f["path"]}" target="_blank">原图 SVG</a></span></div></div>')
    rows = []
    for r in d['params']['rows']:
        rows.append([f'<code>{html.escape(x)}</code>' for x in r])
    hdr7 = ['配置域', '频段', '模块', '参数', '值', '单位', '备注']
    ncol = max(len(r) for r in rows)
    pr = tbl(hdr7[:ncol] if ncol == 7 else [f'列{i}' for i in range(ncol)], rows)
    body = f"""<h1>电路设计（b7e7 出稿 · 组长集成）</h1>
<p class="muted">唯一数据源 = <code>design_circuit/params.csv</code>（budget_check.py 直接读取）；
电路级参数、拓扑与版图规划见 <a href="/docs">文档库</a>。</p>
<h2>电路参数表</h2>{pr}
<h2>图形资产（SVG 内嵌）</h2><div class="grid g2">{gal}</div>"""
    return page('电路', body, '/circuit')


def wjson(rel):
    """工作区 JSON 直读（动态指标页的数据源；页面按 mtime 懒加载，不进 site.json）"""
    p = os.path.join(WS, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8') as f:
        return json.load(f)


@app.get('/scan', response_class=HTMLResponse)
def scan_page():
    """SOW-3 v2.4 · 混频器 ACPR 限制的参数扫描（一次一因子 + 等功率复核）"""
    d = wjson('phys/gilbert/sim/mix_acpr_scan.json')
    if not d or not d.get('phases', {}).get('1'):
        return page('ACPR 参数扫描', '<h2>数据尚未生成</h2><p class="muted">'
                        '<code>python phys/gilbert/sim/mix_acpr_scan.py all</code></p>', '/scan')
    ph = d['phases']['1']
    ph2 = d.get('phases', {}).get('2', {})
    AX = [('gmnx', 'gm 对管尺寸 nx', 'RF 口线性度 ↔ gm 兑换率'),
          ('regm', 'gm 退化 Re (Ω)', '线性 ↑ / gm ↓'),
          ('swnx', 'LO 开关对 nx', '开关锐度 ↔ 电流窃取'),
          ('rd', 'LO 口串阻 Rd (Ω)', 'LO 驱动摆幅 ↔ 开关管 Vbe 摆幅'),
          ('cc', 'LO 耦合 Cc (pF)', 'LO 驱动电平，唯一不加直流功耗的旋钮'),
          ('rl', 'RF 负载 RL (Ω)', '输出摆幅 ↔ 压缩点')]
    BASE = {'gmnx': '3', 'regm': '15', 'swnx': '4', 'rd': '10', 'cc': '10p', 'rl': '45'}

    def num(v):
        try:
            return float(str(v).rstrip('pfΩ'))
        except Exception:
            return None

    def axis_items(ax):
        ks = [k for k, c in ph.items() if c.get('axis') == ax]
        return sorted(ks, key=lambda k: (num(ph[k]['val']) is None, num(ph[k]['val']) or 0))

    base = next((c for c in ph.values() if c.get('is_base')), None)
    B = [f"""<h2>SOW-3 v2.4 · 混频器 ACPR 限制的参数扫描（一次一因子）</h2>
<p class="muted">数据源 <code>{html.escape(d.get('_src',''))}</code>；口径：{html.escape(d.get('_method',''))}<br>
<b>为什么扫这个</b>：v2.3 实测证明混频器是 ACPR 第一限制级（×1 档链出 −27.7 dBc 时混频器出已 −36.9 dBc），
而 spec S6 判据是 ≥45 dBc。本页逐个旋钮问同一个问题：<b>改它能换回几个 dB，代价是什么（增益/电流/摆幅）。</b></p>
<div class="card"><b>读表纪律</b>：各变体在同一 IF 输入电平（×1 档）下跑，<b>增益不同 ⇒ 输出功率不同 ⇒ ACPR 不可直接比</b>。
本页同时给出 ACPR 与输出功率两列；真正的设计处方看 §2 <b>等功率/等线性复核</b>（阶段 2）。<br>
<b>DC 门口径</b>：45 mA 判据线是<b>混频器自身电流</b>（XBI1+XBI2 两条尾流之和，b7e7 口径 typ 44.6 mA），
<b>不是全链 Vcc</b>——实测全链 Vcc = 0.51 A 级（含 LO_BUF+DRV1+DRV2），套错会全表误判；
Vce 门按混频器基线实测值定（开关对 1.186 V、gm 对 0.961 V），不套 drv2 的 1.2 V 线。</div>"""]

    if base:
        B.append('<div class="kpirow">' + ''.join([
            kpi(f"{base['mix']['ACPR1_dBc_mt']:.2f} dBc", '基线 混频器出 ACPR1', f"混频器出 {base['mix']['P_mt_dBm']:.1f} dBm"),
            kpi(f"{base['out']['ACPR1_dBc_mt']:.2f} dBc", '基线 链出 ACPR1', f"链出 {base['out']['P_mt_dBm']:.1f} dBm"),
            kpi(f"{base.get('i_mix_mA', float('nan')):.1f} mA", '基线 混频器 i_mix', f"Vce_sw {base.get('vce_sw_V', 0):.3f} V / Vce_gm {base.get('vce_gm_V', 0):.3f} V"),
        ]) + '</div>')

    # ---- §1 逐轴柱状图 ----
    B.append('<h2>§1 逐轴扫描（混频器出 ACPR1，虚线 = S6 判据 −45 dBc）</h2>')
    for ax, name, hint in AX:
        ks = axis_items(ax)
        if not ks:
            continue
        vals = [ph[k]['mix']['ACPR1_dBc_mt'] for k in ks]
        pw = [ph[k]['mix']['P_mt_dBm'] for k in ks]
        labs = [f"{ph[k]['val']}{' ★' if ph[k].get('is_base') else ''}" for k in ks]
        B.append(charts.bar_chart(
            labs, [{'name': '混频器出 ACPR1 (dBc)', 'values': vals},
                   {'name': '混频器出功率 (dBm)', 'values': pw, 'axis': 2}],
            title=f'{name} —— {hint}', ylabel='ACPR1 (dBc)', ylabel2='混频器出功率 (dBm)',
            hlines=[(-45, 'S6 判据 −45 dBc')], value_fmt='{:.2f}', height=330))

    # ---- ACPR vs 输出功率（暴露混淆） ----
    ser = []
    for i, (ax, name, _) in enumerate(AX):
        ks = axis_items(ax)
        pts = sorted(((ph[k]['mix']['P_mt_dBm'], ph[k]['mix']['ACPR1_dBc_mt']) for k in ks))
        if len(pts) > 1:
            ser.append({'name': name, 'x': [p[0] for p in pts], 'y': [p[1] for p in pts],
                        'markers': True, 'color': charts.PALETTE[i % len(charts.PALETTE)]})
    if ser:
        B.append(charts.line_chart(ser, title='混频器出 ACPR1 vs 输出功率（左下 = 又线性又有功率；同一斜率带 = 只差增益）',
                                    xlabel='混频器出带内功率 (dBm)', ylabel='ACPR1 (dBc)',
                                    height=360, hlines=[(-45, 'S6 判据')]))

    # ---- §1b 全表 ----
    rows = []
    for ax, name, _ in AX:
        for k in axis_items(ax):
            c = ph[k]
            m = c['mix']
            rows.append([name, f"{c['val']}{'（基线）' if c.get('is_base') else ''}",
                         f"{m['P_mt_dBm']:.2f}", f"{m['ACPR1_dBc_mt']:.2f}", f"{m['EVM_dB']:.1f}",
                         f"{m['ripple_dB']:.2f}", f"{m['IM3_edge_dBc']:.2f}", f"{m['cw_dBc']:.2f}",
                         f"{c['out']['ACPR1_dBc_mt']:.2f}", f"{c['out']['P_mt_dBm']:.2f}",
                         f"{c.get('i_mix_mA', float('nan')):.1f}", f"{c.get('vce_sw_V', float('nan')):.3f}",
                         f"{c.get('vce_gm_V', float('nan')):.3f}",
                         'PASS' if c.get('pass_dc') else '待确认'])
    B.append('<h2>§1b 全表（含 DC 健康度）</h2>' + tbl(
        ['旋钮', '值', '混频器出 dBm', '混频器 ACPR1', 'EVM', '纹波', 'IM3@带边', 'LOFT',
         '链出 ACPR1', '链出 dBm', '混频器 i_mix mA', 'Vce_sw', 'Vce_gm', 'DC门'], rows))

    # ---- §2 等功率/等线性处方（summary 由 mix_acpr_scan.py 预算好，避免两处实现漂移） ----
    summ = d.get('summary') or []
    if summ:
        B.append('<h2>§2 等功率 / 等线性处方（这才是给设计岗的数字）</h2>'
                 '<p class="muted">两个工程量：① <b>P_REF（基线 ×1 档混频器输出）处的 ACPR</b>——同功率比线性；'
                 '② <b>ACPR = −45 dBc（S6 判据）时的最大输出功率</b>——这条链能给到多大功率。'
                 '每个候选跑 ×0.5/×1/×2 三档输入得 (Pmt, ACPR) 曲线后插值；'
                 '「外推」= 目标点落在三点区间之外，线性外推，可信度低一档。</p>')
        b0 = next((r for r in summ if r['name'].startswith('baseline')), None)
        rows = []
        for r in summ:
            d1 = r['acpr_at_pref'] - b0['acpr_at_pref'] if b0 else float('nan')
            d2 = r['p_at_m45'] - b0['p_at_m45'] if b0 else float('nan')
            cv = ' · '.join(f'{q[0]:.1f}/{q[1]:.1f}' for q in r['curve'])   # 曲线元组=(Pmt,ACPR,EVM,纹波)
            rows.append([r['name'], r.get('src', ''), cv, f"{r['acpr_at_pref']:.2f}",
                         f"{d1:+.2f}", f"{r.get('evm_at_pref', float('nan')):.1f}",
                         f"{r.get('evm_at_pref', 0) - b0.get('evm_at_pref', 0):+.1f}" if b0 else '—',
                         f"{r['p_at_m45']:.2f}", f"{d2:+.2f}",
                         '是' if r.get('extrapolated') else '否'])
        B.append(tbl(['方案', '曲线来源', '三点 (Pmt dBm/ACPR dBc)', 'P_REF 处 ACPR dBc', 'vs 基线',
                      'P_REF 处 EVM dB', 'ΔEVM', 'ACPR=−45dBc 时最大输出 dBm', 'vs 基线', '外推?'], rows))
    if ph2:
        rows2 = []
        for k, c in sorted(ph2.items()):
            m = c['mix']
            rows2.append([k, f"×{c.get('scale', 1):g}", f"{m['P_mt_dBm']:.2f}", f"{m['ACPR1_dBc_mt']:.2f}",
                          f"{m['ACPR2_dBc']:.2f}", f"{m['EVM_dB']:.1f}", f"{m['ripple_dB']:.2f}",
                          f"{c['out']['ACPR1_dBc_mt']:.2f}", f"{c['out']['P_mt_dBm']:.2f}",
                          f"{c.get('i_mix_mA', float('nan')):.1f}",
                          'PASS' if c.get('pass_dc') else '待确认'])
        B.append('<h3>阶段 2 原始逐档读数</h3>' + tbl(
            ['变体', '输入档', '混频器出 dBm', '混频器 ACPR1', 'ACPR2', 'EVM', '纹波',
             '链出 ACPR1', '链出 dBm', '混频器 i_mix mA', 'DC门'], rows2))
    return page('ACPR 参数扫描', ''.join(B), '/scan')


@app.get('/dyn', response_class=HTMLResponse)
def dyn_page():
    d = wjson('phys/gilbert/sim/dyn_metrics.json')
    if not d:
        return page('动态指标', '<h2>数据尚未生成</h2><p class="muted">'
                        '<code>phys/gilbert/sim/dyn_metrics.py all</code></p>', '/dyn')
    cs = d.get('cases', {})
    mts = [(k, v) for k, v in cs.items() if v.get('kind') == 'mt']
    mts.sort(key=lambda kv: kv[1]['stages']['out']['P_mt_dBm'])
    STG = [('mix', 'MIXER 出'), ('drv1', 'DRV1 出'), ('out', 'DRV2/PA 出')]
    B = []
    cal, calb, lo = cs.get('calorig', {}), cs.get('cal1tone', {}), cs.get('loooff', {})

    B.append(f"""<h2>SOW-3 v2.3 · TX 链动态指标实测：ACPR / EVM / LOFT / OOB 谱廓</h2>
<p class="muted">数据源 <code>{html.escape(d['_src'])}</code>（b7e7 v014 定稿板，<b>器件零改动</b>）；
口径：{html.escape(d['_calib'])}。<br>
激励：IF 端基带 <b>64 音多载波</b>（5…320MHz，间隔 5MHz）经 LO 5.5GHz 上变频 →
射频 5.5GHz±(5…320)MHz = 320MHz 信道的 DSB 表示；相干窗 200ns 整窗使所有谱线正落
Δf=5MHz 栅格，<b>矩形窗零泄漏</b>，逐 bin 幅度即真实正弦幅度 → ACPR/EVM 直读 bin，无需拟合。</p>""")

    # ---- §0 交叉校验 ----
    if cal and calb:
        B.append(f"""<h2>§0 交叉校验（实验可信度门槛）</h2>
{tbl(['读数', 'calorig（SOW-2 原口径复现）', 'cal1tone（B 源激励）', '差'],
     [['链出单音幅度（峰值差分）', f"{cal.get('cal_tone_dBV_peak', 0):.4f} dBV",
       f"{calb.get('cal_tone_dBV_peak', 0):.4f} dBV",
       f"{abs(cal.get('cal_tone_dBV_peak', 0) - calb.get('cal_tone_dBV_peak', 0)):.4f} dB"],
      ['LO 摆幅 @混频口', f"{cal.get('lo_pp_V', 0):.4f} Vpp", f"{calb.get('lo_pp_V', 0):.4f} Vpp", '—'],
      ['频谱杂散底', f"{cal.get('spurious_floor_dBV', 0):.0f} dBV", f"{calb.get('spurious_floor_dBV', 0):.0f} dBV", '—']])}
<p class="muted">同工况下 <b>B 源激励 ≡ 原解析 sin 源</b>（差 {abs(cal.get('cal_tone_dBV_peak', 0)-calb.get('cal_tone_dBV_peak', 0)):.4f} dB）；
杂散底比载波低 70dB → 窗相干性已验证。</p>
<div class="card"><b>口径勘误（SOW-2 链级 CG）</b>：SOW-2 记 fourband 回归 −47.17 dBV / CG −19.22 dB；
本脚本在同一份数据上复跑同一回归得 {cal.get('cal_tone_dBV_peak', 0)-3.98:.2f} dBV（复现 ✓），
而<b>相干 bin 直读</b>为 <b>{cal.get('cal_tone_dBV_peak', 0):.2f} dBV → CG {cal.get('chain_CG_bin_dB', 0):.2f} dB</b>，
差 <b>{cal.get('chain_CG_gap_dB', 0):+.2f} dB</b>。两处来源：①fourband 的 4 个基波取在 ±9/±11MHz（非 ±10MHz），
500ns 窗上与真实 ±10MHz 音不正交，24 频最小二乘把一根本拆两根，系统性低估 3.9dB；
②回归里 cg 用 2·ifamp 而传的是 ifamp=20mV（v014 链板实际 15.8mV），再差 2.05dB。
物理侧自洽：vr 时域包络峰值 14.0mV = 两个边带各 6.89mV ×2。</div>""")

    if lo:
        B.append(f"""<h2>§1 LO 馈通单测（IF 关，仅 LO 驱动）</h2>
<div class="kpirow">{kpi(f"{lo.get('cal_tone_dBm_50R', 0):.2f} dBm", '链出 5.5GHz 馈通（50Ω 差分）', 'IF=0，仅 LO')}</div>
<p class="muted">LO 摆幅 {(cal.get('lo_pp_V') or 0):.3f} Vpp @混频口（SOW-2 记 0.4067 ✓）。</p>""")

    # ---- §2 逐级曲线（x 轴统一用链出功率，便于三级对比） ----
    xs = [m['stages']['out']['P_mt_dBm'] for _, m in mts]
    for field, ylabel, title, hline in (
            ('EVM_dB', 'EVM (dB)', 'EVM vs 链出功率（逐级分解；−38dB 为 802.11 1024-QAM 门限）', -38),
            ('ACPR1_dBc_mt', 'ACPR (dBc)', '邻道 ACPR vs 链出功率（邻道=320MHz 宽，偏置 320~640MHz）', -45),
            ('cw_dBc', 'LOFT (dBc)', 'LO 馈通 LOFT vs 链出功率（5.5GHz CW / 多音带内）', None),
            ('ripple_dB', '带内纹波 (dB pk-pk)', '带内幅频纹波 vs 链出功率（320MHz 内逐音）', None)):
        ser = [{'name': cn, 'x': xs, 'y': [m['stages'][sk][field] for _, m in mts],
                'markers': True, 'color': charts.PALETTE[i % len(charts.PALETTE)]}
               for i, (sk, cn) in enumerate(STG)]
        hl = [(hline, '802.11 门限')] if hline else ()
        B.append(charts.line_chart(ser, title=title, xlabel='链出带内功率 (dBm)', ylabel=ylabel,
                                   height=330, hlines=hl))

    # ---- 带内幅频 + OOB 谱廓 ----
    for tag, m in mts:
        if abs(m['scale'] - 1.0) > 1e-9:
            continue
        A = m.get('A_up_V') or []
        if A:
            B.append(charts.line_chart(
                [{'name': '链出每音幅度（正侧带）', 'x': [(i + 1) * 5 for i in range(len(A))],
                  'y': [v * 1e3 for v in A], 'markers': False},
                 {'name': '镜像侧带', 'x': [(i + 1) * 5 for i in range(len(A))],
                  'y': [v * 1e3 * 1.0 for v in A], 'dash': '5,4', 'markers': False}],
                title=f'带内幅频响应（{tag}，64 音）：320MHz 内起伏 {m["stages"]["out"]["ripple_dB"]:.2f} dB',
                xlabel='距 LO 的频偏 (MHz)', ylabel='每音幅度 (mV pk)', height=320))
    for tag, m in mts[::max(1, len(mts) // 4)]:
        prof = m['stages']['out'].get('profile_dBc') or []
        if not prof:
            continue
        B.append(charts.line_chart(
            [{'name': f'{tag}（链出 {m["stages"]["out"]["P_mt_dBm"]:.1f} dBm）',
              'x': [p[0] for p in prof], 'y': [p[1] for p in prof], 'markers': False}],
            title='带外谱廓（20MHz 分箱，相对带内总功率；带边外第一个箱即再生起点）',
            xlabel='距 LO 的频偏 (MHz)', ylabel='dBc', height=320))

    # ---- 表 ----
    rows = []
    for tag, m in mts:
        for sk, cn in STG:
            s = m['stages'][sk]
            rows.append([f'{tag} (×{m["scale"]:g})', cn, f'{s["P_mt_dBm"]:.2f}', f'{s["EVM_dB"]:.1f}',
                         f'{s["ripple_dB"]:.2f}', f'{s["ACPR1_dBc_mt"]:.2f}', f'{s["ACPR2_dBc"]:.2f}',
                         f'{s["IM3_edge_dBc"]:.2f}', f'{s["cw_dBc"]:.2f}'])
    B.append('<h2>§3 全表</h2>' + tbl(
        ['工况', '级', '带内功率 dBm', 'EVM dB', '纹波 dB', 'ACPR1 dBc', 'ACPR2 dBc', 'IM3@带边 dBc', 'LOFT dBc'],
        rows))
    return page('动态指标', ''.join(B), '/dyn')


@app.get('/phys', response_class=HTMLResponse)
def phys_page():
    d = S()
    ph = d['phys']
    chip_cards = []
    for ch in ph['chips']:
        drc_rows = [(x['name'],
                     badge(x['violations'] == 0, f"零违规 ({x['violations']})", f"{x['violations']} 项违规"),
                     f"{x['runtime_s']}s" if x['runtime_s'] else '—') for x in ch['drc']]
        lvs = ch['lvs'] or {}
        pex_rows = [(f'<b>{n["net"]}</b>', n['layer'], f'{n["r"]:.2f}', f'{n["c"]:.2f}', str(n['npin']))
                    for n in sorted(ch['pex_nets'], key=lambda z: -z['r'])]
        hg = lvs.get('hbt_geom') or {}
        chip_cards.append(f"""<div class="card">
<h2>{html.escape(ch['name'])} <span class="badge {'b-ok' if ch['drc_final'] and ch['drc_final']['violations'] == 0 else 'b-no'}">
{'DRC 零违规' if ch['drc_final'] and ch['drc_final']['violations'] == 0 else 'DRC 有违规'}</span>
 <span class="badge {'b-ok' if lvs.get('match') else 'b-no'}">{'LVS PASS' if lvs.get('match') else 'LVS FAIL'}</span>
 <span class="muted small">{html.escape(ch['ver'])}</span></h2>
<p class="muted">{html.escape(ch['desc'])}</p>
<p>GDS <code>{html.escape(ch['gds'])}</code>（{ch['gds_info']['size'] // 1024 if ch['gds_info'] else '?'} KB）
 · 提取器件 <b>{lvs.get('n_dev', '?')}</b> 个（{html.escape(str(lvs.get('dev_kinds', '')))}）
 · LVS 实测 HBT 几何 we={html.escape(str(hg.get('we', '—')))} le={html.escape(str(hg.get('le', '—')))} Nx={html.escape(str(hg.get('Nx', '—')))}</p>
{tbl(['DRC 轮次', '违规数', 'deck 运行'], drc_rows)}
{tbl(['网', '层', 'R_total (Ω)', 'C_total (fF)', '引脚数'], pex_rows)}
<p class="muted small">报告：
{' · '.join(f'<a href="/raw?p={quote(r["path"])}">{html.escape(os.path.basename(r["path"]))}</a>' for r in ch['reports_info'])}</p>
</div>""")

    # 前/后对拍（两块的增益现算）
    cats, gains, drops = [], [], []
    for ch in ph['chips']:
        if ch['pre_gain'] is None:
            continue
        cats.append(ch['key'])
        drops.append(ch['drop_dB'])
    ch_prepost = charts.bar_chart(
        cats, [{'name': '前仿真电压增益', 'values': [c['pre_gain'] for c in ph['chips'] if c['pre_gain'] is not None],
                'color': '#10b981'},
               {'name': '后仿真（真实版图 PEX）', 'values': [c['post_gain'] for c in ph['chips'] if c['post_gain'] is not None],
                'color': '#f97316'}],
        title='SOW-3 两块实证：前仿真 vs 后仿真电压增益（dB，激励 50mV，口径现算）',
        ylabel='电压增益 (dB)', value_fmt='{:+.2f}', height=320)

    blocks = []
    at = ph['extra'].get('attrib_amp2') or {}
    cases = at.get('cases') or []
    base = next((c for c in cases if c['tag'] == 'nominal'), None)
    solo = [c for c in cases if c['tag'].startswith('solo_')]
    if base and solo:
        # 口径统一：全页一律用【电压增益】= A0(dBV) + 26.02dB（激励 50mV），
        # 与 /phys 其余三张图和判读纪要一致，不在同一页混用 dBV。
        K = 20 * math.log10(1 / 0.05)   # = 26.02dB
        solo_s = sorted(solo, key=lambda c: -c['A0_dB'])
        pre_dBV = (at.get('pre') or {}).get('A0_dB')
        blocks.append(charts.bar_chart(
            [c['tag'][5:] for c in solo_s],
            [{'name': '单网归零后的电压增益', 'values': [c['A0_dB'] + K for c in solo_s], 'color': '#3b82f6'},
             {'name': '标称（全寄生）', 'values': [base['A0_dB'] + K] * len(solo_s), 'color': '#ef4444'}],
            title=f'TX5G_AMP2 单网归零敏感度（其余全保留）· 标称 {base["A0_dB"] + K:+.2f} dB',
            ylabel='电压增益 (dB)',
            hlines=[(pre_dBV + K, '前仿真基线')] if pre_dBV is not None else (),
            value_fmt='{:+.2f}', height=340))
    me = ph['extra'].get('mech_amp2') or {}
    mcases = me.get('cases') or []
    e1 = [c for c in mcases if c['tag'].startswith('emit_x')]
    e2 = [c for c in mcases if c['tag'].startswith('deg_x')]
    e3 = [c for c in mcases if c['tag'].startswith('vss_x')]
    if e1:
        blocks.append(charts.line_chart(
            [{'name': '发射极路径 R ×k → 电压增益', 'x': [c['k_emit'] for c in e1],
              'y': [c.get('gain_dB') for c in e1], 'markers': True},
             {'name': '前仿真基线', 'x': [c['k_emit'] for c in e1],
              'y': [me.get('pre_gain_dB')] * len(e1), 'dash': '5,4', 'markers': False}],
            title=f'机理判定 E1：只缩放发射极路径电阻（×k 从 1 到 0）→ 增益单调回升，'
                  f'电流几乎不动（Ic1 {e1[0].get("Ic1_mA")}→{e1[-1].get("Ic1_mA")} mA）= 小信号阻抗失配，非直流漂移',
            xlabel='发射极路径电阻缩放 ×k', ylabel='电压增益 (dB)', height=320, legend=True,
            xtick_fmt='{:g}'))
    if e2:
        blocks.append(charts.bar_chart(
            [c['tag'] for c in e2],
            [{'name': '电压增益', 'values': [c.get('gain_dB') for c in e2], 'color': '#a855f7'},
             {'name': 'Ic1 (mA)', 'values': [c.get('Ic1_mA') for c in e2], 'color': '#14b8a6',
              'axis': 2}],
            title='机理判定 E2：加大退化电阻 Re（×2/×4/×8）→ 增益单调变差、Ic1 被饿 = 错处方',
            ylabel='增益 (dB)', ylabel2='Ic1 (mA)', height=300))
    opc = ph['extra'].get('opcheck_amp2') or {}
    oc = opc.get('cases') or []
    if oc:
        blocks.append(charts.bar_chart(
            [c['tag'] for c in oc],
            [{'name': 'Ic1 (mA)', 'values': [c.get('Ic1_mA') for c in oc], 'color': '#10b981'},
             {'name': 'Ic2 (mA)', 'values': [c.get('Ic2_mA') for c in oc], 'color': '#f97316'},
             {'name': 'Vce1 (V)（右轴）', 'values': [c.get('Vce1_V') for c in oc], 'color': '#3b82f6',
              'axis': 2}],
            title='直流工作点随归零工况的变化：电流漂移 ≤7.3%（最大工况 zero_emit_all）、'
                  'Vce 全程 >1.2V（无 quasi-sat）→ 排除直流机理',
            ylabel='Ic (mA)', ylabel2='Vce1 (V)', height=300))

    rule_keys = list((ph.get('rules') or {}).keys())
    rule_txt = ph.get('rule_text') or ''
    rule_body = markdown.markdown(rule_txt, extensions=['tables', 'fenced_code']) if rule_txt else ''
    rule_link = ph.get('rule_doc') or {}

    # ---- v2.2：各级实测工作点与回流预算（v014 定稿板 .op 现算 JSON） ----
    v22 = []
    opd = ph['extra'].get('opcheck_drv2') or {}
    l27, lc = opd.get('t27C', {}).get('levels') or {}, opd.get('t-40C', {}).get('levels') or {}
    order = ['drv2', 'lb_lim', 'drv1', 'mix', 'lb_ef']
    cn = {'drv2': 'DRV2/PA (cascode nx=10)', 'lb_lim': 'LO_BUF 限幅对 (nx=4)',
          'drv1': 'DRV1 (nx=6)', 'mix': 'MIXER gm 对 (nx=3)', 'lb_ef': 'LO_BUF EF 输入级 (nx=2)'}
    if l27:
        rows22 = [(f'<b>{html.escape(cn[k])}</b>', f"{l27[k]['ic_mA']:.2f}", f"{l27[k]['Re_ohm']:g}",
                   f"{l27[k]['gm_mS']:.1f}", f"{l27[k]['Ze_ohm']:.3f}",
                   f"<b>≤{l27[k]['budget_ohm']:.3f}</b>",
                   f"≤{lc[k]['budget_ohm']:.3f}" if k in lc else '—',
                   f"{l27[k]['ic_mA']/(l27[k]['gm_mS']*1e-3*0.02585):.2f}")
                  for k in order if k in l27]
        v22.append(f"""<h2>各级发射极回流预算 · v2.2 实测定稿（v014 定稿板 .op 现场取数）</h2>
<p class="muted">数据源 <code>phys/gilbert/sim/opcheck_drv2.py</code>：在 b7e7 的 <b>v014 定稿板原网表</b>上跑
<code>.op</code>，网表逐字不改，只换 <code>.temp</code> 角。<b>gm = ngspice 模型实测小信号跨导</b>，
不是 Ic/VT 理想公式（SG13G2 HBT 理想因子 n = 1.3~1.8，用 Ic/VT 会把预算放宽 15~20%）。</p>
{tbl(['级', 'Ic/边 (mA)', 'Re (Ω)', 'gm 实测 (mS)', 'Ze (Ω)', '预算 0.1×Ze @27℃ (Ω)', '@−40℃ (Ω)', 'n=Ic/(gm·VT)'], rows22)}
<p class="muted small">同时更正两处口径：① DRV2 的 Re 设计值 <b>1.5Ω/边</b>（v014 网表
<code>Re1/Re2</code> 行），v1 准则里的 8.7Ω 是由 gm_eff 反解的错误值，已作废；
② Ze 折算必须用实测 gm。b7e7 11:5xZ 给的 <code>gm=Ic/VT</code> 折算表更严（保守），
签核按<b>两者取小</b>。</p>""")
        v22.append(charts.bar_chart(
            [cn[k].split(' (')[0] for k in order if k in l27],
            [{'name': '预算 @27℃ (Ω)', 'values': [l27[k]['budget_ohm'] for k in order if k in l27], 'color': '#3b82f6'},
             {'name': '预算 @−40℃ (Ω)', 'values': [lc[k]['budget_ohm'] for k in order if k in lc], 'color': '#0ea5e9'}],
            title='R-EMIT-01 签核预算：DRV2/PA 与 LO_BUF 限幅对是最紧两级（取严后 ≤0.078 / ≤0.160 Ω/边）',
            ylabel='发射极回流预算 (Ω/边)', value_fmt='{:.3f}', height=300))

    sc = ph['extra'].get('emit_scan_drv2') or {}
    srows = sc.get('rows') or []
    if srows:
        xs = [r['rp_ohm'] for r in srows]
        v22.append(f"""<h2>DRV2 发射极回流电阻 Rp 的实证扫描（v014 网表 · AC @5.51GHz + op）</h2>
<p class="muted">只在 drv2 两条发射极支路上各串一个 Rp（Rp=0 用 <code>1e-6Ω</code>，不写 0Ω），
其余网表逐字不动。<b>口径更正</b>：Gilbert 在 LO=DC 的 AC 平衡态把差分 IF 映射成共模、差分输出恒 0，
全链 AC 读数无意义（实测 −256dB），故撤掉 mixer、IF 源直驱 DRV1，测
<b>DRV1→DRV2 两级级联增益 Gdd</b>。曲线回答的是：<b>R-EMIT-01 那条 0.078Ω 的线，够不够？</b></p>""")
        v22.append(charts.line_chart(
            [{'name': 'Gdd 两级级联增益 (dB)', 'x': xs, 'y': [r['CG_dB'] for r in srows], 'markers': True},
             {'name': 'ΔGdd vs 零阻 (dB)', 'x': xs, 'y': [r['dCG_dB'] for r in srows], 'markers': True},
             {'name': '−0.5dB 判据线', 'x': [xs[0], xs[-1]], 'y': [-0.5, -0.5], 'dash': '4,4', 'markers': False}],
            title='发射极回流电阻代价：Gdd 随 Rp 单调下降，而 drv2 直流几乎不动 → 又一次证实小信号机理',
            xlabel='Rp（每边发射极回流总阻，Ω，对数轴）', ylabel='Gdd / ΔGdd (dB)',
            height=330, legend=True, xlog=True))
        v22.append(charts.line_chart(
            [{'name': 'DRV2 XQ1 Ic (mA)', 'x': xs, 'y': [r['ic_mA'] for r in srows], 'markers': True},
             {'name': 'gm (mS)', 'x': xs, 'y': [r['gm_mS'] for r in srows], 'markers': True}],
            title='直流侧几乎不动：Rp 加 4000 倍，Ic 只掉 0.6%、gm 掉 0.5% → 增益损失是纯小信号分压',
            xlabel='Rp（Ω，对数轴）', ylabel='mA / mS', height=300, legend=True, xlog=True))
        v22.append(tbl(['Rp/边 (Ω)', 'Gdd (dB)', 'ΔGdd (dB)', 'drv2 Ic (mA)', 'gm (mS)',
                        'Vce (V)', '发射极电压 (V)', 'Re 压降 (mV)'],
                       [(f"{r['rp_ohm']:g}", f"{r['CG_dB']:.3f}", f"<b>{r['dCG_dB']:+.3f}</b>",
                         str(r['ic_mA']), str(r['gm_mS']),
                         str(r['vce_V']), str(r['v_emitter_V']), str(r['dvR_mV'])) for r in srows]))
        bv = sc.get('budget_verdict') or {}
        v22.append(f"""<p class="muted small"><b>签核判据</b>：{html.escape(bv.get('criterion', ''))} →
实测可用上限 <b>Rp ≤ {bv.get('max_rp_ok_ohm')} Ω/边</b>；ΔCG 跌破 −1dB 的起点
{bv.get('rows_below_1db')} Ω/边。</p>""")

    if ph.get('route_plan_text'):
        v22.append(f"""<h2>DRV2/PA 发射极回流的几何处方表</h2>
<p class="muted small">由 <code>phys/gilbert/sim/emit_route_plan.py</code> 从实测工作点算出，
预算 {0.078:.3f}Ω/边 分配为金属 43mΩ / via 23mΩ / 地轨 12mΩ。RSH 为工程估值（PDK 未随附金属层 R/C 表），
thick-metal 实测值待 b7e7 版图侧 PEX 回填。</p>
{markdown.markdown(ph['route_plan_text'], extensions=['tables', 'fenced_code'])}""")

    body = f"""<h1>版图实证（SOW-3 · 真实 GDS → DRC/LVS → PEX → 后仿真）</h1>
<div class="card"><b>SOW-6 全链版图（2026-10-23 现役面锚：mix v35 / drv1 v23 / drv2 v22）</b>：
MIX v35（ntaila 同域已消除 + M4.b 根修 δ=0.100 落地）+ DRV1 v23 + DRV2 v22 全链 GDS。
DRC 现算 <b>{(d.get('sow6', {}).get('drc', {}).get('mix_v35') or {}).get('violations', '—')}
/ {(d.get('sow6', {}).get('drc', {}).get('drv1_v23') or {}).get('violations', '—')}
/ {(d.get('sow6', {}).get('drc', {}).get('drv2_v22') or {}).get('violations', '—')}</b> 项残留
（mix 侧 M1.b 8 条经独立复现 8/8 落 PCell 实例内、0/8 落顶层自画 M1 域内 ⇒ 归 PCell 内部账；<b>M4.b 已清零</b>），
LVS 官方真跑：mix v35×v1g <b>PASS</b>（net_pair 29 Match 29）／drv1 v23 <b>PASS</b>（13/13）／drv2 v22 <b>PASS</b>。
里程碑全景与判读纪要见<a href="/">总览 · SOW-6 区块</a>与
<a href="/docs/{re.sub(r'[^0-9A-Za-z一-鿿]+', '-', 'phys/report/SOW-6_全链版图报告.md').strip('-')}>结项报告 v0.3</a>。</div>
<p class="muted">本页所有数字都由 <code>sitebuild.py</code> 现场解析：DRC 违规数 = KLayout lyrdb 里的
<code>&lt;item&gt;</code> 计数；LVS 状态 = 官方 deck 日志；PEX 逐网 R/C = 后仿真网表注释行；
前/后指标 = ngspice wrdata 首行现算。<b>没有任何手填结论。</b></p>
{ch_prepost}
{''.join(chip_cards)}
<h2>TX5G_AMP2 · 寄生机理（v2.1 脚本化判定）</h2>
<p class="muted">三个判据实验，全部秒级可复现：<code>attrib_amp2.py</code>（逐网/渐进归零）、
<code>mech_amp2.py</code>（单因子缩放）、<code>opcheck_amp2.py</code>（直流工作点）。</p>
{''.join(blocks)}
{''.join(v22)}
<h2>反哺主链的强制准则{'（' + ' / '.join(rule_keys) + '）' if rule_keys else ''}</h2>
<p class="muted small">{html.escape(rule_link.get('path', ''))}（组长 b7a0 发布，{rule_link.get('size', 0)} B）
· 已并入 <code>design_circuit/layout_plan.md</code> §11</p>
{rule_body}
<p class="muted small">负面结论同样留档：Gilbert 混频级 4 种拓扑均未跑出合格乘积，
测量口径与方法已固化 —— <a href="/raw?p={quote('phys/gilbert/report/附_Gilbert混频级试跑记录.md')}">Gilbert 混频级试跑记录</a>。</p>"""
    return page('版图实证', body, '/phys')


@app.get('/layout', response_class=HTMLResponse)
def layout():
    d = S()
    big = next((f for f in d['figures'] if f['name'] == 'floorplan_top.svg'), None)
    gal = ''
    for f in d['figures']:
        if big and f['name'] == big['name']:
            continue
        gal += (f'<div class="fig"><div>{f["svg_inline"]}</div>'
                f'<div class="cap"><b>{f["title"]}</b> — {f["desc"]}</div></div>')
    body = f"""<h1>版图与物理实现（规划级）</h1>
<p class="muted">无 EDA/GDS 交付：以下为规划级布局与拓扑图；DRC/LVS/PEX 与后仿真签核清单见
layout_plan.md §9~10（PDK 到位后执行）。</p>
<div class="fig"><div>{big['svg_inline'] if big else ''}</div>
<div class="cap"><b>{big['title'] if big else ''}</b> — {big['desc'] if big else ''}</div></div>
<div class="grid g2">{gal}</div>
<h2>版图规划全文</h2><div class="card">{md_html('design_circuit/layout_plan.md')}</div>"""
    return page('版图', body, '/layout')


# ---------------------------------------------------------------- 网表
@app.get('/netlist', response_class=HTMLResponse)
def netlist_index(p: str = Query('')):
    if p:
        return netlist_view(p)
    d = S()
    body = ['<h1>网表浏览器</h1><p class="muted">全部晶体管级网表（ngspice-47 / SG13G2 corner 模型）'
            '——在线阅读、语法高亮、按需下载。</p>']
    for g in d['netlists']:
        body.append(f'<h2>{html.escape(g["group"])} <span class="muted small">({g["items"][0]["dir"]})</span></h2>')
        rows = []
        for it in g['items']:
            rows.append((f'<a href="/netlist?p={it["path"]}"><code>{it["name"]}</code></a>',
                         it['lines'], f'{it["size"]/1024:.1f} KB', it['sha'], it['mtime'],
                         f'<a href="/raw?p={it["path"]}">下载</a>'))
        body.append(tbl(['文件', '行数', '大小', 'sha256', '更新', ''], rows))
    return page('网表', ''.join(body), '/netlist')


def netlist_view(p: str):
    path = safe_path(p, ['pdk', 'design_circuit'])
    txt = open(path, encoding='utf-8', errors='replace').read()
    if len(txt) > 400_000:
        txt_head = txt[:400_000]
    else:
        txt_head = txt
    code = highlight_code(txt_head, 'spice')
    n = txt_head.count('\n') + 1
    body = f"""<h1><code>{html.escape(os.path.basename(p))}</code></h1>
<p class="muted"><a href="/netlist">← 网表列表</a> · {html.escape(p)} · {n} 行 ·
<a href="/raw?p={p}">下载原文</a></p>{code}"""
    return page(os.path.basename(p), body, '/netlist')


# ---------------------------------------------------------------- 仿真
@app.get('/sim', response_class=HTMLResponse)
def sim_index():
    d = S()
    op, sp, tr, dv, b1 = d['op27'], d['sp'], d['tran'], d['device'], d['b1']
    m8h = sp.get('stats') or {}
    mix = tr['ext'].get('mix', {})
    cards = [
        ('/sim/op', 'OP27 工作点',
         f'81 deck（3 板 × 27 角）· 判据域 {op["axis_pass"]}/{op["axis_total"]} · '
         f'锚 δ {op["anchor"][0]["delta_mV"]:+}mV · i_vcc {op["spec_iv"]}mA'),
        ('/sim/sp', 'sp 频域全 S 谱',
         f'27 角 × 61 频点（0.1~100G）· eig 带内 {m8h.get("eig_wb_max")} · '
         f'Scc_LO {m8h.get("scc_lo_wb_max")}/{m8h.get("scc_lo_ab_max")}'),
        ('/sim/tran', 'tran 时域波形',
         f'2.5µs 双音：mix CG {mix.get("CG_dB_per_tone")}dB/音 · OIP3 {mix.get("OIP3_dBm")}dBm · '
         f'链级 CG {tr["ext"].get("chain",{}).get("CG_chain_dB")}dB'),
        ('/sim/device', '器件特性 d1',
         f'{dv["n_points"]} 点 corner 网格（typ/bcs/wcs × Vce × Ic）· ft/gm/β'),
        ('/sim/linearity', '线性度 / 噪声 / S（单板）',
         f'{len(b1)} 组 B1 批次数据（typ/t27/v2500）'),
        ('/sim/iter', '迭代路径与判读',
         'v011a→v012→v013→v014 四轮，四步判据逐条对照'),
    ]
    body = '<h1>仿真总览</h1><p class="muted">晶体管级仿真在 IHP SG13G2 开源 PDK + ngspice-47 环境完成；'
    body += ('原始波形与全量结果文件保留在本机，可按需下载。</p><div class="grid g2">')
    for u, t, s in cards:
        body += (f'<div class="card"><a href="{u}"><b>{t}</b></a><br>'
                 f'<span class="muted small">{s}</span></div>')
    body += '</div>'
    return page('仿真', body, '/sim')


@app.get('/sim/op', response_class=HTMLResponse)
def sim_op():
    d = S()
    op = d['op27']
    axis, edge, ivcc, cal = op['axis'], op['edge'], op['ivcc'], op['calib']
    # 判据轴残差：按 corner × 测点分组柱
    cats = list(CRIT_ORDER)
    series = []
    for seg in ('typ', 'bcs', 'wcs'):
        series.append({'name': f'{seg}（t125−t27）',
                       'values': [next((x['d_mV'] for x in axis if x['node'] == nm
                                        and x['corner'] == seg), None) for nm in cats],
                       'color': {'typ': '#3b82f6', 'bcs': '#f97316', 'wcs': '#a855f7'}[seg]})
    ch1 = charts.bar_chart(cats, series, title='判据轴（v2500）t125−t27 尾流电压残差',
                           ylabel='mV', hlines=[(6.4, '判据 +6.4'), (-6.4, '判据 −6.4')],
                           value_fmt='{:+.2f}', height=340)
    # 版本对照（判据轴最差点）
    vs = op['versions']
    vcats = [v['ver'] for v in vs]
    worst = [{'name': '判据轴最大 |残差|',
              'values': [abs(v['axis_worst']['d_mV']) if v['axis_worst'] else None for v in vs],
              'color': '#f97316'}]
    ch2 = charts.bar_chart(vcats, worst, title='四轮迭代：判据轴最大温漂残差（收敛轨迹）',
                           ylabel='mV', hlines=[(6.4, '判据线 6.4mV')], height=300)
    over = [{'name': '判据轴超线点数',
             'values': [v['axis_total'] - v['axis_pass'] for v in vs], 'color': '#ef4444'},
            {'name': '边角域超线点数（备案）',
             'values': [v['edge_total'] - v['edge_pass'] for v in vs], 'color': '#fbbf24'}]
    ch3 = charts.bar_chart(vcats, over, title='超线点数（判据轴 vs 边角备案域）', ylabel='点',
                           height=300)
    # i_vcc：按 corner × vdd（spec temp）
    cats2 = [f'{c}/v{v}' for c in ('typ', 'bcs', 'wcs') for v in (2250, 2500, 2750)]
    iv_series = []
    for tn, col in (('tm40', '#64748b'), ('t27', '#3b82f6'), ('t125', '#ef4444')):
        iv_series.append({'name': f'mix {tn}', 'color': col, 'values': [
            next((x['mA'] for x in ivcc if x['board'] == 'mix' and x['corner'] == c
                  and x['vdd'] == v and x['temp'] == tn), None)
            for c, v in ((c, v) for c in ('typ', 'bcs', 'wcs') for v in (2250, 2500, 2750))]})
    ch4 = charts.bar_chart(cats2, iv_series, title='混频器本体 i_vcc（|I|−200mA 口径）',
                           ylabel='mA', hlines=[(45.0, '45mA 判据线')], height=330)
    # ntail 全角矩阵
    mtx = ''
    for b in ('mix', 'chain', 'lob'):
        rows = [m for m in op['matrix'] if m['board'] == b]
        if not rows:
            continue
        rr = ''
        for m in rows:
            cells = ''.join(('<td class="num ok">%s</td>' if v is not None and 350 <= v <= 360
                             else ('<td class="num no">%s</td>' if v is not None else '<td>—</td>')) % v
                            for v in m['v'])
            rr += f'<tr><th>{m["corner"]}/{m["temp"]}</th>{cells}</tr>'
        mtx += (f'<h3>{rows[0]["label"]} · mix/mi/lb.ntaila（mV，定标窗 350~360）</h3>'
                f'<table><tr><th>corner/temp</th><th class="num">vdd 2250</th>'
                f'<th class="num">vdd 2500</th><th class="num">vdd 2750</th></tr>{rr}</table>')
    anchor_rows = [(a['label'], f'{a["nsens"]:.6f} V', f'{a["delta_mV"]:+.3f} mV',
                    badge(a['pass'], '✓ |δ|<1mV', '✗')) for a in op['anchor']]
    cal_rows = [(c['label'], c['node'], f'{c["v"]:.5f} V', f'{c["dev_mV"]:+.2f} mV',
                 badge(c['in_window'], '窗内', '窗外')) for c in cal]
    tm40 = op['tm40']
    ch5 = charts.line_chart(
        [{'name': f'{x["corner"]}', 'x': [y['vdd'] for y in tm40 if y['corner'] == x['corner']],
          'y': [y['d_mV'] for y in tm40 if y['corner'] == x['corner']],
          'color': {'typ': '#3b82f6', 'bcs': '#f97316', 'wcs': '#a855f7'}[x['corner']]}
         for x in tm40[:3]], title='tm40 − t27 观测项（PTAT 冷角代价，备案不判）',
        xlabel='vdd (mV)', ylabel='mV', height=300)
    body = f"""<h1>OP27 工作点（27 角 × 3 板 = 81 deck）</h1>
<p class="muted">源：<code>{op['csv']['path']}</code>（{op['csv']['size']/1024:.1f} KB，
sha {op['csv']['sha']}…）· 判据四步：①锚回填 ②typ 定标 ③i_vcc 45mA 线 ④t125 温漂 6.4mV 判据线。</p>
<div class="grid g4">
{kpi(f'{op["axis_pass"]}/{op["axis_total"]}', '④ 判据轴温漂全过', f'最差 {op["axis_worst"]["d_mV"]:+}mV（{op["axis_worst"]["corner"]}/{op["axis_worst"]["node"]}）', 'ok')}
{kpi(f'{op["edge_total"]-op["edge_pass"]}/{op["edge_total"]}', '边角域超线（备案）', f'最差 {op["edge_worst"]["d_mV"]:+}mV @ {op["edge_worst"]["corner"]}/v{op["edge_worst"]["vdd"]} · 拍板划 dcvr')}
{kpi(f'{op["spec_iv"]} mA', '③ i_vcc 规格点', 'mix typ/t27/v2500，45mA 线内')}
{kpi(f'{op["anchor"][0]["delta_mV"]:+.3f} mV', '① 锚 δ（nsens−0.8359）', '三板逐位一致')}
</div>
<h2>② typ 定标（0.350~0.360V 窗）</h2>{tbl(['板', '节点', '实测', '相对 0.35 线', '判定'], anchor_rows + cal_rows)}
<h2>④ 温漂残差</h2>{ch1}{ch2}{ch3}{ch5}
<h2>③ i_vcc 全角</h2>{ch4}
<h2>ntail 全角矩阵</h2>{mtx}
<h2>版本对照明细</h2>
{tbl(['版本', 'deck 数', '改动', '判据轴（v2500）', '边角域（v2250/v2750，备案）', '规格点 ntail min', '规格点 i_vcc'],
     [(f'<b>{v["ver"]}</b>', v['n_decks'], v['note'],
       badge(v['axis_pass'] == v['axis_total'],
             f'{v["axis_pass"]}/{v["axis_total"]} 过（max {v["axis_worst"]["d_mV"]:+.2f}mV）',
             f'{v["axis_total"]-v["axis_pass"]}/{v["axis_total"]} 超线（max {v["axis_worst"]["d_mV"]:+.2f}mV）'),
       f'{v["edge_pass"]}/{v["edge_total"]} 过（max {v["edge_worst"]["d_mV"]:+.2f}mV）',
       f'{v["spec"].get("mix",{}).get("ntail_min_mV")} mV',
       f'{v["spec"].get("mix",{}).get("ivcc_mA")} mA') for v in vs])}
<p class="muted small">判据域口径：5 测点（mix.ntaila / chain.mi.ntaila / chain.lb.ntaila / chain.lb.ntailb /
lob.ntaila）× 3 corner = 15 点，v2500 为判据轴；v2250/v2750 划 dcvr 备案域（30 点）。</p>"""
    return page('OP27', body, '/sim')


CRIT_ORDER = ['mix.ntaila', 'chain.mi.ntaila', 'chain.lb.ntaila', 'chain.lb.ntailb', 'lob.ntaila']


@app.get('/sim/sp', response_class=HTMLResponse)
def sim_sp(deck: str = Query('')):
    d = S()
    sp = d['sp']
    keys = list(sp['series'])
    deck = deck if deck in keys else ('typ/t27/v2500' if 'typ/t27/v2500' in keys else keys[0])
    ser = sp['series'][deck]
    meta = next((x for x in sp['decks'] if x['name'] == deck), None)
    plots = ''
    for pr in ser['pairs']:
        plots += (f'<h3>{pr["label"]}</h3>' +
                  charts.line_chart([{'name': f'{deck} · {pr["key"]}', 'x': ser['freq'],
                                      'y': pr['y'], 'markers': False}],
                                    title=f'{pr["key"]} 幅度 (dB) vs 频率', xlabel='频率 (GHz)',
                                    ylabel='|S| (dB)', xlog=True, height=300, legend=False))
    nav = ' · '.join(f'<a href="/sim/sp?deck={k}">{k}</a>' for k in keys)
    m8 = sp['m8']
    h = sp['stats']
    stat_rows = [(k, v) for k, v in h.items() if not isinstance(v, dict)]
    body = f"""<h1>sp 频域（27 角 × 61 频点 · 全 S 复数谱）</h1>
<p class="muted">deck 选择：{nav}　·　当前 <b>{deck}</b>
{'（' + meta['path'] + '，' + str(meta['size']//1024) + ' KB）' if meta else ''}</p>
<div class="card"><b>M8 终审（SOW-2 口径 B = 参考绝对）</b>
{tbl(['项', '值'], [(html.escape(str(k)), html.escape(str(v)[:400])) for k, v in stat_rows])}
</div>{plots}
<p class="muted small">端口定义（gen_r2sp.py）：1=nifp 2=nifn 3=nlop 4=nlon 5=nrfp 6=nrfn；
频点 0.1GHz→100GHz dec 20（61 点）。LO 半端口强互耦，单端口 Rollett 口径失真，混合模口径为准。</p>"""
    return page('sp', body, '/sim')


@app.get('/sim/tran', response_class=HTMLResponse)
def sim_tran(which: str = Query('mix'), win: str = Query('zoom'), vec: str = Query('')):
    d = S()
    tr = d['tran'][which if which in ('mix', 'chain') else 'mix']
    ext = d['tran']['ext']
    vecs = [v['vec'] for v in tr['zoom']['v']]
    sel = [v for v in vecs if not vec or v in vec.split(',')]
    plots = ''
    for v in sel:
        if win == 'zoom':
            y = next(x['y'] for x in tr['zoom']['v'] if x['vec'] == v)
            xs = tr['zoom']['t']
            title = f'{v} 时域波形（zoom 200~260ns，5.5GHz 载波可见）'
        else:
            env = next(b['bins'] for b in tr['env'] if b['vec'] == v)
            xs = [b['t'] for b in env]
            y = [b['mean'] for b in env]
            title = f'{v} 包络均值（全窗 60ns~2.5µs，150 桶）'
        plots += charts.line_chart([{'name': v, 'x': xs, 'y': y, 'markers': False}],
                                   title=title, xlabel='时间 (ns)', ylabel='电压 (V)',
                                   height=300, legend=False, width=900)
    links = ' · '.join(
        f'<a href="/sim/tran?which={w}&win={win}">{w}</a>' for w in ('mix', 'chain'))
    wlinks = ' · '.join(f'<a href="/sim/tran?which={which}&win={w}">{w}</a>' for w in ('zoom', 'full'))
    vlinks = ' '.join(f'<a href="/sim/tran?which={which}&win={win}&vec={v}">{v}</a>' for v in vecs)
    m = ext.get(which, {})
    rows = []
    for k, v in m.items():
        if isinstance(v, dict):
            rows.append((f'<code>{k}</code>', ' '.join(
                f'<span class="pill">{kk}: {vv}</span>' for kk, vv in list(v.items())[:8])))
        else:
            rows.append((f'<code>{k}</code>', str(v)))
    body = f"""<h1>tran 时域（2.5µs · IF 9/11MHz 双音 · LO 5.5GHz）</h1>
<p class="muted">源：<code>{tr['file']['path']}</code>（{tr['file']['size']/1e6:.0f} MB 原始波形，
sha {tr['file']['sha']}…）· deck：<code>{tr['deck']}</code>。板：{links}　窗口：{wlinks}</p>
<div class="grid g2"><div class="card">{plots}</div>
<div class="card"><b>提取读数（ext v2.1，判读口径 [60,560]ns）</b>
{tbl(['项', '值'], rows)}</div></div>
<p class="muted small">向量：{vlinks}</p>
<p class="muted small">{m.get('_caveat', '')}</p>"""
    return page('tran', body, '/sim')


@app.get('/sim/device', response_class=HTMLResponse)
def sim_device(vce: str = Query('1.2')):
    d = S()
    dv = d['device']
    try:
        vcef = float(vce)
    except ValueError:
        vcef = 1.2
    colors = {'typ': '#3b82f6', 'bcs': '#f97316', 'wcs': '#a855f7'}
    series = []
    for c, rows in dv['series'].items():
        pts = [r for r in rows if abs(r['vce'] - vcef) < 1e-6]
        series.append({'name': c, 'color': colors.get(c), 'markers': True,
                       'x': [r['ic_mA'] for r in pts], 'y': [r['ft_GHz'] for r in pts]})
    ch1 = charts.line_chart(series, title=f'fT vs Ic（Vce = {vcef}V，nx=4 HBT）',
                            xlabel='Ic (mA)', ylabel='fT (GHz)', xlog=True, ylog=True, height=360)
    series2 = []
    for c, rows in dv['series'].items():
        pts = [r for r in rows if abs(r['vce'] - vcef) < 1e-6]
        series2.append({'name': c, 'color': colors.get(c), 'markers': True,
                        'x': [r['ic_mA'] for r in pts], 'y': [r['gm_mS'] for r in pts]})
    ch2 = charts.line_chart(series2, title=f'gm vs Ic（Vce = {vcef}V）', xlabel='Ic (mA)',
                            ylabel='gm (mS)', xlog=True, ylog=True, height=340)
    series3 = []
    for c, rows in dv['series'].items():
        pts = [r for r in rows if abs(r['vce'] - vcef) < 1e-6]
        series3.append({'name': c, 'color': colors.get(c), 'markers': True,
                        'x': [r['ic_mA'] for r in pts], 'y': [r['beta'] for r in pts]})
    ch3 = charts.line_chart(series3, title=f'β vs Ic（Vce = {vcef}V）', xlabel='Ic (mA)',
                            ylabel='β', xlog=True, height=320)
    vlinks = ' · '.join(f'<a href="/sim/device?vce={v}">Vce={v}</a>'
                        for v in (0.6, 1.2, 1.8, 2.4))
    decl = dv['declarations']
    body = f"""<h1>器件特性（IHP SG13G2 HBT · d1 corner 网格）</h1>
<p class="muted">{dv['n_points']} 点（3 corner × Vce 网格 × Ic 网格），源
<code>{dv['file']['path']}</code>。Vce：{vlinks}</p>
{ch1}{ch2}{ch3}
<div class="card"><b>口径声明</b><pre>{html.escape(json.dumps(decl, ensure_ascii=False, indent=1))}</pre></div>"""
    return page('器件', body, '/sim')


@app.get('/sim/linearity', response_class=HTMLResponse)
def sim_lin():
    d = S()
    b1 = d['b1']
    body = ['<h1>线性度 / 噪声 / S 参数（B1 单板批次 · typ/t27/v2500）</h1>'
            '<p class="muted">组长侧 ngspice-47 单板扫描；与 SOW-2 三板级 OP/sp/tran 互补。</p>']
    order = ['b1_m1', 'b1_m2', 'b1_lobuf_l1', 'b1_m7', 'b1_lobuf_l7', 'b1_m4', 'b1_lobuf_l8']
    for k in order + [x for x in b1 if x not in order]:
        if k not in b1:
            continue
        it = b1[k]
        pts = it['points']
        if it['kind'] == 'lobuf_lin':
            ch = charts.line_chart(
                [{'name': '输出差分摆幅', 'x': [p['x'] for p in pts], 'y': [p['out_pp'] for p in pts],
                  'markers': True}, {'name': '输入差分摆幅', 'x': [p['x'] for p in pts],
                                     'y': [p['in_pp'] for p in pts], 'dash': '4,3', 'markers': True}],
                title='LO 缓冲 差分摆幅 vs 输入幅值', xlabel='LO 输入幅值 (mV)', ylabel='差分峰峰 (V)',
                height=300)
            ch2 = charts.line_chart([{'name': 'HD2', 'x': [p['x'] for p in pts],
                                      'y': [p['y2'] for p in pts], 'markers': True}],
                                   title='二次谐波 HD2 vs 输入幅值', xlabel='LO 输入幅值 (mV)',
                                   ylabel='HD2 (dBc)', height=280)
        elif it['kind'] == 'mix_cg':
            ch = charts.line_chart([{'name': 'CG 每音', 'x': [p['x'] for p in pts], 'y': [p['y'] for p in pts],
                                     'markers': True}],
                                   title='混频器 转换增益 vs LO 幅值', xlabel='LO 幅值 (mV)',
                                   ylabel='CG (dB)', height=300)
            ch2 = charts.line_chart([{'name': 'Pout', 'x': [p['x'] for p in pts], 'y': [p['y2'] for p in pts],
                                      'markers': True}],
                                   title='混频器 每音输出功率 vs LO 幅值', xlabel='LO 幅值 (mV)',
                                   ylabel='Pout (dBm)', height=280)
        elif it['kind'] == 'mix_if':
            ch = charts.line_chart([{'name': 'Pout', 'x': [p['x'] for p in pts], 'y': [p['y'] for p in pts],
                                     'markers': True}],
                                   title='混频器 输出功率 vs IF 幅值', xlabel='IF 幅值 (mV)',
                                   ylabel='Pout (dBm)', height=300)
            ch2 = ''
        elif it['kind'] == 'noise':
            ch = charts.line_chart([{'name': '输出噪声 PSD', 'x': [p['x'] for p in pts], 'y': [p['y'] for p in pts],
                                     'markers': False}],
                                   title='输出噪声谱密度', xlabel='频率 (Hz)', ylabel='dBV/√Hz',
                                   xlog=True, height=320)
            ch2 = ''
        elif it['kind'] == 'sparam':
            sers = []
            pk = it.get('pair_keys', [])[:6]
            for i, key in enumerate(pk):
                sers.append({'name': key, 'x': [p['x'] for p in pts], 'y': [p[key] for p in pts],
                             'color': charts.PALETTE[i % len(charts.PALETTE)], 'markers': False})
            ch = charts.line_chart(sers, title='S 参数幅度 vs 频率', xlabel='频率 (Hz)',
                                   ylabel='|S| (dB)', xlog=True, height=340)
            ch2 = ''
        else:
            def _flat(v):
                if isinstance(v, (dict, list, tuple)):
                    return html.escape(json.dumps(v, ensure_ascii=False)[:220])
                return html.escape(str(v))
            ch = (tbl(list(pts[0].keys()), [[_flat(v) for v in p.values()] for p in pts])
                  if pts else '')
            ch2 = ''
        body.append(f'<h2>{html.escape(it["title"])} <span class="muted small">'
                    f'{html.escape(it["file"]["path"])}</span></h2>'
                    f'<p class="muted">{html.escape(it["desc"])}</p>{ch}{ch2}')
    return page('线性度', ''.join(body), '/sim')


@app.get('/sim/iter', response_class=HTMLResponse)
def sim_iter():
    d = S()
    vs = d['op27']['versions']
    cats = [v['ver'] for v in vs]
    groups = []
    for i, seg in enumerate(('typ', 'bcs', 'wcs')):
        groups.append({'name': seg, 'color': charts.PALETTE[i],
                       'values': [next((x['d_mV'] for x in v['axis'] if x['node'] == 'mix.ntaila'
                                        and x['corner'] == seg), None) for v in vs]})
    ch = charts.bar_chart(cats, groups, title='mix.ntaila t125−t27 残差：四轮迭代（判据轴 v2500）',
                          ylabel='mV', hlines=[(6.4, '+6.4'), (-6.4, '−6.4')], value_fmt='{:+.2f}',
                          height=340)
    rows = [(f'<b>{it["ver"]}</b>', it['change'], badge('全过' in it['verdict'], 'PASS', '—'),
             it['verdict'], it['note'],
             (f'<span class="muted small">{it["src"]} · 判据域 '
              f'{it["axis_pass"]}/{it["axis_total"]} · 最差点 {it.get("worst5") or "—"}</span>'))
            for it in d['iteration']]
    vrows = [(f'<b>{v["ver"]}</b>', v['note'],
              f'{v["axis_total"]-v["axis_pass"]}/{v["axis_total"]} 超线（max {v["axis_worst"]["d_mV"]:+.2f}mV）',
              f'{v["edge_total"]-v["edge_pass"]}/{v["edge_total"]} 超线（max {v["edge_worst"]["d_mV"]:+.2f}mV）',
              f'{v["spec"].get("mix",{}).get("ntail_min_mV")} mV',
              f'{v["spec"].get("mix",{}).get("nsens_V")} V',
              f'{v["spec"].get("mix",{}).get("ivcc_mA")} mA') for v in vs]
    body = f"""<h1>迭代路径与判读</h1>
<p class="muted">SOW-2 OP27 温漂轴四轮迭代：v011a-r2 → v012 → v013 → v014（单参数收口，结项）。</p>
{ch}
{tbl(['版本', '改动', '状态', '裁决', '机理/备注', '来源'], rows)}
{tbl(['版本', '改动', '判据轴超线', '边角超线', '规格点 ntail min', 'nsens', 'i_vcc'], vrows)}
<p class="muted small">判读纪要全文见 <a href="/docs">文档库 · 判读纪要</a>（含口径拍板 B 口径复合判据）。</p>"""
    return page('迭代', body, '/sim')


# ---------------------------------------------------------------- 数据
@app.get('/data', response_class=HTMLResponse)
def data_page():
    d = S()
    rows = [(f'<b>{a["title"]}</b>', f'<code>{a["path"]}</code>',
             f'{a["size"]/1024:.1f} KB' if a['size'] < 1e6 else f'{a["size"]/1e6:.1f} MB',
             a['sha'], a['mtime'], f'<a href="/raw?p={a["path"]}">下载</a>') for a in d['artifacts']]
    body = f"""<h1>交付物清单（{len(rows)} 项）</h1>
<p class="muted">全部文件位于本机 <code>/data/workspace</code>，WebUI 只读挂载；点击可下载原文。</p>
{tbl(['交付物', '路径', '大小', 'sha256', '更新', ''], rows)}
<p class="muted small">快照时间 {d['meta']['built_at']} · 数据管线
<code>webui/sitebuild.py</code>（扫描全案 → <code>site.json</code>）。</p>"""
    return page('数据', body, '/data')


@app.get('/tree', response_class=HTMLResponse)
def tree_page():
    """全案文件树（仅交付白名单目录；绝不出现凭据/密钥/同伴信箱等非交付物）。"""
    roots = ['pdk/sim', 'pdk/SOW-2_结项报告_v011a-r2.md', 'design_circuit', 'sim_report', 'research',
             'phys/report', 'phys/top',
             'spec.md', 'architecture.md', 'final_report.md', 'integration_review.md',
             'SOW_电路设计.md', 'SOW_仿真验证.md']
    skip_names = {'__pycache__', '.git', 'models', 'ngroot', 'debs', 'bin', 'd1_batch', 'd1_batch2',
                  'd1_mc', 'd1_p0', 'h21_', 'logs', 'raw_r2sp', 'raw_r2tran', 'decks_r2',
                  'decks_r2abs', 'decks_r2sp', 'decks_r2tran', 'decks_is0scan', 'decks_r2_v012',
                  'decks_r2_v013', 'decks_r2_v014', 'logs_r2', 'logs_r2abs', 'logs_r2sp',
                  'logs_r2tran', 'logs_r2_v012', 'logs_r2_v013', 'logs_r2_v014', 'orig_v091_bak'}
    max_n = 320

    def size_of(pth):
        try:
            n = os.path.getsize(pth)
            return f'{n/1e6:.1f} MB' if n >= 1e6 else f'{n/1024:.1f} KB'
        except Exception:
            return ''

    lines, count = [], 0

    def walk(rel, depth=0):
        nonlocal count
        full = os.path.join(WS, rel)
        if count > max_n or depth > 4:
            return
        if os.path.isfile(full):
            count += 1
            link = (f'<a href="/raw?p={rel}">{os.path.basename(rel)}</a>'
                    if safe_ok(rel) else html.escape(os.path.basename(rel)))
            lines.append([f'<span class="muted">{html.escape(rel.rsplit("/", 1)[0] if "/" in rel else "")}</span>',
                          f'<code>{link}</code>', f'{size_of(full)}'])
            return
        try:
            entries = sorted(os.listdir(full))
        except Exception:
            return
        lines.append([f'<b>{html.escape(rel)}/</b>', '', ''])
        for e in entries:
            if e in skip_names or e.startswith('.'):
                continue
            walk(rel.rstrip('/') + '/' + e, depth + 1)

    def safe_ok(rel):
        try:
            safe_path(rel, ALLOW_ROOTS)
            return True
        except Exception:
            return False

    for r in roots:
        walk(r)
    body = f"""<h1>全案文件树（交付白名单）</h1>
<p class="muted">仅列交付物目录（pdk/sim 仿真资产、design_circuit 电路与版图、sim_report、research 与顶层文档）；
凭据、信箱、缓存、批量 deck/原始波形等非展示资产已排除（本页与 /raw 取件同白名单口径）。共 {count} 个文件。</p>
{tbl(['目录', '文件', '大小'], lines)}
"""
    return page('文件树', body, '/docs')


ALLOW_ROOTS = ['pdk', 'design_circuit', 'sim_report', 'spec.md', 'architecture.md',
               'final_report.md', 'integration_review.md', 'research', 'outbox_files',
               'phys/gilbert/report', 'phys/gilbert/sim', 'phys/report', 'phys/top',
               'phys/sow6_run/run_v2/gds']   # 2026-10-17: +SOW-6 纪要族/版图 GDS 取件


@app.get('/raw')
def raw(p: str = Query(...)):
    path = safe_path(p, ALLOW_ROOTS)
    if not os.path.isfile(path):
        raise HTTPException(404, 'not found')
    return FileResponse(path, filename=os.path.basename(path))


@app.get('/healthz', response_class=PlainTextResponse)
def healthz():
    d = S()
    return f'ok docs={len(d["docs"])} built={d["meta"]["built_at"]}'


if __name__ == '__main__':
    import uvicorn
    port = int(os.environ.get('WEBUI_PORT', '8600'))
    uvicorn.run(app, host='0.0.0.0', port=port, log_level='warning')
