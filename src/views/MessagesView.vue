<template>
  <div class="msg-page">
    <!-- Left: Conversation List -->
    <aside class="msg-page__list">
      <div class="msg-page__list-header">
        <h2>消息</h2>
      </div>

      <div v-if="loading" class="msg-page__loading">
        <div class="vk-skeleton-row" v-for="i in 3" :key="i"></div>
      </div>

      <EmptyState
        v-else-if="conversations.length === 0"
        title="暂无消息"
        description="当有人联系你或有系统通知时会显示"
        icon="message"
      />

      <div v-else class="msg-page__conv-list">
        <div
          v-for="conv in sortedConversations"
          :key="conv.id"
          :class="['msg-page__conv-item', { active: activeConv?.id === conv.id }]"
          @click="selectConv(conv)"
        >
          <div :class="['msg-page__avatar', `msg-page__avatar--${conv.type}`]">
            <component :is="getConvIcon(conv.type)" :size="20" />
          </div>
          <div class="msg-page__conv-info">
            <div class="msg-page__conv-top">
              <span class="msg-page__conv-name">
                {{ conv.title || '聊天' }}
                <span v-if="conv.type==='customer_service'" class="msg-page__badge">客服</span>
              </span>
              <span class="msg-page__conv-time">{{ formatTime(conv.lastMessageAt) }}</span>
            </div>
            <p class="msg-page__conv-preview">{{ conv.lastMessage || '暂无消息' }}</p>
          </div>
        </div>
      </div>
    </aside>

    <!-- Right: Chat Area -->
    <main class="msg-page__chat">
      <!-- No conversation selected -->
      <div v-if="!activeConv" class="msg-page__empty">
        <MessageCircle :size="48" stroke-width="1.5" class="msg-page__empty-icon" />
        <p class="msg-page__empty-text">选择一条消息开始聊天</p>
      </div>

      <!-- Active chat -->
      <template v-else>
        <!-- Chat top bar -->
        <div class="msg-page__chat-top">
          <div class="msg-page__chat-top-left">
            <span class="msg-page__chat-title">{{ activeConv.title || '聊天' }}</span>
            <span v-if="activeConv.type==='customer_service'" class="msg-page__ai-badge">
              <Sparkles :size="12" /> AI客服
            </span>
          </div>
          <!-- Product info card (if present) -->
          <div v-if="productInfo" class="msg-page__product-card">
            <div class="msg-page__product-img" v-if="productInfo.image">
              <img :src="productInfo.image" :alt="productInfo.title" />
            </div>
            <div class="msg-page__product-detail">
              <span class="msg-page__product-title">{{ productInfo.title }}</span>
              <span class="msg-page__product-price">¥{{ productInfo.price }}</span>
            </div>
          </div>
        </div>

        <!-- Messages -->
        <div class="msg-page__chat-body" ref="msgContainer">
          <div v-if="chatLoading" class="msg-page__chat-loading">加载中...</div>

          <div v-if="aiThinking" class="msg-bubble msg-bubble--ai">
            <div class="msg-thinking">
              <span class="msg-thinking__ring"></span>
              <span>AI 正在思考...</span>
            </div>
          </div>

          <div
            v-for="msg in messages"
            :key="msg.id"
            :class="['msg-bubble', {
              'msg-bubble--mine': msg.senderId === myId,
              'msg-bubble--system': msg.messageType === 'system'
            }]"
          >
            <div v-if="msg.messageType === 'system'" class="msg-system">{{ msg.content }}</div>
            <template v-else>
              <div v-if="msg.messageType === 'image'" class="msg-bubble__img-wrap">
                <img :src="getImageSrc(msg.content)" class="msg-bubble__img" @click="previewImage = getImageSrc(msg.content)" />
              </div>
              <div v-else class="msg-bubble__text">{{ msg.content }}</div>
              <div class="msg-bubble__time">{{ formatTime(msg.createdAt) }}</div>
            </template>
          </div>
        </div>

        <!-- Input -->
        <div class="msg-page__chat-input">
          <ChatInput
            placeholder="输入消息... Enter 发送"
            accept="image/*,.pdf,.xlsx,.docx"
            :max-file-size="8"
            @submit="onSend"
          />
        </div>
      </template>
    </main>

    <!-- Image preview overlay -->
    <teleport to="body">
      <div v-if="previewImage" class="msg-preview-overlay" @click="previewImage = ''">
        <img :src="previewImage" class="msg-preview-img" />
      </div>
    </teleport>

    <MobileNav />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { MessageCircle, MessageSquare, Headphones, Bell, ShoppingBag, Sparkles } from 'lucide-vue-next';
import MobileNav from '@/components/layout/MobileNav.vue';
import EmptyState from '@/components/base/EmptyState.vue';
import ChatInput from '@/components/chat/ChatInput.vue';
import { getConversations, getMessages, sendMessage, type Conversation, type ChatMessage } from '@/api/messages';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const auth = useAuthStore();

const conversations = ref<Conversation[]>([]);
const loading = ref(true);
const activeConv = ref<Conversation | null>(null);
const messages = ref<ChatMessage[]>([]);
const chatLoading = ref(false);
const aiThinking = ref(false);
const msgContainer = ref<HTMLDivElement | null>(null);
const previewImage = ref('');
const myId = ref(1);

// Sort: customer_service + system always on top
const sortedConversations = computed(() => {
  const pinned: Conversation[] = [];
  const normal: Conversation[] = [];
  for (const c of conversations.value) {
    if (c.type === 'customer_service' || c.type === 'system') {
      pinned.push(c);
    } else {
      normal.push(c);
    }
  }
  return [...pinned, ...normal];
});

// Product info from marketplace "contact seller"
const productInfo = ref<{ title: string; price: number; image?: string; listingId?: string } | null>(null);

onMounted(async () => {
  conversations.value = await getConversations(1);
  loading.value = false;

  // Check URL params for pre-selected conversation or product
  const convId = route.query.conv as string;
  const productTitle = route.query.productTitle as string;
  const productPrice = route.query.productPrice as string;
  const productImage = route.query.productImage as string;
  const listingId = route.query.listingId as string;

  if (productTitle) {
    productInfo.value = {
      title: productTitle,
      price: Number(productPrice) || 0,
      image: productImage || '',
      listingId: listingId || '',
    };
  }

  if (convId) {
    const conv = conversations.value.find(c => c.id === convId || String(c.id) === convId);
    if (conv) {
      selectConv(conv);
    }
  }
});

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

function getImageSrc(content: string): string {
  if (!content) return '';
  try { const d = JSON.parse(content); return d.url || d.src || content; } catch { return content; }
}

async function selectConv(conv: Conversation) {
  activeConv.value = conv;
  chatLoading.value = true;
  try {
    messages.value = await getMessages(conv.id);
    await nextTick();
    scrollBottom();
  } catch { messages.value = []; }
  finally { chatLoading.value = false; }
}

async function onSend(data: { text?: string; file?: File }) {
  if (!activeConv.value) return;
  try {
    const msg = await sendMessage(activeConv.value.id, {
      content: data.text || '',
      file: data.file,
      senderId: myId.value,
    });
    if (msg) {
      messages.value.push(msg);
      await nextTick();
      scrollBottom();
    }
    // Simulate AI reply for customer service
    if (activeConv.value.type === 'customer_service' && data.text) {
      aiThinking.value = true;
      await nextTick();
      scrollBottom();
      await new Promise(r => setTimeout(r, 1200));
      aiThinking.value = false;
      const reply: ChatMessage = {
        id: Date.now(),
        conversationId: activeConv.value.id,
        senderId: 0,
        content: `收到你的消息："${data.text}"。我是 Vekus AI 客服，目前可以帮你查询库存、订单状态、报价参数等。如需人工服务，请在工作时间联系。`,
        messageType: 'text',
        createdAt: new Date().toISOString(),
      };
      messages.value.push(reply);
      await nextTick();
      scrollBottom();
    }
  } catch { /* silent */ }
}

function scrollBottom() {
  const el = msgContainer.value;
  if (el) el.scrollTop = el.scrollHeight;
}
</script>

<style scoped>
.msg-page {
  display: flex;
  height: calc(100vh - 56px);
  background: #f8fafc;
}

/* ===== Left List ===== */
.msg-page__list {
  width: 340px;
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.msg-page__list-header {
  padding: 20px 20px 12px;
  border-bottom: 1px solid #f1f5f9;
}
.msg-page__list-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
}
.msg-page__loading {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.vk-skeleton-row {
  height: 64px;
  background: #f1f5f9;
  border-radius: 12px;
  animation: pulse 1.5s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }

.msg-page__conv-list {
  flex: 1;
  overflow-y: auto;
}
.msg-page__conv-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 20px;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid #f8fafc;
}
.msg-page__conv-item:hover { background: #f8fafc; }
.msg-page__conv-item.active { background: #eff6ff; border-left: 3px solid #3b82f6; padding-left: 17px; }

.msg-page__avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}
.msg-page__avatar--system { background: #dbeafe; color: #2563eb; }
.msg-page__avatar--customer_service { background: #dcfce7; color: #16a34a; }
.msg-page__avatar--order { background: #fef3c7; color: #ca8a04; }
.msg-page__avatar--user_chat { background: #ede9fe; color: #7c3aed; }

.msg-page__conv-info { flex: 1; min-width: 0; }
.msg-page__conv-top { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px; }
.msg-page__conv-name { font-size: 14px; font-weight: 600; color: #0f172a; }
.msg-page__badge {
  display: inline-block;
  margin-left: 6px;
  padding: 1px 6px;
  border-radius: 100px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 9px;
  font-weight: 700;
  vertical-align: middle;
}
.msg-page__conv-time { font-size: 11px; color: #94a3b8; flex-shrink: 0; margin-left: 8px; }
.msg-page__conv-preview {
  font-size: 12px;
  color: #94a3b8;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ===== Right Chat ===== */
.msg-page__chat {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #fff;
}
.msg-page__empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #cbd5e1;
}
.msg-page__empty-icon { margin-bottom: 16px; }
.msg-page__empty-text { font-size: 15px; color: #94a3b8; margin: 0; }

.msg-page__chat-top {
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}
.msg-page__chat-top-left { display: flex; align-items: center; gap: 8px; }
.msg-page__chat-title { font-size: 16px; font-weight: 600; color: #0f172a; }
.msg-page__ai-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 100px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-size: 10px;
  font-weight: 600;
}

/* Product card in chat */
.msg-page__product-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  background: #f8fafc;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  max-width: 280px;
}
.msg-page__product-img {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: #e2e8f0;
}
.msg-page__product-img img { width: 100%; height: 100%; object-fit: cover; }
.msg-page__product-detail { display: flex; flex-direction: column; min-width: 0; }
.msg-page__product-title { font-size: 12px; color: #0f172a; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.msg-page__product-price { font-size: 14px; color: #dc2626; font-weight: 700; }

/* Messages body */
.msg-page__chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.msg-page__chat-loading { text-align: center; color: #94a3b8; font-size: 13px; padding: 40px; }

/* Bubbles */
.msg-bubble { max-width: 70%; display: flex; flex-direction: column; }
.msg-bubble--mine { align-self: flex-end; }
.msg-bubble--system { align-self: center; max-width: 90%; }
.msg-bubble--ai { align-self: flex-start; }

.msg-bubble__text {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.5;
  color: #0f172a;
  background: #f1f5f9;
  white-space: pre-wrap;
  word-break: break-word;
}
.msg-bubble--mine .msg-bubble__text { background: #3b82f6; color: #fff; }
.msg-bubble__time { font-size: 10px; color: #94a3b8; margin-top: 4px; padding: 0 4px; }
.msg-bubble--mine .msg-bubble__time { text-align: right; }

.msg-bubble__img-wrap { max-width: 240px; }
.msg-bubble__img {
  width: 100%;
  border-radius: 12px;
  cursor: pointer;
}
.msg-system {
  font-size: 12px;
  color: #94a3b8;
  text-align: center;
  padding: 6px 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.msg-thinking {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #f1f5f9;
  border-radius: 18px;
  font-size: 13px;
  color: #64748b;
}
.msg-thinking__ring {
  width: 16px; height: 16px;
  border: 2px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to{transform:rotate(360deg)} }

/* Input */
.msg-page__chat-input { padding: 12px 20px 16px; border-top: 1px solid #f1f5f9; flex-shrink: 0; }

/* Image preview */
.msg-preview-overlay {
  position: fixed; inset: 0; z-index: 10000;
  background: rgba(0,0,0,0.85); display: flex;
  align-items: center; justify-content: center; cursor: pointer;
}
.msg-preview-img { max-width: 90vw; max-height: 90vh; border-radius: 8px; }

@media (max-width: 768px) {
  .msg-page { flex-direction: column; height: auto; min-height: 100vh; }
  .msg-page__list { width: 100%; max-height: 50vh; border-right: none; border-bottom: 1px solid #e2e8f0; }
  .msg-page__chat { min-height: 50vh; }
}
</style>
