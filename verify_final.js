const fs = require('fs');
const file = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const content = fs.readFileSync(file, 'utf8');

// Extract the questionBank object using string-aware bracket matching
const startMarker = 'const questionBank = ';
const startIdx = content.indexOf(startMarker);
if (startIdx === -1) {
    console.error('ERROR: Could not find questionBank');
    process.exit(1);
}

let pos = startIdx + startMarker.length;
// Skip whitespace
while (content[pos] === ' ' || content[pos] === '\t' || content[pos] === '\n') pos++;

if (content[pos] !== '{') {
    console.error('ERROR: Expected { after questionBank =');
    process.exit(1);
}

// String-aware bracket matching
let depth = 0;
let inString = false;
let escape = false;
const objStart = pos;
for (; pos < content.length; pos++) {
    const ch = content[pos];
    if (escape) {
        escape = false;
        continue;
    }
    if (ch === '\\') {
        escape = true;
        continue;
    }
    if (ch === '"') {
        inString = !inString;
        continue;
    }
    if (inString) continue;
    if (ch === '{') depth++;
    else if (ch === '}') {
        depth--;
        if (depth === 0) break;
    }
}

const objEnd = pos + 1;
const jsonStr = content.substring(objStart, objEnd);

console.log('Extracted questionBank object:', jsonStr.length, 'characters');

// Parse the JSON
let questionBank;
try {
    questionBank = JSON.parse(jsonStr);
    console.log('✓ JSON parse successful!');
} catch (e) {
    console.error('✗ JSON parse error:', e.message);
    // Find the error position
    const match = e.message.match(/position (\d+)/);
    if (match) {
        const errPos = parseInt(match[1]);
        console.error('Context around error:', JSON.stringify(jsonStr.substring(errPos - 50, errPos + 50)));
    }
    process.exit(1);
}

// Verify shuyi structure
const shuyi = questionBank.shuyi;
if (!shuyi) {
    console.error('✗ shuyi not found');
    process.exit(1);
}
console.log('\n=== shuyi structure ===');
console.log('Keys:', Object.keys(shuyi));

// Verify supplement array
const supplement = shuyi.supplement;
if (!Array.isArray(supplement)) {
    console.error('✗ supplement is not an array');
    process.exit(1);
}
console.log('\nsupplement array length:', supplement.length);

// Count liyongle questions in supplement
const liyongleInSupp = supplement.filter(q => q.id && q.id.startsWith('liyongle_shuyi_'));
console.log('liyongle questions in supplement:', liyongleInSupp.length);

// Verify distribution
const gaoshu = liyongleInSupp.filter(q => q.subject === 'gaoshu');
const xiandai = liyongleInSupp.filter(q => q.subject === 'xiandai');
const gailv = liyongleInSupp.filter(q => q.subject === 'gailv');
console.log('  - gaoshu:', gaoshu.length);
console.log('  - xiandai:', xiandai.length);
console.log('  - gailv:', gailv.length);

// Verify IDs
const expectedGaoshu = Array.from({length: 30}, (_, i) => `liyongle_shuyi_gaoshu_${String(i+1).padStart(4, '0')}`);
const expectedXiandai = Array.from({length: 15}, (_, i) => `liyongle_shuyi_xiandai_${String(i+1).padStart(4, '0')}`);
const expectedGailv = Array.from({length: 15}, (_, i) => `liyongle_shuyi_gailv_${String(i+1).padStart(4, '0')}`);

const actualGaoshuIds = gaoshu.map(q => q.id);
const actualXiandaiIds = xiandai.map(q => q.id);
const actualGailvIds = gailv.map(q => q.id);

const gaoshuMatch = JSON.stringify(expectedGaoshu) === JSON.stringify(actualGaoshuIds);
const xiandaiMatch = JSON.stringify(expectedXiandai) === JSON.stringify(actualXiandaiIds);
const gailvMatch = JSON.stringify(expectedGailv) === JSON.stringify(actualGailvIds);

console.log('\nID verification:');
console.log('  gaoshu IDs match:', gaoshuMatch);
console.log('  xiandai IDs match:', xiandaiMatch);
console.log('  gailv IDs match:', gailvMatch);

if (!gaoshuMatch) {
    console.log('  Expected:', expectedGaoshu);
    console.log('  Actual:', actualGaoshuIds);
}
if (!xiandaiMatch) {
    console.log('  Expected:', expectedXiandai);
    console.log('  Actual:', actualXiandaiIds);
}
if (!gailvMatch) {
    console.log('  Expected:', expectedGailv);
    console.log('  Actual:', actualGailvIds);
}

// Verify no liyongle questions in other shuyi arrays
const otherArrays = ['gaoshu', 'xiandai', 'gailv'];
for (const arrName of otherArrays) {
    const arr = shuyi[arrName];
    if (Array.isArray(arr)) {
        const liyongleHere = arr.filter(q => q.id && q.id.startsWith('liyongle_shuyi_'));
        console.log(`\nliyongle questions in shuyi.${arrName}:`, liyongleHere.length);
        if (liyongleHere.length > 0) {
            console.error(`✗ ERROR: Found ${liyongleHere.length} liyongle questions in shuyi.${arrName}!`);
        }
    }
}

// Verify all liyongle questions have required fields
let fieldErrors = 0;
const requiredFields = ['id', 'subject', 'mathType', 'chapter', 'source', 'page', 'type', 'content', 'formula', 'options', 'answer', 'analysis', 'hint', 'video'];
for (const q of liyongleInSupp) {
    for (const field of requiredFields) {
        if (!(field in q)) {
            console.error(`✗ Missing field '${field}' in question ${q.id}`);
            fieldErrors++;
        }
    }
    // Verify options is array
    if (!Array.isArray(q.options)) {
        console.error(`✗ options is not an array in question ${q.id}`);
        fieldErrors++;
    }
    // Verify hint has required subfields
    if (q.hint) {
        if (!Array.isArray(q.hint.knowledgePoints)) {
            console.error(`✗ hint.knowledgePoints is not an array in question ${q.id}`);
            fieldErrors++;
        }
    }
    // Verify video has required subfields
    if (q.video) {
        if (typeof q.video.title !== 'string') {
            console.error(`✗ video.title is not a string in question ${q.id}`);
            fieldErrors++;
        }
    }
}

console.log('\nField verification:');
console.log('  Field errors:', fieldErrors);

// Verify type distribution
const choiceQs = liyongleInSupp.filter(q => q.type === '选择题');
const fillQs = liyongleInSupp.filter(q => q.type === '填空题');
console.log('\nType distribution:');
console.log('  选择题:', choiceQs.length, `(${(choiceQs.length/60*100).toFixed(1)}%)`);
console.log('  填空题:', fillQs.length, `(${(fillQs.length/60*100).toFixed(1)}%)`);

// Verify fill questions have empty options
const fillWithOpts = fillQs.filter(q => q.options.length > 0);
if (fillWithOpts.length > 0) {
    console.error(`✗ ${fillWithOpts.length} 填空题 have non-empty options!`);
}

// Summary
console.log('\n=== SUMMARY ===');
const allGood = liyongleInSupp.length === 60 && gaoshuMatch && xiandaiMatch && gailvMatch && fieldErrors === 0;
if (allGood) {
    console.log('✓ All 60 liyongle questions are correctly placed in supplement array!');
    console.log('✓ ID distribution: 30 gaoshu, 15 xiandai, 15 gailv');
    console.log('✓ All required fields present');
    console.log('✓ No liyongle questions in other shuyi arrays');
} else {
    console.error('✗ Some issues found, please review above!');
}
