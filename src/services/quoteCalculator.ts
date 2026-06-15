import type { QuoteInput, QuoteBreakdown, QuoteResult, RecognizedResult } from '@/api/quote';

export const MATERIAL_PRICES: Record<string, number> = {
  '镀锌板': 8.5,
  '冷轧板': 7.2,
  '铝板': 18.0,
  '不锈钢': 22.0,
};

export const SURFACE_PRICES: Record<string, number> = {
  '喷粉': 2.8,
  '喷漆': 3.2,
  '电镀': 4.5,
  '钝化': 1.8,
  '无': 0,
};

export interface BreakdownParams {
  material: string;
  thickness: number;
  quantity: number;
  surface: string;
  recognized: RecognizedResult;
  profitRate?: number;
}

export function computeBreakdown(params: BreakdownParams): QuoteBreakdown {
  const { material, thickness, quantity, surface, recognized, profitRate = 0.28 } = params;

  const materialPrice = MATERIAL_PRICES[material] || MATERIAL_PRICES['镀锌板'];
  const surfacePrice = SURFACE_PRICES[surface] || 0;

  const area = (recognized.expandLength / 1000) * (recognized.expandWidth / 1000);
  const materialCost = area * thickness * 7.85 * materialPrice * quantity;
  const cuttingCost = recognized.cutLength * 0.12;
  const bendingCost = recognized.bendCount * 1.5;
  const weldingCost = recognized.weldLength * 0.35 + recognized.weldPoints * 0.8;
  const surfaceCost = recognized.paintArea * surfacePrice * quantity;
  const adminCost = 50 + recognized.cutLength * 0.05;

  const sub = materialCost + cuttingCost + bendingCost + weldingCost + surfaceCost + adminCost;
  const profit = sub * profitRate;

  return {
    material: Math.round(materialCost),
    cutting: Math.round(cuttingCost),
    bending: Math.round(bendingCost),
    welding: Math.round(weldingCost),
    surface: Math.round(surfaceCost),
    admin: Math.round(adminCost),
    profit: Math.round(profit),
  };
}

export function calculateQuote(input: QuoteInput): QuoteResult {
  const { basics, recognized, manualOverrides, coefficients } = input;
  const final = { ...recognized, ...manualOverrides };

  const breakdown = computeBreakdown({
    material: basics.material,
    thickness: final.thickness,
    quantity: basics.quantity,
    surface: basics.surface,
    recognized: final,
    profitRate: coefficients.profitRate,
  });

  const totalCost = breakdown.material + breakdown.cutting + breakdown.bending + breakdown.welding + breakdown.surface + breakdown.admin;
  const subTotal = totalCost + breakdown.profit;
  const totalPrice = Math.round(subTotal * coefficients.tax * coefficients.discount + coefficients.packaging);
  const unitPrice = Math.round(totalPrice / basics.quantity);
  const profitMargin = Math.round((breakdown.profit / totalPrice) * 100 * 100) / 100;

  const warnings: string[] = [];
  if (final.bendCount > 12) warnings.push('折弯数较多，建议人工复核');
  if (final.weldPoints > 30) warnings.push('焊点数量较多，建议确认焊接工艺');
  if (basics.quantity < 10) warnings.push('数量较少，单价可能偏高');

  return {
    breakdown,
    totalCost,
    totalPrice,
    unitPrice,
    profitMargin,
    warnings,
  };
}
