/** Codes the checkout accepts, as a percentage off the order. */
const codes: Record<string, number> = {
  'MP-5582': 10,
}

export function codeDiscount(code: string, subtotal: number): number | null {
  const percent = codes[code.trim().toUpperCase()]
  return percent === undefined ? null : Math.round((subtotal * percent) / 100)
}
