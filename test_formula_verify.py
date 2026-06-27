#!/usr/bin/env python3
"""验证 mathToLatex 函数对典型公式的转换结果 - 三遍审查第三遍"""
import re

def simulate_math_to_latex(s):
    """精确模拟 HTML 中的 mathToLatex 函数核心逻辑"""

    # ---- LaTeX 结构保护机制 ----
    # 0. 修复 \frac{²}{2} 类模式：在 \frac{ 后紧跟 Unicode 上下标时补 x
    s = re.sub(r'\\frac\{([⁰¹²³⁴⁵⁶⁷⁸⁹ⁿ⁺⁻ᵃᵇᶜˣʸᵗʲᵏˡᵐᵀⁱ₀₁₂₃₄₅₆₇₈₉ₙₐₑᵢⱼₓ₊₋]+)\}\{', r'\\frac{x\1}{', s)

    # 辅助：找到匹配的闭花括号位置
    def find_close_brace(str, start):
        depth = 1
        j = start + 1
        while j < len(str) and depth > 0:
            if str[j] == '{': depth += 1
            elif str[j] == '}': depth -= 1
            if depth > 0: j += 1
        return j if depth == 0 else -1

    # 1. 保护 \frac{...}{...} 结构（支持嵌套花括号）
    def protect_frac(str):
        result = ''
        i = 0
        while i < len(str):
            if str.startswith('\\frac{', i):
                num_open = i + 5
                num_close = find_close_brace(str, num_open)
                if num_close != -1:
                    numerator = str[num_open + 1:num_close]
                    den_open = num_close + 1
                    while den_open < len(str) and str[den_open] == ' ': den_open += 1
                    if den_open < len(str) and str[den_open] == '{':
                        den_close = find_close_brace(str, den_open)
                        if den_close != -1:
                            denominator = str[den_open + 1:den_close]
                            result += '\x00FRAC0\x00' + numerator + '\x00FRAC1\x00\x00FRAC2\x00' + denominator + '\x00FRAC3\x00'
                            i = den_close + 1
                            continue
            result += str[i]
            i += 1
        return result
    s = protect_frac(s)

    # 2. 保护 _{...} 和 ^{...} 结构（仅当前面是字母/数字/)/]时）
    def protect_subsup(str):
        result = ''
        i = 0
        while i < len(str):
            if (str[i] == '^' or str[i] == '_') and i + 1 < len(str) and str[i + 1] == '{':
                if len(result) > 0 and re.match(r'[a-zA-Z0-9\)\]]', result[-1]):
                    close_pos = find_close_brace(str, i + 1)
                    if close_pos != -1:
                        content = str[i + 2:close_pos]
                        marker = 'SUP' if str[i] == '^' else 'SUB'
                        result += '\x00' + marker + '0\x00' + content + '\x00' + marker + '1\x00'
                        i = close_pos + 1
                        continue
            result += str[i]
            i += 1
        return result
    s = protect_subsup(s)

    # ---- 积分号上下限预处理 ----
    sup_chars = '\u00B2\u00B3\u00B9\u2070-\u2079\u207A\u207B\u207F\u2071\u02B0-\u02B8\u02E1-\u02E3\u1D43-\u1D61\u1D9C-\u1DA1\u1D40\u1D50'
    sub_chars = '\u2080-\u209C\u1D62-\u1D6A'
    sup_map_pre = {'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9','ⁿ':'n','⁺':'+','⁻':'-','ᵃ':'a','ᵇ':'b','ᶜ':'c','ˣ':'x','ʸ':'y','ᵗ':'t','ʲ':'j','ᵏ':'k','ˡ':'l','ᵐ':'m','ᵀ':'T','ⁱ':'i'}
    sub_map_pre = {'₀':'0','₁':'1','₂':'2','₃':'3','₄':'4','₅':'5','₆':'6','₇':'7','₈':'8','₉':'9','ₙ':'n','ₐ':'a','ₑ':'e','ᵢ':'i','ⱼ':'j','ₓ':'x','₊':'+','₋':'-'}

    # 模式1：∫ + 下标 + 上标
    s = re.sub('∫([' + sub_chars + ']+)([' + sup_chars + ']+)', lambda m: '\\int_{' + ''.join(sub_map_pre.get(c,c) for c in m.group(1)) + '}^{' + ''.join(sup_map_pre.get(c,c) for c in m.group(2)) + '}', s)
    # 模式2：∫ + 下标 + ^
    s = re.sub('∫([' + sub_chars + ']+)\\^', lambda m: '\\int_{' + ''.join(sub_map_pre.get(c,c) for c in m.group(1)) + '}^', s)
    # 模式3：∫ + 下标（无上限）
    s = re.sub('∫([' + sub_chars + ']+)(?![\\^' + sup_chars + '])', lambda m: '\\int_{' + ''.join(sub_map_pre.get(c,c) for c in m.group(1)) + '}', s)
    # 模式4：] + 下标 + 上标
    s = re.sub('\\]([' + sub_chars + ']+)([' + sup_chars + ']+)', lambda m: ']_{' + ''.join(sub_map_pre.get(c,c) for c in m.group(1)) + '}^{' + ''.join(sup_map_pre.get(c,c) for c in m.group(2)) + '}', s)

    # ---- Unicode 上下标转 ASCII ----
    sup_map = {'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9','ⁿ':'n','⁺':'+','⁻':'-','ᵃ':'a','ᵇ':'b','ᶜ':'c','ˣ':'x','ʸ':'y','ᵗ':'t','ʲ':'j','ᵏ':'k','ˡ':'l','ᵐ':'m','ᵀ':'T','ⁱ':'i'}
    sub_map = {'₀':'0','₁':'1','₂':'2','₃':'3','₄':'4','₅':'5','₆':'6','₇':'7','₈':'8','₉':'9','ₙ':'n','ₐ':'a','ₑ':'e','ᵢ':'i','ⱼ':'j','ₓ':'x','₊':'+','₋':'-'}

    s = re.sub(r'[\u00B2\u00B3\u00B9\u2070-\u2079\u207A\u207B\u207F\u2071\u02B0-\u02B8\u02E1-\u02E3\u1D43-\u1D61\u1D9C-\u1DA1\u1D40\u1D50]+',
               lambda m: '^{' + ''.join(sup_map.get(c, c) for c in m.group()) + '}', s)
    s = re.sub(r'[\u2080-\u209C\u1D62-\u1D6A]+',
               lambda m: '_{' + ''.join(sub_map.get(c, c) for c in m.group()) + '}', s)

    # ---- 还原 _{...} 和 ^{...} 占位符 ----
    s = s.replace('\x00SUB0\x00', '_{')
    s = s.replace('\x00SUB1\x00', '}')
    s = s.replace('\x00SUP0\x00', '^{')
    s = s.replace('\x00SUP1\x00', '}')

    # Σ 上下文处理
    s = re.sub(r'Σ\s*\(\s*(\w+)\s*=\s*(\w+)\s*,\s*∞\s*\)', r'\\sum_{\1=\2}^{\\infty}', s)
    s = re.sub(r'Σ\s*\(\s*(\w+)\s*=\s*(\w+)\s*,\s*\+∞\s*\)', r'\\sum_{\1=\2}^{+\\infty}', s)
    s = s.replace('_Σ', '_{\\Sigma}')
    s = re.sub(r'Σ(?=[a-zA-Z0-9(])', r'\\sum', s)
    s = re.sub(r'Σ\s+(?=[a-zA-Z0-9])', r'\\sum ', s)

    greek_map = {'α':'\\alpha','β':'\\beta','γ':'\\gamma','δ':'\\delta','ε':'\\varepsilon',
                 'ζ':'\\zeta','η':'\\eta','θ':'\\theta','ι':'\\iota','κ':'\\kappa','λ':'\\lambda',
                 'μ':'\\mu','ν':'\\nu','ξ':'\\xi','π':'\\pi','ρ':'\\rho','σ':'\\sigma','τ':'\\tau',
                 'υ':'\\upsilon','φ':'\\varphi','χ':'\\chi','ψ':'\\psi','ω':'\\omega',
                 'Γ':'\\Gamma','Δ':'\\Delta','Θ':'\\Theta','Λ':'\\Lambda','Ξ':'\\Xi','Π':'\\Pi',
                 'Σ':'\\Sigma','Φ':'\\Phi','Ψ':'\\Psi','Ω':'\\Omega'}
    for k, v in greek_map.items():
        s = s.replace(k, v)

    # 数学符号
    s = s.replace('∞', '\\infty')
    s = s.replace('≤', '\\leq')
    s = s.replace('≥', '\\geq')
    s = s.replace('≠', '\\neq')
    s = s.replace('→', '\\to')
    s = s.replace('←', '\\leftarrow')
    s = s.replace('⇒', '\\Rightarrow')
    s = s.replace('⇔', '\\Leftrightarrow')
    s = s.replace('±', '\\pm')
    s = s.replace('×', '\\times')
    s = s.replace('÷', '\\div')
    s = s.replace('·', '\\cdot')
    s = s.replace('~', '\\sim ')
    s = s.replace('≈', '\\approx ')
    s = s.replace('√', '\\sqrt')
    s = s.replace('∮', '\\oint')
    s = s.replace('∬', '\\iint')
    s = s.replace('∭', '\\iiint')
    s = s.replace('∯', '\\oiint')
    s = s.replace('∰', '\\oiiint')
    s = s.replace('∫', '\\int')
    s = s.replace('∑', '\\sum')
    s = s.replace('∏', '\\prod')
    s = s.replace('∂', '\\partial')
    s = s.replace('∇', '\\nabla')
    s = s.replace('∈', '\\in ')
    s = s.replace('∉', '\\notin ')
    s = s.replace('⊂', '\\subset ')
    s = s.replace('⊃', '\\supset ')
    s = s.replace('∪', '\\cup ')
    s = s.replace('∩', '\\cap ')
    s = s.replace('∀', '\\forall ')
    s = s.replace('∃', '\\exists ')
    s = s.replace('∝', '\\propto ')

    # sqrt(...)
    s = re.sub(r'\\sqrt\s*\(([^)]+)\)', r'\\sqrt{\1}', s)

    # 函数命令后补空格（第24272-24273行）
    s = re.sub(r'\\(sin|cos|tan)(?=[a-zA-Z])(?!h)', r'\\\1 ', s)
    s = re.sub(r'\\(cot|sec|csc|arcsin|arccos|arctan|sinh|cosh|tanh|log|ln|exp|lim|max|min|sup|int|sum|prod|sqrt)(?=[a-zA-Z])', r'\\\1 ', s)

    # 统一处理：长命令在前（第24277行），\in单独处理排除\int和\infty
    cmd_list = (r'notin|infty|leftarrow|Rightarrow|Leftrightarrow|forall|exists|propto|partial|nabla|'
                r'oint|iint|iiint|oiint|oiiint|varepsilon|upsilon|varphi|Gamma|Delta|Theta|Lambda|'
                r'Xi|Pi|Sigma|Phi|Psi|Omega|int|sim|neq|to|pm|times|div|cdot|approx|subset|supset|'
                r'cup|cap|leq|geq|alpha|beta|gamma|delta|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|'
                r'pi|rho|sigma|tau|chi|psi|omega')
    s = re.sub(r'\\(' + cmd_list + r')(?=[a-zA-Z])', r'\\\1 ', s)
    # \in 单独处理：排除 \int (后跟t) 和 \infty (后跟f)
    s = re.sub(r'\\in(?![tf])(?=[a-zA-Z])', r'\\in ', s)

    # ---- 还原 \frac{...}{...} 占位符 ----
    s = s.replace('\x00FRAC0\x00', '\\frac{')
    s = s.replace('\x00FRAC1\x00', '}')
    s = s.replace('\x00FRAC2\x00', '{')
    s = s.replace('\x00FRAC3\x00', '}')

    return s

# 测试用例：题库中的典型公式
test_cases = [
    ("X~N(0,1)", "正态分布", "X\\sim N(0,1)"),
    ("X~N(3, σ²)", "正态分布带σ²", None),
    ("X+Y~N(0, 2)", "和的分布", None),
    ("∯_Σ (x dydz + y dzdx + z dxdy)", "曲面积分", None),
    ("∬_D (x² + y²) dxdy", "二重积分", None),
    ("∮_L (x² + y²) ds", "曲线积分", None),
    ("∫∫∫_Ω 3 dV", "三重积分", None),
    ("Σ 为球面 x²+y²+z²=R²", "Sigma曲面", None),
    ("ΣXᵢ", "求和符号", None),
    ("x ∈ ℝ", "属于", None),
    ("A ∪ B", "并集", None),
    ("±∞", "正负无穷", None),
    ("∂f/∂x", "偏导", None),
    ("√2", "根号", None),
    ("a ≈ b", "约等于", None),
    ("f(x) → 0", "趋向", None),
    ("∮ P dx + Q dy = ∬(∂Q/∂x - ∂P/∂y) dxdy", "格林公式", None),
    ("∫₀¹ (4x + 3) dx", "定积分上下限", None),
    ("∫₀² kx dx", "定积分下限2", None),
    ("[x²]₀¹", "定积分求值", None),
    ("∫₀^(2π) dθ ∫₀^1 r²·r dr", "定积分复合", None),
    ("\\frac{²}{2}", "frac上标修复", "\\frac{x^{2}}{2}"),
]

print("=" * 80)
print("公式转换验证（三遍审查 - 第三遍）")
print("=" * 80)

all_pass = True
for formula, desc, expected in test_cases:
    result = simulate_math_to_latex(formula)
    issues = []

    # 检查所有可能的乱码模式
    # 1. \command 后直接跟字母（没有空格），排除已有空格的
    # 检查 \sim 后跟字母
    if re.search(r'\\sim[a-zA-Z]', result):
        issues.append("\\sim后跟字母")
    # 检查 \in 后跟字母（排除 \infty \notin \int）
    if re.search(r'\\in(?!fty|ot|t)[a-zA-Z]', result):
        issues.append("\\in后跟字母")
    # 检查 \int 被拆分为 \in t
    if '\\in t' in result:
        issues.append("\\int被拆分为\\in t")
    # 检查 \infty 被拆分为 \in fty
    if '\\in fty' in result:
        issues.append("\\infty被拆分为\\in fty")
    # 检查 \oiint 后跟字母
    if re.search(r'\\oiint[a-zA-Z]', result):
        issues.append("\\oiint后跟字母")
    # 检查 \sum 后跟字母
    if re.search(r'\\sum[a-zA-Z]', result):
        issues.append("\\sum后跟字母")
    # 检查 \pm 后跟字母
    if re.search(r'\\pm[a-zA-Z]', result):
        issues.append("\\pm后跟字母")
    # 检查 \frac{^ 非法模式（\frac{²}{2} bug 的核心检测）
    if re.search(r'\\frac\{\^', result):
        issues.append("\\frac后直接跟^（非法结构）")

    status = "✓ 通过" if not issues else f"✗ 失败: {', '.join(issues)}"
    if issues:
        all_pass = False
    print(f"\n[{desc}]")
    print(f"  原始: {formula}")
    print(f"  结果: {result}")
    if expected:
        print(f"  期望: {expected}")
        if result.strip() == expected.strip():
            print(f"  匹配: ✓")
        else:
            print(f"  匹配: ✗")
            all_pass = False
    print(f"  状态: {status}")

print("\n" + "=" * 80)
print(f"总结: {'全部通过 ✓' if all_pass else '存在问题 ✗'}")
print("=" * 80)
