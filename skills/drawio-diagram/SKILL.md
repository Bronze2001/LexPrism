---
name: drawio-diagram
description: 专注于【股权结构图】（境内穿透、跨境出海ODI、协议控制VIE与动态并购变动）与【交易结构图】（步骤与资金交割流向）的高保真生成与可编辑交付。基于红圈所涉外标准设计，支持典雅藏青涉外风与清爽冰蓝现代并购风，具备跨境法域分隔、总线式汇流与确定性法律数据闭环，输出完全兼容本地 Draw.io 工作台（tools/drawio/index.html）及 VS Code 的原生可编辑 .drawio 矢量图。
metadata:
  version: 0.3.0-crossborder-modern
---

# Draw.io 股权与交易流程图生成器 (Equity & Transaction Diagrams)

本技能**专精于商事非诉与涉外投资核心法律图表的高保真生成与可编辑交付**：
1. **🏢 股权结构图 (Equity Structure)**：
   - **跨境出海与协议控制 (Cross-Border ODI & VIE)**：支持横向点状虚线切分境内（中国 China）与境外法域（印尼 Indonesia 等），支持直接持股（100%）与协议控制（控制 Control）双轨制及当地自然人接入；
   - **并购受让与动态股权变动 (M&A Acquisition & Transition)**：支持横向受让动作指向虚线（`Acquire 30% of the shares`）与线上动态跃迁（`0 → 30%`、`90% → 60%`），严格闭环 100%；
   - **境内穿透与实控人认定 (Penetration & Ultimate Controller)**：实控人、控股 SPV、员工持股平台 (ESOP) 与下属子公司多层总线汇流穿透。
2. **🤝 交易结构图 (Transaction Structure)**：
   - 并购重组、先决条件 (CPs)、共管账户 (Escrow) 分期划付、工商变更与交割流程泳道图。

所有生成的图表均具备**确定性法律数据、大圆角现代胶囊卡片（arcSize 16~22）、100% 节点几何对齐，并可直接在本地 Draw.io 中自由拖拽、修改文字与实时保存**。

---

## 两大顶级实务视觉风格 (Two Prestigious Visual Styles)

| 视觉风格 | 适用实务场景 | 视觉设计与色盘系统 |
| :--- | :--- | :--- |
| **🌟 风格 A：典雅藏青 · 涉外跨境风** | 境外直接投资 (ODI)、外资准入限制出海设厂、红筹/VIE 架构、中外合资与协议控制 | 全图统一高雅冷调深海普鲁士藏青色 (`#163854`)，纯白/浅灰中英双语文字；点状跨境法域分隔线 (`#4A5568`)；当地自然人深石青卡片 (`#1D5174`)；深灰蓝连线 (`#204868`)。 |
| **💎 风格 B：清爽冰蓝 · 现代并购风** | 上市公司协议受让 (SPA)、引入战略投资人、增资扩股与交割前后股权变动 | 出资层采用清透温润的冰蓝胶囊卡片 (`#DDF1FC`)，深藏青文本；核心标的采用高对比度海洋蔚蓝大卡片 (`#0284C7`) 纯白大字；横向受让虚线 + 动态比例跃迁 (`0 → 30%`)。 |

---

## 核心交付与可编辑链路 (Editable Workflow)

为确保用户“生成即刻可自由拖拽微调”，Agent 在交付图表时，遵循以下标准交互：

### 1. 成果输出形式
- **直接保存为本地 `.drawio` 文件**：存放在当前项目成果目录（如 `drawings/cross_border_equity.drawio` 或 `drawings/equity_transition.drawio`）；
- **对话中输出原生 `<mxfile>...</mxfile>` XML 代码块**：用户可一键复制。

### 2. 用户可编辑方式 (Three Editing Options)
- **方式 A（本地工作台一键编辑 - 推荐）**：
  双击打开项目内置的 `tools/drawio/index.html`，点击顶部 **【⚡ 导入 Agent 代码】**，粘贴 XML 代码，图表立即呈现在画布上；用户可自由拖拽调整主体位置、双击修改持股比例或增减法域，按 `Ctrl+S` 原路写回本地文件。
- **方式 B（VS Code 内嵌编辑）**：
  在 VS Code 中安装 `Draw.io Integration` 插件，直接点击生成的 `.drawio` 文件即可在代码编辑器内所见即所得绘图。
- **方式 C（官方客户端 / 网页版）**：
  在桌面版 Draw.io 或 [app.diagrams.net](https://app.diagrams.net) 直接打开编辑。

---

## 图表生成与质量控制规程 (Generation Protocol)

1. **三问前置原则**：
   - **What Claim?**（如：中国母公司通过协议控制印尼工程公司，张某某转让 30% 股权后仍保留 60% 绝对控股权）；
   - **Which Source?**（如：商务部 ODI 备案通知书、股份购买协议第 2.1 条、印尼投资部 BKPM 批复）；
   - **Where in Delivery?**（如：法律尽调报告第 3.2 节、重组法律意见书正文）。
2. **法定结构要素（必须包含）**：
   - **主标题与基准日横幅**：顶部包含项目性质及 `基准日：YYYY年M月D日 | 适用法：PRC Law / 境外法`；
   - **【经办律师核查备忘卡片】**：底端锚定淡黄便利贴卡片 (`fillColor=#FEFCBF;strokeColor=#D69E2E;dashed=1;`)，阐明控制权定性、数学闭环与境外合规要点。
3. **几何与走线铁律**：
   - **总线汇流 (Tee Bus)**：多股东引线向下汇流至单根平直总线，严禁多条斜向折线乱穿；
   - **跨境虚线分界**：涉及跨国主体时，使用点状虚线切分法域；
   - **数学闭环**：静态直接持股之和必须为 100.00%；动态变动终态之和必须为 100.00%。

---

## 参考规范索引 (References)

- `references/diagram-patterns.md`：包含藏青跨境出海、冰蓝并购受让、经典多层穿透等模式的原生 XML 范式。
- `references/color-systems.md`：典雅藏青、清爽冰蓝与经典律所商务色盘及十六进制白名单。
- `references/layout-guide.md`：跨境法域分隔线、总线汇流走线与大圆角胶囊卡片几何布局指南。
- `references/render-check.md`：渲染核验清单与自动化门禁脚本核验规程。
