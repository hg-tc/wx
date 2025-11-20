#!/bin/bash

echo "===================================="
echo "🔍 容器网络诊断"
echo "===================================="
echo ""

echo "【1】环境检测"
echo "----------------------------------------"
echo "容器ID: $(cat /proc/1/cgroup | head -1)"
echo "主机名: $(hostname)"
echo ""

echo "【2】网络接口"
echo "----------------------------------------"
ip addr show | grep -E "inet |eth" | head -10
echo ""

echo "【3】默认网关（宿主机）"
echo "----------------------------------------"
ip route | grep default
GATEWAY=$(ip route | grep default | awk '{print $3}')
echo "网关IP: $GATEWAY"
echo ""

echo "【4】测试外网连接"
echo "----------------------------------------"
echo -n "百度: "
timeout 5 curl -s -o /dev/null -w "%{http_code}" https://www.baidu.com && echo " ✅" || echo " ❌"

echo -n "企业微信API: "
timeout 5 curl -s -o /dev/null -w "%{http_code}" "https://qyapi.weixin.qq.com/cgi-bin/gettoken" && echo " ✅" || echo " ❌"

echo ""

echo "【5】尝试获取真实出站IP"
echo "----------------------------------------"
echo "方法1（ipify）:"
timeout 5 curl -s https://api.ipify.org 2>/dev/null && echo "" || echo "  超时/失败"

echo "方法2（ifconfig.me）:"
timeout 5 curl -s https://ifconfig.me 2>/dev/null && echo "" || echo "  超时/失败"

echo "方法3（ip.sb）:"
timeout 5 curl -s https://ip.sb 2>/dev/null && echo "" || echo "  超时/失败"

echo ""

echo "【6】测试企业微信API"
echo "----------------------------------------"
echo "请求: https://qyapi.weixin.qq.com/cgi-bin/token"
RESPONSE=$(timeout 10 curl -s "https://qyapi.weixin.qq.com/cgi-bin/token?corpid=wwa3df69d6b762af53&corpsecret=n-Wqxpc5WmFit0v4ZEImtWMLUE4SmYl_bwFql6chjyw" 2>&1)
echo "响应: $RESPONSE"

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "状态: ✅ 成功"
else
    echo "状态: ❌ 失败"
    
    if echo "$RESPONSE" | grep -q "errcode"; then
        echo "错误: $(echo $RESPONSE | grep -o 'errcode":[0-9]*')"
    fi
fi

echo ""

echo "【7】测试宿主机代理（如果存在）"
echo "----------------------------------------"
if [ ! -z "$GATEWAY" ]; then
    echo "测试网关 $GATEWAY 的常见代理端口..."
    for PORT in 8888 3128 1080 8080; do
        echo -n "  端口 $PORT: "
        timeout 2 curl -s -x http://$GATEWAY:$PORT https://www.baidu.com > /dev/null 2>&1 && echo "✅ 可用" || echo "❌ 不可用"
    done
fi

echo ""

echo "【8】DNS解析"
echo "----------------------------------------"
echo "解析 qyapi.weixin.qq.com:"
getent hosts qyapi.weixin.qq.com 2>/dev/null || echo "  解析失败"

echo ""

echo "===================================="
echo "📊 诊断总结"
echo "===================================="
echo ""
echo "容器网关（宿主机）: $GATEWAY"
echo "已配置白名单IP: 116.136.130.162"
echo ""
echo "💡 建议："
echo ""
echo "如果所有出站IP测试都失败："
echo "  → 使用方案1: 在宿主机配置代理"
echo "  → 或联系管理员确认真实出站IP"
echo ""
echo "如果获取到了出站IP（不是116.136.130.162）："
echo "  → 将该IP添加到企业微信白名单"
echo ""
echo "如果可以访问宿主机："
echo "  → 在 $GATEWAY 上安装tinyproxy"
echo "  → 修改代码使用代理: http://$GATEWAY:8888"
echo ""
echo "===================================="

