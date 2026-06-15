<template>
  <div class="messages-view">
    <Sidebar />
    <main class="messages-view__main">
      <TopBar
        title="消息"
        description="系统通知、客服、交易沟通"
      />

      <div v-if="loading" class="messages-view__loading">
        <div class="vk-skeleton-row" v-for="i in 3" :key="i"></div>
      </div>

      <EmptyState
        v-else-if="conversations.length === 0"
        title="暂无消息"
        description="当有人联系你或有系统通知时，会在这里显示"
        icon="message"
      />

      <div v-else class="messages-view__list">
        <!-- Pinned: Customer Service -->
        <div
          v-for="conv in pinnedConversations"
          :key="'pin-' + conv.id"
          class="messages-view__item messages-view__item--pinned"
          @click="$router.push(`/messages/${conv.id}`)"
        >
          <div :class="['messages-view__avatar', `messages-view__avatar--${conv.type}`]">
            <component :is="getConvIcon(conv.type)" :size="20" />
          </div>
          <div class="messages-view__info">
            <div class="messages-view__info-top">
              <span class="messages-view__name">{{ conv.title || '聊天' }}
                <span class="messages-view__pinned-badge">客服</span>
              </span>
              <span class="messages-view__time">{{ formatTime(conv.lastMessageAt) }}</span>
            </div>
            <p class="messages-view__preview">{{ conv.lastMessage || '暂无消息' }}</p>
          </div>
          <ChevronRight :size="16" class="messages-view__arrow" />
        </div>
        <!-- Other conversations -->
        <div
          v-for="conv in normalConversations"
          :key="conv.id"
          class="messages-view__item"
          @click="$router.push(`/messages/${conv.id}`)"
        >
          <div :class="['messages-view__avatar', `messages-view__avatar--${conv.type}`]">
            <component :is="getConvIcon(conv.type)" :size="20" />
          </div>
          <div class="messages-view__info">
            <div class="messages-view__info-top">
              <span class="messages-view__name">{{ conv.title || '聊天' }}</span>
              <span class="messages-view__time">{{ formatTime(conv.lastMessageAt) }}</span>
            </div>
            <p class="messages-view__preview">{{ conv.lastMessage || '暂无消息' }}</p>
          </div>
          <ChevronRight :size="16" class="messages-view__arrow" />
        </div>
      </div>
    </main>
    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ChevronRight, MessageSquare, Headphones, Bell, ShoppingBag } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import TopBar from '@/components/layout/TopBar.vue';
import MobileNav from '@/components/layout/MobileNav.vue';
import EmptyState from '@/components/base/EmptyState.vue';
import { getConversations, type Conversation } from '@/api/messages';

const conversations = ref<Conversation[]>([]);
const loading = ref(true);

onMounted(async () => {
  conversations.value = await getConversations(1);
  loading.value = false;
});

const pinnedConversations = computed(() =>
  conversations.value.filter(c => c.type === 'customer_service' || c.type === 'system')
);

const normalConversations = computed(() =>
  conversations.value.filter(c => c.type !== 'customer_service' && c.type !== 'system')
);

function getConvIcon(type: string) {
  const icons: Record<string, any> = { system: Bell, customer_service: Headphones, order: ShoppingBag };
  return icons[type] || MessageSquare;
}

function formatTime(dateStr: string): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
  if (diff < 86400000) return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
  return `${date.getMonth() + 1}/${date.getDate()}`;
}
</script>

<style scoped>
.messages-view {
  display: grid;
  display: block;
  min-height: 100vh;
}

.messages-view__main {
  padding: 24px 32px 120px;
  max-width: 640px;
}

.messages-view__loading {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.vk-skeleton-row {
  height: 72px;
  background: var(--surface-sunken);
  border-radius: var(--r-input);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.messages-view__list {
  display: flex;
  flex-direction: column;
}

.messages-view__item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background var(--duration-fast);
}

.messages-view__item:hover {
  background: var(--surface-sunken);
}

.messages-view__avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.messages-view__avatar--system { background: var(--info-bg); color: var(--info); }
.messages-view__avatar--customer_service { background: var(--success-bg); color: var(--success); }
.messages-view__avatar--order { background: var(--warn-bg); color: var(--warn); }
.messages-view__avatar--user_chat { background: var(--brand-light); color: var(--brand); }

.messages-view__info {
  flex: 1;
  min-width: 0;
}

.messages-view__info-top {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 4px;
}

.messages-view__name {
  font-size: var(--fz-body);
  font-weight: var(--fw-semibold);
  color: var(--text);
}

.messages-view__time {
  font-size: var(--fz-xs);
  color: var(--text-faint);
  flex-shrink: 0;
  margin-left: 12px;
}

.messages-view__preview {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.messages-view__arrow {
  color: var(--text-faint);
  flex-shrink: 0;
}

.messages-view__item--pinned {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.04), rgba(139, 92, 246, 0.04));
  border: 1px solid rgba(99, 102, 241, 0.12);
  border-radius: var(--r-card);
  margin-bottom: 12px;
}

.messages-view__pinned-badge {
  display: inline-flex;
  margin-left: 6px;
  padding: 1px 6px;
  border-radius: 999px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 9px;
  font-weight: var(--fw-bold);
  vertical-align: middle;
}

@media (max-width: 768px) {
  .messages-view {
    grid-template-columns: 1fr;
    overflow-x: hidden;
  }
  .messages-view__main {
    padding: 16px 16px 100px;
    overflow-x: hidden;
    max-width: 100vw;
  }
  .messages-view__list {
    overflow-x: hidden;
  }
  .messages-view__item {
    overflow: hidden;
  }
}
</style>
