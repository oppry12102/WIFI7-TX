# cdl_nref_map_pex_drv1_v19 — nref 网映射证据件（drv1，含 R4/R5 显式声明）

b7e7 · 2026-10-18 · 依裁定二十五 §二/§四（到件三要件之三）＋裁定二十九 §二组长口径对照补强
对象：`pex_drv1_v19.cdl`（sha 60093747…，SRC_GDS_SHA256: fe2ff903…，源 m3_drv1_v20_r2.gds）
nref 出现在器件行的行数自检：**3**（与组长侧实测 drv1=3 一致）。

## 一、★ R4/R5 显式声明（裁定二十九 §二组长口径；裁定十六 RRin 化石回改的并域烙印）

```
L20: R4 inp gnd rhigh l=1.0u w=1.36u sub=0
L21: R5 inn gnd rhigh l=1.0u w=1.36u sub=0
```

- **这是设计意图的体现，不是提取事故**：裁定十六批准 sch 侧 RRin 下端回改接 0（`Rin1 inp 0` / `Rin2 inn 0`，
  1k）——版图同批回改落实，r2 重提取按现役几何实读为 **`inp gnd` / `inn gnd`**。
- legacy→现网对照：deck legacy `Rin1 inp nref 1k` ⇒ 现网 `R4 inp gnd rhigh`——legacy nref 下拉域已并入
  **gnd 域**（inp/inn 经 Rin1/Rin2 1k 到 gnd）；与 drv2 件 §一 R7/R8 同构同批。
- 网名映射：inp/inn 的 R4/R5 下端版图域 = gnd 域（金属并入 gnd 干线）⇒ cdl 网名 gnd。
- 后人判读锚：sch `inp 0/inn 0`（裁定十六）↔ 版图 gnd 域 ↔ cdl `R4 inp gnd/R5 inn gnd` 三位一体。

## 二、nref 器件行清单（cdl 行号 + 原文）

| cdl 行 | 原文 | 端子角色 |
|---|---|---|
| L17 | `Q3 ntail nref gnd npn13G2 we=70n le=900n NX=8 M=1 sub=0` | B=nref（cascode 管 XQo 基极） |
| L18 | `Q4 nref nref gnd npn13G2 we=70n le=900n NX=1 M=1 sub=0` | C=B=nref（二极管接法，E=gnd） |
| L19 | `R3 vcc nref rhigh l=1.19u w=1.0u sub=0` | 下端=nref（vcc 上拉） |

## 三、nref 网身份与去向

- **物理身份**：cascode 基极偏置基准网（deck XBI/nref，XQr 集电极/基极二极管 + 上拉）。
- **版图域实读**（pex_drv1_v20_r2.json nets，同批 SRC）：`XBI/nref` root=M3[3]，members=8（by_layer M1×3/M2×4/M3×1，65.99 µm²）。
- **直流去向链**：
  - nref →(Q4 C-B 二极管，E 落 gnd)→ **gnd** ✓
  - nref →(R3)→ **vcc**（上拉偏置）✓
- **结论**：nref 每一器件行端子均有直流路径（gnd 侧二极管钳位 + vcc 侧上拉），无悬空。

## 四、随件备案

- Q=4（Q1/Q2 电路管 + Q3 cascode + Q4 二极管）、R=9、C=0；**惰性普查 C n1==n2 = 0**（无 C 件）。
- drv1 版图衬底浮空问题（组长裁定二十七定谳：XQo/XQr 所在 pwell 岛无接地 tap）属**版图回改清单 v3 第①项**，与本 nref 映射件无关——nref 是金属网连通，不依赖衬底 tap。
