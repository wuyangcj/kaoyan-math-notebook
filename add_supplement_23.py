#!/usr/bin/env python3
# 给 shuer 和 shusan 添加 supplement 数组并插入题目

import json
import re

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open('/Users/wuyangcj/trae/回甘demo/collected_real_exams.json', 'r', encoding='utf-8') as f:
    real_questions = json.load(f)

with open('/Users/wuyangcj/trae/回甘demo/collected_social_questions.json', 'r', encoding='utf-8') as f:
    social_questions = json.load(f)

# 按卷种分组真题
math2_real = [q for q in real_questions if q.get('paper') == '数学二']
math3_real = [q for q in real_questions if q.get('paper') == '数学三']
# 自建题目：数二只分高数和线代（不考概率），数三全科目
social_math2 = [q for q in social_questions if q.get('subject') in ['高数', '线代']]
social_math3 = social_questions

print(f'数二: 真题{len(math2_real)} + 自建{len(social_math2)} = {len(math2_real)+len(social_math2)}')
print(f'数三: 真题{len(math3_real)} + 自建{len(social_math3)} = {len(math3_real)+len(social_math3)}')

with open(FILE, 'r', encoding='utf-8') as f:
    html = f.read()

def question_to_js(q, math_type):
    obj = {
        'id': q.get('id', '') + '_' + math_type,
        'subject': q.get('subject', '高数'),
        'mathType': math_type,
        'type': q.get('type', '选择'),
        'difficulty': q.get('difficulty', 2),
        'content': q.get('content', ''),
        'options': q.get('options', []),
        'answer': q.get('answer', ''),
        'analysis': q.get('analysis', ''),
        'source': q.get('source', '自建题目'),
    }
    if 'hint' in q:
        obj['hint'] = q['hint']
    elif 'tags' in q:
        obj['hint'] = {
            'knowledgePoints': q['tags'] if isinstance(q['tags'], list) else [q['tags']],
            'approach': '请参考解析中的思路。',
            'tips': '注意相关定理和公式的灵活运用。'
        }
    if 'year' in q:
        obj['year'] = q['year']
        obj['paper'] = q.get('paper', '')

    lines = ['        {']
    for k, v in obj.items():
        if isinstance(v, str):
            v_escaped = v.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            lines.append(f'            "{k}": "{v_escaped}",')
        elif isinstance(v, list):
            arr_items = ', '.join([f'"{item.replace(chr(92), chr(92)+chr(92)).replace(chr(34), chr(92)+chr(34))}"' for item in v])
            lines.append(f'            "{k}": [{arr_items}],')
        elif isinstance(v, dict):
            lines.append(f'            "{k}": {{')
            for dk, dv in v.items():
                if isinstance(dv, list):
                    arr_items = ', '.join([f'"{item.replace(chr(92), chr(92)+chr(92)).replace(chr(34), chr(92)+chr(34))}"' for item in dv])
                    lines.append(f'                "{dk}": [{arr_items}],')
                elif isinstance(dv, str):
                    dv_escaped = dv.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                    lines.append(f'                "{dk}": "{dv_escaped}",')
            lines.append('            },')
        elif isinstance(v, (int, float)):
            lines.append(f'            "{k}": {v},')
    lines.append('        }')
    return '\n'.join(lines)

# 找到 questionBank 中的 shuer 和 shusan（在27261和31971行附近）
# questionBank 从4405行开始
qb_start = html.find('const questionBank = ')
# 找到 shuer 在 questionBank 中的位置
shuer_pos = html.find('"shuer":', qb_start)
shusan_pos = html.find('"shusan":', qb_start)

print(f'shuer 位置: {shuer_pos}')
print(f'shusan 位置: {shusan_pos}')

# 给 shuer 添加 supplement 数组
# shuer 的结构: "shuer": { "gaoshu": [...], "xiandai": [...], "gailv": [...] }
# 我们需要在 shuer 对象的末尾（} 之前）添加 "supplement": [...]
# 找到 shuer 对象的结束 }

def find_object_end(text, start_pos):
    """找到 { ... } 的结束位置，start_pos 指向 {"""
    depth = 0
    i = start_pos
    in_string = False
    string_char = None
    escape = False
    while i < len(text):
        c = text[i]
        if escape:
            escape = False
            i += 1
            continue
        if c == '\\':
            escape = True
            i += 1
            continue
        if in_string:
            if c == string_char:
                in_string = False
        else:
            if c == '"' or c == "'":
                in_string = True
                string_char = c
            elif c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    return None

# shuer_pos 指向 "shuer": 后面的位置，找到 {
brace_start = html.find('{', shuer_pos)
shuer_end = find_object_end(html, brace_start)
print(f'shuer 对象: {brace_start} - {shuer_end}')

# 在 shuer_end 之前插入 supplement 数组
math2_js = [question_to_js(q, 'shuer') for q in math2_real + social_math2]
supplement_text = ',\n        "supplement": [\n' + ',\n'.join(math2_js) + '\n        ]'
html = html[:shuer_end] + supplement_text + html[shuer_end:]
print(f'shuer 插入 {len(math2_js)} 题')

# 重新找 shusan（位置可能变了）
shusan_pos = html.find('"shusan":', qb_start)
brace_start = html.find('{', shusan_pos)
shusan_end = find_object_end(html, brace_start)
print(f'shusan 对象: {brace_start} - {shusan_end}')

math3_js = [question_to_js(q, 'shusan') for q in math3_real + social_math3]
supplement_text = ',\n        "supplement": [\n' + ',\n'.join(math3_js) + '\n        ]'
html = html[:shusan_end] + supplement_text + html[shusan_end:]
print(f'shusan 插入 {len(math3_js)} 题')

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(html)
print('文件已更新')
