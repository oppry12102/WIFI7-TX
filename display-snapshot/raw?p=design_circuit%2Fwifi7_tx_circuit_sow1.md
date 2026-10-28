# 指针：WiFi7-TX 电路设计 SOW-1 → design_circuit/

组长 b7a0 任务书 SOW-1 的交付落在（按任务书指定路径）：

- `../design_circuit/design_circuit.md` — 主文档（口径假设、逐级参数表、预算复算、EVM 对账、风险、待裁决项）
- `../design_circuit/budget_check.py` — 复算脚本（级联增益/OP1dB/OIP3、EVM RSS、相噪积分、PA 扫描、参考源对比）
- `../design_circuit/params.csv` — 参数表（唯一数据源）

复跑：`cd ../design_circuit && python3 budget_check.py`

一句话结论：全链 EVM 6G −44.7 dB / 2.4G −44.9 dB（目标 −41），功耗 881/731 mW（上限 1000/800），
7 个 EVM 块全部达标（每块裕量 ≥2.1 dB）；但闭环依赖架构未列的 DPD（6G 13 dB / 2.4G 24 dB 三阶 IM3 对消）。
