# Vekus 统一 AI 客服部署与排查指南

## 1. 目的
本文用于说明统一 AI 客服的部署方式、依赖配置与常见问题排查方法，避免后续页面被覆盖或客服入口丢失。

---

## 2. 前端核心文件
统一客服入口主要由以下文件提供：

- `frontend-pages/quote-data.js`

其中核心函数是：
- `initCustomerServiceWidget()`
- `pageWelcome()`
- `sendToAI()`
- `setStatus()`

---

## 3. 接入页面
当前统一客服应在以下页面可见：

- `frontend-pages/index.html`
- `frontend-pages/login.html`
- `frontend-pages/quote.html`
- `frontend-pages/history.html`
- `frontend-pages/marketplace.html`
- `frontend-pages/settings.html`
- `frontend-pages/profile.html`

如果任一页面缺失客服入口，优先检查页面是否仍然引入了 `quote-data.js`，以及是否调用了 `window.VekusData.initCustomerServiceWidget()`。

---

## 4. 当前核对结果
截至本次更新，以下页面已完成统一客服入口接入：

- [x] 首页 `index.html`
- [x] 登录页 `login.html`
- [x] 报价页 `quote.html`
- [x] 历史页 `history.html`
- [x] 交易页 `marketplace.html`
- [x] 参数页 `settings.html`
- [x] 我的页 `profile.html`

---

## 5. 后端接口
统一客服依赖后端接口：

- `POST /api/ai/customer-service`

成功时可能返回：
- `provider: remote`
- `model`
- `endpoint`
- `used_context`
- `status: connected`

失败降级时可能返回：
- `provider: local-fallback`
- `status: fallback`
- `remote_error`

---

## 6. 环境变量
远程模型接入可通过以下环境变量配置：

- `AI_CHAT_API_KEY`
- `AI_CHAT_API_BASE`
- `AI_CHAT_MODEL`
- `AI_CHAT_HTTP_REFERER`
- `AI_CHAT_TITLE`

如果没有配置 `AI_CHAT_API_KEY`，后端会自动降级为本地文档回答。

---

## 7. 动图不显示排查
如果客服按钮动图不显示，按以下顺序检查：

1. 确认 `/在线客服.lottie` 文件存在
2. 确认文件不是空文件
3. 确认页面可访问该路径
4. 确认浏览器没有缓存旧资源
5. 如果加载失败，前端会自动回退成文字按钮 `AI / 客服`

---

## 8. AI 不接入排查
如果客服能打开，但回答一直走本地兜底，按以下顺序检查：

1. 后端是否启动成功
2. `AI_CHAT_API_KEY` 是否配置
3. `AI_CHAT_API_BASE` 是否可访问
4. 模型名是否可用
5. 浏览器控制台和后端日志是否有 401 / 403 / 5xx 错误

---

## 9. 页面被覆盖后的恢复方法
如果页面被旧版本覆盖，优先检查：

1. 页面是否仍然引入 `frontend-pages/quote-data.js`
2. 是否仍调用 `initCustomerServiceWidget()`
3. 是否存在缓存未刷新
4. 是否部署到了正确目录

恢复时应优先保证：
- 客服入口存在
- 欢迎语存在
- 后端接口仍可请求
- 本地兜底逻辑未丢失

---

## 10. 部署建议
- 前端改动后务必重新部署静态文件
- 后端改动后务必重启服务
- 发布前先检查页面是否能加载统一客服
- 必要时清理浏览器缓存

---

## 11. 验收清单
部署完成后建议检查：
- [ ] 首页可见客服入口
- [ ] 登录页可见客服入口
- [ ] 报价页可见客服入口
- [ ] 历史页可见客服入口
- [ ] 交易页可见客服入口
- [ ] 参数页可见客服入口
- [ ] 我的页可见客服入口
- [ ] 发送问题后能显示“正在思考中”
- [ ] 远程模型成功时返回 `provider: remote`
- [ ] 远程失败时可自动降级本地回答
