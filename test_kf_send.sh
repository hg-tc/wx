#!/bin/bash

echo "===================================="
echo "测试发送客服消息"
echo "===================================="
echo ""

# 获取access_token
echo "1️⃣ 获取access_token..."
TOKEN_RESPONSE=$(curl -s "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wwa3df69d6b762af53&corpsecret=n-Wqxpc5WmFit0v4ZEImtWMLUE4SmYl_bwFql6chjyw")
echo "响应: $TOKEN_RESPONSE"

ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "access_token: ${ACCESS_TOKEN:0:20}..."
echo ""

# 测试发送消息
echo "2️⃣ 测试发送客服消息..."
SEND_RESPONSE=$(curl -s -X POST "https://qyapi.weixin.qq.com/cgi-bin/kf/send_msg?access_token=$ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "touser": "wm7lKAVwAAG68dSOO7G4EVpN1eScOUPw",
    "open_kfid": "wk7lKAVwAAADCtArVetgUpxDBFQHef6A",
    "msgtype": "text",
    "text": {
      "content": "这是一条测试消息"
    }
  }')

echo "发送响应: $SEND_RESPONSE"
echo ""

if echo "$SEND_RESPONSE" | grep -q '"errcode":0'; then
    echo "✅ 发送成功！"
else
    echo "❌ 发送失败"
    ERROR_CODE=$(echo $SEND_RESPONSE | grep -o '"errcode":[0-9]*' | cut -d':' -f2)
    echo "错误码: $ERROR_CODE"
    
    if [ "$ERROR_CODE" = "95018" ]; then
        echo ""
        echo "💡 错误95018的可能原因："
        echo "  1. 客服账号需要使用独立的Secret（WECOM_KF_SECRET）"
        echo "  2. 会话状态不允许机器人发送（需要人工接待人员）"
        echo "  3. 客服账号配置不完整"
    fi
fi

echo ""
echo "===================================="

