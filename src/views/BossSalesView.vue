<template>
  <div class="boss-sales">
    <Sidebar />
    <main class="boss-sales__main">
      <button class="boss-sales__back" @click="$router.back()"><ChevronLeft :size="20" /> 返回</button>
      <h1 class="boss-sales__title">业务员管理</h1>
      <div v-if="loading">加载中...</div>
      <div v-else-if="salesList.length === 0" class="boss-sales__empty">暂无业务员</div>
      <Card v-for="s in salesList" :key="s.userId" class="boss-sales__card">
        <div class="boss-sales__header">
          <div class="boss-sales__avatar">{{ s.name.charAt(0) }}</div>
          <div class="boss-sales__info">
            <h3 class="boss-sales__name">{{ s.name }}</h3>
            <p class="boss-sales__phone">{{ s.phone }}</p>
          </div>
          <div class="boss-sales__stats">
            <div class="boss-sales__stat"><span class="boss-sales__stat-val">{{ s.totalQuotes }}</span><span class="boss-sales__stat-label">总报价</span></div>
            <div class="boss-sales__stat"><span class="boss-sales__stat-val">{{ s.wonQuotes }}</span><span class="boss-sales__stat-label">已成交</span></div>
            <div class="boss-sales__stat"><span class="boss-sales__stat-val">{{ s.totalQuotes > 0 ? Math.round(s.wonQuotes/s.totalQuotes*100) : 0 }}%</span><span class="boss-sales__stat-label">成交率</span></div>
          </div>
        </div>
      </Card>
    </main>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ChevronLeft } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import { api } from '@/api';

interface SalesItem { userId: string; name: string; phone: string; totalQuotes: number; wonQuotes: number }
const salesList = ref<SalesItem[]>([]);
const loading = ref(true);

onMounted(async () => {
  const r = await api.get<SalesItem[]>('/boss/sales-stats');
  if (r.data) salesList.value = r.data;
  loading.value = false;
});
</script>

<style scoped>
.boss-sales { display: grid; display: block; min-height: 100vh; }
.boss-sales__main { padding: 24px 32px 120px; max-width: 700px; }
.boss-sales__back { display: flex; align-items: center; gap: 4px; padding: 8px 0; margin-bottom: 8px; border: none; background: none; color: var(--text-muted); cursor: pointer; }
.boss-sales__title { font-size: var(--fz-h1); font-weight: var(--fw-bold); margin: 0 0 24px; }
.boss-sales__card { padding: 20px; margin-bottom: 12px; }
.boss-sales__header { display: flex; align-items: center; gap: 14px; }
.boss-sales__avatar { width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, var(--brand), var(--accent)); color: white; display: grid; place-items: center; font-size: 20px; font-weight: var(--fw-bold); flex-shrink: 0; }
.boss-sales__info { flex: 1; }
.boss-sales__name { font-size: var(--fz-body); font-weight: var(--fw-semibold); margin: 0; }
.boss-sales__phone { font-size: var(--fz-sm); color: var(--text-muted); margin: 2px 0 0; }
.boss-sales__stats { display: flex; gap: 20px; }
.boss-sales__stat { text-align: center; }
.boss-sales__stat-val { display: block; font-family: var(--font-mono); font-size: 18px; font-weight: var(--fw-bold); color: var(--brand); }
.boss-sales__stat-label { font-size: 11px; color: var(--text-muted); }
.boss-sales__empty { text-align: center; padding: 48px; color: var(--text-muted); }
@media (max-width: 768px) { .boss-sales { grid-template-columns: 1fr; } .boss-sales__main { padding: 16px 16px 100px; } .boss-sales__stats { gap: 12px; } }
</style>
