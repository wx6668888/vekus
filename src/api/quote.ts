import { api } from './client';

export interface RecognizedResult {
  thickness: number;
  expandLength: number;
  expandWidth: number;
  cutLength: number;
  bendCount: number;
  paintArea: number;
  weldPoints: number;
  weldLength: number;
  holes: {
    plain: number;
    threaded: number;
    counterbored: number;
  };
}

export interface QuoteInput {
  basics: {
    material: string;
    thickness: number;
    quantity: number;
    surface: string;
    customerName: string;
    customerId?: string;
    deliveryDays: number;
    note?: string;
  };
  recognized: RecognizedResult;
  manualOverrides: Partial<RecognizedResult>;
  coefficients: {
    tax: number;
    discount: number;
    packaging: number;
    profitRate: number;
  };
}

export interface QuoteBreakdown {
  material: number;
  cutting: number;
  bending: number;
  welding: number;
  surface: number;
  admin: number;
  profit: number;
}

export interface QuoteResult {
  breakdown: QuoteBreakdown;
  totalCost: number;
  totalPrice: number;
  unitPrice: number;
  profitMargin: number;
  warnings: string[];
}

export interface Quote {
  id: string;
  quoteNo: string;
  customerId: string;
  customerName: string;
  material: string;
  thickness: number;
  quantity: number;
  surface: string;
  deliveryDays: number;
  note: string;
  recognized: RecognizedResult;
  manualOverrides: Partial<RecognizedResult>;
  coefficients: {
    tax: number;
    discount: number;
    packaging: number;
    profitRate: number;
  };
  totalCost: number;
  totalPrice: number;
  unitPrice: number;
  profitMargin: number;
  status: 'draft' | 'sent' | 'viewed' | 'won' | 'lost';
  createdAt: string;
  updatedAt: string;
}

export async function scanDrawing(file: File): Promise<RecognizedResult> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch('/api/ai/scan', {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    throw new Error('识别失败');
  }
  return response.json();
}

export async function saveQuote(input: QuoteInput): Promise<Quote> {
  const result = await api.post<Quote>('/quotes', {
    customer_name: input.basics.customerName,
    material: input.basics.material,
    thickness: input.basics.thickness,
    quantity: input.basics.quantity,
    surface: input.basics.surface,
    delivery_days: input.basics.deliveryDays,
    note: input.basics.note || '',
    recognized: input.recognized,
    manual_overrides: input.manualOverrides,
    coefficients: input.coefficients,
  });
  if (result.error) {
    throw new Error(result.error);
  }
  return result.data;
}

export async function updateQuote(id: string, input: QuoteInput): Promise<Quote> {
  const result = await api.put<Quote>(`/quotes/${id}`, {
    customer_name: input.basics.customerName,
    material: input.basics.material,
    thickness: input.basics.thickness,
    quantity: input.basics.quantity,
    surface: input.basics.surface,
    delivery_days: input.basics.deliveryDays,
    note: input.basics.note || '',
    recognized: input.recognized,
    manual_overrides: input.manualOverrides,
    coefficients: input.coefficients,
  });
  if (result.error) {
    throw new Error(result.error);
  }
  return result.data;
}

export async function getQuote(id: string): Promise<Quote> {
  const result = await api.get<Quote>(`/quotes/${id}`);
  if (result.error) {
    throw new Error(result.error);
  }
  return result.data;
}

export async function listQuotes(params?: {
  customer?: string;
  status?: string;
  page?: number;
}): Promise<Quote[]> {
  const query = new URLSearchParams();
  if (params?.customer) query.set('customer', params.customer);
  if (params?.status) query.set('status', params.status);
  if (params?.page) query.set('page', String(params.page));
  const result = await api.get<Quote[]>(`/quotes?${query}`);
  if (result.error) {
    throw new Error(result.error);
  }
  return result.data;
}
