# API 文档

## 基础信息

- **Base URL**: `http://your-domain.com/api/v1`
- **Content-Type**: `application/json`
- **认证方式**: 企业微信签名验证

## 端点列表

### 企业微信回调

#### 验证回调 URL

```http
GET /wecom/callback
```

**查询参数**:
- `msg_signature`: 消息签名
- `timestamp`: 时间戳
- `nonce`: 随机数
- `echostr`: 验证字符串

**响应**:
```
<解密后的 echostr>
```

#### 接收消息/事件

```http
POST /wecom/callback
```

**查询参数**:
- `msg_signature`: 消息签名
- `timestamp`: 时间戳
- `nonce`: 随机数

**请求体**: XML 格式的加密消息

**响应**:
```
success
```

### 服务管理

#### 发布服务

```http
POST /services
```

**请求体**:
```json
{
  "title": "服务标题",
  "description": "服务描述",
  "category": "服务分类",
  "price": 100.00,
  "location": "服务地点"
}
```

**响应**:
```json
{
  "id": "service_id",
  "title": "服务标题",
  "status": "active",
  "created_at": "2025-11-20T10:00:00Z"
}
```

#### 搜索服务

```http
GET /services/search?q=关键词
```

**查询参数**:
- `q`: 搜索关键词
- `category`: 分类筛选（可选）
- `min_price`: 最低价格（可选）
- `max_price`: 最高价格（可选）

**响应**:
```json
{
  "results": [
    {
      "id": "service_id",
      "title": "服务标题",
      "description": "服务描述",
      "price": 100.00,
      "relevance_score": 0.95
    }
  ],
  "total": 10
}
```

### 比价购物

#### 商品比价

```http
POST /shopping/compare
```

**请求体**:
```json
{
  "product_name": "iPhone 15",
  "platforms": ["taobao", "xianyu"]
}
```

**响应**:
```json
{
  "product_name": "iPhone 15",
  "results": [
    {
      "platform": "taobao",
      "title": "Apple iPhone 15",
      "price": 5999.00,
      "url": "https://...",
      "shop_name": "Apple官方旗舰店"
    }
  ],
  "lowest_price": 5999.00
}
```

### 健康检查

#### 应用健康状态

```http
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-11-20T10:00:00Z"
}
```

## 会话状态说明

企业微信客服会话状态（`service_state`）:

| 状态码 | 状态名称 | 说明 | 是否可发送消息 |
|--------|---------|------|--------------|
| 0 | 新接入待处理 | 新会话，未分配 | ✅ 是 |
| 1 | 智能助手接待 | 由智能助手接待 | ✅ 是 |
| 2 | 待接入池排队 | 等待人工接入 | ❌ 否 |
| 3 | 人工接待中 | 人工接待中 | ❌ 否（API限制） |
| 4 | 已结束 | 会话已关闭 | ❌ 否 |

## 错误码

| 错误码 | 说明 | 解决方法 |
|--------|------|---------|
| 40058 | 缺少必需参数 | 检查请求参数完整性 |
| 45009 | API调用频率超限 | 等待1-2分钟后重试 |
| 95014 | 用户不是接待人员 | 检查servicer_userid |
| 95016 | 不允许的状态转换 | 检查会话状态和转换规则 |
| 95018 | 会话状态不允许发送 | 修改企业微信后台配置 |

## 示例代码

### Python

```python
import httpx

# 发布服务
async def publish_service():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://your-domain.com/api/v1/services",
            json={
                "title": "家政服务",
                "description": "专业家庭保洁",
                "category": "家政",
                "price": 100.00
            }
        )
        return response.json()
```

### JavaScript

```javascript
// 搜索服务
async function searchServices(keyword) {
  const response = await fetch(
    `http://your-domain.com/api/v1/services/search?q=${keyword}`
  );
  return await response.json();
}
```

### cURL

```bash
# 商品比价
curl -X POST http://your-domain.com/api/v1/shopping/compare \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "iPhone 15",
    "platforms": ["taobao", "xianyu"]
  }'
```

