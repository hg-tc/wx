#!/bin/bash

echo "===================================="
echo "添加客服接待人员"
echo "===================================="
echo ""

# 获取access_token
echo "1️⃣ 获取access_token..."
TOKEN_RESPONSE=$(curl -s "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wwa3df69d6b762af53&corpsecret=n-Wqxpc5WmFit0v4ZEImtWMLUE4SmYl_bwFql6chjyw")
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "access_token: ${ACCESS_TOKEN:0:20}..."
echo ""

# 获取当前接待人员列表
echo "2️⃣ 查询当前接待人员..."
LIST_RESPONSE=$(curl -s -X POST "https://qyapi.weixin.qq.com/cgi-bin/kf/servicer/list?access_token=$ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "open_kfid": "wk7lKAVwAAADCtArVetgUpxDBFQHef6A"
  }')

echo "响应: $LIST_RESPONSE"
echo ""

# 检查是否有接待人员
if echo "$LIST_RESPONSE" | grep -q '"servicer_list":\[\]'; then
    echo "⚠️  当前没有接待人员"
    echo ""
    echo "💡 需要添加接待人员（使用你的企业微信账号UserID）"
    echo ""
    echo "请问你的企业微信UserID是什么？"
    echo "（可以在企业微信管理后台 → 通讯录 → 成员详情 中查看）"
else
    echo "✅ 已有接待人员"
fi

echo ""
echo "===================================="

