#!/usr/bin/env python3
"""Fix the 2 remaining edge cases with square brackets in shuyi/shuer."""

FILE_PATH = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Edge case 1 (shuyi, line ~17897): [(2+h)³ - 2³]/h -> \frac{(2+h)³ - 2³}{h}
old1 = '[(2+h)³ - 2³]/h'
new1 = '\\frac{(2+h)³ - 2³}{h}'

# Edge case 2 (shuer, line ~26889): [ln(\mathrm{e}+h) - ln \mathrm{e}]/h -> \frac{...}{h}
old2 = '[ln(\\mathrm{e}+h) - ln \\mathrm{e}]/h'
new2 = '\\frac{ln(\\mathrm{e}+h) - ln \\mathrm{e}}{h}'

count1 = content.count(old1)
count2 = content.count(old2)
print(f'Found {count1} occurrence(s) of old1')
print(f'Found {count2} occurrence(s) of old2')

content = content.replace(old1, new1)
content = content.replace(old2, new2)

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Replaced {count1 + count2} edge case(s)')
