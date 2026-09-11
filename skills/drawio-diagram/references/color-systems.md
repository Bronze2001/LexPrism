# 律所商务与法律图表色彩规范 (Color Systems)

## 设计哲学 (Design Philosophy)

在严肃法律图表中，颜色不是用于“美化”，而是承载**法律关系定性、责任层级与风险状态**的语义工具。每一处颜色运用必须服务于以下三个核心目的之一：

1. **主体定性与身份 (Identity)**：这是目标公司、实控人、外部投资人还是持股通道/SPV？
2. **法律状态与方向 (Direction / Status)**：先决条件是否达成（合规/有效）？是否存在实质性违约或对赌回购风险（警示/未决）？
3. **法律责任与层级 (Hierarchy)**：哪一个是核心争议焦点主体或重组主体（深色、高明度），哪一个是辅助主体或背景子公司（浅色、素雅灰白）？

---

## 标准色板系统 (Legal Palette System)

### 1. 核心主体与控制权色盘 (Entity & Control Palette)

```python
PALETTE_ENTITY = {
    # 核心目标主体 / 发行主体 / 争议焦点原被告
    'core_target': {
        'fill': '#1B365D',      # 经典深海蓝 (Navy)
        'stroke': '#0B1E38',    # 深蓝实线 (加粗 2px)
        'text': '#FFFFFF',      # 纯白加粗文字
    },
    # 实控人 / 控股股东 / 核心领投机构
    'holding_shareholder': {
        'fill': '#2B6CB0',      # 专业深蓝 (Corporate Blue)
        'stroke': '#1A365D',
        'text': '#FFFFFF',
    },
    # 普通子公司 / 关联履约主体 / 合同相对方
    'subsidiary': {
        'fill': '#EDF2F7',      # 素雅浅灰白 (Light Neutral)
        'stroke': '#CBD5E0',    # 中灰边框
        'text': '#2D3748',      # 深灰文字
    },
    # 资金通道 / 员工持股平台 (ESOP) / 共管账户 (Escrow)
    'channel_platform': {
        'fill': '#ED8936',      # 商务橙 / 土黄 (#D69E2E)
        'stroke': '#C05621',
        'text': '#FFFFFF',
    },
}
```

**恒定原则 (Invariants)**：核心标的主体永远使用深海蓝 (`#1B365D`)，控股层使用深蓝 (`#2B6CB0`)。普通履约主体统一使用浅灰白 (`#EDF2F7`)，严禁喧宾夺主。

---

### 2. 状态与信号色盘 (Status & Signal Palette)

```python
PALETTE_SIGNAL = {
    # 条件满足 / 有力书证 / 合规通过
    'positive': {
        'fill': '#2E7D32',      # 合规深绿
        'fill_light': '#E8F5E9',# 浅绿背景
        'stroke': '#1B5E20',
        'text': '#FFFFFF',
    },
    # 违约节点 / 争议焦点 / 处罚与对赌风险
    'negative': {
        'fill': '#E53E3E',      # 警示红
        'fill_light': '#FFF5F5',# 浅粉红背景
        'stroke': '#9B2C2C',
        'text': '#9B2C2C',      # 或白底红字
    },
}
```

**严苛铁律**：
- **绿色 (`#2E7D32`) 与红色 (`#E53E3E`) 是方向与风险保留色**。
- 绝不允许将绿色用于“某某子公司 A”，红色用于“某某子公司 B”仅仅为了区分。
- 只有发生实质性违约、诉讼冻结、监管处罚、对赌触发时，才允许使用红色警示；只有在先决条件成就、书证原件固化时才使用合规绿色。

---

### 3. 律师核查备忘与辅助色盘 (Memo & Neutral Palette)

```python
PALETTE_NEUTRAL = {
    # 经办律师特别提示 / 未决尽调缺口卡片 (Convenience Note)
    'lawyer_memo': {
        'fill': '#FEFCBF',      # 柔和淡黄
        'stroke': '#D69E2E',    # 黄褐色虚线 (Dashed)
        'text': '#744210',      # 棕褐色文字
    },
    # 画布背景、网格与连接线
    'canvas_bg': '#FFFFFF',     # 正式交付一律白底
    'grid_line': '#E2E8F0',     # 浅灰参考线
    'connector': '#4A5568',     # 连接线深灰
    'connector_highlight': '#1A365D', # 核心交易主线深蓝
}
```

---

## 黑白复印与灰度友好适配原则 (Monochrome & Grayscale)

诉讼举证材料或并购底稿经常会被黑白复印或双面打印。图表必须保证在完全去除色彩后，各主体与线条依然具备明确辨识度：

1. **边框虚实区分**：
   - 确定事实 / 正式主体：实线 (`strokeWidth=1.5` 或 `2`)；
   - 推演事实 / 假设条件 / 附延缓条件交易：虚线 (`dashed=1;dashPattern=4 4;`)；
   - 经办律师核查备忘：双线或细虚线 (`dashed=1;dashPattern=2 2;`)。
2. **明度与对比度差**：
   - 核心主体填充色灰度值低（暗），文字为纯白；
   - 次级主体填充色灰度值高（亮），文字为深黑；
   - 避免使用灰度相近的中间调（如黄绿与浅蓝并排而无边框区分）。
3. **文字与符号强化**：
   - 警示红节点除颜色外，文字前缀强制添加 `【违约】` 或 `[RISK]`；
   - 条件达成节点前缀添加 `【成就】` 或 `[OK]`。

---

## 自动化核验色盘白名单 (Whitelist for verify_diagram.py)

以下十六进制颜色为合规白名单。所有正式交付图表的 `fillColor` 与 `strokeColor` 必须命中该集合：

```text
#1B365D, #0B1E38, #1A365D, #2C5282, #2B6CB0, #3182CE, #1E40AF, #1D4ED8,
#BEE3F8, #EDF2F7, #CBD5E0, #2D3748, #E2E8F0, #F8FAFC, #334155, #4A5568,
#718096, #A0AEC0, #ED8936, #D69E2E, #C05621, #DD6B20, #B7791F, #FEEBC8,
#7B341E, #2E7D32, #1B5E20, #E8F5E9, #38A169, #2F855A, #9AE6B4, #F0FFF4,
#22543D, #0E3813, #319795, #C6F6D5, #276749, #285E61, #E53E3E, #9B2C2C,
#FFF5F5, #C53030, #FEB2B2, #7B1113, #FEFCBF, #744210, #FAF089, #EBF8FF,
#1A202C, #E9D8FD, #6B46C1, #FFFFFF, #000000, #CCCCCC, #D8D8D8, none
```
