// find_all_errors_v3.mjs - Render KB content by calling showKnowledgeDetail
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

  // Get all KB items by clicking 知识库 and reading cards
  await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('.nav-item'));
    for (const el of els) {
      if ((el.textContent || '').trim() === '知识库') { el.click(); return; }
    }
  });
  await page.waitForTimeout(2000);

  const kbCards = await page.evaluate(() => {
    const cards = document.querySelectorAll('.kb-card');
    return Array.from(cards).map((c, i) => ({
      index: i,
      title: (c.querySelector('.kb-card-title, h3, h4, strong')?.textContent || c.textContent || '').trim().split('\n')[0].trim(),
    }));
  });

  console.log(`Found ${kbCards.length} KB cards`);

  const allErrors = [];

  for (let i = 0; i < kbCards.length; i++) {
    // Click card
    await page.evaluate((idx) => {
      const cards = document.querySelectorAll('.kb-card');
      if (cards[idx]) cards[idx].click();
    }, i);
    await page.waitForTimeout(1500);
    await page.waitForFunction(() => window.MathJax && window.MathJax.typesetPromise, { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(2000);

    // Check modal for errors
    const errors = await page.evaluate(() => {
      const modal = document.querySelector('#modalBody') || document.querySelector('.modal-body') || document.querySelector('.kb-detail-content');
      if (!modal) return [];

      const results = [];

      // 1. merror (yellow background red text)
      const merrors = modal.querySelectorAll('[data-mml-node="merror"]');
      merrors.forEach(el => {
        const errorText = el.getAttribute('data-mjx-error') || '';
        const container = el.closest('mjx-container');
        const parentEl = container ? container.parentElement : null;
        let context = '';
        if (parentEl) {
          // Get the surrounding text from the parent's parent for more context
          let p = parentEl.parentElement;
          while (p && p !== modal) {
            const t = (p.textContent || '').trim();
            if (t.length > 5 && t.length < 200) { context = t; break; }
            p = p.parentElement;
          }
          if (!context) context = (parentEl.textContent || '').slice(0, 120);
        }
        results.push({ type: 'merror', error: errorText, context });
      });

      // 2. Red mtext
      const redMtexts = modal.querySelectorAll('[data-mml-node="mtext"][fill="red"], [data-mml-node="mtext"][mathcolor="red"]');
      redMtexts.forEach(el => {
        const container = el.closest('mjx-container');
        const parentEl = container ? container.parentElement : null;
        const text = el.textContent || '';
        let context = '';
        if (parentEl) {
          let p = parentEl.parentElement;
          while (p && p !== modal) {
            const t = (p.textContent || '').trim();
            if (t.length > 5 && t.length < 200) { context = t; break; }
            p = p.parentElement;
          }
          if (!context) context = (parentEl.textContent || '').slice(0, 120);
        }
        results.push({ type: 'red-mtext', text, context });
      });

      return results;
    });

    if (errors.length > 0) {
      console.log(`\n❌ [${i}] ${kbCards[i].title}: ${errors.length} errors`);
      errors.forEach((e, j) => {
        console.log(`   ${j+1}. ${e.type}: ${e.error || e.text}`);
        console.log(`      Context: ${e.context}`);
      });
      allErrors.push({ index: i, title: kbCards[i].title, errors });
    } else {
      console.log(`✅ [${i}] ${kbCards[i].title}`);
    }

    // Close modal
    await page.keyboard.press('Escape').catch(() => {});
    await page.waitForTimeout(400);
  }

  console.log(`\n========== SUMMARY ==========`);
  console.log(`Total cards: ${kbCards.length}`);
  console.log(`Cards with errors: ${allErrors.length}`);
  console.log(`Total errors: ${allErrors.reduce((s, p) => s + p.errors.length, 0)}`);

  await browser.close();
  process.exit(allErrors.length > 0 ? 1 : 0);
}

main().catch(e => { console.error(e); process.exit(1); });
