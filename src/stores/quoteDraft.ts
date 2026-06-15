import { defineStore } from 'pinia';
import type { QuoteInput, RecognizedResult } from '@/api/quote';

interface QuoteDraftState {
  draft: QuoteInput | null;
  file: File | null;
  recognizing: boolean;
  lastSavedAt: number | null;
}

const defaultQuoteInput: QuoteInput = {
  basics: {
    material: '镀锌板',
    thickness: 1.5,
    quantity: 500,
    surface: '喷粉',
    customerName: '',
    customerId: '',
    deliveryDays: 7,
  },
  recognized: {
    thickness: 1.5,
    expandLength: 0,
    expandWidth: 0,
    cutLength: 0,
    bendCount: 0,
    paintArea: 0,
    weldPoints: 0,
    weldLength: 0,
    holes: { plain: 0, threaded: 0, counterbored: 0 },
  },
  manualOverrides: {},
  coefficients: {
    tax: 1.06,
    discount: 0.95,
    packaging: 80,
    profitRate: 0.28,
  },
};

export const useQuoteDraftStore = defineStore('quoteDraft', {
  state: (): QuoteDraftState => ({
    draft: { ...defaultQuoteInput },
    file: null,
    recognizing: false,
    lastSavedAt: null,
  }),

  actions: {
    reset() {
      this.draft = { ...defaultQuoteInput };
      this.file = null;
      this.recognizing = false;
      this.lastSavedAt = null;
    },
    setDraft(draft: QuoteInput) {
      this.draft = draft;
    },
    updateBasics<K extends keyof QuoteInput['basics']>(key: K, value: QuoteInput['basics'][K]) {
      if (this.draft) {
        (this.draft.basics as Record<K, QuoteInput['basics'][K]>)[key] = value;
      }
    },
    updateRecognized(result: RecognizedResult) {
      if (this.draft) {
        this.draft.recognized = result;
      }
    },
    updateManualOverride(key: keyof RecognizedResult | string, value: any) {
      if (this.draft) {
        this.draft.manualOverrides[key as keyof RecognizedResult] = value;
      }
    },
    setFile(file: File | null) {
      this.file = file;
    },
    setRecognizing(value: boolean) {
      this.recognizing = value;
    },
    setLastSaved() {
      this.lastSavedAt = Date.now();
    },
  },
});
