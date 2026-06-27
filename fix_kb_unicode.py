#!/usr/bin/env python3
"""Fix Unicode math symbols in knowledgeBaseDetail content fields.

Reads the HTML file, finds the knowledgeBaseDetail region, and converts
Unicode math symbols to LaTeX in content fields (outside <code> tags).
Idempotent: can be run multiple times safely.
"""
import re
import sys

# === Character maps ===

# Unicode superscripts -> ASCII equivalents (for ^{...} conversion)
SUP_MAP = {
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
    'ⁿ': 'n', '⁺': '+', '⁻': '-',
    'ᵃ': 'a', 'ᵇ': 'b', 'ᶜ': 'c', 'ˣ': 'x', 'ʸ': 'y',
    'ᵗ': 't', 'ʲ': 'j', 'ᵏ': 'k', 'ˡ': 'l', 'ᵐ': 'm',
    'ᵀ': 'T', 'ⁱ': 'i'
}

# Unicode subscripts -> ASCII equivalents (for _{...} conversion)
SUB_MAP = {
    '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
    '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
    'ₙ': 'n', 'ₐ': 'a', 'ₑ': 'e', 'ᵢ': 'i', 'ⱼ': 'j',
    'ₓ': 'x', '₊': '+', '₋': '-'
}

# Unicode symbols -> LaTeX commands (double backslash for JS string in file)
SYM_MAP = {
    '×': r'\\times',
    '≠': r'\\ne',
    '≤': r'\\le',
    '≥': r'\\ge',
    'Σ': r'\\sum',
    '∫': r'\\int',
    'α': r'\\alpha',
    'β': r'\\beta',
    'γ': r'\\gamma',
    'δ': r'\\delta',
    'θ': r'\\theta',
    'λ': r'\\lambda',
    'μ': r'\\mu',
    'ξ': r'\\xi',
    'π': r'\\pi',
    'σ': r'\\sigma',
    'φ': r'\\varphi',
    'ω': r'\\omega',
    'Δ': r'\\Delta',
    'Γ': r'\\Gamma'
}

# Chinese punctuation that acts as segment boundary
CN_PUNCT = set('，。；：、""''（）【】《》…—')


def is_cjk(ch):
    """Check if character is CJK ideograph or Chinese punctuation."""
    if '\u4e00' <= ch <= '\u9fff':
        return True
    if ch in CN_PUNCT:
        return True
    return False


def convert_unicode(text):
    """Convert Unicode math symbols to LaTeX."""
    # Convert consecutive superscripts: x²³ -> x^{23}
    sup_chars = ''.join(re.escape(c) for c in SUP_MAP)
    text = re.sub(
        f'[{sup_chars}]+',
        lambda m: '^{' + ''.join(SUP_MAP[c] for c in m.group(0)) + '}',
        text
    )
    # Convert consecutive subscripts: x₀₁ -> x_{01}
    sub_chars = ''.join(re.escape(c) for c in SUB_MAP)
    text = re.sub(
        f'[{sub_chars}]+',
        lambda m: '_{' + ''.join(SUB_MAP[c] for c in m.group(0)) + '}',
        text
    )
    # Convert symbols: α -> \\alpha
    for uc, latex in SYM_MAP.items():
        text = text.replace(uc, latex)
    return text


def has_latex(text):
    """Check if text contains a LaTeX command or math syntax.

    In the file, LaTeX commands are written as \\\\command (double backslash).
    Math syntax includes ^{...} and _{...}.
    """
    n = len(text)
    for j in range(n):
        # Check for LaTeX command: \\ followed by a letter
        if text[j] == '\\' and j + 2 < n and text[j + 1] == '\\' and text[j + 2].isalpha():
            return True
        # Check for math syntax: ^{ or _{
        if text[j] in '^_' and j + 1 < n and text[j + 1] == '{':
            return True
    return False


def unwrap_latex(text):
    """Remove existing \\(...\\) wrappers to make processing idempotent.

    Matches \\(...\\) where the content doesn't contain \\) (to avoid
    matching across multiple wrappers).
    """
    # In the file, \\( is two backslashes + (, and \\) is two backslashes + )
    # Pattern: \\\\((?!\\\\\)).*?)\\\\\)
    pattern = re.compile(r'\\\\\(((?:(?!\\\\\)).)*?)\\\\\)')
    # Repeat until stable (handles nested cases, though nesting shouldn't occur)
    prev = None
    while prev != text:
        prev = text
        text = pattern.sub(r'\1', text)
    return text


def wrap_latex(text):
    """Wrap LaTeX-containing segments with \\(...\\).

    Segments are maximal runs of non-CJK, non-HTML, non-placeholder text
    that contain at least one LaTeX command or math syntax element.
    Placeholders (\\x00...\\x00) are treated as boundaries.
    """
    result = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] == '<':
            # HTML tag - copy as-is
            j = text.find('>', i)
            if j == -1:
                result.append(text[i:])
                break
            result.append(text[i:j + 1])
            i = j + 1
        elif text[i] == '\x00':
            # Placeholder - copy as-is (find closing \x00)
            j = text.find('\x00', i + 1)
            if j == -1:
                result.append(text[i:])
                break
            result.append(text[i:j + 1])
            i = j + 1
        elif is_cjk(text[i]):
            # CJK character - copy as-is
            result.append(text[i])
            i += 1
        else:
            # Potential math segment - extend until CJK, HTML tag, or placeholder
            j = i
            while j < n and not is_cjk(text[j]) and text[j] != '<' and text[j] != '\x00':
                j += 1
            seg = text[i:j]
            if has_latex(seg):
                stripped = seg.strip()
                if stripped:
                    lead = seg[:len(seg) - len(seg.lstrip())]
                    trail = seg[len(seg.rstrip()):]
                    result.append(lead)
                    result.append(r'\\(' + stripped + r'\\)')
                    result.append(trail)
                else:
                    result.append(seg)
            else:
                result.append(seg)
            i = j
    return ''.join(result)


def process_content(content):
    """Process a content string value.

    1. Unwrap existing \\(...\\) wrappers (for idempotency)
    2. Protect <code>...</code> blocks with placeholders
    3. Convert Unicode math symbols to LaTeX
    4. Wrap LaTeX segments with \\(...\\)
    5. Restore <code> blocks
    """
    # Step 1: Unwrap existing \\(...\\) wrappers (idempotency)
    content = unwrap_latex(content)

    # Step 2: Protect <code> blocks
    blocks = []

    def save_code(m):
        blocks.append(m.group(0))
        return f'\x00C{len(blocks) - 1}\x00'

    content = re.sub(r'<code>.*?</code>', save_code, content, flags=re.DOTALL)

    # Step 3: Convert Unicode to LaTeX
    content = convert_unicode(content)

    # Step 4: Wrap LaTeX segments
    content = wrap_latex(content)

    # Step 5: Restore <code> blocks
    for idx, code in enumerate(blocks):
        content = content.replace(f'\x00C{idx}\x00', code)

    return content


def main():
    filepath = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # Find the knowledgeBaseDetail region
    start_marker = 'const knowledgeBaseDetail = '
    end_marker = 'const animalAvatars = '

    start = text.find(start_marker)
    end = text.find(end_marker, start)

    if start == -1 or end == -1:
        print('Error: Could not find knowledgeBaseDetail region')
        sys.exit(1)

    region = text[start:end]
    count = [0]

    def process_match(m):
        prefix = m.group(1)   # "content": "
        value = m.group(2)    # the content value
        suffix = m.group(3)   # "
        converted = process_content(value)
        if converted != value:
            count[0] += 1
        return prefix + converted + suffix

    # Pattern matches "content": "..." where value can contain escaped chars
    pattern = re.compile(r'("content": ")((?:[^"\\]|\\.)*?)(")')

    new_region = pattern.sub(process_match, region)
    new_text = text[:start] + new_region + text[end:]

    if new_text != text:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_text)

    print(f'Fixed {count[0]} content fields')


if __name__ == '__main__':
    main()
