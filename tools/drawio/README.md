# 法律图形工作台

用浏览器打开 [index.html](index.html)，编辑股权结构图或交易步骤图。页面在本地启动，但编辑器从 embed.diagrams.net 在线加载，须能联网；包内不包含离线 draw.io 引擎。

## 使用

1. 选择“预制法律模板”，或“打开本地文件”载入 .drawio / .xml。
2. 也可通过“导入 Agent 代码”粘贴图表 XML 或 Mermaid，再在画布调整。
3. 点击“保存文件”或按 Ctrl+S。浏览器支持且已授予文件权限时写回原文件；否则按页面提示另存或下载，核对实际保存位置。
4. 需要图片时，使用编辑器的导出菜单；保留 .drawio 作为可编辑原件。

两份示例：[股权结构](templates/equity_structure_sample.drawio)、[交易步骤](templates/transaction_steps_sample.drawio)。示例仅用于结构参考，实际主体、比例、日期和条件须按本案材料核验。

## 交付检查

图表方法、分类与核验要求统一见 [绘图技能](../../skills/drawio-diagram/SKILL.md)。助手可使用 scripts/verify_diagram.py 检查 XML、声明和色盘；静态检查不能代替实际渲染、文字可读性与法律内容核验。
