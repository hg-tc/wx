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
echo "  3. 安装PostgreSQL数据库"
echo "  4. 创建Python虚拟环境"
echo "  5. 安装Python依赖"
echo "  6. 初始化数据库表结构"
echo "  7. 配置Nginx"
echo "  8. 准备配置文件"
echo "  9. 完成安装"
echo ""

read -p "是否继续？(y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# ============================================
# 1. 检查系统环境
# ============================================
print_info "【1/9】检查系统环境..."

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
print_info "【2/9】安装系统依赖..."

print_info "更新包管理器..."
apt-get update -qq

print_info "安装必要的系统包..."
apt-get install -y -qq \
    nginx \
    redis-server \
    redis-tools \
    curl \
    lsof \
    net-tools

print_info "✅ 系统依赖安装完成"

# 启动 Redis
print_info "启动 Redis 服务..."
if pgrep redis-server >/dev/null; then
    print_info "✅ Redis 已在运行"
else
    redis-server --daemonize yes
    sleep 2
    if redis-cli ping >/dev/null 2>&1; then
        print_info "✅ Redis 已启动"
    else
        print_warning "⚠️  Redis 启动失败"
    fi
fi

# ============================================
# 3. 安装PostgreSQL数据库
# ============================================
print_info "【3/9】安装PostgreSQL数据库..."

if [ -f "scripts/install_postgresql.sh" ]; then
    print_info "调用 PostgreSQL 安装脚本..."
    bash scripts/install_postgresql.sh
    if [ $? -eq 0 ]; then
        print_info "✅ PostgreSQL 安装完成"
    else
        print_error "PostgreSQL 安装失败"
        print_info "您可以稍后手动运行: sudo bash scripts/install_postgresql.sh"
        read -p "是否继续安装其他组件？(y/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    print_warning "未找到 PostgreSQL 安装脚本，跳过数据库安装"
    print_info "请稍后手动运行: sudo bash scripts/install_postgresql.sh"
fi

# ============================================
# 4. 创建Python虚拟环境
# ============================================
print_info "【4/9】创建Python虚拟环境..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_info "✅ 虚拟环境已创建"
else
    print_info "虚拟环境已存在"
fi

# ============================================
# 5. 安装Python依赖
# ============================================
print_info "【5/9】安装Python依赖..."

source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

print_info "✅ Python依赖安装完成"

# ============================================
# 6. 初始化数据库表结构
# ============================================
print_info "【6/9】初始化数据库表结构..."

# 检查是否已配置数据库
if grep -q "^DATABASE_URL=postgresql" .env 2>/dev/null; then
    print_info "数据库连接已配置，运行迁移..."
    
    # 激活虚拟环境（如果尚未激活）
    source venv/bin/activate
    
    # 运行数据库迁移
    if alembic upgrade head 2>&1; then
        print_info "✅ 数据库表结构创建成功"
    else
        print_warning "⚠️  数据库迁移失败"
        print_info "可能原因："
        print_info "  - 数据库尚未启动"
        print_info "  - 数据库连接配置不正确"
        print_info "  - 数据库用户权限不足"
        print_info ""
        print_info "可以稍后手动运行："
        print_info "  cd /root/wx && source venv/bin/activate && alembic upgrade head"
        echo ""
        read -p "是否继续安装？(y/n) " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    print_warning "数据库连接尚未配置，跳过表结构创建"
    print_info "安装完成后请运行："
    print_info "  1. 配置数据库连接（DATABASE_URL）"
    print_info "  2. 运行迁移：cd /root/wx && source venv/bin/activate && alembic upgrade head"
fi

# ============================================
# 7. 配置Nginx
# ============================================
print_info "【7/9】配置Nginx..."

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
# 8. 准备配置文件
# ============================================
print_info "【8/9】准备配置文件..."

if [ ! -f ".env" ]; then
    print_info "创建配置文件模板..."
    cp env.example .env 2>/dev/null || touch .env
    print_success "✅ 已创建 .env 配置文件"
else
    print_info "✅ .env 配置文件已存在"
fi

echo ""
print_warning "⚠️  请注意："
echo "   安装完成后，需要编辑 .env 文件填入真实配置："
echo ""
echo "   【必填配置】"
echo "   - 企业微信配置：WECOM_CORP_ID, WECOM_AGENT_ID, WECOM_SECRET"
echo "   - 企业微信回调：WECOM_TOKEN, WECOM_ENCODING_AES_KEY"
echo "   - DeepSeek API：DEEPSEEK_API_KEY"
echo "   - 数据库连接：DATABASE_URL, DATABASE_URL_SYNC"
echo "   - 安全密钥：SECRET_KEY"
echo ""
echo "   【可选配置（使用客服功能时需要）】"
echo "   - WECOM_KF_ACCOUNT_ID: 通过 'python scripts/get_kf_info.py' 获取"
echo "   - WECOM_KF_SECRET: 客服应用的Secret"
echo ""
echo "   快速配置方法："
echo "   1. 手动编辑: nano .env"
echo "   2. 使用向导: ./scripts/config_wizard.sh"
echo "   3. 获取客服ID: python scripts/get_kf_info.py"
echo ""

# ============================================
# 9. 完成安装
# ============================================
print_info "【9/9】完成安装..."

# 创建日志目录
mkdir -p logs

echo ""
print_warning "⚠️  在启动服务前，请先完成配置："
echo ""
read -p "是否现在启动服务（需要已完成配置）？(y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "启动应用服务..."
    
    # 停止旧进程
    if pgrep -f "uvicorn app.main:app" >/dev/null; then
        print_info "停止旧的应用进程..."
        pkill -f "uvicorn app.main:app"
        sleep 2
    fi
    
    # 启动应用
    source venv/bin/activate
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info > logs/uvicorn.log 2>&1 &
    APP_PID=$!
    
    sleep 3
    
    # 检查应用是否启动成功
    if ps -p $APP_PID > /dev/null; then
        print_success "✅ 应用已启动 (PID: $APP_PID)"
        SERVICE_STARTED=true
    else
        print_error "应用启动失败，请检查日志："
        echo "  tail -f logs/uvicorn.log"
        echo ""
        print_info "可能原因：配置文件未正确填写"
        SERVICE_STARTED=false
    fi
else
    print_info "跳过服务启动"
    SERVICE_STARTED=false
fi

if [ "$SERVICE_STARTED" = true ]; then
    # 测试应用
    if curl -s http://localhost:8000/health | grep -q "healthy" 2>/dev/null; then
        print_success "✅ 应用健康检查通过"
    else
        print_warning "⚠️  应用健康检查失败（可能需要配置数据库）"
    fi
    
    # 测试Nginx转发
    if curl -s http://localhost:13000/health | grep -q "healthy" 2>/dev/null; then
        print_success "✅ Nginx转发测试通过"
    else
        print_warning "⚠️  Nginx转发测试失败"
    fi
fi

# ============================================
# 安装完成
# ============================================
echo ""
echo "=========================================="
echo "✅ 环境安装完成！"
echo "=========================================="
echo ""

if [ "$SERVICE_STARTED" = true ]; then
    echo "📊 服务状态："
    echo "  - 应用程序: http://0.0.0.0:8000 ✅"
    echo "  - Nginx转发: http://0.0.0.0:13000 ✅"
    echo "  - API文档: http://localhost:8000/docs"
    echo ""
else
    echo "⚠️  服务未启动（需要先配置）"
    echo ""
fi

echo "📋 容器信息："
echo "  - 容器IP: $CONTAINER_IP"
echo "  - 应用端口: 8000"
echo "  - Nginx端口: 13000"
echo ""

echo "⚙️  后续配置步骤："
echo ""
echo "  1️⃣  编辑配置文件（必需）："
echo "     nano .env"
echo ""
echo "  2️⃣  或使用配置向导："
echo "     ./scripts/config_wizard.sh"
echo ""
echo "  3️⃣  启动服务："
echo "     ./scripts/start_services.sh"
echo ""

if [ "$SERVICE_STARTED" = false ]; then
    echo "  ⚠️  重要：必须先完成步骤1或2，填写真实配置后才能启动服务"
    echo ""
fi

echo "🔧 管理命令："
echo "  - 启动服务: ./scripts/start_services.sh"
echo "  - 停止服务: ./scripts/stop_services.sh"
echo "  - 查看状态: ./scripts/status.sh"
echo "  - 查看日志: tail -f logs/uvicorn.log"
echo ""
echo "📱 企业微信回调配置（配置完成后设置）："
echo "  - 回调URL: https://你的域名/api/v1/wecom/callback"
echo "  - Token: 使用 .env 中的 WECOM_TOKEN"
echo "  - EncodingAESKey: 使用 .env 中的 WECOM_ENCODING_AES_KEY"
echo ""
echo "📚 更多文档："
echo "  - README: cat README.md"
echo "  - 安装指南: cat docs/SETUP.md"
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

