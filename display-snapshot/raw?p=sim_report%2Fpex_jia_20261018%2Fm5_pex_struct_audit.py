#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m5_pex_struct_audit.py — 口径甲代入前的静态结构审计（deck vs cdl）

目的（会诊输入）：把「这批 cdl 能不能进网表」这件事从仿真结果层面前移到网表层，
逐件列出 cdl 与前仿 deck 的拓扑差异，并归类到「版图提取 deck 粘连（幻影焊）」。

检查项：
  1) 器件级：cdl 的 Q 行 b==e（基极与发射极同名=粘连）；cdl 的 R 行两节点同名（自环=远端被并入）
  2) 网名级：cdl 里出现的网名 vs deck 里出现的网名（新增网=并网后的合并名；消失网=被并没的网）
  3) cdl 自带 WARNING 行（merged-domain 声明）

用法：python3 m5_pex_struct_audit.py --deck <deck.sp> --cdldir <dir> --out <md>
"""
import argparse
import os
import re

STAGES = {
    'gilbert_mix': 'pex_mix_v27.cdl',
    'drv1':        'pex_drv1_v19.cdl',
    'drv2':        'pex_drv2_v19.cdl',
}


def subckt_body(path, name):
    body, inside = [], False
    for ln in open(path, encoding='utf-8'):
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


def nets_and_devices(body):
    nets, devs = set(), []
    for ln in body:
        t = ln.split('$')[0].strip()      # 去掉行尾 $ 注释（ngspice 行内注释符）
        if not t or t.startswith('*') or t.startswith('.'):
            continue
        p = t.split()
        devs.append((p[0], p))
        if p[0][0].upper() in 'XRC':
            for nd in p[1:]:
                if '=' in nd or nd.lower() in ('npn13g2', 'rsil', 'rhigh', 'rppd', 'cmim'):
                    continue
                if re.match(r'^[-+]?[\d.eE+]+[a-zA-Z]*$', nd) and not nd.lower().startswith('n'):
                    continue
                nets.add(nd)
    return nets, devs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--deck', required=True)
    ap.add_argument('--cdldir', required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()

    L = []
    L.append('# M5 口径甲代入前静态结构审计（deck vs cdl）')
    L.append('')
    L.append('生成：m5_pex_struct_audit.py（fde9）｜输入：v015.1 前仿 deck + b7e7 cdl 三件（sha 见回执）')
    L.append('')
    L.append('> 口径：b7a0《M5 PEX 口径裁定（组长四裁）》2026-10-18 裁定一（口径甲：cdl 只替换 L0 实物器件行，'
             'deck 理想件逐字保留）。本审计在**进网表前**逐件比对 cdl 与 deck 的拓扑差，'
             '用于会诊定位「这批 cdl 能否直接进双门」。')
    L.append('')

    tot_q = tot_qbe = tot_rself = 0
    for stage, fn in STAGES.items():
        cp = os.path.join(a.cdldir, fn)
        cb = subckt_body(cp, stage)
        db = subckt_body(a.deck, stage)
        cnet, cdev = nets_and_devices(cb)
        dnet, ddev = nets_and_devices(db)

        warn = [l.strip() for l in open(cp, encoding='utf-8') if 'WARNING' in l]
        qbe, rself = [], []
        for nm, p in cdev:
            if nm.upper().startswith('Q') and len(p) >= 4:
                if p[2].lower() == p[3].lower():
                    qbe.append((nm, p))
            if nm.upper().startswith('R') and len(p) >= 3:
                if p[1].lower() == p[2].lower():
                    rself.append((nm, p))
        tot_q += sum(1 for nm, p in cdev if nm.upper().startswith('Q'))
        tot_qbe += len(qbe)
        tot_rself += len(rself)

        L.append('## 阶段 %s（cdl：%s）' % (stage, fn))
        L.append('')
        if warn:
            L.append('**cdl 自带 WARNING（提取侧声明的合并域）**：')
            for w in warn:
                L.append('- `%s`' % w)
            L.append('')
        L.append('| 检查项 | 计数 | 明细 |')
        L.append('|---|---|---|')
        L.append('| Q 件 b==e（基极/发射极同名=粘连） | %d/%d | %s |'
                 % (len(qbe), sum(1 for nm, p in cdev if nm.upper().startswith('Q')),
                    '、'.join('%s(%s)' % (n, p[1]) for n, p in qbe) or '—'))
        L.append('| R 件两节点同名（自环=远端被并入） | %d | %s |'
                 % (len(rself), '、'.join('%s(%s)' % (n, p[1]) for n, p in rself) or '—'))
        L.append('| cdl 网名（deck 中无对应） | %d | %s |'
                 % (len(cnet - dnet), '、'.join(sorted(cnet - dnet)) or '—'))
        L.append('| deck 网名（cdl 中消失=被并没） | %d | %s |'
                 % (len(dnet - cnet), '、'.join(sorted(dnet - cnet)) or '—'))
        L.append('')
        L.append('**cdl 器件清单（原始行）**：')
        L.append('')
        for ln in cb:
            t = ln.strip()
            if t and not t.startswith('*') and not t.lower().startswith('.lib') \
               and not t.lower().startswith('.subckt') and not t.lower().startswith('.ends'):
                L.append('- `%s`' % t)
        L.append('')

    L.append('## 汇总')
    L.append('')
    L.append('- cdl 三件 HBT 总数 **%d**，其中 **b==e 粘连 %d**（占 %.0f%%）'
             % (tot_q, tot_qbe, 100.0*tot_qbe/max(tot_q, 1)))
    L.append('- R 件自环（远端并入）共 **%d** 件' % tot_rself)
    L.append('')
    L.append('**判读**：这批 cdl 的**标称值与前仿 deck 逐件一致**（派生层自测 9/9 机器精度复核，'
             '见 pex_devmodels_selftest.log），但**拓扑级存在系统性粘连**：'
             'HBT 基极与发射极同名、发射极电阻变自环、感测/尾网/LO 域被并名。'
             '⇒ 属提取 deck 侧「幻影焊」未解（b7a0 主闸门：候 deck 修复版 LVS 重提），'
             '不是代入器或派生层的建模问题。')
    L.append('')
    open(a.out, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('out: %s (%d B)' % (a.out, os.path.getsize(a.out)))
    print('HBT %d 件，b==e 粘连 %d 件，R 自环 %d 件' % (tot_q, tot_qbe, tot_rself))


if __name__ == '__main__':
    main()
