# 故障排查指南

## 常见问题

### 1. API 错误码

#### errcode: 95018 - 会话状态不允许发送消息

**原因**：会话处于人工接待状态（state=3）或已结束（state=4），send_msg API 不支持这些状态。

**解决方法**：
1. 进入企业微信后台 → 微信客服 → 接待设置
2. 修改为「仅智能助手接待」
3. 用户重新进入会话

#### errcode: 45009 - API 调用频率超限

**原因**：API 调用太频繁，触发企业微信频率限制。

**解决方法**：
1. 等待 1-2 分钟后重试
2. 检查代码逻辑，避免重复调用
3. 企业微信客服 API 限制约为每分钟 20 次

#### errcode: 40058 - 缺少必需参数

**原因**：请求缺少必需的 `touser` 或其他参数。

**解决方法**：
1. 检查日志中的请求参数
2. 确保 `external_userid` 正确传递
3. 对于事件类型消息，从 `event` 字段提取 `external_userid`

#### errcode: 95016 - 不允许的状态转换

**原因**：尝试进行不被允许的会话状态转换。

**解决方法**：
1. 检查当前会话状态
2. 参考官方文档的状态转换规则
3. 考虑修改企业微信后台配置

#### errcode: 95014 - 用户不是接待人员

**原因**：尝试使用非接待人员的 `servicer_userid` 进行操作。

**解决方法**：
1. 检查 `servicer_userid` 是否正确
2. 确保该用户已配置为客服接待人员
3. 使用正确的接待人员凭证

### 2. 网络问题

#### HTTP/2 403/404 错误

**原因**：服务器 IP 未添加到企业微信白名单。

**解决方法**：
1. 获取服务器公网 IP：`curl ifconfig.me`
2. 进入企业微信后台 → 我的企业 → IP 白名单
3. 添加服务器 IP

#### 连接超时

**原因**：网络连接问题或防火墙限制。

**解决方法**：
1. 检查网络连接：`curl https://qyapi.weixin.qq.com`
2. 检查防火墙规则
3. 确认服务器可以访问外网

### 3. 数据库问题

#### pgvector 扩展未安装

**错误**：`NameError: name 'pgvector' is not defined`

**解决方法**：
```bash
sudo apt install postgresql-14-pgvector
sudo -u postgres psql -d your_database -c "CREATE EXTENSION vector;"
```

#### 数据库连接失败

**解决方法**：
1. 检查 `.env` 中的 `DATABASE_URL`
2. 确认 PostgreSQL 服务运行中
3. 检查数据库用户权限

### 4. AI 引擎问题

#### DeepSeek API 认证失败

**错误**：`Error code: 401 - Authentication Fails`

**解决方法**：
1. 检查 `.env` 中的 `DEEPSEEK_API_KEY`
2. 确认 API Key 有效且未过期
3. 访问 DeepSeek 官网确认账户状态

### 5. 应用问题

#### 应用启动失败

**排查步骤**：
1. 检查日志：`tail -f logs/app_*.log`
2. 确认所有环境变量已配置
3. 检查端口是否被占用：`lsof -i :8000`

#### 消息无法接收

**排查步骤**：
1. 检查回调 URL 是否正确配置
2. 确认服务器可以从外网访问
3. 查看日志是否有接收到回调请求
4. 验证 Token 和 EncodingAESKey 配置

## 调试技巧

### 启用详细日志

在 `.env` 中设置：
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

### 监控实时日志

```bash
# 监控所有日志
tail -f logs/app_*.log

# 只看错误
tail -f logs/error_*.log

# 搜索特定内容
tail -f logs/app_*.log | grep "会话状态"
```

### 测试 API 连接

```bash
# 测试企业微信 API
curl "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=YOUR_CORP_ID&corpsecret=YOUR_SECRET&debug=1"

# 测试本地 API
curl http://localhost:8000/health
```

## 获取帮助

如果问题仍未解决：

1. 查看 [GitHub Issues](https://github.com/hg-tc/wx/issues)
2. 提交新的 Issue，包含：
   - 错误信息和日志
   - 环境信息（OS、Python 版本等）
   - 复现步骤
3. 参考企业微信官方文档：https://developer.work.weixin.qq.com/

