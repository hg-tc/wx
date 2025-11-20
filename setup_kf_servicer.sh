#!/bin/bash

echo "===================================="
echo "🔧 配置客服接待人员"
echo "===================================="
echo ""

# 从.env读取配置
source .env

# 获取access_token
echo "1️⃣ 获取access_token..."
TOKEN_RESPONSE=$(curl -s "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=$WECOM_CORP_ID&corpsecret=$WECOM_SECRET")
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ 获取access_token失败"
    echo "响应: $TOKEN_RESPONSE"
    exit 1
fi

echo "✅ access_token: ${ACCESS_TOKEN:0:20}..."
echo ""

# 查询企业成员列表，获取可用的UserID
echo "2️⃣ 查询企业成员列表..."
MEMBER_RESPONSE=$(curl -s "https://qyapi.weixin.qq.com/cgi-bin/user/list?access_token=$ACCESS_TOKEN&department_id=1")

echo "成员列表响应: $MEMBER_RESPONSE"
echo ""

# 提取第一个成员的userid
FIRST_USERID=$(echo $MEMBER_RESPONSE | grep -o '"userid":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$FIRST_USERID" ]; then
    echo "⚠️  未找到企业成员"
    echo ""
    echo "请手动指定UserID："
    echo "bash setup_kf_servicer.sh YOUR_USERID"
    exit 1
fi

# 如果命令行提供了UserID，使用提供的
if [ ! -z "$1" ]; then
    USERID="$1"
    echo "📝 使用指定的UserID: $USERID"
else
    USERID="$FIRST_USERID"
    echo "📝 使用第一个成员的UserID: $USERID"
fi

echo ""

# 添加接待人员
echo "3️⃣ 添加接待人员..."
ADD_RESPONSE=$(curl -s -X POST "https://qyapi.weixin.qq.com/cgi-bin/kf/servicer/add?access_token=$ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"open_kfid\": \"$WECOM_KF_ACCOUNT_ID\",
    \"userid_list\": [\"$USERID\"]
  }")

echo "添加响应: $ADD_RESPONSE"
echo ""

if echo "$ADD_RESPONSE" | grep -q '"errcode":0'; then
    echo "✅ 成功添加接待人员: $USERID"
    echo ""
    echo "🎉 现在可以发送客服消息了！"
    echo ""
    echo "📱 请在微信中发送一条新消息测试"
else
    ERROR_CODE=$(echo $ADD_RESPONSE | grep -o '"errcode":[0-9]*' | cut -d':' -f2)
    if [ "$ERROR_CODE" = "86216" ]; then
        echo "ℹ️  该用户已经是接待人员"
        echo "✅ 接待人员配置正常"
    else
        echo "❌ 添加接待人员失败"
        echo "错误码: $ERROR_CODE"
    fi
fi

echo ""
echo "===================================="

