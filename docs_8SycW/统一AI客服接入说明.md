# Vekus 统一 AI 客服接入说明

## 1. 接入目标
为 Vekus 前端全站页面提供统一的 AI 客服入口，支持：
- 页面场景化问答
- 报价、参数、历史、交易、账号咨询
- 后端模型代理
- 本地文档兜底
- 手机端与桌面端统一体验

---

## 2. 前端接入方式

### 2.1 统一公共组件
AI 客服主要由 `frontend-pages/quote-data.js` 中的 `initCustomerServiceWidget()` 负责注入。

### 2.2 已接入页面
以下页面均调用同一套客服组件：
- `frontend-pages/index.html`
- `frontend-pages/login.html`
- `frontend-pages/quote.html`
- `frontend-pages/history.html`
- `frontend-pages/marketplace.html`
- `frontend-pages/settings.html`
- `frontend-pages/profile.html`

### 2.3 前端交互能力
客服组件包含：
- 悬浮入口按钮
- 动图 / 文本兜底入口
- 苹果式圆角聊天卡片
- 页面欢迎语
- 快捷问题按钮
- 思考中状态
- 时间戳
- 重试按钮
- 关闭按钮 `×`
- 消息滚动到底部

---

## 3. 后端接口

### 3.1 接口地址
`POST /api/ai/customer-service`

### 3.2 请求参数
```json
{
  "question": "如何设置材料参数？",
  "context": "可选的文档上下文",
  "source": "frontend-customer-service"
}
```

### 3.3 返回字段
#### 远程模型成功时
```json
{
  "answer": "...",
  "provider": "remote",
  "model": "openai/gpt-4o-mini",
  "endpoint": "https://openrouter.ai/api/v1/chat/completions",
  "used_context": true,
  "status": "connected"
}
```

#### 本地兜底时
```json
{
  "answer": "...",
  "provider": "local-fallback",
  "status": "fallback",
  "remote_error": "missing_api_key",
  "context": "..."
}
```

---

## 4. 模型代理策略

### 4.1 优先远程模型
后端优先读取环境变量：
- `AI_CHAT_API_KEY`
- `AI_CHAT_API_BASE`
- `AI_CHAT_MODEL`

默认支持 OpenRouter 风格的 Chat Completions 接口。

### 4.2 文档上下文
后端会自动读取 `docs/` 下的项目文档，并将摘要拼接进 system prompt。

### 4.3 本地兜底
当远程模型不可用时，后端会根据关键字返回本地说明，例如：
- 报价参数
- 系统配置
- 历史页说明

---

## 5. 页面场景欢迎语
客服组件会根据当前页面自动生成欢迎语：
- 首页：产品功能与工作台入口
- 登录页：账号、角色、登录方式
- 报价页：报价、识图、参数计算
- 历史页：历史搜索、复用、详情
- 交易页：发布、库存、供需信息
- 参数页：材料、表面处理、焊接、孔类配置
- 我的页：账号、角色、权限、快捷入口

---

## 6. 维护说明
- 修改客服组件时，优先改 `quote-data.js`
- 如调整问答策略，优先更新后端 `/api/ai/customer-service`
- 每次修改后需要同步更新此文档，确保前后端一致

---

## 7. 注意事项
- 不要在前端硬编码 API Key
- 动图资源若不可用，应自动回退到文本按钮
- 客服面板在移动端应保持圆角卡片，不建议改成全屏模式
- 修改 UI 时要保持全站一致性
