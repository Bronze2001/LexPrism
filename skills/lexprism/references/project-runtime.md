# 项目程序调用与记录

供 Agent 按需读取，律师不用操作。使用完整工作区的 scripts/document_workflow.py（Python 3.10+，标准库）；先查看 --help。这里的参数是 0.8.0 运行程序的实际接口。W 为授权工作区绝对路径，M 为已选事项目录；所有相对文件路径以相应工作区、事项或副本为界。

## 定位与送审

- 先定位已有事项；需要时用 `--root W discover` 只查登记元数据，或不带 `--create`／`--new` 的 `bind` 沿用已有绑定。确认需要创建后，先按 [project-collaboration.md](project-collaboration.md) 提供可选命名机会，再调用创建动作；不能用会立即创建的命令代替前置判断。
- `--root W bind --actor 实际窗口标识 --role generation --create`：沿用绑定或匹配唯一事项；无事项才创建。明确新业务事项时改用 `--new`。用户已提供名称时带 `--project-name` 记录初始显示名；未命名或只有空白时省略，程序沿用 `matters/m-<自动编号>/`，不另造占位项目名。命名交互由 Agent 完成，程序不等待终端输入；初始名称不等于正式发布确认。
- `--root W bind --actor 实际审阅窗口标识 --role review --matter matters/事项目录`：绑定相同事项。明确项目名称可用 `--project-name` 定位。多候选返回 selection_required，不猜选。
- `--root M status`：校验历史、重建 WORK；`discover` 仅查元数据。
- `--root M checkout --actor 实际生成窗口标识`：使用返回的 files 路径。恢复旧内容可带 `--from-version v0001`，仍产生新副本。
- 在 files 中写 BRIEF.md、RESPONSE.md、evidence、所有成果和 deliverables.json；送审前固定候选 Word。
- `--root M submit --draft 返回编号 --deliverables deliverables.json --execution-ref 实际生成对话或消息定位`：封存全部文件，不是 Git 或上传。

成果清单示例仅定义结构，替换为实际文件和用途：

```json
{
  "primary": "letter",
  "deliverables": [
    {"id":"letter","title":"律师函","purpose":"external","verification":"律师函核验稿.md","clean":"律师函.docx","page_check_required":true,"related":["memo"]},
    {"id":"memo","title":"内部备忘录","purpose":"internal","verification":"备忘录核验稿.md","clean":"备忘录.docx","page_check_required":true,"related":[]}
  ]
}
```

每份成果的两个视图是不同文件；候选交付文件就是 clean。相关成果分别登记，不能把不同用途成果拼成一个双视图。程序校验 Word 容器等结构，不证明语义、原生脚注或页面合格。实际任务要求页面检查时 page_check_required 必须为 true。

## 独立审阅

`--root M start-review --actor 实际审阅窗口标识` 返回所审版本、意见目录和 result.json 模板。读取完整成果包，在本轮目录写 REVIEW.md 并按实际执行填 result.json：

- 沿用生成的 review_protocol。四个 checks 分别记录真实判定、依据和限制。
- scope 用 full 或 limited，reviewed_deliverables 写实际检查的成果编号。完整审阅须覆盖全部成果。
- execution_ref 写本次真实审阅记录。independence.status 只有确属独立对话才写 separate_conversation；generation_ref 对应已登记生成记录，review_ref 对应本次 execution_ref。
- pages 写 PASS、PENDING 或有理由的 NOT_REQUIRED，以及实际页面检查依据。必要页面未查不能记通过。
- findings 保留稳定编号；正文、证据等锚点须位于本版实际文件中。继承阻断问题必须明确处理，确认解决、撤回或降级须附 resolution 的真实理由及证据。
- unperformed_checks 不隐藏必要漏检。生成侧回应不代替复审。supersedes 仅用于有理由替代同版旧意见。

`--root M finish-review --review 返回编号` 封存实际完整意见。`cancel-review --review 编号 --reason 真实原因` 仅取消确已停止的未完成审阅，不能借此绕开实质问题。

## 正式交付

1. `--root M prepare-release --workspace W --project-name 项目名 --file-name 文件名`：完整通过后预检并返回候选链接及目标。名称已有记录可省略；默认选 primary。多个附件用重复的 `--deliverable 编号`，文件名按各成果 title 生成。程序自动加版本和原格式扩展名。
2. 把确切候选、名称和范围向律师确认。真实确认保存为事项内 JSON：`{"decision":"approve","text":"律师实际原话","source_ref":"实际用户消息或可回查来源"}`。示例文字不能当作真实批准。
3. `--root M confirm-release --release 返回发布编号 --confirmation-file 确认输入.json`：绑定完整请求和原始确认。程序不自动验证消息真实性，Agent 必须实际收到并核对原话。
4. `--root M publish --release 发布编号`：再核验并复制，成功返回正式路径。失败或登记未完成返回非零退出状态，不能称已交付；修复原因后用同一编号重试。
5. 未发布前撤回用 `revoke-release --release 编号 --reason 真实原因`。已发布文件不覆盖；实质修改新建副本，重新送审、审阅和确认。

版本、有效审阅集合或交付目标改变需重新准备请求和确认。已有成功发布请求重复执行只返回原文件；若原文件丢失或被改，不静默重建。当前版本与最近交付版本分别记录。已写入但登记失败时按发布归属及指纹恢复，不重复生成。

旧单 pair 事项可读取并继续，正式发布前需提交带成果清单的新版本并重新审阅；不补造历史字段或改旧 manifest。状态 schema_version=1 保持兼容，新送审包使用 submission_protocol=2、独立审阅使用 review_protocol=3。
