# Public release sanitization

- 源包：`WIFI7-TX_release_v1.tar.gz`（b7a0 / xusi agent-4ab5 交付）
  - sha256：`41e5b401d761b1fa6fc2825544a3ab05e4c7ec110bd5a3d9e14e15829c2334f3`
- 公开树处理：`02_spec_and_reports/sow_reports/SOW-6_全链版图报告.md` 中一处历史 file-key 形态值（`fk-*`）已替换为 `<redacted>`；其余凭据/PDK 本体/中间产物未入包。
- 本目录保留源包的 `RELEASE_MANIFEST.sha256` 与 `MANIFEST.json` 作为来源存证；它们描述的是**原始包**，因此对应被脱敏文件的那一条不会与公开树逐位一致。校验公开树请用 **`PUBLIC_MANIFEST.sha256`**。
- PDK 仅保留 IHP SG13G2 的名称/版本/来源指针，不包含 PDK 二进制与文档。
