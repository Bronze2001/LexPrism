# LexPrism 两窗口工作区

律师在生成、审阅两个对话中提供需求和材料，查看成果并确认交付；文件、版本和意见由助手管理。

| 你要做什么 | 从这里开始 |
| --- | --- |
| 第一次安装或升级 | [一次性部署说明](docs/一次性部署说明.md) |
| 已安装，开始日常工作 | [律师使用说明](docs/律师使用说明.md) |
| 在千问分别导入三个技能 | [技能导入清单](skill-imports/README.md) |
| 让助手读取项目规则 | [PROJECT.md](PROJECT.md)（AGENTS.md 自动引导至此） |
| 处理备份、失败恢复或旧事项升级 | [项目协作操作说明](docs/项目协作操作说明.md) |
| 编辑股权或交易图 | [绘图工作台](tools/drawio/README.md) |

完整工作区 ZIP 解压后使用；不要把它整体作为单个技能导入。三个技能导入包位于 skill-imports，技能规则的可读副本位于 skills。组件版本见 [版本信息](版本信息.md)。

## 目录用途

| 目录或文件 | 用途 |
| --- | --- |
| docs | 安装、日常使用、运维说明；流程图放在其下的 workflow-design-2026-09-17 |
| skills | 生成、审阅、绘图规则；两个文本技能须能分别独立导入 |
| skill-imports | 千问专用的三个独立导入 ZIP |
| config | MCP 脱敏模板与服务目录；真实凭据在千问私有配置中填写 |
| scripts / templates | 助手使用的程序与事项入口模板 |
| tools/drawio / evals/templates | 绘图工作台、示例及图表计划模板 |
| deployment-manifest.json | 出包文件的完整性清单，供部署检查使用 |
| matters / .lexprism / output | 使用后生成：事项档案 / 绑定与输出记录 / 正式交付文件 |

备份须同时保留 matters、.lexprism 和 output。升级规则与程序时保留这些业务目录和私人配置。

包内不含客户材料、真实凭据或 Python、Word、离线 draw.io 引擎。包检查通过只代表本地结构与完整性合格；千问导入、Word 页面、连接器和法律质量需在实际环境验收。
