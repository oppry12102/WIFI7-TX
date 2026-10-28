# cdl_nref_map_pex_drv2_v19 — nref 网映射证据件（drv2，含 R7/R8 显式声明）

b7e7 · 2026-10-18 · 依裁定二十五 §二/§四（到件三要件之三；§四点名要求在本件显式声明）
对象：`pex_drv2_v19.cdl`（注记版（注记行致正文行号较 v19 旧版整体 +1，本件行号以现役注记版为准），SRC_GDS_SHA256: c9363888…，源 m3_drv2_v20_r2.gds）
nref 出现在器件行的行数自检：**12**（与组长侧实测 drv2=12 一致）。

## 一、★ R7/R8 显式声明（裁定二十五 §四点名；裁定十六 RRin 化石回改的并域烙印）

```
L32: R7 inp gnd rhigh l=1.0u w=1.36u sub=0
L33: R8 inn gnd rhigh l=1.0u w=1.36u sub=0
```

- **这是设计意图的体现，不是提取事故**：裁定十六批准 sch 侧 RRin 下端回改接 0（`R7 inp 0` / `R8 inn 0`）——
  版图同批回改落实。v20 旧件提取曾读出 `R7 inp nref`（历史提取域并组状态），r2 重提取按现役几何
  实读为 **`inp gnd` / `inn gnd`**，与设计意图一致。
- 网名映射：inp/inn 的 R7/R8 下端版图域 = gnd 域（金属并入 gnd 干线）⇒ cdl 网名 gnd。
- 后人判读锚：sch `inp 0/inn 0`（裁定十六）↔ 版图 gnd 域 ↔ cdl `R7 inp gnd/R8 inn gnd` 三位一体。

## 二、nref 器件行清单（12 行，四组同构）

| cdl 行 | 原文 | 端子角色 |
|---|---|---|
| L22 | `Q5 ntail nref gnd … NX=8` | B=nref（第 1 路 cascode 基极） |
| L22 | `Q6 nref nref gnd … NX=1` | C=B=nref（二极管，E=gnd） |
| L22 | `R3 vcc nref rhigh …` | 下端=nref（上拉） |
| L23/L24/L25 | Q7/Q8/R4（同构） | 第 2 路 |
| L26/L27/L28 | Q9/Q10/R5（同构） | 第 3 路 |
| L29/L30/L31 | Q11/Q12/R6（同构） | 第 4 路 |

## 三、nref 网身份与去向

- **物理身份**：四路 cascode 基极偏置汇点（deck XBI1–XBI4/nref）。
- **版图域实读**（pex_drv2_v20_r2.json nets，同批 SRC）：`XBI1/nref` root=M5[1]、`XBI2/nref` root=M5[2]、
  `XBI3/nref` root=M5[11]、`XBI4/nref` root=M5[18]（各 members=16：M1×3/M2×4/M3×4/M4×4/M5×1，52.99 µm²）。
- **直流去向链**（每组同构）：
  - nref →(Q6/Q8/Q10/Q12 C-B 二极管，E 落 gnd)→ **gnd** ✓
  - nref →(R3/R4/R5/R6)→ **vcc**（上拉）✓
- **结论**：nref 每一器件行端子均有直流路径，无悬空。

## 四、随件备案

- Q=12、R=12、C=0；**惰性普查 C n1==n2 = 0**（无 C 件）。
- 件内头部已加 WATCH 注记（裁定二十五 §五）：ccas1 = RESOLVED 正向异动（R 自环已解，R1/R2 迁 e1/e2 ntail；
  ccas1 现为 Q1 集电极（L14）/Q3 基极（L16））。
