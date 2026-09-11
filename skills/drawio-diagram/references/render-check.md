# Draw.io 法律图表渲染核验清单 (Render Check)

## 核心质控铁律 (Core Quality Invariant)

> **“代码生成成功或 XML 语法合法，绝不代表渲染结果合格 (Code execution / XML validity != Render verification)。”**

在 `[G5: CITATION_AUDITED]` 审计门控与正式向客户/法庭交付图表前，经办律师与审计员必须逐项审查渲染后的实际图像或交互页面，阻断低级失误。

---

## 逐项核验清单 (Checklist)

### 1. 几何排版与视觉清晰度 (Visual & Layout Checks)

- [ ] **无文字截断或压框 (No Text Clipping)**：
  节点宽度与高度充分包裹内部文字，主体法定全称、统一社会信用代码、持股百分比无跑出节点边框或显示为 `...` 的情况。
- [ ] **无文字与线条重叠遮挡 (No Overlap Obscuring Text)**：
  正交连接线未穿透不相关节点的文本区域；连接线上的持股比例或步骤标签设置了白色防压线背景 (`labelBackgroundColor=#FFFFFF`)。
- [ ] **字号层级清晰可辨 (Readable Font Hierarchy)**：
  在 100% 原始尺寸下，核心标题 (16~18px)、主体全称 (13~14px)、说明注记 (10~11px) 层次分明，最小字体不低于 10px。
- [ ] **黑白复印/双面打印保真 (Monochrome Readability)**：
  若转换为黑白灰度视图，重要主体、持股平台与普通子公司仍可通过边框粗细、虚线与灰阶明度清晰辨析。

---

### 2. 法律数据与依据一致性 (Data & Citation Consistency)

- [ ] **持股比例 100% 数学闭环 (Mathematical Closure)**：
  股权架构图上直接股东持股比例相加必须严格等于 100.00%。若存在未穿透的公众股或隐名部分，必须显式设立一个节点注明“其他少数股东持股 XX.XX%”。
- [ ] **日期与序号 100% 证据溯源 (100% Citation Traceability)**：
  时间线图上的每个违约日、催告日、签约交割步骤，必须在 `frozen_citations.json` 或证据清单中具备对应的凭证编号（如 `CIT-001` 或 `证据一`）。
- [ ] **严禁将推论混淆为生效裁判 (Claims vs Judgments)**：
  尚未生效的裁判或单方诉求，必须标明“原告主张”、“一审未生效”或“尚待查证”，严禁直接标注为确定性事实。

---

### 3. 法定结构要素完备性 (Mandatory Structural Elements)

- [ ] **图表主标题完备**：指明案由、交易性质或主体。
- [ ] **法律基准日 (Legal As-Of Date) 声明完备**：清晰注明“基准日：XXXX年XX月XX日”。
- [ ] **【经办律师核查备忘卡片】完备**：画布底端或侧边锚定备忘卡片，记录核查结论与尽调待办缺口。
- [ ] **色盘合规白名单**：全部图形填充与线条颜色 100% 符合律所商务色盘白名单。

---

## 自动化静态合规核验 (Automated Static Verification)

在交付前，直接在终端执行核验脚本：

```bash
python scripts/verify_diagram.py path/to/diagram.drawio
```

核验器将自动执行：
1. **XML 语法合法性**与节点树完整性；
2. **基准日声明识别**（检测 `基准日` 或 `As-Of` 关键字）；
3. **经办律师核查备忘卡片识别**（检测 `核查备忘` 或 `律师提示` 关键字）；
4. **律所色盘白名单校验**（拦截未经批准的非标准配色）；
5. **节点尺寸健康度初筛**。

只有当脚本输出 `[PASS]` 且人工复核无误后，方可由审计员签发 `G5: PASS`，撤除草稿标识。
