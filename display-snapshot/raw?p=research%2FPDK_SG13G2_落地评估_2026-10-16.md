# IHP SG13G2 开源 PDK 落地评估（真实芯片设计环境）

- 日期：2026-10-16（UTC）
- 触发：管理员指令（事实账 n=891）「找找开源 PDK，做真正的芯片设计。miro-v2 搜索应该有结果了。在 research 目录」
- 依据：research/EDA_RFIC_WiFi7TX_调研报告_2026-10-15.md 结论——IHP SG13G2 是开源生态唯一明确面向 RF 的 PDK
- 状态：**环境已完全跑通，首个器件级仿真数据已产出**

---

## 1. 环境栈（全部免 root，固化于 /data/workspace/pdk/）

| 组件 | 版本/来源 | 安装方式 |
|---|---|---|
| ngspice | **47**（2025，KLU 求解器） | Debian 13 pool 的 .deb（ngspice_47+ds-1 + libngspice0_47+ds-1），dpkg-deb -x 提取到 pdk/ngroot/，补齐 18 个动态库依赖 |
| PDK 模型 | IHP-Open-PDK main 分支（331c004…） | 不走 git clone（TLS 中断），改 GitHub API 文件树 + raw 单文件并行下载 **44 文件 429KB**（libs.tech/ngspice/ 全部 + 官方 testbench 样例） |
| 运行封装 | skills/sg13g2_sim.py（已注册技能 sg13g2_sim） | 封装 LD_LIBRARY_PATH / cwd / 超时 |

- 磁盘占用：模型 429KB + ngspice 及依赖 ~15MB + debs 缓存 ~20MB
- 内存：单电路仿真 <100MB（3GB 机器余量充足）
- 遗留：Xschem/KLayout 版图工具链未装（下一步版图阶段再评估）；OSDI（Verilog-A）模块未启用（MoM 电容模型 cap_cmomf 需要，本次未用）

## 2. 踩坑实录（后续复用，重要度排序）

1. **subckt 实例必须 X 前缀**：`Q1 c b e 0 npn13G2` 会被当 BJT 原语找 .model 报 "could not find a valid modelname"；必须 `XQ1 …`（PDK 官方 testbench 全用 X）。这一条浪费了最长时间。
2. **include 路径/sourcepath 机制**：netlist 里 `.include` 绝对路径会被 sourcepath 前缀拼接（ngspice 47 行为）；官方 .spiceinit 的 `$PDK_ROOT/$PDK` 变量在 batch 模式不展开。**解法**：模型文件拷贝至网表目录相对引用（sim/models/ 已固化）。
3. **netlist 第一行永远是标题（注释）**：`.include` 放第一行会被吃掉。
4. **模型文件含 latin1 字节**（µm/°C）：部分解析路径受影响；已做 ASCII 清洗（>127 字节替换为 ?），原件保留在 pdk/ihp_sg13g2/。
5. **AC 激励必须显式给 ac 幅值**：串入的测流电压源要 `dc 0 ac 1`（归一化 1V 激励，h21 直接=db 差）。
6. **0V 测流源串接会悬空被测节点**：发射极经 VBE2 链接后无地路径，v(e) 浮到 0.87V、Vbe 实际为 0（Ic 仅 pA 级）。测流源必须串在**有偏置源的一侧**。
7. deb 依赖手工解析：pool 目录按**源码包名**组织（libflac14 在 f/flac/ 下），直接猜路径会 404；用 packages.debian.org 的 download 页解析 pool 路径最稳。

## 3. 首个器件数据：npn13G2 SiGe HBT（Nx=4，Vce=1.2V，typ 角，27℃）

| Vbe (V) | Ic (mA) | β | fT (GHz) |
|---|---|---|---|
| 0.75 | 0.096 | 812 | 32.6 |
| 0.78 | 0.286 | 821 | 86.5 |
| 0.81 | 0.791 | 798 | 187.2 |
| 0.84 | 1.890 | 725 | 302.1 |
| 0.87 | 3.761 | 615 | 382.2 |
| 0.90 | 6.374 | 498 | 422.4 |
| 0.93 | 9.603 | 394 | 434.2 |

- 数据文件：pdk/sim/ft_ic_np13G2_Nx4.csv、pdk/sim/gummel_Nx4.csv；testbench：pdk/sim/tb_hbt_ft.sp、tb_gummel.sp
- β 峰值 ~820 @ 0.1~0.3mA；fT 随 Ic 单调上升，Nx=4 器件电流上限（0.003A×4=12mA）附近达 **434GHz**
- **调研报告遗留的「HBT fT 未确认」项就此关闭**：模型实测口径 fT 峰值 >430GHz（Nx=4；更大 Nx 及峰值电流须待器件级详细扫描）

## 4. 对 Wi-Fi 7 TX 项目的结论

1. **工艺可行性正式确认**：SG13G2 HBT fT（434GHz）≈ 工作频率（5~7GHz）的 60 倍以上，PA 驱动/混频对/LNA 级有巨大裕量；130nm CMOS（sg13_lv/hv_mos）可承载基带接口与数字控制。
2. **设计口径升级**：design_circuit/ 原为「规划级/抽象 PDK」；现可升级为 **SG13G2 真实器件级**——器件名、参数、corner（tt/ss/ff + mismatch）全部可引用真模型。
3. **仿真流程闭环**：行为级（Python）↔ 晶体管级（ngspice+SG13G2）两层已在同一台机器上跑通；EM 层（Palace/openEMS）留待版图阶段。
4. **流片路径**（供管理员决策）：TinyTapeout SKY Analog 模板（教学级）或 IHP 官方 MPW shuttle（正式 RF，PDK 仍标 preview 需留意）。

## 5. 下一步（已派工）

- **b7e7（电路设计）**：TX 链晶体管化 SOW-2——混频器核心/PA 驱动级用 npn13G2+sg13_mos 落图，偏置点参考本文件 §3
- **fde9（仿真验证）**：SOW-2 仿真侧——器件级 corner/mismatch 扫描流程、与行为级模型对拍口径
- 组长：架构文档 PDK 章节更新（v1.1）+ 集成评审口径刷新
