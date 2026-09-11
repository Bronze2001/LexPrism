# Draw.io 法律图表排版与几何布局指南 (Layout Guide)

## 三层法律论证模型 (Three-Level Legal Layout Model)

与严肃学术图表类似，一份能够进入庭审或并购谈判交付物的法律图表，排版应体现自上而下或自左而右的逻辑推进：

| 论证层级 | 法律问题 | 视觉呈现角色 | Draw.io 典型实现组件 |
| :--- | :--- | :--- | :--- |
| **1. 概览层 (Overview)** | 案件/交易的全貌与适用法域基准？ | 建立法律前提与全貌框架 | 顶部大标题横幅、基准日声明、阶段泳道 (Pool/Lane) |
| **2. 实质层 (Main Evidence)** | 核心权利义务、控制权或事实脉络？ | 承载核心法律主张与证明链 | 树状股权层级、正交交割流向线、带证据编号的时间节点 |
| **3. 校验层 (Validation / Caveats)** | 存在哪些法律风险、假设或未决缺口？ | 揭示实质限定前提与责任边界 | 底部/右侧锚定的【经办律师核查备忘卡片】 |

---

## 几何尺寸与节点规范 (Geometry Standards)

### 1. 节点尺寸与间距 (Node Dimensions & Spacing)

- **核心主体节点 (Core Entity)**：
  - 推荐尺寸：宽 `180px` ~ `220px`，高 `50px` ~ `65px`；
  - 内部留白：文字与边框四周至少保留 `8px` 间距，严禁文字挤压边框；
  - 字号规范：主体中文全称 `13px` ~ `14px` 加粗，英文/简称 `10px` ~ `11px`。
- **次级主体 / 子公司节点**：
  - 推荐尺寸：宽 `160px` ~ `180px`，高 `45px` ~ `55px`；
  - 字号规范：`11px` ~ `12px`。
- **节点间距 (Spacing)**：
  - 同一层级横向间距 (Horizontal Gap)：至少 `40px` ~ `60px`；
  - 上下层级纵向间距 (Vertical Gap)：至少 `50px` ~ `70px`。

---

## 连接线走线规范 (Connectors & Routing)

在 Draw.io 中，杂乱无章的斜向交叉线是专业性崩塌的主因。必须严格遵循：

1. **正交折线优先 (Orthogonal Routing)**：
   - 样式设置：`edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;`；
   - 保持线条水平或垂直，尽量减少折角次数（原则上单条线折弯不超过 2 次）。
2. **连接线文字标签规范 (Edge Labels)**：
   - 股权持股线：居中显示百分比（如 `60.00%`），字体颜色设为 `#2D3748`，可加淡色背景以防压线（`labelBackgroundColor=#FFFFFF;`）；
   - 交易步骤线：带有步骤序号与行为（如 `步骤 1：支付首期款`）；
   - 时间线箭头：单向箭头指引时间向前推进。
3. **防交叉与避让原则**：
   - 严禁线条横穿任何非目标主体节点的内部；
   - 交叉不可避免时，使用标准跳线模式或适度扩大节点间距绕行。

---

## 必备结构要素与锚定位置 (Mandatory Structural Blocks)

每张正式交付图表必须在固定几何锚点包含以下两大组件：

### 1. 顶部标题与法律基准日横幅 (Top Header)

- **主标题 (`id="title"`)**：
  - 几何坐标：`x="50" y="30" width="800+" height="30"`；
  - 样式：`text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=18;fontStyle=1;fontColor=#1A365D;`；
  - 内容示例：`【LexPrism 股权穿透报告】目标公司实际控制人与持股架构图`。
- **副标题与基准日声明 (`id="subtitle"`)**：
  - 几何坐标：`x="50" y="60" width="800+" height="20"`；
  - 样式：`text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=11;fontColor=#718096;`；
  - 内容规则：**必须明确写明法律基准日 (As-Of Date)**，示例：`基准日：2026年9月8日 | 数据来源：国家企业信用信息公示系统 (CIT-001) | 适用法：PRC Law`。

### 2. 底部经办律师核查备忘卡片 (Lawyer Memo Card)

- **卡片容器 (`id="memo_card"`)**：
  - 几何坐标：位于画布底端（如 `x="50" y="450+" width="850+" height="100+"`）；
  - 样式：`rounded=1;whiteSpace=wrap;html=1;fillColor=#FEFCBF;strokeColor=#D69E2E;dashed=1;align=left;verticalAlign=top;spacingLeft=15;spacingTop=10;fontColor=#744210;`；
  - 内容要素：
    1. `【经办律师核查备忘与风险提示】`（加粗）；
    2. 穿透结论或核心交割风险简要归纳；
    3. 存疑事实前提或尽调未解决缺口（Actionable Gaps）；
    4. 签名与日期占位符。

---

## 图表反冗余审查清单 (Redundancy Checklist)

在定稿前，必须自查以下各项，凡未通过者均视为不合格交付物：

- [ ] **信息独立性**：图表中的每一个分支和节点，是否均承担不可替代的法律论证职责？
- [ ] **无孤立游离节点**：画布上是否存在没有连接线、无归属关系的悬空图形？
- [ ] **文字完整无截断**：所有节点在 100% 缩放下，主体全称和关键数据是否完整展示，无 `...` 省略或压框现象？
- [ ] **持股数学闭环**：股权图中，同一目标公司的直接股东百分比相加是否严格等于 100%？
- [ ] **步骤顺序自洽**：交易步骤图中的“步骤 1、步骤 2、步骤 3”逻辑是否与交付意见书正文段落一一对应？
