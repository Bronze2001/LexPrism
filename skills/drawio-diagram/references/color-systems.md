# 律所商务与法律图表色彩规范 (Color Systems)

## 设计哲学 (Design Philosophy)

在严肃法律图表中，颜色不是用于“美化”，而是承载**法律关系定性、责任层级与风险状态**的语义工具。每一处颜色运用必须服务于以下三个核心目的之一：

1. **主体定性与身份 (Identity)**：目标公司、实控人、外部战略投资人、境外当地股东还是代持主体？
2. **法律状态与方向 (Direction / Status)**：股权是否发生交割变动（`0 → 30%`）？控制权属于直接持股还是协议控制（Control）？
3. **法域与责任层级 (Jurisdiction & Hierarchy)**：境内主体（中国 China）还是境外主体（印尼 Indonesia、香港 HK 等）？核心标的深色居中锚定，辅助主体内敛协调。

---

## 两大顶级实务视觉风格 (Two Prestigious Practical Styles)

### 🌟 风格 A：典雅藏青 · 涉外跨境与协议控制风 (Deep Prussian Navy Style)
适用于：**跨境投资 (ODI)、外资准入受限行业重组、红筹/VIE 架构、中外合资经营及复杂实控权穿透**。
视觉特点：全图采用统一纯正的高级冷调藏青系，摒弃花哨杂色；中英双语居中排版；搭配点状跨境法域分隔线，极具涉外顶级红圈所与国际投行法律意见书质感。

```python
STYLE_PRUSSIAN_NAVY = {
    # 境内/境外核心主体 (控股公司、运营子公司)
    'primary_entity': {
        'fill': '#163854',      # 经典深海普鲁士藏青 (Deep Prussian Navy)
        'stroke': '#0F293D',    # 极深藏青实线边框 (1.5px)
        'text': '#FFFFFF',      # 纯白加粗中文 + 浅灰英文小字 (#E2E8F0)
        'arcSize': 18,          # 大圆角胶囊卡片
    },
    # 境外当地合作方 / 当地自然人代持 / 参股股东
    'local_partner': {
        'fill': '#1D5174',      # 深石青色 (Slate Prussian)
        'stroke': '#153E5D',
        'text': '#FFFFFF',
        'arcSize': 18,
    },
    # 跨境法域分隔线 (Cross-Border Jurisdiction Divider)
    'jurisdiction_divider': {
        'stroke': '#4A5568',    # 沉稳深灰
        'pattern': '2 3',       # 点状虚线 (Dotted Line)
        'strokeWidth': 1.5,
        'label_text': '#2D3748',# 左右法域标注 (如: 中国 China / 印尼 Indonesia)
    },
    # 走线与连接线 (Connectors & Labels)
    'connector': {
        'stroke': '#204868',    # 藏青深灰蓝连接线 (2px 实线)
        'text': '#163854',      # 持股比例/控制权说明 (#163854)
        'label_bg': '#FFFFFF',  # 防压线白色背景
    }
}
```

---

### 💎 风格 B：清爽冰蓝 · 现代并购受让与动态变动风 (Crisp Ice Blue M&A Style)
适用于：**上市公司协议收购 (SPA)、并购重组股权变动、增资扩股与战略投资退退出演变**。
视觉特点：出资层采用通透温润的“清透冰蓝/天青色”胶囊卡片，底部标的采用“高对比度海洋蔚蓝”宽卡片居中锚定；横向虚线指引收购动作（`Acquire 30% of the shares`），垂直总线清晰呈现持股前后动态跃迁（`0 → 30%`、`90% → 60%`）。

```python
STYLE_CRISP_ICE_BLUE = {
    # 顶层股东 / 投资人 / 转让受让方 (悬浮清爽卡片)
    'shareholder_card': {
        'fill': '#DDF1FC',      # 清透冰蓝 (Ice Cyan / Pale Sky Blue)
        'stroke': '#B3DDF2',    # 微青冰蓝细边框 (1.2px)
        'text': '#163854',      # 深藏青文字 (对比高雅清晰)
        'arcSize': 20,          # 极具流线感的大圆角
    },
    # 核心目标主体 / 标的上市公司 (高对比视觉锚点)
    'target_company': {
        'fill': '#0284C7',      # 纯粹海洋蔚蓝 (Ocean Blue / Cerulean)
        'stroke': '#0369A1',    # 蔚蓝深色边框 (1.5px)
        'text': '#FFFFFF',      # 纯白居中大字
        'arcSize': 16,
    },
    # 动态变动线与受让动向线 (Acquisition & Dynamic Lines)
    'acquisition_arrow': {
        'stroke': '#204868',    # 动作指向虚线 (Dashed)
        'text': '#163854',      # 动作标注 (如: Acquire 30% of the shares)
        'pattern': '4 4',
    },
    'connector_bus': {
        'stroke': '#2D7A9E',    # 青灰/灰蓝汇流总线 (Tee Bus)
        'text': '#163854',      # 动态持股标记 (如: 0 → 30%, 90% → 60%)
        'label_bg': '#FFFFFF',
    }
}
```

---

### 🏛️ 风格 C：经典商事多层穿透风 (Classic Multi-Tier Corporate Palette)
适用于：常规非诉证券申报、多层 SPV、ESOP 平台与各级全资/控股子公司梳理。

```python
STYLE_CLASSIC_CORPORATE = {
    'core_target': {'fill': '#1B365D', 'stroke': '#0B1E38', 'text': '#FFFFFF'},
    'holding_spv': {'fill': '#2B6CB0', 'stroke': '#1A365D', 'text': '#FFFFFF'},
    'subsidiary':  {'fill': '#EDF2F7', 'stroke': '#CBD5E0', 'text': '#2D3748'},
    'esop_escrow': {'fill': '#ED8936', 'stroke': '#C05621', 'text': '#FFFFFF'},
}
```

---

## 信号与特殊备忘色盘 (Signal & Memo Palette)

```python
PALETTE_SIGNAL_AND_MEMO = {
    # 条件成就 / 合规通过
    'positive': {'fill': '#2E7D32', 'stroke': '#1B5E20', 'text': '#FFFFFF'},
    # 违约警示 / 争议风险
    'negative': {'fill': '#E53E3E', 'stroke': '#9B2C2C', 'text': '#9B2C2C'},
    # 经办律师特别核查备忘卡片 (Lawyer Memo Card)
    'lawyer_memo': {
        'fill': '#FEFCBF',      # 柔和便签淡黄
        'stroke': '#D69E2E',    # 黄褐色虚线
        'text': '#744210',      # 沉稳棕褐色文字
    },
    'canvas_bg': '#FFFFFF',     # 正式交付一律纯白无噪点
}
```

---

## 自动化核验色盘白名单 (Approved Palette Whitelist)

所有正式交付 `.drawio` 图表的 `fillColor`、`strokeColor`、`fontColor` 与 `labelBackgroundColor` 必须命中以下集合：

```text
#163854, #0F293D, #1D5174, #153E5D, #204868, #1B3E5C, #1E3D59, #243B53,
#DDF1FC, #E1F3FD, #E2F2FC, #B3DDF2, #B6E1F7, #9FD2EE, #0284C7, #0084C8,
#0369A1, #2D7A9E, #3683A3, #1B365D, #0B1E38, #1A365D, #2C5282, #2B6CB0,
#3182CE, #1E40AF, #1D4ED8, #BEE3F8, #EDF2F7, #CBD5E0, #2D3748, #E2E8F0,
#F8FAFC, #334155, #4A5568, #718096, #A0AEC0, #ED8936, #D69E2E, #C05621,
#DD6B20, #B7791F, #FEEBC8, #7B341E, #2E7D32, #1B5E20, #E8F5E9, #38A169,
#2F855A, #9AE6B4, #F0FFF4, #22543D, #0E3813, #319795, #C6F6D5, #276749,
#285E61, #E53E3E, #9B2C2C, #FFF5F5, #C53030, #FEB2B2, #7B1113, #FEFCBF,
#744210, #FAF089, #EBF8FF, #1A202C, #E9D8FD, #6B46C1, #64748B, #475569,
#FFFFFF, #000000, #CCCCCC, #D8D8D8, none
```
