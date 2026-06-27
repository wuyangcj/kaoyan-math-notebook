// find_all_errors_v2.mjs - Comprehensive error detection
// Directly renders each knowledge point's content and checks for MathJax errors
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForFunction(() => window.MathJax && window.MathJax.typesetPromise, { timeout: 30000 });
  await page.waitForTimeout(2000);

  // Get all knowledge base detail keys
  const kbInfo = await page.evaluate(() => {
    const results = [];
    for (const subject of ['gaoshu', 'xiandai', 'gailv']) {
      if (window.knowledgeBaseDetail && window.knowledgeBaseDetail[subject]) {
        for (const key in window.knowledgeBaseDetail[subject]) {
          const detail = window.knowledgeBaseDetail[subject][key];
          results.push({
            subject,
            key,
            title: detail.title || key,
            contentLength: detail.content ? detail.content.length : 0,
          });
        }
      }
    }
    return results;
  });

  console.log(`Found ${kbInfo.length} knowledge points`);

  // For each knowledge point, render its content and check for errors
  const allErrors = [];

  for (let i = 0; i < kbInfo.length; i++) {
    const { subject, key, title, contentLength } = kbInfo[i];

    // Render this knowledge point's content in a hidden div
    const errors = await page.evaluate(async (subj, k) => {
      const detail = window.knowledgeBaseDetail[subj][k];
      if (!detail || !detail.content) return [];

      // Create a hidden container
      const testDiv = document.createElement('div');
      testDiv.style.position = 'absolute';
      testDiv.style.left = '-9999px';
      testDiv.style.top = '0';
      testDiv.style.width = '800px';
      document.body.appendChild(testDiv);

      try {
        // Use the same rendering as showKnowledgeDetail
        let html = window._mathToLatex(detail.content);
        html = window.wrapMathInHtmlText(html);
        // Also process <code> blocks
        html = html.replace(/<code>([\s\S]*?)<\/code>/g, function(m, code) {
          // Decode HTML entities
          const decoded = code.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
          const hasMath = /[\\^_∑∫√αβγπσμλφθωΔΣΩ∞≤≥≠→∈∀∃∂∇·×±∘∝≡≅≈]|\\[a-zA-Z]/.test(decoded);
          if (hasMath) {
            return '<code>\\(' + decoded + '\\)</code>';
          }
          return m;
        });

        testDiv.innerHTML = '<div class="kb-detail-content">' + html + '</div>';

        // Wait for MathJax to render
        await window.MathJax.typesetPromise([testDiv]);

        // Check for errors
        const errors = [];

        // 1. merror elements (yellow background, red text)
        const merrors = testDiv.querySelectorAll('[data-mml-node="merror"]');
        merrors.forEach(el => {
          const errorText = el.getAttribute('data-mjx-error') || '';
          const container = el.closest('mjx-container');
          const parentEl = container ? container.parentElement : null;
          // Get surrounding text for context
          let context = '';
          if (parentEl) {
            const parentText = parentEl.textContent || '';
            context = parentText.slice(0, 120);
          }
          errors.push({
            type: 'merror',
            error: errorText,
            context: context,
          });
        });

        // 2. Red mtext elements (literal \( \) etc.)
        const redMtexts = testDiv.querySelectorAll('[data-mml-node="mtext"][fill="red"], [data-mml-node="mtext"][mathcolor="red"]');
        redMtexts.forEach(el => {
          const container = el.closest('mjx-container');
          const parentEl = container ? container.parentElement : null;
          const text = el.textContent || '';
          let context = '';
          if (parentEl) {
            context = (parentEl.textContent || '').slice(0, 120);
          }
          errors.push({
            type: 'red-mtext',
            text: text,
            context: context,
          });
        });

        return errors;
      } finally {
        document.body.removeChild(testDiv);
      }
    }, subject, key);

    if (errors.length > 0) {
      console.log(`\n❌ [${i+1}] ${subject}/${key} (${title}):`);
      errors.forEach((e, j) => {
        console.log(`   Error ${j+1}: ${e.type} - ${e.error || e.text}`);
        console.log(`     Context: ${e.context}`);
      });
      allErrors.push({ subject, key, title, errors });
    } else {
      console.log(`✅ [${i+1}] ${subject}/${key} (${title})`);
    }
  }

  console.log(`\n\n========== SUMMARY ==========`);
  console.log(`Total knowledge points: ${kbInfo.length}`);
  console.log(`Points with errors: ${allErrors.length}`);
  console.log(`Total errors: ${allErrors.reduce((s, p) => s + p.errors.length, 0)}`);

  if (allErrors.length > 0) {
    console.log(`\n=== Error Details ===`);
    allErrors.forEach((p, i) => {
      console.log(`\n[${i+1}] ${p.subject}/${p.key} (${p.title}):`);
      p.errors.forEach((e, j) => {
        console.log(`  ${j+1}. ${e.type}: ${e.error || e.text}`);
        console.log(`     Context: ${e.context}`);
      });
    });
  }

  await browser.close();
  process.exit(allErrors.length > 0 ? 1 : 0);
}

main().catch(e => { console.error(e); process.exit(1); });
