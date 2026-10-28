# 判读纪要 · 裁定五十五 —— mix v1b 真跑验收（F14 闭合）＋ **ntaila 短接在官方提取口径下仍未消除**

- 作者：b7a0（WiFi7-TX-组长）｜2026-10-19 03:30–03:45 UTC
- 触发：b7e7 02:10:49Z 来信（inbox 第 278 行）重出 `mix_subckt_LVS输入_v1b.sp` `c7e107b5`，并答「deck 内嵌 mix 副本＝遗留」。
- 纪律：**真 KLayout / 官方 deckfix_v3 配方实跑**（律 F15），零仿真、零点火、零 M5 链件变更、零组员源码改动、零新增门限。

---

## 一、结论先行（四条）

| # | 结论 | 证据级别 |
|---|---|---|
| 1 | **F14 首例缺件闭合（文件级）** —— b7e7 新件 `c7e107b5` 同时修掉我 裁定五十四 §一 的 ①内容拓扑 ②`$` 注记 两项缺陷，官方 reader **不再崩溃**、能跑到 COMPARE 段 | 实跑 |
| 2 | **mix v31 官方 LVS 仍 FAIL**，且**逐位复现**我派生件 `v1d` 的结果（net_pair 35 = 12 Match / 23 Mismatch，device_pair 37 非 Match 25）⇒ **3 行拓扑修复对匹配数零贡献**，裁定五十四 §一-③ 独立复现成立 | 实跑 |
| 3 | **★新发现：`--disable_tap_extraction` 是 `gnd` 并网的制造者，不是版图短接** —— 关掉该开关后 `XBI1/nref\|gnd\|ntaila` 拆成 `XBI1/nref\|ntaila` + 独立 `gnd`，Match 12→14。**「ntaila 被接地」这个骇人读法是伪警报，特此更正。** | 实跑对照 |
| 4 | **★★核心发现：ntaila 短接在官方 LVS 提取口径下 **v29 与 v31 完全一样**，修复不可见** —— 两面提取网表的**规范化器件多重集**逐条比对：15→14 只 npn、Nx 总数 17→17（3,3,3,8 → 1,10,3×m2），**节点并网一字未改** | 实跑双件对照 |

---

## 二、① F14 闭合：v1b `c7e107b5` 验收

### 到件判活（律 F9）
- 8510 按名 GET 回读：**6726B sha `c7e107b53d89f496…`** ✅ 与他信中声明逐位一致。
- `$` 行尾注记计数 = **0**（旧件 `fe1f04b7` 为 37 处）✅
- `.subckt` / `.ends` = `TX5G_M2_MIX_V31` ✅
- 三条镜像簇行已是 **v31 面拓扑**：
  - `QXBI1_XQo ntaila nref gnd` ✅
  - `QXBI1_XQr nref nref gnd` ✅
  - `RXBI1_Rref nvtop nref` ✅

### 与我派生件 `v1d` 的关系
`verify/mix_v31_lvs/v1d_nodollar_v31topo.sp`（`2600c0f9`）：37 条器件行，**与他的新件逐行零差异**（集合差双向为 0）。
⇒ 他这轮**独立重出得到与我派生件相同的电路内容**；我的派生定位准确（他按我的口径执行，不是照抄）。

### F15 真跑（官方 reader，非自检台）
配方：`run_lvs_v20_pass.sh`（deckfix_v3 四开关）｜版图 `m2_mix_v31.gds` `ef034d51`｜网表 8510 取回的真件 `c7e107b5`
- **reader 不再报错**（旧件在 line 46 崩于 `'Q' element must have three or four nodes`）→ ✅ 走完到 COMPARE 段
- **Status = FAIL**｜Outcome = Comparison mode: FAIL (netlists do not match)
- **net_pair 35 = Match 12 / Mismatch 23**｜**device_pair 37，非 Match 25**

> **⇒ F14 闭合（配套网表已具备、被官方 reader 完整读取），但 mix v31 的 LVS 状态仍为「FAIL」。**
> 「具备 LVS 能力」与「LVS 通过」是两件事，不得混用（**律 F14 补记**）。

---

## 三、② 归因再修正：3 行拓扑修复零贡献（复现裁定五十四 §一-③）

| 跑件 | 网表内容 | net_pair | Match | device 非 Match |
|---|---|---|---|---|
| 我 `v1c_nodollar_v29topo`（`b80c23a2`） | v29 拓扑 | 34 | 12 | 23 |
| 我 `v1d_nodollar_v31topo`（`2600c0f9`） | v31 拓扑 | 35 | **12** | 25 |
| **他 `v1b`（`c7e107b5`）本口** | **v31 拓扑** | **35** | **12** | **25** |

**三条跑件 Match 数全部 = 12。** ⇒ 把网表从 v29 拓扑改到 v31 拓扑，**一条匹配都没多**。
裁定五十四 的修正（拓扑代差不是失配主因）**由独立第三跑再次坐实**。

---

## 四、★★★ 核心发现：ntaila 短接在官方提取口径下 **v29 ≡ v31**

### 做法
两面各跑官方 deckfix_v3 提取，**用规范化器件多重集**逐条比对（不按器件索引——索引随提取顺序漂移，按索引比会读出假差异；fde9 note260 §二亦建议此口径）。

### 结果（归一化后把并网节点记作 `MERGED`）

**v29（15 只 npn）**
| Nx | m | 数量 | 三节点 |
|---|---|---|---|
| 3 | 1 | **×3** | MERGED MERGED MERGED |
| 8 | 1 | ×1 | MERGED MERGED MERGED |
| 10 | 1 | ×1 | ntailb XBI2/nref MERGED |

**v31（14 只 npn）**
| Nx | m | 数量 | 三节点 |
|---|---|---|---|
| 1 | 1 | ×1 | MERGED MERGED MERGED |
| 10 | 1 | ×1 | MERGED MERGED MERGED |
| 3 | **2** | ×1 | MERGED MERGED MERGED |
| 10 | 1 | ×1 | ntailb XBI2/nref MERGED |

**⇒ 并网轨上的总指数：v29 = 3+3+3+8 = 17；v31 = 1+10+3×2 = 17。**
**只发生了 Nx 重新分配（3,3,3,8 → 1,10,3×m2），器件数 15→14，但并网事实一字未改。**

**电阻 R$16–R$31（16 只）逐条节点全同；电容 C$32–C$37 仅 w/l 23.66→23.61（A 559.7956p→557.4321p）。**

### 判读
> **v29 与 v31 的官方 LVS 提取网表，在 `ntaila`/`nref` 这件事上完全等价。**
> 裁定四十「ntaila 短接修复、QR_L 装为 12.0 并入 v31」——**该修复在官方提取口径下不可见**。

**这不否定裁定四十的定责（QR_L 确为诱因、几何确已改），但它把「已修复」的适用范围收窄为：**
- ✅ 几何层：QR_L 已装 12.0（`cbpath`/gen 侧可查）
- ❌ **连接层：`ntaila` 与 `XBI1/nref` 仍是同一金属域，官方提取器仍判为同一网**

**与 b7e7 自述一致、且互为佐证**：他在 `gen_M2_mix_v33.py` 纪要里写「XBI1 组版图实态：XQo/XQr 的 C=B 同落 nref 轨金属域（域 M1:6 **双标签 XBI1/nref+ntaila** 实测，非提取合并产物）」。
**他自己已经测到该域是双标签的**——也就是说**版图侧 `ntaila` 与 `XBI1/nref` 确实同域**，而 `pex_mix_v31.cdl`（`f6ba9560`）却按**分开的两个网**写 R5/Q7/Q8。
**两件工具对同一 GDS 给出互相矛盾的连通性判断，且官方提取器站版图这一边。**

---

## 五、★★ 伪警报更正：`gnd` 并网是提取开关制造的，不是版图短接

### 对照实跑（同一版图、同一网表、同一 deckfix_v3，只改 tap 开关）

| 项 | `--disable_tap_extraction` **开**（现行配方） | **关**（本口对照 `run_v2/lvs/probe_notap/`） |
|---|---|---|
| 顶层端口 | `XBI1/nref\|gnd\|ntaila ifp ifn nifbias nvtop XBI2/nref` | `XBI1/nref\|ntaila gnd ifp ifn nifbias nvtop XBI2/nref` |
| 并网节点 | `XBI1/nref\|gnd\|ntaila` | **`XBI1/nref\|ntaila`**（`gnd` 独立成网、且升为端口） |
| Q$1/Q$2 三节点 | MERGED MERGED MERGED | `XBI1/nref\|ntaila` ×2 + **`gnd`** |
| net_pair | 35 | 34 |
| **Match** | **12** | **14** |
| Mismatch | 23 | 20 |

> **`gnd` 并入该节点，是 `--disable_tap_extraction` 这条“为绕开 0.30.0 tap 器件”而设的开关的副作用。**
> 提取网表里「ntaila 被接地」的读法**不成立**——mix 尾节点没有被短到地。
> **本纪要据此撤回任何基于该节点名的「ntaila 接地」推断。**

### 但：nref ↔ ntaila 的合并**不是**开关造成的
关掉 tap 开关后，`XBI1/nref|ntaila` **仍然是一个网**。
⇒ **真实残差有两层，必须分开记**：
1. ~~`gnd` 并网~~ —— **提取设置产物**（本纪要更正）
2. **`XBI1/nref` ↔ `ntaila` 同域** —— **版图事实**，双开关下都在

---

## 六、剩余失配的构成（关 tap 开关后的净表）

- Match 14 / Mismatch 20。失配可归为三类：
  - **① `XBI1/nref,ntaila` ↔ sch `0`**（一行）：版图 nref≡ntaila 同域 vs 网表 Q7/Q8/R5 分网 —— **本轮核心残差**。
  - **② 端口集合口径差**（成片出现）：版图导出 `XBI1/nref|ntaila / gnd / ifp / ifn / nifbias / nvtop / XBI2/nref`（7）
    vs v1b `.subckt` 声明 `ifp ifn lop lon rfop rfon vcc`（7）——**两边根本不是同一组端口**，
    于是 `IFN/IFP/RFOP/RFON/NTAILA/NVTOP/NVREF` 一律 `layout=? ↔ sch=?` 成对翻车。
  - **③ 端口同名大小写差**（`layout=gnd ↔ sch=GND` 等）：reader 不做大小写归一。

**⇒ 判读：mix v31 要 PASS，需要同时解决「①nref/ntaila 真的拆开」和「②端口集合对齐」两件事；
只做其中任一件都不会让 Match 上去。** 现在这三类混在一个 20 条的失配表里，看不出主次。

---

## 七、处置与交办

**对 b7e7**（信已投）：
1. **`mix_subckt_LVS输入_v1b.sp` `c7e107b5` 验收通过** —— F14 闭合，三重缺陷的 ①② 均修掉，官方 reader 跑通到 COMPARE。与我 `v1d` 器件行逐行零差异。
2. **⚠ 需你决断的硬交办（第一硬交办）**：`XBI1/nref` 与 `ntaila` 在 v31 版图上是**同一个金属域**（你纪要自述「域 M1:6 双标签」已承认），
   官方 LVS 提取器据此判为**同一个网**；而 `pex_mix_v31.cdl` 与 v1b 网表都按**两个网**写。
   **请二择一并给出依据**：
   - 甲案（改版图，真修）：把该域**真的拆开** —— 这才是「ntaila 短接」缺陷的正解，也与裁定四十的定责一致；代价是要重出 v32 面与配套 cdl/网表。
   - 乙案（改网表，对齐现状）：承认 `nref ≡ ntaila` 同网，v1b 按同网写。**代价＝ntaila 短接缺陷在版图上长期存在、deck 副本「遗留」性质继续挂账**，我不倾向。
   - **未获令不擅改任一件。**
3. **端口集合口径差（第二交办）**：版图导出 7 端口 vs v1b 声明 7 端口**不是同一组**。请给一版
   `.subckt` 端口与**版图实际导出端口**一致的网表（可另立 v1c，不动 v1b）。此项与①独立，可并行。
4. **deck 副本「遗留」的定调我照收**，并入裁定五十三台账口径（deck 不动、冻结不换、补登记源面）。**处置不变。**
5. `gen_M3_drv1_v22.py` 源件（按 `0ea46101` 修）**仍未到**；v23 已含修法，此项**已降级为可选**（你上轮已答「不必照抄」），请确认是否**正式作废**。

**对 fde9**（信已投）：
1. 裁定五十三交办①（mix 段源面/源 cdl）**验收通过** —— 规范化差 2 条（vcc↔rfop/rfon 直连电阻），非 76；判别力边界两句随登记引用。
2. **台账新增一行待你登记**：mix v31 的 **LVS 状态＝FAIL（官方 reader 真跑，2026-10-19）**，
   配套网表 `c7e107b5` 已具备（F14 闭合）。**请勿引用任何 mix LVS 结论。**
3. `PASS → PASS_ARCHIVE`：**本轮仍不授权改台账字节**（ledger sha 已被 note261 引用）。维持你的处置。
4. 判据设计缺项下轮**跑前预注册**改法：维持未动。**Q3 两臂未获令不跑**，27 角已放跑，**M5 主基线不升 v21 面**。

---

## 八、产出件（真实执行记录）

| 件 | sha256 | 说明 |
|---|---|---|
| `verify/mix_v31_f14_closure_55/v31_extracted_TAPOFF.cir` | `bce66961197e3e20` | v31 提取网表（tap 开关开，现行配方） |
| `verify/mix_v31_f14_closure_55/v31_extracted_NOTAP.cir` | `707c157c92ead55f` | v31 提取网表（**tap 开关关**，gnd 独立） |
| `verify/mix_v31_f14_closure_55/v29_extracted_TAPOFF.cir` | `478af7c688ea84ed` | v29 提取网表（对照面） |
| `verify/mix_v31_f14_closure_55/v31_TAPOFF_lvsdb_diff_dump.txt` | `e7295e6c8bec0d5c` | 12/23 失配明细 |
| `verify/mix_v31_f14_closure_55/v31_NOTAP_lvsdb_diff_dump.txt` | `234ba18226ca3ab7` | 14/20 失配明细 |
| `run_v2/lvs/probe_notap/` | — | 关 tap 开关的对照跑（Status FAIL，Match 14） |
| `run_v2/lvs/deckfix_v1/out_drv2v20_mixv31_v1b_c7e107b5/` | — | b7e7 真件 `c7e107b5` 的官方跑 |
| `run_v2/lvs/deckfix_v1/out_drv2v20_mixv29_probe/` | — | v29 提取对照（比较段因顶层名 V29≠V31 中止，**提取段完整**，故仍可用） |

**跑法留痕**：`run_lvs_v20_pass.sh` 第四参数路径须**绝对**（相对路径会被脚本 `cd` 到 `run_v2/lvs` 下 → 误报 GDS 不存在；本口第一次即踩，已纠正重跑）。

---

## 九、纪律自证

- 真 KLayout / 官方 deckfix_v3 **实跑 4 次**（v1b×v31、v1b×v29 提取、v1b×v31 关 tap、对照基线沿用既有留痕）。
- **零仿真（ngspice 未启）、零点火、零 M5 链件变更、零组员源码改动、零新增门限、零面锚更换。**
- 三锚（drv1 v21_r1 `62c27a42` / drv2 v20 `c9363888` / mix v31 `ef034d51`）与三份 cdl **一概未动**。
- 未据「Status PASS」下结论：v29 对照跑曾报 `Status PASS`，但同页 `Outcome = completed (no explicit PASS/FAIL signature found)`、`Top Cell = n/a`、`Errors = 9`、**无 `.lvsdb`**、退出码 1 ⇒ **判为假阳性，只取其提取段**（律 F9 补记第 2 例）。
