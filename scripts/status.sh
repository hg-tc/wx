#!/bin/bash
# 查看服务状态

cd /root/wx

echo "=========================================="
echo "服务状态"
echo "=========================================="
echo ""

# 1. Redis
echo "【1/4】Redis 服务"
if pgrep redis-server >/dev/null; then
    REDIS_PID=$(pgrep redis-server)
    echo "  状态: ✅ 运行中"
    echo "  PID: $REDIS_PID"
    echo "  端口: 6379"
    
    # 测试连接
    if redis-cli ping >/dev/null 2>&1; then
        echo "  连接测试: ✅ 通过 (PONG)"
    else
        echo "  连接测试: ❌ 失败"
    fi
else
    echo "  状态: ❌ 未运行"
    echo "  提示: Redis 是 Celery 的必需依赖"
fi

echo ""

# 2. 应用程序
echo "【2/4】FastAPI 应用"
if pgrep -f "uvicorn app.main:app" >/dev/null; then
    APP_PID=$(pgrep -f "uvicorn app.main:app")
    echo "  状态: ✅ 运行中"
    echo "  PID: $APP_PID"
    echo "  端口: 8000"
    
    # 测试健康检查
    if curl -s http://localhost:8000/health | grep -q "healthy" 2>/dev/null; then
        echo "  健康检查: ✅ 通过"
    else
        echo "  健康检查: ❌ 失败"
    fi
else
    echo "  状态: ❌ 未运行"
fi

echo ""

# 3. Celery Worker
echo "【3/4】Celery Worker"
if pgrep -f "celery.*worker" >/dev/null; then
    CELERY_PIDS=$(pgrep -f "celery.*worker" | head -5)
    WORKER_COUNT=$(pgrep -f "celery.*worker" | wc -l)
    echo "  状态: ✅ 运行中"
    echo "  Workers: ${WORKER_COUNT} 个"
    echo "  主进程 PID: $(echo $CELERY_PIDS | awk '{print $1}')"
    
    # 检查日志中的任务
    if [ -f logs/celery.log ]; then
        READY_COUNT=$(grep -c "ready" logs/celery.log | tail -1)
        if [ "$READY_COUNT" -gt 0 ]; then
            echo "  就绪状态: ✅ Ready"
        fi
    fi
else
    echo "  状态: ❌ 未运行"
    echo "  提示: 商品比价和服务匹配功能需要 Celery"
fi

echo ""

# 4. Nginx
echo "【4/4】Nginx 服务"
if pgrep nginx >/dev/null; then
    NGINX_PID=$(pgrep nginx | head -1)
    echo "  状态: ✅ 运行中"
    echo "  PID: $NGINX_PID"
    echo "  端口: 13000, 80"
    
    # 测试转发
    if curl -s http://localhost:13000/health 2>/dev/null | grep -q "healthy"; then
        echo "  转发测试: ✅ 通过"
    else
        echo "  转发测试: ❌ 失败"
    fi
else
    echo "  状态: ❌ 未运行"
fi

echo ""
echo "=========================================="
echo "系统信息"
echo "=========================================="
echo ""

# 端口监听
echo "【端口监听】"
if command -v netstat >/dev/null; then
    PORT_INFO=$(netstat -tlnp 2>/dev/null | grep -E ':(6379|8000|13000|80)' | awk '{printf "  - %-22s %s\n", $4, $7}')
    if [ -n "$PORT_INFO" ]; then
        echo "$PORT_INFO"
    else
        echo "  无监听端口"
    fi
else
    echo "  (netstat 未安装)"
fi

echo ""

# 内存使用
echo "【内存使用】"
if command -v free >/dev/null; then
    free -h | grep "Mem:" | awk '{printf "  总内存: %s | 已用: %s | 可用: %s\n", $2, $3, $7}'
else
    echo "  (free 命令未安装)"
fi

echo ""

# 磁盘使用
echo "【磁盘使用】"
df -h /root/wx 2>/dev/null | grep -v "Filesystem" | awk '{printf "  使用率: %s | 可用: %s | 挂载点: %s\n", $5, $4, $6}' || echo "  无信息"

echo ""

# 最近的应用日志
echo "【最近日志】(最新5条)"
if ls logs/app_*.log >/dev/null 2>&1; then
    tail -5 logs/app_*.log 2>/dev/null | while read line; do
        # 截取日志长度
        SHORT_LINE=$(echo "$line" | cut -c1-100)
        echo "  $SHORT_LINE"
    done
else
    echo "  无应用日志文件"
fi

echo ""

# Celery 任务信息
if pgrep -f "celery.*worker" >/dev/null && [ -f logs/celery.log ]; then
    echo "【Celery 任务】(最新3条)"
    grep -E "Task|tasks|ready" logs/celery.log 2>/dev/null | tail -3 | while read line; do
        SHORT_LINE=$(echo "$line" | cut -c1-100)
        echo "  $SHORT_LINE"
    done
    echo ""
fi

echo "=========================================="
echo "管理命令"
echo "=========================================="
echo ""
echo "  启动服务: ./scripts/start_services.sh"
echo "  停止服务: ./scripts/stop_services.sh"
echo "  重启服务: ./scripts/restart_services.sh"
echo ""
echo "  查看日志:"
echo "    - 应用: tail -f logs/app_*.log"
echo "    - Uvicorn: tail -f logs/uvicorn.log"
echo "    - Celery: tail -f logs/celery.log"
echo "    - Nginx: tail -f /var/log/nginx/wecom_*.log"
echo ""
echo "  访问地址:"
echo "    - API: http://localhost:8000"
echo "    - 文档: http://localhost:8000/docs"
echo "    - Nginx: http://localhost:13000"
echo ""
echo "=========================================="
echo ""
