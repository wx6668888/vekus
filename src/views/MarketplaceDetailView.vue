<template>
  <div class="detail-view">
    <Sidebar />
    <main class="detail-view__main">
      <button class="detail-view__back" @click="$router.back()">
        <ChevronLeft :size="20" /> 返回
      </button>

      <div v-if="loading" class="detail-view__loading">
        <div class="vk-skeleton-hero"></div>
      </div>

      <template v-else-if="item">
        <div class="detail-view__header">
          <Badge :variant="item.listingType === 'sell' ? 'info' : 'warn'">
            {{ item.listingType === 'sell' ? '出售' : '求购' }}
          </Badge>
          <h1 class="detail-view__title">{{ item.title }}</h1>
        </div>

        <div class="detail-view__content">
          <Card class="detail-view__price-card">
            <div class="detail-view__price-row">
              <PriceDisplay :value="item.price" size="display" color="accent" />
              <span class="detail-view__unit">/ {{ item.unit }}</span>
            </div>
            <div class="detail-view__meta-row">
              <span>{{ item.viewsCount + 1 }} 次浏览</span>
              <span>{{ item.createdAt }}</span>
            </div>
          </Card>

          <Card class="detail-view__card">
            <h3 class="detail-view__section-title">规格参数</h3>
            <div class="detail-view__spec-grid">
              <div><span class="vk-text-muted">分类</span><div>{{ item.category }}</div></div>
              <div v-if="item.material"><span class="vk-text-muted">材料</span><div>{{ item.material }}</div></div>
              <div v-if="item.thickness"><span class="vk-text-muted">厚度</span><div>{{ item.thickness }} mm</div></div>
              <div v-if="item.dimensions"><span class="vk-text-muted">尺寸</span><div>{{ item.dimensions }}</div></div>
              <div v-if="item.surface"><span class="vk-text-muted">表面处理</span><div>{{ item.surface }}</div></div>
              <div><span class="vk-text-muted">数量</span><div>{{ item.quantity }} {{ item.unit }}</div></div>
              <div v-if="item.location"><span class="vk-text-muted">所在地</span><div>{{ item.location }}</div></div>
            </div>
          </Card>

          <Card v-if="item.description" class="detail-view__card">
            <h3 class="detail-view__section-title">详细描述</h3>
            <p class="detail-view__description">{{ item.description }}</p>
          </Card>

          <div class="detail-view__actions">
            <Button variant="secondary" size="lg" block @click="contactSeller">
              <MessageSquare :size="18" class="mr-2" /> 联系卖家
            </Button>
            <Button v-if="item.contactPhone" variant="primary" size="lg" block @click="callSeller">
              <Phone :size="18" class="mr-2" /> {{ item.contactPhone }}
            </Button>
          </div>
        </div>
      </template>
    </main>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { ChevronLeft, MessageSquare, Phone } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import Card from '@/components/base/Card.vue';
import Button from '@/components/base/Button.vue';
import Badge from '@/components/base/Badge.vue';
import PriceDisplay from '@/components/data/PriceDisplay.vue';
import { getListing, type Listing } from '@/api/marketplace';
import { sendMessage } from '@/api/messages';

const route = useRoute();
const router = useRouter();
const item = ref<Listing | null>(null);
const loading = ref(true);

onMounted(async () => {
  try {
    item.value = await getListing(route.params.id as string);
  } catch { /* ignore */ }
  loading.value = false;
});

async function contactSeller() {
  if (!item.value) return;
  try {
    const msg = await sendMessage({
      senderId: 1,
      content: `你好，我对你发布的"${item.value.title}"很感兴趣，请问还在吗？`,
      messageType: 'text',
      type: 'user_chat',
      title: `${item.value.title}`,
      participants: [1, item.value.ownerUserId || 2],
    });
    const convId = msg.conversationId;
    router.push(`/messages/${convId}`);
  } catch {
    router.push('/messages');
  }
}

function callSeller() {
  if (item.value?.contactPhone) {
    window.open(`tel:${item.value.contactPhone}`);
  }
}
</script>

<style scoped>
.detail-view {
  display: grid;
  display: block;
  min-height: 100vh;
}

.detail-view__main {
  padding: 24px 32px 120px;
  max-width: 700px;
}

.detail-view__back {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 0;
  margin-bottom: 16px;
  border: none;
  background: none;
  color: var(--text-muted);
  font-size: var(--fz-body);
  cursor: pointer;
}

.detail-view__back:hover {
  color: var(--brand);
}

.detail-view__header {
  margin-bottom: 24px;
}

.detail-view__title {
  font-size: var(--fz-h1);
  font-weight: var(--fw-bold);
  color: var(--text);
  margin: 12px 0 0;
}

.detail-view__price-card {
  padding: 24px;
  margin-bottom: 16px;
  text-align: center;
}

.detail-view__price-row {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
  margin-bottom: 12px;
}

.detail-view__unit {
  font-size: var(--fz-body);
  color: var(--text-muted);
}

.detail-view__meta-row {
  display: flex;
  justify-content: center;
  gap: 20px;
  font-size: var(--fz-sm);
  color: var(--text-muted);
}

.detail-view__card {
  padding: 20px;
  margin-bottom: 16px;
}

.detail-view__section-title {
  font-size: var(--fz-h3);
  font-weight: var(--fw-semibold);
  margin: 0 0 14px;
  color: var(--text);
}

.detail-view__spec-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.detail-view__spec-grid > div > span {
  display: block;
  font-size: var(--fz-sm);
  margin-bottom: 4px;
}

.detail-view__spec-grid > div > div {
  font-size: var(--fz-body);
  color: var(--text);
  font-family: var(--font-mono);
}

.detail-view__description {
  font-size: var(--fz-body);
  color: var(--text);
  line-height: var(--lh-loose);
  margin: 0;
  white-space: pre-wrap;
}

.detail-view__actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 8px;
}

.mr-2 { margin-right: 8px; }

@media (max-width: 768px) {
  .detail-view {
    grid-template-columns: 1fr;
  }
  .detail-view__main {
    padding: 16px 16px 100px;
  }
  .detail-view__actions {
    grid-template-columns: 1fr;
  }
}
</style>
