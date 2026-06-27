// find_question_errors_v2.mjs - 题库 LaTeX 渲染错误检测脚本
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';
import fs from 'fs';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3000);

  // 收集所有题目
  const questions = await page.evaluate(() => {
    const all = [];
    // 辅助：安全遍历数组
    const forEachArr = (val, fn) => {
      if (Array.isArray(val)) val.forEach(fn);
      else if (val && typeof val === 'object') {
        // 如果是对象但不是数组，尝试遍历其值
        Object.keys(val).forEach(k => forEachArr(val[k], fn));
      }
    };
    // questionBank: { shuyi: { supplement: [...], gaoshu: [...] }, shuer: {...}, ... }
    for (const mt of Object.keys(questionBank || {})) {
      for (const cat of Object.keys(questionBank[mt] || {})) {
        forEachArr(questionBank[mt][cat], q => {
          if (q && q.id) all.push({ id: q.id, source: `questionBank.${mt}.${cat}`, content: q.content, options: q.options, answer: q.answer, analysis: q.analysis });
        });
      }
    }
    // chapterQuestionBank: { gaoshu: [ {chapter, questions: [...]}, ... ], ... }
    for (const subject of Object.keys(chapterQuestionBank || {})) {
      forEachArr(chapterQuestionBank[subject], item => {
        if (item && item.questions) {
          forEachArr(item.questions, q => {
            if (q && q.id) all.push({ id: q.id, source: `chapterQuestionBank.${subject}`, content: q.content, options: q.options, answer: q.answer, analysis: q.analysis });
          });
        } else if (item && item.id) {
          all.push({ id: item.id, source: `chapterQuestionBank.${subject}`, content: item.content, options: item.options, answer: item.answer, analysis: item.analysis });
        }
      });
    }
    // examPaperBank: { shuyi: [...], shuer: [...], ... }
    for (const paper of Object.keys(examPaperBank || {})) {
      forEachArr(examPaperBank[paper], q => {
        if (q && q.id) all.push({ id: q.id, source: `examPaperBank.${paper}`, content: q.content, options: q.options, answer: q.answer, analysis: q.analysis });
      });
    }
    return all;
  });

  console.log(`Total questions: ${questions.length}`);

  // 逐题检测：用 formatMath 处理后插入 DOM，再用 MathJax typeset 检查错误
  const testContainerId = 'test-math-container';
  await page.evaluate((id) => {
    let c = document.getElementById(id);
    if (!c) {
      c = document.createElement('div');
      c.id = id;
      c.style.position = 'absolute';
      c.style.left = '-9999px';
      c.style.top = '0';
      document.body.appendChild(c);
    }
  }, testContainerId);

  const errors = [];
  const batchSize = 20;

  for (let i = 0; i < questions.length; i += batchSize) {
    const batch = questions.slice(i, i + batchSize);
    const batchErrors = await page.evaluate(async ({qs, cid}) => {
      const container = document.getElementById(cid);
      container.innerHTML = '';
      const results = [];

      for (const q of qs) {
        const div = document.createElement('div');
        div.className = 'q-test';
        div.dataset.qid = q.id;
        // 模拟实际渲染：content + options + answer + analysis
        let html = '';
        if (q.content) html += formatMath(q.content);
        if (q.options) {
          for (const opt of q.options) html += '<br>' + formatMath(opt);
        }
        if (q.answer) html += '<br>答案：' + formatMath(q.answer);
        if (q.analysis) html += '<br>解析：' + formatMath(q.analysis);
        div.innerHTML = html;
        container.appendChild(div);
      }

      // MathJax typeset
      if (window.MathJax && window.MathJax.typesetPromise) {
        await window.MathJax.typesetPromise([container]);
      }

      // 检查错误
      for (const div of container.querySelectorAll('.q-test')) {
        const qid = div.dataset.qid;
        const merrors = div.querySelectorAll('merror');
        const text = div.textContent || '';
        // 检查 literal \( 或 \)（未被 MathJax 处理的定界符）
        const literalMatch = text.match(/\\\(|\\\)/);
        if (merrors.length > 0 || literalMatch) {
          const errorTypes = [];
          if (merrors.length > 0) errorTypes.push('merror');
          if (literalMatch) errorTypes.push('literal \\( or \\)');
          results.push({ id: qid, types: errorTypes, text: text.substring(0, 200) });
        }
      }
      return results;
    }, {qs: batch, cid: testContainerId});

    errors.push(...batchErrors);
    if ((i + batchSize) % 200 === 0 || i + batchSize >= questions.length) {
      console.log(`Progress: ${Math.min(i + batchSize, questions.length)}/${questions.length}, errors: ${errors.length}`);
    }
  }

  console.log(`\n========== RESULTS ==========`);
  console.log(`Total questions checked: ${questions.length}`);
  console.log(`Questions with errors: ${errors.length}`);

  // 按错误类型分类
  const merrorCount = errors.filter(e => e.types.includes('merror')).length;
  const literalCount = errors.filter(e => e.types.includes('literal \\( or \\)')).length;
  console.log(`  merror: ${merrorCount}`);
  console.log(`  literal \\( or \\): ${literalCount}`);

  // 输出前 100 个错误详情
  console.log(`\n--- Error Details (first 100) ---`);
  for (let i = 0; i < Math.min(100, errors.length); i++) {
    const e = errors[i];
    console.log(`\n[${e.id}]`);
    console.log(`  Types: ${e.types.join(', ')}`);
    console.log(`  Text: ${e.text}`);
  }

  // 保存完整结果到文件
  const report = {
    total: questions.length,
    errors: errors.length,
    merrorCount,
    literalCount,
    details: errors,
  };
  fs.writeFileSync('/Users/wuyangcj/trae/回甘demo/question_errors_v2.json', JSON.stringify(report, null, 2));
  console.log(`\nFull report saved to question_errors_v2.json`);

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
