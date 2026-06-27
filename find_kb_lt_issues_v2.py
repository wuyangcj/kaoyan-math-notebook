#!/usr/bin/env python3
"""精确查找知识库详情中数学小于号被误解析为HTML标签的位置"""
import re

file_path = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 知识库详情数据范围
START_LINE = 43937
END_LINE = 44330

# 已知的HTML标签列表，用于排除
html_tags = ['h1','h2','h3','h4','h5','h6','p','ul','ol','li','strong','em','code','pre',
             'div','span','br','hr','table','tr','td','th','thead','tbody','img','a',
             'sup','sub','dl','dt','dd','blockquote','q','cite','b','i','u','s']

# 查找所有 < 字符
issues = []
for line_num in range(START_LINE - 1, min(END_LINE, len(lines))):
    line = lines[line_num]
    # 查找所有 < 字符的位置
    for match in re.finditer(r'<', line):
        pos = match.start()
        # 获取 < 后面的内容
        after = line[pos+1:pos+30]
        # 检查是否是HTML标签（已知标签 + / + !）
        is_html_tag = False
        for tag in html_tags:
            if after.startswith(tag) or after.startswith('/' + tag) or after.startswith('!'):
                is_html_tag = True
                break
        # 检查是否是 \( 或 \[ 等 MathJax 定界符
        if after.startswith('\\(') or after.startswith('\\['):
            is_html_tag = True
        if not is_html_tag:
            # 获取上下文
            context_start = max(0, pos - 40)
            context_end = min(len(line), pos + 40)
            context = line[context_start:context_end]
            issues.append((line_num + 1, pos + 1, after[:10], context))

print(f"找到 {len(issues)} 处可能的数学小于号问题:")
for line_num, col, after, context in issues:
    print(f"行{line_num} 列{col}: <{after}  上下文: ...{context}...")

# 同时查找可能是之前 < 被误删除留下的双空格（数学不等式）
print("\n--- 检查可能被删除的 < 留下的双空格 ---")
double_space_issues = []
for line_num in range(START_LINE - 1, min(END_LINE, len(lines))):
    line = lines[line_num]
    # 查找模式: r(A)  n, r(A)  m, r(A)  r 等数学表达式
    for match in re.finditer(r'(r\(A\)|r\(A\|b\)|\|A\|)\s{2,}[nmrA-Za-z]', line):
        pos = match.start()
        context_start = max(0, pos - 30)
        context_end = min(len(line), pos + 50)
        context = line[context_start:context_end]
        double_space_issues.append((line_num + 1, pos + 1, context))

print(f"找到 {len(double_space_issues)} 处可能的双空格问题:")
for line_num, col, context in double_space_issues:
    print(f"行{line_num} 列{col}:  上下文: ...{context}...")
