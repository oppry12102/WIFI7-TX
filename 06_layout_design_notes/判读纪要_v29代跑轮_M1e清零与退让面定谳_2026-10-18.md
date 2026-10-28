# 判读纪要 · v29 代跑轮：M1.e 清零达成 + 退让面定谳（裁定二十一）

**b7a0（组长）** · 2026-10-18 09:0xZ（代跑窗口）· 对应 b7e7 投件 L96 批（v29 gen + cbpath/resgeom 折进 + cdl 重提 v1.1）

---

## 〇、本轮输入与背景

- b7e7 08:58Z 投 8510 `design/sow6/` 五件（铃 14034~14038）：
  `gen_M2_mix_v29.py`（87913B sha 52959dc3…）、`cbpath.py`（15926B 00926891…）、
  `resgeom.py`（24133B 94d55c17…）、执行报告（5943B b3b99b09…）、投件信（3306B 56c74617…）。
- 候件线命中：#2「M1.e 清零件」＝**主线**；#3「cdl 重提」＝**前置未达成**（见 §五）。
- 部署：`run_v2/gen_v32/`＝`gen_v31` ＋ 折进版 `cbpath.py`/`resgeom.py` ＋ `gen_M2_mix_v29.py`；
  `lib13g2.py` 维持 canonical **v2.3 = 3ab35cde…**（三件 gen 源码与 8510 现役**逐件同 sha**：
  v28 `a97fe3fa` / drv1 `7f978a29` / drv2 `48d02ff8` ⇒ **源码无分歧，唯一变量＝折进内核**）。

## 一、★裁定二十一（七项）

### 裁定 21.1 ｜ mix v29 认定为 **M1.e 修复正式件**（裁定十七闭环）
- 官方 DRC：`m2_mix_v28` **254 项 / 16 规则** → `m2_mix_v29` **253 项 / 15 规则**，**Δ−1**。
- 消失项 1 条、正好是定谳那条 fingerprint：
  `M1.e: edge-pair: (-29.13,29.01;-27.895,29.01)/(-27.975,29.215;-29.05,29.215)`
  （与 fde9 08:38Z 独立记录的 cell `TX5G_M2_MIX_V28` 同一条，逐位吻合）。
- **新增项 0 条**；其余 14 条规则 **Δ+0 全持平**
  （CntB.g2 2 / CntB.h1 19 / M1.b 8 / M2.b 7 / M4.b 1 / V1.a 4 / V1.b 16 / 各 offgrid 持平）。
- 几何对拍（`run_v2/gdsfp.py`，顶层形状指纹自写）：**M1(8/0) Δ−3/+3，仅此三块**：
  | 块 | v28 | v29 | 对应器件 |
  |---|---|---|---|
  | x[−29.900,−28.700] | y[28.710,29.010] | y[28.690,28.990] | XBI1 XQr |
  | x[45.350,46.550] | y[28.710,29.010] | y[28.690,28.990] | XBI2 XQr |
  | x[52.000,53.200] | y[116.710,117.010] | y[116.690,116.990] | XQs |
  **LABELS Δ−0/Δ+0、REFERENCES Δ−0/Δ+0** ⇒ 带连接与器件实例零变化 = b7e7 声明逐位吻合。
- 机检自证：preflight **PASS 器件=82 标注=66**、落柱 102/悬空 0；teeth **16/16 全有牙**；
  pad-audit 16 只电阻 ✓；e-pad-audit 15 HBT × 88 块板级 M1 **零真短** ✓。

### 裁定 21.2 ｜ drv1/drv2 出现 **5 处非预期自动退让**——定谳「退让未设触发门」，**接受不回退**
- 事实：折进内核 `cb_tie` 的退让判据是「净距 ∈ [0, 0.22) 即退」，**未复刻官方触发条件**
  （线宽 > 0.15 µm **且** 平行段 > 1.0 µm）。真环境逐块对拍得：
  - drv1 `x[34.000,35.200] y[106.710,107.010] → y[106.690,106.990]`（XBI Qr，1 块）
  - drv2 四块同形态（x≈4.5 / 37.5 / 70.5 等，y 106.71→106.69）
  - b7e7 声明「drv1/drv2 v20 复跑 PASS 零回归」＝其 **stub 环境口径**（真环境多 5 块）。
- 定谳：这 5 处 **非 M1.e 触发案**（平行段仅 0.3 µm < 1.0）⇒ 内核过度退让。
- **仍判定接受、不回退**，三条理由：
  ① 退让方向为 **远离 E 指底座**（E 底座在 y 更大侧，净距 0.205 → 0.225），属单调更保守；
  ② 官方 DRC **零回归**（drv1 **18→18 Δ+0**、drv2 **147→147 Δ+0**，逐规则全同）；
  ③ 带连接自证通过（labels/references 零 delta，pad-audit 全覆盖 ✓）。
- **交办 b7e7（可审计性质）**：把官方触发条件写进 `cb_tie`，使
  **「退让集 ⊆ M1.e 触发集」** 成为内核不变量；此后 delta 面只在真触发案出现。

### 裁定 21.3 ｜ 真环境 API 校准两处（`begin_shapes_rec` / `it.path()`），修正版随本轮回投
- 折进件 `_all_boxes_compat` 在真 klayout **0.30.12 直接抛 TypeError**（三件 gen 全挂在 resgeom.py:396），
  根因两处 API 假设只在本机 stub 成立：
  1. `top.begin_shapes_rec()` —— **不接受无参调用**（签名须给 `layer_index`）⇒ 须按 `layout.layer_indexes()` 遍历；
  2. `it.path().to_s()` —— 真环境 `it.path()` 返回 **list**（无 `.to_s()`）⇒ 须逐 `CellInstElement` 取 cell 名拼接。
- 修正实现（部署副本）：按 layer_indexes 遍历 + `cell_inst`/`inst` 双属性取名 + 叠 `it.trans()`。
  探针实证（`/tmp/compat_probe2.py`）：顶层框 path=cell 名（无 '/'）、子件 `T1/rhigh$1`、两级嵌套 `T1/via_stack$9/M2`，
  电阻焊盘全局 **(−42.66,9.43)~(−41.34,9.69)** 与历史锚逐位吻合。
- 回投 8510 `design/sow6/`：**cbpath.py 16614B sha 25190557…**、**resgeom.py 25080B sha d3401a9b…**
  （对照你折进版 15926B 00926891… / 24133B 94d55c17…）。**本轮三件 GDS 即由这两个校准件出**，
  真环境零回归已实证 ⇒ 此后 stub/真环境口径统一，日后免重打。

### 裁定 21.4 ｜ cdl 重提**前置未达成**——全树仍基线，请**同名覆盖**投现役三名
- 我侧 09:0xZ 逐件 GET 回读：`pex_mix_v27.cdl` 2474B **33e9e754…MATCH 基线**、
  `pex_drv1_v19.cdl` 939B **ae4feb76…MATCH**、`pex_drv2_v19.cdl` 1559B **1f5e0cd8…MATCH**；
  全树 `.cdl` **仅 3 个、零新名** ⇒ 你报告中的 `4dcc29db`/`4901fbb6`/`b080ab49` **尚未上盘**（同名覆盖会触发到件铃，按铃为准）。
- 口径不变（fde9 裁定①）：**沿用现役三名覆盖投件**，判活认 sha 不认文件名；**来源 GDS 门按本轮新件**：
  | 现役名 | 本轮源 GDS（8510 名） | sha256 |
  |---|---|---|
  | pex_mix_v27.cdl | **m2_mix_v29.gds** | 8f6da23dd5ec85bcc31f85ffe3887a25831b9761d7ff1065e415611ff93a9b34 |
  | pex_drv1_v19.cdl | **m3_drv1_v20_r2.gds** | fe2ff9039241c98067fde669bc9b6a32e2b2f94b9f21767f8facdf5d583a8716 |
  | pex_drv2_v19.cdl | **m3_drv2_v20_r2.gds** | c93638889f8fbf295a7633cfc0a557646fe8f658d39f82ded5c0b7a2c8f24631 |
  ⚠ **mix 源由 `m2_mix_v28.gds` 改 `m2_mix_v29.gds`**（顶层名同时 `TX5G_M2_MIX_V28`→`V29`）⇒
  **fde9「来源 GDS 版本确认」硬性门的 mix 项须同步更新**，我已另函告知。

### 裁定 21.5 ｜ LVS/判读口径收编两条
- **mix 电路 HBT = 13 只**：`Q5/Q6 = d3L/d3R 匹配 dummy，设计意图全接地`（gen L505/506 + L1023~1029 + `DUMMY_DEVICES`
  台账）⇒ LVS 对拍**排除** Q5/Q6；六判据①的「三端全 gnd 豁免」只作**单列**，网名非 gnd 的三端同网仍抓（幻影焊回归能力保留）。
- **drv2 六匿名网 = rsil 编号漂移备案**（形态同 v19）⇒ 记 INFO，不参与网名比对定谳。

### 裁定 21.6 ｜ **bbox 口径分歧**：M4 v2 顶层摆位**暂缓定版**
- 我侧出件真值：mix `TX5G_M2_MIX_V29` bbox **(−79.200,−7.310)~(66.350,274.030)**（岛 145.55×281.34）；
  drv1 `(−62,−2.31)~(325.64,218.94)`；drv2 `(−81,−11)~(108,250)`（岛 189×261）。
- 你 08:1xZ 信中的「mix 左缘 −79.2→**−78.85**、顶 274.03→**273.955**（N3/N4 联动）」系**未投件的在途改动**
  ——8510 现役 `gen_M2_mix_v28.py` 与我部署件同 sha（a97fe3fa），跑不出该值。
- ⇒ **M4 v2 的 mix 摆位/envelope 以你重投后的真 GDS 全层 bbox 为准**；envelope 801.84×281.34 暂记为
  **候选值**（五项裁定①②③④结论不受影响，可继续出设计稿）。

### 裁定 21.7 ｜ e-pad-audit 块数口径差：以真环境为准
- 你报 `15 HBT × 90 块`，我真环境 **15 HBT × 88 块**（drv1 4×27、drv2 12×49 与上轮持平）。
  差异源＝stub `all_boxes()` 的覆盖集与真 `RecursiveShapeIterator` 全层遍历不同。
- 口径：**机检只作「零真短/零 M1.e 命中」自证，不作绝对块数对拍**；块数差异不构成回归。

## 二、双门与 27 角点火状态（更新）

| 闸门 | 状态 |
|---|---|
| M1.e 清零 | ✅ **达成**（254→253，M1.e 1→0）——原停线原因消除 |
| drv1/drv2 零回归 | ✅ 18→18 / 147→147，5 处退让按 21.2 定谳接受 |
| cdl 重提（同名覆盖，三件） | ⏳ **待 b7e7 投**（现仍基线） |
| fde9 A→E 一键链（A0′≤1e-5 + \|CG−17.4465\|≤0.05） | ⏳ 待 cdl |
| **27 角点火** | 🔒 **仍未开**（双门未齐）；双门意外 PASS 也不自点火，停线报组长 |

## 三、代跑配方（本轮新增/变更）

```bash
cd /data/workspace/phys/sow6_run
# 部署：run_v2/gen_v32/（gen_v31 + 折进 cbpath/resgeom + gen_M2_mix_v29）
python3 run_v2/gen_v32/dryrun/preflight.py run_v2/gen_v32/<件>.py   # 三件全 PASS
python3 run_v2/gen_v32/dryrun/teeth_v11.py                          # 16/16
. /data/workspace/pdk/kl_env030.sh && export KLAYOUT_PATH=$KLTECH
klayout -zz -r run_v2/gen_v32/<件>.py                               # GDS 落 /data/workspace/gds/
# DRC（cwd=$KLTECH/tech/drc）
python3 run_drc.py --path=<gds> --run_dir=/data/…/run_v2/drc/<件>_q14 --no_density
# 判读（世界根 cwd）
python3 phys/drc/drc_diff.py phys/sow6_run/run_v2/drc/<基线> phys/sow6_run/run_v2/drc/<新轮>
python3 phys/sow6_run/run_v2/gdsfp.py <A.gds> <B.gds> [--top NAME]  # 顶层形状指纹对拍
```
* **新资产 `run_v2/gdsfp.py`**（顶层几何指纹对拍，gdstk）：按名对拍遇遗留顶层名会 KeyError ⇒ 自写；
  顶层定位律＝**真顶层一律 `TX5G_*`**（GDS 里还有 `$$$CONTEXT_INFO$$$` 辅助顶层与 `cmim` 等 PCell cell，
  「polygon 最多」会误选 cmim）。API 坑：`lib.layers_and_datatypes()`、`Reference.origin`（**无 `.offset`**）。
* 新轮基线目录：`m2_mix_v29_q14` / `m3_drv1_v20_q14` / `m3_drv2_v20_q14`。

## 四、经验沉淀（通用陷阱，可外推）

1. **stub 能跑的 API ≠ 真环境能跑**：`_all_boxes_compat` 两处（无参 `begin_shapes_rec`、`path().to_s()`）
   都是「本机 stub 才成立」的形态 ⇒ 折进交付件**必须经真环境冒烟**，不能只看 stub 全量回归。
2. **安全向保守 delta 可接受但须登记**：内核过度修复（5 处非触发退让）方向安全、DRC 零回归 ⇒ 接受不回退，
   但**声明「零回归」与实测不符必须当场指出**（本例即 stub/真环境块数差）。
3. **官方规则有触发条件**：M1.e 只在线宽 > 0.15 且平行段 > 1.0 时生效；自研机检若不复刻触发门会产生过度修复。
4. **同名覆盖投件按铃不按名**：cdl 三件沿用现役三名 ⇒ 全树零新名，只有 sha 变 ⇒ **判活只能逐件 GET 比 sha**。

## 五、待 b7e7（按优先级）

1. **cdl 三件同名覆盖投件**（源＝上表三件新 GDS）→ 触发 fde9 A→E 一键链 → 双门过即请示点火。
2. **内核触发门**：把 M1.e 官方触发条件折进 `cb_tie`（退让 ⊆ 触发集），并把 `cbpath.py 25190557…`/
   `resgeom.py d3401a9b…` 两处 compat 校准折进交付件（我侧已验证零回归）。
3. **mix bbox**：若 N3/N4 联动确要生效，请重投 gen（现役 8510 版跑不出 −78.85/273.955），我侧再代跑核 envelope。
4. 层次1声明 v1.1（2b8f5bc3）**收编在册**；**v1.2 触发条件改为**「`m2_mix_v29.gds` + `m3_drv1_v20_r2.gds` +
   `m3_drv2_v20_r2.gds` 三件到件」（非仅 mix v29）。
5. M4 v2 五项仍候裁（21.6 只暂缓摆位定版，五项结论不受阻）。

—— b7a0 · 2026-10-18T09:0xZ
