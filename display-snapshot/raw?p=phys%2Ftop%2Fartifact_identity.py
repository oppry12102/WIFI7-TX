#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
artifact_identity.py — 件身份判定器（b7a0，2026-10-19）

立器动机（裁定六十五 §自纠③ 的工具化）：
  我方在裁定六十四把「我方 8510 滞后镜像件 ca74fd53」当成「fde9 现役件」，
  据此判对方 runbook 记载过期 —— 差点污染对方的谱系权威源。
  根因不是「不知道有镜像台账」，而是**判身份靠人脑记忆，没有机器闸**。
  本器把「这个 sha / 这个件名，在我方是现役还是镜像/历史/夹具」变成一次可复现查询。

三条律的落地点：
  ★★镜像件身份先验律  → whois / audit：对他人资产下结论前先查身份
  ★★件引用双标识律    → census：同名多件必须靠 sha+目录区分，本器直接列出全部同名件
  ★引用数字前必实测律  → 所有 sha 现算，不读任何既有记载

用法：
  python3 artifact_identity.py index                 # 建/刷新盘内索引（写 /tmp 与 phys/top/artifact_index.json）
  python3 artifact_identity.py whois <sha8|件名>    # 判身份：命中路径 + 同名件全谱 + 8510 现役对照
  python3 artifact_identity.py census [--top N]     # 同名多件普查（项目目录内）
  python3 artifact_identity.py audit <md文件...>     # 扫文档里的 8 位 sha 引用，逐条判身份并标警
  python3 artifact_identity.py live8510 [件名...]    # GET 8510 现役面回读（不传=白名单关键件）

身份分类（按路径规则，可在 CLASSIFY 里改）：
  LIVE_ANCHOR   现役面锚（phys/top/）
  PUBLISH       我方发布面（outbox_files/design/sow6/ = 8510 白名单根）
  RUN_DEPLOY    代跑部署（phys/sow6_run/run_v2/gen_vNN/）
  PEER_LANDING  组员到件落地区（inbox_land/ inbox_get/ inbox_files/）
  MIRROR_AUDIT  镜像审计区（sim_report/mirror_audit_*/ tmp_m5head/）
  FIXTURE       夹具/自测件（含 selftest / fixture / rehearsal / dryrun）
  VERIFY        我方复核隔离区（verify/）
  ARCHIVE       其余（历史档）
"""
import tempfile
import os, sys, json, hashlib, re, urllib.request, urllib.parse, collections, time

ROOT = os.environ.get('ARTIFACT_IDENTITY_ROOT', '/data/workspace')
# ★两个层次，勿串（本器首版即在此串面：把本地盘路径当成 8510 的 name 前缀 ⇒ 全 404）
PUB_LOCAL = 'outbox_files/design/sow6'   # 本地盘：8510 白名单根
PUB_REMOTE = 'design/sow6'               # 8510 /files 的 name= 前缀（相对白名单根）
PUB = PUB_LOCAL                          # 兼容旧引用
IDX_TMP = os.path.join(tempfile.gettempdir(), 'artifact_index.json')
IDX_KEEP = os.path.join(ROOT, 'phys/top/artifact_index.json')
KEYFILE = os.environ.get('ARTIFACT_IDENTITY_KEYFILE', os.path.join(ROOT, 'filekey'))
BASE8510 = os.environ.get('ARTIFACT_IDENTITY_BASE8510', 'http://127.0.0.1:8510')

_scan_env = os.environ.get('ARTIFACT_IDENTITY_SCAN_DIRS')
SCAN_DIRS = _scan_env.split(':') if _scan_env else ['phys', 'verify', 'run_v2', 'outbox_files', 'outbox_draft', 'design', 'design_circuit',
             'sim_report', 'gds', 'incoming', 'inbox_files', 'inbox_get', 'inbox_land', 'tmp_m5head',
             'tmp_gateB', 'tools', 'webui', 'playbook', 'pdk/sim', 'pex_in', 'fetch_v091',
             'kb7a43', 'kb7a43_v1', 'research', 'dryrun', 'amem']
# v3（2026-10-20，裁定七十三）：工作区根散文件补扫（首版漏 → 引用根级交付件永远假 not-local）
ROOT_FILES = ['BOOT.md', 'summary.md', 'spec.md', 'architecture.md', 'final_report.md',
              'SOW_仿真验证.md', 'SOW_电路设计.md', 'integration_review.md',
              '结案简报_正式稿_8510.md', '结案简报_正式稿_fde9.md']
SKIP_DIRNAMES = {'__pycache__', '.git', 'ngroot', 'openvaf', '.venv', 'node_modules', 'ihp_open'}
MAXB = 20 * 1024 * 1024

CLASSIFY = [
    (r'^phys/top/', 'LIVE_ANCHOR'),
    (r'^outbox_files/design/sow6/', 'PUBLISH'),
    # v3：outbox_draft/＝我方发信底稿区（引自己发过的信底稿是合法现役引用；宽口径后裸 sha 落此 ⇒ 须正名，否则假 RISK）
    (r'^outbox_draft/', 'OUTBOX'),
    (r'^phys/sow6_run/run_v2/gen_v\d+/', 'RUN_DEPLOY'),
    # ★代跑产出区（LVS/DRC run_dir、gds 出件）——首版漏了这层 ⇒ 提取件被误归 ARCHIVE 而假报 RISK
    # v3：根散文件（ROOT_FILES）→ ROOT_DOC（build_index 里按集合判定，不经此表）
    (r'^phys/sow6_run/run_v2/(lvs|gds)/', 'RUN_OUTPUT'),
    (r'^phys/(drc|sow6_run)/', 'RUN_OUTPUT'),
    (r'^gds/', 'RUN_OUTPUT'),
    (r'^(inbox_land|inbox_get|inbox_files|incoming)/', 'PEER_LANDING'),
    (r'^(sim_report/mirror_audit|tmp_m5head)/', 'MIRROR_AUDIT'),
    (r'(selftest|fixture|rehearsal|dryrun)', 'FIXTURE'),
    (r'^verify/', 'VERIFY'),
]


def classify(rel):
    for pat, tag in CLASSIFY:
        if re.search(pat, rel):
            return tag
    return 'ARCHIVE'


def sha8(b):
    return hashlib.sha256(b).hexdigest()[:8]


def build_index(verbose=True):
    byname = collections.defaultdict(list)
    bysha = collections.defaultdict(list)
    n = 0
    for inc in SCAN_DIRS:
        base = os.path.join(ROOT, inc)
        if not os.path.isdir(base):
            continue
        for dp, dn, fn in os.walk(base):
            dn[:] = [d for d in dn if d not in SKIP_DIRNAMES]
            for f in fn:
                p = os.path.join(dp, f)
                try:
                    sz = os.path.getsize(p)
                    if sz > MAXB:
                        continue
                    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
                except Exception:
                    continue
                rel = os.path.relpath(p, ROOT)
                cls = 'ROOT_DOC' if rel in set(ROOT_FILES) else classify(rel)
                rec = {'path': rel, 'bytes': sz, 'sha256': h, 'sha8': h[:8], 'cls': cls}
                byname[f].append(rec)
                bysha[h[:8]].append(rec)
                n += 1
    # v3：根散文件补扫（ROOT_FILES；缺席 ⇒ audit 引用根级交付件永远假 not-local）
    for f in ROOT_FILES:
        p = os.path.join(ROOT, f)
        if not os.path.isfile(p):
            continue
        try:
            sz = os.path.getsize(p)
            h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        except Exception:
            continue
        rec = {'path': f, 'bytes': sz, 'sha256': h, 'sha8': h[:8], 'cls': 'ROOT_DOC'}
        byname[f].append(rec)
        bysha[h[:8]].append(rec)
        n += 1
    idx = {'built_at': time.strftime('%FT%TZ', time.gmtime()), 'files': n,
           'names': len(byname), 'byname': dict(byname), 'bysha': dict(bysha)}
    json.dump(idx, open(IDX_TMP, 'w'))
    try:
        json.dump(idx, open(IDX_KEEP, 'w'))
    except Exception as e:
        print('WARN keep-index write failed:', e)
    if verbose:
        multi = sum(1 for v in byname.values() if len({r['sha256'] for r in v}) > 1)
        print('indexed %d files / %d names / %d names with >1 sha -> %s' % (n, len(byname), multi, IDX_TMP))
    return idx


def load_index():
    for p in (IDX_TMP, IDX_KEEP):
        if os.path.exists(p):
            try:
                return json.load(open(p))
            except Exception:
                pass
    return build_index()


def tok8510():
    try:
        return open(KEYFILE).read().strip()
    except Exception:
        return None


def get8510(name, tok=None):
    tok = tok or tok8510()
    if not tok:
        return None
    url = '%s/files?token=%s&name=%s/%s' % (BASE8510, tok, PUB_REMOTE, urllib.parse.quote(name))
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            b = r.read()
        return {'sha8': sha8(b), 'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b)}
    except Exception as e:
        return {'error': str(e)}


def cmd_whois(arg):
    idx = load_index()
    recs = idx['bysha'].get(arg) or idx['byname'].get(arg) or []
    if not recs:
        print('NO HIT in local index for %r' % arg)
    name = recs[0]['path'].split('/')[-1] if recs else arg
    print('=== %s : %d local copies ===' % (arg, len(recs)))
    for r in sorted(recs, key=lambda x: x['path']):
        print('  %-12s %-10s %9d  %s' % (r['cls'], r['sha8'], r['bytes'], r['path']))
    fam = idx['byname'].get(name, [])
    shas = sorted({r['sha8'] for r in fam})
    print('--- same-name family: %s -> %d sha: %s' % (name, len(shas), ' '.join(shas)))
    live = get8510(name)
    if live:
        if 'error' in live:
            print('--- 8510 live: ERR %s' % live['error'])
        else:
            hit = [r for r in fam if r['sha8'] == live['sha8']]
            print('--- 8510 live(PUBLISH face): %s %dB' % (live['sha8'], live['bytes']))
            for r in hit:
                print('      matches local: [%s] %s' % (r['cls'], r['path']))
            if not hit:
                print('      !! 8510 live sha NOT present locally -> local copies are ALL stale/mirror')
    return recs


def cmd_census(top=25):
    idx = load_index()
    multi = [(n, v) for n, v in idx['byname'].items() if len({r['sha256'] for r in v}) > 1]
    multi.sort(key=lambda kv: (-len({r['sha256'] for r in kv[1]}), kv[0]))
    print('names with >1 sha: %d (of %d names)' % (len(multi), len(idx['byname'])))
    for n, v in multi[:top]:
        shas = sorted({r['sha8'] for r in v})
        print('\n%-44s %2d copies / %2d sha' % (n, len(v), len(shas)))
        for r in sorted(v, key=lambda x: (x['cls'], x['path']))[:10]:
            print('    %-12s %-10s %9d  %s' % (r['cls'], r['sha8'], r['bytes'], r['path']))
        if len(v) > 10:
            print('    ... +%d more' % (len(v) - 10))
    return multi


SHA_RE = re.compile(r'(?<![0-9a-f-])([0-9a-f]{8})(?:[0-9a-f]{8,120})?(?![0-9a-fTZ])')
# v3（D1 修复）：旧式 `([0-9a-f]{8})` 只认反引号包裹的 sha8 ⇒ 表格裸写/sha16/sha64 长形式**静默漏检**（覆盖降级，
# ★★静默跳过降覆盖律家族）。宽口径：裸 8 位十六进制，允许后接 8~120 位十六进制（长形式取前 8）。
# 排除声明（代价）：①前邻 '-'（ik-/fk- 类 token 键不当作 sha）②纯数字跳过（日期/epoch 如 20261020；
# 纯数字 sha8 ≈0.2% 样本空间会假阴性——接受并声明）③后邻 T/Z（ISO 时刻）。
NAME_RE = re.compile(r'`?([A-Za-z0-9_\.\-\u4e00-\u9fff]+\.[A-Za-z0-9]{1,6})`?')
# 风险分级：只有「本地有副本但只在镜像/落地/历史区」与「同名件在 8510 现役面是另一个 sha」才算真风险。
# 「本地无副本」对他人资产是**正常态**（我方从不搬运对方全部件），只记 INFO，不报警——
# 首版把 NOT-LOCAL 当警 ⇒ 53/137 全红，等于没有信号。
RISKY_ONLY = {'MIRROR_AUDIT', 'PEER_LANDING', 'ARCHIVE', 'FIXTURE'}
# 裁定六十九·b7e7 建议②：PEER_LANDING 按盘区分——我盘=中转区（该警）；他盘=同伴件唯一实体所在（不该警）。
# 他侧跑本器时置 ARTIFACT_IDENTITY_PEER_LANDING_AS_INFO=1 即按 INFO 处理（只对 tags 恰为 {PEER_LANDING} 的引用生效）。
PEER_LANDING_AS_INFO = os.environ.get('ARTIFACT_IDENTITY_PEER_LANDING_AS_INFO', '') == '1'
# 同行若已明确标注「这是旧件」，则引用旧 sha 是**合法**的（留档语义），降级不报警。
# ⚠词表是启发式：补「镜像/旧版」等词（2026-10-20，采 b7e7 建议）会同时把批评语境（如「镜像件当现役引用是错的」）洗成 OKARCH
# ⇒ 属可接受假阴性，由「RISK=0 不得当『引用全对』证据」补偿控制兜底（裁定六十八 §四）。
ARCHIVE_WORDS = ('留档', '候补', '旧面', '降名', '降级', '历史', '作废', '撤销', '回滚', '原 ', '原版',
                 '旧代', '旧装配', '冻结', '滞后', '镜像', '旧版', '旧件', '副本', '扩展版', '中间版',
                 'ARCHIVE', 'archive', 'stale', 'prev', 'bak')

# ★阶段 142 新增：文档级「快照/留档」横幅声明词（横幅在头部、引用在正文 ⇒ 行级判据读不到）
SNAPSHOT_WORDS = ('历史快照', '非现行', '不作现行', '降级为历史', '历史留痕', '留痕',
                  '非现役', '非当前口径', '已降级')
# ★阶段 142 新增：对照语义与横幅声明的**适用范围**（横幅只看前 N 行，防正文里的自述误判）
BANNER_HEAD_LINES = 40


def cmd_audit(paths, win=70, show_info=False):
    idx = load_index()
    live_cache = {}
    tot = risk = okarch = info = 0
    localpass = notlocal = infoland = 0
    WHITELIST = {'PUBLISH', 'LIVE_ANCHOR', 'RUN_DEPLOY', 'RUN_OUTPUT', 'VERIFY', 'ROOT_DOC', 'OUTBOX'}  # v3 +ROOT_DOC+OUTBOX
    for p in paths:
        if not os.path.exists(p):
            print('SKIP missing', p)
            continue
        txt = open(p, encoding='utf-8', errors='replace').read()
        lines = txt.splitlines()
        print('\n########## %s (%d lines) ##########' % (p, len(lines)))
        # ★阶段 142：文档级横幅声明（历史快照/非现行/留痕）⇒ 全文引用按留档语义处理
        head = "\n".join(lines[:BANNER_HEAD_LINES])
        doc_declared = any(w in head for w in SNAPSHOT_WORDS)
        for i, ln in enumerate(lines, 1):
            for m in SHA_RE.finditer(ln):
                s = m.group(1)
                if s.isdigit():
                    continue  # v3：纯数字=日期/epoch，非 sha（代价声明见 SHA_RE 注）
                tot += 1
                recs = idx['bysha'].get(s, [])
                # ★邻近窗配名（首版取「整行所有件名」⇒ 把同行无关件错配给本 sha，假阳性）
                seg = ln[max(0, m.start() - win): m.end() + win]
                nm = [x for x in NAME_RE.findall(seg)
                      if not re.fullmatch(r'[0-9a-f]{8}', x) and x in idx['byname']]
                tags = sorted({r['cls'] for r in recs})
                declared = any(w in ln for w in ARCHIVE_WORDS)
                line_shas = set(SHA_RE.findall(ln))
                # ★阶段 142 二修：对照语义的名字取**整行**（表格行常把件名放最左、指纹放最右，
                #   ±70 字符邻近窗够不着 ⇒ 判不出对照）；名字关联仍用 nm 判 RISK（不放宽）。
                line_names_all = [x for x in NAME_RE.findall(ln)
                                  if not re.fullmatch(r'[0-9a-f]{8}', x) and x in idx['byname']]
                # ★阶段 142：同行对照语义——同一行若同时出现该件名的**现役指纹**，
                #   则本行是「现役面 vs 另一面」的对照行 ⇒ 所引旧指纹属声明式对照，非「镜像当现役」。
                contrast = False
                live_marks = {}
                for n in set(nm) | set(line_names_all):
                    fam = idx['byname'].get(n, [])
                    fs = {r['sha8'] for r in fam}
                    if len(fs) > 1:
                        if n not in live_cache:
                            live_cache[n] = get8510(n)
                        lv = live_cache[n]
                        if lv and 'error' not in lv:
                            live_marks[n] = lv
                            if lv['sha8'] in line_shas:
                                contrast = True
                if doc_declared:
                    decl_note = '文档横幅已声明快照/留档'
                elif declared:
                    decl_note = '同行已声明留档'
                elif contrast:
                    decl_note = '同行含现役指纹⇒对照语义'
                else:
                    decl_note = ''
                declared_eff = bool(decl_note)
                lvl, why = '', ''
                if PEER_LANDING_AS_INFO and set(tags) == {'PEER_LANDING'}:
                    lvl, why = 'INFO', 'peer-landing-as-info（他盘模式：PEER_LANDING=同伴件唯一实体所在，非中转嫌疑）'
                elif not recs:
                    lvl, why = 'INFO', 'not-local（他人资产/未搬运，正常态）'
                elif not (set(tags) & WHITELIST):
                    if declared_eff:
                        lvl, why = 'OKARCH', '本地副本只在 %s，但%s ⇒ 合法' % (','.join(tags), decl_note)
                    else:
                        lvl, why = 'RISK', '本地副本只在 %s ⇒ 疑似镜像/历史件被当现役引用（同行无留档声明）' % ','.join(tags)
                # 同名件在 8510 现役面是否为另一个 sha（★这是「件引用双标识律」的机器闸）
                for n in set(nm):
                    lv = live_marks.get(n)
                    if not lv:
                        continue
                    fam = idx['byname'].get(n, [])
                    fs = {r['sha8'] for r in fam}
                    if lv['sha8'] != s and s in fs:
                        if declared_eff:
                            lvl = lvl or 'OKARCH'
                            why += ' | 同名件 %s 8510 现役=%s≠所引 %s（%s）' % (n, lv['sha8'], s, decl_note)
                        else:
                            lvl = 'RISK'
                            why += ' | ★同名件 %s 的 8510 现役面=%s ≠ 本文所引 %s（同名多件×%d，未声明留档）' % (
                                n, lv['sha8'], s, len(fs))
                if lvl == 'RISK':
                    risk += 1
                    print('L%-5d [RISK] %s  %s' % (i, s, why))
                    print('        %s' % ln.strip()[:200])
                    for r in recs[:5]:
                        print('        [%s] %s' % (r['cls'], r['path']))
                elif lvl == 'OKARCH':
                    okarch += 1
                    if show_info:
                        print('L%-5d [ok-arch] %s %s' % (i, s, why))
                elif lvl == 'INFO' and show_info:
                    info += 1
                    print('L%-5d [info] %s  %s' % (i, s, why))
                # v3（D2 修复）：分桶计数——本地白名单命中=local-pass（旧版灌进 not-local 桶=命名误导，
                # 「not-local 6」读作 6 条全缺实体、实则 4 条本地 PASS——读者被误导方向=假阴性）
                if lvl == '':
                    localpass += 1
                elif lvl == 'INFO':
                    if why.startswith('peer-landing'):
                        infoland += 1
                    else:
                        notlocal += 1
    print('\n=== audit: %d citations | RISK %d | ok-archive %d | local-pass %d | not-local %d | peer-info %d ==='
          % (tot, risk, okarch, localpass, notlocal, infoland))


KEY_LIVE = ['m2_mix_v35.gds', 'm2_mix_v34.gds', 'm2_mix_v31.gds', 'm3_drv1_v21_r1.gds',
            'm3_drv1_v21.gds', 'pex_mix_v27.cdl', 'pex_mix_v31.cdl', 'pex_drv1_v19.cdl',
            'pex_drv2_v19.cdl', 'mix_subckt_LVS输入_v1g.sp', 'gen_M2_mix_v35.py',
            'm5_pex_substitute_jia.py', 'm5_cdl_reship_check.py', 'lib13g2.py', 'cbpath.py']


def cmd_live(names=None):
    names = names or KEY_LIVE
    idx = load_index()
    print('%-34s %-10s %8s | %-10s %-12s | local shas' % ('8510 name', 'live sha8', 'bytes', 'pub sha8', 'verdict'))
    for n in names:
        lv = get8510(n)
        fam = idx['byname'].get(n, [])
        locs = sorted({r['sha8'] for r in fam})
        pubrec = [r for r in fam if r['cls'] == 'PUBLISH']
        pubs = pubrec[0]['sha8'] if pubrec else 'NOPUB'
        if not lv or 'error' in lv:
            print('%-34s ERR %s' % (n, (lv or {}).get('error')))
            continue
        if pubs == lv['sha8']:
            v = 'PUB==LIVE'
        else:
            v = '!!PUB≠LIVE'
        stale = [r for r in fam if r['sha8'] != lv['sha8']]
        print('%-34s %-10s %8d | %-10s %-12s | %s%s' % (
            n, lv['sha8'], lv['bytes'], pubs, v, ' '.join(locs),
            ('  stale×%d' % len(stale)) if stale else ''))
        for r in stale[:6]:
            print('        stale [%s] %s %s' % (r['cls'], r['sha8'], r['path']))


def _run_core(cmd='whois', arg='', info=False, **kw):
    """技能入口（register_skill 契约）。cmd=index/whois/census/audit/live8510。
    arg：whois 的 sha8|件名；census 的 '--top N'；audit 的空格分隔 md 路径；live8510 的空格分隔件名。"""
    import io as _io, contextlib as _cl
    buf = _io.StringIO()
    s = str(arg).strip()
    # 多值子命令按空白拆分；whois 单值（件名可能含空格则整体保留）
    if cmd in ('census', 'audit', 'live8510'):
        a = [cmd] + (s.split() if s else [])
    else:
        a = [cmd] + ([s] if s else [])
    if info and '--info' not in a:
        a.append('--info')
    old = sys.argv
    try:
        sys.argv = ['artifact_identity.py'] + a
        with _cl.redirect_stdout(buf):
            main()
    finally:
        sys.argv = old
    return buf.getvalue()


# ── 阶段 142 · 判据器有齿自检（真阳必报 / 假阳必压 双向）────────────────
def _audit_counts(paths, show_info=False):
    """跑 cmd_audit 并解析汇总行 ⇒ (citations, risk)。"""
    import io as _io, contextlib as _cl
    buf = _io.StringIO()
    with _cl.redirect_stdout(buf):
        cmd_audit(list(paths), show_info=show_info)
    t = buf.getvalue()
    m = re.search(r"audit:\s*(\d+)\s*citations\s*\|\s*RISK\s*(\d+)", t)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def cmd_selftest():
    """★阶段 142 自检：三条新判据（同行对照语义 / 文档横幅声明）＋ 原有真阳路径，双向校准。

    用真实素材：netaudit.py 现役面（8510）vs 本地另一面（多 sha 家族）⇒ 造四份夹具文档：
      NC1 真阳必报：只引另一面 sha、无任何声明 ⇒ 必须 RISK≥1
      NC2 假阳必压：同一行同时出现现役 sha ⇒ 对照语义 ⇒ 必须 RISK==0
      NC3 假阳必压：文档横幅声明「历史快照 · 非现行」＋ 只引另一面 ⇒ 必须 RISK==0
      NC4 真阳必报：横幅声明写在**头部之外** ⇒ 不生效 ⇒ 必须 RISK≥1
        （★横幅只降「同名件对照」类，不许把整篇文档的风险洗掉 ⇒ 判据不许过宽）
    """
    import tempfile, shutil
    cases = []
    idx = load_index()
    fam = idx['byname'].get('netaudit.py', [])
    fs = sorted({r['sha8'] for r in fam})
    live = get8510('netaudit.py') or {}
    lv = live.get('sha8')
    others = [x for x in fs if x != lv]
    d = tempfile.mkdtemp(prefix='a1probe_identity_selftest_')   # ★沿用既有族（阶段 141 新族须入族表）
    try:
        def write(name, text):
            p = os.path.join(d, name)
            with open(p, 'w', encoding='utf-8') as f:
                f.write(text)
            return p

        if not lv or not others:
            print('判定: FAIL  素材不足（netaudit.py 现役/另一面取不到）')
            print('结论行: 总项数 1 ／ FAIL 1')
            return
        o1 = others[0]
        o2 = others[-1] if len(others) > 1 else o1
        p_nc1 = write('nc1.md', "# 夹具·无声明\n\n| 件 | 指纹 |\n|---|---|\n| `netaudit.py` | `%s` | 取件锚 |\n" % o1)
        p_nc2 = write('nc2.md', "# 夹具·同行对照\n\n| 件 | 现役 | 另一面 |\n|---|---|---|\n| `netaudit.py` | `%s` | `%s` |\n" % (lv, o1))
        p_nc3 = write('nc3.md', "# 夹具·历史快照\n\n> 本文件是**历史快照 · 非现行**，内容作历史留痕。\n\n| 件 | 指纹 |\n|---|---|\n| `netaudit.py` | `%s` |\n" % o1)
        pad = '\n'.join(['（填充行 %d）' % i for i in range(1, 46)])
        p_nc4 = write('nc4.md', "# 夹具·横幅不在头部\n\n| 件 | 指纹 |\n|---|---|\n| `netaudit.py` | `%s` |\n\n" % o1 + pad + "\n\n> 本文件是**历史快照 · 非现行**，内容作历史留痕。\n")

        c1, r1 = _audit_counts([p_nc1])
        cases.append({"case": "NC1 真阳必报：无声明只引另一面 ⇒ RISK≥1", "ok": r1 >= 1, "got": r1})
        c2, r2 = _audit_counts([p_nc2])
        cases.append({"case": "NC2 假阳必压：同行含现役指纹 ⇒ RISK==0", "ok": r2 == 0, "got": r2})
        c3, r3 = _audit_counts([p_nc3])
        cases.append({"case": "NC3 假阳必压：横幅声明快照 ⇒ RISK==0", "ok": r3 == 0, "got": r3})
        c4, r4 = _audit_counts([p_nc4])
        cases.append({"case": "NC4 真阳必报：横幅不在头部不生效 ⇒ RISK≥1", "ok": r4 >= 1, "got": r4})
    finally:
        shutil.rmtree(d, ignore_errors=True)
    n_ok = sum(1 for c in cases if c['ok'])
    for c in cases:
        print("  [%s] %s: got=%s" % ("OK " if c['ok'] else "BAD", c['case'], c['got']))
    print("selftest:", "PASS" if n_ok == len(cases) else "FAIL", "%d/%d" % (n_ok, len(cases)))
    print("结论行: 总项数 %d ／ FAIL %d" % (len(cases), len(cases) - n_ok))
    return 0 if n_ok == len(cases) else 1


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 0
    c = a[0]
    if c == 'index':
        build_index()
    elif c == 'whois':
        cmd_whois(a[1])
    elif c == 'census':
        top = 25
        if '--top' in a:
            top = int(a[a.index('--top') + 1])
        cmd_census(top)
    elif c == 'audit':
        rest = [x for x in a[1:] if not x.startswith('--')]
        cmd_audit(rest, show_info=('--info' in a))
    elif c == 'live8510':
        cmd_live(a[1:] or None)
    elif c == 'selftest':
        cmd_selftest()
    else:
        print('unknown cmd', c)
        return 2
    return 0


# ── 阶段 127 · 裁定一百一十七 · 统一闸套（异常兜底 ＋ 标准结论行）────────────
# 律 A2「闸自身不崩律」：异常路径不得吐 traceback 当报告；律 A3「验证器报告完整性律」：
# 末行必为「结论行: 总项数 N ／ FAIL n」（N/n 取自本工具真实计数，不臆造）。
_GATE_CORE_HAS_CONCL = False


def _gate_counts(res):
    """派生「总项数 N ／ FAIL n」：优先真实计数字段，其次检查清单，最后整体判定。"""
    """本工具＝子命令级判定：audit 子命令按引用条数计项、RISK 计 FAIL；其余子命令计 1 项。"""
    import re as _re
    if isinstance(res, str):
        _m = _re.search(r"audit:\s*(\d+)\s*citations\s*\|\s*RISK\s*(\d+)", res)
        if _m:
            return int(_m.group(1)), int(_m.group(2))
    return 1, 0


def run(*args, **kw):
    """技能入口（闸套）：异常兜底 ＋ 标准结论行。"""
    try:
        res = _run_core(*args, **kw)
    except Exception as e:  # ★律 A2：异常路径不吐 traceback 当报告
        res = {"verdict": "FAIL", "error": "%s: %s" % (type(e).__name__, e), "n_fail": 1}
        print("判定: FAIL  异常: %s: %s" % (type(e).__name__, e))
        try:
            import json as _j
            import os as _o
            for _k in ("out", "out_json", "json_out"):
                _v = kw.get(_k)
                if isinstance(_v, str) and _v:
                    _d = _o.path.dirname(_v)
                    if _d:
                        _o.makedirs(_d, exist_ok=True)
                    with open(_v, "w", encoding="utf-8") as _f:
                        _j.dump(res, _f, ensure_ascii=False, indent=1)
                    break
        except Exception:
            pass
        print("结论行: 总项数 1 ／ FAIL 1")
        return res
    if not _GATE_CORE_HAS_CONCL:
        _nt, _nf = _gate_counts(res)
        print("结论行: 总项数 %d ／ FAIL %d" % (_nt, _nf))
    return res


if __name__ == '__main__':
    sys.exit(main())
