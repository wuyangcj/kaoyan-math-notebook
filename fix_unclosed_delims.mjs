// fix_unclosed_delims.mjs - 修复未闭合定界符
import fs from 'fs';

const file = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
let content = fs.readFileSync(file, 'utf-8');

// 文件中是 \\frac{1}{e\\}) （JSON转义），需要改为 \\frac{1}{e}\\)
// 正则中 \\\\ 匹配 \\（两个反斜杠），\\} 匹配 \}
const patterns = [
    { from: /\\\\frac\{1\}\{e\\\\\}\)/g, to: '\\\\frac{1}{e}\\\\)' },
    { from: /\\\\frac\{1\}\{2\\\\\}\)/g, to: '\\\\frac{1}{2}\\\\)' },
];

let totalFixed = 0;
for (const { from, to } of patterns) {
    const matches = content.match(from);
    if (matches) {
        console.log(`Found ${matches.length} matches for pattern ${from}`);
        console.log(`  Example: ${matches[0]}`);
        content = content.replace(from, to);
        totalFixed += matches.length;
    } else {
        console.log(`No matches for pattern ${from}`);
    }
}

if (totalFixed > 0) {
    fs.writeFileSync(file, content);
    console.log(`Fixed ${totalFixed} unclosed delimiters`);
} else {
    console.log('No fixes applied');
}
