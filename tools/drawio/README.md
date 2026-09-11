# LexPrism 法律流程图工作台 (Diagram Studio)

`tools/drawio/` 是 LexPrism 专为律师设计的本地流程图与法律架构图工作台。基于全球领先的开源图表引擎 draw.io（diagrams.net）内核构建，深度适配非诉交易架构、股权穿透、合规风控及诉讼证据链可视化。

---

## 特性一览

1. **开箱即用，纯本地启动**：
   - 零依赖、无需 Node.js / Python 或构建打包，直接双击 `index.html` 即可在本地浏览器（Chrome、Edge、Safari 等）中打开完整的全功能图形编辑器。
2. **本地文件双向读写**：
   - 深度集成现代浏览器 **File System Access API**：点击“打开本地文件”可直接读取磁盘上的 `.drawio` 或 `.xml`；按 `Ctrl+S` 或点击“保存文件”即可**原路写回本地磁盘**。
3. **内置 2 套高价值核心实务模板（完全可编辑）**：
   - 🏢 **股权结构图 (穿透与控制权)**：实控人、SPV、员工持股平台 (ESOP)、外部机构投资人及下属子公司持股比例与表决权穿透。
   - 🤝 **交易结构图 (步骤与交割流程)**：签署前置、交割先决条件 (CPs)、共管账户 (Escrow) 资金划转、工商变更与后交割质保金清算。
4. **Agent 成果无缝导入并即时编辑**：
   - 点击顶部“⚡ 导入 Agent 代码”，支持一键粘贴大模型输出的 `.drawio` XML 或 Mermaid 代码，毫秒级转为可随意拖拽微调的矢量图形，按 `Ctrl+S` 原路保存。
5. **无水印高清导出**：
   - 支持通过编辑器菜单导出为高清 **PNG、SVG 矢量图、PDF** 或嵌入式 HTML，直接插入法律意见书或交易备忘录。

---

## 快速使用与编辑方法

### 方式 A：本地工作台直接打开与编辑（最快推荐）
1. 在文件管理器中找到 `tools/drawio/index.html`，双击或右键选择 Chrome / Edge 打开。
2. 在顶部工具栏中：
   - 点击 **📑 预制法律模板**：一键载入【股权结构图】或【交易结构图】并直接在画布中拖拽编辑。
   - 点击 **📂 打开本地文件**：打开磁盘上的 `.drawio` 文件直接编辑。
   - 点击 **⚡ 导入 Agent 代码**：粘贴 LexPrism Agent 生成的图表 XML 代码立即生成可编辑图表。
   - 按 **Ctrl+S** 随时将修改保存回本地文件。

### 方式 B：在 VS Code 中所见即所得编辑
如果使用 VS Code：
- 安装插件：`Draw.io Integration`（作者：Henning Dieterichs）；
- 直接点击任何 `.drawio` 文件即可在 VS Code 标签页内自由编辑节点与文字。

---

## 预制核心模板文件目录

- `templates/equity_structure_sample.drawio`：股权结构图 (穿透与控制权)
- `templates/transaction_steps_sample.drawio`：交易结构图 (步骤与交割流向)

---

## 法律图表质量控制与自动化核验 (Render Check)

对标严格的学术与工程质量控制标准，本工具链配套完整的质控闭环：

1. **严格四级图表分类 (Four-Tier Classification)**：
   - **Type 1 (Diagnostic)**：办案内部备忘图，严禁交付给客户。
   - **Type 2 (Comparison)**：交易/诉讼策略比选图。
   - **Type 3 (Core Delivery ★)**：正式交付核心图（股权穿透/交割流向/违约时间线），**必须经办案律师在 [G4 👤] 显式签署确认**。
   - **Type 4 (Appendix)**：附录证据展开图。
2. **自动化静态合规核验**：
   在正式交付图表前，可运行项目内置的核验脚本进行自动化扫描：
   ```bash
   python scripts/verify_diagram.py [path_to_diagram.drawio]
   ```
   脚本将自动核对：
   - XML 语法与结构完整性；
   - 法律基准日 (As-Of Date) 与图表标题声明；
   - 经办律师核查备忘卡片；
   - 律所标准商务色盘白名单（深海蓝 `#1B365D`、合规绿 `#2E7D32` 等）。

