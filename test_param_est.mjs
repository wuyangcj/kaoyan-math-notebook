// test_param_est.mjs - Test _mathToLatex on 参数估计
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(2000);

  const result = await page.evaluate(() => {
    const detail = knowledgeBaseDetail['gailv']['参数估计'];
    let html = _mathToLatex(detail.content);
    html = wrapMathInHtmlText(html);
    html = html.replace(/<code>([\s\S]*?)<\/code>/g, (m, code) => {
        let c = code.trim();
        if (c.startsWith('\\(') && c.endsWith('\\)')) return '<code>' + c + '</code>';
        if (c.includes('\\(') || c.includes('\\)')) {
            if (!c.includes('\\begin{')) c = c.replace(/&/g, '\\&');
            return '<code>' + c + '</code>';
        }
        if (!c.includes('\\begin{')) c = c.replace(/&/g, '\\&');
        return '<code>\\(' + c + '\\)</code>';
    });

    // Search for double exponent patterns in the final HTML
    const patterns = [
      { regex: /\^\^[0-9a-zA-Z{]/g, name: 'double ^^' },
      { regex: /\^\{[^\}]+\}\^[0-9a-zA-Z{]/g, name: '^{...}^...' },
      { regex: /\^[0-9a-zA-Z]\^[0-9a-zA-Z{]/g, name: '^x^x' },
    ];

    const findings = [];
    for (const { regex, name } of patterns) {
      regex.lastIndex = 0;
      let m;
      while ((m = regex.exec(html)) !== null) {
        const start = Math.max(0, m.index - 30);
        const end = Math.min(html.length, m.index + m[0].length + 30);
        findings.push({ name, match: m[0], context: html.substring(start, end) });
      }
    }

    return { findings, contentLength: html.length };
  });

  console.log(`Content length: ${result.contentLength}`);
  console.log(`Double exponent patterns found: ${result.findings.length}`);
  for (const f of result.findings) {
    console.log(`\n  ${f.name}: ${f.match}`);
    console.log(`  Context: ${f.context}`);
  }

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
