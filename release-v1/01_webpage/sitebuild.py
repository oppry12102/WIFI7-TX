#!/usr/bin/env python3
# sitebuild.py —— WiFi7-TX WebUI 数据构建：扫描 /data/workspace 全案交付物，
# 抽取结构化数据集 -> webui/data/site.json（服务端渲染用）
# 用法: python3 webui/sitebuild.py [--force]
import csv
import glob
import hashlib
import json
import math
import os
import re
import sys
import time

WS = '/data/workspace'
OUT = os.path.join(WS, 'webui', 'data', 'site.json')

# ---------------------------------------------------------------- 基础工具


def sha256(path, limit=None):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def finfo(path, rel=True):
    p = path if os.path.isabs(path) else os.path.join(WS, path)
    st = os.stat(p)
    return {
        'path': os.path.relpath(p, WS) if rel else p,
        'size': st.st_size,
        'mtime': time.strftime('%Y-%m-%d %H:%M', time.gmtime(st.st_mtime)),
        'sha': sha256(p)[:12],
    }


def load_json(p):
    with open(os.path.join(WS, p), encoding='utf-8') as f:
        return json.load(f)


def r4(x, n=4):
    try:
        return round(float(x), n)
    except Exception:
        return x


# ---------------------------------------------------------------- 文档清单
DOC_GROUPS = [
    ('顶层规格与报告', ['spec.md', 'architecture.md', 'final_report.md']),
    ('评审与任务书', ['integration_review.md', 'SOW_电路设计.md', 'SOW_仿真验证.md']),
    ('动态指标与 ACPR（v2.3/v2.4）',
     ['phys/gilbert/report/SOW-3_v2.3_TX链动态指标_ACPR_EVM_LOFT.md',
      'phys/gilbert/report/SOW-3_v2.4_混频器ACPR参数扫描.md']),
    ('SOW-4 级间匹配 v015（组长）',
     ['pdk/sim/r2run/判读纪要_v015_SOW4_2026-10-16.md',
      'pdk/openvaf/OSDI整链验证纪要_2026-10-16.md']),
    ('电路设计（b7e7）', ['design_circuit/design_circuit.md', 'design_circuit/wifi7_tx_circuit_sow1.md',
                          'design_circuit/layout_plan.md']),
    ('版图准则与实证（组长）', ['design_circuit/HBT级版图准则_发射极路径与地轨回流_v1.md',
                              'design/回填_SG13G2_via_EM_20261016.md',
                              'phys/gilbert/report/SOW-3_v2_TX5G_AMP2_版图实证.md',
                              'phys/gilbert/report/SOW-3_v2.1_TX5G_AMP2_机理判定.md',
                              'phys/gilbert/report/附_Gilbert混频级试跑记录.md',
                              'phys/report/SOW-3_版图实证报告.md']),
    ('SOW-6 全链版图（组长·2026-10-17）',
     ['phys/report/SOW-6_全链版图报告.md',
      'phys/top/判读纪要_v19修复代跑轮_2026-10-17.md',
      'phys/top/判读纪要_E回流链断路四方实锤_2026-10-17.md',
      'phys/top/判读纪要_drv1LVS立照_bb1验证点_2026-10-17.md',
      'phys/top/判读纪要_deck4数校准_桥元素实锤_2026-10-17.md',
      'phys/top/判读纪要_LVS粘连三刀二分_幻影焊判决_2026-10-17.md',
      'phys/top/判读纪要_LVS粘连三轮排障_v2b口径_2026-10-17.md',
      'phys/top/判读纪要_LVSsch对拍首跑_2026-10-17.md',
      'phys/top/判读纪要_LVS首跑net_only_BJT端子粘连排查_2026-10-17.md',
      'phys/top/判读纪要_v18补环代跑轮_2026-10-17.md',
      'phys/top/判读纪要_Q12代跑v17轮_2026-10-17.md',
      'phys/top/判读纪要_Q11代跑v16轮_2026-10-17.md',
      'phys/top/判读纪要_Q10代跑v27轮_增补_定版收讫_2026-10-17.md',
      'phys/top/判读纪要_Q10代跑v27轮_2026-10-17.md',
      'phys/top/判读纪要_Q9代跑v26轮_2026-10-17.md',
      'phys/top/判读纪要_Q8代跑v25轮_2026-10-17.md',
      'phys/top/判读纪要_M2M3代跑v24全链_2026-10-17.md',
      'phys/top/判读纪要_M3接收与八项回执_2026-10-17.md',
      'phys/top/判读纪要_Q4注释层与Rsheet真值_2026-10-17.md',
      'phys/top/判读纪要_lib13g2v2_guardring_keepout_2026-10-17.md',
      'outbox_files/design/sow6/knife_骑体对照表与指派定律_v2_2026-10-17.md',
      'outbox_files/design/sow6/M4顶层_设计输入预案_v0.2.md',
      'phys/top/单元几何真值表_v1.1.md',
      'phys/top/probe_viastack_阵列外推_v22_2026-10-17.md',
      'design_circuit/HBT级版图准则_v1.3_b7a0注记.md',
      'design_circuit/HBT级版图准则_v1.2_b7e7.md',
      'pdk/sim/r2run/判读纪要_sow6m5_typ基线_2026-10-17.md']),
    ('PDK 与结项（组长）', ['pdk/SOW-2_结项报告_v011a-r2.md',
                          'pdk/sim/v013_1/V0131_归档与v014血缘核验_2026-10-16.md']),
    ('判读纪要（组长）', ['pdk/sim/r2run/判读纪要_v011a_r2_快验与OP27_2026-10-16.md',
                          'pdk/sim/r2run/判读纪要_v012_OP_2026-10-16.md',
                          'pdk/sim/r2run/判读纪要_v013_OP_2026-10-16.md',
                          'pdk/sim/r2run/判读纪要_v014_OP_2026-10-16.md',
                          'pdk/sim/r2run/口径拍板_B口径复合判据_2026-10-16.md']),
    ('调研与工程评估', ['research/EDA_RFIC_WiFi7TX_调研报告_2026-10-15.md',
                        'research/PDK_SG13G2_落地评估_2026-10-16.md']),
]

FIG_TITLES = {
    'floorplan_top.svg': ('顶层 Floorplan', '芯片顶层布局规划：TX 链沿天线口方向排布，LO 分配树居中，供电域隔离'),
    'power_isolation.svg': ('电源域与隔离', '模拟/数字/射频三域供电与隔离带，衬底与 well 划分'),
    'lo_distribution.svg': ('LO 分配树', '本振分配：LO_BUF → 混频器/驱动级，阻抗匹配与隔离电阻'),
    'schematic_tx_chain.svg': ('TX 模拟链路全图', '基带 I/Q → VGA → Gilbert 混频器 → DRV → PA → 天线口'),
    'schematic_mixer.svg': ('混频器拓扑', 'Gilbert 双平衡无源混频器：尾流管/电感退化/双臂 Rd 去耦'),
    'schematic_pa.svg': ('PA 输出级', '驱动级 + 功率放大输出级，匹配网络与偏置链'),
}

NETLIST_SETS = [
    ('v015 草案（SOW-4 级间匹配四件套）', 'pdk/sim/v015'),
    ('v014 定稿（SOW-2 终态）', 'pdk/sim/v014'),
    # v013 有两版：初版（.lib 用单引号）与 v013.1（引号归一）。v014 是从 **v013.1** patch 出来的，
    # 且 v014 终态 LO 板原件 = v013.1 的 lobuf（sha 079a1293…），所以溯源必须能读到 v013.1。
    # （b7e7 2026-10-16 09:55Z WebUI 校核①；组长已取件归档并独立复跑 patch 验过血缘，见 v013_1/ 核验记录）
    ('v013.1 定稿（v014 实际基线）', 'pdk/sim/v013_1'),
    ('v013 初版 / v012 中间版（仅历史）', 'pdk/sim/v013'),
    ('v011a-r2 投件主版', 'pdk/sim/sow2/v011a_r2_submit'),
    ('组长代跑主版（v011a-r2）', 'pdk/sim/r2run'),
    ('b7e7 出稿（SOW-2 TX5G）', 'design_circuit/sow2_tx5g'),
]


def build_docs():
    docs = []
    for gname, paths in DOC_GROUPS:
        for rel in paths:
            p = os.path.join(WS, rel)
            if not os.path.exists(p):
                continue
            txt = open(p, encoding='utf-8').read()
            title = rel.split('/')[-1]
            m = re.search(r'^#\s+(.+)$', txt, re.M)
            if m:
                title = m.group(1).strip()
            d = finfo(rel)
            d.update(group=gname, title=title, name=os.path.basename(rel),
                     slug=re.sub(r'[^0-9A-Za-z一-鿿]+', '-', rel).strip('-'),
                     head=len(txt.splitlines()), chars=len(txt))
            docs.append(d)
    return docs


def build_netlists():
    out = []
    for gname, d in NETLIST_SETS:
        root = os.path.join(WS, d)
        if not os.path.isdir(root):
            continue
        items = []
        for fn in sorted(os.listdir(root)):
            if not fn.endswith('.sp'):
                continue
            p = os.path.join(root, fn)
            f = finfo(os.path.relpath(p, WS))
            f['lines'] = sum(1 for _ in open(p, encoding='utf-8', errors='replace'))
            f['name'] = fn
            f['dir'] = d
            items.append(f)
        if items:
            out.append({'group': gname, 'items': items})
    return out


# ---------------------------------------------------------------- OP27 工作点
BOARD_COLS = {
    'mix': ['ntaila', 'ntailb', 'nifbias', 'nsens', 'nvtop', 'nswa', 'nswb', 'ivcc'],
    'lob': ['ntaila', 'ntailb', 'nbias1', 'nbias2', 'nsens', 'nvtop', 'ivcc'],
    'chain': ['mi.ntaila', 'mi.ntailb', 'lb.ntaila', 'lb.ntailb', 'nifbias', 'nsens', 'ivcc'],
}
BOARD_IV_EXTRA = {'mix': 200.0, 'lob': 0.0, 'chain': 200.0}   # mA，本体口径扣除镜像/偏置支路
BOARD_LABEL = {'mix': '混频器单体 mix', 'lob': 'LO 缓冲 lobuf', 'chain': '链级联 chain'}
CORNER = {'typ': 'typ', 'bcs': 'bcs', 'wcs': 'wcs'}
TEMP = {'tm40': -40, 't27': 27, 't125': 125}


CRITERION_NODES = [   # 判据域 5 测点 x 3 corner = 15 点（口径拍板 §一.2 / 判读纪要 v014）
    ('mix', 0, 'mix.ntaila'),
    ('chain', 0, 'chain.mi.ntaila'),
    ('chain', 2, 'chain.lb.ntaila'),
    ('chain', 3, 'chain.lb.ntailb'),
    ('lob', 0, 'lob.ntaila'),
]
CRIT_LINE = 6.4


def parse_op_csv(rel, re_pat):
    idx, n = {}, 0
    with open(os.path.join(WS, rel), encoding='utf-8') as f:
        for r in csv.reader(f):
            if not r or r[0] == 'deck' or r[0].startswith('ALL'):
                continue
            m = re.match(re_pat, r[0])
            if not m:
                continue
            vals = [float(v) for v in r[2:]]
            if len(vals) != len(BOARD_COLS[m.group(1)]):
                continue
            idx[(m.group(1), m.group(2), m.group(3), int(m.group(4)))] = {'vals': vals, 'exit': int(r[1])}
            n += 1
    return idx, n


def version_summary(rel, re_pat, ver, note):
    """同口径版本对照：判据轴（v2500）15 点 + 边角备案域 30 点 + 规格点定标/电流。"""
    idx, n = parse_op_csv(rel, re_pat)
    if not idx:
        return None

    def g(board, seg, tn, vdd, i):
        e = idx.get((board, seg, tn, vdd))
        return None if e is None else e['vals'][i]

    axis, edge = [], []
    for b, i, nm in CRITERION_NODES:
        for seg in ('typ', 'bcs', 'wcs'):
            for vdd, bucket in ((2500, axis), (2250, edge), (2750, edge)):
                a = g(b, seg, 't125', vdd, i)
                c = g(b, seg, 't27', vdd, i)
                if a is None or c is None:
                    continue
                d = (a - c) * 1000
                bucket.append({'corner': seg, 'node': nm, 'vdd': vdd, 'd_mV': r4(d, 2),
                               'pass': abs(d) <= CRIT_LINE})
    spec = {}
    for b in ('mix', 'lob', 'chain'):
        e = idx.get((b, 'typ', 't27', 2500))
        if e:
            cols = BOARD_COLS[b]
            spec[b] = {'ntail_min_mV': r4(min(e['vals'][0], e['vals'][1]) * 1000, 3),
                       'nsens_V': r4(e['vals'][cols.index('nsens')], 6),
                       'ivcc_mA': r4(abs(e['vals'][-1]) * 1000 - BOARD_IV_EXTRA[b], 3)}
    return {
        'ver': ver, 'n_decks': n, 'csv': finfo(rel), 'note': note,
        'axis': axis, 'edge': edge, 'spec': spec,
        'axis_pass': sum(1 for x in axis if x['pass']), 'axis_total': len(axis),
        'axis_worst': max(axis, key=lambda x: abs(x['d_mV'])) if axis else None,
        'edge_pass': sum(1 for x in edge if x['pass']), 'edge_total': len(edge),
        'edge_worst': max(edge, key=lambda x: abs(x['d_mV'])) if edge else None,
    }


def build_op27():
    csvp = 'pdk/sim/r2run/results_r2_v014/op27_summary_v014.csv'
    rows = []
    with open(os.path.join(WS, csvp), encoding='utf-8') as f:
        for r in csv.reader(f):
            if not r or r[0] == 'deck' or r[0].startswith('ALL'):
                continue
            name = r[0]
            m = re.match(r'(mix|lob|chain)op13_(typ|bcs|wcs)_(tm40|t27|t125)_v(\d+)', name)
            if not m:
                continue
            board, seg, tn, vdd = m.group(1), m.group(2), m.group(3), int(m.group(4))
            vals = [float(v) for v in r[2:]]
            cols = BOARD_COLS[board]
            d = {'deck': name, 'board': board, 'corner': seg, 'temp': tn, 'tC': TEMP[tn],
                 'vdd': vdd, 'exit': int(r[1])}
            for c, v in zip(cols, vals):
                d[c] = v
            rows.append(d)
    idx = {(r['board'], r['corner'], r['temp'], r['vdd']): r for r in rows}

    def get(board, seg, tn, vdd, key):
        r = idx.get((board, seg, tn, vdd))
        return None if r is None else r.get(key)

    # 1 锚（nsens - 0.8359）
    anchor = []
    for b in ('mix', 'lob', 'chain'):
        v = get(b, 'typ', 't27', 2500, 'nsens')
        anchor.append({'board': b, 'label': BOARD_LABEL[b], 'nsens': r4(v, 6),
                       'delta_mV': r4((v - 0.8359) * 1000, 3) if v is not None else None,
                       'pass': abs((v - 0.8359) * 1000) < 1.0 if v is not None else None})
    # 2 typ 定标（ntail - 0.35 线）
    calib = []
    for b, pairs in (('mix', [('ntaila', 'mix.ntaila'), ('ntailb', 'mix.ntailb')]),
                     ('lob', [('ntaila', 'lob.ntaila'), ('ntailb', 'lob.ntailb')]),
                     ('chain', [('mi.ntaila', 'mi.ntaila'), ('mi.ntailb', 'mi.ntailb'),
                                ('lb.ntaila', 'lb.ntaila'), ('lb.ntailb', 'lb.ntailb')])):
        for key, nm in pairs:
            v = get(b, 'typ', 't27', 2500, key)
            calib.append({'board': b, 'label': BOARD_LABEL[b], 'node': nm, 'v': r4(v, 5),
                          'dev_mV': r4((v - 0.35) * 1000, 2),
                          'in_window': 0.350 <= v <= 0.360 if v is not None else None})
    # 3 t125 - t27 温漂残差：判据轴（v2500）与边角备案域分列
    drift = []
    crit_names = {nm for _, _, nm in CRITERION_NODES}
    for b, i, nm in CRITERION_NODES + [('lob', 1, 'lob.ntailb')]:
        in_crit = nm in crit_names
        for seg in ('typ', 'bcs', 'wcs'):
            for vdd in (2250, 2500, 2750):
                a = get(b, seg, 't125', vdd, BOARD_COLS[b][i])
                c = get(b, seg, 't27', vdd, BOARD_COLS[b][i])
                if a is None or c is None:
                    continue
                d = (a - c) * 1000
                if not in_crit:
                    dom = 'lob.ntailb 备案（未入判据 5 测点）'
                elif vdd == 2500:
                    dom = '判据轴 v2500'
                else:
                    dom = '边角备案 vdd 轴'
                drift.append({'board': b, 'label': BOARD_LABEL[b], 'node': nm, 'corner': seg,
                              'vdd': vdd, 'd_mV': r4(d, 2), 'pass': abs(d) <= CRIT_LINE,
                              'domain': dom, 't125_mV': r4(a * 1000, 3), 't27_mV': r4(c * 1000, 3)})
    axis = [x for x in drift if x['domain'].startswith('判据')]
    edge = [x for x in drift if x['domain'].startswith('边角')]
    # 4 i_vcc 本体（45mA 线）
    ivcc = []
    for b in ('mix', 'lob', 'chain'):
        for seg in ('typ', 'bcs', 'wcs'):
            for tn in ('tm40', 't27', 't125'):
                for vdd in (2250, 2500, 2750):
                    v = get(b, seg, tn, vdd, 'ivcc')
                    if v is None:
                        continue
                    body = abs(v) * 1000 - BOARD_IV_EXTRA[b]
                    ivcc.append({'board': b, 'label': BOARD_LABEL[b], 'corner': seg, 'temp': tn,
                                 'vdd': vdd, 'mA': r4(body, 3),
                                 'spec_point': seg == 'typ' and tn == 't27' and vdd == 2500})
    spec_iv = [x for x in ivcc if x['board'] == 'mix' and x['spec_point']]
    # 5 tm40 观测项（PTAT 代价备案）
    tm40 = []
    for seg in ('typ', 'bcs', 'wcs'):
        for vdd in (2250, 2500, 2750):
            a = get('mix', seg, 'tm40', vdd, 'ntaila')
            c = get('mix', seg, 't27', vdd, 'ntaila')
            if a is not None and c is not None:
                tm40.append({'corner': seg, 'vdd': vdd, 'd_mV': r4((a - c) * 1000, 2)})
    # 6 ntail 全角矩阵（窗 0.350~0.360）
    matrix = []
    for b in ('mix', 'lob', 'chain'):
        key = 'mi.ntaila' if b == 'chain' else 'ntaila'
        for seg in ('typ', 'bcs', 'wcs'):
            for tn in ('tm40', 't27', 't125'):
                row = [get(b, seg, tn, vdd, key) for vdd in (2250, 2500, 2750)]
                matrix.append({'board': b, 'label': BOARD_LABEL[b], 'corner': seg, 'temp': tn,
                              'v': [None if x is None else round(x * 1000, 2) for x in row]})
    # 7 kptat（从 v014 定稿网表解析）
    kptat = None
    m = re.search(r'\.param kptat\s*=\s*([0-9.]+)',
                  open(os.path.join(WS, 'pdk/sim/v014/mixer_tb_v014.sp'), encoding='utf-8').read())
    if m:
        kptat = float(m.group(1))
    # 8 版本对照（v011a -> v014，同口径 45 点域）
    RE_V = [
        ('v011a-r2', 'pdk/sim/r2run/results_r2/op27_summary.csv',
         r'(mix|lob|chain)op_(typ|bcs|wcs)_(tm40|t27|t125)_v(\d+)',
         '首版晶体管级三板（锚未回填 nsens=0.6806）'),
        ('v012', 'pdk/sim/r2run/results_r2_v012/op27_summary_v012.csv',
         r'(mix|lob|chain)op12_(typ|bcs|wcs)_(tm40|t27|t125)_v(\d+)', '感测管 Is0 x4'),
        ('v013', 'pdk/sim/r2run/results_r2_v013/op27_summary_v013.csv',
         r'(mix|lob|chain)op13_(typ|bcs|wcs)_(tm40|t27|t125)_v(\d+)',
         '锚回填 + rr680 + PTAT(kptat=2.53)'),
        ('v014', csvp, r'(mix|lob|chain)op13_(typ|bcs|wcs)_(tm40|t27|t125)_v(\d+)',
         '单参数收口 kptat=3.98'),
    ]
    versions = []
    for ver, rel, pat, note in RE_V:
        if os.path.exists(os.path.join(WS, rel)):
            s = version_summary(rel, pat, ver, note)
            if s:
                versions.append(s)
    return {
        'rows': rows, 'anchor': anchor, 'calib': calib, 'drift': drift,
        'axis': axis, 'edge': edge, 'ivcc': ivcc, 'tm40': tm40, 'matrix': matrix,
        'kptat': kptat, 'versions': versions, 'crit_line': CRIT_LINE,
        'axis_pass': sum(1 for x in axis if x['pass']), 'axis_total': len(axis),
        'edge_pass': sum(1 for x in edge if x['pass']), 'edge_total': len(edge),
        'axis_worst': max(axis, key=lambda x: abs(x['d_mV'])) if axis else None,
        'edge_worst': max(edge, key=lambda x: abs(x['d_mV'])) if edge else None,
        'spec_iv': spec_iv[0]['mA'] if spec_iv else None,
        'ivcc_max_all': max(ivcc, key=lambda x: x['mA']) if ivcc else None,
        'csv': finfo(csvp),
    }


# ---------------------------------------------------------------- sp 频域
SP_PAIRS = [((1, 1), 'S11 IF 反射'), ((3, 3), 'S33 LO 反射'), ((5, 5), 'S55 RF 反射'),
            ((1, 5), 'S15 IF→RF'), ((3, 5), 'S35 LO→RF'), ((5, 3), 'S53 RF→LO'),
            ((1, 3), 'S13 IF→LO 隔离'), ((2, 4), 'S24 IF 反相→LO')]


def parse_sp_csv(path):
    """wrdata 全 6×6 复数谱：每行 36 组 (f, re, im)。"""
    series = {f'S{i}{j}': ([], []) for i in range(1, 7) for j in range(1, 7)}
    freqs = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            p = line.split()
            if len(p) < 36 * 3:
                continue
            fl = [float(x) for x in p]
            k = 0
            for i in range(1, 7):
                for j in range(1, 7):
                    fr, re_, im_ = fl[k * 3], fl[k * 3 + 1], fl[k * 3 + 2]
                    if not freqs:
                        pass
                    mag = math.hypot(re_, im_)
                    series[f'S{i}{j}'][0].append(fr / 1e9)
                    series[f'S{i}{j}'][1].append(20 * math.log10(mag) if mag > 0 else -200)
                    k += 1
            freqs.append(fl[0] / 1e9)
    return freqs, series


def build_sp():
    root = os.path.join(WS, 'outbox_files/r2sp_all')
    decks = []
    series = {}
    for seg in ('typ', 'bcs', 'wcs'):
        for tn in ('tm40', 't27', 't125'):
            for vdd in (2250, 2500, 2750):
                fn = f'rsp_B_{seg}_{tn}_v{vdd}.csv'
                p = os.path.join(root, fn)
                if not os.path.exists(p):
                    continue
                decks.append({'name': f'{seg}/{tn}/v{vdd}', 'corner': seg, 'temp': tn, 'vdd': vdd,
                              'file': fn, **finfo(os.path.relpath(p, WS))})
                if (seg, tn, vdd) in (('typ', 't27', 2500), ('bcs', 't125', 2250), ('wcs', 't125', 2750),
                                      ('typ', 't125', 2500)):
                    freqs, ss = parse_sp_csv(p)
                    series[f'{seg}/{tn}/v{vdd}'] = {
                        'freq': freqs,
                        'pairs': [{'key': f'S{i}{j}', 'label': lab, 'y': ss[f'S{i}{j}'][1]}
                                  for (i, j), lab in SP_PAIRS],
                    }
    m8 = load_json('pdk/sim/r2run/m8_final_pkg_v1.json')
    h = m8.get('seg1_sp_full_criteria_B', {}).get('harness', {})
    stats = {
        'n_files': h.get('n_files'), 'single_fails_total': h.get('single_fails_total'),
        'fails_by_pair': h.get('fails_by_pair'), 'sdd_fails': h.get('sdd_fails'),
        'eig_wb_max': h.get('eig_wb_max'), 'eig_wb_at': h.get('eig_wb_at'),
        'eig_ab_max': h.get('eig_ab_max'), 'eig_ab_at': h.get('eig_ab_at'),
        'scc_lo_wb_max': h.get('scc_lo_wb_max'), 'scc_lo_ab_max': h.get('scc_lo_ab_max'),
        'eig_judgement': h.get('eig_judgement'), 'lo_pair_literal': h.get('lo_pair_literal'),
        'spurious_20pts': h.get('spurious_20pts'),
    }
    # sp deck 内嵌 OP27 读数（27 角）
    opcsv = os.path.join(WS, 'pdk/sim/r2run/results_r2sp/sp27_summary.csv')
    spop = []
    if os.path.exists(opcsv):
        for r in csv.reader(open(opcsv, encoding='utf-8')):
            if not r or r[0] in ('deck',) or r[0].startswith('ALL'):
                continue
            spop.append(r)
    return {'decks': decks, 'series': series, 'stats': stats, 'm8': m8,
            'pairs': [{'key': f'S{i}{j}', 'label': lab} for (i, j), lab in SP_PAIRS],
            'op_rows': spop, 'pairs_n': len(SP_PAIRS)}


# ---------------------------------------------------------------- tran 时域
def sample_wave(path, *, vectors, t0, dt, npts, t_from=None, t_to=None):
    """定宽 wrdata 大文件按字节偏移抽样（不整读 900MB）。"""
    size = os.path.getsize(path)
    with open(path, 'rb') as f:
        line = f.readline()
    L = len(line)
    n_lines = size // L
    idx = []
    if t_from is None:
        step = max(1, n_lines // npts)
        idx = list(range(0, n_lines, step))[:npts]
    else:
        i0 = max(0, int((t_from - t0) / dt))
        i1 = min(n_lines, int((t_to - t0) / dt))
        step = max(1, (i1 - i0) // npts)
        idx = list(range(i0, i1, step))[:npts]
    out_t, out_v = [], [[] for _ in vectors]
    with open(path, 'rb') as f:
        for i in idx:
            f.seek(i * L)
            p = f.readline().split()
            if len(p) < len(vectors) * 2:
                continue
            out_t.append(float(p[0]))
            for k in range(len(vectors)):
                out_v[k].append(float(p[2 * k + 1]))
    return out_t, out_v


def envelope(t, v, nbins=150):
    """分桶取 min/max/mean，得到包络带（混频器载波 5.5GHz 下全窗采样会糊成一条线）。"""
    n = len(t)
    env = []
    for b in range(nbins):
        i0 = b * n // nbins
        i1 = max(i0 + 1, (b + 1) * n // nbins)
        seg = v[i0:i1]
        env.append({'t': t[(i0 + i1) // 2], 'min': min(seg), 'max': max(seg),
                    'mean': sum(seg) / len(seg)})
    return env


def build_tran():
    mix_p = 'pdk/sim/r2run/raw_r2tran/v011ar2_mixA_typ.csv'
    ch_p = 'pdk/sim/r2run/raw_r2tran/v011ar2_chain_typ.csv'
    mix_vec = ['ntaila', 'ntailb', 'nlop', 'nlon', 'nrfp', 'nrfn']
    ch_vec = ['noutp', 'noutn', 'nmixp', 'nmixn', 'nd1p', 'nd1n', 'nlop', 'nlon',
              'nblop', 'nblon', 'mi.ntaila', 'mi.ntailb']
    t0, dt = 60e-9, 1e-12
    mix = {'vectors': mix_vec, 'file': finfo(mix_p), 'deck': 'decks_r2tran/tran_r2mix_typ.sp'}
    ch = {'vectors': ch_vec, 'file': finfo(ch_p), 'deck': 'decks_r2tran/tran_r2chain_typ.sp'}
    t, v = sample_wave(os.path.join(WS, mix_p), vectors=mix_vec, t0=t0, dt=dt, npts=1400)
    mix['t'] = [round(x * 1e9, 4) for x in t]
    mix['env'] = [{'vec': nm, 'bins': envelope(t, v[k], 150)} for k, nm in enumerate(mix_vec)]
    tz, vz = sample_wave(os.path.join(WS, mix_p), vectors=mix_vec, t0=t0, dt=dt, npts=1100,
                         t_from=200e-9, t_to=260e-9)
    mix['zoom'] = {'t': [round(x * 1e9, 4) for x in tz],
                   'v': [{'vec': nm, 'y': [round(x, 6) for x in vz[k]]}
                         for k, nm in enumerate(mix_vec)]}
    t, v = sample_wave(os.path.join(WS, ch_p), vectors=ch_vec, t0=t0, dt=dt, npts=1400)
    ch['t'] = [round(x * 1e9, 4) for x in t]
    ch['env'] = [{'vec': nm, 'bins': envelope(t, v[k], 150)} for k, nm in enumerate(ch_vec)]
    tz, vz = sample_wave(os.path.join(WS, ch_p), vectors=ch_vec, t0=t0, dt=dt, npts=1100,
                         t_from=200e-9, t_to=260e-9)
    ch['zoom'] = {'t': [round(x * 1e9, 4) for x in tz],
                  'v': [{'vec': nm, 'y': [round(x, 6) for x in vz[k]]}
                        for k, nm in enumerate(ch_vec)]}
    ext = load_json('pdk/sim/r2run/results_r2tran/ext_r2tran_v2_1.json')
    return {'mix': mix, 'chain': ch, 'ext': ext}


# ---------------------------------------------------------------- 器件 / 线性度
def build_device():
    d = load_json('sim_report/sow2_results/d1_npn_corner_grid_v1.json')
    series = {}
    for rec in d['records']:
        c = rec['corner'].replace('hbt_', '')
        series.setdefault(c, []).append({'ic_mA': round(rec['ic_actual_A'] * 1e3, 4),
                                         'ic_tgt_mA': round(rec['ic_target_A'] * 1e3, 4),
                                         'vce': rec['vce_v'], 'gm_mS': round(rec['gm_dIcdVbe_S'] * 1e3, 4),
                                         'beta': round(rec['beta'], 1), 'ft_GHz': rec['ft_cross_GHz'],
                                         'vbe': round(rec['vbe_solved_V'], 4)})
    for c in series:
        series[c].sort(key=lambda r: (r['vce'], r['ic_mA']))
    p0 = load_json('sim_report/sow2_results/d1_p0_sanity_typ_v1.json')
    return {'declarations': d['declarations'], 'n_points': d['n_points'],
            'generated_at': d['generated_at'], 'series': series,
            'file': finfo('sim_report/sow2_results/d1_npn_corner_grid_v1.json'),
            'p0': p0, 'p0_file': finfo('sim_report/sow2_results/d1_p0_sanity_typ_v1.json')}


B1_TITLES = {
    'b1_m1': ('混频器 双音 CG / 输出功率 vs LO 幅值', 'mixer：LO 与 IF 双音驱动下的转换增益与每音输出功率'),
    'b1_m2': ('混频器 IF 幅值扫描（增益压缩）', 'mixer：固定 LO 下扫 IF 幅值，观察 Pout 与差分输出幅度'),
    'b1_m3': ('混频器 双音失真点', 'mixer：IM3/IM2/OIP3/IIP3 单点双音分析'),
    'b1_m4': ('混频器 S 参数（对角）', 'mixer：6 端口对角 Sii vs 频率'),
    'b1_m5': ('混频器 杂散与隔离', 'mixer：LO 馈通、LO→RF 隔离、镜像抑制单点'),
    'b1_m6': ('混频器 IM2 分析', 'mixer：不同谱线组合的 IM2/OIP2'),
    'b1_m7': ('混频器 输出噪声谱', 'mixer：输出端噪声 PSD vs 频率'),
    'b1_m8': ('混频器 全 S 参数', 'mixer：6×6 全 S 复数谱 vs 频率'),
    'b1_lobuf_l1': ('LO 缓冲 线性度（HD2）', 'lobuf：输入/输出差分摆幅与二次谐波'),
    'b1_lobuf_l7': ('LO 缓冲 输出噪声谱', 'lobuf：输出噪声 PSD vs 频率'),
    'b1_lobuf_l8': ('LO 缓冲 S 参数', 'lobuf：全 S 复数谱 vs 频率'),
}


def build_b1():
    """B1 批次（组长侧 ngspice-47 单板扫频/扫幅）——取 typ/t27/v2500 规格点，按 schema 分派。"""
    root = os.path.join(WS, 'outbox_files/b1_results_v2/results_b1')
    picks = {}
    for fn in sorted(os.listdir(root)):
        if not fn.endswith('.json'):
            continue
        m = re.match(r'(b1_[a-z0-9_]+)_hbt_(typ|bcs|wcs)_(t27|t125|tm40)_v(2250|2500|2750)_v2\.json', fn)
        if not m:
            continue
        name, seg, tn, vdd = m.groups()
        if (seg, tn, vdd) != ('typ', 't27', '2500'):
            continue
        rel = os.path.join('outbox_files/b1_results_v2/results_b1', fn)
        d = load_json(rel)
        pts = d['points']
        keys = set(pts[0].keys()) if pts else set()
        title, desc = B1_TITLES.get(name, (name, ''))
        item = {'title': title, 'desc': desc, 'decl': d.get('declarations', {}), 'file': finfo(rel),
                'kind': 'other', 'points': []}
        if {'lo_in_amp_mv', 'out_diff_pp_V'} <= keys:
            item['kind'] = 'lobuf_lin'
            item['points'] = [{'x': p['lo_in_amp_mv'], 'in_pp': p['in_diff_pp_V'],
                               'out_pp': p['out_diff_pp_V'], 'y2': p['hd2_dbc'],
                               'gain': 20 * math.log10(p['out_diff_pp_V'] / p['in_diff_pp_V'])}
                              for p in pts]
        elif {'loamp_mv', 'CG_dB'} <= keys:
            item['kind'] = 'mix_cg'
            item['points'] = [{'x': p['loamp_mv'], 'y': p['CG_dB'], 'y2': p['pout_dBm'],
                               'ifamp': p.get('ifamp_mv')} for p in pts]
        elif {'ifamp_mv', 'pout_dBm'} <= keys:
            item['kind'] = 'mix_if'
            item['points'] = [{'x': p['ifamp_mv'], 'y': p['pout_dBm'], 'y2': p.get('a_diff_V')}
                              for p in pts]
        elif keys == {'f_Hz', 'inoise_V_rHz'}:
            item['kind'] = 'noise'
            item['points'] = [{'x': p['f_Hz'],
                               'y': 20 * math.log10(p['inoise_V_rHz']) if p['inoise_V_rHz'] > 0 else None}
                              for p in pts]
        elif 'f_Hz' in keys and any(k.startswith('s') for k in keys):
            item['kind'] = 'sparam'
            sp = []
            for p in pts:
                row = {'x': p['f_Hz']}
                for k, v in p.items():
                    if k == 'f_Hz':
                        continue
                    if isinstance(v, (list, tuple)) and len(v) == 2:
                        row[k] = round(20 * math.log10(math.hypot(v[0], v[1])) if math.hypot(v[0], v[1]) > 0
                                       else -200, 3)
                sp.append(row)
            item['points'] = sp
            item['pair_keys'] = [k for k in sp[0] if k != 'x']
        else:
            item['points'] = pts
        picks[name] = item
    return picks


def build_spec_table():
    """从 spec.md §2 抽取 S 指标表（编号 / 指标 / 规范要求 / 本设计目标 / 备注）。"""
    txt = open(os.path.join(WS, 'spec.md'), encoding='utf-8').read()
    rows = []
    for line in txt.splitlines():
        if not line.strip().startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) >= 4 and re.match(r'^S\d+[a-z]?$', cells[0]):
            rows.append({'id': cells[0], 'metric': cells[1], 'req': cells[2],
                         'goal': cells[3], 'note': cells[4] if len(cells) > 4 else ''})
    head = ''
    m = re.search(r'## 1\. 范围与定位(.*?)\n## ', txt, re.S)
    if m:
        head = m.group(1).strip()
    ver = ''
    m2 = re.search(r'^- 版本：\*\*(.+?)\*\*', txt, re.M)
    if m2:
        ver = m2.group(1)
    return {'rows': rows, 'scope': head, 'version': ver,
            'file': finfo('spec.md'), 'n': len(rows)}


# ---------------------------------------------------------------- 参数表
def build_params():
    path = os.path.join(WS, 'design_circuit/params.csv')
    rows = []
    for line in open(path, encoding='utf-8'):
        s = line.strip()
        if not s or s.startswith('#'):
            continue
        parts = [p.strip() for p in s.split(',')]
        rows.append(parts)
    return {'rows': rows, 'file': finfo('design_circuit/params.csv')}


# ---------------------------------------------------------------- 版本迭代史
# 口径纪律（2026-10-16 修正，fde9 WebUI 校核建议①）：
#   typ/bcs/wcs 三列一律由 op27 CSV 现算 = 判据点 mix.ntaila 的 (t125−t27) 残差（判读纪要同口径），
#   **不再手填预测值**；v013 收口时对 v014 做过的线性外推预测另存 pred 字段并显式标注「预测」。
#   （旧表把预测 +1.58/+5.61/−5.58 与 KPI/判读纪要的实测 +1.75/+5.79/−5.65 并排，看着像矛盾。）
ITER_META = [
    {'ver': 'v011a-r2', 'change': '首版晶体管级三板（Gilbert mix + LO BUF + 链级联），链路基准入版',
     'verdict': 'FAIL（t125 残差 −35mV 失守）',
     'note': 'vdd 轴 9/27 角塌 <0.35V；wcs+t125 在 v2500 亦 0.2816 失守；B 口径 mix 13/27 失守',
     'src': '判读纪要_v011a_r2_快验与OP27', 'pred': None},
    {'ver': 'v012', 'change': '感测管 Is0 ×4（感测密度修正）',
     'verdict': 'FAIL（方向判死）',
     'note': '三口径预期（−6.4/−8.8/−21）全部落空 → 机理=感测/gm 两管 Vbe TC 失配（−0.32mV/K），Is0 路线判死',
     'src': '判读纪要_v012_OP', 'pred': None},
    {'ver': 'v013', 'change': '锚回填 0.8260→0.8359 + rr 672→680 + PTAT 注入（kptat=2.53）',
     'verdict': '三过一不足',
     'note': 'η=1 假设定标致三 corner 仍超 6.4mV 判据线 → 引出 η 实测标定',
     'src': '判读纪要_v013_OP', 'pred': None},
    {'ver': 'v014', 'change': '单参数收口 kptat 2.53→3.98（η 实测 min-max 线性折中）',
     'verdict': '全过（判据线 6.4mV）',
     'note': 'η 实测 typ .670 / bcs .815 / wcs .552；补偿斜率 +0.4755mV/K；t27 零点不动 → 定标与 i_vcc 零移动',
     'src': '判读纪要_v014_OP', 'pred': (1.58, 5.61, -5.58),
     'pred_note': 'v013 收口时按 η 实测线性外推的预测值（判读纪要 v014 §预测），非实测'},
]


def build_iteration(versions):
    """迭代表：静态元信息（改动/裁决/机理）+ 现算数值。

    列口径 = 判据点 mix.ntaila 的 (t125 − t27) 残差，按 corner 分列 —— 与判读纪要各版表格、
    /sim/iter 收敛轨迹图完全同一口径（v013 纪要 −9.78/−8.21/−14.95 = mix.ntaila 三 corner，
    v014 实测 +1.75/+5.79/−5.65 同源）。另附 axis_worst5 = 判据域 5 节点里的最差点，
    两者可能不同（如 v013 typ：mix.ntaila −9.78 vs chain.mi.ntaila −9.87），裁决看 5 节点全域。
    """
    by = {v['ver']: v for v in versions}
    out = []
    for m in ITER_META:
        v = by.get(m['ver'])
        per = {}
        if v:
            for x in v['axis']:
                if x['node'] == 'mix.ntaila':
                    per[x['corner']] = x['d_mV']
        row = dict(m)
        row.update({'typ': per.get('typ'), 'bcs': per.get('bcs'), 'wcs': per.get('wcs'),
                    'axis_pass': v['axis_pass'] if v else None,
                    'axis_total': v['axis_total'] if v else None,
                    'worst5': (f"{v['axis_worst']['node']} {v['axis_worst']['d_mV']:+.2f}mV"
                               if v and v.get('axis_worst') else None)})
        out.append(row)
    return out


# ---------------------------------------------------------------- 交付物总表
KEY_ARTIFACTS = [
    # ---- SOW-6 全链版图（2026-10-17 一日战果）----
    ('SOW-6 结项报告 v0.2', 'phys/report/SOW-6_全链版图报告.md'),
    ('HBT 级版图准则 v1.3（b7a0 注记版·收编真值）', 'design_circuit/HBT级版图准则_v1.3_b7a0注记.md'),
    ('knife 骑体对照表与指派定律 v2（LVS 幻影焊判决产出）', 'outbox_files/design/sow6/knife_骑体对照表与指派定律_v2_2026-10-17.md'),
    ('M4 顶层设计输入预案 v0.2', 'outbox_files/design/sow6/M4顶层_设计输入预案_v0.2.md'),
    ('单元几何真值表 v1.1（via/cmim 镜像判定）', 'phys/top/单元几何真值表_v1.1.md'),
    ('lib13g2 单元库 v2.3（29102B·canonical）', 'phys/top/lib13g2.py'),
    ('DRV1 v19 版图 GDS（E 断路修复版）', 'phys/sow6_run/run_v2/gds/m3_drv1_v19.gds'),
    ('DRV2 v19 版图 GDS（E 断路修复版）', 'phys/sow6_run/run_v2/gds/m3_drv2_v19.gds'),
    ('v19 判读纪要（修复三轮实证）', 'phys/top/判读纪要_v19修复代跑轮_2026-10-17.md'),
    # ---- SOW-1/SOW-2 全案 ----
    ('顶层规格 spec v1.3', 'spec.md'), ('架构 architecture v1.2', 'architecture.md'),
    ('终稿报告 final_report v1.2', 'final_report.md'), ('集成评审记录', 'integration_review.md'),
    ('结项报告终稿 v2', 'pdk/SOW-2_结项报告_v011a-r2.md'),
    ('电路设计说明 v1.4', 'design_circuit/design_circuit.md'),
    ('版图与物理实现规划', 'design_circuit/layout_plan.md'),
    ('电路参数表（唯一数据源）', 'design_circuit/params.csv'),
    ('v014 定稿网表 mix', 'pdk/sim/v014/mixer_tb_v014.sp'),
    ('v014 定稿网表 chain', 'pdk/sim/v014/chain_top_tb_v014.sp'),
    ('v014 投件 sha 表', 'pdk/sim/v014/sha256_v014_submit.txt'),
    ('v013.1 定稿 sha 表（v014 基线）', 'pdk/sim/v013_1/sha256_v013_submit.txt'),
    ('v013.1 归档与 v014 血缘核验记录', 'pdk/sim/v013_1/V0131_归档与v014血缘核验_2026-10-16.md'),
    ('v012 投件 sha 表', 'pdk/sim/v013/sha256_v012_submit.txt'),
    ('v011a-r2 投件 manifest', 'pdk/sim/sow2/v011a_r2_submit/v011a_r2_submit_manifest.md'),
    ('v011a-r2 主版 mix', 'pdk/sim/sow2/v011a_r2_submit/mixer_tb_v011a_r2.sp'),
    ('v011a-r2 主版 chain', 'pdk/sim/sow2/v011a_r2_submit/chain_top_tb_v011a_r2.sp'),
    ('M8 终审三段合一', 'pdk/sim/r2run/m8_final_pkg_v1.json'),
    ('M8 收官 sha', 'pdk/sim/r2run/m8_final_pkg_v1.sha256.txt'),
    ('OP27 v014 全扫结果（81 deck）', 'pdk/sim/r2run/results_r2_v014/op27_summary_v014.csv'),
    ('sp 27 角 61 点 OP 汇总', 'pdk/sim/r2run/results_r2sp/sp27_summary.csv'),
    ('tran 提取 ext v2.1', 'pdk/sim/r2run/results_r2tran/ext_r2tran_v2_1.json'),
    ('tran 原始波形 mix（470MB）', 'pdk/sim/r2run/raw_r2tran/v011ar2_mixA_typ.csv'),
    ('tran 原始波形 chain（939MB）', 'pdk/sim/r2run/raw_r2tran/v011ar2_chain_typ.csv'),
    ('器件 corner 网格 d1', 'sim_report/sow2_results/d1_npn_corner_grid_v1.json'),
    ('器件 sanity p0', 'sim_report/sow2_results/d1_p0_sanity_typ_v1.json'),
    ('op27 判读脚本 v014', 'pdk/sim/r2run/judge_v014.py'),
    ('v014 批跑管线', 'pdk/sim/r2run/run_v014op.py'),
    ('PDK 落地评估', 'research/PDK_SG13G2_落地评估_2026-10-16.md'),
    ('EDA/RFIC 调研报告', 'research/EDA_RFIC_WiFi7TX_调研报告_2026-10-15.md'),
]


def build_artifacts():
    out = []
    for title, rel in KEY_ARTIFACTS:
        p = os.path.join(WS, rel)
        if os.path.exists(p):
            d = finfo(rel)
            d['title'] = title
            out.append(d)
    return out


# ---------------------------------------------------------------- 版图实证（SOW-3）
# 口径纪律：本页所有数字现场解析——DRC 违规数 = lyrdb 里 <item> 计数；LVS = 官方 log 的
# "Netlists match" + 提取网表器件计数；PEX 逐网 R/C = 后仿真网表里的注释行；前/后指标 =
# wrdata 首行现算。没有任何手填结论。
PHYS_CHIPS = [
    {'key': 'amp2', 'name': 'TX5G_AMP2 · 两级 HBT 放大级', 'ver': 'SOW-3 v2.0 / v2.1',
     'desc': '驱动 Nx=4 + 输出 Nx=4；rsil 发射极退化 + rppd 集电极负载 + rsil 级间耦合；'
             'M1/M2 两层布线 + via_stack 落层。39×21µm。',
     'gds': 'phys/gilbert/gds/amp2.gds',
     'drc_dirs': ['phys/gilbert/drc/final', 'phys/gilbert/drc/final2',
                  'phys/gilbert/drc/final3', 'phys/gilbert/drc/final4'],
     'lvs_dir': 'phys/gilbert/lvs/run4', 'lvs_cell': 'amp2',
     'cdl': 'phys/gilbert/lvs/amp2.cdl',
     'post_cir': 'phys/gilbert/pex/amp2_post.cir',
     'pre_ac': 'phys/gilbert/pre/ac_pre.txt', 'post_ac': 'phys/gilbert/pex/ac_post.txt',
     'pre_sp': 'phys/gilbert/pre/amp2_pre.sp',
     'reports': ['phys/gilbert/report/SOW-3_v2_TX5G_AMP2_版图实证.md',
                 'phys/gilbert/report/SOW-3_v2.1_TX5G_AMP2_机理判定.md'],
     'json': ['phys/gilbert/sim/attrib_amp2.json', 'phys/gilbert/sim/mech_amp2.json',
              'phys/gilbert/sim/opcheck_amp2.json'],
     'ac_src': 0.05},
    {'key': 'hbtdiff', 'name': 'TX5G_HBTDIFF · 单级 HBT 差分级', 'ver': 'SOW-3 v1.0',
     'desc': 'npn13G2 Nx=4 单级差分放大，22×32µm；全链跑通的第一个块（寄生影响小，0.4dB）。',
     'gds': 'phys/gds/hbtdiff.gds',
     'drc_dirs': ['phys/drc/final'],
     'lvs_dir': 'phys/lvs/run9', 'lvs_cell': 'hbtdiff',
     'cdl': 'phys/lvs/hbtdiff.cdl',
     'post_cir': 'phys/pex/hbtdiff_post.cir',
     'pre_ac': 'phys/pre/ac_pre.txt', 'post_ac': 'phys/pex/hbtdiff_post_ac.txt',
     'pre_sp': 'phys/pre/hbtdiff_pre.sp',
     'reports': ['phys/report/SOW-3_版图实证报告.md'],
     'json': [], 'ac_src': 0.05},
]


def _drc_items(d):
    """lyrdb 里 <item> 的个数 = 违规数（0 = 干净）。final4 实测 0，final 实测 19。"""
    fs = glob.glob(os.path.join(WS, d, '*_full.lyrdb'))
    if not fs:
        return None
    s = open(fs[0], encoding='utf-8', errors='replace').read()
    return len(re.findall(r'<item>', s))


def _drc_runtime(d):
    fs = glob.glob(os.path.join(WS, d, '*_sg13g2_maximal.log'))
    if not fs:
        return None
    m = re.search(r'completed in ([\d.]+) seconds', open(fs[0], encoding='utf-8', errors='replace').read())
    return float(m.group(1)) if m else None


def _ac_first_row(path):
    """wrdata ascii：首行即最低频点。返回 (freq, re, im)。不整file读入，只取首行。"""
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            for line in f:
                p = line.split()
                if len(p) >= 3:
                    try:
                        return float(p[0]), float(p[1]), float(p[2])
                    except ValueError:
                        continue
    except OSError:
        return None
    return None


def _gain_db(path, ac_src):
    r = _ac_first_row(path)
    if not r:
        return None
    f, re_, im = r
    mag = math.hypot(re_, im)
    if mag <= 0:
        return None
    return r4(20 * math.log10(mag / ac_src), 2), r4(20 * math.log10(mag), 2), r4(f / 1e9, 4)


def _pex_nets(cir_rel):
    """从 PEX 网表注释行现场提逐网 R/C：* --- net NAME [LAYER]: R_total=XΩ C_total=YfF 引脚数=N"""
    p = os.path.join(WS, cir_rel)
    if not os.path.exists(p):
        return []
    out = []
    for ln in open(p, encoding='utf-8'):
        # v2.0 网表带层名 [M1]；v1.0 网表不带（`--- net et1: R_total=…`），层名置 None
        m = re.search(r'\* --- net (\S+)(?: \[(\w+)\])?: R_total=([\d.]+)Ω\s+C_total=([\d.]+)fF\s+引脚数=(\d+)', ln)
        if m:
            out.append({'net': m.group(1), 'layer': m.group(2) or '—', 'r': float(m.group(3)),
                        'c': float(m.group(4)), 'npin': int(m.group(5))})
    return out


def _lvs_status(lvs_dir, cell):
    p = os.path.join(WS, lvs_dir, f'{cell}.log')
    if not os.path.exists(p):
        return None
    s = open(p, encoding='utf-8', errors='replace').read()
    m = re.search(r'(Congratulations! Netlists match|No\. of nets|netlists do not match)', s)
    rt = re.search(r'LVS Total Run time ([\d.]+) seconds', s)
    cir = os.path.join(WS, lvs_dir, f'{cell}_extracted.cir')
    devs = []
    hbt = None
    if os.path.exists(cir):
        for ln in open(cir, encoding='utf-8'):
            t = ln.strip()
            if re.match(r'^[QR]\$', t):
                devs.append(t.split()[0][0])
            m2 = re.search(r'npn13G2.*we=(\S+)\s+le=(\S+)\s+Nx=(\d+)', t)
            if m2:
                hbt = {'we': m2.group(1), 'le': m2.group(2), 'Nx': m2.group(3)}
    return {'match': bool(m and 'Congratulations' in m.group(1)),
            'run_s': float(rt.group(1)) if rt else None,
            'n_dev': len(devs), 'dev_kinds': ''.join(sorted(set(devs))),
            'hbt_geom': hbt, 'log': finfo(f'{lvs_dir}/{cell}.log')}


def build_phys():
    chips = []
    for c in PHYS_CHIPS:
        gds = finfo(c['gds']) if os.path.exists(os.path.join(WS, c['gds'])) else None
        drcs = [{'dir': d, 'name': os.path.basename(d), 'violations': _drc_items(d),
                 'runtime_s': _drc_runtime(d)} for d in c['drc_dirs']]
        pre = _gain_db(os.path.join(WS, c['pre_ac']), c['ac_src'])
        post = _gain_db(os.path.join(WS, c['post_ac']), c['ac_src'])
        chips.append({
            **{k: v for k, v in c.items() if k not in ('drc_dirs',)},
            'gds_info': gds, 'drc': drcs,
            'drc_final': next((x for x in reversed(drcs) if x['violations'] is not None), None),
            'lvs': _lvs_status(c['lvs_dir'], c['lvs_cell']),
            'pex_nets': _pex_nets(c['post_cir']),
            'pre_gain': pre[0] if pre else None, 'pre_dBV': pre[1] if pre else None,
            'post_gain': post[0] if post else None, 'post_dBV': post[1] if post else None,
            'drop_dB': (r4(pre[0] - post[0], 2) if pre and post else None),
            'reports_info': [finfo(r) for r in c['reports'] if os.path.exists(os.path.join(WS, r))],
            'json_info': [finfo(j) for j in c['json'] if os.path.exists(os.path.join(WS, j))],
        })
    extra = {}
    for j in ('phys/gilbert/sim/attrib_amp2.json', 'phys/gilbert/sim/mech_amp2.json',
              'phys/gilbert/sim/opcheck_amp2.json', 'phys/gilbert/sim/opcheck_drv2.json',
              'phys/gilbert/sim/emit_scan_drv2.json'):
        if os.path.exists(os.path.join(WS, j)):
            extra[os.path.basename(j)[:-5]] = load_json(j)
    rules = {}
    for rv in ('v1.1', 'v1'):
        rp = f'design_circuit/HBT级版图准则_发射极路径与地轨回流_{rv}.md'
        if os.path.exists(os.path.join(WS, rp)):
            rules[rv] = {'path': rp, 'size': os.path.getsize(os.path.join(WS, rp)),
                         'text': open(os.path.join(WS, rp), encoding='utf-8').read(),
                         'info': finfo(rp)}
    plan = 'phys/gilbert/sim/emit_route_plan.md'
    opmd = 'phys/gilbert/sim/opcheck_drv2.md'
    return {'chips': chips, 'extra': extra,
            'rules': rules,
            'rule_doc': finfo(rules['v1.1']['path']) if 'v1.1' in rules
                         else (finfo(list(rules.values())[0]['path']) if rules else None),
            'rule_text': list(rules.values())[0]['text'] if rules else '',
            'route_plan_text': open(os.path.join(WS, plan), encoding='utf-8').read()
                               if os.path.exists(os.path.join(WS, plan)) else '',
            'route_plan_info': finfo(plan) if os.path.exists(os.path.join(WS, plan)) else None,
            'opcheck_md_text': open(os.path.join(WS, opmd), encoding='utf-8').read()
                               if os.path.exists(os.path.join(WS, opmd)) else '',
            'mixer_neg': finfo('phys/gilbert/report/附_Gilbert混频级试跑记录.md')
            if os.path.exists(os.path.join(WS, 'phys/gilbert/report/附_Gilbert混频级试跑记录.md')) else None,
            'ac_src': 0.05}


# ---------------------------------------------------------------- SOW-6 全链版图（2026-10-17）
# 口径纪律同 phys：DRC 违规数 = lyrdb <item> 现数；LVS = 官方 log 现读（match 布尔）；
# 纪要 = phys/top 目录现扫。里程碑叙述在 server 渲染层（内容编组），数字全部现场解析。
SOW6_DRC_DIRS = {
    # ★现役面锚（2026-10-23 换锚轮）：mix 面 v35（v34 + M4.b 根修 δ=0.100，phys/top/m2_mix_v35.gds）；
    #   drv1 面 v23（verify/drv1_v23_run）、drv2 面 v22（gds/m3_drv2_v22.gds）。
    #   历史轮留档不作现算口径：drv1 v21_r1（62c27a42）／drv1 v22／drv2 v20；mix v31（ef034d51）／v34（0fc902ec）。
    #   数字一律现场 lyrdb <item> 现数，此处只给取数目录（口径纪律：不写死结论）。
    #   mix v35 的 M1.b 8 条全归 PCell 内部账（裁定四十六 §四 / 六十五 §二.5 独立复现 8/8 落实例内、0/8 落顶层自画 M1 域内）。
    # 历史轮留档不作现算口径：m2_mix_v31_q14（225，旧面基准 ef034d51）／v34_q14（221，候补 0fc902ec）／m2_mix_v29_q14（253）。
    'mix_v35': 'phys/drc/v35_q1',
    'drv1_v23': 'verify/drv1_v23_run/drc_out',
    'drv2_v22': 'phys/drc/m3_drv2_v22_b7a0',
}
SOW6_LVS = {
    # 现行标准输入对（裁定二十，2026-10-18 首达 PASS）：
    #   v20 GDS × drv2 sch 整改版 × deckfix_v3 × {--ignore_top_ports_mismatch,
    #   --disable_tap_extraction, --no_series_res, --no_parallel_res}
    #   配方 phys/sow6_run/run_v2/lvs/run_lvs_v20_pass.sh（v8/v8_rerun/v9 三连 PASS）
    # ★现役面锚的官方 LVS（裁定六十五/四十九）：mix 面 v35 × 网表 v1g = PASS（net_pair 29 Match 29）；
    #   drv1 面 v23（out_drv2v20_v23_drv1）= PASS（net_pair 13/13 Match）；drv2 面 v22 × sch = PASS（out_drv2v20_drv2v22labels）。
    #   历史轮留档：out_drv2v20_v34_v1f（mix 面 v34 × v1f，PASS，提取件与 v35×v1g 除时间戳外逐字节同）。
    'mix_v35×v1g': ('phys/sow6_run/run_v2/lvs/deckfix_v1/out_drv2v20_v35_v1g', 'm2_mix_v35'),
    'drv1_v23×sch': ('phys/sow6_run/run_v2/lvs/deckfix_v1/out_drv2v20_v23_drv1', 'm3_drv1_v23'),
    'drv2_v22×sch': ('phys/sow6_run/run_v2/lvs/deckfix_v1/out_drv2v20_drv2v22labels', 'm3_drv2_v22'),
}


def build_sow6():
    drcs = {k: {'dir': d, 'violations': _drc_items(d), 'runtime_s': _drc_runtime(d)}
            for k, d in SOW6_DRC_DIRS.items()}
    lvss = {k: _lvs_status(d, cell) for k, (d, cell) in SOW6_LVS.items()}
    memo_paths = sorted(set(glob.glob(os.path.join(WS, 'phys/top/判读纪要*.md'))
                            + glob.glob(os.path.join(WS, 'phys/top/回执*.md'))
                            + glob.glob(os.path.join(WS, 'phys/top/单元几何真值表*.md'))
                            + glob.glob(os.path.join(WS, 'phys/top/probe_viastack*.md'))))
    memo_info = [finfo(os.path.relpath(m, WS)) for m in memo_paths]
    n_runs = sum(1 for m in memo_paths if '代跑' in os.path.basename(m))
    gds = {}
    for k, rel in (('mix_v35', 'phys/top/m2_mix_v35.gds'),
                   ('drv1_v23', 'verify/drv1_v23_run/out/m3_drv1_v23.gds'),
                   ('drv2_v22', 'gds/m3_drv2_v22.gds')):
        if os.path.exists(os.path.join(WS, rel)):
            gds[k] = finfo(rel)
    lib = 'phys/top/lib13g2.py'
    return {'drc': drcs, 'lvs': lvss, 'memos': memo_info, 'n_memos': len(memo_info),
            'n_runs': n_runs, 'gds': gds,
            'lib_info': finfo(lib) if os.path.exists(os.path.join(WS, lib)) else None,
            'report_info': finfo('phys/report/SOW-6_全链版图报告.md')
            if os.path.exists(os.path.join(WS, 'phys/report/SOW-6_全链版图报告.md')) else None}


def main():
    force = '--force' in sys.argv
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if os.path.exists(OUT) and not force:
        age = time.time() - os.path.getmtime(OUT)
        if age < 3600:
            print(f'site.json 存在且新鲜（{age/60:.0f} 分钟前），跳过构建。加 --force 强制重建。')
            return
    t0 = time.time()
    S = {}
    S['meta'] = {
        'title': 'Wi-Fi 7（IEEE 802.11be）射频发射 TX 模组 · 设计交付全景',
        'sub': 'SOW-1 系统/行为级 → SOW-2 SG13G2 晶体管级（v014 终态结项）→ SOW-6 全链版图',
        'team': '组长 b7a0（WiFi7-TX-组长）· 电路 b7e7 · 仿真 fde9',
        'status': 'SOW-2 结项条件达成 · SOW-6 全链版图代跑推进中（v19 修复版三轮实证收口）',
        'tool': 'IHP SG13G2 开源 PDK · ngspice-47（晶体管级）· KLayout（版图/DRC/LVS）· Python 行为级（SOW-1）',
        'built_at': time.strftime('%Y-%m-%dT%H:%MZ', time.gmtime()),
    }
    print('· docs');     S['docs'] = build_docs()
    print('· netlists'); S['netlists'] = build_netlists()
    print('· figures');  S['figures'] = []
    for fn, (t, dsc) in FIG_TITLES.items():
        rel = 'design_circuit/figures/' + fn
        if not os.path.exists(os.path.join(WS, rel)):
            continue
        svg = open(os.path.join(WS, rel), encoding='utf-8').read()
        svg = re.sub(r'^\s*<\?xml[^>]*\?>', '', svg).strip()
        S['figures'].append({'name': fn, 'title': t, 'desc': dsc, 'svg_inline': svg, **finfo(rel)})
    print('· params');   S['params'] = build_params()
    print('· spec');     S['spec_table'] = build_spec_table()
    print('· op27');     S['op27'] = build_op27()
    print('· sp');       S['sp'] = build_sp()
    print('· tran');     S['tran'] = build_tran()
    print('· device');   S['device'] = build_device()
    print('· b1');       S['b1'] = build_b1()
    print('· phys');     S['phys'] = build_phys()
    print('· sow6');     S['sow6'] = build_sow6()
    S['iteration'] = build_iteration(S['op27']['versions'])
    print('· artifacts'); S['artifacts'] = build_artifacts()
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(S, f, ensure_ascii=False, separators=(',', ':'))
    sz = os.path.getsize(OUT)
    print(f'OK -> {OUT}  {sz/1e6:.2f} MB  {time.time()-t0:.1f}s')
    print('  op27 rows', len(S['op27']['rows']), '| axis', S['op27']['axis_pass'], '/',
          S['op27']['axis_total'], '| edge', S['op27']['edge_pass'], '/', S['op27']['edge_total'],
          '| spec iv', S['op27']['spec_iv'], '| kptat', S['op27']['kptat'])
    print('  sp decks', len(S['sp']['decks']), 'series', list(S['sp']['series']))
    print('  docs', len(S['docs']), 'netlists', sum(len(g['items']) for g in S['netlists']),
          'figures', len(S['figures']), 'artifacts', len(S['artifacts']))
    for ch in S['phys']['chips']:
        print(f"  phys {ch['key']:8s} DRC={ch['drc_final']['violations'] if ch['drc_final'] else '?'} "
              f"viol LVS={'match' if (ch['lvs'] or {}).get('match') else '?'} "
              f"pre={ch['pre_gain']} post={ch['post_gain']} dB drop={ch['drop_dB']}")
    print('  sow6 drc', {k: v['violations'] for k, v in S['sow6']['drc'].items()},
          '| lvs', {k: bool((v or {}).get('match')) for k, v in S['sow6']['lvs'].items()},
          '| memos', S['sow6']['n_memos'])


if __name__ == '__main__':
    main()
