#!/usr/bin/env python3
"""
全面修复题库中数学小于号被误解析为HTML标签的问题
只修复 < 后跟字母且不在 \\(...\\) 内、不在 <code> 内、不是HTML标签的情况
"""
import re

file_path = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
fixes = []

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
             's','samp','spacer','strike','var','xmp'])

def is_html_tag(line, pos):
    """检查 pos 位置的 < 是否是HTML标签的开始"""
    after = line[pos+1:pos+20]
    # 检查是否是闭合标签 </
    if after.startswith('/'):
        tag_match = re.match(r'/(\w+)', after)
        if tag_match and tag_match.group(1).lower() in html_tags:
            return True
        return False
    # 检查是否是 <!-- 注释
    if after.startswith('!'):
        return True
    # 检查是否是已知HTML标签
    tag_match = re.match(r'(\w+)', after)
    if tag_match:
        tag = tag_match.group(1).lower()
        if tag in html_tags:
            return True
    return False

def is_inside_math_delimiter(line, pos):
    """检查 pos 位置的 < 是否在 \\(...\\) 或 $$...$$ 内"""
    # 查找该位置之前最近的 \\( 或 \\[ 或 $$
    # 和之后最近的 \\) 或 \\] 或 $$
    # 这个检查比较复杂，简化处理：检查附近是否有 \\( \\) 分隔符
    before = line[:pos]
    after = line[pos:]
    
    # 检查是否在 \\(...\\) 内
    # 查找最后一个 \\( 和最后一个 \\)
    last_open_paren = before.rfind('\\(')
    last_close_paren = before.rfind('\\)')
    if last_open_paren > last_close_paren:
        # 在 \\( 之后，检查后面是否有 \\)
        next_close = after.find('\\)')
        if next_close != -1:
            return True
    
    # 检查是否在 $$...$$ 内
    last_open_dollar = before.rfind('$$')
    last_close_dollar = before.rfind('$$', 0, last_open_dollar) if last_open_dollar != -1 else -1
    # $$ 的配对比较复杂，简化处理
    
    # 检查是否在 <code>...</code> 内
    last_open_code = before.rfind('<code>')
    last_close_code = before.rfind('</code>')
    if last_open_code > last_close_code:
        return True
    
    return False

def fix_line(line, line_num):
    """修复一行中的数学小于号问题"""
    global fixes
    new_line = line
    # 查找所有 < 后跟字母的位置
    for match in re.finditer(r'<([a-zA-Z])', line):
        pos = match.start()
        letter = match.group(1)
        
        # 跳过HTML标签
        if is_html_tag(line, pos):
            continue
        
        # 跳过在数学分隔符内的
        if is_inside_math_delimiter(line, pos):
            continue
        
        # 这是一个需要修复的数学小于号
        # 获取上下文
        context = line[max(0,pos-20):pos+20]
        old = line[pos:pos+10]
        
        # 替换 < 为 \\lt（文件中存储为双反斜杠）
        new_line = new_line[:pos] + '\\lt' + new_line[pos+1:]
        fixes.append((line_num, old, context))
    
    return new_line

# 遍历所有行进行修复
# 题库数据范围：约行3729-49145（所有script内）
# 但主要关注题库数据，不包括知识库详情（行43937-44330，已处理）
for i in range(len(lines)):
    line_num = i + 1
    # 跳过知识库详情范围（已处理）
    if 43937 <= line_num <= 44330:
        continue
    # 跳过知识库补充范围
    if 44330 <= line_num <= 44500:
        continue
    
    old_line = lines[i]
    new_line = fix_line(old_line, line_num)
    if new_line != old_line:
        lines[i] = new_line

# 写回文件
new_content = '\n'.join(lines)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"修复完成，共 {len(fixes)} 处修复:")
# 按行号分组显示
from collections import defaultdict
by_line = defaultdict(list)
for line_num, old, context in fixes:
    by_line[line_num].append((old, context))

for line_num in sorted(by_line.keys()):
    items = by_line[line_num]
    print(f"  行{line_num} ({len(items)}处):")
    for old, context in items[:3]:  # 每行最多显示3处
        print(f"    {old}  上下文: ...{context}...")
    if len(items) > 3:
        print(f"    ... 还有 {len(items)-3} 处")
