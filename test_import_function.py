#!/usr/bin/env python3
"""
自测自建题库导入功能
1. 检查JS语法
2. 检查HTML结构
3. 检查与现有功能的衔接
"""
import re
import subprocess

file_path = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

errors = []
warnings = []

# 1. 检查关键函数是否存在
required_functions = [
    'triggerImport', 'handleImportFile', 'parseJSONQuestions', 
    'parseTXTQuestions', 'parseExcelQuestions', 'showImportPreview',
    'confirmImport', 'cancelImport', 'normalizeQuestion', 'escapeHtml',
    'renderCustomQuestions', 'deleteCustomQuestion'
]
for fn in required_functions:
    pattern = rf'function\s+{fn}\s*\('
    if not re.search(pattern, content):
        errors.append(f"缺少函数: {fn}")

# 2. 检查HTML元素是否存在
required_elements = [
    'importFileInput', 'importPreviewCard', 'importPreviewList', 
    'importPreviewCount', 'customListCard', 'customList', 'customCount'
]
for el in required_elements:
    pattern = rf'id=["\']{el}["\']'
    if not re.search(pattern, content):
        errors.append(f"缺少HTML元素: id={el}")

# 3. 检查SheetJS CDN是否加载
if 'xlsx.full.min.js' not in content:
    errors.append("SheetJS CDN未加载")

# 4. 检查导入卡片onclick是否正确
import_cards = re.findall(r'onclick=["\']triggerImport\([\'"]?(\w+)[\'"]?\)["\']', content)
print(f"导入卡片格式: {import_cards}")
if len(import_cards) != 3:
    warnings.append(f"期望3个导入卡片，实际{len(import_cards)}个")
if 'json' not in import_cards:
    errors.append("缺少JSON导入卡片")
if 'txt' not in import_cards:
    errors.append("缺少TXT导入卡片")
if 'excel' not in import_cards:
    errors.append("缺少Excel导入卡片")

# 5. 检查是否还有旧的手动添加表单
if 'addForm' in content and 'id="addForm"' in content:
    warnings.append("仍存在手动添加表单 addForm")
if 'qContent' in content and 'id="qContent"' in content:
    warnings.append("仍存在手动添加字段 qContent")

# 6. 检查showAddForm和addCustomQuestion是否被替换为提示
if '请使用文件导入功能添加题目' not in content:
    warnings.append("showAddForm/addCustomQuestion 未正确替换为提示")

# 7. 检查JS语法 - 提取导入相关函数代码
# 查找 triggerImport 到 deleteCustomQuestion 之间的代码
match = re.search(r'(// ========== 自建题库导入功能.*?function deleteCustomQuestion.*?\n\})', content, re.DOTALL)
if match:
    js_code = match.group(1)
    # 写入临时文件检查语法
    with open('/tmp/check_import_syntax.mjs', 'w') as f:
        # 包装成模块
        f.write("const practiceState = { selectedMathType: 'shuyi' };\n")
        f.write("const currentUser = { stats: { customQuestions: [] } };\n")
        f.write("function showToast(msg, type) { console.log(msg); }\n")
        f.write("function formatMath(s) { return s; }\n")
        f.write("const subjectNames = { gaoshu: '高等数学', xiandai: '线性代数', gailv: '概率论' };\n")
        f.write("function saveUserData() { return Promise.resolve(); }\n")
        f.write("const XLSX = { read: () => {}, utils: { sheet_to_json: () => [] } };\n")
        # 移除重复的 pendingImportQuestions 声明
        cleaned_code = js_code.replace('let pendingImportQuestions = []; // 待确认导入的题目缓存', '// pendingImportQuestions declared externally')
        # 处理 export，注意 async function 的情况
        cleaned_code = cleaned_code.replace('async function ', 'export async function ')
        cleaned_code = cleaned_code.replace('function ', 'export function ')
    
    result = subprocess.run(['node', '--check', '/tmp/check_import_syntax.mjs'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ JS语法检查通过")
    else:
        errors.append(f"JS语法错误: {result.stderr}")

# 8. 检查与renderCustomQuestions的衔接
# 确认 confirmImport 调用 renderCustomQuestions
if 'renderCustomQuestions();' not in content.split('function confirmImport')[1].split('function renderCustomQuestions')[0]:
    errors.append("confirmImport 未调用 renderCustomQuestions")

# 9. 检查与deleteCustomQuestion的衔接
if 'deleteCustomQuestion' not in content:
    errors.append("缺少 deleteCustomQuestion 函数")

# 10. 检查与做题功能的衔接
# 自建题目应该能被做题功能使用
if 'customQuestions' not in content:
    warnings.append("做题功能未引用 customQuestions")

print(f"\n=== 检查结果 ===")
print(f"错误: {len(errors)}")
for e in errors:
    print(f"  ✗ {e}")
print(f"警告: {len(warnings)}")
for w in warnings:
    print(f"  ⚠ {w}")

if len(errors) == 0:
    print("\n✓ 所有检查通过")
else:
    print(f"\n✗ 有 {len(errors)} 个错误需要修复")
