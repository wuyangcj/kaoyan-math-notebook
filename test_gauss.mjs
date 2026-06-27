// test_gauss.mjs - Test _mathToLatex on Gauss formula
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(2000);

  // Test _mathToLatex on the Gauss formula
  const result = await page.evaluate(() => {
    const input = '<code>\\(\\oiint_{\\sum} P dydz + Q dzdx + R dxdy = \\iiint_{\\Omega}(\\frac{\\partial P}{\\partial x} + \\frac{\\partial Q}{\\partial y} + \\frac{\\partial R}{\\partial z}) dv\\)</code>';
    const afterMath = _mathToLatex(input);
    const afterWrap = wrapMathInHtmlText(afterMath);

    // Also get the actual detail content
    const detail = knowledgeBaseDetail['gaoshu']['曲线曲面积分'];
    const realInput = detail.content;
    // Find the Gauss formula part
    const gaussIdx = realInput.indexOf('oiint');
    const gaussPart = realInput.substring(gaussIdx - 20, gaussIdx + 200);

    const realAfterMath = _mathToLatex(gaussPart);

    return {
      input,
      afterMath,
      afterWrap,
      gaussPart,
      realAfterMath
    };
  });

  console.log('=== Input ===');
  console.log(result.input);
  console.log('\n=== After _mathToLatex ===');
  console.log(result.afterMath);
  console.log('\n=== After wrapMathInHtmlText ===');
  console.log(result.afterWrap);
  console.log('\n=== Real Gauss part from source ===');
  console.log(result.gaussPart);
  console.log('\n=== Real after _mathToLatex ===');
  console.log(result.realAfterMath);

  await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
