# 免费云端部署方案与后端账号容量评估

## 一、项目架构分析

当前项目是一个**纯前端单文件Web应用**（`回甘—考研数学智题本.html`，约3.2MB），架构特点：

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | HTML+CSS+JS（单文件） | 含题库、知识库、UI、渲染逻辑 |
| 本地存储 | localStorage（7个key） | 用户数据、设置、AI对话历史 |
| 云端后端 | Supabase（PostgreSQL） | 用户账号同步、stats_json |

## 二、免费云端部署方案推荐

### 方案1：Cloudflare Pages（推荐）

| 项目 | 详情 |
|------|------|
| 免费额度 | 无限带宽、无限请求、500次构建/月 |
| 适用性 | ★★★★★ 纯静态网站，完美匹配 |
| 优点 | 全球CDN、速度快、无限带宽、自定义域名 |
| 缺点 | 需要注册Cloudflare账号 |
| 部署方式 | 拖拽上传HTML文件即可 |

### 方案2：GitHub Pages

| 项目 | 详情 |
|------|------|
| 免费额度 | 100GB/月流量、1GB存储 |
| 适用性 | ★★★★★ 纯静态网站 |
| 优点 | 与Git集成、自动部署、HTTPS支持 |
| 缺点 | 单文件3.2MB接近建议上限（建议<1GB） |
| 部署方式 | 创建GitHub仓库→上传文件→启用Pages |

### 方案3：Vercel

| 项目 | 详情 |
|------|------|
| 免费额度 | 100GB/月流量、无限静态部署 |
| 适用性 | ★★★★★ 纯静态网站 |
| 优点 | 自动部署、全球CDN、速度快 |
| 缺点 | 免费计划有商业用途限制 |
| 部署方式 | 连接Git仓库或拖拽上传 |

### 方案4：Netlify

| 项目 | 详情 |
|------|------|
| 免费额度 | 100GB/月流量、300分钟构建时间 |
| 适用性 | ★★★★★ 纯静态网站 |
| 优点 | 拖拽部署、表单处理、自定义域名 |
| 缺点 | 免费计划有月活限制 |
| 部署方式 | 拖拽上传HTML文件 |

## 三、推荐部署步骤（以Cloudflare Pages为例）

### 步骤1：准备文件
```bash
# 文件已准备好：/Users/wuyangcj/trae/回甘demo/回甘—考研数学智题本.html
# 重命名为 index.html（便于直接访问根路径）
cp 回甘—考研数学智题本.html index.html
```

### 步骤2：部署到Cloudflare Pages
1. 访问 https://dash.cloudflare.com → Pages
2. 点击"Create a project" → "Upload assets"
3. 拖拽 `index.html` 文件上传
4. 点击"Deploy site"
5. 获得 `https://xxx.pages.dev` 的访问地址

### 步骤3：配置Supabase后端（云端账号同步）
当前代码已配置Supabase（行44370-44371）：
```javascript
const SUPABASE_URL = 'https://fqjcygttgtcnpiilpubd.supabase.co';
const SUPABASE_KEY = 'sb_publishable_KUvUv-b-tKWI67X9CVcLcA_sz7LMW6s';
```

**需要在Supabase控制台创建users表**（测试时发现表不存在报错 PGRST205）：

```sql
-- 在Supabase SQL Editor中执行
CREATE TABLE IF NOT EXISTS public.users (
    username TEXT PRIMARY KEY,
    nickname TEXT,
    avatar TEXT,
    avatar_color TEXT,
    stats_json JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 启用行级安全
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- 允许所有操作（简单方案，生产环境建议细化权限）
CREATE POLICY "Enable all for all users" ON public.users
    FOR ALL USING (true) WITH CHECK (true);
```

## 四、后端账号容量评估

### Supabase免费计划容量

| 资源 | 免费额度 | 本项目预估用量 | 可支撑用户数 |
|------|----------|---------------|-------------|
| 月活用户（MAU） | 50,000 | 每用户1条记录 | **50,000用户** |
| 数据库大小 | 500 MB | 每用户约2-5KB | **10万-25万用户** |
| 流量（egress） | 5 GB/月 | 每用户约2KB/次同步 | **~250万次同步** |
| 文件存储 | 1 GB | 不使用 | - |
| API请求 | 无限 | - | - |

### 实际可支撑用户数分析

**瓶颈分析：**
1. **MAU限制**：50,000月活用户 → 这是主要限制
2. **数据库大小**：每用户约2-5KB（stats_json含做题记录、错题、自建题目）
   - 50,000用户 × 5KB = 250MB < 500MB ✓
3. **流量**：假设每用户每天同步1次，每次2KB
   - 50,000用户 × 30天 × 2KB = 3GB < 5GB ✓

**结论：免费计划可支撑约50,000月活用户**

### 如果用户量超过免费额度

升级到Supabase Pro计划（$25/月）：
- 100,000 MAU（超出后 $0.00325/MAU）
- 8GB数据库（超出后 $0.125/GB）
- 250GB流量（超出后 $0.09/GB）

## 五、注意事项

### 1. 免费计划限制
- Supabase免费项目**1周不活动会暂停**（需定期访问唤醒）
- 最多2个活跃项目

### 2. 当前代码需要修复的问题
- Supabase的users表未创建（测试时报错 PGRST205）
- 需要在Supabase控制台执行上面的SQL创建表

### 3. 数据安全建议
- 当前RLS策略允许所有操作，生产环境建议细化
- 可考虑只允许用户操作自己的记录（按username过滤）

### 4. 备份建议
- 用户数据同时存储在localStorage和Supabase，即使Supabase暂停，本地数据仍可用
- 建议定期导出Supabase数据库备份

## 六、总结

| 项目 | 推荐方案 | 预估可支撑用户数 |
|------|----------|-----------------|
| 前端托管 | Cloudflare Pages（免费） | 无限（纯静态） |
| 后端账号 | Supabase Free（免费） | **50,000月活用户** |
| 总成本 | ¥0 | - |

这个方案完全免费，足以支撑中小型应用的用户量。当用户量增长到5万月活以上时，再考虑升级到Supabase Pro计划（$25/月）。
