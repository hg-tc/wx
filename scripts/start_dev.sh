#!/bin/bash
# 开发环境启动脚本

cd /root/wx

echo "🔍 检查配置..."
source venv/bin/activate
python scripts/test_wecom_callback.py

if [ $? -ne 0 ]; then
    echo "❌ 配置检查失败，请修复后再启动"
    exit 1
fi

echo ""
echo "🔍 检查端口占用..."
if lsof -i :8000 >/dev/null 2>&1; then
    echo "⚠️  端口 8000 已被占用"
    echo ""
    echo "当前占用的进程:"
    lsof -i :8000
    echo ""
    read -p "是否要停止旧进程？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PID=$(lsof -t -i :8000)
        echo "正在停止进程 $PID..."
        kill $PID
        sleep 2
        if lsof -i :8000 >/dev/null 2>&1; then
            echo "进程未停止，强制终止..."
            kill -9 $PID
        fi
        echo "✅ 旧进程已停止"
    else
        echo "❌ 取消启动"
        exit 1
    fi
fi

echo ""
echo "🚀 启动应用..."
echo "访问地址:"
echo "  - API文档: http://localhost:8000/docs"
echo "  - 根路径: http://localhost:8000/"
echo "  - 健康检查: http://localhost:8000/health"
echo ""
echo "企业微信配置参数:"
echo "  Token: $(grep WECOM_TOKEN .env | cut -d= -f2)"
echo "  EncodingAESKey: $(grep WECOM_ENCODING_AES_KEY .env | cut -d= -f2)"
echo ""
echo "按 Ctrl+C 停止应用"
echo "=========================================="
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

