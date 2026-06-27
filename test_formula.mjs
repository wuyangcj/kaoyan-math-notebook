// test_formula.mjs - Test the 洛必达法则 formula rendering
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

  // Test the formula
  const result = await page.evaluate(() => {
    const formula = "lim \\frac{f(x)}{g(x)} = lim \\frac{f'(x)}{g'(x)}（\\frac{0}{0} 或 \\frac{∞}{∞} 型）";

    // Check what character the ' is
    const primeChar = formula.indexOf("'") >= 0 ? {
      index: formula.indexOf("'"),
      code: formula.charCodeAt(formula.indexOf("'")),
      hex: 'U+' + formula.charCodeAt(formula.indexOf("'")).toString(16).toUpperCase().padStart(4, '0'),
    } : null;

    // Run through formatMath
    const formatted = formatMath(formula);

    // Run through _mathToLatex
    const mathLatex = _mathToLatex(formula);

    return {
      original: formula,
      primeChar,
      formatted,
      mathLatex,
    };
  });

  console.log('=== Formula Test ===');
  console.log('Original:', result.original);
  console.log('Prime char:', JSON.stringify(result.primeChar));
  console.log('');
  console.log('_mathToLatex output:', result.mathLatex);
  console.log('');
  console.log('formatMath output:', result.formatted);
  console.log('');

  // Now render it in a div and check
  const renderResult = await page.evaluate(async () => {
    const formula = "lim \\frac{f(x)}{g(x)} = lim \\frac{f'(x)}{g'(x)}（\\frac{0}{0} 或 \\frac{∞}{∞} 型）";
    const formatted = formatMath(formula);

    const div = document.createElement('div');
    div.innerHTML = formatted;
    div.style.position = 'absolute';
    div.style.top = '0';
    div.style.left = '0';
    div.style.background = 'white';
    div.style.padding = '20px';
    div.style.zIndex = '9999';
    document.body.appendChild(div);

    await window.MathJax.typesetPromise([div]);

    // Check for red elements
    const redElements = [];
    div.querySelectorAll('*').forEach(el => {
      const style = window.getComputedStyle(el);
      const color = style.color;
      if (color) {
        const m = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
        if (m) {
          const r = parseInt(m[1]), g = parseInt(m[2]), b = parseInt(m[3]);
          if (r > 180 && g < 80 && b < 80) {
            redElements.push({
              tag: el.tagName,
              text: (el.textContent || '').slice(0, 50),
              html: el.outerHTML.slice(0, 200),
            });
          }
        }
      }
    });

    return {
      innerHTML: div.innerHTML,
      textContent: div.textContent.slice(0, 200),
      redElements,
    };
  });

  console.log('=== Rendered ===');
  console.log('innerHTML:', renderResult.innerHTML.slice(0, 500));
  console.log('textContent:', renderResult.textContent);
  console.log('Red elements:', renderResult.redElements.length);
  renderResult.redElements.forEach((r, i) => {
    console.log(`  [${i}] ${r.tag}: "${r.text}" html=${r.html}`);
  });

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
