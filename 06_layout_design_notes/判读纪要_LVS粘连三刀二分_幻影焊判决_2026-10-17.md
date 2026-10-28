# 判读纪要：LVS 粘连三刀二分 → 幻影焊判决（2026-10-17 晚 · b7a0）

**口径**：v17 对拍 FAIL 两簇——簇乙=XBI1..4/nref+gnd（镜像区）、簇甲=ccas1+ccas2+e1+e2+nbcas（主管区）。
**一句话判决**：**两簇粘连均为 deck 幻影焊**——真实连通图（含 pwell/ptap/cont 半导体链的全保真 flood）在两个最小案发现场上完全分离；焊接发生在 npn13G2 器件端子识别层（body 级矩形端子区 + 骑体金属拽网）。版图与 PCell 几何无罪（第三次），设计金属走线无罪（b7e7 净距清单 + 本轮刀证互证）。

---

## 一、刀单与结果总表（12 变体，net_only 提取，基线=drv2_v17_netonly）

| 变体 | 刀 | 簇乙(XBI1..4/nref+gnd) | 簇甲(ccas1+ccas2+e1+e2+nbcas) | 判读 |
|---|---|---|---|---|
| ctrl_asis | 原样重写 | 原样 | 原样 | 手术管线无罪 |
| clip_bottom | y<140 空间二分 | **原样复现**（含 R$13 m=4 合体） | 无 | 簇乙纯局部生成 |
| clip_top | y>140 空间二分 | 无 | **原样复现** | 簇甲纯局部生成 |
| k2_noRES | 删 128/0（电阻器件全灭） | **原样** | **原样** | **电阻派生/端子切片无罪**（嫌疑排除） |
| k6_noM2 | 删 10/0 | **全散**（零 merge） | **全散**（ccas1/ccas2 干净） | **M2=两簇焊接承重层** |
| k4_noM5 | 删 67/0 | 散但 XQr 全端子+Rin.P2 并进 gnd；Rref 四远端分家 | 裂为 ccas1\|e1 + ccas2\|e2（nbcas 标签消失残段孤立） | M5 参与 nbcas 桥与网名归属 |
| k5_noM4 | 删 50/0 | 全散（比 k4 更碎） | 同 k4（nbcas 出簇） | M4 与 M5 对簇甲等效；M4 必要于乙簇焊接 |
| ct_XQ1only | 单管（XQ1+XQ3 半列） | — | **ccas1\|e1 单管即焊** | **管内 C/E 混淆实锤** |
| ct_XQ1_noM5 | 单管+删 M5 | — | ccas1\|e1 不变 | 甲核焊接不依赖 M5 |
| cb_G1only | 单组1（XQo+XQr） | **XBI1/nref⊕gnd 单组即焊**（连过路 Rin2.P2 也入簇） | — | 组内 1.35µm 缝机制 |
| k1_noM1 | 删 8/0 | 全灭（器件全灭，粗糙刀） | 全灭 | 仅证 Rref m=4 合体依赖 M1 |
| k3_noNWmain | （作废） | — | — | **全 GDS 无 31/0 nwell、无 60/0 digisub**——「nwell 掘断 pwell」假说证伪于探测第一步 |

**副产物**：①全版无 nwell/digisub ⇒ pwell=整片 CHIP，Q$1~12 sub 同为 $1 全局节点 ✓（解释 sub=$1）；②R$21 m=4 合体=四条 Rref P2 已被并网（粘连的另一表现）。

## 二、幻影焊判决（决定性实验）

**flood_full.py**——按 deck general_connections 逐条复刻 connect 图（pwell↔ptap↔cont↔M1、poly_con↔cont、全金属链），派生 pwell=CHIP、ptap=activ∩psd−gatpoly：

| 最小案发现场 | deck 提取 | 全保真连通 flood |
|---|---|---|
| cb_G1only（单组） | XBI1/nref⊕gnd 焊 | **XBI1/nref 独占、gnd 独占** |
| ct_XQ1only（单管） | ccas1⊕e1 焊 | **ccas1、e1 各自独占** |

⇒ 连通层零短路（半导体链也查了，此前两轮 metal-only flood 未覆盖此链）⇒ 焊接不在物理连通，**在器件端子识别**。

## 三、机制族定位（deck 原文 + 骑体普查）

**bjt_derivations.lvs 55~66 行**（原文）：
```
npn13G2_dev = npn_dev.join(nsd_block).extents.covering(e_pin).covering(b_pin).covering(c_pin)  # covering bbox!
npn13G2_c   = npn13G2_dev.sized(-1nm)          # 整个包络盒
npn13G2_tc  = (dev − c) ∩ c_pin                # 1nm 边框环 ∩ c_pin
npn13G2_b   = dev − c_pin                      # ≈ 整个 body 矩形!
npn13G2_tb  = b − e_pin
npn13G2_e/te = e_pin                           # 0.07×0.9µm 窗
```
**端子识别区是 body 级矩形族**（covering=bbox 包络）。extract_devices 把 'C'/'B'/'E'/'S'+tC/tB/tE/tS 注入端子识别——骑体金属落入端子矩形即被拽进该端子节点。

**骑体普查（真 GDS 逐件坐实，组1+主管左列）**：
- XQr body ← gnd **M2 穿廊臂压体 3.35µm**（b7e7 净距清单 §四坐标逐位吻合）、← B/C M1 竖线+M5 柱顶骑体
- XQo body ← 自身 E M2 线、← gnd M4 立柱、← ntail M1 竖线进体 2.54µm（109.24~111.78）
- XQ1 body ← ccas1 M1 立管 2.54µm、← **bin B 细线束压体 11.67µm 宽**、← e1 M2 回流臂压体 3.32µm 高
- XQ3 body ← ccas1 立管 3.32µm、← nbcas M5 立线 2.19µm、← M1 立线(-34.15,191.24~193.78)（网名待查）

**骑体拽网定律**（观察反推，指派细节候 b7e7 用最小复现件锁定）：
> 骑体金属落入端子识别区 → 拽进该端子节点；命中**非自身所连**端子区 ⇒ 幻影焊；命中自身区 ⇒ 无表面效应。
- ntail 幸免：竖线命中 XQo 真 C 端子区（自己）✓
- bin/bb1 幸免：细线束命中真 B 区（自己）✓
- outp/outn 幸免：不骑体或命中自身区 ✓
- gnd⊕XBIk：gnd 骑体段命中对方 B/E 区、XBIk 柱命中 E 区 → 互拽 ✓
- ccas1⊕e1：立管/回流臂命中对方端子区 → 互拽 ✓

## 四、留档资产（phys/sow6_run/run_v2/lvs/）
- knife/*.gds ×11 + knife/<名>/ 提取件 ×12（ctrl+k1/k2/k4/k5/k6+clip_bottom/clip_top+ct_×3+cb_×3）
- knife_surgeon.py / knife_surgeon2.py / knife_surgeon3.py（手术脚本）；flood_full.py（全保真连通验尸，含半导体链——**比 metal-only connect_autopsy 强，建议列 LVS 排障标准件**）
- 层号新证：M2=10/0、M4=50/0、M5=67/0、cont=6/0、gatpoly=21/0、polyres=128/0、extblock=111/0；npn13G2 PCell 内部携 activ/psd/nsd_block/emwind/trans/cont/M1/M2/VIA1——**31/0 nwell 与 60/0 digisub 全版不存在**
- 已知残留：R$13/14 P2=$67/$68（rsil 远端标签缺失，与粘连无关的孤立现象，k1 变体中变 $150/$151）；主管 ptap_holes=0 复刻缺口与本案同源（同一 npn 派生族，npn_mk=trans∩ptap_holes 在主管应为非空）

## 五、下一步交棒（b7e7）
1. **最小复现件**：ct_XQ1only.gds / cb_G1only.gds（knife/ 目录，提取件同目录）——用 KLayout 单步 dump npn13G2_dev/c/b/tc/tb/te 于两件之上，把骑体金属与各端子区相交逐一对照 → 锁定「区→节点」指派定律（custom_bjt_extractor.lvs Ruby 段是主战场）
2. 主管 ptap_holes=0 缺口：npn_mk=trans(26/0)∩pwell∩ptap_holes 在主管四管必为非空（否则无器件）——对我 replica 的 ptap_holes 链修正后，簇甲派生可全文复刻
3. **工程规避预案（M4 设计输入）**：若 deck 短期不修，版图规避=外部金属不覆盖 PCell body bbox（M2 回流臂/立管/立线绕体走）——drv2 拓扑不动，仅走线避让；与 LVS 列候办（v2b 网表对齐）并行推进
4. v2b 口径维持正线；v18 补环照旧立项（pwell 浮阱是独立的真问题）

—— b7a0 · 2026-10-17 晚（UTC 12:1x）
