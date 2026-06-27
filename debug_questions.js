const fs = require('fs');
const content = fs.readFileSync('/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html', 'utf-8');

// Check what's around position 309369
console.log('Content around 309369:');
console.log(JSON.stringify(content.substring(309340, 309420)));
console.log();

// Count lines up to position 309369
const lines = content.substring(0, 309369).split('\n');
console.log('Line number at 309369:', lines.length);

// Show the line
console.log('Line content:', lines[lines.length - 1]);

// Now let's check: is the ] at 309369 inside a string?
// Let's track string state from the array start
const arrStart = 269476;
let inStr = false, esc = false;
let depth = 0;
for (let i = arrStart; i <= 309369; i++) {
    const c = content[i];
    if (esc) { esc = false; continue; }
    if (c === '\\') { esc = true; continue; }
    if (inStr) {
        if (c === '"') inStr = false;
        continue;
    }
    if (c === '"') { inStr = true; continue; }
    if (c === '[') depth++;
    else if (c === ']') depth--;
}
console.log('\nDepth at 309369:', depth);
console.log('In string at 309369:', inStr);

// Let's also check: what's the depth right before the ] at 309369?
inStr = false; esc = false; depth = 0;
for (let i = arrStart; i < 309369; i++) {
    const c = content[i];
    if (esc) { esc = false; continue; }
    if (c === '\\') { esc = true; continue; }
    if (inStr) {
        if (c === '"') inStr = false;
        continue;
    }
    if (c === '"') { inStr = true; continue; }
    if (c === '[') depth++;
    else if (c === ']') depth--;
}
console.log('Depth right before 309369:', depth);

// Check what character is at 309369
console.log('Character at 309369:', JSON.stringify(content[309369]));
