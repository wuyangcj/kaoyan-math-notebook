// find_question_errors.mjs - 全面检测题库（刷题）内容的 LaTeX 渲染错误
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3000);

  // 收集所有题目并检测错误
  const results = await page.evaluate(async () => {
    const errors = [];
    const allQuestions = [];

    // 1. 收集 questionBank 中的题目
    if (typeof questionBank !== 'undefined') {
      for (const mathType of Object.keys(questionBank)) {
        const bank = questionBank[mathType];
        if (!bank) continue;
        // 收集 supplement
        if (bank.supplement && Array.isArray(bank.supplement)) {
          for (const q of bank.supplement) {
            allQuestions.push({ source: `questionBank.${mathType}.supplement`, q });
          }
        }
        // 收集各科目
        for (const subject of Object.keys(bank)) {
          if (subject === 'supplement') continue;
          if (Array.isArray(bank[subject])) {
            for (const q of bank[subject]) {
              allQuestions.push({ source: `questionBank.${mathType}.${subject}`, q });
            }
          }
        }
      }
    }

    // 2. 收集 chapterQuestionBank 中的题目
    if (typeof chapterQuestionBank !== 'undefined') {
      for (const mathType of Object.keys(chapterQuestionBank)) {
        const subjects = chapterQuestionBank[mathType];
        if (!subjects) continue;
        for (const subject of Object.keys(subjects)) {
          const chapters = subjects[subject];
          if (!Array.isArray(chapters)) continue;
          for (const chapterObj of chapters) {
            if (chapterObj && Array.isArray(chapterObj.questions)) {
              for (const q of chapterObj.questions) {
                allQuestions.push({ source: `chapterQuestionBank.${mathType}.${subject}.${chapterObj.chapter}`, q });
              }
            }
          }
        }
      }
    }

    // 3. 收集 examPaperBank 中的题目
    if (typeof examPaperBank !== 'undefined') {
      for (const mathType of Object.keys(examPaperBank)) {
        const years = examPaperBank[mathType];
        if (!years) continue;
        for (const year of Object.keys(years)) {
          const paper = years[year];
          if (paper && Array.isArray(paper.questions)) {
            for (const q of paper.questions) {
              allQuestions.push({ source: `examPaperBank.${mathType}.${year}`, q });
            }
          }
        }
      }
    }

    // 4. 逐题渲染并检测错误
    const testContainer = document.createElement('div');
    testContainer.style.position = 'absolute';
    testContainer.style.left = '-9999px';
    testContainer.style.top = '0';
    testContainer.style.width = '800px';
    document.body.appendChild(testContainer);

    for (let i = 0; i < allQuestions.length; i++) {
      const { source, q } = allQuestions[i];
      const qid = q.id || `idx${i}`;

      // 构建渲染内容
      let html = '';
      if (q.content) html += `<div class="qc">${formatMath(q.content)}</div>`;
      if (q.formula) html += `<div class="qf">$$${formatMathLatex(q.formula)}$$</div>`;
      if (q.options && Array.isArray(q.options)) {
        for (const opt of q.options) {
          html += `<div class="qo">${formatMath(opt)}</div>`;
        }
      }
      if (q.answer) html += `<div class="qa">${formatMath(q.answer)}</div>`;
      if (q.analysis) {
        const lines = String(q.analysis).split('\\n');
        for (const line of lines) {
          html += `<div class="qal">${formatMath(line)}</div>`;
        }
      }

      testContainer.innerHTML = html;

      // 等 MathJax 排版
      if (window.MathJax && window.MathJax.typesetPromise) {
        try {
          await window.MathJax.typesetPromise([testContainer]);
        } catch (e) { /* ignore */ }
      }

      // 检测错误
      // 1. merror 元素（黄底红字 MathJax 错误）
      const merrors = testContainer.querySelectorAll('mjx-container[jax="SVG"] merror, mjx-container merror');
      // 2. 红色 mtext（\( \) 字面量未被渲染）
      const redMtexts = testContainer.querySelectorAll('mjx-container mjx-text[style*="color"], mjx-container mjx-mtext[style*="color"]');

      // 更通用的检测：查找所有红色文本的 MathJax 元素
      const allMjx = testContainer.querySelectorAll('mjx-container');
      let hasError = false;
      let errorDetails = [];

      for (const mjx of allMjx) {
        // 检查 merror
        const merr = mjx.querySelector('merror');
        if (merr) {
          hasError = true;
          const text = merr.textContent || '';
          errorDetails.push(`merror: ${text.substring(0, 100)}`);
          continue;
        }
        // 检查红色文本（通常是未渲染的 \( \) 等）
        const styled = mjx.querySelectorAll('[style*="color"], [color]');
        for (const el of styled) {
          const style = el.getAttribute('style') || '';
          const color = el.getAttribute('color') || '';
          if (style.includes('color') || color) {
            const text = el.textContent || '';
            if (text.includes('(') || text.includes(')') || text.includes('\\')) {
              hasError = true;
              errorDetails.push(`red-mtext: ${text.substring(0, 100)}`);
            }
          }
        }
      }

      // 也检查文本中的字面量 \( 和 \)
      const rawText = testContainer.textContent || '';
      if (rawText.includes('\\(') || rawText.includes('\\)')) {
        hasError = true;
        errorDetails.push('literal \\( or \\) in text');
      }

      if (hasError) {
        errors.push({
          qid,
          source,
          content: (q.content || '').substring(0, 80),
          details: errorDetails
        });
      }

      // 清空容器，避免累积
      testContainer.innerHTML = '';

      // 每100题输出一次进度
      if ((i + 1) % 100 === 0) {
        console.log(`Processed ${i + 1}/${allQuestions.length} questions, ${errors.length} errors so far`);
      }
    }

    document.body.removeChild(testContainer);

    return { total: allQuestions.length, errors };
  });

  console.log(`\n========== QUESTION BANK ERROR DETECTION ==========`);
  console.log(`Total questions checked: ${results.total}`);
  console.log(`Questions with errors: ${results.errors.length}`);
  console.log(`\n--- Error Details ---`);

  for (const err of results.errors) {
    console.log(`\n[${err.qid}] (${err.source})`);
    console.log(`  Content: ${err.content}`);
    for (const d of err.details) {
      console.log(`  - ${d}`);
    }
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
