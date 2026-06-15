<template>
  <div class="vk-customer-picker">
    <label class="vk-input__label">客户名称</label>

    <!-- Dropdown selector -->
    <div class="vk-customer-picker__input-wrap" @click="toggleDropdown" ref="pickerRef">
      <input
        v-model="searchText"
        class="vk-input__field vk-customer-picker__input"
        :placeholder="selectedCustomer ? selectedCustomer.name : '搜索或选择客户...'"
        @focus="showDropdown = true"
        @input="onSearch"
      />
      <ChevronDown :size="16" class="vk-customer-picker__arrow" :class="{ 'vk-customer-picker__arrow--open': showDropdown }" />
    </div>

    <!-- Dropdown list -->
    <div v-if="showDropdown" class="vk-customer-picker__dropdown">
      <div v-if="loading" class="vk-customer-picker__option vk-customer-picker__option--loading">搜索中...</div>
      <div
        v-for="cust in filteredCustomers"
        :key="cust.id"
        class="vk-customer-picker__option"
        @click="selectCustomer(cust)"
      >
        <div class="vk-customer-picker__option-name">{{ cust.name }}</div>
        <div class="vk-customer-picker__option-info">{{ cust.contactName }} · {{ cust.phone }}</div>
        <Badge :variant="cust.tier === 'A' ? 'success' : cust.tier === 'B' ? 'info' : 'default'" size="sm">{{ cust.tier }}级</Badge>
      </div>
      <div
        v-if="searchText && !filteredCustomers.length"
        class="vk-customer-picker__option vk-customer-picker__option--new"
        @click="startNewCustomer"
      >
        <Plus :size="16" />
        <span>新增客户 "{{ searchText }}"</span>
      </div>
    </div>

    <!-- New customer form -->
    <div v-if="showNewForm" class="vk-customer-picker__new-form">
      <div class="vk-customer-picker__form-row">
        <Input v-model="newCustomer.name" label="客户名称 *" placeholder="公司/工厂名称" />
        <Input v-model="newCustomer.contactName" label="联系人" placeholder="联系人姓名" />
      </div>
      <div class="vk-customer-picker__form-row">
        <Input v-model="newCustomer.phone" label="电话" placeholder="联系电话" />
        <div class="quote-form__select">
          <label class="vk-input__label">客户等级</label>
          <select v-model="newCustomer.tier" class="vk-input__field">
            <option value="B">B级（普通）</option>
            <option value="A">A级（VIP）</option>
            <option value="C">C级（新客户）</option>
          </select>
        </div>
      </div>
      <Input v-model="newCustomer.address" label="地址" placeholder="选填" />
      <div class="vk-customer-picker__form-actions">
        <Button variant="ghost" size="sm" @click="showNewForm = false">取消</Button>
        <Button variant="primary" size="sm" :loading="creating" @click="createCustomer">保存并选择</Button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { ChevronDown, Plus } from 'lucide-vue-next';
import Input from '../base/Input.vue';
import Button from '../base/Button.vue';
import Badge from '../base/Badge.vue';
import { api } from '@/api';
import { createCustomer } from '@/api/customer';

interface CustomerItem {
  id: string; name: string; contactName: string; phone: string; tier: string; address?: string;
}

const emit = defineEmits<{ 'update:customerName': [name: string]; 'update:customerId': [id: string] }>();

const searchText = ref('');
const showDropdown = ref(false);
const showNewForm = ref(false);
const loading = ref(false);
const creating = ref(false);
const selectedCustomer = ref<CustomerItem | null>(null);
const customers = ref<CustomerItem[]>([]);
const pickerRef = ref<HTMLElement | null>(null);
const newCustomer = ref({ name: '', contactName: '', phone: '', tier: 'B', address: '' });

let searchTimer: ReturnType<typeof setTimeout> | null = null;

onMounted(async () => {
  const r = await api.get<CustomerItem[]>('/customers');
  if (r.data) customers.value = r.data;
});

function onSearch() {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(async () => {
    if (!searchText.value) { filteredCustomers.value = customers.value; return; }
    loading.value = true;
    const r = await api.get<CustomerItem[]>(`/customers/search?q=${encodeURIComponent(searchText.value)}`);
    customers.value = r.data || [];
    loading.value = false;
  }, 200);
}

const filteredCustomers = computed(() => {
  if (!searchText.value) return customers.value.slice(0, 8);
  const q = searchText.value.toLowerCase();
  return customers.value.filter(c => c.name.toLowerCase().includes(q) || c.contactName?.toLowerCase().includes(q)).slice(0, 8);
});

function toggleDropdown() { showDropdown.value = !showDropdown.value; if (showDropdown.value) showNewForm.value = false; }

function selectCustomer(cust: CustomerItem) {
  selectedCustomer.value = cust;
  searchText.value = cust.name;
  showDropdown.value = false;
  emit('update:customerName', cust.name);
  emit('update:customerId', cust.id);
}

function startNewCustomer() {
  showDropdown.value = false;
  showNewForm.value = true;
  newCustomer.value.name = searchText.value;
}

async function createCustomer() {
  if (!newCustomer.value.name) return;
  creating.value = true;
  try {
    const r = await createCustomer({
      name: newCustomer.value.name,
      contactName: newCustomer.value.contactName,
      phone: newCustomer.value.phone,
      tier: newCustomer.value.tier as 'A' | 'B' | 'C',
      tags: ['新客户'],
      status: 'active',
    } as any);
    selectedCustomer.value = { id: r.id, name: r.name, contactName: r.contactName || '', phone: r.phone || '', tier: r.tier || 'B' };
    searchText.value = r.name;
    showNewForm.value = false;
    emit('update:customerName', r.name);
    emit('update:customerId', r.id);
  } catch { alert('创建失败'); }
  finally { creating.value = false; }
}

function handleClickOutside(e: MouseEvent) {
  if (pickerRef.value && !pickerRef.value.contains(e.target as Node)) {
    showDropdown.value = false;
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside));
onUnmounted(() => document.removeEventListener('click', handleClickOutside));
</script>

<style scoped>
.vk-customer-picker { position: relative; }
.vk-customer-picker__input-wrap { position: relative; cursor: pointer; }
.vk-customer-picker__input { padding-right: 32px; cursor: pointer; height: 48px; width: 100%; border-radius: var(--r-input); border: 1px solid var(--border); background: var(--surface); font-size: var(--fz-body); padding: 0 14px; outline: none; }
.vk-customer-picker__input:focus { border-color: var(--brand); }
.vk-customer-picker__arrow { position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); transition: transform 0.2s; pointer-events: none; }
.vk-customer-picker__arrow--open { transform: translateY(-50%) rotate(180deg); }
.vk-customer-picker__dropdown { position: absolute; top: 100%; left: 0; right: 0; z-index: 100; background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-input); box-shadow: var(--sh-lg); max-height: 300px; overflow-y: auto; margin-top: 4px; }
.vk-customer-picker__option { display: flex; align-items: center; gap: 10px; padding: 12px 14px; cursor: pointer; transition: background var(--duration-fast); border-bottom: 1px solid var(--border); }
.vk-customer-picker__option:last-child { border-bottom: none; }
.vk-customer-picker__option:hover { background: var(--surface-sunken); }
.vk-customer-picker__option--loading { justify-content: center; color: var(--text-muted); cursor: default; }
.vk-customer-picker__option--new { color: var(--brand); font-weight: var(--fw-medium); justify-content: center; gap: 6px; }
.vk-customer-picker__option-name { font-weight: var(--fw-semibold); font-size: var(--fz-body); flex: 1; }
.vk-customer-picker__option-info { font-size: var(--fz-sm); color: var(--text-muted); }
.vk-customer-picker__new-form { margin-top: 12px; padding: 16px; border: 1px dashed var(--border); border-radius: var(--r-input); background: var(--surface-sunken); display: flex; flex-direction: column; gap: 12px; }
.vk-customer-picker__form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.vk-customer-picker__form-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 4px; }
.quote-form__select { display: flex; flex-direction: column; gap: 6px; }
.quote-form__select select { height: 48px; padding: 0 14px; border-radius: var(--r-input); border: 1px solid var(--border); background: var(--surface); color: var(--text); font-size: var(--fz-body); cursor: pointer; }
.vk-input__label { font-size: var(--fz-sm); font-weight: var(--fw-medium); color: var(--text); margin-bottom: 6px; display: block; }
@media (max-width: 768px) { .vk-customer-picker__form-row { grid-template-columns: 1fr; } }
</style>
