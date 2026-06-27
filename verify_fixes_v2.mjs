// verify_fixes_v2.mjs - More accurate verification
// Fixes: exclude <script>/<style> from text, wait for AI streaming, take screenshots

import { chromium } from 'playwright';
import { pathToFileURL } from 'url';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;
const SCREENSHOT_DIR = '/Users/wuyangcj/trae/回甘demo/screenshots';

import fs from 'fs';
if (!fs.existsSync(SCREENSHOT_DIR)) fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

const results = { passed: [], failed: [], warnings: [] };

function log(msg) { console.log(msg); }

async function checkForErrors(page, label, selector) {
  const errorInfo = await page.evaluate((sel) => {
    // Clone the root to safely remove script/style without affecting the page
    const root = sel ? document.querySelector(sel) : document.body;
    if (!root) return { error: 'selector not found' };
    const clone = root.cloneNode(true);
    // Remove script, style, noscript, svg content from clone
    clone.querySelectorAll('script, style, noscript').forEach(el => el.remove());

    const issues = [];
    // 1. Red colored text (MathJax errors)
    const allElements = root.querySelectorAll('*');
    let redCount = 0;
    const redSamples = [];
    for (const el of allElements) {
      // Skip elements inside script/style
      if (el.closest('script, style, noscript')) continue;
      const style = window.getComputedStyle(el);
      const color = style.color;
      if (color) {
        const m = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
        if (m) {
          const r = parseInt(m[1]), g = parseInt(m[2]), b = parseInt(m[3]);
          if (r > 180 && g < 80 && b < 80) {
            redCount++;
            if (redSamples.length < 8) {
              redSamples.push({
                tag: el.tagName,
                text: (el.textContent || '').slice(0, 120),
                color: color,
                html: el.outerHTML.slice(0, 200),
              });
            }
          }
        }
      }
    }

    // 2. Use clone's textContent (without script/style)
    const text = clone.textContent || '';
    const rawLatexMatches = [];
    // Only look for raw LaTeX that's NOT inside mjx- containers (visible text)
    // Check for literal \frac, \sum etc in the visible text (not in MathJax output)
    const rawLatexPattern = /\\(frac|sum|int|lim|alpha|beta|gamma|delta|sqrt|infty|cdot|times|partial|nabla|leq|geq|neq|to|sin|cos|tan|log|ln|pi|sigma|mu|lambda|phi|theta|omega|Delta|Sigma|Omega|begin|end|arcsin|arccos|arctan|left|right|displaystyle|mathrm|bar|vec|hat)\b/g;
    let lm;
    while ((lm = rawLatexPattern.exec(text)) !== null) {
      const context = text.slice(Math.max(0, lm.index - 30), lm.index + 50);
      rawLatexMatches.push(context.replace(/\n/g, '\\n'));
      if (rawLatexMatches.length >= 10) break;
    }

    // 3. Literal \n in visible text
    const literalN = (text.match(/\\n/g) || []).length;

    // 4. MathJax error strings
    const mathErrorText = [];
    if (text.includes('Math input error')) mathErrorText.push('Math input error');
    if (text.includes('Double exponent')) mathErrorText.push('Double exponent');
    if (text.includes('Undefined control sequence')) mathErrorText.push('Undefined control sequence');

    return {
      redCount,
      redSamples,
      rawLatexCount: rawLatexMatches.length,
      rawLatexSamples: rawLatexMatches,
      literalNCount: literalN,
      mathErrorText,
      textLength: text.length,
    };
  }, selector);

  const issues = [];
  if (errorInfo.error) {
    issues.push(`Selector not found: ${selector}`);
  } else {
    if (errorInfo.redCount > 0) {
      issues.push(`Red text elements: ${errorInfo.redCount}`);
      issues.push(`Red samples: ${JSON.stringify(errorInfo.redSamples, null, 0)}`);
    }
    if (errorInfo.rawLatexCount > 0) {
      issues.push(`Raw LaTeX leakage: ${errorInfo.rawLatexCount} occurrences`);
      issues.push(`Samples: ${JSON.stringify(errorInfo.rawLatexSamples)}`);
    }
    if (errorInfo.literalNCount > 0) {
      issues.push(`Literal \\n in visible text: ${errorInfo.literalNCount}`);
    }
    if (errorInfo.mathErrorText.length > 0) {
      issues.push(`MathJax error strings: ${errorInfo.mathErrorText.join(', ')}`);
    }
  }

  if (issues.length === 0) {
    results.passed.push(label);
    log(`  ✅ ${label}: PASS (text length: ${errorInfo.textLength || 'N/A'})`);
  } else {
    results.failed.push({ label, issues });
    log(`  ❌ ${label}: FAIL`);
    for (const issue of issues) log(`     - ${issue}`);
  }
  return issues.length === 0;
}

async function main() {
  log('Launching browser...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const consoleErrors = [];
  const page = await context.newPage();
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text().slice(0, 300));
  });
  page.on('pageerror', (err) => {
    consoleErrors.push(`PAGE ERROR: ${err.message.slice(0, 300)}`);
  });

  log(`Loading ${fileUrl} ...`);
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
  log('Waiting for MathJax...');
  await page.waitForFunction(() => window.MathJax && window.MathJax.typesetPromise, { timeout: 30000 });
  await page.waitForTimeout(3000);

  // ===== Test 1: Knowledge Base =====
  log('\n=== Test 1: Knowledge Base ===');

  // Click 知识库 nav
  await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('.nav-item'));
    for (const el of els) {
      if ((el.textContent || '').trim() === '知识库') { el.click(); return; }
    }
  });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: `${SCREENSHOT_DIR}/01-kb-overview.png`, fullPage: false });

  // Check overview page
  await checkForErrors(page, 'KB-overview', '#kbResults, .kb-results');

  // Click 高等数学 chapter to filter
  await page.evaluate(() => {
    const items = document.querySelectorAll('.kb-chapter-header');
    for (const item of items) {
      if ((item.textContent || '').includes('函数') || (item.textContent || '').includes('极限')) {
        item.click();
        return;
      }
    }
  });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: `${SCREENSHOT_DIR}/02-kb-gaoshu.png`, fullPage: false });
  await checkForErrors(page, 'KB-高数-cards', '#kbResults, .kb-results');

  // Click first KB card to open detail
  const openedDetail = await page.evaluate(() => {
    const card = document.querySelector('.kb-card');
    if (card) { card.click(); return true; }
    return false;
  });
  log(`  Opened detail: ${openedDetail}`);
  await page.waitForTimeout(3000);
  await page.screenshot({ path: `${SCREENSHOT_DIR}/03-kb-detail.png`, fullPage: false });
  await checkForErrors(page, 'KB-detail', '#modalBody, .modal-body, .kb-detail-content, .modal');

  // Close modal
  await page.keyboard.press('Escape').catch(() => {});
  await page.waitForTimeout(500);

  // ===== Test 2: AI Assistant =====
  log('\n=== Test 2: AI Assistant ===');

  // Navigate to AI assistant
  await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('.nav-item'));
    for (const el of els) {
      if ((el.textContent || '').trim().includes('AI')) { el.click(); return; }
    }
  });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${SCREENSHOT_DIR}/04-ai-welcome.png`, fullPage: false });

  // Click demo chip "请讲解极限的求法"
  const clickedDemo = await page.evaluate(() => {
    const chips = document.querySelectorAll('.ai-suggestion-chip');
    for (const chip of chips) {
      if ((chip.textContent || '').includes('极限')) { chip.click(); return chip.textContent; }
    }
    return false;
  });
  log(`  Clicked demo: ${clickedDemo}`);

  // Wait for streaming to complete (response is ~350 chars, 24ms/char = ~8.5s, plus 600-1000ms delay)
  log('  Waiting for AI streaming to complete (12 seconds)...');
  await page.waitForTimeout(12000);
  await page.screenshot({ path: `${SCREENSHOT_DIR}/05-ai-response.png`, fullPage: false });
  await checkForErrors(page, 'AI-response', '#aiChatMessages, .ai-messages, .chat-messages');

  // ===== Test 3: Question Bank (刷题) =====
  log('\n=== Test 3: Question Bank ===');
  await page.evaluate(() => {
    const els = Array.from(document.querySelectorAll('.nav-item'));
    for (const el of els) {
      if ((el.textContent || '').trim() === '开始刷题') { el.click(); return; }
    }
  });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: `${SCREENSHOT_DIR}/06-quiz-config.png`, fullPage: false });
  await checkForErrors(page, 'Quiz-config', '#quizConfig, .quiz-config, .main-content');

  // ===== Console errors =====
  log('\n=== Console Errors ===');
  const mathConsoleErrors = consoleErrors.filter(e =>
    e.includes('MathJax') || e.includes('math') || e.includes('LaTeX') || e.includes('tex') || e.includes('Undefined')
  );
  if (mathConsoleErrors.length > 0) {
    log(`MathJax-related console errors: ${mathConsoleErrors.length}`);
    mathConsoleErrors.slice(0, 20).forEach((e, i) => log(`  [${i}] ${e}`));
    results.warnings.push(`${mathConsoleErrors.length} MathJax console errors`);
  } else {
    log('No MathJax-related console errors ✅');
  }
  if (consoleErrors.length > 0) {
    log(`\nTotal console errors: ${consoleErrors.length}`);
    consoleErrors.slice(0, 10).forEach((e, i) => log(`  [${i}] ${e}`));
  }

  // ===== Summary =====
  log('\n========== SUMMARY ==========');
  log(`Passed: ${results.passed.length}`);
  results.passed.forEach(p => log(`  ✅ ${p}`));
  log(`Failed: ${results.failed.length}`);
  results.failed.forEach(f => {
    log(`  ❌ ${f.label}`);
    f.issues.forEach(i => log(`     - ${i}`));
  });
  if (results.warnings.length > 0) {
    log(`Warnings: ${results.warnings.length}`);
    results.warnings.forEach(w => log(`  ⚠️  ${w}`));
  }

  log(`\nScreenshots saved to: ${SCREENSHOT_DIR}/`);
  await browser.close();
  process.exit(results.failed.length > 0 ? 1 : 0);
}

main().catch(e => { console.error('Fatal:', e); process.exit(1); });
