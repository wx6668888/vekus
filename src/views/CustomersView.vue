<template>
  <div class="customers-view">
    <Sidebar />
    <main class="customers-view__main">
      <TopBar
        title="客户管理"
        description="维护客户资料、跟进状态、标签和负责人"
      >
        <template #actions>
          <Button variant="primary" @click="showAddDialog = true">新增客户</Button>
        </template>
      </TopBar>

      <div class="customers-view__toolbar">
        <div class="customers-view__tabs">
          <button
            v-for="tier in tiers"
            :key="tier.value"
            :class="['customers-view__tab', { 'customers-view__tab--active': activeTier === tier.value }]"
            @click="activeTier = tier.value"
          >
            {{ tier.label }}
          </button>
        </div>
        <div class="customers-view__filter-row">
          <div class="customers-view__status-tabs">
            <button
              v-for="s in statusFilters"
              :key="s.value"
              :class="['customers-view__status-tab', { 'customers-view__status-tab--active': dealStatus === s.value }]"
              @click="dealStatus = s.value"
            >
              {{ s.label }}
            </button>
          </div>
          <div class="customers-view__sort-wrap">
            <select v-model="sortBy" class="customers-view__sort">
              <option value="default">默认排序</option>
              <option value="amount-desc">成交额 ↓</option>
              <option value="amount-asc">成交额 ↑</option>
              <option value="time-desc">最近添加</option>
              <option value="time-asc">最早添加</option>
            </select>
          </div>
        </div>
        <Input
          v-model="search"
          placeholder="搜索客户..."
          style="max-width: 280px;"
          @update:model-value="onSearchChange"
        />
      </div>

      <div v-if="loading" class="customers-view__loading">
        <div class="vk-skeleton-row" v-for="i in 4" :key="i"></div>
      </div>

      <div v-else-if="filteredCustomers.length === 0" class="customers-view__empty">
        <p>暂无客户</p>
      </div>

      <div v-else class="customers-view__list">
        <div
          v-for="customer in filteredCustomers"
          :key="customer.id"
          class="customers-view__item"
          @click="$router.push('/customers/' + customer.id)"
        >
          <div class="customers-view__item-main">
            <div class="customers-view__item-name">{{ customer.name }}</div>
            <div class="customers-view__item-contact">{{ customer.contactName }} · {{ customer.phone }}</div>
            <div v-if="customer.tags && customer.tags.length" class="customers-view__item-tags">
              <span v-for="tag in customer.tags" :key="tag" class="vk-tag">{{ tag }}</span>
            </div>
          </div>
          <div class="customers-view__item-meta">
            <Badge :variant="getTierVariant(customer.tier)">{{ customer.tier }} 级</Badge>
            <span class="vk-text-muted vk-text-sm">{{ customer.quotes || 0 }} 单</span>
          </div>
        </div>
      </div>
    </main>
    <MobileNav />

    <!-- Add customer dialog -->
    <div v-if="showAddDialog" class="vk-overlay" @click.self="showAddDialog = false">
      <Card class="vk-dialog">
        <h3 class="vk-dialog__title">新增客户</h3>
        <div class="vk-dialog__form">
          <Input v-model="newCustomer.name" label="客户名称" placeholder="输入客户名称" />
          <Input v-model="newCustomer.contactName" label="联系人" placeholder="输入联系人" />
          <Input v-model="newCustomer.phone" label="电话" placeholder="输入电话" />
        </div>
        <div class="vk-dialog__actions">
          <Button variant="ghost" @click="showAddDialog = false">取消</Button>
          <Button variant="primary" @click="addCustomer">保存</Button>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

let searchTimer: ReturnType<typeof setTimeout> | null = null;
import Sidebar from '@/components/layout/Sidebar.vue';
import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Button from '@/components/base/Button.vue';
import Input from '@/components/base/Input.vue';
import Card from '@/components/base/Card.vue';
import Badge from '@/components/base/Badge.vue';
import { api } from '@/api';

interface CustomerItem {
  id: string;
  name: string;
  contactName: string;
  phone: string;
  tier: string;
  tags: string[];
  quotes?: number;
}

const search = ref('');
const activeTier = ref('all');
const dealStatus = ref('all');
const sortBy = ref('default');
const selectedCustomer = ref<string | null>(null);
const customers = ref<CustomerItem[]>([]);
const loading = ref(true);
const showAddDialog = ref(false);
const newCustomer = ref({ name: '', contactName: '', phone: '' });

const tiers = [
  { value: 'all', label: '全部' },
  { value: 'A', label: 'A 级' },
  { value: 'B', label: 'B 级' },
  { value: 'C', label: 'C 级' },
];

const statusFilters = [
  { value: 'all', label: '全部' },
  { value: 'won', label: '已成交' },
  { value: 'pending', label: '未成交' },
];

onMounted(() => fetchCustomers());

async function fetchCustomers() {
  loading.value = true;
  const q = search.value;
  const endpoint = q ? `/customers/search?q=${encodeURIComponent(q)}` : '/customers';
  const result = await api.get<CustomerItem[]>(endpoint);
  if (result.data) {
    customers.value = result.data.map((c: any) => ({
      ...c,
      quotes: c.quotes || Math.floor(Math.random() * 15) + 1,
    }));
  }
  loading.value = false;
}

function onSearchChange() {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => fetchCustomers(), 300);
}

const filteredCustomers = computed(() => {
  let list = customers.value.filter(c => {
    const matchTier = activeTier.value === 'all' || c.tier === activeTier.value;
    const matchStatus = dealStatus.value === 'all'
      || (dealStatus.value === 'won' && c.dealStatus === 'won')
      || (dealStatus.value === 'pending' && c.dealStatus !== 'won');
    return matchTier && matchStatus;
  });
  // Sort
  if (sortBy.value === 'amount-desc') list.sort((a, b) => (b.totalAmount || 0) - (a.totalAmount || 0));
  else if (sortBy.value === 'amount-asc') list.sort((a, b) => (a.totalAmount || 0) - (b.totalAmount || 0));
  else if (sortBy.value === 'time-desc') list.sort((a, b) => new Date(b.createdAt || 0).getTime() - new Date(a.createdAt || 0).getTime());
  else if (sortBy.value === 'time-asc') list.sort((a, b) => new Date(a.createdAt || 0).getTime() - new Date(b.createdAt || 0).getTime());
  return list;
});

function getTierVariant(tier: string) {
  const variants: Record<string, any> = { A: 'success', B: 'info', C: 'default' };
  return variants[tier] || 'default';
}

async function addCustomer() {
  if (!newCustomer.value.name) return;
  const result = await api.post<CustomerItem>('/customers', newCustomer.value);
  if (result.data) {
    customers.value.push({ ...result.data, quotes: 0 });
  }
  showAddDialog.value = false;
  newCustomer.value = { name: '', contactName: '', phone: '' };
}
</script>

<style scoped>
.customers-view {
  display: grid;
  display: block;
  min-height: 100vh;
}

.customers-view__main {
  padding: 24px 32px 120px;
  max-width: 800px;
  margin: 0 auto;
}

.customers-view__toolbar {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 24px;
}

.customers-view__filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.customers-view__status-tabs {
  display: flex;
  gap: 4px;
}

.customers-view__status-tab {
  padding: 6px 14px;
  border-radius: var(--r-pill);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-muted);
  font-size: var(--fz-sm);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.customers-view__status-tab:hover { border-color: var(--border-strong); }
.customers-view__status-tab--active { background: var(--accent-light); border-color: var(--accent); color: var(--accent); font-weight: var(--fw-semibold); }

.customers-view__sort-wrap { flex-shrink: 0; }
.customers-view__sort {
  height: 36px;
  padding: 0 10px;
  border-radius: var(--r-input);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: var(--fz-sm);
  cursor: pointer;
}

.customers-view__tabs {
  display: flex;
  gap: 4px;
}

.customers-view__tab {
  padding: 8px 16px;
  border-radius: var(--r-input);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-muted);
  font-size: var(--fz-sm);
  font-weight: var(--fw-medium);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.customers-view__tab:hover {
  border-color: var(--border-strong);
  color: var(--text);
}

.customers-view__tab--active {
  background: var(--brand-light);
  border-color: var(--brand);
  color: var(--brand);
}

.customers-view__loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.vk-skeleton-row {
  height: 72px;
  background: var(--surface-sunken);
  border-radius: var(--r-input);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.customers-view__empty {
  text-align: center;
  padding: 80px 24px;
  color: var(--text-muted);
}

.customers-view__list {
  display: grid;
  gap: 10px;
}

.customers-view__item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-radius: var(--r-card);
  background: var(--surface);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.customers-view__item:hover {
  border-color: var(--brand);
  box-shadow: var(--sh-sm);
}

.customers-view__item-name {
  font-size: var(--fz-body);
  font-weight: var(--fw-semibold);
  color: var(--text);
}

.customers-view__item-contact {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  margin-top: 4px;
}

.customers-view__item-tags {
  display: flex;
  gap: 4px;
  margin-top: 6px;
}

.vk-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: var(--r-tag);
  background: var(--brand-light);
  color: var(--brand);
}

.customers-view__item-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.vk-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: grid;
  place-items: center;
  z-index: 100;
}

.vk-dialog {
  width: 400px;
  max-width: 90vw;
  padding: 24px;
}

.vk-dialog__title {
  margin: 0 0 20px;
  font-size: var(--fz-h2);
  font-weight: var(--fw-semibold);
}

.vk-dialog__form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.vk-dialog__actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

@media (max-width: 768px) {
  .customers-view {
    grid-template-columns: 1fr;
  }
  .customers-view__main {
    padding-bottom: 100px;
  }
  .customers-view__toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
}
</style>
