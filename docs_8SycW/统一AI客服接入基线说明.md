# Vekus 统一 AI 客服接入基线说明

## 1. 基线目标
本文用于固化当前统一 AI 客服的实现方式，作为后续页面改版、重构和恢复时的参考基线。

只要遵守本基线，就可以保证：
- 全站客服入口一致
- 页面欢迎语一致
- 后端 AI 接口一致
- 远程模型与本地兜底策略一致
- 手机端与桌面端体验一致

---

## 2. 当前统一接入方式
### 2.1 前端入口
统一客服组件由 `frontend-pages/quote-data.js` 提供，核心函数为：
- `initCustomerServiceWidget()`
- `pageWelcome()`
- `sendToAI()`
- `setStatus()`
- `showTyping()`

### 2.2 已接入页面
以下页面均应调用同一套客服入口：
- `frontend-pages/index.html`
- `frontend-pages/login.html`
- `frontend-pages/quote.html`
- `frontend-pages/history.html`
- `frontend-pages/marketplace.html`
- `frontend-pages/settings.html`
- `frontend-pages/profile.html`

### 2.3 接入时机
页面在完成导航渲染后，应调用：
```javascript
window.VekusData.initCustomerServiceWidget();
```

---

## 3. 视觉基线
### 3.1 入口按钮
- 右下角悬浮
- 优先显示 Lottie 动图
- 动图失败时自动回退成 `AI / 客服` 文本按钮
- 保持明显可点击

### 3.2 客服面板
- 苹果式圆角卡片
- 桌面与手机端统一为居中浮层
- 手机端不使用全屏模式
- 面板约占屏幕 70% 高度
- 关闭按钮只保留 `×`

### 3.3 交互风格
- 欢迎语
- 快捷问题
- 正在思考中
- 时间戳
- 重试按钮
- 状态提示

---

## 4. 问答基线
### 4.1 页面欢迎语
客服首次打开时，应根据当前页面显示不同欢迎语：
- 首页：产品功能与工作台入口
- 登录页：账号、角色、登录方式
- 报价页：报价、识图、参数计算
- 历史页：历史搜索、复用、详情
- 交易页：发布、库存、供需信息
- 参数页：材料、表面处理、焊接、孔类配置
- 我的页：账号、角色、权限、快捷入口

### 4.2 首次引导
首次打开时应再补一条引导提示，帮助用户快速理解可问内容。

---

## 5. 后端基线
### 5.1 统一接口
统一客服后端接口为：
- `POST /api/ai/customer-service`

### 5.2 远程模型优先
后端应优先使用远程模型代理。

推荐环境变量：
- `AI_CHAT_API_KEY`
- `AI_CHAT_API_BASE`
- `AI_CHAT_MODEL`
- `AI_CHAT_HTTP_REFERER`
- `AI_CHAT_TITLE`

### 5.3 本地兜底
当远程模型不可用时，必须自动降级为本地文档回答。

---

## 6. 文档基线
当客服逻辑变化时，必须同步更新以下文档：
- `docs/页面功能介绍.md`
- `docs/统一AI客服接入说明.md`
- `docs/统一AI客服部署与排查指南.md`

如有新的客服策略或接入调整，应在本文件新增记录。

---

## 7. 恢复步骤
如果后续页面被覆盖或丢失客服入口，按以下顺序恢复：
1. 确认页面仍引入 `frontend-pages/quote-data.js`
2. 确认页面调用 `window.VekusData.initCustomerServiceWidget()`
3. 检查后端 `/api/ai/customer-service`
4. 检查环境变量是否配置
5. 检查浏览器缓存和静态文件部署
6. 检查 `/在线客服.lottie` 是否可访问

---

## 8. 当前版本状态
截至本次记录，统一 AI 客服已覆盖：
- 首页
- 登录页
- 报价页
- 历史页
- 交易页
- 参数页
- 我的页

并且对应的说明文档均已保存。

---

## 9. 版本备注
- 2026-04-28：建立统一 AI 客服基线说明，作为后续恢复与回归检查依据。
