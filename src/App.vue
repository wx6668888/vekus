<template>
  <DesktopTopNav v-if="!isAuthPage" />
  <router-view />
  <div class="vk-toast-container">
    <transition-group name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        :class="['vk-toast', `vk-toast--${t.variant}`]"
      >
        <span class="vk-toast__icon">{{ icons[t.variant] }}</span>
        <span class="vk-toast__message">{{ t.message }}</span>
      </div>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import DesktopTopNav from '@/components/layout/DesktopTopNav.vue';
import { toast } from '@/services/toast';

const route = useRoute();
const isAuthPage = computed(() => ['/login', '/register'].includes(route.path));

const { toasts } = toast;

const icons: Record<string, string> = {
  success: '✓',
  info: 'ℹ',
  warn: '⚠',
  error: '✕',
};
</script>

<style>
#app {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
}

.vk-toast-container {
  position: fixed;
  right: 24px;
  bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 9999;
  pointer-events: none;
}

.vk-toast {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-radius: var(--r-input);
  background: var(--surface-blueprint);
  color: white;
  font-size: var(--fz-body);
  box-shadow: var(--sh-lg);
  min-width: 280px;
  max-width: 400px;
  pointer-events: auto;
}

.vk-toast__icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: var(--fw-bold);
  background: rgba(255,255,255,0.15);
}

.vk-toast--success .vk-toast__icon { background: #16A34A; }
.vk-toast--info .vk-toast__icon { background: #0891B2; }
.vk-toast--warn .vk-toast__icon { background: #CA8A04; }
.vk-toast--error .vk-toast__icon { background: #DC2626; }

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease-out;
}

.toast-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.toast-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
