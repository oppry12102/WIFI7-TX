# 判读纪要：M2 mix v31 合并版一次代跑收口（裁定四十 §二.1 执行完毕）

- 纪要编号：判读纪要_M4v31代跑收口（mix 线）；日期：2026-10-18 12:5xZ；记录人：b7a0（组长）
- 触发：b7e7 三件到站（gen_M2_mix_v31.py 96302B **1281d606**／preflight 24146B **b941a41d**／HBT 档位设计依据 4477B **6b70f66a**），8510 GET 三件 sha 全 MATCH。

## 一、代跑（gen_v35 适配副本）
- 副本 `run_v2/gen_v35/gen_M2_mix_v31_local.py`：差异 2 处且头注披露——①披露行；②sys.path 注入路径适配（b7e7 侧 `__file__` 相对推导 → 本机写死 `/data/workspace/phys/top`，同 gen_v34 L444 惯例；lib13g2 v2.3 **3ab35cde** 验明在位）。resgeom/cbpath 随行自 gen_v32 现役部署（**d3401a9b/25190557**）。其余逐字节同投件。
- 运行自证全绿：`_qr_l_assert` PASS（12.0 ≥ 9.3+0.98+0.63=10.91，内缘净空 1.09µm）；pad-audit 16 电阻全覆；e-pad-audit 15 HBT 零真短；relabel 66 处。

## 二、出件与校验
- **出件 `design/sow6/m2_mix_v31.gds` 95028B sha `ef034d51202c2db8ebc8f78c74c798c55b90f984870181839d885d39985837c1`**（回投 8510，GET 回读双 MATCH）。
- bbox 与 v29 逐位同 `(-79.2,-7.31,66.35,274.03)`——cell bbox 不动 ⇒ M4 顶层 envelope 801.84×281.34 不动预告坐实（preflight 的 −78.85 口径=占位回落几何差，真件口径两版逐位同）。
- 器件 96 refs 与 v29 逐类同构（npn 15/cmim 6/rhigh 8/rsil 8/via_stack 51/ptap 8）。
- 几何 diff（gdsfp）恰两类：cmim 六只 23.66→23.610；XBI1 侧整组左移 3.3µm（QR_L 生效）。VERDICT −112/+118，零意外差异。

## 三、DRC 对拍（vs `drc/m2_mix_v29_q14` 基线 253）
- **253 → 225（Δ−28）**，规则 15→14。
- 消失 33 条全落根修区：CntB.h1 −16／V1.b −8／V1.a −4 ⇒ **ntaila 真短修复在 DRC 面兑现**。
- 新增 5 条（明示，判读归 b7e7）：CntB.h1 ×3＋CntB.g2 ×2 @ (−31.7~−28.6, y≈31)——XQr 搬家新位置邻域 CntB 再分布，同族可归因；CntB 族净 21→5。
- 其余逐位平：Offgrid 全族＋M1.b 8／M2.b 7／M4.b 1 原位。
- label −32 处（67/126 注释层 ifp/ifn/gnd/na1p/na2n/nb1p/nb2n 副本）＝mkpc_at 直传参路径不打 mim_cap 时代板注释；功能性标注 29/29＋零悬空＋pin 126/2 同心 ✓，已请 b7e7 确认归档。

## 四、裁决：cmim w=23.610 批准
- 理由：①Offgrid 5nm=官方 GridFix 硬纪律优先于字面精确值；②Δ−0.0088% 电学影响 <0.001dB ≪ 门2 判据 0.05dB；③比 23.66（+0.41%）近 47 倍。头注⑦推导＋「参数→网格」规则收回，收编归档。
- cdl/PEX 口径 w=l=23.610；C_model=839.9257fF（模型卡公式）与 c_ff 常数口径 839.896fF 微差来自 CJSW≈0.0403，pex 复核以提取实物报数。

## 五、附记
- M4 v3「仍在候」＝交叉时差：上口已收口（418+0，现役切 v3，出件 88d5d9c4），见《判读纪要_M4v3代跑收口》。
- 下一步：b7e7 pex_extract 复核 → 报 fde9 双 sha → B 批全链闭环跑（v31 PEX cdl＋typ 单角，断言器 check_v30_cdl_symmetry 收编）。
- 本轮零仿真、零点火、零 M5 链件变更；gen_v35 适配副本已披露。
