// check_html.mjs - Check rendered HTML for errors
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

  // Click 知识库
  await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('.nav-item'));
    for (const el of els) {
      if ((el.textContent || '').trim() === '知识库') { el.click(); return; }
    }
  });
  await page.waitForTimeout(2000);

  // Check card 59 (大数定律) - error 1
  const cards = await page.evaluate(() => document.querySelectorAll('.kb-card').length);
  console.log(`Total cards: ${cards}`);

  // Click card 59 (大数定律)
  await page.evaluate(() => {
    const c = document.querySelectorAll('.kb-card');
    if (c[59]) c[59].click();
  });
  await page.waitForTimeout(3000);

  // Get HTML of the first error
  const errorInfo = await page.evaluate(() => {
    const modal = document.querySelector('#modalBody') || document.querySelector('.modal-body');
    if (!modal) return { error: 'no modal' };

    // Find red mtext elements
    const redMtexts = modal.querySelectorAll('[data-mml-node="mtext"][fill="red"], [data-mml-node="mtext"][mathcolor="red"]');
    const results = [];
    redMtexts.forEach((el, i) => {
      if (i >= 2) return; // only first 2
      const container = el.closest('mjx-container');
      const parentEl = container ? container.parentElement : null;
      results.push({
        text: el.textContent,
        parentTag: parentEl ? parentEl.tagName : 'none',
        parentHTML: parentEl ? parentEl.outerHTML.substring(0, 500) : 'none',
        grandparentHTML: parentEl && parentEl.parentElement ? parentEl.parentElement.outerHTML.substring(0, 300) : 'none',
      });
    });
    return results;
  });

  console.log('\n=== 大数定律 card errors ===');
  console.log(JSON.stringify(errorInfo, null, 2));

  // Also check card 3 (洛必达法则)
  await page.keyboard.press('Escape');
  await page.waitForTimeout(500);
  await page.evaluate(() => {
    const c = document.querySelectorAll('.kb-card');
    if (c[3]) c[3].click();
  });
  await page.waitForTimeout(3000);

  const lhopitalInfo = await page.evaluate(() => {
    const modal = document.querySelector('#modalBody') || document.querySelector('.modal-body');
    if (!modal) return { error: 'no modal' };

    const redMtexts = modal.querySelectorAll('[data-mml-node="mtext"][fill="red"], [data-mml-node="mtext"][mathcolor="red"]');
    const results = [];
    redMtexts.forEach((el, i) => {
      if (i >= 2) return;
      const container = el.closest('mjx-container');
      const parentEl = container ? container.parentElement : null;
      results.push({
        text: el.textContent,
        parentTag: parentEl ? parentEl.tagName : 'none',
        parentHTML: parentEl ? parentEl.outerHTML.substring(0, 500) : 'none',
      });
    });
    return results;
  });

  console.log('\n=== 洛必达法则 card errors ===');
  console.log(JSON.stringify(lhopitalInfo, null, 2));

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
