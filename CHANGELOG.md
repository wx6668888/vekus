# Changelog

所有显著的项目变更都会记录在此文件中。

---

## [2026-06-16] — 微信二维码弹窗 + 科技感动态 Logo

### 变更
- **LoginView / RegisterView**: 微信按钮去文字、图标居中、点击弹出二维码模态框（Canvas 模拟 QR 码）
- **Logo**: 新增跑马灯渐变边框 + 脉冲呼吸动画，科技感效果
- QR 模态框：白色卡片 + 模糊遮罩 + 缩放进场动画

### 部署
- 119.91.31.248 ✅

---

## [2026-06-16] — 注册页公司字段 + 微信登录

### 变更
- **RegisterView.vue**: 业务员角色也需要填写公司，合并为统一的「选择或输入公司」字段（不再区分 boss/sales）
- **LoginView.vue**: 社交登录区改为仅微信登录按钮，绿色主题
- **RegisterView.vue**: 同上，微信登录按钮

### 部署
- 119.91.31.248 ✅

---

## [2026-06-16] — 登录/注册页 UI 重设计

### 变更
- **LoginView.vue**: 全新设计 —— 深蓝渐变背景、Canvas 粒子动画、浮动标签输入框、暗色/亮色模式切换、密码显隐切换、社交登录装饰图标
- **RegisterView.vue**: 全新设计 —— 与登录页统一风格、角色选择动画、老板自动展开工厂名称
- **App.vue**: 登录/注册页自动隐藏顶部导航栏
- **router**: `/login` 和 `/register` 路由保持原样，meta 已有 `public: true`

### 技术细节
- 使用 Canvas API 实现粒子动画背景
- 浮动标签通过 CSS `:placeholder-shown` + `:focus` 实现
- 暗色模式跟随 `prefers-color-scheme` 系统偏好
- 所有现有 API 调用和状态管理逻辑保持不变
- 部署到 119.91.31.248 ✅

### 文件
- `src/App.vue` — 添加 `useRoute` 判断 auth 页面
- `src/views/LoginView.vue` — 完全重写
- `src/views/RegisterView.vue` — 完全重写
- `CHANGELOG.md` — 新建

---

## [2026-06-15] — 华为云新服务器部署

### 变更
- 在华为云 42.123.123.155 (wabzrtbljqk1rd6y) 部署 Vekus 项目
- 安装依赖: nginx, Python 3.11, venv, fastapi, uvicorn, sqlalchemy 等
- 配置 Nginx + systemd vekus-api 服务
- 初始化 SQLite 数据库 (22 张表，含种子数据)
- 外部访问被天翼云网络层拦截（待解决）

### 文件
- 服务器部署配置文件 (nginx.conf, vekus-api.service)
- 数据库 seed 脚本 seed_all.py
