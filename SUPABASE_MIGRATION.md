# Supabase 数据库迁移指南

## 步骤 1: 在 Supabase 创建项目

1. 访问 [https://supabase.com](https://supabase.com) 并注册/登录
2. 点击 **New Project**
3. 填写：
   - **Name**: `wordmachine` (或任何你喜欢的名字)
   - **Database Password**: 自动生成或自定义（记住这个！）
   - **Region**: 选择离你最近的区域（如 `us-east-1` 或 `ap-southeast-1`）
4. 点击 **Create New Project** 并等待初始化完成（~2分钟）

## 步骤 2: 获取连接信息

1. 进入项目 Dashboard
2. 点击左侧 **Settings** → **Database**
3. 找到 **Connection string** 部分，选择 **URI** 标签
4. 复制 PostgreSQL 连接字符串，形式如：
   ```
   postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
   ```

   postgresql://postgres:[YOUR_PASSWORD]@db.awaeitychaggcxpwimrl.supabase.co:5432/postgres

## 步骤 3: 创建数据库表结构

在 Supabase Dashboard 中打开 **SQL Editor**，执行以下 SQL 脚本创建表：

```sql
-- 创建 user 表
CREATE TABLE IF NOT EXISTS "user" (
  id SERIAL PRIMARY KEY,
  username VARCHAR(255) NOT NULL UNIQUE,
  pwhash VARCHAR(255) NOT NULL,
  introduction TEXT DEFAULT '',
  rating INTEGER DEFAULT 0,
  type VARCHAR(50) DEFAULT 'normal',
  deleted BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建 dict 表
CREATE TABLE IF NOT EXISTS dict (
  id SERIAL PRIMARY KEY,
  dictname VARCHAR(255) NOT NULL,
  deleted BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建 word 表
CREATE TABLE IF NOT EXISTS word (
  id SERIAL PRIMARY KEY,
  dictid INTEGER NOT NULL REFERENCES dict(id),
  english VARCHAR(255) NOT NULL,
  chinese VARCHAR(255) NOT NULL,
  deleted BOOLEAN DEFAULT false,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建 game 表
CREATE TABLE IF NOT EXISTS game (
  id SERIAL PRIMARY KEY,
  dictid INTEGER REFERENCES dict(id),
  users JSON DEFAULT '[]',
  wordlist JSON DEFAULT '[]',
  result JSON DEFAULT '[]',
  status INTEGER DEFAULT -1,
  perf JSON,
  ownerid INTEGER REFERENCES "user"(id),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 步骤 4: 在 Vercel 配置环境变量

1. 进入 Vercel Dashboard → 你的项目 → **Settings** → **Environment Variables**
2. 添加以下环境变量（Production、Preview、Development 都添加）：

   ```
   DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
   ```

   其中 `[PASSWORD]` 和 `[HOST]` 从 Supabase 连接字符串复制。

3. **重要**：点击 **Save** 后，需要重新部署才能使用新的环境变量。

## 步骤 5: 本地测试（可选）

在本地 `.env` 文件中添加（不要提交到 Git）：

```bash
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
```

然后运行：

```bash
pip install -r requirements.txt
export FLASK_APP=api/app.py
export DATABASE_URL=<你的Supabase连接字符串>
python -m flask run
```

访问 `http://localhost:5000` 测试。

## 步骤 6: 部署到 Vercel

```bash
git add .
git commit -m "Migrate to SQLAlchemy and Supabase"
git push origin main
```

Vercel 会自动部署。部署完成后，访问你的生产 URL 并测试：

- 注册新用户
- 登录
- 创建词典和单词
- 玩游戏

## 常见问题

### 1. "connection refused" 或 "ssl certificate problem"

**解决**：Supabase 连接字符串通常包含 SSL 模式。确保在连接字符串末尾添加：

```
?sslmode=require
```

### 2. "password authentication failed"

**解决**：检查 `[PASSWORD]` 是否正确，特殊字符是否需要 URL 编码。

### 3. 在 Vercel 上部署后仍无法连接数据库

**解决**：
- 确认环境变量已添加并已重新部署（部署历史中会显示新的构建）
- 检查 Supabase 项目是否仍在运行（Dashboard 中查看）
- 查看 Vercel 的 **Functions** 日志了解具体错误

### 4. 迁移现有数据

如果你的旧 MySQL 数据库中有数据，可以：

1. **导出** 旧数据为 CSV 或 SQL dump
2. **导入** 到 Supabase（通过 SQL Editor 或使用工具如 `pgloader`）

## 数据库连接池设置（高级）

如果遇到"too many connections"错误，可以在 Supabase 中配置 **PgBouncer**：

1. 进入 Supabase Dashboard → **Settings** → **Database** → **Connection Pooling**
2. 启用 PgBouncer，选择 **Transaction** 模式
3. 使用 PgBouncer 提供的连接字符串（通常端口是 6543）

然后在 Vercel 环境变量中使用该字符串。

## 参考资源

- [Supabase 官方文档](https://supabase.com/docs)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Vercel Python 函数指南](https://vercel.com/docs/serverless-functions/python)
