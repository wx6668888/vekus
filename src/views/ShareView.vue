<template>
  <div class="share-view">
    <div v-if="loading" class="share-view__loading">
      <div class="vk-skeleton-hero"></div>
    </div>

    <div v-else-if="error" class="share-view__error">
      <p>报价不存在或已失效</p>
    </div>

    <template v-else>
      <div class="share-view__hero blueprint-grid">
        <div class="share-view__hero-content">
          <div class="share-view__brand">
            <div class="share-view__logo">V</div>
            <span>Vekus 智能报价</span>
          </div>
          <div class="share-view__amount">
            <div class="share-view__amount-label">报价金额</div>
            <PriceDisplay :value="totalPrice" size="display" color="accent" />
          </div>
          <div class="share-view__meta">
            <span class="share-view__quote-no">{{ quoteNo }}</span>
            <span class="share-view__sep">|</span>
            <span>{{ customerName }}</span>
          </div>
        </div>
      </div>

      <div class="share-view__body">
        <Card class="share-view__card">
          <h3 class="share-view__section-title">配置摘要</h3>
          <div class="share-view__summary-grid">
            <div><span class="vk-text-muted">材料</span><div class="vk-font-mono">{{ material }}</div></div>
            <div><span class="vk-text-muted">厚度</span><div class="vk-font-mono">{{ thickness }} mm</div></div>
            <div><span class="vk-text-muted">数量</span><div class="vk-font-mono">{{ quantity }} 件</div></div>
            <div><span class="vk-text-muted">表面处理</span><div>{{ surface }}</div></div>
          </div>
        </Card>

        <Card class="share-view__card">
          <h3 class="share-view__section-title">
            成本明细
            <button class="share-view__toggle" @click="showBreakdown = !showBreakdown">
              {{ showBreakdown ? '收起' : '展开' }}
            </button>
          </h3>
          <div v-if="showBreakdown" class="share-view__breakdown">
            <div v-for="(value, key) in breakdown" :key="key" class="share-view__breakdown-item">
              <span class="vk-text-muted">{{ breakdownLabels[key as keyof typeof breakdownLabels] }}</span>
              <PriceDisplay :value="value" size="sm" />
            </div>
          </div>
        </Card>

        <div class="share-view__actions">
          <Button variant="secondary" size="lg" block @click="copyLink">
            <Share :size="18" class="mr-2" />复制链接
          </Button>
          <Button variant="primary" size="lg" block @click="contactSales">
            <Phone :size="18" class="mr-2" />联系业务员
          </Button>
        </div>

        <div class="share-view__footer">
          <p class="vk-text-faint">由 Vekus 智能报价平台生成 · 仅供参考</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { api } from '@/api';
import { computeBreakdown } from '@/services/quoteCalculator';
import type { RecognizedResult, QuoteBreakdown } from '@/api/quote';
import PriceDisplay from '@/components/data/PriceDisplay.vue';
import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';
import { Share, Phone } from 'lucide-vue-next';

const route = useRoute();
const loading = ref(true);
const error = ref(false);
const salesContact = ref<{ name: string; phone: string }>({ name: '', phone: '400-888-9999' });
const showBreakdown = ref(false);
const quoteNo = ref('');
const customerName = ref('');
const totalPrice = ref(0);
const material = ref('');
const thickness = ref(0);
const quantity = ref(0);
const surface = ref('');
const breakdown = ref<QuoteBreakdown>({ material: 0, cutting: 0, bending: 0, welding: 0, surface: 0, admin: 0, profit: 0 });

const breakdownLabels: Record<string, string> = {
  material: '材料费', cutting: '切割费', bending: '折弯费',
  welding: '焊接费', surface: '表面处理', admin: '管理费', profit: '利润',
};

onMounted(async () => {
  // Fetch sales contact info
  try {
    const profileResult = await api.get<any>('/profile');
    if (profileResult.data) {
      salesContact.value = {
        name: profileResult.data.name || '业务员',
        phone: profileResult.data.phone || '400-888-9999',
      };
    }
  } catch { /* ignore */ }

  try {
    const result = await api.get<any>(`/quotes/${route.params.id}`);
    if (!result.data) {
      error.value = true;
      return;
    }
    const q = result.data;
    quoteNo.value = q.quoteNo || '';
    customerName.value = q.customerName || '';
    totalPrice.value = q.totalPrice || 0;
    material.value = q.material || '';
    thickness.value = q.thickness || 0;
    quantity.value = q.quantity || 0;
    surface.value = q.surface || '';

    const recognized: RecognizedResult = q.recognized || {
      thickness: q.thickness || 1.5, expandLength: 420, expandWidth: 280,
      cutLength: 2140, bendCount: 6, paintArea: 0.32,
      weldPoints: 14, weldLength: 0,
      holes: { plain: 8, threaded: 4, counterbored: 2 },
    };
    const coef = q.coefficients || {};
    breakdown.value = computeBreakdown({
      material: q.material || '镀锌板',
      thickness: q.thickness || 1.5,
      quantity: q.quantity || 1,
      surface: q.surface || '喷粉',
      recognized,
      profitRate: coef.profitRate || 0.28,
    });
  } catch {
    error.value = true;
  } finally {
    loading.value = false;
  }
});

function copyLink() {
  navigator.clipboard.writeText(window.location.href).then(() => {
    alert('链接已复制');
  });
}

function contactSales() {
  alert(`请联系 ${salesContact.value.name || '业务员'}：${salesContact.value.phone || '400-888-9999'}`);
}
</script>

<style scoped>
.share-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}

.share-view__hero {
  padding: 40px 24px;
  background: linear-gradient(180deg, var(--surface-blueprint), var(--surface-blueprint-light));
  color: white;
}

.share-view__hero-content {
  max-width: 500px;
  margin: 0 auto;
  text-align: center;
}

.share-view__brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 32px;
  font-size: var(--fz-body);
  opacity: 0.8;
}

.share-view__logo {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, var(--brand), var(--accent));
  display: grid;
  place-items: center;
  font-size: 18px;
  font-weight: var(--fw-bold);
}

.share-view__amount-label {
  font-size: var(--fz-sm);
  opacity: 0.6;
  margin-bottom: 8px;
}

.share-view__meta {
  margin-top: 16px;
  font-size: var(--fz-sm);
  opacity: 0.7;
}

.share-view__sep {
  margin: 0 8px;
}

.share-view__body {
  flex: 1;
  padding: 24px 16px;
  max-width: 500px;
  margin: -24px auto 0;
  position: relative;
  z-index: 1;
  width: 100%;
}

.share-view__card {
  padding: 20px;
  margin-bottom: 16px;
}

.share-view__section-title {
  font-size: var(--fz-h3);
  font-weight: var(--fw-semibold);
  margin: 0 0 16px;
  color: var(--text);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.share-view__toggle {
  background: none;
  border: 1px solid var(--border);
  padding: 4px 12px;
  border-radius: var(--r-tag);
  font-size: var(--fz-sm);
  color: var(--brand);
  cursor: pointer;
}

.share-view__summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.share-view__breakdown {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.share-view__breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.share-view__actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 8px;
}

.share-view__footer {
  text-align: center;
  padding: 24px;
  margin-top: 16px;
}

.share-view__footer p {
  margin: 0;
}

.mr-2 { margin-right: 8px; }

.vk-skeleton-hero {
  height: 100vh;
  background: var(--surface-sunken);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.share-view__loading,
.share-view__error {
  min-height: 100vh;
  display: grid;
  place-items: center;
  color: var(--text-muted);
}
</style>
