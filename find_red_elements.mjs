// find_red_elements.mjs - Find the exact location of red \( \) elements
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

  const redInfo = await page.evaluate(() => {
    const results = [];
    const allElements = document.querySelectorAll('*');
    for (const el of allElements) {
      if (el.closest('script, style, noscript')) continue;
      const style = window.getComputedStyle(el);
      const color = style.color;
      if (color) {
        const m = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
        if (m) {
          const r = parseInt(m[1]), g = parseInt(m[2]), b = parseInt(m[3]);
          if (r > 180 && g < 80 && b < 80) {
            // Get parent chain
            const parents = [];
            let p = el.parentElement;
            while (p && parents.length < 8) {
              parents.push({
                tag: p.tagName,
                id: p.id || '',
                cls: (p.className || '').toString().slice(0, 80),
                text: (p.textContent || '').trim().slice(0, 60),
              });
              p = p.parentElement;
            }
            results.push({
              tag: el.tagName,
              text: (el.textContent || '').slice(0, 100),
              color: color,
              html: el.outerHTML.slice(0, 300),
              parentChain: parents,
            });
          }
        }
      }
    }
    return results;
  });

  console.log(`Found ${redInfo.length} red elements:\n`);
  redInfo.forEach((r, i) => {
    console.log(`--- Red Element ${i+1} ---`);
    console.log(`Tag: ${r.tag}`);
    console.log(`Text: "${r.text}"`);
    console.log(`HTML: ${r.html}`);
    console.log(`Parent chain:`);
    r.parentChain.forEach((p, j) => {
      console.log(`  ${j}: <${p.tag} id="${p.id}" class="${p.cls}"> text="${p.text}"`);
    });
    console.log('');
  });

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
