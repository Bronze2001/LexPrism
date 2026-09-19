---
name: lexprism-review
description: 为律师独立复核法律意见书、检索报告、营商环境与海外投资合规指南或合同审查成果，检查引用是否支持结论、漏项和前提，按修改稿复审。可直接审阅用户给出的文件，无需先建项目。直接审合同或改正文用 lexprism；普通校对不冒充独立法律验收。
metadata:
  version: 0.8.3-letter-format
---

# LexPrism 文本审阅

## 工作顺序

1. **固定所审文件**：直接读取完整文稿、原始要求、对应证据和已有意见。已配置两窗口工作区、已登记事项或明确要求版本管理时，按 [project-collaboration.md](references/project-collaboration.md) 绑定生成窗口的同一事项，每次被律师触发都刷新状态并固定版本；不另建事项。其他独立文件按 [file-delivery.md](references/file-delivery.md) 直接审阅，不为审一份文件补造第二份正文。
2. **执行检查**：按 [review-protocol.md](references/review-protocol.md) 检查证据、覆盖、文风和适用的一致性。涉及法律依据读 [research.md](references/research.md)；需要判断正文或引注的具体规范时读 [drafting-review.md](references/drafting-review.md)。仅核对给定文字时按该范围完成，不自动扩大为整份法律验收。
3. **写意见**：区分已证实错误、尚未核实、表达建议。替代法条、金额、期限或结论也须有适用依据；复核生成侧异议，允许撤回误报。普通文件只出一份审阅意见；已登记事项才写 REVIEW.md 和程序生成的 result.json，不修改送审正文。
4. **结论与停止**：按 [review-decisions.md](references/review-decisions.md) 给出通过、修改后复审或待补件；项目模式核对实际登记结果。复审必须读新稿；旧稿续查不等于新稿验收。通过后结束本轮，提示律师回生成窗口办理交付；通过不替代律师确认，不触发发布。待外部补件时集中说明缺口及影响，不自动唤起另一窗口或催办。

同一生成对话换角色仍是自检；一个审阅对话检查四维，不宣称多个独立审计员。工具失败或材料不足如实记录，不假造完成。

成篇报告或复杂文稿的阶段记录按 [阶段监控](references/checkpoints.md) 检查；缺历史记录不要求补造。结论标签或建议变化时，复核对应依据、限定及整份纯净稿，不能仅核销旧问题。

## 按任务选择参考

下表按需读取，不遍历全部文件；本对话已读且未变化的规则不重复加载。共同参考的起草要求用于验收，不把本对话变成生成侧。原始文件和所用证据不因精简加载而省略。

| 需要 | 读取 |
| --- | --- |
| 营商环境指南、国别投资摘要、海外子公司运营指南或经商常见问题解答 | [overseas-investment-guide.md](references/overseas-investment-guide.md)，检查所选结构、办理条件与持续义务 |
| 法律检索报告或具体权利义务 | [legal-research-report.md](references/legal-research-report.md) |
| 律师函、催告函或对外争议沟通 | [lawyer-letters.md](references/lawyer-letters.md)，需要时检查 [disputes.md](references/disputes.md) 中的行动条件 |
| 指定样本或读者／文种不明确 | [intake-and-samples.md](references/intake-and-samples.md) |
| 合同、尽调合规、争议证据或客户服务成果 | 分别选 [contract-review.md](references/contract-review.md)、[nonlitigation.md](references/nonlitigation.md)、[disputes.md](references/disputes.md)、[client-service.md](references/client-service.md) |
| 法源工具选型／覆盖不明 | [mcp-routing.md](references/mcp-routing.md) |
| 方法不足，需要独立找专业参考 | [reference-learning.md](references/reference-learning.md)，沿用八家律所及办公室偏好 |
| 补充材料或专家偏好发生变化 | [supplemental-materials.md](references/supplemental-materials.md)／[expert-feedback.md](references/expert-feedback.md) |
| 译文／仅本地处理；实质法律交付的文末说明 | [translation-privacy.md](references/translation-privacy.md)；[delivery-notices.md](references/delivery-notices.md) |
| 引用记录缺项或字段含义不明 | [data-and-tools.md](references/data-and-tools.md) |
