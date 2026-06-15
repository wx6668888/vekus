import { api } from './client';

export interface Conversation {
  id: string;
  type: 'system' | 'customer_service' | 'user_chat' | 'order';
  title: string;
  participants: number[];
  lastMessage: string;
  lastMessageAt: string;
  createdAt: string;
}

export interface Message {
  id: string;
  conversationId: string;
  senderId: number;
  content: string;
  messageType: 'text' | 'image' | 'system';
  isRead: boolean;
  createdAt: string;
}

export async function getConversations(userId: number): Promise<Conversation[]> {
  const result = await api.get<Conversation[]>(`/messages/conversations?user_id=${userId}`);
  return result.data || [];
}

export async function getUnreadCount(userId: number = 0): Promise<number> {
  const result = await api.get<{ count: number }>(`/messages/unread-count?user_id=${userId}`);
  return result.data?.count || 0;
}

export async function getMessages(conversationId: string): Promise<Message[]> {
  const result = await api.get<Message[]>(`/messages/conversations/${conversationId}`);
  return result.data || [];
}

export async function sendMessage(data: {
  conversationId?: string;
  senderId: number;
  content: string;
  messageType?: string;
  type?: string;
  title?: string;
  participants?: number[];
}): Promise<Message> {
  const result = await api.post<Message>('/messages/send', data);
  if (result.error) throw new Error(result.error);
  return result.data;
}

export async function markRead(conversationId: string): Promise<void> {
  await api.post(`/messages/read/${conversationId}`, {});
}
