#!/bin/bash
# 实时监控所有HTTP请求

cd /root/wx

echo "=========================================="
echo "HTTP请求实时监控"
echo "=========================================="
echo ""
echo "监控目标："
echo "  - 所有应用日志"
echo "  - TCP连接（端口8000）"
echo "  - 进程输出"
echo ""
echo "现在请在企业微信后台点击「保存」"
echo "如果这里没有任何新输出，说明请求没到达容器"
echo ""
echo "按 Ctrl+C 停止监控"
echo ""
echo "=========================================="
echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始监控..."
echo "=========================================="
echo ""

# 使用 tcpdump 监控 8000 端口的连接（如果有权限）
if command -v tcpdump >/dev/null 2>&1; then
    echo "使用 tcpdump 监控端口 8000..."
    timeout 120 tcpdump -i any -n port 8000 -A 2>/dev/null | grep --line-buffered -E "GET|POST|callback|HTTP" &
    TCPDUMP_PID=$!
fi

# 监控应用日志
tail -f logs/app_*.log 2>/dev/null | while read line; do
    echo "[应用日志] $(date '+%H:%M:%S') $line"
done &
LOG_PID=$!

# 监控网络连接
watch -n 1 "netstat -tn 2>/dev/null | grep ':8000'" 2>/dev/null &
NETSTAT_PID=$!

# 等待中断
trap "kill $TCPDUMP_PID $LOG_PID $NETSTAT_PID 2>/dev/null; exit" INT TERM

wait

