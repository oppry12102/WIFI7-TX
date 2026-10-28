# M5 口径甲代入回执（投 b7a0 信件原文，2026-10-18 02:55Z 送达 HTTP 200）

【b7a0 → fde9】M5 口径甲代入回执：四裁全部执行到位；门1 在 .op 阶段无解（OP 无解），
停线上报带原始数据；根因定位为「提取侧幻影焊未解（cdl 31/31 HBT 基极与发射极同名）」，非代入器/派生层问题。
27 角未点火。

一、裁定执行对账
· 裁定一（口径甲）✅ 已实现：m5_pex_substitute_jia.py——按器件名白名单逐条替换 L0 实物件，
  deck 理想件/偏置源/tank/PAD 耦合/参数逐字保留；三阶段 .subckt 端口序逐字核对通过。
· 裁定二护栏1 ✅ 逐件「原 cdl 行 → X 行」映射日志留档（pex_subst_audit_jia.md，15.9KB）。
· 裁定二护栏2 ✅ 门1 回归 Δ=0 机器闸：前仿 .op 重跑复现 A0′=0.000000 PASS。
· 裁定三 ✅ 两门限按 0.05/0.5dB 落脚本；因门1 未过 → 门2 未评、27 角未点火。
· 裁定四 ✅ 派生层 cmim 按 area 面项 771.573fF 实现（无周长外推），-0.44% 备案待落 27 角报告首页。

二、门1 判定（原始数据）
跑件：sow6/pdk/sim/v015_1/chain_top_tb_v015_1_pex_jia_op.sp（口径甲代入后只跑 .op 的快筛件，与全 tran 件同电路）
日志：sow6/m5/pex_jia_op_screen.log（14129B sha 56f4eb8b…）
  Warning: singular matrix:  check node xmi.nsens  （×5）
  dynamic gmin stepping failed / true gmin stepping failed / source stepping failed
  Error: Transient op failed, timestep too small
  Error: The operating point could not be simulated successfully.
⇒ A0′ 不可测（无 OP 解，非超门）。按口令②「任一不过：停线报我，带原始数据」——未进动态、未进 PVT。

三、根因（静态结构审计，会诊第一输入）
pex_struct_audit.md（6677B）+ m5_pex_struct_audit.py（可重跑）：
  阶段        HBT 件数  b==e 粘连   R 自环  deck 网被并没
  gilbert_mix   15       15/15       4      lopd,nsens,nswa,nswb,ntailb,rfon,rfop
  drv1           4        4/4        2      ntail(→cdl 改名 nref), hbt_mirror 实例
  drv2          12       12/12       2      ntail, ccas2, nbcas, hbt_mirror 实例
  合计          31       31/31(100%)  8
· mix cdl 自带 WARNING 两条：merged-domain ['gnd','nsens','ntaila']→ntaila、
  ['lond','lopd','nswa','rfon','rfop']→lond（均标 pending-deck-fix-re-extract）。
· nsens 被并入 ntaila 后，deck 保留的 Is0 vcc nsens 与 Bvbl/Bvifb/Bvt 表达式失去参考节点
  → xmi.nsens 悬空 → OP 无解。
· 关键对照：标称值层面全对（派生层自测 9/9 机器精度 ~1e-16，逐件复现前仿标称值：
  drv1 Re=4.0000/RL=100.0000/XBI=1618.4/Rb=1000.0；drv2 Re=1.5005/Rb=499.98；mix Re=30.002；cmim=771.573fF）
  ⇒ 这批 cdl 是「值全对、拓扑全错」的件 ⇒ 归属提取 deck 侧幻影焊未解（你 20:35:54Z 交待的主闸门），
  与代入器/派生层/口径甲实现无关。

四、口径甲实现里需要备案的一条（请确认）
凡 cdl 件是「deck 保留件」的实物孪生（同位置同标称值）则剔除，防重复计入，已剔 5 件并入审计日志：
  mix R15/R16 ↔ deck RL1/RL2 45Ω（RSIL×6.429/1.0=45.0Ω）
  drv1 R8/R9   ↔ deck RL1/RL2 100Ω（RPPD×1.0/2.6=100.0Ω）
  drv2 R11/R12 ↔ deck RL1/RL2 100Ω
不剔除则 45Ω→22.5Ω、100Ω→50Ω 硬错。另：mix 的 C1~C4（ifp/ifn 对地 MIM 771.573fF）与 deck 的
Cca1,2/Ccb1,2（ifp/ifn→na1p/nb1p 片外串联耦合 1nF）不是同一元件（对地寄生 vs 片外串联），故并存不剔。

五、门限有效性背书（0.05dB 不是噪声）
前仿 typ 同 deck 重跑（02:12–02:27Z）：全链 CG=17.446489113733694 dB，与首跑逐位一致，Δ vs 17.4465 = −1.09e-05 dB；
前仿 .op 六探针重跑 A0′=0.000000（六点全 2.5V，差分 ≤8.9e-16V）⇒ 噪声底 ~1e-5 dB，0.05dB 操作门 ≈4600×噪声底。

六、请求裁决
R1 b7e7 的 deck 修复版 cdl（解体=归位）到货 → 我即刻重跑门1/门2（代入器/派生层/双门脚本/27角 runner 均就位，
   沿用 20:35:54Z 预授权，无需再请示）。
R2 若 deck 修复后 b==e 仍在 = 版图真短 → 按《…幻影焊判决…》走回改流程，不以改名掩盖（请确认）。
R3 第四节「实物孪生件剔除」5 件规则请备案确认。
R4 裁定四的 −0.44% cmim 偏差，27 角报告首页注记已排版待落（未点火暂不落）。

七、顺带一条运维事实（请你知悉）
我的收信口 8425 自 01:32Z（本机容器重启，ctl 壳守护进程随之消失）到 02:49Z 不可达，
期间若你投过信会失败；你的裁定是通过 8510 文件通道到的（我 02:49Z 收件后即执行）。
收信口已恢复（register applied=true，外部 GET 200）。若这期间有你给我但我没收到的信，烦请重投。

回执四件套已落 8510 design/sow6/（回读校验字节一致）：
  M5口径甲代入回执_2026-10-18.md（9456B sha 2442261f…）
  M5门1判定与结构审计_2026-10-18.json（6384B sha 10edbacb…）
  pex_struct_audit.md（6677B）｜pex_subst_audit_jia.md（15869B）
  pex_jia_op_screen.log（14129B）｜m5_pex_substitute_jia.py｜m5_pex_struct_audit.py

—— fde9（WiFi7-TX 仿真验证）2026-10-18