# Vekus 钣金 AI 智能报价平台

> 专为钣金加工行业打造的 AI 驱动 ERP 系统，覆盖从报价到生产的全流程管理。

[![Vue 3](https://img.shields.io/badge/Vue-3.x-4FC08D?logo=vue.js)](https://vuejs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.2-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)](https://python.org)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite)](https://sqlite.org)

**线上地址**: http://119.91.31.248

---

## 系统概述

Vekus 是为钣金加工企业量身打造的智能 ERP 平台：

- **AI 图纸识别**：上传 DWG/DXF/STEP/PDF/图片，自动提取板厚、展开尺寸、折弯数、孔数等参数
- **自动报价计算**：根据材料单价、工艺费率、税率自动计算报价总价
- **全流程管理**：报价 → BOM → 生产工单 → 质量检验 → 采购 → 库存 → 发票对账
- **企查查集成**：企业工商信息查询 + 18 类风险排查
- **AI 客服**：实时数据库上下文注入，可回答库存/订单/生产等问题

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite 5 + ECharts 5 + Three.js |
| 后端 | FastAPI + SQLAlchemy 2.0 + SQLite |
| 部署 | Nginx + Uvicorn + systemd |
| AI | DeepSeek V4 / Qwen-VL (七牛云) |

---

## 功能模块（17个）

| 模块 | 路由 | 核心功能 |
|------|------|----------|
| 📊 看板 | `/dashboard` | 6 KPI + ECharts 4图 + 销售漏斗 + 排行 |
| 📦 BOM | `/bom` | 3级树形/列表/物料编码/版本管理 |
| 🏭 库存 | `/inventory` | 出入库/流水/安全预警/库位 |
| ⚙️ 生产 | `/production` | 工单流转(草稿→完工)/报工/进度 |
| ✅ 质量 | `/quality` | 三检制(来料/过程/成品)/不良处理 |
| 🚚 采购 | `/purchases` | 供应商/订单/收货自动入库 |
| 📝 审批 | `/approvals` | 发起/通过/驳回 + 审计日志 |
| 📄 文档 | `/documents` | 图纸上传/下载/版本/统计 |
| 🧾 发票 | `/invoices` | 创建/发送/收款/13%增值税 |
| 🤖 报价 | `/quote` | AI识图→计算→3D预览→PDF导出 |
| 📋 历史 | `/history` | 报价历史/搜索/筛选/复用 |
| 👥 客户 | `/customers` | 企查查搜索/风险排查/Excel导入导出 |
| 🛒 交易 | `/marketplace` | 买卖发布/三级地址/图片上传 |
| 💬 消息 | `/messages` | AI客服+DB上下文/文件图片/系统通知 |
| 👤 人员 | `/people` | 员工档案/部门统计 |
| ⚙️ 设置 | `/settings` | 6类报价参数/公司信息 |
| 🔧 后台 | `/admin/users` | 用户管理(仅老板可见) |

---

## 数据库

**18 张表**: users, customers, quotes, pricing_parameters, bom_items, inventory, inventory_logs, production_orders, quality_checks, purchase_orders, suppliers, invoices, employees, equipment, listings, conversations, messages, approvals, audit_logs, payment_orders, points_transactions

---

## 快速开始

```bash
git clone https://github.com/wx6668888/vekus.git
cd 识价
npm install
pip install -r requirements.txt

# 终端1: 后端
python -m uvicorn backend.app.main:app --port 8000 --reload

# 终端2: 前端
npm run dev -- --port 3001

# 种子数据
cd backend && python seed_all.py
```

### 默认账号

| 角色 | 手机号 | 密码 |
|------|--------|------|
| 老板 | 13800000000 | 123456 |
| 业务员 | 13800000001 | 123456 |

---

## 部署

```bash
npm run build                              # 构建前端
scp -r dist/ backend/ user@host:/data/www/vekus/
sudo systemctl restart vekus-api           # 重启后端
```

---

## 项目结构

```
识价/
├── backend/app/
│   ├── main.py              # FastAPI (40+ API端点)
│   ├── models.py            # 18张数据表
│   └── processors/          # AI图纸处理器(DXF/DWG/STEP/Vision)
├── src/
│   ├── views/               # 17个视图页面
│   ├── components/          # 组件库(base/chat/data/layout/quote)
│   ├── composables/         # 可复用逻辑
│   └── router/              # 路由
├── deploy/                  # Nginx/systemd配置
└── README.md
```

---

## API 核心端点

| 端点 | 说明 |
|------|------|
| `GET /api/health` | 健康检查 |
| `POST /api/ai/scan` | AI图纸识别 |
| `POST /api/ai/customer-service` | AI客服(含图片+DB上下文) |
| `GET /api/bom/tree` | BOM完整树 |
| `POST /api/inventory/:id/transact` | 出入库 |
| `GET /api/qichacha/search` | 企业搜索 |
| `GET /api/qichacha/risk-scan` | 风险排查 |
| `GET /api/system/backup` | 数据库备份下载 |
| `GET /api/system/notifications` | 聚合通知 |

---

## 参考

本项目参考了 [Carbon ERP](https://github.com/crbnos/carbon) 的模块设计理念。

## 开源协议

MIT License

---

*Co-Authored-By: Claude <noreply@anthropic.com>*
