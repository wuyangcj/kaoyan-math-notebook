// verify_fixes.mjs - Verify LaTeX rendering fixes using Playwright
// Checks: AI assistant demo response, Knowledge base (高数/概率论/线代) detail pages
// Looks for: red error text (MathJax errors), unrendered LaTeX source, \\n literal leakage

import { chromium } from 'playwright';
import { pathToFileURL } from 'url';
import path from 'path';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

const results = {
  passed: [],
  failed: [],
  warnings: [],
};

function log(msg) {
  console.log(msg);
}

async function checkForErrors(page, label, selector) {
  // Check for MathJax error text (red color)
  const errorInfo = await page.evaluate((sel) => {
    const root = sel ? document.querySelector(sel) : document.body;
    if (!root) return { error: 'selector not found' };
    const issues = [];
    // 1. Red colored text (MathJax errors render red)
    const allElements = root.querySelectorAll('*');
    let redCount = 0;
    const redSamples = [];
    for (const el of allElements) {
      const style = window.getComputedStyle(el);
      const color = style.color;
      // Check for red-ish colors (rgb(255,0,0) or similar)
      if (color) {
        const m = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
        if (m) {
          const r = parseInt(m[1]), g = parseInt(m[2]), b = parseInt(m[3]);
          // Red dominant and high
          if (r > 180 && g < 80 && b < 80) {
            redCount++;
            if (redSamples.length < 5) {
              redSamples.push({
                tag: el.tagName,
                text: (el.textContent || '').slice(0, 100),
                color: color,
              });
            }
          }
        }
      }
    }
    // 2. Unrendered LaTeX source (literal \frac, \sum, etc. visible as text without math delimiters)
    const text = root.textContent || '';
    // Look for literal backslash-letter sequences that look like unrendered LaTeX
    // MathJax renders \(...\) and \[...\]. If we see raw \frac{ outside of mjx containers, it's a problem
    const rawLatexMatches = [];
    const rawLatexPattern = /\\(frac|sum|int|lim|alpha|beta|gamma|delta|sqrt|infty|cdot|times|partial|nabla|leq|geq|neq|to|sin|cos|tan|log|ln|pi|sigma|mu|lambda|phi|theta|omega|Delta|Sigma|Omega|begin|end|arcsin|arccos|arctan|left|right|displaystyle)\b/g;
    let lm;
    while ((lm = rawLatexPattern.exec(text)) !== null) {
      // Check if this is inside a MathJax container or script
      // We'll check by looking at surrounding context
      const context = text.slice(Math.max(0, lm.index - 20), lm.index + 40);
      rawLatexMatches.push(context);
      if (rawLatexMatches.length >= 10) break;
    }
    // 3. Literal \n appearing as text (the bug we fixed)
    const literalN = (text.match(/\\n/g) || []).length;

    // 4. "Math input error" or "Double exponent" strings
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
      issues.push(`Red samples: ${JSON.stringify(errorInfo.redSamples)}`);
    }
    if (errorInfo.rawLatexCount > 0) {
      issues.push(`Raw LaTeX leakage: ${errorInfo.rawLatexCount} occurrences`);
      issues.push(`Samples: ${JSON.stringify(errorInfo.rawLatexSamples)}`);
    }
    if (errorInfo.literalNCount > 0) {
      issues.push(`Literal \\n in text: ${errorInfo.literalNCount}`);
    }
    if (errorInfo.mathErrorText.length > 0) {
      issues.push(`MathJax error strings: ${errorInfo.mathErrorText.join(', ')}`);
    }
  }

  if (issues.length === 0) {
    results.passed.push(label);
    log(`✅ ${label}: PASS (text length: ${errorInfo.textLength || 'N/A'})`);
  } else {
    results.failed.push({ label, issues });
    log(`❌ ${label}: FAIL`);
    for (const issue of issues) log(`   - ${issue}`);
  }
  return issues.length === 0;
}

async function main() {
  log('Launching browser...');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 900 },
  });
  // Capture console errors
  const consoleErrors = [];
  const page = await context.newPage();
  page.on('console', (msg) => {
    if (msg.type() === 'error') {
      consoleErrors.push(msg.text().slice(0, 200));
    }
  });
  page.on('pageerror', (err) => {
    consoleErrors.push(`PAGE ERROR: ${err.message.slice(0, 200)}`);
  });

  log(`Loading ${fileUrl} ...`);
  await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
  // Wait for MathJax to initialize
  log('Waiting for MathJax...');
  await page.waitForFunction(() => window.MathJax && window.MathJax.typesetPromise, { timeout: 30000 });
  await page.waitForTimeout(3000);

  // ===== Test 1: Knowledge Base - 高数 =====
  log('\n=== Test 1: Knowledge Base - 高数 ===');
  try {
    // Find and click 高数 knowledge base tab/button
    // First, let's see what's on the page
    const navInfo = await page.evaluate(() => {
      const buttons = Array.from(document.querySelectorAll('button, .nav-item, .tab, [data-tab], .kb-item, .knowledge-item'));
      return buttons.slice(0, 30).map(b => ({
        tag: b.tagName,
        text: (b.textContent || '').trim().slice(0, 40),
        cls: b.className.slice(0, 60),
        id: b.id,
      }));
    });
    log(`Found ${navInfo.length} clickable elements (showing first 30)`);
    navInfo.forEach((n, i) => log(`  [${i}] ${n.tag} .${n.cls} #${n.id} = "${n.text}"`));

    // Try to navigate to knowledge base
    // Look for knowledge base related elements
    const kbNav = await page.evaluate(() => {
      const els = Array.from(document.querySelectorAll('*'));
      const matches = els.filter(el => {
        const t = (el.textContent || '').trim();
        return t.length < 20 && (t.includes('知识库') || t.includes('高数') || t.includes('概率') || t.includes('线代'));
      });
      return matches.slice(0, 10).map(el => ({
        tag: el.tagName,
        text: (el.textContent || '').trim().slice(0, 40),
        cls: el.className.toString().slice(0, 60),
        id: el.id,
      }));
    });
    log(`\nKnowledge-related elements:`);
    kbNav.forEach((n, i) => log(`  [${i}] ${n.tag} .${n.cls} #${n.id} = "${n.text}"`));

    // Click on 知识库 nav
    const clicked = await page.evaluate(() => {
      const els = Array.from(document.querySelectorAll('*'));
      for (const el of els) {
        if ((el.textContent || '').trim() === '知识库') {
          el.click();
          return true;
        }
      }
      return false;
    });
    log(`Clicked 知识库: ${clicked}`);
    await page.waitForTimeout(1500);

    // Now look for 高数 and click it
    const clickedGao = await page.evaluate(() => {
      const els = Array.from(document.querySelectorAll('*'));
      for (const el of els) {
        if ((el.textContent || '').trim() === '高数') {
          el.click();
          return true;
        }
      }
      return false;
    });
    log(`Clicked 高数: ${clickedGao}`);
    await page.waitForTimeout(2000);

    // Wait for MathJax to render
    await page.waitForFunction(() => window.MathJax && window.MathJax.typesetPromise, { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(3000);

    // Check for errors in the visible content
    await checkForErrors(page, 'KB-高数-list', null);

    // Try to open a detail - click on first knowledge item
    const openedDetail = await page.evaluate(() => {
      // Look for clickable items in the knowledge base area
      const items = document.querySelectorAll('.kb-item, .knowledge-item, .kb-card, [data-knowledge], .topic-item');
      if (items.length > 0) {
        items[0].click();
        return items.length;
      }
      return 0;
    });
    log(`Opened detail: ${openedDetail} items found`);
    await page.waitForTimeout(2000);
    await page.waitForFunction(() => window.MathJax && window.MathJax.typesetPromise, { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(3000);

    // Check detail modal
    await checkForErrors(page, 'KB-高数-detail', '#modalBody, .modal-body, .kb-detail-content, .modal');

  } catch (e) {
    log(`Error in 高数 test: ${e.message}`);
    results.failed.push({ label: 'KB-高数', issues: [e.message] });
  }

  // ===== Test 2: AI Assistant =====
  log('\n=== Test 2: AI Assistant ===');
  try {
    // Close any modal first
    await page.keyboard.press('Escape').catch(() => {});
    await page.waitForTimeout(500);

    // Find AI assistant
    const clickedAI = await page.evaluate(() => {
      const els = Array.from(document.querySelectorAll('*'));
      for (const el of els) {
        const t = (el.textContent || '').trim();
        if (t === 'AI助手' || t === 'AI 助手' || t.includes('AI助手')) {
          el.click();
          return t;
        }
      }
      return false;
    });
    log(`Clicked AI助手: ${clickedAI}`);
    await page.waitForTimeout(1500);

    // Look for demo/example buttons or input area
    const aiInfo = await page.evaluate(() => {
      const els = Array.from(document.querySelectorAll('button, .demo-btn, .example-btn, .prompt-btn, [data-example]'));
      return els.slice(0, 20).map(b => ({
        tag: b.tagName,
        text: (b.textContent || '').trim().slice(0, 60),
        cls: b.className.slice(0, 60),
      }));
    });
    log(`AI assistant buttons:`);
    aiInfo.forEach((n, i) => log(`  [${i}] ${n.tag} .${n.cls} = "${n.text}"`));

    // Try clicking a demo/example button
    const clickedDemo = await page.evaluate(() => {
      const btns = Array.from(document.querySelectorAll('button, .demo-btn, .example-btn'));
      for (const b of btns) {
        const t = (b.textContent || '').trim();
        if (t.includes('演示') || t.includes('示例') || t.includes('demo') || t.includes('例题') || t.includes('极限') || t.includes('导数')) {
          b.click();
          return t;
        }
      }
      return false;
    });
    log(`Clicked demo button: ${clickedDemo}`);
    await page.waitForTimeout(3000);
    await page.waitForFunction(() => window.MathJax && window.MathJax.typesetPromise, { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(3000);

    // Check AI response area
    await checkForErrors(page, 'AI-assistant-response', '#aiChatMessages, .ai-messages, .chat-messages, .ai-response, #aiPanel');

  } catch (e) {
    log(`Error in AI test: ${e.message}`);
    results.failed.push({ label: 'AI-assistant', issues: [e.message] });
  }

  // ===== Console errors summary =====
  log('\n=== Console Errors (MathJax related) ===');
  const mathConsoleErrors = consoleErrors.filter(e =>
    e.includes('MathJax') || e.includes('math') || e.includes('LaTeX') || e.includes('tex')
  );
  if (mathConsoleErrors.length > 0) {
    log(`Found ${mathConsoleErrors.length} MathJax-related console errors:`);
    mathConsoleErrors.slice(0, 15).forEach((e, i) => log(`  [${i}] ${e}`));
    results.warnings.push(`${mathConsoleErrors.length} MathJax console errors`);
  } else {
    log('No MathJax-related console errors');
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

  await browser.close();
  process.exit(results.failed.length > 0 ? 1 : 0);
}

main().catch(e => {
  console.error('Fatal:', e);
  process.exit(1);
});
