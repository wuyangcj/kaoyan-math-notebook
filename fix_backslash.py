#!/usr/bin/env python3
"""
Fix backslash encoding: in strings using \\\\frac (4-backslash) notation,
replace incorrectly added \\frac (2-backslash) with \\\\frac (4-backslash).
"""

import re

FILE_PATH = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'


def main():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find questionBank region
    qb_start = content.index('const questionBank = {')
    exam_start = content.index('const examPaperBank = {')
    qb_end = content.rfind('};', 0, exam_start)

    qb_text = content[qb_start:qb_end + 2]

    # Find shuyi and shuer regions
    shuyi_start = qb_text.index('"shuyi":')
    shuer_start = qb_text.index('"shuer":')
    shusan_start = qb_text.index('"shusan":')

    shuyi_text = qb_text[shuyi_start:shuer_start]
    shuer_text = qb_text[shuer_start:shusan_start]

    total_fixes = [0]

    def fix_region(text):
        """Fix \\frac (2 backslash) to \\\\frac (4 backslash) in double-escaped strings."""

        def fix_field(match):
            prefix = match.group(1)
            value = match.group(2)
            suffix = match.group(3)

            # Only fix if the string uses \\\\frac (4 backslashes) notation
            if r'\\\\frac' not in value and r'\\\\sin' not in value and r'\\\\cos' not in value and r'\\\\lim' not in value:
                return prefix + value + suffix

            # Count current \\frac (2 backslash, not part of \\\\frac)
            # Regex: exactly 2 backslashes before frac, not preceded by another backslash
            two_bs_frac = re.findall(r'(?<!\\)\\\\(?!\\)frac', value)
            total_fixes[0] += len(two_bs_frac)

            # Replace \\frac (2 backslash) with \\\\frac (4 backslash)
            new_value = re.sub(r'(?<!\\)\\\\(?!\\)frac', lambda m: r'\\\\frac', value)

            return prefix + new_value + suffix

        field_pattern = r'("(?:content|analysis|answer|approach|tips)"\s*:\s*")((?:[^"\\]|\\.)*)(\")'
        text = re.sub(field_pattern, fix_field, text)

        # Also fix knowledgePoints
        def fix_kp(match):
            prefix = match.group(1)
            array_content = match.group(2)
            suffix = match.group(3)

            def fix_item(m):
                full = m.group(0)
                v = full[1:-1]
                if r'\\\\frac' not in v and r'\\\\sin' not in v:
                    return full
                two_bs_frac = re.findall(r'(?<!\\)\\\\(?!\\)frac', v)
                total_fixes[0] += len(two_bs_frac)
                new_v = re.sub(r'(?<!\\)\\\\(?!\\)frac', lambda m: r'\\\\frac', v)
                return '"' + new_v + '"'

            array_content = re.sub(r'"(?:[^"\\]|\\.)*"', fix_item, array_content)
            return prefix + array_content + suffix

        kp_pattern = r'("knowledgePoints"\s*:\s*\[)([^\]]*)(\])'
        text = re.sub(kp_pattern, fix_kp, text)

        return text

    new_shuyi = fix_region(shuyi_text)
    new_shuer = fix_region(shuer_text)

    new_qb_text = qb_text[:shuyi_start] + new_shuyi + new_shuer + qb_text[shusan_start:]
    new_content = content[:qb_start] + new_qb_text + content[qb_end + 2:]

    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Fixed {total_fixes[0]} backslash encoding issues.")


if __name__ == '__main__':
    main()
