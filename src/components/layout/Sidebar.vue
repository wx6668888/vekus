<template>
  <aside class="vk-sidebar">
    <div class="vk-sidebar__brand">
      <div class="vk-sidebar__logo">V</div>
      <div class="vk-sidebar__brand-text">
        <div class="vk-sidebar__brand-name">Vekus</div>
        <div class="vk-sidebar__brand-sub">AI 报价工作台</div>
      </div>
    </div>

    <nav class="vk-sidebar__nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="vk-sidebar__item"
        :class="{ 'vk-sidebar__item--active': isActive(item.path) }"
      >
        <component :is="item.icon" :size="20" />
        <span>{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="vk-sidebar__card">
      <div class="vk-sidebar__card-label">当前状态</div>
      <div class="vk-sidebar__status-row">
        <StatusDot color="success" size="sm" />
        <span>系统运行正常</span>
      </div>
      <p class="vk-sidebar__card-text">报价、识图、客户管理功能已就绪</p>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { LayoutDashboard, FileText, History, Users, Settings, User, ShoppingBag, MessageSquare, Layers, Package, Wrench, ShieldCheck, Truck, CheckCircle, FolderOpen } from 'lucide-vue-next';
import StatusDot from '../base/StatusDot.vue';

const route = useRoute();

const navItems = computed(() => [
  { path: '/dashboard', label: '看板', icon: LayoutDashboard },
  { path: '/bom', label: 'BOM', icon: Layers },
  { path: '/inventory', label: '库存', icon: Package },
  { path: '/production', label: '生产', icon: Wrench },
  { path: '/quality', label: '质量', icon: ShieldCheck },
  { path: '/purchases', label: '采购', icon: Truck },
  { path: '/approvals', label: '审批', icon: CheckCircle },
  { path: '/documents', label: '文档', icon: FolderOpen },
  { path: '/quote', label: '报价', icon: FileText },
  { path: '/history', label: '历史', icon: History },
  { path: '/customers', label: '客户', icon: Users },
  { path: '/marketplace', label: '交易', icon: ShoppingBag },
  { path: '/messages', label: '消息', icon: MessageSquare },
  { path: '/settings', label: '设置', icon: Settings },
  { path: '/me', label: '我的', icon: User },
]);

function isActive(path: string): boolean {
  if (path === '/quote' && route.path.startsWith('/quote')) return true;
  return route.path === path;
}
</script>

<style scoped>
.vk-sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  width: 240px;
  padding: 24px 16px 120px;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.vk-sidebar__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding: 0 8px;
}

.vk-sidebar__logo {
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--brand), var(--accent));
  color: white;
  display: grid;
  place-items: center;
  font-size: 20px;
  font-weight: var(--fw-bold);
  box-shadow: var(--sh-md);
}

.vk-sidebar__brand-name {
  font-size: 16px;
  font-weight: var(--fw-bold);
  color: var(--text);
}

.vk-sidebar__brand-sub {
  font-size: 12px;
  color: var(--text-muted);
}

.vk-sidebar__nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.vk-sidebar__item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: var(--r-input);
  color: var(--text-muted);
  font-size: var(--fz-body);
  font-weight: var(--fw-medium);
  transition: all var(--duration-fast) var(--ease-out);
  text-decoration: none;
}

.vk-sidebar__item:hover {
  background: var(--surface-sunken);
  color: var(--text);
}

.vk-sidebar__item--active {
  background: var(--brand-light);
  color: var(--brand);
}

.vk-sidebar__card {
  margin-top: auto;
  padding: 16px;
  border-radius: var(--r-card);
  background: var(--surface-sunken);
  border: 1px solid var(--border);
}

.vk-sidebar__card-label {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  margin-bottom: 10px;
}

.vk-sidebar__status-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--fz-body);
  font-weight: var(--fw-semibold);
  color: var(--text);
  margin-bottom: 8px;
}

.vk-sidebar__card-text {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  line-height: var(--lh-relaxed);
  margin: 0;
}

/* Sidebar hidden on both mobile (<768px) and when desktop topnav is active (>=769px) */
.vk-sidebar {
  display: none;
}

</style>
