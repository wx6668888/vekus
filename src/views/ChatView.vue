<template>
  <div class="chat-view">
    <Sidebar />
    <main class="chat-view__main">
      <div class="chat-view__topbar">
        <button class="chat-view__back" @click="$router.push('/messages')">
          <ChevronLeft :size="20" />
        </button>
        <span class="chat-view__title">{{ convTitle || '聊天' }}</span>
        <span v-if="convType === 'customer_service'" class="chat-view__ai-badge">
          <Sparkles :size="12" /> AI客服
        </span>
      </div>

      <div class="chat-view__messages" ref="msgContainer">
        <div v-if="loading" class="chat-view__loading">加载中...</div>
        <div v-if="aiThinking" class="chat-view__bubble chat-view__bubble--ai">
          <div class="chat-view__thinking-new">
            <div class="chat-view__thinking-ring">
              <div class="chat-view__thinking-ring-inner"></div>
            </div>
            <div class="chat-view__thinking-content">
              <span class="chat-view__thinking-title">AI 正在思考</span>
              <span class="chat-view__thinking-hint">分析中，请稍候...</span>
            </div>
          </div>
        </div>
        <div
          v-for="msg in messages"
          :key="msg.id"
          :class="['chat-view__bubble', { 'chat-view__bubble--mine': msg.senderId === myId, 'chat-view__bubble--system': msg.messageType === 'system' }]"
        >
          <div v-if="msg.messageType === 'system'" class="chat-view__system-msg">
            {{ msg.content }}
          </div>
          <template v-else>
            <img
              v-if="msg.messageType === 'image'"
              :src="msg.content"
              class="chat-view__bubble-img"
              @click="previewImage = msg.content"
            />
            <div v-else class="chat-view__bubble-content">{{ msg.content }}</div>
            <div class="chat-view__bubble-time">{{ formatTime(msg.createdAt) }}</div>
          </template>
        </div>
      </div>

      <div class="chat-view__input-bar">
        <ChatInput
          placeholder="输入消息... Enter 发送"
          accept="image/*,.pdf,.xlsx,.docx"
          :max-file-size="8"
          @submit="onSend"
        />
      </div>
    </main>

    <!-- Image lightbox -->
    <div v-if="previewImage" class="chat-view__img-overlay" @click="previewImage = ''">
      <img :src="previewImage" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { ChevronLeft, Sparkles } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import ChatInput from '@/components/chat/ChatInput.vue';
import { getMessages, sendMessage, markRead, type Message, type Conversation, getConversations } from '@/api/messages';
import { askCustomerService } from '@/api/ai';
import { compressImage } from '@/composables/useImageCompress';

const route = useRoute();
const conversationId = route.params.id as string;
const convTitle = ref('聊天');
const convType = ref('');
const myId = 1;
const messages = ref<Message[]>([]);
const inputText = ref('');
const loading = ref(true);
const aiThinking = ref(false);
const msgContainer = ref<HTMLElement | null>(null);
const previewImage = ref('');
let pollTimer: ReturnType<typeof setInterval> | null = null;

onMounted(async () => {
  // Find conversation type and load messages in parallel
  const [convs, msgs] = await Promise.all([
    getConversations(myId),
    getMessages(conversationId),
  ]);
  const conv = convs.find(c => c.id === conversationId);
  if (conv) {
    convTitle.value = conv.title;
    convType.value = conv.type;
  }
  messages.value = msgs;
  loading.value = false;
  await nextTick();
  scrollToBottom();
  markRead(conversationId); // fire-and-forget
  pollTimer = setInterval(pollNewMessages, 15000); // 15s poll, not 5s
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
});

async function pollNewMessages() {
  // Only poll new messages, don't replace entire list to avoid flicker
  try {
    const latest = await getMessages(conversationId);
    if (latest.length > messages.value.length) {
      messages.value = latest;
      await nextTick();
    }
  } catch { /* ignore poll errors */ }
}

function scrollToBottom() {
  if (msgContainer.value) {
    msgContainer.value.scrollTop = msgContainer.value.scrollHeight;
  }
}

async function onSend(text: string, file?: File) {
  let content = text;
  let messageType = 'text';
  let compressedBase64: string | undefined;

  if (file) {
    if (file.type.startsWith('image/')) {
      messageType = 'image';
      compressedBase64 = await compressImage(file, 1024, 512 * 1024);
      content = compressedBase64;
    } else {
      content = text ? `${text}\n[附件: ${file.name}]` : `[附件: ${file.name}]`;
    }
  }
  if (!content) return;
  inputText.value = '';

  // Optimistic UI: add user message immediately
  const optimisticMsg: Message = {
    id: 'temp-' + Date.now(),
    conversationId,
    senderId: myId,
    content,
    messageType: messageType as any,
    isRead: true,
    createdAt: new Date().toISOString(),
  };
  messages.value.push(optimisticMsg);
  await nextTick();
  scrollToBottom();

  // Send to server (fire and update ID when done)
  const sendPromise = sendMessage({
    conversationId,
    senderId: myId,
    content,
    messageType,
  }).then(realMsg => {
    // Replace optimistic message with real one
    const idx = messages.value.findIndex(m => m.id === optimisticMsg.id);
    if (idx >= 0) messages.value[idx] = realMsg;
  }).catch(() => {
    // Mark failed
    const idx = messages.value.findIndex(m => m.id === optimisticMsg.id);
    if (idx >= 0) messages.value[idx] = { ...messages.value[idx], content: messages.value[idx].content + ' (发送失败)' };
  });

  // If AI customer service, start thinking immediately (don't wait for send)
  if (convType.value === 'customer_service') {
    aiThinking.value = true;
    await nextTick();
    scrollToBottom();

    try {
      const imageData = compressedBase64;
      const question = text || (imageData ? '请帮我分析这张图片的内容' : '');
      const response = await askCustomerService(question, imageData);

      // Add AI reply
      const aiMsg: Message = {
        id: 'ai-' + Date.now(),
        conversationId,
        senderId: 0,
        content: response,
        messageType: 'text',
        isRead: true,
        createdAt: new Date().toISOString(),
      };
      messages.value.push(aiMsg);

      // Send AI reply to server (don't block)
      sendMessage({
        conversationId,
        senderId: 0,
        content: response,
        messageType: 'text',
      }).catch(() => {});
    } catch {
      const errMsg: Message = {
        id: 'err-' + Date.now(),
        conversationId,
        senderId: 0,
        content: '抱歉，我暂时无法处理您的问题，请稍后再试或拨打客服电话 400-888-9999。',
        messageType: 'text',
        isRead: true,
        createdAt: new Date().toISOString(),
      };
      messages.value.push(errMsg);
    } finally {
      aiThinking.value = false;
      await nextTick();
      scrollToBottom();
    }
  }

  // Ensure send completed
  await sendPromise;
}

function formatTime(dateStr: string): string {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return `${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`;
}
</script>

<style scoped>
.chat-view {
  display: grid;
  display: block;
  min-height: 100vh;
}

.chat-view__main {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.chat-view__topbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}

.chat-view__back {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: var(--r-input);
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
}

.chat-view__back:hover { background: var(--surface-sunken); color: var(--text); }

.chat-view__title {
  font-size: var(--fz-h3);
  font-weight: var(--fw-semibold);
}

.chat-view__messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-view__bubble {
  display: flex;
  flex-direction: column;
  max-width: 70%;
  align-self: flex-start;
}

.chat-view__bubble--mine {
  align-self: flex-end;
  text-align: right;
}

.chat-view__bubble--mine .chat-view__bubble-content {
  background: var(--brand);
  color: white;
  border-radius: 16px 16px 4px 16px;
}

.chat-view__bubble--system {
  align-self: center;
  max-width: 100%;
}

.chat-view__bubble-content {
  padding: 10px 16px;
  border-radius: 16px 16px 16px 4px;
  background: var(--surface-sunken);
  color: var(--text);
  font-size: var(--fz-body);
  line-height: var(--lh-relaxed);
}

.chat-view__bubble-time {
  font-size: 10px;
  color: var(--text-faint);
  margin-top: 4px;
  padding: 0 4px;
}

.chat-view__system-msg {
  padding: 8px 16px;
  background: var(--surface-sunken);
  border-radius: var(--r-pill);
  font-size: var(--fz-sm);
  color: var(--text-muted);
  text-align: center;
}

.chat-view__input-bar {
  padding: 0 20px 4px;
  border-top: 1px solid var(--border);
  background: var(--surface);
}

/* Image bubble */
.chat-view__bubble-img {
  max-width: 240px;
  max-height: 320px;
  border-radius: 14px;
  cursor: pointer;
  object-fit: cover;
  border: 1px solid var(--border);
  transition: transform 0.15s;
}
.chat-view__bubble-img:hover { transform: scale(1.02); }
.chat-view__bubble--mine .chat-view__bubble-img {
  border-radius: 14px 14px 4px 14px;
}

/* Image preview overlay */
.chat-view__img-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  display: grid;
  place-items: center;
  z-index: 9999;
  cursor: pointer;
}
.chat-view__img-overlay img {
  max-width: 90vw;
  max-height: 90vh;
  border-radius: 12px;
}

.chat-view__ai-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 999px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-size: 10px;
  font-weight: var(--fw-bold);
  white-space: nowrap;
}

.chat-view__bubble--ai {
  align-self: flex-start;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--surface-sunken);
  border-radius: 16px 16px 16px 4px;
}

/* New thinking animation — LLM-style shimmer ring */
.chat-view__thinking-new {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chat-view__thinking-ring {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: conic-gradient(from 0deg, var(--brand) 0%, var(--brand-light) 30%, var(--surface-sunken) 60%, var(--brand) 100%);
  animation: think-spin 1.2s linear infinite;
  display: grid;
  place-items: center;
}

.chat-view__thinking-ring-inner {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--surface);
}

@keyframes think-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.chat-view__thinking-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.chat-view__thinking-title {
  font-size: var(--fz-sm);
  font-weight: var(--fw-semibold);
  color: var(--text);
  background: linear-gradient(90deg, var(--text) 0%, var(--brand) 50%, var(--text) 100%);
  background-size: 200% 100%;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmer-text 2s ease-in-out infinite;
}

@keyframes shimmer-text {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.chat-view__thinking-hint {
  font-size: var(--fz-xs);
  color: var(--text-faint);
}

@media (max-width: 768px) {
  .chat-view { grid-template-columns: 1fr; }
}
</style>
