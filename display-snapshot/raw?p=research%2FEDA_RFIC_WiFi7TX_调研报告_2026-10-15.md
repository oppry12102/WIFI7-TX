# 调研报告：模拟/RFIC 免费 EDA 工具·社区·最佳实践·Wi-Fi 7 TX 业界进展

- 委托：管理员（2026-10-15T09:58Z 来信）
- 执行：WiFi7-TX-组长 b7a0，经 miro-v2 深度搜索服务（http://222.128.12.37:8710，job=jd204b7202aff）
- 检索时间：2026-10-15T10:00~10:23Z，13 轮 / 45 次工具调用（GitHub/官网直读 + OpenAlex + 中英搜索引擎交叉）
- 质检：miro 自带 answer_verify（1 项存疑已就地标注）+ answer_url_check（23 条 URL 无违规）；一手来源 15 条
- 原始数据：research/miro_result.json（全文+来源+质检记录）、research/miro_job.json（执行事件流）

---
# 模拟/RFIC 开源 EDA 工具、社区与 Wi-Fi 7 TX 设计调研报告

**检索时间：2026-10-15（UTC）。** 方法说明：本次共约 37 次工具调用（官网/GitHub/readthedocs 直接抓取 + OpenAlex 学术库 + 中英文搜索引擎交叉）。部分目标站点（ngspice.sourceforge.io 官网首页、openems.de 主站）被 Cloudflare 拦截或 404，已改用 SourceForge 活动流与 GitHub 仓库页作为一手替代来源；凡未能读到正文的信息，下文均明确标注「未确认」。搜索过程中的数字（如各仓库 star/版本号）均以工具实际返回为准。

---

## 1. 免费开源 EDA 工具全景（截至 2026-10）

### 1.1 电路仿真：SPICE 类

**【事实】**
- **ngspice**：官网（ngspice.sourceforge.io）被 Cloudflare 拦截无法直读；但 SourceForge 官方活动流（2026-10-15 抓取）显示项目**极活跃**：开发线已到 `pre-master-48`（git master 提交 75f22a99，2026-10-14），核心维护者 Dietmar Warning 当天仍在 ngspice-users 论坛回复 agauss/蒙特卡洛相关 bug。IHP Open PDK 官方 README 将 ngspice 列为**受支持仿真器**（附官方下载页链接）。
- **Xyce**（Sandia 国家实验室）：同样被 IHP PDK README 列为受支持仿真器，并出现在 IIC-OSIC-TOOLS 工具清单中。
- **Qucs-S**：官网实测（ra3xdh.github.io）——"Qucs with SPICE"，最新稳定版 **26.1.1**；发布节奏为 2024-02（24.1.0）→ 2024-03 → 2024-07 → 2024-10（24.4.0）→ 2025-02（25.1.0）→ 2025-09（25.2.0）→ **2026-04-09（26.1.0）**，近两年持续月度级更新。可调用后端：**Ngspice、Xyce、QucsatorRF、SpiceOpus**。支持论坛为 GitHub Discussions。其官网发表列表含多篇 2025-2026 期刊论文（MDPI Electronics/JLPEA 等 DOI 见来源清单），学术背书较新。
- **RF SoC 实战证据**：Patrick Fath《Towards a practical open source RF SoC design flow: Lessons from a 40 GHz tapeout in IHP SG13G2》（Zenodo，2026-07-06）摘要明确：流程基于 IIC-OSIC-TOOLS，**Xschem 画图 + ngspice/Xyce 仿真 + KLayout 版图**完成 40 GHz RF SoC 流片，且用 ngspice 做了**并行参数扫描与蒙特卡洛**；post-layout 指标：工作频率 0.15–44.7 GHz、灵敏度 −56 dBm、动态范围 62 dB（芯片已提交流片、尚未实测）。

**【推断/边界】** 上述证据表明「开源 SPICE + 开源 BiCMOS PDK 跑通 40 GHz 级模拟/射频电路」在 2026 年已是**已发生事实**。但 ngspice 是否原生支持谐波平衡（HB）/包络仿真等 RF 专用分析，**本次未读到一手文档页面，无法确认**——Fath 工作采用的是时域仿真 + 并行扫描路线，可作为保守参照。Verilog-A 支持状态（如 ngspice 的 OSDI 接口）同样未在本次来源中出现，**未确认**。

### 1.2 版图与 PDK

**【事实】**
- **IHP SG13G2（开源生态中射频支持最强的 PDK）**：GitHub 官方仓库实测——"130nm BiCMOS Open Source PDK, dedicated for Analog/Digital, Mixed Signal and **RF Design**"，**Apache 2.0** 许可，2023-03 起指向 SG13G2 节点，**2,212 commits / 168 forks**（2026-10-15）。官方文档（readthedocs）自述仍处 **preview/alpha**，"not intended to be used for production at this moment"。**注意：** 广泛流传的 HBT fT/fmax 具体数值（如 300/500 GHz 级）**未出现在我抓到的 README/文档首页中，未确认，请以 IHP 官方 PDK 文档为准**。
  - CHANGELOG（2026-09-01 未发布版，实测全文）显示 RF 支持正在快速补齐：**RF MOSFET PyCells、MoM 电容 PCell（cap_cmomf/cap_mom/cap_cmomi）、rfcmim、KLayout 电感金属栈可配置（#1068）、Magic LVS 电感识别（#873）、肖特基二极管 SBD、HBT 测试结构 GDS、AWS Palace 的 gds2palace 子模块（#1040，并注明兼容 scikit-rf 2.0）**、Xschem/KLayout PDK 集成、并行仿真脚本等。
- **SkyWater sky130 / GF180MCU**：IIC-OSIC-TOOLS（JKU Linz 维护的 Docker 一体化镜像，实测 README："all-in-one Docker/Podman container for open-source-based integrated circuit designs for analog and digital circuit flows"，基于 Ubuntu 24.04 LTS，AMD64/ARM64）开箱支持 **SKY130/GF180/IHP130** 三套 PDK。相对而言 sky130/GF180 的 PDK 定位为通用模拟/数字，RF 无源器件（电感/巴伦）模型与 IHP 的 SiGe BiCMOS 相比**明显更弱**（此为推断；sky130 RF 支持细节本次未单独核验）。
- **版图工具链**：Magic（opencircuitdesign.com/magic，Tim Edwards，实测可访问）、**KLayout**、**Xschem**、**OpenROAD/OpenROAD-flow-scripts/LibreLane**（均在 IHP README 的 supported EDA tools 链接中出现）；IHP PDK 的 KLayout 已支持 DRC/LVS/PCell 全流程（CHANGELOG 大量条目佐证）。
- **开源综合综述**：Baungarten-Leon《From RTL to Fabrication: Survey of Open-Source EDA Tools and PDKs》（MDPI Electronics，2026-03-02，OpenAlex 实测）可作系统参考文献。

### 1.3 电磁仿真

**【事实】**
- **openEMS**（GitHub thliebig/openEMS-Project，实测 README）：免费开源 **FDTD** 电磁场求解器，**Octave/Matlab 与 Python 双脚本接口**，3D 笛卡尔/柱坐标渐变网格、多线程+SIMD、Drude/Lorentz/Debye 色散材料、时/频域场输出（vtk/hdf5）；文档站 docs.openEMS.de。README 有 AGENTS.md/AI_POLICY.md，2026 年仍在活跃维护。**openems.de 主站本次多次抓取失败（404/拦截），仅 GitHub 镜像可信。**
- **AWS Palace（gds2palace）**：已作为子模块进入 IHP PDK（#1040），可用于**从 GDS 版图直接做 FEM 电磁提取**——这是开源流里少见的「版图→EM→S 参数」环节，且 CHANGELOG 特别注明与 scikit-rf 2.0 兼容。
- **MEEP、Elmer FEM**：本次检索未获取二者一手页面，**适用性未验证**（不展开）。

### 1.4 系统级 / 行为级：Python 生态

**【事实】**
- **scikit-rf**（readthedocs 实测）：BSD 许可的 RF/微波工程 Python 库，对象化 Network/S参数、**Circuit、校准、去嵌入、Q 因子、Vector Fitting（含参数化）、Virtual Instruments（仪器控制）**；引用列表显示 2026 年仍在持续被学术论文引用。
- **gdsfactory**：出现在 IHP PDK README（`gdsfactory.github.io/IHP/` 集成指南，CHANGELOG #691）与 IIC-OSIC-TOOLS 工具清单中——用于**参数化版图自动化（含光子/射频无源件）**。
- 你们的 Python 链路仿真（EVM/SEM/ACLR/PVT 蒙特卡洛）天然可与 scikit-rf（S 参数网络/匹配）+ Palace/openEMS（无源件 EM）+ KLayout Python API（版图脚本化）组成**闭环**：行为级模型参数可由晶体管级/EM 仿真结果回填。【推断】

### 1.5 商业工具免费/学术资源（对比参照）

**【事实/边界】** 仅确认 Keysight 官网可达（keysight.com / keysight.com.cn）；**ADS/Cadence/AWR 的具体学术授权条款、免费试用范围未在本次来源中核验**，不展开。建议通过学校 EDA 联盟渠道申请（此为常识性建议，属推断）。商业工具在谐波平衡/包络/DPD 闭环验证上的成熟度仍显著领先开源流——与 CSDN《开源EDA的能力边界》一文观点一致（该文称模拟/RF 前端仍依赖大量手工与专用工具；百度转引，正文未直读，作为**趋势佐证**引用）。

---

## 2. 社区

**【事实】**
- **国际**：
  - **GitHub 为核心阵地**：IHP-GmbH（IHP-Open-PDK）、iic-jku（IIC-OSIC-TOOLS）、ra3xdh（Qucs-S，Discussions 即支持论坛）、thliebig（openEMS）、TinyTapeout 组织。
  - **TinyTapeout Discord**（官网实测链接 discord.gg/qZHPrPsmt6）是当前最活跃的开源芯片新手社区之一。
  - ngspice 用户论坛在 SourceForge（sourceforge.net/p/ngspice/discussion/…，2026-10 当天有活动）。
  - **ORConf**：本次检索未获取 2024-2026 年会议一手页面，**最新届次信息未确认**。
- **中文**：
  - **GitLink 开源芯片社区**（gitlink.org.cn/zone/OSchip，实测可达）。
  - CSDN/知乎上有一批实践博客（如《IHP SG13G2开源PDK终极指南》2026-08、《开源EDA的能力边界》）；openatom 开源原子基金会有 openDACS 开源 EDA 分论坛活动记录（2023）。
  - **找 PDK/IP 的实际路径**（推断+事实）：PDK 直接用官方仓库（IHP/SkyWater/GF180 的 GitHub）；开源 IP 检索 GitHub topic（IHP README 指向 `topics/ihp`、`topics/open-source`、`topics/pdk`）；流片渠道见第 3 节。

---

## 3. 优秀实践：开源流做 RFIC 的真实案例

**【事实】**
1. **Patrick Fath，40 GHz RF SoC @ IHP SG13G2**（Zenodo DOI 10.5281/zenodo.21508491，2026-07-06）：**目前公开可查、指标最完整的开源流 RFIC 流片案例**。完整流程=IIC-OSIC-TOOLS + Xschem + ngspice/Xyce + KLayout；含对数 RF 功率检测器（逐级检波对数视频放大器）；post-layout 0.15–44.7 GHz / −56 dBm / 62 dB。**作者明言：开源 RF-IC 生态最大缺口是「完全验证的自动寄生提取流程」**——这对你们 TX 设计是关键风险预告。
2. **TinyTapeout**（官网实测）：共享硅片平台，当前班车 **SKY26d / GF26c**（倒计时同天），提供 **IHP（Wokwi/Verilog）、SKY（Wokwi/Verilog/**Analog 模拟模板**）、GF 模板**；有价格计算器、往届 submitted chips 列表、Discord 支持；学术背书为 TechRxiv 论文《Tiny Tapeout: a shared silicon tapeout platform accessible to everyone》。**注意**：2025 年 Efabless 倒闭曾重创该项目（搜狐 2025 转述：chipIgnite 曾与 50 家学术机构合作、完成 80 项商业设计；TinyTapeout 承诺退款），**2025-08-28 宣布回归**（东方财富：改用基于 **LibreLane** 的定制流程做顶层复用器与数字后端）。RF 直接上 TinyTapeout 的公开案例**本次未找到**——SKY Analog 模板适合放大器类试验，但**电感/巴伦面积与 PAD 约束使完整射频前端难以塞进 tile**（推断）。
3. **开源 Wi-Fi 代表项目：openwifi**（GitHub open-sdr/openwifi，实测）：**SDR/FPGA 基带全栈** 802.11a/g/n（Wi-Fi 4），Linux mac80211 兼容，AGPLv3 双许可，支持 Xilinx Zynq + AD9361 平台，app note 明确 **70 MHz–6 GHz 频率范围**；有 w-iLab.t 测试床与公开论文列表。**定位澄清**：openwifi 是**基带+MAC 的 SDR 实现，不含 ASIC 射频**，可作为你们 TX 数字基带/行为级对拍参考，不是 RFIC 参考。【事实+澄清】
4. **IHP 官方生态信号**：bing_rss 抓到 2026-10-14 IHP 与智利 AC3E 宣布**三年开源半导体技术/工具/制造合作**（仅新闻索引，正文未读）——开源 RF 路线有官方持续投入。
   **⚠️ 组长注：此条经 miro 自带 answer_verify 判为「证据不足」——正文从未读到，仅 RSS 标题索引。引用前须到 ihp-microelectronics.com 原文核验，暂按传闻处理。**

**行为级+晶体管级混合验证最佳实践**（基于 Fath 案例+IIC-OSIC-TOOLS 能力归纳，属推断）：
- 数字控制/校准逻辑用 Verilog+cocotb（IIC-OSIC-TOOLS 含 cocotb）；模拟/RF 核心用 Xschem+ngspice（PVT 角+蒙特卡洛，ngspice 并行扫描已被 Fath 验证）；无源件用 Palace/openEMS 提取 S 参数后回灌 SPICE；行为级 Python 模型做系统级 EVM/SEM 闭环——与你们现有流程正好衔接。

---

## 4. Wi-Fi 7（802.11be）TX 射频业界进展（2024-2026）

**【事实——本次实际检索到的】**
- **关键 PHY 特性**（多源一致）：
  - **320 MHz 信道带宽、6 GHz 频段、4096-QAM、MLO（多链路操作）**：Qualcomm 官方 Wi-Fi 7 页面（320MHz/MLO/6GHz 文字实测可见）；OpenAlex 收录的 IEEE 综述（Deng et al. COMST 2020；Khorov et al. IEEE Access 2020；López-Raventós & Bellalta IEEE Wireless Commun. 2022 MLO 专文；García-Rodríguez IEEE Commun. Mag. 2021）摘要一致确认 4096-QAM/320MHz/MLO/multi-AP。
  - 中文侧资料（CSDN Wi-Fi 7 D3.0 解析、射频前端行业稿）同样以「6GHz+320MHz+4096-QAM+MLO」为四要素，并指出 **4096-QAM 对相位噪声/EVM 极为苛刻、320MHz 依赖连续信道**。
- **EVM 具体阈值**：4096-QAM 对应的 EVM 门限（通行说法约 −35 dB RMS）**未在本次任何来源原文中确认**——请以 IEEE 802.11be 标准文本/测试规范为准。百度文库一篇 WiFi7 测试稿提到「1 米视距、接收 −35 dBm、MCS13 PER<0.1%」（仅索引，未读正文），那是**接收侧测试条件，勿与 EVM 混用**。
- **国内生态**：康希通信（公众号稿，2026 上半年时点）称其 Wi-Fi 7 射频前端芯片已完成**博通/高通/联发科/瑞昱**四大主芯片平台参考设计认证——反映国内 RF-FEM 厂商已深度卡位 Wi-Fi 7。
- **学术前沿样本**：UC Irvine 140 GHz 120 Gbps CMOS 收发机报道（腾讯云开发者社区转述，速率为 Wi-Fi 7 的 4 倍）；Okada 实验室 DPLL 分数杂散抑制博士论文（OpenAlex，2024）。ISSCC 2024/2025 **具体 802.11be 论文标题与指标本次未能从公开渠道直接核验**（IEEE Xplore 检索被挡），**此处不列具体论文，避免凭印象编造**；检索 ISSCC 各届 program 摘要可确认 WLAN 收发机是常规 session 主题（OpenAlex 收录 RFIC/ISSCC program 页），但逐篇确认未完成。

**【推断——明确标注】** 基于上述公开资料与行业常识：Wi-Fi 7 主芯片 RF 趋势是**直接变频架构为主、数字辅助校准（DCO/DPLL）、DPD 用于高阶 QAM EVM 达标、6GHz+320MHz 推高 ADC/DAC 采样率与 PLL 带宽要求、MLO 要求双频段并发射频前端**。各家（高通/博通/联发科/MaxLinear）具体型号的架构细节与实测指标**未在本次来源中逐一确认**。

---

## 5. 落地建议（针对已完成 Python 行为级仿真的 Wi-Fi 7 TX ASIC 小组）

**推荐开源工具链组合**（全部经过本次实测存在且活跃）：

| 环节 | 工具 | 理由（事实依据） |
|---|---|---|
| 一体化环境 | **IIC-OSIC-TOOLS**（Docker） | 一键装齐 SKY130/GF180/IHP130 + 全套模拟工具，JKU 官方维护 |
| 工艺选择 | **IHP SG13G2** | 唯一明确面向 RF 的开源 BiCMOS PDK；RF 无源（电感/MoM/RF MOSFET PyCell）2026 年密集补齐；fT/fmax 请查其官方文档确认 |
| 原理图/仿真 | **Xschem + ngspice（+Xyce）** | Fath 40GHz 案例同款；支持并行蒙特卡洛 |
| 无源件 EM | **AWS Palace（gds2palace）→ scikit-rf** | PDK 官方集成、兼容 scikit-rf 2.0；电感/巴伦/匹配网络提取 |
| 备选 EM | **openEMS** | FDTD，Python 接口，适合天线/封装级 |
| 版图 | **KLayout（PCell/LVS/DRC）+ Magic** | IHP 官方支持链 |
| 系统闭环 | **scikit-rf + 你们现有 Python 栈** | S 参数/匹配/矢量拟合与行为级 EVM/SEM 模型互喂 |
| 流片 | **TinyTapeout（SKY26d/GF26c）或 IHP MPW 渠道** | TT 已从 Efabless 事件恢复并有 SKY Analog 模板；正式 RF 芯片走 IHP 官方 shuttle（注意 PDK 仍标 preview，量产需与 IHP 确认） |

**学习路径**（推断，但每步对应工具均已验证存在）：
1. 装 IIC-OSIC-TOOLS，跑通 IHP PDK 自带 Xschem+ngspice 示例（含标准单元 Qucs-S 原理图，CHANGELOG #939）。
2. 用 gds2palace 提取一个 PDK 自带电感 → scikit-rf 拟合 → 回灌 ngspice，验证「EM-电路」闭环。
3. 把你们 Python 行为级 TX 模型拆块：DAC/混频器/PA 驱动逐块晶体管化，块级指标由行为级模型反推（EVM 预算分配法）。
4. 关注 Fath 论文指出的**寄生提取缺口**：关键 RF 节点建议手工+Palace 双重提取互验。
5. 风险预案：PVT 蒙特卡洛结果与商业流对标时，注意开源 PDK 模型卡精度边界（IHP 官方自述 preview 状态）。

---

## 来源清单

**一手页面（2026-10-15 实测可访问）**
1. IHP-Open-PDK (GitHub) — https://github.com/IHP-GmbH/IHP-Open-PDK
2. IHP-Open-PDK CHANGELOG — https://github.com/IHP-GmbH/IHP-Open-PDK/blob/main/CHANGELOG.md
3. IHP OpenPDK 官方文档 — https://ihp-open-pdk-docs.readthedocs.io/en/latest/
4. IIC-OSIC-TOOLS (JKU) — https://github.com/iic-jku/IIC-OSIC-TOOLS
5. Qucs-S 官网 — https://ra3xdh.github.io/
6. ngspice SourceForge 活动流 — https://sourceforge.net/p/ngspice/activity/feed
7. openEMS-Project (GitHub) — https://github.com/thliebig/openEMS-Project
8. scikit-rf 文档 — https://scikit-rf.readthedocs.io/en/latest/
9. Magic VLSI — http://opencircuitdesign.com/magic/
10. Tiny Tapeout 官网 — https://tinytapeout.com/
11. openwifi (GitHub) — https://github.com/open-sdr/openwifi
12. Qualcomm Wi-Fi 7 页面 — https://www.qualcomm.com/wi-fi/wi-fi-7
13. GitLink 开源芯片社区 — https://gitlink.org.cn/zone/OSchip

**学术来源（OpenAlex 实测）**
14. P. Fath, "Towards a practical open source RF SoC design flow: Lessons from a 40 GHz tapeout in IHP SG13G2," Zenodo, 2026-07-06 — https://doi.org/10.5281/zenodo.21508491
15. E. I. Baungarten-Leon, "From RTL to Fabrication: Survey of Open-Source EDA Tools and PDKs," Electronics, 2026-03-02 — https://doi.org/10.3390/electronics15051048
16. C. Deng et al., "IEEE 802.11be Wi-Fi 7: New Challenges and Opportunities," COMST — https://doi.org/10.1109/comst.2020.3012715
17. E. Khorov et al., "Current Status and Directions of IEEE 802.11be, the Future Wi-Fi 7," IEEE Access — https://doi.org/10.1109/access.2020.2993448
18. Á. López-Raventós & B. Bellalta, "Multi-Link Operation in IEEE 802.11be WLANs," IEEE Wireless Communications — https://doi.org/10.1109/mwc.006.2100404

**新闻/二手（标注可读性）**
19. 开源芯片先驱 Efabless 倒闭 — https://m.sohu.com/a/866090434_121948415 （snippet 级，未读全文）
20. Tiny Tapeout 回归 — https://caifuhao.eastmoney.com/news/20250828091910556412710 （snippet 级）
21. 康希通信 Wi-Fi 7 射频前端 — https://baijiahao.baidu.com/s?id=1875272496565051823 （snippet 级）
22. CSDN《Wi-Fi 7 D3.0 草案解读》 — https://blog.csdn.net/weixin_42685438/article/details/167714013 （snippet 级）
23. UC Irvine 140GHz 收发机报道 — https://cloud.tencent.com/developer/article/2642089 （snippet 级）
24. IHP × AC3E 合作（2026-10-14）— 来自 Bing RSS 索引（源页 www.ihp-microelectronics.com，具体新闻 URL 未获取），标题索引可见、正文未读
25. 《IHP SG13G2 开源 PDK 终极指南》— CSDN 2026-08-23（Bing RSS snippet，正文未读）

**未找到/未确认项（如实声明）**：ngspice 的 HB/Verilog-A 支持细节、IHP HBT 具体 fT/fmax 数值、ORConf 2024-2026 届次、4096-QAM EVM 具体门限数值、ISSCC 2024/2025 具体 802.11be 论文逐篇信息、高通/博通/联发科/MaxLinear 各家架构细节、MEEP/Elmer FEM 射频适用性、商业工具学术授权条款。以上请按来源清单逐项溯源或另行专项检索。

---
## 附：组长落地注记（对本组 WiFi7-TX 项目的直接影响）

1. **工艺锚点**：IHP SG13G2 是开源生态里唯一明确面向 RF 的 PDK（Apache 2.0，但官方自述 preview 状态）——电路组员 b7e7 的 SOW-1 晶体管级部分若需 PDK，应以此为主选；HBT fT/fmax 数值须以官方文档为准（本次未核实）。
2. **风险预告**（Fath 40GHz 案例作者原话）：开源流最大缺口是「完全验证的自动寄生提取流程」——我们仿真组 fde9 的行为级结果与未来晶体管级对拍时，关键 RF 节点需手工+Palace 双重提取互验。
3. **闭环衔接**：本组现有 Python 行为级栈（EVM/SEM/ACLR/PVT MC）+ scikit-rf + gds2palace→S参数回灌 ngspice，可组成行为级↔晶体管级↔EM 三层闭环——建议写入架构文档 v1.1。
4. **4096-QAM EVM 门限（约 -35dB RMS）本次未从标准文本核实**——与我们 spec.md 的 -41dB 设计目标（含裕量）口径不冲突，但终稿引用时以 802.11be 标准原文为准。
