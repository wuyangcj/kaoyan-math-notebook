#!/usr/bin/env python3
"""检查bak2中行44033的原始内容"""
file_path = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html.bak2'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

line = lines[44033 - 1]
import re
# 查找 r(A)  r(A|b) 的上下文
for m in re.finditer(r'r\(A\)\s{2,}r\(A\|b\)', line):
    pos = m.start()
    context = line[max(0,pos-50):pos+80]
    print(f"位置{pos}: {repr(context)}")
