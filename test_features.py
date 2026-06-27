#!/usr/bin/env python3
"""
TDD 测试：账号导出/导入、侧边栏 z-index、登录页自适应、每日海报。
"""
import re
import subprocess
from pathlib import Path

HTML = Path(__file__).with_name('回甘—考研数学智题本.html')


def extract_js():
    html = HTML.read_text(encoding='utf-8')
    scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
    return '\n'.join(scripts)


def extract_html():
    return HTML.read_text(encoding='utf-8')


# ========== 测试 1：侧边栏 z-index 必须高于遮罩层 ==========
def test_sidebar_zindex_higher_than_overlay():
    """侧边栏 z-index 必须大于遮罩层 z-index，否则遮罩层会覆盖侧边栏。"""
    html = extract_html()
    # 提取 .sidebar 的 z-index
    sidebar_match = re.search(r'\.sidebar\s*\{[^}]*z-index:\s*(\d+)', html)
    overlay_match = re.search(r'\.sidebar-overlay\s*\{[^}]*z-index:\s*(\d+)', html)
    assert sidebar_match, '未找到 .sidebar 的 z-index'
    assert overlay_match, '未找到 .sidebar-overlay 的 z-index'
    sidebar_z = int(sidebar_match.group(1))
    overlay_z = int(overlay_match.group(1))
    assert sidebar_z > overlay_z, f'侧边栏 z-index({sidebar_z}) 必须大于遮罩层 z-index({overlay_z})'


# ========== 测试 2：登录页必须使用 height:100vh 而非 min-height ==========
def test_auth_page_uses_height_not_min_height():
    """登录页应使用 height:100vh + overflow:hidden 防止空白滚动。"""
    html = extract_html()
    # 检查 .auth-page 规则
    auth_page_match = re.search(r'\.auth-page\s*\{([^}]+)\}', html)
    assert auth_page_match, '未找到 .auth-page 规则'
    auth_page_css = auth_page_match.group(1)
    assert 'height: 100vh' in auth_page_css, '.auth-page 必须使用 height:100vh'
    assert 'min-height: 100vh' not in auth_page_css, '.auth-page 不应使用 min-height:100vh'
    assert 'overflow: hidden' in auth_page_css, '.auth-page 必须有 overflow:hidden'


# ========== 测试 3：导出/导入函数必须定义 ==========
def test_export_import_functions_defined():
    """exportAccountData 和 importAccountData 函数必须定义。"""
    js = extract_js()
    assert 'function exportAccountData' in js, 'exportAccountData 函数未定义'
    assert 'function importAccountData' in js, 'importAccountData 函数未定义'
    assert 'function showImportModal' in js, 'showImportModal 函数未定义'
    assert 'function closeImportModal' in js, 'closeImportModal 函数未定义'


# ========== 测试 4：导入模态框 HTML 必须存在 ==========
def test_import_modal_html_exists():
    """导入账号模态框 HTML 必须存在。"""
    html = extract_html()
    assert 'id="importModalOverlay"' in html, '导入模态框 importModalOverlay 不存在'
    assert 'id="importCodeInput"' in html, '导入输入框 importCodeInput 不存在'


# ========== 测试 5：导出码格式必须正确 ==========
def test_export_code_format():
    """导出码必须以 ZCB1.0: 开头，使用 Base64 编码。"""
    js = extract_js()
    assert "'ZCB1.0:'" in js or '"ZCB1.0:"' in js, '导出码必须以 ZCB1.0: 开头'
    assert 'btoa(' in js, '导出必须使用 Base64 编码'
    assert 'atob(' in js, '导入必须使用 Base64 解码'


# ========== 测试 6：每日海报函数必须定义 ==========
def test_daily_poster_functions_defined():
    """getDailyPosterUrl 和 updateHeroPoster 函数必须定义。"""
    js = extract_js()
    assert 'function getDailyPosterUrl' in js, 'getDailyPosterUrl 函数未定义'
    assert 'function updateHeroPoster' in js, 'updateHeroPoster 函数未定义'
    assert 'heroPosterPrompts' in js, 'heroPosterPrompts 数组未定义'


# ========== 测试 7：海报必须按天更换 ==========
def test_poster_changes_by_day():
    """海报 URL 必须基于日期计算，不同日期应返回不同 prompt。"""
    js = extract_js()
    # 检查是否使用 Date.now() / 86400000 计算天数
    assert 'Date.now() / 86400000' in js, '海报必须按天更换（使用 Date.now()/86400000）'


# ========== 测试 8：海报 CSS 必须使用 cover 适配 ==========
def test_poster_css_uses_cover():
    """海报 CSS 必须使用 background-size:cover 适配区域。"""
    html = extract_html()
    poster_match = re.search(r'\.hero-poster\s*\{([^}]+)\}', html)
    assert poster_match, '未找到 .hero-poster 规则'
    poster_css = poster_match.group(1)
    assert 'background-size: cover' in poster_css, '.hero-poster 必须使用 background-size:cover'
    assert 'background-position: center' in poster_css, '.hero-poster 必须使用 background-position:center'


# ========== 测试 9：设置页数据管理区已移除（云端自动同步） ==========
def test_settings_has_data_management():
    """设置页不应再有数据管理区域——已由云端自动同步替代。"""
    html = extract_html()
    assert '数据管理' not in html, '设置页仍残留已废弃的数据管理区域'
    # 导入入口仍保留在登录页，函数以 @deprecated 形式存在
    assert 'showImportModal()' in html, '登录页导入入口仍需保留'


# ========== 测试 10：登录页必须有导入入口 ==========
def test_auth_page_has_import_entry():
    """登录页必须有从其他设备导入账号的入口。"""
    html = extract_html()
    assert 'auth-import-entry' in html, '登录页缺少导入账号入口'
    assert '从其他设备导入账号' in html, '登录页缺少导入账号链接文本'


# ========== 测试 11：closeResult 死代码必须已删除 ==========
def test_close_result_removed():
    """closeResult 函数和 resultOverlay 元素必须已删除。"""
    html = extract_html()
    js = extract_js()
    assert 'function closeResult' not in js, 'closeResult 函数应已删除'
    assert 'id="resultOverlay"' not in html, 'resultOverlay 元素应已删除'


# ========== 测试 12：JS 语法必须通过 Node.js 检查 ==========
def test_js_syntax_valid():
    """所有 JS 必须通过 Node.js 语法检查。"""
    js = extract_js()
    js_file = Path('/tmp/app_features_test.js')
    js_file.write_text(js, encoding='utf-8')
    result = subprocess.run(
        ['node', '--check', str(js_file)],
        capture_output=True,
        text=True,
        errors='replace',
    )
    if result.returncode != 0:
        raise AssertionError('JS syntax error:\n' + result.stderr)


if __name__ == '__main__':
    test_sidebar_zindex_higher_than_overlay()
    print('✓ 侧边栏 z-index 测试通过')
    test_auth_page_uses_height_not_min_height()
    print('✓ 登录页自适应测试通过')
    test_export_import_functions_defined()
    print('✓ 导出/导入函数测试通过')
    test_import_modal_html_exists()
    print('✓ 导入模态框 HTML 测试通过')
    test_export_code_format()
    print('✓ 导出码格式测试通过')
    test_daily_poster_functions_defined()
    print('✓ 每日海报函数测试通过')
    test_poster_changes_by_day()
    print('✓ 海报按天更换测试通过')
    test_poster_css_uses_cover()
    print('✓ 海报 CSS 适配测试通过')
    test_settings_has_data_management()
    print('✓ 设置页数据管理测试通过')
    test_auth_page_has_import_entry()
    print('✓ 登录页导入入口测试通过')
    test_close_result_removed()
    print('✓ 死代码删除测试通过')
    test_js_syntax_valid()
    print('✓ JS 语法检查通过')
    print('\n所有测试通过！')
