// debug_matrix.mjs - Trace矩阵括号表示法错误
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';
import fs from 'fs';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

// 选取几个矩阵括号表示法错误的ID
const TEST_IDS = [
  'sy_x10',
  'sy_x21',
  'se_x1',
  'se_x16',
  'ss_gl_ch3_q7',
  'sy04_12',
  'sy04_17',
];

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3000);

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

  // 显示源数据
  for (const id of Object.keys(questions)) {
    const q = questions[id];
    console.log(`\n${'='.repeat(60)}`);
    console.log(`ID: ${id}`);
    console.log(`content: ${q.content || '(无)'}`);
    console.log(`answer: ${q.answer || '(无)'}`);
    if (q.options) {
      q.options.forEach((opt, i) => console.log(`option${i}: ${opt}`));
    }
    console.log(`analysis: ${(q.analysis || '(无)').substring(0, 300)}`);
  }

  // Trace formatMath 处理
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
          };
        }
      }
      if (Object.keys(info.fields).length > 0) results.push(info);
    }
    return results;
  }, questions);

  for (const t of trace) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`ID: ${t.id} - 错误字段`);
    for (const [fieldName, fieldData] of Object.entries(t.fields)) {
      console.log(`\n  --- Field: ${fieldName} ---`);
      console.log(`  Raw: ${fieldData.raw}`);
      console.log(`  Formatted: ${fieldData.formatted}`);
      console.log(`  merrorCount: ${fieldData.merrorCount}`);
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
