# 任务书 SOW-1 · 电路设计岗（WiFi7-TX-电路设计）

- 发起：组长 b7a0，2026-10-15 | 依据：spec.md v1.0、architecture.md v1.0（全文随信附上或自取）
- 交付物落盘：你自己的 workspace 下 `design_circuit/design_circuit.md`（主文档）+ `budget_check.py`（链路验算脚本）+ `params.csv`（逐级参数表）

## 工作内容（行为级，无 EDA 环境）

1. **逐级参数表**：按 architecture.md §2 链路预算，对 DAC→重构LPF→VGA→GM/混频→驱动→功率级
   （2.4G 与 5/6G 双路）逐级给出：结构选型（含备选与理由）、偏置/电源、增益、OP1dB/OIP3、
   电流功耗、关键无源（transformer 匝比/电感量级，声明假设）。
2. **链路预算验算脚本 budget_check.py**：实现级联增益/OP1dB（含压缩交互的简化级联公式）、
   OIP3 级联、EVM 按 RSS 合成；复算 spec §7 预算表与 architecture §2 合计，输出对比表。
3. **EVM 分配对账**：你给的逐级线性度参数换算成各块 EVM 贡献，必须 ≤ spec §7 分配值
   （留 ≥2 dB 每块裕量声明）。若某块做不到，**回信组长**重议分配，不要自行压指标。
4. **风险清单**：与 architecture §7 对照，补充你视角的设计风险（工艺角、版图敏感点）。

## 验收口径
- 数字与 spec/architecture 一一对应；所有假设显式声明；
- budget_check.py 在任意 40nm 风格参数下可复跑（参数化，不写死）。
- 完成后：向组长收信口 POST /inbox?token=…（token 查根目录 b7a0 条目），
  信中给出：交付文件清单 + 三行结论（预算闭环? / 超差项? / 风险头条）。
