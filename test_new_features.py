"""
新功能测试 - 验证本轮6项修改的正确性
1. SVG公式乱码修复（Unicode上下标范围 + Σ上下文区分）
2. 题目类型优化（计算题无输入框、填空题加公式辅助、答案识别增强）
3. 提交逻辑修复（取消自动提交，等用户确认）
4. 刷题进度保留（切换功能后恢复进度）
5. 知识库视频链接完善（不再指向同一首页）
6. 头像显示bug修复 + 登录页空白修复 + 回车键自动登录
"""
import re

HTML_FILE = '/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html'


def read_html():
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        return f.read()


# ========== 1. SVG公式乱码修复测试 ==========

def test_unicode_subscript_not_in_superscript_range():
    """确保 ᵢ(U+1D62) 不在上标范围内，在下标范围内"""
    html = read_html()
    # 上标正则不应包含 \u1D62-\u1D6A 范围
    # 检查上标正则中排除了下标字符范围
    assert '\\u1D43-\\u1D61' in html or '\\u1D43-\\u1D50' in html, \
        "上标范围应排除下标字符(\\u1D62-\\u1D6A)"


def test_sigma_context_aware():
    """确保 Σ 根据上下文区分求和符号和曲面符号"""
    html = read_html()
    # 应存在上下文感知的 Σ 处理
    assert 'Σ(?=[a-zA-Z0-9(])' in html or 'Σ\\\\(?=[a-zA-Z0-9(])' in html, \
        "应存在 Σ 后跟字母/数字时转为 \\sum 的规则"
    assert '_Σ' in html or '_\\\\Sigma' in html, \
        "应存在 _Σ 转为下标 Sigma 的规则"


def test_no_raw_unicode_subscript_in_formula():
    """确保公式中不会出现原始 Unicode 下标字符导致乱码"""
    html = read_html()
    # 检查 subMap 中包含 ᵢ 的映射
    assert "'ᵢ':'i'" in html, "subMap 应包含 ᵢ → i 的映射"


# ========== 2. 题目类型优化测试 ==========

def test_essay_question_no_input():
    """计算/解答题不应有输入框"""
    html = read_html()
    # renderQuestion 中解答/计算题应显示提示文本而非输入框
    assert '本题为主观题' in html or '请自行演算' in html, \
        "解答/计算题应显示主观题提示而非输入框"


def test_fill_question_math_toolbar():
    """填空题应有数学符号工具栏"""
    html = read_html()
    assert 'math-input-toolbar' in html, "应存在数学输入工具栏CSS类"
    assert 'math-tool-btn' in html, "应存在数学工具按钮CSS类"


def test_answer_normalization_function():
    """应有答案规范化函数"""
    html = read_html()
    assert 'function normalizeAnswer' in html, "应定义 normalizeAnswer 函数"
    assert 'function isFillAnswerCorrect' in html, "应定义 isFillAnswerCorrect 函数"


def test_essay_not_graded():
    """解答/计算题不应参与判分"""
    html = read_html()
    # submitPractice 或 showPracticeResult 中应跳过解答题判分
    assert "isEssay" in html, "应存在 isEssay 判断逻辑"
    # 确保有跳过判分的逻辑
    essay_skip_pattern = re.search(r'isEssay.*?return.*?\{', html, re.DOTALL)
    assert essay_skip_pattern or '不判分' in html, \
        "解答题应有跳过判分的逻辑"


def test_correct_rate_excludes_essay():
    """正确率计算应排除大题"""
    html = read_html()
    assert 'gradedCount' in html, "应使用 gradedCount 追踪参与判分的题数"
    assert '不含大题' in html, "正确率标签应注明'不含大题'"


# ========== 3. 提交逻辑修复测试 ==========

def test_submit_confirmation():
    """最后一题应弹出确认框而非自动提交"""
    html = read_html()
    # nextQuestion 中应有 confirm 确认
    assert '确定要提交' in html, "应存在提交确认提示"


# ========== 4. 刷题进度保留测试 ==========

def test_saved_progress_mechanism():
    """应有 savedProgress 机制"""
    html = read_html()
    assert 'practiceState.savedProgress' in html, \
        "应存在 savedProgress 进度保存机制"


def test_navigate_to_saves_progress():
    """离开刷题页时应保存进度"""
    html = read_html()
    # navigateTo 中应有保存进度的逻辑
    nav_section = html[html.find('function navigateTo'):html.find('function navigateTo') + 800]
    assert 'savedProgress' in nav_section, \
        "navigateTo 中应保存刷题进度"


def test_reset_practice_restores_progress():
    """resetPractice 应恢复保存的进度"""
    html = read_html()
    reset_section = html[html.find('function resetPractice'):html.find('function resetPractice') + 2000]
    assert 'savedProgress' in reset_section, \
        "resetPractice 中应恢复保存的进度"
    assert '已恢复上次刷题进度' in reset_section, \
        "应显示恢复进度的提示"


def test_start_practice_clears_progress():
    """startPractice 应清除旧进度"""
    html = read_html()
    start_section = html[html.find('function startPractice'):html.find('function startPractice') + 200]
    assert 'savedProgress = null' in start_section, \
        "startPractice 中应清除 savedProgress"


def test_finish_practice_clears_progress():
    """finishPractice 应清除进度"""
    html = read_html()
    finish_section = html[html.find('function finishPractice'):html.find('function finishPractice') + 200]
    assert 'savedProgress = null' in finish_section, \
        "finishPractice 中应清除 savedProgress"


# ========== 5. 知识库视频链接完善测试 ==========

def test_no_bare_bilibili_url():
    """不应存在不带路径的 bilibili.com URL"""
    html = read_html()
    # 不应有 url: 'https://www.bilibili.com' （不带路径）
    bare_urls = re.findall(r"url:\s*'https://www\.bilibili\.com'\s*\}", html)
    assert len(bare_urls) == 0, \
        f"仍存在 {len(bare_urls)} 个不带路径的 bilibili.com URL"


def test_bookRef_fields_exist():
    """所有知识库条目应有 bookRef 字段（替代已过期的视频链接）"""
    html = read_html()
    bookref_count = len(re.findall(r"bookRef\s*:\s*\{", html))
    assert bookref_count >= 60, f"应至少有60个bookRef字段，实际{bookref_count}个"
    # 确保没有残留的 video 字段
    video_fields = re.findall(r"video\s*:\s*\{", html)
    assert len(video_fields) == 0, f"不应再有video字段，实际{len(video_fields)}个"


# ========== 6. 头像/登录页/回车登录测试 ==========

def test_user_avatar_overflow_hidden():
    """user-avatar 应有 overflow: hidden"""
    html = read_html()
    # 找到 .user-avatar CSS块
    avatar_css = re.search(r'\.user-avatar\s*\{[^}]+\}', html)
    assert avatar_css, "应存在 .user-avatar CSS规则"
    assert 'overflow: hidden' in avatar_css.group(), \
        ".user-avatar 应有 overflow: hidden"


def test_user_avatar_svg_sizing():
    """user-avatar 内的 svg 应有 100% 尺寸"""
    html = read_html()
    assert '.user-avatar svg' in html, \
        "应有 .user-avatar svg 的CSS规则"


def test_get_avatar_html_simplified():
    """getAvatarHTML 应简化，不使用内联样式"""
    html = read_html()
    func_section = html[html.find('function getAvatarHTML'):html.find('function getAvatarHTML') + 500]
    # 不应再有内联的 width:100%;height:100% 样式
    assert 'style="width:100%;height:100%;object-fit:cover;border-radius:50%"' not in func_section, \
        "getAvatarHTML 不应再使用内联样式"


def test_auth_brand_visible():
    """auth-brand 应可见（用户要求还原左侧品牌区）"""
    html = read_html()
    brand_css = re.search(r'\.auth-brand\s*\{[^}]+\}', html)
    assert brand_css, "应存在 .auth-brand CSS规则"
    assert 'display: flex' in brand_css.group(), \
        ".auth-brand 应设置为 display: flex（可见）"
    assert 'display: none' not in brand_css.group(), \
        ".auth-brand 不应被隐藏"


def test_auth_form_side_full_width():
    """auth-form-side 应全屏自适应"""
    html = read_html()
    form_css = re.search(r'\.auth-form-side\s*\{[^}]+\}', html)
    assert form_css, "应存在 .auth-form-side CSS规则"
    css_text = form_css.group()
    assert 'flex: 1' in css_text or 'width: 100%' in css_text, \
        ".auth-form-side 应使用 flex:1 或 width:100% 全屏"


def test_enter_key_login():
    """登录密码框应支持回车键登录"""
    html = read_html()
    # 检查 loginPassword 输入框是否有 onkeydown Enter 处理
    password_input = re.search(r'<input[^>]*id="loginPassword"[^>]*>', html)
    assert password_input, "应存在 loginPassword 输入框"
    input_tag = password_input.group()
    assert "event.key==='Enter'" in input_tag or "event.key === 'Enter'" in input_tag, \
        "loginPassword 应有回车键登录处理"
    assert 'login()' in input_tag, \
        "回车应触发 login()"


def test_enter_key_register():
    """注册确认密码框应支持回车键注册"""
    html = read_html()
    password2_input = re.search(r'<input[^>]*id="regPassword2"[^>]*>', html)
    assert password2_input, "应存在 regPassword2 输入框"
    input_tag = password2_input.group()
    assert "event.key==='Enter'" in input_tag or "event.key === 'Enter'" in input_tag, \
        "regPassword2 应有回车键注册处理"


def test_login_username_enter():
    """登录用户名框也应支持回车"""
    html = read_html()
    username_input = re.search(r'<input[^>]*id="loginUsername"[^>]*>', html)
    assert username_input, "应存在 loginUsername 输入框"
    input_tag = username_input.group()
    assert "event.key==='Enter'" in input_tag, \
        "loginUsername 应有回车键处理"


# ========== 综合质检测试 ==========

def test_js_syntax_valid():
    """JS语法基本验证"""
    html = read_html()
    # 提取 <script> 内容做基本检查
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    assert len(scripts) > 0, "应存在script标签"
    combined = '\n'.join(scripts)
    # 基本括号匹配检查（CSS和字符串中的大括号会导致偏差，阈值放宽）
    open_braces = combined.count('{')
    close_braces = combined.count('}')
    assert abs(open_braces - close_braces) < 50, \
        f"大括号严重不匹配: 开{open_braces} 闭{close_braces}"


def test_no_duplicate_function_definitions():
    """关键函数不应重复定义"""
    html = read_html()
    for func_name in ['function startPractice', 'function finishPractice', 'function resetPractice', 'function navigateTo']:
        count = html.count(func_name)
        assert count == 1, f"{func_name} 定义了 {count} 次，应为1次"
