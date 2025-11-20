# 配置参数获取指南

本文档说明如何获取 `.env` 文件中的各项配置参数。

## 📋 配置项清单

### ✅ 必填配置

| 配置项 | 说明 | 获取方式 |
|-------|------|---------|
| `WECOM_CORP_ID` | 企业ID | 企业微信管理后台 → 我的企业 → 企业信息 |
| `WECOM_AGENT_ID` | 应用ID | 企业微信管理后台 → 应用管理 → 自建应用 → 应用详情 |
| `WECOM_SECRET` | 应用Secret | 企业微信管理后台 → 应用管理 → 自建应用 → 应用详情 |
| `WECOM_TOKEN` | 回调验证Token | 自定义（任意字符串，建议随机生成） |
| `WECOM_ENCODING_AES_KEY` | 回调加密密钥 | 自定义（43位字符，或企业微信后台随机生成） |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | [DeepSeek开放平台](https://platform.deepseek.com) 注册获取 |
| `DATABASE_URL` | 数据库连接（异步） | 格式：`postgresql+asyncpg://user:pass@host:5432/db` |
| `DATABASE_URL_SYNC` | 数据库连接（同步） | 格式：`postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | 应用安全密钥 | 自定义（建议使用随机字符串） |

### 🔧 可选配置（客服功能）

| 配置项 | 说明 | 获取方式 |
|-------|------|---------|
| `WECOM_KF_ACCOUNT_ID` | 客服账号ID (open_kfid) | **见下方详细说明** |
| `WECOM_KF_SECRET` | 客服应用Secret | 企业微信管理后台 → 微信客服 → 应用Secret |

### 📦 可选配置（其他功能）

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `REDIS_URL` | Redis连接地址 | `redis://localhost:6379/0` |
| `TAOBAO_APP_KEY` | 淘宝联盟AppKey | 无（留空） |
| `TAOBAO_APP_SECRET` | 淘宝联盟AppSecret | 无（留空） |

---

## 🔍 详细获取方法

### 1. 企业微信基础配置

#### WECOM_CORP_ID - 企业ID

1. 登录 [企业微信管理后台](https://work.weixin.qq.com/wework_admin/frame)
2. 点击「我的企业」
3. 在「企业信息」页面找到「企业ID」

#### WECOM_AGENT_ID 和 WECOM_SECRET - 应用配置

1. 进入「应用管理」→「应用」→「自建」
2. 创建新应用或选择已有应用
3. 进入应用详情页面
   - `AgentId` 即为 `WECOM_AGENT_ID`
   - 点击「查看Secret」获取 `WECOM_SECRET`

#### WECOM_TOKEN 和 WECOM_ENCODING_AES_KEY - 回调配置

**方式1：企业微信后台生成（推荐）**

1. 进入应用详情 → 「接收消息」→「设置API接收」
2. 点击「随机获取」生成 Token（10-32位字符）
3. 点击「随机获取」生成 EncodingAESKey（43位字符）
4. 将这两个值复制到 `.env` 文件

**方式2：自己生成**

```bash
# 生成Token（10-32位）
openssl rand -base64 16 | head -c 20

# 生成EncodingAESKey（必须43位）
openssl rand -base64 32 | head -c 43
```

### 2. 客服账号ID获取 ⭐

`WECOM_KF_ACCOUNT_ID` (open_kfid) 无法直接在后台查看，必须通过API获取。

#### 方法1：使用项目脚本（推荐） ✅

**前提条件**：
- 已配置 `WECOM_CORP_ID`
- 已配置 `WECOM_SECRET`（客服应用的Secret）
- 已在企业微信后台创建客服账号

**执行步骤**：

```bash
# 1. 进入项目目录
cd /root/wx

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 运行获取脚本
python scripts/get_kf_info.py
```

**输出示例**：

```
============================================================
🔍 正在获取企业微信客服账号信息...
============================================================

📡 步骤1: 获取access_token...
✅ 成功获取access_token: Sa-CcJk8u2RYmqxZ7kJX...

📡 步骤2: 获取客服账号列表...
✅ 找到 2 个客服账号

============================================================
📋 客服账号详细信息:
============================================================

客服账号 #1
  名称: 智能客服
  OpenKfId: wkAJ2GCAAASSm4_FhToWJFzaIxq8jPtA
  头像: http://example.com/avatar.jpg

客服账号 #2
  名称: 人工客服
  OpenKfId: wkAJ2GCAAAXxqYUfjJU7f3Oc_d0IGN2A
  头像: http://example.com/avatar2.jpg

============================================================
✅ 配置建议:
============================================================

请将以下配置添加到 .env 文件：

WECOM_KF_ACCOUNT_ID=wkAJ2GCAAASSm4_FhToWJFzaIxq8jPtA

⚠️  注意: 你有多个客服账号，请选择需要使用的账号ID
```

将显示的 `OpenKfId` 复制到 `.env` 文件中。

#### 方法2：从回调事件中获取

启动应用后，当有用户首次发送消息时：

```bash
# 查看应用日志
tail -f logs/uvicorn.log | grep OpenKfId
```

会看到类似输出：
```
✅ 提取到客服事件 - OpenKfId: wkAJ2GCAAASSm4_FhToWJFzaIxq8jPtA, Token: ENCApHxnGD...
```

#### 方法3：手动调用API

```bash
# 1. 获取access_token
TOKEN=$(curl -s "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=YOUR_CORP_ID&corpsecret=YOUR_SECRET" | jq -r .access_token)

# 2. 获取客服账号列表
curl -s "https://qyapi.weixin.qq.com/cgi-bin/kf/account/list?access_token=$TOKEN&offset=0&limit=100" | jq '.account_list'
```

### 3. DeepSeek API配置

#### DEEPSEEK_API_KEY

1. 访问 [DeepSeek开放平台](https://platform.deepseek.com)
2. 注册/登录账号
3. 进入「API密钥」页面
4. 创建新的API密钥
5. 复制密钥到 `.env` 文件

### 4. 数据库配置

#### DATABASE_URL 和 DATABASE_URL_SYNC

**格式说明**：

```bash
# 异步连接（使用 asyncpg 驱动）
DATABASE_URL=postgresql+asyncpg://username:password@host:port/database

# 同步连接（使用 psycopg2 驱动）
DATABASE_URL_SYNC=postgresql://username:password@host:port/database
```

**示例**：

```bash
# 本地数据库
DATABASE_URL=postgresql+asyncpg://postgres:mypassword@localhost:5432/wecom_agent
DATABASE_URL_SYNC=postgresql://postgres:mypassword@localhost:5432/wecom_agent

# 远程数据库
DATABASE_URL=postgresql+asyncpg://user:pass@192.168.1.100:5432/wecom_agent
DATABASE_URL_SYNC=postgresql://user:pass@192.168.1.100:5432/wecom_agent
```

### 5. 安全密钥生成

#### SECRET_KEY

```bash
# 生成随机密钥
openssl rand -hex 32
```

或使用Python：

```python
import secrets
print(secrets.token_hex(32))
```

---

## ✅ 配置检查清单

完成配置后，按以下清单检查：

- [ ] `WECOM_CORP_ID` - 企业ID已填写
- [ ] `WECOM_AGENT_ID` - 应用ID已填写
- [ ] `WECOM_SECRET` - 应用Secret已填写
- [ ] `WECOM_TOKEN` - Token已生成（10-32位）
- [ ] `WECOM_ENCODING_AES_KEY` - AES密钥已生成（必须43位）
- [ ] `DEEPSEEK_API_KEY` - DeepSeek API密钥已填写
- [ ] `DATABASE_URL` - 数据库连接已配置（异步）
- [ ] `DATABASE_URL_SYNC` - 数据库连接已配置（同步）
- [ ] `SECRET_KEY` - 应用密钥已生成

**可选（使用客服功能时）**：
- [ ] `WECOM_KF_ACCOUNT_ID` - 客服账号ID已获取
- [ ] `WECOM_KF_SECRET` - 客服Secret已填写

---

## 🔧 配置验证

配置完成后，可以运行以下命令验证：

```bash
# 激活虚拟环境
source venv/bin/activate

# 验证配置加载
python -c "from app.config import get_settings; s=get_settings(); print('✅ 配置加载成功')"
```

如果没有报错，说明配置正确。

---

## 📚 相关文档

- [完整安装指南](SETUP.md)
- [故障排查指南](TROUBLESHOOTING.md)
- [项目概览](OVERVIEW.md)
- [API文档](API.md)

---

## ❓ 常见问题

### Q: EncodingAESKey长度必须是43位吗？

A: 是的，这是企业微信的强制要求。如果不是43位，回调验证会失败。

### Q: 客服账号ID一定要配置吗？

A: 如果只使用应用消息功能，可以不配置。但如果要使用客服功能（处理客服会话），则必须配置。

### Q: 数据库连接为什么要配置两个？

A: 项目中同时使用了异步和同步的数据库操作，需要分别配置对应的驱动。

### Q: 如何测试配置是否正确？

A: 运行 `python scripts/get_kf_info.py` 可以测试企业微信配置是否正确。

