// debug_remaining_5.mjs - 调试修复后剩余5个错误
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

const TARGET_IDS = [
    'real_2018_math3_q8_shusan',
    'sy_p11',
    'sy_gs_ch7_q4',
    'sy_gl_ch3_q4',
    'ss_gs_ch7_q3',
];

async function main() {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForTimeout(3000);

    // 收集所有匹配的题目（包括ID重复的）
    const questions = await page.evaluate((ids) => {
        const result = [];
        const forEachArr = (val, fn) => {
            if (Array.isArray(val)) val.forEach(fn);
            else if (val && typeof val === 'object') {
                Object.keys(val).forEach(k => forEachArr(val[k], fn));
            }
        };
        const collect = (q, source) => {
            if (q && q.id && ids.includes(q.id)) {
                result.push({
                    id: q.id,
                    source,
                    content: q.content,
                    options: q.options,
                    answer: q.answer,
                    analysis: q.analysis
                });
            }
        };
        for (const mt of Object.keys(questionBank || {})) {
            for (const cat of Object.keys(questionBank[mt] || {})) {
                forEachArr(questionBank[mt][cat], q => collect(q, `questionBank.${mt}.${cat}`));
            }
        }
        for (const subject of Object.keys(chapterQuestionBank || {})) {
            forEachArr(chapterQuestionBank[subject], item => {
                if (item && item.questions) forEachArr(item.questions, q => collect(q, `chapterQuestionBank.${subject}`));
                else collect(item, `chapterQuestionBank.${subject}`);
            });
        }
        for (const paper of Object.keys(examPaperBank || {})) {
            forEachArr(examPaperBank[paper], q => collect(q, `examPaperBank.${paper}`));
        }
        return result;
    }, TARGET_IDS);

    // 对每个题目，输出原始数据和formatMath后的内容
    const output = await page.evaluate((qs) => {
        const out = [];
        for (const q of qs) {
            out.push({
                id: q.id,
                source: q.source,
                raw: {
                    content: q.content,
                    answer: q.answer,
                    analysis: q.analysis
                },
                formatted: {
                    content: q.content ? formatMath(q.content) : '',
                    answer: q.answer ? formatMath(q.answer) : '',
                    analysis: q.analysis ? formatMath(q.analysis) : ''
                }
            });
        }
        return out;
    }, questions);

    console.log(JSON.stringify(output, null, 2));

    await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
