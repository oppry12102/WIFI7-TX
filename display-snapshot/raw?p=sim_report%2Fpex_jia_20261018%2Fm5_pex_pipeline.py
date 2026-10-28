#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""m5_pex_pipeline.py — M5 PEX 一键链：静态审计 → 口径甲代入 → 门1(.op) → 门2(动态) → 27 角

用途：b7e7 的 deck 修复版 cdl 到货后，一条命令跑完全链；每级自带**硬闸**，
任何一级不过即停并写报告（不越级、不自调参、不过门不点火 PVT）。

级与闸：
  A 静态审计   ：cdl 的 HBT b==e 粘连数必须 = 0（否则不���进网表）——本轮 cdl 31/31 粘连即在此拦下
  B 口径甲代入 ：m5_pex_substitute_jia.py（端口序核对 + 逐件映射日志）
  C 门1 快筛 .op：ngspice .op 必须有解；再 m5_pex_op_gate.py 判 A0′≤1e-5（ref=前仿 typ_v015_1.raw）
  D 门2 动态    ：tran 2.5us（5.51G 窗 [60,560]ns）+ m5_parse_pex_tran.py 判 |ΔCG|≤0.05 dB（锚 17.4465）
  E 27 角       ：仅当 C、D 双过才跑 sow6_pvt27_runner.py（工程门 0.5 dB 判读在 E 之后）

用法：
  python3 m5_pex_pipeline.py --cdldir <cdl目录> --tag <tag> [--stage A|B|C|D|E|all] [--force]
  # --force：即使 cdl sha 未变也继续（默认：sha 与已知粘连件相同则只跑 A 级并停）
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
WS = '/data/workspace'
SIM = os.path.join(WS, 'sow6/pdk/sim/v015_1')
NG = '/data/workspace/tools/ngspice-root/usr/bin/ngspice'
ENVLIB = '/data/workspace/tools/runtime/usr/lib/x86_64-linux-gnu'
CDLS = {'mix': 'pex_mix_v27.cdl', 'drv1': 'pex_drv1_v19.cdl', 'drv2': 'pex_drv2_v19.cdl'}
KNOWN_BAD_SHA = {   # 2026-10-18 02:5xZ 实测：31/31 HBT b==e 粘连，OP 无解
    'pex_mix_v27.cdl': '33e9e75451ab5cb8e222ca6f728ff2a1514bbffefa8011b4ee6852be9c8ac07b',
    'pex_drv1_v19.cdl': 'ae4feb76076ae01c64d17a75009ef6936f7d7f1199a0e366ab32f2b0d2d00e3d',
    'pex_drv2_v19.cdl': '1f5e0cd837b9af17cc36f2c1e6c6ddc1d0804b87dbedcb9c2b7cba211f373bf8',
}


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def run(cmd, cwd=None, env=None, timeout=3600, log=None):
    e = dict(os.environ)
    if env:
        e.update(env)
    t0 = time.time()
    if log:
        with open(log, 'w') as lf:
            r = subprocess.run(cmd, stdout=lf, stderr=subprocess.STDOUT, cwd=cwd, env=e, timeout=timeout)
    else:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=e, timeout=timeout)
    return r, time.time() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cdldir', required=True)
    ap.add_argument('--tag', default='fix')
    ap.add_argument('--stage', default='all')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--ignore-a-gate', action='store_true',
                    help='仅供脚本自测：跳过 A 级粘连闸（不用于正式跑件）')
    a = ap.parse_args()

    out = {'tag': a.tag, 'started_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
           'cdldir': a.cdldir, 'stages': {}}
    resfile = os.path.join(HERE, 'm5_pex_pipeline_%s.json' % a.tag)
    res = out

    def save():
        json.dump(res, open(resfile, 'w'), indent=1, ensure_ascii=False)

    # ── A 静态审计 ───────────────────────────────────────────────────────────
    audit_md = os.path.join(HERE, 'pex_struct_audit_%s.md' % a.tag)
    r, dt = run([sys.executable, os.path.join(HERE, 'm5_pex_struct_audit.py'),
                 '--deck', os.path.join(SIM, 'chain_top_tb_v015_1.sp'),
                 '--cdldir', a.cdldir, '--out', audit_md])
    txt = open(audit_md, encoding='utf-8').read()
    m = re.search(r'HBT (\d+) 件，b==e 粘连 (\d+) 件，R 自环 (\d+) 件', r.stdout or '')
    shas = {k: sha256(os.path.join(a.cdldir, v)) for k, v in CDLS.items()}
    res['stages']['A_audit'] = {'HBT_total': int(m.group(1)) if m else None,
                                'b_eq_e': int(m.group(2)) if m else None,
                                'R_selfloop': int(m.group(3)) if m else None,
                                'cdl_sha256': shas, 'audit_md': audit_md}
    save()
    if not a.force and all(shas[k] == KNOWN_BAD_SHA[CDLS[k]] for k in shas):
        res['stages']['A_audit']['stop'] = 'cdl sha 与已知粘连件相同（未换新件）；--force 可强推'
        save()
        print('[A] cdl 未更新（sha 仍为已知粘连件）→ 停。%s' % resfile)
        return
    if m and int(m.group(2)) > 0 and not a.ignore_a_gate:
        res['stages']['A_audit']['stop'] = 'HBT b==e 粘连 %s 件 > 0 → 不进网表（提取侧幻影焊未解）' % m.group(2)
        save()
        print('[A] 粘连未解 → 停：%s' % res['stages']['A_audit']['stop'])
        return
    print('[A] 静态审计通过：无 b==e 粘连')

    if a.stage == 'A':
        save(); return

    # ── B 口径甲代入 ────────────────────────────────────────────────────────
    deck_full = os.path.join(SIM, 'chain_top_tb_v015_1_pex_%s.sp' % a.tag)
    deck_op = os.path.join(SIM, 'chain_top_tb_v015_1_pex_%s_op.sp' % a.tag)
    tran_raw = os.path.join(HERE, 'pex_%s_tran.raw' % a.tag)
    op_raw = os.path.join(HERE, 'pex_%s_op.raw' % a.tag)
    maplog = os.path.join(HERE, 'pex_subst_audit_%s.md' % a.tag)
    r, _ = run([sys.executable, os.path.join(HERE, 'm5_pex_substitute_jia.py'),
                '--deck', os.path.join(SIM, 'chain_top_tb_v015_1.sp'),
                '--cdldir', a.cdldir, '--out', deck_full,
                '--tran-raw', tran_raw, '--audit', maplog])
    r2, _ = run([sys.executable, os.path.join(HERE, 'm5_pex_substitute_jia.py'),
                 '--deck', os.path.join(SIM, 'chain_top_tb_v015_1.sp'),
                 '--cdldir', a.cdldir, '--out', deck_op, '--op-only',
                 '--audit', maplog + '.op'])
    res['stages']['B_substitute'] = {'deck_full': deck_full, 'deck_sha256': sha256(deck_full),
                                     'deck_op': deck_op, 'maplog': maplog,
                                     'rc': (r.returncode, r2.returncode)}
    save()
    if r.returncode or r2.returncode:
        print('[B] 代入失败：%s %s' % (r.stdout[-300:], r.stdout[-300:])); return
    print('[B] 口径甲代入完成：%s' % deck_full)

    if a.stage == 'B':
        save(); return

    # ── C 门1（.op 快筛 + A0′ 判定）────────────────────────────────────────
    oplog = os.path.join(HERE, 'pex_%s_op_screen.log' % a.tag)
    r, dt = run([NG, '-b', '-r', op_raw, os.path.basename(deck_op)], cwd=SIM,
                env={'LD_LIBRARY_PATH': ENVLIB}, timeout=600, log=oplog)
    oplogtxt = open(oplog, errors='replace').read()
    opfail = ('could not be simulated' in oplogtxt) or ('singular matrix' in oplogtxt)
    c = {'op_log': oplog, 'op_rc': r.returncode, 'elapsed_s': round(dt, 1),
         'op_solved': not opfail}
    if not opfail:
        g, _ = run([sys.executable, os.path.join(HERE, 'm5_pex_op_gate.py'),
                    '--ref', os.path.join(HERE, 'typ_v015_1.raw'), '--dut', op_raw,
                    '--out', os.path.join(HERE, 'm5_pex_op_gate_%s.json' % a.tag)])
        gj = json.load(open(os.path.join(HERE, 'm5_pex_op_gate_%s.json' % a.tag)))
        c.update({'A0p_max': gj['A0p_max'], 'gate': gj['gate_threshold'], 'PASS': gj['PASS'],
                  'gate_json': os.path.join(HERE, 'm5_pex_op_gate_%s.json' % a.tag)})
    else:
        c['PASS'] = False
        c['stop'] = 'OP 无解（门1 不可测）'
    res['stages']['C_op_gate'] = c
    save()
    if not c.get('PASS'):
        print('[C] 门1 未过 → 停：%s' % c.get('stop', 'A0′ 超门')); return
    print('[C] 门1 PASS：A0′=%.3g' % c['A0p_max'])

    if a.stage == 'C':
        save(); return

    # ── D 门2（动态对拍）───────────────────────────────────────────────────
    tranlog = os.path.join(HERE, 'pex_%s_tran.log' % a.tag)
    r, dt = run([NG, '-b', '-r', op_raw, os.path.basename(deck_full)], cwd=SIM,
                env={'LD_LIBRARY_PATH': ENVLIB}, timeout=3600, log=tranlog)
    pj = os.path.join(HERE, 'm5_pex_tran_%s.json' % a.tag)
    pr, _ = run([sys.executable, os.path.join(HERE, 'm5_parse_pex_tran.py'), tran_raw,
                 '--corner', 'pex_%s_typ' % a.tag, '--out', pj], timeout=1200)
    d = {'tran_log': tranlog, 'tran_raw': tran_raw, 'elapsed_s': round(dt, 1)}
    if os.path.exists(pj):
        pd = json.load(open(pj))
        d.update({'CG_dB': pd['level_gains']['CG_chain_dB'], 'delta_dB': pd['delta_vs_anchor_dB'],
                  'gate_dB': pd['gate_dB'], 'PASS': pd['PASS'], 'parse_json': pj})
    else:
        d.update({'PASS': False, 'stop': 'tran 解析失败：%s' % (pr.stdout or pr.stderr)[-300:]})
    res['stages']['D_tran_gate'] = d
    save()
    if not d.get('PASS'):
        print('[D] 门2 未过 → 停：ΔCG=%s' % d.get('delta_dB')); return
    print('[D] 门2 PASS：CG=%.6f dB Δ=%.2e dB' % (d['CG_dB'], d['delta_dB']))

    if a.stage == 'D':
        save(); return

    # ── E 27 角（双门已过 → 直接点火，runbook 口令②预授权）────────────────
    outdir = os.path.join(HERE, 'pvt27_%s' % a.tag)
    ledger = os.path.join(outdir, 'pvt27_ledger.json')
    r, dt = run([sys.executable, os.path.join(HERE, 'sow6_pvt27_runner.py'),
                 '--deck', deck_full, '--outdir', outdir], timeout=36000,
                log=os.path.join(HERE, 'pvt27_%s.log' % a.tag))
    res['stages']['E_pvt27'] = {'outdir': outdir, 'ledger': ledger,
                                'elapsed_s': round(dt, 1), 'rc': r.returncode}
    if os.path.exists(ledger):
        lg = json.load(open(ledger))
        n_ok = sum(1 for c in lg['corners'].values() if c.get('PASS'))
        res['stages']['E_pvt27']['PASS_corners'] = n_ok
        res['stages']['E_pvt27']['total_corners'] = len(lg['corners'])
    save()
    print('[E] 27 角完成：%s' % res['stages']['E_pvt27'])
    res['finished_utc'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    save()
    print('结果：%s' % resfile)


if __name__ == '__main__':
    main()
