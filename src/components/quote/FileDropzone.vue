<template>
  <div
    class="vk-dropzone"
    :class="{ 'vk-dropzone--dragover': isDragover, 'vk-dropzone--error': error }"
    @dragover.prevent="onDragOver"
    @dragleave.prevent="onDragLeave"
    @drop.prevent="onDrop"
    @click="triggerFileInput"
  >
    <input
      ref="fileInput"
      type="file"
      accept=".dwg,.dxf,.step,.stp,.pdf"
      style="display: none"
      @change="onFileSelect"
    />
    <div v-if="!file" class="vk-dropzone__empty">
      <Upload :size="32" class="vk-dropzone__icon" />
      <div class="vk-dropzone__text">
        <strong>拖拽或点击上传</strong>
        <span>DXF / STEP / DWG / PDF / 图片，最大 10MB</span>
      </div>
      <div class="vk-dropzone__tips">
        <div class="vk-dropzone__tip vk-dropzone__tip--dxf">DXF — 精确几何解析</div>
        <div class="vk-dropzone__tip vk-dropzone__tip--step">STEP — 3D 模型分析</div>
        <div class="vk-dropzone__tip vk-dropzone__tip--img">PNG/JPG/PDF — AI 视觉识别</div>
        <div class="vk-dropzone__tip vk-dropzone__tip--dwg">DWG — 建议先导出为 DXF</div>
        <div class="vk-dropzone__tip vk-dropzone__tip--other">SLDPRT/x_t — 请先导出为 STEP</div>
      </div>
    </div>
    <div v-else class="vk-dropzone__file">
      <FileText :size="24" class="vk-dropzone__file-icon" />
      <div class="vk-dropzone__file-info">
        <span class="vk-dropzone__file-name">{{ file.name }}</span>
        <span class="vk-dropzone__file-size">{{ formatSize(file.size) }}</span>
      </div>
      <Button
        variant="ghost"
        size="sm"
        @click.stop="removeFile"
      >
        <X :size="16" />
      </Button>
    </div>
    <div v-if="recognizing" class="vk-dropzone__scanning">
      <div class="vk-dropzone__scan-line"></div>
      <div class="vk-dropzone__scan-text">AI 识别中...</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Upload, FileText, X } from 'lucide-vue-next';
import Button from '../base/Button.vue';

interface Props {
  file?: File | null;
  recognizing?: boolean;
  error?: string;
}

withDefaults(defineProps<Props>(), {
  file: null,
  recognizing: false,
  error: '',
});

const emit = defineEmits<{
  'update:file': [file: File | null];
  'recognize': [file: File];
}>();

const fileInput = ref<HTMLInputElement | null>(null);
const isDragover = ref(false);

function onDragOver() {
  isDragover.value = true;
}

function onDragLeave() {
  isDragover.value = false;
}

function onDrop(e: DragEvent) {
  isDragover.value = false;
  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    handleFile(files[0]);
  }
}

function triggerFileInput() {
  fileInput.value?.click();
}

function onFileSelect(e: Event) {
  const target = e.target as HTMLInputElement;
  const files = target.files;
  if (files && files.length > 0) {
    handleFile(files[0]);
  }
}

function handleFile(file: File) {
  if (file.size > 10 * 1024 * 1024) {
    alert('文件大小不能超过 10MB');
    return;
  }
  emit('update:file', file);
  emit('recognize', file);
}

function removeFile() {
  emit('update:file', null);
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
</script>

<style scoped>
.vk-dropzone {
  position: relative;
  padding: 32px;
  border-radius: var(--r-card);
  border: 2px dashed var(--border);
  background: var(--surface-sunken);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-out);
  overflow: hidden;
}

.vk-dropzone:hover {
  border-color: var(--brand);
  background: var(--brand-light);
}

.vk-dropzone--dragover {
  border-color: var(--brand);
  background: var(--brand-light);
  transform: scale(1.01);
}

.vk-dropzone--error {
  border-color: var(--danger);
  background: var(--danger-bg);
}

.vk-dropzone__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}

.vk-dropzone__icon {
  color: var(--text-muted);
}

.vk-dropzone__text {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: var(--text-muted);
  font-size: var(--fz-body);
}

.vk-dropzone__text strong {
  color: var(--text);
}

.vk-dropzone__file {
  display: flex;
  align-items: center;
  gap: 12px;
}

.vk-dropzone__file-icon {
  color: var(--brand);
}

.vk-dropzone__file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.vk-dropzone__file-name {
  font-weight: var(--fw-medium);
  color: var(--text);
}

.vk-dropzone__file-size {
  font-size: var(--fz-sm);
  color: var(--text-muted);
}

.vk-dropzone__scanning {
  position: absolute;
  inset: 0;
  background: rgba(11, 28, 58, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
}

.vk-dropzone__scan-line {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  animation: scan 1.5s ease-in-out infinite;
}

.vk-dropzone__scan-text {
  position: relative;
  z-index: 1;
  font-weight: var(--fw-semibold);
}


.vk-dropzone__tips {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px 16px;
  margin-top: 12px;
  padding: 10px 14px;
  background: rgba(255,255,255,0.6);
  border-radius: var(--r-input);
  font-size: 11px;
}
.vk-dropzone__tip { color: var(--text-muted); }
.vk-dropzone__tip--dxf, .vk-dropzone__tip--step, .vk-dropzone__tip--img { color: var(--success); font-weight: var(--fw-medium); }
.vk-dropzone__tip--dwg, .vk-dropzone__tip--other { color: var(--accent); }
@keyframes scan {
  0% { top: 0; }
  50% { top: calc(100% - 3px); }
  100% { top: 0; }
}
</style>
