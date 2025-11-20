#!/bin/bash
# 部署脚本

set -e

APP_DIR="/opt/wecom-agent"
VENV_DIR="$APP_DIR/venv"

echo "==> 停止服务"
sudo systemctl stop wecom-api || true
sudo systemctl stop wecom-celery || true
sudo systemctl stop wecom-celery-beat || true

echo "==> 拉取最新代码"
cd $APP_DIR
git pull origin main || echo "跳过git pull（非git仓库或无远程）"

echo "==> 激活虚拟环境"
source $VENV_DIR/bin/activate

echo "==> 安装/更新依赖"
pip install -r requirements.txt

echo "==> 运行数据库迁移"
alembic upgrade head

echo "==> 重启服务"
sudo systemctl start wecom-api
sudo systemctl start wecom-celery
sudo systemctl start wecom-celery-beat

echo "==> 等待服务启动..."
sleep 3

echo "==> 检查服务状态"
sudo systemctl status wecom-api --no-pager
sudo systemctl status wecom-celery --no-pager
sudo systemctl status wecom-celery-beat --no-pager

echo "==> 部署完成！"

