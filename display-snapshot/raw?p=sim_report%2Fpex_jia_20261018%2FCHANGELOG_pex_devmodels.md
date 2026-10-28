# CHANGELOG — pex_devmodels.lib（fde9 侧 PDK 器件模型派生层）

派生层纪律：**确定性换算，不拟合、不调参、不反推**。任何改动必须留档 + 回归自测。

---

## 2026-10-18 03:00Z — cmim 周长项前置（向后兼容，零点火口径变更）

**触发**：b7a0《M5 PEX 口径裁定（组长四裁）》裁定四 + 同信补记（02:52Z）——
b7e7 侧根因已定位（`pex_extract.py` 算周长未存、`pex_to_cdl.py` 只取 area），
改法 = cdl 的 cmim 行升为 `area=<A> perim=<P> sub=0`（无 perimeter_um 保持旧格式，向后兼容）；
v1.1 预备件（sha `c62af2ed…`）候 V19 统一重提窗随窗投 8510，届时派生层读 area+perim 双参精化重跑。

**改动（2 件）**：
1. `pex_devmodels.lib` — `.subckt cmim` 增形参 `perim=0.0`，
   `Ccm = area*1.5e-15 + perim*0.04e-15`（CMIMA 1.5 fF/µm²、CMIMP 40 aF/µm，PDK spec §2.12）。
   **形参语义唯一口径**：`area` 单位 µm²、`perim` 单位 µm。
2. `m5_pex_substitute_jia.py` — cmim 改写分支：解析可选周长键
   （`perim` / `perimeter_um` / `perimeter` / `peri`），一律归一到 µm 语义后显式传参；
   带 SI 后缀者（`area=514.382u`）按 ngspice 单位语义折算回 µm，避免 1e6 量级错。

**为何现在做**：新件到货即插即用，无需再改派生层（避免「件到货当日动派生层」的自查负担）；
且**现役口径一个数都不变**（perim 缺省 0 ⇒ 纯面项 771.573 fF，裁定四原口径）。

**回归证据（`m5_pex_cmim_perim_selftest.py`，log `pex_devmodels_cmim_selftest.log`）**：
| 用例 | 派生值 | 期望 | 相对误差 | 判定 |
|---|---|---|---|---|
| 纯面项回归 area=514.382（perim 缺省） | 771.573000 fF | 771.573000 | 1.5e-16 | PASS |
| 双参 area=514.382 perim=90.72（v1.1 口径） | 775.201800 fF | 775.201800 | 2.9e-16 | PASS |
| 显式 perim=0.0 | 771.573000 fF | 771.573000 | 1.5e-16 | PASS |
| 代入器归一自检 4 写法（裸数字 / 单位后缀 / perimeter_um 别名） | — | — | — | 4/4 PASS |

- 代入器全量回归：用现役三件 cdl 重跑 `m5_pex_substitute_jia.py`，
  产出与升级前**仅差 6 行**（mix 6 件 cmim 的 X 行追加 ` perim=0`），其余逐字一致。
- 门1 `.op` 快筛回归：新旧网表**报错签名逐条相同**（`singular matrix: check node xmi.nsens` ×6、
  gmin/source stepping failed、OP 无解），**无新增错误类** ⇒ 行为零差。
- 佐证：b7e7 dry-run 记 775 fF（含周长 3.4fF）与我侧复算 775.2018 fF 自洽；
  裁定四备案口径 −0.44% / 补记实值 −0.470% 维持不改文。

**未做（纪律）**：未改任何标称值、未改裁定口径、未改点火门限、未触碰 b7e7 件。

—— fde9（WiFi7-TX-仿真验证）2026-10-18T03:00Z
