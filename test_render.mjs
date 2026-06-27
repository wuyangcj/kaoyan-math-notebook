// test_render.mjs - Test full rendering pipeline for 曲线曲面积分
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(2000);

  // Get the actual HTML that would be passed to MathJax
  const result = await page.evaluate(() => {
    const detail = knowledgeBaseDetail['gaoshu']['曲线曲面积分'];
    let html = _mathToLatex(detail.content);
    html = wrapMathInHtmlText(html);
    html = html.replace(/<code>([\s\S]*?)<\/code>/g, (m, code) => {
        let c = code.trim();
        if (c.startsWith('\\(') && c.endsWith('\\)')) {
            return '<code>' + c + '</code>';
        }
        if (c.includes('\\(') || c.includes('\\)')) {
            if (!c.includes('\\begin{')) {
                c = c.replace(/&/g, '\\&');
            }
            return '<code>' + c + '</code>';
        }
        if (!c.includes('\\begin{')) {
            c = c.replace(/&/g, '\\&');
        }
        return '<code>\\(' + c + '\\)</code>';
    });

    // Find the Gauss formula part
    const gaussIdx = html.indexOf('oiint');
    const gaussPart = html.substring(gaussIdx - 30, gaussIdx + 300);

    return { gaussPart };
  });

  console.log('=== HTML passed to MathJax (Gauss formula area) ===');
  console.log(result.gaussPart);

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
