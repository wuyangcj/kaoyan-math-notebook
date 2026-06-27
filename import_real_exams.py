#!/usr/bin/env python3
"""把收集到的真实真题导入到 examPaperBank 中，替换编造的题目"""
import json
import re

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

# 读取所有真题数据
data_files = {
    '2025': 'real_exam_2025.json',
    '2024': 'real_exam_2024.json',
    '2023': 'real_exam_2023.json',
}

# 数一 2020-2022
shuyi_old = json.load(open('real_exam_shuyi_2020_2022.json'))
# 数二数三 2020-2022
shuer_shusan_old = json.load(open('real_exam_shuer_shusan_2020_2022.json'))

# 读取HTML
with open(FILE, 'r', encoding='utf-8') as f:
    html = f.read()

def question_to_js(q):
    """把题目对象转为JS对象字面量字符串"""
    parts = []
    parts.append(f'id: "{q.get("id","")}"')
    parts.append(f'type: "{q.get("type","选择")}"')
    content = q.get('content','').replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')
    parts.append(f'content: "{content}"')
    if 'options' in q and q['options']:
        opts = ', '.join([f'"{o.replace(chr(92),chr(92)+chr(92)).replace(chr(34),chr(92)+chr(34))}"' for o in q['options']])
        parts.append(f'options: [{opts}]')
    ans = q.get('answer','').replace('\\','\\\\').replace('"','\\"')
    parts.append(f'answer: "{ans}"')
    analysis = q.get('analysis','').replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')
    parts.append(f'analysis: "{analysis}"')
    hint = q.get('hint','').replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')
    parts.append(f'hint: "{hint}"')
    return '{ ' + ', '.join(parts) + ' }'

def make_year_block(year_data, id_prefix):
    """生成一年的真题块"""
    title = year_data.get('title', '')
    duration = year_data.get('duration', 180)
    questions = year_data.get('questions', [])
    qs_js = ',\n                '.join([question_to_js(q) for q in questions])
    return f'''        "{year_data.get("_year","")}": {{
            title: "{title}",
            duration: {duration},
            questions: [
                {qs_js}
            ]
        }}'''

# 收集所有要替换的数据
# 格式: replacements[math_type][year] = year_data
replacements = {
    'shuyi': {},
    'shuer': {},
    'shusan': {}
}

# 2025/2024/2023
for year, fname in data_files.items():
    d = json.load(open(fname))
    for mt in ['shuyi','shuer','shusan']:
        if mt in d and 'questions' in d[mt]:
            replacements[mt][year] = d[mt]

# 数一 2020-2022
for year in ['2022','2021','2020']:
    if year in shuyi_old:
        replacements['shuyi'][year] = shuyi_old[year]

# 数二数三 2020-2022
for mt in ['shuer','shusan']:
    if mt in shuer_shusan_old:
        for year in ['2022','2021','2020']:
            if year in shuer_shusan_old[mt]:
                replacements[mt][year] = shuer_shusan_old[mt][year]

# 统计
print('=== 收集到的真题统计 ===')
for mt in replacements:
    print(f'{mt}:')
    for year in sorted(replacements[mt].keys(), reverse=True):
        q = replacements[mt][year]
        print(f'  {year}: {len(q.get("questions",[]))} 题')

# 现在需要在 examPaperBank 中替换对应年份的数据
# examPaperBank 结构: { shuyi: { "2025": {title,duration,questions:[...]}, ... }, ... }

# 找到 examPaperBank 的位置
epb_start = html.find('const examPaperBank = ')
if epb_start == -1:
    print('ERROR: 找不到 examPaperBank')
    exit(1)

# 找到 examPaperBank 的结束位置（下一个 const ）
epb_end = html.find('\nconst ', epb_start + 10)
print(f'\nexamPaperBank 位置: {epb_start} - {epb_end}')

epb_content = html[epb_start:epb_end]

# 对每个卷种和年份，替换 questions 数组
for mt in ['shuyi','shuer','shusan']:
    for year in replacements[mt]:
        year_data = replacements[mt][year]
        questions = year_data.get('questions', [])
        if not questions:
            continue

        # 生成新的 questions 数组内容
        qs_js = ',\n                '.join([question_to_js(q) for q in questions])

        # 找到该年份的块并替换 questions 数组
        # 模式: "2025": { title: ..., duration: ..., questions: [ ... ] }
        # 我们需要找到 questions: [ ... ] 并替换

        # 先找到该年份块的位置
        # 在 epb_content 中找 "year": {
        year_pattern = f'"{year}": {{'
        year_pos = epb_content.find(year_pattern)
        if year_pos == -1:
            # 尝试不带引号的格式
            year_pattern = f'"{year}":{{'
            year_pos = epb_content.find(year_pattern)
        if year_pos == -1:
            print(f'  跳过 {mt}.{year}: 找不到年份块')
            continue

        # 找到 questions: [ 的位置
        q_start = epb_content.find('questions: [', year_pos)
        if q_start == -1:
            print(f'  跳过 {mt}.{year}: 找不到 questions 数组')
            continue

        # 找到匹配的 ] - 需要处理嵌套
        bracket_start = epb_content.find('[', q_start)
        depth = 0
        i = bracket_start
        in_string = False
        string_char = None
        escape = False
        while i < len(epb_content):
            c = epb_content[i]
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
                        break
            i += 1

        q_end = i  # 指向 ]

        # 替换 questions 数组内容
        old_questions = epb_content[q_start:q_end+1]
        new_questions = f'questions: [\n                {qs_js}\n            ]'
        epb_content = epb_content[:q_start] + new_questions + epb_content[q_end+1:]

        # 同时更新 title
        old_title = year_data.get('title', '')
        if old_title:
            # 找到 title: "..." 并替换
            title_pattern = re.compile(r'title:\s*"[^"]*"')
            epb_content_year = epb_content[year_pos:year_pos+500]
            if title_pattern.search(epb_content_year):
                epb_content = epb_content[:year_pos] + title_pattern.sub(f'title: "{old_title}"', epb_content[year_pos:], count=1)

        print(f'  替换 {mt}.{year}: {len(questions)} 题')

# 写回
html = html[:epb_start] + epb_content + html[epb_end:]
with open(FILE, 'w', encoding='utf-8') as f:
    f.write(html)

print('\n文件已更新')
