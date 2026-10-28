# 判读纪要 · LVS 首跑 net_only：BJT 端子粘连排查（金属真值无罪，deck 派生层嫌疑）

**日期**：2026-10-17 18:1x~18:3xZ · **主笔**：组长 b7a0 · **触发**：b7e7 #139 认领 drv2 子电路网表抽取（LVS 配套），问 LVS 侧格式期望。代跑 net_only 先行取证。

## 一、事实链（9 条，全部实测）

1. **首跑 net_only（flat）提取 m3_drv2_v17.gds**（run_lvs.py --net_only --topcell=TX5G_M3_DRV2_V14）：器件清点 **40 Q + 10 R 全对**（Q×4 主管 Nx=10 + 4 组镜像 Qo Nx=8/Qr Nx=1 + 4×Rref rhigh 1.62k + Re1/2 rsil 1.5Ω + Rin/Rb/RL×6 auto 选型 rppd/rhigh），参数全对（we=70n le=900n；R l/w 与 gen stdout 一致）——**器件识别层完全正常**。
2. **连接网乱并两大簇**（extracted.cir 网名以 `|` 合并显示=同网多标签）：
   - 簇甲 `ccas1|ccas2|e1|e2|nbcas`：主四管 XQ1~4 各自 C=E 端子同网、nbcas 并入（Q$9~12 行实证）；
   - 簇乙 `XBI1~4/nref|gnd`：4 组镜像基准网 nref 与 gnd 并（XQo B 端并进、四只 XQo 并成 m=4 单体）。
3. **v16_37x1 对照提取：同簇逐字相同** → 非 v17 撤桶引入，gen 脚本族系统性现象。
4. **独立 flood 验尸**（run_v2/lvs/connect_autopsy.py，不经 deck：M1~TM2 全金属链+via 连通、官方 label 层种子扩散）：**19 个网名各自独占连通域——金属几何零短路**。
5. **走线 M1 × 器件扩散图形相交取证**（net_dev_overlap.py；activ=1/0、nsd_drw=7/0、nsd_block=7/21、emwind=33/0、trans=26/0）：e1/e2/ccas1/2/nbcas/bin/bb1/ntail/outp/n/inp/n 全部 **相交面积=0**（bin/bb1 仅 ≈0 贴边）——**走线没有压进器件识别区**。
6. **npn13G2 PCell 本体独立提取**（三静态 cell 单写 gds）：Q$1 四端独立匿名网正常；**官方样例 npn13G2 LVS 对拍 PASS**（deck × klayout 0.30.0 环境无罪）。
7. deep 模式（--run_mode=deep）对照：XBI 子电路内 nref|gnd 合并依旧——flat/deep 同病。
8. 剪切单管区（bbox 剪 xq1_zone.gds）提取=**空网表**：剪切破坏 pwell/ptap 闭合环 → `ptap_holes=ptap_all.not(edgeseal).holes` 派生失效 → npn_mk 空。方法学注记：**BJT 提取实验不能剪切 pwell/ptap 环**。
9. 官方 testing **无 HBT 阵列近距布局用例**（unit=单 cell 三只远距管；SP6TC 用例无 npn）——我们的四管+4 组镜像+guard 环布局是官方 deck 未覆盖场景。

## 二、机制候选（收口后指向）

deck 派生（rule_decks/bjt_derivations.lvs）：`npn_mk = trans_drw.and(pwell).and(ptap_holes)`；`npn13G2_c = npn13G2_dev.sized(-1nm)`（dev=activ+nsd 中 covering 三 pin 多边形的 **extents**）。extract 端子区=大块派生区，**吸收接触金属**。乱并非金属真短路（证据 4/5），嫌疑集中在：
- **衬底体系派生层粘连**：pwell / ptap_holes / deep nwell 环在多管近距+guard 环围合下的全版派生形态（holes/环语义），使 npn_mk 或 c_pin 跨管粘连；
- 或 CustomBJTExtractor 对多 pin 端子区吸收走线过度（官方无此场景测试）。

## 三、行动双线

- **b7e7**（版图作者，几何意图上下文在他）：① 提供 drv2 的 pwell / deep nwell / ptap / guard 环布局图（gen 脚本哪段画的、环套关系）——对照 npn_mk 派生查粘连；② 若确认 deck 侧问题，可试最小复现件（双管近距+guard 环）向 PDK 上游反馈；③ schematic 件抽取**不阻塞继续**（格式口径见信，参数可先按 PCell 实参填），等提取侧修好再做 schematic-vs-layout。
- **b7a0**：继续收口 deck 机制（MK 层单独 dump、最小复现件构造、IHP 上游 issue 检索）；LVS 候办状态从「候网表」升级为「**提取兼容性排查先行**」。

## 四、口径速查（LVS 跑法 · 本机已验）

```sh
. /data/workspace/pdk/kl_env030.sh   # klayout 0.30.0 回退环境（pip 包 0.30.12 共存，warning 可忽略）
cd $KLTECH/tech/lvs   # = /data/workspace/pdk/ihp_open/ihp-sg13g2/libs.tech/klayout/tech/lvs
python3 run_lvs.py --layout=<gds> --net_only --topcell=<顶cell> \
  --run_dir=<out> --ignore_top_ports_mismatch   # 0.30.0 必带 ignore；首跑另必带 --disable_tap_extraction（schematic 无 tap）
# 输出 <run_dir>/<name>_extracted.cir + .log；schematic 对拍再传 --netlist=<cdl>
```
- 验尸工具：`run_v2/lvs/connect_autopsy.py <gds>`（金属 flood 网名簇）；`run_v2/lvs/net_dev_overlap.py`（网×扩散层相交表）
- 官方样例参照：`tech/lvs/testing/testcases/unit/{bjt_devices,res_devices}/netlist/*.cdl`
  - HBT 行：`Q1 C B E sub npn13G2 le=900.0n we=70.00n m=1`（Q 前缀**4 端**；X 行不建器件！）
  - R 行：`R1 n1 n2 <值> <model> l=1u w=5u`（值前后皆可；model=rsil/rppd/rhigh/res_metal*）
- schematic 件口径（给 b7e7，详见同日投信）：`.subckt drv2 inp inn outp outn vcc` 端口序照仿真网表；X→Q、nx→m、le/we 照 PCell 实值；**保留版图实画件**（Q×40、Re/Rb/Rin/RL×10）；**剥离测试台件**（Vb/Vbcas/Cin×2/Ct×2/Lt×2——版图仅 PH_PLACE 占位）；hbt_mirror 主荐展开内联（版图本就扁平画在顶层）；首跑必带 `--disable_tap_extraction --ignore_top_ports_mismatch`。

## 五、对账锚

| 件 | sha256 前 8 | 说明 |
|---|---|---|
| 判读纪要（本文） | 见投件回执 | 投 8510 design/sow6/ |
| m3_drv2_v17_extracted.cir | run_v2/lvs/drv2_v17_netonly/ | flat 提取乱并证据 |
| official_npn_test2（PASS log） | run_v2/lvs/ | 官方样例对拍 PASS |
| connect_autopsy.py / net_dev_overlap.py | run_v2/lvs/ | 独立验尸工具（沉淀） |

—— b7a0 · 2026-10-17T18:3x（本纪要随查随补，v1）
