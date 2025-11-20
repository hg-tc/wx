# 📜 脚本说明文档

本项目提供了一套完整的管理脚本，用于安装、配置、启动和管理系统。

## 📦 安装脚本

### setup_complete.sh
**用途**: 完整的一键安装脚本

**功能**:
- 检查系统环境
- 安装系统依赖（Nginx、PostgreSQL客户端等）
- 创建Python虚拟环境
- 安装Python依赖
- 配置Nginx转发
- 验证配置
- 启动所有服务

**使用**:
```bash
./scripts/setup_complete.sh
```

**适用场景**: 首次安装或完全重新部署

---

### install_postgresql.sh
**用途**: 安装和配置PostgreSQL数据库

**功能**:
- 安装PostgreSQL 14
- 安装pgvector扩展
- 创建数据库和用户
- 配置数据库连接字符串

**使用**:
```bash
./scripts/install_postgresql.sh
```

**适用场景**: 需要独立安装数据库时

---

## 🎮 服务管理脚本

### start_services.sh
**用途**: 启动所有服务

**功能**:
- 启动Nginx（如未运行）
- 启动应用程序（8000端口）
- 验证服务状态

**使用**:
```bash
./scripts/start_services.sh
```

**输出**: 显示服务启动状态和PID

---

### stop_services.sh
**用途**: 停止所有服务

**功能**:
- 停止应用程序
- 停止Nginx
- 清理PID文件

**使用**:
```bash
./scripts/stop_services.sh
```

**注意**: 优雅停止，如失败则强制终止

---

### restart_services.sh
**用途**: 重启所有服务

**功能**:
- 依次调用stop和start脚本
- 等待服务完全停止后再启动

**使用**:
```bash
./scripts/restart_services.sh
```

**适用场景**: 更新代码或配置后

---

### status.sh
**用途**: 查看服务状态

**功能**:
- 显示应用程序状态（PID、端口、健康检查）
- 显示Nginx状态（PID、端口、转发测试）
- 显示端口监听情况
- 显示最近日志

**使用**:
```bash
./scripts/status.sh
```

**输出示例**:
```
【应用程序】
  状态: ✅ 运行中
  PID: 12345
  端口: 8000
  健康检查: ✅ 通过

【Nginx】
  状态: ✅ 运行中
  PID: 67890
  端口: 13000, 80
  转发测试: ✅ 通过
```

---

## 🔧 配置脚本

### config_wizard.sh
**用途**: 企业微信配置向导

**功能**:
- 交互式输入企业微信参数
- 自动生成Token和AES Key
- 验证配置格式
- 更新.env文件

**使用**:
```bash
./scripts/config_wizard.sh
```

**流程**:
1. 输入Corp ID
2. 输入Agent ID
3. 输入Secret
4. 选择生成或输入Token
5. 选择生成或输入AES Key
6. 验证并保存

---

## 🔍 诊断脚本

### diagnose.sh
**用途**: 系统诊断

**功能**:
- 检查应用进程
- 检查端口监听
- 测试本地访问
- 测试Nginx转发
- 检查配置格式
- 搜索回调日志
- 生成本地测试命令

**使用**:
```bash
./scripts/diagnose.sh
```

**输出**: 完整的诊断报告和建议

**适用场景**: 排查问题时首先运行

---

### monitor_simple.sh
**用途**: 实时监控企业微信回调

**功能**:
- 实时显示应用日志
- 高亮显示回调请求
- 添加时间戳

**使用**:
```bash
./scripts/monitor_simple.sh
```

**适用场景**: 
- 配置企业微信回调URL时
- 测试消息收发时
- 调试回调问题时

**操作**: 保持运行，然后在企业微信操作，观察日志输出

---

### monitor_requests.sh
**用途**: 监控HTTP请求（高级）

**功能**:
- 监控所有HTTP请求
- 使用grep过滤关键信息
- 显示回调相关的日志

**使用**:
```bash
./scripts/monitor_requests.sh
```

---

### watch_requests.sh
**用途**: 监控网络连接（更高级）

**功能**:
- 使用tcpdump监控端口8000
- 监控应用日志
- 监控网络连接状态

**使用**:
```bash
./scripts/watch_requests.sh
```

**要求**: 需要root权限

---

## 🚀 启动脚本变体

### start_dev.sh
**用途**: 开发环境启动（交互式）

**功能**:
- 检查配置
- 检查端口占用（交互式处理）
- 前台启动应用（可以看到实时日志）
- 显示配置信息

**使用**:
```bash
./scripts/start_dev.sh
```

**适用场景**: 开发调试时

---

### start_background.sh
**用途**: 后台启动（非交互式）

**功能**:
- 检查配置
- 检查端口占用（交互式询问）
- 后台启动应用（使用nohup）
- 显示PID和日志路径

**使用**:
```bash
./scripts/start_background.sh
```

**适用场景**: 生产环境或远程启动

---

### start_container.sh
**用途**: 容器环境启动（exec方式）

**功能**:
- 检查配置
- 检查端口
- 使用exec启动（替换shell进程）
- 适合容器前台运行

**使用**:
```bash
./scripts/start_container.sh
```

**适用场景**: Docker容器中作为入口点

---

### stop_app.sh
**用途**: 仅停止应用程序

**功能**:
- 查找uvicorn进程
- 交互式确认
- 优雅停止或强制终止

**使用**:
```bash
./scripts/stop_app.sh
```

**适用场景**: 只需要停止应用，保留Nginx运行时

---

## 📊 测试脚本

### test_wecom_callback.py
**用途**: 测试企业微信回调配置

**功能**:
- 测试配置加载
- 测试加解密功能
- 模拟企业微信URL验证
- 生成测试curl命令

**使用**:
```bash
python scripts/test_wecom_callback.py
```

**输出**: 完整的测试报告和测试命令

---

## 📁 脚本分类索引

### 安装部署
- `setup_complete.sh` - 完整安装
- `install_postgresql.sh` - 数据库安装
- `deploy.sh` - 生产部署

### 服务管理
- `start_services.sh` - 启动服务
- `stop_services.sh` - 停止服务
- `restart_services.sh` - 重启服务
- `status.sh` - 查看状态

### 开发调试
- `start_dev.sh` - 开发启动
- `start_background.sh` - 后台启动
- `start_container.sh` - 容器启动
- `stop_app.sh` - 停止应用

### 配置工具
- `config_wizard.sh` - 配置向导

### 诊断监控
- `diagnose.sh` - 系统诊断
- `monitor_simple.sh` - 简单监控
- `monitor_requests.sh` - 请求监控
- `watch_requests.sh` - 网络监控

### 测试工具
- `test_wecom_callback.py` - 回调测试

---

## 🎯 使用建议

### 首次安装
```bash
1. ./scripts/setup_complete.sh      # 完整安装
2. ./scripts/config_wizard.sh       # 配置企业微信
3. ./scripts/status.sh               # 查看状态
```

### 日常使用
```bash
# 启动
./scripts/start_services.sh

# 查看状态
./scripts/status.sh

# 查看日志
tail -f logs/app_*.log

# 停止
./scripts/stop_services.sh
```

### 更新代码后
```bash
./scripts/restart_services.sh
```

### 排查问题
```bash
1. ./scripts/diagnose.sh            # 运行诊断
2. ./scripts/monitor_simple.sh      # 监控请求
3. 在企业微信测试
4. 查看日志
```

---

## 🔗 相关文档

- **安装指南**: [INSTALL.md](INSTALL.md)
- **快速参考**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **企业微信配置**: [WECOM_SETUP.md](WECOM_SETUP.md)
- **故障排查**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**所有脚本都已添加执行权限，可以直接运行！** 🚀

