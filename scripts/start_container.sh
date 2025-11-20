#!/bin/bash
# 容器环境启动脚本

set -e

cd /root/wx

echo "======================================"
echo "容器环境启动脚本"
echo "======================================"

# 激活虚拟环境
source venv/bin/activate

# 检查配置
echo "检查配置..."
python scripts/test_wecom_callback.py
if [ $? -ne 0 ]; then
    echo "❌ 配置验证失败"
    exit 1
fi

echo ""
echo "配置验证通过！"
echo ""

# 检查端口占用
if lsof -i :8000 >/dev/null 2>&1; then
    echo "⚠️  端口 8000 已被占用"
    OLD_PID=$(lsof -t -i :8000)
    echo "旧进程 PID: $OLD_PID"
    echo "正在停止..."
    kill $OLD_PID 2>/dev/null || kill -9 $OLD_PID 2>/dev/null
    sleep 2
    echo "✅ 旧进程已停止"
fi

# 创建日志目录
mkdir -p logs

echo ""
echo "======================================"
echo "启动应用..."
echo "======================================"
echo ""
echo "访问地址:"
echo "  - API文档: http://localhost:8000/docs"
echo "  - 根路径: http://localhost:8000/"
echo "  - 健康检查: http://localhost:8000/health"
echo ""
echo "日志文件:"
echo "  - 应用日志: /root/wx/logs/app_*.log"
echo "  - uvicorn日志: /root/wx/logs/uvicorn.log"
echo ""
echo "企业微信回调URL:"
echo "  https://你的域名/api/v1/wecom/callback"
echo ""
echo "======================================"
echo ""

# 启动应用
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info

