import { ref } from 'vue';

export function useFileInput(options: { accept?: string; maxSize?: number } = {}) {
  const { accept = 'image/*', maxSize = 5 } = options;
  const fileName = ref('');
  const fileSize = ref(0);
  const error = ref('');
  const fileInputRef = ref<HTMLInputElement | null>(null);
  const selectedFile = ref<File | null>(null);

  function handleFileSelect(e: Event) {
    const target = e.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file) validateAndSetFile(file);
  }

  function validateAndSetFile(file: File) {
    error.value = '';

    if (maxSize && file.size > maxSize * 1024 * 1024) {
      error.value = `文件大小不能超过 ${maxSize}MB`;
      return;
    }

    const acceptType = accept.replace('/*', '/');
    if (accept !== '*' && !file.type.startsWith(acceptType)) {
      error.value = `仅支持 ${accept} 格式`;
      return;
    }

    fileSize.value = file.size;
    fileName.value = file.name;
    selectedFile.value = file;
  }

  function clearFile() {
    fileName.value = '';
    error.value = '';
    fileSize.value = 0;
    selectedFile.value = null;
    if (fileInputRef.value) {
      fileInputRef.value.value = '';
    }
  }

  return {
    fileName,
    fileSize,
    error,
    fileInputRef,
    selectedFile,
    handleFileSelect,
    clearFile,
  };
}
