import { api } from './client';

export interface Customer {
  id: string;
  code: string;
  name: string;
  contactName: string;
  phone: string;
  email?: string;
  address?: string;
  tier: 'A' | 'B' | 'C';
  tags: string[];
  status: 'active' | 'inactive';
  createdAt: string;
}

export async function searchCustomers(query: string): Promise<Customer[]> {
  if (!query) return [];
  const result = await api.get<Customer[]>(`/customers/search?q=${encodeURIComponent(query)}`);
  return result.data || [];
}

export async function createCustomer(data: Omit<Customer, 'id' | 'code' | 'createdAt'>): Promise<Customer> {
  const result = await api.post<Customer>('/customers', data);
  if (result.error) {
    throw new Error(result.error);
  }
  return result.data;
}

export async function getCustomer(id: string): Promise<Customer> {
  const result = await api.get<Customer>(`/customers/${id}`);
  if (result.error) {
    throw new Error(result.error);
  }
  return result.data;
}
