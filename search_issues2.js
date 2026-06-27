const fs = require('fs');
const lines = fs.readFileSync('/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html', 'utf8').split('\n');
const line = lines[44012];
let idx = 0;
while ((idx = line.indexOf('sigma^{2}0', idx)) >= 0) {
  console.log('Found "sigma^{2}0" at ' + idx + ':');
  console.log(line.substring(Math.max(0, idx - 80), idx + 120));
  console.log('---');
  idx += 5;
}
idx = 0;
while ((idx = line.indexOf('0p1', idx)) >= 0) {
  console.log('Found "0p1" at ' + idx + ':');
  console.log(line.substring(Math.max(0, idx - 80), idx + 120));
  console.log('---');
  idx += 5;
}
