#!/bin/bash
# 启动所有服务

cd /root/wx

echo "=========================================="
echo "启动服务"
echo "=========================================="
echo ""

# 1. 启动 Redis
echo "【1/4】Redis 服务"
if pgrep redis-server >/dev/null; then
    echo "  ✅ Redis 已在运行"
else
    echo "  启动 Redis..."
    redis-server --daemonize yes
    sleep 2
    if redis-cli ping >/dev/null 2>&1; then
        echo "  ✅ Redis 已启动"
    else
        echo "  ❌ Redis 启动失败"
        exit 1
    fi
fi

echo ""

# 2. 启动 Nginx
echo "【2/4】Nginx 服务"
if pgrep nginx >/dev/null; then
    echo "  ✅ Nginx 已在运行"
else
    echo "  启动 Nginx..."
    nginx
    sleep 1
    if pgrep nginx >/dev/null; then
        echo "  ✅ Nginx 已启动"
    else
        echo "  ❌ Nginx 启动失败"
        exit 1
    fi
fi

echo ""

# 3. 启动应用
echo "【3/4】FastAPI 应用"
if pgrep -f "uvicorn app.main:app" >/dev/null; then
    echo "  ⚠️  应用已在运行"
    echo "  如需重启，请运行: ./scripts/restart_services.sh"
else
    echo "  启动应用..."
    source venv/bin/activate
    mkdir -p logs
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info > logs/uvicorn.log 2>&1 &
    APP_PID=$!
    echo $APP_PID > /tmp/wecom_app.pid
    sleep 3
    
    if ps -p $APP_PID > /dev/null; then
        echo "  ✅ 应用已启动 (PID: $APP_PID)"
        
        # 健康检查
        if curl -s http://localhost:8000/health | grep -q "healthy" 2>/dev/null; then
            echo "  ✅ 健康检查通过"
        else
            echo "  ⚠️  健康检查失败（可能正在初始化）"
        fi
    else
        echo "  ❌ 应用启动失败"
        echo ""
        echo "  错误日志："
        tail -20 logs/uvicorn.log
        exit 1
    fi
fi

echo ""

# 4. 启动 Celery Worker
echo "【4/4】Celery Worker"
if pgrep -f "celery.*worker" >/dev/null; then
    echo "  ✅ Celery Worker 已在运行"
else
    echo "  启动 Celery Worker..."
    source venv/bin/activate
    nohup celery -A app.tasks.celery_app worker --loglevel=info > logs/celery.log 2>&1 &
    CELERY_PID=$!
    echo $CELERY_PID > /tmp/wecom_celery.pid
    sleep 3
    
    if pgrep -f "celery.*worker" >/dev/null; then
        WORKER_COUNT=$(pgrep -f "celery.*worker" | wc -l)
        echo "  ✅ Celery Worker 已启动 (${WORKER_COUNT} workers)"
    else
        echo "  ❌ Celery Worker 启动失败"
        echo ""
        echo "  错误日志："
        tail -20 logs/celery.log
        echo ""
        echo "  提示：Celery 依赖 Redis，请确保 Redis 正常运行"
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "✅ 服务启动完成"
echo "=========================================="
echo ""

# 服务状态汇总
echo "📊 服务状态："
echo "  - Redis:         $(pgrep redis-server >/dev/null && echo '✅ 运行中' || echo '❌ 未运行')"
echo "  - Nginx:         $(pgrep nginx >/dev/null && echo '✅ 运行中' || echo '❌ 未运行')"
echo "  - FastAPI:       $(pgrep -f 'uvicorn app.main:app' >/dev/null && echo '✅ 运行中' || echo '❌ 未运行')"
echo "  - Celery:        $(pgrep -f 'celery.*worker' >/dev/null && echo '✅ 运行中' || echo '❌ 未运行')"
echo ""

# 端口监听
echo "🔌 端口监听："
netstat -tlnp 2>/dev/null | grep -E ':(6379|8000|13000)' | awk '{printf "  - %-20s %s\n", $4, $7}' || echo "  无"
echo ""

# 访问地址
echo "🌐 访问地址："
echo "  - 应用: http://localhost:8000"
echo "  - Nginx: http://localhost:13000"
echo "  - API文档: http://localhost:8000/docs"
echo ""

# 管理命令
echo "🔧 管理命令："
echo "  - 查看状态: ./scripts/status.sh"
echo "  - 停止服务: ./scripts/stop_services.sh"
echo "  - 重启服务: ./scripts/restart_services.sh"
echo ""

# 日志文件
echo "📄 日志文件："
echo "  - 应用日志: tail -f logs/app_*.log"
echo "  - Uvicorn日志: tail -f logs/uvicorn.log"
echo "  - Celery日志: tail -f logs/celery.log"
echo "  - Nginx日志: tail -f /var/log/nginx/wecom_*.log"
echo ""

echo "=========================================="
echo ""

