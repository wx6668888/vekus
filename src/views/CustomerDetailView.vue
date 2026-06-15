<template>
  <div class="cust-detail">
    <Sidebar />
    <main class="cust-detail__main">
      <button class="cust-detail__back" @click="$router.back()"><ChevronLeft :size="20" /> 返回</button>
      <div v-if="loading">加载中...</div>
      <template v-else-if="customer">
        <Card class="cust-detail__card">
          <div class="cust-detail__header">
            <div class="cust-detail__avatar">{{ customer.name.charAt(0) }}</div>
            <div>
              <h1 class="cust-detail__name">{{ customer.name }}</h1>
              <p class="cust-detail__contact">{{ customer.contactName }} · {{ customer.phone }}</p>
              <div class="cust-detail__tags">
                <Badge :variant="tierVariant">{{ customer.tier }} 级客户</Badge>
                <span v-for="tag in customer.tags" :key="tag" class="vk-tag">{{ tag }}</span>
              </div>
            </div>
          </div>
        </Card>
        <Card class="cust-detail__card">
          <h3 class="cust-detail__section-title">基本信息</h3>
          <div class="cust-detail__info-grid">
            <div><span>客户名称</span><strong>{{ customer.name }}</strong></div>
            <div><span>联系人</span><strong>{{ customer.contactName }}</strong></div>
            <div><span>电话</span><strong>{{ customer.phone }}</strong></div>
            <div v-if="customer.email"><span>邮箱</span><strong>{{ customer.email }}</strong></div>
            <div v-if="customer.address"><span>地址</span><strong>{{ customer.address }}</strong></div>
            <div><span>客户等级</span><strong>{{ customer.tier }} 级</strong></div>
            <div><span>成交状态</span><strong>{{ customer.dealStatus === 'won' ? '已成交' : '未成交' }}</strong></div>
            <div><span>创建时间</span><strong>{{ customer.createdAt }}</strong></div>
          </div>
        </Card>
        <Card class="cust-detail__card">
          <h3 class="cust-detail__section-title">交易概况</h3>
          <div class="cust-detail__deal-stats">
            <div class="cust-detail__deal-stat">
              <span class="cust-detail__deal-value">¥{{ formattedNumber(customer.totalAmount || 0) }}</span>
              <span class="cust-detail__deal-label">总成交额</span>
            </div>
            <div class="cust-detail__deal-stat">
              <span class="cust-detail__deal-value">{{ customer.quoteCount || quotes.length }}</span>
              <span class="cust-detail__deal-label">报价次数</span>
            </div>
            <div class="cust-detail__deal-stat">
              <span class="cust-detail__deal-value">¥{{ formattedNumber(customer.avgDealSize || 0) }}</span>
              <span class="cust-detail__deal-label">平均客单价</span>
            </div>
            <div class="cust-detail__deal-stat">
              <span class="cust-detail__deal-value">{{ customer.dealStatus === 'won' ? customer.lastDealDate || '-' : '-' }}</span>
              <span class="cust-detail__deal-label">最近成交</span>
            </div>
          </div>
        </Card>
        <Card class="cust-detail__card">
          <h3 class="cust-detail__section-title">历史报价 ({{ quotes.length }})</h3>
          <div v-if="quotes.length === 0" class="cust-detail__empty">暂无报价记录</div>
          <div v-for="q in quotes" :key="q.id" class="cust-detail__quote" @click="$router.push('/quote/result/'+q.id)">
            <div class="cust-detail__quote-main">
              <span class="vk-font-mono">{{ q.quoteNo }}</span>
              <Badge :variant="q.status === 'won' ? 'success' : q.status === 'lost' ? 'danger' : q.status === 'sent' ? 'info' : 'default'" size="sm">{{ statusLabel(q.status) }}</Badge>
            </div>
            <div class="cust-detail__quote-info">
              <span>{{ q.material }} / {{ q.thickness }}mm / {{ q.quantity }}件</span>
              <PriceDisplay :value="q.totalPrice" size="sm" />
            </div>
          </div>
        </Card>
        <Card class="cust-detail__card">
          <h3 class="cust-detail__section-title">图纸管理 ({{ drawings.length }})</h3>
          <div v-if="drawings.length === 0" class="cust-detail__empty">暂无关联图纸</div>
          <div v-for="d in drawings" :key="d.id" class="cust-detail__drawing">
            <div class="cust-detail__drawing-icon">
              <FileImage :size="20" />
            </div>
            <div class="cust-detail__drawing-info">
              <div class="cust-detail__drawing-name">{{ d.fileName || '未命名图纸' }}</div>
              <div class="cust-detail__drawing-meta">{{ d.fileType || '未知类型' }} · {{ d.createdAt || '-' }}</div>
            </div>
            <Badge :variant="d.status === 'done' ? 'success' : d.status === 'processing' ? 'info' : 'default'" size="sm">
              {{ d.status === 'done' ? '已识别' : d.status === 'processing' ? '识别中' : '待识别' }}
            </Badge>
          </div>
        </Card>
      </template>
    </main>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { ChevronLeft, FileImage } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import Badge from '@/components/base/Badge.vue';
import PriceDisplay from '@/components/data/PriceDisplay.vue';
import { api } from '@/api';

const route = useRoute();
const customer = ref<any>(null);
const quotes = ref<any[]>([]);
const drawings = ref<any[]>([]);
const loading = ref(true);

const tierVariant = computed(() => {
  const v: Record<string, any> = { A: 'success', B: 'info', C: 'default' };
  return v[customer.value?.tier] || 'default';
});

function statusLabel(s: string) {
  const m: Record<string, string> = { draft: '草稿', sent: '已发送', won: '已成交', lost: '已失单' };
  return m[s] || s;
}

function formattedNumber(v: number) { return new Intl.NumberFormat('zh-CN').format(v); }

onMounted(async () => {
  const id = route.params.id as string;
  const r1 = await api.get<any>('/customers/' + id);
  if (r1.data) customer.value = r1.data;
  const r2 = await api.get<any[]>('/quotes');
  if (r2.data) quotes.value = r2.data.filter((q: any) => q.customerName === customer.value?.name);
  // Fetch drawings - get unique filenames from quotes
  if (r2.data) {
    const seen = new Set<string>();
    drawings.value = r2.data
      .filter((q: any) => q.customerName === customer.value?.name && q.recognized)
      .map((q: any) => ({
        id: q.id,
        fileName: `${q.quoteNo}.dwg`,
        fileType: 'DWG Drawing',
        status: q.recognized?.thickness ? 'done' : 'processing',
        createdAt: q.createdAt,
      }))
      .filter((d: any) => { const k = d.fileName; if (seen.has(k)) return false; seen.add(k); return true; });
  }
  loading.value = false;
});
</script>

<style scoped>
.cust-detail { display: grid; display: block; min-height: 100vh; }
.cust-detail__main { padding: 24px 32px 120px; max-width: 800px; margin: 0 auto; }
.cust-detail__back { display: flex; align-items: center; gap: 4px; padding: 8px 0; margin-bottom: 8px; border: none; background: none; color: var(--text-muted); cursor: pointer; }
.cust-detail__card { padding: 20px; margin-bottom: 16px; }
.cust-detail__header { display: flex; gap: 16px; }
.cust-detail__avatar { width: 56px; height: 56px; border-radius: 50%; background: linear-gradient(135deg, var(--brand), var(--accent)); color: white; display: grid; place-items: center; font-size: 24px; font-weight: var(--fw-bold); flex-shrink: 0; }
.cust-detail__name { font-size: var(--fz-h2); font-weight: var(--fw-bold); margin: 0 0 4px; }
.cust-detail__contact { font-size: var(--fz-sm); color: var(--text-muted); margin: 0 0 6px; }
.cust-detail__tags { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; }
.vk-tag { font-size: 11px; padding: 2px 8px; border-radius: var(--r-tag); background: var(--brand-light); color: var(--brand); }
.cust-detail__section-title { font-size: var(--fz-h3); font-weight: var(--fw-semibold); margin: 0 0 14px; }
.cust-detail__info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; }
.cust-detail__info-grid > div > span { display: block; font-size: var(--fz-sm); color: var(--text-muted); margin-bottom: 2px; }
.cust-detail__info-grid > div > strong { font-size: var(--fz-body); color: var(--text); }
.cust-detail__quote { padding: 14px; border-radius: var(--r-input); border: 1px solid var(--border); margin-bottom: 8px; cursor: pointer; transition: border-color var(--duration-fast); }
.cust-detail__quote:hover { border-color: var(--brand); }
.cust-detail__deal-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.cust-detail__deal-stat { text-align: center; padding: 12px; }
.cust-detail__deal-value { display: block; font-family: var(--font-mono); font-size: 24px; font-weight: var(--fw-bold); color: var(--brand); margin-bottom: 4px; }
.cust-detail__deal-label { font-size: var(--fz-sm); color: var(--text-muted); }
.cust-detail__quote-main { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.cust-detail__quote-info { display: flex; justify-content: space-between; font-size: var(--fz-sm); color: var(--text-muted); }
.cust-detail__empty { text-align: center; padding: 32px; color: var(--text-muted); }
.cust-detail__drawing { display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: var(--r-input); border: 1px solid var(--border); margin-bottom: 8px; }
.cust-detail__drawing-icon { width: 40px; height: 40px; border-radius: var(--r-tag); background: var(--brand-light); color: var(--brand); display: grid; place-items: center; flex-shrink: 0; }
.cust-detail__drawing-info { flex: 1; }
.cust-detail__drawing-name { font-size: var(--fz-body); font-weight: var(--fw-medium); color: var(--text); }
.cust-detail__drawing-meta { font-size: var(--fz-sm); color: var(--text-muted); margin-top: 2px; }
@media (max-width: 768px) { .cust-detail { grid-template-columns: 1fr; } .cust-detail__main { padding: 16px 16px 100px; } .cust-detail__info-grid { grid-template-columns: 1fr; } }
</style>
