#!/usr/bin/env python3
# Fix bare subscripts/superscripts in chapterQuestionBank region.

import re

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# chapterQuestionBank region: from "const chapterQuestionBank = " to "const questionBank = "
start_marker = 'const chapterQuestionBank = '
end_marker = 'const questionBank = '

start_idx = content.find(start_marker)
if start_idx == -1:
    print("ERROR: chapterQuestionBank not found")
    exit(1)

end_idx = content.find(end_marker, start_idx + len(start_marker))
if end_idx == -1:
    end_idx = len(content)

region = content[start_idx:end_idx]
original_region = region
fix_count = 0

# Fix \int_0 -> \int_{0}, etc.
for cmd in ['int', 'iint', 'iiint', 'oint', 'oiint', 'sum', 'prod']:
    pattern = re.compile(r'(\\' + cmd + r')_([a-zA-Z0-9])(?![a-zA-Z0-9{}\\])')
    def make_replacer():
        def replacer(m):
            return m.group(1) + '_{' + m.group(2) + '}'
        return replacer
    new_region, cnt = pattern.subn(make_replacer(), region)
    if cnt > 0:
        region = new_region
        fix_count += cnt
        print(f"  \\{cmd}_ fixed: {cnt}")

# Fix }^1 -> }^{1}
pattern = re.compile(r'\}(\^)([a-zA-Z0-9])(?![a-zA-Z0-9{}\\])')
def replacer_sup(m):
    return '}^{' + m.group(2) + '}'
new_region, cnt = pattern.subn(replacer_sup, region)
if cnt > 0:
    region = new_region
    fix_count += cnt
    print(f"  }}^ fixed: {cnt}")

print(f"\nTotal fixes in chapterQuestionBank: {fix_count}")

if region != original_region:
    content = content[:start_idx] + region + content[end_idx:]
    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print("File updated successfully.")
else:
    print("No changes needed.")
