#!/usr/bin/env python3
# 把收集到的真题和自建题目导入到 HTML 题库的 questionBank.supplement 数组中
# questionBank 结构: { shuyi: {gaoshu:[], xiandai:[], gailv:[], supplement:[]}, shuer:{...}, shusan:{...} }

import json
import re

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

# 读取收集的题目
with open('/Users/wuyangcj/trae/回甘demo/collected_real_exams.json', 'r', encoding='utf-8') as f:
    real_questions = json.load(f)

with open('/Users/wuyangcj/trae/回甘demo/collected_social_questions.json', 'r', encoding='utf-8') as f:
    social_questions = json.load(f)

print(f'真题: {len(real_questions)} 道')
print(f'自建: {len(social_questions)} 道')

# 读取HTML文件
with open(FILE, 'r', encoding='utf-8') as f:
    html = f.read()

# 找到 questionBank 的 supplement 数组位置
# 结构: const questionBank = { shuyi: { ..., supplement: [...] }, ... }
# 我们需要找到 shuyi 的 supplement 数组的结束位置，在其前面插入新题目

# 先找到 "shuyi" 对象中的 "supplement" 数组
# 模式: supplement: [ ... ] 在 shuyi 块内
# 用正则找到 supplement: [ 的位置，然后找到匹配的 ]

def find_supplement_array(text, start_pos):
    """找到 "supplement": [ ... ] 的内容，返回 (start, end) 位置"""
    pattern = re.compile(r'"supplement"\s*:\s*\[')
    m = pattern.search(text, start_pos)
    if not m:
        return None, None

    bracket_start = m.end() - 1  # 指向 [
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

# 找到 shuyi 的 supplement 数组
shuyi_start = html.find('"shuyi":', 4400)  # 从4400开始找questionBank里的shuyi
if shuyi_start == -1:
    print("ERROR: 找不到 shuyi")
    exit(1)

arr_start, arr_end = find_supplement_array(html, shuyi_start)
if arr_start is None:
    print("ERROR: 找不到 shuyi 的 supplement 数组")
    exit(1)

print(f'\nshuyi.supplement 数组位置: {arr_start} - {arr_end}')
# 检查数组是否为空
arr_content = html[arr_start+1:arr_end].strip()
print(f'数组当前内容长度: {len(arr_content)} 字符')

# 生成新题目的JS对象字符串
def question_to_js(q):
    """把题目对象转为JS对象字面量字符串"""
    # 确定科目映射
    subject_map = {'高数': 'gaoshu', '线代': 'xiandai', '概率': 'gailv'}
    math_type = 'shuyi'  # 默认放数一

    # 构建题目对象
    obj = {
        'id': q.get('id', ''),
        'subject': q.get('subject', '高数'),
        'type': q.get('type', '选择'),
        'difficulty': q.get('difficulty', 2),
        'content': q.get('content', ''),
        'options': q.get('options', []),
        'answer': q.get('answer', ''),
        'analysis': q.get('analysis', ''),
        'source': q.get('source', '自建题目'),
    }

    # 添加 hint 如果有
    if 'hint' in q:
        obj['hint'] = q['hint']
    elif 'tags' in q:
        obj['hint'] = {
            'knowledgePoints': q['tags'] if isinstance(q['tags'], list) else [q['tags']],
            'approach': '请参考解析中的思路。',
            'tips': '注意相关定理和公式的灵活运用。'
        }

    # 添加年份信息（真题）
    if 'year' in q:
        obj['year'] = q['year']
        obj['paper'] = q.get('paper', '')

    # 转为JS对象字符串（不是JSON，因为JS对象key不需要引号）
    lines = []
    lines.append('        {')
    for k, v in obj.items():
        if isinstance(v, str):
            # 转义字符串中的特殊字符
            v_escaped = v.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
            lines.append(f'            {k}: "{v_escaped}",')
        elif isinstance(v, list):
            arr_items = ', '.join([f'"{item.replace(chr(92), chr(92)+chr(92)).replace(chr(34), chr(92)+chr(34))}"' for item in v])
            lines.append(f'            {k}: [{arr_items}],')
        elif isinstance(v, dict):
            lines.append(f'            {k}: {{')
            for dk, dv in v.items():
                if isinstance(dv, list):
                    arr_items = ', '.join([f'"{item.replace(chr(92), chr(92)+chr(92)).replace(chr(34), chr(92)+chr(34))}"' for item in dv])
                    lines.append(f'                {dk}: [{arr_items}],')
                elif isinstance(dv, str):
                    dv_escaped = dv.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
                    lines.append(f'                {dk}: "{dv_escaped}",')
            lines.append('            },')
        elif isinstance(v, (int, float)):
            lines.append(f'            {k}: {v},')
    lines.append('        }')
    return '\n'.join(lines)

# 生成所有新题目
new_questions_js = []
for q in real_questions:
    new_questions_js.append(question_to_js(q))
for q in social_questions:
    new_questions_js.append(question_to_js(q))

print(f'\n生成 {len(new_questions_js)} 道题目的JS代码')

# 在 supplement 数组末尾插入新题目
if arr_content:  # 数组不为空
    # 在 ] 前面加逗号和新题目
    insert_text = ',\n' + ',\n'.join(new_questions_js)
else:  # 数组为空
    insert_text = '\n'.join(new_questions_js)

# 在 arr_end 位置（] 之前）插入
new_html = html[:arr_end] + insert_text + html[arr_end:]

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f'\n已插入 {len(new_questions_js)} 道题目到 questionBank.shuyi.supplement')
print(f'文件已更新')
