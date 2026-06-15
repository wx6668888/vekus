import { ref } from 'vue';

const MIME_MAP: Record<string, string[]> = {
  '.pdf': ['application/pdf'],
  '.xlsx': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/octet-stream'],
  '.xls': ['application/vnd.ms-excel', 'application/octet-stream'],
  '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/octet-stream'],
  '.doc': ['application/msword', 'application/octet-stream'],
  '.csv': ['text/csv', 'application/octet-stream'],
  '.png': ['image/png'],
  '.jpg': ['image/jpeg'],
  '.jpeg': ['image/jpeg'],
  '.gif': ['image/gif'],
  '.webp': ['image/webp'],
};

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

    // Parse comma-separated accept types
    const acceptTypes = accept.split(',').map(s => s.trim()).filter(Boolean);

    if (acceptTypes.length === 0 || acceptTypes.includes('*')) {
      // Accept all
    } else {
      let allowed = false;
      for (const at of acceptTypes) {
        if (at.endsWith('/*')) {
          // Wildcard MIME type, e.g. "image/*"
          const prefix = at.slice(0, -1); // "image/"
          if (file.type.startsWith(prefix)) {
            allowed = true;
            break;
          }
        } else if (at.startsWith('.')) {
          // Extension-based type, e.g. ".pdf"
          const ext = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
          if (ext === at.toLowerCase()) {
            allowed = true;
            break;
          }
          // Also check MIME map
          const mimes = MIME_MAP[at.toLowerCase()];
          if (mimes && mimes.includes(file.type)) {
            allowed = true;
            break;
          }
        } else {
          // Exact MIME type
          if (file.type === at) {
            allowed = true;
            break;
          }
        }
      }
      if (!allowed) {
        error.value = `仅支持 ${accept} 格式`;
        return;
      }
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
