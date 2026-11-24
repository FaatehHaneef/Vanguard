import { lineExtras, lineTitle, type OrderLine } from './cart'

export const PICKUP_OPENS = '12:00'
export const PICKUP_CLOSES = '21:30'

export interface PlacedOrder {
  number: string
  name: string
  phone: string
  time: string
  notes: string
  lines: { title: string; extras: string; quantity: number; price: number }[]
  subtotal: number
  discount: number
  total: number
}

const LAST_ORDER_KEY = 'emberline-last-order'

/** "18:30" from "18:30", "18.30" or "9:05"; null when it is not a time. */
export function parseTime(value: string): string | null {
  const match = value.trim().match(/^([01]?\d|2[0-3])[:.]([0-5]\d)$/)
  if (!match) return null
  return `${match[1].padStart(2, '0')}:${match[2]}`
}

export function withinPickupHours(time: string): boolean {
  return time >= PICKUP_OPENS && time <= PICKUP_CLOSES
}

export function validPhone(value: string): boolean {
  return /^0\d{9,10}$/.test(value.replace(/[\s()-]/g, ''))
}

/** A four-digit order number that depends only on the order itself. */
export function orderNumber(seed: string): string {
  let hash = 5381
  for (const char of seed) hash = ((hash * 33) ^ char.charCodeAt(0)) >>> 0
  return String(1000 + (hash % 9000))
}

export function placeOrder(
  details: { name: string; phone: string; time: string; notes: string },
  lines: OrderLine[],
  discount: number,
): PlacedOrder {
  const items = lines.map((line) => ({
    title: lineTitle(line),
    extras: lineExtras(line),
    quantity: line.quantity,
    price: line.unitPrice * line.quantity,
  }))
  const subtotal = items.reduce((sum, item) => sum + item.price, 0)
  const order: PlacedOrder = {
    ...details,
    number: orderNumber(JSON.stringify([details.name, details.phone, details.time, items])),
    lines: items,
    subtotal,
    discount,
    total: Math.max(0, subtotal - discount),
  }
  sessionStorage.setItem(LAST_ORDER_KEY, JSON.stringify(order))
  return order
}

export function lastOrder(): PlacedOrder | null {
  try {
    return JSON.parse(sessionStorage.getItem(LAST_ORDER_KEY) ?? 'null')
  } catch {
    return null
  }
}
