---
name: drawio-diagram
description: 专注于【股权结构图】（穿透与控制权）与【交易结构图】（步骤与交割流向）的生成与可编辑交付。基于前置规划契约、三问反装饰原则、律所商务色彩与几何规范，输出完全兼容本地 Draw.io 工作台（tools/drawio/index.html）及 VS Code 的原生可编辑 .drawio 矢量图。
metadata:
  version: 0.2.0-clean-focused
---

# Draw.io 股权与交易结构图生成器 (Equity & Transaction Diagrams)

本技能**专精于两大核心商事法律图表的生成与可编辑交付**：
1. **🏢 股权结构图 (Equity Structure)**：实控人认定、控股 SPV、员工持股平台 (ESOP)、外部机构投资人及下属子公司持股与表决权穿透图；
2. **🤝 交易结构图 (Transaction Structure)**：并购重组、协议收购 (SPA)、先决条件 (CPs)、共管账户 (Escrow) 分期划付、工商变更与交割流程图。

所有生成的图表均具备**确定性法律数据、100% 节点坐标规范，并可直接在本地 Draw.io 中自由拖拽、修改文字与实时保存**。

---

## 核心交付与可编辑链路 (Editable Workflow)

为确保用户“生成即刻可编辑”，Agent 在交付股权结构图或交易结构图时，遵循以下三级交互：

### 1. 成果输出形式
- **直接保存为本地 `.drawio` 文件**：存放在当前项目成果目录（如 `drawings/equity_structure.drawio` 或 `drawings/transaction_structure.drawio`）；
- **对话中输出原生 `<mxfile>...</mxfile>` XML 代码块**：用户可一键复制。

### 2. 用户可编辑方式 (Three Editing Options)
- **方式 A（本地工作台一键编辑 - 推荐）**：
  双击打开项目内置的 `tools/drawio/index.html`，点击顶部 **【⚡ 导入 Agent 代码】**，粘贴生成的 XML 代码，图表立即呈现在画布上；用户可自由拖拽调整主体位置、双击修改持股比例或步骤说明，按 `Ctrl+S` 原路写回本地文件。
- **方式 B（VS Code 内嵌编辑）**：
  在 VS Code 中安装 `Draw.io Integration` 插件，直接点击生成的 `.drawio` 文件即可在代码编辑器内所见即所得绘图。
- **方式 C（官方客户端 / 网页版）**：
  在桌面版 Draw.io 或 [app.diagrams.net](https://app.diagrams.net) 直接打开编辑。

---

## 图表生成与质量控制规程 (Generation Protocol)

1. **三问前置原则**：
   - **What Claim?**（如：张某某合计支配 66.00% 表决权；2026年9月完成首期交割款解付）；
   - **Which Source?**（如：工商内档切片、收购框架协议第 4.2 条）；
   - **Where in Delivery?**（如：法律意见书第 2.1 节）。
2. **法定结构要素（必须包含）**：
   - **主标题与基准日横幅**：顶部包含 `【LexPrism ...架构图/流向图】` 与 `基准日：YYYY年M月 | 适用法：PRC Law`；
   - **【经办律师核查备忘卡片】**：底端锚定淡黄便利贴卡片 (`fillColor=#FEFCBF;strokeColor=#D69E2E;dashed=1;`)，列明控制权结论或交割实质风险防范要点。
3. **视觉与色彩恒定原则**：
   - 核心标的主体 / 发行公司：深海蓝 (`#1B365D`)，白色加粗文字；
   - 控股股东 / 实控人 SPV：专业深蓝 (`#2B6CB0`)；
   - 普通子公司 / 关联履约主体：素雅浅灰白 (`#EDF2F7`)，深灰文字；
   - 员工持股平台 (ESOP) / 资金通道：商务橙 (`#ED8936`)；
   - 先决条件达成 / 关键闭环：合规绿 (`#2E7D32`)；
   - 违约风险 / 重大不利影响 (MAC)：警示红 (`#E53E3E`)。
4. **数学闭环与事实自洽**：
   - 股权图上的直接股东持股比例之和必须严格闭环为 100.00%；
   - 交易步骤图必须标明清晰的步骤序号（如“步骤 1”、“步骤 2”）。

---

## 参考规范索引 (References)

- `references/diagram-patterns.md`：股权结构图与交易结构图的原生 XML 范式与常用节点坐标。
- `references/color-systems.md`：律所标准商务色盘与白名单。
- `references/layout-guide.md`：树状层级穿透与横向泳道几何布局指南。
- `references/render-check.md`：可读性、防截断与数据闭环渲染核验清单。
