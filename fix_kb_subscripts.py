#!/usr/bin/env python3
# Fix bare subscripts/superscripts in knowledgeBaseDetail and knowledgeBaseSupplement
# that cause MathJax "Missing open brace for subscript" errors.

import re

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Find knowledgeBaseDetail and knowledgeBaseSupplement regions
regions = [
    ('knowledgeBaseDetail', 'const knowledgeBaseDetail = ', 'const animalAvatars = '),
    ('knowledgeBaseSupplement', 'const knowledgeBaseSupplement = ', 'const knowledgeNameMap = '),
]

total_fixes = 0

for name, start_marker, end_marker in regions:
    start_idx = content.find(start_marker)
    if start_idx == -1:
        print(f"WARNING: {name} not found")
        continue
    search_from = start_idx + len(start_marker)
    end_idx = content.find(end_marker, search_from)
    if end_idx == -1:
        end_idx = len(content)

    region = content[start_idx:end_idx]
    original_region = region
    fix_count = 0

    # Fix \int_0 -> \int_{0}, \iint_D -> \iint_{D}, etc.
    for cmd in ['int', 'iint', 'iiint', 'oint', 'oiint', 'sum', 'prod']:
        pattern = re.compile(r'(\\' + cmd + r')_([a-zA-Z0-9])(?![a-zA-Z0-9{}\\])')
        def make_replacer(c):
            def replacer(m):
                return m.group(1) + '_{' + m.group(2) + '}'
            return replacer
        new_region, cnt = pattern.subn(make_replacer(cmd), region)
        if cnt > 0:
            region = new_region
            fix_count += cnt
            print(f"  {name}: \\{cmd}_ fixed: {cnt}")

    # Fix }^1 -> }^{1} (bare superscript after closing brace)
    pattern = re.compile(r'\}(\^)([a-zA-Z0-9])(?![a-zA-Z0-9{}\\])')
    def replacer_sup(m):
        return '}^{' + m.group(2) + '}'
    new_region, cnt = pattern.subn(replacer_sup, region)
    if cnt > 0:
        region = new_region
        fix_count += cnt
        print(f"  {name}: }}^ fixed: {cnt}")

    if region != original_region:
        content = content[:start_idx] + region + content[end_idx:]
        total_fixes += fix_count
        print(f"  {name}: total fixes: {fix_count}")

print(f"\nTotal fixes across knowledge base: {total_fixes}")

if total_fixes > 0:
    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print("File updated successfully.")
else:
    print("No changes needed.")
