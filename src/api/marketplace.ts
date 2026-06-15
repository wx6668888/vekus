import { api } from './client';

export interface Listing {
  id: string;
  ownerUserId: number;
  title: string;
  listingType: 'sell' | 'buy';
  category: string;
  material: string;
  thickness: number;
  dimensions: string;
  surface: string;
  quantity: number;
  price: number;
  unit: string;
  description: string;
  images: string[];
  location: string;
  contactPhone: string;
  status: 'active' | 'sold' | 'closed';
  viewsCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface CreateListingData {
  ownerUserId: number;
  title: string;
  listingType: 'sell' | 'buy';
  category: string;
  material: string;
  thickness: number;
  dimensions: string;
  surface: string;
  quantity: number;
  price: number;
  unit: string;
  description: string;
  images: string[];
  location: string;
  contactPhone: string;
}

export async function listMarketplace(params?: {
  category?: string;
  listingType?: string;
  keyword?: string;
  page?: number;
}): Promise<Listing[]> {
  const query = new URLSearchParams();
  if (params?.category) query.set('category', params.category);
  if (params?.listingType) query.set('listing_type', params.listingType);
  if (params?.keyword) query.set('keyword', params.keyword);
  if (params?.page) query.set('page', String(params.page));
  const result = await api.get<Listing[]>(`/marketplace/listings?${query}`);
  return result.data || [];
}

export async function getListing(id: string): Promise<Listing> {
  const result = await api.get<Listing>(`/marketplace/listings/${id}`);
  if (result.error) throw new Error(result.error);
  return result.data;
}

export async function createListing(data: CreateListingData): Promise<Listing> {
  const result = await api.post<Listing>('/marketplace/listings', data);
  if (result.error) throw new Error(result.error);
  return result.data;
}

export async function updateListing(id: string, data: Partial<CreateListingData>): Promise<Listing> {
  const result = await api.put<Listing>(`/marketplace/listings/${id}`, data);
  if (result.error) throw new Error(result.error);
  return result.data;
}

export async function deleteListing(id: string): Promise<void> {
  const result = await api.delete(`/marketplace/listings/${id}`);
  if (result.error) throw new Error(result.error);
}

export async function myListings(userId: number): Promise<Listing[]> {
  const result = await api.get<Listing[]>(`/marketplace/my-listings?owner_user_id=${userId}`);
  return result.data || [];
}
