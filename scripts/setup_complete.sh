#!/bin/bash
# 企业微信智能客服中介系统 - 完整安装脚本
# 适用于容器环境（无systemd）

set -e

cd /root/wx

echo "=========================================="
echo "企业微信智能客服中介系统 - 完整安装"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查是否在项目根目录
if [ ! -f "app/main.py" ]; then
    print_error "请在项目根目录运行此脚本"
    exit 1
fi

echo "安装步骤："
echo "  1. 检查系统环境"
echo "  2. 安装系统依赖"
echo "  3. 创建Python虚拟环境"
echo "  4. 安装Python依赖"
echo "  5. 配置Nginx"
echo "  6. 配置企业微信参数"
echo "  7. 启动服务"
echo ""

read -p "是否继续？(y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# ============================================
# 1. 检查系统环境
# ============================================
print_info "【1/7】检查系统环境..."

if ! command -v python3 &> /dev/null; then
    print_error "Python3 未安装"
    exit 1
fi
print_info "✅ Python3: $(python3 --version)"

if ! command -v pip3 &> /dev/null; then
    print_error "pip3 未安装"
    exit 1
fi
print_info "✅ pip3 已安装"

# ============================================
# 2. 安装系统依赖
# ============================================
print_info "【2/7】安装系统依赖..."

print_info "更新包管理器..."
apt-get update -qq

print_info "安装必要的系统包..."
apt-get install -y -qq \
    nginx \
    postgresql-client \
    redis-tools \
    curl \
    lsof \
    net-tools

print_info "✅ 系统依赖安装完成"

# ============================================
# 3. 创建Python虚拟环境
# ============================================
print_info "【3/7】创建Python虚拟环境..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_info "✅ 虚拟环境已创建"
else
    print_info "虚拟环境已存在"
fi

# ============================================
# 4. 安装Python依赖
# ============================================
print_info "【4/7】安装Python依赖..."

source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

print_info "✅ Python依赖安装完成"

# ============================================
# 5. 配置Nginx
# ============================================
print_info "【5/7】配置Nginx..."

# 获取容器IP
CONTAINER_IP=$(hostname -I | awk '{print $1}')
print_info "容器IP: $CONTAINER_IP"

# 创建Nginx配置
cat > /etc/nginx/sites-available/wecom << EOF
# 企业微信后端服务配置
# 监听13000端口，转发到8000端口

server {
    listen 13000;
    server_name _ localhost;
    
    # 日志
    access_log /var/log/nginx/wecom_access.log;
    error_log /var/log/nginx/wecom_error.log;
    
    # 转发到本地8000端口
    location / {
        proxy_pass http://127.0.0.1:8000;
        
        # 传递请求头
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$http_host;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
}
EOF

# 启用配置
ln -sf /etc/nginx/sites-available/wecom /etc/nginx/sites-enabled/wecom
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
if nginx -t >/dev/null 2>&1; then
    print_info "✅ Nginx配置正确"
else
    print_error "Nginx配置错误"
    nginx -t
    exit 1
fi

# 启动或重启Nginx
if pgrep nginx >/dev/null; then
    nginx -s reload
    print_info "✅ Nginx已重新加载"
else
    nginx
    print_info "✅ Nginx已启动"
fi

sleep 2
if netstat -tlnp 2>/dev/null | grep -q ':13000'; then
    print_info "✅ Nginx监听13000端口成功"
else
    print_error "Nginx未能监听13000端口"
    exit 1
fi

# ============================================
# 6. 配置企业微信参数
# ============================================
print_info "【6/7】配置企业微信参数..."

if [ ! -f ".env" ]; then
    print_warning ".env 文件不存在，创建默认配置..."
    cp .env.example .env 2>/dev/null || touch .env
fi

# 检查必要的配置
source venv/bin/activate
python3 << 'PYEOF'
import sys
sys.path.insert(0, '/root/wx')
try:
    from app.config import get_settings
    settings = get_settings()
    
    print("\n当前企业微信配置：")
    print(f"  Corp ID: {settings.WECOM_CORP_ID}")
    print(f"  Agent ID: {settings.WECOM_AGENT_ID}")
    print(f"  Token长度: {len(settings.WECOM_TOKEN)} 字符")
    print(f"  AES Key长度: {len(settings.WECOM_ENCODING_AES_KEY)} 字符")
    
    if len(settings.WECOM_ENCODING_AES_KEY) != 43:
        print(f"\n❌ EncodingAESKey长度错误（当前{len(settings.WECOM_ENCODING_AES_KEY)}位，应为43位）")
        sys.exit(1)
    
    print("\n✅ 配置格式正确")
    
except Exception as e:
    print(f"\n❌ 配置加载失败: {e}")
    sys.exit(1)
PYEOF

if [ $? -ne 0 ]; then
    print_error "配置验证失败"
    print_info "请运行配置向导: ./scripts/config_wizard.sh"
    exit 1
fi

# ============================================
# 7. 启动服务
# ============================================
print_info "【7/7】启动服务..."

# 创建日志目录
mkdir -p logs

# 停止旧进程
if pgrep -f "uvicorn app.main:app" >/dev/null; then
    print_info "停止旧的应用进程..."
    pkill -f "uvicorn app.main:app"
    sleep 2
fi

# 启动应用
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info > logs/uvicorn.log 2>&1 &
APP_PID=$!

sleep 3

# 检查应用是否启动成功
if ps -p $APP_PID > /dev/null; then
    print_info "✅ 应用已启动 (PID: $APP_PID)"
else
    print_error "应用启动失败"
    tail -20 logs/uvicorn.log
    exit 1
fi

# 测试应用
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    print_info "✅ 应用健康检查通过"
else
    print_error "应用健康检查失败"
    exit 1
fi

# 测试Nginx转发
if curl -s http://localhost:13000/health | grep -q "healthy"; then
    print_info "✅ Nginx转发测试通过"
else
    print_error "Nginx转发测试失败"
    exit 1
fi

# ============================================
# 安装完成
# ============================================
echo ""
echo "=========================================="
echo "✅ 安装完成！"
echo "=========================================="
echo ""
echo "📊 服务状态："
echo "  - 应用程序: http://0.0.0.0:8000 ✅"
echo "  - Nginx转发: http://0.0.0.0:13000 ✅"
echo "  - API文档: http://localhost:8000/docs"
echo ""
echo "📋 容器信息："
echo "  - 容器IP: $CONTAINER_IP"
echo "  - 应用端口: 8000"
echo "  - Nginx端口: 13000"
echo ""
echo "🔧 管理命令："
echo "  - 启动服务: ./scripts/start_services.sh"
echo "  - 停止服务: ./scripts/stop_services.sh"
echo "  - 重启服务: ./scripts/restart_services.sh"
echo "  - 查看状态: ./scripts/status.sh"
echo "  - 查看日志: tail -f logs/app_*.log"
echo ""
echo "📱 企业微信配置："
echo "  - 回调URL: https://你的域名/api/v1/wecom/callback"
echo "  - Token: $(grep WECOM_TOKEN .env | cut -d= -f2)"
echo "  - EncodingAESKey: $(grep WECOM_ENCODING_AES_KEY .env | cut -d= -f2)"
echo ""
echo "📚 文档："
echo "  - 配置指南: cat WECOM_SETUP.md"
echo "  - 故障排查: cat TROUBLESHOOTING.md"
echo "  - 使用手册: cat USAGE.md"
echo ""
echo "=========================================="

# 保存PID
echo $APP_PID > /tmp/wecom_app.pid

# 显示实时日志提示
echo ""
read -p "是否查看实时日志？(y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    tail -f logs/app_*.log
fi

