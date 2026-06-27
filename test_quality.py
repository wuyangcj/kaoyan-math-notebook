#!/usr/bin/env python3
r"""
TDD 测试：题目数据与知识库中的公式垃圾模式。
确保不会把明显损坏的 LaTeX（如 \frac{^{n}}{n}、\sigm\frac{a^2}{n} 等）渲染到页面上。
"""
import re
from pathlib import Path

HTML = Path(__file__).with_name('回甘—考研数学智题本.html')


def _data_text():
    """提取 HTML 中可能包含公式数据的所有文本内容（简单、保守）。"""
    return HTML.read_text(encoding='utf-8')


def test_no_broken_sigma_square():
    r"""\sigma^2 不能被拆成 \sigm\frac{a^2}{n} 这种垃圾。"""
    text = _data_text()
    bad = re.findall(r'\\\\sigm\\\\frac\{a\^2\}', text)
    assert not bad, f'发现 {len(bad)} 处 \\sigma^2 被错误拆分'


def test_no_broken_pi_square():
    r"""\pi^2 不能被拆成 \p\frac{i^2}{n} 这种垃圾。"""
    text = _data_text()
    bad = re.findall(r'\\\\p\\\\frac\{i\^2\}', text)
    assert not bad, f'发现 {len(bad)} 处 \\pi^2 被错误拆分'


def test_no_frac_with_symbol_only_numerator():
    r"""\frac 的分子不能只有 ^/_/) 等孤立符号。"""
    text = _data_text()
    bad = []
    for m in re.finditer(r'\\\\frac\{([\^_)\]]+)\}\{', text):
        content = m.group(1).strip()
        if content in ('^', '_', ')', ']', '^{', '_{'):
            bad.append(m.group(0))
        elif re.match(r'^[\^_)\]]+$', content):
            bad.append(m.group(0))
    assert not bad, f'发现 {len(bad)} 处 \\frac 分子只有符号: {bad[:5]}'


def test_no_frac_with_power_base_missing():
    r"""\frac{^{n}}{...} 这类丢失幂底的写法是垃圾。"""
    text = _data_text()
    bad = re.findall(r'\\\\frac\{\^\{[^}]+\}\}\{', text)
    assert not bad, f'发现 {len(bad)} 处 \\frac 分子丢失幂底: {bad[:5]}'


def test_no_frac_with_sub_base_missing():
    r"""\frac{_{n}}{...} 这类丢失下标底的写法是垃圾。"""
    text = _data_text()
    bad = re.findall(r'\\\\frac\{_\{[^}]+\}\}\{', text)
    assert not bad, f'发现 {len(bad)} 处 \\frac 分子丢失下标底: {bad[:5]}'


def test_no_frac_with_closing_paren_only():
    r"""\frac{)^{n}}{...} 这类把右括号单独放分子的写法是垃圾。"""
    text = _data_text()
    bad = re.findall(r'\\\\frac\{\)[\^\{]?[^}]*\}\{', text)
    assert not bad, f'发现 {len(bad)} 处 \\frac 分子只有右括号: {bad[:5]}'


def test_no_pmb_instead_of_pm_b():
    r"""依概率收敛性质里 a\pmb 应是 a \pm b。"""
    text = _data_text()
    bad = re.findall(r'[a-zA-Z]\\\\pmb\\b', text)
    assert not bad, f'发现 {len(bad)} 处 \\pmb 垃圾（应为 \\pm b）'


def test_sqrt_followed_by_lowercase_letter():
    r"""\sqrt 紧跟小写字母（非命令）时应带花括号，如 \sqrt{x}。"""
    text = _data_text()
    bad = re.findall(r'\\\\sqrt([a-z])', text)
    assert not bad, f'发现 {len(bad)} 处 \\sqrt 后缺花括号: {bad[:10]}'


if __name__ == '__main__':
    test_no_broken_sigma_square()
    test_no_broken_pi_square()
    test_no_frac_with_symbol_only_numerator()
    test_no_frac_with_power_base_missing()
    test_no_frac_with_sub_base_missing()
    test_no_frac_with_closing_paren_only()
    test_no_pmb_instead_of_pm_b()
    test_sqrt_followed_by_lowercase_letter()
    print('All quality tests passed.')
