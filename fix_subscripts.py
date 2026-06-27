#!/usr/bin/env python3
# Fix bare subscripts/superscripts in questionBank that cause MathJax errors.
# Patterns: \int_0 -> \int_{0}, \iint_D -> \iint_{D}, \sum_k -> \sum_{k}
# Also fix variable subscripts: x_0 -> x_{0}, C_1 -> C_{1} (in LaTeX context)

import re

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# Find questionBank region: from "const questionBank =" to the next top-level "const "
start_marker = 'const questionBank = '
end_marker = '\nconst '
start_idx = content.find(start_marker)
if start_idx == -1:
    print("ERROR: questionBank not found")
    exit(1)

# Find the end - look for the next "const " at the start of a line after questionBank
search_from = start_idx + len(start_marker)
# Find closing of questionBank object - look for "\nconst " pattern
end_idx = content.find('\nconst ', search_from)
if end_idx == -1:
    end_idx = len(content)

region = content[start_idx:end_idx]
original_region = region
fix_count = 0

# Pattern 1: \int_ followed by a single char that's not { or \ or (
# \int_0 -> \int_{0}, \int_a -> \int_{a}, \int_1 -> \int_{1}
# But NOT \int_{0} (already correct), \int_\infty (command), \int_( (parenthesized)
def fix_integral_subscript(text, cmd):
    """Fix bare subscripts on integral/sum commands: \int_0 -> \int_{0}"""
    count = 0
    # Match \cmd_ followed by a single alphanumeric char, not followed by { or \ or (
    pattern = re.compile(r'(\\' + cmd + r')_([a-zA-Z0-9])(?![a-zA-Z0-9{}\\])')
    def replacer(m):
        nonlocal count
        count += 1
        return m.group(1) + '_{' + m.group(2) + '}'
    text = pattern.sub(replacer, text)
    return text, count

for cmd in ['int', 'iint', 'iiint', 'oint', 'oiint', 'sum', 'prod', 'bigcup', 'bigcap']:
    region, cnt = fix_integral_subscript(region, cmd)
    fix_count += cnt
    if cnt > 0:
        print(f"  \\{cmd}_ bare subscripts fixed: {cnt}")

# Pattern 2: Fix bare superscripts on integrals: \int_0^1 -> \int_{0}^{1}
# \int_{0}^1 -> \int_{0}^{1} (superscript still bare)
def fix_integral_superscript(text):
    """Fix bare superscripts on integrals: ^1 -> ^{1}, ^\infty is OK (command)"""
    count = 0
    # Match ^ followed by single alphanumeric, not { or \ or ( or )
    pattern = re.compile(r'\^([a-zA-Z0-9])(?![a-zA-Z0-9{}\\])')
    def replacer(m):
        nonlocal count
        count += 1
        return '^{' + m.group(1) + '}'
    text = pattern.sub(replacer, text)
    return text, count

# Only apply superscript fix within LaTeX contexts (after \int, \sum, etc.)
# This is tricky - let's be conservative and only fix ^ after } (like \int_{0}^1)
def fix_superscript_after_brace(text):
    """Fix ^1 after }: }^1 -> }^{1}"""
    count = 0
    pattern = re.compile(r'\}(\^)([a-zA-Z0-9])(?![a-zA-Z0-9{}\\])')
    def replacer(m):
        nonlocal count
        count += 1
        return '}^{' + m.group(2) + '}'
    text = pattern.sub(replacer, text)
    return text, count

region, cnt = fix_superscript_after_brace(region)
fix_count += cnt
if cnt > 0:
    print(f"  }}^ bare superscripts fixed: {cnt}")

# Pattern 3: Fix variable subscripts in LaTeX: x_0 -> x_{0}, C_1 -> C_{1}
# Only fix when preceded by a letter or ) or ] (variable context)
# And NOT when followed by { (already braced) or \ (command) or ( (parenthesized)
def fix_variable_subscript(text):
    """Fix x_0 -> x_{0} but not x_{0} or x_\text"""
    count = 0
    # Match: letter/digit/)] followed by _ followed by single alphanumeric, not followed by { \ (
    pattern = re.compile(r'([a-zA-Z0-9\)\]])_([a-zA-Z0-9])(?![a-zA-Z0-9{}\\])')
    def replacer(m):
        nonlocal count
        count += 1
        return m.group(1) + '_{' + m.group(2) + '}'
    text = pattern.sub(replacer, text)
    return text, count

# This is too aggressive - it would match JS identifiers like practiceState_selected
# Let's only apply it within string values (between quotes)
# Actually, let's skip this for now - the main issue is \int_ patterns

print(f"\nTotal fixes in questionBank: {fix_count}")

if region != original_region:
    content = content[:start_idx] + region + content[end_idx:]
    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    print("File updated successfully.")
else:
    print("No changes needed.")
