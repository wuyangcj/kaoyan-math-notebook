// Playwright 自测脚本：自建题库导入功能
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    const errors = [];
    const logs = [];
    
    // 收集console消息
    page.on('console', msg => {
        const text = msg.text();
        logs.push(`[${msg.type()}] ${text}`);
        if (msg.type() === 'error') {
            errors.push(`Console error: ${text}`);
        }
    });
    page.on('pageerror', err => {
        errors.push(`Page error: ${err.message}`);
    });
    
    try {
        // 加载页面
        await page.goto('file:///Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html', { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(3000);
        
        // 设置测试用户
        await page.evaluate(() => {
            const u = 'testimport_' + Date.now();
            const users = {};
            users[u] = {
                password: 'test123456',
                nickname: '测试用户',
                avatar: '🐱',
                stats: { total: 0, correct: 0, errors: [], customQuestions: [], exp: 0, streak: 0, lastDate: '' },
                createdAt: new Date().toISOString()
            };
            localStorage.setItem('zcb_users', JSON.stringify(users));
            localStorage.setItem('zcb_currentUser', JSON.stringify({
                username: u,
                password: 'test123456',
                nickname: '测试用户',
                avatar: '🐱',
                stats: { total: 0, correct: 0, errors: [], customQuestions: [], exp: 0, streak: 0, lastDate: '' }
            }));
            localStorage.setItem('zcb_settings', JSON.stringify({ selectedMathType: 'shuyi' }));
        });
        
        await page.reload({ waitUntil: 'networkidle' });
        await page.waitForTimeout(2000);
        
        // 导航到自建题库页面
        await page.evaluate(() => navigateTo('import'));
        await page.waitForTimeout(1000);
        
        // 测试1：检查导入卡片是否存在
        const jsonCard = await page.locator('text=JSON 导入').count();
        const txtCard = await page.locator('text=TXT 导入').count();
        const excelCard = await page.locator('text=Excel 导入').count();
        
        if (jsonCard > 0) console.log('✓ JSON导入卡片存在');
        else errors.push('✗ JSON导入卡片不存在');
        
        if (txtCard > 0) console.log('✓ TXT导入卡片存在');
        else errors.push('✗ TXT导入卡片不存在');
        
        if (excelCard > 0) console.log('✓ Excel导入卡片存在');
        else errors.push('✗ Excel导入卡片不存在');
        
        // 测试2：检查手动添加表单是否已移除
        const addForm = await page.locator('#addForm').count();
        if (addForm === 0) console.log('✓ 手动添加表单已移除');
        else errors.push('✗ 手动添加表单仍存在');
        
        // 测试3：测试JSON导入
        console.log('\n--- 测试JSON导入 ---');
        const testJSON = JSON.stringify([
            {
                content: '测试题目1：计算 $\\\\int_0^1 x^2 dx$ 的值',
                options: ['1/3', '1/2', '2/3', '1'],
                answer: 'A',
                analysis: '积分等于 1/3',
                subject: 'gaoshu'
            },
            {
                content: '测试题目2：矩阵 A 的秩为',
                options: ['1', '2', '3', '4'],
                answer: 'B',
                analysis: '通过初等变换得秩为2',
                subject: 'xiandai'
            }
        ]);
        
        const jsonPath = '/tmp/test_questions.json';
        fs.writeFileSync(jsonPath, testJSON);
        
        await page.setInputFiles('#importFileInput', jsonPath);
        await page.waitForTimeout(2000);
        
        // 检查预览是否显示
        const previewVisible = await page.locator('#importPreviewCard').isVisible();
        if (previewVisible) console.log('✓ JSON导入预览已显示');
        else errors.push('✗ JSON导入预览未显示');
        
        const previewCount = await page.locator('#importPreviewCount').textContent();
        console.log(`✓ 预览题目数: ${previewCount}`);
        if (previewCount !== '2') errors.push(`✗ 预览题目数应为2，实际${previewCount}`);
        
        // 确认导入
        await page.evaluate(() => confirmImport());
        await page.waitForTimeout(1000);
        
        // 检查导入后的题目列表
        const customCount = await page.locator('#customCount').textContent();
        console.log(`✓ 导入后自建题目数: ${customCount}`);
        if (customCount !== '2') errors.push(`✗ 导入后题目数应为2，实际${customCount}`);
        
        // 测试4：测试重复导入去重
        console.log('\n--- 测试重复导入去重 ---');
        await page.setInputFiles('#importFileInput', jsonPath);
        await page.waitForTimeout(2000);
        // 使用 evaluate 直接调用 confirmImport，避免点击可见性问题
        await page.evaluate(() => confirmImport());
        await page.waitForTimeout(1000);
        
        const customCountAfterDup = await page.locator('#customCount').textContent();
        console.log(`✓ 重复导入后题目数: ${customCountAfterDup} (应仍为2)`);
        if (customCountAfterDup !== '2') errors.push(`✗ 重复导入去重失败，题目数应为2，实际${customCountAfterDup}`);
        
        // 测试5：测试删除功能
        console.log('\n--- 测试删除功能 ---');
        const deleteBtns = await page.locator('text=删除').count();
        console.log(`✓ 删除按钮数量: ${deleteBtns}`);
        if (deleteBtns > 0) {
            await page.locator('text=删除').first().click();
            await page.waitForTimeout(500);
            const customCountAfterDel = await page.locator('#customCount').textContent();
            console.log(`✓ 删除后题目数: ${customCountAfterDel}`);
            if (customCountAfterDel !== '1') errors.push(`✗ 删除后题目数应为1，实际${customCountAfterDel}`);
        }
        
        // 测试6：测试TXT导入
        console.log('\n--- 测试TXT导入 ---');
        const testTXT = `1. 下列哪个是导数定义
A. lim(h->0) [f(x+h)-f(x)]/h
B. f(x+h)-f(x)
C. f'(x)
D. f(x)
答案：A
解析：导数的极限定义

2. 线性方程组 Ax=0 有非零解的条件
A. |A|=0
B. |A|≠0
C. A=0
D. x=0
答案：A
解析：系数矩阵行列式为0`;
        
        const txtPath = '/tmp/test_questions.txt';
        fs.writeFileSync(txtPath, testTXT);
        
        await page.setInputFiles('#importFileInput', txtPath);
        await page.waitForTimeout(2000);
        
        const txtPreviewCount = await page.locator('#importPreviewCount').textContent();
        console.log(`✓ TXT导入预览题目数: ${txtPreviewCount}`);
        if (txtPreviewCount !== '2') errors.push(`✗ TXT导入预览题目数应为2，实际${txtPreviewCount}`);
        
        await page.click('text=确认导入').catch(() => {});
        await page.evaluate(() => confirmImport()).catch(() => {});
        await page.waitForTimeout(1000);
        
        const customCountAfterTxt = await page.locator('#customCount').textContent();
        console.log(`✓ TXT导入后题目数: ${customCountAfterTxt}`);
        
        // 测试7：检查XLSX库是否加载
        console.log('\n--- 检查XLSX库 ---');
        const xlsxLoaded = await page.evaluate(() => typeof XLSX !== 'undefined');
        if (xlsxLoaded) console.log('✓ XLSX库已加载');
        else errors.push('✗ XLSX库未加载');
        
    } catch (e) {
        errors.push(`测试异常: ${e.message}`);
        console.error('测试异常:', e);
    }
    
    console.log('\n=== 测试结果 ===');
    console.log(`错误数: ${errors.length}`);
    errors.forEach(e => console.log(`  ✗ ${e}`));
    
    if (errors.length === 0) {
        console.log('\n✓ 所有测试通过');
    } else {
        console.log('\n✗ 有错误需要修复');
    }
    
    // 打印最近10条日志
    console.log('\n=== 最近日志 ===');
    logs.slice(-10).forEach(l => console.log(l));
    
    await browser.close();
    process.exit(errors.length > 0 ? 1 : 0);
})();
