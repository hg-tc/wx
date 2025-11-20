# 企业微信回调地址故障排查指南

当企业微信后台提示"回调地址请求不通过"时，按照以下步骤逐一排查。

## 📋 问题分类

### 类型1: URL验证失败
- 表现：企业微信后台点击"保存"时提示验证失败
- 原因：服务器无法访问 或 配置参数错误

### 类型2: 收不到消息
- 表现：URL验证通过，但发送消息后没有回复
- 原因：消息处理逻辑错误 或 数据库连接问题

## 🔍 排查步骤

### 步骤1: 检查配置文件

```bash
cd /root/wx
cat .env | grep WECOM
```

**检查清单：**
- [ ] `WECOM_TOKEN` 已填写（和企业微信后台一致）
- [ ] `WECOM_ENCODING_AES_KEY` 长度必须是 **43位**（和企业微信后台一致）
- [ ] `WECOM_CORP_ID` 是你的企业ID（从"我的企业"获取）
- [ ] `WECOM_AGENT_ID` 是应用ID（从应用详情页获取）
- [ ] `WECOM_SECRET` 是应用密钥（从应用详情页获取）

**验证配置：**
```bash
cd /root/wx
source venv/bin/activate
python scripts/test_wecom_callback.py
```

### 步骤2: 检查应用是否运行

```bash
# 检查进程
ps aux | grep uvicorn

# 检查端口
netstat -tlnp | grep 8000

# 或使用 lsof
lsof -i :8000
```

**如果没有运行，启动应用：**
```bash
cd /root/wx
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 步骤3: 测试本地回调

**方法A: 使用测试脚本生成的curl命令**
```bash
# 1. 运行测试脚本
python scripts/test_wecom_callback.py

# 2. 复制输出的curl命令并执行
# 应该返回: test_echo
```

**方法B: 手动测试基本连通性**
```bash
# 测试根路径
curl http://localhost:8000/

# 测试API文档
curl http://localhost:8000/docs

# 测试健康检查
curl http://localhost:8000/health
```

### 步骤4: 检查网络和域名

#### 4.1 本地开发环境

**问题**：企业微信无法访问 localhost 或内网IP

**解决方案A: 使用 ngrok**
```bash
# 1. 安装 ngrok (https://ngrok.com/)
# 2. 启动穿透
ngrok http 8000

# 3. 获得公网地址，如: https://abc123.ngrok.io
# 4. 企业微信配置URL: https://abc123.ngrok.io/api/v1/wecom/callback
```

**解决方案B: 使用 localtunnel**
```bash
# 1. 安装
npm install -g localtunnel

# 2. 启动
lt --port 8000

# 3. 获得地址: https://xxx.loca.lt
```

#### 4.2 生产环境

**检查域名解析：**
```bash
# 测试域名是否解析
nslookup your-domain.com

# 测试HTTPS访问
curl -I https://your-domain.com/api/v1/wecom/callback
```

**检查防火墙：**
```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 443/tcp

# CentOS/RHEL
sudo firewall-cmd --list-all
sudo firewall-cmd --add-service=https --permanent
sudo firewall-cmd --reload
```

**检查Nginx：**
```bash
# 检查Nginx状态
sudo systemctl status nginx

# 测试配置
sudo nginx -t

# 查看日志
sudo tail -f /var/log/nginx/error.log
```

### 步骤5: 检查HTTPS证书

企业微信**强制要求HTTPS**，检查证书是否有效：

```bash
# 检查证书有效期
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates

# 测试HTTPS访问
curl -v https://your-domain.com/api/v1/wecom/callback
```

**如果没有证书，使用 Let's Encrypt（免费）：**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 步骤6: 检查应用日志

```bash
# 查看应用日志
tail -f /root/wx/logs/app_*.log

# 查看错误日志
tail -f /root/wx/logs/error_*.log

# 如果使用systemd
journalctl -u wecom-api -f
```

**常见错误：**

#### 错误1: `binascii.Error: Invalid base64-encoded string`
```
原因：WECOM_ENCODING_AES_KEY 长度不是43位
解决：重新生成43位的AES Key
```

#### 错误2: `签名验证失败`
```
原因：Token 不匹配
解决：确保 .env 中的 WECOM_TOKEN 和企业微信后台一致
```

#### 错误3: `解密echo_str失败`
```
原因：EncodingAESKey 不匹配
解决：确保 .env 中的 WECOM_ENCODING_AES_KEY 和企业微信后台一致
```

## 🎯 企业微信后台配置步骤

### 1. 生成配置参数

**在服务器上生成：**
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

### 2. 更新 .env 文件

```bash
nano /root/wx/.env
```

修改以下配置：
```env
WECOM_CORP_ID=你的企业ID
WECOM_AGENT_ID=你的应用ID
WECOM_SECRET=你的应用密钥
WECOM_TOKEN=上面生成的Token
WECOM_ENCODING_AES_KEY=上面生成的43位AES Key
```

### 3. 重启应用

```bash
cd /root/wx
source venv/bin/activate

# 开发环境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产环境（使用systemd）
sudo systemctl restart wecom-api
```

### 4. 在企业微信后台配置

1. 登录企业微信管理后台
2. 进入「应用管理」→ 选择应用
3. 找到「接收消息」配置：
   - **URL**: `https://你的域名/api/v1/wecom/callback`
   - **Token**: 粘贴刚才生成的Token
   - **EncodingAESKey**: 粘贴刚才生成的43位AES Key
4. 点击「保存」

**重要**：点击保存时，企业微信会立即向你的URL发送验证请求！

### 5. 验证是否成功

如果看到「保存成功」，说明配置正确。

**测试方法：**
1. 在企业微信中找到应用
2. 发送消息："帮助"
3. 应该收到系统自动回复

## 🔧 常见问题解决

### Q1: 使用ngrok但企业微信验证失败

**原因**：ngrok免费版URL会变化

**解决**：
1. 每次启动ngrok都会得到新的URL
2. 需要在企业微信后台重新配置新的URL
3. 或者购买ngrok付费版获得固定域名

### Q2: 本地测试通过，但企业微信验证失败

**可能原因：**
1. 本地和企业微信的Token/AES Key不一致
2. 服务器时间不同步
3. 网络问题导致企业微信无法访问

**解决**：
```bash
# 同步服务器时间
sudo ntpdate -u ntp.ubuntu.com

# 或使用
sudo timedatectl set-ntp on
```

### Q3: 验证通过，但收不到消息

**检查**：
1. 应用的「可见范围」是否包含当前用户
2. 是否已启用「接收消息」
3. 查看应用日志是否有错误

```bash
tail -f /root/wx/logs/app_*.log
```

### Q4: 提示"请求超时"

**原因**：服务器响应太慢（企业微信有5秒超时限制）

**解决**：
1. 优化代码性能
2. 将耗时操作放入后台任务
3. 立即返回"success"，异步处理消息

### Q5: Token或AES Key包含特殊字符导致配置错误

**注意**：
- Token: 只能包含字母、数字、下划线、连字符
- AES Key: Base64格式（字母、数字、+、/）

如果.env中包含特殊字符，使用引号：
```env
WECOM_TOKEN="your-token-here"
WECOM_ENCODING_AES_KEY="your-aes-key-here"
```

## 📱 快速测试流程

```bash
# 1. 验证配置
cd /root/wx
source venv/bin/activate
python scripts/test_wecom_callback.py

# 2. 启动应用
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. 新终端，启动ngrok
ngrok http 8000

# 4. 复制ngrok提供的HTTPS地址
# 如: https://abc123.ngrok.io

# 5. 在企业微信后台配置
# URL: https://abc123.ngrok.io/api/v1/wecom/callback
# Token: (从 test_wecom_callback.py 输出中复制)
# EncodingAESKey: (从 test_wecom_callback.py 输出中复制)

# 6. 点击保存，等待验证

# 7. 验证通过后，在企业微信发送消息测试
```

## 🆘 仍然无法解决？

### 收集诊断信息

```bash
cd /root/wx

# 创建诊断报告
cat > diagnostic_report.txt << 'EOF'
=== 系统信息 ===
EOF

echo "操作系统: $(uname -a)" >> diagnostic_report.txt
echo "Python版本: $(python --version)" >> diagnostic_report.txt
echo "" >> diagnostic_report.txt

echo "=== 配置信息 ===" >> diagnostic_report.txt
cat .env | grep WECOM >> diagnostic_report.txt
echo "" >> diagnostic_report.txt

echo "=== 进程状态 ===" >> diagnostic_report.txt
ps aux | grep uvicorn >> diagnostic_report.txt
echo "" >> diagnostic_report.txt

echo "=== 端口监听 ===" >> diagnostic_report.txt
netstat -tlnp | grep 8000 >> diagnostic_report.txt
echo "" >> diagnostic_report.txt

echo "=== 最近日志 ===" >> diagnostic_report.txt
tail -50 logs/app_*.log >> diagnostic_report.txt 2>/dev/null
echo "" >> diagnostic_report.txt

cat diagnostic_report.txt
```

### 联系支持

提供以上诊断报告，以及：
1. 企业微信后台显示的具体错误信息
2. 应用日志中的错误堆栈
3. 网络架构图（如果有Nginx、防火墙等）

## ✅ 检查清单

部署前请确认：

- [ ] .env 文件配置正确，所有WECOM_*参数已填写
- [ ] WECOM_ENCODING_AES_KEY 长度为43位
- [ ] 应用可以正常启动（无报错）
- [ ] 配置测试脚本全部通过
- [ ] 本地curl测试成功
- [ ] 域名可以公网访问（或使用ngrok）
- [ ] HTTPS证书有效（或使用ngrok的HTTPS）
- [ ] 防火墙已开放443端口
- [ ] Nginx配置正确（如果使用）
- [ ] Token和AES Key与企业微信后台完全一致
- [ ] 应用的「可见范围」包含测试用户

完成以上检查后，企业微信回调应该可以正常工作！🎉

