#!/bin/bash
# 实时监控请求

cd /root/wx

echo "======================================"
echo "实时监控企业微信回调请求"
echo "======================================"
echo ""
echo "监控以下日志文件："
echo "  - 应用日志: logs/app_*.log"
echo "  - uvicorn日志: logs/uvicorn.log"
echo ""
echo "当你在企业微信点击「保存」时，这里会显示请求"
echo "按 Ctrl+C 停止监控"
echo ""
echo "======================================"
echo ""

# 多个日志文件同时监控
if [ -f logs/uvicorn.log ]; then
    tail -f logs/uvicorn.log logs/app_*.log 2>/dev/null | grep --line-buffered -E "callback|wecom|GET|POST|验证|signature"
else
    echo "⚠️  未找到 logs/uvicorn.log，尝试监控应用日志..."
    tail -f logs/app_*.log 2>/dev/null | grep --line-buffered -E "callback|wecom|验证|signature"
fi

