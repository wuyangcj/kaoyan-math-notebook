// debug_specific.mjs - 调试特定题目的 formatMath 处理结果
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(3000);

  const result = await page.evaluate(() => {
    const results = {};

    // 测试几个有代表性的题目
    const testIds = [
      'soc_xd_011',        // 矩阵 AB=\((1⋅0+2⋅1...\\)
      'real_2023_math2_q1_shuer', // 嵌套 \(\(...\)\)
      'soc_xd_012',        // answer: $(4009)$
      'supp_shuyi_xiandai_0008',  // Double exponent 5^8^1
      'se_x3',             // \(|a00b| =\)
    ];

    // 搜索所有题库
    const findQ = (id) => {
      for (const mt of Object.keys(questionBank || {})) {
        for (const cat of Object.keys(questionBank[mt] || {})) {
          const arr = questionBank[mt][cat];
          if (Array.isArray(arr)) {
            for (const q of arr) {
              if (q && q.id === id) return { q, source: `questionBank.${mt}.${cat}` };
            }
          }
        }
      }
      for (const subject of Object.keys(chapterQuestionBank || {})) {
        const arr = chapterQuestionBank[subject];
        if (Array.isArray(arr)) {
          for (const item of arr) {
            if (item && item.questions) {
              for (const q of item.questions) {
                if (q && q.id === id) return { q, source: `chapterQuestionBank.${subject}` };
              }
            }
          }
        }
      }
      for (const paper of Object.keys(examPaperBank || {})) {
        const arr = examPaperBank[paper];
        if (Array.isArray(arr)) {
          for (const q of arr) {
            if (q && q.id === id) return { q, source: `examPaperBank.${paper}` };
          }
        }
      }
      return null;
    };

    for (const id of testIds) {
      const found = findQ(id);
      if (!found) {
        results[id] = { error: 'not found' };
        continue;
      }
      const q = found.q;
      const analysisRaw = q.analysis || '';
      const analysisFormatted = formatMath(analysisRaw);
      const answerRaw = q.answer || '';
      const answerFormatted = formatMath(answerRaw);
      const contentRaw = q.content || '';
      const contentFormatted = formatMath(contentRaw);

      results[id] = {
        source: found.source,
        contentRaw,
        contentFormatted,
        answerRaw,
        answerFormatted,
        analysisRaw: analysisRaw.substring(0, 300),
        analysisFormatted: analysisFormatted.substring(0, 500),
      };
    }

    return results;
  });

  for (const [id, data] of Object.entries(result)) {
    console.log(`\n========== ${id} ==========`);
    if (data.error) {
      console.log(`  ERROR: ${data.error}`);
      continue;
    }
    console.log(`  Source: ${data.source}`);
    console.log(`  Content Raw:      ${data.contentRaw}`);
    console.log(`  Content Formatted: ${data.contentFormatted}`);
    console.log(`  Answer Raw:       ${data.answerRaw}`);
    console.log(`  Answer Formatted:  ${data.answerFormatted}`);
    console.log(`  Analysis Raw:      ${data.analysisRaw}`);
    console.log(`  Analysis Formatted: ${data.analysisFormatted}`);
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
