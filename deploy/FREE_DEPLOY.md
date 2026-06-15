# Vekus 免费部署方案

## 方案A: ngrok（推荐测试用，最简单）

# 1. 下载 ngrok: https://ngrok.com/download
# 2. 注册免费账号获取 authtoken
# 3. 一键暴露本地后端:

ngrok http 8000

# 会得到一个公网URL如 https://xxx.ngrok-free.app
# 前端Vite的代理需要指向这个URL

## 方案B: Render.com 免费部署(推荐)

# 将项目推送到 GitHub，然后在 Render 关联仓库即可自动部署
# 免费额度: 每月750小时运行时间 + 100GB带宽
