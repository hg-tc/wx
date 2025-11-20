# 🚀 快速开始指南

本指南帮助你快速配置和启动企业微信智能客服中介系统。

## ✅ 问题已修复

之前的 `binascii.Error: Invalid base64-encoded string` 错误已经修复！

**原因**：`WECOM_ENCODING_AES_KEY` 长度不正确（40位，应该是43位）

**解决**：已更新为正确的43位AES Key

## 📝 当前配置状态

配置文件：`/root/wx/.env`

```bash
# 查看当前企业微信配置
cat /root/wx/.env | grep WECOM
```

**临时配置值**（测试用）：
- Token: `bX80Ww2YBZS28y0qUxqgyA`
- EncodingAESKey: `RJOvPEZSXMfyRzwCL+nt/fvjL/WNKQlgGwjMVESuQMM` ✅ 43位

**注意**：这些是临时生成的测试值，配置企业微信时需要使用企业微信后台生成的真实值。

## 🎯 三步启动

### 步骤1: 验证配置

```bash
cd /root/wx
source venv/bin/activate
python scripts/test_wecom_callback.py
```

**预期输出**：
```
✅ 所有测试通过！配置正确！
```

### 步骤2: 启动应用

**方法A: 使用启动脚本（推荐）**
```bash
./scripts/start_dev.sh
```

启动脚本会自动：
- ✅ 检查配置
- ✅ 检查端口占用
- ✅ 停止旧进程（如果有）
- ✅ 启动新应用
- ✅ 显示配置参数

**方法B: 手动启动**
```bash
cd /root/wx
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤3: 验证运行

**测试接口：**
```bash
# 根路径
curl http://localhost:8000/

# 健康检查
curl http://localhost:8000/health

# API文档（用浏览器访问）
http://localhost:8000/docs
```

## 🌐 配置企业微信回调

### 场景A: 本地开发（使用ngrok）

#### 1. 安装ngrok
访问：https://ngrok.com/
下载并安装

#### 2. 启动内网穿透
```bash
# 新开一个终端
ngrok http 8000
```

你会得到一个公网HTTPS地址，如：
```
https://abc123def456.ngrok-free.app
```

#### 3. 在企业微信后台配置

1. 登录：https://work.weixin.qq.com/wework_admin/
2. 进入「应用管理」→ 选择应用
3. 找到「接收消息」配置：

**填写参数：**
- **URL**: `https://abc123def456.ngrok-free.app/api/v1/wecom/callback`
- **Token**: `bX80Ww2YBZS28y0qUxqgyA`（从.env复制）
- **EncodingAESKey**: `RJOvPEZSXMfyRzwCL+nt/fvjL/WNKQlgGwjMVESuQMM`（从.env复制）

4. 点击「保存」

**重要**：每次重启ngrok都会得到新的URL，需要重新配置！

#### 4. 测试

在企业微信中向应用发送消息："帮助"

应该收到自动回复！🎉

### 场景B: 生产部署（使用真实域名）

#### 1. 准备域名和服务器
- 域名：如 `api.yourdomain.com`
- 服务器：公网可访问的Linux服务器
- SSL证书：使用 Let's Encrypt 免费证书

#### 2. 配置SSL证书
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
```

#### 3. 配置Nginx

已提供配置文件：`/root/wx/config/nginx/wecom-agent`

```bash
# 复制配置
sudo cp /root/wx/config/nginx/wecom-agent /etc/nginx/sites-available/wecom-agent
sudo ln -s /etc/nginx/sites-available/wecom-agent /etc/nginx/sites-enabled/

# 修改域名
sudo nano /etc/nginx/sites-available/wecom-agent
# 将 api.yourdomain.com 改为你的真实域名

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

#### 4. 配置systemd服务
```bash
# 复制服务文件
sudo cp /root/wx/config/systemd/*.service /etc/systemd/system/

# 重新加载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start wecom-api
sudo systemctl enable wecom-api

# 检查状态
sudo systemctl status wecom-api
```

#### 5. 在企业微信后台配置

**填写参数：**
- **URL**: `https://api.yourdomain.com/api/v1/wecom/callback`
- **Token**: 从你的 `.env` 文件复制
- **EncodingAESKey**: 从你的 `.env` 文件复制

## 🔑 获取企业微信真实配置参数

### 1. 企业ID（Corp ID）
- 位置：企业微信管理后台 → 「我的企业」→ 「企业信息」
- 格式：`ww1234567890abcdef`

### 2. 应用ID（Agent ID）
- 位置：「应用管理」→ 选择应用 → 应用详情页
- 格式：`1000002`（纯数字）

### 3. 应用密钥（Secret）
- 位置：应用详情页，点击「查看」
- 格式：43个字符的字符串

### 4. Token 和 EncodingAESKey

**选项A：使用企业微信生成**
在「接收消息」配置页面：
- Token：可以自己填写（3-32位字符）
- EncodingAESKey：点击「随机生成」按钮

**选项B：自己生成**
```bash
cd /root/wx
python3 << 'EOF'
import base64
import os
import secrets

# 生成43位AES Key
random_bytes = os.urandom(32)
aes_key = base64.b64encode(random_bytes).decode('utf-8').rstrip('=')
print(f"EncodingAESKey: {aes_key}")

# 生成Token
token = secrets.token_urlsafe(16)
print(f"Token: {token}")
EOF
```

### 5. 更新 .env 文件

```bash
nano /root/wx/.env
```

修改企业微信相关配置：
```env
WECOM_CORP_ID=你的企业ID
WECOM_AGENT_ID=你的应用ID
WECOM_SECRET=你的应用密钥
WECOM_TOKEN=你的Token
WECOM_ENCODING_AES_KEY=你的43位AES Key
```

**保存后重启应用！**

## 🔍 故障排查

### 问题1: "回调地址请求不通过"

**检查清单：**
```bash
# 1. 验证配置
python scripts/test_wecom_callback.py

# 2. 确认应用运行
ps aux | grep uvicorn

# 3. 测试本地回调
curl http://localhost:8000/api/v1/wecom/callback

# 4. 检查日志
tail -f /root/wx/logs/app_*.log
```

**详细排查**：查看 `TROUBLESHOOTING.md`

### 问题2: 端口已被占用

```bash
# 查看占用进程
lsof -i :8000

# 停止旧进程
kill $(lsof -t -i :8000)

# 或使用启动脚本（自动处理）
./scripts/start_dev.sh
```

### 问题3: 配置错误

```bash
# 重新生成配置
python3 << 'EOF'
import base64, os, secrets
print(f"Token: {secrets.token_urlsafe(16)}")
print(f"AESKey: {base64.b64encode(os.urandom(32)).decode().rstrip('=')}")
EOF

# 更新 .env
nano /root/wx/.env

# 重新测试
python scripts/test_wecom_callback.py
```

## 📚 相关文档

- **WECOM_SETUP.md** - 企业微信详细配置指南
- **TROUBLESHOOTING.md** - 完整故障排查指南
- **DEPLOYMENT.md** - 生产环境部署指南
- **ARCHITECTURE.md** - 技术架构文档
- **USAGE.md** - 功能使用手册

## 🎓 常用命令

```bash
# 测试配置
python scripts/test_wecom_callback.py

# 启动开发服务器
./scripts/start_dev.sh

# 查看日志
tail -f logs/app_*.log

# 查看进程
ps aux | grep uvicorn

# 查看端口
lsof -i :8000

# API文档（浏览器访问）
http://localhost:8000/docs

# 停止服务（开发环境）
# 按 Ctrl+C

# 停止服务（生产环境）
sudo systemctl stop wecom-api
```

## ✨ 下一步

配置完企业微信后，你可以：

1. **测试服务中介功能**
   - 发送："我可以提供搬家服务"
   - 发送："我需要搬家服务"
   - 系统自动匹配并通知

2. **测试购物比价功能**
   - 发送："我要买 iPhone 15"
   - 系统爬取多平台价格
   - 返回最优惠链接

3. **测试对话功能**
   - 发送："帮助"
   - 发送："你能做什么"
   - 发送："我的服务列表"

4. **查看管理后台**
   - API文档：http://localhost:8000/docs
   - 服务管理：`/api/v1/services/`
   - 用户管理：`/api/v1/admin/users`

## 🎉 总结

问题已完全解决！现在你可以：

✅ 应用正常启动（无配置错误）
✅ 配置验证全部通过
✅ 回调接口正常工作
✅ 完整的故障排查工具
✅ 详细的配置文档

开始使用吧！🚀

