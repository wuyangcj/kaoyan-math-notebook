// 最终全面自测：验证LaTeX渲染、知识库、题库、导入功能
const { chromium } = require('playwright');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    const errors = [];
    
    page.on('pageerror', err => {
        errors.push(`Page error: ${err.message}`);
    });
    
    try {
        await page.goto('file:///Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html', { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(3000);
        
        // 设置测试用户
        await page.evaluate(() => {
            const u = 'testfinal_' + Date.now();
            const users = {};
            users[u] = {
                password: 'test123456', nickname: '测试', avatar: '🐱',
                stats: { total: 0, correct: 0, errors: [], customQuestions: [], exp: 0, streak: 0, lastDate: '' },
                createdAt: new Date().toISOString()
            };
            localStorage.setItem('zcb_users', JSON.stringify(users));
            localStorage.setItem('zcb_currentUser', JSON.stringify({
                username: u, password: 'test123456', nickname: '测试', avatar: '🐱',
                stats: { total: 0, correct: 0, errors: [], customQuestions: [], exp: 0, streak: 0, lastDate: '' }
            }));
            localStorage.setItem('zcb_settings', JSON.stringify({ selectedMathType: 'shuyi' }));
        });
        
        await page.reload({ waitUntil: 'networkidle' });
        await page.waitForTimeout(2000);
        
        // 测试1：知识库页面渲染
        console.log('=== 测试1：知识库页面渲染 ===');
        await page.evaluate(() => navigateTo('knowledge'));
        await page.waitForTimeout(2000);
        
        // 检查是否有code/div源码显示（LaTeX未渲染）
        const kbSourceCode = await page.evaluate(() => {
            const main = document.querySelector('#page-knowledge') || document.body;
            const text = main.innerText;
            // 检查是否有裸露的LaTeX源码
            const patterns = [/\\\\frac\{/, /\\\\lt/, /<div[^>]*>/i, /<code[^>]*>/i];
            let issues = 0;
            for (const p of patterns) {
                const matches = text.match(new RegExp(p.source, 'g'));
                if (matches) issues += matches.length;
            }
            return issues;
        });
        console.log(`知识库页面源码显示问题: ${kbSourceCode}`);
        if (kbSourceCode > 0) errors.push(`知识库有${kbSourceCode}处源码显示问题`);
        else console.log('✓ 知识库页面无源码显示问题');
        
        // 测试2：知识库详情渲染（检查小于号修复）
        console.log('\n=== 测试2：知识库详情小于号渲染 ===');
        // 点击第一个知识点
        const firstKbItem = await page.locator('.kb-card, .knowledge-item, [onclick*="showKnowledgeDetail"]').first();
        if (await firstKbItem.count() > 0) {
            await firstKbItem.click();
            await page.waitForTimeout(2000);
            
            // 检查详情中是否有被误解析的HTML标签
            const detailIssues = await page.evaluate(() => {
                const modal = document.querySelector('.modal-content, .kb-detail, [class*="detail"]') || document.body;
                const html = modal.innerHTML;
                // 检查是否有 \lt 被正确渲染（而不是显示为源码）
                const text = modal.innerText;
                if (text.includes('\\lt')) return '有\\lt源码显示';
                if (text.includes('<n') || text.includes('<x')) return '有未修复的小于号';
                return 'OK';
            });
            console.log(`知识库详情渲染: ${detailIssues}`);
            if (detailIssues !== 'OK') errors.push(`知识库详情: ${detailIssues}`);
            else console.log('✓ 知识库详情小于号渲染正常');
            
            // 关闭详情
            await page.keyboard.press('Escape').catch(() => {});
            await page.waitForTimeout(500);
        }
        
        // 测试3：题库页面渲染
        console.log('\n=== 测试3：题库页面渲染 ===');
        await page.evaluate(() => navigateTo('practice'));
        await page.waitForTimeout(2000);
        
        // 检查题库是否有源码显示
        const practiceSourceCode = await page.evaluate(() => {
            const main = document.querySelector('#page-practice') || document.body;
            const text = main.innerText;
            if (text.includes('\\lt')) return '有\\lt源码';
            if (text.includes('\\frac{')) return '有\\frac源码';
            return 'OK';
        });
        console.log(`题库页面渲染: ${practiceSourceCode}`);
        if (practiceSourceCode !== 'OK') errors.push(`题库: ${practiceSourceCode}`);
        else console.log('✓ 题库页面渲染正常');
        
        // 测试4：自建题库导入功能
        console.log('\n=== 测试4：自建题库导入功能 ===');
        await page.evaluate(() => navigateTo('import'));
        await page.waitForTimeout(1000);
        
        const importCards = await page.locator('.import-card').count();
        console.log(`导入卡片数量: ${importCards}`);
        if (importCards === 3) console.log('✓ 三个导入卡片存在');
        else errors.push(`导入卡片数量应为3，实际${importCards}`);
        
        // 测试5：检查LaTeX渲染（MathJax）
        console.log('\n=== 测试5：LaTeX渲染检查 ===');
        const mathjaxLoaded = await page.evaluate(() => typeof window.MathJax !== 'undefined');
        console.log(`MathJax加载: ${mathjaxLoaded ? '是' : '否'}`);
        if (!mathjaxLoaded) errors.push('MathJax未加载');
        else console.log('✓ MathJax已加载');
        
        // 测试6：检查所有页面可导航
        console.log('\n=== 测试6：页面导航检查 ===');
        const pages = ['practice', 'errors', 'knowledge', 'leaderboard', 'import', 'ai', 'settings'];
        for (const p of pages) {
            try {
                await page.evaluate((pageName) => navigateTo(pageName), p);
                await page.waitForTimeout(500);
                const visible = await page.evaluate((pageName) => {
                    const el = document.getElementById('page-' + pageName);
                    return el && el.style.display !== 'none';
                }, p);
                console.log(`  ${p}: ${visible ? '✓' : '✗'}`);
                if (!visible) errors.push(`页面${p}不可见`);
            } catch (e) {
                console.log(`  ${p}: 导航失败`);
                errors.push(`页面${p}导航失败`);
            }
        }
        
    } catch (e) {
        errors.push(`测试异常: ${e.message}`);
        console.error('测试异常:', e);
    }
    
    console.log('\n=== 最终测试结果 ===');
    console.log(`错误数: ${errors.length}`);
    errors.forEach(e => console.log(`  ✗ ${e}`));
    
    if (errors.length === 0) {
        console.log('\n✓✓✓ 所有功能测试通过，可以交付 ✓✓✓');
    } else {
        console.log('\n✗ 有错误需要修复');
    }
    
    await browser.close();
    process.exit(errors.length > 0 ? 1 : 0);
})();
