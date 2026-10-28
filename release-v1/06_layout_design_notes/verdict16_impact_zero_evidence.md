# 裁定十六知会 · 我侧影响面零改动举证（fde9）

- 时间：2026-10-18T06:39:33Z ｜ 触发：b7a0 2026-10-18T06:38:24Z 知会（裁定十六 · drv2 v3 网表 RRin 化石回改案）

- **结论：VERDICT_ALL_PASS = True**（影响面 = 零，本轮零改动）

- b7a0 原文：「A0→E 一键链、判据器 ca38d0f3、六判据**全部不动**」；「27 角点火仍以 v20 重提后双门过为唯一条件，预授权不变」


## 一、现役件逐位对账（本轮未动任何件）

| 角色 | 路径 | bytes | sha256 | 对上基线 |
|---|---|---|---|---|
| runbook head v2.12 | `sow6/m5/sow6m5_pex_runbook.md` | 41468 | `0566823f966c276c` | ✅ |
| 判据器（六判据载体） | `sow6/m5/m5_cdl_reship_check.py` | 34076 | `ca38d0f3adafc89f` | ✅ |
| A0→E 一键链 | `sow6/m5/m5_pex_pipeline.py` | 12089 | `74c3e83a3dfd09f8` | ✅ |
| §4.1-A 跳变判据 | `sow6/m5/m5_drv2_suspicious.py` | 21048 | `19b268376ae9b998` | ✅ |
| §五 回执装配器 | `sow6/m5/m5_pvt27_receipt.py` | 17687 | `dd31fcade903b043` | ✅ |

## 二、冻结归档未触碰

- `sow6/m5/archive/sow6m5_pex_runbook_b4cc3efb_prev.md` = 39920 B / `b4cc3efb01e58c9d` → ✅ 未动

## 三、§一.0.5 cdl 版本门复跑（06:39:02Z）

- 判定：**STOP** ｜ 情形一：非 TERM_LAYER 修复版（三件逐字仍＝基线）→ A0 不启动、27 角不点火、停线维持
- 三件逐字仍＝基线：pex_mix_v27.cdl`33e9e754` / pex_drv1_v19.cdl`ae4feb76` / pex_drv2_v19.cdl`1f5e0cd8` ｜ 远端新名 `pex_*.cdl` **0 件** ｜ 主闸门＝b7e7 重提三件 cdl（未到货）

## 四、两笔小账（双向销账）

1. **①`runbook_merge_v211_evidence.json`**：b7a0 称已到货（f06131123fc2513d / 4368B）→ 我方 GET 回读实测 **4368 B / `f06131123fc2513d4e157e439b47cdab01e6d3240474f512826176e2062740f2`** → 逐位一致，**销账**。
2. **②复验件 bytes 订正**：b7a0 上口信称 2667B，我 8510 回读实测 4259B / `sha 61ec7961…`；其本信主动订正「以 sha 61ec7961 为准」→ **双方以 4259B / sha 61ec7961 为准，销账**（rule 77 双向适用）。

## 五、落账：v20 判读预期基线（**未写进 runbook**，未获授权改 runbook）

**预期修复项（照此判读，不算链故障）**：

1. Rin P2 网名 nref→gnd 归位（drv2 v3 RRin 化石回改 v4：RRin1/2 回 inp 0 的 sim 侧投影）
2. Re P2 接上 ntail（R P2 悬空根因在 v20 修：stub 改 pin 真值锚定 + |公式−真值|<0.005 断言）
3. 真短 8 案断开
4. nref‖gnd 分域
5. DRC M1.b 桶 −4（两缝缝合 ×2 件，v20 DRC 对拍时核销）

**R P2 定谳受害面**：Re1/Re2 ×2 件共 4 条，显形即全部；mix 不走 emitpath 从 pin 真值画线＝天然免疫（反向印证）；Rin/Rb/RL/mix 其余全连通。

⇒ 推论（我侧判读用）：若门1/门2 因 R P2 类 FAIL 而显形的网名不在 Re1/Re2 之列 ⇒ 非预期，逐项列网名报 b7a0

**非我侧（不自行跟进）**：

- 现役 drv2 sch v3 不动（v20 前擅动＝破坏对拍基准一致性）
- DRC 归属收编（0.03µm 缝＝M1.b 桶内成员，基线在案非新增）
- 镜像 4 只定谳收编（XQ3/4＝nbcas cross 底盘同网合法）
- 裁定十二清单 v2 维持 15 项不变

## 六、本轮刻意未做

未动 runbook（head 仍 v2.12）、未动判据器/pipeline/suspicious/receipt、未跑 A0/A→E、未点火 27 角、未调参、未自行认定 cdl 版本归属、未自行跟进 sch v4 或 DRC 桶销账。
