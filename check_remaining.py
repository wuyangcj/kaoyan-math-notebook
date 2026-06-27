#!/usr/bin/env python3
"""Check for remaining unconverted / divisions in shuyi/shuer content/analysis/answer fields."""
import re

with open('/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html', 'r', encoding='utf-8') as f:
    content = f.read()

qb_start = content.index('const questionBank = {')
exam_start = content.index('const examPaperBank = {')
qb_end = content.rfind('};', 0, exam_start)
qb_text = content[qb_start:qb_end+2]

shuyi_start = qb_text.index('"shuyi":')
shuer_start = qb_text.index('"shuer":')
shusan_start = qb_text.index('"shusan":')

shuyi_text = qb_text[shuyi_start:shuer_start]
shuer_text = qb_text[shuer_start:shusan_start]

pattern = r'("(?:content|analysis|answer)"\s*:\s*")((?:[^"\\]|\\.)*)(\")'
remaining = 0
for region_name, region in [('shuyi', shuyi_text), ('shuer', shuer_text)]:
    for m in re.finditer(pattern, region):
        val = m.group(2)
        for i, c in enumerate(val):
            if c == '/':
                if i > 0 and val[i-1] != ':' and i+1 < len(val):
                    before = val[i-1]
                    after = val[i+1]
                    b_ok = before.isalnum() or before in ')]}'
                    a_ok = after.isalnum() or after in '(\\'
                    if b_ok and a_ok:
                        ctx = val[max(0,i-15):i] + '[' + c + ']' + val[i+1:i+16]
                        print(f'{region_name}: ...{ctx}...')
                        remaining += 1

print(f'\nTotal remaining potential divisions: {remaining}')
