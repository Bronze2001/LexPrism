# LexPrism MCP 接入与部署说明

更新日期：2026-09-11。本文依据千问办公在 2026-09-11 00:24 导出的本机 MCP 配置整理，用于维护、迁移和后续一键式部署设计。

## 1. 安全边界

- 本文、Git 仓库、导入包、日志和截图都**不得**包含真实 Token、API Key、Cookie 或 OAuth 回调信息。
- 北大法宝使用一个共享 Bearer Token；下文统一写作 `<YOUR_PKULAW_BEARER_TOKEN>`。只可在本机千问办公的私有配置中替换该占位符。
- 原始导出文件包含明文 Token，只能保存在用户本机的受控目录，不能复制进仓库或发送给第三方。建议在完成本轮整理后于北大法宝控制台轮换 Token。
- 无认证的公共 MCP 也不代表其输出可直接作为法律结论；仍须记录原文链接、版本／生效时间、定位和取得时间。

## 2. 当前接入状态

当前共有 15 个服务：14 个远程 HTTP 服务、1 个本地 stdio 服务。`已配置`表示已出现在千问办公导出的配置中；`已正常使用`仅用于用户已经确认正常使用的北大法宝。其余服务仍应通过真实任务验证检索、全文、版本与错误处理。

| 组别 | 服务 | 传输 | 当前状态 | 主要范围 |
| --- | --- | --- | --- | --- |
| 中国内地 | 北大法宝 9 项服务 | 远程 `streamableHttp`，Bearer Token | **已配置；北大法宝已正常使用** | 法条、法规、案例、识别、引文和文书关联。 |
| 欧盟 | `eur-lex-mcp-server` | 本地 `stdio`，`npx` | 已配置 | CELLAR / EUR-Lex 检索；依赖 Node.js 和首次联网下载包。 |
| 美国联邦规章 | `federal-regulations-mcp-server` | 远程 `streamable-http` | 已配置 | eCFR 与 Federal Register；社区封装，需核验上游法源。 |
| 英国 | `lex-uk-legislation` | 远程 HTTP（宿主自动识别） | 已配置 | 英国立法与相关检索；重大结论回到 legislation.gov.uk 核验。 |
| 美国判例 | `pipeworx-us-case-law` | 远程 `streamable-http` | 已配置 | CourtListener 数据的美国判例、案卷和 RECAP 资料；第三方网关。 |
| 综合海外法律 | `pipeworx-legal` | 远程 `streamable-http` | 已配置 | 美国判例、US Code、eCFR、Federal Register、联邦／州立法及部分 UK／EU 数据；第三方网关。 |
| 欧盟数据合规 | `overview-legal` | 远程 `streamable-http` | 已配置 | GDPR、AI Act、DSA、NIS2、CJEU／部分国家判例、EDPB 与执法决定。 |

### 北大法宝九项服务

| 名称 | 端点 | 用途 |
| --- | --- | --- |
| `pkulaw-law-search` | `https://apim-gateway.pkulaw.com/mcp-law-search-service` | 法条语义检索 |
| `pkulaw-law-keyword` | `https://apim-gateway.pkulaw.com/mcp-law` | 法规关键词检索 |
| `pkulaw-case-semantic-search` | `https://apim-gateway.pkulaw.com/mcp-case-search-service` | 案例语义检索 |
| `pkulaw-case-keyword` | `https://apim-gateway.pkulaw.com/mcp-case` | 案例关键词检索 |
| `pkulaw-law-item-keyword` | `https://apim-gateway.pkulaw.com/mcp-fatiao` | 法条条项内容 |
| `pkulaw-law-recognition` | `https://apim-gateway.pkulaw.com/law_recognition` | 法规识别 |
| `pkulaw-case-number-recognition` | `https://apim-gateway.pkulaw.com/case_number_recognition` | 案号识别 |
| `pkulaw-citation-validator` | `https://apim-gateway.pkulaw.com/pku_citation_validator` | 引用校验 |
| `pkulaw-doc-link` | `https://apim-gateway.pkulaw.com/add-doc-link` | 文书关联链接 |

## 3. 脱敏配置清单

下列 JSON 可用作迁移或一键部署模板。粘贴前，仅在目标机器的私有配置中把 `<YOUR_PKULAW_BEARER_TOKEN>` 替换为有效 Token；不要把替换后的文件保存到本仓库。

```json
{
  "mcpServers": {
    "pkulaw-law-search": {"type": "streamableHttp", "url": "https://apim-gateway.pkulaw.com/mcp-law-search-service", "headers": {"Authorization": "Bearer <YOUR_PKULAW_BEARER_TOKEN>"}},
    "pkulaw-law-keyword": {"type": "streamableHttp", "url": "https://apim-gateway.pkulaw.com/mcp-law", "headers": {"Authorization": "Bearer <YOUR_PKULAW_BEARER_TOKEN>"}},
    "pkulaw-case-semantic-search": {"type": "streamableHttp", "url": "https://apim-gateway.pkulaw.com/mcp-case-search-service", "headers": {"Authorization": "Bearer <YOUR_PKULAW_BEARER_TOKEN>"}},
    "pkulaw-case-keyword": {"type": "streamableHttp", "url": "https://apim-gateway.pkulaw.com/mcp-case", "headers": {"Authorization": "Bearer <YOUR_PKULAW_BEARER_TOKEN>"}},
    "pkulaw-law-item-keyword": {"type": "streamableHttp", "url": "https://apim-gateway.pkulaw.com/mcp-fatiao", "headers": {"Authorization": "Bearer <YOUR_PKULAW_BEARER_TOKEN>"}},
    "pkulaw-law-recognition": {"type": "streamableHttp", "url": "https://apim-gateway.pkulaw.com/law_recognition", "headers": {"Authorization": "Bearer <YOUR_PKULAW_BEARER_TOKEN>"}},
    "pkulaw-case-number-recognition": {"type": "streamableHttp", "url": "https://apim-gateway.pkulaw.com/case_number_recognition", "headers": {"Authorization": "Bearer <YOUR_PKULAW_BEARER_TOKEN>"}},
    "pkulaw-citation-validator": {"type": "streamableHttp", "url": "https://apim-gateway.pkulaw.com/pku_citation_validator", "headers": {"Authorization": "Bearer <YOUR_PKULAW_BEARER_TOKEN>"}},
    "pkulaw-doc-link": {"type": "streamableHttp", "url": "https://apim-gateway.pkulaw.com/add-doc-link", "headers": {"Authorization": "Bearer <YOUR_PKULAW_BEARER_TOKEN>"}},
    "eur-lex-mcp-server": {"type": "stdio", "command": "npx", "args": ["-y", "@cyanheads/eur-lex-mcp-server@latest"], "env": {"MCP_TRANSPORT_TYPE": "stdio", "MCP_LOG_LEVEL": "info"}},
    "federal-regulations-mcp-server": {"type": "streamable-http", "url": "https://federal-regulations.caseyjhand.com/mcp"},
    "lex-uk-legislation": {"url": "https://lex.lab.i.ai.gov.uk/mcp"},
    "pipeworx-us-case-law": {"type": "streamable-http", "url": "https://gateway.pipeworx.io/court-listener/mcp"},
    "pipeworx-legal": {"type": "streamable-http", "url": "https://gateway.pipeworx.io/mcp?vertical=legal"},
    "overview-legal": {"type": "streamable-http", "url": "https://overview.legal/api/mcp"}
  }
}
```

## 4. 部署与迁移步骤

### 4.1 前置条件

1. 安装并登录千问办公，确认可进入“扩展／连接器”或该客户端对应的 MCP 管理页面。
2. 对需要访问北大法宝的机器，在私有安全位置取得有效 Token；不要经聊天、邮件或 Git 传输。
3. 如启用 `eur-lex-mcp-server`，安装 Node.js，确保终端可运行 `npx`，且首次启动时网络可访问 npm。
4. 确认企业网络允许访问本清单中的 HTTPS 域名；本地 stdio 服务还需允许子进程启动。

### 4.2 导入顺序

1. 先配置北大法宝九项服务，私下填入 Token；重启或刷新连接器列表。
2. 添加五个无凭据远程服务：Federal Regulations、Lex UK Legislation、两个 Pipeworx 服务、overview.legal。
3. 最后添加 EUR-Lex 的 stdio 服务；首次 `npx` 下载失败时先检查 Node.js、npm 网络和企业代理。
4. 不在任何导出、截图或共享文件中保留填好 Token 的 JSON。

### 4.3 最小验收

逐一在新对话中运行，不把模型自然语言回答视作工具成功的证明：

| 服务 | 建议测试 | 通过标准 |
| --- | --- | --- |
| 北大法宝 | 查询一部已知现行法规并要求条款定位 | 输出实际来源、版本／效力字段与正文范围；列表不冒充全文。 |
| EUR-Lex | 查询已知 CELEX 或欧盟法规条文 | 返回可核验的 CELEX、语言和原文链接。 |
| Federal Regulations | 查询已知 CFR 条款 | 返回标题、章节、版本／生效信息和原始来源。 |
| Lex UK Legislation | 查询一部已知英国 Act 的条文 | 返回 legislation.gov.uk 可核验链接及版本信息。 |
| Pipeworx US Case Law | 查询 `Marbury v. Madison` | 返回判例、引文和 CourtListener 原文 URL；注意其案例快照可能滞后。 |
| Pipeworx Legal | 查询指定 US Code 条文或近期联邦立法 | 返回来源、条文定位和状态；不能将网关摘要替代原始文本。 |
| overview.legal | 查询 GDPR 第 6 条及 CJEU 判例 | 返回可回查条文、判例或执法决定链接。 |

每项完成后在 `runs/<case_id>/<run_id>/`（仅存获授权的资料）记录：配置版本、工具名、输入、原始结果、来源 URL、版本／时间点、失败信息和人工复核结论。

## 5. 使用与路由规则

- 仅涉及中国内地法：优先北大法宝，不因“海外”标签无差别调用其他库。
- 美国判例或 RECAP 案卷：优先 `pipeworx-us-case-law`；需要美国法规、US Code 或联邦／州立法时再用 `pipeworx-legal`。
- 美国联邦规章和规则制定：使用 Federal Regulations；对版本、联邦公报发布时间和生效信息逐项核验。
- 欧盟一般立法：先 EUR-Lex；数据保护、AI Act、DSA、NIS2 或 CJEU／执法关联问题可补用 overview.legal。
- 英国立法：用 Lex UK Legislation，并回查 legislation.gov.uk。
- “仅给定材料”“不联网”“不上传云”的任务：不得调用任何 MCP；按 Skill 的材料边界处理。

## 6. 当前未接入或已搁置的候选

| 数据源／候选 | 当前原因 | 何时再评估 |
| --- | --- | --- |
| CourtListener 官方 MCP | 官方 URL 可用，但当前邮箱登录失败，无法完成 OAuth／取得账号 Token | 登录恢复后；它仍是美国判例、案卷与引文服务的官方路线。 |
| Westlaw / Thomson Reuters CoCounsel Legal MCP | 需要现有 Thomson Reuters 账号、CoCounsel Legal 订阅和账户级启用；官方文档当前主要面向 Claude | 有律所订阅并取得书面 API／第三方模型使用许可后。 |
| GovInfo MCP | 需要 API.data.gov / GovInfo Key，尚未注册 | 出现美国联邦出版物、法案或官方文档的真实需求时。 |
| LexisNexis API / MCP | B 端订阅和组织审批路线，个人开发者不能直接取得完整内容权限 | 客户／律所有订阅并确认千问处理、缓存和引用许可时。 |
| vLex / Vincent | 可注册开发者门户，但内容和 Research 权限取决于另行订阅 | 有明确跨法域案件和可用订阅额度时。 |
| PoliticalData Canada | 需要 OAuth 或 API Key，当前仅覆盖加拿大联邦与安大略省 | 出现加拿大事项时。 |
| EULEX.AI | 需要免费账号 OAuth，且与当前 EUR-Lex 范围重叠 | 出现法国／克罗地亚事项，或确需其引文图谱时。 |
| Juriscraper | 是抓取库，不是可直接接入的 MCP；需要自行封装、处理浏览器驱动、限流和许可 | CourtListener／Pipeworx 无法覆盖某个具体美国法院且确有需求时。 |

## 7. 后续一键部署设计

未来若制作一键部署工具，应把“配置模板”与“私密凭据注入”分开：

1. 仓库只维护本文件中的脱敏模板与服务清单。
2. 安装程序从受控的本机输入、系统凭据管理器或企业密钥管理服务读取北大法宝 Token，绝不把它写进 Git、安装日志或生成的公开文档。
3. 程序检测 Node.js／`npx`，仅在用户选择启用 EUR-Lex 本地 stdio 服务时安装或启动相关依赖。
4. 先备份现有千问办公配置，再按服务名进行合并；不覆盖用户自有连接器。
5. 导入后逐项执行第 4.3 节的只读冒烟测试，输出脱敏结果与失败原因；只有通过测试的服务才标记为可用。
6. 远程服务 URL、认证方式、配额和服务状态可能变化，部署工具应版本化维护清单并支持禁用单项服务，而非假定 15 项永久可用。

## 8. 相关记录

- [海外法律数据接入评估](海外法律数据接入评估.md)：法源范围、候选方案、商业库与授权边界。
- [千问办公部署与联调](千问办公部署与联调.md)：Skill 导入、任务级联调和运行证据要求。
- [LexPrism Skill 入口](../skills/lexprism/SKILL.md)：研究、引用、材料和隐私处理规则。
