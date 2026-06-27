#!/usr/bin/env python3
"""Fix the remaining edge case with square brackets in shuer (case 2)."""

FILE_PATH = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Edge case 2 (shuer): [ln(\\mathrm{e}+h) - ln \\mathrm{e}]/h -> \\frac{...}{h}
# In the file, \\mathrm is 2 backslash chars. In Python literal, \\\\ = 2 backslashes.
old2 = '[ln(\\\\mathrm{e}+h) - ln \\\\mathrm{e}]/h'
new2 = '\\\\frac{ln(\\\\mathrm{e}+h) - ln \\\\mathrm{e}}{h}'

count2 = content.count(old2)
print(f'Found {count2} occurrence(s) of old2')

content = content.replace(old2, new2)

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Replaced {count2} edge case(s)')
