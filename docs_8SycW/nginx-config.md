# Vekus Nginx 配置

## 前端静态站点 + 后端 API 反代

```nginx
server {
    listen 80;
    server_name vekus.qzz.io;

    root /www/wwwroot/vekus.qzz.io;
    index index.html;

    # 前端静态资源
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 后端健康检查
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 上传文件限制
    client_max_body_size 50m;

    # 缓存静态资源
    location ~* \.(js|css|png|jpg|jpeg|gif|svg|ico|webp)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

## HTTPS 版建议
- 80 端口做跳转到 443
- 443 端口配置 SSL 证书
- 继续保留 `/api/` 反代到后端

## 推荐额外配置
- gzip 压缩
- HTTP/2
- HSTS
- 上传大小限制
- 安全头
