#!/usr/bin/env python3
# 把之前冒用名师书名的题目source改为"自建题目"或"考研真题改编"
# 规则：
#   - ID 含 zhangyu/liyongle/tangjiafeng/lilin 的，source 改为 "自建题目"
#   - source 为 "张宇1000题"/"李永乐660题"/"汤家凤1800题"/"李林880题" 的，改为 "自建题目"

import re

FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 source 字段值
old_sources = ['张宇1000题', '李永乐660题', '汤家凤1800题', '李林880题']
count = 0
for old in old_sources:
    # 匹配 "source": "张宇1000题" 或 source: "张宇1000题"
    pattern = re.compile(r'("source"\s*:\s*")' + re.escape(old) + r'(")')
    new_content, n = pattern.subn(r'\1自建题目\2', content)
    if n > 0:
        content = new_content
        count += n
        print(f'  {old} -> 自建题目: {n} 处')

print(f'\n共修改 {count} 处 source 标签')

with open(FILE, 'w', encoding='utf-8') as f:
    f.write(content)
print('文件已更新')
