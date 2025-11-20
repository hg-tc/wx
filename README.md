# 企业微信智能客服中介系统

基于 Python、DeepSeek、PostgreSQL 和企业微信 API 构建的智能客服中介系统，实现供需服务匹配和多平台商品比价功能。

## 🚀 快速开始

```bash
# 一键安装（自动安装所有依赖并启动服务）
cd /root/wx
./scripts/setup_complete.sh

# 配置企业微信参数
./scripts/config_wizard.sh

# 查看服务状态
./scripts/status.sh
```

📖 **详细指南**: 
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - 快速参考
- [WECOM_SETUP.md](WECOM_SETUP.md) - 企业微信配置
- [WECOM_KF_SETUP.md](WECOM_KF_SETUP.md) - **客服应用配置**（推荐）

## 功能特性

### 1. 服务中介功能
- 📝 服务供应录入：用户可发布提供的服务
- 🔍 服务需求录入：用户可发布需要的服务
- 🤖 智能匹配：基于向量相似度的智能供需匹配
- 📊 推荐排序：多维度综合评分排序

### 2. 电商比价功能
- 🛒 多平台搜索：支持淘宝、咸鱼、微信小商店
- 💰 价格比对：自动比对多平台价格
- 🔗 链接推送：自动发送最优惠链接
- ⚡ 异步爬取：高效的异步爬虫系统

### 3. AI 对话能力
- 💬 意图识别：自动识别用户意图
- 🎯 实体提取：提取关键信息
- 🔄 上下文管理：维护对话上下文
- 🌟 自然响应：基于 DeepSeek 的自然语言生成

### 4. 客服应用支持
- 🤖 **自动接待**：24小时智能客服，无需人工介入
- 👥 **外部客户**：支持外部客户通过企业微信客服与AI对话
- 🔄 **双模式**：同时支持内部员工应用和外部客服应用
- 📱 **多场景**：适用于企业内部协作和外部客户服务

## 技术架构

### 核心技术栈
- **后端框架**: FastAPI + Uvicorn
- **数据库**: PostgreSQL 14+ with pgvector
- **AI能力**: DeepSeek API + LangChain
- **企业微信**: WeChatPy SDK
- **爬虫**: Scrapy + Playwright + BeautifulSoup
- **任务队列**: Celery + Redis
- **ORM**: SQLAlchemy 2.0
- **日志**: Loguru

### 系统架构图
```
企业微信客户端
    ↓
接入层 (FastAPI)
    ↓
AI对话引擎 (DeepSeek)
    ↓
服务中介模块 / 电商爬虫模块
    ↓
数据存储层 (PostgreSQL + pgvector)
    ↓
任务队列层 (Celery + Redis)
```

## 快速开始

### 环境要求
- Python 3.10+
- PostgreSQL 14+ (with pgvector extension)
- Redis 6.0+

### 安装步骤

1. **克隆项目**
```bash
cd /opt
sudo git clone <your-repo-url> wecom-agent
cd wecom-agent
```

2. **创建虚拟环境**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **安装 Playwright 浏览器**
```bash
playwright install chromium
```

5. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入实际配置
nano .env
```

6. **初始化数据库**
```bash
# 确保 PostgreSQL 已安装 pgvector 扩展
psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 运行数据库迁移
alembic upgrade head
```

7. **启动服务**

开发模式：
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

生产模式：
```bash
# 启动 API 服务
sudo systemctl start wecom-api

# 启动 Celery Worker
sudo systemctl start wecom-celery

# 启动 Celery Beat
sudo systemctl start wecom-celery-beat
```

## 项目结构

```
/opt/wecom-agent/
├── app/                          # 应用代码
│   ├── main.py                   # FastAPI 主应用
│   ├── config.py                 # 配置管理
│   ├── database.py               # 数据库连接
│   ├── models/                   # 数据库模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── service.py
│   │   ├── conversation.py
│   │   └── product.py
│   ├── wecom/                    # 企业微信模块
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── webhook.py
│   │   ├── message_builder.py
│   │   └── auth.py
│   ├── ai_engine/                # AI引擎模块
│   │   ├── __init__.py
│   │   ├── deepseek_client.py
│   │   ├── intent_classifier.py
│   │   ├── entity_extractor.py
│   │   ├── embedding_service.py
│   │   ├── dialogue_manager.py
│   │   └── prompts/
│   ├── service_broker/           # 服务中介模块
│   │   ├── __init__.py
│   │   ├── service_manager.py
│   │   ├── matcher.py
│   │   ├── recommender.py
│   │   └── notification.py
│   ├── ecommerce_crawler/        # 电商爬虫模块
│   │   ├── __init__.py
│   │   ├── base_crawler.py
│   │   ├── taobao_api.py
│   │   ├── xianyu_crawler.py
│   │   ├── wechat_shop.py
│   │   ├── price_comparator.py
│   │   └── anti_crawler.py
│   ├── tasks/                    # Celery任务
│   │   ├── __init__.py
│   │   ├── celery_app.py
│   │   ├── crawler_tasks.py
│   │   └── matcher_tasks.py
│   ├── api/                      # API路由
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── wecom.py
│   │   │   ├── services.py
│   │   │   ├── shopping.py
│   │   │   └── admin.py
│   └── utils/                    # 工具函数
│       ├── __init__.py
│       ├── logger.py
│       └── security.py
├── alembic/                      # 数据库迁移
│   ├── versions/
│   └── env.py
├── logs/                         # 日志目录
├── tests/                        # 测试文件
├── scripts/                      # 部署脚本
│   └── deploy.sh
├── .env                          # 环境变量
├── .env.example                  # 环境变量模板
├── requirements.txt              # 依赖列表
├── alembic.ini                   # Alembic配置
└── README.md                     # 说明文档
```

## API 文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 数据库管理

### 创建迁移
```bash
alembic revision --autogenerate -m "描述信息"
```

### 应用迁移
```bash
alembic upgrade head
```

### 回滚迁移
```bash
alembic downgrade -1
```

## 监控和日志

### 查看日志
```bash
# API 日志
tail -f /opt/wecom-agent/logs/access.log
tail -f /opt/wecom-agent/logs/error.log

# Celery 日志
tail -f /opt/wecom-agent/logs/celery-worker.log
```

### 服务状态
```bash
# 查看服务状态
sudo systemctl status wecom-api
sudo systemctl status wecom-celery
sudo systemctl status wecom-celery-beat

# 重启服务
sudo systemctl restart wecom-api
```

## 部署

详细部署步骤请参考 `scripts/deploy.sh` 脚本。

### Systemd 服务配置
- `/etc/systemd/system/wecom-api.service` - API 服务
- `/etc/systemd/system/wecom-celery.service` - Celery Worker
- `/etc/systemd/system/wecom-celery-beat.service` - Celery Beat

### Nginx 配置
- `/etc/nginx/sites-available/wecom-agent` - Nginx 反向代理配置

## 安全性

- ✅ 企业微信消息签名验证
- ✅ API 接口鉴权
- ✅ 敏感数据加密存储
- ✅ SQL 注入防护
- ✅ XSS 防护
- ✅ 请求频率限制

## 许可证

MIT License

## 作者

企业微信智能客服团队

