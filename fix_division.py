#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

def fix_division_in_text(text):
    """将 / 除法转换为 \\frac{}{}。返回 (新文本, 替换次数)。"""
    count = 0

    # 保护 URL、HTML 标签、日期
    protected = []
    def protect(m):
        protected.append(m.group(0))
        return '\x00PROT{}\x00'.format(len(protected) - 1)

    text = re.sub(r'https?://[^\s"\'<>]+', protect, text)
    text = re.sub(r'<[^>]+>', protect, text)
    text = re.sub(r'\d{4}/\d{1,2}/\d{1,2}', protect, text)

    # 1. 处理 (expr)/(expr) → \frac{expr}{expr}（支持嵌套，循环处理）
    prev = None
    while prev != text:
        prev = text
        def repl1(m):
            nonlocal count
            count += 1
            return '\\frac{' + m.group(1) + '}{' + m.group(2) + '}'
        text = re.sub(r'\(([^()]+)\)/\(([^()]+)\)', repl1, text)

    # 2. 处理 [expr]/atom → \frac{expr}{atom}（如 [ln(1+3x)]/x）
    def repl2(m):
        nonlocal count
        count += 1
        return '\\frac{' + m.group(1) + '}{' + m.group(2) + '}'
    text = re.sub(r'\[([^\[\]]+)\]/([\w.]+)', repl2, text)

    # 3. 处理 atom^sup/(expr) → \frac{atom^sup}{expr}（如 2^k/(k!e^2)）
    def repl3(m):
        nonlocal count
        count += 1
        return '\\frac{' + m.group(1) + '}{' + m.group(2) + '}'
    text = re.sub(r'([\w.]+(?:\^[\w.]+)?)/\(([^()]+)\)', repl3, text)

    # 4. 处理 (expr)/atom → \frac{expr}{atom}
    text = re.sub(r'\(([^()]+)\)/([\w.]+)', repl3, text)

    # 5. 处理简单 atom/atom → \frac{atom}{atom}（如 1/2, 0.5/0.75, π/5）
    def repl5(m):
        nonlocal count
        count += 1
        return '\\frac{' + m.group(1) + '}{' + m.group(2) + '}'
    text = re.sub(r'([\w.]+)/([\w.]+)', repl5, text)

    # 还原保护的内容
    text = re.sub(r'\x00PROT(\d+)\x00', lambda m: protected[int(m.group(1))], text)

    return text, count


filepath = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 定位 examPaperBank 区域
start_marker = 'const examPaperBank = {'
start_idx = content.find(start_marker)
if start_idx == -1:
    print("ERROR: examPaperBank not found")
    exit(1)

# 通过花括号计数找到 examPaperBank 的结束位置
brace_count = 0
i = start_idx + len(start_marker) - 1
end_idx = None
while i < len(content):
    if content[i] == '{':
        brace_count += 1
    elif content[i] == '}':
        brace_count -= 1
        if brace_count == 0:
            end_idx = i + 1
            if end_idx < len(content) and content[end_idx] == ';':
                end_idx += 1
            break
    i += 1

if end_idx is None:
    print("ERROR: examPaperBank closing not found")
    exit(1)

# 提取区域
region = content[start_idx:end_idx]

# 修复前统计
slashes_before = region.count('/')
frac_before = region.count('\\frac{')
braces_before = content.count('{')

# 执行修复
fixed_region, count = fix_division_in_text(region)

# 修复后统计
slashes_after = fixed_region.count('/')
frac_after = fixed_region.count('\\frac{')

# 替换并写回
new_content = content[:start_idx] + fixed_region + content[end_idx:]
braces_after = new_content.count('{')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

# 验证
expected_brace_diff = count * 2
ok = (slashes_after < slashes_before
      and frac_after > frac_before
      and (braces_after - braces_before) == expected_brace_diff)

print("修复数量: {}".format(count))
print("验证结果: OK" if ok else "验证结果: ERROR")
