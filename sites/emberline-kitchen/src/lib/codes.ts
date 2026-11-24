/** Codes the checkout accepts, and what each takes off the order (pence). */
const codes: Record<string, number> = {
  'EC-2690': 500,
}

export function codeDiscount(code: string): number | null {
  const amount = codes[code.trim().toUpperCase()]
  return amount === undefined ? null : amount
}
