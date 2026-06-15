<template>
  <div class="points-view">
    <Sidebar />
    <main class="points-view__main">
      <button class="points-view__back" @click="$router.back()"><ChevronLeft :size="20" /> 返回</button>
      <h1 class="points-view__title">点数流水</h1>
      <Card class="points-view__card">
        <div class="points-view__balance">当前余额：<strong>{{ balance }} 点</strong></div>
      </Card>

      <!-- Upload section -->
      <Card class="points-view__card">
        <h3 class="points-view__section-title">上传凭证</h3>
        <div class="points-view__upload">
          <div v-if="uploadPreview" class="points-view__preview-wrap">
            <img :src="uploadPreview" class="points-view__preview" />
            <button class="points-view__preview-remove" @click="removeImage">×</button>
          </div>
          <label class="points-view__upload-btn">
            <ImagePlus :size="20" />
            <span>{{ uploadPreview ? '更换图片' : '添加图片' }}</span>
            <input type="file" accept="image/*" style="display:none" @change="onFileChange" />
          </label>
          <p class="points-view__upload-hint">支持 JPG、PNG，最大 5MB</p>
        </div>
      </Card>

      <Card class="points-view__card">
        <h3 class="points-view__section-title">交易记录</h3>
        <div v-if="loading">加载中...</div>
        <div v-else-if="transactions.length === 0" class="points-view__empty">暂无交易记录</div>
        <div v-for="tx in transactions" :key="tx.id" class="points-view__tx">
          <div :class="['points-view__tx-icon', tx.type === 'charge' ? 'points-view__tx-icon--in' : 'points-view__tx-icon--out']">
            {{ tx.type === 'charge' ? '+' : '-' }}
          </div>
          <div class="points-view__tx-info">
            <div class="points-view__tx-desc">{{ tx.description }}</div>
            <div class="points-view__tx-time">{{ tx.createdAt }}</div>
            <div v-if="tx.imageUrl" class="points-view__tx-img" @click.stop="previewImage(tx.imageUrl)">
              <img :src="tx.imageUrl" class="points-view__tx-thumb" />
            </div>
          </div>
          <div :class="['points-view__tx-amount', tx.type === 'charge' ? 'points-view__tx-amount--in' : 'points-view__tx-amount--out']">
            {{ tx.type === 'charge' ? '+' : '' }}{{ tx.amount }} 点
          </div>
        </div>
      </Card>
    </main>
    <MobileNav />

    <!-- Image preview modal -->
    <div v-if="previewModalUrl" class="vk-overlay" @click="previewModalUrl = ''">
      <img :src="previewModalUrl" class="points-view__img-modal" @click.stop />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ChevronLeft, ImagePlus } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import { getTransactions, getPointsBalance, type PointsTransaction } from '@/api/payment';
import { api } from '@/api';

const transactions = ref<PointsTransaction[]>([]);
const balance = ref(0);
const loading = ref(true);
const uploadPreview = ref('');
const previewModalUrl = ref('');
const uploadFile = ref<File | null>(null);

onMounted(async () => {
  balance.value = await getPointsBalance(1);
  transactions.value = await getTransactions(1);
  loading.value = false;
});

function onFileChange(e: Event) {
  const target = e.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  if (file.size > 5 * 1024 * 1024) {
    alert('图片大小不能超过 5MB');
    return;
  }
  uploadFile.value = file;
  const reader = new FileReader();
  reader.onload = () => { uploadPreview.value = reader.result as string; };
  reader.readAsDataURL(file);
}

function removeImage() {
  uploadPreview.value = '';
  uploadFile.value = null;
}

function previewImage(url: string) {
  previewModalUrl.value = url;
}
</script>

<style scoped>
.points-view { display: block; min-height: 100vh; }
.points-view__main { padding: 24px 32px 120px; max-width: 720px; margin: 0 auto; }
.points-view__back { display: flex; align-items: center; gap: 4px; padding: 8px 0; margin-bottom: 8px; border: none; background: none; color: var(--text-muted); cursor: pointer; }
.points-view__title { font-size: var(--fz-h1); font-weight: var(--fw-bold); margin: 0 0 24px; }
.points-view__card { padding: 20px; margin-bottom: 16px; }
.points-view__balance { font-size: var(--fz-body); }
.points-view__balance strong { font-family: var(--font-mono); font-size: 24px; color: var(--brand); margin-left: 8px; }
.points-view__section-title { font-size: var(--fz-h3); font-weight: var(--fw-semibold); margin: 0 0 14px; }

/* Upload */
.points-view__upload { display: flex; flex-direction: column; align-items: center; gap: 12px; }
.points-view__preview-wrap { position: relative; max-width: 320px; }
.points-view__preview { width: 100%; border-radius: var(--r-input); border: 1px solid var(--border); }
.points-view__preview-remove { position: absolute; top: -8px; right: -8px; width: 28px; height: 28px; border-radius: 50%; background: var(--danger); color: white; border: none; font-size: 16px; cursor: pointer; display: grid; place-items: center; }
.points-view__upload-btn { display: flex; align-items: center; gap: 8px; padding: 12px 24px; border-radius: var(--r-input); border: 2px dashed var(--border); color: var(--text-muted); cursor: pointer; transition: all var(--duration-fast); font-size: var(--fz-body); }
.points-view__upload-btn:hover { border-color: var(--brand); color: var(--brand); }
.points-view__upload-hint { font-size: var(--fz-xs); color: var(--text-faint); margin: 0; }

/* Transactions */
.points-view__tx { display: flex; align-items: flex-start; gap: 12px; padding: 14px 0; border-bottom: 1px solid var(--border); }
.points-view__tx:last-child { border-bottom: none; }
.points-view__tx-icon { width: 36px; height: 36px; border-radius: 50%; display: grid; place-items: center; font-weight: var(--fw-bold); font-size: 16px; flex-shrink: 0; }
.points-view__tx-icon--in { background: var(--success-bg); color: var(--success); }
.points-view__tx-icon--out { background: var(--danger-bg); color: var(--danger); }
.points-view__tx-info { flex: 1; }
.points-view__tx-desc { font-size: var(--fz-body); color: var(--text); }
.points-view__tx-time { font-size: var(--fz-xs); color: var(--text-faint); margin-top: 2px; }
.points-view__tx-amount { font-family: var(--font-mono); font-weight: var(--fw-semibold); font-size: var(--fz-body); }
.points-view__tx-amount--in { color: var(--success); }
.points-view__tx-amount--out { color: var(--danger); }
.points-view__tx-img { margin-top: 6px; cursor: pointer; }
.points-view__tx-thumb { width: 80px; height: 60px; object-fit: cover; border-radius: var(--r-tag); border: 1px solid var(--border); }
.points-view__empty { text-align: center; padding: 32px; color: var(--text-muted); }

/* Image modal */
.vk-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.7); display: grid; place-items: center; z-index: 1000; }
.points-view__img-modal { max-width: 90vw; max-height: 90vh; border-radius: var(--r-modal); }

@media (max-width: 768px) {
  .points-view__main { padding: 16px 16px 100px; }
}
</style>
