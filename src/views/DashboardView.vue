<template>
  <div class="dashboard-view">
    <Sidebar />
    <main class="dashboard-view__main">
      <TopBar
        title="经营看板"
        description="今日识图、待确认报价、客户增长和成交转化"
        eyebrow="老板视角"
      />

      <!-- Stat blocks -->
      <div class="dashboard-view__stats">
        <StatBlock label="今日识图" :value="stats.todayScans" :change="12" />
        <StatBlock label="待确认报价" :value="stats.pendingQuotes" />
        <StatBlock label="本周成交额" :value="stats.weeklyRevenue" currency :change="8" />
        <StatBlock label="转化率" :value="stats.conversionRate" suffix="%" :change="-2" />
      </div>

      <!-- New: Revenue & conversion mini cards -->
      <div v-if="stats.monthRevenue || stats.avgDealSize" class="dashboard-view__mini-stats">
        <div class="dashboard-view__mini-card" v-if="stats.monthRevenue">
          <span class="dashboard-view__mini-label">本月成交额</span>
          <span class="dashboard-view__mini-value">¥{{ formattedNumber(stats.monthRevenue) }}</span>
        </div>
        <div class="dashboard-view__mini-card" v-if="stats.avgDealSize">
          <span class="dashboard-view__mini-label">平均客单价</span>
          <span class="dashboard-view__mini-value">¥{{ formattedNumber(stats.avgDealSize) }}</span>
        </div>
        <div class="dashboard-view__mini-card" v-if="stats.customerCount !== undefined">
          <span class="dashboard-view__mini-label">总客户数</span>
          <span class="dashboard-view__mini-value">{{ stats.customerCount }}</span>
        </div>
        <div class="dashboard-view__mini-card" v-if="stats.activeQuotes !== undefined">
          <span class="dashboard-view__mini-label">进行中报价</span>
          <span class="dashboard-view__mini-value">{{ stats.activeQuotes }}</span>
        </div>
      </div>

      <div class="dashboard-view__grid">
        <!-- Chart: Quote trend -->
        <Card class="dashboard-view__chart-card">
          <h3 class="dashboard-view__card-title">报价趋势（近7日）</h3>
          <div class="dashboard-view__chart">
            <svg viewBox="0 0 600 200" class="dashboard-view__chart-svg">
              <polyline
                :points="chartPoints"
                fill="none"
                stroke="var(--brand)"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <polygon
                :points="chartArea"
                fill="url(#chartGradient)"
              />
              <defs>
                <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="var(--brand)" stop-opacity="0.15" />
                  <stop offset="100%" stop-color="var(--brand)" stop-opacity="0.02" />
                </linearGradient>
              </defs>
            </svg>
            <div class="dashboard-view__chart-labels">
              <span v-for="(label, i) in chartLabels" :key="i" class="dashboard-view__chart-label">{{ label }}</span>
            </div>
          </div>
        </Card>

        <!-- Ranking: Salesperson -->
        <Card class="dashboard-view__list-card">
          <h3 class="dashboard-view__card-title">业务员排行</h3>
          <div class="dashboard-view__ranking">
            <div v-for="(person, i) in rankings" :key="person.name" class="dashboard-view__rank-item">
              <span class="dashboard-view__rank-num">{{ i + 1 }}</span>
              <span class="dashboard-view__rank-name">{{ person.name }}</span>
              <span class="dashboard-view__rank-value">{{ person.quotes }} 单</span>
              <span class="dashboard-view__rank-rate">{{ person.rate }}%</span>
            </div>
          </div>
        </Card>
      </div>

      <!-- New: Customer growth chart -->
      <Card v-if="customerGrowth.length" class="dashboard-view__section-card">
        <h3 class="dashboard-view__card-title">客户增长趋势</h3>
        <div class="dashboard-view__growth-bars">
          <div v-for="(item, i) in customerGrowth" :key="i" class="dashboard-view__growth-bar-wrap">
            <div class="dashboard-view__growth-bar" :style="{ height: item.percent + '%' }"></div>
            <span class="dashboard-view__growth-label">{{ item.label }}</span>
            <span class="dashboard-view__growth-val">{{ item.count }}</span>
          </div>
        </div>
      </Card>

      <!-- Task list -->
      <Card class="dashboard-view__tasks">
        <h3 class="dashboard-view__card-title">待处理任务</h3>
        <div class="dashboard-view__task-list">
          <div v-for="task in tasks" :key="task.id" class="dashboard-view__task-item">
            <StatusDot :color="task.color" :show-label="false" />
            <span class="dashboard-view__task-title">{{ task.title }}</span>
            <Badge :variant="task.variant" size="sm">{{ task.count }}</Badge>
          </div>
        </div>
      </Card>

      <!-- New: Recent activity -->
      <Card v-if="recentActivity.length" class="dashboard-view__section-card">
        <h3 class="dashboard-view__card-title">最近动态</h3>
        <div class="dashboard-view__activity-list">
          <div v-for="act in recentActivity" :key="act.id" class="dashboard-view__activity-item">
            <div :class="['dashboard-view__activity-dot', 'dot--' + act.type]"></div>
            <span class="dashboard-view__activity-text">{{ act.text }}</span>
            <span class="dashboard-view__activity-time">{{ act.time }}</span>
          </div>
        </div>
      </Card>
    </main>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import Sidebar from '@/components/layout/Sidebar.vue';
import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import StatBlock from '@/components/data/StatBlock.vue';
import StatusDot from '@/components/base/StatusDot.vue';
import Badge from '@/components/base/Badge.vue';
import { api } from '@/api';

const stats = ref({
  todayScans: 0,
  pendingQuotes: 0,
  conversionRate: 0,
  weeklyRevenue: 45680,
  monthRevenue: 0,
  avgDealSize: 0,
  customerCount: 0,
  activeQuotes: 0,
});

const rankings = [
  { name: '张伟', quotes: 24, rate: 42 },
  { name: '李娜', quotes: 18, rate: 38 },
  { name: '王强', quotes: 15, rate: 33 },
  { name: '刘芳', quotes: 12, rate: 29 },
  { name: '陈明', quotes: 10, rate: 25 },
];

const tasks = [
  { id: 1, title: '待审核报价', count: 8, color: 'warn' as const, variant: 'warn' as const },
  { id: 2, title: '待确认客户', count: 12, color: 'info' as const, variant: 'info' as const },
  { id: 3, title: '异常识别需复核', count: 3, color: 'danger' as const, variant: 'danger' as const },
];

const customerGrowth = ref<{ label: string; count: number; percent: number }[]>([]);
const recentActivity = ref<{ id: number; type: string; text: string; time: string }[]>([]);

const chartData = [42000, 38500, 45680, 39800, 52100, 48700, 51200];
const chartLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];

const chartPoints = computed(() => {
  const max = Math.max(...chartData, 1);
  const width = 600; const height = 200; const padX = 30; const padY = 20;
  const stepX = (width - padX * 2) / (chartData.length - 1);
  return chartData.map((v, i) => `${padX + i * stepX},${height - padY - (v / max) * (height - padY * 2)}`).join(' ');
});

const chartArea = computed(() => {
  const max = Math.max(...chartData, 1);
  const width = 600; const height = 200; const padX = 30; const padY = 20;
  const stepX = (width - padX * 2) / (chartData.length - 1);
  const top = chartData.map((v, i) => `${padX + i * stepX},${height - padY - (v / max) * (height - padY * 2)}`).join(' ');
  return `${padX},${height - padY} ${top} ${width - padX},${height - padY}`;
});

function formattedNumber(v: number) {
  return new Intl.NumberFormat('zh-CN').format(v);
}

onMounted(async () => {
  const result = await api.get<any>('/dashboard/summary');
  if (result.data) {
    stats.value = {
      todayScans: result.data.today_scans || 0,
      pendingQuotes: result.data.pending_quotes || 0,
      conversionRate: Math.round((result.data.conversion_rate || 0) * 1000) / 10,
      weeklyRevenue: result.data.weekly_revenue || 45680,
      monthRevenue: result.data.month_revenue || 0,
      avgDealSize: result.data.avg_deal_size || 0,
      customerCount: result.data.customer_count || 0,
      activeQuotes: result.data.active_quotes || 0,
    };
    // Build customer growth from data
    if (result.data.customer_growth) {
      const maxCount = Math.max(...result.data.customer_growth.map((g: any) => g.count), 1);
      customerGrowth.value = result.data.customer_growth.map((g: any) => ({
        label: g.month || g.label,
        count: g.count,
        percent: Math.round((g.count / maxCount) * 100),
      }));
    }
    if (result.data.recent_activity) {
      recentActivity.value = result.data.recent_activity;
    }
  }
});
</script>

<style scoped>
.dashboard-view {
  display: block;
  min-height: 100vh;
}

.dashboard-view__main {
  padding: 24px 32px 120px;
}

/* Stats row */
.dashboard-view__stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

/* Mini stats row */
.dashboard-view__mini-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.dashboard-view__mini-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-card);
}

.dashboard-view__mini-label {
  font-size: var(--fz-sm);
  color: var(--text-muted);
}

.dashboard-view__mini-value {
  font-family: var(--font-mono);
  font-size: 24px;
  font-weight: var(--fw-bold);
  color: var(--text);
}

/* Main grid */
.dashboard-view__grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.dashboard-view__chart-card,
.dashboard-view__list-card {
  padding: 20px;
}

.dashboard-view__section-card {
  padding: 20px;
  margin-bottom: 20px;
}

.dashboard-view__tasks {
  padding: 20px;
}

.dashboard-view__card-title {
  font-size: var(--fz-h3);
  font-weight: var(--fw-semibold);
  margin: 0 0 16px;
  color: var(--text);
}

/* Chart */
.dashboard-view__chart { position: relative; }
.dashboard-view__chart-svg { width: 100%; height: 200px; display: block; }
.dashboard-view__chart-labels { display: flex; justify-content: space-between; padding: 4px 0; }
.dashboard-view__chart-label { font-size: var(--fz-xs); color: var(--text-muted); text-align: center; flex: 1; }

/* Ranking */
.dashboard-view__ranking { display: flex; flex-direction: column; gap: 8px; }
.dashboard-view__rank-item { display: flex; align-items: center; gap: 12px; padding: 10px; border-radius: var(--r-tag); background: var(--surface-sunken); }
.dashboard-view__rank-num { width: 24px; height: 24px; display: grid; place-items: center; background: var(--brand); color: white; border-radius: 50%; font-size: var(--fz-xs); font-weight: var(--fw-bold); }
.dashboard-view__rank-name { flex: 1; font-size: var(--fz-body); }
.dashboard-view__rank-value { font-family: var(--font-mono); font-weight: var(--fw-semibold); color: var(--text); }
.dashboard-view__rank-rate { font-size: var(--fz-sm); color: var(--text-muted); }

/* Tasks */
.dashboard-view__task-list { display: flex; flex-direction: column; gap: 10px; }
.dashboard-view__task-item { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: var(--r-input); background: var(--surface-sunken); }
.dashboard-view__task-title { flex: 1; font-size: var(--fz-body); }

/* Customer growth bars */
.dashboard-view__growth-bars { display: flex; align-items: flex-end; gap: 24px; height: 160px; padding: 0 8px; }
.dashboard-view__growth-bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; height: 100%; justify-content: flex-end; }
.dashboard-view__growth-bar { width: 100%; max-width: 48px; background: linear-gradient(180deg, var(--brand) 0%, var(--brand-light) 100%); border-radius: 8px 8px 0 0; min-height: 4px; transition: height 0.4s ease; }
.dashboard-view__growth-label { font-size: var(--fz-xs); color: var(--text-muted); }
.dashboard-view__growth-val { font-size: var(--fz-sm); font-weight: var(--fw-semibold); color: var(--text); }

/* Activity */
.dashboard-view__activity-list { display: flex; flex-direction: column; gap: 12px; }
.dashboard-view__activity-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--border); }
.dashboard-view__activity-item:last-child { border-bottom: none; }
.dashboard-view__activity-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.dot--quote { background: var(--brand); }
.dot--customer { background: var(--success); }
.dot--deal { background: var(--accent); }
.dot--system { background: var(--text-muted); }
.dashboard-view__activity-text { flex: 1; font-size: var(--fz-body); color: var(--text); }
.dashboard-view__activity-time { font-size: var(--fz-xs); color: var(--text-faint); }

@media (max-width: 768px) {
  .dashboard-view__main { padding: 16px 16px 120px; }
  .dashboard-view__stats { grid-template-columns: repeat(2, 1fr); }
  .dashboard-view__mini-stats { grid-template-columns: repeat(2, 1fr); }
  .dashboard-view__grid { grid-template-columns: 1fr; }
  .dashboard-view__growth-bars { height: 120px; gap: 12px; }
}
</style>
