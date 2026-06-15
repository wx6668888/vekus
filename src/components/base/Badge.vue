<template>
  <span :class="classes">
    <slot />
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type Variant = 'default' | 'success' | 'info' | 'warn' | 'danger';
type Size = 'sm' | 'md';

interface Props {
  variant?: Variant;
  size?: Size;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'md',
});

const classes = computed(() => [
  'vk-badge',
  `vk-badge--${props.variant}`,
  `vk-badge--${props.size}`,
]);
</script>

<style scoped>
.vk-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: var(--r-pill);
  font-size: var(--fz-sm);
  font-weight: var(--fw-medium);
  white-space: nowrap;
}

.vk-badge--sm {
  padding: 2px 8px;
  font-size: var(--fz-xs);
}

.vk-badge--default {
  background: var(--brand-light);
  color: var(--brand);
}

.vk-badge--success {
  background: var(--success-bg);
  color: var(--success);
}

.vk-badge--info {
  background: var(--info-bg);
  color: var(--info);
}

.vk-badge--warn {
  background: var(--warn-bg);
  color: var(--warn);
}

.vk-badge--danger {
  background: var(--danger-bg);
  color: var(--danger);
}
</style>
