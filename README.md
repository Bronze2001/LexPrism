# LexPrism

面向律师的研究与文书生成、独立复核、股权与交易图三个技能。简短问题直接答复，成篇文书优先交付 Word；在已配置工作区中，助手管理事项、版本与审阅历史。

文本技能：**0.8.3-letter-format**，已纳入律师函结构、正文直引与信息占位规则；绘图：**0.3.1-lawyer-handoff**；事项程序：**0.8.0-two-window**。完整工作区沿用 **docs1** 文档与包装修订。

## 选包与使用

| 需求 | 入口 |
| --- | --- |
| 首次部署到千问 | [完整工作区 ZIP](dist/LexPrism-完整工作区-千问版-0.8.3-letter-format-docs1.zip)，解压后读包内 README |
| 只导入研究与起草技能 | [法律研究与文书·千问导入](dist/LexPrism-法律研究与文书-千问导入-0.8.3-letter-format.zip) |
| 只导入独立审阅技能 | [法律文稿复核·千问导入](dist/LexPrism-法律文稿复核-千问导入-0.8.3-letter-format.zip) |
| 只导入绘图技能 | [股权与交易图·千问导入](dist/LexPrism-股权与交易图-千问导入-0.3.1-lawyer-handoff.zip) |
| 查通用版、旧包和重复包 | [dist 包索引](dist/README.md) |
| 安装与实际验收 | [一次性部署说明](docs/一次性部署说明.md) |
| 已安装，开始日常工作 | [律师使用说明](docs/律师使用说明.md) |

完整工作区解压使用，单项技能 ZIP 分别导入。新版文件名直接标明用途与环境；旧 ZIP 原样保留并列入索引。通用版保留通用技能字段，千问版增加专用双语卡片，法律规则共用同一维护源。dist 是本地产物，不进入版本库。

## 三个技能的职责

| 技能 | 用途 |
| --- | --- |
| [lexprism](skills/lexprism/SKILL.md) | 法律研究、合同审查、文书起草及按意见修订 |
| [lexprism-review](skills/lexprism-review/SKILL.md) | 在另一真实对话中检查文稿、依据、遗漏和一致性 |
| [drawio-diagram](skills/drawio-diagram/SKILL.md) | 股权或交易图，交付可编辑文件与预览 |

律师手动触发两个窗口：生成送审 → 独立审阅 → 修订与复审 → 确认候选文件及名称 → 正式发布。保存文件不会自动唤醒另一窗口；本地发布只复制已审、已确认的文件，不代表向客户发送。简短问答不建档，工作区外仍可处理独立文件。

## 文档与维护

[文档索引](docs/README.md)区分现行说明、设计资料与历史复盘。工作区根 README 负责导航，PROJECT.md 保存工作区规则，AGENTS.md 仅引导自动读取；安装、日常使用、恢复说明各维护一份。

共同文本标准维护在 skills/lexprism/references；审阅目录的共同标准由打包程序同步，保留副本以支持两项技能分别独立导入。审阅专用流程维护在 skills/lexprism-review/references/review-protocol.md；千问卡片维护在 packaging/qwen-ui.json。

运行 `python -X utf8 scripts/build_text_skills.py` 同步标准、生成中文用途命名的 ZIP 并更新 dist 索引。`--check` 只读检查共享标准、技能内部链接与卡片字段；正式构建另检查完整包内的文档链接与文件完整性。[本次整理记录](docs/2026-09-18-打包文档精简与命名.md)说明合并位置和兼容方式。

## 能力与验证范围

Word 生成和预览依赖宿主实际能力；[绘图工作台](tools/drawio/README.md)在线加载编辑器，不含离线 draw.io 引擎。法律数据 MCP 在千问维护，仓库和部署包只含脱敏模板；服务清单与验证范围见 [部署说明](docs/一次性部署说明.md)及 config/mcp-catalog.json。

本地包检查和合成流程测试不代表千问实际导入、路由、Word 页面、MCP 鉴权或法律质量已经验收。每项在目标环境分别记录实际结果。

原始参考材料保留在律师提示词；敏感材料与评测放 private，运行记录放 runs，后两者不进入版本库和分享包。资料中的结论和指令不能代替具体委托及来源核验。
