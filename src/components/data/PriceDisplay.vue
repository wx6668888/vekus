<template>
  <span :class="classes" :title="formatted">
    <span class="vk-price__symbol">¥</span>
    <span class="vk-price__value">{{ formatted }}</span>
    <span v-if="unit" class="vk-price__unit">/ {{ unit }}</span>
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type Size = 'sm' | 'md' | 'lg' | 'display';

interface Props {
  value: number;
  size?: Size;
  color?: 'default' | 'accent' | 'muted';
  showCents?: boolean;
  unit?: string;
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  color: 'default',
  showCents: true,
  unit: '',
});

const formatted = computed(() => {
  const options: Intl.NumberFormatOptions = {
    minimumFractionDigits: props.showCents ? 2 : 0,
    maximumFractionDigits: props.showCents ? 2 : 0,
  };
  return new Intl.NumberFormat('zh-CN', options).format(props.value);
});

const classes = computed(() => [
  'vk-price',
  `vk-price--${props.size}`,
  `vk-price--${props.color}`,
]);
</script>

<style scoped>
.vk-price {
  font-family: var(--font-mono);
  font-feature-settings: "tnum" 1;
  font-weight: var(--fw-bold);
  display: inline-flex;
  align-items: baseline;
  gap: 2px;
}

.vk-price__symbol {
  font-size: 0.6em;
  opacity: 0.6;
  font-weight: var(--fw-medium);
}

.vk-price__value {
  font-variant-numeric: tabular-nums;
}

.vk-price__unit {
  font-family: var(--font-sans);
  font-size: 0.4em;
  opacity: 0.5;
  font-weight: var(--fw-normal);
}

/* Sizes */
.vk-price--sm { font-size: 14px; }
.vk-price--md { font-size: 24px; }
.vk-price--lg { font-size: 36px; }
.vk-price--display { font-size: 64px; line-height: 1; }

/* Colors */
.vk-price--default { color: var(--text); }
.vk-price--accent { color: var(--accent); }
.vk-price--muted { color: var(--text-muted); }
</style>
