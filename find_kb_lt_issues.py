#!/usr/bin/env python3
# find_kb_lt_issues.py - 精确查找知识库详情中数学小于号被误解析为HTML标签的位置
import re

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 知识库详情范围（约43937-44320行）
issues = []
known_tags = {'b', 'i', 'p', 'br', 'code', 'div', 'span', 'pre', 'ul', 'ol', 'li',
              'table', 'tr', 'td', 'th', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
              'strong', 'em', 'sup', 'sub', 'blockquote', 'font', 'small', 'big',
              'a', 'img', 'hr', 'dl', 'dt', 'dd', 'caption', 'thead', 'tbody', 'tfoot',
              'col', 'colgroup', 's', 'u', 'mark', 'del', 'ins'}

for line_num, line in enumerate(lines, 1):
    if line_num < 43937 or line_num > 44330:
        continue
    # 查找 < 后跟字母的模式，排除已知HTML标签
    for m in re.finditer(r'<([a-zA-Z])', line):
        char_after = m.group(1)
        # 检查后续字符是否构成已知HTML标签
        after = line[m.start():m.start()+20]
        tag_match = re.match(r'</?(\w+)', after)
        if tag_match and tag_match.group(1).lower() in known_tags:
            continue
        # 这可能是数学小于号
        context = line[max(0, m.start()-20):m.start()+30].strip()
        issues.append({
            'line': line_num,
            'col': m.start(),
            'char': char_after,
            'context': context
        })

print(f'发现 {len(issues)} 处可能的数学小于号问题：\n')
for issue in issues:
    print(f"  行{issue['line']} 列{issue['col']}: <{issue['char']}  上下文: ...{issue['context']}...")
