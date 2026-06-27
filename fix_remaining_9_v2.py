#!/usr/bin/env python3
# fix_remaining_9_v2.py - 批量修复剩余9个错误的源数据（v2: 正确处理双反斜杠）
import re

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
fixes = []

# 文件中的LaTeX命令是双反斜杠（\\frac, \\mathrm等），因为在JS字符串中
# Python中 r'\\' 表示两个反斜杠字符，匹配文件中的 \\

# 修复1: real_2018_math3_q8_shusan (第15213行)
# \\sqrt}{n}} → \\sqrt{n}}
old1 = r'\\frac{\bar{X} - \mu}{\frac{\sigma}{\sqrt}{n}}'
new1 = r'\\frac{\bar{X} - \mu}{\frac{\sigma}{\sqrt{n}}}'
if old1 in content:
    content = content.replace(old1, new1)
    fixes.append('1. real_2018_math3_q8_shusan: \\sqrt}{n}} → \\sqrt{n}}')
else:
    fixes.append('1. real_2018_math3_q8_shusan: 未找到匹配')

# 修复4: ss_gs_ch3_q3 (第4207行)
# (\\mathrm\\frac{{e}^x}{2}) → (\\frac{\\mathrm{e}^x}{2})
old4 = r'(\\mathrm\\frac{{e}^x}{2})'
new4 = r'(\\frac{\\mathrm{e}^x}{2})'
if old4 in content:
    content = content.replace(old4, new4)
    fixes.append('4. ss_gs_ch3_q3: \\mathrm\\frac{{e}^x} → \\frac{\\mathrm{e}^x}')
else:
    fixes.append('4. ss_gs_ch3_q3: 未找到匹配')

# 修复6: ss24_10 (第41659行)
# content中的 |X-Y| → \\lvert X-Y\\rvert
old6a = r'令 Z=|X-Y|，则'
new6a = r'令 Z=\lvert X-Y\rvert，则'
if old6a in content:
    content = content.replace(old6a, new6a)
    fixes.append('6a. ss24_10 content: |X-Y| → \\lvert X-Y\\rvert')
else:
    fixes.append('6a. ss24_10 content: 未找到匹配')

# analysis中的 |X-Y|\\leq z → \\lvert X-Y\\rvert\\leq z
old6b = r'P\{|X-Y|\leq z\}'
new6b = r'P\{\lvert X-Y\rvert\leq z\}'
if old6b in content:
    content = content.replace(old6b, new6b)
    fixes.append('6b. ss24_10 analysis: |X-Y| → \\lvert X-Y\\rvert')
else:
    fixes.append('6b. ss24_10 analysis: |X-Y| 未找到匹配')

# analysis中的 |x-y|\\leq z → \\lvert x-y\\rvert\\leq z
old6c = r'\iint_{|x-y|\leq z}'
new6c = r'\iint_{\lvert x-y\rvert\leq z}'
if old6c in content:
    content = content.replace(old6c, new6c)
    fixes.append('6c. ss24_10 analysis: |x-y| → \\lvert x-y\\rvert')
else:
    fixes.append('6c. ss24_10 analysis: |x-y| 未找到匹配')

# 修复7: sy_p11 (第22964行) - 分段函数
# content: f(x,y) = {2\\mathrm{e}^{-(x+2y}), x>0,y>0; 0, 其他}
old7 = r'f(x,y) = {2\\mathrm{e}^{-(x+2y}), x>0,y>0; 0, 其他}'
new7 = r'f(x,y) = \begin{cases} 2\\mathrm{e}^{-(x+2y)}, x>0,y>0 \\ 0, 其他 \end{cases}'
if old7 in content:
    content = content.replace(old7, new7)
    fixes.append('7. sy_p11 content: 分段函数花括号 → \\begin{cases}')
else:
    fixes.append('7. sy_p11 content: 未找到匹配')

# sy_p11 analysis: 2\\mathrm{e}^{-(x+2y}) → 2\\mathrm{e}^{-(x+2y)}
old7b = r'2\\mathrm{e}^{-(x+2y})'
new7b = r'2\\mathrm{e}^{-(x+2y)}'
count = content.count(old7b)
if count > 0:
    content = content.replace(old7b, new7b)
    fixes.append(f'7b. sy_p11 analysis: 2\\mathrm{{e}}^{{-(x+2y}}) → 2\\mathrm{{e}}^{{-(x+2y)}} (替换{count}处)')
else:
    fixes.append('7b. sy_p11 analysis: 未找到匹配')

# sy_p11 analysis: [-\\mathrm{e}^\\frac{{-2y}}{2}] → [-\\mathrm{e}^{-y}]
old7c = r'[-\\mathrm{e}^\frac{{-2y}}{2}]'
new7c = r'[-\\mathrm{e}^{-y}]'
if old7c in content:
    content = content.replace(old7c, new7c)
    fixes.append('7c. sy_p11 analysis: \\mathrm{e}^\\frac{{-2y}}{2} → \\mathrm{e}^{-y}')
else:
    fixes.append('7c. sy_p11 analysis: 未找到匹配')

# 修复8: sy_gl_ch3_q4 (第3960行) - 分段函数
old8 = r'f(x,y) = { 2\\mathrm{e}^{-(x+2y)}, x>0,y>0; 0, 其他 }'
new8 = r'f(x,y) = \begin{cases} 2\\mathrm{e}^{-(x+2y)}, x>0,y>0 \\ 0, 其他 \end{cases}'
if old8 in content:
    content = content.replace(old8, new8)
    fixes.append('8. sy_gl_ch3_q4: 分段函数花括号 → \\begin{cases}')
else:
    fixes.append('8. sy_gl_ch3_q4: 未找到匹配')

# 写入文件
if content != original:
    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print('文件已更新')
else:
    print('文件未变更')

print('\n修复结果：')
for f in fixes:
    print(f'  {f}')
