<template>
  <button
    :class="classes"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="vk-btn__spinner"></span>
    <slot />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';
type Size = 'sm' | 'md' | 'lg';

interface Props {
  variant?: Variant;
  size?: Size;
  disabled?: boolean;
  loading?: boolean;
  block?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false,
  block: false,
});

const emit = defineEmits<{
  click: [event: MouseEvent];
}>();

const classes = computed(() => [
  'vk-btn',
  `vk-btn--${props.variant}`,
  `vk-btn--${props.size}`,
  {
    'vk-btn--disabled': props.disabled || props.loading,
    'vk-btn--block': props.block,
  },
]);

function handleClick(e: MouseEvent) {
  if (!props.disabled && !props.loading) {
    emit('click', e);
  }
}
</script>

<style scoped>
.vk-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: var(--r-input);
  font-weight: var(--fw-semibold);
  font-size: var(--fz-body);
  transition: all var(--duration-normal) var(--ease-out);
  cursor: pointer;
  white-space: nowrap;
  border: 1px solid transparent;
}

.vk-btn--sm {
  height: 36px;
  padding: 0 14px;
  font-size: var(--fz-sm);
}

.vk-btn--md {
  height: 44px;
  padding: 0 18px;
}

.vk-btn--lg {
  height: 52px;
  padding: 0 24px;
  font-size: var(--fz-h3);
}

.vk-btn--primary {
  background: var(--brand);
  color: white;
  border-color: var(--brand);
}

.vk-btn--primary:hover:not(.vk-btn--disabled) {
  background: var(--brand-strong);
  border-color: var(--brand-strong);
  transform: translateY(-1px);
  box-shadow: var(--sh-md);
}

.vk-btn--secondary {
  background: var(--surface-sunken);
  color: var(--text);
  border-color: var(--border);
}

.vk-btn--secondary:hover:not(.vk-btn--disabled) {
  background: var(--surface-blueprint);
  color: white;
  border-color: var(--surface-blueprint);
}

.vk-btn--ghost {
  background: transparent;
  color: var(--text-muted);
  border-color: var(--border);
}

.vk-btn--ghost:hover:not(.vk-btn--disabled) {
  color: var(--text);
  border-color: var(--border-strong);
  background: var(--surface-sunken);
}

.vk-btn--danger {
  background: var(--danger-bg);
  color: var(--danger);
  border-color: transparent;
}

.vk-btn--danger:hover:not(.vk-btn--disabled) {
  background: var(--danger);
  color: white;
}

.vk-btn--disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.vk-btn--block {
  width: 100%;
}

.vk-btn__spinner {
  width: 16px;
  height: 16px;
  border: 2px solid currentColor;
  border-right-color: transparent;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
