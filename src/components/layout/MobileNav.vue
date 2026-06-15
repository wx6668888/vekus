<template>
  <nav class="vk-mobile-nav">
    <div class="vk-mobile-nav__container">
      <div class="vk-mobile-nav__inner">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="vk-mobile-nav__item"
          :class="{ 'vk-mobile-nav__item--active': isActive(item.path) }"
        >
          <div class="vk-mobile-nav__icon-wrap">
            <component :is="item.icon" :size="22" :stroke-width="isActive(item.path) ? 2.5 : 1.8" />
          </div>
          <span class="vk-mobile-nav__label">{{ item.label }}</span>
        </router-link>
      </div>
    </div>
    <div class="vk-mobile-nav__home-indicator">
      <div class="vk-mobile-nav__indicator-bar"></div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { LayoutDashboard, FileText, ShoppingBag, MessageSquare, User } from 'lucide-vue-next';

const route = useRoute();

const navItems = computed(() => [
  { path: '/dashboard', label: '看板', icon: LayoutDashboard },
  { path: '/quote', label: '报价', icon: FileText },
  { path: '/marketplace', label: '交易', icon: ShoppingBag },
  { path: '/messages', label: '消息', icon: MessageSquare },
  { path: '/me', label: '我的', icon: User },
]);

function isActive(path: string): boolean {
  if (path === '/quote' && route.path.startsWith('/quote')) return true;
  if (path === '/marketplace' && route.path.startsWith('/marketplace')) return true;
  if (path === '/messages' && route.path.startsWith('/messages')) return true;
  return route.path === path;
}
</script>

<style scoped>
.vk-mobile-nav {
  display: none;
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: var(--z-sticky);
  padding: 0 12px env(safe-area-inset-bottom, 0);
  pointer-events: none;
}

.vk-mobile-nav__container {
  background: rgba(255, 255, 255, 0.82);
  backdrop-filter: blur(28px) saturate(200%);
  -webkit-backdrop-filter: blur(28px) saturate(200%);
  border: 0.5px solid rgba(0, 0, 0, 0.06);
  border-radius: 32px;
  box-shadow:
    0 -1px 0 rgba(0, 0, 0, 0.03),
    0 8px 32px rgba(0, 0, 0, 0.06),
    0 2px 8px rgba(0, 0, 0, 0.04);
  pointer-events: auto;
  margin-bottom: 6px;
}

.vk-mobile-nav__inner {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  padding: 8px 6px 4px;
}

.vk-mobile-nav__item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  padding: 4px 2px 2px;
  text-decoration: none;
  position: relative;
  -webkit-tap-highlight-color: transparent;
}

.vk-mobile-nav__icon-wrap {
  display: grid;
  place-items: center;
  width: 34px;
  height: 26px;
  color: #8E8E93;
  transition: all 0.2s ease;
}

.vk-mobile-nav__item--active .vk-mobile-nav__icon-wrap {
  color: var(--brand);
}

.vk-mobile-nav__label {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.1px;
  color: #8E8E93;
  transition: all 0.2s ease;
}

.vk-mobile-nav__item--active .vk-mobile-nav__label {
  color: var(--brand);
  font-weight: 600;
}

.vk-mobile-nav__home-indicator {
  display: flex;
  justify-content: center;
  padding: 5px 0 7px;
  pointer-events: none;
}

.vk-mobile-nav__indicator-bar {
  width: 134px;
  height: 5px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.18);
}

@media (max-width: 768px) {
  .vk-mobile-nav {
    display: block;
  }
}
</style>
