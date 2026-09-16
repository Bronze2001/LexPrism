#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LexPrism Diagram Generator
--------------------------
专注于【股权结构图】与【交易结构图】的快速高保真生成与可编辑交付。
深度对标顶级涉外红圈所与跨国投行视觉标准：
1. 风格 A: 典雅藏青 · 涉外跨境与协议控制风 (Prussian Navy & Cross-Border ODI)
2. 风格 B: 清爽冰蓝 · 现代并购受让与动态变动风 (Crisp Ice Blue & Dynamic Transition)
3. 风格 C: 经典商事多层穿透风 (Classic Corporate Group)
"""

import sys
import os
import argparse
from datetime import datetime

# 保证在 Windows 环境下标准输出为 UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def generate_crossborder_prussian_diagram(title=None, as_of_date=None, china_entity=None, indo_sub1=None, indo_sub2=None):
    title = title or "【LexPrism 跨境投资架构分析】中资企业出海印尼股权与协议控制结构图"
    as_of = as_of_date or datetime.now().strftime("%Y年%m月%d日")
    china_name = china_entity or "华盛海外投资管理 (深圳) 有限公司"
    sub1_name = indo_sub1 or "PT HUASHENG LEASING INDO"
    sub2_name = indo_sub2 or "PT HUASHENG REKAYASA KONSTRUKSI"

    xml_content = f"""<mxfile host="LexPrism" modified="{datetime.now().isoformat()}" agent="LexPrism-Generator" version="24.0.0" type="device">
  <diagram id="cross-border-equity-01" name="跨境出海与协议控制股权图">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" background="#ffffff" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- 1. 顶部标题与法律基准日声明 -->
        <mxCell id="title" value="{title}" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=17;fontStyle=1;fontColor=#163854;" vertex="1" parent="1">
          <mxGeometry x="60" y="30" width="850" height="30" as="geometry" />
        </mxCell>
        <mxCell id="subtitle" value="基准日：{as_of} | 架构类型：境外直接投资 (ODI) &amp; 协议控制 (VIE) | 适用法：PRC Law &amp; Indonesian Law" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=11;fontColor=#718096;" vertex="1" parent="1">
          <mxGeometry x="60" y="60" width="850" height="20" as="geometry" />
        </mxCell>

        <!-- 2. 跨境法域分隔线 (横贯画布) -->
        <mxCell id="geo_line" value="" style="endArrow=none;html=1;rounded=0;dashed=1;dashPattern=2 3;strokeColor=#4A5568;strokeWidth=1.5;" edge="1" parent="1">
          <mxGeometry width="50" height="50" relative="1" as="geometry">
            <mxPoint x="40" y="315" as="sourcePoint" />
            <mxPoint x="1080" y="315" as="targetPoint" />
          </mxGeometry>
        </mxCell>
        <!-- 法域标签 (左侧固定锚点) -->
        <mxCell id="geo_label_top" value="中国 China" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=bottom;fontSize=12;fontStyle=1;fontColor=#2D3748;" vertex="1" parent="1">
          <mxGeometry x="45" y="278" width="100" height="25" as="geometry" />
        </mxCell>
        <mxCell id="geo_label_bottom" value="印尼 Indonesia" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=top;fontSize=12;fontStyle=1;fontColor=#2D3748;" vertex="1" parent="1">
          <mxGeometry x="45" y="325" width="110" height="25" as="geometry" />
        </mxCell>

        <!-- 3. 境内股东层级 -->
        <mxCell id="node_sh1" value="&lt;b&gt;华盛智能重工集团有限公司&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px; color: #CBD5E0;&quot;&gt;Huasheng Heavy Industry Group&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#163854;strokeColor=#0F293D;strokeWidth=1.5;fontColor=#ffffff;arcSize=18;" vertex="1" parent="1">
          <mxGeometry x="200" y="110" width="220" height="55" as="geometry" />
        </mxCell>
        <mxCell id="node_sh2" value="&lt;b&gt;盛泰共创产业合伙企业 (有限合伙)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px; color: #CBD5E0;&quot;&gt;Shengtai Core Team LP&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#163854;strokeColor=#0F293D;strokeWidth=1.5;fontColor=#ffffff;arcSize=18;" vertex="1" parent="1">
          <mxGeometry x="640" y="110" width="220" height="55" as="geometry" />
        </mxCell>

        <!-- 4. 境内控股公司 (Holdco) -->
        <mxCell id="node_china_holdco" value="&lt;b&gt;{china_name}&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px; color: #CBD5E0;&quot;&gt;China Holding Co. (注册资本: 5,000 万元)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#163854;strokeColor=#0F293D;strokeWidth=1.5;fontColor=#ffffff;arcSize=16;" vertex="1" parent="1">
          <mxGeometry x="380" y="225" width="300" height="58" as="geometry" />
        </mxCell>

        <!-- 5. 境外运营子公司层级 -->
        <mxCell id="node_indo_sub1" value="&lt;b&gt;{sub1_name}&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px;&quot;&gt;设备租赁公司 / Equipment Leasing Co.&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#163854;strokeColor=#0F293D;strokeWidth=1.5;fontColor=#ffffff;arcSize=16;" vertex="1" parent="1">
          <mxGeometry x="100" y="440" width="280" height="60" as="geometry" />
        </mxCell>

        <mxCell id="node_indo_sub2" value="&lt;b&gt;{sub2_name}&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px;&quot;&gt;工程公司 / Construction Co.&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#163854;strokeColor=#0F293D;strokeWidth=1.5;fontColor=#ffffff;arcSize=16;" vertex="1" parent="1">
          <mxGeometry x="620" y="440" width="280" height="60" as="geometry" />
        </mxCell>

        <!-- 印尼当地自然人合作方 -->
        <mxCell id="node_local_citizen" value="&lt;b&gt;当地自然人&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px; color: #E2E8F0;&quot;&gt;Local Citizen (Indonesian)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1D5174;strokeColor=#153E5D;strokeWidth=1.5;fontColor=#ffffff;arcSize=18;" vertex="1" parent="1">
          <mxGeometry x="840" y="340" width="160" height="48" as="geometry" />
        </mxCell>

        <!-- 6. 经办律师核查备忘卡片 -->
        <mxCell id="memo_card" value="&lt;b&gt;【经办律师核查备忘与境外合规提示】&lt;/b&gt;&lt;br&gt;1. 境内审批与穿透：境内控股公司已取得发改委 (NDRC) 及商务主管部门 (MOFCOM) 境外直接投资 (ODI) 备案凭证及外汇登记证；直接股东合计持股 88.00% + 12.00% = 100.00% 严格闭环；&lt;br&gt;2. 外资准入合规架构：依据当地《投资负面清单》，设备租赁业务允许 100% 外商独资；工程承包资质业务受限于当地股权比例，故通过当地自然人持股配合全套独家管理咨询、表决权委托及股权质押协议实现实质控制 (Contractual Control)；&lt;br&gt;3. 司法执行防线：已就当地自然人股权办理官方质押登记，确保控制权穿透与跨境执行效力。" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FEFCBF;strokeColor=#D69E2E;fontColor=#744210;align=left;spacingLeft=12;spacingRight=12;fontSize=11;dashed=1;" vertex="1" parent="1">
          <mxGeometry x="60" y="555" width="980" height="90" as="geometry" />
        </mxCell>

        <!-- 7. 正交连线 -->
        <mxCell id="edge_sh1_holdco" value="88%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#204868;strokeWidth=2;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_sh1" target="node_china_holdco" />
        <mxCell id="edge_sh2_holdco" value="12%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#204868;strokeWidth=2;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_sh2" target="node_china_holdco" />
        <mxCell id="edge_holdco_lease" value="100%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#204868;strokeWidth=2;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_china_holdco" target="node_indo_sub1" />
        <mxCell id="edge_holdco_construct" value="控制&lt;br&gt;Control" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#204868;strokeWidth=2;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_china_holdco" target="node_indo_sub2" />
        <mxCell id="edge_local_citizen" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#204868;strokeWidth=2;entryX=0.8;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="node_local_citizen" target="node_indo_sub2" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
    return xml_content

def generate_acquisition_iceblue_diagram(title=None, as_of_date=None, target_company=None, acquirer=None, seller=None):
    title = title or "【LexPrism 并购重组分析】协议收购30%股权变动与交割后结构图"
    as_of = as_of_date or datetime.now().strftime("%Y年%m月%d日")
    target = target_company or "目标标的智能科技股份有限公司"
    buyer = acquirer or "某战略收购方企业"
    owner = seller or "原控股股东 (创始人团队)"

    xml_content = f"""<mxfile host="LexPrism" modified="{datetime.now().isoformat()}" agent="LexPrism-Generator" version="24.0.0" type="device">
  <diagram id="m-and-a-equity-transition-01" name="并购受让与动态股权变动图">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" background="#ffffff" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- 1. 顶部主标题与基准日声明 -->
        <mxCell id="title" value="{title}" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=17;fontStyle=1;fontColor=#163854;" vertex="1" parent="1">
          <mxGeometry x="60" y="30" width="850" height="30" as="geometry" />
        </mxCell>
        <mxCell id="subtitle" value="基准日：{as_of} | 交易结构：协议收购 (Share Purchase Agreement) | 适用法：PRC Law" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=11;fontColor=#718096;" vertex="1" parent="1">
          <mxGeometry x="60" y="60" width="750" height="20" as="geometry" />
        </mxCell>

        <!-- 2. 顶层股东胶囊卡片 (清透冰蓝风格) -->
        <mxCell id="sh_acquirer" value="&lt;b&gt;{buyer}&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px;&quot;&gt;Strategic Acquirer&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DDF1FC;strokeColor=#B3DDF2;strokeWidth=1.2;fontColor=#163854;arcSize=20;" vertex="1" parent="1">
          <mxGeometry x="80" y="130" width="220" height="60" as="geometry" />
        </mxCell>

        <mxCell id="sh_seller" value="&lt;b&gt;{owner}&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px;&quot;&gt;Founding Shareholder&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DDF1FC;strokeColor=#B3DDF2;strokeWidth=1.2;fontColor=#163854;arcSize=20;" vertex="1" parent="1">
          <mxGeometry x="450" y="130" width="220" height="60" as="geometry" />
        </mxCell>

        <mxCell id="sh_others" value="&lt;b&gt;其他现有股东&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px;&quot;&gt;Other Shareholders&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DDF1FC;strokeColor=#B3DDF2;strokeWidth=1.2;fontColor=#163854;arcSize=20;" vertex="1" parent="1">
          <mxGeometry x="780" y="130" width="220" height="60" as="geometry" />
        </mxCell>

        <!-- 3. 横向受让动向虚线 -->
        <mxCell id="edge_acquisition" value="Acquire 30% of&lt;br&gt;the shares" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;dashPattern=4 4;strokeColor=#204868;strokeWidth=1.5;fontSize=11;fontStyle=1;fontColor=#163854;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="sh_acquirer" target="sh_seller" />

        <!-- 4. 汇流总线主连接节点 -->
        <mxCell id="bus_joint" value="" style="shape=ellipse;fillColor=#2D7A9E;strokeColor=none;" vertex="1" parent="1">
          <mxGeometry x="556" y="280" width="8" height="8" as="geometry" />
        </mxCell>

        <!-- 5. 核心标的公司 (高明度海洋蔚蓝居中大卡片) -->
        <mxCell id="node_target" value="&lt;b&gt;&lt;font style=&quot;font-size: 15px;&quot;&gt;{target}&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px;&quot;&gt;(拟上市公司 / 协议受让标的主体 / 注册资本: 10,000 万元)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#0284C7;strokeColor=#0369A1;strokeWidth=1.5;fontColor=#ffffff;arcSize=16;" vertex="1" parent="1">
          <mxGeometry x="360" y="380" width="400" height="75" as="geometry" />
        </mxCell>

        <!-- 6. 经办律师核查备忘卡片 -->
        <mxCell id="memo_card" value="&lt;b&gt;【经办律师并购重组核查备忘】&lt;/b&gt;&lt;br&gt;1. 变动数据闭环校验：战略收购方受让 30.00% 标的股权，原控股股东持股由 90.00% 降为 60.00%，其他股东持股 10.00% 保持不变；重组交割后各股东持股之和 30% + 60% + 10% = 100.00%，数学闭环自洽；&lt;br&gt;2. 实际控制权状态：交割后原控股股东依然持有 60.00% 绝对控股权，上市公司控制权未发生根本性变更；&lt;br&gt;3. 交割先决条件追踪：本次协议受让已完成经营者集中反垄断申报审查豁免，尚待办理中登公司股份过户登记。" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FEFCBF;strokeColor=#D69E2E;fontColor=#744210;align=left;spacingLeft=12;spacingRight=12;fontSize=11;dashed=1;" vertex="1" parent="1">
          <mxGeometry x="60" y="520" width="940" height="85" as="geometry" />
        </mxCell>

        <!-- 7. 正交连线与动态比例标注 (0->30%, 90%->60%, 10%) -->
        <mxCell id="edge_acquirer_bus" value="0 → 30%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#2D7A9E;strokeWidth=2;fontSize=12;fontStyle=1;fontColor=#163854;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="sh_acquirer" target="bus_joint">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="190" y="284" />
            </Array>
          </mxGeometry>
        </mxCell>

        <mxCell id="edge_seller_bus" value="90% → 60%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#2D7A9E;strokeWidth=2;fontSize=12;fontStyle=1;fontColor=#163854;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="sh_seller" target="bus_joint" />

        <mxCell id="edge_others_bus" value="10%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#2D7A9E;strokeWidth=2;fontSize=12;fontStyle=1;fontColor=#163854;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="sh_others" target="bus_joint">
          <mxGeometry relative="1" as="geometry">
            <Array as="points">
              <mxPoint x="890" y="284" />
            </Array>
          </mxGeometry>
        </mxCell>

        <mxCell id="edge_bus_target" value="" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#2D7A9E;strokeWidth=2.5;" edge="1" parent="1" source="bus_joint" target="node_target" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
    return xml_content

def generate_transaction_diagram(title=None, as_of_date=None, project_name=None):
    title = title or "【LexPrism 交易架构报告】重大资产并购重组步骤与交割流向图"
    as_of = as_of_date or datetime.now().strftime("%Y年%m月%d日")
    proj = project_name or "某高新技术企业控股权协议收购项目"

    xml_content = f"""<mxfile host="LexPrism" modified="{datetime.now().isoformat()}" agent="LexPrism-Generator" version="24.0.0" type="device">
  <diagram id="transaction-steps-01" name="并购交易步骤与交割流程">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" background="#ffffff" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- 标题区 -->
        <mxCell id="title" value="{title}" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=17;fontStyle=1;fontColor=#163854;" vertex="1" parent="1">
          <mxGeometry x="50" y="30" width="850" height="30" as="geometry" />
        </mxCell>
        <mxCell id="subtitle" value="基准日：{as_of} | 标的项目：{proj} | 交易结构：协议收购 (SPA) | 适用法：PRC Law" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=11;fontColor=#718096;" vertex="1" parent="1">
          <mxGeometry x="50" y="60" width="750" height="20" as="geometry" />
        </mxCell>

        <!-- 阶段 1：协议签署 -->
        <mxCell id="lane1" value="&lt;b&gt;阶段一：签约与前置审批&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EBF8FF;strokeColor=#3182CE;fontColor=#163854;verticalAlign=top;spacingTop=6;align=center;fontSize=12;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="50" y="100" width="240" height="420" as="geometry" />
        </mxCell>
        <mxCell id="s1" value="&lt;b&gt;步骤 1：签署《股份购买协议》&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;锁定对价 5.8 亿元，确立交割前置条件&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#163854;strokeColor=#0F293D;fontColor=#ffffff;fontSize=11;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="65" y="150" width="210" height="55" as="geometry" />
        </mxCell>
        <mxCell id="s2" value="&lt;b&gt;步骤 2：反垄断审查申报&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;取得市监总局不予进一步审查决定书&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2E7D32;strokeColor=#1B5E20;fontColor=#ffffff;fontSize=11;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="65" y="240" width="210" height="55" as="geometry" />
        </mxCell>
        <mxCell id="s3" value="&lt;b&gt;步骤 3：开立银行共管账户&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;买卖双方与托管行签署三方共管协议&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ED8936;strokeColor=#C05621;fontColor=#ffffff;fontSize=11;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="65" y="330" width="210" height="55" as="geometry" />
        </mxCell>

        <!-- 阶段 2：交割先决条件成就 -->
        <mxCell id="lane2" value="&lt;b&gt;阶段二：资金托管与交割&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F0FFF4;strokeColor=#38A169;fontColor=#22543D;verticalAlign=top;spacingTop=6;align=center;fontSize=12;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="320" y="100" width="240" height="420" as="geometry" />
        </mxCell>
        <mxCell id="s4" value="&lt;b&gt;步骤 4：支付首期款至共管户&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;买方存入 50% 首期对价 (2.9 亿元)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2B6CB0;strokeColor=#1A365D;fontColor=#ffffff;fontSize=11;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="335" y="150" width="210" height="55" as="geometry" />
        </mxCell>
        <mxCell id="s5" value="&lt;b&gt;步骤 5：办理工商变更登记&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;完成标的股权过户及董事会重组备案&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2E7D32;strokeColor=#1B5E20;fontColor=#ffffff;fontSize=11;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="335" y="240" width="210" height="55" as="geometry" />
        </mxCell>
        <mxCell id="s6" value="&lt;b&gt;步骤 6：共管账户首期解付&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;凭新营业执照解付 2.9 亿元至卖方&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ED8936;strokeColor=#C05621;fontColor=#ffffff;fontSize=11;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="335" y="330" width="210" height="55" as="geometry" />
        </mxCell>

        <!-- 阶段 3：资产交接与尾款清算 -->
        <mxCell id="lane3" value="&lt;b&gt;阶段三：资产交接与质保闭环&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EDF2F7;strokeColor=#CBD5E0;fontColor=#2D3748;verticalAlign=top;spacingTop=6;align=center;fontSize=12;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="590" y="100" width="240" height="420" as="geometry" />
        </mxCell>
        <mxCell id="s7" value="&lt;b&gt;步骤 7：标的公司资产与印章移交&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;双方签署《交割备忘录》完成控制权接管&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2B6CB0;strokeColor=#1A365D;fontColor=#ffffff;fontSize=11;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="605" y="150" width="210" height="55" as="geometry" />
        </mxCell>
        <mxCell id="s8" value="&lt;b&gt;步骤 8：支付第二期交割款 40%&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;交割后 15 个工作日内支付 2.32 亿元&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#163854;strokeColor=#0F293D;fontColor=#ffffff;fontSize=11;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="605" y="240" width="210" height="55" as="geometry" />
        </mxCell>
        <mxCell id="s9" value="&lt;b&gt;步骤 9：质保期满解付 10% 尾款&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;12 个月质保期届满后无争议解付 0.58 亿元&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2E7D32;strokeColor=#1B5E20;fontColor=#ffffff;fontSize=11;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="605" y="330" width="210" height="55" as="geometry" />
        </mxCell>

        <!-- 底部经办律师核查备忘卡片 -->
        <mxCell id="memo_card" value="&lt;b&gt;【经办律师并购交易风险防控备忘】&lt;/b&gt;&lt;br&gt;1. 交割日与风险转移：双方于步骤 7 签署《交割备忘录》之日为实质交割日，自该日起标的公司运营损益与重大经营风险转由买方承担；&lt;br&gt;2. 共管资金划付防线：步骤 6 与步骤 8 的放款先决条件必须严格绑定工商登记证照原件及核心管理层交接清单，杜绝款项悬空；&lt;br&gt;3. 重大不利影响 (MAC) 保障：若在步骤 5 前标的公司发生重大行政处罚或核心知识产权失效，买方享有单方解除权并全额退款。" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FEFCBF;strokeColor=#D69E2E;fontColor=#744210;align=left;spacingLeft=12;spacingRight=12;fontSize=11;dashed=1;" vertex="1" parent="1">
          <mxGeometry x="50" y="540" width="780" height="85" as="geometry" />
        </mxCell>

        <!-- 正交连接线 -->
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#163854;strokeWidth=2;" edge="1" parent="1" source="s1" target="s2" />
        <mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#163854;strokeWidth=2;" edge="1" parent="1" source="s2" target="s3" />
        <mxCell id="e3" value="审批通过" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#2E7D32;strokeWidth=2;fontSize=10;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="s3" target="s4" />
        <mxCell id="e4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#163854;strokeWidth=2;" edge="1" parent="1" source="s4" target="s5" />
        <mxCell id="e5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#163854;strokeWidth=2;" edge="1" parent="1" source="s5" target="s6" />
        <mxCell id="e6" value="工商变更完成" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#2E7D32;strokeWidth=2;fontSize=10;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="s6" target="s7" />
        <mxCell id="e7" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#163854;strokeWidth=2;" edge="1" parent="1" source="s7" target="s8" />
        <mxCell id="e8" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#163854;strokeWidth=2;" edge="1" parent="1" source="s8" target="s9" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
    return xml_content

def main():
    parser = argparse.ArgumentParser(description="LexPrism 法律流程图与架构图生成器 (对标涉外红圈所设计规范)")
    parser.add_argument('--type', choices=['equity', 'transaction'], required=True,
                        help="图表类型: equity (股权结构图) 或 transaction (交易步骤流向图)")
    parser.add_argument('--style', choices=['prussian', 'crossborder', 'iceblue', 'acquisition'], default='prussian',
                        help="视觉风格: prussian/crossborder (典雅藏青涉外跨境风) 或 iceblue/acquisition (清爽冰蓝现代并购风)")
    parser.add_argument('--title', help="图表主标题")
    parser.add_argument('--as-of', help="法律基准日 (如: 2026年9月16日)")
    parser.add_argument('--target', help="标的公司/境内控股公司名称")
    parser.add_argument('--controller', help="主要股东/实控人名称")
    parser.add_argument('--project', help="标的项目名称 (交易图专有)")
    parser.add_argument('--output', '-o', help="输出 .drawio 文件路径 (默认保存在当前目录)")

    args = parser.parse_args()

    if args.type == 'equity':
        if args.style in ('iceblue', 'acquisition'):
            xml_data = generate_acquisition_iceblue_diagram(
                title=args.title,
                as_of_date=args.as_of,
                target_company=args.target,
                acquirer=args.controller
            )
            default_filename = "并购股权受让变动图.drawio"
            style_name = "清爽冰蓝 · 现代并购变动风"
        else:
            xml_data = generate_crossborder_prussian_diagram(
                title=args.title,
                as_of_date=args.as_of,
                china_entity=args.target
            )
            default_filename = "跨境出海协议控制股权图.drawio"
            style_name = "典雅藏青 · 涉外跨境风"
    else:
        xml_data = generate_transaction_diagram(
            title=args.title,
            as_of_date=args.as_of,
            project_name=args.project
        )
        default_filename = "交易结构步骤流向图.drawio"
        style_name = "经典律所 · 交易步骤泳道风"

    output_path = args.output or default_filename

    # 确保父级目录存在
    parent_dir = os.path.dirname(output_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_data)

    print("=" * 65)
    print(f"[SUCCESS] 已成功生成【{style_name}】法律专业矢量图！")
    print(f"[FILE]    保存路径: {os.path.abspath(output_path)}")
    print("=" * 65)
    print("\n【如何立即在本地自由拖拽编辑？】")
    print("1. 浏览器工作台 (推荐)：双击打开 tools/drawio/index.html，点击【📂 打开本地文件】选择该文件即可。")
    print("2. VS Code 编辑器：安装 Draw.io Integration 插件，直接点击该 .drawio 文件。")
    print("3. 代码粘贴：点击 tools/drawio/index.html 顶部的【⚡ 导入 Agent 代码】直接粘贴代码。")

if __name__ == '__main__':
    main()
