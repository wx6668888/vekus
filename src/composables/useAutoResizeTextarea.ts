import { ref, onMounted, onUnmounted, nextTick } from 'vue';

export function useAutoResizeTextarea(options: { minHeight: number; maxHeight?: number }) {
  const { minHeight, maxHeight } = options;
  const textareaRef = ref<HTMLTextAreaElement | null>(null);

  function adjustHeight(reset?: boolean) {
    const el = textareaRef.value;
    if (!el) return;

    if (reset) {
      el.style.height = `${minHeight}px`;
      return;
    }

    el.style.height = `${minHeight}px`;
    const newHeight = Math.max(
      minHeight,
      Math.min(el.scrollHeight, maxHeight ?? Number.POSITIVE_INFINITY)
    );
    el.style.height = `${newHeight}px`;
  }

  function onResize() {
    adjustHeight();
  }

  onMounted(() => {
    nextTick(() => {
      const el = textareaRef.value;
      if (el) el.style.height = `${minHeight}px`;
    });
    window.addEventListener('resize', onResize);
  });

  onUnmounted(() => {
    window.removeEventListener('resize', onResize);
  });

  return { textareaRef, adjustHeight };
}
