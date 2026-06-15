export async function askCustomerService(question: string, image?: string): Promise<string> {
  const body: Record<string, string> = { question };
  if (image) body.image = image;

  const response = await fetch('/api/ai/customer-service', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error('AI 客服暂不可用');
  }
  const data = await response.json();
  return data.answer;
}
