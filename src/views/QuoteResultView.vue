<template>
  <div class="quote-result-view">
    <div v-if="loading" class="quote-result-view__loading">
      <div class="vk-skeleton-hero"></div>
    </div>

    <template v-else>
      <div class="quote-result-view__hero blueprint-grid">
        <div class="quote-result-view__content">
          <div class="quote-result-view__quote-no">{{ quoteNo }}</div>
          <PriceDisplay :value="totalPrice" size="display" color="accent" />
          <div class="quote-result-view__customer">
            <span>客户:</span> {{ customerName }}
          </div>
        </div>
      </div>

      <div class="quote-result-view__body">
        <Card class="quote-result-view__card">
          <h3 class="quote-result-view__section-title">配置摘要</h3>
          <div class="quote-result-view__summary-grid">
            <div>
              <span class="vk-text-muted">材料</span>
              <div class="vk-text vk-font-mono">{{ material }}</div>
            </div>
            <div>
              <span class="vk-text-muted">厚度</span>
              <div class="vk-text vk-font-mono">{{ thickness }} mm</div>
            </div>
            <div>
              <span class="vk-text-muted">数量</span>
              <div class="vk-text vk-font-mono">{{ quantity }} 件</div>
            </div>
            <div>
              <span class="vk-text-muted">表面处理</span>
              <div class="vk-text">{{ surface }}</div>
            </div>
          </div>
        </Card>

        <Card class="quote-result-view__card">
          <h3 class="quote-result-view__section-title">成本明细</h3>
          <div class="quote-result-view__breakdown">
            <div v-for="(value, key) in breakdown" :key="key" class="quote-result-view__breakdown-item">
              <span class="vk-text-muted">{{ breakdownLabels[key as keyof typeof breakdownLabels] }}</span>
              <PriceDisplay :value="value" size="sm" />
            </div>
          </div>
        </Card>

        <div class="quote-result-view__actions">
          <Button variant="secondary" size="lg" @click="downloadPdf">
            <FileDown :size="18" class="mr-2" /> 导出 PDF
          </Button>
          <Button variant="secondary" size="lg" @click="copyLink">
            <Share :size="18" class="mr-2" /> 复制链接
          </Button>
          <Button variant="primary" size="lg" @click="contactSales">
            <Phone :size="18" class="mr-2" /> 联系业务员
          </Button>
        </div>

        <div class="quote-result-view__footer">
          <p class="vk-text-faint">由 Vekus 智能报价平台生成</p>
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
import { Share, Phone, FileDown } from 'lucide-vue-next';
import pdfMake from 'pdfmake/build/pdfmake';
import pdfFonts from 'pdfmake/build/vfs_fonts';

const route = useRoute();
const loading = ref(true);
const salesContact = ref<{ name: string; phone: string }>({ name: '', phone: '400-888-9999' });
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
    if (result.data) {
      const q = result.data;
      quoteNo.value = q.quoteNo || '';
      customerName.value = q.customerName || '';
      totalPrice.value = q.totalPrice || 0;
      material.value = q.material || '';
      thickness.value = q.thickness || 0;
      quantity.value = q.quantity || 0;
      surface.value = q.surface || '';
      // Compute breakdown from recognized data
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
    }
  } catch (error) {
    console.error('加载报价失败:', error);
  } finally {
    loading.value = false;
  }
});

function downloadPdf() {
  pdfMake.vfs = pdfFonts.pdfMake ? pdfFonts.pdfMake.vfs : pdfFonts;
  const doc = pdfMake.createPdf({
    content: [
      { text: 'Vekus 智能报价单', style: 'header' },
      { text: `报价单号: ${quoteNo}`, margin: [0,4,0,4] },
      { text: `客户: ${customerName}`, margin: [0,0,0,4] },
      { text: `材料: ${material} / ${thickness}mm`, margin: [0,0,0,2] },
      { text: `数量: ${quantity} 件 · 表面处理: ${surface}`, margin: [0,0,0,2] },
      { text: `交期: ${deliveryDays} 天`, margin: [0,0,0,12] },
      { text: `报价总价: ¥${new Intl.NumberFormat('zh-CN').format(totalPrice.value)}`, style: 'price' },
    ],
    styles: {
      header: { fontSize: 22, bold: true, margin: [0,0,0,8] },
      price: { fontSize: 28, bold: true, color: '#F97316', margin: [0,8,0,0] },
    }
  });
  doc.download(`报价单_${quoteNo}.pdf`);
}

function copyLink() {
  const url = window.location.href;
  navigator.clipboard.writeText(url).then(() => {
    alert('链接已复制');
  });
}

function contactSales() {
  alert(`请联系 ${salesContact.value.name || '业务员'}：${salesContact.value.phone || '400-888-9999'}`);
}
</script>

<style scoped>
.quote-result-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.quote-result-view__loading {
  min-height: 100vh;
}

.vk-skeleton-hero {
  height: 50vh;
  background: var(--surface-sunken);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.quote-result-view__hero {
  padding: 48px 24px;
  background: linear-gradient(180deg, var(--surface-blueprint), var(--surface-blueprint-light));
  color: white;
}

.quote-result-view__content {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.quote-result-view__quote-no {
  font-size: var(--fz-sm);
  font-weight: var(--fw-medium);
  opacity: 0.7;
  font-family: var(--font-mono);
  margin-bottom: 16px;
}

.quote-result-view__customer {
  margin-top: 16px;
  font-size: var(--fz-body);
  opacity: 0.8;
}

.quote-result-view__body {
  flex: 1;
  padding: 32px 24px;
  max-width: 600px;
  margin: -32px auto 0;
  position: relative;
  z-index: 1;
}

.quote-result-view__card {
  padding: 24px;
  margin-bottom: 20px;
}

.quote-result-view__section-title {
  font-size: var(--fz-h3);
  font-weight: var(--fw-semibold);
  margin: 0 0 16px;
  color: var(--text);
}

.quote-result-view__summary-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.quote-result-view__breakdown {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quote-result-view__breakdown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.quote-result-view__actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 24px;
}

.quote-result-view__footer {
  text-align: center;
  padding: 24px;
  margin-top: 32px;
  border-top: 1px solid var(--border);
}

.quote-result-view__footer p {
  margin: 0;
}

.mr-2 { margin-right: 8px; }

@media (max-width: 640px) {
  .quote-result-view__summary-grid,
  .quote-result-view__actions {
    grid-template-columns: 1fr;
  }
}
</style>
