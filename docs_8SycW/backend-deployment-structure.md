# Vekus 可部署后端结构

## 目录结构
backend/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── services/
│   │   ├── ai_pipeline.py
│   │   ├── async_queue.py
│   │   ├── dwg_parser.py
│   │   ├── field_mapper.py
│   │   ├── file_type.py
│   │   ├── processor.py
│   │   └── scan_service.py
│   └── __init__.py
├── storage/
│   └── uploads/
├── requirements.txt
├── .env.example
└── README.md

## 环境变量
- VEKUS_ENV=production
- VEKUS_HOST=0.0.0.0
- VEKUS_PORT=8000
- VEKUS_STORAGE_DIR=backend/storage/uploads
- VEKUS_CORS_ORIGINS=https://vekus.qzz.io
- VEKUS_AI_PROVIDER=mock|openai|anthropic|qwen
- VEKUS_AI_API_KEY=your_key_here
- VEKUS_AI_BASE_URL=https://api.example.com

## 启动方式
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 生产建议
- 使用 systemd / supervisor 守护进程
- Nginx 反向代理 /api 到 uvicorn
- 静态前端由 Nginx 提供
- 上传目录独立挂载
- 任务队列后续可替换为 Redis/Celery

## 部署步骤
1. 安装 Python 依赖
2. 配置 .env
3. 启动 uvicorn
4. 配置 Nginx
5. 验证 /health
6. 验证 /api/ai/scan
7. 验证前端回填闭环
