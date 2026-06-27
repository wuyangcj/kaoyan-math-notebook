#!/usr/bin/env python3
# fix_kb_lt_v4.py - 将知识库详情中误写入的单反斜杠 \lt 修复为双反斜杠 \\lt
# 只修复刚由 fix_kb_lt_v3.py 写入的几处，不影响已有的 \\lt

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
fixes = []

# 修复2: |x|\lt R → |x|\\lt R（单反斜杠改双反斜杠）
old2 = '|x|\\lt R 内绝对收敛'
new2 = '|x|\\\\lt R 内绝对收敛'
if old2 in content:
    content = content.replace(old2, new2)
    fixes.append(f'2. |x|\\lt R → |x|\\\\lt R')
else:
    fixes.append(f'2. 未找到 |x|\\lt R')

# 修复3: r(A)\lt n → r(A)\\lt n
old3 = 'r(A)\\lt n，称 A 为降秩矩阵'
new3 = 'r(A)\\\\lt n，称 A 为降秩矩阵'
if old3 in content:
    content = content.replace(old3, new3)
    fixes.append(f'3. r(A)\\lt n → r(A)\\\\lt n')
else:
    fixes.append(f'3. 未找到 r(A)\\lt n')

# 修复4: f_X(x)=1 (0\xlt x\lt 1) → f_X(x)=1 (0\\lt x\\lt 1)
old4 = 'f_X(x)=1 (0\\lt x\\lt 1)'
new4 = 'f_X(x)=1 (0\\\\lt x\\\\lt 1)'
if old4 in content:
    content = content.replace(old4, new4)
    fixes.append(f'4. 0\\lt x\\lt 1 → 0\\\\lt x\\\\lt 1 (f_X 上下文)')
else:
    fixes.append(f'4. 未找到 f_X(x)=1 上下文')

# 修复5: f(x,y)=2 (0\xlt x\lt 1) → f(x,y)=2 (0\\lt x\\lt 1)
old5 = 'f(x,y)=2 (0\\lt x\\lt 1)'
new5 = 'f(x,y)=2 (0\\\\lt x\\\\lt 1)'
if old5 in content:
    content = content.replace(old5, new5)
    fixes.append(f'5. 0\\lt x\\lt 1 → 0\\\\lt x\\\\lt 1 (f(x,y) 上下文)')
else:
    fixes.append(f'5. 未找到 f(x,y)=2 上下文')

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
