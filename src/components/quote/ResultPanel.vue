<template>
  <div class="vk-result-panel">
    <div class="vk-result-panel__hero blueprint-grid">
      <div class="vk-result-panel__hero-content">
        <div class="vk-result-panel__quote-no">{{ quoteNo }}</div>
        <PriceDisplay :value="result.totalPrice" size="display" color="accent" />
        <div class="vk-result-panel__sub">
          <span>单价</span>
          <PriceDisplay :value="result.unitPrice" size="md" show-cents />
          <span>· 利润率 {{ result.profitMargin }}%</span>
        </div>
      </div>
    </div>

    <div class="vk-result-panel__breakdown">
      <h3 class="vk-result-panel__section-title">成本拆解</h3>
      <div class="vk-result-panel__breakdown-list">
        <div v-for="(value, key) in result.breakdown" :key="key" class="vk-result-panel__breakdown-item">
          <span class="vk-result-panel__breakdown-label">{{ breakdownLabels[key] }}</span>
          <PriceDisplay :value="value" size="sm" />
        </div>
        <div class="vk-result-panel__breakdown-total">
          <span>小计</span>
          <PriceDisplay :value="subtotal" size="md" />
        </div>
      </div>
    </div>

    <div v-if="result.warnings.length > 0" class="vk-result-panel__warnings">
      <h3 class="vk-result-panel__section-title">注意</h3>
      <div v-for="warning in result.warnings" :key="warning" class="vk-result-panel__warning">
        <AlertTriangle :size="14" />
        {{ warning }}
      </div>
    </div>

    <div class="vk-result-panel__actions">
      <Button variant="secondary" size="lg" block @click="$emit('save-draft')">
        保存草稿
      </Button>
      <Button variant="primary" size="lg" block @click="$emit('send')">
        发送报价
      </Button>
    </div>

    <div v-if="lastSaved" class="vk-result-panel__footer">
      上次保存: {{ lastSaved }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { AlertTriangle } from 'lucide-vue-next';
import PriceDisplay from '../data/PriceDisplay.vue';
import Button from '../base/Button.vue';
import type { QuoteResult } from '@/api/quote';

interface Props {
  quoteNo: string;
  result: QuoteResult;
  lastSaved?: string;
}

const props = defineProps<Props>();

defineEmits<{
  'save-draft': [];
  'send': [];
}>();

const breakdownLabels: Record<string, string> = {
  material: '材料费',
  cutting: '切割费',
  bending: '折弯费',
  welding: '焊接费',
  surface: '表面处理',
  admin: '管理费',
  profit: '利润',
};

const subtotal = computed(() => {
  return Object.values(props.result.breakdown).reduce((a, b) => a + b, 0);
});
</script>

<style scoped>
.vk-result-panel {
  position: sticky;
  top: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.vk-result-panel__hero {
  padding: 28px;
  border-radius: var(--r-hero);
  background: linear-gradient(180deg, var(--surface-blueprint), var(--surface-blueprint-light));
  color: white;
  box-shadow: var(--sh-blueprint);
}

.vk-result-panel__quote-no {
  font-size: var(--fz-sm);
  font-weight: var(--fw-medium);
  opacity: 0.7;
  font-family: var(--font-mono);
  margin-bottom: 12px;
}

.vk-result-panel__hero-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.vk-result-panel__sub {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: var(--fz-body);
  opacity: 0.8;
}

.vk-result-panel__breakdown {
  padding: 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-card);
}

.vk-result-panel__section-title {
  font-size: var(--fz-h3);
  font-weight: var(--fw-semibold);
  color: var(--text);
  margin: 0 0 14px;
}

.vk-result-panel__breakdown-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.vk-result-panel__breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--fz-body);
}

.vk-result-panel__breakdown-label {
  color: var(--text-muted);
}

.vk-result-panel__breakdown-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--border);
  margin-top: 4px;
  font-weight: var(--fw-semibold);
}

.vk-result-panel__warnings {
  padding: 16px;
  background: var(--warn-bg);
  border: 1px solid var(--warn-bg);
  border-radius: var(--r-input);
}

.vk-result-panel__warning {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--fz-body);
  color: var(--warn);
}

.vk-result-panel__actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.vk-result-panel__footer {
  text-align: center;
  font-size: var(--fz-sm);
  color: var(--text-faint);
}

@media (max-width: 768px) {
  .vk-result-panel {
    position: static;
  }
}
</style>
