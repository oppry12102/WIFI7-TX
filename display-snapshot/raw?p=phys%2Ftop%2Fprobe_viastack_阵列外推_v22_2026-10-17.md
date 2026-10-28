# Q1 补充实测 · via_stack 阵列外推真值（KLayout pycell 本机实跑）

组长 b7a0 · 2026-10-17T07:4xZ · SOW-6 M2/M3 · 触发：b7e7 inbox 129 行 ④之三
探针：/tmp/probe_viastack_arr2.py、probe_diag.py、probe_v22.py（kl_env030 + KLAYOUT_PATH=$KLTECH + `-zz`）
前置：probe_viastack_truth_2026-10-17.md（1x1 单颗五组合，05:4xZ）

## 结论（阵列档）
1. **薄金属堆（cut=Via1..Via4）**：cols/rows → vn_columns/vn_rows，正常生效。
   cut 0.19×0.19，**pitch=0.41µm 双向**（2x2/3x2 实测一致）；
   每层金属 = **一块合并平台矩形**（非逐 via 小 pad）＝ 阵列外沿 +0.05µm/侧。
   实测平台：2x2 → 0.70×0.61（M1 0.70×0.62）；3x2 → 1.11×0.61。
2. **TM1 跨接堆（cut=TopVia1）**：阵列档位走 **vt1_columns/vt1_rows**，与 vn_* 无关
   （官方 via_stack_code.py `nx_ny_for_via`）。**v2.1 及更早的 Board.via 把 vt1_* 硬编码 1x1**
   → t_layer=TopMetal1 时传 cols/rows 阵列**静默失效**（实测还出现同位堆叠重复形）。
   **v2.2 已修**：t_layer=TopMetal1 时 vt1 缺省继承 cols/rows（显式 vt1_cols/rows 可覆盖）。
3. TV1 阵列实测（3x2，v2.2）：cut 0.42×0.42，**pitch=0.84µm 双向**（x∈{-0.84,0,0.84}, y∈{-0.42,0.42}）；
   M5 平台 2.30×1.46（= 阵列外沿 +0.10µm/侧，1x1 的 0.62 同口径）；
   **TM1 平台非线性**：1x1 → 1.64×1.64（外扩 0.61/侧），3x2 → 2.94×2.10（外扩 0.42/侧）
   ——官方内部另有最小尺寸/规则，**按实测值取用，勿自行外推**。
4. 回归：1x1 五组合逐位复现 05:4xZ 真值（M1 0.29×0.21、M2–M5 0.29×0.20、M5↔TM1 0.62/0.42/1.64）。

## 库版本（2026-10-17T07:44Z）
- **lib13g2 v2.2** · 538 行 · 27592B · sha256 `02ecbfb95b3b4cee51a01a0cae1dde90776acff96271de533cce931fb4b8fbe4`
- canonical 投盘名：`design/sow6/lib13g2.py`（v4 单层名政策后旧多层名 `top/`、`phys/top/` 冻结不可覆盖，
  前者=v2.1 历史快照，后者=v1 遗留，**均弃用**）。
- 变更仅 Board.via 一处（vt1 透传 + 缓存键含 vt1 档位），薄金属堆与既有调用行为逐位不变；
  via_bucket 的 (M2→TopMetal1) 桶自此阵列生效。
- 本地双份同步：phys/top/lib13g2.py 与 phys/sow6_run/run_v2/gen/lib13g2.py（代跑实际解析件）同 sha。
