<template>
  <div class="history-view">
    <Sidebar />
    <main class="history-view__main">
      <TopBar
        title="历史报价"
        description="查询、复用、导出历史报价记录"
      >
        <template #actions>
          <Button variant="primary" @click="$router.push('/quote')">
            <Plus :size="18" class="mr-2" />
            新建报价
          </Button>
        </template>
      </TopBar>

      <div class="history-view__toolbar">
        <Input
          v-model="search"
          class="history-view__search"
          placeholder="搜索报价单号、客户、材料..."
          @update:model-value="onSearchChange"
        />
        <div class="history-view__filters">
          <button
            v-for="s in statuses"
            :key="s.value"
            :class="['history-view__filter', { 'history-view__filter--active': activeStatus === s.value }]"
            @click="activeStatus = s.value; fetchQuotes()"
          >
            {{ s.label }}
          </button>
        </div>
      </div>

      <div v-if="loading" class="history-view__loading">
        <div class="vk-skeleton-row" v-for="i in 4" :key="i"></div>
      </div>

      <div v-else-if="quotes.length === 0" class="history-view__empty">
        <p>暂无报价记录</p>
        <Button variant="primary" @click="$router.push('/quote')">新建第一单</Button>
      </div>

      <Card v-else class="history-view__table">
        <table class="vk-table">
          <thead>
            <tr>
              <th>报价单号</th>
              <th>客户</th>
              <th>材料</th>
              <th>数量</th>
              <th>金额</th>
              <th>状态</th>
              <th>时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="quote in quotes" :key="quote.id">
              <td class="vk-font-mono">{{ quote.quoteNo }}</td>
              <td>{{ quote.customerName }}</td>
              <td>{{ quote.material }}</td>
              <td>{{ quote.quantity }}</td>
              <td>
                <PriceDisplay :value="quote.totalPrice" size="sm" />
              </td>
              <td>
                <Badge :variant="getStatusVariant(quote.status)">
                  {{ getStatusLabel(quote.status) }}
                </Badge>
              </td>
              <td class="vk-text-muted">{{ formatDate(quote.createdAt) }}</td>
              <td>
                <div class="history-view__actions">
                  <button class="history-view__action" @click="$router.push(`/quote/${quote.id}`)">
                    <Copy :size="14" />
                  </button>
                  <button class="history-view__action" @click="shareQuote(quote)">
                    <Share :size="14" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </Card>
    </main>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Plus, Copy, Share } from 'lucide-vue-next';

let searchTimer: ReturnType<typeof setTimeout> | null = null;
import Sidebar from '@/components/layout/Sidebar.vue';
import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import Input from '@/components/base/Input.vue';
import Button from '@/components/base/Button.vue';
import PriceDisplay from '@/components/data/PriceDisplay.vue';
import Badge from '@/components/base/Badge.vue';
import { api } from '@/api';

interface QuoteItem {
  id: string;
  quoteNo: string;
  customerName: string;
  material: string;
  thickness: number;
  quantity: number;
  surface: string;
  totalPrice: number;
  status: string;
  createdAt: string;
}

const search = ref('');
const activeStatus = ref('all');
const quotes = ref<QuoteItem[]>([]);
const loading = ref(true);

const statuses = [
  { value: 'all', label: '全部' },
  { value: 'draft', label: '草稿' },
  { value: 'sent', label: '已发送' },
  { value: 'won', label: '已成交' },
  { value: 'lost', label: '已失单' },
];

onMounted(() => fetchQuotes());

async function fetchQuotes() {
  loading.value = true;
  const params = new URLSearchParams();
  if (activeStatus.value !== 'all') params.set('status', activeStatus.value);
  if (search.value) params.set('customer', search.value);
  const result = await api.get<QuoteItem[]>(`/quotes?${params}`);
  if (result.data) {
    quotes.value = result.data;
  }
  loading.value = false;
}

function onSearchChange() {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => fetchQuotes(), 300);
}

function getStatusVariant(status: string) {
  const variants: Record<string, any> = { draft: 'default', sent: 'info', won: 'success', lost: 'danger' };
  return variants[status] || 'default';
}

function getStatusLabel(status: string) {
  const labels: Record<string, string> = { draft: '草稿', sent: '已发送', won: '已成交', lost: '已失单' };
  return labels[status] || status;
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
}

function shareQuote(quote: QuoteItem) {
  const url = `${window.location.origin}/share/${quote.id}`;
  navigator.clipboard.writeText(url).then(() => {
    alert('分享链接已复制');
  });
}
</script>

<style scoped>
.history-view {
  display: grid;
  display: block;
  min-height: 100vh;
}

.history-view__main {
  padding: 24px 32px;
}

.history-view__toolbar {
  display: flex;
  gap: 16px;
  align-items: center;
}

.history-view__search {
  flex: 1;
  max-width: 420px;
}
.history-view__search :deep(.vk-input__field) {
  height: 44px;
  border-radius: 22px;
  padding: 0 20px;
  background: var(--surface-sunken);
  border: 1px solid transparent;
  font-size: var(--fz-body);
}

.history-view__filters {
  display: flex;
  gap: 4px;
}

.history-view__filter {
  padding: 8px 14px;
  border-radius: var(--r-input);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-muted);
  font-size: var(--fz-sm);
  font-weight: var(--fw-medium);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.history-view__filter:hover {
  border-color: var(--border-strong);
  color: var(--text);
}

.history-view__filter--active {
  background: var(--brand-light);
  border-color: var(--brand);
  color: var(--brand);
}

.history-view__loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.vk-skeleton-row {
  height: 56px;
  background: var(--surface-sunken);
  border-radius: var(--r-input);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.history-view__empty {
  text-align: center;
  padding: 80px 24px;
  color: var(--text-muted);
}

.history-view__table {
  overflow-x: auto;
}

.vk-table {
  width: 100%;
  border-collapse: collapse;
}

.vk-table th {
  text-align: left;
  padding: 12px 16px;
  font-size: var(--fz-sm);
  font-weight: var(--fw-semibold);
  color: var(--text-muted);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}

.vk-table td {
  padding: 14px 16px;
  font-size: var(--fz-body);
  border-bottom: 1px solid var(--border);
  color: var(--text);
}

.vk-table tr:last-child td {
  border-bottom: none;
}

.vk-table tr:hover td {
  background: var(--surface-sunken);
}

.history-view__actions {
  display: flex;
  gap: 8px;
}

.history-view__action {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: var(--r-tag);
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.history-view__action:hover {
  border-color: var(--brand);
  color: var(--brand);
}

.mr-2 { margin-right: 8px; }

@media (max-width: 768px) {
  .history-view {
    grid-template-columns: 1fr;
    overflow-x: hidden;
  }
  .history-view__main {
    padding: 16px 16px 100px;
    overflow-x: hidden;
    max-width: 100vw;
  }
  .history-view__toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  .history-view__filters {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
  .history-view__filter {
    white-space: nowrap;
    flex-shrink: 0;
    font-size: 11px;
    padding: 6px 10px;
  }
  .history-view__table {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
    border-radius: 0;
  }
  .vk-table {
    min-width: 600px;
    table-layout: auto;
  }
  .vk-table th,
  .vk-table td {
    white-space: nowrap;
  }
}
</style>
