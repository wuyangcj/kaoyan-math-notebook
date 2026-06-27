#!/usr/bin/env python3
"""检查当前文件行44033的内容，查找 <lir(A) 的问题"""
file_path = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

line = lines[44033 - 1]
# 查找 <lir 的位置
import re
for m in re.finditer(r'<lir', line):
    pos = m.start()
    context = line[max(0,pos-30):pos+50]
    print(f"<lir 位置{pos}: {repr(context)}")

# 查找 <li>若 的位置
for m in re.finditer(r'<li>若', line):
    pos = m.start()
    context = line[max(0,pos-30):pos+50]
    print(f"<li>若 位置{pos}: {repr(context)}")
