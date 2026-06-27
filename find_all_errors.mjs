// find_all_errors.mjs - Find all MathJax errors with their context
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForFunction(() => window.MathJax && window.MathJax.typesetPromise, { timeout: 30000 });
  await page.waitForTimeout(3000);

  // Navigate to knowledge base
  await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('.nav-item'));
    for (const el of els) {
      if ((el.textContent || '').trim() === '知识库') { el.click(); return; }
    }
  });
  await page.waitForTimeout(2000);

  // Find all knowledge items and test each one
  const kbItems = await page.evaluate(() => {
    const cards = document.querySelectorAll('.kb-card');
    return Array.from(cards).map((c, i) => ({
      index: i,
      text: (c.textContent || '').trim().slice(0, 50),
    }));
  });

  console.log(`Found ${kbItems.length} KB cards`);
  kbItems.forEach(c => console.log(`  [${c.index}] ${c.text}`));

  const allErrors = [];

  // Click each card and check for errors
  for (let i = 0; i < Math.min(kbItems.length, 30); i++) {
    await page.evaluate((idx) => {
      const cards = document.querySelectorAll('.kb-card');
      if (cards[idx]) cards[idx].click();
    }, i);
    await page.waitForTimeout(2000);
    await page.waitForFunction(() => window.MathJax && window.MathJax.typesetPromise, { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(2000);

    const errors = await page.evaluate(() => {
      const modal = document.querySelector('#modalBody, .modal-body, .kb-detail-content, .modal');
      if (!modal) return { error: 'no modal' };
      const results = [];

      // Check for merror (MathJax errors with yellow background)
      const merrors = modal.querySelectorAll('mjx-container [data-mml-node="merror"]');
      merrors.forEach(el => {
        const errorText = el.getAttribute('data-mjx-error') || '';
        const container = el.closest('mjx-container');
        const parentEl = container ? container.parentElement : null;
        results.push({
          type: 'merror',
          error: errorText,
          context: parentEl ? (parentEl.textContent || '').slice(0, 100) : '',
          html: container ? container.outerHTML.slice(0, 200) : '',
        });
      });

      // Check for red mtext (literal \( \) etc.)
      const redMtexts = modal.querySelectorAll('mjx-container [data-mml-node="mtext"][fill="red"], mjx-container [data-mml-node="mtext"][mathcolor="red"]');
      redMtexts.forEach(el => {
        const container = el.closest('mjx-container');
        const parentEl = container ? container.parentElement : null;
        const text = el.textContent || '';
        results.push({
          type: 'red-mtext',
          text: text,
          context: parentEl ? (parentEl.textContent || '').slice(0, 100) : '',
          html: container ? container.outerHTML.slice(0, 200) : '',
        });
      });

      return results;
    });

    if (errors.length > 0) {
      console.log(`\n=== Card [${i}] "${kbItems[i].text}" - ${errors.length} errors ===`);
      errors.forEach((e, j) => {
        console.log(`  Error ${j+1}: type=${e.type}`);
        if (e.error) console.log(`    MathJax error: ${e.error}`);
        if (e.text) console.log(`    Red text: "${e.text}"`);
        if (e.context) console.log(`    Context: "${e.context}"`);
        allErrors.push({ card: i, cardName: kbItems[i].text, ...e });
      });
    }

    // Close modal
    await page.keyboard.press('Escape').catch(() => {});
    await page.waitForTimeout(500);
  }

  console.log(`\n\n========== TOTAL ERRORS FOUND: ${allErrors.length} ==========`);
  allErrors.forEach((e, i) => {
    console.log(`[${i+1}] Card "${e.cardName}": ${e.type} - ${e.error || e.text}`);
  });

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
