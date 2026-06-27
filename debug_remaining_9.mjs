// debug_remaining_9.mjs - 调试剩余9个错误的formatMath处理前后对比
import { chromium } from 'playwright';
import { pathToFileURL } from 'url';

const HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html';
const fileUrl = pathToFileURL(HTML_FILE).href;

const TARGET_IDS = [
    'real_2018_math3_q8_shusan',
    'sy_gs_ch7_q4',
    'sy_gs_ch7_q5',
    'ss_gs_ch3_q3',
    'ss_gs_ch7_q3',
    'ss24_10',
    'sy_p11',
    'tangjiafeng_shuyi_gailv_0004',
    'sy_gl_ch3_q4',
];

async function main() {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 60000 });
    await page.waitForTimeout(3000);

    // 收集目标题目
    const questions = await page.evaluate((ids) => {
        const result = {};
        const forEachArr = (val, fn) => {
            if (Array.isArray(val)) val.forEach(fn);
            else if (val && typeof val === 'object') {
                Object.keys(val).forEach(k => forEachArr(val[k], fn));
            }
        };
        const collect = (q) => {
            if (q && q.id && ids.includes(q.id)) {
                result[q.id] = {
                    id: q.id,
                    content: q.content,
                    options: q.options,
                    answer: q.answer,
                    analysis: q.analysis
                };
            }
        };
        for (const mt of Object.keys(questionBank || {})) {
            for (const cat of Object.keys(questionBank[mt] || {})) {
                forEachArr(questionBank[mt][cat], collect);
            }
        }
        for (const subject of Object.keys(chapterQuestionBank || {})) {
            forEachArr(chapterQuestionBank[subject], item => {
                if (item && item.questions) forEachArr(item.questions, collect);
                else collect(item);
            });
        }
        for (const paper of Object.keys(examPaperBank || {})) {
            forEachArr(examPaperBank[paper], collect);
        }
        return result;
    }, TARGET_IDS);

    // 对每个题目，输出原始数据和formatMath后的内容
    const output = await page.evaluate((qs) => {
        const out = {};
        for (const id of Object.keys(qs)) {
            const q = qs[id];
            out[id] = {
                raw: {
                    content: q.content,
                    options: q.options,
                    answer: q.answer,
                    analysis: q.analysis
                },
                formatted: {
                    content: q.content ? formatMath(q.content) : '',
                    options: q.options ? q.options.map(o => formatMath(o)) : [],
                    answer: q.answer ? formatMath(q.answer) : '',
                    analysis: q.analysis ? formatMath(q.analysis) : ''
                }
            };
        }
        return out;
    }, questions);

    console.log(JSON.stringify(output, null, 2));

    await browser.close();
}

main().catch(e => { console.error(e); process.exit(1); });
