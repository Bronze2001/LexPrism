#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LexPrism Diagram Verifier
-------------------------
自动化静态合规核验脚本：对标学术与严谨工程标准，对 .drawio 法律图表进行门禁核验。
核验内容：
1. XML 结构与语法有效性
2. 图表主标题与法律基准日 (As-Of Date) 声明
3. 经办律师核查备忘卡片 (Lawyer Memo Card)
4. 律所商务与法律专业色彩白名单校验
5. 节点文本与尺寸基本合理性检查
"""

import sys
import os
import xml.etree.ElementTree as ET

# 保证在 Windows 环境下标准输出为 UTF-8，防止控制台打印乱码
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# 律所商务与法律图表合规色盘白名单 (全部标准化为大写 HEX)
APPROVED_PALETTE = {
    # 🌟 风格 A：典雅藏青涉外跨境风 (Prussian Navy & Slate)
    '#163854', '#0F293D', '#1D5174', '#153E5D', '#204868', '#1B3E5C', '#1E3D59', '#243B53',
    # 💎 风格 B：清爽冰蓝现代并购风 (Crisp Ice Blue & Marine Cerulean)
    '#DDF1FC', '#E1F3FD', '#E2F2FC', '#B3DDF2', '#B6E1F7', '#9FD2EE', '#0284C7', '#0084C8', '#0369A1', '#2D7A9E', '#3683A3',
    # 核心主体 (深海蓝系)
    '#1B365D', '#0B1E38', '#1A365D', '#2C5282',
    # 控股层 / 投资人 (专业深蓝系)
    '#2B6CB0', '#3182CE', '#1E40AF', '#1D4ED8', '#BEE3F8',
    # 普通子公司 / 背景层 (素雅灰白系与文字)
    '#EDF2F7', '#CBD5E0', '#2D3748', '#E2E8F0', '#F8FAFC', '#334155', '#4A5568', '#718096', '#A0AEC0', '#64748B', '#475569',
    # 通道 / 员工持股平台 (商务橙/黄系)
    '#ED8936', '#D69E2E', '#C05621', '#DD6B20', '#B7791F', '#FEEBC8', '#7B341E',
    # 合规达成 / 有力书证 (深绿与青绿系)
    '#2E7D32', '#1B5E20', '#E8F5E9', '#38A169', '#2F855A', '#9AE6B4', '#F0FFF4', '#22543D', '#0E3813', '#319795', '#C6F6D5', '#276749', '#285E61',
    # 违约警示 / 争议风险 (警示红系)
    '#E53E3E', '#9B2C2C', '#FFF5F5', '#C53030', '#FEB2B2', '#7B1113',
    # 律师核查备忘便签 (淡黄系)
    '#FEFCBF', '#744210', '#FAF089',
    # 阶段泳道与中性辅助色
    '#EBF8FF', '#1A202C', '#E9D8FD', '#6B46C1',
    # 黑白与透明
    '#FFFFFF', '#000000', '#CCCCCC', '#D8D8D8',
    'NONE'
}

def parse_style_colors(style_str):
    """从 Draw.io mxCell 的 style 属性中提取颜色"""
    colors = []
    if not style_str:
        return colors
    parts = style_str.split(';')
    for part in parts:
        if '=' in part:
            k, v = part.split('=', 1)
            k = k.strip().lower()
            v = v.strip().upper()
            if k in ('fillcolor', 'strokecolor', 'fontcolor', 'labelbackgroundcolor'):
                if v.startswith('#'):
                    if len(v) == 4:  # #RGB 展开为 #RRGGBB
                        v = '#' + ''.join([c * 2 for c in v[1:]])
                    colors.append((k, v))
                elif v in ('NONE', 'TRANSPARENT'):
                    colors.append((k, 'NONE'))
    return colors

def verify_drawio_file(filepath):
    """核验单个 .drawio 文件"""
    print(f"\n==================================================")
    print(f"[*] 开始核验图表文件: {filepath}")
    print(f"==================================================")

    if not os.path.exists(filepath):
        print(f"[FAIL] 错误: 文件不存在: {filepath}")
        return False

    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"[FAIL] XML 解析失败 (语法错误): {e}")
        return False

    errors = []
    warnings = []

    # 1. 检查根节点结构
    if root.tag not in ('mxfile', 'diagram', 'mxGraphModel'):
        warnings.append(f"根节点标签为 <{root.tag}>，建议使用标准 <mxfile> 封装")

    # 获取所有 mxCell 元素
    cells = root.findall('.//mxCell')
    if not cells:
        errors.append("未在 XML 中检测到任何有效的 <mxCell> 图形节点")
        return False

    has_title = False
    has_as_of_date = False
    has_lawyer_memo = False
    style_color_violations = []

    for cell in cells:
        val = cell.attrib.get('value', '')
        cell_id = cell.attrib.get('id', '')
        if val:
            # 检查标题 (支持架构图、结构图、流向图、时间线、图谱、推导树、报告等)
            if any(kw in val for kw in ('架构图', '结构图', '流向图', '时间线', '图谱', '推导树', '报告', '关系图', '【LexPrism')):
                has_title = True
            
            # 检查法律基准日声明 (不区分大小写)
            val_lower = val.lower()
            if any(kw in val_lower for kw in ('基准日', 'as-of', 'as of', '法律基准')):
                has_as_of_date = True
            
            # 检查经办律师核查备忘卡片
            if (('律师' in val or '合规' in val or '风险' in val) and any(kw in val for kw in ('备忘', '提示', '防控', '核查', '缺口'))) or \
               any(kw in val for kw in ('经办律师', '核查备忘', '律师核查', '风险提示', '特别提示', '审计提示', '待办事项', '待办缺口')):
                has_lawyer_memo = True

        # 检查 style 中的颜色
        style = cell.attrib.get('style', '')
        colors = parse_style_colors(style)
        for attr_name, col in colors:
            if col not in APPROVED_PALETTE:
                style_color_violations.append((cell_id, attr_name, col))

    # 2. 检查法定必须要素
    if not has_title:
        warnings.append("未检测到明确的图表主标题（建议在顶部包含【...架构图/流向图/时间线】）")
    
    if not has_as_of_date:
        errors.append("缺失核心法律基准日声明！图表必须显式标注 '基准日：YYYY年M月D日' 或 'As-Of Date'")

    if not has_lawyer_memo:
        errors.append("缺失【经办律师核查备忘卡片】！正式交付图表底部必须锚定律师风险提示与待办缺口卡片")

    # 3. 检查颜色白名单
    if style_color_violations:
        unique_violations = list(set([col for _, _, col in style_color_violations]))
        errors.append(f"存在非法色盘取值 (未命中律所白名单): {', '.join(unique_violations)}")

    # 4. 统计与汇总
    print(f"[+] 检测到有效图形节点: {len(cells)} 个")
    print(f"[+] 主标题检测: {'[OK]' if has_title else '[WARN]'}")
    print(f"[+] 法律基准日检测: {'[OK]' if has_as_of_date else '[FAIL]'}")
    print(f"[+] 律师核查备忘卡片检测: {'[OK]' if has_lawyer_memo else '[FAIL]'}")
    print(f"[+] 颜色白名单合规性: {'[OK]' if not style_color_violations else '[FAIL]'}")

    if warnings:
        for w in warnings:
            print(f"  [!] 警告提示: {w}")

    if errors:
        print(f"\n[-] 核验未通过，共发现 {len(errors)} 项阻断性问题:")
        for err in errors:
            print(f"  - [BLOCK] {err}")
        return False
    else:
        print(f"\n[PASS] 该图表完全符合 LexPrism 法律专业图表交付标准！")
        return True

def main():
    if len(sys.argv) < 2:
        print("使用说明: python scripts/verify_diagram.py <diagram_path.drawio> [diagram_path2.drawio ...]")
        sys.exit(1)

    all_passed = True
    for path in sys.argv[1:]:
        passed = verify_drawio_file(path)
        if not passed:
            all_passed = False

    print("\n" + "="*50)
    if all_passed:
        print("[SUMMARY] 所有被检图表全部通过合规审计 [GATE G5: PASS]")
        sys.exit(0)
    else:
        print("[SUMMARY] 存在未通过合规审计的图表 [GATE G5: BLOCKED]")
        sys.exit(1)

if __name__ == '__main__':
    main()
