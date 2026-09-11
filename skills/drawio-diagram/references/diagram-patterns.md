# Draw.io 股权与交易结构图模式库 (Diagram Patterns)

本参考提供专属于【股权结构图】与【交易结构图】的原生 `.drawio` XML 代码范式。所有范式均经过几何验证、色盘合规化与全功能可编辑测试。

---

## 1. 股权结构图模式 (Equity Structure Pattern)

适用于：上市穿透核查、实际控制人认定、控股 SPV 架构、员工持股平台 (ESOP) 及下属子公司分层梳理。

### 原生 XML 完整代码范式（可直接导入与编辑）

```xml
<mxfile host="LexPrism" modified="2026-09-08T15:00:00.000Z" agent="LexPrism-Agent" version="24.0.0" type="device">
  <diagram id="equity-structure-01" name="股权穿透与架构图">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" background="#ffffff" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- 1. 顶部主标题与基准日声明 -->
        <mxCell id="title" value="【LexPrism 股权架构分析】某智能科技集团股权穿透与实际控制权结构图" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=18;fontStyle=1;fontColor=#1A365D;" vertex="1" parent="1">
          <mxGeometry x="60" y="40" width="700" height="30" as="geometry" />
        </mxCell>
        <mxCell id="subtitle" value="基准日：2026年9月8日 | 适用法：PRC Law | 数据来源：国家企业信用信息公示系统 (CIT-001)" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=11;fontColor=#718096;" vertex="1" parent="1">
          <mxGeometry x="60" y="70" width="600" height="20" as="geometry" />
        </mxCell>

        <!-- 2. 实控人与高管自然人层级 -->
        <mxCell id="node_founder" value="&lt;b&gt;张某某 (创始人)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px;&quot;&gt;实际控制人 / 董事长兼CEO&lt;br&gt;中国籍 (未取得境外永久居留权)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1B365D;strokeColor=#0B1E38;fontColor=#ffffff;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="180" y="130" width="200" height="60" as="geometry" />
        </mxCell>
        <mxCell id="node_cofounder" value="&lt;b&gt;李某 (联合创始人)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px;&quot;&gt;董事 / 首席技术官&lt;br&gt;中国籍&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2C5282;strokeColor=#1A365D;fontColor=#ffffff;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="460" y="130" width="180" height="60" as="geometry" />
        </mxCell>
        <mxCell id="node_esop_gp" value="&lt;b&gt;张某某 (GP)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;出资比例 1.00%&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2B6CB0;strokeColor=#1A365D;fontColor=#ffffff;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="720" y="130" width="160" height="40" as="geometry" />
        </mxCell>
        <mxCell id="node_esop_lp" value="&lt;b&gt;核心员工35人 (LP)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;合计出资 99.00%&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#4A5568;strokeColor=#2D3748;fontColor=#ffffff;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="900" y="130" width="160" height="40" as="geometry" />
        </mxCell>

        <!-- 3. 中间持股平台与机构投资人层 -->
        <mxCell id="node_holdco" value="&lt;b&gt;聚智投资管理 (深圳) 有限公司&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;(境内控股 SPV 1)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#3182CE;strokeColor=#2B6CB0;fontColor=#ffffff;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="280" y="240" width="220" height="50" as="geometry" />
        </mxCell>
        <mxCell id="node_esop" value="&lt;b&gt;共创致远投资合伙企业 (有限合伙)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;员工持股平台 (ESOP)&lt;br&gt;张某某任GP行使全部表决权&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ED8936;strokeColor=#C05621;fontColor=#ffffff;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="760" y="235" width="240" height="60" as="geometry" />
        </mxCell>

        <!-- 4. 核心标的公司 (发行人 - 突出深海蓝) -->
        <mxCell id="node_target" value="&lt;b&gt;&lt;font style=&quot;font-size: 14px;&quot;&gt;华创未来智能科技股份有限公司&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px;&quot;&gt;(拟上市发行主体 / 注册资本：人民币 8,000 万元)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1B365D;strokeColor=#0B1E38;fontColor=#ffffff;arcSize=8;" vertex="1" parent="1">
          <mxGeometry x="380" y="380" width="380" height="70" as="geometry" />
        </mxCell>
        <mxCell id="node_investor" value="&lt;b&gt;领航新动能一期基金 (有限合伙)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;A轮领投机构 (已完成备案登记)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#718096;strokeColor=#4A5568;fontColor=#ffffff;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="80" y="385" width="210" height="60" as="geometry" />
        </mxCell>

        <!-- 5. 控股子公司层 -->
        <mxCell id="node_sub_a" value="&lt;b&gt;华创云联 (北京) 软件技术有限公司&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px; color: #4A5568;&quot;&gt;核心研发中心 / 高新认证企业&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EDF2F7;strokeColor=#CBD5E0;fontColor=#2D3748;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="120" y="520" width="230" height="55" as="geometry" />
        </mxCell>
        <mxCell id="node_sub_b" value="&lt;b&gt;华创微芯 (深圳) 半导体制造有限公司&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px; color: #4A5568;&quot;&gt;芯片制造基地 / 重点重资产主体&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EDF2F7;strokeColor=#CBD5E0;fontColor=#2D3748;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="455" y="520" width="230" height="55" as="geometry" />
        </mxCell>
        <mxCell id="node_sub_c" value="&lt;b&gt;华创智造 (苏州) 自动化设备有限公司&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px; color: #4A5568;&quot;&gt;生产与装配基地&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EDF2F7;strokeColor=#CBD5E0;fontColor=#2D3748;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="780" y="520" width="230" height="55" as="geometry" />
        </mxCell>

        <!-- 6. 经办律师核查备忘卡片 -->
        <mxCell id="legal_notice" value="&lt;b&gt;【经办律师核查备忘与风险提示】&lt;/b&gt;&lt;br&gt;1. 控制权认定：张某某通过全资控股SPV直接控制发行人55.00%表决权，并通过合伙平台(GP)间接控制15.00%表决权，合计支配70.00%绝对控股权，控制权清晰稳定；&lt;br&gt;2. 数值闭环核验：直接股东合计持股比例 55% + 15% + 30% = 100.00%，无隐名或未穿透股东；&lt;br&gt;3. 待办事项：外部投资人对赌协议中的一票否决权条款已于申报前彻底清理，无恢复效力约定。" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FEFCBF;strokeColor=#D69E2E;fontColor=#744210;align=left;spacingLeft=10;spacingRight=10;fontSize=11;dashed=1;" vertex="1" parent="1">
          <mxGeometry x="80" y="630" width="930" height="85" as="geometry" />
        </mxCell>

        <!-- 7. 连接线 (正交折线 + 居中持股比例) -->
        <mxCell id="e_f_spv" value="80.00%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#2B6CB0;strokeWidth=2;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_founder" target="node_holdco" />
        <mxCell id="e_cf_spv" value="20.00%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#2B6CB0;strokeWidth=2;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_cofounder" target="node_holdco" />
        <mxCell id="e_gp_esop" value="GP (1%)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#DD6B20;strokeWidth=1.5;fontSize=10;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_esop_gp" target="node_esop" />
        <mxCell id="e_lp_esop" value="LP (99%)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#718096;strokeWidth=1.5;fontSize=10;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_esop_lp" target="node_esop" />
        <mxCell id="e_spv_target" value="持股 55.00%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#1B365D;strokeWidth=2.5;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_holdco" target="node_target" />
        <mxCell id="e_esop_target" value="持股 15.00%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#DD6B20;strokeWidth=2;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_esop" target="node_target" />
        <mxCell id="e_inv_target" value="持股 30.00%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#718096;strokeWidth=2;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_investor" target="node_target" />
        <mxCell id="e_target_sub_a" value="100% 全资" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#4A5568;strokeWidth=1.5;fontSize=10;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_target" target="node_sub_a" />
        <mxCell id="e_target_sub_b" value="100% 全资" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#4A5568;strokeWidth=1.5;fontSize=10;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_target" target="node_sub_b" />
        <mxCell id="e_target_sub_c" value="70% 控股" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#4A5568;strokeWidth=1.5;fontSize=10;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_target" target="node_sub_c" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

## 2. 交易结构图模式 (Transaction Structure Pattern)

适用于：并购重组交易步骤、交割先决条件 (CPs)、共管账户 (Escrow) 分期放款、工商登记与交割流向。

### 原生 XML 核心架构与要素
- **横向分阶段容器 (Swimlanes / Phases)**：
  - 阶段一：签署与准备（SPA 签署、反垄断审查、外汇登记）；
  - 阶段二：先决条件达成与共管入资（Escrow 账户存入首期款）；
  - 阶段三：股权交割与工商登记变更（标的过户、换发营业执照）；
  - 阶段四：尾款清算与质保金解付（完成交割后最终闭环）。
- **步骤编号与连接线**：正交折线标明 `步骤 1`、`步骤 2` 至 `步骤 N`；
- **状态信号色**：先决条件成就标深绿 (`#2E7D32`)，附延缓条件使用虚线，重大风险标注警示红 (`#E53E3E`)；
- **经办律师备忘卡片**：固定在画布底部，提示交割日所有权转移法律界限与重大不利影响 (MAC) 条款。

---

## 如何在本地编辑上述图表？

1. **一键导入**：打开 `tools/drawio/index.html`，点击顶部 **【⚡ 导入 Agent 代码】**，直接粘贴上述 XML 代码块即可在画布中实时拖拽修改。
2. **快捷保存**：按 `Ctrl+S` 将编辑结果原路写回本地 `.drawio` 文件。
