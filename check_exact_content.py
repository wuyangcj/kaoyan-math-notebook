#!/usr/bin/env python3
"""检查行44197和44311中的实际内容"""
file_path = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 行44197 - 查找 < 1 附近的上下文
line = lines[44197 - 1]
# 查找 e}} < 1 的位置
import re
for m in re.finditer(r'e\}\} < 1', line):
    pos = m.start()
    context = line[max(0,pos-20):pos+30]
    print(f"行44197 列{pos}: ...{repr(context)}...")

# 行44311 - 查找 chi^{2}< 的上下文
line = lines[44311 - 1]
for m in re.finditer(r'chi\^\{2\}<', line):
    pos = m.start()
    context = line[max(0,pos-20):pos+40]
    print(f"行44311 列{pos}: ...{repr(context)}...")
