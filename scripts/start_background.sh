#!/bin/bash
# 后台启动脚本（适用于容器环境）

cd /root/wx

echo "======================================"
echo "后台启动应用"
echo "======================================"

# 激活虚拟环境
source venv/bin/activate

# 检查配置
echo "检查配置..."
python scripts/test_wecom_callback.py > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ 配置验证失败，请先运行: python scripts/test_wecom_callback.py"
    exit 1
fi

# 检查端口占用
if lsof -i :8000 >/dev/null 2>&1; then
    echo "⚠️  端口 8000 已被占用"
    OLD_PID=$(lsof -t -i :8000)
    echo "旧进程 PID: $OLD_PID"
    read -p "是否停止旧进程？(y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill $OLD_PID 2>/dev/null || kill -9 $OLD_PID 2>/dev/null
        sleep 2
        echo "✅ 旧进程已停止"
    else
        echo "❌ 取消启动"
        exit 1
    fi
fi

# 创建日志目录
mkdir -p logs

# 启动应用
echo "启动应用..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > logs/uvicorn.log 2>&1 &

PID=$!
echo ""
echo "✅ 应用已在后台启动"
echo ""
echo "进程ID: $PID"
echo "日志文件: /root/wx/logs/uvicorn.log"
echo ""
echo "常用命令:"
echo "  查看日志: tail -f /root/wx/logs/uvicorn.log"
echo "  查看进程: ps aux | grep uvicorn"
echo "  停止应用: kill $PID"
echo "  或使用: ./scripts/stop_app.sh"
echo ""

# 等待应用启动
sleep 3

# 检查应用是否正常运行
if ps -p $PID > /dev/null; then
    echo "✅ 应用运行正常"
    
    # 测试健康检查
    if command -v curl >/dev/null 2>&1; then
        sleep 2
        HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo "✅ 健康检查通过: $HEALTH"
        else
            echo "⚠️  健康检查失败，请查看日志"
        fi
    fi
    
    echo ""
    echo "访问地址:"
    echo "  - API文档: http://localhost:8000/docs"
    echo "  - 根路径: http://localhost:8000/"
    echo "  - 健康检查: http://localhost:8000/health"
    echo ""
else
    echo "❌ 应用启动失败，请查看日志:"
    echo "   tail -f /root/wx/logs/uvicorn.log"
    exit 1
fi

echo "======================================"

