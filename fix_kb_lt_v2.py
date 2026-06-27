#!/usr/bin/env python3
"""
重新修复知识库详情中的数学小于号问题（行43951-44330）
基于detect_kb_issues.py的检测结果
"""
import re

file_path = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
fixes = []

START = 43951
END = 44330

# HTML标签集合
html_tags = set(['h1','h2','h3','h4','h5','h6','p','ul','ol','li','strong','em','code','pre',
             'div','span','br','hr','table','tr','td','th','thead','tbody','img','a',
             'sup','sub','dl','dt','dd','blockquote','q','cite','b','i','u','s','font',
             'svg','path','circle','ellipse','rect','line','polyline','polygon','g',
             'defs','use','text','tspan','style','script','meta','link','head','body',
             'html','title','form','input','button','label','select','option','textarea',
             'canvas','video','audio','source','track','iframe','embed','object','param',
             'map','area','details','summary','dialog','figure','figcaption','main','header',
             'footer','nav','section','article','aside','time','mark','ruby','rt','rp',
             'bdi','bdo','wbr','col','colgroup','caption','optgroup','fieldset','legend',
             'datalist','keygen','output','progress','meter','center','strike','big',
             'small','tt','abbr','address','base','basefont','bgsound','command','data',
             'del','dfn','ins','kbd','menu','menuitem','nobr','noframes','noscript',
             'plaintext','samp','spacer','var','xmp'])

def is_html_tag_start(line, pos):
    after = line[pos+1:pos+20]
    if after.startswith('/'):
        m = re.match(r'/(\w+)', after)
        if m and m.group(1).lower() in html_tags:
            return True
        return False
    if after.startswith('!'):
        return True
    m = re.match(r'(\w+)', after)
    if m and m.group(1).lower() in html_tags:
        return True
    return False

def is_inside_code_tag(line, pos):
    before = line[:pos]
    last_open = before.rfind('<code>')
    last_close = before.rfind('</code>')
    return last_open > last_close

def is_inside_math_delim(line, pos):
    before = line[:pos]
    after = line[pos:]
    # \( ... \)
    last_open = before.rfind('\\(')
    last_close = before.rfind('\\)')
    if last_open > last_close:
        if after.find('\\)') != -1:
            return True
    return False

# 收集所有需要修复的位置
for i in range(START - 1, min(END, len(lines))):
    line = lines[i]
    line_num = i + 1
    
    # 查找所有 < 后跟字母的位置
    positions_to_fix = []
    for match in re.finditer(r'<([a-zA-Z])', line):
        pos = match.start()
        if is_html_tag_start(line, pos):
            continue
        if is_inside_code_tag(line, pos):
            continue
        if is_inside_math_delim(line, pos):
            continue
        positions_to_fix.append(pos)
    
    # 从后往前替换，避免位置偏移
    for pos in reversed(positions_to_fix):
        old_char = line[pos:pos+5]
        context = line[max(0,pos-20):pos+20]
        line = line[:pos] + '\\lt' + line[pos+1:]
        fixes.append((line_num, old_char, context))
    
    lines[i] = line

# 查找双空格问题（缺少<）
double_space_fixes = []
for i in range(START - 1, min(END, len(lines))):
    line = lines[i]
    line_num = i + 1
    for match in re.finditer(r'(r\(A\)|r\(A\|b\)|\|A\|)\s{2,}[nmr]', line):
        pos = match.start()
        # 找到双空格的位置并替换为 \lt
        full_match = match.group(0)
        # 替换双空格为 \lt
        new_full = re.sub(r'\s{2,}', ' \\\\lt ', full_match)
        line = line[:pos] + new_full + line[match.end():]
        context = line[max(0,pos-20):pos+30]
        double_space_fixes.append((line_num, full_match, context))
    lines[i] = line

# 写回文件
new_content = '\n'.join(lines)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"小于号修复完成，共 {len(fixes)} 处:")
from collections import defaultdict
by_line = defaultdict(list)
for ln, old, ctx in fixes:
    by_line[ln].append((old, ctx))
for ln in sorted(by_line.keys()):
    items = by_line[ln]
    print(f"  行{ln} ({len(items)}处):")
    for old, ctx in items[:2]:
        print(f"    {old}  上下文: ...{ctx}...")
    if len(items) > 2:
        print(f"    ... 还有 {len(items)-2} 处")

print(f"\n双空格修复完成，共 {len(double_space_fixes)} 处:")
for ln, old, ctx in double_space_fixes:
    print(f"  行{ln}: {old} → 上下文: ...{ctx}...")
