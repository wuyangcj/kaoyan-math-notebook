// analyze_errors.mjs - 分析剩余错误模式
import fs from 'fs';

const report = JSON.parse(fs.readFileSync('/Users/wuyangcj/trae/回甘demo/question_errors_v2.json', 'utf-8'));

console.log(`Total errors: ${report.errors}`);
console.log(`  merror: ${report.merrorCount}`);
console.log(`  literal: ${report.literalCount}`);

// 分类错误模式
const patterns = {
  '未闭合定界符_ frac': 0,      // \frac{1}{e\}) 格式
  '未闭合定界符_其他': 0,
  '矩阵括号表示法': 0,           // \([1234]\) 格式
  'HTML标签_小于号': 0,          // \(x<b\) 格式
  '定界符顺序错误': 0,           // \)其他\( 格式
  'dollar定界符': 0,             // $...$ 格式
  '其他': 0,
};

const examples = {};

for (const e of report.details) {
  const text = e.text || '';
  let matched = false;

  // 未闭合定界符：\frac{...}{...\}) 
  if (/\\frac\{[^}]*\}\{[^}]*\\\}\)/.test(text)) {
    patterns['未闭合定界符_ frac']++;
    if (!examples['未闭合定界符_ frac']) examples['未闭合定界符_ frac'] = e.id + ': ' + text.substring(0, 150);
    matched = true;
  }
  // 矩阵括号表示法：\([数字]\) 或 \([数字 \\ 数字]\)
  else if (/\\\(\s*\[?\s*[\d\s\\\-.]+\s*\]?\s*\\\)/.test(text)) {
    patterns['矩阵括号表示法']++;
    if (!examples['矩阵括号表示法']) examples['矩阵括号表示法'] = e.id + ': ' + text.substring(0, 150);
    matched = true;
  }
  // dollar定界符
  else if (/\$[^$]+\$/.test(text)) {
    patterns['dollar定界符']++;
    if (!examples['dollar定界符']) examples['dollar定界符'] = e.id + ': ' + text.substring(0, 150);
    matched = true;
  }
  // 定界符顺序错误：\)...\( 
  else if (/\\\)[^\\]{0,20}\\\(/.test(text)) {
    patterns['定界符顺序错误']++;
    if (!examples['定界符顺序错误']) examples['定界符顺序错误'] = e.id + ': ' + text.substring(0, 150);
    matched = true;
  }
  // HTML标签：\(.*<.*\)
  else if (/\\\(.*<[a-zA-Z].*\\\)/.test(text)) {
    patterns['HTML标签_小于号']++;
    if (!examples['HTML标签_小于号']) examples['HTML标签_小于号'] = e.id + ': ' + text.substring(0, 150);
    matched = true;
  }

  if (!matched) {
    patterns['其他']++;
    if (!examples['其他']) examples['其他'] = e.id + ': ' + text.substring(0, 200);
  }
}

console.log('\n=== 错误模式分类 ===');
for (const [pattern, count] of Object.entries(patterns)) {
  console.log(`${pattern}: ${count}`);
  if (examples[pattern]) console.log(`  示例: ${examples[pattern]}`);
}

// 输出前30个"其他"类错误的完整文本
console.log('\n=== "其他"类错误前30个 ===');
let otherCount = 0;
for (const e of report.details) {
  const text = e.text || '';
  const isUnmatchedFrac = /\\frac\{[^}]*\}\{[^}]*\\\}\)/.test(text);
  const isMatrix = /\\\(\s*\[?\s*[\d\s\\\-.]+s*\]?\s*\\\)/.test(text);
  const isDollar = /\$[^$]+\$/.test(text);
  const isOrderErr = /\\\)[^\\]{0,20}\\\(/.test(text);
  const isHtmlTag = /\\\(.*<[a-zA-Z].*\\\)/.test(text);

  if (!isUnmatchedFrac && !isMatrix && !isDollar && !isOrderErr && !isHtmlTag) {
    otherCount++;
    if (otherCount <= 30) {
      console.log(`\n[${e.id}]`);
      console.log(`  ${text.substring(0, 250)}`);
    }
  }
}
