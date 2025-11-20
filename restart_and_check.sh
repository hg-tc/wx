#!/bin/bash
# 检查状态并重启应用

cd /root/wx

echo "========================================"
echo "🔍 客服会话状态检查与应用重启"
echo "========================================"
echo ""

# 激活虚拟环境
source venv/bin/activate

# 1. 检查现有会话状态
echo "📋 步骤1: 检查现有会话状态"
echo "----------------------------------------"
python3 check_existing_sessions.py
echo ""

# 2. 停止旧应用
echo "📋 步骤2: 停止旧应用"
echo "----------------------------------------"
pkill -f "uvicorn.*app.main:app"
echo "✅ 已停止旧应用进程"
sleep 2

# 3. 启动新应用
echo ""
echo "📋 步骤3: 启动新应用"
echo "----------------------------------------"
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > logs/uvicorn.log 2>&1 &
PID=$!
echo "✅ 应用已启动 (PID: $PID)"
sleep 3

# 4. 检查应用状态
echo ""
echo "📋 步骤4: 检查应用状态"
echo "----------------------------------------"
if ps -p $PID > /dev/null; then
    echo "✅ 应用运行正常"
else
    echo "❌ 应用启动失败，查看日志:"
    echo "   tail logs/uvicorn.log"
    exit 1
fi

# 5. 显示最新日志
echo ""
echo "📋 步骤5: 显示最新启动日志"
echo "----------------------------------------"
tail -n 20 logs/app_*.log | grep -E "应用启动|environment|DEBUG"

echo ""
echo "========================================"
echo "✅ 检查与重启完成"
echo "========================================"
echo ""
echo "📝 下一步操作:"
echo "1. 如果需要修改企业微信后台配置，现在去修改"
echo "2. 修改后，删除/退出当前客服会话"
echo "3. 重新进入客服发送消息测试"
echo "4. 监控日志:"
echo "   tail -f logs/app_*.log | grep -E '会话状态|发送'"
echo ""
echo "预期看到:"
echo "   📊 当前会话状态: 智能助手接待 (state=1)"
echo "   ✅ 成功发送客服消息"
echo ""
echo "========================================"

