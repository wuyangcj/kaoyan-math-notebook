#!/usr/bin/env python3
"""全面检测知识库详情中的数学小于号问题 - 不限定行号范围"""
import re

file_path = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 已知HTML标签列表
html_tags = set(['h1','h2','h3','h4','h5','h6','p','ul','ol','li','strong','em','code','pre',
             'div','span','br','hr','table','tr','td','th','thead','tbody','img','a',
             'sup','sub','dl','dt','dd','blockquote','q','cite','b','i','u','s','font',
             'svg','path','circle','ellipse','rect','line','polyline','polygon','g',
             'defs','use','text','tspan','linearGradient','radialGradient','stop',
             'pattern','mask','clipPath','filter','feGaussianBlur','feOffset','feMerge',
             'feMergeNode','feColorMatrix','animate','animateTransform','animateMotion',
             'style','script','meta','link','head','body','html','title','form','input',
             'button','label','select','option','textarea','canvas','video','audio',
             'source','track','iframe','embed','object','param','map','area','details',
             'summary','dialog','figure','figcaption','main','header','footer','nav',
             'section','article','aside','time','mark','ruby','rt','rp','bdi','bdo',
             'wbr','col','colgroup','caption','optgroup','fieldset','legend','datalist',
             'keygen','output','progress','meter','center','strike','big','small','tt',
             'abbr','address','base','basefont','bgsound','command','data','del','dfn',
             'ins','kbd','menu','menuitem','nobr','noframes','noscript','plaintext',
             'samp','spacer','var','xmp'])

# 查找知识库详情数据范围
# 搜索 "knowledgeBaseDetail" 的位置
kb_start = None
kb_end = None
for i, line in enumerate(lines):
    if 'knowledgeBaseDetail' in line and ':' in line:
        kb_start = i + 1
        break

if kb_start:
    # 找到知识库详情的结束位置（下一个顶级变量声明）
    for i in range(kb_start, min(kb_start + 1000, len(lines))):
        line = lines[i]
        # 检查是否是新的变量声明（如 const, var, let 后跟标识符）
        if re.match(r'\s*(const|var|let)\s+\w+\s*=', line) and i > kb_start + 10:
            kb_end = i + 1
            break
        # 或者检查是否是 knowledgeBaseSupplement 的开始
        if 'knowledgeBaseSupplement' in line and ':' in line and i > kb_start + 10:
            kb_end = i + 1
            break

if not kb_end:
    kb_end = min(kb_start + 500, len(lines)) if kb_start else 0

print(f"知识库详情范围: 行{kb_start}-{kb_end}")

# 查找所有 < 后跟字母的问题
issues = []
double_space_issues = []

for i in range(kb_start - 1 if kb_start else 0, min(kb_end, len(lines))):
    line = lines[i]
    line_num = i + 1
    
    # 查找所有 < 字符
    for match in re.finditer(r'<', line):
        pos = match.start()
        after = line[pos+1:pos+30]
        
        # 检查是否是HTML标签
        is_html_tag = False
        for tag in html_tags:
            if after.lower().startswith(tag) or after.startswith('/' + tag) or after.startswith('!'):
                is_html_tag = True
                break
        if after.startswith('\\(') or after.startswith('\\['):
            is_html_tag = True
        
        if not is_html_tag:
            context_start = max(0, pos - 40)
            context_end = min(len(line), pos + 40)
            context = line[context_start:context_end]
            issues.append((line_num, pos + 1, after[:10], context))
    
    # 查找双空格问题（缺少 <）
    for match in re.finditer(r'(r\(A\)|r\(A\|b\)|\|A\|)\s{2,}[nmrA-Za-z]', line):
        pos = match.start()
        context_start = max(0, pos - 30)
        context_end = min(len(line), pos + 50)
        context = line[context_start:context_end]
        double_space_issues.append((line_num, pos + 1, context))

print(f"\n找到 {len(issues)} 处可能的数学小于号问题:")
for line_num, col, after, context in issues:
    # 只显示 < 后跟字母的问题（最危险的）
    if after and after[0].isalpha():
        print(f"  行{line_num} 列{col}: <{after}  上下文: ...{context}...")

print(f"\n找到 {len(double_space_issues)} 处双空格问题:")
for line_num, col, context in double_space_issues:
    print(f"  行{line_num} 列{col}:  上下文: ...{context}...")
