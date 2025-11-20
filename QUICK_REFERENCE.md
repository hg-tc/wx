# 🚀 快速参考指南

## 📦 一键安装

```bash
cd /root/wx
./scripts/setup_complete.sh
```

这个脚本会自动完成：
- ✅ 检查系统环境
- ✅ 安装系统依赖（Nginx等）
- ✅ 创建Python虚拟环境
- ✅ 安装Python依赖
- ✅ 配置Nginx转发（13000 → 8000）
- ✅ 验证配置
- ✅ 启动所有服务

## 🎮 服务管理

### 启动服务
```bash
./scripts/start_services.sh
```

### 停止服务
```bash
./scripts/stop_services.sh
```

### 重启服务
```bash
./scripts/restart_services.sh
```

### 查看状态
```bash
./scripts/status.sh
```

## 📊 日志查看

### 实时日志
```bash
tail -f /root/wx/logs/app_*.log
```

### 只看企业微信相关
```bash
tail -f /root/wx/logs/app_*.log | grep "🔔\|wecom\|callback"
```

### Nginx日志
```bash
tail -f /var/log/nginx/wecom_access.log
tail -f /var/log/nginx/wecom_error.log
```

## 🔧 配置企业微信

### 运行配置向导
```bash
./scripts/config_wizard.sh
```

### 手动编辑配置
```bash
nano /root/wx/.env
```

### 需要配置的参数
```env
WECOM_CORP_ID=你的企业ID
WECOM_AGENT_ID=你的应用ID  
WECOM_SECRET=你的应用密钥
WECOM_TOKEN=随机生成的Token
WECOM_ENCODING_AES_KEY=43位的AES密钥
```

### 生成Token和AES Key
```bash
# Token
python3 -c "import secrets; print(secrets.token_urlsafe(16))"

# AES Key（43位）
python3 -c "import base64, os; print(base64.b64encode(os.urandom(32)).decode().rstrip('='))"
```

## 🌐 企业微信后台配置

**回调URL格式：**
```
https://你的域名/api/v1/wecom/callback
```

**配置位置：**
1. 登录企业微信管理后台
2. 进入「应用管理」→ 选择应用
3. 找到「接收消息」配置
4. 填写：
   - URL: 上面的回调URL
   - Token: 从 `.env` 文件复制
   - EncodingAESKey: 从 `.env` 文件复制
5. 点击「保存」

## 🔍 故障排查

### 测试应用
```bash
# 健康检查
curl http://localhost:8000/health

# 测试Nginx转发
curl http://localhost:13000/health
```

### 运行诊断
```bash
./scripts/diagnose.sh
```

### 监控请求
```bash
./scripts/monitor_simple.sh
```

## 📂 重要文件

```
/root/wx/
├── .env                    # 环境配置（重要！）
├── app/                    # 应用代码
├── logs/                   # 日志文件
│   ├── app_*.log          # 应用日志
│   └── uvicorn.log        # 服务器日志
├── scripts/               # 管理脚本
│   ├── setup_complete.sh  # 完整安装
│   ├── start_services.sh  # 启动服务
│   ├── stop_services.sh   # 停止服务
│   ├── restart_services.sh# 重启服务
│   ├── status.sh          # 查看状态
│   └── config_wizard.sh   # 配置向导
└── /etc/nginx/
    └── sites-available/wecom  # Nginx配置
```

## 🆘 常见问题

### Q: 如何查看当前配置？
```bash
cat /root/wx/.env | grep WECOM
```

### Q: 如何重新配置企业微信？
```bash
./scripts/config_wizard.sh
```

### Q: 端口被占用怎么办？
```bash
# 查看端口
lsof -i :8000
lsof -i :13000

# 停止服务
./scripts/stop_services.sh

# 重新启动
./scripts/start_services.sh
```

### Q: 企业微信验证失败？
```bash
# 1. 查看实时日志
tail -f /root/wx/logs/app_*.log

# 2. 在企业微信点击保存

# 3. 观察日志输出
#    - 如果看到日志：请求到达了，检查配置
#    - 如果没有日志：请求未到达，检查网络/Nginx
```

### Q: 应用启动失败？
```bash
# 查看启动日志
tail -50 /root/wx/logs/uvicorn.log

# 查看错误日志
tail -50 /root/wx/logs/app_*.log | grep ERROR
```

## 📚 完整文档

- **配置指南**: `cat WECOM_SETUP.md`
- **故障排查**: `cat TROUBLESHOOTING.md`
- **转发排查**: `cat FORWARD_TROUBLESHOOTING.md`
- **使用手册**: `cat USAGE.md`
- **架构说明**: `cat ARCHITECTURE.md`
- **部署指南**: `cat DEPLOYMENT.md`

## 🎯 快速命令速查表

| 操作 | 命令 |
|------|------|
| 完整安装 | `./scripts/setup_complete.sh` |
| 启动服务 | `./scripts/start_services.sh` |
| 停止服务 | `./scripts/stop_services.sh` |
| 重启服务 | `./scripts/restart_services.sh` |
| 查看状态 | `./scripts/status.sh` |
| 查看日志 | `tail -f logs/app_*.log` |
| 配置向导 | `./scripts/config_wizard.sh` |
| 运行诊断 | `./scripts/diagnose.sh` |
| 监控请求 | `./scripts/monitor_simple.sh` |
| 测试应用 | `curl http://localhost:8000/health` |
| 测试转发 | `curl http://localhost:13000/health` |

## 🌟 推荐工作流

### 首次安装
```bash
# 1. 完整安装
./scripts/setup_complete.sh

# 2. 配置企业微信参数
./scripts/config_wizard.sh

# 3. 查看状态
./scripts/status.sh

# 4. 测试
curl http://localhost:13000/health
```

### 日常管理
```bash
# 查看状态
./scripts/status.sh

# 查看日志
tail -f logs/app_*.log

# 重启服务（更新代码后）
./scripts/restart_services.sh
```

### 排查问题
```bash
# 1. 运行诊断
./scripts/diagnose.sh

# 2. 监控请求
./scripts/monitor_simple.sh

# 3. 在企业微信测试
# （在另一个终端观察日志）

# 4. 查看详细日志
tail -100 logs/app_*.log
```

---

**有问题？查看完整文档或运行 `./scripts/diagnose.sh` 进行诊断！** 🚀

