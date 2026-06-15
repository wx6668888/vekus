<template>
  <transition name="toast">
    <div v-if="visible" :class="classes">
      <span v-if="icon" class="vk-toast__icon">{{ icon }}</span>
      <span class="vk-toast__message">{{ message }}</span>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

type Variant = 'success' | 'info' | 'warn' | 'error';

interface Props {
  message: string;
  variant?: Variant;
  duration?: number;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'info',
  duration: 3000,
});

const visible = ref(false);

const classes = computed(() => [
  'vk-toast',
  `vk-toast--${props.variant}`,
]);

const icons: Record<Variant, string> = {
  success: '✓',
  info: 'ℹ',
  warn: '⚠',
  error: '✕',
};

const icon = computed(() => icons[props.variant]);

onMounted(() => {
  visible.value = true;
  if (props.duration > 0) {
    setTimeout(() => {
      visible.value = false;
    }, props.duration);
  }
});
</script>

<style scoped>
.vk-toast {
  position: fixed;
  right: 24px;
  bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-radius: var(--r-input);
  background: var(--surface-blueprint);
  color: white;
  font-size: var(--fz-body);
  box-shadow: var(--sh-lg);
  z-index: var(--z-toast);
  min-width: 280px;
  max-width: 400px;
}

.vk-toast__icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  font-weight: var(--fw-bold);
}

.vk-toast--success .vk-toast__icon { background: var(--success); }
.vk-toast--info .vk-toast__icon { background: var(--info); }
.vk-toast--warn .vk-toast__icon { background: var(--warn); }
.vk-toast--error .vk-toast__icon { background: var(--danger); }

.toast-enter-active,
.toast-leave-active {
  transition: all var(--duration-normal) var(--ease-out);
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
