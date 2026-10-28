# 判读纪要 · 真短定谳收编 + deckfix 落码三轮（2026-10-18 · b7a0）

**口径**：b7e7 六受害面定谳（#187）全文到件收编 + 「区→节点指派锁定」补丁稿（0049c60a）落码。
**一句话结论**：补丁稿落码三轮——v1/v2（M1 域=terminal 路线）实证语义损害**证伪废弃**；
v3（识别面收紧路线）五局**零回归零 delta**；由此坐实材料级事实：**现版 GDS 的 LVS 粘连全部
经由真通道（E 窗骑=真短8案+簇甲汇流域、基带交越/cont=簇乙），deck 识别区收紧在现版无幻影
可杀——「合并名消散」判据对 deck fix 作废，消散责任在 v20 版图回改**。

---

## 一、到件验收（8510 design/sow6/，04:51–04:52Z 九件，尺寸+sha 逐件对铃全过）

| 件 | B | sha16 |
|---|---|---|
| deck修复_区到节点指派锁定_补丁稿_2026-10-18.md | 6947 | 0049c60a7dc0d886 |
| 真短定谳_回改候补名单_2026-10-18.md | 4641 | 707c039cae672259 |
| deckfix_备料报告_2026-10-18.md | 5347 | bbc7e4541c211f7c |
| pex_cdl_audit.py | 6921 | 20b5e69a0d110ad2 |
| pex_extract.py | 26037 | 186576a0fd9aec99 |
| diag_terminal_anchor.py | 8597 | 5e702f5059ee182f |
| diag_stuck_v2.py | 9545 | d2801825d8b128fb |
| diag_true_short.py | 5321 | b77a09c0a1a72624 |
| m4_top_v1.dryrun.json | 2954 | 4833f06e0a270cea |

- 真短名单全文与 #187 信逐点一致（8 案定谳表+XQo 连带+镜像 4 只作废声明）；**裁定十二维持不变**。
- m4_top_v1.dryrun.json：strip235_top_absolute 已按组长复核口径订正（139.55,10.31)~(511.19,221.25)，
  首版 cell 原点平移系注记为错——**235/5 旧账双销**。
- 三件 py + 两件 diag 本机 py_compile 全绿。

## 二、deckfix 落码（我侧分工，pya 真库在组长侧——补丁稿 §四）

- 目录：`phys/sow6_run/run_v2/lvs/deckfix_v1/`（副本树按原相对深度重组，
  `ihp_open/versions.txt` 就位）。**PDK 原件不动**：bjt_derivations.lvs pristine=03fa1f8a2d22639d（验毕）。
- 副本现役：`…/tech/lvs/rule_decks/bjt_derivations.lvs`=**584ab4eaffb22906**；diff 存档
  `deckfix_v1/deckfix_v3.diff`（1833B/**960af29fe2988249**）。跑法=副本 run_lvs.py（net_only
  `--net_only --disable_tap_extraction`；对拍另加 `--netlist --ignore_top_ports_mismatch`）。

### 三轮始末（全部实证，无推测）

| 轮 | 落码 | 实证结果 | 判 |
|---|---|---|---|
| v1 | tC/tB=M1 域（cont 门含 dev bbox） | ct 刀件：收集极 cont 同在 dev bbox 内被误判 base cont → ccas1 大域反遭拽入（bin⊕ccas1⊕e1 全并）；drv2_v18 **15→13 器件**、bb1⊕bin 大并 | **证伪①**（cont 门错） |
| v2 | tC/tB=M1 域（cont 门收窄到 b_pin/c_pin 带） | drv2_v18 仍 **15→13**、`bb1|bin|ccas…|nbcas` 巨并、R$15/16 并 m=2 | **证伪②**（路线本身错） |
| v3 | 端子识别面保持 region 族；仅 tb：body bbox−e_pin → **b_pin 真带**；tc/te 不动 | **五局零回归零 delta**（下表） | **采纳** |

**证伪②根因（落码旁注，防止重蹈）**：custom_bjt_extractor 对同一 device_region 命中的
**每个** tb poly 逐个 define_terminal——把多个 M1 域设为 terminal 等于让器件当桥把多域绑死
（bb1/bin 两条真实基极馈线经器件节点短接、器件数掉 2）。补丁稿 §二 伪码字面路线**不可落 deck**；
其「识别面收紧+域级指派语义不变」的真意由 v3 实现。

### v3 五局验证表

| 局 | 输入 | vs 旧 deck 基线 | 判 |
|---|---|---|---|
| cb_G1only（乙簇单组） | knife/cb_G1only.gds | 合并仍在（§三 预期「仍焊」✓），仅端口排序差 | PASS |
| ct_XQ1only（甲簇单管） | knife/ct_XQ1only.gds | **逐字节同**（§三「仍焊」✓） | PASS |
| drv1_v19（bb1 立照） | m3_drv1_v19.gds | 拓扑全等：bb1/bin/cop/con/e1/e2/ntail 独立✓、XBI/nref⊕gnd 维持（真短#4 实体） | PASS |
| mix_v27（ntailb 幸免） | m2_mix_v27.gds | 拓扑全等（旧基线本轮补跑 out_mix_OLDBASE）：ntailb 独立✓、10 Q 全识别（含镜像） | PASS |
| **drv2_v18×v3（主验证场）** | 标准输入对 | **15=15 器件、提取网表逐字节同** | PASS（零 delta） |

## 三、材料级结论（本轮核心产出）

1. **粘连全真通道**：v3 把 tb 识别面从 body bbox 收到 b_pin 带，五局零 delta ⇒ 骑体拽网在
   (旧tb−新tb) 环带（收集极区/上下缘）**没有任何受害者**；现版全部合并经由仍保留的真通道——
   E 窗骑（connect(emwind∼metal1)=PDK 通道真值，真短8案+簇甲汇流域 18.6×13.6 骑窗）、
   基带交越/cont（簇乙 M1 打底 y−1.45..+1.44 与基带 −2.43..−0.83 交越）。
   ⇒ **deck 识别区收紧在现版 GDS 上无幻影可杀**；flood_full「零短路」判决需注记：其连通图
   未含器件端子桥与 emwind∼M1 边的完整语义，**粘连非 deck 造，而是真几何**（与 b7e7 真短
   定谳互证，判定链条自洽收口）。
2. **「合并名消散」闭环判据（Q12 版）作废**：deck fix 重跑不会消散合并名。新判据 =
   **v20 版图回改 GDS**（15 项清单落地）重提后：合并域归零 + bulk 对上 v3 + R$13/14 归位 +
   pex_cdl_audit 六判据过 ⇒ 粘连案闭环。中间态判读照裁定十二：真短预期项单独记账，其余硬闸。
3. **deckfix v3 采纳为重提轮现役 deck**：零回归实证 + 收紧对 v20 回改后的新版图是正确卫生
   （届时骑体几何消失，环带暴露本就不存在；万一回改有漏，环带不再兜底）。PDK 原件永不动。
4. **主管识别项剔除落码范围**：真 deck flat 模式 mix_v27 10 Q 全识别（含镜像组），「主管
   ptap_holes=0」系 b7e7 replica 推导链缺口，非真 deck 缺口——补丁稿 §二.5 二选一**两个都不选**，
   撤案；其 pex_extract TERM_LAYER 修复（第四受害面）仍是你侧 cdl 主闸门正件。

## 四、资产

- `run_v2/lvs/deckfix_v1/`：副本树 + deckfix_v3.diff（960af29f）+ orig（03fa1f8a）+
  out_cb / out_ct / out_drv1 / out_mix / out_mix_OLDBASE / out_drv2v18_v3 六局全档（lvsdb+cir+log）。
- 验证配方：`. pdk/kl_env030.sh && export KLAYOUT_PATH=$KLTECH && python3
  deckfix_v1/ihp_open/…/tech/lvs/run_lvs.py --layout=<gds> --net_only --disable_tap_extraction
  --topcell=<cell> --run_dir=<out>`（versions.txt 由副本树 parents[5] 解析，已就位）。

## 五、下一步

1. b7e7：v20 回改单（15 项）落图 → 回改 GDS 投 8510；pex_extract TERM_LAYER 版重提三件 cdl（主闸门，fde9 守候中）。
2. 我侧：回改 GDS 到货 → deckfix_v3 跑 LVS×v3（判读=合并应归零）+ 收编闭环纪要。
3. fde9：cdl 重提到货 → A0→E 一键链（重提期判读口径照裁定十二）→ 双门过 → 27 角点火。

—— b7a0 · 2026-10-18T05:3xZ
