#!/usr/bin/env python3
# 修复收集到的题目JSON文件：
# 1. 把 $...$ 替换为 \(...\)（与项目MathJax配置一致）
# 2. 把单反斜杠LaTeX命令改为双反斜杠（因为要写入JS字符串）
# 3. 修复裸下标/上标

import json
import re
import os

def fix_latex_in_text(text):
    """修复文本中的LaTeX格式"""
    if not text:
        return text

    # 1. 把 $...$ 替换为 \(...\)
    # 非贪婪匹配，注意 $$ 的情况
    text = re.sub(r'\$\$([^\$]+)\$\$', r'\\[\1\\]', text)
    text = re.sub(r'\$([^\$]+)\$', r'\\(\1\\)', text)

    # 2. 把单反斜杠LaTeX命令改为双反斜杠
    # 匹配 \letter 但不是 \\letter（已经是双反斜杠的不动）
    # 用负向回顾断言：前面不是反斜杠
    text = re.sub(r'(?<!\\)\\([a-zA-Z]+)', r'\\\\\1', text)

    # 3. 修复裸下标：\int_0 -> \int_{0}（在双反斜杠上下文中）
    for cmd in ['int', 'iint', 'iiint', 'oint', 'sum', 'prod']:
        # \int_0 -> \int_{0}，但不改 \int_{0} 或 \int_\infty
        text = re.sub(
            r'(\\\\' + cmd + r')_([a-zA-Z0-9])(?![a-zA-Z0-9{}\\])',
            r'\1_{\2}',
            text
        )

    # 4. 修复 }^1 -> }^{1}
    text = re.sub(r'\}\^([a-zA-Z0-9])(?![a-zA-Z0-9{}\\])', r'}^{\1}', text)

    return text

def fix_question(q):
    """修复一道题的所有文本字段"""
    for field in ['content', 'analysis']:
        if field in q and q[field]:
            q[field] = fix_latex_in_text(q[field])

    if 'options' in q and q['options']:
        q['options'] = [fix_latex_in_text(opt) for opt in q['options']]

    if 'hint' in q and isinstance(q['hint'], dict):
        for field in ['approach', 'tips']:
            if field in q['hint'] and q['hint'][field]:
                q['hint'][field] = fix_latex_in_text(q['hint'][field])

    return q

def main():
    base = '/Users/wuyangcj/trae/回甘demo'

    for fname in ['collected_real_exams.json', 'collected_social_questions.json']:
        fpath = os.path.join(base, fname)
        if not os.path.exists(fpath):
            print(f'跳过（不存在）: {fname}')
            continue

        with open(fpath, 'r', encoding='utf-8') as f:
            questions = json.load(f)

        print(f'\n=== 修复 {fname} ===')
        print(f'题目数: {len(questions)}')

        fixed_count = 0
        for i, q in enumerate(questions):
            original = json.dumps(q, ensure_ascii=False)
            q = fix_question(q)
            fixed = json.dumps(q, ensure_ascii=False)
            if fixed != original:
                fixed_count += 1

        print(f'修复了 {fixed_count} 道题')

        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

        # 验证：检查还有没有单反斜杠
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        # 在JSON文件中，双反斜杠显示为 \\
        # 检查是否有 \letter 但不是 \\letter
        bad = re.findall(r'(?<!\\)\\(?!\\)[a-zA-Z]+', content)
        print(f'剩余单反斜杠LaTeX: {len(bad)}')

if __name__ == '__main__':
    main()
