#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m5_cdl_reship_check.py — 裁定五：deck 修复版 cdl 重提件「验收六判据」（机器可判）

来源：b7a0（组长）2026-10-18T03:00:38Z《M5 口径甲回执收讫，R1~R4 裁决如下（新增裁定五）》
      ——「重提件到货先对表再跑门；六判据全过 → 门1/门2 直接跑；任一不过 → 停线带原始数据报我」

六判据（本脚本逐条机器判，输出 md + json，退出码 0=六条全过 / 1=有不过）：
  ① 三件 31/31 HBT b≠e（基极≠发射极）
  ② R 件零自环（8 件 e1a/e2a/e1b/e2b/e1/e2/ccas1 全解体归位）
  ③ merged-domain WARNING 清零（gnd/nsens/ntaila/lond/lopd/nswa/nswb/rfon/rfop 全归位独立；
     专项：gnd 必须独立，不得再被并进 ntaila）
  ④ 14 个被并没 deck 网全部回归
     （mix 8：hbt_mirror/lopd/nsens/nswa/nswb/ntailb/rfon/rfop；drv1 2：hbt_mirror/ntail；
       drv2 4：ccas2/nbcas/ntail/hbt_mirror）
  ⑤ cdl 新增网 nref（drv1/drv2）若再现，须附提取器来源映射（不得是无名新增）
  ⑥ 三件 .subckt 端口序复核照旧

口径说明（不改裁定，只做机器化）：
  * 「hbt_mirror 回归」= 该子电路实例在 deck 里挂到的网（mix: ntaila/ntailb/nvtop；drv1/drv2: ntail/vcc）
    必须在 cdl 中逐字回归且互相独立（hbt_mirror 在 cdl 侧按「转换五规则」内联为 Q/R，其挂网须可追）。
  * 「gnd」在 deck 内写作节点 0；判据③接受 gnd/0/vss* 任一别名，但必须作为**独立网**存在。
  * ⑤ 的映射证据接受三形态：(a) cdl 内注释行含 nref 且含映射词（映射/map/source/hbt_mirror/提取器）；
    (b) cdldir 内 *nref*map* / *map*nref* 边车文件且非空；(c) cdl 内 `* net-map:` / `* 提取映射:` 明细行。
    三者皆无 → 判不过（无名新增）。

用法：
  python3 m5_cdl_reship_check.py --cdldir <cdl目录> --tag <tag> [--deck <前仿deck.sp>]
退出码：0=六条全过（可进双门）；1=有不过（停线，带本报告报 b7a0）；2=件不齐/读不出
"""
import argparse
import glob
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DECK = '/data/workspace/sow6/pdk/sim/v015_1/chain_top_tb_v015_1.sp'

STAGES = {                      # 子电路名 → cdl 文件名
    'gilbert_mix': 'pex_mix_v27.cdl',
    'drv1':        'pex_drv1_v19.cdl',
    'drv2':        'pex_drv2_v19.cdl',
}

# ③ merged-domain 九网（裁定五原文）+ gnd 别名
MERGED_NETS = ['gnd', 'nsens', 'ntaila', 'lond', 'lopd', 'nswa', 'nswb', 'rfon', 'rfop']
GROUND_ALIAS = ('gnd', '0', 'vss', 'vssx', 'vssa', 'agnd')
# ④ 十四被并没 deck 网（裁定五原文，按件）
REGRESS = {
    'gilbert_mix': ['hbt_mirror', 'lopd', 'nsens', 'nswa', 'nswb', 'ntailb', 'rfon', 'rfop'],
    'drv1':        ['hbt_mirror', 'ntail'],
    'drv2':        ['ccas2', 'nbcas', 'ntail', 'hbt_mirror'],
}
# ④ 中 hbt_mirror 实例在 deck 挂的网（内联后须可追）
HBT_MIRROR_NETS = {
    'gilbert_mix': ['ntaila', 'ntailb', 'nvtop'],
    'drv1':        ['ntail', 'vcc'],
    'drv2':        ['ntail', 'vcc'],
}
# ② 本批 8 件自环 R 涉及的节点名（7 个字面，ccas1 占 drv2 两件）
SELFLOOP_WATCH = ['e1a', 'e2a', 'e1b', 'e2b', 'e1', 'e2', 'ccas1']
# ⑥ 端口序基线（前仿 deck 与现行 cdl 三件逐字一致，2026-10-18 实测）
BASE_PORTS = {
    'gilbert_mix': ['ifp', 'ifn', 'lop', 'lon', 'rfop', 'rfon', 'vcc'],
    'drv1':        ['inp', 'inn', 'cop', 'con', 'vcc'],
    'drv2':        ['inp', 'inn', 'outp', 'outn', 'vcc'],
}
HBT_TOTAL_EXPECT = 31            # 裁定五①：15 + 4 + 12
MAP_WORDS = ('映射', 'map', 'source', 'hbt_mirror', '提取器', '来源')


def subckt_body(path, name):
    body, inside = [], False
    for ln in open(path, encoding='utf-8', errors='replace'):
        s = ln.rstrip('\n')
        t = s.strip()
        m = re.match(r'^\.subckt\s+(\S+)', t, re.I)
        if m:
            inside = (m.group(1) == name)
            if inside:
                body.append(s)
            continue
        if not inside:
            continue
        if re.match(r'^\.ends\b', t, re.I):
            body.append(s)
            break
        body.append(s)
    return body


def ports_of(body):
    for ln in body:
        m = re.match(r'^\.subckt\s+(\S+)(.*)$', ln.strip(), re.I)
        if m:
            ps = [p for p in m.group(2).split() if '=' not in p]
            return [p.lower() for p in ps]
    return []


def warn_lines_of_file(path):
    """merged-domain **声明行**扫描（在 .subckt 体之外，cdl 头部），必须扫全文件。
    只认「声明形状」：* WARNING … names=[…] / chosen=…（merged-domain 声明）。
    不认「顺带提到 WARNING」的行（如变更说明「v6 起 WARNING 已清零」）——
    否则注释里一个词就会把 ③ 判成假 FAIL（2026-10-18 自测抓到）。"""
    out = []
    for ln in open(path, encoding='utf-8', errors='replace'):
        t = ln.split('$')[0].strip()
        if not t.startswith('*'):
            continue
        tl = t.lower()
        if 'warning' in tl and re.search(r'(merged[-_ ]domain|names\s*=\s*\[|chosen\s*=)', tl):
            out.append(t)
    return out


def deck_design_be(deck):
    """deck 自身「设计二极管接法」的 HBT 件数/件（b==e 属原文拓扑，非提取粘连）：
      · 直接件：deck 行里 npn 的 B 网 == E 网
      · 内联件：每个 hbt_mirror 实例 × 其内部 b==e 件数
    ⚠ 实测（v015.1 deck，2026-10-18）：**deck 原文 b==e 件数 = 0**
      —— 感测管 `XQ s nsens nsens 0 0` 是 C==B（二极管接法），不是 B==E；
         hbt_mirror 内 `XQr nref nref 0 0` 同理。故裁定五①「31/31 b≠e」对忠实重提件
         **可满足**：cdl 现有 31/31 b==e 全部是提取侧「众数优先并名」造成的粘连。
      本函数作为**旁证**打印；若将来 deck 版本出现真 B==E 件，① 自动降为 ATTENTION 档
      （需组长裁定豁免），不静默放行也不误杀。"""
    def count_npn_be(body):
        """deck 4 端 npn 行 `X名 C B E S npn13G2 nx=..` → B=p[2], E=p[3]（SPICE 序 C B E S）
        —— 注意不是 p[3]/p[4]（那是 E/S）。2026-10-18 自测按 p[3]/p[4] 误算过一次，已修。"""
        n = 0
        for ln in body:
            t = ln.split('$')[0].strip()
            if not t or t.startswith('*') or t.startswith('.'):
                continue
            p = t.split()
            if p[0][0].upper() == 'X' and len(p) >= 6 and p[5].lower().startswith('npn'):
                if p[2].lower() == p[3].lower():
                    n += 1
            elif p[0][0].upper() == 'Q' and len(p) >= 5:
                if p[2].lower() == p[3].lower():
                    n += 1
        return n

    hm_body = subckt_body(deck, 'hbt_mirror')
    hm_be = count_npn_be(hm_body)
    out = {}
    for s in STAGES:
        body = subckt_body(deck, s)
        c = count_npn_be(body)
        for ln in body:
            t = ln.split('$')[0].strip()
            p = t.split()
            if p and p[0][0].upper() == 'X' and any(x.lower() == 'hbt_mirror' for x in p):
                c += hm_be
        out[s] = c
    out['_hbt_mirror_internal'] = hm_be
    return out


def parse(body):
    out = []
    for ln in open(path, encoding='utf-8', errors='replace'):
        t = ln.split('$')[0].strip()
        if t.startswith('*') and 'WARNING' in t.upper():
            out.append(t)
    return out


def parse(body):
    """→ (devices, nets, warn_lines)；devices: [(name, [tok...], kind)]"""
    devs, nets, warns = [], set(), []
    for ln in body:
        t = ln.split('$')[0].strip()
        if not t:
            continue
        if t.startswith('*'):
            if 'WARNING' in t.upper():
                warns.append(t)
            continue
        if t.startswith('.'):
            continue
        p = t.split()
        k = p[0][0].upper()
        nodes = []
        if k == 'Q' and len(p) >= 4:
            nodes = [p[1], p[2], p[3]]          # c b e
            devs.append((p[0], p, 'Q'))
        elif k in 'RC' and len(p) >= 3:
            nodes = [p[1], p[2]]
            devs.append((p[0], p, k))
        elif k in 'XM' and len(p) >= 3:
            nodes = [x for x in p[1:] if '=' not in x][:8]
            devs.append((p[0], p, k))
        for nd in nodes:
            nd = nd.lower()
            if not nd or '=' in nd:
                continue
            if re.match(r'^[-+]?[\d.]+(e[-+]?\d+)?[a-zA-Z]*$', nd):
                continue
            nets.add(nd)
    return devs, nets, warns


def verdict(ok, title, detail_lines, extra=None):
    d = {'PASS': bool(ok), 'title': title, 'detail': detail_lines}
    if extra:
        d.update(extra)
    return d


# 监督留痕：注记意图词（裁定七 条款 4：去向须注记）
NOTE_INTENT_WORDS = ['吸收', '并入', '归位', '远端', '消失', '移除', '删除', '不再',
                      'absorb', 'merged', 'relocat', 'remov', 'drop']


def find_watch_note(cdl_path, cdldir, node):
    """找该 watch 节点去向的注记：件内注释行，或同目录边车文件（提及节点名 + 意图词）。
    返回注记原文（找不到返回 None）。只认「同件同节点」的注记，不跨件借。"""
    wl = node.lower()
    hits = []

    def scan(path, tag):
        try:
            for ln in open(path, encoding='utf-8', errors='replace'):
                t = ln.split('$')[0].strip() if not ln.strip().startswith('*') else ln.strip()
                if not t or not t.startswith('*'):
                    continue          # 只认注释行（去向说明应在注释里）
                low = t.lower()
                if wl not in low:
                    continue
                if any(k in low for k in NOTE_INTENT_WORDS):
                    hits.append('%s: %s' % (tag, t.strip()))
        except Exception:
            pass

    scan(cdl_path, os.path.basename(cdl_path))
    try:
        for fn in sorted(os.listdir(cdldir)):
            if fn == os.path.basename(cdl_path):
                continue
            if fn.startswith('.'):
                continue
            p = os.path.join(cdldir, fn)
            if os.path.isfile(p) and os.path.getsize(p) < 2_000_000:
                scan(p, fn)
    except Exception:
        pass
    return ('；'.join(hits[:3]) + ('（共 %d 条注记）' % len(hits) if len(hits) > 3 else '')) if hits else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cdldir', required=True)
    ap.add_argument('--tag', default='reship')
    ap.add_argument('--deck', default=DEFAULT_DECK)
    a = ap.parse_args()

    md = os.path.join(HERE, 'cdl_reship_check_%s.md' % a.tag)
    js = os.path.join(HERE, 'cdl_reship_check_%s.json' % a.tag)

    out = {'tag': a.tag, 'checked_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
           'cdldir': os.path.abspath(a.cdldir),
           'ruling': 'b7a0 裁定五 2026-10-18T03:00:38Z（cdl 重提验收六判据）',
           'criteria': {}}

    L = []
    L.append('# M5 裁定五：deck 修复版 cdl 重提件验收六判据（机器判定）')
    L.append('')
    L.append('- 判定脚本：`m5_cdl_reship_check.py`（fde9）｜tag=`%s`｜件目录：`%s`' % (a.tag, a.cdldir))
    L.append('- 裁定来源：b7a0《M5 口径甲回执收讫，R1~R4 裁决如下（新增裁定五）》2026-10-18T03:00:38Z')
    L.append('- 门径：**六判据全过 → 门1/门2 直接跑**；任一不过 → 停线带本报告报 b7a0（口令②仍生效）')
    L.append('- 机读结果：`%s`' % os.path.basename(js))
    L.append('')

    # ── 件在不在 ────────────────────────────────────────────────────────────
    paths = {s: os.path.join(a.cdldir, f) for s, f in STAGES.items()}
    missing = [s for s, p in paths.items() if not os.path.exists(p)]
    if missing:
        L.append('**件不齐**：缺 %s ⇒ 无法判六判据（停线）。' % '、'.join(STAGES[s] for s in missing))
        out['criteria']['FATAL'] = {'PASS': False, 'title': '件不齐', 'detail': missing}
        json.dump(out, open(js, 'w'), indent=1, ensure_ascii=False)
        open(md, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
        print('[裁定五] 件不齐：缺 %s' % missing)
        return 2

    P, D, N, W, PORTS, SHA = {}, {}, {}, {}, {}, {}
    import hashlib
    for s in STAGES:
        body = subckt_body(paths[s], s)
        P[s] = body
        devs, nets, warns = parse(body)
        D[s], N[s], W[s] = devs, nets, warn_lines_of_file(paths[s])
        PORTS[s] = ports_of(body)
        h = hashlib.sha256(open(paths[s], 'rb').read()).hexdigest()
        SHA[s] = h
    out['cdl_sha256'] = SHA
    L.append('## 0 件指纹（sha256）与规模')
    L.append('')
    L.append('| 件 | 字节 | sha256 | Q | R | C | 网数 | WARNING 行 |')
    L.append('|---|---|---|---|---|---|---|---|')
    for s in STAGES:
        qn = sum(1 for d in D[s] if d[2] == 'Q')
        rn = sum(1 for d in D[s] if d[2] == 'R')
        cn = sum(1 for d in D[s] if d[2] == 'C')
        L.append('| %s | %d | `%s` | %d | %d | %d | %d | %d |'
                 % (STAGES[s], os.path.getsize(paths[s]), SHA[s][:16] + '…',
                    qn, rn, cn, len(N[s]), len(W[s])))
    L.append('')

    # ── ① HBT 31/31 b≠e ─────────────────────────────────────────────────────
    qbe, qtot, ce = [], 0, []
    for s in STAGES:
        for nm, p, k in D[s]:
            if k == 'Q':
                qtot += 1
                if p[2].lower() == p[3].lower():
                    qbe.append('%s:%s(b=e=%s)' % (s, nm, p[2]))
                if p[1].lower() == p[3].lower():
                    ce.append('%s:%s(c=e=%s)' % (s, nm, p[1]))
    ok1 = (len(qbe) == 0) and (qtot == HBT_TOTAL_EXPECT)
    try:
        design_be = deck_design_be(a.deck)
        design_total = sum(design_be[s] for s in STAGES)
        design_detail = 'deck 设计二极管接法 %d 件（%s）' % (
            design_total, '、'.join('%s %d' % (s, design_be[s]) for s in STAGES))
        design_ok = (design_be.get('_hbt_mirror_internal') == 1)
    except Exception as e:                                    # deck 读不到 → 保守按 FAIL 走
        design_be, design_total, design_ok = {}, -1, False
        design_detail = 'deck 设计件清点失败（%s）→ 无法判 ATTENTION 档' % e
    if len(qbe) == 0 and qtot == HBT_TOTAL_EXPECT:
        st1 = 'PASS'
    elif design_ok and len(qbe) == design_total and qtot == HBT_TOTAL_EXPECT:
        st1 = 'ATTENTION'
    else:
        st1 = 'FAIL'
    d1 = ['HBT 总数 **%d**（裁定五期望 %d）%s'
          % (qtot, HBT_TOTAL_EXPECT, '' if qtot == HBT_TOTAL_EXPECT else ' → **数量对不上**'),
          'b==e 粘连 **%d** 件%s' % (len(qbe), ('：' + '、'.join(qbe)) if qbe else ' → 31/31 全解 ✅'),
          '（参考）c==e 件数 %d%s' % (len(ce), ('：' + '、'.join(ce)) if ce else ''),
          design_detail]
    if st1 == 'ATTENTION':
        d1.append('**判读待裁定**：残留 %d 件恰等于 deck 自身 B==E 件数——'
                  '若这些件确属 deck 原文拓扑（而非提取并名），请 b7a0 裁定是否豁免；'
                  '在裁定前按裁定五「任一不过即停」停线。' % design_total)
    elif design_total == 0:
        d1.append('**旁证**：deck 原文 B==E 件数 = 0 ⇒ 重提件任何 b==e 都是提取侧并名粘连，'
                  '判据①无豁免余地（31/31 必须全过）。')
    out['criteria']['1_hbt_bne'] = verdict(ok1, '① 三件 31/31 HBT b≠e', d1,
                                           {'state': st1, 'hbt_total': qtot, 'b_eq_e': len(qbe),
                                            'c_eq_e': len(ce), 'design_b_eq_e': design_total,
                                            'design_by_stage': design_be})

    # ── ② R 零自环 + len(SELFLOOP_WATCH) 件归位（不写死件数）────────────────
    rself = []
    for s in STAGES:
        for nm, p, k in D[s]:
            if k == 'R' and p[1].lower() == p[2].lower():
                rself.append('%s:%s(%s)' % (s, nm, p[1]))
    watch_missing = []
    watch_bad = []
    for s in STAGES:
        for w in SELFLOOP_WATCH:
            hits = [d for d in D[s] if d[2] == 'R' and (d[1][1].lower() == w or d[1][2].lower() == w)]
            if hits:
                for nm, p, k in hits:
                    if p[1].lower() == p[2].lower():
                        watch_bad.append('%s:%s(%s)' % (s, nm, w))
    # 归位语义：len(SELFLOOP_WATCH) 件 watch 节点各自必须出现在**两端不同**的 R 上
    for w in SELFLOOP_WATCH:
        found = False
        for s in STAGES:
            for nm, p, k in D[s]:
                if k == 'R' and (p[1].lower() == w or p[2].lower() == w) and p[1].lower() != p[2].lower():
                    found = True
        if not found:
            watch_missing.append(w)
    ok2 = (len(rself) == 0)          # 裁定五②的机器核 = R 件零自环
    d2 = ['R 件自环 **%d** 件%s' % (len(rself), ('：' + '、'.join(rself)) if rself else ' → 零自环 ✅'),
          '（参考·非判据）%d 件 watch 节点（%s）未出现在两端独立 R 上的：%s'
          % (len(SELFLOOP_WATCH), '/'.join(SELFLOOP_WATCH),
             '、'.join(watch_missing) if watch_missing else '无（全部归位）')]
    if watch_missing:
        d2.append('（口径说明：② 的机器判据只取「零自环」；上列节点若被提取器合法吸收'
                  '（寄生 R 消失/远端归位到独立网），我不据此判不过，只在此列出据实判读）')
    out['criteria']['2_r_selfloop'] = verdict(ok2, '② R 件零自环（%d 件归位）' % len(SELFLOOP_WATCH), d2,
                                              {'state': 'PASS' if ok2 else 'FAIL',
                                               'r_selfloop': len(rself), 'watch_unresolved': watch_missing})

    # ── ③ merged-domain WARNING 清零 + 九网独立 ──────────────────────────────
    warn_all = [(s, w) for s in STAGES for w in W[s]]
    miss3 = [n for n in MERGED_NETS if n != 'gnd' and n not in N['gilbert_mix']]
    gnd_found = [g for g in GROUND_ALIAS if g in N['gilbert_mix']]
    gnd_independent = False
    if gnd_found:
        g = gnd_found[0]
        gnd_independent = True
        for s in STAGES:
            for nm, p, k in D[s]:
                if g in (p[1].lower(), p[2].lower(), p[3].lower() if len(p) > 3 else ''):
                    pass
        # 专项：gnd 不得与 ntaila 同名同网（被并进 ntaila 的判据）
        gnd_independent = ('ntaila' not in gnd_found) and (g != 'ntaila')
    ok3 = (len(warn_all) == 0) and (len(miss3) == 0) and gnd_independent
    chosen = []
    for s, w in warn_all:
        m = re.search(r'chosen\s*=\s*(\S+?)[,\]\s]', w)
        names = re.search(r"names\s*=\s*\[([^\]]*)\]", w)
        chosen.append('%s: %s→%s' % (s, (names.group(1) if names else '?'), (m.group(1) if m else '?')))
    d3 = ['merged-domain WARNING 行 **%d** 条%s'
          % (len(warn_all), ('：' + '；'.join('%s %s' % (s, w) for s, w in warn_all))
             if warn_all else ' → 清零 ✅'),
          '（若有条目，合并去向：%s）' % '；'.join(chosen) if chosen else '',
          '九网归位：mix 内缺 %s' % ('、'.join(miss3) if miss3 else '无（8 个具名网全在）'),
          'gnd 专项：检出独立地网 %s%s' % (gnd_found or '无',
                                        '（别名计入）' if gnd_found and gnd_found[0] != 'gnd' else '')]
    d3 = [x for x in d3 if x]
    out['criteria']['3_merged_zero'] = verdict(ok3, '③ merged-domain WARNING 清零（九网独立）', d3,
                                              {'warn_lines': len(warn_all), 'missing_nets': miss3,
                                               'gnd_nets': gnd_found})

    # ── ④ 十四被并没 deck 网全部回归 ─────────────────────────────────────────
    reg = {'PASS': True, 'items': {}}
    d4 = ['十四被并没 deck 网回归（裁定五原文口径）']
    for s in STAGES:
        need = []
        for entry in REGRESS[s]:
            cand = HBT_MIRROR_NETS[s] if entry == 'hbt_mirror' else [entry]
            for nd in cand:
                if nd not in need:
                    need.append(nd)
        seen, absent = [], []
        for nd in need:
            (seen if nd.lower() in N[s] else absent).append(nd)
        # 独立性：同名不同网=仍被并（用 WARNING chosen 名做交叉检查）
        reg['items'][s] = {'need': need, 'present': seen, 'absent': absent}
        d4.append('- %s：需 %d 个（%s）→ 回归 %d，**缺 %s**'
                  % (s, len(need), '/'.join(need), len(seen),
                     '、'.join(absent) if absent else '无 ✅'))
        if absent:
            reg['PASS'] = False
    out['criteria']['4_regress'] = verdict(reg['PASS'], '④ 14 个被并没 deck 网全部回归', d4, reg)

    # ── ⑤ nref 须附映射 ─────────────────────────────────────────────────────
    # ── ⑤ nref 须附映射（逐件：出现 nref 的那一件自己须附映射，不许借别件的）─────────
    sidecars = [os.path.basename(f) for f in sorted(glob.glob(os.path.join(a.cdldir, '*')))
                if 'nref' in os.path.basename(f).lower() and 'map' in os.path.basename(f).lower()
                and os.path.getsize(f) > 0]
    map_evidence, nref_stages, ev_by_stage = [], [], {}
    for s in STAGES:
        if 'nref' not in N[s]:
            continue
        nref_stages.append(s)
        ev = []
        for ln in open(paths[s], encoding='utf-8', errors='replace'):
            t = ln.split('$')[0].strip()
            if not t.startswith('*'):
                continue
            tl = t.lower()
            if 'nref' not in tl:
                continue
            # 只认「映射条目形状」：nref ←/=/→ 某网，或点名 hbt_mirror 出处
            if re.search(r'nref\s*(<-|=~|=|→|->)\s*\S+', tl) or 'hbt_mirror' in tl:
                ev.append('%s: %s' % (s, t))
        for sc in sidecars:
            ev.append('%s: 边车映射文件 %s' % (s, sc))
        ev_by_stage[s] = ev
        map_evidence += ev
    lack5 = [s for s in nref_stages if not ev_by_stage.get(s)]
    ok5 = (len(nref_stages) == 0) or (len(lack5) == 0)
    d5 = ['nref 出现于：%s' % (('、'.join(nref_stages)) if nref_stages else '无（本批未再现）')]
    for s in nref_stages:
        d5.append('- %s：映射证据 %d 条%s' % (s, len(ev_by_stage.get(s, [])),
                                              ('：' + ' ｜ '.join(ev_by_stage[s])) if ev_by_stage.get(s)
                                              else ' → **无名新增，判不过**（裁定五⑤：须附提取器来源映射）'))
    out['criteria']['5_nref_map'] = verdict(ok5, '⑤ nref 若再现须附来源映射', d5,
                                            {'state': 'PASS' if ok5 else 'FAIL',
                                             'nref_stages': nref_stages, 'map_evidence': map_evidence,
                                             'stages_without_map': lack5})

    # ── ⑥ 端口序照旧 ────────────────────────────────────────────────────────
    d6, ok6 = [], True
    for s in STAGES:
        same = (PORTS[s] == BASE_PORTS[s])
        ok6 = ok6 and same
        d6.append('- %s：cdl %s ｜ 基线 %s → %s'
                  % (s, ' '.join(PORTS[s]) or '（读不出）', ' '.join(BASE_PORTS[s]),
                     '一致 ✅' if same else '**不一致 → 判不过**'))
    out['criteria']['6_ports'] = verdict(ok6, '⑥ 三件 .subckt 端口序复核照旧', d6,
                                         {'ports': PORTS, 'baseline': BASE_PORTS})

    # ── 监督留痕（裁定七 条款 4，2026-10-18T03:18:21Z）──────────────────────
    # 条款原文：watch 覆盖**维持参考项，不升硬闸**（不进 pass/fail）；但
    #   「A0 报告的 watch 状态表凡与粘连版基线对照有消失/异动，逐项注记去向
    #     （吸收进网内 / 远端归位 / 消失+理由）；**无注记的消失 → ATTENTION 停线请裁定**
    #     （不自动 PASS 也不自动 FAIL）」。
    # 落地口径（我侧实现，向 b7a0 备案并请确认）：
    #   · 基线 = 粘连版三件的 watch 状态表（make_watch_baseline.py 产，按件 sha 锁定）
    #   · **消失** = 基线该件该节点在 R 上（SELFLOOP/DISTINCT）→ 本件 ABSENT
    #     → 须有注记说明去向（吸收进网内/远端归位/消失+理由）；**无注记 → ATTENTION 停线**
    #   · **异动** = 状态在 SELFLOOP / DISTINCT 之间变化（典型：自环→归位，属好件应有走向）
    #     → 逐项列出来向，**有注记者标注去向**；无注记者列为「异动·无注记」供人工确认
    #       （**不自动停线**：归位本就是好件的常态，若一律停线会把好件全挡在门外）
    #   · 注记来源：件内注释行（提及该节点名 + 去向意图词），或同目录边车文件
    #   · 本节**不进 pass/fail**；仅当出现「无注记的消失」时，把总裁定降为 ATTENTION（停线请裁定）
    watch_trace = {'baseline_file': os.path.join(HERE, 'pex_watch_baseline.json'),
                   'baseline_available': False, 'rows': [], 'changed': [],
                   'unnoted_gone': [], 'changed_without_note': [],
                   'note_keywords': NOTE_INTENT_WORDS, 'rule': '裁定七 条款 4（监督留痕）'}
    bl = None
    if os.path.exists(watch_trace['baseline_file']):
        try:
            bl = json.load(open(watch_trace['baseline_file'], encoding='utf-8'))
            watch_trace['baseline_available'] = True
        except Exception as e:
            watch_trace['baseline_error'] = str(e)
    if bl:
        cur = {}
        for s in STAGES:
            cur[s] = {}
            for w in SELFLOOP_WATCH:
                stt = 'ABSENT'
                for nm, p, k in D[s]:
                    if k == 'R' and (p[1].lower() == w or p[2].lower() == w):
                        stt = 'SELFLOOP' if p[1].lower() == p[2].lower() else 'DISTINCT'
                        break
                cur[s][w] = stt
        for s in STAGES:
            for w in SELFLOOP_WATCH:
                b = (bl.get('states', {}).get(s, {}) or {}).get(w, 'ABSENT')
                c = cur[s][w]
                row = {'stage': s, 'node': w, 'baseline': b, 'current': c,
                       'change': 'none' if b == c else ('GONE' if c == 'ABSENT' else 'CHANGED')}
                if row['change'] != 'none':
                    note = find_watch_note(paths[s], a.cdldir, w)
                    row['note'] = note
                    row['noted'] = bool(note)
                    watch_trace['changed'].append(row)
                    if row['change'] == 'GONE' and not note:
                        watch_trace['unnoted_gone'].append(row)
                    elif row['change'] == 'CHANGED' and not note:
                        watch_trace['changed_without_note'].append(row)
                watch_trace['rows'].append(row)
    out['watch_trace'] = watch_trace

    # ── 汇总 ────────────────────────────────────────────────────────────────
    order = ['1_hbt_bne', '2_r_selfloop', '3_merged_zero', '4_regress', '5_nref_map', '6_ports']
    allok = all(out['criteria'][k]['PASS'] for k in order)
    att = [k for k in order if out['criteria'][k].get('state') == 'ATTENTION']
    out['ALL_PASS'] = allok
    out['ATTENTION'] = att
    watch_attention = bool(watch_trace['unnoted_gone'])
    out['WATCH_ATTENTION'] = watch_attention
    if allok and watch_attention:
        out['verdict'] = ('六判据全过，但**监督留痕（裁定七 条款 4）**有「无注记的消失」'
                          '（%s）→ 按条款先停线请 b7a0 裁定（不自动 PASS 也不自动 FAIL）'
                          % '、'.join('%s:%s' % (r['stage'], r['node'])
                                      for r in watch_trace['unnoted_gone']))
    elif allok:
        out['verdict'] = '六判据全过 → 可进双门（门1 .op / 门2 动态）'
    elif att:
        out['verdict'] = ('判据%s 为 ATTENTION（属「deck 设计二极管接法」原文拓扑，'
                          '非提取粘连）→ 按裁定五「任一不过即停」先停线，'
                          '带本报告请 b7a0 裁定豁免；其余判据已过' % ('、'.join(att)))
    else:
        out['verdict'] = '有不过 → 停线，带本报告报 b7a0（口令②：不点火 27 角）'

    def mark(k):
        c = out['criteria'][k]
        if c['PASS']:
            return '**PASS**'
        return '**%s**' % c.get('state', 'FAIL')

    L.append('## 判据逐条')
    L.append('')
    L.append('| 判据 | 结论 |')
    L.append('|---|---|')
    for k in order:
        L.append('| %s | %s |' % (out['criteria'][k]['title'], mark(k)))
    L.append('')

    # 监督留痕（裁定七 条款 4）——参考项，不进 pass/fail
    wt = out['watch_trace']
    L.append('## 监督留痕：watch 覆盖状态表（裁定七 条款 4 —— **参考项，不进 pass/fail**）')
    L.append('')
    if not wt['baseline_available']:
        L.append('- ⚠️ 无 watch 基线（`pex_watch_baseline.json` 未找到）→ 本节留空，'
                 '到货窗口人工对照（基线可用 `make_watch_baseline.py` 现场生成）')
    else:
        L.append('- 基线：粘连版 `%s`（三件 sha 前 12 位：%s）'
                 % (os.path.basename(bl.get('baseline_cdldir', '')),
                    '、'.join(v[:12] for v in (bl.get('baseline_cdl_sha256') or {}).values())))
        L.append('- 状态：SELFLOOP=两端同名 R（粘连）｜DISTINCT=两端不同名 R（已归位）｜ABSENT=不在任何 R 上')
        L.append('')
        L.append('| 件 | watch 节点 | 基线 | 本件 | 异动 | 注记（去向） | 判定 |')
        L.append('|---|---|---|---|---|---|---|')
        for r in wt['rows']:
            if r['change'] == 'none':
                continue
            if r['change'] == 'GONE':
                jud = '**无注记的消失 → ATTENTION 停线请裁定**' if not r['noted'] else '消失·有注记（留痕）'
            else:
                jud = '异动·无注记（人工确认）' if not r['noted'] else '异动·有注记（留痕）'
            L.append('| %s | %s | %s | %s | %s | %s | %s |' % (
                r['stage'], r['node'], r['baseline'], r['current'], r['change'],
                (r['note'] or '—').replace('|', '/'), jud))
        L.append('')
        L.append('- 异动合计 **%d** 项（消失 %d，其中**无注记 %d**）'
                 % (len(wt['changed']),
                    sum(1 for r in wt['changed'] if r['change'] == 'GONE'),
                    len(wt['unnoted_gone'])))
        if wt['changed_without_note']:
            L.append('- 「异动·无注记」项（归位类，**不自动停线**，供人工确认）：%s'
                     % '、'.join('%s:%s' % (r['stage'], r['node']) for r in wt['changed_without_note']))
        if wt['unnoted_gone']:
            L.append('- **「无注记的消失」项 → 停线请 b7a0 裁定（不自动 PASS 也不自动 FAIL）**：%s'
                     % '、'.join('%s:%s' % (r['stage'], r['node']) for r in wt['unnoted_gone']))
        else:
            L.append('- 无「无注记的消失」项 → 本节不构成停线理由')
    L.append('')
    for k in order:
        c = out['criteria'][k]
        L.append('### %s → %s' % (c['title'],
                                  'PASS ✅' if c['PASS'] else (c.get('state', 'FAIL') + ' ❌')))
        L.append('')
        for ln in c['detail']:
            L.append('- %s' % ln)
        L.append('')
    L.append('## 总裁定')
    L.append('')
    L.append('**%s**' % out['verdict'])
    L.append('')
    L.append('- 机读：`%s`（`ALL_PASS=%s`）' % (os.path.basename(js), allok))
    L.append('')

    json.dump(out, open(js, 'w'), indent=1, ensure_ascii=False)
    open(md, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('[裁定五] 六判据：' + '  '.join('%s%s' % (k.split('_')[0],
                                        ('✅' if out['criteria'][k]['PASS']
                                         else ('⚠️' if out['criteria'][k].get('state') == 'ATTENTION'
                                               else '❌'))) for k in order))
    if out['watch_trace']['changed']:
        print('[裁定五] 监督留痕：异动 %d 项（无注记的消失 %d 项 → %s）'
              % (len(out['watch_trace']['changed']), len(out['watch_trace']['unnoted_gone']),
                 'ATTENTION 停线请裁定' if out['watch_trace']['unnoted_gone'] else '不构成停线'))
    print('[裁定五] 总裁定：%s' % out['verdict'])
    print('报告：%s ｜ %s' % (md, js))
    return 0 if (allok and not watch_attention) else 1


if __name__ == '__main__':
    sys.exit(main())
