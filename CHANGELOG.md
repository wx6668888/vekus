# Changelog

所有显著的项目变更都会记录在此文件中。

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
