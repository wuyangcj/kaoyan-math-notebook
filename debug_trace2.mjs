// debug_trace2.mjs - Trace questions with REAL errors (from error report)
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';
import fs from 'fs';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

// Read error IDs from the report
const report = JSON.parse(fs.readFileSync('/Users/wuyangcj/trae/回甘demo/question_errors_v2.json', 'utf-8'));
const TEST_IDS = report.details.slice(0, 15).map(e => e.id);

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3000);

  // Collect the test questions
  const questions = await page.evaluate((ids) => {
    const result = {};
    const forEachArr = (val, fn) => {
      if (Array.isArray(val)) val.forEach(fn);
      else if (val && typeof val === 'object') {
        Object.keys(val).forEach(k => forEachArr(val[k], fn));
      }
    };
    const allQs = [];
    for (const mt of Object.keys(questionBank || {})) {
      for (const cat of Object.keys(questionBank[mt] || {})) {
        forEachArr(questionBank[mt][cat], q => { if (q && q.id) allQs.push(q); });
      }
    }
    for (const subject of Object.keys(chapterQuestionBank || {})) {
      forEachArr(chapterQuestionBank[subject], item => {
        if (item && item.questions) {
          forEachArr(item.questions, q => { if (q && q.id) allQs.push(q); });
        } else if (item && item.id) {
          allQs.push(item);
        }
      });
    }
    for (const paper of Object.keys(examPaperBank || {})) {
      forEachArr(examPaperBank[paper], q => { if (q && q.id) allQs.push(q); });
    }
    for (const q of allQs) {
      if (ids.includes(q.id)) result[q.id] = q;
    }
    return result;
  }, TEST_IDS);

  // For each test question, trace each field separately
  const trace = await page.evaluate(async (qs) => {
    const results = [];
    const container = document.createElement('div');
    container.style.position = 'absolute';
    container.style.left = '-9999px';
    document.body.appendChild(container);

    for (const id of Object.keys(qs)) {
      const q = qs[id];
      const info = { id, fields: {} };

      const fields = [
        { name: 'content', val: q.content },
        { name: 'answer', val: q.answer },
        { name: 'analysis', val: q.analysis },
      ];
      if (q.options) {
        q.options.forEach((opt, i) => fields.push({ name: `option${i}`, val: opt }));
      }

      for (const { name, val } of fields) {
        if (!val) continue;
        const formatted = formatMath(val);
        container.innerHTML = '';
        const div = document.createElement('div');
        div.innerHTML = formatted;
        container.appendChild(div);

        if (window.MathJax && window.MathJax.typesetPromise) {
          await window.MathJax.typesetPromise([div]);
        }

        const merrors = div.querySelectorAll('merror');
        const text = div.textContent || '';
        const hasLiteral = /\\\(|\\\)/.test(text);

        if (merrors.length > 0 || hasLiteral) {
          info.fields[name] = {
            raw: val.substring(0, 300),
            formatted: formatted.substring(0, 400),
            merrorCount: merrors.length,
            hasLiteral,
            literalMatches: text.match(/\\\(|\\\)/g),
            textAfterTypeset: text.substring(0, 300),
            merrorText: Array.from(merrors).map(m => m.textContent.substring(0, 100)),
          };
        }
      }
      if (Object.keys(info.fields).length > 0) results.push(info);
    }
    return results;
  }, questions);

  for (const t of trace) {
    console.log(`\n${'='.repeat(70)}`);
    console.log(`ID: ${t.id}`);
    for (const [fieldName, fieldData] of Object.entries(t.fields)) {
      console.log(`\n  --- Field: ${fieldName} ---`);
      console.log(`  Raw: ${fieldData.raw}`);
      console.log(`  Formatted: ${fieldData.formatted}`);
      console.log(`  merrorCount: ${fieldData.merrorCount}`);
      if (fieldData.merrorText.length > 0) {
        console.log(`  merrorText: ${JSON.stringify(fieldData.merrorText)}`);
      }
      console.log(`  hasLiteral: ${fieldData.hasLiteral}`);
      if (fieldData.literalMatches) {
        console.log(`  literalMatches: ${JSON.stringify(fieldData.literalMatches)}`);
      }
      console.log(`  textAfterTypeset: ${fieldData.textAfterTypeset}`);
    }
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
