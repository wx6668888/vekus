# Vekus 智能报价平台 · 精工蓝图版

基于 Vue 3 + Vite + TypeScript 构建的钣金 AI 报价平台前端。

## 设计风格

- **精工蓝图(Precision Blueprint)**: 浅灰底 + 深蓝 Hero + 工程橙强调 + 等宽数字
- 核心特征:工程网格底纹、等宽数字字体、高对比度数据展示、卡片化布局

## 快速开始

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 类型检查
npm run type-check
```

默认在 `http://localhost:3001` 启动。

## 项目结构

```
src/
├── api/              # API 接口层
├── components/       # 组件库
│   ├── base/        # 基础组件(Button/Input/Card/Badge/StatusDot/Toast)
│   ├── data/        # 数据组件(PriceDisplay/StatBlock)
│   ├── layout/      # 布局组件(Sidebar/TopBar/MobileNav)
│   └── quote/       # 报价业务组件(FileDropzone/RecognizedFieldList/ResultPanel)
├── services/         # 业务服务(报价计算引擎)
├── stores/           # 状态管理(Pinia)
├── styles/           # 样式系统(tokens/reset/globals)
├── views/            # 页面组件
└── router/           # 路由配置
```

## 核心页面

| 路由 | 页面 | 说明 |
|---|---|---|
| `/login` | 登录页 | 手机号/微信扫码登录 |
| `/quote` | 报价工作台 | 核心功能,支持上传识图、参数修正、实时计算 |
| `/quote/:id` | 编辑报价 | 编辑已有报价 |
| `/quote/result/:id` | 报价结果 | 可分享的客户报价页 |
| `/history` | 历史报价 | 查询、筛选、复用历史记录 |
| `/customers` | 客户管理 | 客户列表与详情 |
| `/settings` | 系统设置 | 参数字典维护 |
| `/dashboard` | 经营看板 | 老板视角的数据概览 |
| `/me` | 个人中心 | 用户信息与快捷入口 |
| `/share/:id` | 分享页 | 客户查看报价的入口(无需登录) |

## 设计 Token

所有设计变量定义在 `src/styles/tokens.css`:

- `--bg`: 页面背景 `#F7F8FA`
- `--surface`: 卡片背景 `#FFFFFF`
- `--surface-blueprint`: 蓝图 Hero `#0B1C3A`
- `--brand`: 品牌主色 `#1E40AF`
- `--accent`: 强调色 `#F97316`
- `--text`: 主文本 `#0F172A`
- `--font-mono`: 等宽数字字体 `JetBrains Mono`

## 组件使用示例

```vue
<template>
  <Button variant="primary" size="lg">发送报价</Button>
  <PriceDisplay :value="12480" size="display" color="accent" />
  <Card class="my-card">卡片内容</Card>
  <Badge variant="success">已成交</Badge>
</template>

<script setup lang="ts">
import { Button, PriceDisplay, Card, Badge } from '@/components';
</script>
```

## 报价计算引擎

```ts
import { calculateQuote } from '@/services';

const result = calculateQuote({
  basics: { material: '镀锌板', thickness: 1.5, quantity: 500, surface: '喷粉', ... },
  recognized: { thickness: 1.5, expandLength: 420, ... },
  manualOverrides: {},
  coefficients: { tax: 1.06, discount: 0.95, ... },
});
// result: { breakdown: {...}, totalPrice: 12480, unitPrice: 24.96, ... }
```

## 开发说明

- 使用 Vue 3 Composition API + `<script setup>`
- 状态管理使用 Pinia
- 路由使用 Vue Router
- 样式使用原生 CSS + CSS 变量
- 字体使用 Inter(中文) + JetBrains Mono(数字)

## 待接入后端

当前使用 mock 数据和纯前端计算,待接入的后端接口:
- `POST /api/ai/scan` - 图纸识别
- `POST /api/quotes` - 保存报价
- `GET /api/quotes/:id` - 获取报价
- `GET /api/quotes` - 报价列表
- `GET /api/customers/search` - 客户搜索

## 与旧版对比

- 旧版: 单页 HTML + 原生 JS,深色沉浸风格
- 新版: Vue 3 工程化,精工蓝图风格,组件化,类型安全

## 许可

内部项目
