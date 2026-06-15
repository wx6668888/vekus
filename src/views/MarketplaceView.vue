<template>
  <div class="marketplace-view">
    <Sidebar />
    <main class="marketplace-view__main">
      <TopBar
        title="交易广场"
        description="钣金材料、余料、设备、加工服务"
      >
        <template #actions>
          <Button variant="primary" @click="$router.push('/marketplace/post')">
            <Plus :size="18" class="mr-2" />
            发布信息
          </Button>
        </template>
      </TopBar>

      <div class="marketplace-view__toolbar">
        <Input
          v-model="search"
          class="marketplace-view__search"
          placeholder="搜索材料、规格..."
          @update:model-value="onSearch"
        />
        <div class="marketplace-view__filters">
          <button
            v-for="t in typeFilters"
            :key="t.value"
            :class="['marketplace-view__filter', { 'marketplace-view__filter--active': activeType === t.value }]"
            @click="activeType = t.value; fetchListings()"
          >
            {{ t.label }}
          </button>
        </div>
      </div>

      <div class="marketplace-view__categories">
        <button
          v-for="cat in categories"
          :key="cat.value"
          :class="['marketplace-view__cat', { 'marketplace-view__cat--active': activeCategory === cat.value }]"
          @click="activeCategory = cat.value; fetchListings()"
        >
          {{ cat.label }}
        </button>
      </div>

      <div class="marketplace-view__extra-filters">
        <div class="marketplace-view__region-select-wrap">
          <MapPin :size="14" class="marketplace-view__region-icon" />
          <SelectMenu v-model="activeRegion" :options="regions" @update:model-value="fetchListings()" />
        </div>
        <div class="marketplace-view__sort">
          <span class="marketplace-view__sort-label">排序：</span>
          <SelectMenu v-model="sortBy" :options="sortOptions" @update:model-value="fetchListings()" />
        </div>
      </div>

      <div v-if="loading" class="marketplace-view__loading">
        <div class="vk-skeleton-row" v-for="i in 4" :key="i"></div>
      </div>

      <EmptyState
        v-else-if="listings.length === 0"
        title="暂无交易信息"
        description="还没有人发布交易信息，来发布第一条吧"
        icon="package"
      >
        <template #actions>
          <Button variant="primary" @click="$router.push('/marketplace/post')">发布信息</Button>
        </template>
      </EmptyState>

      <div v-else class="marketplace-view__grid">
        <ListingCard
          v-for="item in listings"
          :key="item.id"
          :title="item.title"
          :listing-type="item.listingType"
          :price="item.price"
          :unit="item.unit"
          :material="item.material"
          :thickness="item.thickness"
          :dimensions="item.dimensions"
          :surface="item.surface"
          :quantity="item.quantity"
          :location="item.location"
          :views-count="item.viewsCount"
          @click="$router.push(`/marketplace/${item.id}`)"
        />
      </div>
    </main>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Plus, MapPin } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Button from '@/components/base/Button.vue';
import Input from '@/components/base/Input.vue';
import EmptyState from '@/components/base/EmptyState.vue';
import SelectMenu from '@/components/base/SelectMenu.vue';
import ListingCard from '@/components/quote/ListingCard.vue';
import { listMarketplace, type Listing } from '@/api/marketplace';

const search = ref('');
const activeType = ref('all');
const activeCategory = ref('all');
const activeRegion = ref('all');
const sortBy = ref<'newest' | 'price_asc' | 'price_desc' | 'views'>('newest');
const loading = ref(true);
const listings = ref<Listing[]>([]);

const typeFilters = [
  { value: 'all', label: '全部' },
  { value: 'sell', label: '出售' },
  { value: 'buy', label: '求购' },
];

const categories = [
  { value: 'all', label: '全部' },
  { value: '板材', label: '板材' },
  { value: '型材', label: '型材' },
  { value: '余料', label: '余料' },
  { value: '设备', label: '设备' },
  { value: '加工服务', label: '加工服务' },
];

const regions = [
  { value: 'all', label: '全国' },
  { value: '北京', label: '北京' },
  { value: '上海', label: '上海' },
  { value: '天津', label: '天津' },
  { value: '重庆', label: '重庆' },
  { value: '广东-深圳', label: '广东-深圳' },
  { value: '广东-广州', label: '广东-广州' },
  { value: '广东-东莞', label: '广东-东莞' },
  { value: '广东-佛山', label: '广东-佛山' },
  { value: '广东-中山', label: '广东-中山' },
  { value: '广东-惠州', label: '广东-惠州' },
  { value: '广东-其他', label: '广东-其他' },
  { value: '浙江-宁波', label: '浙江-宁波' },
  { value: '浙江-杭州', label: '浙江-杭州' },
  { value: '浙江-温州', label: '浙江-温州' },
  { value: '浙江-台州', label: '浙江-台州' },
  { value: '浙江-其他', label: '浙江-其他' },
  { value: '江苏-苏州', label: '江苏-苏州' },
  { value: '江苏-无锡', label: '江苏-无锡' },
  { value: '江苏-常州', label: '江苏-常州' },
  { value: '江苏-南京', label: '江苏-南京' },
  { value: '江苏-其他', label: '江苏-其他' },
  { value: '河北', label: '河北' },
  { value: '山东', label: '山东' },
  { value: '福建', label: '福建' },
  { value: '湖北', label: '湖北' },
  { value: '湖南', label: '湖南' },
  { value: '四川', label: '四川' },
  { value: '河南', label: '河南' },
  { value: '安徽', label: '安徽' },
  { value: '辽宁', label: '辽宁' },
  { value: '其他', label: '其他地区' },
];

const sortOptions = [
  { value: 'newest' as const, label: '最新发布' },
  { value: 'price_asc' as const, label: '价格从低到高' },
  { value: 'price_desc' as const, label: '价格从高到低' },
  { value: 'views' as const, label: '最多浏览' },
];

let searchTimer: ReturnType<typeof setTimeout> | null = null;

onMounted(() => fetchListings());

async function fetchListings() {
  loading.value = true;
  const params: Record<string, string> = {};
  if (activeType.value !== 'all') params.listingType = activeType.value;
  if (activeCategory.value !== 'all') params.category = activeCategory.value;
  if (activeRegion.value !== 'all') params.keyword = activeRegion.value;
  if (search.value) params.keyword = search.value;
  let result = await listMarketplace(params);
  // Client-side sort
  if (sortBy.value === 'price_asc') result.sort((a, b) => a.price - b.price);
  else if (sortBy.value === 'price_desc') result.sort((a, b) => b.price - a.price);
  else if (sortBy.value === 'views') result.sort((a, b) => b.viewsCount - a.viewsCount);
  // newest is default (API returns by id desc)
  listings.value = result;
  loading.value = false;
}

function onSearch() {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => fetchListings(), 300);
}
</script>

<style scoped>
.marketplace-view {
  display: grid;
  display: block;
  min-height: 100vh;
}

.marketplace-view__main {
  padding: 24px 32px 120px;
}

.marketplace-view__toolbar {
  display: flex;
  gap: 16px;
  align-items: center;
  margin-bottom: 16px;
}

.marketplace-view__search {
  flex: 1;
  max-width: 420px;
}
.marketplace-view__search :deep(.vk-input__field) {
  height: 44px;
  border-radius: 22px;
  padding: 0 20px;
  background: var(--surface-sunken);
  border: 1px solid transparent;
  font-size: var(--fz-body);
}

.marketplace-view__filters {
  display: flex;
  gap: 4px;
}

.marketplace-view__filter {
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

.marketplace-view__filter:hover {
  border-color: var(--border-strong);
  color: var(--text);
}

.marketplace-view__filter--active {
  background: var(--brand-light);
  border-color: var(--brand);
  color: var(--brand);
}

.marketplace-view__categories {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.marketplace-view__cat {
  padding: 6px 14px;
  border-radius: var(--r-pill);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-muted);
  font-size: var(--fz-sm);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.marketplace-view__cat:hover {
  border-color: var(--brand);
  color: var(--brand);
}

.marketplace-view__cat--active {
  background: var(--brand);
  border-color: var(--brand);
  color: white;
}

.marketplace-view__extra-filters {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.marketplace-view__region-select-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: var(--r-input);
  border: 1px solid var(--border);
  background: var(--surface);
  transition: border-color var(--duration-fast);
}

.marketplace-view__region-select-wrap:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px var(--brand-light);
}

.marketplace-view__region-icon {
  color: var(--text-muted);
  flex-shrink: 0;
}

.marketplace-view__region-select {
  flex: 1;
  border: none;
  background: transparent;
  color: var(--text);
  font-size: var(--fz-body);
  font-family: var(--font-sans);
  cursor: pointer;
  outline: none;
  min-width: 120px;
}

.marketplace-view__sort {
  display: flex;
  align-items: center;
  gap: 6px;
}

.marketplace-view__sort-label {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  white-space: nowrap;
}

.marketplace-view__sort-select {
  padding: 6px 10px;
  border-radius: var(--r-tag);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: var(--fz-sm);
  cursor: pointer;
}

.marketplace-view__loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.vk-skeleton-row {
  height: 140px;
  background: var(--surface-sunken);
  border-radius: var(--r-card);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.marketplace-view__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.mr-2 { margin-right: 8px; }

@media (max-width: 768px) {
  .marketplace-view {
    grid-template-columns: 1fr;
  }
  .marketplace-view__main {
    padding: 16px 16px 100px;
  }
  .marketplace-view__toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  .marketplace-view__grid {
    grid-template-columns: 1fr;
  }
  .marketplace-view__filters {
    overflow-x: auto;
    flex-wrap: nowrap;
  }
  .marketplace-view__filter {
    flex-shrink: 0;
  }
  .marketplace-view__categories {
    flex-wrap: nowrap;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
  }
  .marketplace-view__cat {
    flex-shrink: 0;
  }
}
</style>
