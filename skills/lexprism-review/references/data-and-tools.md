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
| Draft | draft_id、version、稳定段落ID、引用claim_id、frozen_citations_ref、自检与独立审阅状态、双文件名称及版本、变更记录、交付状态 |
| AuditReport | report_id、task_id、draft_version、所审双文件、consistency_audit结果、contradiction_audit结果、tone_audit结果、view_consistency结果、overall_verdict（PASS/REVISE/PENDING）、findings、gate_clearance |
| Run | run_id、输入／技能／模板版本、门禁进度（G1~G5）、步骤状态、工具结果引用、失败、耗时、模型参数 |
| Feedback | 评测案例、run_id、答案版本、专家原话、位置、类别、适用范围、修复与采纳状态 |

文书事实材料另保留提供人、来源链、是否签署、是否完整、是否争议；不把证据可信性压缩为法源T1/T2/T3。

## 输出与增量修改字段

这些是工作记录约定，未提供存储工具时在当前回复中保留，不声称已有数据库实现。

- Task 增加 output_mode（comparison／clean／both）、输出偏好与审查立场；Draft 增加底本版本和各视图对应版本。
- Source 增加提供渠道、原始来源类型、source_tier（T1／T2／T3／pending）、分级规则版本和理由；真实性、译文、效力和适用性保持独立状态。
- 团队分级采用 research.md 的现行定义；另记 original_language、translation_type、tier_adjustment_reason。可下载材料记录 archive_status（saved／failed／unavailable／restricted）、原始网址、保存位置与实际可得哈希，不能用“有链接”代替已留档。
- Citation 记录 citation_id、claim_id、passage_id、逐处脚注位置、文末汇总项；同一来源的不同语句分开定位。法律使用等级与效力字段分开保存。
- 本地限制记录 processing_boundary（local_only／authorized_host）、核实的处理引擎和存储边界；未确认时为 unknown，不依据脚本位于本机推定模型离线。
- 材料影响记录包括 source_id／passage_id、目标 claim_id／段落 ID、关系、匹配理由、采用／不采用原因、旧／新版本与待核实事项。
- 合同清单记录包括原序号 0—30、子项、适用性、状态、条款定位、依据、风险及修改建议。
- 视图共享主张和引用，不独立保存相互漂移的结论；增量修订记录旧／新文字及理由，文末说明随实质风险变化更新。

## 门禁流转状态机

```text
[G1 受理] → [G2 来源核验与冻结] → [G3 底本及双文件，自检]
                                         ↓ 写入共享项目送审版本
                         [G5 另一对话审阅双文件]
                            ↓ REVISE / PENDING：返回修改／补件后复审
                            ↓ PASS：该版本审阅通过
[G4 对当前版本的真实律师确认] + [G5 PASS] → [正式交付]
```

- G1、G2、G3 依次推进；G4 和 G5 独立记录，先后均可。G5 只有针对当前成对版本的完整独立审阅 PASS 才记 `G5_AUDITED`；生成自检不推进 G5。
- 交付许可：`BLOCKED`（存在重大证据缺陷或未冻结引用，仍可提供注明限制的草稿）／`RESTRICTED_DRAFT`（G4 或 G5 未完成）／`UNRESTRICTED_DELIVERY`（当前版本两者均完成）。这是交付状态，不与审阅的 REVISE／PENDING 混用。

## 能力协商

检索提供方参考 [mcp-routing.md](mcp-routing.md) 的法域及材料类型建议，再匹配真实工具。服务名不是函数名；模型可自主选择表外已暴露且合适的 MCP 或网络搜索，不把推荐表当白名单。部署说明中的配置状态与当前可用性、覆盖范围、实际运行结果分开记录。

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
- 审阅维度与整体裁决：PASS／REVISE／PENDING，中文为审阅通过／修改后复审／待补件或待确认；旧 BLOCKED 报告保留原值，不重写历史。

只记录实际观察；缺失模型用量或版本时记unknown，而不是编造。

审阅状态另记 review_mode（self_check／separate_conversation／human）、execution_ref（实际审阅回复或可导出对话记录）、draft_version、verification_file、clean_file、checked_scope、findings、unperformed_checks。没有真实审阅记录不宣称独立运行；一个 separate_conversation 不代表三个 Agent。同一生成对话切换角色记 self_check。人工确认须对应真实反馈及版本。来源目录、gid、格式完整的 JSON 或自定义 ID 不提升取得／定位／语义核验状态。成文日、公布日、网页发布日期及施行日分别保存，未知值不互相代填。

项目交接使用 WORK.md 索引、成对版本快照和独立审阅文件，Agent 维护结构化记录，不要求律师填写 JSON。问题记录包含稳定编号、目标版本、视图和原句／上下文位置、类别、是否阻断、依据、修订要求与解决条件。学习记录包含出处／位置、用途、提炼规则、应用位置及核验结果。细节见 [project-collaboration.md](project-collaboration.md) 和 [reference-learning.md](reference-learning.md)。

项目程序的 state.json 用于文件版本和审阅登记，不能替代完整 Task／Claim／Source 数据。它的四个检查键 evidence／coverage／prose／views 分别对应实质引注、反向与覆盖、文风、双版一致性；不把旧模板字段默认解释为已经自动互转。版本与完成审阅的文件清单／哈希必须实际计算；新增版本不继承旧 PASS。

## 存储与调用边界

如果宿主支持文件保存，使用项目指定位置按task_id/run_id分开存放；原始材料、法源、范例和专家答案分区。`frozen_citations.json` 与 `audit_report.json` 与任务文稿并列存放，不进版本库的保密目录。日志不记录凭据。外部查询发送解决问题所需的信息，不默认上传整个案件目录。

保留来源许可范围；明确可保存时留原始文件与哈希，保存权不明确则保存允许的元数据、链接和核验记录。自建MCP优先对接受支持API，不以模拟登录绕过接口授权。云端宿主不能直接读取用户电脑的localhost服务，接入前确认使用桌面STDIO还是经授权的远程部署。
