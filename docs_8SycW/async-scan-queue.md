# Vekus 异步识图任务队列

## 目标
上传文件后立即返回 scanId，后台异步处理，前端轮询结果。

## 流程
1. POST /api/ai/scan 上传文件
2. 创建 scanId
3. 入队
4. 后台线程处理
5. GET /api/ai/scan/{scanId} 查询状态
6. 完成后返回 quotePayload

## 状态
- pending
- processing
- done
- failed

## 优点
- 上传接口响应快
- 大文件不会阻塞前端
- 支持后续替换成 Celery / Redis Queue / RabbitMQ

## 当前实现
- 内存队列
- 后台线程
- 适合原型和单机部署

## 后续升级
- 持久化任务表
- 任务重试
- 分布式队列
- 结果缓存
