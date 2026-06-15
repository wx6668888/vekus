<template>
  <div class="customers-view">
    <Sidebar />
    <main class="customers-view__main">
      <TopBar
        title="客户管理"
        description="维护客户资料、跟进状态、标签和负责人"
      >
        <template #actions>
          <Button variant="secondary" size="sm" @click="exportExcel" class="mr-2">
            <Download :size="14" class="mr-1" /> 导出
          </Button>
          <label class="bom-view__action" style="cursor:pointer;display:inline-flex;align-items:center;gap:4px;margin-right:8px">
            <Upload :size="14" /> 导入
            <input type="file" accept=".xlsx,.xls" style="display:none" @change="importExcel" />
          </label>
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
            <SelectMenu v-model="sortBy" :options="sortOptions" />
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
      <Card class="vk-dialog vk-dialog--wide">
        <h3 class="vk-dialog__title">新增客户</h3>

        <!-- Company search -->
        <div class="vk-dialog__search">
          <div class="vk-dialog__search-row">
            <Input
              v-model="companySearch"
              label="企业名称搜索"
              placeholder="输入企业名称关键词，自动匹配工商信息..."
              @update:model-value="onCompanySearch"
            />
            <span v-if="searching" class="vk-dialog__search-hint">搜索中...</span>
          </div>

          <!-- Search results -->
          <div v-if="companyResults.length > 0" class="vk-dialog__results">
            <div
              v-for="r in companyResults"
              :key="r.KeyNo"
              class="vk-dialog__result-item"
              @click="selectCompany(r)"
            >
              <div class="vk-dialog__result-main">
                <span class="vk-dialog__result-name">{{ r.Name }}</span>
                <span v-if="r.OperName" class="vk-dialog__result-person">{{ r.OperName }}</span>
              </div>
              <div class="vk-dialog__result-meta">
                <span v-if="r.Status" :class="['vk-dialog__result-status', r.Status === '存续' ? 'status-ok' : '']">{{ r.Status }}</span>
                <span v-if="r.StartDate">成立 {{ r.StartDate }}</span>
                <span v-if="r.CreditCode" class="vk-font-mono">统一社会信用代码: {{ r.CreditCode }}</span>
              </div>
              <div v-if="r.Address" class="vk-dialog__result-addr">{{ r.Address }}</div>
            </div>
          </div>
          <div v-if="companySearched && companyResults.length === 0 && !searching" class="vk-dialog__results-empty">
            未找到匹配企业
          </div>
        </div>

        <div class="vk-dialog__form">
          <div class="vk-dialog__form-row">
            <Input v-model="newCustomer.name" label="客户名称 *" placeholder="公司/工厂全称" />
            <Input v-model="newCustomer.contactName" label="联系人" placeholder="姓名" />
          </div>
          <div class="vk-dialog__form-row">
            <Input v-model="newCustomer.phone" label="电话" placeholder="手机号" />
            <Input v-model="newCustomer.email" label="邮箱" placeholder="选填" />
          </div>
          <Input v-model="newCustomer.address" label="地址" placeholder="公司地址" />
          <div class="vk-dialog__form-row">
            <div class="post-view__select">
              <label class="vk-input__label">客户等级</label>
              <SelectMenu v-model="newCustomer.tier" :options="tierOptions" />
            </div>
            <Input v-model="newCustomer.tagsStr" label="标签" placeholder="逗号分隔，如：钣金,长期合作" />
          </div>
        </div>
        <div class="vk-dialog__actions">
          <Button variant="ghost" @click="showAddDialog = false">取消</Button>
          <Button variant="primary" :loading="savingCustomer" @click="addCustomer">保存</Button>
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
import SelectMenu from '@/components/base/SelectMenu.vue';
import { api } from '@/api';
import { Download, Upload } from 'lucide-vue-next';
import * as XLSX from 'xlsx';

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
const savingCustomer = ref(false);
const newCustomer = ref({ name: '', contactName: '', phone: '', email: '', address: '', tier: 'B', tagsStr: '' });
const tierOptions = [
  { value: 'A', label: 'A级（VIP）' },
  { value: 'B', label: 'B级（普通）' },
  { value: 'C', label: 'C级（新客户）' },
];

// Company search
const companySearch = ref('');
const companyResults = ref<any[]>([]);
const searching = ref(false);
const companySearched = ref(false);
const selectedCompany = ref<any>(null);
let companySearchTimer: ReturnType<typeof setTimeout> | null = null;

function onCompanySearch() {
  if (companySearchTimer) clearTimeout(companySearchTimer);
  const kw = companySearch.value.trim();
  if (!kw) { companyResults.value = []; companySearched.value = false; return; }
  companySearchTimer = setTimeout(async () => {
    searching.value = true;
    companySearched.value = true;
    try {
      const res = await api.get<any>(`/qichacha/search?searchKey=${encodeURIComponent(kw)}`);
      if (res.data?.ok) companyResults.value = res.data.results;
      else companyResults.value = [];
    } catch { companyResults.value = []; }
    searching.value = false;
  }, 500);
}

function selectCompany(c: any) {
  newCustomer.value.name = c.Name || '';
  newCustomer.value.address = c.Address || '';
  selectedCompany.value = c;
  companyResults.value = [];
  companySearch.value = c.Name || '';
}

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

const sortOptions = [
  { value: 'default', label: '默认排序' },
  { value: 'amount-desc', label: '成交额 ↓' },
  { value: 'amount-asc', label: '成交额 ↑' },
  { value: 'time-desc', label: '最近添加' },
  { value: 'time-asc', label: '最早添加' },
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

async function importExcel(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0];
  if (!file) return;
  const data = await file.arrayBuffer();
  const wb = XLSX.read(data);
  const rows = XLSX.utils.sheet_to_json<any>(wb.Sheets[wb.SheetNames[0]]);
  let count = 0;
  for (const r of rows) {
    if (!r['客户名称'] && !r.name) continue;
    try {
      await api.post('/customers', {
        name: r['客户名称'] || r.name || '',
        contactName: r['联系人'] || r.contactName || '',
        phone: String(r['电话'] || r.phone || ''),
        email: r['邮箱'] || r.email || '',
        address: r['地址'] || r.address || '',
        tier: r['等级'] || r.tier || 'B',
        tags: (r['标签'] || r.tags || '').toString().split(/[,，]/).filter(Boolean),
      });
      count++;
    } catch { /* skip */ }
  }
  alert(`成功导入 ${count} 个客户`);
  fetchCustomers();
  (e.target as HTMLInputElement).value = '';
}

function exportExcel() {
  const data = customers.value.map(c => ({
    '客户名称': c.name, '联系人': c.contactName, '电话': c.phone,
    '等级': c.tier, '标签': (c.tags || []).join(','),
    '成交状态': c.dealStatus === 'won' ? '已成交' : '未成交',
  }));
  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, '客户列表');
  XLSX.writeFile(wb, '客户列表.xlsx');
}

async function addCustomer() {
  if (!newCustomer.value.name) return;
  savingCustomer.value = true;
  try {
    const tags = newCustomer.value.tagsStr
      ? newCustomer.value.tagsStr.split(',').map(t => t.trim()).filter(Boolean)
      : [];
    const result = await api.post<CustomerItem>('/customers', {
      name: newCustomer.value.name,
      contactName: newCustomer.value.contactName,
      phone: newCustomer.value.phone,
      email: newCustomer.value.email,
      address: newCustomer.value.address,
      tier: newCustomer.value.tier,
      tags,
      extInfo: selectedCompany.value || {},
    });
    if (result.data) {
      customers.value.push({ ...result.data, quotes: 0, tags });
    }
    showAddDialog.value = false;
    newCustomer.value = { name: '', contactName: '', phone: '', email: '', address: '', tier: 'B', tagsStr: '' };
    companySearch.value = '';
    companyResults.value = [];
    selectedCompany.value = null;
  } catch { alert('保存失败'); }
  finally { savingCustomer.value = false; }
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
.vk-dialog--wide { width: 560px; }

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
.vk-dialog__form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.vk-dialog__actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* Company search */
.vk-dialog__search {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border);
}

.vk-dialog__search-row { position: relative; }

.vk-dialog__search-hint {
  font-size: var(--fz-xs);
  color: var(--brand);
  position: absolute;
  right: 0;
  top: -2px;
}

.vk-dialog__results {
  max-height: 240px;
  overflow-y: auto;
  margin-top: 8px;
  border: 1px solid var(--border);
  border-radius: var(--r-input);
}

.vk-dialog__result-item {
  padding: 10px 14px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background 0.1s;
}
.vk-dialog__result-item:last-child { border-bottom: none; }
.vk-dialog__result-item:hover { background: var(--brand-light); }

.vk-dialog__result-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.vk-dialog__result-name {
  font-size: var(--fz-body);
  font-weight: var(--fw-semibold);
  color: var(--text);
}

.vk-dialog__result-person {
  font-size: var(--fz-sm);
  color: var(--text-muted);
}

.vk-dialog__result-meta {
  display: flex;
  gap: 12px;
  font-size: var(--fz-xs);
  color: var(--text-muted);
  margin-bottom: 2px;
}

.vk-dialog__result-status {
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--surface-sunken);
  font-weight: var(--fw-medium);
}
.vk-dialog__result-status.status-ok {
  background: var(--success-bg);
  color: var(--success);
}

.vk-dialog__result-addr {
  font-size: var(--fz-xs);
  color: var(--text-faint);
  margin-top: 2px;
}

.vk-dialog__results-empty {
  text-align: center;
  padding: 20px;
  font-size: var(--fz-sm);
  color: var(--text-muted);
}

.vk-input__label {
  font-size: var(--fz-sm);
  font-weight: var(--fw-medium);
  color: var(--text);
  margin-bottom: 6px;
  display: block;
}
.post-view__select { display: flex; flex-direction: column; gap: 6px; }

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
