#!/bin/bash
# 停止所有服务（包括 Redis）- 非交互式

cd /root/wx

echo "=========================================="
echo "停止所有服务（包括 Redis）"
echo "=========================================="
echo ""

# 1. 停止 Celery Worker
echo "【1/4】Celery Worker"
if pgrep -f "celery.*worker" >/dev/null; then
    echo "  停止 Celery Worker..."
    pkill -f "celery.*worker"
    sleep 3
    
    if ! pgrep -f "celery.*worker" >/dev/null; then
        echo "  ✅ Celery Worker 已停止"
    else
        pkill -9 -f "celery.*worker"
        echo "  ✅ Celery Worker 已强制停止"
    fi
else
    echo "  Celery Worker 未运行"
fi

echo ""

# 2. 停止应用
echo "【2/4】FastAPI 应用"
if pgrep -f "uvicorn app.main:app" >/dev/null; then
    echo "  停止应用..."
    pkill -f "uvicorn app.main:app"
    sleep 2
    
    if ! pgrep -f "uvicorn app.main:app" >/dev/null; then
        echo "  ✅ 应用已停止"
    else
        pkill -9 -f "uvicorn app.main:app"
        echo "  ✅ 应用已强制停止"
    fi
    
    rm -f /tmp/wecom_app.pid
else
    echo "  应用未运行"
fi

echo ""

# 3. 停止 Nginx
echo "【3/4】Nginx 服务"
if pgrep nginx >/dev/null; then
    echo "  停止 Nginx..."
    nginx -s stop 2>/dev/null || pkill nginx
    sleep 2
    
    if ! pgrep nginx >/dev/null; then
        echo "  ✅ Nginx 已停止"
    else
        pkill -9 nginx
        echo "  ✅ Nginx 已强制停止"
    fi
else
    echo "  Nginx 未运行"
fi

echo ""

# 4. 停止 Redis
echo "【4/4】Redis 服务"
if pgrep redis-server >/dev/null; then
    echo "  停止 Redis..."
    redis-cli shutdown 2>/dev/null || pkill redis-server
    sleep 2
    
    if ! pgrep redis-server >/dev/null; then
        echo "  ✅ Redis 已停止"
    else
        pkill -9 redis-server
        echo "  ✅ Redis 已强制停止"
    fi
else
    echo "  Redis 未运行"
fi

echo ""
echo "=========================================="
echo "✅ 所有服务已停止"
echo "=========================================="
echo ""

# 验证
echo "📊 服务状态验证："
echo "  - Redis:         $(pgrep redis-server >/dev/null && echo '⚠️  仍在运行' || echo '✅ 已停止')"
echo "  - Nginx:         $(pgrep nginx >/dev/null && echo '⚠️  仍在运行' || echo '✅ 已停止')"
echo "  - FastAPI:       $(pgrep -f 'uvicorn app.main:app' >/dev/null && echo '⚠️  仍在运行' || echo '✅ 已停止')"
echo "  - Celery:        $(pgrep -f 'celery.*worker' >/dev/null && echo '⚠️  仍在运行' || echo '✅ 已停止')"
echo ""

# 清理 PID 文件
rm -f /tmp/wecom_celery.pid /tmp/wecom_app.pid

echo "重新启动服务: ./scripts/start_services.sh"
echo ""

