<template>
  <header class="vk-topnav">
    <div class="vk-topnav__brand">
      <div class="vk-topnav__logo">V</div>
      <span class="vk-topnav__brand-name">Vekus</span>
    </div>
    <nav class="vk-topnav__nav">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="vk-topnav__item"
        :class="{ 'vk-topnav__item--active': isActive(item.path) }"
      >
        <component :is="item.icon" :size="18" :stroke-width="isActive(item.path) ? 2.2 : 1.6" />
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
    <div class="vk-topnav__user" @click="$router.push('/me')">
      <div class="vk-topnav__avatar">{{ userName.charAt(0) }}</div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import { LayoutDashboard, FileText, History, Users, ShoppingBag, MessageSquare, Settings, User } from 'lucide-vue-next';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const authStore = useAuthStore();
const userName = ref(authStore.user?.name || 'User');

const navItems = computed(() => [
  { path: '/dashboard', label: '看板', icon: LayoutDashboard },
  { path: '/quote', label: '报价', icon: FileText },
  { path: '/history', label: '历史', icon: History },
  { path: '/customers', label: '客户', icon: Users },
  { path: '/marketplace', label: '交易', icon: ShoppingBag },
  { path: '/messages', label: '消息', icon: MessageSquare },
  { path: '/settings', label: '设置', icon: Settings },
]);

function isActive(path: string): boolean {
  if (path === '/quote' && route.path.startsWith('/quote')) return true;
  if (path === '/marketplace' && route.path.startsWith('/marketplace')) return true;
  if (path === '/messages' && route.path.startsWith('/messages')) return true;
  if (path === '/customers' && route.path.startsWith('/customers')) return true;
  return route.path === path;
}
</script>

<style scoped>
.vk-topnav {
  display: none;
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  height: 56px;
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(24px) saturate(200%);
  -webkit-backdrop-filter: blur(24px) saturate(200%);
  border-bottom: 0.5px solid rgba(0, 0, 0, 0.08);
  padding: 0 20px;
  align-items: center;
  gap: 8px;
}

.vk-topnav__brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: 12px;
  flex-shrink: 0;
}

.vk-topnav__logo {
  width: 34px; height: 34px;
  border-radius: 9px;
  background: linear-gradient(135deg, var(--brand), var(--accent));
  color: white;
  display: grid; place-items: center;
  font-size: 16px; font-weight: var(--fw-bold);
}

.vk-topnav__brand-name {
  font-size: 15px; font-weight: var(--fw-bold);
  color: var(--text);
}

.vk-topnav__nav {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
  overflow-x: auto;
}

.vk-topnav__item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 10px;
  color: #8E8E93;
  font-size: 13px;
  font-weight: 500;
  text-decoration: none;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.vk-topnav__item:hover { background: rgba(0,0,0,0.04); color: var(--text); }
.vk-topnav__item--active { background: var(--brand-light); color: var(--brand); font-weight: 600; }

.vk-topnav__user { margin-left: auto; flex-shrink: 0; cursor: pointer; }
.vk-topnav__avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--brand), var(--accent));
  color: white;
  display: grid; place-items: center;
  font-size: 14px; font-weight: var(--fw-bold);
}

@media (min-width: 769px) {
  .vk-topnav { display: flex; }
}
</style>
