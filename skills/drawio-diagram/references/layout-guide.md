# Draw.io 法律流程图与架构图几何排版指南 (Layout Guide)

## 三层法律论证排版模型 (Three-Level Legal Layout Model)

与严肃学术与商务图表类似，一份能够进入庭审举证、监管申报或跨国并购谈判交付物的法律图表，排版必须体现自上而下或自左而右的严谨逻辑推进：

| 论证层级 | 法律问题 | 视觉呈现角色 | Draw.io 典型组件实现 |
| :--- | :--- | :--- | :--- |
| **1. 概览层 (Overview)** | 案件/交易的全貌与适用法域基准？ | 确立管辖法域与全貌框架 | 顶部大标题、基准日横幅、横向跨境法域分隔虚线 (Jurisdiction Line) |
| **2. 实质层 (Main Evidence)** | 核心权利义务、股权变动或控制权脉络？ | 承载核心法律主张与证明链 | 树状持股总线、并购受让虚线箭头、协议控制分支、中英双语胶囊卡片 |
| **3. 校验层 (Validation / Caveats)** | 存在哪些法律风险、假设或未决合规缺口？ | 揭示实质限定前提与责任边界 | 底部/右侧锚定的【经办律师核查备忘卡片】 |

---

## 核心几何组件与排版规范 (Core Geometry Standards)

### 1. 跨境法域分隔线 (Cross-Border Jurisdiction Divider)
在涉及 ODI 境外投资、红筹/VIE、跨国合资架构时，必须清晰划分境内与境外法域：
- **线条样式**：横贯画布的水平点状虚线，贯穿整个主体层级中间；
  - `endArrow=none;html=1;rounded=0;dashed=1;dashPattern=2 3;strokeColor=#4A5568;strokeWidth=1.5;`
- **法域标签锚定**：
  - 位于虚线左侧边缘，上下分别锚定境内法域与境外法域；
  - 上层示例：`x="45" y="278" width="100" height="25"`，文字 `中国 China` (加粗 12px)；
  - 下层示例：`x="45" y="325" width="110" height="25"`，文字 `印尼 Indonesia` 或 `香港 HK`。

---

### 2. 总线式汇流与正交走线 (Tee / Bus Junction Routing)
当多个股东共同持有一家目标公司，或由一家控股公司向下分发到多家子公司时，**严禁多根斜向折线乱穿**，必须采用总线汇流几何：
- **总线汇流方式 (Top-Down Tee Bus)**：
  1. 上层多个股东的垂直向下引线落入同一条水平横梁（Bus Bar）；
  2. 在横梁几何中心设立汇流锚点节点（`shape=ellipse;width=8;height=8;fillColor=#2D7A9E;strokeColor=none;`）；
  3. 由该汇流中心引出单根垂直主干线直达标的公司，极具工业级对齐美感。
- **线段与标签设置**：
  - 静态持股比例：居中标注 `88%`、`12%`；
  - 动态变动标注：居中显式标注跃迁过程 `0 → 30%`、`90% → 60%`，字体颜色设为 `#163854`，背景设为纯白 (`labelBackgroundColor=#ffffff`)。

---

### 3. 大圆角现代卡片规范 (Capsule / Rounded Cards)
为了摆脱老旧 Visio 的生硬方框，全面推行圆润高雅的现代胶囊卡片设计：
- **圆角弧度参数**：
  - 顶层股东/投资方：`arcSize=18~22`（如 `rounded=1;arcSize=20;`）；
  - 核心标的主体：`arcSize=16`，尺寸宽阔（宽 `380~420px`，高 `65~75px`）；
  - 境外当地合作方/自然人：`arcSize=18`（宽 `160~180px`，高 `48~52px`）。
- **中英双语文字层级排版**：
  - 中文主体全称：居中 `13px` ~ `14px` 加粗；
  - 英文法定名称/法域注记：置于换行 `<br>` 之后，`10px` ~ `11px`，浅灰色（如 `#CBD5E0` 或 `#E2E8F0`）与深底色形成温和对比。

---

### 4. 动作动向线与协议控制分支 (Action & Control Routing)
- **并购收购动向线 (Acquisition Arrow)**：
  - 由受让方指向转让方（或标的），使用横向虚线箭头：
  - `edgeStyle=orthogonalEdgeStyle;dashed=1;dashPattern=4 4;strokeColor=#204868;strokeWidth=1.5;endArrow=classic;`
  - 动作标签：标注 `Acquire 30% of the shares` 或 `受让 30% 股权`。
- **协议控制与代持分支 (Contractual Control Routing)**：
  - 从控股公司引出至外资受限业务子公司，线上文字注明：`控制<br>Control`（加粗 11px）；
  - 当地自然人代持/名义股东从侧方正交折线汇入同一入口，表达名义持股与实际控制的分离。

---

## 必备结构要素与锚定位置 (Mandatory Structural Blocks)

每张正式交付图表必须在固定几何锚点包含以下两大组件：

### 1. 顶部标题与法律基准日横幅 (Top Header)
- **主标题 (`id="title"`)**：
  - 几何坐标：`x="50~60" y="30" width="850+" height="30"`；
  - 样式：`text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=17~18;fontStyle=1;fontColor=#163854;`；
- **副标题与基准日声明 (`id="subtitle"`)**：
  - 几何坐标：`x="50~60" y="60" width="800+" height="20"`；
  - 样式：`text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;fontSize=11;fontColor=#718096;`；
  - 必备要素：`基准日：YYYY年M月D日 | 交易结构/出海类型 | 适用法：PRC Law / Target Law`。

### 2. 底部经办律师核查备忘卡片 (Lawyer Memo Card)
- **卡片容器 (`id="memo_card"`)**：
  - 几何坐标：锚定在画布最底端（如 `y="520+"`，宽度 `900~980px`，高度 `80~95px`）；
  - 样式：`rounded=1;whiteSpace=wrap;html=1;fillColor=#FEFCBF;strokeColor=#D69E2E;dashed=1;align=left;verticalAlign=top;spacingLeft=12;spacingRight=12;fontColor=#744210;fontSize=11;`；
  - 内容要素：
    1. `【经办律师核查备忘与风险提示】`（加粗）；
    2. 数值数学闭环结论（如 $30\% + 60\% + 10\% = 100.00\%$ 或 $88\% + 12\% = 100\%$）；
    3. 控制权与外资准入定性（直接持股、协议控制 VIE 或代持质押合规性）；
    4. 待办尽调或监管审批凭证。
