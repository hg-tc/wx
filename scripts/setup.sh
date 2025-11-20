#!/bin/bash
# 初始化安装脚本

set -e

echo "==> 企业微信智能客服中介系统 - 初始化安装"

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# 创建虚拟环境
echo "==> 创建虚拟环境"
python3 -m venv venv

# 激活虚拟环境
echo "==> 激活虚拟环境"
source venv/bin/activate

# 安装依赖
echo "==> 安装Python依赖"
pip install --upgrade pip
pip install -r requirements.txt

# 安装Playwright浏览器
echo "==> 安装Playwright浏览器"
playwright install chromium

# 创建.env文件
if [ ! -f .env ]; then
    echo "==> 创建.env文件"
    cp .env.example .env
    echo "请编辑 .env 文件，填入实际配置！"
fi

# 创建日志目录
echo "==> 创建日志目录"
mkdir -p logs

# PostgreSQL配置提示
echo ""
echo "==> PostgreSQL配置"
echo "请确保PostgreSQL已安装并启用pgvector扩展："
echo "  sudo apt install postgresql-14 postgresql-14-pgvector"
echo "  sudo -u postgres psql -c \"CREATE DATABASE wecom_db;\""
echo "  sudo -u postgres psql -d wecom_db -c \"CREATE EXTENSION vector;\""
echo ""

# Redis安装和配置
echo "==> Redis配置"
if ! command -v redis-server &> /dev/null; then
    echo "Redis未安装，正在安装..."
    apt-get update -qq
    apt-get install -y redis-server
    echo "✅ Redis已安装"
fi

if ! pgrep redis-server >/dev/null; then
    echo "启动Redis..."
    redis-server --daemonize yes
    sleep 2
    if redis-cli ping >/dev/null 2>&1; then
        echo "✅ Redis已启动"
    else
        echo "⚠️  Redis启动失败，请手动启动：redis-server --daemonize yes"
    fi
else
    echo "✅ Redis已在运行"
fi
echo ""

# 数据库迁移
echo "==> 初始化数据库"
read -p "是否现在运行数据库迁移？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    alembic upgrade head
fi

echo ""
echo "==> 安装完成！"
echo ""
echo "后续步骤："
echo "1. 编辑 .env 文件，填入实际配置"
echo "2. 配置Systemd服务（参考README.md）"
echo "3. 配置Nginx反向代理"
echo "4. 启动服务"
echo ""
echo "开发模式启动："
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""

