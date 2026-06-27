#!/usr/bin/env python3
"""Comprehensive fix v7: Fix remaining LaTeX errors that v6 missed.
Key insight: In the HTML file, LaTeX commands are stored as \\\\ (two backslash chars)
because they are inside JS strings. So regex needs \\\\ (four backslashes in raw string)
to match two backslash chars.

v6 failed for patterns with MULTIPLE backslash positions (like \\sum (n=1\\to \\infty))
because the regex only matched ONE backslash at each position, but the file has TWO.
The regex would start matching at the 2nd backslash of the first position, but then
fail at subsequent positions because it expected 1 backslash but found 2.

This script fixes: \sum, \lim, \oiint, 点火公式, and other remaining patterns.
"""
import re

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
fix_count = 0

def apply_regex(pattern, replacement, desc):
    """Apply a regex replacement fix."""
    global content, fix_count
    try:
        matches = re.findall(pattern, content)
        if matches:
            count = len(matches)
            content = re.sub(pattern, replacement, content)
            print(f"  Fixed [{count}x]: {desc}")
            fix_count += count
            return True
    except Exception as e:
        print(f"  ERROR in '{desc}': {e}")
    return False

def apply_fix(old, new, desc):
    """Apply a simple string replacement fix."""
    global content, fix_count
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        print(f"  Fixed [{count}x]: {desc}")
        fix_count += count
        return True
    return False

# ============================================================
# Phase A: Fix \sum (n=...\to ...\infty ) patterns
# File stores: \\sum (n=1\\to \\infty )  (two backslashes each)
# Regex needs: \\\\sum\s*\(n=1\\\\to\s*\\\\infty\s*\)
# Replacement: \\\\sum_{n=1}^{\\\\infty}  (two backslashes each)
# ============================================================
print("=== Phase A: Fix \\sum (n=...) patterns ===")
# \sum (n=1\to \infty ) → \sum_{n=1}^{\infty}
apply_regex(
    r'\\\\sum\s*\(n=1\\\\to\s*\\\\infty\s*\)',
    r'\\\\sum_{n=1}^{\\\\infty}',
    '\\sum (n=1\\to \\infty) → \\sum_{n=1}^{\\infty}'
)
# \sum (n=0\to \infty ) → \sum_{n=0}^{\infty}
apply_regex(
    r'\\\\sum\s*\(n=0\\\\to\s*\\\\infty\s*\)',
    r'\\\\sum_{n=0}^{\\\\infty}',
    '\\sum (n=0\\to \\infty) → \\sum_{n=0}^{\\infty}'
)
# Also handle without spaces: \sum(n=1\to\infty)
apply_regex(
    r'\\\\sum\(n=1\\\\to\\\\infty\)',
    r'\\\\sum_{n=1}^{\\\\infty}',
    '\\sum(n=1\\to\\infty) → \\sum_{n=1}^{\\infty}'
)
apply_regex(
    r'\\\\sum\(n=0\\\\to\\\\infty\)',
    r'\\\\sum_{n=0}^{\\\\infty}',
    '\\sum(n=0\\to\\infty) → \\sum_{n=0}^{\\infty}'
)

# ============================================================
# Phase B: Fix \lim(n\to \infty ) patterns
# File stores: \\lim(n\\to \\infty )  (two backslashes each)
# ============================================================
print("\n=== Phase B: Fix \\lim(n...) patterns ===")
# \lim(n\to \infty ) with spaces
apply_regex(
    r'\\\\lim\(n\\\\to\s*\\\\infty\s*\)',
    r'\\\\lim_{n\\\\to\\\\infty}',
    '\\lim(n\\to \\infty) → \\lim_{n\\to\\infty}'
)
# \lim(n\to\infty) without spaces
apply_regex(
    r'\\\\lim\(n\\\\to\\\\infty\)',
    r'\\\\lim_{n\\\\to\\\\infty}',
    '\\lim(n\\to\\infty) → \\lim_{n\\to\\infty}'
)
# \lim(x\to \infty ) with spaces
apply_regex(
    r'\\\\lim\(x\\\\to\s*\\\\infty\s*\)',
    r'\\\\lim_{x\\\\to\\\\infty}',
    '\\lim(x\\to \\infty) → \\lim_{x\\to\\infty}'
)
# \lim(x\to\infty) without spaces
apply_regex(
    r'\\\\lim\(x\\\\to\\\\infty\)',
    r'\\\\lim_{x\\\\to\\\\infty}',
    '\\lim(x\\to\\infty) → \\lim_{x\\to\\infty}'
)
# \lim(x\to 0)
apply_regex(
    r'\\\\lim\(x\\\\to\s*0\s*\)',
    r'\\\\lim_{x\\\\to 0}',
    '\\lim(x\\to 0) → \\lim_{x\\to 0}'
)
# \lim(x\to x_{0})
apply_regex(
    r'\\\\lim\(x\\\\to\s*x_\{0\}\s*\)',
    r'\\\\lim_{x\\\\to x_{0}}',
    '\\lim(x\\to x_{0}) → \\lim_{x\\to x_{0}}'
)
# \lim(\lambda \to 0)
apply_regex(
    r'\\\\lim\(\\\\lambda\\\\to\s*0\s*\)',
    r'\\\\lim_{\\\\lambda\\\\to 0}',
    '\\lim(\\lambda\\to 0) → \\lim_{\\lambda\\to 0}'
)
# \lim(\lambda \to 0) with space after \lambda
apply_regex(
    r'\\\\lim\(\\\\lambda\s*\\\\to\s*0\s*\)',
    r'\\\\lim_{\\\\lambda\\\\to 0}',
    '\\lim(\\lambda \\to 0) → \\lim_{\\lambda\\to 0}'
)

# ============================================================
# Phase C: Fix \oiint _\sum → \oiint_{\sum}
# File stores: \\oiint _\\sum
# ============================================================
print("\n=== Phase C: Fix \\oiint _\\sum ===")
apply_regex(
    r'\\\\oiint\s*_\\\\sum',
    r'\\\\oiint_{\\\\sum}',
    '\\oiint _\\sum → \\oiint_{\\sum}'
)

# ============================================================
# Phase D: Fix 点火公式 stray delimiters
# File stores: \\(\\frac{\\)点火公式}{Wallis}公式）
# Actual chars: \\(\\frac{\\)点火公式}{Wallis}公式）
# Should be: 点火公式（Wallis公式）
# ============================================================
print("\n=== Phase D: Fix 点火公式 stray delimiters ===")
# The full pattern in file: （\\(\\frac{\\)点火公式}{Wallis}公式）
# Replace with: （点火公式（Wallis公式））
# Note: file uses two backslashes for each \\
apply_fix(
    '（\\\\(\\\\frac{\\\\)点火公式}{Wallis}公式）',
    '（点火公式（Wallis公式））',
    '点火公式 stray delimiters (full)'
)
# Also try a regex version in case spacing differs
apply_regex(
    r'（\\\\\(\\\\frac\{\\\\\)点火公式\}\{Wallis\}公式）',
    '（点火公式（Wallis公式））',
    '点火公式 stray delimiters (regex)'
)

# ============================================================
# Phase E: Fix \hat{\theta}^{n} → \hat{\theta}_{n} (Double exponent)
# File stores: \\hat{\\theta}^{n}
# ============================================================
print("\n=== Phase E: Fix \\hat{\\theta}^{n} → \\hat{\\theta}_{n} ===")
apply_regex(
    r'\\\\hat\{\\\\theta\}\^\{(\d+)\}',
    r'\\\\hat{\\\\theta}_{\1}',
    '\\hat{\\theta}^{n} → \\hat{\\theta}_{n}'
)
# Also fix \hat{\theta}^1, \hat{\theta}^2 etc without braces
apply_regex(
    r'\\\\hat\{\\\\theta\}\^(\d+)',
    r'\\\\hat{\\\\theta}_{\1}',
    '\\hat{\\theta}^n (no braces) → \\hat{\\theta}_{n}'
)

# ============================================================
# Phase F: Fix remaining \to followed by letter (no space)
# File stores: \\to followed by letter
# Use \\\\to([a-zA-Z]) to match two backslashes + to + letter
# ============================================================
print("\n=== Phase F: Fix \\to followed by letter ===")
# Don't match if the letter is part of a command like \tox_{0}
# Actually \tox is not a command, so \to followed by x should be \to x
# But be careful: \to\infty is fine (backslash after \to)
# \to followed by a letter (not backslash) needs a space
apply_regex(
    r'\\\\to([a-zA-Z])',
    r'\\\\to \1',
    '\\to + letter → \\to + space + letter'
)

# ============================================================
# Phase G: Fix any remaining \sum(n=...) without space
# ============================================================
print("\n=== Phase G: Fix remaining \\sum patterns ===")
# \sum(n=1\to\infty) without any spaces
apply_regex(
    r'\\\\sum\(n=1\\\\to\\\\infty\)',
    r'\\\\sum_{n=1}^{\\\\infty}',
    '\\sum(n=1\\to\\infty) no space'
)
# \sum (n=1\to \infty ) - already handled above but check again
apply_regex(
    r'\\\\sum\s*\(n=1\\\\to\s*\\\\infty\s*\)',
    r'\\\\sum_{n=1}^{\\\\infty}',
    '\\sum (n=1\\to \\infty) retry'
)

# ============================================================
# Phase H: Fix \lim patterns with Unicode arrow →
# File stores: \\lim(n→∞)  (Unicode arrow and infinity)
# ============================================================
print("\n=== Phase H: Fix \\lim with Unicode arrow ===")
# \lim(n→∞) with Unicode
apply_regex(
    r'\\\\lim\(n→∞\)',
    r'\\\\lim_{n\\\\to\\\\infty}',
    '\\lim(n→∞) → \\lim_{n\\to\\infty}'
)
# \lim(n→+∞)
apply_regex(
    r'\\\\lim\(n→\+∞\)',
    r'\\\\lim_{n\\\\to+\\\\infty}',
    '\\lim(n→+∞) → \\lim_{n\\to+\\infty}'
)
# \lim(x→0)
apply_regex(
    r'\\\\lim\(x→0\)',
    r'\\\\lim_{x\\\\to 0}',
    '\\lim(x→0) → \\lim_{x\\to 0}'
)
# \lim(x→∞)
apply_regex(
    r'\\\\lim\(x→∞\)',
    r'\\\\lim_{x\\\\to\\\\infty}',
    '\\lim(x→∞) → \\lim_{x\\to\\infty}'
)

# ============================================================
# Phase I: Fix 3σ → 3\sigma (if any remaining)
# ============================================================
print("\n=== Phase I: Fix 3σ ===")
apply_fix('3σ 原则', r'3\\sigma 原则', '3σ 原则 → 3\\sigma 原则')
apply_fix('3σ原则', r'3\\sigma原则', '3σ原则 → 3\\sigma原则')

# ============================================================
# Phase J: Fix X−μ → X-\mu (using en-dash or em-dash)
# File may have X−μ (with minus sign U+2212) or X-μ (with hyphen)
# ============================================================
print("\n=== Phase J: Fix X−μ ===")
# X−μ with U+2212 minus
apply_fix('X−μ', r'X-\\\\mu', 'X−μ → X-\\mu')
# X-μ with hyphen
apply_fix('X-μ', r'X-\\\\mu', 'X-μ → X-\\mu')

# Write the file
if content != original:
    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    diff = len(content) - len(original)
    print(f"\n✅ Total fixes applied: {fix_count}")
    print(f"   Character length change: {diff:+d}")
else:
    print("\n⚠️ No changes made.")
