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
          <div class="chat-view__thinking">
            <span class="chat-view__thinking-dot"></span>
            <span class="chat-view__thinking-dot"></span>
            <span class="chat-view__thinking-dot"></span>
          </div>
          <span class="chat-view__thinking-text">AI 正在思考...</span>
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
            <div class="chat-view__bubble-content">{{ msg.content }}</div>
            <div class="chat-view__bubble-time">{{ formatTime(msg.createdAt) }}</div>
          </template>
        </div>
      </div>

      <div class="chat-view__input-bar">
        <input
          v-model="inputText"
          class="chat-view__input"
          placeholder="输入消息..."
          @keydown.enter="sendMsg"
        />
        <button class="chat-view__send-btn" :disabled="!inputText.trim()" @click="sendMsg">
          <Send :size="20" />
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { ChevronLeft, Send, Sparkles } from 'lucide-vue-next';
import Sidebar from '@/components/layout/Sidebar.vue';
import { getMessages, sendMessage, markRead, type Message, type Conversation, getConversations } from '@/api/messages';
import { askCustomerService } from '@/api/ai';

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
let pollTimer: ReturnType<typeof setInterval> | null = null;

onMounted(async () => {
  // Find conversation type
  const convs = await getConversations(myId);
  const conv = convs.find(c => c.id === conversationId);
  if (conv) {
    convTitle.value = conv.title;
    convType.value = conv.type;
  }
  await fetchMessages();
  await markRead(conversationId);
  pollTimer = setInterval(fetchMessages, 5000);
});

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer);
});

async function fetchMessages() {
  messages.value = await getMessages(conversationId);
  loading.value = false;
  await nextTick();
  scrollToBottom();
}

function scrollToBottom() {
  if (msgContainer.value) {
    msgContainer.value.scrollTop = msgContainer.value.scrollHeight;
  }
}

async function sendMsg() {
  const text = inputText.value.trim();
  if (!text) return;
  inputText.value = '';

  // Send user message
  await sendMessage({
    conversationId,
    senderId: myId,
    content: text,
    messageType: 'text',
  });

  await fetchMessages();

  // Auto-reply from AI if customer service
  if (convType.value === 'customer_service') {
    aiThinking.value = true;
    await fetchMessages(); // refresh to show "thinking" state
    try {
      const response = await askCustomerService(text);
      await sendMessage({
        conversationId,
        senderId: 0,
        content: response,
        messageType: 'text',
      });
    } catch {
      await sendMessage({
        conversationId,
        senderId: 0,
        content: '抱歉，我暂时无法处理您的问题，请稍后再试或拨打客服电话 400-888-9999。',
        messageType: 'text',
      });
    } finally {
      aiThinking.value = false;
      await fetchMessages();
    }
  }
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
  display: flex;
  gap: 10px;
  padding: 14px 20px;
  border-top: 1px solid var(--border);
  background: var(--surface);
}

.chat-view__input {
  flex: 1;
  height: 44px;
  padding: 0 16px;
  border-radius: 22px;
  border: 1px solid var(--border);
  background: var(--surface-sunken);
  font-size: var(--fz-body);
  outline: none;
}

.chat-view__input:focus {
  border-color: var(--brand);
}

.chat-view__send-btn {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: none;
  background: var(--brand);
  color: white;
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: opacity var(--duration-fast);
}

.chat-view__send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
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

.chat-view__thinking {
  display: flex;
  gap: 4px;
}

.chat-view__thinking-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: bounce 1.4s ease-in-out infinite both;
}

.chat-view__thinking-dot:nth-child(1) { animation-delay: -0.32s; }
.chat-view__thinking-dot:nth-child(2) { animation-delay: -0.16s; }
.chat-view__thinking-dot:nth-child(3) { animation-delay: 0s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.chat-view__thinking-text {
  font-size: var(--fz-sm);
  color: var(--text-muted);
}

@media (max-width: 768px) {
  .chat-view { grid-template-columns: 1fr; }
}
</style>
