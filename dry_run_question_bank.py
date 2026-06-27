#!/usr/bin/env python3
"""
试运行：只检查会修复哪些位置，不实际修改文件
重点检查是否会有误伤JS代码的情况
"""
import re

file_path = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
fixes = []

QUESTION_BANK_START = 3747
QUESTION_BANK_END = 43951

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
    before = line[:pos]
    last_open = before.rfind('<code>')
    last_close = before.rfind('</code>')
    return last_open > last_close

def is_inside_math_delim(line, pos):
    before = line[:pos]
    after = line[pos:]
    last_open = before.rfind('\\(')
    last_close = before.rfind('\\)')
    if last_open > last_close:
        if after.find('\\)') != -1:
            return True
    return False

# 检查可能误伤的JS代码模式
js_patterns = [
    r'\.replace\s*\(',  # 字符串替换
    r'\.match\s*\(',    # 正则匹配
    r'\.split\s*\(',    # 字符串分割
    r'innerHTML',       # innerHTML操作
    r'outerHTML',
    r'document\.write',
    r'\.insertAdjacentHTML',
    r'/[^/]+/[gimsuy]*',  # 正则表达式
]

suspicious_fixes = []

for i in range(QUESTION_BANK_START - 1, min(QUESTION_BANK_END, len(lines))):
    line = lines[i]
    line_num = i + 1
    
    stripped = line.strip()
    if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
        continue
    
    for match in re.finditer(r'<([a-zA-Z])', line):
        pos = match.start()
        if is_html_tag_start(line, pos):
            continue
        if is_inside_code_tag(line, pos):
            continue
        if is_inside_math_delim(line, pos):
            continue
        
        # 检查是否在JS代码中
        context = line[max(0,pos-50):pos+50]
        is_suspicious = False
        for pattern in js_patterns:
            if re.search(pattern, context):
                is_suspicious = True
                break
        
        fixes.append((line_num, line[max(0,pos-15):pos+15], is_suspicious, context))
        if is_suspicious:
            suspicious_fixes.append((line_num, context))

print(f"总共会修复 {len(fixes)} 处")
print(f"其中 {len(suspicious_fixes)} 处可能是JS代码（需要检查）:")

if suspicious_fixes:
    for ln, ctx in suspicious_fixes[:20]:
        print(f"  行{ln}: ...{ctx}...")
else:
    print("  无可疑JS代码，可以安全修复")

print(f"\n前20处修复预览:")
for ln, ctx, susp, full_ctx in fixes[:20]:
    marker = " [可疑]" if susp else ""
    print(f"  行{ln}{marker}: ...{ctx}...")
