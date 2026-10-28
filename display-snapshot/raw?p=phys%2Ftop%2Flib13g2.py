"""SOW-6 共享版图库 v2.3（M1.5 · 组长 b7a0 2026-10-17）· 提炼 SOW-3 两轮实证原语 + M2 需求单全项
==========================================================================
v2.3 变更（2026-10-17T08:3xZ · Q9 三问裁决后空闲轮补齐）：Board.via 增 vt2_cols/vt2_rows
  （TopVia2 阵列档位，官方 via_stack_code.py nx_ny_for_via 第三分支）；t_layer=TopMetal2
  时缺省继承 cols/rows、显式传值覆盖，其余堆缺省 1x1；仅 t_layer=TopMetal2 时向 pcell
  传 vt2_columns/vt2_rows 并在缓存键追加 _vt2{c}x{r} 段——既有调用与缓存键逐位不变。
v2.2 变更（2026-10-17T07:4xZ · via_stack 阵列外推实证后）：
  · Board.via 增 vt1_cols/vt1_rows（TopVia1 阵列档位）；t_layer=TopMetal1 时缺省继承
    cols/rows——修「TM1 跨接堆传阵列静默仍 1x1」坑（官方 nx_ny_for_via 只认 vt1_*）。
    向后兼容：薄金属堆与显式旧调用行为逐位不变。缓存键已含 vt1 档位。
用法（klayout batch 内，pya 由 klayout 注入）：
    . /data/workspace/pdk/kl_env030.sh        # 铁律 0.30.0；0.30.12 启动清 PYTHONPATH 必死
    KLAYOUT_PATH=$KLTECH klayout -zz -r your_gen.py
    your_gen.py:  import sys; sys.path.insert(0, '/data/workspace/phys/top')
                  import lib13g2 as L

v1 内容（SOW-3 hbtdiff + gilbert/amp2 两轮 DRC/LVS 验证）：
  · Board：layout/cell 封装 + rect/wire_h/wire_v/path/label（DBox µm 坐标，Text dbu 坑已处理）
  · Board.mkpc_at：PCell 锚点摆放（HBT 锚=集电极列/原点，电阻锚=P1 下端；mirror=True 绕 y 镜像）
  · Board.via：官方 via_stack PCell（M1↔M2 已验证）
  · Board.bondpad：官方 bondpad PCell（统一默认 octagon——square 分支 evaluate OOM=PDK bug）
  · Board.net_check：连通簇/短路自检（v2 升级：sym_pairs 镜像轴网名互换校验）
  · 层号表 LG：官方 sg13g2.map 提取

v2 新增（M2 需求单 8 项对应，官方真值取 sg13g2_tech.json 运行时直读）：
  · hbtdiff_array：共质心阵列（ABBA/quad 2D pattern + dummy 注入 + 各单元端口坐标返回）
  · via_bucket：减层 stack（如 Via1+TopVia1 各 n 件，M2 横向汇流），返回占位外接框
  · resistor：rsil/rhigh/rppd 按目标 R 自动解 W/L（方阻=官方 rspec 真值）
  · mim_cap：cmim 按目标 C 自动解 W/L（官方密度 1.5 fF/µm²）
  · guard_ring：ptap1(±ntap1) 环 + M1 互连，引出点坐标化
  · keepout：L1 备案禁区标注层 (235,5)（非制造层，不进 DRC）

坑位实录（SOW-3 + 2026-10-17 再实证）：
  ① rect 必须用 pya.DBox（pya.Box 按 dbu 解释，µm 值直接给会被截碎）。
  ② Text 的 Trans 按 dbu 整数解释，µm 值先除以 ly.dbu。
  ③ bondpad PCell shape='square' 分支 evaluate 直接 OOM Killed（PDK pycell bug）；
     bondpad 的参数名映射未解（带显式 params 创建失败）——全链统一默认 octagon。
     注意：参数映射是 per-PCell 的，npn13G2/rsil/rhigh/via_stack/cmim 的 params 实测有效。
  ④ klayout 必须用 0.30.0（kl_env030.sh）；0.30.12 启动清 PYTHONPATH 起不来。
"""
import json
import pya

# SG13G2 GDS 层号（官方 sg13g2.map + SOW-3 两轮 DRC 实证）
LG = {
    "M1": (8, 0), "VIA1": (19, 0), "M2": (10, 0), "VIA2": (29, 0),
    "M3": (30, 0), "VIA3": (49, 0), "M4": (50, 0), "VIA4": (66, 0),
    "M5": (67, 0), "TOPVIA1": (125, 0), "TOPM1": (126, 0),
    "TOPVIA2": (133, 0), "TOPM2": (134, 0),
}
DT_TXT, DT_PIN = 25, 2
_SG13 = "SG13_dev"
_KEEPOUT = (235, 5)  # L1 备案禁区标注层（同 prBoundary 族、非制造、DRC deck 不查）

_TECH_JSON = ("/data/workspace/pdk/ihp_open/ihp-sg13g2/libs.tech/klayout/"
              "python/sg13g2_pycell_lib/sg13g2_tech.json")


def _eng(s):
    """官方 tech.json 的工程字符串 → float（'1.5m'→1.5e-3, '0.78u'→7.8e-7, '1m'→1e-3）"""
    s = str(s).strip()
    mult = {"u": 1e-6, "n": 1e-9, "m": 1e-3, "k": 1e3, "M": 1e6}
    if s and s[-1] in mult:
        return float(s[:-1]) * mult[s[-1]]
    return float(s)


_GRID = 0.005  # SG13G2 绘图 grid（µm）——传给 PCell 的 w/l 必须 snap，否则 Offgrid 族 DRC 违规


def snap(x, g=_GRID):
    return round(x / g) * g


def tech_params():
    """官方 sg13g2_tech.json techParams 段（真值唯一来源，不硬编码）"""
    global _TP
    try:
        return _TP
    except NameError:
        _TP = json.load(open(_TECH_JSON))["techParams"]
        return _TP


class Dev:
    """已摆放器件：各端在 top 坐标下的引脚中心（µm）"""

    def __init__(self, name, cell, trans, kind, board):
        self.name, self.cell, self.kind, self.b = name, cell, kind, board
        self.trans = trans
        self.p = {}
        m1p = board.pin_centers(cell, "M1")
        m2p = board.pin_centers(cell, "M2")
        if kind == "hbt":
            t = board.rec_texts(cell)
            self.p["C"] = self.xf(board.nearest(m1p, t["C"]))
            self.p["B"] = self.xf(board.nearest(m1p, t["B"]))
            self.p["E"] = self.xf(board.nearest(m2p, t["E"]))
        elif kind == "pad":
            # bondpad：官方 pin 在 TopMetal 层（TM2=134），M1 无 pin——锚点即中心
            tm = board.pin_centers(cell, "TOPM2") or board.pin_centers(cell, "TOPM1")
            self.p["PAD"] = self.xf(tm[0]) if tm else (self.trans.disp.x, self.trans.disp.y)
        elif kind == "tap":
            # ptap1/ntap1：单端（M1 引脚），引出点=pin 中心
            if m1p:
                q = self.xf(m1p[0])
                self.p["T"] = q
            else:
                self.p["T"] = (self.trans.disp.x, self.trans.disp.y)
        elif kind == "cap":
            # cmim：官方 pin = 底板 Metal5 + 顶板 TopMetal1（无 M1/M2 pin）
            m5p = board.pin_centers(cell, "M5")
            tm1 = board.pin_centers(cell, "TOPM1")
            if m5p:
                self.p["BOT"] = self.xf(m5p[0])
            if tm1:
                self.p["TOP"] = self.xf(tm1[0])
        else:  # 电阻：两个 M1 引脚按 y 分下/上端
            s = sorted((self.xf(q) for q in m1p), key=lambda q: q[1])
            self.p["P1"], self.p["P2"] = s[0], s[-1]

    def xf(self, pt):
        q = self.trans * pya.DPoint(pt[0], pt[1])
        return (q.x, q.y)

    def report(self):
        return f"{self.name:8s} {self.kind:4s} " + " ".join(
            f"{k}=({v[0]:.3f},{v[1]:.3f})" for k, v in self.p.items())


class Board:
    def __init__(self, top_name, W=0.30):
        self.ly = pya.Layout()
        self.ly.technology_name = "sg13g2"
        self.top = self.ly.create_cell(top_name)
        self.W = W
        self._l = {}
        self.devs = {}

    # ---- 层与基本图形 ------------------------------------------------------
    def layer(self, name):
        if name not in self._l:
            g = LG[name]
            self._l[name] = self.ly.layer(g[0], g[1])
        return self._l[name]

    def rect(self, lname, x1, y1, x2, y2):
        # 必须用 DBox：pya.Box 的坐标按 dbu 解释，给 µm 会被截成碎片（SOW-3 坑）
        self.top.shapes(self.layer(lname)).insert(pya.DBox(x1, y1, x2, y2))

    def wire_h(self, lname, y, x1, x2, w=None):
        w = w or self.W
        self.rect(lname, min(x1, x2), y - w / 2, max(x1, x2), y + w / 2)

    def wire_v(self, lname, x, y1, y2, w=None):
        w = w or self.W
        self.rect(lname, x - w / 2, min(y1, y2), x + w / 2, max(y1, y2))

    def path(self, lname, pts, w=None):
        """直角折线；斜段自动拆成 L（本设计只走直角）"""
        for a, b in zip(pts, pts[1:]):
            if abs(a[1] - b[1]) < 1e-9:
                self.wire_h(lname, a[1], a[0], b[0], w)
            elif abs(a[0] - b[0]) < 1e-9:
                self.wire_v(lname, a[0], a[1], b[1], w)
            else:
                self.wire_h(lname, a[1], a[0], b[0], w)
                self.wire_v(lname, b[0], a[1], b[1], w)

    def label(self, lname, x, y, text):
        """网名标注到该金属的 text 层（datatype=25）；Text 的 Trans 按 dbu 整数解释（SOW-3 坑）"""
        dbu = self.ly.dbu
        li = self.ly.layer(LG[lname][0], DT_TXT)
        t = pya.Trans(pya.Trans.R0, int(round(x / dbu)), int(round(y / dbu)))
        self.top.shapes(li).insert(pya.Text(text, t))

    # ---- PCell 摆放 --------------------------------------------------------
    def pin_centers(self, cell, lname):
        out = []
        li = self.ly.layer(LG[lname][0], DT_PIN)
        for s in cell.each_shape(li):
            if s.is_box() or s.is_path():
                out.append((s.dbbox().center().x, s.dbbox().center().y))
        return out

    def rec_texts(self, cell):
        """63/0 器件标注文本（端名等）→ {text: (x µm, y µm)}"""
        d = self.ly.dbu
        out = {}
        for s in cell.each_shape(self.ly.layer(63, 0)):
            if s.is_text():
                out[s.text.string] = (s.text.trans.disp.x * d, s.text.trans.disp.y * d)
        return out

    @staticmethod
    def nearest(pts, p):
        return min(pts, key=lambda q: (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)

    def mkpc_at(self, name, pname, params, target, kind, mirror=False):
        """锚点摆放：HBT 锚=集电极列 x、cell 原点 y；电阻锚=P1(下端引脚中心)。
        mirror=True：先绕 y 轴左右镜像，再把锚点落到 target（对称轴 = (原x+target.x)/2）。"""
        cell = self.ly.create_cell(pname, _SG13, params)
        assert cell is not None, f"PCell {pname} {params} 创建失败"
        if kind == "hbt":
            t = self.rec_texts(cell)
            ax, ay = t["C"][0], 0.0
        elif kind == "cap":
            # cmim 无 M1 pin，锚=bbox 中心
            bb = cell.dbbox()
            ax, ay = (bb.left + bb.right) / 2, (bb.bottom + bb.top) / 2
        else:
            ps = self.pin_centers(cell, "M1")
            ax = (min(p[0] for p in ps) + max(p[0] for p in ps)) / 2
            ay = min(p[1] for p in ps)
        tr = pya.DTrans(pya.DVector(target[0], target[1]))
        if mirror:
            tr = tr * pya.DTrans(pya.Trans(2, True, 0, 0))
        tr = tr * pya.DTrans(pya.DVector(-ax, -ay))
        self.top.insert(pya.DCellInstArray(cell, tr))
        d = Dev(name, cell, tr, kind, self)
        self.devs[name] = d
        return d

    def _pcell(self, key, pname, params):
        """按参数组合缓存 PCell 代理 cell（避免同名重复创建出 name$1 漂移）"""
        if not hasattr(self, "_pc"):
            self._pc = {}
        if key not in self._pc:
            c = self.ly.create_cell(pname, _SG13, params)
            assert c is not None, f"PCell {pname} {params} 创建失败"
            self._pc[key] = c
        return self._pc[key]

    def via(self, x, y, b_layer="Metal1", t_layer="Metal2", cols=2, rows=2,
            vt1_cols=None, vt1_rows=None, vt2_cols=None, vt2_rows=None):
        """官方 via_stack PCell（M1↔M2 为 SOW-3 验证组合）。
        v2.3（2026-10-17）：TopVia2 阵列档位走 vt2_columns/vt2_rows（官方 nx_ny_for_via
        第三分支；SG13G2 has_top_metal2=True 恒注册）。t_layer=TopMetal2（堆含 TopVia2）
        时缺省继承 cols/rows，显式传值覆盖；其余堆 vt2 恒 1x1 且不向 pcell 传该键
        （官方 setupParams 按 in-params 兼容）。缓存键含 vt2 档位（仅 TM2 顶堆追加段）。
        v2.2（2026-10-17 阵列外推实证后补）：TopVia1 阵列档位走 vt1_columns/vt1_rows，
        与 vn_columns/vn_rows 无关（官方 via_stack_code.py nx_ny_for_via；cols/rows 给
        TM1 跨接堆传 3x2 会静默仍出 1x1=坑）。约定：t_layer=TopMetal1 时 vt1_cols/rows
        缺省继承 cols/rows（阵列语义跨堆一致）；显式传值则覆盖；薄金属堆不受影响。
        阵列外推真值（2026-10-17 实测）：cut pitch=0.41µm（双向，薄金属）；平台=阵列
        外沿 +0.05µm/侧（每层一块合并矩形，非逐 via 小 pad）；TopVia1 pitch 实测 0.84µm。
        注：M?↔TopMetal2 长堆中 TopVia1 段按 v2.2 规则缺省 1x1（vt1_cols/rows 显式给可解）。
        """
        if t_layer == "TopMetal1":
            vt1c = cols if vt1_cols is None else vt1_cols
            vt1r = rows if vt1_rows is None else vt1_rows
        else:
            vt1c = 1 if vt1_cols is None else vt1_cols
            vt1r = 1 if vt1_rows is None else vt1_rows
        if t_layer == "TopMetal2":
            vt2c = cols if vt2_cols is None else vt2_cols
            vt2r = rows if vt2_rows is None else vt2_rows
            key = f"via_{b_layer}_{t_layer}_{cols}x{rows}_vt{vt1c}x{vt1r}_vt2{vt2c}x{vt2r}"
            params = {"b_layer": b_layer, "t_layer": t_layer,
                      "vn_columns": cols, "vn_rows": rows,
                      "vt1_columns": vt1c, "vt1_rows": vt1r,
                      "vt2_columns": vt2c, "vt2_rows": vt2r}
        else:
            key = f"via_{b_layer}_{t_layer}_{cols}x{rows}_vt{vt1c}x{vt1r}"
            params = {"b_layer": b_layer, "t_layer": t_layer,
                      "vn_columns": cols, "vn_rows": rows,
                      "vt1_columns": vt1c, "vt1_rows": vt1r}
        c = self._pcell(key, "via_stack", params)
        self.top.insert(pya.DCellInstArray(c, pya.DTrans(pya.DVector(x, y))))
        return c

    def bondpad(self, x, y, diameter=80.0, shape="octagon", name=None):
        # 官方 PCell 默认参数创建（octagon，tech 默认 diameter）。
        # 2026-10-17 实证两坑：① shape='square' 分支 evaluate OOM（PDK pycell bug，Killed）；
        # ② bondpad 的参数名映射未解（create_cell 带显式 params 创建失败）。统一默认 octagon。
        c = self._pcell("bondpad_default", "bondpad", {})
        self.top.insert(pya.DCellInstArray(c, pya.DTrans(pya.DVector(x, y))))
        if name:
            self.devs[name] = Dev(name, c, pya.DTrans(pya.DVector(x, y)), "pad", self)
        return c

    # ---- v2：共质心 HBT 阵列 -----------------------------------------------
    def hbtdiff_array(self, pattern, target, nx=1, pitch=7.40, row_pitch=7.85,
                      dummies=0, mirror=True):
        """共质心 HBT 阵列（M2 需求单 #1）。
        pattern：str（1D，如 'ABBA'）或 list[str]（2D，如 ['AB','BA']）；
          同一字符=同一差分半边（同一 net 组）；'.'=dummy。
        dummies：1D 模式下两端各注入 dummies 颗 dummy（2D 模式忽略，请显式写 '.'）。
        pitch：实例中心距。**官方 Nx=1 bbox=6.7µm，pSD↔n+Activ 间距需 0.7µm →
          最小实例 pitch=7.40µm（2026-10-17 DRC 二分实测：6.7/6.75/7.0 违规 pSD.b，7.4 起干净）**。
          真值表 v1 的 1.85µm 是多指方向 C 轨 step（Nx 档 bbox 增量），不是实例间距——勘误见真值表 v1.1。
        row_pitch：行距（bbox 高 7.11 + 0.7 余量 → 7.85）。
        mirror=True：1D 中线右半单元绕 y 镜像（SOW-3 差分对口径，镜像行 DRC 同验干净）；2D 恒不镜像。
        返回 ({char: [Dev,...]}, 阵列中心)；dummy 归在 'D' 键。"""
        if isinstance(pattern, str):
            rows = [pattern]
            if dummies:
                rows[0] = "." * dummies + rows[0] + "." * dummies
        else:
            rows = [r for r in pattern]
        ncol = max(len(r) for r in rows)
        nrow = len(rows)
        cx, cy = target
        x0 = cx - (ncol - 1) * pitch / 2.0
        y0 = cy + (nrow - 1) * row_pitch / 2.0   # pattern[0] 是最上行
        params = {"Nx": nx}
        out = {}
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                ch = "." if ch == "." else ch
                x = x0 + i * pitch
                y = y0 - j * row_pitch
                mirror_i = False
                if mirror and nrow == 1 and ncol > 2:
                    c_mid = (ncol - 1) / 2.0
                    mirror_i = i > c_mid
                d = self.mkpc_at(f"{ch}{j}_{i}", "npn13G2", dict(params), (x, y), "hbt",
                                 mirror=mirror_i)
                out.setdefault(ch, []).append(d)
        center = (x0 + (ncol - 1) * pitch / 2.0, y0 - (nrow - 1) * row_pitch / 2.0)
        return out, center

    # ---- v2：减层 via 桶 ----------------------------------------------------
    @staticmethod
    def _factor(n):
        """n 件最方分解 cols×rows（精确 n；取长宽比最接近 1 的因子对）"""
        best = (n, 1)
        for a in range(int(n ** 0.5), 0, -1):
            if n % a == 0:
                best = (n // a, a)
                break
        return best

    def via_bucket(self, x, y, n_total, layers=(("Metal1", "Metal2"), ("Metal2", "TopMetal1")),
                   ext=0.3, tag=""):
        """减层 via 桶（M2 需求单 #2；R-VIA-01 v1.2 减层 stack 口径）。
        每层 n_total 件（cols×rows 最方分解），自底向上：底层阵列→金属平台→上层阵列→平台。
        ext=金属平台超出阵列的外扩（µm）。返回 {pair: {'n':int,'cols','rows','bbox':(x1,y1,x2,y2)}}。
        注意：TopVia1（M2↔TopMetal1）为跨厚金属组合，官方 DRC 冒烟随 M2 里程碑实跑销点。"""
        res = {}
        cx, cy = x, y
        for bi, (bl, tl) in enumerate(layers):
            cols, rows = self._factor(n_total)
            c = self.via(cx, cy, b_layer=bl, t_layer=tl, cols=cols, rows=rows)
            bb = c.dbbox()
            w, h = bb.width(), bb.height()
            x1, y1 = cx - w / 2 - ext, cy - h / 2 - ext
            x2, y2 = cx + w / 2 + ext, cy + h / 2 + ext
            res[f"{bl}->{tl}"] = {"n": n_total, "cols": cols, "rows": rows,
                                  "bbox": (x1, y1, x2, y2)}
            print(f"[via_bucket{(' '+tag) if tag else ''}] {bl}->{tl} {cols}x{rows}={n_total}件 "
                  f"bbox=({x1:.2f},{y1:.2f})~({x2:.2f},{y2:.2f})", flush=True)
            # 金属平台（下层板已含在 PCell 内，这里补上层汇流板）
            pl = "M2" if bl == "Metal2" else ("TOPM1" if tl == "TopMetal1" else None)
            if pl:
                self.rect(pl, x1, y1, x2, y2)
        return res

    # ---- v2：电阻 / MIM 电容 -------------------------------------------------
    def resistor(self, name, model, r_target, target, w=None, mirror=False):
        """rsil/rhigh/rppd 按目标 R 自动解 W/L（M2 需求单 #3）。
        方阻与 minW/minL 取官方 sg13g2_tech.json rspec/minL/minW 真值；
        名义口径 R = rspec×L/W（PCell 自带端头修正）；蛇形不在此版（M3 按需）。
        返回 Dev（kind='res'，P1 下端/P2 上端）。"""
        tp = tech_params()
        rspec = _eng(tp[f"{model}_rspec"])
        # tech.json 长度为米制（'0.50u'=5e-7 m）→ ×1e6 转 µm（2026-10-17 坑：不转换解出 l≈2e-6µm）
        minL = _eng(tp[f"{model}_minL"]) * 1e6
        minW = _eng(tp[f"{model}_minW"]) * 1e6
        maxL = _eng(tp[f"{model}_maxL"]) * 1e6
        w = w or minW
        length = r_target * w / rspec
        if length < minL:            # 太短：顶到 minL，反解加宽
            length = minL
            w = rspec * length / r_target
        assert w >= minW - 1e-9, f"{name}: 解出 w={w:.3f} < minW={minW}"
        assert length <= maxL, f"{name}: l={length:.1f} 超 maxL={maxL*1e3:.0f}µm，请改蛇形"
        # snap 到 0.01（半宽也对齐 0.005 grid；0.005 级 snap 会出 w/2 相位 offgrid——rhigh 0.625 实证）
        length, w = snap(length, 0.01), snap(w, 0.01)
        r_nom = rspec * length / w
        d = self.mkpc_at(name, model,
                         {"Calculate": "l", "l": f"%.3fu" % length, "w": f"%.3fu" % w},
                         target, "res", mirror=mirror)
        print(f"[resistor] {name} {model} 目标={r_target}Ω → grid 落位 l={length}µm w={w}µm "
              f"名义 R={r_nom:.2f}Ω", flush=True)
        return d

    def mim_cap(self, name, c_fF, target, square=True):
        """cmim 按目标 C 自动解 W/L（M2 需求单 #4）。
        官方面密度 Cspec = cmim_caspec = 1.5 fF/µm²（sg13g2_tech.json，2026-10-17 读出备案）。
        square=True 时 w=l=sqrt(C/Cspec)。返回 (Dev|None, (w,l), c_nominal_fF)。"""
        tp = tech_params()
        # cmim_caspec='1.5m'（F/m²）→ fF/µm²：×1e15(fF/F)÷1e12(µm²/m²)=×1e3 → 官方密度 1.5 fF/µm²
        cspec = _eng(tp["cmim_caspec"]) * 1e3
        minlw = _eng(tp["cmim_minLW"]) * 1e6 if "cmim_minLW" in tp else 5.0
        area = c_fF / cspec
        side = area ** 0.5
        assert side >= minlw, f"{name}: {side:.2f}µm < cmim_minLW={minlw}"
        # 相位对齐（官方 cmim generateVias：n=fix((w+0.12)/1.26)，xoffset=(w-(n*1.26-0.12))/2
        # 须落在 0.005 grid——即 w 与 n*1.26-0.12 同 0.01 相位，否则内部 Vmim 阵列全体 offgrid
        # （2026-10-17 实证：23.665 → vmim_offgrid×1296；23.66 干净）。TV1_a=0.42,Mim_d=0.36。
        n = int((side + 0.12) / 1.26 + 1e-9)
        w1 = n * 1.26 - 0.12
        side = w1 + round((side - w1) / 0.01) * 0.01
        assert int((side + 0.12) / 1.26 + 1e-9) == n, f"{name}: 相位 snap 跨过 via 计数档"
        w = l = side
        c_nom = cspec * w * l                   # 落位后名义值
        d = self.mkpc_at(name, "cmim",
                         {"Calculate": "w&l", "w": "%.3fu" % w, "l": "%.3fu" % l},
                         target, "cap")
        print(f"[mim_cap] {name} 目标={c_fF}fF @ {cspec}fF/µm² → {w}×{l}µm 名义 C={c_nom:.1f}fF",
              flush=True)
        return d, (w, l), c_nom


    # ---- v2：guard ring / keepout --------------------------------------------
    def _place_tap(self, pname, x, y, name=None):
        """tap 单元（ptap1/ntap1，默认 0.78×0.78）按 pin 中心锚到 (x,y)。返回 Dev|None"""
        c = self._pcell(f"{pname}_default", pname, {})
        ps = self.pin_centers(c, "M1")
        ax = ay = 0.0
        if ps:
            ax = sum(p[0] for p in ps) / len(ps)
            ay = sum(p[1] for p in ps) / len(ps)
        tr = pya.DTrans(pya.DVector(x - ax, y - ay))
        self.top.insert(pya.DCellInstArray(c, tr))
        if name:
            d = Dev(name, c, tr, "tap", self)
            self.devs[name] = d
            return d
        return None

    def guard_ring(self, x1, y1, x2, y2, step=2.2, w_ring=0.5, inner_ntap=False,
                   step_n=2.8):
        """保护环（M2 需求单 #5）：ptap1 沿矩形四边等距排布 + M1 环互连；
        inner_ntap=True 时内缩 2µm 再一圈 ntap1（nwell，接高电位——与器件阱区间距 DRC 未验证，默认关）。
        tap 等距分布（间距=min(step, 边长/整数段)）——尾段禁止挤压（append 式摆法 0.2µm 尾距实证违规）。
        step_n：ntap 环专用最小中心距。ntap1 自带 NBL 层宽 1.26µm，NBL same-net
        space=1.5µm（NBL.b）→ 中心距 ≥2.76，默认 2.8（v2b 冒烟 2.2/2.4 实证 ×42 违规后定）。
        返回 {'pg':(x,y), 'ng':(x,y)|None, 'n_tap':int}。"""

        def _axis(a, b, st=None):
            # floor 段数 → 每段 ≥ step；段长 snap 0.005、每点 snap——非 grid 坐标=全体 offgrid（实证）
            st = st or step
            n = max(2, int((b - a) / st) + 1)
            if n == 2:
                return [a, b]
            seg = snap((b - a) / (n - 1))
            out = [snap(a + i * seg) for i in range(n - 1)]
            out.append(b)
            return out

        n = 0
        xs = _axis(x1, x2)                 # 底/顶边
        ys = _axis(y1, y2)                 # 左/右边
        for x in xs:
            self._place_tap("ptap1", x, y1)
            self._place_tap("ptap1", x, y2)
            n += 2
        for y in ys[1:-1]:
            self._place_tap("ptap1", x1, y)
            self._place_tap("ptap1", x2, y)
            n += 2
        self.path("M1", [(x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)], w=w_ring)
        pg = (x1, (y1 + y2) / 2)
        ng = None
        if inner_ntap:
            inset = 2.0
            a1, b1, a2, b2 = x1 + inset, y1 + inset, x2 - inset, y2 - inset
            xs2 = _axis(a1, a2, st=step_n)
            ys2 = _axis(b1, b2, st=step_n)
            for x in xs2:
                self._place_tap("ntap1", x, b1)
                self._place_tap("ntap1", x, b2)
            for y in ys2[1:-1]:
                self._place_tap("ntap1", a1, y)
                self._place_tap("ntap1", a2, y)
            self.path("M1", [(a1, b1), (a2, b1), (a2, b2), (a1, b2), (a1, b1)], w=w_ring)
            ng = (a2, (b1 + b2) / 2)
        self.label("M1", pg[0], pg[1], "pg")
        if ng:
            self.label("M1", ng[0], ng[1], "ng")
        print(f"[guard_ring] ptap×{n} 环 ({x1},{y1})~({x2},{y2}) pg={pg} ng={ng}", flush=True)
        return {"pg": pg, "ng": ng, "n_tap": n}

    def keepout(self, x1, y1, x2, y2, text):
        """L1 备案禁区标注（M2 需求单 #6）：非制造层 (235,5) rect+text，不进 DRC。"""
        li = self.ly.layer(*_KEEPOUT)
        self.top.shapes(li).insert(pya.DBox(x1, y1, x2, y2))
        dbu = self.ly.dbu
        t = pya.Trans(pya.Trans.R0, int(round((x1 + 0.5) / dbu)), int(round((y2 - 0.5) / dbu)))
        self.top.shapes(li).insert(pya.Text(text, t))
        print(f"[keepout] ({x1},{y1})~({x2},{y2}) {text}", flush=True)

    # ---- 自检与落盘 --------------------------------------------------------
    def net_check(self, which="ALL", pad=2, sym_pairs=None, axis_x=None, tol=0.05):
        """连通簇/短路自检（SOW-3 net_check.py 内置化）。返回 (簇数, 短路嫌疑列表)。
        v2 升级：sym_pairs=[('lopd','lond'),…] + axis_x → 镜像轴两侧网名互换校验（M2 需求单 #7）：
        要求每对网名的 label x 坐标集合互为轴镜像（|x_a − (2·axis_x − x_b)| ≤ tol）。"""
        import klayout.db as db
        sel = {"M1": [("M1", 0), ("M1", DT_PIN)],
               "M2": [("M2", 0), ("M2", DT_PIN)],
               "ALL": [("M1", 0), ("M1", DT_PIN), ("M2", 0), ("M2", DT_PIN)]}[which]
        dbu = self.ly.dbu
        reg = db.Region()
        for ln, dt in sel:
            li = self.ly.layer(LG[ln][0], dt)
            for s in self.top.begin_shapes_rec(li):
                reg.insert(s.shape().polygon.transform(s.trans()))
        polys = list(reg.merged().each_merged())
        labels = []
        for ln in {ln for ln, _ in sel}:
            li = self.ly.layer(LG[ln][0], DT_TXT)
            for s in self.top.begin_shapes_rec(li):
                if s.shape().is_text():
                    t = s.shape().text
                    labels.append((t.string,
                                   (t.trans.disp.x + s.trans().disp.x) * dbu,
                                   (t.trans.disp.y + s.trans().disp.y) * dbu))
        groups = {}
        for name, x, y in labels:
            p = db.Point(int(round(x / dbu)), int(round(y / dbu)))
            hit = -1
            for i, poly in enumerate(polys):
                bb = poly.bbox()
                # 先 bbox 粗筛再 contains 精判：环形/凹形多边形 bbox 误吸环内点
                # （v2b 实证：ng 内环 bbox 把环内 in1/out1 误归同簇=假短路，2026-10-17）
                if (bb.left - pad <= p.x <= bb.right + pad
                        and bb.bottom - pad <= p.y <= bb.top + pad
                        and poly.touches(db.Box(p.x, p.y, p.x, p.y))):
                    hit = i
                    break
            groups.setdefault(hit, []).append(name)
        # 悬空桶（hit=-1）不参与短路判定：悬空 label 各自独立，非同簇金属
        # （v2a 复跑实证：4 个悬空 quad label 被误报成 lopd/lond 短路，2026-10-17）
        shorts = [sorted(set(v)) for k, v in groups.items() if k != -1 and len(set(v)) > 1]
        print(f"[net_check/{which}] 簇={len(polys)} 标注={len(labels)} "
              f"短路嫌疑={shorts if shorts else '无'} 悬空={groups.get(-1, [])}", flush=True)
        if sym_pairs and axis_x is not None:
            import collections
            pts = collections.defaultdict(list)
            for name, x, y in labels:
                pts[name].append(x)
            for a, b in sym_pairs:
                A = sorted(pts.get(a, []))
                B = sorted(pts.get(b, []))
                Bm = sorted(2 * axis_x - bx for bx in B)
                ok = (A and B and len(A) == len(B)
                      and all(abs(u - v) <= tol for u, v in zip(A, Bm)))
                detail = (f"A@{['%.2f' % v for v in A]} vs mirror(B)@{['%.2f' % v for v in Bm]}"
                          if not ok else "")
                print(f"[sym] {a}<->{b} 轴x={axis_x}: {'OK' if ok else 'FAIL ' + detail}", flush=True)
        return len(polys), shorts

    def save(self, path):
        self.ly.write(path)
        print(f"bbox={self.top.dbbox()}  →  {path}", flush=True)
