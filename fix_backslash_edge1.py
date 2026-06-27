#!/usr/bin/env python3
"""Fix the backslash issue in edge case 1 - should be 2 backslashes not 1."""

FILE_PATH = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Current (wrong): \frac{(2+h)³ - 2³}{h}  (1 backslash)
# Should be:       \\frac{(2+h)³ - 2³}{h} (2 backslashes)
# In Python: '\\frac' = 1 backslash, '\\\\frac' = 2 backslashes
old = '\\frac{(2+h)³ - 2³}{h}'
new = '\\\\frac{(2+h)³ - 2³}{h}'

count = content.count(old)
print(f'Found {count} occurrence(s) of wrong backslash version')

content = content.replace(old, new)

with open(FILE_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Fixed {count} occurrence(s)')
