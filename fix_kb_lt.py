#!/usr/bin/env python3
# fix_kb_lt.py - 修复知识库中数学小于号 < 被浏览器误解析为HTML标签的问题
# 将知识库内容中的数学 < 替换为 \\lt（LaTeX小于号命令）
FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
fixes = []

# 修复1: j<i\\le n → j\\lt i\\le n (范德蒙德行列式, 行 44017, 44237)
old1 = r'j<i\le n'
new1 = r'j\\lt i\le n'
count1 = content.count(old1)
if count1 > 0:
    content = content.replace(old1, new1)
    fixes.append(f'1. j<i\\le n → j\\lt i\\le n: {count1}处 (范德蒙德行列式)')

# 修复2: i_{1}<i_{2} → i_{1}\\lt i_{2} (事件独立性, 行 44294)
old2 = r'i_{1}<i_{2}'
new2 = r'i_{1}\\lt i_{2}'
count2 = content.count(old2)
if count2 > 0:
    content = content.replace(old2, new2)
    fixes.append(f'2. i_{{1}}<i_{{2}} → i_{{1}}\\lt i_{{2}}: {count2}处 (事件独立性)')

# 修复3: <i_{k} → \\lt i_{k} (事件独立性, 行 44294) — 注意这是 <...<i_{k} 中的 <i_{k}
old3 = r'<i_{k}'
new3 = r'\\lt i_{k}'
count3 = content.count(old3)
if count3 > 0:
    content = content.replace(old3, new3)
    fixes.append(f'3. <i_{{k}} → \\lt i_{{k}}: {count3}处 (事件独立性)')

# 修复4: x_{1}<x_{2} → x_{1}\\lt x_{2} (随机变量与分布函数, 行 44304)
old4 = r'x_{1}<x_{2}'
new4 = r'x_{1}\\lt x_{2}'
count4 = content.count(old4)
if count4 > 0:
    content = content.replace(old4, new4)
    fixes.append(f'4. x_{{1}}<x_{{2}} → x_{{1}}\\lt x_{{2}}: {count4}处 (分布函数单调性)')

# 修复5: r(A)<r(A|b) → r(A)\\lt r(A|b) (矩阵的秩, 方程组解的结构, 行 44252, 44262)
old5 = r'r(A)<r(A|b)'
new5 = r'r(A)\\lt r(A|b)'
count5 = content.count(old5)
if count5 > 0:
    content = content.replace(old5, new5)
    fixes.append(f'5. r(A)<r(A|b) → r(A)\\lt r(A|b): {count5}处 (矩阵的秩/方程组)')

# 修复6: 修复数据中缺失的 < 号 (行 44262 表格中 r(A)n 应为 r(A)<n)
# 注意: 只修复知识库范围的表格内容
# <td>r(A)n</td> → <td>r(A)\\lt n</td>
old6a = r'<td>r(A)n</td>'
new6a = r'<td>r(A)\\lt n</td>'
count6a = content.count(old6a)
if count6a > 0:
    content = content.replace(old6a, new6a)
    fixes.append(f'6a. <td>r(A)n</td> → <td>r(A)\\lt n</td>: {count6a}处 (修复缺失小于号)')

# <td>r(A)=r(A|b)n</td> → <td>r(A)=r(A|b)\\lt n</td>
old6b = r'<td>r(A)=r(A|b)n</td>'
new6b = r'<td>r(A)=r(A|b)\\lt n</td>'
count6b = content.count(old6b)
if count6b > 0:
    content = content.replace(old6b, new6b)
    fixes.append(f'6b. <td>r(A)=r(A|b)n</td> → <td>r(A)=r(A|b)\\lt n</td>: {count6b}处 (修复缺失小于号)')

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

if not fixes:
    print('  (无匹配)')
