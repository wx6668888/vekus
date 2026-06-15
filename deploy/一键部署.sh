#!/bin/bash
# Vekus 钣金AI报价平台 - 一键部署脚本
# 使用: scp 一键部署.sh ubuntu@119.91.31.248:/home/ubuntu/ && ssh ubuntu@119.91.31.248 "bash 一键部署.sh"
set -e

GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}   Vekus 钣金AI报价平台 - 服务器一键部署           ${NC}"
echo -e "${GREEN}================================================${NC}"

# 配置
APP_DIR="/data/www/vekus"
DOMAIN="119.91.31.248"

# 1. 更新系统并安装依赖
echo ">>> [1/6] 安装系统依赖..."
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip nginx curl

# 2. 创建目录结构
echo ">>> [2/6] 创建应用目录..."
sudo mkdir -p $APP_DIR/storage/uploads $APP_DIR/logs
sudo chown -R ubuntu:ubuntu /data/www

# 3. 创建 Python 虚拟环境并安装依赖
echo ">>> [3/6] 安装 Python 依赖..."
python3.11 -m venv $APP_DIR/venv
source $APP_DIR/venv/bin/activate
pip install fastapi uvicorn[standard] sqlalchemy pydantic python-multipart requests

# 4. 配置 Nginx
echo ">>> [4/6] 配置 Nginx..."
sudo tee /etc/nginx/sites-available/vekus > /dev/null << 'NGINX_EOF'
upstream vekus_api {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    keepalive 16;
}
server {
    listen 80;
    server_name _;
    client_max_body_size 20m;
    gzip on; gzip_vary on; gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml text/javascript image/svg+xml;
    root /data/www/vekus/dist;
    index index.html;
    location / { try_files $uri $uri/ /index.html; }
    location /api/ {
        proxy_pass http://vekus_api;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Connection "";
        proxy_read_timeout 120s;
    }
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
NGINX_EOF

sudo ln -sf /etc/nginx/sites-available/vekus /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

# 5. 创建环境配置
echo ">>> [5/6] 创建环境配置..."
sudo tee $APP_DIR/.env > /dev/null << 'ENV_EOF'
VEKUS_AI_PROVIDER=deepseek
VEKUS_AI_API_KEY=<填写API_KEY>
AI_CHAT_API_KEY=<填写API_KEY>
AI_CHAT_API_BASE=https://api.deepseek.com/v1
AI_CHAT_MODEL=deepseek-chat
ENV_EOF

# 6. 创建 systemd 服务
echo ">>> [6/6] 配置后台服务..."
sudo tee /etc/systemd/system/vekus-api.service > /dev/null << 'SVC_EOF'
[Unit]
Description=Vekus API Service
After=network.target
[Service]
Type=simple
User=ubuntu
WorkingDirectory=/data/www/vekus
EnvironmentFile=/data/www/vekus/.env
ExecStart=/data/www/vekus/venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
Restart=on-failure
RestartSec=5
[Install]
WantedBy=multi-user.target
SVC_EOF

sudo systemctl daemon-reload
sudo systemctl enable vekus-api

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}   基础环境部署完成!                                ${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "后续步骤:"
echo "1. 上传应用代码: scp -r backend/ dist/ ubuntu@$DOMAIN:$APP_DIR/"
echo "2. 编辑配置: sudo nano $APP_DIR/.env  (填入API Key)"
echo "3. 启动服务: sudo systemctl start vekus-api"
echo "4. 访问验证: http://$DOMAIN/"
echo ""
