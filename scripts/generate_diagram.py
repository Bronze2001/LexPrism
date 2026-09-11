#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LexPrism Diagram Generator
--------------------------
专注于【股权结构图】与【交易结构图】的快速生成与可编辑交付。
支持生成标准的原生 .drawio 矢量图文件，生成后可直接在 tools/drawio/index.html 或 VS Code 中拖拽编辑。
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

def generate_equity_diagram(title=None, as_of_date=None, target_company=None, controller=None):
    title = title or "【LexPrism 股权架构报告】目标公司股权穿透与实际控制权结构图"
    as_of = as_of_date or datetime.now().strftime("%Y年%m月%d日")
    target = target_company or "北京华创未来医疗科技股份有限公司"
    ctrl = controller or "张某某"

    xml_content = f"""<mxfile host="LexPrism" modified="{datetime.now().isoformat()}" agent="LexPrism-Generator" version="24.0.0" type="device">
  <diagram id="equity-diagram-01" name="股权结构图">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" background="#ffffff" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- 1. 顶部主标题与基准日声明 -->
        <mxCell id="title" value="{title}" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=18;fontStyle=1;fontColor=#1A365D;" vertex="1" parent="1">
          <mxGeometry x="60" y="40" width="800" height="30" as="geometry" />
        </mxCell>
        <mxCell id="subtitle" value="基准日：{as_of} | 适用法：PRC Law | 核心主张：确认实际控制人地位与穿透持股比例" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=11;fontColor=#718096;" vertex="1" parent="1">
          <mxGeometry x="60" y="70" width="700" height="20" as="geometry" />
        </mxCell>

        <!-- 2. 实控人层级 -->
        <mxCell id="node_controller" value="&lt;b&gt;{ctrl} (创始人)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px;&quot;&gt;单一实际控制人 / 董事长兼总经理&lt;br&gt;中国国籍 (未取得境外居留权)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1B365D;strokeColor=#0B1E38;fontColor=#ffffff;arcSize=12;" vertex="1" parent="1">
          <mxGeometry x="240" y="130" width="220" height="60" as="geometry" />
        </mxCell>
        <mxCell id="node_esop_gp" value="&lt;b&gt;{ctrl} (普通合伙人 GP)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;认缴出资 1.00% / 实际支配表决权&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2B6CB0;strokeColor=#1A365D;fontColor=#ffffff;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="680" y="130" width="190" height="40" as="geometry" />
        </mxCell>

        <!-- 3. 持股平台层 -->
        <mxCell id="node_spv" value="&lt;b&gt;华领投资发展 (深圳) 有限公司&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;实控人 100% 全资持股 SPV&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2B6CB0;strokeColor=#1A365D;fontColor=#ffffff;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="250" y="240" width="200" height="50" as="geometry" />
        </mxCell>
        <mxCell id="node_esop" value="&lt;b&gt;华领共创投资合伙企业 (有限合伙)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;员工持股平台 (ESOP)&lt;br&gt;核心骨干员工 32 人任 LP&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ED8936;strokeColor=#C05621;fontColor=#ffffff;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="665" y="235" width="220" height="60" as="geometry" />
        </mxCell>
        <mxCell id="node_investor" value="&lt;b&gt;深创鼎盛战略投资基金 (有限合伙)&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;A轮领投机构 (已备案财务投资人)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EDF2F7;strokeColor=#CBD5E0;fontColor=#2D3748;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="50" y="385" width="210" height="60" as="geometry" />
        </mxCell>

        <!-- 4. 核心标的主体 -->
        <mxCell id="node_target" value="&lt;b&gt;&lt;font style=&quot;font-size: 15px;&quot;&gt;{target}&lt;/font&gt;&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 11px;&quot;&gt;(拟上市发行主体 / 注册资本：人民币 6,000 万元)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1B365D;strokeColor=#0B1E38;strokeWidth=2;fontColor=#ffffff;arcSize=8;" vertex="1" parent="1">
          <mxGeometry x="320" y="380" width="380" height="70" as="geometry" />
        </mxCell>

        <!-- 5. 控股子公司层 -->
        <mxCell id="node_sub_a" value="&lt;b&gt;华领云联 (北京) 信息技术有限公司&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px; color: #4A5568;&quot;&gt;软件研发中心 / 专精特新主体&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EDF2F7;strokeColor=#CBD5E0;fontColor=#2D3748;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="200" y="520" width="220" height="55" as="geometry" />
        </mxCell>
        <mxCell id="node_sub_b" value="&lt;b&gt;华领智造 (江苏) 医疗装备有限公司&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px; color: #4A5568;&quot;&gt;核心生产与装配基地&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EDF2F7;strokeColor=#CBD5E0;fontColor=#2D3748;arcSize=10;" vertex="1" parent="1">
          <mxGeometry x="540" y="520" width="220" height="55" as="geometry" />
        </mxCell>

        <!-- 6. 经办律师核查备忘卡片 -->
        <mxCell id="memo_card" value="&lt;b&gt;【经办律师核查备忘与风险提示】&lt;/b&gt;&lt;br&gt;1. 控制权闭环认定：{ctrl}通过持有SPV 100%股权直接控制发行人55.00%表决权，通过持股平台(GP)实际支配15.00%表决权，合计支配70.00%表决权，单一控制权清晰稳定；&lt;br&gt;2. 数值闭环核验：直接股东持股比例为 55.00% (SPV) + 15.00% (ESOP) + 30.00% (投资人) = 100.00%，无未披露少数股权；&lt;br&gt;3. 待办事项：ESOP 平台穿透自然人 32 人，未超过 200 人法定红线；投资人特殊股东权利条款已于申报前彻底解除并无效力恢复。" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FEFCBF;strokeColor=#D69E2E;fontColor=#744210;align=left;spacingLeft=12;spacingRight=12;fontSize=11;dashed=1;" vertex="1" parent="1">
          <mxGeometry x="50" y="630" width="940" height="85" as="geometry" />
        </mxCell>

        <!-- 7. 正交连接线 -->
        <mxCell id="e1" value="100.00%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#2B6CB0;strokeWidth=2;fontSize=10;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_controller" target="node_spv" />
        <mxCell id="e2" value="GP (1.00%)" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#ED8936;strokeWidth=1.5;fontSize=10;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_esop_gp" target="node_esop" />
        <mxCell id="e3" value="持股 55.00%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#1B365D;strokeWidth=2.5;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_spv" target="node_target" />
        <mxCell id="e4" value="持股 15.00%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#ED8936;strokeWidth=2;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_esop" target="node_target" />
        <mxCell id="e5" value="持股 30.00%" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#718096;strokeWidth=2;fontSize=11;fontStyle=1;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_investor" target="node_target" />
        <mxCell id="e6" value="100% 全资" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#4A5568;strokeWidth=1.5;fontSize=10;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_target" target="node_sub_a" />
        <mxCell id="e7" value="100% 全资" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#4A5568;strokeWidth=1.5;fontSize=10;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="node_target" target="node_sub_b" />
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
  <diagram id="transaction-steps-01" name="交易结构图">
    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" background="#ffffff" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- 标题区 -->
        <mxCell id="title" value="{title}" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=18;fontStyle=1;fontColor=#1A365D;" vertex="1" parent="1">
          <mxGeometry x="50" y="30" width="850" height="30" as="geometry" />
        </mxCell>
        <mxCell id="subtitle" value="基准日：{as_of} | 标的项目：{proj} | 交易结构：协议收购 (SPA) | 适用法：PRC Law" style="text;html=1;strokeColor=none;fillColor=none;align=left;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=11;fontColor=#718096;" vertex="1" parent="1">
          <mxGeometry x="50" y="60" width="750" height="20" as="geometry" />
        </mxCell>

        <!-- 阶段 1：协议签署 -->
        <mxCell id="lane1" value="&lt;b&gt;阶段一：签约与前置审批&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EBF8FF;strokeColor=#3182CE;fontColor=#1B365D;verticalAlign=top;spacingTop=6;align=center;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="50" y="100" width="240" height="420" as="geometry" />
        </mxCell>
        <mxCell id="s1" value="&lt;b&gt;步骤 1：签署《股份购买协议》&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;锁定对价 5.8 亿元，确立交割前置条件&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1B365D;strokeColor=#0B1E38;fontColor=#ffffff;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="65" y="150" width="210" height="55" as="geometry" />
        </mxCell>
        <mxCell id="s2" value="&lt;b&gt;步骤 2：反垄断审查申报&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;取得市监总局不予进一步审查决定书&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2E7D32;strokeColor=#1B5E20;fontColor=#ffffff;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="65" y="240" width="210" height="55" as="geometry" />
        </mxCell>
        <mxCell id="s3" value="&lt;b&gt;步骤 3：开立银行共管账户&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;买卖双方与托管行签署三方共管协议&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ED8936;strokeColor=#C05621;fontColor=#ffffff;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="65" y="330" width="210" height="55" as="geometry" />
        </mxCell>

        <!-- 阶段 2：交割先决条件成就 -->
        <mxCell id="lane2" value="&lt;b&gt;阶段二：资金托管与交割&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F0FFF4;strokeColor=#38A169;fontColor=#22543D;verticalAlign=top;spacingTop=6;align=center;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="320" y="100" width="240" height="420" as="geometry" />
        </mxCell>
        <mxCell id="s4" value="&lt;b&gt;步骤 4：支付首期款至共管户&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;买方存入 50% 首期对价 (2.9 亿元)&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2B6CB0;strokeColor=#1A365D;fontColor=#ffffff;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="335" y="150" width="210" height="55" as="geometry" />
        </mxCell>
        <mxCell id="s5" value="&lt;b&gt;步骤 5：办理工商变更登记&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;完成标的股权过户及董事会重组备案&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2E7D32;strokeColor=#1B5E20;fontColor=#ffffff;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="335" y="240" width="210" height="55" as="geometry" />
        </mxCell>
        <mxCell id="s6" value="&lt;b&gt;步骤 6：共管账户首期解付&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;凭新营业执照解付 2.9 亿元至卖方&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ED8936;strokeColor=#C05621;fontColor=#ffffff;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="335" y="330" width="210" height="55" as="geometry" />
        </mxCell>

        <!-- 阶段 3：资产交接与尾款清算 -->
        <mxCell id="lane3" value="&lt;b&gt;阶段三：资产交接与质保闭环&lt;/b&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#EDF2F7;strokeColor=#CBD5E0;fontColor=#2D3748;verticalAlign=top;spacingTop=6;align=center;fontSize=12;" vertex="1" parent="1">
          <mxGeometry x="590" y="100" width="240" height="420" as="geometry" />
        </mxCell>
        <mxCell id="s7" value="&lt;b&gt;步骤 7：标的公司资产与印章移交&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;双方签署《交割备忘录》完成控制权接管&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2B6CB0;strokeColor=#1A365D;fontColor=#ffffff;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="605" y="150" width="210" height="55" as="geometry" />
        </mxCell>
        <mxCell id="s8" value="&lt;b&gt;步骤 8：支付第二期交割款 40%&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;交割后 15 个工作日内支付 2.32 亿元&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#1B365D;strokeColor=#0B1E38;fontColor=#ffffff;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="605" y="240" width="210" height="55" as="geometry" />
        </mxCell>
        <mxCell id="s9" value="&lt;b&gt;步骤 9：质保期满解付 10% 尾款&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 10px;&quot;&gt;12 个月质保期届满后无争议解付 0.58 亿元&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#2E7D32;strokeColor=#1B5E20;fontColor=#ffffff;fontSize=11;" vertex="1" parent="1">
          <mxGeometry x="605" y="330" width="210" height="55" as="geometry" />
        </mxCell>

        <!-- 底部经办律师核查备忘卡片 -->
        <mxCell id="memo_card" value="&lt;b&gt;【经办律师并购交易风险防控备忘】&lt;/b&gt;&lt;br&gt;1. 交割日与风险转移：双方于步骤 7 签署《交割备忘录》之日为实质交割日，自该日起标的公司运营损益与重大经营风险转由买方承担；&lt;br&gt;2. 共管资金划付防线：步骤 6 与步骤 8 的放款先决条件必须严格绑定工商登记证照原件及核心管理层交接清单，杜绝款项悬空；&lt;br&gt;3. 重大不利影响 (MAC) 保障：若在步骤 5 前标的公司发生重大行政处罚或核心知识产权失效，买方享有单方解除权并全额退款。" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#FEFCBF;strokeColor=#D69E2E;fontColor=#744210;align=left;spacingLeft=12;spacingRight=12;fontSize=11;dashed=1;" vertex="1" parent="1">
          <mxGeometry x="50" y="540" width="780" height="85" as="geometry" />
        </mxCell>

        <!-- 正交连接线 -->
        <mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#1A365D;strokeWidth=2;" edge="1" parent="1" source="s1" target="s2" />
        <mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#1A365D;strokeWidth=2;" edge="1" parent="1" source="s2" target="s3" />
        <mxCell id="e3" value="审批通过" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#2E7D32;strokeWidth=2;fontSize=10;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="s3" target="s4" />
        <mxCell id="e4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#1A365D;strokeWidth=2;" edge="1" parent="1" source="s4" target="s5" />
        <mxCell id="e5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#1A365D;strokeWidth=2;" edge="1" parent="1" source="s5" target="s6" />
        <mxCell id="e6" value="工商变更完成" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#2E7D32;strokeWidth=2;fontSize=10;labelBackgroundColor=#ffffff;" edge="1" parent="1" source="s6" target="s7" />
        <mxCell id="e7" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#1A365D;strokeWidth=2;" edge="1" parent="1" source="s7" target="s8" />
        <mxCell id="e8" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#1A365D;strokeWidth=2;" edge="1" parent="1" source="s8" target="s9" />
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>"""
    return xml_content

def main():
    parser = argparse.ArgumentParser(description="LexPrism 股权结构图与交易结构图生成器")
    parser.add_argument('--type', choices=['equity', 'transaction'], required=True,
                        help="图表类型: equity (股权结构图) 或 transaction (交易结构图)")
    parser.add_argument('--title', help="图表主标题")
    parser.add_argument('--as-of', help="法律基准日 (如: 2026年9月8日)")
    parser.add_argument('--target', help="标的公司名称 (股权图专有)")
    parser.add_argument('--controller', help="实际控制人名称 (股权图专有)")
    parser.add_argument('--project', help="标的项目名称 (交易图专有)")
    parser.add_argument('--output', '-o', help="输出 .drawio 文件路径 (默认保存在当前目录)")

    args = parser.parse_args()

    if args.type == 'equity':
        xml_data = generate_equity_diagram(
            title=args.title,
            as_of_date=args.as_of,
            target_company=args.target,
            controller=args.controller
        )
        default_filename = "股权结构图.drawio"
    else:
        xml_data = generate_transaction_diagram(
            title=args.title,
            as_of_date=args.as_of,
            project_name=args.project
        )
        default_filename = "交易结构图.drawio"

    output_path = args.output or default_filename

    # 确保父级目录存在
    parent_dir = os.path.dirname(output_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_data)

    print("=" * 60)
    print(f"[SUCCESS] 已成功生成标准的【{'股权结构图' if args.type == 'equity' else '交易结构图'}】！")
    print(f"[FILE] 保存路径: {os.path.abspath(output_path)}")
    print("=" * 60)
    print("\n【如何立即进行自由编辑？】")
    print("方式 1 (推荐)：双击打开 tools/drawio/index.html，点击顶部【📂 打开本地文件】，选择上述文件即可拖拽微调并按 Ctrl+S 保存。")
    print("方式 2：在 VS Code 中安装 Draw.io Integration 插件，直接在编辑器侧边栏点击该文件编辑。")
    print("方式 3：打开 tools/drawio/index.html 点击【⚡ 导入 Agent 代码】，将该文件内容粘贴导入。")

if __name__ == '__main__':
    main()
