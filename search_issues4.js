const fs = require('fs');
const lines = fs.readFileSync('/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html', 'utf8').split('\n');
const line = lines[44173];
let idx = 0;
while ((idx = line.indexOf('aₙxⁿ', idx)) >= 0) {
  console.log('Found "aₙxⁿ" at ' + idx + ':');
  console.log(line.substring(Math.max(0, idx - 80), idx + 200));
  console.log('---');
  idx += 5;
}
// Also search for x^\frac{n+1}{n+1}
idx = 0;
while ((idx = line.indexOf('\\frac{n+1}{n+1}', idx)) >= 0) {
  console.log('Found "\\frac{n+1}{n+1}" at ' + idx + ':');
  console.log(line.substring(Math.max(0, idx - 80), idx + 100));
  console.log('---');
  idx += 5;
}
