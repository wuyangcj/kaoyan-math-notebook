#!/usr/bin/env python3
"""Fix the ASCII apostrophe issue in mathSegmentRegex and wrapMathInHtmlText split regex.
Replace ASCII apostrophe pair (U+0027 U+0027) with Unicode curly quotes (U+2018 U+2019).
"""
import sys

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# ASCII apostrophe (U+0027) - we want to replace the pair '' in the regex character classes
ASCII_APOS = '\x27'  # U+0027
LEFT_SQUOTE = '\u2018'   # ' left single quotation mark
RIGHT_SQUOTE = '\u2019'  # ' right single quotation mark

# The two lines to fix:
# Line 45653: const mathSegmentRegex = /([^\u4e00-\u9fff，。；：！？（）【】""''、…—]+)/g;
# Line 47331: const segments = text.split(/([\u4e00-\u9fff，。；：！？（）【】""''、…—]+)/);

# Strategy: find lines containing both 'u4e00' and 'u9fff' and the regex pattern,
# then replace ASCII apostrophe pairs with curly quotes

lines = content.split('\n')
fixed_count = 0

for i, line in enumerate(lines):
    if 'u4e00' in line and 'u9fff' in line and ('mathSegmentRegex' in line or 'split(' in line):
        # Check if this line has ASCII apostrophes in the character class
        # The pattern is: after the "" (double quotes) and before the 、
        # We need to find '' (two ASCII apostrophes) and replace with '' (curly quotes)
        if ASCII_APOS + ASCII_APOS in line:
            new_line = line.replace(ASCII_APOS + ASCII_APOS, LEFT_SQUOTE + RIGHT_SQUOTE)
            print(f"Fixed line {i+1}:")
            print(f"  Before: {line.strip()[:120]}")
            print(f"  After:  {new_line.strip()[:120]}")
            lines[i] = new_line
            fixed_count += 1

if fixed_count == 0:
    print("ERROR: No lines found to fix!")
    sys.exit(1)

content = '\n'.join(lines)

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\nFixed {fixed_count} lines.")

# Verify the fix
with open(FILE, 'r', encoding='utf-8') as f:
    verify_content = f.read()

verify_lines = verify_content.split('\n')
for i, line in enumerate(verify_lines):
    if 'u4e00' in line and 'u9fff' in line and ('mathSegmentRegex' in line or 'split(' in line):
        has_ascii = ASCII_APOS + ASCII_APOS in line
        has_curly = LEFT_SQUOTE + RIGHT_SQUOTE in line
        print(f"Line {i+1}: ASCII pair={has_ascii}, Curly pair={has_curly}")
