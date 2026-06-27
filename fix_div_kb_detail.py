#!/usr/bin/env python3
"""
Fix division in math expressions in knowledgeBaseDetail.
Convert / division to \\frac{}{} in math contexts.

Rules:
- 1/2 → \\frac{1}{2}
- a/b → \\frac{a}{b}
- dy/dx → \\frac{dy}{dx}
- (x+1)/(x-1) → \\frac{x+1}{x-1}
- 2x/y → \\frac{2x}{y}

Do NOT convert:
- / in URLs
- / in HTML tags
- / in dates
- / already inside \\frac{}{}
"""

import json
import re
import sys


def find_matching_bracket_backward(text, pos, open_bracket, close_bracket):
    """Find the opening bracket that matches the closing bracket at pos.
    pos points to the closing bracket.
    Returns the position of the opening bracket, or -1 if not found.
    """
    depth = 1
    i = pos - 1
    while i >= 0 and depth > 0:
        if text[i] == close_bracket:
            depth += 1
        elif text[i] == open_bracket:
            depth -= 1
        i -= 1
    if depth == 0:
        return i + 1
    return -1


def find_matching_bracket_forward(text, pos, open_bracket, close_bracket):
    """Find the closing bracket that matches the opening bracket at pos.
    pos points to the opening bracket.
    Returns the position of the closing bracket, or -1 if not found.
    """
    depth = 1
    i = pos + 1
    while i < len(text) and depth > 0:
        if text[i] == open_bracket:
            depth += 1
        elif text[i] == close_bracket:
            depth -= 1
        i += 1
    if depth == 0:
        return i - 1
    return -1


def strip_outer_brackets(s):
    """Strip outer brackets if they match."""
    if len(s) < 2:
        return s
    bracket_pairs = [('(', ')'), ('[', ']'), ('{', '}')]
    for open_b, close_b in bracket_pairs:
        if s[0] == open_b and s[-1] == close_b:
            end = find_matching_bracket_forward(s, 0, open_b, close_b)
            if end == len(s) - 1:
                return s[1:-1]
    return s


def get_left_operand_range(text, slash_pos):
    """Returns (start, end) where text[start:end] is the left operand."""
    i = slash_pos - 1
    # Skip whitespace
    while i >= 0 and text[i] in ' \t':
        i -= 1
    if i < 0:
        return None

    end = i + 1

    # Check for closing bracket
    if text[i] == ')':
        start = find_matching_bracket_backward(text, i, '(', ')')
        if start >= 0:
            return (start, end)
        return None
    elif text[i] == ']':
        start = find_matching_bracket_backward(text, i, '[', ']')
        if start >= 0:
            return (start, end)
        return None
    elif text[i] == '}':
        start = find_matching_bracket_backward(text, i, '{', '}')
        if start >= 0:
            return (start, end)
        return None
    elif text[i] == '|':
        # Find the other |
        j = i - 1
        while j >= 0:
            if text[j] == '|':
                return (j, end)
            j -= 1
        return None

    # Simple token: alphanumeric, ^, _, ', *, and LaTeX commands
    while i >= 0:
        c = text[i]
        if c.isalnum() or c in "_^'*":
            i -= 1
        elif c == '}':
            # Part of a subscript/superscript like x^{2}
            start = find_matching_bracket_backward(text, i, '{', '}')
            if start >= 0:
                i = start - 1
            else:
                break
        elif c == '\\':
            # LaTeX command
            i -= 1
            while i >= 0 and text[i].isalpha():
                i -= 1
            break
        else:
            break

    start = i + 1
    if start < end:
        return (start, end)
    return None


def get_right_operand_range(text, slash_pos):
    """Returns (start, end) where text[start:end] is the right operand."""
    i = slash_pos + 1
    # Skip whitespace
    while i < len(text) and text[i] in ' \t':
        i += 1
    if i >= len(text):
        return None

    start = i

    # Check for opening bracket
    if text[i] == '(':
        end = find_matching_bracket_forward(text, i, '(', ')')
        if end >= 0:
            return (start, end + 1)
        return None
    elif text[i] == '[':
        end = find_matching_bracket_forward(text, i, '[', ']')
        if end >= 0:
            return (start, end + 1)
        return None
    elif text[i] == '{':
        end = find_matching_bracket_forward(text, i, '{', '}')
        if end >= 0:
            return (start, end + 1)
        return None
    elif text[i] == '|':
        # Find the other |
        j = i + 1
        while j < len(text):
            if text[j] == '|':
                return (start, j + 1)
            j += 1
        return None

    # Simple token
    while i < len(text):
        c = text[i]
        if c.isalnum() or c in "_^'*":
            i += 1
        elif c == '{':
            end = find_matching_bracket_forward(text, i, '{', '}')
            if end >= 0:
                i = end + 1
            else:
                break
        elif c == '\\':
            i += 1
            while i < len(text) and text[i].isalpha():
                i += 1
            break
        else:
            break

    end = i
    if start < end:
        return (start, end)
    return None


def is_inside_frac(text, pos):
    """Check if position pos is inside a \\frac{...} argument."""
    depth = 0
    i = pos - 1
    while i >= 0:
        if text[i] == '}':
            depth += 1
        elif text[i] == '{':
            if depth == 0:
                # This is the most recent unclosed {
                # Case 1: \frac{arg1} - check if text before { ends with \frac
                prefix = text[:i]
                if prefix.endswith('\\frac'):
                    return True
                # Case 2: \frac{arg1}{arg2} - the { is preceded by }
                if i > 0 and text[i - 1] == '}':
                    # Find the matching { for this }
                    first_brace = find_matching_bracket_backward(text, i - 1, '{', '}')
                    if first_brace >= 0:
                        prefix2 = text[:first_brace]
                        if prefix2.endswith('\\frac'):
                            return True
                return False
            depth -= 1
        i -= 1
    return False


def convert_division_in_math(text):
    """Convert / division to \\frac{}{} in math text.
    Returns (converted_text, num_replacements).
    """
    replacements = []
    i = 0
    while i < len(text):
        if text[i] == '/':
            # Skip if preceded by \ (LaTeX command like \/)
            if i > 0 and text[i - 1] == '\\':
                i += 1
                continue

            # Skip if part of // (URL or comment)
            if i > 0 and text[i - 1] == '/':
                i += 1
                continue
            if i + 1 < len(text) and text[i + 1] == '/':
                i += 1
                continue

            # Skip if part of HTML tag </ or />
            if i > 0 and text[i - 1] == '<':
                i += 1
                continue
            if i + 1 < len(text) and text[i + 1] == '>':
                i += 1
                continue

            # Skip if inside \frac{}{}
            if is_inside_frac(text, i):
                i += 1
                continue

            left = get_left_operand_range(text, i)
            right = get_right_operand_range(text, i)

            if left and right:
                left_text = text[left[0]:left[1]]
                right_text = text[right[0]:right[1]]

                # Skip if either operand is empty
                if not left_text.strip() or not right_text.strip():
                    i += 1
                    continue

                # Strip outer brackets
                left_stripped = strip_outer_brackets(left_text)
                right_stripped = strip_outer_brackets(right_text)

                replacement = '\\frac{' + left_stripped + '}{' + right_stripped + '}'
                replacements.append((left[0], right[1], replacement))
                i = right[1]
                continue

        i += 1

    # Apply replacements from right to left
    result = text
    for start, end, replacement in sorted(replacements, key=lambda x: -x[0]):
        result = result[:start] + replacement + result[end:]

    return result, len(replacements)


def process_string(s):
    """Process a string value, converting / to \\frac{}{} in math contexts.
    Returns (converted_string, num_replacements).
    """
    if not isinstance(s, str):
        return s, 0

    total_replacements = 0
    result_parts = []
    pos = 0

    # Find all math regions
    math_regions = []

    # \( ... \) - inline math
    for m in re.finditer(r'\\\((.+?)\\\)', s, re.DOTALL):
        math_regions.append((m.start(), m.end()))

    # $$ ... $$ - display math
    for m in re.finditer(r'\$\$(.+?)\$\$', s, re.DOTALL):
        math_regions.append((m.start(), m.end()))

    # <code>...</code>
    for m in re.finditer(r'<code>(.+?)</code>', s, re.DOTALL):
        math_regions.append((m.start(), m.end()))

    # Sort and merge overlapping regions
    math_regions.sort()
    merged = []
    for start, end in math_regions:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    # Process each region
    for start, end in merged:
        if start > pos:
            result_parts.append(s[pos:start])
        math_text = s[start:end]
        converted, count = convert_division_in_math(math_text)
        result_parts.append(converted)
        total_replacements += count
        pos = end

    if pos < len(s):
        result_parts.append(s[pos:])

    return ''.join(result_parts), total_replacements


def process_object(obj):
    """Recursively process an object, converting / to \\frac{}{} in string values.
    Returns (processed_object, num_replacements).
    """
    total = 0
    if isinstance(obj, dict):
        for key in obj:
            obj[key], count = process_object(obj[key])
            total += count
    elif isinstance(obj, list):
        for i in range(len(obj)):
            obj[i], count = process_object(obj[i])
            total += count
    elif isinstance(obj, str):
        processed, count = process_string(obj)
        return processed, count
    return obj, total


def main():
    html_file = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the knowledgeBaseDetail region
    start_marker = 'const knowledgeBaseDetail = '
    end_marker = 'const animalAvatars'

    start_pos = content.find(start_marker)
    if start_pos == -1:
        print("ERROR: Could not find knowledgeBaseDetail")
        return 1

    json_start = start_pos + len(start_marker)

    end_pos = content.find(end_marker, json_start)
    if end_pos == -1:
        print("ERROR: Could not find end of knowledgeBaseDetail")
        return 1

    # Use JSONDecoder to find the end of the JSON object
    decoder = json.JSONDecoder()
    try:
        data, json_end = decoder.raw_decode(content[json_start:])
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}")
        return 1

    json_end_abs = json_start + json_end

    # Process the data
    data, total_replacements = process_object(data)

    # Serialize back to JSON
    new_json_text = json.dumps(data, ensure_ascii=False, indent=2)

    # Replace in the content
    new_content = content[:json_start] + new_json_text + content[json_end_abs:]

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Fixed {total_replacements} divisions")
    return 0


if __name__ == '__main__':
    sys.exit(main())
