<template>
  <div class="dashboard-view">
    <Sidebar />
    <main class="dashboard-view__main">
      <TopBar
        title="经营看板"
        description="关键经营指标、销售漏斗与客户分析"
        eyebrow="老板视角"
      />

      <!-- Row 1: Primary KPIs -->
      <div class="dashboard-view__stats">
        <div class="dashboard-view__stat-card" v-for="kpi in primaryKpis" :key="kpi.label">
          <div class="dashboard-view__stat-top">
            <span class="dashboard-view__stat-label">{{ kpi.label }}</span>
            <span v-if="kpi.change !== undefined" :class="['dashboard-view__stat-change', kpi.change >= 0 ? 'up' : 'down']">
              {{ kpi.change >= 0 ? '↑' : '↓' }} {{ Math.abs(kpi.change) }}%
            </span>
          </div>
          <div class="dashboard-view__stat-value-row">
            <span v-if="kpi.currency" class="dashboard-view__stat-currency">¥</span>
            <span class="dashboard-view__stat-value">{{ kpi.formatted }}</span>
            <span v-if="kpi.suffix" class="dashboard-view__stat-suffix">{{ kpi.suffix }}</span>
          </div>
          <div v-if="kpi.sub" class="dashboard-view__stat-sub">{{ kpi.sub }}</div>
        </div>
      </div>

      <!-- Row 2: Secondary KPIs -->
      <div class="dashboard-view__mini-stats">
        <div class="dashboard-view__mini-card" v-for="mk in miniKpis" :key="mk.label">
          <span class="dashboard-view__mini-label">{{ mk.label }}</span>
          <span class="dashboard-view__mini-value">{{ mk.value }}</span>
          <span v-if="mk.hint" class="dashboard-view__mini-hint">{{ mk.hint }}</span>
        </div>
      </div>

      <!-- Row 3: Chart + Funnel -->
      <div class="dashboard-view__grid">
        <!-- Quote trend chart -->
        <Card class="dashboard-view__card-block">
          <h3 class="dashboard-view__card-title">报价趋势（近7日）</h3>
          <div class="dashboard-view__chart">
            <svg viewBox="0 0 600 200" class="dashboard-view__chart-svg">
              <polyline :points="chartPoints" fill="none" stroke="var(--brand)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
              <polygon :points="chartArea" fill="url(#chartGradient)" />
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

        <!-- Sales funnel -->
        <Card class="dashboard-view__card-block">
          <h3 class="dashboard-view__card-title">销售漏斗</h3>
          <div class="dashboard-view__funnel">
            <div v-for="(step, i) in funnelSteps" :key="step.label" class="dashboard-view__funnel-step">
              <div class="dashboard-view__funnel-bar-wrap" :style="{ width: (100 - i * 12) + '%', margin: '0 auto' }">
                <div class="dashboard-view__funnel-bar" :style="{ width: '100%' }">
                  <span class="dashboard-view__funnel-label">{{ step.label }}</span>
                  <span class="dashboard-view__funnel-value">{{ step.value }}</span>
                </div>
              </div>
              <span v-if="i < funnelSteps.length - 1" class="dashboard-view__funnel-rate">
                {{ step.convRate }}% 转化
              </span>
            </div>
          </div>
        </Card>
      </div>

      <!-- Row 4: Material breakdown + Customer tier -->
      <div class="dashboard-view__grid">
        <Card class="dashboard-view__card-block">
          <h3 class="dashboard-view__card-title">材料类目分布</h3>
          <div class="dashboard-view__bars">
            <div v-for="item in materialBreakdown" :key="item.label" class="dashboard-view__bar-row">
              <span class="dashboard-view__bar-label">{{ item.label }}</span>
              <div class="dashboard-view__bar-track">
                <div class="dashboard-view__bar-fill" :style="{ width: item.percent + '%', background: item.color }"></div>
              </div>
              <span class="dashboard-view__bar-value">{{ item.value }} 单</span>
            </div>
          </div>
        </Card>

        <Card class="dashboard-view__card-block">
          <h3 class="dashboard-view__card-title">客户等级分布</h3>
          <div class="dashboard-view__tier-donut">
            <svg viewBox="0 0 160 160" class="dashboard-view__donut-svg">
              <circle v-for="(seg, i) in tierSegments" :key="seg.tier"
                cx="80" cy="80" :r="54"
                fill="none"
                :stroke="seg.color"
                stroke-width="28"
                :stroke-dasharray="seg.dashArray"
                :stroke-dashoffset="seg.dashOffset"
                transform="rotate(-90 80 80)"
                stroke-linecap="butt"
              />
              <text x="80" y="74" text-anchor="middle" class="dashboard-view__donut-center">{{ totalCustomers }}</text>
              <text x="80" y="94" text-anchor="middle" class="dashboard-view__donut-sub">总客户</text>
            </svg>
            <div class="dashboard-view__tier-legend">
              <div v-for="seg in tierSegments" :key="seg.tier" class="dashboard-view__tier-item">
                <span class="dashboard-view__tier-dot" :style="{ background: seg.color }"></span>
                <span>{{ seg.tier }}级客户</span>
                <span class="dashboard-view__tier-count">{{ seg.count }}</span>
              </div>
            </div>
          </div>
        </Card>
      </div>

      <!-- Row 5: Customer growth -->
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

      <!-- Row 6: Ranking + Tasks -->
      <div class="dashboard-view__grid">
        <Card class="dashboard-view__card-block">
          <h3 class="dashboard-view__card-title">业务员排行</h3>
          <div class="dashboard-view__ranking">
            <div v-for="(person, i) in rankings" :key="person.name" class="dashboard-view__rank-item">
              <span :class="['dashboard-view__rank-num', i < 3 ? 'dashboard-view__rank-num--top' : '']">{{ i + 1 }}</span>
              <span class="dashboard-view__rank-name">{{ person.name }}</span>
              <span class="dashboard-view__rank-value">{{ person.quotes }} 单</span>
              <span class="dashboard-view__rank-rate">{{ person.rate }}%</span>
            </div>
          </div>
        </Card>

        <Card class="dashboard-view__card-block">
          <h3 class="dashboard-view__card-title">待处理任务</h3>
          <div class="dashboard-view__task-list">
            <div v-for="task in tasks" :key="task.id" class="dashboard-view__task-item">
              <StatusDot :color="task.color" :show-label="false" />
              <span class="dashboard-view__task-title">{{ task.title }}</span>
              <Badge :variant="task.variant" size="sm">{{ task.count }}</Badge>
            </div>
          </div>
          <div v-if="recentActivity.length" style="margin-top: 24px;">
            <h3 class="dashboard-view__card-title">最近动态</h3>
            <div class="dashboard-view__activity-list">
              <div v-for="act in recentActivity" :key="act.id" class="dashboard-view__activity-item">
                <div :class="['dashboard-view__activity-dot', 'dot--' + act.type]"></div>
                <span class="dashboard-view__activity-text">{{ act.text }}</span>
                <span class="dashboard-view__activity-time">{{ act.time }}</span>
              </div>
            </div>
          </div>
        </Card>
      </div>
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
import StatusDot from '@/components/base/StatusDot.vue';
import Badge from '@/components/base/Badge.vue';
import { api } from '@/api';

/* ── Raw data ── */
const stats = ref({
  todayScans: 0, todayNewCustomers: 0, pendingQuotes: 0,
  weeklyRevenue: 0, monthWonDeals: 0, wonRate: 0,
  monthRevenue: 0, avgDealSize: 0, customerCount: 0,
  activeQuotes: 0, totalQuotes: 0, sentQuotes: 0, viewedQuotes: 0,
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

/* ── Computed primary KPIs ── */
const primaryKpis = computed(() => [
  {
    label: '今日识图',
    value: stats.value.todayScans,
    formatted: formattedNumber(stats.value.todayScans),
    change: 12,
    sub: '较昨日 +12%',
  },
  {
    label: '今日新增客户',
    value: stats.value.todayNewCustomers,
    formatted: formattedNumber(stats.value.todayNewCustomers),
    change: 8,
    sub: '较昨日 +8%',
  },
  {
    label: '待确认报价',
    value: stats.value.pendingQuotes,
    formatted: formattedNumber(stats.value.pendingQuotes),
    sub: '需及时跟进',
  },
  {
    label: '本周成交额',
    value: stats.value.weeklyRevenue,
    formatted: formattedNumber(stats.value.weeklyRevenue),
    currency: true,
    change: 8,
    sub: '较上周 +8%',
  },
  {
    label: '本月赢单数',
    value: stats.value.monthWonDeals,
    formatted: formattedNumber(stats.value.monthWonDeals),
    suffix: '单',
    change: 5,
    sub: '较上月 +5%',
  },
  {
    label: '赢单率',
    value: stats.value.wonRate,
    formatted: stats.value.wonRate.toFixed(1),
    suffix: '%',
    change: -2,
    sub: '目标 40%',
  },
]);

const miniKpis = computed(() => [
  { label: '本月成交额', value: `¥${formattedNumber(stats.value.monthRevenue)}`, hint: stats.value.monthRevenue > 0 ? '含税' : '' },
  { label: '平均客单价', value: `¥${formattedNumber(stats.value.avgDealSize)}`, hint: '' },
  { label: '总客户数', value: formattedNumber(stats.value.customerCount), hint: '' },
  { label: '进行中报价', value: formattedNumber(stats.value.activeQuotes), hint: '' },
  { label: '本月报价总数', value: formattedNumber(stats.value.totalQuotes), hint: '' },
  { label: '已发送报价', value: formattedNumber(stats.value.sentQuotes), hint: '' },
]);

/* ── Sales funnel ── */
const funnelSteps = computed(() => {
  const total = stats.value.totalQuotes || 1;
  const sent = stats.value.sentQuotes || 0;
  const viewed = stats.value.viewedQuotes || 0;
  const won = stats.value.monthWonDeals || 0;
  return [
    { label: '总报价', value: stats.value.totalQuotes, convRate: total > 0 ? 100 : 0 },
    { label: '已发送', value: sent, convRate: total > 0 ? Math.round((sent / total) * 100) : 0 },
    { label: '已查看', value: viewed, convRate: sent > 0 ? Math.round((viewed / sent) * 100) : 0 },
    { label: '已成交', value: won, convRate: viewed > 0 ? Math.round((won / viewed) * 100) : 0 },
    { label: '成交额', value: `¥${formattedNumber(stats.value.monthRevenue)}`, convRate: 0 },
  ];
});

/* ── Material breakdown ── */
const materialBreakdown = [
  { label: '镀锌板', value: 128, percent: 42, color: '#2563EB' },
  { label: '冷轧板', value: 76, percent: 25, color: '#0891B2' },
  { label: '铝板', value: 52, percent: 17, color: '#7C3AED' },
  { label: '不锈钢', value: 48, percent: 16, color: '#D97706' },
];

/* ── Customer tier donut ── */
const tierData = [
  { tier: 'A', count: 28, color: '#16A34A' },
  { tier: 'B', count: 85, color: '#2563EB' },
  { tier: 'C', count: 64, color: '#9CA3AF' },
];

const totalCustomers = computed(() => tierData.reduce((s, t) => s + t.count, 0));

const tierSegments = computed(() => {
  const total = totalCustomers.value || 1;
  const circ = 2 * Math.PI * 54; // r=54
  let offset = 0;
  return tierData.map(t => {
    const pct = t.count / total;
    const dashLen = circ * pct;
    const seg = {
      tier: t.tier,
      count: t.count,
      color: t.color,
      dashArray: `${dashLen} ${circ - dashLen}`,
      dashOffset: -offset,
    };
    offset += dashLen;
    return seg;
  });
});

/* ── Chart helpers ── */
const chartPoints = computed(() => {
  const max = Math.max(...chartData, 1);
  const w = 600, h = 200, px = 30, py = 20;
  const stepX = (w - px * 2) / (chartData.length - 1);
  return chartData.map((v, i) => `${px + i * stepX},${h - py - (v / max) * (h - py * 2)}`).join(' ');
});

const chartArea = computed(() => {
  const max = Math.max(...chartData, 1);
  const w = 600, h = 200, px = 30, py = 20;
  const stepX = (w - px * 2) / (chartData.length - 1);
  const top = chartData.map((v, i) => `${px + i * stepX},${h - py - (v / max) * (h - py * 2)}`).join(' ');
  return `${px},${h - py} ${top} ${w - px},${h - py}`;
});

function formattedNumber(v: number) {
  return new Intl.NumberFormat('zh-CN').format(Math.round(v));
}

/* ── Fetch ── */
onMounted(async () => {
  const result = await api.get<any>('/dashboard/summary');
  if (result.data) {
    const d = result.data;
    stats.value = {
      todayScans: d.today_scans || 0,
      todayNewCustomers: d.today_new_customers || 0,
      pendingQuotes: d.pending_quotes || 0,
      weeklyRevenue: d.weekly_revenue || 0,
      monthWonDeals: d.month_won_deals || 0,
      wonRate: Math.round((d.won_rate || 0) * 1000) / 10,
      monthRevenue: d.month_revenue || 0,
      avgDealSize: d.avg_deal_size || 0,
      customerCount: d.customer_count || 0,
      activeQuotes: d.active_quotes || 0,
      totalQuotes: d.total_quotes || 0,
      sentQuotes: d.sent_quotes || 0,
      viewedQuotes: d.viewed_quotes || 0,
    };
    if (d.customer_growth) {
      const maxCount = Math.max(...d.customer_growth.map((g: any) => g.count), 1);
      customerGrowth.value = d.customer_growth.map((g: any) => ({
        label: g.month || g.label,
        count: g.count,
        percent: Math.round((g.count / maxCount) * 100),
      }));
    }
    if (d.recent_activity) {
      recentActivity.value = d.recent_activity;
    }
  }
});
</script>

<style scoped>
.dashboard-view { display: block; min-height: 100vh; }
.dashboard-view__main { padding: 24px 32px 120px; }

/* ── Primary KPI cards ── */
.dashboard-view__stats {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 14px;
  margin-bottom: 18px;
}

.dashboard-view__stat-card {
  padding: 18px 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  transition: box-shadow 0.2s;
}
.dashboard-view__stat-card:hover { box-shadow: var(--sh-sm); }

.dashboard-view__stat-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.dashboard-view__stat-label {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  font-weight: var(--fw-medium);
}

.dashboard-view__stat-change {
  font-size: 11px;
  font-weight: var(--fw-semibold);
  padding: 2px 6px;
  border-radius: var(--r-pill);
}
.dashboard-view__stat-change.up { color: #16A34A; background: #F0FDF4; }
.dashboard-view__stat-change.down { color: #DC2626; background: #FEF2F2; }

.dashboard-view__stat-value-row {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.dashboard-view__stat-currency {
  font-size: 14px;
  color: var(--text-muted);
  font-weight: var(--fw-medium);
}

.dashboard-view__stat-value {
  font-family: var(--font-mono);
  font-size: 28px;
  font-weight: var(--fw-bold);
  font-feature-settings: "tnum" 1;
  color: var(--text);
}

.dashboard-view__stat-suffix {
  font-size: 16px;
  font-weight: var(--fw-semibold);
  color: var(--text-muted);
}

.dashboard-view__stat-sub {
  font-size: 11px;
  color: var(--text-faint);
  margin-top: 4px;
}

/* ── Secondary mini cards ── */
.dashboard-view__mini-stats {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.dashboard-view__mini-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 18px;
  background: var(--surface-sunken);
  border: 1px solid var(--border);
  border-radius: 12px;
}

.dashboard-view__mini-label {
  font-size: var(--fz-xs);
  color: var(--text-muted);
}

.dashboard-view__mini-value {
  font-family: var(--font-mono);
  font-size: 20px;
  font-weight: var(--fw-bold);
  color: var(--text);
}

.dashboard-view__mini-hint {
  font-size: 10px;
  color: var(--text-faint);
}

/* ── Main grid (2 columns) ── */
.dashboard-view__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
  margin-bottom: 18px;
}

.dashboard-view__card-block {
  padding: 20px;
}

.dashboard-view__section-card {
  padding: 20px;
  margin-bottom: 18px;
}

.dashboard-view__card-title {
  font-size: var(--fz-h3);
  font-weight: var(--fw-semibold);
  margin: 0 0 16px;
  color: var(--text);
}

/* ── Chart ── */
.dashboard-view__chart { position: relative; }
.dashboard-view__chart-svg { width: 100%; height: 200px; display: block; }
.dashboard-view__chart-labels {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}
.dashboard-view__chart-label {
  font-size: var(--fz-xs);
  color: var(--text-muted);
  text-align: center;
  flex: 1;
}

/* ── Sales funnel ── */
.dashboard-view__funnel {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
}

.dashboard-view__funnel-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.dashboard-view__funnel-bar-wrap {
  transition: width 0.5s ease;
}

.dashboard-view__funnel-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--brand) 0%, #3B82F6 100%);
  color: #fff;
  font-size: var(--fz-sm);
  font-weight: var(--fw-medium);
}

.dashboard-view__funnel-value {
  font-family: var(--font-mono);
  font-weight: var(--fw-bold);
}

.dashboard-view__funnel-rate {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 2px;
}

.dashboard-view__funnel-step:first-child .dashboard-view__funnel-bar {
  background: linear-gradient(135deg, #6B7280 0%, #9CA3AF 100%);
}
.dashboard-view__funnel-step:nth-child(3) .dashboard-view__funnel-bar {
  background: linear-gradient(135deg, #0891B2 0%, #06B6D4 100%);
}
.dashboard-view__funnel-step:nth-child(4) .dashboard-view__funnel-bar {
  background: linear-gradient(135deg, #16A34A 0%, #22C55E 100%);
}
.dashboard-view__funnel-step:last-child .dashboard-view__funnel-bar {
  background: linear-gradient(135deg, #D97706 0%, #F59E0B 100%);
}

/* ── Material bars ── */
.dashboard-view__bars {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.dashboard-view__bar-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dashboard-view__bar-label {
  width: 56px;
  font-size: var(--fz-sm);
  color: var(--text);
  flex-shrink: 0;
}

.dashboard-view__bar-track {
  flex: 1;
  height: 8px;
  background: var(--surface-sunken);
  border-radius: 4px;
  overflow: hidden;
}

.dashboard-view__bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.6s ease;
}

.dashboard-view__bar-value {
  font-family: var(--font-mono);
  font-size: var(--fz-sm);
  font-weight: var(--fw-semibold);
  color: var(--text-muted);
  width: 40px;
  text-align: right;
}

/* ── Customer tier donut ── */
.dashboard-view__tier-donut {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 8px 0;
}

.dashboard-view__donut-svg {
  width: 140px;
  height: 140px;
  flex-shrink: 0;
}

.dashboard-view__donut-center {
  font-size: 24px;
  font-weight: var(--fw-bold);
  fill: var(--text);
}

.dashboard-view__donut-sub {
  font-size: 11px;
  fill: var(--text-muted);
}

.dashboard-view__tier-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dashboard-view__tier-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--fz-sm);
}

.dashboard-view__tier-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.dashboard-view__tier-count {
  margin-left: auto;
  font-family: var(--font-mono);
  font-weight: var(--fw-semibold);
  color: var(--text);
}

/* ── Ranking ── */
.dashboard-view__ranking {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dashboard-view__rank-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--r-tag);
  background: var(--surface-sunken);
}

.dashboard-view__rank-num {
  width: 24px; height: 24px;
  display: grid; place-items: center;
  background: var(--border);
  color: var(--text-muted);
  border-radius: 50%;
  font-size: var(--fz-xs);
  font-weight: var(--fw-bold);
}

.dashboard-view__rank-num--top { background: var(--brand); color: #fff; }

.dashboard-view__rank-name { flex: 1; font-size: var(--fz-body); }
.dashboard-view__rank-value {
  font-family: var(--font-mono);
  font-weight: var(--fw-semibold);
  color: var(--text);
}
.dashboard-view__rank-rate {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  width: 34px;
  text-align: right;
}

/* ── Tasks ── */
.dashboard-view__task-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.dashboard-view__task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: var(--r-input);
  background: var(--surface-sunken);
}

.dashboard-view__task-title { flex: 1; font-size: var(--fz-body); }

/* ── Customer growth ── */
.dashboard-view__growth-bars {
  display: flex;
  align-items: flex-end;
  gap: 24px;
  height: 140px;
  padding: 0 8px;
}

.dashboard-view__growth-bar-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  height: 100%;
  justify-content: flex-end;
}

.dashboard-view__growth-bar {
  width: 100%;
  max-width: 44px;
  background: linear-gradient(180deg, var(--brand) 0%, var(--brand-light) 100%);
  border-radius: 6px 6px 0 0;
  min-height: 4px;
  transition: height 0.4s ease;
}

.dashboard-view__growth-label { font-size: var(--fz-xs); color: var(--text-muted); }
.dashboard-view__growth-val { font-size: var(--fz-sm); font-weight: var(--fw-semibold); color: var(--text); }

/* ── Activity ── */
.dashboard-view__activity-list { display: flex; flex-direction: column; gap: 10px; }
.dashboard-view__activity-item {
  display: flex; align-items: center; gap: 12px;
  padding: 8px 0; border-bottom: 1px solid var(--border);
}
.dashboard-view__activity-item:last-child { border-bottom: none; }
.dashboard-view__activity-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot--quote { background: var(--brand); }
.dot--customer { background: var(--success); }
.dot--deal { background: var(--accent); }
.dot--system { background: var(--text-muted); }
.dashboard-view__activity-text { flex: 1; font-size: var(--fz-sm); color: var(--text); }
.dashboard-view__activity-time { font-size: var(--fz-xs); color: var(--text-faint); }

/* ── Responsive ── */
@media (max-width: 1400px) {
  .dashboard-view__stats { grid-template-columns: repeat(3, 1fr); }
  .dashboard-view__mini-stats { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 768px) {
  .dashboard-view__main { padding: 16px 16px 120px; }
  .dashboard-view__stats { grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .dashboard-view__mini-stats { grid-template-columns: repeat(2, 1fr); }
  .dashboard-view__grid { grid-template-columns: 1fr; }
  .dashboard-view__stat-value { font-size: 22px; }
  .dashboard-view__stat-card { padding: 14px; }
  .dashboard-view__tier-donut { flex-direction: column; }
  .dashboard-view__growth-bars { height: 100px; gap: 12px; }
  .dashboard-view__funnel-bar { font-size: 12px; padding: 8px 12px; }
}
</style>
