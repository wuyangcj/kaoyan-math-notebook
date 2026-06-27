const fs = require('fs');
const file = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
let content = fs.readFileSync(file, 'utf8');
let lines = content.split('\n');

// Verify boundary lines (0-indexed: line N = index N-1)
console.log('=== Verification of boundary lines ===');
console.log('Line 5594 (supplement end):', JSON.stringify(lines[5593]));
console.log('Line 5595 (gaoshu start):', JSON.stringify(lines[5594]));
console.log('Line 12565 (last original gailv Q):', JSON.stringify(lines[12564]));
console.log('Line 12566 (first liyongle Q):', JSON.stringify(lines[12565]));
console.log('Line 14395 (last Q video close):', JSON.stringify(lines[14394]));
console.log('Line 14396 (gailv array close):', JSON.stringify(lines[14395]));
console.log('Line 14397 (shuyi close):', JSON.stringify(lines[14396]));

// Verify the first question ID
if (!lines[12565].includes('{') || !lines[12566].includes('liyongle_shuyi_gaoshu_0001')) {
    console.error('ERROR: Expected first liyongle question at line 12566-12567');
    process.exit(1);
}

// Verify the last question ID
if (!lines[14370].includes('liyongle_shuyi_gailv_0015')) {
    console.error('ERROR: Expected last liyongle question at line 14371');
    process.exit(1);
}

// Step 1: Extract the 60 questions
// Lines 12566-14395 (indices 12565-14394) contain the 60 questions
// Q1-Q59 end with `},` and Q60's video closes with `}` on line 14395
// The `}` that closes Q60 is the first char of `}]` on line 14396
const questionsLines = lines.slice(12565, 14395); // indices 12565 to 14394 (lines 12566-14395)
// Add `}` to close Q60 (this was the `}` in `}]` on line 14396)
questionsLines.push('}');

console.log('\nExtracted', questionsLines.length, 'lines of questions');
console.log('First line:', JSON.stringify(questionsLines[0]));
console.log('Last line:', JSON.stringify(questionsLines[questionsLines.length - 1]));

// Step 2: Remove the 60 questions from gailv and fix closing
// Change line 12565 (index 12564) from `},` to `}]` to close the gailv array
lines[12564] = '}]';
// Remove lines 12566-14396 (indices 12565-14395)
const removedCount = 14395 - 12565 + 1; // = 1831
lines.splice(12565, removedCount);
console.log('\nRemoved', removedCount, 'lines from gailv array');
console.log('Line 12565 after removal:', JSON.stringify(lines[12564]));
console.log('Line 12566 after removal:', JSON.stringify(lines[12565]));

// Step 3: Insert at supplement array end
// Line 5594 (index 5593) was `        }],`
// Change to `        },` (comma to separate from new questions)
lines[5593] = '        },';
// Insert questions + `        }],` after index 5593
const insertLines = [...questionsLines, '        }],'];
lines.splice(5594, 0, ...insertLines);
console.log('\nInserted', insertLines.length, 'lines at supplement end');
console.log('Line 5594 after insert:', JSON.stringify(lines[5593]));
console.log('Line 5595 after insert:', JSON.stringify(lines[5594]));
console.log('Line 5596 after insert:', JSON.stringify(lines[5595]));

// Write the file
fs.writeFileSync(file, lines.join('\n'));
console.log('\nFile written successfully!');
console.log('Total lines:', lines.length);
