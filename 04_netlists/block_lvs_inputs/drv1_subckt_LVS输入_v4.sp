* ----------------------------------------------------------------------------
* v3 变更（vs v2，**仅顶层名一处两行**，拓扑与形态逐字零改动）:
*   `.subckt TX5G_M3_DRV1_V22` -> `.subckt TX5G_M3_DRV1_V22`，`.ends` 同步。
*   起因：裁定二十七 §一② —— 「网表顶层名 V16 vs 版图 TX5G_M3_DRV1_V20」滞后，
*   KLayout 直接 `Can't find a schematic counterpart for the top cell`；组长当场
*   用仅改 2 行的派生件（drv1_subckt_LVS输入_v2b_topname.sp）完成真对拍，并交办
*   「请把顶层名随下一版改正」。本版随版图 v2.1（gen_M3_drv1_v21.py，pwell 接地
*   tap 轮）一并改正 ⇒ **网表顶层名与版图顶层 cell 名逐字一致**。
*   等价自证: lvs_source_audit.py pair(v2, v3) 拓扑等价断言 PASS。
* ----------------------------------------------------------------------------
* ============================================================================
* drv1 子电路 schematic（LVS schematic-vs-layout 对拍用）· v3（顶层名对齐 V21）
* ----------------------------------------------------------------------------
* 日期     : 2026-10-18 (b7e7)
* 口径来源 : b7a0《判读纪要_LVS首达PASS_源网表四缺陷与串并联开关_2026-10-18.md》
*            (sha16 8ecf7255d258a14f) §三 D1-D4 · 裁定二十第 5 条（全项目推广体检）
* 源锚     : v1（组长代造首件，bb1 M5 验证点立照专用）—— 拓扑零改动，只动形态
* 版图真值 : gen_M3_drv1_v18.py (2a305b68) DEV_NETS/NET_DECL + v18 stdout [res] 行
* ----------------------------------------------------------------------------
* v2 变更（vs v1，四处形态，与 drv2 sch v5 同口径）:
*   D1 电阻 3T 语法（9/9 行）: 删阻值 token、model 前插衬底网
*      （`R名 n1 n2 sub MODEL l=… w=…`；否则 rewrite_res_from_model_position
*       把阻值 token 当衬底网 → 凭空浮出 1000/4/100/1620 数字网）
*   D2 新插衬底一律全局 `0`（9 处；禁字面 gnd）
*   D3 网名禁 `/`（4 处引用）: XBI/nref -> NREF1（`/` 是 SPICE 层次分隔符）
*   D4 npn13G2 显式 Nx: m=6 -> Nx=6 m=1（XQ1/XQ2）、m=8 -> Nx=8 m=1（XQo）、
*      m=1 -> Nx=1 m=1（XQr）——reader 提取侧固定 m=1 另设 Nx
* 拓扑不变自证: lvs_source_audit.py pair(v1,v2) 等价断言 PASS + v2 形态全绿
* ----------------------------------------------------------------------------
* v1 备案（组长代造，2026-10-17）: drv2 v3 形态学；差异: 主管 Nx=6×2、镜像 1 组、
*   R 选型 Re=4 rsil 1.000/1.750 / Rb=1k rhigh / Rin=1k rhigh / RL=100 rppd；
*   Rin1/2 下端=0（版图 gnd 真值）；剥离 Cin/Ct/Lt/Vb/Vbcas；
*   bb1 网 = XQ2.B + Rb2.P1（bb1 M5 横带骑 XQr body 必不焊验证点）
* 组长侧跑法: --disable_tap_extraction --ignore_top_ports_mismatch
*   --no_series_res --no_parallel_res（H1: Rb1/Rb2 同端子 bin–nbias、bb1–nbias）
* ============================================================================
.subckt TX5G_M3_DRV1_V22 inp inn cop con vcc
* --- 输入网络: Rin1/2 1k rhigh（P2=gnd 真值→0）[D1: 删阻值 token 插衬底 0] ---
RRin1 inp 0 0 rhigh l=1.000u w=1.360u
RRin2 inn 0 0 rhigh l=1.000u w=1.360u
* --- 主两管 npn13G2（版图 Nx=6 m=1）[D4: m=6 -> Nx=6 m=1] ---
QXQ1 cop bin e1 0 npn13G2 le=900.0n we=70.00n Nx=6 m=1
QXQ2 con bb1 e2 0 npn13G2 le=900.0n we=70.00n Nx=6 m=1
* --- 发射极负反馈 Re1/2 4R rsil（v18 stdout 真值 w=1.750）[D1] ---
RRe1 e1 ntail 0 rsil l=1.000u w=1.750u
RRe2 e2 ntail 0 rsil l=1.000u w=1.750u
* --- 基极偏置 Rb1/2 1k rhigh（Vb 源已剥离）[D1]（H1: 同端子对，禁开串并联简化） ---
RRb1 bin nbias 0 rhigh l=1.000u w=1.360u
RRb2 bb1 nbias 0 rhigh l=1.000u w=1.360u
* --- 输出负载 RL1/2 100R rppd（版图真画件）[D1] ---
RRL1 vcc cop 0 rppd l=1.000u w=2.600u
RRL2 vcc con 0 rppd l=1.000u w=2.600u
* --- 尾流镜像 hbt_mirror 单组展开内联（Qr Nx=1 + Qo Nx=8 + Rref 1.62k rhigh;
*     nref 独立网 [D3: XBI/nref -> NREF1]） ---
QXBI_XQr NREF1 NREF1 0 0 npn13G2 le=900.0n we=70.00n Nx=1 m=1
QXBI_XQo ntail NREF1 0 0 npn13G2 le=900.0n we=70.00n Nx=8 m=1
RXBI_Rref vcc NREF1 0 rhigh l=1.190u w=1.000u
* --- 已剥离件备案（版图仅 235/5 预留/测试台专有，不在本件） ---
*   Cin1 inp bin 10p / Cin2 inn bb1 10p   （cmim 外置预留 16+16 只）
*   Ct1 cop 0 0.84p / Ct2 con 0 0.84p     （cmim 外置预留，p2 侧真接 gnd）
*   Lt1 vcc cop 0.7n / Lt2 vcc con 0.7n   （tank L 禁区占位）
*   Vb nbias 0 1.25 / Vbcas nbcas 0 2.05  （测试台理想源；drv1 无 nbcas 网）
.ends TX5G_M3_DRV1_V22
