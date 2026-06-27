#!/usr/bin/env python3
# fix_remaining_5.py - 修复第二轮检测后的5个错误
FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
fixes = []

# 修复1补丁: real_2018_math3_q8_shusan - \\sqrt{n}} 缺少一个 }
# 当前: \\frac{\\sigma}{\\sqrt{n}} \\sim
# 正确: \\frac{\\sigma}{\\sqrt{n}}} \\sim
old1 = r'\\frac{\\sigma}{\\sqrt{n}} \\sim N(0, 1)'
new1 = r'\\frac{\\sigma}{\\sqrt{n}}} \\sim N(0, 1)'
if old1 in content:
    content = content.replace(old1, new1)
    fixes.append('1. real_2018_math3_q8_shusan: \\sqrt{n}} → \\sqrt{n}}} (补一个})')
else:
    fixes.append('1. real_2018_math3_q8_shusan: 未找到匹配')

# 修复2补丁: sy_gs_ch7_q4 analysis - 还有 \u0001 和 \u0002
# analysis: Σ|\\frac{(\u0001)^n}{\u0002}| = Σ \\frac{1}{n}
# 注意：\u0001 在文件中是字面的 \1（反斜杠+1）
old2 = r'Σ|\\frac{(\1)^n}{\2}| = Σ'
new2 = r'Σ\\lvert\\frac{(-1)^n}{n}\\rvert = Σ'
if old2 in content:
    content = content.replace(old2, new2)
    fixes.append('2. sy_gs_ch7_q4 analysis: \\frac{(\\1)^n}{\\2}| → \\lvert\\frac{(-1)^n}{n}\\rvert')
else:
    fixes.append('2. sy_gs_ch7_q4 analysis: 未找到匹配')

# 修复3: sy_p11 和 sy_gl_ch3_q4 - \\begin{cases} 和 \\end{cases} 需要双反斜杠
# 当前文件中是单反斜杠的 \begin{cases}（被JS解释为退格符+egin）
# 需要改为双反斜杠的 \\begin{cases}（JS解释为\begin{cases}）
# 行分隔符 \\ 需要四个反斜杠 \\\\

# sy_p11 content
old3a = r'f(x,y) = \begin{cases} 2\\mathrm{e}^{-(x+2y)}, x>0,y>0 \\ 0, 其他 \end{cases}'
new3a = r'f(x,y) = \\begin{cases} 2\\mathrm{e}^{-(x+2y)}, x>0,y>0 \\\\ 0, 其他 \\end{cases}'
if old3a in content:
    content = content.replace(old3a, new3a)
    fixes.append('3a. sy_p11 content: \\begin→\\\\begin, \\→\\\\\\\\, \\end→\\\\end')
else:
    fixes.append('3a. sy_p11 content: 未找到匹配')

# sy_gl_ch3_q4 content
old3b = r'f(x,y) = \begin{cases} 2\\mathrm{e}^{-(x+2y)}, x>0,y>0 \\ 0, 其他 \end{cases}'
new3b = r'f(x,y) = \\begin{cases} 2\\mathrm{e}^{-(x+2y)}, x>0,y>0 \\\\ 0, 其他 \\end{cases}'
# 注意：sy_gl_ch3_q4 的格式可能略有不同（有空格）
old3b_alt = r'f(x,y) = \begin{cases} 2\\mathrm{e}^{-(x+2y)}, x>0,y>0 \\ 0, 其他 \end{cases}'
if old3b in content:
    count = content.count(old3b)
    content = content.replace(old3b, new3b)
    fixes.append(f'3b. sy_gl_ch3_q4: 同上修复 (替换{count}处)')
else:
    fixes.append('3b. sy_gl_ch3_q4: 未找到匹配（可能已被3a修复）')

# 修复4: ss_gs_ch7_q3 content - \frac 和 \right 用了单反斜杠（JS中 \f 是换页符）
# 当前: \\left(\frac{-1}{2}\right)^{n}
# 正确: \\left(\\frac{-1}{2}\\right)^{n}
old4 = r'\\left(\frac{-1}{2}\right)^{n}'
new4 = r'\\left(\\frac{-1}{2}\\right)^{n}'
if old4 in content:
    content = content.replace(old4, new4)
    fixes.append('4. ss_gs_ch7_q3 content: \\frac→\\\\frac, \\right→\\\\right')
else:
    fixes.append('4. ss_gs_ch7_q3 content: 未找到匹配')

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
