#!/bin/bash
# 重启所有服务

cd /root/wx

echo "=========================================="
echo "重启服务"
echo "=========================================="
echo ""

echo "提示：重启时不会停止 Redis 服务"
echo ""

# 停止服务（跳过 Redis）
echo "【第1步】停止服务..."
echo ""

# 1. 停止 Celery Worker
if pgrep -f "celery.*worker" >/dev/null; then
    echo "停止 Celery Worker..."
    pkill -f "celery.*worker"
    sleep 3
    [ ! $(pgrep -f "celery.*worker") ] || pkill -9 -f "celery.*worker"
    echo "✅ Celery Worker 已停止"
fi

# 2. 停止应用
if pgrep -f "uvicorn app.main:app" >/dev/null; then
    echo "停止 FastAPI 应用..."
    pkill -f "uvicorn app.main:app"
    sleep 2
    [ ! $(pgrep -f "uvicorn app.main:app") ] || pkill -9 -f "uvicorn app.main:app"
    rm -f /tmp/wecom_app.pid
    echo "✅ FastAPI 应用已停止"
fi

# 3. 停止 Nginx
if pgrep nginx >/dev/null; then
    echo "停止 Nginx..."
    nginx -s stop 2>/dev/null || pkill nginx
    sleep 2
    [ ! $(pgrep nginx) ] || pkill -9 nginx
    echo "✅ Nginx 已停止"
fi

echo ""
sleep 2

# 启动服务
echo "【第2步】启动服务..."
echo ""
./scripts/start_services.sh

echo ""
echo "=========================================="
echo "✅ 服务重启完成"
echo "=========================================="
echo ""
echo "查看状态: ./scripts/status.sh"
echo ""
