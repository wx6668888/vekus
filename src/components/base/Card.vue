<template>
  <div :class="classes" :style="style">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

type Variant = 'default' | 'sunken' | 'blueprint';

interface Props {
  variant?: Variant;
  padding?: string;
  shadow?: 'none' | 'sm' | 'md' | 'lg';
  borderless?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  padding: '',
  shadow: 'md',
  borderless: false,
});

const classes = computed(() => [
  'vk-card',
  `vk-card--${props.variant}`,
  `vk-card--shadow-${props.shadow}`,
  { 'vk-card--borderless': props.borderless },
]);

const style = computed(() => {
  if (!props.padding) return {};
  return { padding: props.padding };
});
</script>

<style scoped>
.vk-card {
  background: var(--surface);
  border-radius: var(--r-card);
  border: 1px solid var(--border);
  transition: all var(--duration-normal) var(--ease-out);
}

.vk-card--sunken {
  background: var(--surface-sunken);
}

.vk-card--blueprint {
  background: var(--surface-blueprint);
  border-color: var(--border-blueprint);
  color: white;
}

.vk-card--shadow-none { box-shadow: none; }
.vk-card--shadow-sm { box-shadow: var(--sh-sm); }
.vk-card--shadow-md { box-shadow: var(--sh-md); }
.vk-card--shadow-lg { box-shadow: var(--sh-lg); }
.vk-card--blueprint.vk-card--shadow-lg { box-shadow: var(--sh-blueprint); }

.vk-card--borderless {
  border: none;
}
</style>
