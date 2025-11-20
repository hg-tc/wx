#!/bin/bash
# 查看服务状态

cd /root/wx

echo "=========================================="
echo "服务状态"
echo "=========================================="
echo ""

# 检查应用
echo "【应用程序】"
if pgrep -f "uvicorn app.main:app" >/dev/null; then
    APP_PID=$(pgrep -f "uvicorn app.main:app")
    echo "  状态: ✅ 运行中"
    echo "  PID: $APP_PID"
    echo "  端口: 8000"
    
    # 测试健康检查
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo "  健康检查: ✅ 通过"
    else
        echo "  健康检查: ❌ 失败"
    fi
else
    echo "  状态: ❌ 未运行"
fi

echo ""

# 检查Nginx
echo "【Nginx】"
if pgrep nginx >/dev/null; then
    NGINX_PID=$(pgrep nginx | head -1)
    echo "  状态: ✅ 运行中"
    echo "  PID: $NGINX_PID"
    echo "  端口: 13000, 80"
    
    # 测试转发
    if curl -s http://localhost:13000/health | grep -q "healthy"; then
        echo "  转发测试: ✅ 通过"
    else
        echo "  转发测试: ❌ 失败"
    fi
else
    echo "  状态: ❌ 未运行"
fi

echo ""

# 端口监听
echo "【端口监听】"
netstat -tlnp 2>/dev/null | grep -E ':(8000|13000|80)' | awk '{print "  " $4 " -> " $7}' || echo "  无"

echo ""

# 最近的日志
echo "【最近日志】(最新5条)"
if [ -f logs/app_*.log ]; then
    tail -5 logs/app_*.log 2>/dev/null | while read line; do
        echo "  $line"
    done
else
    echo "  无日志文件"
fi

echo ""

echo "=========================================="
echo "管理命令"
echo "=========================================="
echo "  启动: ./scripts/start_services.sh"
echo "  停止: ./scripts/stop_services.sh"
echo "  重启: ./scripts/restart_services.sh"
echo "  日志: tail -f logs/app_*.log"
echo "=========================================="
echo ""

