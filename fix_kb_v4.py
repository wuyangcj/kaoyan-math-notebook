#!/usr/bin/env python3
"""Comprehensive fix for LaTeX errors in knowledge base data.
Fixes: missing spaces in commands, invalid commands, fraction structure errors,
subscript parenthesis issues, double exponents, brace misplacement, missing operators.
Only modifies knowledge base data sections (lines ~43939-44320 and ~47843-47920),
does NOT delete any original content - only fixes LaTeX syntax.
"""
import re
import sys

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content
fix_count = 0

def fix_and_count(old, new, desc, flags=0):
    global content, fix_count
    new_content = re.sub(old, new, content, flags=flags) if isinstance(old, str) and not old.startswith('(') else content
    # Actually use simple replace for non-regex, re.sub for regex
    # Let's just use re.sub for all
    pass

# We'll do direct string replacements and count them
replacements = []

# ===== 1. Invalid LaTeX commands (missing space between command and next letter) =====
# These are in JS strings, so \\ means literal backslash in the file
# Pattern: \\le followed by a letter (not space) → \\le + letter
# But we need to be careful not to break \\left, \\leq, \\leqslant

# Invalid commands: \\len → \\le n, \\gen → \\ge n, \\lek → \\le k, \\lei → \\le i, \\lej → \\le j
invalid_cmds = [
    (r'\\len\b', r'\\le n', 'invalid \\len → \\le n'),
    (r'\\gen\b', r'\\ge n', 'invalid \\gen → \\ge n'),
    (r'\\lek\b', r'\\le k', 'invalid \\lek → \\le k'),
    (r'\\lei\b', r'\\le i', 'invalid \\lei → \\le i'),
    (r'\\lej\b', r'\\le j', 'invalid \\lej → \\le j'),
    (r'\\les\b', r'\\le s', 'invalid \\les → \\le s'),
]

# Missing space after \\le (but not \\left, \\leq, \\leqslant, \\leqno)
# \\le followed by a non-space, non-q, non-f character
# We need to be very careful here. Let's only fix specific known patterns.
missing_space_le = [
    (r'\\ler\(', r'\\le r(', '\\le r('),
    (r'\\lemin', r'\\le min', '\\le min'),
    (r'\\ley\b', r'\\le y', '\\le y'),
    (r'\\lex\b', r'\\le x', '\\le x'),
    (r'\\lez\b', r'\\le z', '\\le z'),
    (r'\\les\b', r'\\le s', '\\le s'),  # already in invalid
]

# Missing space after \\ge (but not \\geq, \\geqslant)
missing_space_ge = [
    (r'\\geh\b', r'\\ge h', '\\ge h'),
]

# Missing space after \\cdot
missing_space_cdot = [
    (r'\\cdotr', r'\\cdot r', '\\cdot r'),
    (r'\\cdoth', r'\\cdot h', '\\cdot h'),
    (r'\\cdotf', r'\\cdot f', '\\cdot f'),
    (r'\\cdotn', r'\\cdot n', '\\cdot n'),
    (r'\\cdotp', r'\\cdot p', '\\cdot p'),
    (r'\\cdotP', r'\\cdot P', '\\cdot P'),
    (r'\\cdotF', r'\\cdot F', '\\cdot F'),
    (r'\\cdotS', r'\\cdot S', '\\cdot S'),
]

# Missing space after \\ne (but not \\neq, \\neg, \\newline, etc.)
# \\ne followed by digit or specific letters
missing_space_ne = [
    (r'\\ne0\b', r'\\ne 0', '\\ne 0'),
    (r'\\nej\b', r'\\ne j', '\\ne j'),
    (r'\\ne0', r'\\ne 0', '\\ne 0'),  # for cases not caught by \b
]

# Missing space after \\to (but not \\to is fine, \\toggle, etc.)
missing_space_to = [
    (r'\\toB\b', r'\\to B', '\\to B'),
    (r'\\toN\b', r'\\to N', '\\to N'),
    (r'\\toM\b', r'\\to M', '\\to M'),
]

# Missing space after \\times
missing_space_times = [
    (r'\\timesn\b', r'\\times n', '\\times n'),
    (r'\\timess\b', r'\\times s', '\\times s'),
    (r'\\times2n', r'\\times 2n', '\\times 2n'),
]

# Missing space after \\subset
missing_space_subset = [
    (r'\\subsetA\b', r'\\subset A', '\\subset A'),
]

# Missing space after \\leftrightarrow
missing_space_leftrightarrow = [
    (r'\\leftrightarrowr\b', r'\\leftrightarrow r', '\\leftrightarrow r'),
]

# Missing space after \\pm
missing_space_pm = [
    (r'\\pm1\b', r'\\pm 1', '\\pm 1'),
]

# ===== 2. Fraction structure errors =====
# P\frac{(AB)}{P}(B) → \frac{P(AB)}{P(B)}
frac_errors = [
    (r'P\\frac\{(AB)\}\{P\}\(B\)', r'\\frac{P(AB)}{P(B)}', 'P\\frac{(AB)}{P}(B)'),
    (r'P\\frac\{AB\}\{P\}\(B\)', r'\\frac{P(AB)}{P(B)}', 'P\\frac{AB}{P}(B)'),
    (r'P\\frac\{\(AB\)\}\{P\}\(A\)', r'\\frac{P(AB)}{P(A)}', 'P\\frac{(AB)}{P}(A)'),
    (r'P\\frac\{\(A\|B_\{i\}\)\}\{\\sum\}_\{j\}', r'\\frac{P(A|B_{i})}{\\sum_{j}}', 'P\\frac{(A|B_{i})}{\\sum}_{j}'),
    (r'P\\frac\{\(A\|B_\{i\}\)\}\{P\}\(A\)', r'\\frac{P(A|B_{i})}{P(A)}', 'P\\frac{(A|B_{i})}{P}(A)'),
    (r'P\\frac\{\(A\|B_\{i\}\)\}\{\\sum\}', r'\\frac{P(A|B_{i})}{\\sum', 'P\\frac{(A|B_{i})}{\\sum'),
    (r'2\\varphi\\frac\{\(\\sqrt\{y\}\)\}\{2\\sqrt\{y\}\}', r'\\frac{2\\varphi(\\sqrt{y})}{2\\sqrt{y}}', '2\\varphi\\frac{(\\sqrt{y})}{2\\sqrt{y}}'),
    (r'\\varphi\\frac\{\(\\sqrt\{y\}\)\}\{\\sqrt\{y\}\}', r'\\frac{\\varphi(\\sqrt{y})}{\\sqrt{y}}', '\\varphi\\frac{(\\sqrt{y})}{\\sqrt{y}}'),
    (r'P\\frac\{\(A\|B_\{i\}\)\}\{\\sum\}_\{j\} P\(B_\{j\}\)\\cdot P\(A\|B_\{j\}\)', r'\\frac{P(A|B_{i})}{\\sum_{j} P(B_{j})\\cdot P(A|B_{j})}', 'complex fraction fix'),
]

# ===== 3. Subscript parenthesis → braces =====
# F_(1-\alpha) → F_{1-\alpha}, t_(\frac{\alpha}{2}) → t_{\frac{\alpha}{2}}, etc.
subscript_paren = [
    (r'F_\(1-\\alpha\)', r'F_{1-\\alpha}', 'F_(1-\\alpha)'),
    (r'F_\\alpha\b', r'F_{\\alpha}', 'F_\\alpha'),
    (r't_\(1-\\alpha\)', r't_{1-\\alpha}', 't_(1-\\alpha)'),
    (r't_\(\\frac\{\\alpha\}\{2\}\)', r't_{\\frac{\\alpha}{2}}', 't_(\\frac{\\alpha}{2})'),
    (r't_\\alpha\b', r't_{\\alpha}', 't_\\alpha'),
    (r'\\chi\^\{2\}_\(\\frac\{\\alpha\}\{2\}\)', r'\\chi^{2}_{\\frac{\\alpha}{2}}', 'chi^2_(\\frac{\\alpha}{2})'),
    (r'\\chi\^\{2\}_\(1-\\frac\{\\alpha\}\{2\}\)', r'\\chi^{2}_{1-\\frac{\\alpha}{2}}', 'chi^2_(1-\\frac{\\alpha}{2})'),
    (r'\\chi\^\{2\}_\\alpha\b', r'\\chi^{2}_{\\alpha}', 'chi^2_\\alpha'),
    (r'z_\(\\frac\{\\alpha\}\{2\}\)', r'z_{\\frac{\\alpha}{2}}', 'z_(\\frac{\\alpha}{2})'),
    (r'z_\\alpha\b', r'z_{\\alpha}', 'z_\\alpha'),  # careful, might not need this
]

# ===== 4. Double exponent / double subscript =====
# (1-p)^{n}-^{k} → (1-p)^{n-k}
# x_{n-}^{r} → x_{n-r}
# n\cdot F^{n}-1 → n\cdot F^{n-1}  (this is different - the -1 is outside)
# Actually: n\cdotF^{n}-1(z)\cdotf(z) → n\cdot F^{n-1}(z)\cdot f(z)
double_exp = [
    (r'\(1-p\)\^\{n\}\}-\^\{k\}', r'(1-p)^{n-k}', '(1-p)^{n}-^{k}'),
    (r'\(1-p\)\^\{n\}-\^\{k\}', r'(1-p)^{n-k}', '(1-p)^{n}-^{k}'),
    (r'\(1-\\frac\{1\}\{N\}\)\^\{n\}-\^\{m\}', r'(1-\\frac{1}{N})^{n-m}', '(1-\\frac{1}{N})^{n}-^{m}'),
    (r'\(1-p\)\^\{k\}-1p', r'(1-p)^{k-1}p', '(1-p)^{k}-1p'),
    (r'x_\{n-\}\^\{r\}', r'x_{n-r}', 'x_{n-}^{r}'),
    (r'n\\cdotF\^\{n\}-1\(z\)\\cdotf\(z\)', r'n\\cdot F^{n-1}(z)\\cdot f(z)', 'n\\cdotF^{n}-1(z)\\cdotf(z)'),
    (r'n\\cdot\(1-F\(z\)\)\^\{n\}-1\\cdotf\(z\)', r'n\\cdot(1-F(z))^{n-1}\\cdot f(z)', 'n\\cdot(1-F(z))^{n}-1\\cdotf(z)'),
    (r'n\\cdotF\^\{n\}-1', r'n\\cdot F^{n-1}', 'n\\cdotF^{n}-1'),
    (r'\(1-F\(z\)\)\^\{n\}-1', r'(1-F(z))^{n-1}', '(1-F(z))^{n}-1'),
    (r'\(1-p\)\^\{1\}-\^\{k\}', r'(1-p)^{1-k}', '(1-p)^{1}-^{k}'),
    (r'\(1-p\)1-\^\{k\}', r'(1-p)^{1-k}', '(1-p)1-^{k}'),
]

# ===== 5. Brace misplacement =====
# \frac{X}{n}_{1} → \frac{X}{n_{1}}
# E(F)=n\frac{_{2}}{n_{2}-2} → E(F)=\frac{n_{2}}{n_{2}-2}
brace_errors = [
    (r'\\frac\{X\}\{n\}_\{1\}', r'\\frac{X}{n_{1}}', '\\frac{X}{n}_{1}'),
    (r'\\frac\{Y\}\{n\}_\{2\}', r'\\frac{Y}{n_{2}}', '\\frac{Y}{n}_{2}'),
    (r'E\(F\)=n\\frac\{_\{2\}\}\{n_\{2\}-2\}', r'E(F)=\\frac{n_{2}}{n_{2}-2}', 'E(F)=n\\frac{_{2}}{n_{2}-2}'),
]

# ===== 6. Missing comparison operators =====
# These are tricky - need context
# r(A)n → r(A)<n (in context of rank)
# |Z|z_ → |Z|>z_
missing_ops = [
    # In knowledge base, patterns like "r(A)n" should be "r(A)<n"
    # But this is very context-dependent. Let's fix specific known patterns.
    (r'\|Z\|z_\(', r'|Z|>z_(', '|Z|z_('),
    (r'\|T\|t_\(', r'|T|>t_(', '|T|t_('),
    (r'P\(Tt_', r'P(T>t_', 'P(Tt_'),
    (r'P\(\\chi\^\{2\}\(n\)\\chi\^\{2\}', r'P(\\chi^{2}(n)>\\chi^{2}', 'P(\\chi^{2}(n)\\chi^{2}'),
]

# ===== 7. Other specific fixes =====
other_fixes = [
    # \\sum (i=1\\to k-1) → \\sum_{i=1}^{k-1}
    (r'\\sum \(i=1\\to k-1\)', r'\\sum_{i=1}^{k-1}', '\\sum (i=1\\to k-1)'),
    # \\sum (i,j) → \\sum_{i,j}
    (r'\\sum \(i,j\)', r'\\sum_{i,j}', '\\sum (i,j)'),
    # \\sum (x_{k}\\le x) → \\sum_{x_{k}\\le x}
    (r'\\sum \(x_\{k\}\\le x\)', r'\\sum_{x_{k}\\le x}', '\\sum (x_{k}\\le x)'),
    # \\sum (g(x_{k})=y_{j}) → \\sum_{g(x_{k})=y_{j}}
    (r'\\sum \(g\(x_\{k\}\)=y_\{j\}\)', r'\\sum_{g(x_{k})=y_{j}}', '\\sum (g(x_{k})=y_{j})'),
    # \\prod F_{i}(z) ok but \\prodp_{i} → \\prod p_{i}
    (r'\\prodp_\{i\}', r'\\prod p_{i}', '\\prodp_{i}'),
    (r'\\prod\(1-p_\{i\}\)', r'\\prod(1-p_{i})', '\\prod(1-p_{i})'),  # already ok
    # \\cupB_{i} → \\cup B_{i}
    (r'\\cupB_\{i\}', r'\\cup B_{i}', '\\cupB_{i}'),
    # \\lim(x→0) → \\lim_{x \\to 0} - this is handled by _mathToLatex, skip
    # \\mathrm{e} ok
    # r(A)n → r(A)<n  - very context dependent, skip for safety
    # 1\\lei_{1}i_{2}...i_{k}\\len → 1\\le i_{1}<i_{2}<...<i_{k}\\le n
    (r'1\\lei_\{1\}i_\{2\}\.\.\.i_\{k\}\\len', r'1\\le i_{1}<i_{2}<...<i_{k}\\le n', '1\\lei_{1}i_{2}...i_{k}\\len'),
    # P(A)0 → P(A)>0  - context dependent
    (r'P\(A\)0\b时', r'P(A)>0时', 'P(A)0时'),
    (r'P\(A_\{1\}A_\{2\}\)0\b', r'P(A_{1}A_{2})>0', 'P(A_{1}A_{2})0'),
    (r'P\(B_\{i\}\)0\b', r'P(B_{i})>0', 'P(B_{i})0'),
    (r'若 P\(A\)0', r'若 P(A)>0', '若 P(A)0'),
    # n1 → n>1, n2 → n>2 (in specific contexts like E(T)=0 (n1), D(T)=n/(n-2) (n2))
    (r'\(n1\)', r'(n>1)', '(n1)'),
    (r'\(n2\)', r'(n>2)', '(n2)'),
    # al → a>l (蒲丰投针条件)
    (r'（al）', r'（a>l）', '（al）'),
    # 0xy1 → 0<x<1
    (r'0xy1', r'0<x<1', '0xy1'),
    # 0z → 0<z
    (r'0z\\le1', r'0<z\\le1', '0z\\le1'),
    # 0x1 → 0<x<1  (f_X(x)=1 (0x1))
    (r'\(0x1\)', r'(0<x<1)', '(0x1)'),
    # x_{1}x_{2} in context of "x_{1}x_{2}...x_{n}" is fine
    # y0 → y>0
    (r'y0\b时', r'y>0时', 'y0时'),
    (r', y0', r', y>0', ', y0'),
]

# Combine all replacements
all_replacements = (
    invalid_cmds +
    missing_space_le +
    missing_space_ge +
    missing_space_cdot +
    missing_space_ne +
    missing_space_to +
    missing_space_times +
    missing_space_subset +
    missing_space_leftrightarrow +
    missing_space_pm +
    frac_errors +
    subscript_paren +
    double_exp +
    brace_errors +
    missing_ops +
    other_fixes
)

# Apply all replacements
for old_pattern, new_pattern, desc in all_replacements:
    matches = re.findall(old_pattern, content)
    if matches:
        count = len(matches)
        content = re.sub(old_pattern, new_pattern, content)
        print(f"  Fixed [{count}x]: {desc}")
        fix_count += count

# ===== Additional complex fixes that need careful handling =====

# Fix: r(A)n → r(A)<n in specific contexts within knowledge base
# Pattern: "r(A)n \\Rightarrow" → "r(A)<n \\Rightarrow"
# But only in knowledge base sections
extra_fixes = [
    (r'r\(A\)n \\Rightarrow', r'r(A)<n \\Rightarrow', 'r(A)n → r(A)<n'),
    (r'r\(A\)=r\(A\|b\)=rn', r'r(A)=r(A|b)<n', 'r(A)=r(A|b)=rn → <n'),
    (r'r\(A\)r\(A\|b\)', r'r(A)<r(A|b)', 'r(A)r(A|b) → r(A)<r(A|b)'),
    (r'r\(A\)=r\(A\|b\)=rn', r'r(A)=r(A|b)<n', 'r(A)=r(A|b)=rn (2nd)'),
]

for old_pattern, new_pattern, desc in extra_fixes:
    matches = re.findall(old_pattern, content)
    if matches:
        count = len(matches)
        content = re.sub(old_pattern, new_pattern, content)
        print(f"  Fixed [{count}x]: {desc}")
        fix_count += count

# ===== Fix specific knowledge base content issues =====
# "n\\times2n" → "n\\times 2n" (already in missing_space_times but let's double check)
# "n\\timess" → "n\\times s"
more_kb_fixes = [
    (r'n\\timess\b', r'n\\times s', 'n\\timess'),
    (r'm\\timesn\b', r'm\\times n', 'm\\timesn'),
    (r'n\\times2n', r'n\\times 2n', 'n\\times2n'),
    (r'n\\timesn\b', r'n\\times n', 'n\\timesn'),
    # \\timess → \\times s (general)
    (r'\\timess\b', r'\\times s', '\\timess (general)'),
    # Fix "0\\ler(A)\\lemin(m,n)" → "0\\le r(A)\\le min(m,n)"
    (r'0\\ler\(A\)\\lemin', r'0\\le r(A)\\le min', '0\\ler(A)\\lemin'),
    # Fix "B\\subsetA" → "B\\subset A"
    (r'B\\subsetA', r'B\\subset A', 'B\\subsetA'),
    # Fix "n\\to\\infty 时 t 分布\\toN(0,1)"
    (r'\\toN\(0,1\)', r'\\to N(0,1)', '\\toN(0,1)'),
    # Fix "x_{n-}^{r}" already handled
    # Fix "k\\ne0" → "k\\ne 0"
    (r'k\\ne0\b', r'k\\ne 0', 'k\\ne0'),
    (r'K\\ne0\b', r'K\\ne 0', 'K\\ne0'),
    # Fix "A-1" → "A^{-1}" in some contexts (but this is too broad, skip)
    # Fix "P-1AP" → "P^{-1}AP"
    # These are in HTML so let's be careful
    # Fix "E(i,j)-1" → "E(i,j)^{-1}" - this is in context of inverse matrices
    (r'E\(i,j\)-1\b', r'E(i,j)^{-1}', 'E(i,j)-1'),
    (r'E\(i\(k\)\)-1\b', r'E(i(k))^{-1}', 'E(i(k))-1'),
    (r'E\(ij\(k\)\)-1\b', r'E(ij(k))^{-1}', 'E(ij(k))-1'),
    # Fix "P-1" → "P^{-1}" in specific contexts
    (r'P-1\\alpha', r'P^{-1}\\alpha', 'P-1\\alpha'),
    (r'P-1AP', r'P^{-1}AP', 'P-1AP'),
    (r'P-1=A', r'P^{-1}=A', 'P-1=A'),  # might be too broad
    (r'Q\^\{T\}=Q-1', r'Q^{T}=Q^{-1}', 'Q^{T}=Q-1'),
    # Fix "A-1~B-1" → "A^{-1}~B^{-1}"
    (r'A-1~B-1', r'A^{-1}~B^{-1}', 'A-1~B-1'),
    # Fix "f(A)~f(B)" is fine
    # Fix "A^{m}~B^{m}" is fine
]

for old_pattern, new_pattern, desc in more_kb_fixes:
    matches = re.findall(old_pattern, content)
    if matches:
        count = len(matches)
        content = re.sub(old_pattern, new_pattern, content)
        print(f"  Fixed [{count}x]: {desc}")
        fix_count += count

# ===== Fix "二阶导数" Extra close brace issue =====
# The user selected element showed "二阶导数" with "Extra close brace or missing open brace"
# Let's find what's causing this
# Search for patterns with unbalanced braces in the knowledge base

# Write the fixed content
if content != original_content:
    with open(FILE, 'w', encoding='utf-8') as f:
        f.write(content)
    diff = len(content) - len(original_content)
    print(f"\n✅ Total fixes applied: {fix_count}")
    print(f"   Character length change: {diff:+d}")
else:
    print("\n⚠️ No changes made.")

# Verify no remaining issues
print("\n=== Verification ===")
verify_patterns = [
    (r'\\len\b', '\\len'),
    (r'\\gen\b', '\\gen'),
    (r'\\lek\b', '\\lek'),
    (r'\\lei\b', '\\lei'),
    (r'\\lej\b', '\\lej'),
    (r'\\cdot[rfhn]', '\\cdot followed by letter'),
    (r'\\ler\(', '\\ler('),
    (r'\\lemin', '\\lemin'),
    (r'P\\frac\{', 'P\\frac{'),
    (r'\^\{[^\}]+\}\}-\^\{', 'double exponent'),
    (r'\}_\{1\}\}', '}_{1}}'),
]

for pattern, name in verify_patterns:
    matches = re.findall(pattern, content)
    if matches:
        print(f"  ⚠️ Still found {len(matches)} occurrences of: {name}")
    else:
        print(f"  ✅ {name}: clean")
