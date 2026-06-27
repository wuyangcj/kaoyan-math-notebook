#!/usr/bin/env python3
# 把 questionBank.supplement 数组中的 "历年真题" 改为 "真题模拟题"
# 但保留真题模考区域（examPaperBank）的 "历年真题" 不变

import re

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    html = f.read()

# questionBank 从第4405行开始，到 const animalAvatars 之前结束
# 找到 questionBank 的范围
qb_start = html.find('const questionBank = ')
qb_end = html.find('const animalAvatars = ', qb_start)
print(f'questionBank 范围: {qb_start} - {qb_end}')

# 只在 questionBank 范围内替换
qb_content = html[qb_start:qb_end]
count = qb_content.count('"source": "历年真题"') + qb_content.count("source: \"历年真题\"")
print(f'找到 {count} 处"历年真题"')

# 替换两种格式
qb_content = qb_content.replace('"source": "历年真题"', '"source": "真题模拟题"')
qb_content = qb_content.replace('source: "历年真题"', 'source: "真题模拟题"')

# 重新组装
html = html[:qb_start] + qb_content + html[qb_end:]

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'已替换 {count} 处 "历年真题" -> "真题模拟题"')
