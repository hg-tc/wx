# 企业微信配置指南

本指南将详细说明如何配置企业微信，使其能够与智能客服中介系统对接。

## 📋 配置流程概览

```
注册企业微信 → 创建应用 → 配置接收消息 → 获取配置参数 → 更新.env文件
```

## 1️⃣ 注册企业微信

### 如果还没有企业微信

1. 访问：https://work.weixin.qq.com/
2. 点击「注册」
3. 选择企业类型：
   - 中小企业
   - 个体工商户
   - 个人（用于测试）
4. 完成手机验证和企业信息填写
5. 记录**企业ID（Corp ID）**

### 查看企业ID

登录企业微信管理后台后：
- 进入「我的企业」→ 「企业信息」
- 找到「企业ID」，格式类似：`ww1234567890abcdef`

## 2️⃣ 创建自建应用

### 步骤

1. 登录企业微信管理后台：https://work.weixin.qq.com/wework_admin/
2. 进入「应用管理」→「自建」
3. 点击「创建应用」
4. 填写应用信息：
   - **应用名称**：智能客服中介系统
   - **应用Logo**：上传一个图标
   - **可见范围**：选择需要使用的成员
5. 点击「创建应用」

### 获取配置信息

创建完成后，在应用详情页可以看到：

- **AgentId**（应用ID）：纯数字，如 `1000002`
- **Secret**（应用密钥）：点击「查看」获取，格式：`Abc123...`（43个字符）

## 3️⃣ 配置接收消息服务器

这是最关键的一步！

### 3.1 确定回调URL

**格式**：`https://你的域名/api/v1/wecom/callback`

**示例**：
```
https://api.example.com/api/v1/wecom/callback
https://wecom.yourdomain.com/api/v1/wecom/callback
```

**重要提示**：
- ✅ 必须是 **HTTPS**（企业微信强制要求）
- ✅ 必须是**公网可访问**的域名或IP
- ✅ 端口必须是 **443**（HTTPS默认端口）
- ❌ 不能使用 `http://`
- ❌ 不能使用 `localhost` 或 `127.0.0.1`
- ❌ 不能使用内网IP

### 3.2 生成Token和EncodingAESKey

在应用详情页，找到「接收消息」配置：

1. **URL**：填写你的回调URL（上面确定的）

2. **Token**：随机字符串（3-32位）
   ```bash
   # 生成Token的方法
   python3 -c "import secrets; print(secrets.token_urlsafe(16))"
   # 示例输出：TqK8JxN_4mHgWoP2
   ```

3. **EncodingAESKey**：43位随机字符串
   - 可以点击「随机生成」按钮
   - 或者手动生成：
   ```bash
   # 生成EncodingAESKey的方法（必须是43位）
   python3 -c "import secrets; print(secrets.token_urlsafe(32)[:43])"
   # 示例输出：abcdefghijklmnopqrstuvwxyz0123456789ABCD
   ```

### 3.3 验证URL

**重要**：在保存配置前，企业微信会向你的URL发送验证请求！

#### 准备工作

1. 确保应用已经部署到服务器
2. 确保 `.env` 文件已填写正确的Token和EncodingAESKey
3. 确保应用正在运行
4. 确保域名能正常访问

#### 验证步骤

```bash
# 1. 更新.env文件（填入真实值）
nano /root/wx/.env

# 修改以下配置：
WECOM_CORP_ID=你的企业ID
WECOM_AGENT_ID=你的应用ID
WECOM_SECRET=你的应用密钥
WECOM_TOKEN=你生成的Token
WECOM_ENCODING_AES_KEY=你生成的43位Key

# 2. 重启应用
cd /root/wx
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. 在企业微信后台点击「保存」
# 系统会自动验证URL，验证通过后配置生效
```

## 4️⃣ 本地开发环境配置

如果你在本地开发，无法直接配置HTTPS回调URL，有以下几种方案：

### 方案A：使用内网穿透工具（推荐）

#### 使用 ngrok

```bash
# 1. 安装 ngrok（访问 https://ngrok.com/）

# 2. 启动应用
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. 启动 ngrok 穿透
ngrok http 8000

# 4. ngrok 会给你一个公网HTTPS地址，如：
# https://abc123.ngrok.io

# 5. 在企业微信配置回调URL：
# https://abc123.ngrok.io/api/v1/wecom/callback
```

#### 使用 localtunnel

```bash
# 1. 安装
npm install -g localtunnel

# 2. 启动穿透
lt --port 8000 --subdomain mywecom

# 3. 获得地址：https://mywecom.loca.lt
```

### 方案B：部署到云服务器

推荐使用：
- 阿里云ECS
- 腾讯云CVM
- AWS EC2
- DigitalOcean

配置SSL证书（免费）：
```bash
# 使用 Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 5️⃣ 完整配置示例

### .env 文件配置

```bash
# 企业微信配置（替换为你的真实值）
WECOM_CORP_ID=ww1234567890abcdef           # 企业ID（从"我的企业"获取）
WECOM_AGENT_ID=1000002                      # 应用ID（应用详情页）
WECOM_SECRET=Abc123Def456Ghi789Jkl012      # 应用密钥（应用详情页，点击查看）
WECOM_TOKEN=TqK8JxN_4mHgWoP2                # 自己生成的Token
WECOM_ENCODING_AES_KEY=abcdefghijk12345678 # 企业微信生成或自己生成（43位）
```

### Nginx配置（生产环境）

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 6️⃣ 测试配置

### 测试回调URL

```bash
# 1. 查看日志
tail -f /root/wx/logs/app_*.log

# 2. 在企业微信中向应用发送消息
# 应该能在日志中看到接收到的消息

# 3. 测试API文档
# 访问：https://your-domain.com/docs
```

### 测试消息收发

1. 在企业微信中找到创建的应用
2. 点击「发消息」
3. 发送一条测试消息，如：「帮助」
4. 应该收到系统的自动回复

## 7️⃣ 常见问题

### Q1: URL验证失败

**原因**：
- URL不可访问
- Token/EncodingAESKey配置错误
- 应用未运行

**解决**：
```bash
# 1. 检查应用是否运行
ps aux | grep uvicorn

# 2. 检查端口是否监听
netstat -tlnp | grep 8000

# 3. 检查.env配置
cat /root/wx/.env | grep WECOM

# 4. 测试URL可访问性
curl -I https://your-domain.com/api/v1/wecom/callback

# 5. 查看应用日志
tail -f /root/wx/logs/app_*.log
```

### Q2: 收不到消息

**原因**：
- 应用可见范围未包含当前用户
- 接收消息未开启

**解决**：
1. 进入应用管理 → 可见范围
2. 确保当前用户在范围内
3. 检查「接收消息」配置是否已保存

### Q3: EncodingAESKey格式错误

**要求**：
- 必须是43位字符
- Base64编码格式
- 只能包含字母、数字、`+`、`/`

**正确生成方法**：
```python
import base64
import os

# 生成32字节随机数据
random_bytes = os.urandom(32)
# Base64编码
aes_key = base64.b64encode(random_bytes).decode('utf-8')
print(aes_key)  # 输出43位字符
```

### Q4: 本地开发无法配置HTTPS

**解决方案**：
1. 使用 ngrok/localtunnel 等内网穿透工具
2. 在本地配置自签名证书（企业微信可能不信任）
3. 部署到测试服务器

## 8️⃣ 配置检查清单

使用前请确认：

- [ ] 企业微信已注册并获取Corp ID
- [ ] 已创建自建应用并获取Agent ID和Secret
- [ ] 已生成Token（3-32位）
- [ ] 已生成EncodingAESKey（43位）
- [ ] 回调URL使用HTTPS协议
- [ ] 回调URL可以公网访问
- [ ] .env文件已更新所有配置
- [ ] 应用已启动并正常运行
- [ ] 企业微信后台URL验证已通过
- [ ] 可见范围已设置

## 9️⃣ 获取帮助

如果遇到问题：

1. 查看应用日志：`tail -f /root/wx/logs/app_*.log`
2. 查看错误日志：`tail -f /root/wx/logs/error_*.log`
3. 检查系统日志：`journalctl -u wecom-api -f`
4. 企业微信开发文档：https://developer.work.weixin.qq.com/document/

## 📱 快速开始示例

最简单的测试流程：

```bash
# 1. 使用 ngrok 创建临时HTTPS地址
ngrok http 8000
# 获得：https://abc123.ngrok.io

# 2. 在企业微信配置
URL: https://abc123.ngrok.io/api/v1/wecom/callback
Token: test_token_123
EncodingAESKey: （点击随机生成）

# 3. 更新本地.env
WECOM_TOKEN=test_token_123
WECOM_ENCODING_AES_KEY=（企业微信生成的43位key）

# 4. 启动应用
cd /root/wx
source venv/bin/activate
uvicorn app.main:app --reload

# 5. 在企业微信保存配置（会自动验证）

# 6. 发送测试消息
在企业微信中向应用发送："帮助"
```

完成以上步骤后，您的企业微信智能客服系统就配置好了！🎉

