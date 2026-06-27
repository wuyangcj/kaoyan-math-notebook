#!/usr/bin/env python3
"""
Fix missing hints in question objects.

Adds hint fields to questions that have a 'source' field but no 'hint' field.
Targets the chapterQuestionBank (single-line format) and questionBank (multi-line format).

The hint includes:
- knowledgePoints: 1-2 tags derived from the chapter/topic
- approach: a 1-2 sentence hint about the approach (NOT the full answer)
- tips: a short tip related to the question type
"""

import re
import os
import sys
import shutil

HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'


# ============================================================
# Chapter to knowledge points mapping
# ============================================================
CHAPTER_KP_MAP = [
    ('函数极限连续', ['极限', '连续性']),
    ('一元函数微分学', ['导数', '微分中值定理']),
    ('一元函数积分学', ['不定积分', '定积分']),
    ('多元函数微分学', ['偏导数', '全微分']),
    ('多重积分', ['二重积分', '三重积分']),
    ('微分方程', ['微分方程', '通解']),
    ('无穷级数', ['级数收敛', '幂级数']),
    ('行列式', ['行列式', '克莱姆法则']),
    ('矩阵', ['矩阵运算', '逆矩阵']),
    ('向量', ['向量组', '线性相关性']),
    ('线性方程组', ['齐次方程组', '非齐次方程组']),
    ('特征值', ['特征值', '特征向量']),
    ('二次型', ['二次型', '正定矩阵']),
    ('随机事件与概率', ['概率', '条件概率']),
    ('随机变量及其分布', ['分布函数', '概率密度']),
    ('多维随机变量', ['联合分布', '边缘分布']),
    ('数字特征', ['期望', '方差']),
    ('大数定律与中心极限', ['大数定律', '中心极限定理']),
    ('数理统计', ['参数估计', '假设检验']),
]

# Content keywords to knowledge points (used when chapter is unavailable)
CONTENT_KP_MAP = [
    (['极限', 'lim'], ['极限', '未定式']),
    (['间断', '连续'], ['连续性', '间断点']),
    (['导数', '求导', '可导'], ['导数', '求导法则']),
    (['积分', '∫'], ['积分', '积分法']),
    (['偏导', '∂'], ['偏导数', '多元函数']),
    (['全微分', 'dz'], ['全微分', '偏导数']),
    (['微分方程', '通解', '特解'], ['微分方程', '通解']),
    (['级数', 'Σ', '收敛'], ['级数', '收敛性']),
    (['行列式'], ['行列式']),
    (['矩阵'], ['矩阵运算']),
    (['特征值', '特征向量'], ['特征值', '特征向量']),
    (['二次型'], ['二次型', '正定']),
    (['正交'], ['正交矩阵', '施密特正交化']),
    (['概率'], ['概率', '概率公式']),
    (['分布'], ['分布函数', '概率密度']),
    (['期望'], ['期望']),
    (['方差'], ['方差']),
    (['秩', 'r('], ['矩阵的秩']),
    (['线性方程组'], ['线性方程组']),
    (['向量'], ['向量组', '线性相关性']),
]

# Content keywords to approach hints
APPROACH_MAP = [
    (['极限', 'lim'], '分析极限类型，选择合适的求解方法（等价无穷小、洛必达法则或泰勒展开）。'),
    (['间断', '连续'], '利用连续性定义分析函数在给定点的极限和函数值。'),
    (['导数', '求导', '可导'], '利用导数定义或求导法则，注意复合函数的链式法则。'),
    (['微分'], '利用微分定义或运算法则进行计算。'),
    (['积分', '∫'], '确定积分类型，选择合适的积分方法（换元法或分部积分法）。'),
    (['偏导', '∂'], '对相应变量求偏导，将其余变量视为常数。'),
    (['全微分', 'dz'], '先计算各偏导数，再写出全微分表达式。'),
    (['微分方程', '通解', '特解'], '判断微分方程类型，选择对应的求解方法。'),
    (['级数', 'Σ', '收敛'], '利用级数收敛判别法（比较判别法、比值判别法等）判断。'),
    (['泰勒'], '利用泰勒公式展开，注意余项形式。'),
    (['中值定理', '罗尔', '拉格朗日', '柯西'], '构造辅助函数，应用微分中值定理。'),
    (['极值', '最值'], '求导找驻点，利用极值判别法判断。'),
    (['拐点', '凹凸'], '求二阶导数，分析函数的凹凸性。'),
    (['拉格朗日乘数', '约束条件'], '利用拉格朗日乘数法求解条件极值。'),
    (['方向导数', '梯度'], '利用方向导数和梯度的定义计算。'),
    (['隐函数'], '利用隐函数求导公式计算。'),
    (['格林公式', '曲线积分'], '利用格林公式将曲线积分转化为二重积分。'),
    (['高斯公式', '曲面积分'], '利用高斯公式将曲面积分转化为三重积分。'),
    (['二重积分', '∫∫'], '确定积分区域，选择合适的坐标系和积分次序。'),
    (['三重积分', '∫∫∫'], '选择合适的坐标系（直角坐标、柱坐标或球坐标）计算。'),
    (['面积', '体积'], '利用定积分的几何应用求解。'),
    (['行列式'], '利用行列式性质或展开定理进行计算。'),
    (['矩阵'], '利用矩阵运算性质和初等变换求解。'),
    (['逆', '可逆', 'A⁻¹'], '利用逆矩阵定义或伴随矩阵法求逆。'),
    (['秩', 'r('], '利用初等行变换化为阶梯形求秩。'),
    (['特征值', '特征向量'], '求解特征方程 |λE-A|=0 得特征值，再解齐次方程组得特征向量。'),
    (['二次型'], '写出二次型矩阵，利用正交变换化标准形。'),
    (['正交'], '利用正交矩阵的性质和施密特正交化方法。'),
    (['线性方程组', 'Ax=0', 'Ax=b'], '对系数矩阵进行初等行变换，分析解的结构。'),
    (['向量'], '利用向量组的线性相关性和秩的概念分析。'),
    (['概率'], '利用概率公式（加法公式、乘法公式、全概率公式等）计算。'),
    (['分布', '随机变量'], '分析随机变量的分布类型，利用分布函数或概率密度求解。'),
    (['期望', 'E('], '利用期望的定义或性质进行计算。'),
    (['方差', 'D('], '利用方差的定义或性质，注意方差的计算公式。'),
    (['协方差', 'Cov'], '利用协方差和相关系数的定义与性质计算。'),
    (['极大似然', '似然'], '构造似然函数，求导得极大似然估计。'),
    (['估计'], '利用参数估计方法（矩估计或极大似然估计）求解。'),
    (['大数定律', '中心极限'], '利用大数定律或中心极限定理分析。'),
    (['假设检验'], '建立原假设和备择假设，选择合适的检验统计量。'),
    (['置信区间'], '利用抽样分布构造置信区间。'),
    (['证明'], '分析已知条件和结论，构造合适的证明思路。'),
]


def get_knowledge_points(chapter, content):
    """Get 1-2 knowledge points based on chapter and content."""
    if chapter:
        for key, kps in CHAPTER_KP_MAP:
            if key in chapter:
                return kps
    if content:
        for keywords, kps in CONTENT_KP_MAP:
            if any(kw in content for kw in keywords):
                return kps
    return ['基础概念', '计算方法']


def generate_approach(content, analysis, qtype, chapter):
    """Generate a 1-2 sentence approach hint."""
    if content:
        for keywords, approach in APPROACH_MAP:
            if any(kw in content for kw in keywords):
                return approach
    if qtype == '选择':
        return '分析题意，利用相关定义和性质逐一判断各选项。'
    elif qtype == '填空':
        return '根据相关公式直接计算，注意化简和变形。'
    else:
        return '按步骤求解，注意每步的理论依据和逻辑严密性。'


def generate_tips(qtype, content):
    """Generate a short tip related to the question type."""
    content = content or ''
    if qtype == '选择':
        if '下列' in content or '以下' in content:
            return '逐项验证，善用排除法。'
        return '注意排除法和特殊值法的灵活运用。'
    elif qtype == '填空':
        return '注意计算精度和符号的确定。'
    else:
        if '证明' in content:
            return '注意证明过程的逻辑严密性。'
        return '注意书写规范，步骤完整。'


def escape_js_string(s):
    """Escape a string for use in a JavaScript string literal."""
    if not s:
        return ''
    s = s.replace('\\', '\\\\')
    s = s.replace('"', '\\"')
    s = s.replace('\n', '\\n')
    s = s.replace('\r', '\\r')
    s = s.replace('\t', '\\t')
    return s


def extract_field(obj_text, field):
    """Extract a string field value from a JS object literal text.

    Handles both quoted keys ("field": "value") and unquoted keys (field: "value").
    The value can contain escaped characters like \\" and \\\\.
    Only matches double-quoted values (questions use double quotes).
    """
    # Try quoted key: "field": "value"
    pattern = r'"' + re.escape(field) + r'"\s*:\s*"((?:[^"\\]|\\.)*)"'
    match = re.search(pattern, obj_text)
    if match:
        return match.group(1)
    # Try unquoted key: field: "value"
    pattern = r'\b' + re.escape(field) + r'\s*:\s*"((?:[^"\\]|\\.)*)"'
    match = re.search(pattern, obj_text)
    if match:
        return match.group(1)
    return None


def find_matching_brace(text, start):
    """Find the position of the closing brace that matches the opening brace at start.

    Tracks string context (both single and double quotes) and escape characters
    to correctly handle braces inside strings.
    """
    in_dq_string = False  # double quote string
    in_sq_string = False  # single quote string
    escape = False
    depth = 0

    for i in range(start, len(text)):
        c = text[i]
        if escape:
            escape = False
            continue
        if c == '\\':
            escape = True
            continue
        if in_dq_string:
            if c == '"':
                in_dq_string = False
            continue
        if in_sq_string:
            if c == "'":
                in_sq_string = False
            continue
        if c == '"':
            in_dq_string = True
            continue
        if c == "'":
            in_sq_string = True
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i

    return -1


def has_direct_field(obj_text, field):
    """Check if a field exists as a DIRECT field of the object (not in nested objects/arrays).

    Reads the entire object text character by character, tracking brace/bracket depth.
    At depth 1 (direct fields), checks if any key matches the given field name.
    Handles both quoted keys ("field":) and unquoted keys (field:), and properly
    skips strings (so braces inside strings don't affect depth tracking).
    """
    depth = 0
    i = 0
    n = len(obj_text)

    while i < n:
        c = obj_text[i]

        # Handle strings (both single and double quoted)
        if c == '"' or c == "'":
            quote = c
            i += 1
            str_start = i
            # Read until matching closing quote, handling escapes
            while i < n:
                if obj_text[i] == '\\':
                    i += 2
                    continue
                if obj_text[i] == quote:
                    break
                i += 1
            str_content = obj_text[str_start:i]
            i += 1  # Skip closing quote

            # At depth 1, check if this string is a key (followed by ':')
            if depth == 1:
                j = i
                while j < n and obj_text[j] in ' \t\n\r':
                    j += 1
                if j < n and obj_text[j] == ':':
                    # It's a key
                    if str_content == field:
                        return True
                    # Skip the ':' and let the main loop handle the value
                    i = j + 1
            continue

        if c == '{' or c == '[':
            depth += 1
            i += 1
            continue
        if c == '}' or c == ']':
            depth -= 1
            i += 1
            continue

        # Check for unquoted keys at depth 1 (e.g., field: value)
        if depth == 1 and (c.isalpha() or c == '_' or c == '$'):
            j = i
            while j < n and (obj_text[j].isalnum() or obj_text[j] in '_$'):
                j += 1
            key = obj_text[i:j]
            k = j
            while k < n and obj_text[k] in ' \t\n\r':
                k += 1
            if k < n and obj_text[k] == ':':
                if key == field:
                    return True
                i = k + 1  # Skip ':' and let main loop handle value
            else:
                i = j
            continue

        i += 1

    return False


def generate_hint_json(content, analysis, source, qtype, chapter):
    """Generate the hint JSON string to insert into the question object."""
    kps = get_knowledge_points(chapter, content)
    approach = generate_approach(content, analysis, qtype, chapter)
    tips = generate_tips(qtype, content or '')

    approach = escape_js_string(approach)
    tips = escape_js_string(tips)

    kp_str = ', '.join(f'"{escape_js_string(kp)}"' for kp in kps)
    hint_json = f', "hint": {{ "knowledgePoints": [{kp_str}], "approach": "{approach}", "tips": "{tips}" }}'

    return hint_json


def find_section_bounds(text, section_name):
    """Find the bounds of a const section like 'const sectionName = {...};'.

    Returns (start_pos, end_pos) where start_pos is the position of the opening brace
    and end_pos is the position of the matching closing brace.
    """
    pattern = r'const\s+' + re.escape(section_name) + r'\s*=\s*'
    match = re.search(pattern, text)
    if not match:
        return None, None

    brace_pos = text.find('{', match.end())
    if brace_pos == -1:
        return None, None

    end_pos = find_matching_brace(text, brace_pos)
    if end_pos == -1:
        return None, None

    return brace_pos, end_pos


def find_questions_in_text(text, start_offset=0):
    """Find all question objects in the text that have 'source' but no 'hint'.

    A question object is identified by having 'content' and 'source' fields.
    Uses brace-matching with continued scanning inside non-question objects.

    Returns a list of dicts with 'start', 'end', 'text', and 'chapter' keys.
    """
    questions = []
    pos = 0
    current_chapter = ''

    while pos < len(text):
        brace_pos = text.find('{', pos)
        if brace_pos == -1:
            break

        end_pos = find_matching_brace(text, brace_pos)
        if end_pos == -1:
            break

        obj_text = text[brace_pos:end_pos + 1]

        # Track chapter context by looking for "chapter": "..." before this object
        before_text = text[:brace_pos]
        chapter_matches = list(re.finditer(r'"chapter"\s*:\s*"([^"]*)"', before_text))
        if chapter_matches:
            current_chapter = chapter_matches[-1].group(1)

        # Check if this is a question object:
        # Must have 'content' and 'source' fields, and must NOT have 'hint'
        is_question = (has_direct_field(obj_text, 'content') and
                       has_direct_field(obj_text, 'source') and
                       not has_direct_field(obj_text, 'hint'))

        if is_question:
            # Also check if it has a 'video' field (questionBank questions do)
            has_video = has_direct_field(obj_text, 'video')

            questions.append({
                'start': start_offset + brace_pos,
                'end': start_offset + end_pos,
                'text': obj_text,
                'chapter': current_chapter,
                'has_video': has_video,
            })
            pos = end_pos + 1  # Move past this question
        else:
            pos = brace_pos + 1  # Continue scanning inside this object

    return questions


def process_file(filepath):
    """Process the HTML file and add missing hints."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the sections to scan
    sections = []
    for section_name in ['chapterQuestionBank', 'questionBank']:
        start, end = find_section_bounds(content, section_name)
        if start is not None and end is not None:
            sections.append((section_name, start, end))
            print(f'Found {section_name}: positions {start}-{end}')

    # Find all questions needing hints
    all_questions = []
    for section_name, start, end in sections:
        section_text = content[start:end + 1]
        questions = find_questions_in_text(section_text, start_offset=start)
        print(f'  {section_name}: found {len(questions)} questions needing hints')
        all_questions.extend(questions)

    print(f'Total questions needing hints: {len(all_questions)}')

    # Generate hints and collect insertions
    insertions = []
    for q in all_questions:
        obj_text = q['text']
        content_val = extract_field(obj_text, 'content')
        analysis_val = extract_field(obj_text, 'analysis')
        source_val = extract_field(obj_text, 'source')
        type_val = extract_field(obj_text, 'type')
        chapter = q['chapter']

        # Also try to get chapter from the object itself
        if not chapter:
            chapter = extract_field(obj_text, 'chapter') or ''

        hint_json = generate_hint_json(content_val, analysis_val, source_val, type_val, chapter)

        # Find insertion point
        if q['has_video']:
            # Insert before "video" field
            video_match = re.search(r'(\s*)"video"\s*:', obj_text)
            if video_match:
                pre_video = obj_text[:video_match.start()]
                stripped = pre_video.rstrip()
                if stripped.endswith(','):
                    # Insert before the comma
                    comma_pos = q['start'] + len(stripped) - 1
                    insertions.append((comma_pos, hint_json))
                else:
                    insert_offset = q['start'] + len(stripped)
                    insertions.append((insert_offset, hint_json))
            else:
                # Fallback: insert before closing brace
                pre_close = obj_text[:-1]
                stripped = pre_close.rstrip()
                if stripped.endswith(','):
                    comma_pos = q['start'] + len(stripped) - 1
                    insertions.append((comma_pos, hint_json))
                else:
                    insert_offset = q['start'] + len(stripped)
                    insertions.append((insert_offset, hint_json))
        else:
            # Insert before closing brace
            pre_close = obj_text[:-1]
            stripped = pre_close.rstrip()
            if stripped.endswith(','):
                comma_pos = q['start'] + len(stripped) - 1
                insertions.append((comma_pos, hint_json))
            else:
                insert_offset = q['start'] + len(stripped)
                insertions.append((insert_offset, hint_json))

    # Apply insertions in reverse order (to preserve positions)
    insertions.sort(key=lambda x: x[0], reverse=True)
    for pos, text in insertions:
        content = content[:pos] + text + content[pos:]

    # Write the modified file back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return len(all_questions)


def main():
    print(f'Processing {HTML_FILE}...')

    if not os.path.exists(HTML_FILE):
        print(f'Error: File not found: {HTML_FILE}')
        sys.exit(1)

    # Make a backup
    backup_path = HTML_FILE + '.bak'
    if not os.path.exists(backup_path):
        shutil.copy2(HTML_FILE, backup_path)
        print(f'Backup created: {backup_path}')

    count = process_file(HTML_FILE)
    print(f'Done! Added {count} hints.')
    return count


if __name__ == '__main__':
    main()
