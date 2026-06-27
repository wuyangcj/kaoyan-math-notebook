#!/usr/bin/env python3
"""Comprehensive fix v5: Fix all 72 remaining LaTeX errors in knowledge base.
Fixes identified by find_all_errors_v3.mjs browser testing.
Only modifies knowledge base data, does NOT delete original content.
"""
import re
import sys

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

original = content
fix_count = 0

def apply_fix(old, new, desc, content_var):
    global fix_count
    count = content_var.count(old)
    if count > 0:
        content_var = content_var.replace(old, new)
        print(f"  Fixed [{count}x]: {desc}")
        fix_count += count
    return content_var

# We'll use a list of (old, new, desc) tuples and apply them
fixes = []

# ===== 1. \ne followed by letter (not \neq, \neg, \newline, etc.) =====
# \nef → \ne f, \neF → \ne F
# But NOT \neq, \neg, \newline, \neqno, \nexists
ne_followed = [
    (r'\nef', r'\ne f', '\\ne f'),
    (r'\neF', r'\ne F', '\\ne F'),
]
for old, new, desc in ne_followed:
    # Use regex with negative lookahead to avoid \neq etc
    # Actually \nef won't match \neq since f != q
    fixes.append((old, new, desc))

# ===== 2. Fraction missing in 洛必达法则 =====
# (00型) → (\frac{0}{0}型), (∞∞型) → (\frac{\infty}{\infty}型)
# These are in the content as \\(00型) etc.
frac_missing = [
    (r'\\((00型)\\)', r'\\(\\frac{0}{0}型\\)', '(00型)'),
    (r'\\((∞∞型)\\)', r'\\(\\frac{\\infty}{\\infty}型\\)', '(∞∞型)'),
    (r'\\((0⋅∞型)\\)', r'\\(0\\cdot\\infty型\\)', '(0⋅∞型)'),
    (r'\\((∞−∞型)\\)', r'\\(\\infty-\\infty型\\)', '(∞−∞型)'),
    (r'\\((1∞型)\\)', r'\\(1^{\\infty}型\\)', '(1∞型)'),
    (r'\\((00型)\\)', r'\\(0^{0}型\\)', '(00型) - second'),
    (r'\\((∞0型)\\)', r'\\(\\infty^{0}型\\)', '(∞0型)'),
]
# Actually these appear as literal text, let me check the actual patterns
# From the error: \((00型)\) - so it's \(00型\) being rendered
# The issue is that 00 should be \frac{0}{0}
# Let me fix the source: 00型 → \frac{0}{0}型 when inside \(...\)
frac_in_delim = [
    (r'\\\(00型\\\)', r'\\(\\frac{0}{0}型\\)', '\\(00型\\)'),
    (r'\\\(∞∞型\\\)', r'\\(\\frac{\\infty}{\\infty}型\\)', '\\(∞∞型\\)'),
    (r'\\\(0⋅∞型\\\)', r'\\(0\\cdot\\infty型\\)', '\\(0⋅∞型\\)'),
    (r'\\\(∞−∞型\\\)', r'\\(\\infty-\\infty型\\)', '\\(∞−∞型\\)'),
    (r'\\\(1∞型\\\)', r'\\(1^{\\infty}型\\)', '\\(1∞型\\)'),
    (r'\\\(00型\\\)', r'\\(0^{0}型\\)', '\\(00型\\) v2'),
    (r'\\\(∞0型\\\)', r'\\(\\infty^{0}型\\)', '\\(∞0型\\)'),
]
for old, new, desc in frac_in_delim:
    fixes.append((old, new, desc))

# ===== 3. \le followed by letter (not \leq, \left, \leqslant) =====
le_followed = [
    (r'\leg', r'\le g', '\\le g'),
    (r'\lef', r'\le f', '\\le f'),
    (r'\leM', r'\le M', '\\le M'),
    (r'\leun', r'\le un', '\\le un'),
    (r'\levn', r'\le vn', '\\le vn'),
    (r'\leR', r'\le R', '\\le R'),
    (r'\ler', r'\le r', '\\le r'),
]
for old, new, desc in le_followed:
    fixes.append((old, new, desc))

# ===== 4. \leftrightarrow followed by letter =====
leftrightarrow_fix = [
    (r'\leftrightarrowr', r'\leftrightarrow r', '\\leftrightarrow r'),
]
for old, new, desc in leftrightarrow_fix:
    fixes.append((old, new, desc))

# ===== 5. β used as ≤ (should be \le) =====
# Context: "2βkβn" should be "2\le k\le n"
# "pβ1" should be "p\le 1"  -- but wait, this might be actual beta
# Let's check: "2\lek\len" was already fixed, but "2βkβn" is different
# The β (U+03B2) is being used where ≤ was intended
# But we need context. From error: "2βkβn" → "2\le k\le n"
# "pβ1" → "p\le 1" -- hmm, actually "p≥1" makes more sense for p-series
# Let me look at the context more carefully:
# "p>1 收敛，p≤1 发散" - so β here means ≤
# But "2βkβn" means "2≤k≤n"
beta_as_le = [
    (r'2βkβn', r'2\\le k\\le n', '2βkβn → 2\\le k\\le n'),
    (r'pβ1', r'p\\le 1', 'pβ1 → p\\le 1'),  # p≤1
    (r'1β', r'1\\le ', '1β → 1\\le '),  # might be too aggressive
]
# Actually, let me be more careful. The β might be legitimate.
# From the errors:
# - "2βkβn" in 事件独立性 → "2≤k≤n"
# - "pβ1" in 幂级数 → "p≤1" (convergence condition)
# But I need to check if β is actually used as a Greek letter elsewhere.
# Let's only fix the specific patterns we know are wrong.
beta_fixes = [
    (r'任意 k（2βkβn）', r'任意 k（2\\le k\\le n）', '2βkβn'),
    (r'（2βkβn）', r'（2\\le k\\le n）', '(2βkβn)'),
    (r'2βkβn', r'2\\le k\\le n', '2βkβn direct'),
]
for old, new, desc in beta_fixes:
    fixes.append((old, new, desc))

# ===== 6. Missing open brace for subscript (三重积分) =====
# The error is in 三重积分: "∭_\Omega" type patterns
# \iiint_\Omega should be \iiint_{\Omega}
# Let's find the actual patterns
# From error context: "体积：Missing open brace..." and "几何意义：当f≡1时..."
# These involve \iiint with subscript that needs braces
# Pattern: \iiint_ followed by single char without braces
iiint_fixes = [
    (r'\\iiint_\\Omega', r'\\iiint_{\\Omega}', '\\iiint_\\Omega'),
    (r'\\iiint_\\\\Omega', r'\\iiint_{\\\\Omega}', '\\iiint_\\\\Omega'),
]
for old, new, desc in iiint_fixes:
    fixes.append((old, new, desc))

# ===== 7. Extra close brace in 二阶导数 =====
# Need to find the actual content. The error is "二阶导数：Extra close brace"
# This is in 导数与微分 knowledge point
# Let me search for the pattern in the content
# The issue might be with f''(x) = ... having extra }

# ===== 8. Double exponent in 参数估计 =====
# Need to find the specific pattern

# ===== 9. \theta without backslash =====
# From error: "θ^1" should be "\hat{\theta}_1"
# "D(θ1)< D(\theta _{2})" - θ1 should be \hat{\theta}_1
theta_fixes = [
    (r'θ\^1', r'\\hat{\\theta}_1', 'θ^1 → \\hat{\\theta}_1'),
    (r'θ\^2', r'\\hat{\\theta}_2', 'θ^2 → \\hat{\\theta}_2'),
    (r'θ\^n', r'\\hat{\\theta}_n', 'θ^n → \\hat{\\theta}_n'),
    (r'D\(θ1\)', r'D(\\hat{\\theta}_1)', 'D(θ1)'),
    (r'θn−θ', r'\\hat{\\theta}_n-\\theta', 'θn−θ'),
    (r'θ\^', r'\\hat{\\theta}^', 'θ^ (general)'),
]
for old, new, desc in theta_fixes:
    fixes.append((old, new, desc))

# ===== 10. \lim without braces =====
# "limn→∞" should be "\lim_{n\to\infty}" or "\lim_{n\\to\\infty}"
# These appear as literal text that _mathToLatex should handle but isn't
lim_fixes = [
    (r'limn→∞', r'\\lim_{n\\to\\infty}', 'limn→∞'),
    (r'limn\\\\to∞', r'\\lim_{n\\\\to\\infty}', 'limn\\\\to∞'),
]
for old, new, desc in lim_fixes:
    fixes.append((old, new, desc))

# ===== 11. \sum with wrong subscript format =====
# "\sum(n=0→∞)" should be "\sum_{n=0}^{\infty}"
sum_fixes = [
    (r'\\sum\(n=0→∞\)', r'\\sum_{n=0}^{\\infty}', '\\sum(n=0→∞)'),
    (r'\\sum\(n=1→∞\)', r'\\sum_{n=1}^{\\infty}', '\\sum(n=1→∞)'),
    (r'\\sum\(n=0\\\\to∞\)', r'\\sum_{n=0}^{\\\\infty}', '\\sum(n=0\\\\to∞)'),
]
for old, new, desc in sum_fixes:
    fixes.append((old, new, desc))

# ===== Apply all fixes =====
for old, new, desc in fixes:
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        print(f"  Fixed [{count}x]: {desc}")
        fix_count += count

# Now let's handle the more complex patterns that need regex
# These need careful regex matching

# ===== 12. Fix \oiint and \iiint with missing braces =====
# \iiint_\Omega → \iiint_{\Omega} (already handled above)
# Also fix: ∭_\Omega → \iiint_{\Omega}
# And: \oiint_\sum → \oiint_{\sum} (曲面曲面积分)

# ===== 13. Fix β used as ≤ in specific contexts =====
# In 幂级数: "0\leRβ+∞" should be "0\le R\le +\infty"
more_beta = [
    (r'0\\leRβ\+∞', r'0\\le R\\le +\\infty', '0\\leRβ+∞'),
    (r'0\\leRβ', r'0\\le R\\le ', '0\\leRβ'),
    (r'β1 \\\\Rightarrow', r'\\le 1 \\\\Rightarrow', 'β1 \\\\Rightarrow'),
    (r'pβ1', r'p\\le 1', 'pβ1'),
    (r'≥1', r'\\ge 1', '≥1 in p-series'),  # already might be handled
]
for old, new, desc in more_beta:
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        print(f"  Fixed [{count}x]: {desc}")
        fix_count += count

# ===== 14. Fix "→∞" and "→" in math contexts =====
# These should be \to\infty
arrow_fixes = [
    (r'→∞', r'\\to\\infty', '→∞'),
    (r'→0', r'\\to 0', '→0'),
]
# Be careful - → might be in HTML text. Only fix in specific math contexts
# Skip for now as it might break things

# ===== 15. Fix ignition formula (点火公式) =====
# The error shows: "四、重要积分（点火公式\)点火公式\(Wallis公式）"
# This means there's a stray \) and \( in the middle
# Let's find and fix this
ignition_fix = [
    (r'点火公式\\\)点火公式\\\(', r'点火公式（', '点火公式\\\)点火公式\\\('),
    (r'点火公式\\\)\\\(', r'点火公式（', '点火公式\\\)\\\('),
]
for old, new, desc in ignition_fix:
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        print(f"  Fixed [{count}x]: {desc}")
        fix_count += count

# ===== 16. Fix f'' issues in 导数与微分 =====
# The "Extra close brace" error suggests there's an unmatched }
# Let me search for patterns like f''(x) = ... } in the content
# This needs manual inspection

# ===== 17. Fix \varepsilon without backslash =====
# "ε0" should be "\varepsilon > 0" or "\varepsilon > 0"
eps_fixes = [
    (r'ε0', r'\\varepsilon > 0', 'ε0 → \\varepsilon > 0'),
    (r'ε\)', r'\\varepsilon)', 'ε)'),
]
for old, new, desc in eps_fixes:
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        print(f"  Fixed [{count}x]: {desc}")
        fix_count += count

# ===== 18. Fix "→(P)" pattern =====
# "Xn→(P)a" should be "X_n \xrightarrow{P} a" or similar
# Let's just fix the arrow
# Skip for now - too complex

# Write the file
if content != original:
    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    diff = len(content) - len(original)
    print(f"\n✅ Total fixes applied: {fix_count}")
    print(f"   Character length change: {diff:+d}")
else:
    print("\n⚠️ No changes made.")

print(f"\nDone. Now need to manually fix:")
print("  - Extra close brace in 导数与微分 (二阶导数)")
print("  - Missing open brace for subscript in 三重积分")
print("  - Double exponent in 参数估计")
print("  - Various \\( \\) red mtext issues")
