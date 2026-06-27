#!/usr/bin/env python3
"""Fix MathJax rendering errors in the HTML file.

Fixes:
1. Misplaced & : bare & in LaTeX regions -> \\&
2. Bare subscripts: _x -> _{x}
3. Bare superscripts: ^x -> ^{x}
4. Incomplete \\frac: check and report
5. Invalid LaTeX commands: check and report
"""

import re
import sys

FILE_PATH = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

# Data sections to process
SECTIONS = [
    'questionBank',
    'questionBankSupplement',
    'examPaperBank',
    'knowledgeBaseDetail',
    'knowledgeBaseSupplement',
]


def find_section(text, name):
    """Find a const NAME = { ... }; section. Returns (start, end) or None."""
    pattern = r'const ' + re.escape(name) + r'\s*=\s*\{'
    m = re.search(pattern, text)
    if not m:
        return None
    start = m.start()
    depth = 0
    i = m.end() - 1  # position of opening {
    while i < len(text):
        c = text[i]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                # Include trailing semicolon
                while end < len(text) and text[end] in ' \t':
                    end += 1
                if end < len(text) and text[end] == ';':
                    end += 1
                return (start, end)
        i += 1
    return None


def find_latex_regions(text):
    """Find all LaTeX regions: \\( ... \\), $$ ... $$, <code> ... </code>.

    Returns list of (start, end, type) tuples sorted by start position.
    """
    regions = []

    # Inline math: \( ... \) — in the file this appears as \\( ... \\)
    # Use non-greedy match; [\s\S] to match across newlines if needed
    for m in re.finditer(r'\\\\\([\s\S]+?\\\\\)', text):
        regions.append((m.start(), m.end(), 'inline'))

    # Display math: $$ ... $$
    for m in re.finditer(r'\$\$[\s\S]+?\$\$', text):
        regions.append((m.start(), m.end(), 'display'))

    # Code blocks: <code> ... </code>
    for m in re.finditer(r'<code>[\s\S]+?</code>', text):
        regions.append((m.start(), m.end(), 'code'))

    regions.sort()
    return regions


def fix_bare_amp(text):
    """Fix bare & -> \\& in LaTeX text.

    Don't touch HTML entities (&amp;, &lt;, &gt;, &nbsp;, &quot;, &#...;).
    Don't touch already-escaped & (\\&).
    """
    fixes = []

    def repl(m):
        fixes.append((m.group(0), '\\\\&'))
        return '\\\\&'

    # Match & not preceded by \ and not followed by HTML entity name
    text = re.sub(
        r'(?<!\\)&(?!amp;|lt;|gt;|nbsp;|quot;|#[0-9]+;|#[xX][0-9a-fA-F]+;)',
        repl,
        text,
    )
    return text, fixes


def fix_bare_subscript(text):
    """Fix bare subscripts: _x -> _{x}.

    Don't touch _{...} (already braced).
    Don't touch \\_ (escaped underscore).
    Don't touch \\underline (command).
    """
    fixes = []

    def repl(m):
        replacement = '_{' + m.group(1) + '}'
        fixes.append((m.group(0), replacement))
        return replacement

    # Match _ not preceded by \, followed by alphanumeric chars (not {)
    text = re.sub(r'(?<!\\)_([a-zA-Z0-9]+)', repl, text)
    return text, fixes


def fix_bare_superscript(text):
    """Fix bare superscripts: ^x -> ^{x}.

    Don't touch ^{...} (already braced).
    Don't touch \\^ (escaped).
    """
    fixes = []

    def repl(m):
        replacement = '^{' + m.group(1) + '}'
        fixes.append((m.group(0), replacement))
        return replacement

    # Match ^ not preceded by \, followed by alphanumeric chars (not {)
    text = re.sub(r'(?<!\\)\^([a-zA-Z0-9]+)', repl, text)
    return text, fixes


def check_incomplete_frac(text):
    """Check for \\frac not followed by {..}{..}."""
    issues = []
    # In the file, \frac is written as \\frac
    for m in re.finditer(r'\\\\frac(?!\s*\{[^}]*\}\s*\{[^}]*\})', text):
        pos = m.start()
        context = text[max(0, pos - 20):min(len(text), pos + 60)]
        issues.append(context)
    return issues


def check_invalid_commands(text):
    """Check for common misspelled LaTeX commands."""
    issues = []
    # Common misspellings
    misspellings = [
        (r'\\\\frak\b', '\\\\frac'),      # \frak -> \frac
        (r'\\\\sqr\b', '\\\\sqrt'),        # \sqr -> \sqrt
        (r'\\\\sqrtp\b', '\\\\sqrt'),      # \sqrtp -> \sqrt
        (r'\\\\intf\b', '\\\\int'),        # \intf -> \int
        (r'\\\\limt\b', '\\\\lim'),        # \limt -> \lim
        (r'\\\\sigt\b', '\\\\sum'),        # \sigt -> \sum
        (r'\\\\alph\b', '\\\\alpha'),      # \alph -> \alpha
        (r'\\\\bet\b', '\\\\beta'),        # \bet -> \beta
        (r'\\\\thet\b', '\\\\theta'),      # \thet -> \theta
        (r'\\\\sinx\b', '\\\\sin'),        # \sinx -> \sin
        (r'\\\\cosx\b', '\\\\cos'),        # \cosx -> \cos
        (r'\\\\frac\b(?!\{)', None),       # \frac without { — just report
    ]
    for pattern, replacement in misspellings:
        for m in re.finditer(pattern, text):
            pos = m.start()
            context = text[max(0, pos - 20):min(len(text), pos + 40)]
            issues.append((m.group(0), replacement, context))
    return issues


def fix_latex_region(region_text):
    """Apply all fixes to a single LaTeX region.

    Returns (fixed_text, fix_count, fix_details, check_issues).
    """
    all_fixes = []
    check_issues = []

    # Fix 1: Bare & -> \\&
    region_text, fixes = fix_bare_amp(region_text)
    all_fixes.extend([('amp', old, new) for old, new in fixes])

    # Fix 2: Bare subscripts _x -> _{x}
    region_text, fixes = fix_bare_subscript(region_text)
    all_fixes.extend([('sub', old, new) for old, new in fixes])

    # Fix 3: Bare superscripts ^x -> ^{x}
    region_text, fixes = fix_bare_superscript(region_text)
    all_fixes.extend([('sup', old, new) for old, new in fixes])

    # Check 4: Incomplete \frac
    frac_issues = check_incomplete_frac(region_text)
    for issue in frac_issues:
        check_issues.append(('frac', issue))

    # Check 5: Invalid commands
    cmd_issues = check_invalid_commands(region_text)
    for found, repl, ctx in cmd_issues:
        check_issues.append(('cmd', found, repl, ctx))

    return region_text, len(all_fixes), all_fixes, check_issues


def main():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    original_len = len(text)
    total_fixes = 0
    all_details = []
    all_checks = []

    for section_name in SECTIONS:
        section_range = find_section(text, section_name)
        if not section_range:
            print(f'{section_name}: NOT FOUND')
            continue

        start, end = section_range
        section_text = text[start:end]

        # Find LaTeX regions in this section
        regions = find_latex_regions(section_text)

        # Apply fixes from end to start (so positions don't shift)
        section_fixes = 0
        section_checks = []
        for r_start, r_end, r_type in reversed(regions):
            region_text = section_text[r_start:r_end]
            fixed_text, fix_count, fixes, checks = fix_latex_region(region_text)
            if fix_count > 0:
                section_text = (
                    section_text[:r_start] + fixed_text + section_text[r_end:]
                )
                section_fixes += fix_count
                for fix_type, old, new in fixes:
                    all_details.append(
                        (section_name, r_type, fix_type, old, new)
                    )
            for check in checks:
                section_checks.append((section_name, r_type, check))

        # Replace the section in the original text
        text = text[:start] + section_text + text[end:]
        print(f'{section_name}: {section_fixes} fixes, {len(section_checks)} checks')
        total_fixes += section_fixes
        all_checks.extend(section_checks)

    # Verify text length hasn't changed unexpectedly
    if len(text) != original_len:
        print(
            f'WARNING: text length changed from {original_len} to {len(text)}'
        )

    # Write the fixed text
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f'\nTotal fixes applied: {total_fixes}')

    # Print fix summary by type
    by_type = {}
    for section, rtype, fix_type, old, new in all_details:
        key = (section, rtype, fix_type)
        by_type[key] = by_type.get(key, 0) + 1

    if by_type:
        print('\nFix summary:')
        for (section, rtype, fix_type), count in sorted(by_type.items()):
            print(f'  {section}/{rtype}/{fix_type}: {count}')

    # Print sample fixes
    if all_details:
        print(f'\nSample fixes (first 30 of {len(all_details)}):')
        for section, rtype, fix_type, old, new in all_details[:30]:
            print(f'  [{section}/{rtype}] {fix_type}: {old!r} -> {new!r}')

    # Print check issues
    if all_checks:
        print(f'\nCheck issues ({len(all_checks)} found, not auto-fixed):')
        for section, rtype, check in all_checks[:20]:
            if check[0] == 'frac':
                print(f'  [{section}/{rtype}] incomplete \\frac: ...{check[1]}...')
            elif check[0] == 'cmd':
                repl_str = repr(check[2]) if check[2] else 'REPORT'
                print(
                    f'  [{section}/{rtype}] invalid cmd: {check[1]!r}'
                    f' -> {repl_str}'
                    f'  ctx: ...{check[3]}...'
                )


if __name__ == '__main__':
    main()
