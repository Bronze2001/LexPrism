# 数据与工具约定

这些是LexPrism拟使用的逻辑对象与能力名称，不是宿主已安装工具清单。首次连接工具时读取其真实定义，再映射；没有相应工具的能力保持不可用。

## 任务交接对象

| 对象 | 核心字段 |
| --- | --- |
| Task | task_id、目标、业务类型、jurisdictions、as_of、reader、deliverable、source_mode、输入版本、当前门禁状态 |
| Issue | issue_id、问题、前置条件、待查法域／来源、覆盖状态 |
| Source | source_id、provider、原始出处、来源类型、content_kind、法域、语言、版本、效力核验状态、取得时间、访问／保存范围 |
| Passage | passage_id、source_id、原文、location、解析方式与状态、原文／译文关系 |
| FrozenCitations | snapshot_id、task_id、run_id、frozen_at、legal_as_of、jurisdictions、statutes清单、precedents清单、institutional_docs清单、unsupported清单、sha256 |
| Claim | claim_id、issue_id、类型、表述、事实前提、支持及反对passage_id、关联citation_id、四层核验状态 |
| Draft | draft_id、version、稳定段落ID、引用claim_id、frozen_citations_ref、三审计员状态、变更记录、交付状态 |
| AuditReport | report_id、task_id、draft_version、consistency_audit结果、contradiction_audit结果、tone_audit结果、overall_verdict（PASS/BLOCKED）、gate_clearance |
| Run | run_id、输入／技能／模板版本、门禁进度（G1~G5）、步骤状态、工具结果引用、失败、耗时、模型参数 |
| Feedback | 评测案例、run_id、答案版本、专家原话、位置、类别、适用范围、修复与采纳状态 |

文书事实材料另保留提供人、来源链、是否签署、是否完整、是否争议；不把证据可信性压缩为法源T1/T2/T3。

## 门禁流转状态机

```text
[G1: INTAKE_LOCKED] ──> [G2: SOURCES_ENTITLED (生成 frozen_citations.json)] ──> [G3: CLAIMS_MAPPED]
                                                                                        │
[UNRESTRICTED_DELIVERY] <── [G5: CITATION_AUDITED (audit_report 全 PASS)] <── [G4: LAWYER_SANCTIONED 👤]
```

- 门禁状态：`G1_PENDING` → `G1_LOCKED` → `G2_FROZEN` → `G3_MAPPED` → `G4_SANCTIONED` → `G5_AUDITED`。
- 交付许可：`BLOCKED`（存在重大证据缺陷或未冻结引用）／`RESTRICTED_DRAFT`（未获 G4 律师签署或 G5 审计未全绿）／`UNRESTRICTED_DELIVERY`（正式交付）。

## 能力协商

| 能力 | 要解决的问题 |
| --- | --- |
| search | 查找记录；返回metadata或snippet不代表取得全文 |
| fetch_document | 读取完整或明确片段范围的原始文书 |
| get_versions | 取得法规版本和修订关系，不保证自动判定适用 |
| get_citation_links | 取得引用关系，不等同于负面司法处理分析 |
| get_treatment | 提供有依据的后续司法处理／引证效力信息，仅在上游实际支持时启用 |
| start_research / poll_research / get_report | 供应商异步研究；结果标为供应商生成报告 |

结果至少带provider、上游记录ID、content_kind、范围、完整性、时间和可用定位。能力缺失返回unsupported；无权限、限流、来源不可用、解析失败与没有结果分别记录。部分成功保留数据和缺口，不能把失败转换为“没有法律规定”。

数据库AI报告可以参与研究，但报告里的引用只有在实际取得对应原始文书并核对后，才能标“已核对原文”。专业数据库品牌不能自动覆盖LexPrism新增的推理。

## 分层状态

- 获取：not_requested／retrieved／partial／unavailable。
- 文字定位：not_checked／matched／mismatched／unreadable。
- 语义支持：not_reviewed／supported／contradicted／insufficient。
- 专家复核：not_reviewed／accepted／revise／disputed。
- 审计员裁决：PASS／BLOCKED／PENDING。

只记录实际观察；缺失模型用量或版本时记unknown，而不是编造。

## 存储与调用边界

如果宿主支持文件保存，使用项目指定位置按task_id/run_id分开存放；原始材料、法源、范例和专家答案分区。`frozen_citations.json` 与 `audit_report.json` 与任务文稿并列存放，不进版本库的保密目录。日志不记录凭据。外部查询发送解决问题所需的信息，不默认上传整个案件目录。

保留来源许可范围；明确可保存时留原始文件与哈希，保存权不明确则保存允许的元数据、链接和核验记录。自建MCP优先对接受支持API，不以模拟登录绕过接口授权。云端宿主不能直接读取用户电脑的localhost服务，接入前确认使用桌面STDIO还是经授权的远程部署。
