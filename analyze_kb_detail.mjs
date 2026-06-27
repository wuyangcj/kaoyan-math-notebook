// analyze_kb_detail.mjs - 分析知识库详情内容中的潜在渲染问题
import fs from 'fs';

const html = fs.readFileSync('/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html', 'utf-8');

// 提取 knowledgeBaseDetail 对象（从第43937行开始）
const startIdx = html.indexOf('const knowledgeBaseDetail = {');
const endIdx = html.indexOf('// ========== 知识点名称映射');
const detailCode = html.substring(startIdx, endIdx);

// 也提取 knowledgeBaseSupplement
const suppStart = html.indexOf('const knowledgeBaseSupplement = {');
const suppEnd = html.indexOf('Object.assign(knowledgeBaseDetail');
const suppCode = html.substring(suppStart, suppEnd);

// 使用 eval 解析（在沙箱中）
const sandbox = {};
try {
    eval('sandbox.knowledgeBaseDetail = ' + detailCode.replace('const knowledgeBaseDetail = ', ''));
} catch(e) {
    console.error('解析 knowledgeBaseDetail 失败:', e.message);
}

try {
    eval('sandbox.knowledgeBaseSupplement = ' + suppCode.replace('const knowledgeBaseSupplement = ', ''));
} catch(e) {
    console.error('解析 knowledgeBaseSupplement 失败:', e.message);
}

const detail = sandbox.knowledgeBaseDetail || {};
const supp = sandbox.knowledgeBaseSupplement || {};

// 合并
for (const subject of Object.keys(supp)) {
    if (!detail[subject]) detail[subject] = {};
    Object.assign(detail[subject], supp[subject]);
}

console.log('知识库详情分析');
console.log('='.repeat(60));

let totalEntries = 0;
let issues = [];

for (const subject of Object.keys(detail)) {
    const entries = detail[subject];
    console.log(`\n科目: ${subject} (${Object.keys(entries).length} 个知识点)`);

    for (const key of Object.keys(entries)) {
        totalEntries++;
        const entry = entries[key];
        if (!entry || !entry.content) continue;

        const content = entry.content;

        // 检查1: 是否包含字面的 <code> 或 <div> HTML标签
        if (/<code[\s>]/i.test(content) || /<div[\s>]/i.test(content) || /<span[\s>]/i.test(content)) {
            // 这些是合法的HTML标签，检查是否正确闭合
            const codeOpen = (content.match(/<code[\s>]/gi) || []).length;
            const codeClose = (content.match(/<\/code>/gi) || []).length;
            if (codeOpen !== codeClose) {
                issues.push({
                    subject, key,
                    type: 'unclosed_code_tag',
                    detail: `有${codeOpen}个<code>开始标签但只有${codeClose}个关闭标签`,
                    snippet: content.substring(0, 100)
                });
            }
        }

        // 检查2: 是否包含未转义的小于号 < 后跟字母（可能被误解析为HTML标签）
        // 排除已知的合法HTML标签
        const lessThanMatches = content.match(/<(?!\/?(b|i|p|br|code|div|span|pre|ul|ol|li|table|tr|td|th|h[1-6]|strong|em|sup|sub|blockquote)\b)[a-zA-Z]/g);
        if (lessThanMatches) {
            issues.push({
                subject, key,
                type: 'unescaped_less_than',
                detail: `发现${lessThanMatches.length}个可能被误解析的<字符`,
                matches: lessThanMatches.slice(0, 3),
                snippet: content.substring(0, 150)
            });
        }

        // 检查3: 是否包含单反斜杠的LaTeX命令（在JS中会被转义）
        // 检测模式: \字母 但不是 \\字母
        const singleBackslashLatex = content.match(/(?<!\\)\\(?!\\)(frac|begin|end|sqrt|lim|sum|int|alpha|beta|sigma|partial|infty|mathrm|mathbb|left|right|cdot|le|ge|ne|approx|sim|to|in|not|forall|exists|nabla|times|div|pm|mp|infty|vec|hat|bar|tilde|dot|ddot)\b/g);
        if (singleBackslashLatex) {
            issues.push({
                subject, key,
                type: 'single_backslash_latex',
                detail: `发现${singleBackslashLatex.length}个单反斜杠LaTeX命令`,
                commands: [...new Set(singleBackslashLatex)].slice(0, 5),
                snippet: content.substring(0, 150)
            });
        }

        // 检查4: 检查 \begin{cases} 等环境是否正确
        const beginMatches = content.match(/\\begin\{/g) || [];
        const endMatches = content.match(/\\end\{/g) || [];
        if (beginMatches.length !== endMatches.length) {
            issues.push({
                subject, key,
                type: 'unbalanced_begin_end',
                detail: `\\begin{}有${beginMatches.length}个，\\end{}有${endMatches.length}个`,
                snippet: content.substring(0, 150)
            });
        }
    }
}

console.log(`\n${'='.repeat(60)}`);
console.log(`总计: ${totalEntries} 个知识点`);
console.log(`发现问题: ${issues.length} 个\n`);

for (const issue of issues) {
    console.log(`[${issue.type}] ${issue.subject}/${issue.key}`);
    console.log(`  详情: ${issue.detail}`);
    if (issue.matches) console.log(`  匹配: ${issue.matches.join(', ')}`);
    if (issue.commands) console.log(`  命令: ${issue.commands.join(', ')}`);
    console.log(`  片段: ${issue.snippet}...`);
    console.log('');
}
