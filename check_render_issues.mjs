// check_render_issues.mjs - 检查知识库和题库中的源码显示问题
import { chromium } from 'playwright';
import fs from 'fs';

const HTML_PATH = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const FILE_URL = 'file://' + HTML_PATH;

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();

    const consoleMsgs = [];
    page.on('console', msg => {
        if (msg.type() === 'error') consoleMsgs.push(`[console.error] ${msg.text()}`);
    });
    page.on('pageerror', err => consoleMsgs.push(`[pageerror] ${err.message}`));

    console.log('1. 打开页面...');
    await page.goto(FILE_URL, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // 直接通过JS设置localStorage绕过登录
    console.log('2. 设置测试用户...');
    await page.evaluate(() => {
        const u = 'testchk_' + Date.now();
        const users = JSON.parse(localStorage.getItem('zcb_users') || '[]');
        users.push({
            username: u, password: 'test123456', nickname: '测试用户',
            avatar: '🐱',
            stats: { total: 0, correct: 0, errors: [], customQuestions: [], exp: 0, streak: 0, lastDate: '' },
            createdAt: new Date().toISOString()
        });
        localStorage.setItem('zcb_users', JSON.stringify(users));
        localStorage.setItem('zcb_currentUser', u);
    });
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // 检查是否已进入主界面
    const isAuth = await page.isVisible('#authPage');
    if (isAuth) {
        console.log('   仍在登录页，尝试直接调用navigateTo...');
    }

    console.log('3. 检查知识库页面...');
    await page.evaluate(() => navigateTo('knowledge'));
    await page.waitForTimeout(3000);

    // 展开所有知识点详情
    const kbIssues = await page.evaluate(() => {
        const issues = [];
        const container = document.querySelector('#page-knowledge');
        if (!container) return [{ type: 'no_container' }];

        // 检查 MathJax 错误
        const merrors = container.querySelectorAll('mjx-error');
        for (const me of merrors) {
            issues.push({ type: 'mathjax_error', text: me.textContent.substring(0, 150) });
        }

        // 检查未渲染的 LaTeX 源码（不在 MathJax 容器内的）
        const patterns = [/\\frac\{/, /\\begin\{/, /\\sum_/, /\\int_/, /\\sqrt\{/, /\\lim_/, /\\mathrm\{/, /\\alpha/, /\\sigma/, /\\partial/];
        const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, null);
        while (walker.nextNode()) {
            const text = walker.currentNode.textContent;
            for (const p of patterns) {
                if (p.test(text)) {
                    let parent = walker.currentNode.parentElement;
                    let inMathJax = false;
                    while (parent) {
                        if (parent.tagName && parent.tagName.toLowerCase().startsWith('mjx-')) { inMathJax = true; break; }
                        parent = parent.parentElement;
                    }
                    if (!inMathJax) {
                        issues.push({
                            type: 'unrendered_latex',
                            pattern: p.source,
                            text: text.substring(0, 120).trim(),
                            tag: walker.currentNode.parentElement?.tagName,
                            cls: walker.currentNode.parentElement?.className?.substring(0, 50)
                        });
                        break; // 每个文本节点只报告一次
                    }
                }
            }
        }

        // 检查字面的 HTML 标签文本
        const htmlTagPattern = /<\/?(code|div|span|pre|p|br|img|table|td|tr|ul|li|strong|em|b|i)[\s>]/i;
        const walker2 = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, null);
        while (walker2.nextNode()) {
            if (htmlTagPattern.test(walker2.currentNode.textContent)) {
                issues.push({
                    type: 'literal_html_tag',
                    text: walker2.currentNode.textContent.substring(0, 120).trim()
                });
            }
        }

        return issues;
    });

    console.log(`   知识库问题: ${kbIssues.length} 个`);
    for (const issue of kbIssues.slice(0, 15)) {
        console.log(`   - [${issue.type}] ${issue.text || JSON.stringify(issue)}`);
    }

    // 截图知识库
    await page.screenshot({ path: '/Users/wuyangcj/trae/回甘demo/screenshots/kb_render_check.png' });

    console.log('\n4. 检查题库页面...');
    await page.evaluate(() => navigateTo('practice'));
    await page.waitForTimeout(1000);
    // 选择科目和题型
    await page.click('[data-subject="gaoshu"]').catch(() => {});
    await page.waitForTimeout(300);
    await page.click('[data-mathtype="shuyi"]').catch(() => {});
    await page.waitForTimeout(300);
    // 开始练习
    await page.click('button:has-text("开始"), button:has-text("练习"), button:has-text("刷题"), button:has-text("开始刷题")').catch(() => {});
    await page.waitForTimeout(3000);

    const practiceIssues = await page.evaluate(() => {
        const issues = [];
        const container = document.querySelector('#page-practice') || document.body;
        const merrors = container.querySelectorAll('mjx-error');
        for (const me of merrors) {
            issues.push({ type: 'mathjax_error', text: me.textContent.substring(0, 150) });
        }
        const patterns = [/\\frac\{/, /\\begin\{/, /\\sqrt\{/, /\\lim_/, /\\mathrm\{/];
        const walker = document.createTreeWalker(container, NodeFilter.SHOW_TEXT, null);
        while (walker.nextNode()) {
            const text = walker.currentNode.textContent;
            for (const p of patterns) {
                if (p.test(text)) {
                    let parent = walker.currentNode.parentElement;
                    let inMathJax = false;
                    while (parent) {
                        if (parent.tagName && parent.tagName.toLowerCase().startsWith('mjx-')) { inMathJax = true; break; }
                        parent = parent.parentElement;
                    }
                    if (!inMathJax) {
                        issues.push({ type: 'unrendered_latex', text: text.substring(0, 120).trim() });
                        break;
                    }
                }
            }
        }
        return issues;
    });

    console.log(`   题库问题: ${practiceIssues.length} 个`);
    for (const issue of practiceIssues.slice(0, 10)) {
        console.log(`   - [${issue.type}] ${issue.text || JSON.stringify(issue)}`);
    }

    await page.screenshot({ path: '/Users/wuyangcj/trae/回甘demo/screenshots/practice_render_check.png' });

    console.log('\n5. 控制台错误:');
    if (consoleMsgs.length === 0) console.log('   无错误');
    else consoleMsgs.slice(0, 10).forEach(m => console.log(`   ${m}`));

    await browser.close();
    console.log('\n检测完成');
})();
