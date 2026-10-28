* ============================================================================
* drv2 子电路网表抽取件（LVS 配套输入）· v1 · 2026-10-17
* 抽取人：b7e7（WiFi7-TX-组员）· SOW-6 · 对应组长 Q12 闭环信「LVS 配套（候你 drv2 子电路网表抽取）」
*
* 来源锚（逐字拷贝，零改动）：
*   design/chain_top_tb_v015_1.sp  sha256[:16]=3b6a305ec3566cf3
*   hbt_mirror 段 = 行 126~130；drv2 段（含段注释）= 行 240~271
* 口径：
*   - 网表本体逐字保真（含行内 $ 注释与沿革注），不改名、不删独立源（Vb/Vbcas，LVS 侧按 deck 口径忽略）；
*   - hbt_mirror 一并带上（drv2 的 XBI1~4 依赖，参数缺省 nx=8 rr=1.62k）；
*   - v015[4] Cbc 删除 / v015[1~3] RL=100 Rin=1k Cin=10p 已在源头，本件不重复表达；
*   - 版图侧对拍件 = gen_M3_drv2_v17.py（DEV_NETS/NET_DECL），对拍结论见投件信。
* ============================================================================
* ==== 原文段一：公共参数化 HBT 电流镜 ====
.subckt hbt_mirror nout ntop nx=8 rr=1.62k      $ v011a: 顶接=ntop(联动轨或vcc), vcc端口删除(零引用)
XQr nref nref 0 0 npn13G2 nx=1
XQo nout nref 0 0 npn13G2 nx={nx}
Rref ntop nref {{rr}}                  $ v011a: 顶接改挂联动轨 ntop (拍板(2))
.ends hbt_mirror

* ==== 原文段二：DRV2 ====
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
