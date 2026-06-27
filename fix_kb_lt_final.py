#!/usr/bin/env python3
"""修复行44197和44311 - 文件中是双反斜杠"""

file_path = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
fixes = []

# ===== 修复: 行44197 - 级数内容 =====
line_idx = 44197 - 1
old_line = lines[line_idx]

# 文件中实际是: \\frac{1}{\\mathrm{e}} < 1 (双反斜杠)
# Python原始字符串: r'\\frac{1}{\\mathrm{e}} < 1'
search = r'\\frac{1}{\\mathrm{e}} < 1'
replace = r'\\frac{1}{\\mathrm{e}} \\lt 1'
if search in old_line:
    old_line = old_line.replace(search, replace)
    fixes.append(('44197', '\\frac{1}{\\mathrm{e}} < 1 → \\frac{1}{\\mathrm{e}} \\lt 1'))
else:
    print(f"行44197: 未找到匹配模式")

lines[line_idx] = old_line

# ===== 修复: 行44311 - 假设检验内容 =====
line_idx = 44311 - 1
old_line = lines[line_idx]

# 文件中实际是: \\chi^{2}<\\chi^{2} (双反斜杠)
search = r'\\chi^{2}<\\chi^{2}'
replace = r'\\chi^{2}\\lt\\chi^{2}'
if search in old_line:
    old_line = old_line.replace(search, replace)
    fixes.append(('44311', '\\chi^{2}<\\chi^{2} → \\chi^{2}\\lt\\chi^{2}'))
else:
    print(f"行44311: 未找到匹配模式")

lines[line_idx] = old_line

# ===== 写回文件 =====
new_content = '\n'.join(lines)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"\n修复完成，共 {len(fixes)} 处修复:")
for line_num, desc in fixes:
    print(f"  行{line_num}: {desc}")
