#!/bin/bash
# 应用诊断脚本

cd /root/wx

echo "======================================"
echo "容器应用完整诊断"
echo "======================================"

# 1. 检查进程
echo -e "\n【1/8】检查应用进程"
echo "-------------------------------------"
if ps aux | grep -q '[u]vicorn app.main:app'; then
    echo "✅ 应用正在运行"
    ps aux | grep '[u]vicorn app.main:app'
else
    echo "❌ 应用未运行"
    echo "   请运行: ./scripts/start_background.sh"
    exit 1
fi

# 2. 检查端口
echo -e "\n【2/8】检查端口监听"
echo "-------------------------------------"
if netstat -tlnp 2>/dev/null | grep -q ':8000'; then
    echo "✅ 端口 8000 正在监听"
    netstat -tlnp | grep ':8000'
elif lsof -i :8000 >/dev/null 2>&1; then
    echo "✅ 端口 8000 正在监听"
    lsof -i :8000
else
    echo "❌ 端口 8000 未监听"
    exit 1
fi

# 3. 测试本地访问 - 健康检查
echo -e "\n【3/8】测试本地健康检查"
echo "-------------------------------------"
HEALTH=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8000/health 2>/dev/null)
if echo "$HEALTH" | grep -q "HTTP_CODE:200"; then
    echo "✅ 健康检查通过"
    echo "$HEALTH" | grep -v HTTP_CODE
else
    echo "❌ 健康检查失败"
    echo "$HEALTH"
fi

# 4. 测试回调接口
echo -e "\n【4/8】测试回调接口可访问性"
echo "-------------------------------------"
CALLBACK_TEST=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8000/api/v1/wecom/callback 2>/dev/null)
HTTP_CODE=$(echo "$CALLBACK_TEST" | grep HTTP_CODE | cut -d: -f2)
if [ "$HTTP_CODE" = "422" ] || [ "$HTTP_CODE" = "400" ]; then
    echo "✅ 回调接口可访问（参数缺失是正常的）"
    echo "HTTP状态码: $HTTP_CODE"
else
    echo "⚠️  HTTP状态码: $HTTP_CODE"
fi

# 5. 检查配置
echo -e "\n【5/8】检查企业微信配置"
echo "-------------------------------------"
source venv/bin/activate
python3 << 'EOF'
import sys
sys.path.insert(0, '/root/wx')
try:
    from app.config import get_settings
    settings = get_settings()
    
    print(f"Corp ID: {settings.WECOM_CORP_ID}")
    print(f"Agent ID: {settings.WECOM_AGENT_ID}")
    print(f"Token: {settings.WECOM_TOKEN[:10]}...（已隐藏）")
    print(f"Token长度: {len(settings.WECOM_TOKEN)} 字符")
    
    aes_len = len(settings.WECOM_ENCODING_AES_KEY)
    if aes_len == 43:
        print(f"✅ EncodingAESKey长度: {aes_len} 字符（正确）")
    else:
        print(f"❌ EncodingAESKey长度: {aes_len} 字符（应该是43）")
        sys.exit(1)
except Exception as e:
    print(f"❌ 配置加载失败: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo "配置有误，请检查 .env 文件"
    exit 1
fi

# 6. 检查日志
echo -e "\n【6/8】检查最近的请求日志"
echo "-------------------------------------"
if [ -f logs/uvicorn.log ]; then
    echo "最近5条uvicorn日志:"
    tail -5 logs/uvicorn.log | grep -v "^$"
else
    echo "⚠️  未找到 logs/uvicorn.log"
fi

if ls logs/app_*.log 1> /dev/null 2>&1; then
    echo -e "\n最近5条应用日志:"
    tail -5 logs/app_*.log | grep -v "^$" | head -5
fi

# 7. 搜索回调相关日志
echo -e "\n【7/8】搜索企业微信回调日志"
echo "-------------------------------------"
if [ -f logs/uvicorn.log ]; then
    CALLBACK_LOGS=$(grep -i "callback" logs/uvicorn.log 2>/dev/null | tail -3)
    if [ -n "$CALLBACK_LOGS" ]; then
        echo "✅ 找到回调请求记录:"
        echo "$CALLBACK_LOGS"
    else
        echo "⚠️  未找到任何回调请求记录"
        echo "   这意味着企业微信的请求可能没有到达容器"
    fi
fi

# 8. 生成测试命令
echo -e "\n【8/8】生成本地测试命令"
echo "-------------------------------------"
source venv/bin/activate
python3 << 'EOF'
import sys
sys.path.insert(0, '/root/wx')
from app.wecom.auth import WXBizMsgCrypt
from app.config import get_settings
import time
import urllib.parse

settings = get_settings()
crypto = WXBizMsgCrypt(
    settings.WECOM_TOKEN,
    settings.WECOM_ENCODING_AES_KEY,
    settings.WECOM_CORP_ID
)

timestamp = str(int(time.time()))
nonce = "test_nonce"
echostr_plain = "test_success"
encrypted_echostr, _ = crypto.encrypt_message(echostr_plain, nonce, timestamp)
signature = crypto._generate_signature(timestamp, nonce, encrypted_echostr)

# URL编码
encrypted_encoded = urllib.parse.quote(encrypted_echostr)

print("\n在容器内测试（复制以下命令执行）:")
print(f'curl "http://localhost:8000/api/v1/wecom/callback?msg_signature={signature}&timestamp={timestamp}&nonce={nonce}&echostr={encrypted_encoded}"')
print(f"\n✅ 期望返回: {echostr_plain}")
print(f"\n如果返回正确，说明应用本身工作正常")
print(f"如果企业微信验证失败，问题可能在转发服务器")
EOF

echo -e "\n======================================"
echo "诊断完成"
echo "======================================"
echo ""
echo "📌 下一步操作:"
echo ""
echo "1️⃣  如果上面的测试都通过，但企业微信验证失败："
echo "   → 问题在转发服务器"
echo "   → 查看文档: cat /root/wx/FORWARD_TROUBLESHOOTING.md"
echo ""
echo "2️⃣  监控实时请求："
echo "   → 运行: ./scripts/monitor_requests.sh"
echo "   → 然后在企业微信后台点击「保存」"
echo "   → 观察是否有请求到达"
echo ""
echo "3️⃣  如果没有看到任何请求到达："
echo "   → 检查转发服务器的Nginx配置"
echo "   → 在转发服务器测试: curl http://容器IP:8000/health"
echo ""
echo "======================================"

