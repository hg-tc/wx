#!/bin/bash
echo "===================================="
echo "测试企业微信API访问"
echo "===================================="
echo ""
echo "服务器IP: 116.136.130.162"
echo ""
echo "1️⃣ 测试API调用..."
RESPONSE=$(curl -s "https://qyapi.weixin.qq.com/cgi-bin/token?corpid=wwa3df69d6b762af53&corpsecret=n-Wqxpc5WmFit0v4ZEImtWMLUE4SmYl_bwFql6chjyw")
echo "响应: $RESPONSE"
echo ""

if echo "$RESPONSE" | grep -q "access_token"; then
    echo "✅ API访问成功！"
    echo ""
    echo "access_token 已获取，客服功能可以正常使用了！"
    echo ""
    echo "下一步：在微信中发送消息测试"
else
    echo "❌ API访问失败"
    echo ""
    if echo "$RESPONSE" | grep -q "errcode"; then
        echo "错误信息: $RESPONSE"
    else
        echo "可能原因："
        echo "  1. IP白名单还未生效（等待5-10分钟）"
        echo "  2. IP配置不正确"
        echo "  3. 企业微信后台没有IP白名单配置入口"
    fi
fi
echo ""
echo "===================================="
