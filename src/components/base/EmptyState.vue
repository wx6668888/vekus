<template>
  <div class="vk-empty">
    <div class="vk-empty__icon">
      <component :is="iconComponent" :size="48" />
    </div>
    <h3 class="vk-empty__title">{{ title }}</h3>
    <p v-if="description" class="vk-empty__desc">{{ description }}</p>
    <div v-if="$slots.actions" class="vk-empty__actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { FileText, Users, Package, MessageSquare, Inbox } from 'lucide-vue-next';

interface Props {
  title?: string;
  description?: string;
  icon?: 'file' | 'users' | 'package' | 'message' | 'inbox';
}

const props = withDefaults(defineProps<Props>(), {
  title: '暂无数据',
  description: '',
  icon: 'inbox',
});

const iconMap: Record<string, any> = {
  file: FileText,
  users: Users,
  package: Package,
  message: MessageSquare,
  inbox: Inbox,
};

const iconComponent = computed(() => iconMap[props.icon] || Inbox);
</script>

<style scoped>
.vk-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 24px;
  text-align: center;
}

.vk-empty__icon {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: var(--surface-sunken);
  display: grid;
  place-items: center;
  color: var(--text-faint);
  margin-bottom: 20px;
}

.vk-empty__title {
  font-size: var(--fz-h2);
  font-weight: var(--fw-semibold);
  color: var(--text);
  margin: 0 0 8px;
}

.vk-empty__desc {
  font-size: var(--fz-body);
  color: var(--text-muted);
  margin: 0 0 24px;
  max-width: 320px;
}

.vk-empty__actions {
  display: flex;
  gap: 12px;
}
</style>
