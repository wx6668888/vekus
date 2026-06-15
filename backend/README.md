# Vekus Backend

本地开发示例：

```bash
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

启动后会自动创建 `vekus.db`，并初始化示例用户、客户、报价和参数数据。

可用接口：
- `GET /api/health`
- `GET /api/dashboard/summary`
- `GET /api/customers`
- `GET /api/quotes`
- `GET /api/settings`
