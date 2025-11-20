# 企业微信智能客服系统

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

基于企业微信客服 API 的智能客服系统，集成 AI 对话、服务发布与匹配、商品比价等功能。

## ✨ 功能特性

### 🤖 智能对话
- **AI 驱动**: 使用 DeepSeek API 提供智能对话能力
- **意图识别**: 自动识别用户意图（服务发布、服务查找、商品比价等）
- **上下文管理**: 多轮对话上下文保持
- **向量检索**: 基于 pgvector 的语义搜索

### 💼 服务中介平台
- **服务发布**: 用户可发布各类服务需求
- **智能匹配**: 基于向量相似度的服务匹配
- **服务推荐**: 自动推荐相关服务
- **实时通知**: 匹配成功后实时通知双方

### 🛒 比价购物
- **多平台爬虫**: 支持淘宝、闲鱼等平台
- **价格对比**: 自动比较不同平台价格
- **智能排序**: 按价格、信誉等多维度排序

### 📊 企业微信集成
- **客服应用**: 完整支持企业微信客服 API
- **会话管理**: 自动管理客服会话状态
- **消息回调**: 实时接收用户消息
- **主动推送**: 支持向用户主动发送消息

## 🚀 快速开始

### 前置要求

- Python 3.10+
- PostgreSQL 14+ (需安装 pgvector 扩展)
- Redis 6+ (可选，用于 Celery)
- 企业微信账号和客服应用

### 安装

```bash
# 克隆项目
git clone https://github.com/hg-tc/wx.git
cd wx

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要配置

# 初始化数据库
alembic upgrade head

# 启动应用
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 配置企业微信

1. **创建客服应用**
   - 登录企业微信管理后台
   - 进入「应用管理」→「微信客服」
   - 创建新的客服账号

2. **获取客服账号ID (open_kfid)**
   ```bash
   # 运行获取脚本
   python scripts/get_kf_info.py
   ```
   将获取到的 `open_kfid` 填入 `.env` 文件的 `WECOM_KF_ACCOUNT_ID` 配置项

3. **配置回调地址**
   - URL: `https://your-domain.com/api/v1/wecom/callback`
   - 设置 Token 和 EncodingAESKey

4. **配置接待模式**
   - ⚠️ **重要**: 必须设置为「仅智能助手接待」
   - 否则会话状态会导致消息发送失败

4. **添加 IP 白名单**
   - 将服务器公网 IP 添加到企业微信白名单

详细配置请参考 [安装配置指南](docs/SETUP.md)

## 📖 文档

- [安装配置指南](docs/SETUP.md) - 详细的安装和配置步骤
- [API 文档](docs/API.md) - 完整的 API 接口说明
- [故障排查](docs/TROUBLESHOOTING.md) - 常见问题和解决方案

## 🏗️ 项目结构

```
wx/
├── app/                    # 应用主目录
│   ├── ai_engine/         # AI 引擎模块
│   │   ├── deepseek_client.py      # DeepSeek API 客户端
│   │   ├── dialogue_manager.py     # 对话管理
│   │   ├── intent_classifier.py    # 意图识别
│   │   └── embedding_service.py    # 向量嵌入服务
│   ├── api/               # API 路由
│   │   └── v1/
│   │       ├── wecom.py           # 企业微信回调
│   │       ├── services.py        # 服务管理
│   │       └── shopping.py        # 比价购物
│   ├── wecom/             # 企业微信集成
│   │   ├── kf_client.py           # 客服 API 客户端
│   │   ├── webhook.py             # Webhook 处理
│   │   └── message_builder.py     # 消息构建器
│   ├── service_broker/    # 服务中介
│   │   ├── matcher.py             # 服务匹配
│   │   └── recommender.py         # 服务推荐
│   ├── ecommerce_crawler/ # 电商爬虫
│   │   ├── taobao_api.py         # 淘宝 API
│   │   └── xianyu_crawler.py     # 闲鱼爬虫
│   ├── models/            # 数据模型
│   │   ├── user.py               # 用户模型
│   │   ├── service.py            # 服务模型
│   │   └── conversation.py       # 对话模型
│   └── main.py            # 应用入口
├── alembic/               # 数据库迁移
├── config/                # 配置文件模板
│   ├── nginx/            # Nginx 配置
│   └── systemd/          # Systemd 服务
├── docs/                  # 文档
├── scripts/               # 脚本工具
├── tests/                 # 测试
└── requirements.txt       # Python 依赖
```

## 🛠️ 技术栈

### 后端框架
- **FastAPI**: 现代、高性能的 Python Web 框架
- **SQLAlchemy**: ORM 和数据库工具
- **Alembic**: 数据库迁移工具

### 数据库
- **PostgreSQL**: 主数据库
- **pgvector**: 向量相似度搜索扩展
- **Redis**: 缓存和任务队列

### AI/ML
- **DeepSeek API**: 大语言模型
- **pgvector**: 向量嵌入和语义搜索

### 任务队列
- **Celery**: 异步任务处理
- **Redis**: Celery 消息代理

### 企业微信
- **企业微信客服 API**: 消息接收和发送
- **Webhook**: 事件回调处理

## 🔧 开发

### 运行测试

```bash
pytest
```

### 代码检查

```bash
# 安装开发依赖
pip install -r requirements-dev.txt

# 运行 linter
flake8 app/
black app/ --check
```

### 数据库迁移

```bash
# 创建迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## 📊 监控和日志

### 查看日志

```bash
# 应用日志
tail -f logs/app_*.log

# 错误日志
tail -f logs/error_*.log

# 搜索特定内容
tail -f logs/app_*.log | grep "关键词"
```

### 健康检查

```bash
curl http://localhost:8000/health
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [pgvector](https://github.com/pgvector/pgvector) - PostgreSQL 向量扩展
- [企业微信开放平台](https://developer.work.weixin.qq.com/) - 企业微信 API

## 📧 联系方式

- GitHub Issues: [https://github.com/hg-tc/wx/issues](https://github.com/hg-tc/wx/issues)
- 企业微信开发文档: [https://developer.work.weixin.qq.com/](https://developer.work.weixin.qq.com/)

## ⚠️ 重要提示

### 企业微信客服配置

**必须将接待模式设置为「仅智能助手接待」！**

如果设置为「人工接待优先」，会话会进入 `state=3`（人工接待），此时 `send_msg` API 无法发送消息。

**配置路径**：
企业微信后台 → 微信客服 → 接待设置 → 选择「仅智能助手接待」

### API 频率限制

企业微信客服 API 有频率限制（约每分钟 20 次），请注意：
- 避免频繁调用 API
- 实现合理的重试机制
- 使用日志监控 API 调用情况

### 日志管理

生产环境请配置日志轮转，避免日志文件过大：
- 使用 `logrotate` 或类似工具
- 定期清理旧日志
- 监控磁盘空间使用

---

**⭐ 如果这个项目对你有帮助，欢迎 Star！**
