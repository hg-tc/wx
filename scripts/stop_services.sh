#!/bin/bash
# 停止所有服务

cd /root/wx

echo "=========================================="
echo "停止服务"
echo "=========================================="

# 停止应用
if pgrep -f "uvicorn app.main:app" >/dev/null; then
    echo "停止应用..."
    pkill -f "uvicorn app.main:app"
    sleep 2
    
    if pgrep -f "uvicorn app.main:app" >/dev/null; then
        echo "⚠️  正常停止失败，强制终止..."
        pkill -9 -f "uvicorn app.main:app"
        sleep 1
    fi
    
    echo "✅ 应用已停止"
    rm -f /tmp/wecom_app.pid
else
    echo "应用未运行"
fi

# 停止Nginx
if pgrep nginx >/dev/null; then
    echo "停止 Nginx..."
    nginx -s stop
    sleep 1
    echo "✅ Nginx已停止"
else
    echo "Nginx未运行"
fi

echo ""
echo "=========================================="
echo "✅ 服务已停止"
echo "=========================================="
echo ""

