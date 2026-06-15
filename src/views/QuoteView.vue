<template>
  <div class="quote-view">
    <Sidebar />
    <main class="quote-view__main">
      <!-- Step indicator -->
      <div class="quote-view__steps">
        <div
          v-for="(s, i) in steps"
          :key="i"
          :class="['quote-view__step', {
            'quote-view__step--active': currentStep === i,
            'quote-view__step--done': currentStep > i
          }]"
        >
          <div class="quote-view__step-num">{{ currentStep > i ? '✓' : i + 1 }}</div>
          <span class="quote-view__step-label">{{ s }}</span>
          <div v-if="i < steps.length - 1" class="quote-view__step-line"></div>
        </div>
      </div>

      <!-- Step 1: Basic Info -->
      <div v-if="currentStep === 0" class="quote-view__panel">
        <Card class="quote-form__section">
          <h3 class="quote-form__section-title">基础信息</h3>
          <p class="quote-form__section-desc">填写客户和材料的基本参数</p>
          <div class="quote-form__grid">
            <CustomerPicker
              @update:customer-name="draft.basics.customerName = $event"
              @update:customer-id="draft.basics.customerId = $event"
            />
            <Input v-model.number="draft.basics.quantity" type="number" label="数量" placeholder="500" />
            <div class="quote-form__select">
              <label class="vk-input__label">材料</label>
              <SelectMenu v-model="draft.basics.material" :options="materialOptions" />
            </div>
            <Input v-model.number="draft.basics.thickness" type="number" step="0.1" label="厚度 (mm)" placeholder="1.5" />
            <div class="quote-form__select">
              <label class="vk-input__label">表面处理</label>
              <SelectMenu v-model="draft.basics.surface" :options="surfaceOptions" />
            </div>
            <Input v-model.number="draft.basics.deliveryDays" type="number" label="交期 (天)" placeholder="7" />
          </div>
          <Input :model-value="draft.basics.note || ''" label="备注" placeholder="特殊要求说明..."
            @update:model-value="(v: string | number) => draft.basics.note = String(v)" />
          <div class="quote-form__actions">
            <Button variant="primary" size="lg" @click="currentStep = 1">下一步：上传图纸</Button>
          </div>
        </Card>
      </div>

      <!-- Step 2: Upload + AI Recognition -->
      <div v-if="currentStep === 1" class="quote-view__panel">
        <Card class="quote-form__section">
          <h3 class="quote-form__section-title">上传图纸</h3>
          <p class="quote-form__section-desc">支持 DWG / DXF / STEP / PDF / 图片，最大 10MB</p>
          <FileDropzone :file="file" :recognizing="recognizing" @update:file="file = $event" @recognize="handleRecognize" />
        </Card>

        <Card v-if="showRecognition" class="quote-form__section">
          <h3 class="quote-form__section-title">
            AI 识别结果
            <Badge v-if="recognizing" variant="info" size="sm">识别中...</Badge>
            <Badge v-else variant="success" size="sm">识别完成</Badge>
          </h3>
          <div v-if="recognizing" class="quote-view__scanning">
            <div class="quote-view__scan-animation">
              <div class="quote-view__scan-ring"></div>
              <Loader :size="32" class="quote-view__scan-icon" />
            </div>
            <p class="quote-view__scan-text">AI 正在分析图纸...</p>
            <p class="quote-view__scan-sub">识别板厚、尺寸、折弯数、孔数等参数</p>
          </div>
          <RecognizedFieldList
            v-else
            :recognized="draft.recognized"
            :overrides="draft.manualOverrides"
            @update:field="handleFieldUpdate"
          />
        </Card>

        <div class="quote-form__actions">
          <Button variant="ghost" size="lg" @click="currentStep = 0">上一步</Button>
          <Button variant="primary" size="lg" @click="currentStep = 2" :disabled="recognizing">
            {{ recognizing ? '请等待识别完成...' : '下一步：确认报价' }}
          </Button>
        </div>
      </div>

      <!-- Step 3: Review & Confirm -->
      <div v-if="currentStep === 2" class="quote-view__panel">
        <Card class="quote-form__section">
          <h3 class="quote-form__section-title">系数与调整</h3>
          <p class="quote-form__section-desc">调整税率、折扣、利润率等系数</p>
          <div class="quote-form__grid">
            <Input v-model.number="draft.coefficients.tax" type="number" step="0.01" label="税管费系数" />
            <Input v-model.number="draft.coefficients.discount" type="number" step="0.01" label="折扣系数" />
            <Input v-model.number="draft.coefficients.packaging" type="number" label="包装费 (¥)" />
            <Input v-model.number="draft.coefficients.profitRate" type="number" step="0.01" label="利润率" />
          </div>
        </Card>

        <!-- System pricing parameters reference -->
        <Card class="quote-form__section">
          <h3 class="quote-form__section-title">系统报价参数</h3>
          <p class="quote-form__section-desc">以下参数来自系统设置，影响最终报价计算</p>
          <div v-if="systemParams.length === 0" class="quote-view__params-empty">
            加载中...
          </div>
          <div v-else class="quote-view__params-grid">
            <div v-for="cat in paramCategories" :key="cat.id" class="quote-view__params-cat">
              <div class="quote-view__params-cat-name">{{ cat.label }}</div>
              <div class="quote-view__params-items">
                <div v-for="p in getParamsByCategory(cat.id)" :key="p.id" class="quote-view__params-item">
                  <span class="quote-view__params-item-name">{{ p.name }}</span>
                  <span class="quote-view__params-item-value">{{ p.value }} {{ p.unit }}</span>
                </div>
                <div v-if="getParamsByCategory(cat.id).length === 0" class="quote-view__params-none">暂无</div>
              </div>
            </div>
          </div>
        </Card>

        <Card class="quote-form__section">
          <h3 class="quote-form__section-title">报价确认</h3>
          <div class="quote-view__summary">
            <div class="quote-view__summary-row"><span>客户</span><strong>{{ draft.basics.customerName || '未填写' }}</strong></div>
            <div class="quote-view__summary-row"><span>材料</span><strong>{{ draft.basics.material }} / {{ draft.basics.thickness }}mm</strong></div>
            <div class="quote-view__summary-row"><span>数量</span><strong>{{ draft.basics.quantity }} 件</strong></div>
            <div class="quote-view__summary-row"><span>表面处理</span><strong>{{ draft.basics.surface }}</strong></div>
            <div class="quote-view__summary-row"><span>交期</span><strong>{{ draft.basics.deliveryDays }} 天</strong></div>
          </div>

          <div class="quote-view__total">
            <div class="quote-view__total-label">报价总价</div>
            <PriceDisplay :value="calculated.totalPrice" size="display" color="accent" />
            <div class="quote-view__total-sub">
              单价 ¥{{ calculated.unitPrice }} · 利润率 {{ calculated.profitMargin }}%
            </div>
          </div>

          <!-- Breakdown -->
          <div class="quote-view__breakdown-mini">
            <div v-for="(value, key) in calculated.breakdown" :key="key" class="quote-view__breakdown-row">
              <span>{{ breakdownLabels[key as keyof typeof breakdownLabels] }}</span>
              <PriceDisplay :value="value" size="sm" />
            </div>
          </div>

          <div v-if="calculated.warnings.length" class="quote-view__warnings">
            <AlertTriangle :size="14" />
            <span v-for="w in calculated.warnings" :key="w">{{ w }}</span>
          </div>
        </Card>

        <div class="quote-form__actions">
          <Button variant="ghost" size="lg" @click="currentStep = 1">上一步</Button>
          <Button variant="ghost" size="lg" @click="saveDraft">保存草稿</Button>
          <Button variant="primary" size="lg" @click="sendQuote">发送报价</Button>
        </div>
      </div>

      <!-- Mobile floating bar (shown only when price available) -->
      <div v-if="calculated.totalPrice > 0" class="quote-view__mobile-bar">
        <div class="quote-view__mobile-bar-price">
          <span class="quote-view__mobile-bar-label">总价</span>
          <PriceDisplay :value="calculated.totalPrice" size="md" />
        </div>
        <Button variant="primary" size="lg" class="quote-view__mobile-bar-btn" @click="currentStep = 2; sendQuote()">发送报价</Button>
      </div>
    </main>

    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { AlertTriangle, Loader } from 'lucide-vue-next';
import { useQuoteDraftStore } from '@/stores/quoteDraft';
import { calculateQuote, toast } from '@/services';
import { scanDrawing, saveQuote, getQuote, updateQuote } from '@/api/quote';
import Sidebar from '@/components/layout/Sidebar.vue';
import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import Input from '@/components/base/Input.vue';
import Button from '@/components/base/Button.vue';
import Badge from '@/components/base/Badge.vue';
import SelectMenu from '@/components/base/SelectMenu.vue';
import PriceDisplay from '@/components/data/PriceDisplay.vue';
import { FileDropzone, RecognizedFieldList } from '@/components/quote';
import CustomerPicker from '@/components/quote/CustomerPicker.vue';

const route = useRoute();
const router = useRouter();
const draftStore = useQuoteDraftStore();

const currentStep = ref(0);
const showRecognition = ref(false);
const file = ref<File | null>(null);
const recognizing = ref(false);
const lastSaved = ref<number | null>(null);
const savedId = ref<string | null>(null);

const steps = ['基础信息', '上传识图', '确认报价'];

const materialOptions = [
  { value: '镀锌板', label: '镀锌板' },
  { value: '冷轧板', label: '冷轧板' },
  { value: '铝板', label: '铝板' },
  { value: '不锈钢', label: '不锈钢' },
];

const surfaceOptions = [
  { value: '喷粉', label: '喷粉' },
  { value: '喷漆', label: '喷漆' },
  { value: '电镀', label: '电镀' },
  { value: '钝化', label: '钝化' },
  { value: '无', label: '无' },
];

const breakdownLabels: Record<string, string> = {
  material: '材料费', cutting: '切割费', bending: '折弯费',
  welding: '焊接费', surface: '表面处理', admin: '管理费', profit: '利润',
};

const draft = computed({
  get: () => draftStore.draft || draftStore.$state.draft!,
  set: (v) => draftStore.setDraft(v),
});

const isEdit = computed(() => !!route.params.id);
const quoteNo = computed(() => {
  if (isEdit.value) return `QT-${route.params.id}`;
  return (draftStore.draft as any)?._quoteNo || `QT-${Date.now().toString(36).toUpperCase()}`;
});

const calculated = computed(() => calculateQuote(draft.value));

const lastSavedText = computed(() => {
  if (!lastSaved.value) return '';
  const diff = Math.floor((Date.now() - lastSaved.value) / 60000);
  return diff < 1 ? '刚刚' : diff < 60 ? `${diff} 分钟前` : `${Math.floor(diff / 60)} 小时前`;
});

function showToast(msg: string) { toast.show(msg, 'success'); }

async function handleRecognize(f: File) {
  recognizing.value = true;
  showRecognition.value = true;
  try {
    const result = await scanDrawing(f);
    draftStore.updateRecognized(result);
    showToast('AI 识别完成');
  } catch {
    showToast('图纸识别失败，请手动输入参数');
  } finally {
    recognizing.value = false;
  }
}

function handleFieldUpdate(key: string, value: any) {
  if (key === 'holes') {
    draft.value.manualOverrides = {
      ...draft.value.manualOverrides,
      holes: { ...((draft.value.manualOverrides as any).holes || {}), ...value },
    };
  } else {
    (draft.value.manualOverrides as any)[key] = value;
  }
}

async function saveDraft() {
  try {
    if (isEdit.value && savedId.value) {
      await updateQuote(savedId.value, draft.value);
    } else {
      const result = await saveQuote(draft.value);
      savedId.value = result.id;
    }
    lastSaved.value = Date.now();
    showToast('草稿已保存');
  } catch { showToast('保存失败，请重试'); }
}

async function sendQuote() {
  try {
    let id = savedId.value;
    if (!id) {
      const result = await saveQuote(draft.value);
      id = result.id;
    } else if (isEdit.value) {
      await updateQuote(id, draft.value);
    }
    router.push(`/quote/result/${id}`);
  } catch { showToast('发送失败，请重试'); }
}

// System pricing params
interface SystemParam { id: number; category: string; name: string; value: string; unit: string; enabled: number; }
const systemParams = ref<SystemParam[]>([]);
const paramCategories = [
  { id: 'material', label: '材料单价' },
  { id: 'surface', label: '表面处理' },
  { id: 'weld', label: '焊接' },
  { id: 'bend', label: '折弯' },
  { id: 'hole', label: '孔类' },
  { id: 'coefficient', label: '系数' },
];
function getParamsByCategory(cat: string) {
  return systemParams.value.filter(p => p.category === cat && p.enabled === 1);
}

async function fetchSystemParams() {
  const result = await api.get<SystemParam[]>('/settings');
  if (result.data) systemParams.value = result.data;
}

onMounted(async () => {
  fetchSystemParams();
  if (isEdit.value) {
    try {
      const quote = await getQuote(route.params.id as string);
      savedId.value = quote.id;
      draftStore.setDraft({
        basics: {
          material: quote.material || '镀锌板', thickness: quote.thickness || 1.5,
          quantity: quote.quantity || 100, surface: quote.surface || '喷粉',
          customerName: quote.customerName || '', deliveryDays: quote.deliveryDays || 7,
          note: quote.note || '',
        },
        recognized: quote.recognized || {
          thickness: 1.5, expandLength: 420, expandWidth: 280,
          cutLength: 2140, bendCount: 6, paintArea: 0.32,
          weldPoints: 14, weldLength: 0,
          holes: { plain: 8, threaded: 4, counterbored: 2 },
        },
        manualOverrides: quote.manualOverrides || {},
        coefficients: quote.coefficients || { tax: 1.06, discount: 0.95, packaging: 80, profitRate: 0.28 },
      });
      currentStep.value = 2; // Jump to review for edits
    } catch { showToast('加载报价失败'); }
  }
});
</script>

<style scoped>
.quote-view {
  display: grid;
  display: block;
  min-height: 100vh;
}

.quote-view__main {
  padding: 24px 32px 120px;
  overflow-y: auto;
  max-width: 720px;
  margin: 0 auto;
}

/* Step indicator */
.quote-view__steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  margin-bottom: 32px;
  padding: 0 24px;
}

.quote-view__step {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--fz-sm);
  color: var(--text-muted);
}

.quote-view__step-num {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 12px;
  font-weight: var(--fw-bold);
  background: var(--surface-sunken);
  color: var(--text-muted);
  flex-shrink: 0;
}

.quote-view__step--active .quote-view__step-num {
  background: var(--brand);
  color: white;
}

.quote-view__step--done .quote-view__step-num {
  background: var(--success);
  color: white;
}

.quote-view__step--active .quote-view__step-label {
  color: var(--text);
  font-weight: var(--fw-semibold);
}

.quote-view__step--done .quote-view__step-label {
  color: var(--success);
}

.quote-view__step-line {
  width: 40px;
  height: 2px;
  background: var(--border);
  margin: 0 12px;
  flex-shrink: 0;
}

.quote-view__step--done + .quote-view__step-line,
.quote-view__step--done .quote-view__step-line {
  background: var(--success);
}

/* Panel */
.quote-view__panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.quote-form__section {
  padding: 24px;
}

.quote-form__section-title {
  font-size: var(--fz-h3);
  font-weight: var(--fw-semibold);
  color: var(--text);
  margin: 0 0 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.quote-form__section-desc {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  margin: 0 0 20px;
}

.quote-form__grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.quote-form__select {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.quote-form__select select {
  height: 48px;
  padding: 0 14px;
  border-radius: var(--r-input);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: var(--fz-body);
  cursor: pointer;
}

.quote-form__actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}

/* Scanning animation */
.quote-view__scanning {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  text-align: center;
}

.quote-view__scan-animation {
  position: relative;
  width: 80px;
  height: 80px;
  display: grid;
  place-items: center;
  margin-bottom: 20px;
}

.quote-view__scan-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 3px solid var(--border);
  border-top-color: var(--brand);
  animation: spin 1s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.quote-view__scan-icon {
  color: var(--brand);
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.quote-view__scan-text {
  font-size: var(--fz-h3);
  font-weight: var(--fw-semibold);
  color: var(--text);
  margin: 0 0 8px;
}

.quote-view__scan-sub {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  margin: 0;
}

/* Summary */
.quote-view__summary {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px;
  background: var(--surface-sunken);
  border-radius: var(--r-input);
  margin-bottom: 20px;
}

.quote-view__summary-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--fz-body);
}

.quote-view__summary-row span { color: var(--text-muted); }
.quote-view__summary-row strong { color: var(--text); }

.quote-view__total {
  text-align: center;
  padding: 20px 0;
  margin-bottom: 16px;
}

.quote-view__total-label {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  margin-bottom: 8px;
}

.quote-view__total-sub {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  margin-top: 8px;
}

.quote-view__breakdown-mini {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 16px;
  background: var(--surface-sunken);
  border-radius: var(--r-input);
}

.quote-view__breakdown-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--fz-body);
}

.quote-view__breakdown-row span { color: var(--text-muted); }

/* System params display */
.quote-view__params-empty {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  text-align: center;
  padding: 20px;
}

.quote-view__params-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.quote-view__params-cat {
  background: var(--surface-sunken);
  border-radius: var(--r-input);
  padding: 12px;
}

.quote-view__params-cat-name {
  font-size: var(--fz-xs);
  font-weight: var(--fw-semibold);
  color: var(--brand);
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}

.quote-view__params-items {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.quote-view__params-item {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 8px;
  font-size: var(--fz-sm);
}

.quote-view__params-item-name {
  color: var(--text-muted);
}

.quote-view__params-item-value {
  font-family: var(--font-mono);
  font-weight: var(--fw-semibold);
  color: var(--text);
}

.quote-view__params-none {
  font-size: var(--fz-xs);
  color: var(--text-faint);
}

.quote-view__warnings {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px;
  background: var(--warn-bg);
  border-radius: var(--r-input);
  color: var(--warn);
  font-size: var(--fz-sm);
}

/* Mobile bar */
.quote-view__mobile-bar {
  display: none;
}

@media (max-width: 768px) {
  .quote-view {
    grid-template-columns: 1fr;
  }

  .quote-view__main {
    padding: 16px 16px 140px;
    max-width: 100%;
  }

  .quote-view__steps {
    padding: 0 8px;
    gap: 4px;
    margin-bottom: 20px;
  }

  .quote-view__step-label {
    display: none;
  }

  .quote-view__step-line {
    width: 24px;
    margin: 0 6px;
  }

  .quote-form__grid {
    grid-template-columns: 1fr;
  }

  .quote-form__actions {
    flex-wrap: wrap;
    position: sticky;
    bottom: 0;
    padding: 12px 0;
    background: var(--bg);
  }

  .quote-view__mobile-bar {
    display: flex;
    position: fixed;
    bottom: 76px;
    left: 12px;
    right: 12px;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 20px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
    z-index: 50;
  }

  .quote-view__mobile-bar-price {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .quote-view__mobile-bar-label {
    font-size: 11px;
    color: var(--text-muted);
  }

  .quote-view__mobile-bar-btn {
    flex-shrink: 0;
  }
}
</style>
