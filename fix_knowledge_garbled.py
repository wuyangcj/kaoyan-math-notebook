#!/usr/bin/env python3
"""
Fix garbled LaTeX expressions in <code> blocks within the knowledgeBaseDetail
and knowledgeBaseSupplement regions of the HTML file.

Fixes applied:
  a/b/c. LaTeX commands (\\mathrm, \\cdot, \\int, \\frac, \\sqrt, ...) are
         verified to already use double backslashes in the JSON source — no
         change needed (defensive check included).
  d. Fix bare subscripts:   _n  -> _{n},  _0  -> _{0},  _(expr) -> _{(expr)}
     (leaves _{n} and _\\command untouched)
  e. Fix bare superscripts: ^x  -> ^{x},  ^2  -> ^{2},  ^(expr) -> ^{(expr)}
     (leaves ^{x} and ^\\command untouched)
"""

import os
import re

HTML_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '回甘—考研数学智题本.html',
)

# Region markers
DETAIL_START = 'const knowledgeBaseDetail = {'
DETAIL_END = 'const animalAvatars ='
SUP_START = 'const knowledgeBaseSupplement = {'
SUP_END = 'const knowledgeNameMap ='

# Patterns for bare subscripts / superscripts.
# Negative lookahead (?![{\\(]) skips already-braced forms (_{...}, ^{...})
# and LaTeX command forms (_\\infty, ^\\mathrm).
SUB_PAREN = re.compile(r'_\(([^()]*)\)')
SUB_SINGLE = re.compile(r'_(?![{\\(])([a-zA-Z0-9])')
SUP_PAREN = re.compile(r'\^\(([^()]*)\)')
SUP_SINGLE = re.compile(r'\^(?![{\\(])([a-zA-Z0-9])')

# Defensive: a single backslash before a letter that is not part of a "\\" pair.
# In valid JSON source, every literal backslash is written as "\\". Analysis
# showed zero such issues; this is a safety net that reports (not fixes) them
# to avoid any risk of corrupting JSON escape sequences like \n or \t.
LONE_BACKSLASH = re.compile(r'(?<!\\)\\(?![\\])(?=[a-zA-Z])')


def fix_code_block(inner):
    """Return (fixed_text, changed_flag) for a <code> block's inner text."""
    original = inner

    # (d) Bare subscripts: parenthesized form first, then single char.
    inner = SUB_PAREN.sub(r'_{(\1)}', inner)
    inner = SUB_SINGLE.sub(r'_{\1}', inner)

    # (e) Bare superscripts: parenthesized form first, then single char.
    inner = SUP_PAREN.sub(r'^{(\1)}', inner)
    inner = SUP_SINGLE.sub(r'^{\1}', inner)

    return inner, inner != original


def count_bare(text, paren_re, single_re):
    return len(paren_re.findall(text)) + len(single_re.findall(text))


def main():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    ds = html.find(DETAIL_START)
    de = html.find(DETAIL_END, ds)
    ss = html.find(SUP_START)
    se = html.find(SUP_END, ss)

    if ds == -1 or de == -1:
        raise SystemExit('ERROR: knowledgeBaseDetail region not found')
    if ss == -1 or se == -1:
        raise SystemExit('ERROR: knowledgeBaseSupplement region not found')

    print(f'Detail region:      bytes {ds}..{de} ({de - ds} bytes)')
    print(f'Supplement region:  bytes {ss}..{se} ({se - ss} bytes)')

    stats = {
        'blocks_seen': 0,
        'blocks_changed': 0,
        'subs_fixed': 0,
        'sups_fixed': 0,
        'lone_backslash_blocks': 0,
    }

    def process_region(region):
        def repl(m):
            stats['blocks_seen'] += 1
            inner = m.group(1)

            if LONE_BACKSLASH.search(inner):
                stats['lone_backslash_blocks'] += 1

            subs = count_bare(inner, SUB_PAREN, SUB_SINGLE)
            sups = count_bare(inner, SUP_PAREN, SUP_SINGLE)

            fixed, changed = fix_code_block(inner)

            if changed:
                stats['blocks_changed'] += 1
                stats['subs_fixed'] += subs
                stats['sups_fixed'] += sups
            return '<code>' + fixed + '</code>'

        return re.sub(r'<code>([^<]*)</code>', repl, region)

    detail_fixed = process_region(html[ds:de])
    sup_fixed = process_region(html[ss:se])

    new_html = html[:ds] + detail_fixed + html[de:ss] + sup_fixed + html[se:]

    if new_html == html:
        print('\nNo changes were needed.')
        return

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print('\n=== Summary of fixes ===')
    print(f'<code> blocks scanned:      {stats["blocks_seen"]}')
    print(f'<code> blocks modified:     {stats["blocks_changed"]}')
    print(f'Bare subscripts fixed:      {stats["subs_fixed"]}')
    print(f'Bare superscripts fixed:    {stats["sups_fixed"]}')
    print(f'Blocks with lone backslash: {stats["lone_backslash_blocks"]} '
          f'(reported only, not modified)')
    print(f'\nFile updated: {HTML_PATH}')


if __name__ == '__main__':
    main()
