#!/bin/bash
# 重启所有服务

cd /root/wx

echo "=========================================="
echo "重启服务"
echo "=========================================="
echo ""

./scripts/stop_services.sh
echo ""
sleep 2
./scripts/start_services.sh

