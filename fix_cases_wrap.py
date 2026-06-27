#!/usr/bin/env python3
# fix_cases_wrap.py - 将 sy_p11 和 sy_gl_ch3_q4 的 cases 环境包裹在 \(...\) 中
FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
fixes = []

# 修复: 将 f(x,y) = \\begin{cases}...\\end{cases} 包裹在 \\(...\\) 中
# 当前: f(x,y) = \\begin{cases} 2\\mathrm{e}^{-(x+2y)}, x>0,y>0 \\\\ 0, 其他 \\end{cases}
# 正确: f(x,y) = \\(\\begin{cases} 2\\mathrm{e}^{-(x+2y)}, x>0,y>0 \\\\ 0, 其他 \\end{cases}\\)
old = r'f(x,y) = \\begin{cases} 2\\mathrm{e}^{-(x+2y)}, x>0,y>0 \\\\ 0, 其他 \\end{cases}'
new = r'f(x,y) = \\(\\begin{cases} 2\\mathrm{e}^{-(x+2y)}, x>0,y>0 \\\\ 0, 其他 \\end{cases}\\)'

count = content.count(old)
if count > 0:
    content = content.replace(old, new)
    fixes.append(f'cases环境包裹\\(...\\): 替换{count}处 (sy_p11 + sy_gl_ch3_q4)')
else:
    fixes.append('cases环境包裹: 未找到匹配')

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
