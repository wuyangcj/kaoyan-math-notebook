#!/usr/bin/env python3
"""
全面修复知识库详情中的数学小于号问题
将数学表达式中的 < 替换为 \\lt（文件中存储为双反斜杠 \\lt）
同时修复之前被误删除 < 留下的双空格问题
"""
import re

file_path = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# 记录所有修复
fixes = []

# ===== 修复1: 行44019 - 线性方程组内容 =====
line_idx = 44019 - 1  # 0-based
old_line = lines[line_idx]

# 1a. r(A)=r<n → r(A)=r\\lt n
if 'r(A)=r<n' in old_line:
    old_line = old_line.replace('r(A)=r<n', 'r(A)=r\\\\lt n')
    fixes.append(('44019', 'r(A)=r<n → r(A)=r\\\\lt n'))

# 1b. r(A)  n (双空格，缺少<) → r(A) \\lt n
# 上下文: Ax=0 有非零解 ⟺ r(A)  n
if 'r(A)  n。' in old_line:
    old_line = old_line.replace('r(A)  n。', 'r(A) \\\\lt n。')
    fixes.append(('44019', 'r(A)  n → r(A) \\\\lt n (双空格修复)'))

# 1c. r(A)  r(A|b) (双空格，缺少<) → r(A) \\lt r(A|b)
if 'r(A)  r(A|b)' in old_line:
    old_line = old_line.replace('r(A)  r(A|b)', 'r(A) \\\\lt r(A|b)')
    fixes.append(('44019', 'r(A)  r(A|b) → r(A) \\\\lt r(A|b) (双空格修复)'))

lines[line_idx] = old_line

# ===== 修复2: 行44024 - 向量组线性相关性内容 =====
line_idx = 44024 - 1
old_line = lines[line_idx]

# r(A)  m (双空格，缺少<) → r(A) \\lt m
if 'r(A)  m' in old_line:
    old_line = old_line.replace('r(A)  m', 'r(A) \\\\lt m')
    fixes.append(('44024', 'r(A)  m → r(A) \\\\lt m (双空格修复)'))

lines[line_idx] = old_line

# ===== 修复3: 行44137 - 极限内容 =====
line_idx = 44137 - 1
old_line = lines[line_idx]

# |f(x)-A|<\varepsilon → |f(x)-A|\lt\varepsilon (在<p>文本中，不在<code>内)
# 上下文: 当 |x|>X 时 |f(x)-A|<\varepsilon。
if '|f(x)-A|<\\varepsilon' in old_line:
    old_line = old_line.replace('|f(x)-A|<\\varepsilon', '|f(x)-A|\\\\lt\\varepsilon')
    fixes.append(('44137', '|f(x)-A|<\\varepsilon → |f(x)-A|\\\\lt\\varepsilon'))

lines[line_idx] = old_line

# ===== 修复4: 行44142 - 连续函数内容 =====
line_idx = 44142 - 1
old_line = lines[line_idx]

# f(a)\cdot f(b)<0 → f(a)\cdot f(b)\lt 0
if 'f(a)\\cdot f(b)<0' in old_line:
    old_line = old_line.replace('f(a)\\cdot f(b)<0', 'f(a)\\cdot f(b)\\\\lt 0')
    fixes.append(('44142', 'f(a)\\cdot f(b)<0 → f(a)\\cdot f(b)\\\\lt 0'))

lines[line_idx] = old_line

# ===== 修复5: 行44167 - 极值内容（表格中） =====
line_idx = 44167 - 1
old_line = lines[line_idx]

# A < 0 → A \lt 0 (在<td>中)
# \Delta < 0 → \Delta \lt 0 (在<td>中)
# 需要精确匹配，避免误改
# 上下文1: <td>\Delta > 0 且 A < 0</td>
if '\\Delta > 0 且 A < 0' in old_line:
    old_line = old_line.replace('\\Delta > 0 且 A < 0', '\\Delta > 0 且 A \\\\lt 0')
    fixes.append(('44167', 'A < 0 → A \\\\lt 0 (表格中)'))

# 上下文2: <td>\Delta < 0</td>
if '\\Delta < 0</td>' in old_line:
    old_line = old_line.replace('\\Delta < 0</td>', '\\Delta \\\\lt 0</td>')
    fixes.append(('44167', '\\Delta < 0 → \\Delta \\\\lt 0 (表格中)'))

lines[line_idx] = old_line

# ===== 修复6: 行44197 - 级数内容 =====
line_idx = 44197 - 1
old_line = lines[line_idx]

# \frac{1}{\mathrm{e}} < 1 → \frac{1}{\mathrm{e}} \lt 1
if '\\frac{1}{\\mathrm{e}} < 1' in old_line:
    old_line = old_line.replace('\\frac{1}{\\mathrm{e}} < 1', '\\frac{1}{\\mathrm{e}} \\\\lt 1')
    fixes.append(('44197', '\\frac{1}{\\mathrm{e}} < 1 → \\frac{1}{\\mathrm{e}} \\\\lt 1'))

lines[line_idx] = old_line

# ===== 修复7: 行44202 - 幂级数内容 =====
line_idx = 44202 - 1
old_line = lines[line_idx]

# |x|<|x_{1}| → |x|\lt|x_{1}|
if '|x|<|x_{1}|' in old_line:
    old_line = old_line.replace('|x|<|x_{1}|', '|x|\\\\lt|x_{1}|')
    fixes.append(('44202', '|x|<|x_{1}| → |x|\\\\lt|x_{1}|'))

lines[line_idx] = old_line

# ===== 修复8: 行44207 - 泰勒级数内容 =====
line_idx = 44207 - 1
old_line = lines[line_idx]

# |x|<1 → |x|\lt 1 (多处)
count = old_line.count('|x|<1')
if count > 0:
    old_line = old_line.replace('|x|<1', '|x|\\\\lt 1')
    fixes.append(('44207', f'|x|<1 → |x|\\\\lt 1 ({count}处)'))

lines[line_idx] = old_line

# ===== 修复9: 行44276 - 概率内容 =====
line_idx = 44276 - 1
old_line = lines[line_idx]

# i_{2}<... → i_{2}\lt...
if "i_{2}<..." in old_line:
    old_line = old_line.replace("i_{2}<...", "i_{2}\\\\lt...")
    fixes.append(('44276', "i_{2}<... → i_{2}\\\\lt..."))

lines[line_idx] = old_line

# ===== 修复10: 行44311 - 假设检验内容 =====
line_idx = 44311 - 1
old_line = lines[line_idx]

# \chi^{2}<\chi^{2} → \chi^{2}\lt\chi^{2}
if '\\chi^{2}<\\chi^{2}' in old_line:
    old_line = old_line.replace('\\chi^{2}<\\chi^{2}', '\\chi^{2}\\\\lt\\chi^{2}')
    fixes.append(('44311', '\\chi^{2}<\\chi^{2} → \\chi^{2}\\\\lt\\chi^{2}'))

lines[line_idx] = old_line

# ===== 写回文件 =====
new_content = '\n'.join(lines)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"修复完成，共 {len(fixes)} 处修复:")
for line_num, desc in fixes:
    print(f"  行{line_num}: {desc}")
