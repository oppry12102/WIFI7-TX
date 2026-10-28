#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_v015_1.py — v015.1 混频器 ACPR 处方落地（b7e7 2026-10-16, 指令=inbox#51 组长 14:12Z 判读回音+放行）

v015 -> v015.1：混频器两处（ACPR 处方表**推荐档**，组长 v2.4 混频器单板扫描实证，
b7e7 13:35Z 签字回信；落地顺序=级间匹配已落地(v015 判读 PASS, 链级 CG +15.74dB 落带)→混频器旋钮）：
  [1] gm 对 Re 15 -> 30 Ω（gilbert_mix 共 4 条：Re1a/Re2a/Re1b/Re2b）—— ACPR +24.7dB 主项
  [2] 开关对 nx 4 -> 6   （gilbert_mix XQ3~XQ6 共 4 管）             —— EVM −1.1dB；i_mix −4.9mA

严格处方组合，不做未实测叠加：
  - RL 100 不动（判读②: 链级 CG +15.74dB 已落 +14~16 带，收敛旋钮不启用）
  - gm 对 nx=3 不动（nx=2 反例未实测，不叠）
  - drv 四件套原样；drv 段现为链内新第一限制级（判读④），若叠加后 drv 段 ACPR 恶化
    再开 drv 旋钮轮（组长已诺配合判读）
观察条件（入组长判读项）：Vce_sw 相对 1.112V 再降 >100mV 或输出摆幅下探逼近 0.5V → 回退 nx=5

幂等：SRC(v015) 只读，每处替换带计数断言（恰好 1 次/处）。
"""
import hashlib, re, sys

SRC = 'design/chain_top_tb_v015.sp'
DST = 'design/chain_top_tb_v015_1.sp'

base = open(SRC, encoding='utf-8').read()

def subckt_window(text, name):
    m = re.search(rf'^\.subckt {name}\b.*?^\.ends', text, re.S | re.M)
    assert m, f'subckt {name} not found'
    return m.start(), m.end()

def replace_in_window(text, name, old, new, expect=1):
    s, e = subckt_window(text, name)
    win = text[s:e]
    n = win.count(old)
    assert n == expect, f'{name}: {old!r} found {n}x, expect {expect}'
    win = win.replace(old, new)
    return text[:s] + win + text[e:]

# ---- 头注沿革（插在最顶部 "====" 分隔线之后、v015 沿革之前） ----
HEAD = """* ============================================================================
* ---- v015.1 沿革（b7e7 2026-10-16, 指令=inbox#51 组长 14:12Z v015 判读回音+放行; ACPR 处方 v2.4 推荐档）----
*   v015 -> v015.1: 混频器两处(ACPR 处方表推荐档, 组长 v2.4 混频器单板扫描实证, b7e7 13:35Z 签字;
*   落地顺序=级间匹配已落地(v015 判读 PASS, 链级 CG +15.74dB 落 +14~16 带) -> 混频器旋钮):
*   [1] gm 对 Re 15->30Ω (gilbert_mix 共4条: Re1a/Re2a/Re1b/Re2b) [ACPR +24.7dB 主项(单板)]
*   [2] 开关对 nx 4->6    (gilbert_mix XQ3~XQ6 共4管)             [EVM -1.1dB; i_mix -4.9mA]
*   其余零变更: RL 100 不动(判读②: +15.74dB 落带, 收敛旋钮不启用); gm 对 nx=3 不动(nx=2 反例
*   未实测不叠); drv 四件套原样。严格处方组合, 不做未实测叠加。
*   预期(处方=单板口径; 链板叠加非加法, v015 实测交互项 -3.86dB 为鉴, 以代跑为准):
*   混频器单板 ACPR +24.7dB/EVM -1.1/i_mix -4.9mA/Vce_sw 1.112V(相对 v015 口径 -74mV);
*   链级 ACPR 地板可能转移至 drv 段(判读④: v015 后 drv 段已是新第一限制级)——
*   若叠加后 drv 段 ACPR 恶化, 开 drv 旋钮轮(组长配合判读)。
*   判读观察条件(已入组长判读项): Vce_sw 相对 1.112V 再降 >100mV 或输出摆幅下探逼近 0.5V
*   -> 回退 nx=5; 组长侧另核: ACPR@P_REF 复现(链出等功率点对齐口径)/EVM@P_REF>=-52/op 零扰动声明重跑。
"""
anchor = "* ============================================================================\n* ---- v015 草案沿革"
assert base.count(anchor) == 1
base = base.replace(anchor, HEAD + anchor)

# ---- [1] gm 对 Re 15 -> 30（gilbert_mix 共 4 条）----
for old, tag in [
    ('Re1a  e1a  ntaila 15', 'Re1a'),
    ('Re2a  e2a  ntaila 15', 'Re2a'),
    ('Re1b  e1b  ntailb 15', 'Re1b'),
    ('Re2b  e2b  ntailb 15', 'Re2b'),
]:
    base = replace_in_window(base, 'gilbert_mix', old,
                             old.replace(' 15', ' 30') + '   $ v015.1[1]: 15->30 (ACPR 处方推荐档)', expect=1)

# ---- [2] 开关对 nx 4 -> 6（gilbert_mix XQ3~XQ6 共 4 管；窗口内断言防误伤 lo_buf/drv 同名行）----
s, e = subckt_window(base, 'gilbert_mix')
win = base[s:e]
assert win.count('npn13G2 nx=4') == 4, f'gilbert_mix npn13G2 nx=4 count={win.count("npn13G2 nx=4")}, expect 4'
win = win.replace('npn13G2 nx=4', 'npn13G2 nx=6   $ v015.1[2]: 4->6 (ACPR 处方推荐档; Vce_sw 观察条件见头注)')
win = win.replace('* ---- 开关对: nx=4 + v011a C 臂 Rd 10Ω (定稿, 紧贴基极侧) ----',
                  '* ---- 开关对: nx=6 (v015.1[2]: 4->6) + v011a C 臂 Rd 10Ω (定稿, 紧贴基极侧) ----')
assert win.count('nx=4') == 0, '窗口内 nx=4 残留'
base = base[:s] + win + base[e:]

open(DST, 'w', encoding='utf-8').write(base)

# ---- 复验 ----
out = open(DST, encoding='utf-8').read()
s2, e2 = subckt_window(out, 'gilbert_mix')
win2 = out[s2:e2]
checks = [
    ('Re 30 x4 (mix 窗口)',   win2.count('ntaila 30') == 2 and win2.count('ntailb 30') == 2),
    ('Re 15 残留 (mix 窗口)',  win2.count('ntaila 15') == 0 and win2.count('ntailb 15') == 0),
    ('开关对 nx=6 x4 (mix 窗口)', win2.count('npn13G2 nx=6') == 4),
    ('mix 窗口内 nx=4 清零',   win2.count('nx=4') == 0),
    ('全文件 npn13G2 nx=4 只剩 lo_buf 2 处', out.count('npn13G2 nx=4') == 2),
    ('RL 100 不动 (drv1/drv2)', out.count('RL1 vcc cop 100') == 1 and out.count('RL1 vcc outp 100') == 1),
    ('mix 内 RL 45 不动',      win2.count('RL1  vcc  rfop  45') == 1),
    ('gm 对 nx=3 不动 (mix 窗口 x4)', win2.count('npn13G2 nx=3') == 4),
    ('Cin/Rin 四件套原样',     out.count('Rin1 inp 0 1k') == 2 and out.count('Cin1 inp bin 10p') == 2),
    ('Cbc 仍删除态',           re.search(r'^Cbc[12] ccas', out, re.M) is None),
    ('kptat=3.98 不动 (唯一定义行)', out.count('.param kptat = 3.98') == 1),
]
for name, ok in checks:
    print(f'{"PASS" if ok else "FAIL"}  {name}')
assert all(ok for _, ok in checks), '复验失败'

sha = hashlib.sha256(out.encode()).hexdigest()
print('sha256(v015.1) =', sha)
print('bytes =', len(out.encode()))
