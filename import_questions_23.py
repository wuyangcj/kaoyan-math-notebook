#!/usr/bin/env python3
# 把真题按卷种分配到 shuer 和 shusan 的 supplement 数组
# 真题中有数学二和数学三的题目，需要放到对应卷种

import json
import re

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open('/Users/wuyangcj/trae/回甘demo/collected_real_exams.json', 'r', encoding='utf-8') as f:
    real_questions = json.load(f)

with open('/Users/wuyangcj/trae/回甘demo/collected_social_questions.json', 'r', encoding='utf-8') as f:
    social_questions = json.load(f)

# 按卷种分组真题
math2_questions = [q for q in real_questions if q.get('paper') == '数学二']
math3_questions = [q for q in real_questions if q.get('paper') == '数学三']
print(f'数学二真题: {len(math2_questions)} 道')
print(f'数学三真题: {len(len3_questions) if False else len(math3_questions)} 道')

# 自建题目按科目均分到数二和数三（数二不考概率论，所以只分高数和线代）
social_math2 = [q for q in social_questions if q.get('subject') in ['高数', '线代']]
social_math3 = social_questions  # 数三全科目

print(f'自建题目分给数二: {len(social_math2)} 道')
print(f'自建题目分给数三: {len(social_math3)} 道')

# 读取HTML
with open(FILE, 'r', encoding='utf-8') as f:
    html = f.read()

def question_to_js(q, math_type):
    """把题目对象转为JS对象字面量字符串"""
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

    lines = []
    lines.append('        {')
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

def find_supplement_array(text, start_pos):
    """找到 "supplement": [ ... ] 的内容"""
    pattern = re.compile(r'"supplement"\s*:\s*\[')
    m = pattern.search(text, start_pos)
    if not m:
        return None, None
    bracket_start = m.end() - 1
    depth = 0
    i = bracket_start
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
            elif c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    return bracket_start, i
        i += 1
    return None, None

# 处理 shuer
shuer_start = html.find('"shuer":', 4400)
if shuer_start != -1:
    arr_start, arr_end = find_supplement_array(html, shuer_start)
    if arr_start is not None:
        arr_content = html[arr_start+1:arr_end].strip()
        # 生成数二题目
        math2_js = [question_to_js(q, 'shuer') for q in math2_questions + social_math2]
        if arr_content:
            insert_text = ',\n' + ',\n'.join(math2_js)
        else:
            insert_text = '\n'.join(math2_js)
        html = html[:arr_end] + insert_text + html[arr_end:]
        print(f'shuer.supplement 插入 {len(math2_js)} 题')

# 处理 shusan（位置可能因前面的插入而改变，重新查找）
shusan_start = html.find('"shusan":', 4400)
if shusan_start != -1:
    arr_start, arr_end = find_supplement_array(html, shusan_start)
    if arr_start is not None:
        arr_content = html[arr_start+1:arr_end].strip()
        # 生成数三题目
        math3_js = [question_to_js(q, 'shusan') for q in math3_questions + social_math3]
        if arr_content:
            insert_text = ',\n' + ',\n'.join(math3_js)
        else:
            insert_text = '\n'.join(math3_js)
        html = html[:arr_end] + insert_text + html[arr_end:]
        print(f'shusan.supplement 插入 {len(math3_js)} 题')

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(html)
print('文件已更新')
