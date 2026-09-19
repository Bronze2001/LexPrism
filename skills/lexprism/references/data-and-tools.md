# 引用记录与实际运行文件

仅在创建记录或确认字段含义时读取。普通文件把下列信息合并在核验说明中，保留可访问原件即可；表中 BRIEF.md、evidence、RESPONSE.md 是已有项目的存放约定，不是普通任务的建文件清单。可用 JSON 或核验表，字段多不代表核验完成。

## 本版材料如何对应

| 记录 | 必要内容与保存位置 |
| --- | --- |
| 任务 | BRIEF.md保留原始要求及补充、事实前提、读者／立场、文种、法域、基准日、来源与隐私限制、样本偏好。 |
| 依据 | evidence内保留原始出处、提供渠道、来源性质与团队等级、语言／译文类型、版本／各类日期、取得范围、许可、存档位置及实际可得哈希。事实材料另记提供人、完整性、签署和争议状态。 |
| 原文与主张 | 稳定编号关联原句、条款／页段位置、支持或反向关系、理解与适用前提、正文使用句及脚注。关键事实、规则、推论、建议可分别追溯，不要求重复全文。 |
| 引用快照 | frozen_citations.json或完整核验附录固定本版实际使用的依据和映射，标事项、版本及取得时间；变更后保留旧版。其有效内容必须随双文件快照保存，不能仅指向可被覆盖的共用sources目录。 |
| 修订回应 | RESPONSE.md写意见编号、接受处理／证据异议／待补件、原新位置、原因和未决影响；原始专家反馈及适用范围一并保留。 |

决定性依据分别记 text_check（原文对应）、temporal_check（基准日效力）、applicability_check（本案支持与条件），每项有实际依据或缺口。不以 verified-verbatim 覆盖另外两项。原文、语言等级、法律效力与适用性是不同判断，详细标准见 [research.md](research.md)。

## 已登记项目的审阅与版本

state.json、manifest.json、WORK.md由项目程序维护。审阅写入该次reviews目录下的REVIEW.md及程序生成的result.json，保留其实际字段，不另造audit_report.json来登记第二套结论。

新版 review_protocol=2；四维键为evidence、coverage、prose、views；每项含status和实际检查范围／依据。findings含稳定id、kind、basis、blocking、status、anchor、reason、requested_change、acceptance；RESOLVED另填resolution。execution_ref记录真实执行位置，unperformed_checks记录未完成的必要检查。字段及关闭标准见审阅技能和 [review-decisions.md](review-decisions.md)，程序只验字段与版本，不判断法律正确性。

上述 protocol=2 对应旧单 pair 记录。0.8.0 的受管理成果包采用 submission_protocol=2、review_protocol=3，补充成果范围、独立对话来源、必要页面检查和发布记录；具体字段见 [project-runtime.md](project-runtime.md)。保留旧记录，不就地补造为新协议。

G1受理、G2依据、G3生成自检、G5独立审阅、G4律师确认仅用于理解历史记录，不另建状态机。当前工作以程序登记和实际证据为准；旧报告字段原样保留，不猜测自动互转或重写历史。

## 工具记录与存储

仅使用真实暴露且获授权的工具。记录提供方、查询／筛选、时间、结果定位、完整性及限制；区分原始全文、片段、搜索摘要、供应商AI报告。未取得原文、无权限、限流、解析失败和检索空结果不能混同，失败不等于没有法律规定；未知用量或版本如实记未知。

普通文件的材料和记录在授权成果位置保存，送审后保留对应旧版；已登记项目在独占工作副本保存并随提交封存。许可不允许留全文时保留允许的元数据、位置和核验记录；日志不记录凭据，外部查询只发必要信息，不默认上传案件目录。本地限制见 [translation-privacy.md](translation-privacy.md)，选源需要时见 [mcp-routing.md](mcp-routing.md)。客户端本地脚本不证明模型离线，云端也不能假定能访问用户电脑服务。
