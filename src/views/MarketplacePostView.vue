<template>
  <div class="post-view">
    <Sidebar />
    <main class="post-view__main">
      <button class="post-view__back" @click="$router.back()">
        <ChevronLeft :size="20" /> 返回
      </button>

      <h1 class="post-view__title">{{ isEdit ? '编辑信息' : '发布交易信息' }}</h1>

      <Card class="post-view__card">
        <div class="post-view__form">
          <div class="post-view__type-toggle">
            <button
              :class="['post-view__type-btn', { 'post-view__type-btn--active': form.listingType === 'sell' }]"
              @click="form.listingType = 'sell'"
            >出售</button>
            <button
              :class="['post-view__type-btn', { 'post-view__type-btn--active': form.listingType === 'buy' }]"
              @click="form.listingType = 'buy'"
            >求购</button>
          </div>

          <Input v-model="form.title" label="标题" placeholder="例如：1.5mm 镀锌板余料出售" />

          <div class="post-view__select">
            <label class="vk-input__label">分类</label>
            <SelectMenu v-model="form.category" :options="categoryOptions" />
          </div>

          <div class="post-view__row">
            <Input v-model="form.material" label="材料" placeholder="如：镀锌板" />
            <Input v-model.number="form.thickness" type="number" label="厚度 (mm)" placeholder="1.5" />
          </div>

          <Input v-model="form.dimensions" label="尺寸规格" placeholder="如：2000×1000mm" />

          <div class="post-view__row">
            <Input v-model="form.surface" label="表面处理" placeholder="如：喷粉" />
            <div class="post-view__row-inner">
              <Input v-model.number="form.quantity" type="number" label="数量" placeholder="1" />
              <Input v-model="form.unit" label="单位" placeholder="件" />
            </div>
          </div>

          <div class="post-view__row">
            <Input v-model.number="form.price" type="number" label="单价 (¥)" placeholder="0.00" />
            <div class="post-view__select">
              <label class="vk-input__label">所在地</label>
              <CascadingLocation v-model="regionPath" placeholder="选择省市区" />
            </div>
          </div>

          <Input v-model="addressDetail" label="详细地址" placeholder="如：XX街道XX工业园XX号" />

          <Input v-model="form.contactPhone" label="联系电话" placeholder="选填" />

          <!-- Image upload -->
          <div class="post-view__image-section">
            <label class="vk-input__label">产品图片（最多 6 张）</label>
            <div class="post-view__image-grid">
              <div
                v-for="(img, i) in imagePreviews"
                :key="'img-' + i"
                class="post-view__image-item"
              >
                <img :src="img" class="post-view__image-thumb" />
                <button class="post-view__image-remove" @click="removeImage(i)">✕</button>
              </div>
              <label
                v-if="imagePreviews.length < 6"
                class="post-view__image-add"
              >
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  style="display:none"
                  @change="onImagesSelected"
                />
                <Plus :size="24" />
                <span>上传图片</span>
              </label>
            </div>
          </div>

          <div class="post-view__textarea-group">
            <label class="vk-input__label">详细描述</label>
            <textarea
              v-model="form.description"
              class="vk-input__field post-view__textarea"
              placeholder="描述材料规格、用途、交货方式等..."
              rows="5"
            ></textarea>
          </div>

          <!-- AI Smart Recognition -->
          <div class="post-view__ai-section">
            <div class="post-view__ai-header">
              <label class="vk-input__label">AI 智能识别（可选）</label>
              <span class="post-view__ai-badge">AI</span>
            </div>
            <p class="post-view__ai-desc">上传规格表、清单等文档，自动提取材料参数填充表单</p>
            <div class="post-view__ai-upload">
              <input
                ref="aiFileInput"
                type="file"
                accept=".pdf,.xlsx,.xls,.csv,.png,.jpg,.docx"
                style="display:none"
                @change="onAiFileSelect"
              />
              <Button variant="secondary" size="sm" :loading="aiRecognizing" @click="aiFileInput?.click()">
                <Upload :size="16" class="mr-2" />
                {{ aiRecognizing ? '识别中...' : aiFile ? aiFile.name : '上传文档/表格' }}
              </Button>
              <button v-if="aiFile" class="post-view__ai-clear" @click="aiFile = null; aiRecognized = false">✕</button>
            </div>
            <div v-if="aiRecognized" class="post-view__ai-result">
              <Badge variant="success" size="sm">✓ 已自动填充</Badge>
              <span class="post-view__ai-fields">材料、规格、数量等字段已从文档中提取</span>
            </div>
          </div>
        </div>
      </Card>

      <div class="post-view__actions">
        <Button variant="ghost" size="lg" @click="$router.back()">取消</Button>
        <Button variant="primary" size="lg" :loading="submitting" @click="handleSubmit">
          {{ isEdit ? '保存修改' : '发布' }}
        </Button>
      </div>
    </main>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ChevronLeft, Upload, Plus } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import Input from '@/components/base/Input.vue';
import Button from '@/components/base/Button.vue';
import Badge from '@/components/base/Badge.vue';
import SelectMenu from '@/components/base/SelectMenu.vue';
import CascadingLocation from '@/components/base/CascadingLocation.vue';
import { createListing, type CreateListingData } from '@/api/marketplace';
import { scanDrawing } from '@/api/quote';

const route = useRoute();
const router = useRouter();
const isEdit = ref(false);
const submitting = ref(false);
const aiFileInput = ref<HTMLInputElement | null>(null);
const aiFile = ref<File | null>(null);
const aiRecognizing = ref(false);
const aiRecognized = ref(false);
const imageFiles = ref<File[]>([]);
const imagePreviews = ref<string[]>([]);
const regionPath = ref('');
const addressDetail = ref('');

const form = reactive<CreateListingData>({
  ownerUserId: 1,
  title: '',
  listingType: 'sell',
  category: '板材',
  material: '',
  thickness: 0,
  dimensions: '',
  surface: '',
  quantity: 1,
  price: 0,
  unit: '件',
  description: '',
  images: [],
  location: '',
  contactPhone: '',
});

const categoryOptions = [
  { value: '板材', label: '板材' },
  { value: '型材', label: '型材' },
  { value: '余料', label: '余料' },
  { value: '设备', label: '设备' },
  { value: '加工服务', label: '加工服务' },
];

function onImagesSelected(e: Event) {
  const target = e.target as HTMLInputElement;
  const files = target.files;
  if (!files) return;
  for (let i = 0; i < files.length && imagePreviews.value.length < 6; i++) {
    const f = files[i];
    imageFiles.value.push(f);
    const reader = new FileReader();
    reader.onload = (ev) => {
      imagePreviews.value.push(ev.target?.result as string);
    };
    reader.readAsDataURL(f);
  }
  target.value = '';
}

function removeImage(index: number) {
  imageFiles.value.splice(index, 1);
  imagePreviews.value.splice(index, 1);
}

function onAiFileSelect(e: Event) {
  const target = e.target as HTMLInputElement;
  const files = target.files;
  if (files && files.length > 0) {
    aiFile.value = files[0];
    handleAiRecognize(files[0]);
  }
}

async function handleAiRecognize(f: File) {
  aiRecognizing.value = true;
  aiRecognized.value = false;
  try {
    const result = await scanDrawing(f);
    if (result.thickness && !form.thickness) form.thickness = result.thickness;
    if (result.expandLength && result.expandWidth && !form.dimensions) {
      form.dimensions = `${result.expandLength}×${result.expandWidth}mm`;
    }
    if (result.bendCount > 0) {
      form.description = (form.description ? form.description + '\n' : '') + `折弯数: ${result.bendCount}次`;
    }
    if (result.holes) {
      const h = result.holes;
      const holeDesc = [h.plain && `光孔${h.plain}个`, h.threaded && `螺纹孔${h.threaded}个`, h.counterbored && `沉孔${h.counterbored}个`].filter(Boolean).join('、');
      if (holeDesc) form.description = (form.description ? form.description + '\n' : '') + `孔位: ${holeDesc}`;
    }
    aiRecognized.value = true;
  } catch {
    alert('识别失败，请手动填写');
  } finally {
    aiRecognizing.value = false;
  }
}

async function handleSubmit() {
  if (!form.title) return;
  submitting.value = true;
  try {
    form.images = imagePreviews.value;
    form.location = [regionPath.value, addressDetail.value].filter(Boolean).join(' ');
    const result = await createListing(form);
    router.push(`/marketplace/${result.id}`);
  } catch {
    alert('发布失败，请重试');
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.post-view {
  display: block;
  min-height: 100vh;
}

.post-view__main {
  padding: 24px 32px 120px;
  max-width: 680px;
  margin: 0 auto;
}

.post-view__back {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 0;
  margin-bottom: 8px;
  border: none;
  background: none;
  color: var(--text-muted);
  font-size: var(--fz-body);
  cursor: pointer;
}

.post-view__back:hover { color: var(--brand); }

.post-view__title {
  font-size: var(--fz-h1);
  font-weight: var(--fw-bold);
  margin: 0 0 20px;
}

.post-view__card { padding: 24px; }

.post-view__form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.post-view__type-toggle {
  display: flex;
  gap: 8px;
}

.post-view__type-btn {
  flex: 1;
  padding: 10px;
  border-radius: var(--r-input);
  border: 2px solid var(--border);
  background: transparent;
  color: var(--text-muted);
  font-size: var(--fz-body);
  font-weight: var(--fw-semibold);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.post-view__type-btn--active {
  border-color: var(--brand);
  background: var(--brand-light);
  color: var(--brand);
}

.post-view__row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.post-view__row-inner {
  display: grid;
  grid-template-columns: 1fr 100px;
  gap: 12px;
}

.post-view__select {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* Image upload */
.post-view__image-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.post-view__image-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.post-view__image-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--border);
  background: var(--surface-sunken);
}

.post-view__image-thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.post-view__image-remove {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.55);
  color: #fff;
  font-size: 12px;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: background 0.15s;
}

.post-view__image-remove:hover { background: rgba(0,0,0,0.8); }

.post-view__image-add {
  aspect-ratio: 1;
  border-radius: 10px;
  border: 2px dashed var(--border);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: var(--text-muted);
  font-size: var(--fz-sm);
  cursor: pointer;
  transition: all 0.15s;
}

.post-view__image-add:hover {
  border-color: var(--brand);
  color: var(--brand);
  background: var(--brand-light);
}

/* Textarea */
.post-view__textarea-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.post-view__textarea {
  height: auto;
  padding: 14px;
  resize: vertical;
  font-family: inherit;
}

.post-view__actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

/* AI section */
.post-view__ai-section {
  padding: 16px;
  border-radius: var(--r-input);
  border: 1px dashed var(--border);
  background: var(--surface-sunken);
}

.post-view__ai-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.post-view__ai-badge {
  font-size: 10px;
  font-weight: var(--fw-bold);
  padding: 2px 6px;
  border-radius: 4px;
  background: linear-gradient(135deg, var(--brand), #6366f1);
  color: white;
}

.post-view__ai-desc {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  margin: 0 0 12px;
}

.post-view__ai-upload {
  display: flex;
  align-items: center;
  gap: 8px;
}

.post-view__ai-clear {
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 16px;
  padding: 4px;
}

.post-view__ai-result {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding: 10px;
  background: var(--success-bg);
  border-radius: var(--r-tag);
}

.post-view__ai-fields {
  font-size: var(--fz-sm);
  color: var(--success);
}

.mr-2 { margin-right: 8px; }

@media (max-width: 768px) {
  .post-view__main { padding: 16px 16px 100px; }
  .post-view__row { grid-template-columns: 1fr; }
  .post-view__image-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
