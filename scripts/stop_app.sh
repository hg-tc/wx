#!/bin/bash
# 停止应用脚本

echo "======================================"
echo "停止应用"
echo "======================================"

# 查找进程
PIDS=$(ps aux | grep 'uvicorn app.main:app' | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "❌ 没有找到运行中的应用"
    exit 1
fi

echo "找到运行中的进程:"
ps aux | grep 'uvicorn app.main:app' | grep -v grep

echo ""
echo "进程ID: $PIDS"
echo ""
read -p "确认停止？(y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消操作"
    exit 0
fi

# 尝试正常停止
echo "正在停止进程..."
for PID in $PIDS; do
    kill $PID 2>/dev/null
done

# 等待5秒
sleep 5

# 检查是否还在运行
REMAINING=$(ps aux | grep 'uvicorn app.main:app' | grep -v grep | awk '{print $2}')

if [ -z "$REMAINING" ]; then
    echo "✅ 应用已停止"
else
    echo "⚠️  进程未完全停止，强制终止..."
    for PID in $REMAINING; do
        kill -9 $PID 2>/dev/null
    done
    sleep 2
    echo "✅ 应用已强制停止"
fi

echo "======================================"

