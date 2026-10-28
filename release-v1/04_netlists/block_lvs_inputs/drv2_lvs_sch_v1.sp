* drv2 LVS schematic（deck 方言）· 自动生成，勿手改 · make_sch_lvs_netlist.py
* 源: sow6_in/drv2_subckt_LVS输入_v1.sp sha16=d221226f3fd804ec（b7e7 逐字拷贝件）
* R 几何锚: drv2_v17_netonly/m3_drv2_v17_extracted.cir（rsil/rppd/rhigh 三族）
* 转换: X→Q / hbt_mirror 内联 / 剥 V,Cin,Ct,Lt / R→3T 带模型（版图实态）
* 剥离清单: C:Cin1, C:Cin2, V:Vb, V:Vbcas, L:Lt1, L:Lt2, C:Ct1, C:Ct2, XBI:XBI1, XBI:XBI2, XBI:XBI3, XBI:XBI4
.subckt TX5G_M3_DRV2_V14 inp inn outp outn vcc
Q_XQ1 ccas1 bin e1 0 npn13G2 we=70n le=900n NX=10 M=1
Q_XQ2 ccas2 bb1 e2 0 npn13G2 we=70n le=900n NX=10 M=1
Q_XQ3 outp nbcas ccas1 0 npn13G2 we=70n le=900n NX=10 M=1
Q_XQ4 outn nbcas ccas2 0 npn13G2 we=70n le=900n NX=10 M=1
Q_XBI1_Qr XBI1__nref XBI1__nref 0 0 npn13G2 we=70n le=900n NX=1 M=1
Q_XBI1_Qo ntail XBI1__nref 0 0 npn13G2 we=70n le=900n NX=8 M=1
Q_XBI2_Qr XBI2__nref XBI2__nref 0 0 npn13G2 we=70n le=900n NX=1 M=1
Q_XBI2_Qo ntail XBI2__nref 0 0 npn13G2 we=70n le=900n NX=8 M=1
Q_XBI3_Qr XBI3__nref XBI3__nref 0 0 npn13G2 we=70n le=900n NX=1 M=1
Q_XBI3_Qo ntail XBI3__nref 0 0 npn13G2 we=70n le=900n NX=8 M=1
Q_XBI4_Qr XBI4__nref XBI4__nref 0 0 npn13G2 we=70n le=900n NX=1 M=1
Q_XBI4_Qo ntail XBI4__nref 0 0 npn13G2 we=70n le=900n NX=8 M=1
Rin1 inp 0 0 rhigh L=1u W=1.36u M=1
Rin2 inn 0 0 rhigh L=1u W=1.36u M=1
Re1 e1 ntail 0 rsil L=1u W=4.665u M=1
Re2 e2 ntail 0 rsil L=1u W=4.665u M=1
Rb1 bin nbias 0 rppd L=1.923u W=1u M=1
Rb2 bb1 nbias 0 rppd L=1.923u W=1u M=1
RL1 vcc outp 0 rppd L=1u W=2.6u M=1
RL2 vcc outn 0 rppd L=1u W=2.6u M=1
Rref1 vcc XBI1__nref 0 rhigh L=1.19u W=1u M=1
Rref2 vcc XBI2__nref 0 rhigh L=1.19u W=1u M=1
Rref3 vcc XBI3__nref 0 rhigh L=1.19u W=1u M=1
Rref4 vcc XBI4__nref 0 rhigh L=1.19u W=1u M=1
.ends TX5G_M3_DRV2_V14
