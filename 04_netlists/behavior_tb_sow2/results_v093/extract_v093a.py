#!/usr/bin/env python3
# v093a 结果提取: 稳态窗多频正弦最小二乘拟合 (与 v092 同口径)
# 约定: 幅值均为差分峰(PK, 差分口); pin_dBm=10log10(a^2/25/1m) a=单边峰; pout_dBm=10log10(D^2/100/1m) D=差分峰
import numpy as np, json, math, glob, os

R = '/data/workspace/pdk/sim/sow2/results_v093'

def load(fn):
    # wrdata 格式: (时间,值) 对交错 -- 每向量 2 列; 值列 = 奇数列
    a = np.loadtxt(fn)
    if a.ndim == 1: a = a[None, :]
    return a[:, 0], a[:, 1::2]  # t(首列), 值列

def fit_amp(t, x, f0, t0, t1):
    m = (t >= t0) & (t <= t1)
    tt, xx = t[m], x[m]
    c = np.cos(2*np.pi*f0*tt); s = np.sin(2*np.pi*f0*tt)
    A = np.vstack([c, s, np.ones_like(tt)]).T
    coef, *_ = np.linalg.lstsq(A, xx, rcond=None)
    return math.hypot(coef[0], coef[1]), float(np.max(np.abs(xx[m])))

def dB(x): return 10*math.log10(x) if x > 0 else float('-inf')

out = {'meta': {'date': 'auto', 'runner': 'b7a0 组长代跑 (v093a 补丁 deck)',
                'method': '稳态窗正弦拟合 (drv/lob: 40-60n @5.5G; mix/chain: 60-200n @5.51G); 幅值=差分峰',
                'patch': 'DRV2 XQ3/XQ4 集电极 vcc->outp/outn (v092d 修复在 v0.93 丢失, 代跑侧补)'}}

# ---------- drv 单板 (drv1+drv2 级联 tb) ----------
amps = [('15p6u', 15.6e-6), ('31m', 0.031), ('44m', 0.044), ('62m', 0.062), ('88m', 0.088),
        ('125m', 0.125), ('176m', 0.176), ('250m', 0.250), ('350m', 0.350), ('500m', 0.500)]
drv_rows = []
for tag, a in amps:
    fn = f'{R}/v093a_drv_{tag}.csv'
    t, d = load(fn)   # cols: noutp noutn na nan nbin2 nbin3
    ad1, _ = fit_amp(t, d[:, 2] - d[:, 3], 5.5e9, 40e-9, 60e-9)   # na-nan
    avin, _ = fit_amp(t, d[:, 4] - d[:, 5], 5.5e9, 40e-9, 60e-9)  # nbin2-nbin3
    ao, _ = fit_amp(t, d[:, 0] - d[:, 1], 5.5e9, 40e-9, 60e-9)    # noutp-noutn
    pin = dB(a**2/25/1e-3); pout = dB(ao**2/100/1e-3)
    drv_rows.append({'tag': tag, 'a_V': a, 'pin_dBm': round(pin, 2),
                     'pout_dBm': round(pout, 2),
                     'drv1_out_dV': round(ad1, 6), 'drv2_in_dV': round(avin, 6),
                     'out_dV': round(ao, 6),
                     'cg_drv1_dB': round(20*math.log10(ad1/(2*a)), 2),
                     'cg_drv2_dB': round(20*math.log10(ao/avin), 2) if avin > 0 else None,
                     'cg_casc_dB': round(20*math.log10(ao/(2*a)), 2)})
# OP1dB: 线性基线由最小两点斜率定
pins = np.array([r['pin_dBm'] for r in drv_rows]); pouts = np.array([r['pout_dBm'] for r in drv_rows])
k = (pouts[1]-pouts[0])/(pins[1]-pins[0])
lin = pouts[1] + k*(pins-pins[1])
comp = pouts - lin
i1 = next(i for i in range(len(pins)) if comp[i] < -0.95)
# 线性插值到 -1dB
i0 = i1-1
frac = (-1 - comp[i0])/(comp[i1]-comp[i0])
op1db_pin = pins[i0]+frac*(pins[i1]-pins[i0])
op1db_pout = pouts[i0]+frac*(pouts[i1]-pouts[i0])
out['drv_single'] = {'rows': drv_rows, 'slope': round(k, 3),
                     'op1db_pin_dBm': round(op1db_pin, 2), 'op1db_pout_dBm': round(op1db_pout, 2),
                     'psat_dBm': round(float(pouts[-1]), 2),
                     'small_cas_dB': drv_rows[0]['cg_casc_dB'],
                     'small_drv1_dB': drv_rows[0]['cg_drv1_dB']}

# ---------- lobuf 单板 ----------
lob_rows = []
for tag in ['28m','40m','56m','80m','113m','160m','225m']:
    fn = f'{R}/v093a_lob_{tag}.csv'
    if not os.path.exists(fn): continue
    t, d = load(fn)   # cols: noutp noutn x1.bin x1.bb1
    ao, _ = fit_amp(t, d[:, 0]-d[:, 1], 5.5e9, 40e-9, 60e-9)
    ain, _ = fit_amp(t, d[:, 2]-d[:, 3], 5.5e9, 40e-9, 60e-9)
    lob_rows.append({'a_V': float(tag.replace('p','.').replace('m','e-3')),
                     'in_dVpp': round(2*float(tag.replace('p','.').replace('m',''))*1e-3*1e3, 1),
                     'gain_x': round(ao/(2*float(tag.replace('p','.').replace('m',''))*1e-3), 3),
                     'out_dVpp': round(2*ao*1e3, 1), 'ef_in_dVpp': round(2*ain*1e3, 1)})
out['lobuf'] = {'rows': lob_rows}

# ---------- mixer 单板 ----------
t, d = load(f'{R}/v093a_mix.csv')   # cols: nrfp nrfn nlop nlon
arf, _ = fit_amp(t, d[:, 0]-d[:, 1], 5.51e9, 60e-9, 200e-9)
alo, _ = fit_amp(t, d[:, 2]-d[:, 3], 5.5e9, 60e-9, 200e-9)
ifamp = 15.8e-3
out['mixer'] = {'if_in_dVpk_diff': round(2*ifamp*1e3, 2),
                'rf_out_dVpk': round(arf*1e3, 3),
                'cg_dB': round(20*math.log10(arf/(2*ifamp)), 2),
                'pout_dBm': round(dB(arf**2/100/1e-3), 2),
                'lo_port_dVpk': round(alo*1e3, 1),
                'ref_v091b_cg_dB': -9.1}

# ---------- chain m20 / m5 ----------
for tag, ifamp in [('m20', 15.8e-3), ('m5', 88.9e-3)]:
    t, d = load(f'{R}/v093a_chain_{tag}.csv')
    # cols: noutp noutn nmixp nmixn nd1p nd1n nlop nlon nblop nblon
    a_lob, _ = fit_amp(t, d[:, 8]-d[:, 9], 5.5e9, 60e-9, 200e-9)    # nblop-nblon
    a_lo, _ = fit_amp(t, d[:, 6]-d[:, 7], 5.5e9, 60e-9, 200e-9)     # nlop-nlon (mix LO 口)
    a_mix, _ = fit_amp(t, d[:, 2]-d[:, 3], 5.51e9, 60e-9, 200e-9)   # nmixp-nmixn
    a_d1, _ = fit_amp(t, d[:, 4]-d[:, 5], 5.51e9, 60e-9, 200e-9)    # nd1p-nd1n
    a_out, _ = fit_amp(t, d[:, 0]-d[:, 1], 5.51e9, 60e-9, 200e-9)   # noutp-noutn
    cg_mix = 20*math.log10(a_mix/(2*ifamp))
    cg_d1 = 20*math.log10(a_d1/a_mix) if a_mix > 0 else None
    cg_d2 = 20*math.log10(a_out/a_d1) if a_d1 > 0 else None
    cg_tot = 20*math.log10(a_out/(2*ifamp))
    pout = dB(a_out**2/100/1e-3)
    out[f'chain_{tag}'] = {
        'if_in_dBm_diff': round(dB((2*ifamp)**2/2/50/1e-3), 1),
        'if_in_dVpk': round(2*ifamp*1e3, 1),
        'lob_out_dVpk': round(a_lob*1e3, 1), 'lo_at_mix_dVpk': round(a_lo*1e3, 1),
        'lo_at_mix_mVpp': round(2*a_lo*1e3, 1),
        'mix_out_dVpk': round(a_mix*1e3, 2), 'drv1_out_dVpk': round(a_d1*1e3, 2),
        'chain_out_dVpk': round(a_out*1e3, 2),
        'cg_mix_dB': round(cg_mix, 2), 'cg_drv1_dB': round(cg_d1, 2),
        'cg_drv2_dB': round(cg_d2, 2), 'cg_total_dB': round(cg_tot, 2),
        'chain_out_dBm': round(pout, 2)}

out['meta']['date'] = __import__('datetime').datetime.utcnow().strftime('%Y-%m-%dT%H:%MZ')
with open('/data/workspace/pdk/sim/sow2/results_v093/sow2_v093a_summary.json', 'w') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
