<template>
  <Teleport to="body">
    <div v-if="visible" class="vk-overlay" @click.self="onCancel">
      <div class="vk-confirm">
        <h3 class="vk-confirm__title">{{ title }}</h3>
        <p class="vk-confirm__message">{{ message }}</p>
        <div class="vk-confirm__actions">
          <Button variant="ghost" @click="onCancel">{{ cancelText }}</Button>
          <Button :variant="confirmVariant" :loading="loading" @click="onConfirm">{{ confirmText }}</Button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import Button from './Button.vue';

interface Props {
  visible?: boolean;
  title?: string;
  message?: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'primary';
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  title: '确认操作',
  message: '确定要执行此操作吗？',
  confirmText: '确定',
  cancelText: '取消',
  variant: 'primary',
  loading: false,
});

const emit = defineEmits<{
  confirm: [];
  cancel: [];
}>();

const confirmVariant = computed<'primary' | 'danger'>(() => {
  return props.variant === 'danger' ? 'danger' : 'primary';
});

function onConfirm() {
  emit('confirm');
}

function onCancel() {
  emit('cancel');
}
</script>

<style scoped>
.vk-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  display: grid;
  place-items: center;
  z-index: var(--z-modal);
  padding: 24px;
}

.vk-confirm {
  background: var(--surface);
  border-radius: var(--r-modal);
  padding: 28px;
  max-width: 400px;
  width: 100%;
  box-shadow: var(--sh-lg);
}

.vk-confirm__title {
  font-size: var(--fz-h2);
  font-weight: var(--fw-semibold);
  color: var(--text);
  margin: 0 0 8px;
}

.vk-confirm__message {
  font-size: var(--fz-body);
  color: var(--text-muted);
  margin: 0 0 24px;
  line-height: var(--lh-loose);
}

.vk-confirm__actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>
