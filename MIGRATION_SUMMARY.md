# Vercel + Supabase 迁移完成总结

## 📋 完成的工作

### 1. **创建 SQLAlchemy 数据库抽象层** (`api/db.py`)

- 使用 SQLAlchemy 2.0 创建统一的数据库访问接口
- 支持 PostgreSQL（Supabase）
- 实现了 4 个核心函数：
  - `fetchone(sql, params)` - 查询单行
  - `fetchall(sql, params)` - 查询多行
  - `execute(sql, params)` - 执行 UPDATE/DELETE
  - `insert_returning_id(sql, params)` - INSERT 并返回新 ID
- 连接字符串从环境变量 `DATABASE_URL` 读取

### 2. **将 `api/app.py` 从 pymysql 迁移到 SQLAlchemy**

转换统计：
- ✓ 移除 22 处 `get_db_connection()` 调用
- ✓ 移除 146 处 `cursor.` 操作
- ✓ 转换 70 处 SQL 占位符（`%s` → `:key`）
- ✓ 更新所有表名为带双引号格式（`"user"`, `"dict"` 等）
- ✓ 所有 70 处新 SQL 查询使用命名参数风格

**已转换函数** (18 个)：
- 用户管理：`check_auth`, `inject_auth_context`, `api_register`, `api_login`, `api_get_user`, `api_update_user`, `api_admin_check`, `api_admin_users`, `api_admin_reset_password`, `api_admin_delete_user`, `api_admin_restore_user`
- 字典管理：`api_get_dicts`, `api_create_dict`, `api_update_dict`, `api_delete_dict`
- 词汇管理：`api_get_words`, `api_create_word`, `api_update_word`, `api_delete_word`
- CSV 操作：`api_import_csv`, `api_export_csv`
- 游戏管理：`api_game_create`, `api_game_list`, `api_game_get`, `api_game_join`, `api_game_leave`, `api_game_start`, `api_game_answer`, `api_game_end`

### 3. **更新依赖** (`requirements.txt`)

```
Flask==3.0.3
psycopg2-binary==2.9.6      # PostgreSQL 驱动
SQLAlchemy==2.0.22          # ORM 框架
python-dotenv==1.0.0        # 环境变量管理
```

### 4. **创建迁移文档** (`SUPABASE_MIGRATION.md`)

包含：
- Supabase 项目创建步骤
- 数据库表结构创建脚本（SQL）
- Vercel 环境变量配置步骤
- 本地测试方法
- 部署流程
- 常见问题解决方案

## 🚀 后续部署步骤

### 第 1 步：创建 Supabase 项目（2-3 分钟）

1. 访问 [https://supabase.com](https://supabase.com)
2. 创建新项目（记住数据库密码）
3. 进入 SQL Editor 执行 `SUPABASE_MIGRATION.md` 中的 SQL 脚本创建表

### 第 2 步：在 Vercel 配置环境变量

1. 进入 Vercel 项目 Settings → Environment Variables
2. 添加 `DATABASE_URL` (Supabase 连接字符串)
   - 需要在所有环境（Production、Preview、Development）中添加
3. **必须重新部署**才能使用新变量

### 第 3 步：部署

```bash
# 本地提交并推送
git add .
git commit -m "Migrate to SQLAlchemy + Supabase"
git push origin main

# Vercel 会自动部署
```

### 第 4 步：验证

部署完成后，测试以下功能：

```bash
# 1. 注册新用户
curl -X POST https://your-vercel-app.vercel.app/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"password123"}'

# 2. 登录
curl -X POST https://your-vercel-app.vercel.app/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"password123"}'

# 3. 访问首页
curl https://your-vercel-app.vercel.app/
```

## 📊 重要变更

| 项目 | 旧方案 | 新方案 |
|------|--------|--------|
| **数据库** | MySQL (mysql2.sqlpub.com) | PostgreSQL (Supabase) |
| **驱动** | pymysql | psycopg2 |
| **ORM** | 原生 cursor 调用 | SQLAlchemy |
| **表名** | 无引号 (user, dict) | 双引号 ("user", "dict") |
| **SQL 占位符** | %s | :key（命名参数） |
| **连接管理** | 每个请求创建连接 | SQLAlchemy 连接池 |
| **环境变量** | DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME | DATABASE_URL |

## ⚠️ 注意事项

### 1. **连接限制**

Supabase 免费级别默认最多 3 并发连接。如遇问题：

- 启用 **PgBouncer** (Supabase Settings → Database → Connection Pooling)
- 选择 **Transaction** 模式
- 使用 PgBouncer 连接字符串（通常是 `:6543` 端口）

### 2. **冷启动延迟**

Vercel Serverless 函数可能在长时间未使用后冷启动。首次连接会慢一些，这是正常的。

### 3. **数据迁移**

如果需要从旧 MySQL 导入数据：

```sql
-- 方法1：通过 CSV 导入
-- 在 Supabase SQL Editor 中使用 COPY 命令

-- 方法2：使用 pgloader（高级）
pgloader --from mysql://user:pass@host/db \
         --to postgresql://user:pass@host/db
```

### 4. **开发环境**

本地开发需要 `.env` 文件（不提交到 Git）：

```bash
# .env (本地，不要提交)
DATABASE_URL=postgresql://postgres:PASSWORD@HOST:5432/postgres
```

## ✅ 验证清单

在部署前检查：

- [ ] `api/db.py` 存在，包含 4 个数据库方法
- [ ] `requirements.txt` 包含 SQLAlchemy、psycopg2-binary、python-dotenv
- [ ] `api/app.py` 中无 `get_db_connection()` 或 `cursor.` 调用
- [ ] 所有 SQL 使用命名参数 (`:key` 格式)
- [ ] 表名都用双引号 (`"user"`, `"dict"` 等)
- [ ] Python 语法检查通过：`python3 -m py_compile api/app.py api/db.py`
- [ ] Supabase 项目已创建，数据库表结构已初始化
- [ ] Vercel 环境变量 `DATABASE_URL` 已配置

## 🔗 相关文件

| 文件 | 说明 |
|------|------|
| `api/db.py` | SQLAlchemy 数据库抽象层（新文件） |
| `api/app.py` | Flask 应用（已迁移） |
| `requirements.txt` | Python 依赖（已更新） |
| `vercel.json` | Vercel 配置（无需改动） |
| `SUPABASE_MIGRATION.md` | 详细迁移指南 |
| `.env` | 本地环境变量（git 忽略） |

## 📞 常见错误排查

### "ModuleNotFoundError: No module named 'psycopg2'"

**解决**: 确保 `requirements.txt` 在 Vercel 部署时被读取。检查 Vercel 部署日志。

### "SSL certificate problem"

**解决**: Supabase 连接字符串需要 SSL。确保字符串包含 `?sslmode=require`。

### "database '<dbname>' does not exist"

**解决**: Supabase 默认数据库是 `postgres`。检查连接字符串中的数据库名。

### 登录后无法创建字典

**解决**: 检查 Vercel 日志（Deployments → Logs）获取具体数据库错误。

## 👍 完成！

代码已完全迁移到 SQLAlchemy 和 Supabase。下一步是按照上述步骤部署到生产环境。

有任何问题，参考 `SUPABASE_MIGRATION.md` 或检查 Vercel 构建/运行时日志。
