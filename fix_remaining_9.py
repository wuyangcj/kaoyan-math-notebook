#!/usr/bin/env python3
# fix_remaining_9.py - 批量修复剩余9个错误的源数据
import sys

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
fixes = []

# 修复1: real_2018_math3_q8_shusan (第15213行)
# \frac{\sigma}{\sqrt}{n}} → \frac{\sigma}{\sqrt{n}}
# 注意：只修改错误的那个（第15213行），正确的（第39027行）不受影响
old1 = '\\frac{\\bar{X} - \\mu}{\\frac{\\sigma}{\\sqrt}{n}}'
new1 = '\\frac{\\bar{X} - \\mu}{\\frac{\\sigma}{\\sqrt{n}}}'
if old1 in content:
    content = content.replace(old1, new1)
    fixes.append('1. real_2018_math3_q8_shusan: \\sqrt}{n}} → \\sqrt{n}}')
else:
    fixes.append('1. real_2018_math3_q8_shusan: 未找到匹配（可能已修复）')

# 修复2: sy_gs_ch7_q4 (第3839行) - \frac{(\1)^n}{\2} → \frac{(-1)^n}{n}
# 在文件中 \1 是字面的反斜杠+1
old2 = '\\frac{(\\1)^n}{\\2} 的收敛性'
new2 = '\\frac{(-1)^n}{n} 的收敛性'
if old2 in content:
    content = content.replace(old2, new2)
    fixes.append('2. sy_gs_ch7_q4: \\frac{(\\1)^n}{\\2} → \\frac{(-1)^n}{n}')
else:
    fixes.append('2. sy_gs_ch7_q4: 未找到匹配')

# 修复3: sy_gs_ch7_q5 (第3840行) - \frac{(\1)^n}{\2} 收敛但 → \frac{(-1)^n}{n} 收敛但
old3 = '\\frac{(\\1)^n}{\\2} 收敛但'
new3 = '\\frac{(-1)^n}{n} 收敛但'
if old3 in content:
    content = content.replace(old3, new3)
    fixes.append('3. sy_gs_ch7_q5: \\frac{(\\1)^n}{\\2} → \\frac{(-1)^n}{n}')
else:
    fixes.append('3. sy_gs_ch7_q5: 未找到匹配')

# 修复4: ss_gs_ch3_q3 (第4207行) - (\mathrm\frac{{e}^x}{2}) → (\frac{\mathrm{e}^x}{2})
old4 = '(\\mathrm\\frac{{e}^x}{2})'
new4 = '(\\frac{\\mathrm{e}^x}{2})'
if old4 in content:
    content = content.replace(old4, new4)
    fixes.append('4. ss_gs_ch3_q3: \\mathrm\\frac{{e}^x}{2} → \\frac{\\mathrm{e}^x}{2}')
else:
    fixes.append('4. ss_gs_ch3_q3: 未找到匹配')

# 修复5: ss_gs_ch7_q3 (第4259行) - \frac{(\1)^n}{\2}^{n} → \left(\frac{-1}{2}\right)^{n}
old5 = '\\frac{(\\1)^n}{\\2}^{n} 的和为'
new5 = '\\left(\\frac{-1}{2}\\right)^{n} 的和为'
if old5 in content:
    content = content.replace(old5, new5)
    fixes.append('5. ss_gs_ch7_q3: \\frac{(\\1)^n}{\\2}^{n} → \\left(\\frac{-1}{2}\\right)^{n}')
else:
    fixes.append('5. ss_gs_ch7_q3: 未找到匹配')

# 修复6: ss24_10 (第41659行) - analysis中 |x-y| → \lvert x-y\rvert, |X-Y| → \lvert X-Y\rvert
# 精确定位：在ss24_10的analysis中
# 原文：F_{Z}(z)=P\{Z\leq z\}=P\{|X-Y|\leq z\}
old6a = 'P\\{|X-Y|\\leq z\\}'
new6a = 'P\\{\\lvert X-Y\\rvert\\leq z\\}'
if old6a in content:
    content = content.replace(old6a, new6a)
    fixes.append('6a. ss24_10: |X-Y| → \\lvert X-Y\\rvert')
else:
    fixes.append('6a. ss24_10: |X-Y| 未找到匹配')

# 原文：\iint_{|x-y|\leq z}
old6b = '\\iint_{|x-y|\\leq z}'
new6b = '\\iint_{\\lvert x-y\\rvert\\leq z}'
if old6b in content:
    content = content.replace(old6b, new6b)
    fixes.append('6b. ss24_10: |x-y| → \\lvert x-y\\rvert')
else:
    fixes.append('6b. ss24_10: |x-y| 未找到匹配')

# 修复7: sy_p11 (第22964行) - 分段函数花括号嵌套错误
# content: f(x,y) = {2\mathrm{e}^{-(x+2y}), x>0,y>0; 0, 其他}
# 改为: f(x,y) = \begin{cases} 2\mathrm{e}^{-(x+2y)}, x>0,y>0 \\ 0, 其他 \end{cases}
old7 = 'f(x,y) = {2\\mathrm{e}^{-(x+2y}), x>0,y>0; 0, 其他}'
new7 = 'f(x,y) = \\begin{cases} 2\\mathrm{e}^{-(x+2y)}, x>0,y>0 \\\\ 0, 其他 \\end{cases}'
if old7 in content:
    content = content.replace(old7, new7)
    fixes.append('7. sy_p11 content: 分段函数花括号 → \\begin{cases}')
else:
    fixes.append('7. sy_p11 content: 未找到匹配')

# sy_p11 analysis: 2\mathrm{e}^{-(x+2y}) → 2\mathrm{e}^{-(x+2y)}
old7b = '2\\mathrm{e}^{-(x+2y})'
new7b = '2\\mathrm{e}^{-(x+2y)}'
count = content.count(old7b)
if count > 0:
    content = content.replace(old7b, new7b)
    fixes.append(f'7b. sy_p11 analysis: 2\\mathrm{{e}}^{{-(x+2y}}) → 2\\mathrm{{e}}^{{-(x+2y)}} (替换{count}处)')
else:
    fixes.append('7b. sy_p11 analysis: 未找到匹配')

# sy_p11 analysis: [-\mathrm{e}^\frac{{-2y}}{2}] → [-\mathrm{e}^{-\frac{2y}{2}}] 或 [-\mathrm{e}^{-y}]
# 原文有问题：\mathrm{e}^\frac{{-2y}}{2} 应该是 \mathrm{e}^{-\frac{2y}{2}} = \mathrm{e}^{-y}
old7c = '[-\\mathrm{e}^\\frac{{-2y}}{2}]_{0}^\\infty = \\frac{1}{2}'
new7c = '[-\\mathrm{e}^{-y}]_{0}^\\infty = \\frac{1}{2}'
if old7c in content:
    content = content.replace(old7c, new7c)
    fixes.append('7c. sy_p11 analysis: \\mathrm{e}^\\frac{{-2y}}{2} → \\mathrm{e}^{-y}')
else:
    fixes.append('7c. sy_p11 analysis: 未找到匹配')

# 修复8: sy_gl_ch3_q4 (第3960行) - 分段函数
# content: f(x,y) = { 2\mathrm{e}^{-(x+2y)}, x>0,y>0; 0, 其他 }
old8 = 'f(x,y) = { 2\\mathrm{e}^{-(x+2y)}, x>0,y>0; 0, 其他 }'
new8 = 'f(x,y) = \\begin{cases} 2\\mathrm{e}^{-(x+2y)}, x>0,y>0 \\\\ 0, 其他 \\end{cases}'
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
