# 脚本使用说明

本目录包含企业微信智能客服系统的所有管理脚本。

## 📋 目录

- [安装脚本](#安装脚本)
- [服务管理](#服务管理)
- [工具脚本](#工具脚本)
- [服务架构](#服务架构)

---

## 🚀 安装脚本

### `setup.sh` - 快速安装
简化的安装脚本，适合开发环境。

```bash
./scripts/setup.sh
```

**包含功能：**
- 创建 Python 虚拟环境
- 安装依赖
- 自动安装和启动 Redis
- 安装 Playwright 浏览器
- 创建配置文件
- 数据库迁移

---

### `setup_complete.sh` - 完整安装
完整的生产环境安装脚本，适合容器环境。

```bash
./scripts/setup_complete.sh
```

**包含功能：**
- 系统依赖安装（Nginx、Redis等）
- PostgreSQL 数据库安装和配置
- Python 环境配置
- Nginx 反向代理配置
- 自动启动所有服务

---

### `install_postgresql.sh` - 数据库安装
单独安装和配置 PostgreSQL 数据库。

```bash
sudo ./scripts/install_postgresql.sh
```

**包含功能：**
- 安装 PostgreSQL 14
- 安装 pgvector 扩展
- 创建数据库和用户
- 初始化数据库表结构

---

## 🔧 服务管理

### `start_services.sh` - 启动所有服务 ⭐

**最常用的启动脚本**，按顺序启动所有必需服务。

```bash
./scripts/start_services.sh
```

**启动顺序：**
1. ✅ Redis 服务（消息队列）
2. ✅ Nginx 服务（反向代理）
3. ✅ FastAPI 应用（主服务）
4. ✅ Celery Worker（异步任务）

**输出示例：**
```
==========================================
启动服务
==========================================

【1/4】Redis 服务
  ✅ Redis 已启动

【2/4】Nginx 服务
  ✅ Nginx 已启动

【3/4】FastAPI 应用
  ✅ 应用已启动 (PID: 12345)
  ✅ 健康检查通过

【4/4】Celery Worker
  ✅ Celery Worker 已启动 (56 workers)

==========================================
✅ 服务启动完成
==========================================

📊 服务状态：
  - Redis:         ✅ 运行中
  - Nginx:         ✅ 运行中
  - FastAPI:       ✅ 运行中
  - Celery:        ✅ 运行中
```

---

### `stop_services.sh` - 停止服务

安全停止服务（保留 Redis）。

```bash
./scripts/stop_services.sh
```

**停止顺序：**
1. Celery Worker
2. FastAPI 应用
3. Nginx 服务
4. Redis 服务（询问是否停止）

**特点：**
- 会询问是否停止 Redis（默认保留，避免影响其他应用）
- 优雅停止（先尝试正常停止，失败后强制停止）
- 自动清理 PID 文件

---

### `stop_all.sh` - 停止所有服务

非交互式停止所有服务（包括 Redis）。

```bash
./scripts/stop_all.sh
```

**使用场景：**
- 完全关闭系统
- 系统维护
- 容器重启前

---

### `restart_services.sh` - 重启服务

快速重启应用（不停止 Redis）。

```bash
./scripts/restart_services.sh
```

**重启内容：**
- Celery Worker
- FastAPI 应用
- Nginx 服务

**不重启：**
- Redis（保持运行，避免中断）

---

### `status.sh` - 查看服务状态 ⭐

**最常用的状态检查脚本**，显示详细的服务运行状态。

```bash
./scripts/status.sh
```

**显示信息：**
- ✅ 各服务运行状态（Redis、Nginx、FastAPI、Celery）
- 🔌 端口监听情况
- 💾 内存使用情况
- 💿 磁盘使用情况
- 📄 最近日志（最新5条）
- 🔧 管理命令提示

**输出示例：**
```
==========================================
服务状态
==========================================

【1/4】Redis 服务
  状态: ✅ 运行中
  PID: 12345
  端口: 6379
  连接测试: ✅ 通过 (PONG)

【2/4】FastAPI 应用
  状态: ✅ 运行中
  PID: 12346
  端口: 8000
  健康检查: ✅ 通过

【3/4】Celery Worker
  状态: ✅ 运行中
  Workers: 56 个
  主进程 PID: 12347
  就绪状态: ✅ Ready

【4/4】Nginx 服务
  状态: ✅ 运行中
  PID: 12348
  端口: 13000, 80
  转发测试: ✅ 通过
```

---

## 🛠️ 工具脚本

### `get_kf_info.py` - 获取客服账号信息

获取企业微信客服账号 ID（open_kfid）。

```bash
python scripts/get_kf_info.py
```

**用途：**
- 获取客服账号列表
- 查看客服账号详细信息
- 用于配置 `WECOM_KF_ACCOUNT_ID`

---

### `test_kf_message.py` - 测试客服消息

测试发送客服消息功能。

```bash
python scripts/test_kf_message.py
```

**测试内容：**
- access_token 获取
- 客服账号状态
- 消息发送功能

---

### `test_wecom_callback.py` - 测试回调接口

测试企业微信回调接口。

```bash
python scripts/test_wecom_callback.py
```

---

### `config_wizard.sh` - 配置向导

交互式配置向导，帮助填写 `.env` 配置文件。

```bash
./scripts/config_wizard.sh
```

---

### `diagnose.sh` - 系统诊断

诊断系统问题，检查配置和环境。

```bash
./scripts/diagnose.sh
```

---

## 📊 服务架构

```
┌─────────────────────────────────────────┐
│       服务启动顺序和依赖关系              │
└─────────────────────────────────────────┘

1️⃣  Redis (端口 6379)
    ↓
    └─── 必需，Celery 依赖
         └─── Celery Worker
              ↓
              └─── 处理异步任务
                   - 商品比价爬虫
                   - 服务匹配

2️⃣  Nginx (端口 13000)
    ↓
    └─── 反向代理
         └─── 转发到 FastAPI

3️⃣  FastAPI (端口 8000)
    ↓
    └─── 主应用服务
         ├─── 企业微信回调
         ├─── AI 对话
         ├─── 服务管理
         └─── API 接口

4️⃣  Celery Worker
    ↓
    └─── 后台任务处理
         ├─── crawl_products (爬虫)
         ├─── match_service (匹配)
         ├─── batch_match_services (批量匹配)
         └─── clean_expired_* (清理任务)
```

---

## 🎯 常用操作

### 首次安装

```bash
# 1. 完整安装
./scripts/setup_complete.sh

# 2. 配置环境变量
nano .env

# 3. 启动服务
./scripts/start_services.sh
```

---

### 日常运维

```bash
# 查看服务状态
./scripts/status.sh

# 查看实时日志
tail -f logs/app_*.log          # 应用日志
tail -f logs/uvicorn.log        # Uvicorn日志
tail -f logs/celery.log         # Celery日志

# 重启服务
./scripts/restart_services.sh

# 停止服务
./scripts/stop_services.sh
```

---

### 故障排查

```bash
# 1. 检查服务状态
./scripts/status.sh

# 2. 查看错误日志
tail -100 logs/error_*.log

# 3. 诊断系统
./scripts/diagnose.sh

# 4. 测试健康检查
curl http://localhost:8000/health

# 5. 测试 Redis 连接
redis-cli ping

# 6. 测试数据库连接
psql -U wecom_user -d wecom_db -c "SELECT 1"
```

---

### 更新代码后

```bash
# 1. 停止服务
./scripts/stop_services.sh

# 2. 拉取代码
git pull

# 3. 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 4. 数据库迁移
alembic upgrade head

# 5. 重启服务
./scripts/start_services.sh
```

---

## ⚠️ 注意事项

### Redis 管理

- **重启时不停止 Redis**：避免影响其他应用或缓存数据丢失
- **完全停止**：使用 `./scripts/stop_all.sh` 停止包括 Redis 在内的所有服务
- **手动停止 Redis**：`redis-cli shutdown`
- **手动启动 Redis**：`redis-server --daemonize yes`

### Celery Worker

- **依赖 Redis**：必须先启动 Redis
- **并发数**：默认根据 CPU 核心数自动设置
- **任务监控**：查看 `logs/celery.log` 了解任务执行情况

### 服务依赖

```
PostgreSQL ─── FastAPI ─┬─── 用户请求
                        └─── Celery 任务
Redis ────────── Celery
Nginx ────────── FastAPI
```

### 端口占用

- **6379**: Redis
- **8000**: FastAPI 应用
- **13000**: Nginx 反向代理
- **5432**: PostgreSQL 数据库

---

## 📚 更多文档

- [README.md](../README.md) - 项目概述
- [docs/SETUP.md](../docs/SETUP.md) - 详细安装指南
- [docs/API.md](../docs/API.md) - API 文档
- [docs/TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md) - 故障排查

---

## 🤝 贡献

如果您发现脚本有问题或需要改进，欢迎提交 Issue 或 Pull Request！

---

**最后更新：** 2025-11-20

