# 判读纪要 · LVS schematic-vs-layout 首跑 + 粘连机制排障（第二轮） · 2026-10-17

**记录人**：b7a0（WiFi7-TX 组长）· SOW-6 LVS 候办 · 前序：判读纪要_LVS首跑net_only_BJT端子粘连排查_2026-10-17.md（35fb5862）

## 一、件收讫（b7e7 → 设计输入）

| 件 | sha16 校验 | 判定 |
|---|---|---|
| drv2_subckt_LVS输入_v1.sp（2708B） | d221226f3fd804ec ✅ | 逐字拷贝件，锚注齐全 |
| drv2_子电路对拍报告_2026-10-17.md（2227B） | 3f434b9da1f1deb8 ✅ | 三层对拍全 PASS + 边界注记 |

信（inbox #140）三条结论核阅：vcc 网无桶残留引用 ✅；nbias/nbcas 口径问询（本口答复见 §五）；抽取件自检 fail=0 ✅。

## 二、转换器（b7e7 逐字段拷贝件 → deck 方言）

**工具**：`phys/sow6_run/run_v2/lvs/make_sch_lvs_netlist.py` → 出件 `drv2_lvs_sch_v1.sp`
（源头 sha 锚 d221226f，R 几何逐行锚定自 drv2_v17_netonly 提取件，阻值反推自检 ±3% 全过）

deck 侧实证前提（读 $KLTECH/tech/lvs 源码）：
- `CUSTOM_READER = %w[M C R Q L D]`——**X 行不建器件**，b7e7 件全 X 行 BJT 必须转 Q 行；
- `map_bjt_params` 读 WE/LE/M/**NX**（Nx 是官方参数，不是 m 的别名）；
- poly R（rsil/rppd/rhigh）须 3T 写法 `R n1 n2 sub model l= w=`（clean_res_line 重写）；
- subckt 名必须=版图 topcell（`align` 按名配对，否则 "Can't find a schematic counterpart"）。

转换五规则：X→Q 行（we=70n le=900n NX= M=）／hbt_mirror 内联展开（XBIk__nref 独立网）／剥 V·Cin·Ct·Lt（12 项，清单注记在件头）／R→3T 带模型+版图实态几何（Re=rsil 4.665u、Rb=rppd 1.923u、RL=rppd 2.6u、Rin=rhigh 1.36u、Rref=rhigh 1.19u）／sub=0。
出件自检：Q=12（4主+4Qr+4Qo）R=12（8顶+4Rref），与 b7e7 对拍报告口径一致（C/L/V 已按口径剥离）。

## 三、schematic-vs-layout 首跑（m3_drv2_v17.gds × drv2_lvs_sch_v1.sp）

```
run_lvs.py --layout=m3_drv2_v17.gds --netlist=drv2_lvs_sch_v1.sp --topcell=TX5G_M3_DRV2_V14
  --run_dir=run_v2/lvs/drv2_v17_schvslyt --ignore_top_ports_mismatch --disable_tap_extraction
→ Status FAIL（netlists do not match），2.9s
```

**失配明细**（新工具 `dump_xref.py` 读 lvsdb 交叉引用）：
- circuit **NoMatch**；schematic 侧 5 pin（INP/INN/OUTP/OUTN/VCC）配对 OK；
- **19 根 schematic 网（0/BB1/BIN/CCAS1/2/E1/2/INN/INP/NBCAS/NTAIL/OUTN/OUTP/VCC/XBI1~4__NREF）全部无版图对应**——零网锚定；
- 24 只 schematic 器件（12Q+12R）全部 L=None 无配对；
- 版图侧 19 根网（含两大粘连簇 + $67/$68 碎网）同样无对应。

**自证实验**：`--layout_netlist=drv2_lvs_sch_v1.sp --netlist=同件` 双侧同源 → **PASS**。
⇒ 转换器方言/参数映射/比较机制全链无罪；FAIL 唯一来源=版图提取侧粘连（与 net_only 轮结论自洽）。

## 四、粘连机制排障（第二轮）——两个假说被排除，一个条款降级

复现件库：`run_v2/lvs/repro_2npn.py`（生成器）+ `repro_2npn/`（4 件 GDS+提取）+ `repro_m1*.py`（探针/对照）+ `dump_pc_layers.py`（PCell 层貌）。

1. **共享 ptap 环假说 → 排除**。四件复现（间距 8µm / 100µm / 外圈 activ+psd 框架触碰 PCell 环 / 框架留 3µm 隙）net_only 全部干净：每管 4 端独立网，仅 sub 共享（真值如此）。
   机制注记：pwell 是隐式层（CHIP−nwell），ptap_holes=ptap 多边形之洞；npn_mk=trans∩pwell∩ptap_holes——ptap 环连通不导致 mk 连片（洞各自独立）。
2. **emwind↔metal1_con 无孔直连条款（bjt_connections.lvs L42）→ 降级为潜在隐患，非本案凶手**。
   推理链：条款本身真存在（33/0 窗口与 M1 无孔直连）；但 PCell 内幕（dump_pc_layers）：发射极 M1 (-0.35..0.35µm) **全覆盖窗口** (±0.035)，且窗口区下有 8 颗 VIA1——任何外来 M1 压窗必先压上自家发射极 M1（M1-M1 重叠=真短路，金属 flood 会看到），故该条款在真实版图中不可单独触发。
3. **本口首个「吸收实证」作废（教训记录）**：r2p_m1cross 探针（M2 竖线过器件中心）被吸进 E 网——复查发现探针踩中 PCell 自带 VIA1（±0.3µm），属真实经孔连接；对照组 misswin（x=+1.0 避窗）干净与 via 位置自洽。**复现实验必须先 dump PCell 内部金属/孔层再定走线**。
4. v17 层面核对：76 窗（40主+32Qo+4Qr 每单元一窗）×M1 相交面积 4.788µm²=恰 76×0.063（自家接触），未见外来 M1 大面积压窗。

**下一轮收口方向**（按嫌疑排序）：
- ① 端子区域粗大吸收：tc/tb/te 派生（npn13G2_tc=dev.not(c).interacting(c_pin) 等）与 npn_sub=npn_mk.not(npn_exclude)（**npn_exclude 不含 activ**——邻管 collector activ+cont 可能落进本管 sub 区→经 cont 直接焊进 gnd）——对 v17「nref+gnd 簇」解释力最强，待逐条款几何验证；
- ② b7e7 的 pwell/guard 环布局意图对照（其已认领）；
- ③ lvsdb 里版图侧终端区域 vs 金属的网级清算（dump_xref 扩展）。

## 五、b7e7 问询答复（nbias/nbcas deck 口径）

**口径确认 = 你的判断正确**：剥 Vb/Vbcas（转换器已剥离，清单在件头）+ `--ignore_top_ports_mismatch`。剥离后 nbias/nbcas 为纯 2-pin 连线网（Rb1/Rb2 P2 与 XQ3/XQ4 B），版图侧同名实画金属带 pin stub，对拍按连通性走。首跑 xref 中该两网与其他网一样未被锚定（粘连全局同构失败所致），粘连修复后重跑时观察这两网的 pin-stub 差异是否为最后一段口径差。

## 六、交付与在册

- 共享盘 8510 design/sow6/：本纪要 + drv2_lvs_sch_v1.sp（转换出件，sha 见投件信）
- 本地工具（workspace，可按需投盘）：make_sch_lvs_netlist.py / dump_xref.py / repro_2npn.py / repro_m1{over,probe,ctrl}.py / dump_pc_layers.py
- 运行存档：run_v2/lvs/{drv2_v17_schvslyt, sch_selftest, repro_2npn/*}

—— b7a0 · 2026-10-17 · 本纪要 sha256 见投件信
