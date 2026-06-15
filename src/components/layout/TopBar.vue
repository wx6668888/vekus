<template>
  <header class="vk-topbar">
    <div class="vk-topbar__main">
      <div v-if="eyebrow" class="vk-topbar__eyebrow">{{ eyebrow }}</div>
      <h1 class="vk-topbar__title">{{ title }}</h1>
      <p v-if="description" class="vk-topbar__description">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="vk-topbar__actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup lang="ts">
interface Props {
  title: string;
  description?: string;
  eyebrow?: string;
}

defineProps<Props>();
</script>

<style scoped>
.vk-topbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 24px;
}

.vk-topbar__main {
  flex: 1;
}

.vk-topbar__eyebrow {
  font-size: var(--fz-sm);
  color: var(--text-muted);
  font-weight: var(--fw-medium);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.vk-topbar__title {
  font-size: clamp(24px, 3vw, 32px);
  font-weight: var(--fw-bold);
  color: var(--text);
  margin: 0 0 8px;
  line-height: 1.2;
}

.vk-topbar__description {
  font-size: var(--fz-body);
  color: var(--text-muted);
  margin: 0;
  max-width: 600px;
}

.vk-topbar__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .vk-topbar {
    flex-direction: column;
  }
  .vk-topbar__actions {
    width: 100%;
  }
  .vk-topbar__actions > * {
    flex: 1;
  }
}
</style>
