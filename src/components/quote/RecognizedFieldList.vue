<template>
  <div class="vk-recognized-list">
    <div class="vk-recognized-list__header">
      <span class="vk-recognized-list__title">AI 识别结果</span>
      <Badge v-if="hasOverrides" variant="info" size="sm">已人工校正</Badge>
    </div>

    <div class="vk-recognized-list__fields">
      <div
        v-for="(value, key) in displayFields"
        :key="key"
        class="vk-recognized-list__field"
        :class="{ 'vk-recognized-list__field--overridden': isOverridden(key) }"
      >
        <span class="vk-recognized-list__label">{{ fieldLabels[key as keyof typeof fieldLabels] }}</span>
        <div class="vk-recognized-list__value-row">
          <Input
            :model-value="getDisplayValue(key, value)"
            type="number"
            step="0.01"
            @update:model-value="(v: string | number) => updateField(key, Number(v))"
          />
          <ChevronRight :size="16" class="vk-recognized-list__arrow" />
        </div>
        <span v-if="isOverridden(key)" class="vk-recognized-list__corrected">已校正</span>
      </div>

      <button
        v-if="!showAll"
        class="vk-recognized-list__expand"
        @click="showAll = true"
      >
        展开更多 ({{ remainingCount }} 项)
        <ChevronDown :size="14" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { ChevronRight, ChevronDown } from 'lucide-vue-next';
import Input from '../base/Input.vue';
import Badge from '../base/Badge.vue';
import type { RecognizedResult } from '@/api/quote';

interface Props {
  recognized: RecognizedResult;
  overrides: Partial<RecognizedResult>;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  'update:field': [key: keyof RecognizedResult, value: number];
}>();

const showAll = ref(false);

const fieldLabels: Record<string, string> = {
  thickness: '板厚',
  expandLength: '展开长',
  expandWidth: '展开宽',
  cutLength: '切割长度',
  bendCount: '折弯总数',
  paintArea: '喷涂面积',
  weldPoints: '焊点数',
  weldLength: '满焊长度',
  'holes.plain': '光孔数',
  'holes.threaded': '螺纹孔数',
  'holes.counterbored': '沉孔数',
};

const mainFields = ['thickness', 'expandLength', 'expandWidth', 'cutLength', 'bendCount', 'paintArea', 'weldPoints'];
const extraFields = ['weldLength', 'holes.plain', 'holes.threaded', 'holes.counterbored'];

const displayFields = computed(() => {
  const fields = showAll.value ? [...mainFields, ...extraFields] : mainFields;
  return fields.reduce((acc, key) => {
    if (key.includes('.')) {
      const [parent, child] = key.split('.');
      const parentVal = props.recognized[parent as keyof RecognizedResult];
      acc[key] = typeof parentVal === 'object' && parentVal !== null
        ? (parentVal as Record<string, number>)[child]
        : 0;
    } else {
      const val = props.recognized[key as keyof RecognizedResult];
      acc[key] = typeof val === 'number' ? val : 0;
    }
    return acc;
  }, {} as Record<string, number>);
});

const hasOverrides = computed(() => Object.keys(props.overrides).length > 0);

const remainingCount = computed(() => {
  let count = 0;
  if (!props.overrides.weldLength) count++;
  if (!props.overrides.holes) {
    count += 3;
  }
  return count;
});

function isOverridden(key: string): boolean {
  if (key.includes('.')) {
    const [parent, child] = key.split('.');
    const parentOverride = props.overrides[parent as keyof RecognizedResult];
    if (typeof parentOverride === 'object' && parentOverride !== null) {
      return child in (parentOverride as Record<string, unknown>);
    }
    return false;
  }
  return key in props.overrides;
}

function getDisplayValue(key: string, defaultValue: number): number {
  if (key.includes('.')) {
    const [parent, child] = key.split('.');
    const parentOverride = props.overrides[parent as keyof RecognizedResult];
    if (parentOverride && child in (parentOverride as Record<string, number>)) {
      return (parentOverride as Record<string, number>)[child];
    }
  }
  return (props.overrides[key as keyof RecognizedResult] as number) ?? defaultValue;
}

function updateField(key: string, value: number) {
  if (key.includes('.')) {
    const [parent, child] = key.split('.');
    emit('update:field', parent as keyof RecognizedResult, {
      ...(props.overrides[parent as keyof RecognizedResult] as Record<string, number> || props.recognized[parent as keyof RecognizedResult] as Record<string, number>),
      [child]: value,
    } as any);
  } else {
    emit('update:field', key as keyof RecognizedResult, value);
  }
}
</script>

<style scoped>
.vk-recognized-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.vk-recognized-list__header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.vk-recognized-list__title {
  font-size: var(--fz-h3);
  font-weight: var(--fw-semibold);
  color: var(--text);
}

.vk-recognized-list__fields {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.vk-recognized-list__field {
  position: relative;
  padding: 14px;
  border-radius: var(--r-input);
  background: var(--surface-sunken);
  border: 1px solid var(--border);
}

.vk-recognized-list__field--overridden {
  border-color: var(--accent);
  background: rgba(249, 115, 22, 0.04);
}

.vk-recognized-list__label {
  display: block;
  font-size: var(--fz-sm);
  color: var(--text-muted);
  margin-bottom: 8px;
}

.vk-recognized-list__value-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.vk-recognized-list__value-row :deep(.vk-input__field) {
  flex: 1;
  font-family: var(--font-mono);
  font-feature-settings: "tnum" 1;
}

.vk-recognized-list__arrow {
  color: var(--text-faint);
  flex-shrink: 0;
}

.vk-recognized-list__corrected {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 10px;
  padding: 2px 6px;
  background: var(--accent);
  color: white;
  border-radius: 4px;
  font-weight: var(--fw-semibold);
}

.vk-recognized-list__expand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 12px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: var(--fz-sm);
  font-weight: var(--fw-medium);
  cursor: pointer;
  transition: color var(--duration-fast);
}

.vk-recognized-list__expand:hover {
  color: var(--brand);
}
</style>
