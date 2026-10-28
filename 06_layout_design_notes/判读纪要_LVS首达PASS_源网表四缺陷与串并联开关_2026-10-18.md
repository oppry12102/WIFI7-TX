# 判读纪要 · LVS 首达 PASS —— 源网表四缺陷 + 电阻串并联开关（裁定二十）

* 日期：2026-10-18（UTC 08:47–08:54Z）
* 作者：组长 b7a0
* 触发：本口无新件无新信，M5 三候件线均在等 b7e7；遂把上口挂为「低优先」的
  **LVS harness 线（engine 真 PASS）**提为当口主线。
* 结论一句话：**LVS engine 首次 PASS。** `v20 GDS × drv2 sch（整改版）× deckfix_v3`
  逐网逐器件全对上，且版图侧提取逐字节未变。

---

## 一、为什么上一口判「engine FAIL 不可用」不够

上口（裁定十八后半句）据四组源网表变体（v5 具名 gnd / v6 补 18 名全引脚 /
v7 Q→X+桩+m→Nx）实测「未匹配网数全 19、结果完全一致」，写下结论：

> 残余 FAIL 属 harness/deck 对齐层、**对源网表形态不变**；engine FAIL 位只是
> 「未完成对拍」状态位，几何/粘连类判读一律以 `*_extracted.cir` 实质比对为准。

**该结论的「对源网表形态不变」半句今日被证伪，本纪要 §五 据此订正。**
判读律的前半句（几何类以 extracted.cir 为准、FAIL 位不作停线或放行依据）**继续有效**，
但须加一条：**engine FAIL 位不得据以推断「改源网表没用」——本项目今天就栽在这。**

---

## 二、突破口：把 `.lvsdb` 读出来

`run_lvs.py` 的 stdout 与 `.log` 对失配只给一句 `ERROR : Netlists don't match`，
不带任何明细，四组变体因此只能盲试。工具链实际把逐项结果写进了 `<cell>.lvsdb`，
而该文件可被 Python 直接读：

* `db.LayoutVsSchematic().read(path)` → `.xref()` → `NetlistCrossReference`
  * `each_circuit_pair()` / `each_net_pair(cp)` / `each_device_pair(cp)`，
    每对带 `status()`（Match / MatchWithWarning / Mismatch / NoMatch / Skipped）。
* `lvs.netlist()` = 版图侧解析结果；`lvs.xref().netlist_b()` = **schematic 侧解析结果**
  （这是关键：看 reader 到底把源文件读成了什么，而不是源文件自己写了什么）。

新增两个诊断件（只读，不改任何 PDK / 交付件）：

| 工具 | 作用 |
|---|---|
| `run_v2/lvs/lvsdb_diff_dump.py` | 逐网对 / 逐器件对 dump 状态 + 状态分布统计 |
| `run_v2/lvs/lvsdb_nl_dump.py`   | 导出 LVS 两侧**实际解析到的**网表（网名/器件/参数） |

用法：`python3 lvsdb_diff_dump.py <run_dir>`、`python3 lvsdb_nl_dump.py <run_dir> A|B|both`

**首读实测（v4 基线 run_dir=deckfix_v1/out_drv2v20_v4）**：
net_pair 42 条**全部单边**、device_pair 40 条全部非 Match —— 连同名的 `bin`/`BIN`
都配不上对。schematic 侧凭空多出 6 个数字网：`0 / 1.5 / 100 / 500 / 1000 / 1620`。

---

## 三、四处源网表缺陷（D1–D4）与一处 harness 不对称（H1）

全部根因均可在 PDK 规则台账里逐行指认，非推测：

### D1 ★电阻 3T 语法：阻值 token 被当成衬底网（凭空 6 个浮网）

`tech/lvs/rule_decks/custom_reader.lvs` L88-101 官方注释写明接受的电阻形态：

```
# 3T (poly resistor)
# - Rs1 net1 net2 sub rsil m=1 l=0.5u w=0.5u R=3.1583k
# - RR1 net8 net9 3.1583k $SUB=sub! $rhigh w=0.5e-6 l=0.96e-6 b=0
# Internal rewrite target: R n1 n2 [sub] [R|0] MODEL=<name> <params>
```

`rewrite_res_from_model_position` 按**模型位**倒推端子：
`n1=f[i-3]  n2=f[i-2]  sub=f[i-1]`（i = 首个 RES_DEV/metal_res_model 字段下标）。

交付件 v4 写的是 2T 直觉形态 `R<名> n1 n2 <阻值> <model> [params]`，于是
`sub` 取到**阻值** token：

```
RRe1 e1 ntail 1.5 rsil l=1.000u w=4.665u
  → clean: RRe1 e1 ntail 1.5 0 MODEL=rsil l=1.000u w=4.665u
                ↑ 阻值 1.5 变成了第 3 端子（衬底）的网名
```

12 只电阻全中招 ⇒ 6 个浮空网（1.5/100/500/1000/1620 + 全局 0）⇒ 全网配对失败。
**修法**：model 之前插入衬底网（12/12 行整改）。

### D2 地网分裂：衬底必须用全局 `0`，不能写字面 `gnd`

首轮整改把衬底写成字面 `gnd`，结果 schematic 侧同时存在 `0`（Q 行衬底）与
`GND`（电阻衬底）两网，版图侧只有合并后的一个 `gnd` ⇒ 仍失配。
**修法**：衬底一律用 SPICE 全局 `0`（整改后 `layout=gnd ↔ sch=0` 配对成功）。

### D3 网名里的 `/` 是 SPICE 层次分隔符 ⇒ 整个镜像子块 12 只器件失配

版图标签真值网名是 `XBI1/nref … XBI4/nref`（b7e7 原始设计名）。但 SPICE 里
`/` 表示层次路径，读入器按 `XBI1` 子电路 / `nref` 节点解析，四个镜像环网
（每组 XQr + XQo + Rref，共 **12 只器件**）全部配不上。
**修法**：schematic 侧改名 `NREF1…NREF4`（拓扑一致即可，net 名本就不参与比对判据）。

### D4 npn13G2 参数是 we/le/**Nx**/m 四项全参与比对，`m=10` 写反了

`custom_bjt_extractor.lvs` L70-78：`CustomBJT4` 定义 `we/le/Nx/m` 四个参数，
且 `enable_parameter(..., true)` **全部开启**；L197-202 提取时
`set_parameter('m', 1)` 并单独 `set_parameter('Nx', nx)`。
版图侧实测：`Q$9 ccas1 bin e1 gnd npn13G2 we=70n le=900n **Nx=10 m=1**`。
v4 schematic 侧写 `m=10`（Nx 缺省 1）⇒ **Nx 与 m 双错**。
**修法**：schematic 侧改写 `Nx=<N> m=1`（主四管 Nx=10、镜像输出管 Nx=8、镜像二极管 Nx=1）。

### H1 ★电阻串/并联合并两侧不对称（最后一个拦路项）

`custom_devices.lvs` L70-71：`if SERIES_RES || PARALLEL_RES then combiner = RESDeviceCombiner`；
`custom_combiner.lvs` L188-195 串联合并把 `l` 相加。v4 修完 D1-D4 后仍 FAIL，
从 lvsdb 导出 schematic 侧网表才看清：**器件 23 只而非 24 只**，
`RB1 l=3.846`（=1.923×2），`RB2` 消失、`nbias` 网消失 —— 基极偏置两只 rppd
（`bin–nbias`、`bb1–nbias` 共用 nbias）被**串联合并成一只**，而版图侧仍提取为两只独立器件。
**修法**：跑法加 `--no_series_res --no_parallel_res`（`run_lvs.py` L832-833 提供的开关），
两侧对称后全数对上。

---

## 四、2×2 矩阵（唯一变量隔离，2026-10-18 16:53Z 一次跑完）

同一 GDS / 同一 deck，只变「源网表形态」与「串并联开关」：

| # | 源网表 | 串并联简化 | 判定 | net_pair 状态分布 | device_pair 非 Match |
|---|---|---|---|---|---|
| M1 | v4 交付件原样 | 开 | **FAIL** | Mismatch 42 | 40 / 40 |
| M2 | v4 交付件原样 | 关 | **FAIL** | Match 1, Mismatch 40 | 44 / 44 |
| M3 | 整改版 v7 | 开 | **FAIL** | Match 11, MatchWithWarning 4, Mismatch 4 | 3 / 25 |
| M4 | 整改版 v7 | 关 | **PASS** | **Match 15, MatchWithWarning 4（19/19）** | **0 / 24** |

读法：**源网表形态是主因**（0/42 → 15/19），**串并联开关是最后一道**（15/19 → 19/19）。
只改其一都到不了 PASS。M4 已连续复现三轮（v8 / v8_rerun / v9 均 PASS）。

配套整改工具（可复用、只读源件、输出新件）：
`run_v2/lvs/drv2_sch_conform.py <in.sp> <out.sp> [--sub 0] [--nref-prefix NREF]`
（改 D1/D2/D3/D4 共 32 处，逐处打印 before→after 摘要）
　　首个 PASS 配方：`run_v2/lvs/run_lvs_v20_pass.sh [tag]`

---

## 五、★裁定二十（LVS engine 首达 PASS · 并订正裁定十八后半句）

1. **标准输入对升级**为
   `m3_drv2_v20.gds × drv2_subckt_LVS输入_v7_conform.sp × deckfix_v3 × {--ignore_top_ports_mismatch, --disable_tap_extraction, --no_series_res, --no_parallel_res}`，
   run_dir=`deckfix_v1/out_drv2v20_v8`（16:53Z 起三连 PASS）。
2. **engine FAIL 位判读律修订**（保留前半、订正后半）：
   * 保留：几何/粘连类一律以 `*_extracted.cir` 实质比对为准，FAIL 位不作停线或放行依据。
   * **订正**：FAIL 位**不得**据以推断「改源网表形态没用」。本项目四组变体同结果
     曾被读成「对源网表形态不变」，实为四组变体都没触到真正的四处形态缺陷。
   * **新增铁律**：任何 FAIL 排查**先 dump `.lvsdb` 逐项明细**（`lvsdb_diff_dump.py`
     + `lvsdb_nl_dump.py`），按 net_pair / device_pair 的单边名单定位，
     **禁止盲试变体**——盲试本项目已空耗四轮。
   * **新增铁律**：「源网表对」≠「reader 解析对」。判断以 `xref().netlist_b()`
     导出结果为准（本项目栽过：v4 源文件逐行看着合理，reader 解析出 6 个浮网）。
3. **版图侧零改动自证**：本轮 PASS 的 run_dir 与 v4 基线 run_dir 的
   `m3_drv2_v20_extracted.cir` **除首行时间戳外逐字节一致**
   （v4=86b78862…，v9=87b31f75…，差异仅 `on : 18/10/2026 16:38` ↔ `16:53`）。
   ⇒ **上口粘连闭环三判据（裁定十八）继续有效**，本轮不构成对粘连案的任何改判。
4. **b7e7 交办**：交付件 `drv2_subckt_LVS输入_v4.sp`（486f6558）请按 §三 D1-D4 出
   **正式整改件 v5**（可直接用 `drv2_sch_conform.py` 或手改），我侧复核后再换
   标准输入对；在此之前标准输入对我侧以 v7-conform 为准（派生件，非交付件）。
5. **推广待办**：D1（3T 电阻语法）与 D3（网名禁 `/`）是 SG13G2 全项目通用陷阱，
   drv1 / mix 的 LVS schematic 与 `pex_extract` 产出的 cdl 都要过同一遍体检。
6. **M5 线零影响**：本轮只动 LVS 对拍面，未触碰 cdl/代入器/判据器/runbook，
   M5 候件三线与预授权顺延全部照旧。

---

## 六、证据清单（本口新增资产）

| 件 | 路径 | 说明 |
|---|---|---|
| 逐项失配 dump 器 | `run_v2/lvs/lvsdb_diff_dump.py` | 新增（只读诊断） |
| 两侧网表导出器 | `run_v2/lvs/lvsdb_nl_dump.py` | 新增（只读诊断） |
| 源网表整改器 | `run_v2/lvs/drv2_sch_conform.py` | 新增（D1–D4 自动化） |
| 首个 PASS 配方 | `run_v2/lvs/run_lvs_v20_pass.sh` | 新增（可直接复跑） |
| 整改后 sch | `run_v2/lvs/drv2_subckt_LVS输入_v7_conform.sp` | 派生件（v4 → 四缺陷整改） |
| 逐项明细 | `deckfix_v1/out_drv2v20_v4|lvsdb_diff_dump.txt` 等 | 各轮 run_dir 内 |
| PASS 轮 run_dir | `deckfix_v1/out_drv2v20_v8` / `_v8_rerun` / `_v9` | 三连 PASS |
| 2×2 矩阵 run_dir | `deckfix_v1/out_drv2v20_M1..M4` | 变量隔离证据 |

—— b7a0 · 2026-10-18T08:54Z
