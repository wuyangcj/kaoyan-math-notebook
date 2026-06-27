#!/usr/bin/env python3
"""
修复剩余的小于号问题 - 使用原始字符串匹配文件中的双反斜杠
"""
import re

file_path = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
fixes = []

# 使用原始字符串，Python r'\\' 匹配文件中的 \\ (两个字符: 反斜杠 反斜杠)
# 文件中存储的是 JS 字符串，所以 \varepsilon 存为 \\varepsilon

# ===== 修复: 行44137 - 极限内容 =====
line_idx = 44137 - 1
old_line = lines[line_idx]

# 文件中: |f(x)-A|<\\varepsilon (双反斜杠)
# Python中需要: r'|f(x)-A|<\\varepsilon' 或 '|f(x)-A|<\\\\varepsilon'
search = r'|f(x)-A|<\\varepsilon'
replace = r'|f(x)-A|\\lt\\varepsilon'
if search in old_line:
    old_line = old_line.replace(search, replace)
    fixes.append(('44137', '|f(x)-A|<\\varepsilon → |f(x)-A|\\lt\\varepsilon'))

lines[line_idx] = old_line

# ===== 修复: 行44142 - 连续函数内容 =====
line_idx = 44142 - 1
old_line = lines[line_idx]

search = r'f(a)\\cdot f(b)<0'
replace = r'f(a)\\cdot f(b)\\lt 0'
if search in old_line:
    old_line = old_line.replace(search, replace)
    fixes.append(('44142', 'f(a)\\cdot f(b)<0 → f(a)\\cdot f(b)\\lt 0'))

lines[line_idx] = old_line

# ===== 修复: 行44197 - 级数内容 =====
line_idx = 44197 - 1
old_line = lines[line_idx]

search = r'\frac{1}{\mathrm{e}} < 1'
replace = r'\frac{1}{\mathrm{e}} \lt 1'
if search in old_line:
    old_line = old_line.replace(search, replace)
    fixes.append(('44197', '\\frac{1}{\\mathrm{e}} < 1 → \\frac{1}{\\mathrm{e}} \\lt 1'))

lines[line_idx] = old_line

# ===== 修复: 行44311 - 假设检验内容 =====
line_idx = 44311 - 1
old_line = lines[line_idx]

search = r'\chi^{2}<\chi^{2}'
replace = r'\chi^{2}\lt\chi^{2}'
if search in old_line:
    old_line = old_line.replace(search, replace)
    fixes.append(('44311', '\\chi^{2}<\\chi^{2} → \\chi^{2}\\lt\\chi^{2}'))

lines[line_idx] = old_line

# ===== 写回文件 =====
new_content = '\n'.join(lines)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"修复完成，共 {len(fixes)} 处修复:")
for line_num, desc in fixes:
    print(f"  行{line_num}: {desc}")

if len(fixes) == 0:
    print("警告: 没有修复任何内容，请检查匹配条件")
