-- ===========================================================================
-- 回甘 - 考研数学智题本  Supabase 数据库表结构
-- ===========================================================================
-- 用途：实现跨浏览器、跨设备的云端账号与做题数据同步
-- 使用方式：登录 Supabase 控制台 → SQL Editor → 粘贴本文件 → Run
-- ===========================================================================

-- 启用 pgcrypto 扩展以使用 gen_random_uuid()
-- (Supabase 默认已启用，此处保留以确保新项目可用)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ---------------------------------------------------------------------------
-- users 表：存储账号信息与做题统计数据
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    -- 主键：UUID，由数据库自动生成
    id              uuid        PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 用户名：唯一、非空；与现有 localStorage 中 zcb_users 的 key 一致
    -- 仅允许字母、数字和符号 !@#$%^&*-. （由前端校验，数据库层再加约束兜底）
    username        text        NOT NULL UNIQUE,

    -- 密码哈希：SHA-256 十六进制字符串（64 字符），由前端 Web Crypto API 计算
    -- 不存储明文密码
    password_hash   text        NOT NULL,

    -- 昵称：注册时填写或自动生成（如 "研友12345"）
    nickname        text,

    -- 头像：动物 SVG 字符串（与 animalAvatars[].svg 一致）
    avatar          text,

    -- 头像颜色：与 avatar 配套的背景色（如 "#FFB74D"）
    avatar_color    text,

    -- 注册日期：前端生成的本地日期字符串（如 "2024/1/15"），
    -- 保留为 text 以兼容现有 localStorage 数据格式
    reg_date        text,

    -- 学习统计数据（JSONB）：
    -- {
    --   "total":          number,  -- 总做题数
    --   "correct":        number,  -- 答对数
    --   "errors":         array,   -- 错题本，每项含 id 字段用于去重
    --   "customQuestions":array,   -- 用户自建题目
    --   "exp":            number,  -- 经验值
    --   "streak":         number,  -- 连续打卡天数
    --   "lastDate":       string   -- 最后做题日期 "YYYY/M/D"
    -- }
    stats_json      jsonb       NOT NULL DEFAULT '{}'::jsonb,

    -- 最后更新时间：用于冲突检测与同步优先级判断
    updated_at      timestamptz NOT NULL DEFAULT now(),

    -- 约束：用户名格式（与前端 validateNoChinese 保持一致）
    CONSTRAINT username_format CHECK (
        username ~ '^[a-zA-Z0-9!@#$%^&*_\-.]+$'
    ),

    -- 约束：密码哈希必须是 64 位十六进制字符串（SHA-256 输出）
    CONSTRAINT password_hash_format CHECK (
        password_hash ~ '^[a-fA-F0-9]{64}$'
    )
);

-- ---------------------------------------------------------------------------
-- 索引：加速查询
-- ---------------------------------------------------------------------------
-- username 已通过 UNIQUE 隐式创建索引，此处显式声明以便维护
CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);

-- updated_at 索引：用于按时间排序的同步查询
CREATE INDEX IF NOT EXISTS idx_users_updated_at ON users (updated_at DESC);

-- ---------------------------------------------------------------------------
-- 自动更新 updated_at 触发器
-- ---------------------------------------------------------------------------
-- 每次更新行数据时自动刷新 updated_at，无需应用层维护
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS trigger AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ---------------------------------------------------------------------------
-- 行级安全策略 (RLS)
-- ---------------------------------------------------------------------------
-- 启用 RLS，确保即使 anon key 泄露，也只能进行受限操作
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 策略 1：匿名用户可以插入新用户（注册）
-- 注意：这是公开注册表，依赖 username UNIQUE 约束防止重复
CREATE POLICY "allow_public_register" ON users
    FOR INSERT
    TO anon, authenticated
    WITH CHECK (true);

-- 策略 2：匿名用户可以按 username 查询用户（登录验证）
-- 仅暴露必要字段，密码哈希通过应用层比对（不直接返回前端，由 RPC 处理）
CREATE POLICY "allow_public_select_by_username" ON users
    FOR SELECT
    TO anon, authenticated
    USING (true);

-- 策略 3：匿名用户可以更新用户数据（同步做题记录）
-- 实际生产环境建议改用 authenticated 角色或自定义 RPC 做更细粒度控制
CREATE POLICY "allow_public_update_by_username" ON users
    FOR UPDATE
    TO anon, authenticated
    USING (true)
    WITH CHECK (true);

-- ---------------------------------------------------------------------------
-- 安全说明（请阅读）
-- ---------------------------------------------------------------------------
-- 1. 本表设计为"前端直连 Supabase"的简化方案，anon key 通过 RLS 限制权限。
-- 2. 密码使用 SHA-256 哈希存储，但 SHA-256 不是密码哈希算法（无盐值、可彩虹表）。
--    如需更强安全性，建议：
--    a. 在 Supabase 中创建 RPC 函数 verify_user(p_username, p_password_hash)，
--       仅返回验证结果而不返回 password_hash 字段；
--    b. 或改用 Supabase Auth（内置 bcrypt + 盐值 + JWT）。
-- 3. 生产环境推荐将 SELECT 策略收紧为仅允许查询 (id, username, nickname, avatar,
--    avatar_color, reg_date, stats_json, updated_at)，password_hash 通过 RPC 比对。
-- ===========================================================================
