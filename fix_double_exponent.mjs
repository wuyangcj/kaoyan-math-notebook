// fix_double_exponent.mjs - 批量修复 5^8^1 → 5 \\cdot 8 \\cdot 1
import fs from 'fs';

const file = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
let content = fs.readFileSync(file, 'utf-8');

// 匹配 "数字^数字^数字" 格式（在引号内，是选项数据）
// 改为 "数字 \\cdot 数字 \\cdot 数字"
const regex = /"(\d+)\^(\d+)\^(\d+)"/g;
const matches = content.match(regex);
console.log(`Found ${matches ? matches.length : 0} matches`);

const newContent = content.replace(regex, (m, a, b, c) => {
    return `"${a}\\cdot ${b}\\cdot ${c}"`;
});

// 验证修改
const newMatches = newContent.match(/"\d+\^\d+\^\d+"/g);
console.log(`After fix: ${newMatches ? newMatches.length : 0} matches remaining`);

if (matches && matches.length > 0) {
    fs.writeFileSync(file, newContent);
    console.log(`Fixed ${matches.length} double exponent options`);
    // 显示前5个修改示例
    matches.slice(0, 5).forEach(m => {
        const fixed = m.replace(/(\d+)\^(\d+)\^(\d+)/, '$1\\cdot $2\\cdot $3');
        console.log(`  ${m} → ${fixed}`);
    });
}
