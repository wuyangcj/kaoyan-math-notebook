// check_math.mjs - Check _mathToLatex output for problematic cards
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

  // Test _mathToLatex on problematic patterns
  const results = await page.evaluate(() => {
    const tests = [
      // 大数定律 - 没有 \(...\) 的 code 块
      '<code>P(|X - \\mu | < \\varepsilon ) \\ge 1 - \\frac{\\sigma^{2}}{\\varepsilon^{2}}</code>',
      '<code>\\lim_{n\\to\\infty} P(|(\\frac{1}{n})\\sum X_{i} - (\\frac{1}{n})\\sum \\mu_{i}| < \\varepsilon ) = 1</code>',
      // 洛必达法则 - 型字在定界符内
      '<code>\\(\\frac{0}{0} 型\\)</code>',
      '<code>\\(\\frac{\\infty}{\\infty} 型\\)</code>',
      '<code>\\(0\\cdot \\infty 型\\)</code>',
      // 常数项级数
      '<code>\\(0\\(l=0 \\Rightarrow \\sum v_{n}\\)收敛</code>',
      // 极值与最值
      '<code>f\'\'(x0) < 0</code>',
      // 三重积分
      '<code>\\iiint_\\Omega dv</code>',
    ];

    return tests.map(t => {
      const afterMath = _mathToLatex(t);
      const afterWrap = wrapMathInHtmlText(afterMath);
      // Apply the code replacement from showKnowledgeDetail
      let final = afterWrap.replace(/<code>([\s\S]*?)<\/code>/g, (m, code) => {
        let c = code.trim();
        if (c.startsWith('\\(') && c.endsWith('\\)')) {
          return '<code>' + c + '</code>';
        }
        if (!c.includes('\\begin{')) {
          c = c.replace(/&/g, '\\&');
        }
        return '<code>\\(' + c + '\\)</code>';
      });
      return { input: t, afterMath, afterWrap, final };
    });
  });

  for (const r of results) {
    console.log('=== TEST ===');
    console.log('Input:', r.input);
    console.log('After _mathToLatex:', r.afterMath);
    console.log('After wrapMath:', r.afterWrap);
    console.log('Final:', r.final);
    console.log('');
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
