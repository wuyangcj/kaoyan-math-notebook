// debug_trace.mjs - Trace exactly what happens with flagged questions
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

const TEST_IDS = [
  'liyongle_shuyi_xiandai_0006',
  'soc_gs_004',
  'soc_xd_011',
  'real_2023_math2_q1_shuer',
  'soc_gl_014',
];

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
        forEachArr(questionBank[mt][cat], q => {
          if (q && q.id) allQs.push(q);
        });
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

  // For each test question, trace the full pipeline
  const trace = await page.evaluate(async (qs) => {
    const results = [];
    const container = document.createElement('div');
    container.style.position = 'absolute';
    container.style.left = '-9999px';
    document.body.appendChild(container);

    for (const id of Object.keys(qs)) {
      const q = qs[id];
      const raw = q.content || '';
      const formatted = formatMath(raw);
      const info = { id, raw, formatted, steps: {} };

      // Set innerHTML
      container.innerHTML = '';
      const div = document.createElement('div');
      div.innerHTML = formatted;
      container.appendChild(div);

      // Before MathJax
      info.steps.beforeTypeset = {
        innerHTML: div.innerHTML.substring(0, 500),
        textContent: (div.textContent || '').substring(0, 500),
      };

      // MathJax typeset
      if (window.MathJax && window.MathJax.typesetPromise) {
        try {
          await window.MathJax.typesetPromise([div]);
        } catch (e) {
          info.steps.typesetError = e.message;
        }
      }

      // After MathJax
      const merrors = div.querySelectorAll('merror');
      const text = div.textContent || '';
      info.steps.afterTypeset = {
        innerHTML: div.innerHTML.substring(0, 800),
        textContent: text.substring(0, 500),
        merrorCount: merrors.length,
        hasLiteralDelim: /\\\(|\\\)/.test(text),
        literalMatches: text.match(/\\\(|\\\)/g),
      };

      results.push(info);
    }
    return results;
  }, questions);

  for (const t of trace) {
    console.log(`\n${'='.repeat(60)}`);
    console.log(`ID: ${t.id}`);
    console.log(`Raw: ${t.raw.substring(0, 200)}`);
    console.log(`Formatted: ${t.formatted.substring(0, 300)}`);
    console.log(`Before typeset textContent: ${t.steps.beforeTypeset.textContent.substring(0, 200)}`);
    if (t.steps.typesetError) console.log(`Typeset ERROR: ${t.steps.typesetError}`);
    console.log(`After typeset merrorCount: ${t.steps.afterTypeset.merrorCount}`);
    console.log(`After typeset hasLiteralDelim: ${t.steps.afterTypeset.hasLiteralDelim}`);
    if (t.steps.afterTypeset.literalMatches) {
      console.log(`Literal matches: ${JSON.stringify(t.steps.afterTypeset.literalMatches)}`);
    }
    console.log(`After typeset textContent: ${t.steps.afterTypeset.textContent.substring(0, 200)}`);
    console.log(`After typeset innerHTML (first 500): ${t.steps.afterTypeset.innerHTML.substring(0, 500)}`);
  }

  // Also check the MathJax config
  const mjConfig = await page.evaluate(() => {
    if (window.MathJax && window.MathJax.config) {
      return JSON.stringify(window.MathJax.config.tex || {});
    }
    return 'no tex config';
  });
  console.log(`\n${'='.repeat(60)}`);
  console.log(`MathJax tex config: ${mjConfig}`);

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
