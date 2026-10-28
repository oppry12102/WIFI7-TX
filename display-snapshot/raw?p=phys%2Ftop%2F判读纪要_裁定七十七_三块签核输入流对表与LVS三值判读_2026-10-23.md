# 判读纪要 · 裁定七十七 · 三块签核输入流对表 ＋ LVS 状态三值判读

- 日期：2026-10-23 20:33–20:36Z（b7a0，WiFi7-TX 组长）
- 上游：裁定七十六（mix v35 同名字节双流 ⇒ 签核承继以语义等价判）裁定七十六只给 **mix 一块**立了「承继三件套」（①GDS 记录级 diff 落点 ②gdsfp 几何指纹零 delta ③日志输入流 sha）。本轮把 ③ 落到**全部三块**，并回答更基础的一问：**三块的签核证据，各自跑在哪个字节流上？**
- 口径边界：**块级**。不涉全链一致性、不升 M5 主基线、不评估情形 B、不跑 Q3 两臂；链件/点火/顶层/M4 **零动作**。

## §1 三块签核输入流对表（本口全量实测）

| 块 | 签核证据（日志） | 日志记录的输入流 | 输入流现算 sha8/bytes | 现行面锚 | 面锚现算 sha8/bytes | 关系 |
|---|---|---|---|---|---|---|
| mix v35 | DRC `phys/drc/v35_q1/*.log`；LVS `phys/sow6_run/run_v2/lvs/deckfix_v1/out_drv2v20_v35_v1g/*` | `gds/m2_mix_v35.gds` | **de323eaf** / 96660 | `phys/top/m2_mix_v35.gds` | **396571f0** / 96660 | **同名字节双流（全舰唯一一例）**；差异经裁定七十六判为纯时间戳 ⇒ 承继成立 |
| drv1 v23 | DRC `verify/drv1_v23_run/drc_out/*.log`；LVS `.../deckfix_v1/out_drv2v20_v23_drv1/*` | `verify/drv1_v23_run/out/m3_drv1_v23.gds` | **d5e1296c** / 63502 | 同路径（面锚本身） | **d5e1296c** / 63502 | **字节同一流**（零继承推理） |
| drv2 v22 | DRC `phys/drc/m3_drv2_v22_b7a0/*.log`；LVS `.../deckfix_v1/out_drv2v20_drv2v22labels/*` | `gds/m3_drv2_v22.gds` | **25adcbd1** / 79564 | 同路径（面锚本身） | **25adcbd1** / 79564 | **字节同一流**（零继承推理） |

⇒ 结论：**只有 mix 一块存在「签核流 ≠ 现行锚字节」**；drv1 v23 与 drv2 v22 的签核**跑的就是现行锚本身**，无需任何继承推理。

## §2 全盘同名多流普查（282 件 .gds 全扫）

| 同名 basename | 盘内份数 | 逐份 sha8（路径） |
|---|---|---|
| `m2_mix_v35.gds` | **4** | de323eaf（`gds/`＝**签核输入流**）；396571f0（`phys/top/`＝面锚）、396571f0（`outbox_files/design/sow6/`＝发布面）、396571f0（`verify/b7e7_batch_20261023T150937Z/`） |
| `m3_drv1_v23.gds` | 2 | d5e1296c（`verify/drv1_v23_run/out/`＝面锚）、d5e1296c（`outbox_files/design/sow6/`＝发布面） |
| `m3_drv2_v22.gds` | 2 | 25adcbd1（`gds/`＝面锚）、25adcbd1（`outbox_files/design/sow6/`＝发布面） |

全盘同名多流 basename 共 **27** 个（含 v34×4、v31×3、v29×4、v28×3、v21×3、v18×3 等历史面）——**历史面一视同仁留档不删**，但逐份现算 sha 是唯一识别手段。

## §3 现役数字本口现算复核（不引用既有记载）

- **DRC 违规数**＝`*_full.lyrdb` 内 `<item>` 计数（口径同 `webui/sitebuild.py::_drc_items`）：mix v35 **219**（`phys/drc/v35_q1`）｜drv1 v23 **18**（`verify/drv1_v23_run/drc_out`）｜drv2 v22 **147**（`phys/drc/m3_drv2_v22_b7a0`）——与 BOOT.md 现役快照**逐位一致**。
- **LVS 官方 log 末行**：三面均 `INFO : Congratulations! Netlists match.`
- **配对明细**（`lvsdb_diff_dump.txt` 现解析）：

| 块 | net pairs | device pairs | NoMatch 计数 | NoMatch 双向段（仅 layout／仅 sch） |
|---|---|---|---|---|
| mix v35 | **29/29** | **36/36** | 0 | **空** |
| drv1 v23 | **13/13** | **13/13** | 0 | **空** |
| drv2 v22 | **19/19**（**含 4 条 MatchWithWarning**） | **24/24** | 0 | **空** |

drv2 v22 的 4 条告警明细：`XBI1/nref↔NREF1`、`XBI2/nref↔NREF2`、`XBI3/nref↔NREF3`、`XBI4/nref↔NREF4`（标签版 nref 对照族）。

## §4 两处新发现（落新律）

1. **★LVS 状态三值判读律**：配对状态为三值——`Match`／`MatchWithWarning`／`NoMatch`。**`MatchWithWarning` 计入匹配**（分子分母都算），只单列告警。判「PASS」须同时满足三条：①官方 log 末行 `Congratulations! Netlists match.`；②NoMatch 双向段（仅 layout／仅 sch）**为空**；③明细中 NoMatch 计数＝0。**禁止**用「非 Match」朴素取反——本轮朴素解析即把 drv2 v22 误报成「19 中 4 处失配」＝**假警报**。
2. **★证据链输入流须在盘可复现律**：`verify/preflight_d4cc_run/out_new_gen_M3_drv1_v23.py.log` 记录的输入 `/data/workspace/verify/preflight_d4cc_run/m3_drv1_v23.gds` **现不在盘**（同名仅面锚与发布面两份）。该日志属 **preflight/生成器链，不是签核 DRC/LVS 证据**，故 **v23 签核仍成立**；但登记为「历史证据输入流已不在盘」的**不可复现项**。引用任何历史证据前，先确认其输入流仍在盘并在盘现算 sha/字节。

## §5 裁定

- **mix v35**：签核跑在 de323eaf 流、现行锚 396571f0；按裁定七十六判语义等价（记录级 diff 132B 全落 BGNLIB/ENDSTR 时间戳；gdsfp 几何指纹 IDENTICAL）⇒ **DRC 219 / LVS PASS 29/29 承继至现行锚成立**。
- **drv1 v23**：签核输入流＝现行锚本身（d5e1296c/63502，字节同一）⇒ **DRC 18 / LVS PASS 13/13 直接成立**，无需继承推理。
- **drv2 v22**：签核输入流＝现行锚本身（25adcbd1/79564，字节同一）⇒ **DRC 147 / LVS PASS 19/19（4 条 MatchWithWarning，非失配）直接成立**，无需继承推理。
- 三块面锚与全部引用数字本口**现算复核**，与既有记载逐位一致（**零漂移**）。

## §6 边界与未做

- 未出全链 GDS、未做全链一致性检查、未升 M5 主基线、未评估情形 B、未跑 Q3 两臂；`corners[].PASS` 纪律未解除。
- 本轮**零修改**于版图/netlist/deck；只新增本纪要 ＋ 三处文档（BOOT.md／律库／索引）＋ 证据件。
- 证据件：`playbook/_evidence_stage86/`（gdsindex／anchor_copies／log_refs／signoff_numbers／lvs_pairs 五个 json）。

—— b7a0（WiFi7-TX 组长）
