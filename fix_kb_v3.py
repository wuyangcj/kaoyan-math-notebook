#!/usr/bin/env python3
"""
Fix remaining LaTeX issues - targeted fix for knowledge base section only.
Only applies single-backslash fixes to lines 43939-44320 (knowledge base).
"""

import re

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Knowledge base section: lines 43939-44320 (0-indexed: 43938-44319)
# AI knowledge base section: lines 47843-47920 (0-indexed: 47842-47919)
KB_START = 43938
KB_END = 44320
AI_KB_START = 47842
AI_KB_END = 47920

def fix_single_backslash_in_line(line):
    """Fix single-backslash LaTeX commands to double-backslash in a single line."""
    # Commands to fix (single backslash → double backslash)
    # Only fix when NOT preceded by another backslash and NOT followed by a letter
    # (to avoid breaking \neq, \int, \infty, etc.)
    commands = [
        # (pattern, replacement)
        (r'(?<!\\)\\lim(?![a-zA-Z])', r'\\\\lim'),
        (r'(?<!\\)\\sum(?![a-zA-Z])', r'\\\\sum'),
        (r'(?<!\\)\\sqrt(?![a-zA-Z])', r'\\\\sqrt'),
        (r'(?<!\\)\\frac(?![a-zA-Z])', r'\\\\frac'),
        (r'(?<!\\)\\to(?![a-zA-Z])', r'\\\\to'),
        (r'(?<!\\)\\in(?![a-zA-Z])', r'\\\\in'),
        (r'(?<!\\)\\ne(?![a-zA-Z])', r'\\\\ne'),
        (r'(?<!\\)\\equiv(?![a-zA-Z])', r'\\\\equiv'),
        (r'(?<!\\)\\Delta(?![a-zA-Z])', r'\\\\Delta'),
        (r'(?<!\\)\\alpha(?![a-zA-Z])', r'\\\\alpha'),
        (r'(?<!\\)\\beta(?![a-zA-Z])', r'\\\\beta'),
        (r'(?<!\\)\\gamma(?![a-zA-Z])', r'\\\\gamma'),
        (r'(?<!\\)\\lambda(?![a-zA-Z])', r'\\\\lambda'),
        (r'(?<!\\)\\mu(?![a-zA-Z])', r'\\\\mu'),
        (r'(?<!\\)\\sigma(?![a-zA-Z])', r'\\\\sigma'),
        (r'(?<!\\)\\rho(?![a-zA-Z])', r'\\\\rho'),
        (r'(?<!\\)\\xi(?![a-zA-Z])', r'\\\\xi'),
        (r'(?<!\\)\\eta(?![a-zA-Z])', r'\\\\eta'),
        (r'(?<!\\)\\theta(?![a-zA-Z])', r'\\\\theta'),
        (r'(?<!\\)\\pi(?![a-zA-Z])', r'\\\\pi'),
        (r'(?<!\\)\\phi(?![a-zA-Z])', r'\\\\phi'),
        (r'(?<!\\)\\partial(?![a-zA-Z])', r'\\\\partial'),
        (r'(?<!\\)\\infty(?![a-zA-Z])', r'\\\\infty'),
        (r'(?<!\\)\\cdot(?![a-zA-Z])', r'\\\\cdot'),
        (r'(?<!\\)\\cdots(?![a-zA-Z])', r'\\\\cdots'),
        (r'(?<!\\)\\ldots(?![a-zA-Z])', r'\\\\ldots'),
        (r'(?<!\\)\\cos(?![a-zA-Z])', r'\\\\cos'),
        (r'(?<!\\)\\sin(?![a-zA-Z])', r'\\\\sin'),
        (r'(?<!\\)\\tan(?![a-zA-Z])', r'\\\\tan'),
        (r'(?<!\\)\\ln(?![a-zA-Z])', r'\\\\ln'),
        (r'(?<!\\)\\log(?![a-zA-Z])', r'\\\\log'),
        (r'(?<!\\)\\le(?![a-zA-Z])', r'\\\\le'),
        (r'(?<!\\)\\leq(?![a-zA-Z])', r'\\\\leq'),
        (r'(?<!\\)\\ge(?![a-zA-Z])', r'\\\\ge'),
        (r'(?<!\\)\\geq(?![a-zA-Z])', r'\\\\geq'),
        (r'(?<!\\)\\neq(?![a-zA-Z])', r'\\\\neq'),
        (r'(?<!\\)\\pm(?![a-zA-Z])', r'\\\\pm'),
        (r'(?<!\\)\\mp(?![a-zA-Z])', r'\\\\mp'),
        (r'(?<!\\)\\times(?![a-zA-Z])', r'\\\\times'),
        (r'(?<!\\)\\div(?![a-zA-Z])', r'\\\\div'),
        (r'(?<!\\)\\int(?![a-zA-Z])', r'\\\\int'),
        (r'(?<!\\)\\iint(?![a-zA-Z])', r'\\\\iint'),
        (r'(?<!\\)\\iiint(?![a-zA-Z])', r'\\\\iiint'),
        (r'(?<!\\)\\oint(?![a-zA-Z])', r'\\\\oint'),
        (r'(?<!\\)\\prod(?![a-zA-Z])', r'\\\\prod'),
        (r'(?<!\\)\\Omega(?![a-zA-Z])', r'\\\\Omega'),
        (r'(?<!\\)\\bar(?![a-zA-Z])', r'\\\\bar'),
        (r'(?<!\\)\\hat(?![a-zA-Z])', r'\\\\hat'),
        (r'(?<!\\)\\vec(?![a-zA-Z])', r'\\\\vec'),
        (r'(?<!\\)\\det(?![a-zA-Z])', r'\\\\det'),
        (r'(?<!\\)\\dim(?![a-zA-Z])', r'\\\\dim'),
        (r'(?<!\\)\\max(?![a-zA-Z])', r'\\\\max'),
        (r'(?<!\\)\\min(?![a-zA-Z])', r'\\\\min'),
        (r'(?<!\\)\\sup(?![a-zA-Z])', r'\\\\sup'),
        (r'(?<!\\)\\inf(?![a-zA-Z])', r'\\\\inf'),
        (r'(?<!\\)\\arcsin(?![a-zA-Z])', r'\\\\arcsin'),
        (r'(?<!\\)\\arccos(?![a-zA-Z])', r'\\\\arccos'),
        (r'(?<!\\)\\arctan(?![a-zA-Z])', r'\\\\arctan'),
        (r'(?<!\\)\\sec(?![a-zA-Z])', r'\\\\sec'),
        (r'(?<!\\)\\csc(?![a-zA-Z])', r'\\\\csc'),
        (r'(?<!\\)\\cot(?![a-zA-Z])', r'\\\\cot'),
        (r'(?<!\\)\\liminf(?![a-zA-Z])', r'\\\\liminf'),
        (r'(?<!\\)\\limsup(?![a-zA-Z])', r'\\\\limsup'),
        (r'(?<!\\)\\exp(?![a-zA-Z])', r'\\\\exp'),
        (r'(?<!\\)\\hom(?![a-zA-Z])', r'\\\\hom'),
        (r'(?<!\\)\\ker(?![a-zA-Z])', r'\\\\ker'),
        (r'(?<!\\)\\deg(?![a-zA-Z])', r'\\\\deg'),
        (r'(?<!\\)\\gcd(?![a-zA-Z])', r'\\\\gcd'),
        (r'(?<!\\)\\arg(?![a-zA-Z])', r'\\\\arg'),
        (r'(?<!\\)\\Pr(?![a-zA-Z])', r'\\\\Pr'),
    ]
    
    for pattern, replacement in commands:
        line = re.sub(pattern, replacement, line)
    
    return line

# Also merge consecutive subscripts and superscripts
def merge_consecutive_braced(text, char):
    """Merge {char}{A}{char}{B} → {char}{AB} for char being ^ or _"""
    pattern = re.compile(re.escape(char) + r'\{([^}]+)\}' + re.escape(char) + r'\{([^}]+)\}')
    while True:
        new_text = pattern.sub(char + r'{\1\2}', text)
        if new_text == text:
            break
        text = new_text
    return text

changes = 0
for i in range(len(lines)):
    # Only fix knowledge base and AI knowledge base sections
    if (KB_START <= i <= KB_END) or (AI_KB_START <= i <= AI_KB_END):
        original_line = lines[i]
        # Merge consecutive subscripts/superscripts first
        lines[i] = merge_consecutive_braced(lines[i], '_')
        lines[i] = merge_consecutive_braced(lines[i], '^')
        # Fix single-backslash commands
        lines[i] = fix_single_backslash_in_line(lines[i])
        if lines[i] != original_line:
            changes += 1

# Also fix the specific broken derivative pattern globally
content = ''.join(lines)
content = content.replace(
    '\\\\sum(n a_{n}x^{n}-1)',
    '\\\\sum n a_{n}x^{n-1}'
)

# Write the fixed content
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed {changes} lines in knowledge base sections.")
print("Second pass fixes applied successfully.")
