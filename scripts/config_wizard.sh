#!/bin/bash
# 企业微信配置向导

cd /root/wx

echo "=============================================="
echo "企业微信配置向导"
echo "=============================================="
echo ""

echo "请按照以下步骤获取配置参数："
echo ""

# 1. Corp ID
echo "📝 1. 获取企业ID (Corp ID)"
echo "   步骤："
echo "   a. 访问: https://work.weixin.qq.com/wework_admin/"
echo "   b. 登录企业微信管理后台"
echo "   c. 点击左侧菜单「我的企业」"
echo "   d. 在「企业信息」区域找到「企业ID」"
echo "   e. 复制企业ID（格式: ww1234567890abcdef）"
echo ""
read -p "请输入企业ID (Corp ID): " CORP_ID

if [ -z "$CORP_ID" ]; then
    echo "❌ 企业ID不能为空"
    exit 1
fi

# 验证格式
if [[ ! $CORP_ID =~ ^ww[a-z0-9]{16}$ ]]; then
    echo "⚠️  警告: 企业ID格式可能不正确（通常是ww开头的18位字符）"
    read -p "是否继续？(y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "✅ 企业ID: $CORP_ID"
echo ""

# 2. Agent ID
echo "📝 2. 获取应用ID (Agent ID)"
echo "   步骤："
echo "   a. 在管理后台，点击「应用管理」"
echo "   b. 点击「自建」标签"
echo "   c. 找到你的应用，点击进入"
echo "   d. 在应用详情页找到「AgentId」"
echo "   e. 复制应用ID（格式: 1000002）"
echo ""
read -p "请输入应用ID (Agent ID): " AGENT_ID

if [ -z "$AGENT_ID" ]; then
    echo "❌ 应用ID不能为空"
    exit 1
fi

echo "✅ 应用ID: $AGENT_ID"
echo ""

# 3. Secret
echo "📝 3. 获取应用密钥 (Secret)"
echo "   步骤："
echo "   a. 在应用详情页找到「Secret」"
echo "   b. 点击「查看」按钮"
echo "   c. 使用管理员扫码验证"
echo "   d. 复制显示的Secret（43个字符）"
echo ""
read -p "请输入应用密钥 (Secret): " SECRET

if [ -z "$SECRET" ]; then
    echo "❌ 应用密钥不能为空"
    exit 1
fi

echo "✅ 应用密钥: ${SECRET:0:10}...（已隐藏）"
echo ""

# 4. Token
echo "📝 4. 配置 Token"
echo "   选项A: 自动生成（推荐）"
echo "   选项B: 手动输入"
echo ""
read -p "是否自动生成Token？(y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    source venv/bin/activate
    TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(16))")
    echo "✅ 已生成Token: $TOKEN"
else
    read -p "请输入Token (3-32位): " TOKEN
    if [ -z "$TOKEN" ]; then
        echo "❌ Token不能为空"
        exit 1
    fi
fi

echo ""

# 5. EncodingAESKey
echo "📝 5. 配置 EncodingAESKey"
echo "   选项A: 自动生成43位密钥（推荐）"
echo "   选项B: 从企业微信后台复制"
echo ""
read -p "是否自动生成EncodingAESKey？(y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    source venv/bin/activate
    AES_KEY=$(python3 -c "import base64, os; print(base64.b64encode(os.urandom(32)).decode().rstrip('='))")
    echo "✅ 已生成EncodingAESKey: $AES_KEY"
    echo "   长度: ${#AES_KEY} 位"
else
    read -p "请输入EncodingAESKey (43位): " AES_KEY
    if [ -z "$AES_KEY" ]; then
        echo "❌ EncodingAESKey不能为空"
        exit 1
    fi
    
    # 验证长度
    if [ ${#AES_KEY} -ne 43 ]; then
        echo "❌ EncodingAESKey长度必须是43位，当前是 ${#AES_KEY} 位"
        exit 1
    fi
fi

echo ""
echo "=============================================="
echo "配置汇总"
echo "=============================================="
echo "WECOM_CORP_ID=$CORP_ID"
echo "WECOM_AGENT_ID=$AGENT_ID"
echo "WECOM_SECRET=${SECRET:0:10}...（已隐藏完整密钥）"
echo "WECOM_TOKEN=$TOKEN"
echo "WECOM_ENCODING_AES_KEY=$AES_KEY"
echo ""

read -p "是否保存到 .env 文件？(y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 备份原文件
    if [ -f .env ]; then
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
        echo "✅ 已备份原 .env 文件"
    fi
    
    # 更新配置
    sed -i "s|^WECOM_CORP_ID=.*|WECOM_CORP_ID=$CORP_ID|" .env
    sed -i "s|^WECOM_AGENT_ID=.*|WECOM_AGENT_ID=$AGENT_ID|" .env
    sed -i "s|^WECOM_SECRET=.*|WECOM_SECRET=$SECRET|" .env
    sed -i "s|^WECOM_TOKEN=.*|WECOM_TOKEN=$TOKEN|" .env
    sed -i "s|^WECOM_ENCODING_AES_KEY=.*|WECOM_ENCODING_AES_KEY=$AES_KEY|" .env
    
    echo "✅ 配置已保存到 .env 文件"
    echo ""
    
    # 验证配置
    echo "正在验证配置..."
    source venv/bin/activate
    python scripts/test_wecom_callback.py
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "=============================================="
        echo "✅ 配置完成！"
        echo "=============================================="
        echo ""
        echo "📌 下一步操作："
        echo ""
        echo "1. 启动应用："
        echo "   ./scripts/start_dev.sh"
        echo ""
        echo "2. （本地开发）启动ngrok:"
        echo "   ngrok http 8000"
        echo ""
        echo "3. 在企业微信后台配置接收消息："
        echo "   URL: https://你的域名/api/v1/wecom/callback"
        echo "   Token: $TOKEN"
        echo "   EncodingAESKey: $AES_KEY"
        echo ""
        echo "4. 点击「保存」进行验证"
        echo ""
        echo "=============================================="
    else
        echo ""
        echo "❌ 配置验证失败，请检查参数是否正确"
    fi
else
    echo ""
    echo "配置未保存。你可以手动编辑 .env 文件："
    echo "nano /root/wx/.env"
fi

