# 安装配置指南

## 环境要求

- Python 3.10+
- PostgreSQL 14+（需安装 pgvector 扩展）
- Redis 6+ （可选，用于 Celery 任务队列）
- 企业微信账号和客服应用

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/hg-tc/wx.git
cd wx
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置数据库

```bash
# 安装 PostgreSQL 和 pgvector
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql -c "CREATE EXTENSION vector;"

# 创建数据库
sudo -u postgres createdb wecom_agent
```

### 5. 配置环境变量

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost/wecom_agent

# 企业微信配置
WECOM_CORP_ID=your_corp_id
WECOM_AGENT_ID=your_agent_id
WECOM_SECRET=your_secret
WECOM_TOKEN=your_token
WECOM_ENCODING_AES_KEY=your_aes_key

# 客服应用配置
WECOM_KF_ACCOUNT_ID=your_kf_account_id
WECOM_KF_SECRET=your_kf_secret

# AI 引擎配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 应用配置
SECRET_KEY=your_secret_key
DEBUG=true
```

### 6. 初始化数据库

```bash
alembic upgrade head
```

### 7. 启动应用

#### 开发模式

```bash
./scripts/start_dev.sh
```

#### 生产模式

```bash
./scripts/deploy.sh
```

## 企业微信配置

### 1. 创建客服应用

1. 登录企业微信管理后台
2. 进入「应用管理」→「微信客服」
3. 创建新的客服账号
4. 获取 `open_kfid` 和 `Secret`

### 2. 配置回调地址

在企业微信后台配置：

- **回调 URL**: `https://your-domain.com/api/v1/wecom/callback`
- **Token**: 与 `.env` 中的 `WECOM_TOKEN` 一致
- **EncodingAESKey**: 与 `.env` 中的 `WECOM_ENCODING_AES_KEY` 一致

### 3. 配置接待模式

**重要**：必须设置为「仅智能助手接待」或「智能助手接待优先」

1. 进入「微信客服」→「接待设置」
2. 选择「仅智能助手接待」
3. 保存配置

### 4. IP 白名单

将服务器公网 IP 添加到企业微信 IP 白名单：

1. 进入企业微信管理后台
2. 「我的企业」→「企业信息」→「IP 白名单」
3. 添加服务器 IP

## 验证安装

```bash
# 测试 API
curl http://localhost:8000/health

# 查看日志
tail -f logs/app_*.log
```

## 常见问题

详见 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

