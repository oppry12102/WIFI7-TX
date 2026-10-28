* ============================================================================
* ---- v015.1 沿革（b7e7 2026-10-16, 指令=inbox#51 组长 14:12Z v015 判读回音+放行; ACPR 处方 v2.4 推荐档）----
*   v015 -> v015.1: 混频器两处(ACPR 处方表推荐档, 组长 v2.4 混频器单板扫描实证, b7e7 13:35Z 签字;
*   落地顺序=级间匹配已落地(v015 判读 PASS, 链级 CG +15.74dB 落 +14~16 带) -> 混频器旋钮):
*   [1] gm 对 Re 15->30Ω (gilbert_mix 共4条: Re1a/Re2a/Re1b/Re2b) [ACPR +24.7dB 主项(单板)]
*   [2] 开关对 nx 4->6    (gilbert_mix XQ3~XQ6 共4管)             [EVM -1.1dB; i_mix -4.9mA]
*   其余零变更: RL 100 不动(判读②: +15.74dB 落带, 收敛旋钮不启用); gm 对 nx=3 不动(nx=2 反例
*   未实测不叠); drv 四件套原样。严格处方组合, 不做未实测叠加。
*   预期(处方=单板口径; 链板叠加非加法, v015 实测交互项 -3.86dB 为鉴, 以代跑为准):
*   混频器单板 ACPR +24.7dB/EVM -1.1/i_mix -4.9mA/Vce_sw 1.112V(相对 v015 口径 -74mV);
*   链级 ACPR 地板可能转移至 drv 段(判读④: v015 后 drv 段已是新第一限制级)——
*   若叠加后 drv 段 ACPR 恶化, 开 drv 旋钮轮(组长配合判读)。
*   判读观察条件(已入组长判读项): Vce_sw 相对 1.112V 再降 >100mV 或输出摆幅下探逼近 0.5V
*   -> 回退 nx=5; 组长侧另核: ACPR@P_REF 复现(链出等功率点对齐口径)/EVM@P_REF>=-52/op 零扰动声明重跑。
* ============================================================================
* ---- v015 草案沿革（b7e7 2026-10-16, 指令=inbox#48 组长 SOW-3 v2.3 报告 12:34Z §4/§6-2）----
*   SOW-3 级间阻抗匹配联合优化: drv 段实测净损耗 -3.3dB(vs 规划 +14~16) 根因修复,
*   四件套纯 AC 改动(DC 零扰动, 依据见各项), 仅动 chain 内嵌 drv1/drv2 副本:
*   [1] RL 25->100 (drv1/drv2 共4条)  [M2 实测锚 +21.5dB; DC 安全=Lt 理想电感短路把
*       集电极静态点钳在 vcc(v092d 口径 noutp=2.5V), RL 只走 AC, op/tran 静态量零移动]
*   [2] Rin 50->1k  (drv1/drv2 共4条) [M1 实测锚链级 +8.1dB; 顺带消除隐藏 DC 负载:
*       50Ω 从 2.5V tank 节点直通地=50mA/条x4=200mA(v013 chain 报告总流 509.2mA 主成分,
*       1k 后 2.5mA/条); i_vcc 判据口径=mix 单板 44.68mA 不受影响]
*   [3] Cin 1p->10p (drv1/drv2 共4条) [对齐 v0.94 LO 口 Cc 10p 先例(v092e: 1p@5.5G≈29Ω
*       分压吃 5dB); drv 输入后级 1/gm=2.6~9.1Ω 更低阻, 同坑吃得更多]
*   [4] Cbc 10p 删除 (drv2 共2条)     [v0.92 拓扑遗留孤儿: nbcas=理想源已 AC 地, Cbc 挂
*       ccas->nbcas 等效 ccas 高频接地, 与共基发射极 1/gm≈2.7Ω 分流(Xc(10p)=2.9Ω,
*       ~-5.7dB); 删除后 ccas 仅剩 Cμ/Cje 本征]
*   预期(损耗预算法, 模型精度 ±3dB, 以代跑为准): 链级 CG(相干 bin 直读口径)
*   -13.19 -> +6~+9dB; drv1 级 -1.25 -> +9~12dB; drv2 级 -2.09 -> +11~13dB;
*   op 全静态量不动(i_vcc mix 口径 44.68 不变; chain 报告总流 509->~330 非判据);
*   带宽: tank 有载 Q=2.9 -> -3dB 带宽 ~1.9GHz >> 320MHz 信道, 纹波不劣化预期 ≤1dB;
*   稳定性: 增益 +20dB 后 8-12G 振荡检查项保留, tran 尾段规则性请盯;
*   判读口径: 链级 CG 一律相干 bin 直读(v2.3 §2.1 勘误采纳); 驱动档联动: 链增益 ~+20dB,
*   v2.4 动态复测如需回原链出工作点, 电压档 x0.5 -> x0.05(-26dB) 归一(ifamp 15.8m->~1.6m)。
*   增益收敛旋钮(若 +14~16 目标严格): RL 100->56 单参数下探 ~-5dB, v015.1 一处变更。
* ============================================================================
* ---- v014 定稿沿革（b7e7 2026-10-16, 指令=inbox#43 组长 v013 判读 81 角+v014 裁决 07:23Z）----
*   单参数收口: .param kptat 2.53 -> **3.98**（全板唯一定义行; Bvifb/Bvbl/Bvbh 表达式引用符号不动）。
*   定标依据（组长 81 角判读④: η=注入->ntail 传递系数逐 corner 0.55~0.82 —— rr680 改尾流工作点,
*   gm 管 TC 曲线随 corner 平移, v013 kptat=2.53 按 η=1 假设定标致 t125 残差
*   typ -9.78 / bcs -8.21 / wcs -14.95, 超 6.4 判据线）:
*   kptat=3.98 = 线性外推（S=11.70mV@t125, η 逐 corner 实测）min-max 折中,
*   预测残差 typ +1.58 / bcs +5.61 / wcs -5.58 —— 三 corner 全落 6.4 判据内（组长裁决口径）;
*   补偿斜率 = 3.98*8.6173e-5*1.3863 = +0.4755mV/K（t125 补 +46.6mV; t27 零点恒不变）。
*   代价备案（不改判据, 裁决 §二.2）: tm40 正漂 +15~18mV（观测项, 结项报告记）;
*   i_vcc t125 +0.13mA（43.1, 不触 45 线）; typ/t27 定标零移动。
*   lob 板 v014 = v013.1 零变更（无 PTAT 项, 判读③过线, sha 079a1293 沿用）。
* ---- v013 草案沿革（b7e7 2026-10-16, 指令=inbox#41 组长 v012 判读+v013 指令 06:48Z）----
*   (1) 锚回填 v012.1: 0.8260 -> **0.8359** 全套(活性源+沿革注释; CONST 不动) ——
*       δ=+9.86mV = 组长代跑 v(nsens)@typ 实测 0.8359 - 0.8260 (超嫌疑区间上限,
*       Rs·ΔI 项 ~10mV 口径闭合; |δ|>1mV 回填条款成立, v011a −28.1mV 同流程);
*   (2) rr 672 -> **680**: XBI1/XBI2 (i_vcc typ 45.43 实测超线 -0.43mA 触发拍板§二.3
*       上报条款, 组长裁决采纳 rr 672->680 预案; 预计 ~43.9mA 余量 +1.1; 尾流 44.0mA/组备案);
*   (3) [指令3-A 案 PTAT 补偿注入] Bvifb/Bvbl/Bvbh 六源(本板 3 + chain 内嵌 3; lob/drv 不动):
*       表达式尾增 `+ kptat*(kB/q)*ln4*(temper+273.15-300.15)`, kptat=2.53 标定:
*       补偿斜率 = 2.53*8.6173e-5*1.3863 = +0.3022mV/K, 对冲 t125 残差 -29.6mV/98K = -0.302mV/K
*       (组长 diag 分解 -87.7+55.6+1.4≈-29.6 闭合: 感测 Vbe TC -0.894 vs gm 管 -0.567 失配,
*       gm 管高注入 TC 平坦化 -> Is0 路线判死, PTAT 归一项结构修);
*       t27 项为零 -> typ 定标/45 线/i_vcc 全不动; t125 补 +29.6mV -> 残差预期 ~0;
*       rr 672->680 密度 -1.2% 二阶交叉项 <0.2mV, kptat 不调, 留代跑复核;
*   判读流程同 v012: ①typ v(nsens)/锚自洽 ②ntail 定标 ③全角 i_vcc (rr 680 预期 typ 43.9)
*   ④t125 残差 (PTAT 后预期 |·|<1mV, 判据线 6.4mV)。
* SOW-2 TX5G · 链级联 top: LO_BUF -> Gilbert MIX -> DRV1 -> DRV2 —— chain v011a (链板·正式投件版)
* b7e7 2026-10-16 v011a 出稿（组长 2026-10-16T01:27Z 拍板信 (4): chain 设计权我侧, 链级仿真组长侧跑）:
*   同步口径 = v011a 单板参数整体换体（单一设计权, 板间判读可比性最大）:
*   (1) lo_buf 换 v011b B 三件套体 + v011a 手术: Re3/4 12->4Ω / Re1/2 40->20Ω /
*       XBIb 1.30k->680 (拍板 lob 800->680 的 -15% 同比应用) / XBIa 4.32k->3.67k (拍板原值) /
*       Vb2 1.25->1.273 / Vb1 1.25 不动 / 两基准 + Rref 顶接全挂 1:1 Vbe 联动轨;
*       [A/B 归因] B 三件套进链板 = 与单板 lob_v011a 同构; A 侧对照由组长侧 chainA/chainB
*       v0.11 链版承担 (拍板信(4) "不白跑"), 读数②结论若不上三件套, v0.12 回退是单参数组;
*   (2) gilbert_mix 换 v0.11 doublet 体 + v011a 手术: 尾流 44.6mA (nx=10 rr=672) /
*       Vifb 1.524 + 联动轨 / VbL/VbH 联动 / C 臂 Rd1/Rd2 10Ω 定稿 / ntop 联动顶接;
*   (3) drv1/drv2 结构零改动（v011a 拍板范围 = mix/lob 两臂, drv 联动不扩范围 ——
*       顶接以 0V 源绑定 vcc 保持原行为, v0.12 拍板后再联动）;
*   (4) IF 源共模 1.35 -> 1.524 (=Vifb 同源纪律, 头注④ 同法); LO 源共模 1.25 (=Vb1) 不动;
*   (5) tran 200n -> 2.5µs (判读口径 v3_fourband 24 频 + [60,560]n 稳态窗; 2MHz 包络
*       周期 500ns 窗长纪律; 与组长侧 chain 链版 2.5µs 同口径; 点数代价已在 mix 板备案);
*   感测支路 XQs/Is0 typ Vbe=0.8359V [v012 重标定] (联动轨, lo_buf/gilbert_mix subckt 内自含, Is0=400u)。
* ---- v0.94 沿革（组长 v092d/v092e 代跑回填, 五处:
*   ① DRV2 CB 集电极 c=vcc->outp/outn（v092d 修订一口径, chain 内嵌 drv2 与 drv_tb 同步——
*     v0.93 的 chain 内嵌 drv2 与 drv_tb 单板同源笔误, 本版一并修正）;
*   ② 尾流抬 Vb 第一轮: lo_buf EF Vb1 1.05->1.25 / drv1 0.95->1.20 / drv2 0.95->1.25 /
*     mix Vifb 1.2->1.35（限幅对 Vb2 1.25 不动, ntailb 0.31V 已合规; 标定曲线 notes §0.4）;
*   ③ LO 驱动: lo_buf->mix LO 口耦合 Cc1/Cc2 1p->10p（v092e 实测 LO 口 178mVpp 欠驱动压 CG,
*     1p@5.5G≈29Ω 串在限幅对 tank 与开关对低阻基极之间分压, 10p -> 2.9Ω 拿回 ~5dB）;
*   ④ 源共模随偏置: LO 源 1.05->1.25V（=Vb1）, IF 源 1.2->1.35V（=Vifb））
* v0.93（组长 v091b 口径合并: ① 源 sin offset(4 源); ② lo_buf EF 基极耦合 Cin1/Cin2 1p
*   (同 lobuf_tb v0.93); ③ four->稳态窗拟合口径; ④ drv 结构修复保持 v0.92 = 组长侧 v091b 的完全体）
* v0.92（drv 结构修复同步: DRV2 补共基管 XQ3/XQ4, DRV1 端口直改 cop/con -- 与 drv_tb v0.92 一致）
* v0.91（组长 DC 诊断修正同步版）| 验证: 全链转换增益 / 级间衔接 / 级联 OP1dB 趋势
* 链路口径（v0.93 修订）: mixer CG 实测 -9.1dB（组长 v091b tran; 原预算 +2 建立在无简并理想开关口径），
*   IF -20dBm 单音进 -> RF 预期约 -29dBm; 链预算重排（方案 B）见 design_notes §0.3: 若 IF -5dBm 进、
*   drv 链 +14~16dB -> 链出约 +0.5~+2dBm, 恰配 PA 输入 +1dBm -> 原计划级间衰减 ~10dB 预计删除（等实测定稿）
* 所有子电路与单模块 tb 完全一致 (自包含, 便于代跑)
* ============================================================================
* v011a-r2 (2026-10-16): 组长快 OP 判读修复 [判读纪要_v011a_快OP_2026-10-16.md]:
*   (1) 常数定标回填: 模型手推值 -> 感测点实测 0.7902 (Is0=100u@typ, -28.1mV, 全文件含 B 源与注释)
*   (2) 同构同步 mix/lob 内嵌副本: Bvifb 1.524->1.530 / Bvbl,Bvbh 1.509,1.539->1.515,1.545 /
*       Vb2 1.273->1.278 / IF 源共模 1.524->1.530 (同构同源纪律, 随单元板判读修正)

* ============================================================================
* v012 (2026-10-16): OP27 口径正式拍板 [口径拍板_B口径复合判据_2026-10-16.md] §二 v012 指令
*   (组长 b7a0 2026-10-16T05:5xZ 信) —— 一处一参数级变更, 草案说明
*   design/sow2_tx5g/v012_草案_b7e7.md:
*   (1) Is0 100u -> 400u [指令 1 主案]: 感测密度 x4 (0.1 -> 0.4mA/unit), 温漂修主案;
*       预期 t125 残差 -35mV -> -6.4mV 量级 (组长口径; 我方 37x 密度口径 -7~-9mV, op 终判);
*   (2) 锚常数 0.7902 -> 0.8359 全套重标定 [指令 2]: 手推 = 0.7902 + Vt(300.15K)·ln4
*       = 0.7902 + 35.85mV; B 源 CONST 不动 (锚自洽则 typ 联动项归零, 定标维持);
*       代跑 op@typ/v2500 第一步实测 v(nsens), δ = 实测 - 0.8359, 若 |δ|>1mV 按 v011a
*       (-28.1mV) 同流程全文件回填 δ 后再判 ntail 定标 (0.7902 含 -28.1mV 实测修正,
*       该修正在 400u 工作点的增量未建模: Rs·ΔI 项 +0~6mV 量级, 高注入弱);
*   (3) Vifb 系 +2mV margin [拍板复合判据 6]: 1.530 -> 1.532 (Bvbl/Bvbh/Bvifb + IF 源
*       共模同步) —— mix typ ntail 0.3504 -> ~0.3524, chain 集成漂移 -1.1mV 后仍留
*       ~+1.3mV 线余量; chain 内嵌 lo_buf/gilbert_mix 副本同构同步 (Bvbl/Bvbh/Bvifb +2mV, lob 臂 CONST 不动);
*       顶层 IF 源共模 1.530 -> 1.532 同源; drv1/drv2 零改动 (指令范围外)。
*   (4) i_vcc 义务核 [指令 3]: v011a_r2 typ 实测基线 44.64mA + 感测增量 +0.3mA
*       = 44.94mA < 45 线 (余量 +0.06mA, 紧); op 实测复核, 若全口径 >45mA 立报组长裁决
*       (备选: rr 微补 / 回退 200µA 中档), 不自行放量;
*   (5) 验收 = 按轴复合判据 (拍板 §一.2): typ 窗 0.35V 定标 / t125 残差 / wcs 复测 /
*       tm40 观测 / vdd 轴划 dcvr ±10% 不入判据。
* ============================================================================
.lib "../models/cornerHBT.lib" hbt_typ

* ---------- 公共: 参数化 HBT 电流镜 ----------
.subckt hbt_mirror nout ntop nx=8 rr=1.62k      $ v011a: 顶接=ntop(联动轨或vcc), vcc端口删除(零引用)
XQr nref nref 0 0 npn13G2 nx=1
XQo nout nref 0 0 npn13G2 nx={nx}
Rref ntop nref {{rr}}                  $ v011a: 顶接改挂联动轨 ntop (拍板(2))
.ends hbt_mirror

* ---------- LO_BUF (同 lobuf_tb.sp v0.91: EF 集电极接轨 + 10p 交流耦合 + 限幅对基极独立偏置) ----------
.subckt lo_buf inp inn outp outn vcc
* v011a: 换 v011b B 三件套体 (Re1/2 20Ω, Re3/4 4Ω) + v011a 联动/rr (见头注 (1))
Rin1 inp 0 50
Rin2 inn 0 50
Cin1 inp bin 1p
Cin2 inn bb1 1p
XQ1  vcc  bin  efp  0  npn13G2 nx=2
XQ2  vcc  bb1  efn  0  npn13G2 nx=2
Re1  efp  ntaila 20                     $ B3: 40->20Ω
Re2  efn  ntaila 20
Rb1 bin nbias1 1k
Rb2 bb1 nbias1 1k
* ---- v011a Vbe 感测支路 (自含; 联动 1:1; typ Vbe=0.7902) ----
XQs  nsens nsens 0 0 npn13G2 nx=1
Is0  vcc nsens dc 400u                   $ v012[指令1]: 100u->400u
Bv1 nbias1 0 v = {1.25 + (v(nsens)-0.8359)}      $ Vb1 typ 1.25 不动 (CONST); v012: 锚重标定
Bvt  nvtop  vcc v = {(v(nsens)-0.8359)}           $ v012: 锚重标定; nvtop = vcc + ΔVbe
XBIa ntaila nvtop hbt_mirror nx=8 rr=3.67k  $ v011a: 4.32k->3.67k (拍板)
Rb3a b3p nbias2 1k
Rb3b b3n nbias2 1k
Bv2 nbias2 0 v = {1.278 + (v(nsens)-0.8359)}     $ Vb2 typ 1.278 不动 (CONST); v012: 锚重标定
Cc1 efp b3p 10p
Cc2 efn b3n 10p
XQ3  outp  b3p  t1  0  npn13G2 nx=4
XQ4  outn  b3n  t2  0  npn13G2 nx=4
Re3  t1  ntailb 4                       $ B1: 12->4Ω
Re4  t2  ntailb 4
RL1 vcc outp 60
RL2 vcc outn 60
Lt1 vcc outp 1n
Lt2 vcc outn 1n
Ct1 outp 0 0.84p
Ct2 outn 0 0.84p
XBIb ntailb nvtop hbt_mirror nx=8 rr=680   $ B2+v011a: 1.30k->680 (B 三件套 16mA 线 + 拍板 -15%) + ntop
.ends lo_buf

* ---------- Gilbert MIX (同 mixer_tb.sp) ----------
.subckt gilbert_mix ifp ifn lop lon rfop rfon vcc
* v011a: 换 v0.11 doublet 体 + v011a 手术 (rr=672 / 联动轨 / C 臂 Rd; 与 mixer_tb_v011a 逐字一致)
* ---- gm 跨导 doublet: 对A + 对B, 各尾流 22.3mA, nx=3/管, Re15 ----
XQ1a  nswa  na1p  e1a  0  npn13G2 nx=3
XQ2a  nswb  na2n  e2a  0  npn13G2 nx=3
Re1a  e1a  ntaila 30   $ v015.1[1]: 15->30 (ACPR 处方推荐档)
Re2a  e2a  ntaila 30   $ v015.1[1]: 15->30 (ACPR 处方推荐档)
XQ1b  nswa  nb1p  e1b  0  npn13G2 nx=3
XQ2b  nswb  nb2n  e2b  0  npn13G2 nx=3
Re1b  e1b  ntailb 30   $ v015.1[1]: 15->30 (ACPR 处方推荐档)
Re2b  e2b  ntailb 30   $ v015.1[1]: 15->30 (ACPR 处方推荐档)
* ---- ΔV 基极偏置网络 + v011a 联动轨 (typ Vbe=0.7902) ----
.param vofs = 15m
.param kptat = 3.98   $ v014[裁决1]: PTAT 系数(2.53->3.98 单参数收口); 补偿斜率=kptat*(kB/q)*ln4=+0.4755mV/K; t27 零点; t125 补+46.6mV; η 逐corner 0.55~0.82 实测定标(判读纪要_v013), min-max 折中预测残差 typ +1.58/bcs +5.61/wcs -5.58 全落 6.4 判据
XQs  nsens nsens 0 0 npn13G2 nx=1
Is0  vcc nsens dc 400u                   $ v012[指令1]: 100u->400u
Bvbl nbiasL 0 v = {1.517 + (v(nsens)-0.8359) + kptat*8.617333262e-5*1.3862943611*(temper+273.15-300.15)}   $ v013: 锚回填 + PTAT (同 mix 板); v012: 1.515->1.517
Bvbh nbiasH 0 v = {1.547 + (v(nsens)-0.8359) + kptat*8.617333262e-5*1.3862943611*(temper+273.15-300.15)}   $ v013: 锚回填 + PTAT; v012: 1.545->1.547
Bvifb nifbias 0 v = {1.532 + (v(nsens)-0.8359) + kptat*8.617333262e-5*1.3862943611*(temper+273.15-300.15)}   $ v013: 锚回填 + PTAT; v012: 1.530->1.532
Bvt  nvtop  vcc v = {(v(nsens)-0.8359)}
Cca1 ifp  na1p 1n
Rba1 na1p nbiasL 2k
Cca2 ifn  na2n 1n
Rba2 na2n nbiasH 2k
Ccb1 ifp  nb1p 1n
Rbb1 nb1p nbiasH 2k
Ccb2 ifn  nb2n 1n
Rbb2 nb2n nbiasL 2k
* ---- 开关对: nx=6 (v015.1[2]: 4->6) + v011a C 臂 Rd 10Ω (定稿, 紧贴基极侧) ----
Rd1  lop  lopd 10
Rd2  lon  lond 10
XQ3  rfop  lopd nswa  0  npn13G2 nx=6   $ v015.1[2]: 4->6 (ACPR 处方推荐档; Vce_sw 观察条件见头注)
XQ4  rfon  lond nswa  0  npn13G2 nx=6   $ v015.1[2]: 4->6 (ACPR 处方推荐档; Vce_sw 观察条件见头注)
XQ5  rfon  lopd nswb  0  npn13G2 nx=6   $ v015.1[2]: 4->6 (ACPR 处方推荐档; Vce_sw 观察条件见头注)
XQ6  rfop  lond nswb  0  npn13G2 nx=6   $ v015.1[2]: 4->6 (ACPR 处方推荐档; Vce_sw 观察条件见头注)
RL1  vcc  rfop  45
RL2  vcc  rfon  45
Lt1  vcc  rfop  1n
Lt2  vcc  rfon  1n
Ct1  rfop  0  0.84p
Ct2  rfon  0  0.84p
Rb1  ifp  nifbias  2k
Rb2  ifn  nifbias  2k
XBI1 ntaila nvtop hbt_mirror nx=10 rr=680   $ v013: 672->680 (同 mix 板裁决)
XBI2 ntailb nvtop hbt_mirror nx=10 rr=680   $ v013: 672->680 (同 mix 板裁决)
.ends gilbert_mix

* ---------- DRV1 (同 drv_tb.sp v0.92: 端口直改 cop/con, tank 即端口) ----------
.subckt drv1 inp inn cop con vcc
Rin1 inp 0 1k      $ v015[2]: 50->1k (M1 实测锚; 隐藏 DC 负载 50mA->2.5mA)
Rin2 inn 0 1k      $ v015[2]
Cin1 inp bin 10p   $ v015[3]: 1p->10p (v092e LO 口同坑先例)
Cin2 inn bb1 10p   $ v015[3]
XQ1  cop  bin  e1  0  npn13G2 nx=6
XQ2  con  bb1  e2  0  npn13G2 nx=6
Re1  e1  ntail 4
Re2  e2  ntail 4
Rb1 bin nbias 1k
Rb2 bb1 nbias 1k
Vb nbias 0 1.20                         $ v0.94 尾流抬 (同 drv_tb drv1)
* v011a: drv 不扩范围, 顶接直挂 vcc (=原行为, 联动待 v0.12 拍板)
RL1 vcc cop 100    $ v015[1]: 25->100 (M2 实测锚; Lt 短路钳位 DC 不动)
RL2 vcc con 100    $ v015[1]
Lt1 vcc cop 1n
Lt2 vcc con 1n
Ct1 cop 0 0.84p
Ct2 con 0 0.84p
XBI ntail vcc hbt_mirror
.ends drv1

* ---------- DRV2 (同 drv_tb.sp) ----------
.subckt drv2 inp inn outp outn vcc
Rin1 inp 0 1k      $ v015[2]
Rin2 inn 0 1k      $ v015[2]
Cin1 inp bin 10p   $ v015[3]
Cin2 inn bb1 10p   $ v015[3]
XQ1  ccas1  bin  e1  0  npn13G2 nx=10
XQ2  ccas2  bb1  e2  0  npn13G2 nx=10
* v0.94 结构修正(组长 v092d 口径): CB 集电极 c=vcc -> outp/outn（与 drv_tb 同步;
*   DC 等价巧合说明见 drv_tb; chain 内嵌 drv2 在 v0.93 同源笔误, 本版一并修正）
XQ3  outp nbcas  ccas1  0  npn13G2 nx=10
XQ4  outn nbcas  ccas2  0  npn13G2 nx=10
Re1  e1  ntail 1.5
Re2  e2  ntail 1.5
Rb1 bin nbias 500
Rb2 bb1 nbias 500
Vb nbias 0 1.25                         $ v0.94 尾流抬 0.95->1.25V (全网最重税点 -54%, 同 drv_tb)
Vbcas nbcas 0 2.05
* v011a: drv 不扩范围, 顶接直挂 vcc (=原行为, 联动待 v0.12 拍板)
* v015[4]: Cbc1 ccas1 nbcas 10p 删除（nbcas=理想源已 AC 地, 孤儿旁路反成 ccas 分流 -5.7dB）
* v015[4]: Cbc2 ccas2 nbcas 10p 删除（nbcas=理想源已 AC 地, 孤儿旁路反成 ccas 分流 -5.7dB）
RL1 vcc outp 100   $ v015[1]
RL2 vcc outn 100   $ v015[1]
Lt1 vcc outp 0.7n
Lt2 vcc outn 0.7n
Ct1 outp 0 1.2p
Ct2 outn 0 1.2p
XBI1 ntail vcc hbt_mirror
XBI2 ntail vcc hbt_mirror
XBI3 ntail vcc hbt_mirror
XBI4 ntail vcc hbt_mirror   $ 4 组 = 32mA (目标 30, +2mA 标定余量)
.ends drv2

* ============================================================================
* top 级联
* ============================================================================
Vcc nvcc 0 2.5

* IF 差分源 (单音 10MHz, -20dBm 差分; 共模 1.530V=Vifb v011a-r2, dc 仅 op 用; 联动角同步由 mix 内轨覆盖)
.param ifamp = 15.8m
Vifp nifp_t 0 dc 1.532 sin(1.532 {ifamp} 10meg)   $ v012: 1.530->1.532 (Vifb 同源 +2mV margin)
Vifn nifn_t 0 dc 1.532 sin(1.532 {-ifamp} 10meg)

* LO 源 (VCO 口径: 0.3Vpp 差分 -> LO_BUF 限幅; 共模 1.25V=EF 基极偏置 v0.94, dc 仅 op 用)
.param loin = 106m
Vlop nlop_t 0 dc 1.25 sin(1.25 {loin} 5.5g)
Vlon nlon_t 0 dc 1.25 sin(1.25 {-loin} 5.5g)

* 级 1: LO_BUF (输出经耦合电容隔直接 mix lop/lon, 共模拉 2.35V=v0.91 开关对基极闭合点)
XLB nlop_t nlon_t nblop nblon nvcc lo_buf
Rcm1 nblop nbcm 1k
Rcm2 nblon nbcm 1k
Vbcm nbcm 0 2.35
* v0.94: 耦合 1p->10p (v092e 实测 LO 口 178mVpp 欠驱动; 1p@5.5G≈29Ω 与开关对低阻基极分压
*   吃掉 ~5dB, 10p->2.9Ω; Rcm 1k 低频角 16MHz->1.6MHz 仍远低于 IF, 无碍)
Cc1 nblop nlop 10p
Cc2 nblon nlon 10p
Rloin1 nlop nbcm 2k
Rloin2 nlon nbcm 2k

* 级 2: MIX
XMI nifp_t nifn_t nlop nlon nmixp nmixn nvcc gilbert_mix

* 级间: mix RF 输出 (对地 25Ω 虚拟负载口径改直驱) -> 隔直 -> drv1
Rtap1 nmixp ntap1 0.01
Rtap2 nmixn ntap2 0.01
Rdc1 ntap1 0 1meg     $ 高阻探针路径 (不加载), 实际耦合由 Cin1 完成
Rdc2 ntap2 0 1meg
XD1 nmixp nmixn nd1p nd1n nvcc drv1

* 级 3: DRV2 (drv1 输出 tank 内阻 25Ω/边 已是 50Ω 口, 直接接)
XD2 nd1p nd1n noutp noutn nvcc drv2
Rload1 noutp 0 25
Rload2 noutn 0 25

* ---------- 仿真 ----------
.temp 27
.op
.control
tran 1p 2.5u 60n                        $ v011a: 200n -> 2.5us (判读口径 v3_fourband 24 频 + 500ns 整窗纪律)
let vr = v(noutp) - v(noutn)
* v011a 判读口径: v3_fourband (基波4+IM3 12+IM2 8=24 频), 稳态窗 [60,560]n (500ns 整窗,
*   2MHz 包络周期); 旧七频组漏谱 70% 作废 (组长 2026-10-16 信三); ngspice-47 无 four ->
*   代跑侧稳态窗拟合; 三行 four 保留注释
* four 5.51g vr
* 全链 CG = 20log10( A5.51差分 / (2*ifamp) )
* 级间探针 (同法 four): nmixp-nmixn (mix CG), nd1p-nd1n (drv1 输出)
let vmix = v(nmixp) - v(nmixn)
* four 5.51g vmix
let vd1 = v(nd1p) - v(nd1n)
* four 5.51g vd1
* 稳定性初查: 8-12G 级间波形无振荡 (目测 tran 尾段规则性; k 因子第二轮)
.endc

* 测量口径汇总 (代跑回填):
*   [ ] 全链 CG @-20dBm IF: v0.93 预期 = -9.1(mix 实测) + drv1 + drv2（drv 链待实测; 旧预算 +15~19dB 作废）
*   [ ] 级间摆幅衔接: mix 输出 tank 摆幅 vs drv1 输入压摆需求 (无削顶)
*   [ ] LO 链: mix lop/lon 实际摆幅 >= 0.3Vpp 差分 (v0.94 Cc 10p 耦合后; v092e 1p 时 178mVpp)
*   [ ] 各级 Vce_max 击穿复核
*   [ ] 尾段波形规则 (无寄生振荡)
* 满功率推算 (v0.93 方案 B 口径, 组长 v091b 实测 mix CG=-9.1dB 回填):
*   IF -5dBm 进 -> mix 出 -14.1dBm -> drv1+drv2 (+14~16dB 待实测) -> 链出 ~+0.5~+2dBm,
*   恰配 PA 输入 +1dBm -> 原 ~10dB 级间衰减预计删除（若 drv 实测增益高于预算, 按
*   链出 +1dBm 反推衰减档, 数据说话）; 链 IM3 预估 ~-33dBc vs WLAN -45dBc 缺口见 §0.3 决策
.end
