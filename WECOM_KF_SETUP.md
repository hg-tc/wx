# 企业微信客服应用配置指南

本文档说明如何配置企业微信客服应用，让系统能够接收和回复外部客户的消息。

## 📋 前置条件

1. 已有企业微信管理员权限
2. 已完成基础配置（WECOM_CORP_ID、WECOM_TOKEN、WECOM_ENCODING_AES_KEY）
3. 已配置并验证通过回调URL

## 🔧 配置步骤

### 步骤1: 创建客服应用

1. 登录 [企业微信管理后台](https://work.weixin.qq.com/wework_admin/frame)
2. 进入 **应用管理** → **客服**
3. 点击 **添加客服账号**
4. 填写客服信息：
   - 客服名称：例如"智能助手"
   - 客服头像：上传头像图片
   - 接待人员：可以不添加（使用机器人自动接待）
5. 点击 **确定** 创建客服账号

### 步骤2: 获取客服配置参数

#### 2.1 获取 OpenKfId（客服账号ID）

**方法1：从日志中获取（推荐）**

1. 启动应用：`bash scripts/start_services.sh`
2. 在微信中扫描客服二维码，发送一条测试消息（如"你好"）
3. 查看应用日志：
```bash
tail -f logs/app_*.log | grep -E "OpenKfId|客服"
```

4. 日志中会显示：
```
✅ 提取到客服事件 - OpenKfId: wkAJ2GCAAASSm4_FhToWMFea0xAFAAAA, Token: ...
```

5. 复制 `OpenKfId` 的值（通常以 `wk` 开头）

**方法2：通过API获取**

运行获取脚本（需要先配置 `WECOM_KF_SECRET`）：
```bash
python scripts/get_kf_info.py
```

#### 2.2 获取 WECOM_KF_SECRET（客服应用Secret）

1. 在企业微信管理后台，进入 **应用管理** → **客服**
2. 点击你的客服应用
3. 找到 **开发者配置** 或 **开发信息** 区域
4. 复制 **Secret**（如果没有显示Secret，说明需要使用普通应用的Secret）

### 步骤3: 配置回调URL

1. 在客服应用设置页面，找到 **接收消息服务器配置**
2. 填写以下信息：
   - **URL**: `https://你的域名/api/v1/wecom/callback`
   - **Token**: 使用现有的 `WECOM_TOKEN`
   - **EncodingAESKey**: 使用现有的 `WECOM_ENCODING_AES_KEY`
3. 点击 **保存**
4. 系统会验证URL，验证成功后配置生效

### 步骤4: 更新环境变量

编辑 `.env` 文件，添加或更新以下配置：

```bash
# 企业微信客服配置
WECOM_KF_ACCOUNT_ID=wkAJ2GCAAASSm4_FhToWMFea0xAFAAAA  # 从步骤2获取
WECOM_KF_SECRET=your_kf_secret_here  # 从步骤2获取（如果有的话）
```

**注意**：
- 如果没有独立的 `WECOM_KF_SECRET`，系统会自动使用 `WECOM_SECRET`
- `WECOM_KF_ACCOUNT_ID` 可以先留空，发送测试消息后从日志获取

### 步骤5: 重启应用

```bash
bash scripts/restart_services.sh
```

### 步骤6: 测试客服功能

1. 在微信中扫描客服二维码（在客服设置页面）
2. 发送测试消息：`你好`
3. 查看日志确认消息被接收：
```bash
tail -f logs/app_*.log
```

4. 应该看到类似日志：
```
🎯 检测到客服消息事件，开始处理...
✅ 提取到客服事件 - OpenKfId: wkXXXX..., Token: YYYY...
📨 处理客服消息 - OpenKfId: wkXXXX...
📬 获取到 1 条客服消息
📝 处理客服消息 - 用户: wmXXXX..., 类型: text
💬 客服消息内容: 你好
```

5. 客服应自动回复欢迎消息

## 🎯 完整配置示例

`.env` 文件示例：

```bash
# 基础配置
WECOM_CORP_ID=wwa3df69d6b762af53
WECOM_AGENT_ID=1000002
WECOM_SECRET=n-Wqxpc5WmFit0v4ZEImtWMLUE4SmYl_bwFql6chjyw
WECOM_TOKEN=your_token_here
WECOM_ENCODING_AES_KEY=your_43_char_aes_key_here

# 客服配置（在发送测试消息后填写）
WECOM_KF_ACCOUNT_ID=wkAJ2GCAAASSm4_FhToWMFea0xAFAAAA
WECOM_KF_SECRET=  # 如果没有独立Secret，留空即可
```

## 📱 客服功能特点

### 自动接待
- 系统自动将会话设置为「机器人接待」状态
- 无需人工介入，24小时自动响应

### 支持的消息类型
- ✅ 文本消息：AI智能回复
- ✅ 图片消息：提示仅支持文字
- ✅ 进入会话事件：发送欢迎消息

### AI功能
- 🤖 意图识别（服务供应/需求、购物比价、查询记录）
- 💬 上下文对话
- 🔍 智能推荐

## 🔍 故障排查

### 问题1: 发送消息后没有响应

**检查步骤**：
1. 查看日志是否收到消息事件：
```bash
tail -100 logs/app_*.log | grep -E "客服|kf_"
```

2. 确认回调URL配置正确
3. 确认 `WECOM_TOKEN` 和 `WECOM_ENCODING_AES_KEY` 与客服应用配置一致

### 问题2: 日志显示"获取access_token失败"

**原因**：`WECOM_KF_SECRET` 配置错误或网络问题

**解决方法**：
1. 确认 `WECOM_KF_SECRET` 正确
2. 如果没有独立Secret，将其设置为空或删除该行
3. 检查服务器网络连接

### 问题3: OpenKfId无法获取

**解决方法**：
1. 先将 `WECOM_KF_ACCOUNT_ID` 留空
2. 启动应用
3. 发送一条测试消息
4. 从日志中复制 `OpenKfId`
5. 更新 `.env` 文件
6. 重启应用

### 问题4: "当前人工坐席繁忙"

**原因**：会话状态未正确设置为机器人接待

**解决方法**：
- 确认代码中调用了 `service_state_trans` 设置状态为 `2`（机器人接待）
- 检查日志确认状态变更成功

## 📚 API参考

### 客服相关API

#### 1. 同步消息
```python
await kf_client.sync_message(token)
```

#### 2. 发送消息
```python
await kf_client.send_text_message(open_kfid, external_userid, content)
```

#### 3. 变更会话状态
```python
await kf_client.service_state_trans(
    open_kfid, 
    external_userid, 
    service_state=2  # 2=机器人接待
)
```

#### 4. 获取客服账号列表
```python
accounts = await kf_client.get_account_list()
```

## 🎉 测试成功标志

当你看到以下响应时，说明配置成功：

1. 发送 `你好` → 收到欢迎消息
2. 发送 `帮助` → 收到功能说明
3. 发送 `我想学Python` → AI识别为服务需求并引导填写
4. 日志中显示完整的消息处理流程

## 📞 支持

如有问题，请查看：
- `logs/app_*.log` - 应用日志
- `TROUBLESHOOTING.md` - 故障排查文档
- `WECOM_SETUP.md` - 基础配置文档

