# 使用指南

## 快速开始

### 1. 环境准备

确保已安装以下软件：
- Python 3.10+
- PostgreSQL 14+（含pgvector扩展）
- Redis 6.0+

### 2. 安装

```bash
# 克隆项目
cd /root/wx

# 运行安装脚本
chmod +x scripts/setup.sh
./scripts/setup.sh

# 编辑配置文件
nano .env
```

### 3. 配置DeepSeek API

在`.env`文件中配置：
```bash
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
```

获取API Key：访问 https://platform.deepseek.com/

### 4. 配置企业微信

#### 4.1 创建企业微信应用

1. 登录企业微信管理后台：https://work.weixin.qq.com/
2. 进入"应用管理" → "创建应用"
3. 填写应用信息并创建
4. 获取以下信息：
   - Corp ID（企业ID）
   - Agent ID（应用ID）
   - Secret（应用密钥）

#### 4.2 配置回调URL

1. 在应用详情页，进入"接收消息"配置
2. 填写回调URL：`https://your-domain.com/api/v1/wecom/callback`
3. 生成Token和EncodingAESKey（或自定义）
4. 保存配置（会自动验证URL）

#### 4.3 更新.env配置

```bash
WECOM_CORP_ID=ww1234567890abcdef
WECOM_AGENT_ID=1000001
WECOM_SECRET=your-secret-here
WECOM_TOKEN=your-token-here
WECOM_ENCODING_AES_KEY=your-aes-key-here
```

### 5. 启动服务

#### 开发模式

```bash
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 生产模式

```bash
# 使用systemd服务
sudo systemctl start wecom-api
sudo systemctl start wecom-celery
sudo systemctl start wecom-celery-beat

# 查看状态
sudo systemctl status wecom-api
```

## 功能使用

### 服务中介功能

#### 1. 发布供应服务

在企业微信中发送消息：
```
我可以提供Python后端开发服务，擅长FastAPI和Django，5年经验，价格面议
```

系统会：
1. 识别意图为"供应服务"
2. 提取关键信息（服务类型、描述、标签等）
3. 生成向量embedding
4. 保存到数据库
5. 自动查找匹配的需求
6. 发送匹配结果

#### 2. 发布需求服务

在企业微信中发送消息：
```
我需要找一个能做微信小程序开发的，要求熟悉uniapp，预算5000-10000元
```

系统会：
1. 识别意图为"需求服务"
2. 提取需求信息
3. 自动匹配供应服务
4. 推送匹配结果

#### 3. 查看匹配结果

发送消息：
```
查看我的服务记录
```

或
```
我的服务
```

系统会返回您发布的所有服务及其状态。

### 购物比价功能

#### 1. 搜索商品

在企业微信中发送消息：
```
帮我找iPhone 15 Pro 256G
```

或
```
搜索小米手环8
```

系统会：
1. 识别意图为"购物比价"
2. 提取商品关键词
3. 并发搜索多个平台（淘宝、咸鱼等）
4. 比对价格
5. 返回最优惠结果

#### 2. 查看比价结果

系统会自动发送格式化的比价结果：
```
🛒 商品比价结果：

⭐ **iPhone 15 Pro 256GB**
🏪 平台：淘宝
💵 价格：¥7999（优惠券：¥200）
💰 到手价：**¥7799** 🏆 最优惠
🔗 [查看详情](https://...)

2. **iPhone 15 Pro 256GB**
🏪 平台：咸鱼
💰 到手价：**¥7850**
🔗 [查看详情](https://...)
```

### 帮助功能

发送以下任一消息获取帮助：
```
帮助
```
```
怎么用
```
```
help
```

系统会返回完整的功能说明。

## API使用

### 访问API文档

启动服务后，访问：
- Swagger UI: http://your-domain.com/docs
- ReDoc: http://your-domain.com/redoc

### 直接调用API

#### 1. 创建供应服务

```bash
curl -X POST "http://localhost:8000/api/v1/services/supply" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-uuid",
    "service_type": "supply",
    "title": "Python开发服务",
    "description": "提供Python后端开发",
    "category": "技术开发",
    "price_range": "500-1000元/天",
    "tags": ["Python", "FastAPI", "后端"]
  }'
```

#### 2. 搜索商品

```bash
curl -X POST "http://localhost:8000/api/v1/shopping/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "iPhone 15",
    "use_cache": true
  }'
```

#### 3. 获取统计数据

```bash
curl -X GET "http://localhost:8000/api/v1/admin/analytics"
```

## 高级配置

### 配置淘宝联盟API

1. 注册淘宝联盟：https://pub.alimama.com/
2. 创建应用获取AppKey和AppSecret
3. 在`.env`中配置：

```bash
TAOBAO_APP_KEY=your-app-key
TAOBAO_APP_SECRET=your-app-secret
```

### 配置代理池

如果需要爬虫使用代理：

```bash
CRAWLER_PROXY_POOL=http://proxy-service.com/api/proxy
```

### 调整Embedding服务

默认使用简单的哈希向量（仅用于开发），生产环境建议：

#### 方案1：使用OpenAI Embedding

在`app/ai_engine/embedding_service.py`中启用：
```python
from openai import AsyncOpenAI
client = AsyncOpenAI(api_key="your-openai-key")
response = await client.embeddings.create(
    model="text-embedding-ada-002",
    input=text
)
return response.data[0].embedding
```

#### 方案2：使用本地模型

安装sentence-transformers：
```bash
pip install sentence-transformers
```

在`embedding_service.py`中：
```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
embedding = model.encode(text)
return embedding.tolist()
```

### 性能调优

#### 1. 调整Worker数量

编辑`config/systemd/wecom-api.service`：
```ini
-w 8  # 根据CPU核心数调整
```

#### 2. 调整Celery并发

编辑`config/systemd/wecom-celery.service`：
```ini
--concurrency=8  # 根据需要调整
```

#### 3. 优化数据库

```sql
-- 增加共享内存
ALTER SYSTEM SET shared_buffers = '256MB';

-- 增加工作内存
ALTER SYSTEM SET work_mem = '16MB';

-- 重启PostgreSQL生效
sudo systemctl restart postgresql
```

## 常见问题

### Q1: 企业微信回调验证失败

**原因**：Token或EncodingAESKey配置错误

**解决**：
1. 检查`.env`中的配置是否与企业微信后台一致
2. 确保服务已启动且可以公网访问
3. 查看日志：`tail -f /root/wx/logs/app_*.log`

### Q2: DeepSeek API调用失败

**原因**：API Key错误或余额不足

**解决**：
1. 检查API Key是否正确
2. 访问DeepSeek平台检查余额
3. 查看详细错误：`tail -f /root/wx/logs/error_*.log`

### Q3: 向量检索不工作

**原因**：pgvector扩展未安装或索引未创建

**解决**：
```sql
-- 检查扩展
\c wecom_db
SELECT * FROM pg_extension WHERE extname = 'vector';

-- 如果没有，安装
CREATE EXTENSION vector;

-- 创建索引
CREATE INDEX idx_services_embedding 
ON services USING ivfflat (embedding vector_cosine_ops);
```

### Q4: Celery任务不执行

**原因**：Redis未启动或配置错误

**解决**：
```bash
# 检查Redis
sudo systemctl status redis-server

# 测试连接
redis-cli ping

# 重启Celery
sudo systemctl restart wecom-celery
```

### Q5: 爬虫超时

**原因**：网络问题或被反爬虫

**解决**：
1. 增加超时时间：`.env`中设置`CRAWLER_TIMEOUT=60`
2. 配置代理池
3. 降低并发：`CRAWLER_MAX_CONCURRENT=3`

## 日志查看

### 应用日志

```bash
# 实时查看
tail -f /root/wx/logs/app_*.log

# 查看错误
tail -f /root/wx/logs/error_*.log

# 查看Celery
tail -f /root/wx/logs/celery-*.log
```

### 系统日志

```bash
# API服务
sudo journalctl -u wecom-api -f

# Celery服务
sudo journalctl -u wecom-celery -f
```

## 数据库管理

### 创建备份

```bash
pg_dump -U wecom wecom_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 恢复备份

```bash
psql -U wecom wecom_db < backup_20250119_120000.sql
```

### 查看数据

```bash
psql -U wecom wecom_db

-- 查看服务数量
SELECT type, status, COUNT(*) FROM services GROUP BY type, status;

-- 查看匹配数量
SELECT status, COUNT(*) FROM matches GROUP BY status;

-- 查看用户数量
SELECT COUNT(*) FROM users;
```

## 监控

### 健康检查

```bash
curl http://localhost:8000/health
```

### 查看队列状态

```bash
# 进入Redis
redis-cli

# 查看队列长度
LLEN celery

# 查看所有key
KEYS *
```

## 更新部署

```bash
cd /root/wx
git pull
./scripts/deploy.sh
```

## 安全建议

1. **定期更新**：及时更新系统和依赖包
2. **强密码**：使用强密码保护数据库和Redis
3. **防火墙**：只开放必要端口（80, 443）
4. **HTTPS**：使用SSL证书加密通信
5. **备份**：定期备份数据库
6. **监控**：设置异常告警

## 技术支持

- 查看文档：README.md, ARCHITECTURE.md, DEPLOYMENT.md
- 查看日志：/root/wx/logs/
- GitHub Issues：<your-repo-url>/issues

---

祝使用愉快！🎉

