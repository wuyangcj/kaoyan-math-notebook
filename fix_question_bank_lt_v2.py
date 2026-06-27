#!/usr/bin/env python3
"""
精确修复题库中数学小于号被误解析为HTML标签的问题
关键改进：
1. 只修复题目数据字段（content, options, analysis, answer, hint, formula, tips, approach, desc）
2. 只修复 < 后跟字母且不在 \\(...\\) 内、不在 <code> 内、不是HTML标签的情况
3. 不触碰JS逻辑代码（正则表达式、HTML字符串操作等）
4. 从后往前替换避免位置偏移
5. 替换 < 为 \\lt 时确保前后有空格
"""
import re

file_path = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
fixes = []

# 题库数据范围
# chapterQuestionBank: 行3747-4427
# questionBank: 行4427-41612
# examPaperBank: 行41612-43951
QUESTION_BANK_START = 3747
QUESTION_BANK_END = 43951

# HTML标签集合（完整的合法HTML标签）
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
    """检查 pos 位置的 < 是否是HTML标签的开始"""
    after = line[pos+1:pos+25]
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
    """检查是否在 <code>...</code> 内"""
    before = line[:pos]
    last_open = before.rfind('<code>')
    last_close = before.rfind('</code>')
    return last_open > last_close

def is_inside_math_delim(line, pos):
    """检查是否在 \\(...\\) 内"""
    before = line[:pos]
    after = line[pos:]
    # \( ... \)
    last_open = before.rfind('\\(')
    last_close = before.rfind('\\)')
    if last_open > last_close:
        if after.find('\\)') != -1:
            return True
    return False

def replace_less_than(line, pos):
    """
    将 pos 位置的 < 替换为 \\lt，确保前后有空格
    返回 (new_line, old_context)
    """
    before_char = line[pos-1] if pos > 0 else ''
    after_char = line[pos+1] if pos+1 < len(line) else ''
    
    # 构建替换字符串
    replacement = '\\lt'
    # 如果前面是字母/数字/右括号/竖线，加空格
    if before_char and (before_char.isalnum() or before_char in ')]}|'):
        replacement = ' ' + replacement
    # 如果后面是字母/数字，加空格
    if after_char and after_char.isalnum():
        replacement = replacement + ' '
    
    old_context = line[max(0,pos-20):pos+20]
    new_line = line[:pos] + replacement + line[pos+1:]
    return new_line, old_context

# 遍历题库数据范围
for i in range(QUESTION_BANK_START - 1, min(QUESTION_BANK_END, len(lines))):
    line = lines[i]
    line_num = i + 1
    
    # 跳过注释行
    stripped = line.strip()
    if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
        continue
    
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
        line, old_ctx = replace_less_than(line, pos)
        fixes.append((line_num, old_ctx))
    
    lines[i] = line

# 写回文件
new_content = '\n'.join(lines)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"题库小于号修复完成，共 {len(fixes)} 处:")
from collections import defaultdict
by_line = defaultdict(list)
for ln, ctx in fixes:
    by_line[ln].append(ctx)
for ln in sorted(by_line.keys()):
    items = by_line[ln]
    print(f"  行{ln} ({len(items)}处):")
    for ctx in items[:3]:
        print(f"    上下文: ...{ctx}...")
    if len(items) > 3:
        print(f"    ... 还有 {len(items)-3} 处")
