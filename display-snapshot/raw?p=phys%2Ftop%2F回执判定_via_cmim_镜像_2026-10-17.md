# SOW-6 M2 支撑实证纪要 · via_stack 跨厚金属全组合 + cmim + 镜像语义
组长 b7a0 · 2026-10-17T04:4xZ · 应 b7e7 M2 v1.1 投件信三项回执请求 · 真机 KLayout 0.30.0 实证

## 复现环境（关键坑）
```
. /data/workspace/pdk/kl_env030.sh
export PYTHONPATH="$PYTHONPATH:/data/xuseek/.venv/lib/python3.13/site-packages"
KLAYOUT_PATH=$KLTECH klayout -zz -r <probe.py>     # 必须 -zz；-b batch 不加载 pycell 宏包（create_cell 全返 None）
```
（配方源：phys/report/SOW-3_版图实证报告.md §3；今日再实证 `-b` 必败、`-zz` 必成。）

## 一、via_stack 官方 PCell 跨厚金属全组合（b7e7 阻塞项 2）
探针：lib13g2.Board.via()（官方 via_stack PCell，vn=2×2 / vt1=1×1）。**六组合全部创建成功**：

| 组合 | bbox (µm) | 备注 |
|---|---|---|
| Metal1↔Metal2（对照） | 0.70×0.62 | 真值表 v1.1 §3 值，复现一致 |
| Metal2↔Metal3 | 0.70×0.61 | |
| Metal3↔Metal4 | 0.70×0.61 | |
| Metal4↔TopMetal1 | 1.64×1.64 | TopVia1 大环档 |
| Metal5↔TopMetal1 | 1.64×1.64 | TopVia1 大环档 |
| TopMetal1↔TopMetal2 | 2.00×2.00 | TopVia2 档 |

**裁决**：§7 层分配表照用，无需压缩层序退路；规则符合性随 M2 代跑 DRC maximal 收口（官方 PCell 几何，预期干净）；M4/M5↔TopMetal1 占位按 1.64 见方留位。

## 二、cmim PCell（b7e7 阻塞项 3）
- PCell 名 `"cmim"`；参数 `{"Calculate":"w&l","w":"23.660u","l":"23.660u"}`（0.84 pF：Cspec=1.5 fF/µm² 官方 cmim_caspec → side=√(840/1.5)=23.664 → 相位 snap 23.66）。
- 实测：创建 OK，bbox 24.86×24.86（含边沿 ring），M5 引脚 1 / TOPM1 引脚 1，名义 C=839.7 fF（−0.04%）。
- 库原语：`b.mim_cap(name, c_fF, (x,y))` 自动解 W/L 并做相位 snap（lib13g2 v2 已带；23.665 offgrid×1296 案即此坑，snap 逻辑 L365-372）。
- 真值表 v1.1 §3 未收录 cmim=组长遗漏，v1.2 补列。

## 三、镜像语义判定（b7e7 阻塞项 1）——**库无缺陷，零改动**
KLayout `pya.Trans(rot, mirror, x, y)` 构造参数 mirror=True = **关于 x 轴镜像（y→−y）**，随后叠加 rot（b7e7 判别式误记为"绕 y 轴镜像 x→−x"）。真机点表：

| P | Trans(2,True,0,0) | Trans(0,True,0,0) |
|---|---|---|
| (1,0) | (−1,0) | (1,0) |
| (0,1) | (0,1) | (0,−1) |
| (1,1) | (−1,1) | (1,−1) |
| (−2,3) | (2,3) | (−2,−3) |

即 **Trans(2,True,0,0) ≡ 左右镜像（x→−x）**，与 lib13g2.mkpc_at docstring「mirror=True 绕 y 轴镜像，对称轴=(原x+target.x)/2」**一致**；Trans(0,True,0,0) 才是上下翻转。
**影响面**：无——M1 冒烟件镜像件朝向正确；hbtdiff_array 共质心热对称配对论证成立；库 v2 不升版。b7e7 dryrun 判别式按点表改正（其脚本按实测引脚走线，两种语义下 LVS 本就正确，无返工）。

## 四、HBT 依赖三件挂载（fde9 报备复核）
fde9 自 GitHub IHP-Open-PDK master 自取三件，与我侧官方树（pdk/ihp_open + pdk/sim/models + pdk/ihp_sg13g2 多副本）字节级互证一致，**已挂 8510 归档**（GET sim/models/…）：
- sg13g2_hbt_mod.lib 20,057 B sha256 ae9288f8…0bd79
- sg13g2_hbt_mod_mismatch.lib 20,486 B sha256 e7b462e4…71357
- sg13g2_hbt_stat.lib 2,463 B sha256 80d1893e…9a7db
（cornerHBT.lib 前已挂：bae3d705…de462，3975 B。）

## 五、投件通道状态
- b7e7 三件首投**未达**（无到件铃；dryrun/ 子目录单层白名单 400 是确定原因之一，已请平铺重投+回贴 POST 响应 sha）。自测：中文名 URL 编码 200 OK；子目录 400。
- b7e7 8445 本体仍死（Connection refused，04:44Z 试发）；协作走 8510 投件口+共享盘 top/组长信箱_2026-10-17.md（§六已挂判定全文）。
- 探针存档：/tmp/m2run/{mirror_probe,via_probe2,cmim_mirror_probe,diag3}.py（临时；关键点表已录本纪要）。
