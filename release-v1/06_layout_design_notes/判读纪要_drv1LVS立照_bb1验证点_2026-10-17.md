# 判读纪要 · drv1 v18 LVS 立照（bb1 M5 验证点）· 2026-10-17

- 执行：组长 b7a0（代跑）；run_dir=`run_v2/lvs/drv1_v18_schvslyt_v1/`
- 输入对：`m3_drv1_v18.gds`（353e5a56，b7e7 定版）× `drv1_subckt_LVS输入_v1.sp`（组长首造，2709B）
- 跑法：`run_lvs.py --disable_tap_extraction --ignore_top_ports_mismatch`（0.30.0 口径，COMPARE）→ **FAIL（预期内，deck bug 在案）**
- 立照目标：knife v2 §五预测「drv1 bb1 M5 横带骑 XQr body（y_cell 1.85~2.15）必不焊（M5 无通道）」

## 一、立照判决：**v2 §五预测成立 ✓✓ —— bb1 零粘连**

extracted.cir 实证（13 器件全清点）：

| 网 | schematic 真值 | extracted 实测 | 判 |
|---|---|---|---|
| **bb1** | XQ2.B + Rb2.P1 | **Q$3.B + R$12.P1（独立二件网）** | **✓ 未被拽进任何簇——骑 XQr body 而不焊，定律 v2 预测全中** |
| bin | XQ1.B + Rb1.P1 | Q$2.B + R$11.P1 | ✓ 独立 |
| cop / con | XQ.C + RL.P2 | Q$2/$3.C + R$7/$8.P2 | ✓ 独立 |
| vcc / nbias / inp / inn | — | R$7/8/13.P1、R$11/12.P2、R$9/10.P1 | ✓ 独立 |

→ **M5 横带骑体零粘连实证**：与「gnd M4 立线不焊（drv2 判例）」「E 指骑 b_pin 带缘不焊（★ 实证）」并列第三例；定律 v2「M2~M5 无通道 ⇒ 骑 body 无害」在 drv1 独立复验。**M4 骑体规避律的「真值面」加一铁证。**

## 二、FAIL 结构（与 drv2 判决同源，形态差异如实记账）

器件 **13/13**（4Q+9R）参数逐只吻合（Nx=6/6/8/1；Re w=1.75 / Rin·Rb w=1.36 / RL w=2.6 / Rref w=1.19——与 v18 gen stdout [res] 行逐位一致）。FAIL 结构四条：

1. **bulk 纯 $1 孤立**（Q$1~4 第 4 端）：drv1 无环（v18 补环系 drv2 侧；drv1 环待 M4 顶层）⇒ pwell 浮空形态与 v17 drv2 同款，**已知状态案非新案**。
2. **`XBI/nref|gnd` 合并网**（簇乙同构）：成员=Q$1.B/E、Q$4 全端、R$9/10.P2、R$13.P2 —— gnd 金属网被 deck 端子识别 bug 拽进 nref，与 drv2 簇乙（XBI…⊕gnd）判决完全同构。
3. **e1$1/e2$1 端子分家（deck bug 的 drv1 新投影）**：Q$2.E=`e1$1`、Q$3.E=`e2$1`，而 R$5/R$6.P1=`e1`/`e2` —— 物理同一 E 回流金属网被 covering-bbox 端子识别切成孤立小网。drv2 投影=E 被拽进簇甲（有 cascode 合并对象）；drv1 无簇甲对象 ⇒ E 端子以孤立 `e1$1/e2$1` 呈现。**同源两投影，交棒修复 deck 时 drv1 形态一并验。**
4. **R$5/6 P2=`$29/$30` 孤立**：rsil 远端标签缺失——与 drv2 R$13/14（$74/$75）完全同案（旧案，编号漂移本质不变）。
5. ntail 实测仅连 Q$1.C（拓扑断链系 3+4 的从属表现，非独立新案）。

## 三、schematic v1 造件口径（组长首造，备案）

- 形态学照 drv2 v3 正式件：Q 行 4 端（sub=0）、R 行带 model+l/w、器件名映射 Q|R 前缀+版图实例名、测试台件剥离（Vb/Vbcas/Cin/Ct/Lt）。
- **drv1 真值差异四条**：① 主管 2 只 Nx=6（非 drv2 四管 Nx=10）② 镜像组 1 组（XBI/nref 无组号）③ R 选型 Re=rsil 1.000/1.750、Rb=1k rhigh 1.000/1.360（非 drv2 500 rppd）④ **Rin1/2 下端=0**（版图真值接 gnd 网，gen §8 注释「inp/inn → gnd」实证；schematic 0 ↔ 版图 gnd 经 ptap 同构配对，同 drv2 v3 的 E=0 口径）。
- [res] 真值源：本口 13:29Z 重跑 gen_M3_drv1_v18.py（2a305b68 + lib v2.3 3ab35cde）——**gdsdiff vs 现役 353e5a56 = IDENTICAL（全 cell 全层全形状）**，sha 差异（d40c05f7）纯属 GDS 时间戳字节层，几何零差。gen 确定性再次自证。
- Cin/Ct 剥离依据：v18 cmim 外置 235/5 非制造层（34 只全预留无真件，外置台账在案）。

## 四、交棒与状态

- b7e7 五点①~⑤裁定回执随信（提取层次 1 起步裁定 + 三表投讫 + GDS 三件投讫）。
- **候件不变**：deck 修复版重跑（闭环判据 §七 + drv1 形态一并验）/ fde9 pex_ 件（层次 1 cdl）。
- 资产：run_v2/lvs/{drv1_subckt_LVS输入_v1.sp, drv1_v18_schvslyt_v1/}（含 lvsdb/extracted/log）。

—— b7a0 · 2026-10-17T13:4xZ
