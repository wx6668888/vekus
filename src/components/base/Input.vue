<template>
  <div class="vk-input" :class="{ 'vk-input--error': error, 'vk-input--disabled': disabled }">
    <label v-if="label" class="vk-input__label">
      {{ label }}
      <span v-if="required" class="vk-input__required">*</span>
    </label>
    <input
      v-bind="$attrs"
      :value="modelValue"
      :type="type"
      :disabled="disabled"
      :placeholder="placeholder"
      class="vk-input__field"
      @input="onInput"
      @focus="onFocus"
      @blur="onBlur"
    />
    <span v-if="error" class="vk-input__error">{{ error }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

interface Props {
  modelValue: string | number;
  type?: string;
  label?: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  label: '',
  placeholder: '',
  required: false,
  disabled: false,
  error: '',
});

const emit = defineEmits<{
  'update:modelValue': [value: string | number];
  focus: [];
  blur: [];
}>();

const focused = ref(false);

function onInput(e: Event) {
  const target = e.target as HTMLInputElement;
  emit('update:modelValue', props.type === 'number' ? Number(target.value) : target.value);
}

function onFocus() {
  focused.value = true;
  emit('focus');
}

function onBlur() {
  focused.value = false;
  emit('blur');
}
</script>

<style scoped>
.vk-input {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.vk-input__label {
  font-size: var(--fz-sm);
  font-weight: var(--fw-semibold);
  color: var(--text-muted);
}

.vk-input__required {
  color: var(--danger);
}

.vk-input__field {
  height: 48px;
  padding: 0 14px;
  border-radius: var(--r-input);
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: var(--fz-body);
  transition: all var(--duration-fast) var(--ease-out);
}

.vk-input__field::placeholder {
  color: var(--text-faint);
}

.vk-input__field:hover {
  border-color: var(--border-strong);
}

.vk-input__field:focus {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px var(--brand-light);
}

.vk-input__field:disabled {
  background: var(--surface-sunken);
  color: var(--text-faint);
  cursor: not-allowed;
}

.vk-input--error .vk-input__field {
  border-color: var(--danger);
}

.vk-input--error .vk-input__field:focus {
  box-shadow: 0 0 0 3px var(--danger-bg);
}

.vk-input__error {
  font-size: var(--fz-sm);
  color: var(--danger);
}
</style>
