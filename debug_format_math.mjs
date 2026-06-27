// debug_format_math.mjs - 调试 formatMath 对特定题目的处理结果
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3000);

  // Collect console messages from the page
  page.on('console', msg => console.log(`[PAGE CONSOLE] ${msg.text()}`));

  const result = await page.evaluate(async () => {
    const testQs = [];

    // Find a few specific failing questions
    if (typeof questionBank !== 'undefined' && questionBank.shuyi && questionBank.shuyi.supplement) {
      for (const q of questionBank.shuyi.supplement) {
        if (q.id === 'lilin_shuyi_xiandai_0003' || q.id === 'real_2022_math1_q1' || q.id === 'soc_gs_009') {
          testQs.push(q);
        }
      }
    }

    const results = [];
    for (const q of testQs) {
      const rawContent = q.content;
      const formattedContent = formatMath(rawContent);
      const rawAnalysis = q.analysis || '';
      const formattedAnalysis = formatMath(rawAnalysis);

      // Build the full HTML
      let html = `<div>${formattedContent}</div>`;
      if (q.answer) html += `<div>${formatMath(q.answer)}</div>`;
      if (q.analysis) {
        for (const line of String(q.analysis).split('\\n')) {
          html += `<div>${formatMath(line)}</div>`;
        }
      }

      // Set innerHTML and check
      const testContainer = document.createElement('div');
      testContainer.style.position = 'absolute';
      testContainer.style.left = '-9999px';
      document.body.appendChild(testContainer);
      testContainer.innerHTML = html;

      // Get textContent before MathJax
      const textBefore = testContainer.textContent;

      // Run MathJax
      if (window.MathJax && window.MathJax.typesetPromise) {
        try {
          await window.MathJax.typesetPromise([testContainer]);
        } catch (e) {
          results.push({ qid: q.id, error: `MathJax error: ${e.message}` });
        }
      }

      // Get textContent after MathJax
      const textAfter = testContainer.textContent;

      // Check for mjx-container elements
      const mjxCount = testContainer.querySelectorAll('mjx-container').length;
      const merrorCount = testContainer.querySelectorAll('merror').length;

      // Check for literal \( in text
      const hasLiteralDelim = textAfter.includes('\\(') || textAfter.includes('\\)');

      results.push({
        qid: q.id,
        rawContent: rawContent.substring(0, 200),
        formattedContent: formattedContent.substring(0, 300),
        formattedAnalysis: formattedAnalysis.substring(0, 300),
        fullHtml: html.substring(0, 500),
        textBefore: textBefore.substring(0, 200),
        textAfter: textAfter.substring(0, 200),
        mjxCount,
        merrorCount,
        hasLiteralDelim,
      });

      document.body.removeChild(testContainer);
    }

    return results;
  });

  for (const r of result) {
    console.log(`\n========== ${r.qid} ==========`);
    if (r.error) {
      console.log(`ERROR: ${r.error}`);
      continue;
    }
    console.log(`Raw content: ${r.rawContent}`);
    console.log(`Formatted:   ${r.formattedContent}`);
    console.log(`Formatted analysis: ${r.formattedAnalysis}`);
    console.log(`Full HTML:   ${r.fullHtml}`);
    console.log(`Text before MathJax: ${r.textBefore}`);
    console.log(`Text after MathJax:  ${r.textAfter}`);
    console.log(`MathJax elements: ${r.mjxCount}, merrors: ${r.merrorCount}`);
    console.log(`Has literal \\( or \\): ${r.hasLiteralDelim}`);
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
