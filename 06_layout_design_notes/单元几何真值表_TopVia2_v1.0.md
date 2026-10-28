# 单元几何真值表 · TopVia2（v1.0 · 组长 b7a0 · 2026-10-17T08:4xZ）

**来源**：lib13g2 v2.3 单测 A/B 逐层几何实测 × 官方 `sg13g2_tech_default.json` 参数双源一致；
实测件 `phys/sow6_run/run_v2/test_v23_vt2.py`（13/13 PASS），对拍 GDS `test_v23_vt2.gds`。

## TopVia2（TopMetal1→TopMetal2）官方真值

| 参数 | 值 | 出处 |
|---|---|---|
| cut 单件 TV2_a | **0.90 × 0.90 µm** | json+实测 1×1=900nm 一致 |
| cut 间距 TV2_b | **1.06 µm** | json |
| **cut pitch** | **0.90+1.06 = 1.96 µm**（双向） | json+实测 3×2 反推 1.9600 一致 |
| enc_bottom（TM1 侧）TV2_c | **0.50 µm**/侧 | json+实测 1×1 平台 1.9 一致 |
| enc_top（TM2 侧）TV2_d | **0.50 µm**/侧 | json+实测 3×2 TM2 平台 5.82 一致 |

**平台律**（n×m 阵列，两厚金属层同宽同高——实测 A/B 证实 TM1≡TM2 外沿）：

- TM1/TM2 平台 = `1.96·(n−1) + 1.90`（µm；= cut 阵列外沿 + 0.5×2）
- 1×1：cut 0.9 见方、平台 1.9×1.9；3×2：cut 4.82×2.86、平台 5.82×3.86（实测）

**与 TopVia1 对照**（v2.2 七档实测律，源码级实证今日补齐）：
TV1_a=0.42、TV1_b=0.42→pitch 0.84；enc：M5 侧 TV1_c=0.10（律 +0.62）、TM1 侧 TV1_d=0.42 endcap（律 +1.26）。

## pcell 阵列键（官方 via_stack_code.py nx_ny_for_via 三分支）

- 薄金属 via（Via1..Via4）→ `vn_columns/vn_rows`
- TopVia1 → `vt1_columns/vt1_rows`（v2.2 已接：t_layer=TopMetal1 缺省继承 cols/rows）
- **TopVia2 → `vt2_columns/vt2_rows`（v2.3 新接：t_layer=TopMetal2 缺省继承 cols/rows；其余堆恒 1×1 且不传该键）**
- 注意：M?↔TopMetal2 长堆中 TopVia1 段按 v2.2 规则缺省 1×1，需整堆同档时显式给 vt1_cols/rows。

## lib13g2 v2.3 验证链

- 单测 13/13 PASS（参数透传 9 + 几何 A/B 4；缓存键 TM2 堆追加 `_vt2{c}x{r}` 段，既有键逐位不变）
- 硬回归：drv1 v15 交付件以 v2.3 库重跑，GDS 与 v26 轮产物 **pya 全 cell 逐形状 IDENTICAL**
  （对拍器 `run_v2/gdsdiff.py`，用法 `klayout -zz -r run_v2/gdsdiff.py -rd ga=<A.gds> -rd gb=<B.gds>`）
- 分发：design/sow6/lib13g2.py（29102B sha 3ab35cdeb7a31b9e…，POST+GET 回读一致）；
  top/ 段与 phys/top/ 段同步覆盖（cp，防旧版回潮）；gen_v26/ 本地副本已同。
