#!/bin/bash
# 启动所有服务

cd /root/wx

echo "=========================================="
echo "启动服务"
echo "=========================================="

# 启动Nginx
if ! pgrep nginx >/dev/null; then
    echo "启动 Nginx..."
    nginx
    echo "✅ Nginx已启动"
else
    echo "✅ Nginx已在运行"
fi

# 启动应用
if pgrep -f "uvicorn app.main:app" >/dev/null; then
    echo "⚠️  应用已在运行"
    echo "如需重启，请运行: ./scripts/restart_services.sh"
else
    echo "启动应用..."
    source venv/bin/activate
    mkdir -p logs
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info > logs/uvicorn.log 2>&1 &
    APP_PID=$!
    echo $APP_PID > /tmp/wecom_app.pid
    sleep 3
    
    if ps -p $APP_PID > /dev/null; then
        echo "✅ 应用已启动 (PID: $APP_PID)"
    else
        echo "❌ 应用启动失败"
        tail -20 logs/uvicorn.log
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "✅ 服务启动完成"
echo "=========================================="
echo ""
echo "查看状态: ./scripts/status.sh"
echo "查看日志: tail -f logs/app_*.log"
echo ""

