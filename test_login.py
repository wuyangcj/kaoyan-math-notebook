#!/usr/bin/env python3
"""
TDD 测试：登录功能。
复现问题：HTML 内嵌 JS 存在语法错误时，整个脚本无法解析，导致 login 未定义、无法登录。
"""
import re
import subprocess
import sys
from pathlib import Path

HTML = Path(__file__).with_name('回甘—考研数学智题本.html')


def extract_js():
    html = HTML.read_text(encoding='utf-8')
    scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
    return '\n'.join(scripts)


def test_html_js_parses():
    """HTML 中的内嵌 JS 必须能被 Node.js 语法检查通过。"""
    js = extract_js()
    js_file = Path('/tmp/app_login_test.js')
    js_file.write_text(js, encoding='utf-8')
    result = subprocess.run(
        ['node', '--check', str(js_file)],
        capture_output=True,
        text=True,
        errors='replace',
    )
    if result.returncode != 0:
        raise AssertionError('JS syntax error:\n' + result.stderr)


def test_login_function_defined():
    """login 函数必须在全局作用域可被调用。"""
    js = extract_js()
    js_file = Path('/tmp/app_login_test.js')
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
        + 'if (typeof login !== "function") { throw new Error("login is not defined"); }\n',
        encoding='utf-8',
    )
    result = subprocess.run(
        ['node', str(js_file)],
        capture_output=True,
        text=True,
        errors='replace',
    )
    if result.returncode != 0:
        raise AssertionError('login function not defined:\n' + result.stderr)


if __name__ == '__main__':
    test_html_js_parses()
    test_login_function_defined()
    print('All login tests passed.')
