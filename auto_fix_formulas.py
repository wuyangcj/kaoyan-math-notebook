#!/usr/bin/env python3
"""
知识库公式自检自改系统
扫描 knowledgeBaseDetail 和 knowledgeBaseSupplement 中的所有 <code> 块，
检测混用 Unicode 上下标和 LaTeX 的公式，自动修复为纯 LaTeX 表达。
循环执行直到没有更多问题。
"""

import re
import sys

HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

# Unicode 下标 → LaTeX 下标映射
SUBSCRIPT_MAP = {
    '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
    '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
    '₊': '+', '₋': '-', '₌': '=', '₍': '(', '₎': ')',
    'ₐ': 'a', 'ₑ': 'e', 'ₒ': 'o', 'ₓ': 'x', 'ₕ': 'h',
    'ₖ': 'k', 'ₗ': 'l', 'ₘ': 'm', 'ₙ': 'n', 'ₚ': 'p',
    'ₛ': 's', 'ₜ': 't', 'ᵢ': 'i', 'ⱼ': 'j', 'ᵣ': 'r',
    'ᵤ': 'u', 'ᵥ': 'v', 'ᵦ': 'beta', 'ᵧ': 'gamma', 'ᵨ': 'rho',
    'ᵩ': 'phi', 'ᵪ': 'chi',
}

# Unicode 上标 → LaTeX 上标映射
SUPERSCRIPT_MAP = {
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
    '⁺': '+', '⁻': '-', '⁼': '=', '⁽': '(', '⁾': ')',
    'ᵃ': 'a', 'ᵇ': 'b', 'ᶜ': 'c', 'ᵈ': 'd', 'ᵉ': 'e',
    'ᶠ': 'f', 'ᵍ': 'g', 'ʰ': 'h', 'ⁱ': 'i', 'ʲ': 'j',
    'ᵏ': 'k', 'ˡ': 'l', 'ᵐ': 'm', 'ⁿ': 'n', 'ᵒ': 'o',
    'ᵖ': 'p', 'ʳ': 'r', 'ˢ': 's', 'ᵗ': 't', 'ᵘ': 'u',
    'ᵛ': 'v', 'ʷ': 'w', 'ˣ': 'x', 'ʸ': 'y', 'ᶻ': 'z',
    'ᴬ': 'A', 'ᴮ': 'B', 'ᴰ': 'D', 'ᴱ': 'E', 'ᴳ': 'G',
    'ᴴ': 'H', 'ᴵ': 'I', 'ᴶ': 'J', 'ᴷ': 'K', 'ᴸ': 'L',
    'ᴹ': 'M', 'ᴺ': 'N', 'ᴼ': 'O', 'ᴾ': 'P', 'ᴿ': 'R',
    'ᵀ': 'T', 'ᵁ': 'U', 'ⱽ': 'V', 'ᵂ': 'W',
    'ⁿ': 'n',  # 常见
}

# 特殊数学符号映射
# 注意：值中用双反斜杠（\\\\）——写入 HTML 文件后为 \\command，
#       因为这些 LaTeX 命令位于 JSON 字符串值内，JSON 要求反斜杠转义。
SPECIAL_MAP = {
    '∪': '\\\\cup ',
    '∩': '\\\\cap ',
    '∈': '\\\\in ',
    '∉': '\\\\notin ',
    '⊂': '\\\\subset ',
    '⊃': '\\\\supset ',
    '⊆': '\\\\subseteq ',
    '⊇': '\\\\supseteq ',
    '∅': '\\\\emptyset ',
    '∀': '\\\\forall ',
    '∃': '\\\\exists ',
    '∇': '\\\\nabla ',
    '∂': '\\\\partial ',
    '∞': '\\\\infty ',
    '√': '\\\\sqrt ',
    '∑': '\\\\sum ',
    '∏': '\\\\prod ',
    '∫': '\\\\int ',
    '∬': '\\\\iint ',
    '∭': '\\\\iiint ',
    '∮': '\\\\oint ',
    '∯': '\\\\oiint ',
    '∰': '\\\\oiiint ',
    '≤': '\\\\le ',
    '≥': '\\\\ge ',
    '≠': '\\\\ne ',
    '≈': '\\\\approx ',
    '≡': '\\\\equiv ',
    '→': '\\\\to ',
    '←': '\\\\leftarrow ',
    '↔': '\\\\leftrightarrow ',
    '⇒': '\\\\Rightarrow ',
    '⇐': '\\\\Leftarrow ',
    '⇔': '\\\\Leftrightarrow ',
    '↦': '\\\\mapsto ',
    '↑': '\\\\uparrow ',
    '↓': '\\\\downarrow ',
    '·': '\\\\cdot ',
    '×': '\\\\times ',
    '÷': '\\\\div ',
    '±': '\\\\pm ',
    '∓': '\\\\mp ',
    'α': '\\\\alpha ',
    'β': '\\\\beta ',
    'γ': '\\\\gamma ',
    'δ': '\\\\delta ',
    'ε': '\\\\varepsilon ',
    'ζ': '\\\\zeta ',
    'η': '\\\\eta ',
    'θ': '\\\\theta ',
    'λ': '\\\\lambda ',
    'μ': '\\\\mu ',
    'ν': '\\\\nu ',
    'ξ': '\\\\xi ',
    'π': '\\\\pi ',
    'ρ': '\\\\rho ',
    'σ': '\\\\sigma ',
    'τ': '\\\\tau ',
    'φ': '\\\\varphi ',
    'χ': '\\\\chi ',
    'ψ': '\\\\psi ',
    'ω': '\\\\omega ',
    'Γ': '\\\\Gamma ',
    'Δ': '\\\\Delta ',
    'Θ': '\\\\Theta ',
    'Λ': '\\\\Lambda ',
    'Ξ': '\\\\Xi ',
    'Π': '\\\\Pi ',
    'Σ': '\\\\Sigma ',
    'Φ': '\\\\Phi ',
    'Ψ': '\\\\Psi ',
    'Ω': '\\\\Omega ',
    'Ā': '\\\\bar{A}',
    'ā': '\\\\bar{a}',
    'Ē': '\\\\bar{E}',
    'ē': '\\\\bar{e}',
    'Ī': '\\\\bar{I}',
    'ī': '\\\\bar{i}',
    'Ō': '\\\\bar{O}',
    'ō': '\\\\bar{o}',
    'Ū': '\\\\bar{U}',
    'ū': '\\\\bar{u}',
    'ι': '\\\\iota ',
    'κ': '\\\\kappa ',
    'ο': '\\\\omicron ',
    'ς': '\\\\varsigma ',
    'υ': '\\\\upsilon ',
}


def has_unicode_math(text):
    """检测文本中是否含有 Unicode 数学字符（上下标、特殊符号）"""
    # 检测 Unicode 上下标
    for ch in text:
        if ch in SUBSCRIPT_MAP or ch in SUPERSCRIPT_MAP:
            return True
        if ch in SPECIAL_MAP:
            return True
        # 检测 Unicode 数学运算符区 (U+2200-U+22FF)
        if '\u2200' <= ch <= '\u22FF':
            return True
        # 检测箭头区 (U+2190-U+21FF)
        if '\u2190' <= ch <= '\u21FF':
            return True
        # 检测希腊字母
        if '\u0391' <= ch <= '\u03C9':
            return True
    return False


def fix_formula_in_code(content):
    r"""
    修复 <code>...</code> 中的公式：
    1. 保护已有的 LaTeX 结构（\frac{}{}, _{}, ^{}, \sqrt{} 等）
    2. 转换 Unicode 上下标为 LaTeX
    3. 转换特殊数学符号为 LaTeX
    4. 还原 LaTeX 结构
    """
    # 收集要保护的 LaTeX 结构
    placeholders = []

    def protect(match):
        placeholders.append(match.group(0))
        return f'\x00PLACEHOLDER_{len(placeholders)-1}\x00'

    # 保护 \frac{...}{...}
    content = re.sub(r'\\frac\{[^{}]*\}\{[^{}]*\}', protect, content)
    # 保护 _{...}
    content = re.sub(r'_\{[^{}]*\}', protect, content)
    # 保护 ^{...}
    content = re.sub(r'\^\{[^{}]*\}', protect, content)
    # 保护 \sqrt{...}
    content = re.sub(r'\\sqrt\{[^{}]*\}', protect, content)
    # 保护 \bar{...}
    content = re.sub(r'\\bar\{[^{}]*\}', protect, content)
    # 保护 \mathrm{...}
    content = re.sub(r'\\mathrm\{[^{}]*\}', protect, content)
    # 保护 \text{...}
    content = re.sub(r'\\text\{[^{}]*\}', protect, content)
    # 保护 LaTeX 命令（如 \sum, \int, \alpha 等）
    content = re.sub(r'\\[a-zA-Z]+', protect, content)

    # 现在转换剩余的 Unicode 字符

    # 转换 Unicode 下标：字符后跟 Unicode 下标 → 字符_{下标}
    # 需要处理连续的 Unicode 下标（如 aᵢⱼ → a_{ij}）
    def replace_subscripts(text):
        result = []
        i = 0
        while i < len(text):
            ch = text[i]
            if ch in SUBSCRIPT_MAP:
                # 收集连续的下标
                subs = []
                while i < len(text) and text[i] in SUBSCRIPT_MAP:
                    subs.append(SUBSCRIPT_MAP[text[i]])
                    i += 1
                result.append('_{' + ''.join(subs) + '}')
            elif ch in SUPERSCRIPT_MAP:
                # 收集连续的上标
                sups = []
                while i < len(text) and text[i] in SUPERSCRIPT_MAP:
                    sups.append(SUPERSCRIPT_MAP[text[i]])
                    i += 1
                result.append('^{' + ''.join(sups) + '}')
            else:
                result.append(ch)
                i += 1
        return ''.join(result)

    content = replace_subscripts(content)

    # 转换特殊数学符号
    for unicode_char, latex in SPECIAL_MAP.items():
        if unicode_char in content:
            content = content.replace(unicode_char, latex)

    # 还原 LaTeX 结构
    for i, ph in enumerate(placeholders):
        content = content.replace(f'\x00PLACEHOLDER_{i}\x00', ph)

    return content


def fix_spacing_in_code(content):
    r"""
    修复 <code> 中的 LaTeX 空格问题：
    1. \command _{...} → \command_{} (移除 LaTeX 命令和下标/上标之间的空格)
    2. 连续多个空格 → 单个空格
    3. \Sigma  P → \Sigma P
    4. A_{n}_{-}_{1} → A_{n-1} (合并连续的下标)
    """
    original = content

    # 4. 合并连续的下标：A_{n}_{-}_{1} → A_{n-1}
    def merge_subscripts(text):
        # 匹配 _{...}_{...}_{...}... 模式，合并为 _{...}
        pattern = r'(_\{[^{}]*\})(_\{[^{}]*\})+'
        while re.search(pattern, text):
            def merge_one(m):
                # 提取所有 _{...} 中的内容
                parts = re.findall(r'_\{([^{}]*)\}', m.group(0))
                return '_{' + ''.join(parts) + '}'
            text = re.sub(pattern, merge_one, text)
        return text

    content = merge_subscripts(content)

    # 1. \command _{...} → \command_{} (移除 LaTeX 命令和下标/上标之间的空格)
    content = re.sub(r'(\\[a-zA-Z]+)\s+(_\{)', r'\1\2', content)
    content = re.sub(r'(\\[a-zA-Z]+)\s+(\^\{)', r'\1\2', content)

    # 2. 连续多个空格 → 单个空格
    content = re.sub(r'  +', ' ', content)

    return content


def process_html(html_content):
    """
    处理 HTML 内容：找到 knowledgeBaseDetail 和 knowledgeBaseSupplement 中的
    所有 <code>...</code> 块，修复其中的公式。
    返回 (修复后的内容, 修复次数)
    """
    fix_count = 0

    def fix_code_block(match):
        nonlocal fix_count
        full_match = match.group(0)
        code_content = match.group(1)

        if not has_unicode_math(code_content):
            # 即使没有 Unicode 字符，也检查空格问题
            fixed = fix_spacing_in_code(code_content)
            if fixed != code_content:
                fix_count += 1
                return f'<code>{fixed}</code>'
            return full_match

        fixed = fix_formula_in_code(code_content)
        # 额外应用空格修复
        fixed = fix_spacing_in_code(fixed)

        if fixed != code_content:
            fix_count += 1
            return f'<code>{fixed}</code>'
        return full_match

    # 只处理 knowledgeBaseDetail 和 knowledgeBaseSupplement 区域
    # 找到这两个区域的起止位置
    # 注意：animalAvatars 在 knowledgeBaseDetail 和 knowledgeBaseSupplement 之间
    patterns = [
        (r'const knowledgeBaseDetail\s*=\s*\{', r'const animalAvatars\s*='),
        (r'const knowledgeBaseSupplement\s*=\s*\{', r'const knowledgeNameMap\s*='),
    ]

    for start_pat, end_pat in patterns:
        start_match = re.search(start_pat, html_content)
        if not start_match:
            continue
        end_match = re.search(end_pat, html_content[start_match.end():])
        if not end_match:
            continue
        region_start = start_match.start()
        region_end = start_match.end() + end_match.start()

        region = html_content[region_start:region_end]
        fixed_region = re.sub(r'<code>(.*?)</code>', fix_code_block, region, flags=re.DOTALL)

        html_content = html_content[:region_start] + fixed_region + html_content[region_end:]

    return html_content, fix_count


def main():
    print("=" * 60)
    print("知识库公式自检自改系统")
    print("=" * 60)

    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        print(f"\n--- 第 {iteration} 轮扫描 ---")

        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            html_content = f.read()

        fixed_content, fix_count = process_html(html_content)

        if fix_count == 0:
            print(f"✅ 第 {iteration} 轮：未检测到需要修复的公式，自检完成！")
            break

        print(f"🔧 第 {iteration} 轮：检测并修复了 {fix_count} 处公式")

        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

    if iteration >= max_iterations:
        print(f"⚠️ 达到最大迭代次数 {max_iterations}，请检查是否有循环依赖")

    print("\n" + "=" * 60)
    print("自检自改系统完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
