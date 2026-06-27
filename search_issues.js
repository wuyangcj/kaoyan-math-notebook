const fs = require('fs');
const lines = fs.readFileSync('/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html', 'utf8').split('\n');
const line = lines[43948];
let idx = 0;
while ((idx = line.indexOf('0 \\le l', idx)) >= 0) {
  console.log('Found "0 \\le l" at ' + idx + ':');
  console.log(line.substring(idx, idx + 200));
  console.log('---');
  idx += 5;
}
idx = 0;
while ((idx = line.indexOf('若 \\ 且', idx)) >= 0) {
  console.log('Found "若 \\ 且" at ' + idx + ':');
  console.log(line.substring(idx, idx + 200));
  console.log('---');
  idx += 5;
}
idx = 0;
while ((idx = line.indexOf('p1 收敛', idx)) >= 0) {
  console.log('Found "p1 收敛" at ' + idx + ':');
  console.log(line.substring(Math.max(0, idx - 50), idx + 100));
  console.log('---');
  idx += 5;
}
idx = 0;
while ((idx = line.indexOf('p  1', idx)) >= 0) {
  console.log('Found "p  1" at ' + idx + ':');
  console.log(line.substring(Math.max(0, idx - 50), idx + 100));
  console.log('---');
  idx += 5;
}
idx = 0;
while ((idx = line.indexOf('a0）', idx)) >= 0) {
  console.log('Found "a0）" at ' + idx + ':');
  console.log(line.substring(Math.max(0, idx - 50), idx + 100));
  console.log('---');
  idx += 5;
}
