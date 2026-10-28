# cdl_nref_map_pex_mix_v27 — nref 网映射证据件（mix）

b7e7 · 2026-10-18 · 依裁定二十五 §二/§四（到件三要件之三）
对象：`pex_mix_v27.cdl`（sha ce97750b…，SRC_GDS_SHA256: 8f6da23d…）
nref 出现在器件行的行数自检：**3**（与组长侧实测 mix=3 一致）。

## 一、nref 器件行清单（cdl 行号 + 原文）

| cdl 行 | 原文 | 端子角色 |
|---|---|---|
| L27 | `Q9 ntailb nref gnd npn13G2 we=70n le=900n NX=10 M=1 sub=0` | B=nref（尾电流管基极） |
| L28 | `Q10 nref nref gnd npn13G2 we=70n le=900n NX=1 M=1 sub=0` | C=B=nref（二极管接法，E=gnd） |
| L29 | `R6 nvtop nref rhigh l=1.0u w=2.0u sub=0` | 下端=nref（rhigh 上拉电阻） |

## 二、nref 网身份与去向（凡现必查，双向可达）

- **物理身份**：偏置基准网（deck 侧 XBI 组 XQr 集电极/基极；电流镜基准电压）。
- **版图域实读**（pex_mix_v29.json nets，同批 SRC）：`XBI1/nref` root=M1[6]（49.18 µm²）；`XBI2/nref` root=M1[67]（19.77 µm²）。
- **直流去向链**：
  - nref →(Q10 C-B 二极管，E 落 gnd)→ **gnd** ✓
  - nref →(R6)→ nvtop →(R5)→ ntaila →(Q7/Q8 E)→ **gnd** ✓
- **结论**：nref 每一器件行端子均有到 gnd 的直流路径，无悬空。

## 三、备案注记（非 nref 行数、但同批机检发现，随件声明）

1. **XBI1 组双标签实态**：域 M1[6] 同时携带 `XBI1/nref` 与 `ntaila` 两枚标签（json nets 首条 names=[XBI1/nref, ntaila]）——提取面 C=B 同落 ntaila 轨的实态（上口 mix_subckt_LVS输入_v1.sp f03737b7 备案在册），非本批引入。
2. **提取面无驱动网**：nvtop / nsens / nifbias 三个网的驱动源（行为源/理想源）不在版图，deck 侧才存在——mix_subckt 备案同条，LVS 对拍按 schematic 侧补源处理。
3. **惰性普查**（裁定二十六新增①，本批机检）：C 件 n1==n2 计数 = **0**（C1–C6 六只全部正常接入，见提取自检报告）。
