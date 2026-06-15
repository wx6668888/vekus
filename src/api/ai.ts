export async function askCustomerService(question: string): Promise<string> {
  const response = await fetch('/api/ai/customer-service', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });
  if (!response.ok) {
    throw new Error('AI 客服暂不可用');
  }
  const data = await response.json();
  return data.answer;
}
