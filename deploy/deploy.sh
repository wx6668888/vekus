#!/bin/bash
# Vekus 部署脚本 — CentOS 7+/Ubuntu 20.04+
set -e

APP_DIR="/data/www/vekus"
echo "=== Vekus 部署开始 ==="

# 1. 系统依赖
if [ -f /etc/redhat-release ]; then
    sudo yum install -y python311 python311-pip nginx
else
    sudo apt update && sudo apt install -y python3.11 python3.11-venv nginx
fi

# 2. 创建目录
sudo mkdir -p $APP_DIR/storage/uploads $APP_DIR/logs

# 3. Python虚拟环境
python3.11 -m venv $APP_DIR/venv
source $APP_DIR/venv/bin/activate
pip install fastapi uvicorn[standard] sqlalchemy pydantic python-multipart requests
deactivate

# 4. 复制文件
cp -r backend $APP_DIR/
cp -r dist $APP_DIR/

# 5. 请在服务器上手动创建 $APP_DIR/.env 文件
echo "请创建 $APP_DIR/.env 文件并配置API Key后再继续"

# 6. Nginx
sudo cp deploy/nginx.conf /etc/nginx/conf.d/vekus.conf
sudo nginx -t && sudo systemctl reload nginx

# 7. Systemd
sudo cp deploy/vekus-api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable vekus-api
echo "=== 部署完成 ==="
