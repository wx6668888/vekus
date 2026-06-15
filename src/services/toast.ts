import { ref } from 'vue';

interface ToastItem {
  id: number;
  message: string;
  variant: 'success' | 'info' | 'warn' | 'error';
}

const toasts = ref<ToastItem[]>([]);
let nextId = 1;

export function useToast() {
  function show(message: string, variant: ToastItem['variant'] = 'success') {
    const id = nextId++;
    toasts.value.push({ id, message, variant });
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id);
    }, 3000);
  }

  return { toasts, show };
}

export const toast = useToast();
