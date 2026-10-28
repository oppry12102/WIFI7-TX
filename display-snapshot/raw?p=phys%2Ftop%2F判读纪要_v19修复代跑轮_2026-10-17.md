# 判读纪要 · v19 E 断路修复件代跑验收轮 · 2026-10-17

**记录人**：b7a0（WiFi7-TX 组长）· SOW-6 M3 代跑 · 前序：判读纪要_deck4数校准_桥元素实锤 / 判读纪要_v18补环代跑轮

## 一、件收讫（b7e7 → 8510 design/sow6/，14:33:20Z 到件铃 ×3，无说明信）

| 件 | 字节 | sha256（对铃全对 ✅） |
|---|---|---|
| gen_M3_drv1_v19.py | 58492 | bfa543523fc0f91594fe9e42ce1be4821cbf95f0ba0e6a1bde61682c7bf6d04f |
| gen_M3_drv2_v19.py | 56269 | 8d8963cb0efe2158bdf1f06ba5f89fc0fc11d603a6c0e8fd6147c806fa88906d |
| emitpath.py | 17133 | 6d70fe82f9cdc1f77128eabef3c4d7dd73045cfd12e9e01818480ef9e3f8386c |

部署：`run_v2/gen_v30/`（自 gen_v29 拷贝换件；lib13g2.py v2.3 29102B 与 resgeom.py 不动；m2_mix_v27 gen 原件保留）。

## 二、源码 diff 判读（唯一变更=修复本体）

- **emitpath.py**：`place_emit_chain` 新增 `lap=0.6` 参数 → `arm_bot = y_b + VH/2 − lap`；新增
  `assert overlap >= 0.5` 硬闸（overlap = 焊盘实顶 `y_b+VH/2−0.085` − arm_bot = **lap−0.085 = 0.515µm ≥ 0.5 验收线**）；
  返回 dict 增 lap/pad_top_real/overlap 审计字段。**与我方裁决口径逐字一致**（只延 0.09 剩 5nm 不收的裁定被采纳为 0.6 栅格）。
- **gen drv1 v18→v19**：28 行 diff，唯一几何变更 = 调用处加 `lap=0.6`；**gen drv2 v18→v19**：19 行同构。
- **mix 自证（候件①闭案）**：`gen_M2_mix_v27.py` grep `emitpath|place_emit_chain` **零命中** → mix 不走该链、
  不受 emitpath 升版影响，**v27 GDS ac3c7284 继续有效，无需 v19**（源码铁证，不必再候回话）。

## 三、代跑全链结果

| 关卡 | drv1_v19 | drv2_v19 | 判 |
|---|---|---|---|
| preflight | PASS 器件=32 标注=32 | PASS 器件=73 标注=59 | ㉑ 落柱悬空双零 ✅ |
| teeth | 16/16 全有牙（同一套） | — | ✅ |
| gen 出件 | m3_drv1_v19.gds 60458B | m3_drv2_v19.gds 76644B | ✅ |
| **gdsdiff vs v18** | 唯一 delta = 两条 M2 宽臂底边 **142.47→141.87（精确 −0.600µm）** ×2 对称 | 唯一 delta = **170.47→169.87（−0.600µm）** ×2 | 1 cells differ，器件 PCell 零变化 ✅ 与投件预告逐字吻合 |
| **LVS**（drv1×v1.sp / drv2×v3.sp） | 整体 FAIL（deck 幻影焊 bug 未修，预期内） | 同左 | 结构化指纹见 §四 |
| **DRC** | **28→25 条（−3 全为断缝 M2.b）新增 0** | **162→159（−3 同案）新增 0** | 净改善实证 ✅ |

## 四、LVS 结构化指纹对照（修复判据逐条）

| 判据 | v18 基线 | v19 实测 | 判 |
|---|---|---|---|
| **e1$1 / e2$1 消散**（drv1，真断如实提取） | 各 2 处 | **0 处** | ✅✅ **E 断路修复的 LVS 直接实证** |
| drv2 合并名五名簇 `ccas1\|ccas2\|e1\|e2\|nbcas` | 在 | **逐字原样** | ✅ deck bug 域，未修复故原样（与版图无关） |
| `nref\|XBI2/3/4` + bulk `$1` | 在 | **逐字原样** | ✅ 同上 |
| R$ 碎网 | drv1 R$5..13 / drv2 R$13..21 | 同名同位 | ✅ 同构 |
| **bb1 立照**（定律 v2：M5 骑 body 必不焊） | Q$3.B + R$12.P1 独立二件网 | **同状复验成立** | ✅ |

## 五、裁定

1. **v19 三件验收 PASS**。E 回流链断路案**物理层正式闭环**：直流断路已修复（三重实证：几何重叠 0.515µm ≥0.5 验收线 assert 硬闸 / LVS e1$1+e2$1 消散 / DRC 断缝违规 −3−3 消散新增 0）。
2. **新版本门三 sha**（fde9 启 PEX 版本门，runbook 升 v2.5 时采用）：
   - m2_mix_v27.gds = `ac3c72849cb17ffd740820ae8675da75d32f7e9680ea717ca8e8557e82e4e9f7`（不变）
   - m3_drv1_v19.gds = `e59cdc33679eb87e7a56d7cb266283c6659d2c627f582da15fd4662dab18469f`
   - m3_drv2_v19.gds = `76ae92cf6c4ee70e5d22576a37c7481fa71eda1dafa3d0d47cd2662c4f5280bf`
3. 双门锚 +17.4465 / 口令② / C 层不做 / 回执四件套全不变（承 fde9 信 §三）。
4. **残留（另案不阻 PEX）**：LVS 整体 PASS 待 deck 幻影焊修复版重跑（候件③，判据 §七判据 v2 照旧——e1$1 已移出该判据因其已消散）；mix v27 三网异常备案待 deck 修复版复判。
5. 教训收编确认：emitpath 根因注记已自带 R-VIA-01 族条款（凡按 PCell 外接尺寸推内部形状位置一律禁止）——与我方准则 v1.4 同律。

资产：run_v2/gen_v30/（部署）、run_v2/gds/m3_drv{1,2}_v19.gds、run_v2/lvs/drv{1,2}_v19_schvslyt_{v1,v3}/、run_v2/drc/m3_drv{1,2}_v19/。

—— b7a0 · 2026-10-17T14:4xZ
