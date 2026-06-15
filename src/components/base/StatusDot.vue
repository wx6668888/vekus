<template>
  <span class="vk-status-dot" :class="`vk-status-dot--${color}`" :title="label">
    <span class="vk-status-dot__dot"></span>
    <span v-if="showLabel" class="vk-status-dot__label">{{ label }}</span>
  </span>
</template>

<script setup lang="ts">
type Color = 'success' | 'info' | 'warn' | 'danger' | 'muted';

interface Props {
  color?: Color;
  label?: string;
  showLabel?: boolean;
}

withDefaults(defineProps<Props>(), {
  color: 'success',
  label: '',
  showLabel: true,
});
</script>

<style scoped>
.vk-status-dot {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.vk-status-dot__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  box-shadow: 0 0 0 4px var(--dot-bg, rgba(22, 163, 74, 0.16));
}

.vk-status-dot--success .vk-status-dot__dot {
  background: var(--success);
  --dot-bg: var(--success-bg);
}

.vk-status-dot--info .vk-status-dot__dot {
  background: var(--info);
  --dot-bg: var(--info-bg);
}

.vk-status-dot--warn .vk-status-dot__dot {
  background: var(--warn);
  --dot-bg: var(--warn-bg);
}

.vk-status-dot--danger .vk-status-dot__dot {
  background: var(--danger);
  --dot-bg: var(--danger-bg);
}

.vk-status-dot--muted .vk-status-dot__dot {
  background: var(--text-faint);
  --dot-bg: var(--surface-sunken);
}

.vk-status-dot__label {
  font-size: var(--fz-sm);
  color: var(--text-muted);
}
</style>
