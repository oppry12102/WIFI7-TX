# watch 覆盖基线（对照锚）—— 粘连版 pex_v27

- 生成：2026-10-18T03:25:30Z（fde9，依据 b7a0 裁定七 条款 5）
- 基线三件 sha256：mix 33e9e75451ab5cb8、drv1 ae4feb76076ae01c、drv2 1f5e0cd837b9af17
- 状态定义：SELFLOOP=两端同名 R（粘连）；DISTINCT=两端不同名 R（已归位）；ABSENT=不在任何 R 上

| watch 节点 | mix | drv1 | drv2 |
|---|---|---|---|
| e1a | SELFLOOP | ABSENT | ABSENT |
| e2a | SELFLOOP | ABSENT | ABSENT |
| e1b | SELFLOOP | ABSENT | ABSENT |
| e2b | SELFLOOP | ABSENT | ABSENT |
| e1 | ABSENT | SELFLOOP | ABSENT |
| e2 | ABSENT | SELFLOOP | ABSENT |
| ccas1 | ABSENT | ABSENT | SELFLOOP |

- 用途：① 判据器 A0「监督留痕」对照（消失/异动须注记去向；无注记的消失 → ATTENTION 停线请裁定）；
  ② v1.1 提取设置声明附录的对照锚（换版提取须重算此基线）。
