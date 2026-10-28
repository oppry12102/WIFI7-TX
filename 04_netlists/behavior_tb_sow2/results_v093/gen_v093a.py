#!/usr/bin/env python3
# v093a deck 生成器: b7e7 v0.93 四板 + 组长补丁(CB 集电极 vcc->outp/outn, v092d 修复在 v0.93 中丢失)
# + foreach 展开硬编码段(id9: wrdata 不展开 $a) + wrdata 落盘 results_v093/
import re, os, sys

SRC = '/data/workspace/pdk/sim/sow2/v093_fresh'
DST = '/data/workspace/pdk/sim/sow2'
RES = 'sow2/results_v093'   # wrdata 相对 cwd(pdk/sim)
os.makedirs(f'{DST}/results_v093', exist_ok=True)

def load(name):
    with open(f'{SRC}/{name}') as f: return f.read()

def must(s, subs, ctx):
    for sub in subs:
        assert s.count(sub) == 1, f'{ctx}: pattern count={s.count(sub)} for {sub!r}'

HDR = """* v093a（组长代跑补丁 deck, 基于 b7e7 v0.93）: DRV2 共基管集电极 vcc->outp/outn (XQ3/XQ4) --
*   v092d 修复在 v0.93 合并时丢失(她从 v0.92 起编, 未同步组长认领的笔误修正)。c=vcc 时信号经 CB
*   直通 AC 地, outp/outn 悬空 -> drv2 输出恒零(v092d 已实证)。仅此 4 行结构差异, 其余 v0.93 原样。
"""

# ---------- 1. drv_tb ----------
s = load('drv_tb.sp')
must(s, ['XQ3  vcc  nbcas  ccas1  0  npn13G2 nx=10', 'XQ4  vcc  nbcas  ccas2  0  npn13G2 nx=10'], 'drv')
s = s.replace('XQ3  vcc  nbcas  ccas1', 'XQ3  outp  nbcas  ccas1')
s = s.replace('XQ4  vcc  nbcas  ccas2', 'XQ4  outn  nbcas  ccas2')
# foreach -> 硬编码段
amps = ['15.6u','31m','44m','62m','88m','125m','176m','250m','350m','500m']
tags = ['15p6u','31m','44m','62m','88m','125m','176m','250m','350m','500m']
seg = []
for a, t in zip(amps, tags):
    seg.append(f"""* v093a 硬编码段 {a} (id9: foreach 变量不进 wrdata 文件名)
alterparam drv_amp = {a}
reset
tran 1p 60n 40n
wrdata {RES}/v093a_drv_{t}.csv v(noutp) v(noutn) v(na) v(nan) v(nbin2) v(nbin3)""")
block = '\n'.join(seg)
pat = re.compile(r"foreach a [^\n]*\n(?:.*\n)*?end\n", re.M)
s2, n = pat.subn(block + '\n', s, count=1)
assert n == 1, 'drv foreach not replaced'
s = s2
lines = s.split('\n')
lines.insert(1, HDR.rstrip('\n'))
with open(f'{DST}/v093a_drv_tb.sp','w') as f: f.write('\n'.join(lines))
print('v093a_drv_tb.sp OK')

# ---------- 2. lobuf_tb ----------
s = load('lobuf_tb.sp')
amps = ['28m','40m','56m','80m','113m','160m','225m']
seg = []
for a in amps:
    t = a.replace('.','p')
    seg.append(f"""* v093a 硬编码段 {a}
alterparam lo_in_amp = {a}
reset
tran 1p 60n 40n
wrdata {RES}/v093a_lob_{t}.csv v(noutp) v(noutn) v(bin) v(bb1)""")
block = '\n'.join(seg)
s2, n = pat.subn(block + '\n', s, count=1)
assert n == 1, 'lob foreach not replaced'
s = s2
lines = s.split('\n')
lines.insert(1, HDR.rstrip('\n'))
with open(f'{DST}/v093a_lob_tb.sp','w') as f: f.write('\n'.join(lines))
print('v093a_lob_tb.sp OK')

# ---------- 3. mixer_tb ----------
s = load('mixer_tb.sp')
must(s, ['let vr = v(nrfp) - v(nrfn)'], 'mix')
s = s.replace('let vr = v(nrfp) - v(nrfn)',
    'let vr = v(nrfp) - v(nrfn)\n'
    f'wrdata {RES}/v093a_mix.csv v(nrfp) v(nrfn) v(nswa) v(nswb) v(nlop) v(nlon)')
lines = s.split('\n')
lines.insert(1, HDR.rstrip('\n'))
with open(f'{DST}/v093a_mix_tb.sp','w') as f: f.write('\n'.join(lines))
print('v093a_mix_tb.sp OK')

# ---------- 4/5. chain m20 / m5 ----------
for tag, amp, note in [('m20','15.8m','-20dBm 差分 (CG 基线)'),
                       ('m5','88.9m','-5dBm 差分 = 15.8m*10^(15/20) (链出绝对电平定衰减档)')]:
    s = load('chain_top_tb.sp')
    must(s, ['XQ3  vcc  nbcas  ccas1', 'XQ4  vcc  nbcas  ccas2',
             '.param ifamp = 15.8m', 'let vd1 = v(nd1p) - v(nd1n)'], f'chain {tag}')
    s = s.replace('XQ3  vcc  nbcas  ccas1', 'XQ3  outp  nbcas  ccas1')
    s = s.replace('XQ4  vcc  nbcas  ccas2', 'XQ4  outn  nbcas  ccas2')
    s = s.replace('.param ifamp = 15.8m', f'.param ifamp = {amp}')
    s = s.replace('let vd1 = v(nd1p) - v(nd1n)',
        'let vd1 = v(nd1p) - v(nd1n)\n'
        f'wrdata {RES}/v093a_chain_{tag}.csv v(noutp) v(noutn) v(nmixp) v(nmixn) v(nd1p) v(nd1n) v(nlop) v(nlon) v(nblop) v(nblon)')
    lines = s.split('\n')
    lines.insert(1, f"* v093a（组长代跑补丁 deck, 基于 b7e7 v0.93）: DRV2 CB 集电极 vcc->outp/outn (v092d 修复在 v0.93 丢失)\n*   口径: IF {note}; CB 补丁外与 v0.93 原样。")
    with open(f'{DST}/v093a_chain_{tag}.sp','w') as f: f.write('\n'.join(lines))
    print(f'v093a_chain_{tag}.sp OK')

print('ALL DECKS GENERATED')
