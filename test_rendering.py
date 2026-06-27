#!/usr/bin/env python3
"""
TDD 测试：公式渲染与页面文本。
确保 _mathToLatex/formatMath 不会把希腊字母/符号映射成断行垃圾，
确保欢迎语文本不会出现原样 LaTeX 命令。
"""
import re
import subprocess
from pathlib import Path

HTML = Path(__file__).with_name('回甘—考研数学智题本.html')


def extract_js():
    html = HTML.read_text(encoding='utf-8')
    scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
    return '\n'.join(scripts)


def run_js_expression(expr: str):
    """在 mock 浏览器环境中运行 JS 表达式并返回标准输出。"""
    js = extract_js()
    js_file = Path('/tmp/app_rendering_test.js')
    js_file.write_text(
        'global.window = global;\n'
        'global.document = {\n'
        '  readyState: "complete",\n'
        '  documentElement: { setAttribute: () => {}, getAttribute: () => null },\n'
        '  getElementById: () => null,\n'
        '  querySelector: () => null,\n'
        '  querySelectorAll: () => [],\n'
        '  addEventListener: () => {},\n'
        '};\n'
        'global.localStorage = { getItem: () => null, setItem: () => {} };\n'
        + js + '\n'
        + 'console.log(' + expr + ');\n',
        encoding='utf-8',
    )
    result = subprocess.run(
        ['node', str(js_file)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError('JS runtime error:\n' + result.stderr)
    return result.stdout.strip()


def test_math_to_latex_greek_nu():
    """希腊字母 ν 必须映射为 \\nu，不能变成断行后的 'u'。"""
    assert run_js_expression("_mathToLatex('ν')") == '\\nu'


def test_math_to_latex_not_equal():
    """≠ 必须映射为 \\neq。"""
    assert run_js_expression("_mathToLatex('≠')") == '\\neq'


def test_math_to_latex_nabla():
    """∇ 必须映射为 \\nabla。"""
    assert run_js_expression("_mathToLatex('∇')") == '\\nabla'


def test_math_to_latex_notin():
    """∉ 必须映射为 \\notin。"""
    assert run_js_expression("_mathToLatex('∉')") == '\\notin'


def test_format_math_wraps_latex_sim():
    """纯文本里的 \\sim 应该被识别为 LaTeX 并包裹进数学定界符。"""
    out = run_js_expression("formatMath('晚间刷题效率更高哦\\\\sim')")
    assert '\\sim' in out
    assert '\\(' in out and '\\)' in out


def test_welcome_subtext_no_raw_latex():
    """欢迎语文本源码中不应该出现原样 \\sim 这类未渲染的 LaTeX 命令。"""
    html = HTML.read_text(encoding='utf-8')
    # 匹配 welcomeSubtext 赋值区域里的字符串字面量
    matches = re.findall(r"subtext = '([^']*\\\\sim[^']*)'", html)
    assert not matches, 'welcomeSubtext 源码里仍含有未处理的 \\sim: ' + str(matches)


def _extract_string_contents(js: str):
    """从 JS 源码中提取所有字符串字面量的内容（简化状态机，不处理嵌套）。"""
    contents = []
    i = 0
    n = len(js)
    while i < n:
        ch = js[i]
        if ch in ('"', "'", '`'):
            quote = ch
            i += 1
            start = i
            while i < n:
                if js[i] == '\\' and i + 1 < n:
                    i += 2
                elif js[i] == quote:
                    contents.append(js[start:i])
                    i += 1
                    break
                else:
                    i += 1
            continue
        i += 1
    return contents


def test_no_url_frac_corruption():
    """URL/路径里不应该出现 \frac{domain}{path} 这种垃圾转换残留。"""
    html = HTML.read_text(encoding='utf-8')
    bad = []
    for m in re.finditer(r'https?://[^\s"\']*\\frac\{[^}]+\}', html):
        bad.append(m.group(0))
    for m in re.finditer(r'api\.[^\s"\']*\\frac\{[^}]+\}', html):
        bad.append(m.group(0))
    assert not bad, '发现 URL 被 \frac 污染: ' + str(bad[:5])


if __name__ == '__main__':
    test_math_to_latex_greek_nu()
    test_math_to_latex_not_equal()
    test_math_to_latex_nabla()
    test_math_to_latex_notin()
    test_format_math_wraps_latex_sim()
    test_welcome_subtext_no_raw_latex()
    test_no_url_frac_corruption()
    print('All rendering tests passed.')
