<template>
  <div class="ci-root">
    <div class="ci-wrapper">
      <!-- File display chip -->
      <transition name="ci-chip">
        <div v-if="fileName" class="ci-chip" @click="fileInputRef?.click()">
          <FileUp :size="14" class="ci-chip-icon" />
          <span class="ci-chip-name">{{ fileName }}</span>
          <button class="ci-chip-close" @click.stop="clearFile">
            <X :size="12" />
          </button>
        </div>
      </transition>

      <div class="ci-bar">
        <!-- Paperclip button -->
        <button class="ci-clip-btn" title="添加附件" @click="fileInputRef?.click()">
          <Paperclip :size="18" class="ci-clip-icon" />
        </button>

        <input
          ref="fileInputRef"
          type="file"
          class="ci-file-input"
          :accept="accept"
          @change="handleFileSelect"
        />

        <!-- Textarea -->
        <textarea
          ref="textareaRef"
          v-model="inputValue"
          class="ci-textarea"
          :placeholder="placeholder"
          :style="{ minHeight: minHeight + 'px' }"
          @input="adjustHeight()"
          @keydown="onKeydown"
          rows="1"
        ></textarea>

        <!-- Send button -->
        <button
          class="ci-send-btn"
          :class="{ 'ci-send-btn--active': inputValue.trim() || fileName }"
          :disabled="!inputValue.trim() && !fileName"
          @click="handleSend"
        >
          <CornerRightUp :size="18" />
        </button>
      </div>

      <p v-if="error" class="ci-error">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { CornerRightUp, FileUp, Paperclip, X } from 'lucide-vue-next';
import { useAutoResizeTextarea } from '@/composables/useAutoResizeTextarea';
import { useFileInput } from '@/composables/useFileInput';

const props = withDefaults(defineProps<{
  placeholder?: string;
  minHeight?: number;
  maxHeight?: number;
  accept?: string;
  maxFileSize?: number;
}>(), {
  placeholder: '输入消息...',
  minHeight: 48,
  maxHeight: 180,
  accept: 'image/*',
  maxFileSize: 5,
});

const emit = defineEmits<{
  (e: 'submit', message: string, file?: File): void;
}>();

const inputValue = ref('');
const { textareaRef, adjustHeight } = useAutoResizeTextarea({
  minHeight: props.minHeight,
  maxHeight: props.maxHeight,
});
const {
  fileName, error, fileInputRef, selectedFile, handleFileSelect, clearFile,
} = useFileInput({ accept: props.accept, maxSize: props.maxFileSize });

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
}

function handleSend() {
  const text = inputValue.value.trim();
  if (!text && !selectedFile.value) return;
  emit('submit', text, selectedFile.value ?? undefined);
  inputValue.value = '';
  adjustHeight(true);
  clearFile();
}
</script>

<style scoped>
.ci-root {
  padding: 10px 0;
}

.ci-wrapper {
  max-width: 640px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

/* File chip */
.ci-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  width: fit-content;
  padding: 4px 12px;
  border-radius: 10px;
  background: var(--surface-sunken);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: background 0.15s;
}
.ci-chip:hover { background: var(--brand-light); }

.ci-chip-icon { color: var(--brand); flex-shrink: 0; }
.ci-chip-name {
  font-size: var(--fz-sm);
  color: var(--text);
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ci-chip-close {
  display: grid;
  place-items: center;
  border: none;
  background: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 2px;
  border-radius: 50%;
  transition: all 0.15s;
}
.ci-chip-close:hover { background: var(--border); color: var(--text); }

/* Bar */
.ci-bar {
  position: relative;
  display: flex;
  align-items: flex-end;
  gap: 0;
  background: var(--surface-sunken);
  border: 1px solid var(--border);
  border-radius: 24px;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.ci-bar:focus-within {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px rgba(30, 64, 175, 0.08);
}

/* Hidden file input */
.ci-file-input { display: none; }

/* Paperclip button */
.ci-clip-btn {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  margin: 6px 0 6px 6px;
  border-radius: 12px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.15s;
}
.ci-clip-btn:hover {
  background: var(--border);
  color: var(--text);
}

.ci-clip-icon {
  transform: scaleX(-1) rotate(45deg);
}

/* Textarea */
.ci-textarea {
  flex: 1;
  border: none;
  background: transparent;
  padding: 11px 4px;
  font-size: var(--fz-body);
  font-family: inherit;
  color: var(--text);
  outline: none;
  resize: none;
  line-height: 1.4;
  overflow-y: auto;
}
.ci-textarea::placeholder { color: var(--text-faint); }

/* Send button */
.ci-send-btn {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  margin: 6px;
  border-radius: 12px;
  border: none;
  background: var(--border);
  color: var(--text-muted);
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.15s;
}
.ci-send-btn--active {
  background: var(--brand);
  color: #fff;
}
.ci-send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Error */
.ci-error {
  font-size: var(--fz-xs);
  color: var(--danger);
  padding: 0 4px;
  margin: 0;
}

/* Chip transition */
.ci-chip-enter-active { transition: all 0.2s ease; }
.ci-chip-leave-active { transition: all 0.15s ease; }
.ci-chip-enter-from { opacity: 0; transform: translateY(-6px) scale(0.95); }
.ci-chip-leave-to { opacity: 0; transform: translateY(-4px) scale(0.97); }

@media (max-width: 768px) {
  .ci-wrapper { padding: 0 8px; }
}
</style>
