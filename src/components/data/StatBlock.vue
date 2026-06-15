<template>
  <div class="vk-stat-block">
    <div class="vk-stat-block__label">
      {{ label }}
      <span v-if="change !== undefined" :class="['vk-stat-block__change', change >= 0 ? 'vk-stat-block__change--up' : 'vk-stat-block__change--down']">
        {{ change >= 0 ? '↑' : '↓' }} {{ Math.abs(change) }}%
      </span>
    </div>
    <div class="vk-stat-block__value-row">
      <span v-if="currency" class="vk-stat-block__currency">¥</span>
      <span class="vk-stat-block__value">{{ formattedValue }}</span>
      <span v-if="suffix" class="vk-stat-block__suffix">{{ suffix }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  label: string;
  value: number;
  change?: number;
  suffix?: string;
  currency?: boolean;
}

withDefaults(defineProps<Props>(), {
  change: undefined,
  suffix: '',
  currency: false,
});

const formattedValue = computed(() => {
  return new Intl.NumberFormat('zh-CN').format(props.value ?? 0);
});
</script>

<script lang="ts">
export default {
  props: {
    label: { type: String, required: true },
    value: { type: Number, required: true },
    change: { type: Number, default: undefined },
    suffix: { type: String, default: '' },
    currency: { type: Boolean, default: false },
  },
};
</script>

<style scoped>
.vk-stat-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-card);
}

.vk-stat-block__label {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  font-weight: var(--fw-medium);
}

.vk-stat-block__change {
  font-size: var(--fz-xs);
  font-weight: var(--fw-semibold);
  margin-left: 4px;
}

.vk-stat-block__change--up { color: var(--success); }
.vk-stat-block__change--down { color: var(--danger); }

.vk-stat-block__value-row {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.vk-stat-block__currency {
  font-size: 0.6em;
  opacity: 0.5;
  font-weight: var(--fw-medium);
  color: var(--text-muted);
}

.vk-stat-block__value {
  font-family: var(--font-mono);
  font-size: 32px;
  font-weight: var(--fw-bold);
  color: var(--text);
  font-feature-settings: "tnum" 1;
}

.vk-stat-block__suffix {
  font-size: 20px;
  font-weight: var(--fw-semibold);
  color: var(--text-muted);
  margin-left: 2px;
}
</style>
