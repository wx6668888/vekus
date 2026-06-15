<template>
  <div class="vk-select" ref="rootEl">
    <button
      :class="['vk-select__trigger', { 'vk-select__trigger--open': open }]"
      @click="toggle"
      @blur="onBlur"
    >
      <span class="vk-select__label">{{ selectedLabel }}</span>
      <svg
        :class="['vk-select__chevron', { 'vk-select__chevron--open': open }]"
        width="12" height="8" viewBox="0 0 12 8" fill="none"
      >
        <path d="M1 1.5L6 6.5L11 1.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>
    <Teleport to="body">
      <Transition name="vk-select-fade">
        <div v-if="open" class="vk-select__portal" :style="portalStyle">
          <div class="vk-select__menu">
            <button
              v-for="opt in options"
              :key="opt.value"
              :class="['vk-select__option', { 'vk-select__option--active': modelValue === opt.value }]"
              @mousedown.prevent="select(opt.value)"
            >
              <span>{{ opt.label }}</span>
              <svg
                v-if="modelValue === opt.value"
                class="vk-select__check"
                width="16" height="16" viewBox="0 0 16 16" fill="none"
              >
                <path d="M3 8.5L6.5 12L13 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>
        </div>
      </Transition>
    </Teleport>
    <!-- Click-outside backdrop -->
    <div v-if="open" class="vk-select__backdrop" @click="open = false"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue';

export interface SelectOption {
  value: string;
  label: string;
}

const props = defineProps<{
  modelValue: string;
  options: SelectOption[];
  placeholder?: string;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void;
}>();

const open = ref(false);
const rootEl = ref<HTMLElement | null>(null);
const triggerRect = ref({ top: 0, left: 0, width: 0, height: 0 });
const menuHeight = ref(0);

const selectedLabel = computed(() => {
  const sel = props.options.find(o => o.value === props.modelValue);
  return sel ? sel.label : (props.placeholder || '请选择');
});

const portalStyle = computed(() => ({
  position: 'fixed' as const,
  top: (triggerRect.value.top + triggerRect.value.height + 6) + 'px',
  left: triggerRect.value.left + 'px',
  minWidth: triggerRect.value.width + 'px',
  zIndex: 10001,
}));

function toggle() {
  if (!open.value) {
    updateRect();
    nextTick(() => (open.value = true));
  } else {
    open.value = false;
  }
}

function updateRect() {
  if (rootEl.value) {
    const r = rootEl.value.querySelector('.vk-select__trigger')!.getBoundingClientRect();
    triggerRect.value = { top: r.top, left: r.left, width: r.width, height: r.height };
  }
}

function onBlur(e: FocusEvent) {
  // Delay to allow mousedown on option to fire first
  setTimeout(() => {
    if (open.value) open.value = false;
  }, 150);
}

function select(value: string) {
  emit('update:modelValue', value);
  open.value = false;
}

function onScroll() {
  if (open.value) {
    updateRect();
  }
}

function onResize() {
  if (open.value) {
    updateRect();
  }
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, true);
  window.addEventListener('resize', onResize);
});

onBeforeUnmount(() => {
  window.removeEventListener('scroll', onScroll, true);
  window.removeEventListener('resize', onResize);
});
</script>

<style scoped>
.vk-select {
  position: relative;
  display: inline-block;
}

.vk-select__trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 36px;
  padding: 0 12px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: var(--fz-sm);
  font-family: inherit;
  cursor: pointer;
  user-select: none;
  transition: all 0.15s ease;
  white-space: nowrap;
  outline: none;
}

.vk-select__trigger:hover {
  border-color: var(--border-strong);
  background: var(--surface-sunken);
}

.vk-select__trigger--open {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.08);
  background: var(--surface);
}

.vk-select__label {
  flex: 1;
  text-align: left;
}

.vk-select__chevron {
  flex-shrink: 0;
  color: var(--text-muted);
  transition: transform 0.2s ease;
}

.vk-select__chevron--open {
  transform: rotate(180deg);
  color: var(--brand);
}

.vk-select__portal {
  position: fixed;
}

.vk-select__menu {
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  box-shadow:
    0 4px 24px rgba(0, 0, 0, 0.08),
    0 0 0 0.5px rgba(0, 0, 0, 0.04);
  padding: 6px;
  overflow: hidden;
}

@media (prefers-color-scheme: dark) {
  .vk-select__menu {
    background: rgba(30, 30, 32, 0.94);
    border-color: rgba(255, 255, 255, 0.08);
    box-shadow:
      0 4px 24px rgba(0, 0, 0, 0.3),
      0 0 0 0.5px rgba(255, 255, 255, 0.04);
  }
}

.vk-select__option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--text);
  font-size: var(--fz-sm);
  font-family: inherit;
  cursor: pointer;
  text-align: left;
  transition: background 0.1s ease;
}

.vk-select__option:hover {
  background: var(--brand-light);
}

.vk-select__option--active {
  font-weight: var(--fw-semibold);
}

.vk-select__check {
  flex-shrink: 0;
  color: var(--brand);
}

.vk-select__backdrop {
  position: fixed;
  inset: 0;
  z-index: 10000;
}

/* Transitions */
.vk-select-fade-enter-active {
  transition: all 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}

.vk-select-fade-leave-active {
  transition: all 0.12s ease-in;
}

.vk-select-fade-enter-from {
  opacity: 0;
  transform: translateY(-6px) scale(0.96);
}

.vk-select-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px) scale(0.98);
}
</style>
