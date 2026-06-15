import { api } from './client';

export interface PricingPlan {
  id: string;
  name: string;
  price: number;
  points: number;
  description: string;
}

export interface PaymentOrder {
  id: string;
  orderNo: string;
  amount: number;
  points: number;
  planName: string;
  status: 'pending' | 'paid' | 'expired';
  createdAt: string;
}

export interface PointsTransaction {
  id: string;
  userId: number;
  amount: number;
  type: 'charge' | 'deduct' | 'expire';
  description: string;
  relatedId: string;
  createdAt: string;
}

export async function getPricing(): Promise<PricingPlan[]> {
  const result = await api.get<PricingPlan[]>('/payment/pricing');
  return result.data || [];
}

export async function createOrder(planId: string, userId: number): Promise<PaymentOrder> {
  const result = await api.post<PaymentOrder>('/payment/create-order', { planId, userId });
  if (result.error) throw new Error(result.error);
  return result.data;
}

export async function completePayment(orderNo: string): Promise<void> {
  const result = await api.post('/payment/complete', { orderNo });
  if (result.error) throw new Error(result.error);
}

export async function getTransactions(userId: number): Promise<PointsTransaction[]> {
  const result = await api.get<PointsTransaction[]>(`/payment/transactions?user_id=${userId}`);
  return result.data || [];
}

export async function getPointsBalance(userId: number): Promise<number> {
  const result = await api.get<{ balance: number }>(`/payment/points?user_id=${userId}`);
  return result.data?.balance || 0;
}

export async function deductPoints(userId: number, description: string, quoteId: string): Promise<{ ok: boolean; balance: number }> {
  const result = await api.post<{ ok: boolean; balance: number }>('/payment/deduct', { userId, description, quoteId });
  if (result.error) throw new Error(result.error);
  return result.data;
}
