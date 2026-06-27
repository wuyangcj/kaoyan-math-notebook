#!/usr/bin/env python3
# fix_remaining_9_v3.py - 修正剩余未匹配项（所有LaTeX命令用双反斜杠）
FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
fixes = []

# 修复1: real_2018_math3_q8_shusan (第15213行)
# 文件中: \\frac{\\bar{X} - \\mu}{\\frac{\\sigma}{\\sqrt}{n}}
# 正确:  \\frac{\\bar{X} - \\mu}{\\frac{\\sigma}{\\sqrt{n}}
old1 = r'\\frac{\\bar{X} - \\mu}{\\frac{\\sigma}{\\sqrt}{n}}'
new1 = r'\\frac{\\bar{X} - \\mu}{\\frac{\\sigma}{\\sqrt{n}}'
if old1 in content:
    content = content.replace(old1, new1)
    fixes.append('1. real_2018_math3_q8_shusan: \\sqrt}{n} → \\sqrt{n}')
else:
    fixes.append('1. real_2018_math3_q8_shusan: 未找到匹配')

# 修复6b: ss24_10 analysis - P\\{|X-Y|\\leq z\\} → P\\{\\lvert X-Y\\rvert\\leq z\\}
old6b = r'P\\{|X-Y|\\leq z\\}'
new6b = r'P\\{\\lvert X-Y\\rvert\\leq z\\}'
if old6b in content:
    content = content.replace(old6b, new6b)
    fixes.append('6b. ss24_10 analysis: |X-Y| → \\lvert X-Y\\rvert')
else:
    fixes.append('6b. ss24_10 analysis: |X-Y| 未找到匹配')

# 修复6c: ss24_10 analysis - \\iint_{|x-y|\\leq z} → \\iint_{\\lvert x-y\\rvert\\leq z}
old6c = r'\\iint_{|x-y|\\leq z}'
new6c = r'\\iint_{\\lvert x-y\\rvert\\leq z}'
if old6c in content:
    content = content.replace(old6c, new6c)
    fixes.append('6c. ss24_10 analysis: |x-y| → \\lvert x-y\\rvert')
else:
    fixes.append('6c. ss24_10 analysis: |x-y| 未找到匹配')

# 修复7c: sy_p11 analysis - [-\\mathrm{e}^\\frac{{-2y}}{2}] → [-\\mathrm{e}^{-y}]
old7c = r'[-\\mathrm{e}^\\frac{{-2y}}{2}]'
new7c = r'[-\\mathrm{e}^{-y}]'
if old7c in content:
    content = content.replace(old7c, new7c)
    fixes.append('7c. sy_p11 analysis: \\mathrm{e}^\\frac{{-2y}}{2} → \\mathrm{e}^{-y}')
else:
    fixes.append('7c. sy_p11 analysis: 未找到匹配')

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
