// check_import_syntax.mjs - 提取并检查自建题库导入功能代码的JS语法
import fs from 'fs';

const html = fs.readFileSync('/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html', 'utf-8');

// 提取从 "// ========== 自建题库导入功能" 到 "// ========== 知识库" 之间的代码
const startMarker = '// ========== 自建题库导入功能（JSON/TXT/Excel） ==========';
const endMarker = '// ========== 知识库（章节树 + 卡片网格 + 搜索高亮） ==========';
const startIdx = html.indexOf(startMarker);
const endIdx = html.indexOf(endMarker);

if (startIdx === -1 || endIdx === -1) {
    console.error('无法找到导入功能代码段');
    process.exit(1);
}

const code = html.substring(startIdx, endIdx);

// 写入临时文件检查语法
fs.writeFileSync('/tmp/import_code_check.mjs', code);

try {
    // 使用 new Function 检查语法（不执行）
    new Function(code);
    console.log('✓ 导入功能代码语法检查通过');
    console.log(`  代码长度: ${code.length} 字符`);
    console.log(`  行数: ${code.split('\n').length}`);
} catch (err) {
    console.error('✗ 语法错误:', err.message);
    process.exit(1);
}

// 同时检查整个文件中所有 <script> 标签内的JS语法
console.log('\n--- 检查所有内联script标签 ---');
const scriptRegex = /<script(?:\s[^>]*)?>([^<]*(?:<(?!\/script>)[^<]*)*)<\/script>/gi;
let match;
let scriptCount = 0;
let hasError = false;
while ((match = scriptRegex.exec(html)) !== null) {
    const scriptContent = match[1];
    if (scriptContent.trim().length < 10) continue; // 跳过空script
    scriptCount++;
    try {
        new Function(scriptContent);
    } catch (err) {
        // 排除已知的MathJax等库的问题，只关注语法错误
        if (err instanceof SyntaxError) {
            console.error(`✗ Script #${scriptCount} 语法错误: ${err.message}`);
            // 输出错误附近的内容
            const lines = scriptContent.split('\n');
            console.error(`  (script总行数: ${lines.length})`);
            hasError = true;
        }
    }
}
console.log(`共检查 ${scriptCount} 个内联script标签`);
if (!hasError) {
    console.log('✓ 所有内联script语法检查通过');
}
