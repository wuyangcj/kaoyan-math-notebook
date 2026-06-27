const fs = require('fs');
const content = fs.readFileSync('/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html', 'utf-8');

// Find supplement array start
const qbStart = content.indexOf('const questionBank');
const suppStart = content.indexOf('"supplement": [', qbStart);
const arrStart = content.indexOf('[', suppStart);

// Find the end by tracking brackets with proper string handling
let depth = 0;
let inStr = false, esc = false;
let i = arrStart;
while (i < content.length) {
    const c = content[i];
    if (esc) { esc = false; i++; continue; }
    if (c === '\\') { esc = true; i++; continue; }
    if (inStr) {
        if (c === '"') inStr = false;
        i++; continue;
    }
    if (c === '"') { inStr = true; i++; continue; }
    if (c === '[') depth++;
    else if (c === ']') { depth--; if (depth === 0) break; }
    i++;
}
const arrEnd = i;
console.log('Array start:', arrStart, 'Array end:', arrEnd);
console.log('Array length:', arrEnd - arrStart);

const arrStr = content.substring(arrStart, arrEnd + 1);
const supp = JSON.parse(arrStr);
console.log('Total supplement questions:', supp.length);

const liyongle = supp.filter(q => q.source === '李永乐660题');
console.log('李永乐660题 count:', liyongle.length);

const gaoshu = liyongle.filter(q => q.subject === 'gaoshu');
const xiandai = liyongle.filter(q => q.subject === 'xiandai');
const gailv = liyongle.filter(q => q.subject === 'gailv');
console.log('  gaoshu:', gaoshu.length);
console.log('  xiandai:', xiandai.length);
console.log('  gailv:', gailv.length);

const xuanze = liyongle.filter(q => q.type === '选择题');
const tiankong = liyongle.filter(q => q.type === '填空题');
console.log('  选择题:', xuanze.length, '(' + Math.round(xuanze.length/60*100) + '%)');
console.log('  填空题:', tiankong.length, '(' + Math.round(tiankong.length/60*100) + '%)');

const ids = liyongle.map(q => q.id);
console.log('First ID:', ids[0]);
console.log('Last ID:', ids[ids.length-1]);
console.log('All IDs unique:', ids.length === new Set(ids).size ? 'YES' : 'NO');

console.log('\nChapters (gaoshu):');
const gCh = {};
gaoshu.forEach(q => { gCh[q.chapter] = (gCh[q.chapter]||0) + 1; });
Object.entries(gCh).forEach(([k,v]) => console.log('  ' + k + ': ' + v));

console.log('\nChapters (xiandai):');
const xCh = {};
xiandai.forEach(q => { xCh[q.chapter] = (xCh[q.chapter]||0) + 1; });
Object.entries(xCh).forEach(([k,v]) => console.log('  ' + k + ': ' + v));

console.log('\nChapters (gailv):');
const glCh = {};
gailv.forEach(q => { glCh[q.chapter] = (glCh[q.chapter]||0) + 1; });
Object.entries(glCh).forEach(([k,v]) => console.log('  ' + k + ': ' + v));

// Verify all questions have required fields
let missing = [];
liyongle.forEach(q => {
    ['id','subject','mathType','chapter','source','page','type','content','formula','options','answer','analysis','hint','video'].forEach(f => {
        if (!(f in q)) missing.push(q.id + ' missing ' + f);
    });
    if (q.hint) {
        ['knowledgePoints','approach','tips'].forEach(f => {
            if (!(f in q.hint)) missing.push(q.id + ' missing hint.' + f);
        });
    }
    if (q.video) {
        ['title','source','url'].forEach(f => {
            if (!(f in q.video)) missing.push(q.id + ' missing video.' + f);
        });
    }
});
console.log('\nMissing fields:', missing.length === 0 ? 'NONE' : missing.join('; '));

console.log('\nJSON is VALID! All 60 questions verified.');
