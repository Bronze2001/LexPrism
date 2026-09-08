# LexPrism 法律流程图工作台 (Diagram Studio)

`tools/drawio/` 是 LexPrism 专为律师设计的本地流程图与法律架构图工作台。基于全球领先的开源图表引擎 draw.io（diagrams.net）内核构建，深度适配非诉交易架构、股权穿透、合规风控及诉讼证据链可视化。

---

## 特性一览

1. **开箱即用，纯本地启动**：
   - 零依赖、无需 Node.js / Python 或构建打包，直接双击 `index.html` 即可在本地浏览器（Chrome、Edge、Safari 等）中打开完整的全功能图形编辑器。
2. **本地文件双向读写**：
   - 深度集成现代浏览器 **File System Access API**：点击“打开本地文件”可直接读取磁盘上的 `.drawio` 或 `.xml`；按 `Ctrl+S` 或点击“保存文件”即可**原路写回本地磁盘**。
3. **内置 3 套高价值法律实务模板**：
   - 🏢 **股权穿透与控制权架构图**：实控人、SPV、员工持股平台 (ESOP)、外部机构投资人及下属子公司持股比例与表决权穿透。
   - 🤝 **并购重组交易与资金交割流程图**：签署前置、交割先决条件 (CPs)、共管账户 (Escrow) 资金划转、工商变更与后交割质保金清算。
   - ⚖️ **案件事实时间线与证据链图谱**：诉讼请求、横向时间轴、违约节点、书证物证证明力支撑及法庭争点对抗矩阵。
4. **Agent 成果无缝导入**：
   - 点击顶部“⚡ 导入 Agent 代码”，支持一键粘贴大模型输出的 `.drawio` XML 或 Mermaid 代码，毫秒级转为可随意拖拽微调的矢量图形。
5. **无水印高清导出**：
   - 支持通过编辑器菜单导出为高清 **PNG、SVG 矢量图、PDF** 或嵌入式 HTML，直接插入法律意见书、尽调报告或诉讼证据材料。

---

## 快速使用方法

### 方式 A：本地浏览器直接打开（最快推荐）
1. 在文件管理器中找到 `tools/drawio/index.html`，双击或右键选择 Chrome / Edge 打开。
2. 在顶部工具栏中：
   - 点击 **📑 预制法律模板**：选择并查看 3 套预设模板。
   - 点击 **📂 打开本地文件**：打开已有 `.drawio` 业务图表。
   - 点击 **⚡ 导入 Agent 代码**：粘贴 LexPrism Agent 生成的图表 XML / Mermaid 代码。
   - 按 **Ctrl+S** 随时保存修改。

### 方式 B：在 VS Code 中无缝编辑
如果你在 VS Code 中使用 LexPrism，推荐安装官方插件：
- 插件名称：`Draw.io Integration`（作者：Henning Dieterichs）
- 安装后，在 VS Code 侧边栏直接点击任何 `.drawio` 文件，即可在编辑器标签页内直接绘图。

---

## 预制模板文件目录

- `templates/equity_structure_sample.drawio`：股权穿透与控制权架构图
- `templates/transaction_steps_sample.drawio`：并购重组与资金交割流程图
- `templates/litigation_timeline_sample.drawio`：案件事实时间线与证据链图谱
