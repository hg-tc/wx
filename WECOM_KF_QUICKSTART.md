# 🚀 微信客服快速开始指南

## ✅ 已完成的工作

系统已完成微信客服API适配，现在支持：
- ✅ 自动接收外部客户消息
- ✅ 自动接待会话（机器人模式）
- ✅ AI智能回复
- ✅ 支持服务供需匹配和购物比价
- ✅ 数据库已更新（支持external_userid）

## 📋 快速配置步骤（3分钟）

### 步骤1: 启动应用

```bash
cd /root/wx
source venv/bin/activate
bash scripts/start_services.sh
```

### 步骤2: 在微信中测试

1. 在企业微信管理后台，找到你的客服应用
2. 扫描客服二维码（或找到客服联系方式）
3. 在微信中发送一条测试消息：**"你好"**

### 步骤3: 查看日志获取OpenKfId

打开另一个终端，查看日志：

```bash
cd /root/wx
tail -f logs/app_*.log | grep -E "OpenKfId|客服"
```

你会看到类似输出：
```
🎯 检测到客服消息事件，开始处理...
✅ 提取到客服事件 - OpenKfId: wkAJ2GCAAASSm4_FhToWMFea0xAFAAAA, Token: ...
```

**复制这个 OpenKfId**（通常以 `wk` 开头）

### 步骤4: 更新配置

编辑 `.env` 文件：

```bash
nano /root/wx/.env
```

添加或更新这一行：
```bash
WECOM_KF_ACCOUNT_ID=wkAJ2GCAAASSm4_FhToWMFea0xAFAAAA  # 替换为你的OpenKfId
```

保存并退出（Ctrl+X, Y, Enter）

### 步骤5: 重启应用

```bash
bash scripts/restart_services.sh
```

### 步骤6: 再次测试

在微信中发送：
- "你好" → 应收到欢迎消息
- "帮助" → 应收到功能说明
- "我想学Python" → AI会识别为服务需求

## 🎯 功能测试

### 1. 基础对话
```
用户: 你好
AI: 您好！我是智能助手，很高兴为您服务！...
```

### 2. 服务供应
```
用户: 我提供Python编程培训
AI: 好的！我帮您登记供应服务...
```

### 3. 服务需求
```
用户: 我需要学习Python
AI: 好的！我帮您寻找服务...
```

### 4. 购物比价
```
用户: 帮我找iPhone 15 Pro
AI: 正在为您搜索「iPhone 15 Pro」的价格信息...
```

## 📱 客服功能特点

### ✅ 已实现
- 自动接收外部客户消息
- 自动接待会话（机器人模式）
- AI意图识别和智能回复
- 文本消息处理
- 进入会话欢迎消息
- 服务供需匹配
- 购物比价

### 🔄 消息处理流程
```
微信用户发送消息
    ↓
企业微信推送kf_msg_or_event事件
    ↓
系统调用sync_message API获取消息详情
    ↓
自动设置会话为"机器人接待"
    ↓
AI分析意图并生成响应
    ↓
调用send_kf_message发送回复
```

## 🔧 可选配置

### 客服专用Secret（可选）

如果你的客服应用有独立的Secret：

1. 在企业微信后台获取客服应用的Secret
2. 在 `.env` 中添加：
```bash
WECOM_KF_SECRET=your_kf_secret_here
```

**注意**：如果没有独立Secret，系统会自动使用 `WECOM_SECRET`

### 测试脚本（可选）

运行交互式测试：
```bash
python scripts/test_kf_message.py
```

可以测试：
- 获取客服账号列表
- 发送测试消息
- 变更会话状态

## 🔍 常见问题

### Q1: 发送消息后没有回复？

**检查清单**：
1. 应用是否正在运行？
```bash
bash scripts/status.sh
```

2. 日志中是否收到消息？
```bash
tail -50 logs/app_*.log | grep -E "客服|kf_"
```

3. 回调URL是否配置正确？
   - 检查企业微信后台的回调URL配置
   - URL应该是: `https://你的域名/api/v1/wecom/callback`

### Q2: 日志显示"获取access_token失败"？

**解决方法**：
1. 确认 `WECOM_CORP_ID` 和 `WECOM_SECRET` 正确
2. 检查服务器网络连接
3. 如果有独立的 `WECOM_KF_SECRET`，确认它是正确的

### Q3: OpenKfId从哪里获取？

**最简单的方法**：
1. 启动应用
2. 发送一条测试消息
3. 从日志中复制 OpenKfId

**API方法**（如果网络允许）：
```bash
python scripts/get_kf_info.py
```

### Q4: 如何同时支持内部员工和外部客户？

系统已经支持！
- **内部员工**：通过普通自建应用与AI对话
- **外部客户**：通过客服应用与AI对话
- 两者使用相同的AI引擎，体验一致

## 📊 监控和调试

### 查看实时日志
```bash
# 查看所有日志
tail -f logs/app_*.log

# 只看客服相关
tail -f logs/app_*.log | grep -E "客服|kf_|external"

# 查看错误
tail -f logs/app_*.log | grep -E "ERROR|错误|失败"
```

### 检查服务状态
```bash
bash scripts/status.sh
```

### 重启服务
```bash
bash scripts/restart_services.sh
```

## 📚 相关文档

- [WECOM_KF_SETUP.md](WECOM_KF_SETUP.md) - 详细配置指南
- [WECOM_SETUP.md](WECOM_SETUP.md) - 基础企业微信配置
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 故障排查
- [README.md](README.md) - 项目总览

## 🎉 成功标志

当你看到以下情况时，说明配置成功：

✅ 日志显示：
```
🎯 检测到客服消息事件，开始处理...
📬 获取到 1 条客服消息
💬 客服消息内容: 你好
✅ 成功发送客服消息给用户 wmXXXXXX...
```

✅ 微信收到AI的智能回复

✅ 可以正常对话，AI能识别意图并正确响应

## 💡 提示

1. **首次配置** `WECOM_KF_ACCOUNT_ID` 可以留空，从日志获取后再配置
2. **网络问题**：如果API调用失败，检查服务器是否能访问 `qyapi.weixin.qq.com`
3. **多个客服**：如果有多个客服账号，使用你想要的那个的 OpenKfId
4. **日志很重要**：遇到问题先查看 `logs/app_*.log`

## 🚀 下一步

配置成功后，你可以：
- 自定义AI回复话术（修改 `app/api/v1/wecom.py` 中的欢迎消息）
- 添加更多意图识别（修改 `app/ai_engine/intent_classifier.py`）
- 接入更多电商平台（扩展 `app/ecommerce_crawler/`）
- 配置DeepSeek API以启用真正的AI能力

祝使用愉快！🎉

