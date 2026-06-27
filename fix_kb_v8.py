#!/usr/bin/env python3
"""Comprehensive fix v8: Fix all remaining LaTeX errors in knowledge base.
Uses simple string replacement (str.replace) with raw strings for safety.
Key insight: In the HTML file, LaTeX commands in knowledge base are stored as \\\\ (two backslash chars)
because they are inside JS strings. So r'\\\\' (raw string with two backslashes) matches file's \\\\ (two backslashes).
Only modifies knowledge base data, does NOT delete original content.
"""
import re

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
fix_count = 0

def apply_fix(old, new, desc):
    """Apply a simple string replacement fix. Uses raw strings."""
    global content, fix_count
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        print(f"  Fixed [{count}x]: {desc}")
        fix_count += count
        return True
    return False

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

# ============================================================
# In the file, knowledge base content stores \\ (two backslash chars) for each LaTeX backslash.
# So r'\\neu' (raw string = two backslash + neu) matches file's \\neu.
# ============================================================

# ============================================================
# Phase 1: Fix \ne followed by letter (not \neq)
# \neu → \ne u, \nef → \ne f
# ============================================================
print("=== Phase 1: Fix \\ne + letter ===")
apply_fix(r'\\neu_{0}', r'\\ne u_{0}', '\\neu_{0} → \\ne u_{0}')
apply_fix(r'\\nef(b)', r'\\ne f(b)', '\\nef(b) → \\ne f(b)')
apply_fix(r'\\ne1', r'\\ne 1', '\\ne1 → \\ne 1')

# ============================================================
# Phase 2: Fix \le followed by letter (not \leq, \left, etc.)
# ============================================================
print("\n=== Phase 2: Fix \\le + letter ===")
apply_fix(r'\\let\\le\\beta', r'\\le t\\le\\beta', '\\alpha\\let\\le\\beta → \\alpha\\le t\\le\\beta')
apply_fix(r'0\\leu_{n}\\lev_{n}', r'0\\le u_{n}\\le v_{n}', '0\\leu_{n}\\lev_{n} → 0\\le u_{n}\\le v_{n}')
apply_fix(r'1\\lei_{1}i_{2}...i_{k}\\le n', r'1\\le i_{1}<i_{2}<...<i_{k}\\le n', '1\\lei_{1}... → 1\\le i_{1}<i_{2}<...')

# ============================================================
# Phase 3: Fix missing comparison operators in 极限卡片
# |f(x)-A|\varepsilon → |f(x)-A|<\varepsilon
# A0（0） → A>0（>0）
# f(x)0（0） → f(x)>0（>0）
# A0 或讨论 → A>0 或讨论
# ============================================================
print("\n=== Phase 3: Fix missing comparison operators in 极限 ===")
apply_fix(r'|f(x)-A|\\varepsilon', r'|f(x)-A|<\\varepsilon', '|f(x)-A|\\varepsilon → |f(x)-A|<\\varepsilon')
apply_fix(r'\\lim f(x)=A0（0）', r'\\lim f(x)=A>0（>0）', '\\lim f(x)=A0（0） → A>0（>0）')
apply_fix(r'f(x)0（0）', r'f(x)>0（>0）', 'f(x)0（0） → f(x)>0（>0）')
apply_fix(r'A0 或讨论', r'A>0 或讨论', 'A0 或讨论 → A>0 或讨论')

# ============================================================
# Phase 4: Fix \lim(var\to ...) → \lim_{var\to ...}
# These appear in multiple cards: 函数连续性, 反常积分, 基本求导公式, 多元函数微分学, 方向导数与梯度, 随机变量与分布函数, 洛必达法则
# ============================================================
print("\n=== Phase 4: Fix \\lim(var\\to ...) → \\lim_{var\\to ...} ===")

# \lim(\Delta x\to 0) → \lim_{\Delta x\to 0}
apply_fix(r'\\lim(\\Delta x\\to 0)', r'\\lim_{\\Delta x\\to 0}', '\\lim(\\Delta x\\to 0)')
apply_fix(r'\\lim(\\Delta x\\to0)', r'\\lim_{\\Delta x\\to 0}', '\\lim(\\Delta x\\to0)')
apply_fix(r'\\lim(\\Delta x\\to 0 )', r'\\lim_{\\Delta x\\to 0}', '\\lim(\\Delta x\\to 0 )')

# \lim(x\to x_{0}^{-}) → \lim_{x\to x_{0}^{-}}
apply_fix(r'\\lim(x\\to x_{0}^{-})', r'\\lim_{x\\to x_{0}^{-}}', '\\lim(x\\to x_{0}^{-})')
apply_fix(r'\\lim(x\\to x_{0}^{+})', r'\\lim_{x\\to x_{0}^{+}}', '\\lim(x\\to x_{0}^{+})')
apply_fix(r'\\lim(x\\to x_{0}+)', r'\\lim_{x\\to x_{0}+}', '\\lim(x\\to x_{0}+)')

# \lim(x\to a^{+}) → \lim_{x\to a^{+}}
apply_fix(r'\\lim(x\\to a^{+})', r'\\lim_{x\\to a^{+}}', '\\lim(x\\to a^{+})')

# \lim(t\to +\infty ) → \lim_{t\to +\infty}
apply_fix(r'\\lim(t\\to +\\infty )', r'\\lim_{t\\to +\\infty}', '\\lim(t\\to +\\infty )')
apply_fix(r'\\lim(t\\to -\\infty )', r'\\lim_{t\\to -\\infty}', '\\lim(t\\to -\\infty )')

# \lim(t\to 0^{+}) → \lim_{t\to 0^{+}}
apply_fix(r'\\lim(t\\to 0^{+})', r'\\lim_{t\\to 0^{+}}', '\\lim(t\\to 0^{+})')

# \lim(\varepsilon \to 0^{+}) → \lim_{\varepsilon \to 0^{+}}
apply_fix(r'\\lim(\\varepsilon \\to 0^{+})', r'\\lim_{\\varepsilon \\to 0^{+}}', '\\lim(\\varepsilon \\to 0^{+})')

# \lim(x\to -\infty ) → \lim_{x\to -\infty}
apply_fix(r'\\lim(x\\to -\\infty )', r'\\lim_{x\\to -\\infty}', '\\lim(x\\to -\\infty )')

# \lim(x\to +\infty ) → \lim_{x\to +\infty}
apply_fix(r'\\lim(x\\to +\\infty )', r'\\lim_{x\\to +\\infty}', '\\lim(x\\to +\\infty )')

# \lim(x\to+\infty) → \lim_{x\to+\infty}  (no spaces)
apply_fix(r'\\lim(x\\to+\\infty)', r'\\lim_{x\\to+\\infty}', '\\lim(x\\to+\\infty)')

# \lim(x\to a) → \lim_{x\to a} (洛必达法则)
# This appears in: \lim(x\to a) [\frac{f'(x)}{g'(x)}]
# Use double-quoted raw strings to handle apostrophes in f'(x)
apply_fix(r"\\lim(x\\to a) [\\frac{f'(x)}{g'(x)}]", r"\\lim_{x\\to a} \\frac{f'(x)}{g'(x)}", "\\lim(x\\to a) [\\frac{f'(x)}{g'(x)}]")
apply_fix(r"\\lim(x\\to a) [\\frac{f(x)}{g(x)}]", r"\\lim_{x\\to a} \\frac{f(x)}{g(x)}", "\\lim(x\\to a) [\\frac{f(x)}{g(x)}]")

# Generic \lim(x\to a) if any remaining
apply_fix(r'\\lim(x\\to a)', r'\\lim_{x\\to a}', '\\lim(x\\to a) generic')

# ============================================================
# Phase 5: Fix \frac{sinx}{x} → \frac{\sin x}{x}
# ============================================================
print("\n=== Phase 5: Fix \\frac{sinx}{x} ===")
apply_fix(r'\\frac{sinx}{x}', r'\\frac{\\sin x}{x}', '\\frac{sinx}{x} → \\frac{\\sin x}{x}')

# ============================================================
# Phase 6: Fix f(a)\cdot f(b)0 → f(a)\cdot f(b)<0 (missing <)
# ============================================================
print("\n=== Phase 6: Fix missing < in f(a)·f(b)0 ===")
apply_fix(r'f(a)\\cdot f(b)0', r'f(a)\\cdot f(b)<0', 'f(a)\\cdot f(b)0 → f(a)\\cdot f(b)<0')

# ============================================================
# Phase 7: Fix u\cdotv → u\cdot v (洛必达法则)
# ============================================================
print("\n=== Phase 7: Fix u\\cdotv → u\\cdot v ===")
apply_fix(r'u\\cdotv', r'u\\cdot v', 'u\\cdotv → u\\cdot v')

# ============================================================
# Phase 8: Fix x_{1}x_{2} → x_{1}<x_{2} (随机变量与分布函数)
# Context: 若 x_{1}x_{2}，则 F(x_{1}) \le F(x_{2})
# ============================================================
print("\n=== Phase 8: Fix x_{1}x_{2} → x_{1}<x_{2} ===")
apply_fix(r'x_{1}x_{2}，则', r'x_{1}<x_{2}，则', 'x_{1}x_{2} → x_{1}<x_{2}')

# ============================================================
# Phase 9: Fix \sum (x_{k}\le x) → \sum_{x_{k}\le x} (随机变量)
# ============================================================
print("\n=== Phase 9: Fix \\sum (x_{k}\\le x) ===")
apply_fix(r'\\sum (x_{k}\\le x) p_{k}', r'\\sum_{x_{k}\\le x} p_{k}', '\\sum (x_{k}\\le x) → \\sum_{x_{k}\\le x}')

# ============================================================
# Phase 10: Fix \prod(i=1\to n) → \prod_{i=1}^{n} (参数估计)
# ============================================================
print("\n=== Phase 10: Fix \\prod(i=1\\to n) ===")
apply_fix(r'\\prod(i=1\\to n) f(X_{i}; \\theta)', r'\\prod_{i=1}^{n} f(X_{i}; \\theta)', '\\prod(i=1\\to n) → \\prod_{i=1}^{n}')

# ============================================================
# Phase 11: Fix \nablaf → \nabla f (方向导数与梯度)
# ============================================================
print("\n=== Phase 11: Fix \\nablaf → \\nabla f ===")
apply_fix(r'\\nablaf', r'\\nabla f', '\\nablaf → \\nabla f')

# ============================================================
# Phase 12: Fix |x|1 → |x|<1 (泰勒级数展开, missing <)
# Context: \frac{1}{1-x} = \sum x^{n}，|x|1
# ============================================================
print("\n=== Phase 12: Fix |x|1 → |x|<1 ===")
apply_fix(r'|x|1；', r'|x|<1；', '|x|1； → |x|<1；')
apply_fix(r'|x|1', r'|x|<1', '|x|1 → |x|<1 (remaining)')

# ============================================================
# Phase 13: Fix 3σ → 3\sigma (切比雪夫不等式, 题库)
# ============================================================
print("\n=== Phase 13: Fix 3σ → 3\\sigma ===")
apply_fix(r'3σ', r'3\\sigma', '3σ → 3\\sigma')

# ============================================================
# Phase 14: Fix \chi^{2}\chi^{2}_ → \chi^{2}>\chi^{2}_ (假设检验)
# Context: \chi^{2}\chi^{2}_(\frac{\alpha}{2})(n-1) 或 \chi^{2}\chi^{2}_(1-\frac{\alpha}{2})(n-1)
# This should be: \chi^{2}>\chi^{2}_{\frac{\alpha}{2}}(n-1) 或 \chi^{2}<\chi^{2}_{1-\frac{\alpha}{2}}(n-1)
# ============================================================
print("\n=== Phase 14: Fix \\chi^{2}\\chi^{2}_ in 假设检验 ===")
apply_fix(r'\\chi^{2}\\chi^{2}_(\\frac{\\alpha}{2})(n-1)', r'\\chi^{2}>\\chi^{2}_{\\frac{\\alpha}{2}}(n-1)', '\\chi^{2}>\\chi^{2}_{\\alpha/2}')
apply_fix(r'\\chi^{2}\\chi^{2}_(1-\\frac{\\alpha}{2})(n-1)', r'\\chi^{2}<\\chi^{2}_{1-\\frac{\\alpha}{2}}(n-1)', '\\chi^{2}<\\chi^{2}_{1-\\alpha/2}')

# Also fix |Z|>z_(\frac{\alpha}{2}) → |Z|>z_{\frac{\alpha}{2}}
apply_fix(r'z_(\\frac{\\alpha}{2})', r'z_{\\frac{\\alpha}{2}}', 'z_(\\frac{\\alpha}{2}) → z_{\\frac{\\alpha}{2}}')
apply_fix(r't_(\\frac{\\alpha}{2})(n-1)', r't_{\\frac{\\alpha}{2}}(n-1)', 't_(\\frac{\\alpha}{2})(n-1) → t_{\\frac{\\alpha}{2}}(n-1)')

# ============================================================
# Phase 15: Fix \lim(1+\frac{1}{t})^t → \lim_{t\to\infty}(1+\frac{1}{t})^t (题库)
# ============================================================
print("\n=== Phase 15: Fix \\lim(1+...) patterns in 题库 ===")
apply_fix(r'\\lim(1+\\frac{1}{t})^t = e', r'\\lim_{t\\to\\infty}(1+\\frac{1}{t})^t = e', '\\lim(1+\\frac{1}{t})^t')
apply_fix(r'\\lim(1+\\frac{a}{x})^x = e^a', r'\\lim_{x\\to\\infty}(1+\\frac{a}{x})^x = e^a', '\\lim(1+\\frac{a}{x})^x')

# ============================================================
# Phase 16: Fix sec^{2}x → \sec^{2}x (基本求导公式)
# ============================================================
print("\n=== Phase 16: Fix sec → \\sec ===")
apply_fix(r'sec^{2}x', r'\\sec^{2}x', 'sec^{2}x → \\sec^{2}x')
apply_fix(r'\\csc^{2}x', r'\\csc^{2}x', 'check \\csc^{2}x (already ok)')

# ============================================================
# Phase 17: Fix \\(\\frac{\\beta}{\\alpha}\\) → \\(\\frac{\\beta}{\\alpha}\\) in 等价无穷小
# The issue is \\lim(\\frac{\\beta}{\\alpha}) → \\lim \\frac{\\beta}{\\alpha}
# ============================================================
print("\n=== Phase 17: Fix \\lim(\\frac{...}{...}) patterns ===")
apply_fix(r'\\lim(\\frac{\\beta}{\\alpha}) = 1', r'\\lim \\frac{\\beta}{\\alpha} = 1', '\\lim(\\frac{\\beta}{\\alpha})')

# ============================================================
# Phase 18: Fix \\frac{(\\sum X_{i} - n\\mu)}{\\sigma\\sqrt{n}} → \\frac{\\sum X_{i} - n\\mu}{\\sigma\\sqrt{n}}
# Extra parens around numerator
# ============================================================
print("\n=== Phase 18: Fix extra parens in fractions ===")
apply_fix(r'\\frac{(\\sum X_{i} - n\\mu)}{\\sigma\\sqrt{n}}', r'\\frac{\\sum X_{i} - n\\mu}{\\sigma\\sqrt{n}}', 'extra parens in numerator')
apply_fix(r'\\frac{(\\bar{X}-\\mu_{0})}{\\frac{\\sigma}{\\sqrt{n}}}', r'\\frac{\\bar{X}-\\mu_{0}}{\\frac{\\sigma}{\\sqrt{n}}}', 'extra parens in Z stat')
apply_fix(r'\\frac{(\\bar{X}-\\mu_{0})}{\\frac{S}{\\sqrt{n}}}', r'\\frac{\\bar{X}-\\mu_{0}}{\\frac{S}{\\sqrt{n}}}', 'extra parens in T stat')
apply_fix(r'\\frac{(n-1)S^{2}}{\\sigma_{0}^{2}}', r'\\frac{(n-1)S^{2}}{\\sigma_{0}^{2}}', 'check (n-1)S^2 (already ok)')

# ============================================================
# Phase 19: Fix \\frac{(\\sum X_{i} - \\sum\\mu_{i})}{B_{n}} → \\frac{\\sum X_{i} - \\sum\\mu_{i}}{B_{n}}
# ============================================================
print("\n=== Phase 19: Fix more extra parens ===")
apply_fix(r'\\frac{(\\sum X_{i} - \\sum\\mu_{i})}{B_{n}}', r'\\frac{\\sum X_{i} - \\sum\\mu_{i}}{B_{n}}', 'extra parens in Liapunov')
apply_fix(r'\\frac{(\\sum X_{i} - n\\mu)}{\\sigma\\sqrt{n}}', r'\\frac{\\sum X_{i} - n\\mu}{\\sigma\\sqrt{n}}', 'extra parens in CLT')

# ============================================================
# Phase 20: Fix (\\frac{1}{n})\\sum → \\frac{1}{n}\\sum (extra parens)
# These are technically not errors but might cause rendering issues
# Actually these are fine, skip
# ============================================================

# ============================================================
# Phase 21: Fix missing > in P(A)0 (事件独立性)
# Context: P(A)0 时，A 与 B 独立
# ============================================================
print("\n=== Phase 21: Fix P(A)0 → P(A)>0 ===")
apply_fix(r'P(A)0 时', r'P(A)>0 时', 'P(A)0 → P(A)>0')
apply_fix(r'P(A)P(B)0 时', r'P(A)P(B)>0 时', 'P(A)P(B)0 → P(A)P(B)>0')

# ============================================================
# Phase 22: Fix 概率\\le\\alpha → 概率\\le\\alpha (假设检验)
# Context: 构造小概率事件（概率\\le\\alpha）
# This is actually correct, skip
# ============================================================

# ============================================================
# Phase 23: Fix \\rho_{XY} missing backslash issue
# Actually this is fine
# ============================================================

# ============================================================
# Phase 24: General cleanup - fix any remaining \\lim( patterns
# Use regex to catch any remaining \\lim(var\\to value) patterns
# ============================================================
print("\n=== Phase 24: General \\lim(...) cleanup with regex ===")
# \lim(var\to value) → \lim_{var\to value}
# Match \lim( followed by variable, \to, value, )
# Be careful: only match when there's a \to inside
apply_regex(
    r'\\lim\((\\?[a-zA-Z]+)\\to\s*([^)]+)\)',
    r'\\lim_{\1\\to \2}',
    'general \\lim(var\\to value) → \\lim_{var\\to value}'
)

# ============================================================
# Phase 25: Fix \\sum ( without subscript
# \\sum (x_{k}\\le x) already handled
# Check for other \\sum ( patterns
# ============================================================
print("\n=== Phase 25: Fix \\sum ( patterns ===")
# Already handled in Phase 9

# ============================================================
# Phase 26: Fix t\\to0+ → t\\to 0^{+} (方向导数)
# Context: t\\to0+ should be t\\to 0^{+}
# ============================================================
print("\n=== Phase 26: Fix t\\to0+ ===")
apply_fix(r't\\to0+', r't\\to 0^{+}', 't\\to0+ → t\\to 0^{+}')

# Write the file
if content != original:
    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    diff = len(content) - len(original)
    print(f"\n✅ Total fixes applied: {fix_count}")
    print(f"   Character length change: {diff:+d}")
else:
    print("\n⚠️ No changes made.")

print(f"\nDone. Now run: node find_all_errors_v3.mjs to verify.")
