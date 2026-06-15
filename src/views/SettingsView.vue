<template>
  <div class="settings-view">
    <Sidebar />
    <main class="settings-view__main">
      <TopBar
        title="系统设置"
        description="维护材料、工艺、税率、报价规则与系统参数"
      />

      <div class="settings-view__layout">
        <div class="settings-view__sidebar">
          <div class="settings-view__categories">
            <button
              v-for="cat in categories"
              :key="cat.id"
              :class="['settings-view__cat', { 'settings-view__cat--active': activeCat === cat.id }]"
              @click="activeCat = cat.id"
            >
              {{ cat.label }}
            </button>
          </div>
        </div>

        <div class="settings-view__content">
          <Card class="settings-view__card">
            <h3 class="settings-view__card-title">
              {{ currentCategory.label }}
              <Button size="sm" variant="secondary" @click="showAddParam = true">新增参数</Button>
            </h3>

            <div v-if="loading" class="vk-skeleton-row"></div>

            <table v-else class="vk-table">
              <thead>
                <tr>
                  <th>名称</th>
                  <th>参数值</th>
                  <th>单位</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody v-if="currentParams.length === 0">
                <tr>
                  <td colspan="5" class="vk-text-muted" style="text-align: center;">暂无数据</td>
                </tr>
              </tbody>
              <tbody>
                <tr v-for="param in currentParams" :key="param.id">
                  <td>{{ param.name }}</td>
                  <td class="vk-font-mono">{{ param.value }}</td>
                  <td>{{ param.unit }}</td>
                  <td>
                    <StatusDot :color="param.enabled ? 'success' : 'muted'" :label="param.enabled ? '启用' : '停用'" />
                  </td>
                  <td>
                    <button class="settings-view__action" @click="deleteParam(param.id)">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </Card>
        </div>
      </div>
    </main>
    <MobileNav />

    <div v-if="showAddParam" class="vk-overlay" @click.self="showAddParam = false">
      <Card class="vk-dialog">
        <h3 class="vk-dialog__title">新增参数</h3>
        <div class="vk-dialog__form">
          <Input v-model="newParam.name" label="名称" placeholder="参数名称" />
          <Input v-model="newParam.value" label="值" placeholder="参数值" />
          <Input v-model="newParam.unit" label="单位" placeholder="单位" />
        </div>
        <div class="vk-dialog__actions">
          <Button variant="ghost" @click="showAddParam = false">取消</Button>
          <Button variant="primary" @click="addParam">保存</Button>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import Sidebar from '@/components/layout/Sidebar.vue';
import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';
import Input from '@/components/base/Input.vue';
import StatusDot from '@/components/base/StatusDot.vue';
import { api } from '@/api';

const activeCat = ref('material');
const loading = ref(true);
const showAddParam = ref(false);
const allParams = ref<any[]>([]);
const newParam = ref({ name: '', value: '', unit: '' });

const categories = [
  { id: 'material', label: '材料' },
  { id: 'surface', label: '表面处理' },
  { id: 'weld', label: '焊接' },
  { id: 'bend', label: '折弯' },
  { id: 'hole', label: '孔类' },
  { id: 'coefficient', label: '系数' },
];

onMounted(async () => {
  const result = await api.get<any[]>('/settings');
  if (result.data) {
    allParams.value = result.data;
  }
  loading.value = false;
});

const currentCategory = computed(() => categories.find(c => c.id === activeCat.value) || categories[0]);
const currentParams = computed(() => allParams.value.filter(p => p.category === activeCat.value));

async function addParam() {
  if (!newParam.value.name) return;
  const result = await api.post<any>('/settings', {
    category: activeCat.value,
    ...newParam.value,
  });
  if (result.data) {
    allParams.value.push(result.data);
  }
  showAddParam.value = false;
  newParam.value = { name: '', value: '', unit: '' };
}

async function deleteParam(id: number) {
  const result = await api.delete(`/settings/${id}`);
  if (!result.error) {
    allParams.value = allParams.value.filter(p => p.id !== id);
  }
}
</script>

<style scoped>
.settings-view {
  display: grid;
  display: block;
  min-height: 100vh;
}

.settings-view__main {
  padding: 24px 32px 120px;
}

.settings-view__layout {
  display: grid;
  grid-template-columns: 200px 1fr;
  gap: 24px;
}

.settings-view__categories {
  display: flex;
  flex-direction: column;
  gap: 4px;
  position: sticky;
  top: 24px;
}

.settings-view__cat {
  padding: 12px 16px;
  border-radius: var(--r-input);
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: var(--fz-body);
  font-weight: var(--fw-medium);
  text-align: left;
  cursor: pointer;
  transition: all var(--duration-fast);
}

.settings-view__cat:hover {
  background: var(--surface-sunken);
  color: var(--text);
}

.settings-view__cat--active {
  background: var(--brand-light);
  color: var(--brand);
  font-weight: var(--fw-semibold);
}

.settings-view__card {
  padding: 20px;
}

.settings-view__card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--fz-h3);
  font-weight: var(--fw-semibold);
  margin: 0 0 16px;
  color: var(--text);
}

.vk-skeleton-row {
  height: 200px;
  background: var(--surface-sunken);
  border-radius: var(--r-input);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
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
}

.vk-table td {
  padding: 14px 16px;
  font-size: var(--fz-body);
  border-bottom: 1px solid var(--border);
  color: var(--text);
}

.settings-view__action {
  padding: 6px 12px;
  border-radius: var(--r-tag);
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  font-size: var(--fz-sm);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.settings-view__action:hover {
  border-color: var(--danger);
  color: var(--danger);
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
  .settings-view {
    grid-template-columns: 1fr;
    overflow-x: hidden;
  }
  .settings-view__main {
    padding: 16px 16px 100px;
    overflow-x: hidden;
    max-width: 100vw;
  }
  .settings-view__layout {
    grid-template-columns: 1fr;
  }
  .settings-view__categories {
    flex-direction: row;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
    position: static;
    padding-bottom: 8px;
  }
  .settings-view__cat {
    white-space: nowrap;
    flex-shrink: 0;
  }
  .settings-view__card {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    overscroll-behavior: contain;
  }
  .vk-table {
    min-width: 500px;
  }
}
</style>
