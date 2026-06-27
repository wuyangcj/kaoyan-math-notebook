"""
云端账号同步功能测试。
验证 Task 7-10 引入的 Supabase 云端同步、密码哈希、离线回退、待同步重试、
手动导入入口隐藏、导出函数废弃标注等改动。
"""
import re
import os

HTML_FILE = os.path.join(os.path.dirname(__file__), '回甘—考研数学智题本.html')


def read_html():
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        return f.read()


# ========== 1. Supabase SDK 引入 ==========

def test_supabase_sdk_imported():
    """HTML 中应引入 Supabase JS SDK 的 script 标签。"""
    html = read_html()
    assert '@supabase/supabase-js' in html, "应引入 Supabase JS SDK"


# ========== 2. Supabase 配置常量 ==========

def test_supabase_config_exists():
    """应定义 SUPABASE_URL、SUPABASE_KEY 常量及 initSupabase 函数。"""
    html = read_html()
    assert 'SUPABASE_URL' in html, "应定义 SUPABASE_URL 常量"
    assert 'SUPABASE_KEY' in html, "应定义 SUPABASE_KEY 常量"
    assert re.search(r'function\s+initSupabase\s*\(', html), \
        "应定义 initSupabase 函数"


# ========== 3. 密码哈希函数 ==========

def test_hash_password_function_exists():
    """应定义 hashPassword 函数，并使用 crypto.subtle.digest('SHA-256', ...)。"""
    html = read_html()
    assert re.search(r'function\s+hashPassword\s*\(', html), \
        "应定义 hashPassword 函数"
    assert "crypto.subtle.digest('SHA-256'" in html or \
           'crypto.subtle.digest("SHA-256"' in html, \
        "hashPassword 应使用 crypto.subtle.digest('SHA-256', ...)"


# ========== 4. register 为 async ==========

def test_register_is_async():
    """register 函数应为 async 函数。"""
    html = read_html()
    assert re.search(r'async\s+function\s+register\s*\(', html) or \
           re.search(r'register\s*=\s*async\s+function', html), \
        "register 应为 async 函数"


# ========== 5. login 为 async ==========

def test_login_is_async():
    """login 函数应为 async 函数。"""
    html = read_html()
    assert re.search(r'async\s+function\s+login\s*\(', html) or \
           re.search(r'login\s*=\s*async\s+function', html), \
        "login 应为 async 函数"


# ========== 6. saveUserData 为 async ==========

def test_saveUserData_is_async():
    """saveUserData 函数应为 async 函数。"""
    html = read_html()
    assert re.search(r'async\s+function\s+saveUserData\s*\(', html) or \
           re.search(r'saveUserData\s*=\s*async\s+function', html), \
        "saveUserData 应为 async 函数"


# ========== 7. 云端用户操作函数 ==========

def test_cloud_user_functions_exist():
    """应定义 fetchCloudUser、insertCloudUser、updateCloudUser 三个云端用户操作函数。"""
    html = read_html()
    for func in ['fetchCloudUser', 'insertCloudUser', 'updateCloudUser']:
        assert re.search(r'function\s+' + func + r'\s*\(', html) or \
               re.search(r'(?:const|let|var)\s+' + func + r'\s*=', html), \
            f"应定义 {func} 函数"


# ========== 8. 数据合并函数 ==========

def test_merge_functions_exist():
    """应定义 mergeErrors、mergeCustomQuestions、mergeStats 三个数据合并函数。"""
    html = read_html()
    for func in ['mergeErrors', 'mergeCustomQuestions', 'mergeStats']:
        assert re.search(r'function\s+' + func + r'\s*\(', html) or \
               re.search(r'(?:const|let|var)\s+' + func + r'\s*=', html), \
            f"应定义 {func} 函数"


# ========== 9. 离线回退逻辑 ==========

def test_offline_fallback():
    """应有 navigator.onLine 检查及 online/offline 事件监听。"""
    html = read_html()
    assert 'navigator.onLine' in html, "应检查 navigator.onLine 状态"
    assert re.search(r"addEventListener\(\s*['\"]online['\"]", html), \
        "应监听 online 事件"
    assert re.search(r"addEventListener\(\s*['\"]offline['\"]", html), \
        "应监听 offline 事件"


# ========== 10. 待同步机制 ==========

def test_pending_sync():
    """应有 pendingSync 标记及 retryPendingSync 函数。"""
    html = read_html()
    assert 'pendingSync' in html, "应存在 pendingSync 标记"
    assert re.search(r'function\s+retryPendingSync\s*\(', html), \
        "应定义 retryPendingSync 函数"


# ========== 11. 手动导入入口已隐藏 ==========

def test_manual_import_hidden():
    """'从其他设备导入账号'相关元素应有 display:none。"""
    html = read_html()
    # 定位"从其他设备导入账号"所在元素及其附近的 display:none
    idx = html.find('从其他设备导入账号')
    assert idx != -1, "应存在'从其他设备导入账号'文本（用于向后兼容）"
    # 向前查找 200 字符内的 display:none
    context = html[max(0, idx - 200):idx]
    assert 'display:none' in context or 'display: none' in context, \
        "'从其他设备导入账号'入口元素应有 display:none"


# ========== 12. 导出函数已标记废弃 ==========

def test_export_deprecated():
    """exportAccountData 函数应有 @deprecated 注释。"""
    html = read_html()
    func_idx = html.find('function exportAccountData')
    assert func_idx != -1, "应定义 exportAccountData 函数"
    # 查找函数定义前 200 字符内的 @deprecated 注释
    before = html[max(0, func_idx - 200):func_idx]
    assert '@deprecated' in before, \
        "exportAccountData 函数前应有 @deprecated 注释"


# ========== 13. 密码不再明文存储 ==========

def test_password_not_plaintext():
    """register 与 login 中均应使用 hashPassword 处理密码。"""
    html = read_html()
    # 定位 register 函数体
    reg_match = re.search(r'async\s+function\s+register\s*\([^)]*\)\s*\{', html)
    assert reg_match, "应存在 async function register"
    reg_start = reg_match.end()
    # 截取 register 函数体（向后取 3000 字符足够覆盖密码处理）
    reg_body = html[reg_start:reg_start + 3000]
    assert 'hashPassword' in reg_body, \
        "register 函数中应使用 hashPassword 处理密码"

    # 定位 login 函数体
    login_match = re.search(r'async\s+function\s+login\s*\([^)]*\)\s*\{', html)
    assert login_match, "应存在 async function login"
    login_start = login_match.end()
    login_body = html[login_start:login_start + 3000]
    assert 'hashPassword' in login_body, \
        "login 函数中应使用 hashPassword 验证哈希后的密码"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
