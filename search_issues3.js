const fs = require('fs');
const lines = fs.readFileSync('/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html', 'utf8').split('\n');
// Line 44003
const line1 = lines[44002];
let idx = 0;
while ((idx = line1.indexOf('\\sqrt D(X)', idx)) >= 0) {
  console.log('Line 44003 "sqrt D(X)" at ' + idx + ':');
  console.log(line1.substring(Math.max(0, idx - 80), idx + 120));
  console.log('---');
  idx += 5;
}
idx = 0;
while ((idx = line1.indexOf('\\frac{q}{p}^{2}', idx)) >= 0) {
  console.log('Line 44003 "frac{q}{p}^{2}" at ' + idx + ':');
  console.log(line1.substring(Math.max(0, idx - 80), idx + 120));
  console.log('---');
  idx += 5;
}
// Line 44028
const line2 = lines[44027];
idx = 0;
while ((idx = line2.indexOf('\\sqrt D(X)', idx)) >= 0) {
  console.log('Line 44028 "sqrt D(X)" at ' + idx + ':');
  console.log(line2.substring(Math.max(0, idx - 80), idx + 120));
  console.log('---');
  idx += 5;
}
// Line 26986 - this is the x^{n+1}/(n+1) issue but it's already in the right form x^\frac{n+1}{n+1} - let me check
const line3 = lines[26985];
console.log('Line 26986:');
console.log(line3);
console.log('---');
// Line 47825
const line4 = lines[47824];
console.log('Line 47825:');
console.log(line4);
