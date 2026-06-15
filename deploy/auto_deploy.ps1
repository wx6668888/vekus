# Vekus 自动部署脚本 - 在本地 PowerShell 运行
# 用法: .\deploy\auto_deploy.ps1

$ServerIP = "119.91.31.248"
$User = "ubuntu"
$Pass = 'M8ZX~Lh4r|3qu[g/'
$AppDir = "/data/www/vekus"
$ProjectDir = "D:\360MoveData\Users\Administrator\Desktop\识价"

Write-Host "=== Vekus 自动部署到 $ServerIP ===" -ForegroundColor Green

# Step 1: Package files
Write-Host "`n[1/4] 打包应用文件..." -ForegroundColor Cyan
Set-Location $ProjectDir
npm run build 2>&1 | Out-Null
Write-Host "  前端构建完成"

# Create temp directory
$tmpDir = "$env:TEMP\vekus_deploy"
Remove-Item -Recurse -Force $tmpDir -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path "$tmpDir\backend\app\processors" -Force | Out-Null
New-Item -ItemType Directory -Path "$tmpDir\dist" -Force | Out-Null

# Copy backend
Copy-Item -Recurse "$ProjectDir\backend\app\*" "$tmpDir\backend\app\" -Force
Copy-Item "$ProjectDir\requirements.txt" "$tmpDir\backend\" -Force

# Copy frontend dist
Copy-Item -Recurse "$ProjectDir\dist\*" "$tmpDir\dist\" -Force

# Create .env
@"
VEKUS_AI_PROVIDER=deepseek
VEKUS_AI_API_KEY=<填写API_KEY>
AI_CHAT_API_KEY=<填写API_KEY>
AI_CHAT_API_BASE=https://api.deepseek.com/v1
AI_CHAT_MODEL=deepseek-chat
"@ | Out-File -FilePath "$tmpDir\.env" -Encoding utf8

# Create setup script for server
@'
#!/bin/bash
set -e
echo ">>> Installing dependencies..."
sudo apt update -qq
sudo apt install -y -qq python3.11 python3.11-venv python3-pip nginx

echo ">>> Creating directories..."
sudo mkdir -p /data/www/vekus/storage/uploads
sudo chown -R ubuntu:ubuntu /data/www

echo ">>> Setting up Python venv..."
python3.11 -m venv /data/www/vekus/venv
source /data/www/vekus/venv/bin/activate
pip install -q fastapi uvicorn[standard] sqlalchemy pydantic python-multipart requests

echo ">>> Moving app files..."
cp -r /home/ubuntu/deploy_backend/* /data/www/vekus/backend/
cp -r /home/ubuntu/deploy_dist/* /data/www/vekus/dist/
cp /home/ubuntu/deploy_env /data/www/vekus/.env

echo ">>> Configuring Nginx..."
sudo tee /etc/nginx/sites-available/vekus > /dev/null << 'NGX'
upstream vekus_api { server 127.0.0.1:8001; server 127.0.0.1:8002; keepalive 16; }
server {
    listen 80; server_name _; client_max_body_size 20m;
    gzip on; gzip_vary on; gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript image/svg+xml;
    root /data/www/vekus/dist; index index.html;
    location / { try_files $uri $uri/ /index.html; }
    location /api/ {
        proxy_pass http://vekus_api; proxy_http_version 1.1;
        proxy_set_header Host $host; proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Connection ""; proxy_read_timeout 120s;
    }
    location /assets/ { expires 1y; add_header Cache-Control "public, immutable"; }
}
NGX
sudo ln -sf /etc/nginx/sites-available/vekus /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx

echo ">>> Configuring systemd..."
sudo tee /etc/systemd/system/vekus-api.service > /dev/null << 'SVC'
[Unit]
Description=Vekus API
After=network.target
[Service]
Type=simple
User=ubuntu
WorkingDirectory=/data/www/vekus
EnvironmentFile=/data/www/vekus/.env
ExecStart=/data/www/vekus/venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
Restart=on-failure
[Install]
WantedBy=multi-user.target
SVC
sudo systemctl daemon-reload
sudo systemctl enable vekus-api
sudo systemctl restart vekus-api

echo ">>> Done! Visit http://$(curl -s ifconfig.me)"
'@ | Out-File -FilePath "$tmpDir\setup.sh" -Encoding ascii -NoNewline

Write-Host "  打包完成"

# Step 2: Upload via SCP
Write-Host "`n[2/4] 上传文件到服务器..." -ForegroundColor Cyan

# Use .NET for SCP with password
Add-Type -AssemblyName System.Windows.Forms
$ErrorActionPreference = 'Stop'

function Scp-File {
    param($LocalPath, $RemotePath)
    $cmd = "scp -o StrictHostKeyChecking=no -o ConnectTimeout=10 -r `"$LocalPath`" ${User}@${ServerIP}:`"$RemotePath`""
    Write-Host "  scp: $LocalPath -> $RemotePath"
    # Use WScript.Shell to send password
    $wshell = New-Object -ComObject WScript.Shell
    $proc = Start-Process -FilePath "cmd.exe" -ArgumentList "/c $cmd" -PassThru -NoNewWindow -RedirectStandardOutput "$env:TEMP\scp_out.txt" -RedirectStandardError "$env:TEMP\scp_err.txt"
    Start-Sleep -Seconds 8
    $wshell.SendKeys("$Pass~")
    $proc.WaitForExit(60000)
    if ($proc.ExitCode -ne 0) { throw "SCP failed" }
}

try {
    # Upload backend
    scp -o StrictHostKeyChecking=no -o ConnectTimeout=10 -r "$tmpDir\backend" "${User}@${ServerIP}:/home/ubuntu/deploy_backend"
    Write-Host "  backend uploaded"
} catch {
    Write-Host "  SCP needs manual execution. Run:" -ForegroundColor Yellow
    Write-Host "  scp -r $tmpDir\backend ${User}@${ServerIP}:/home/ubuntu/deploy_backend" -ForegroundColor Yellow
}

Write-Host "`n[3/4] 请在终端执行以下命令完成部署:" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Yellow
Write-Host "scp -r $tmpDir\* ubuntu@119.91.31.248:/home/ubuntu/"
Write-Host "ssh ubuntu@119.91.31.248"
Write-Host "# 然后在服务器上执行:"
Write-Host "bash /home/ubuntu/setup.sh"
Write-Host "================================================" -ForegroundColor Yellow
Write-Host "`n部署文件已准备在: $tmpDir" -ForegroundColor Green
