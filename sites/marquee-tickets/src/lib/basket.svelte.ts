import { browser } from '$app/environment'
import { eventBySlug, type Event, type TicketType } from './data/events'

export interface BasketLine {
  key: string
  slug: string
  ticket: string
  quantity: number
}

export interface Booking {
  reference: string
  name: string
  email: string
  phone: string
  delivery: 'email' | 'box-office'
  lines: { title: string; date: string; venue: string; ticket: string; quantity: number; price: number }[]
  subtotal: number
  discount: number
  total: number
}

const BASKET_KEY = 'marquee-basket'
const BOOKING_KEY = 'marquee-booking'

function read<T>(key: string, fallback: T): T {
  if (!browser) return fallback
  try {
    return JSON.parse(sessionStorage.getItem(key) ?? 'null') ?? fallback
  } catch {
    return fallback
  }
}

export function resolve(line: BasketLine): { event: Event; ticket: TicketType } | null {
  const event = eventBySlug(line.slug)
  const ticket = event?.tickets.find((t) => t.id === line.ticket)
  return event && ticket ? { event, ticket } : null
}

/** "Northern Static · 2 × Standard" */
export function lineText(line: BasketLine): string {
  const found = resolve(line)
  return found ? `${found.event.title} · ${line.quantity} × ${found.ticket.name}` : line.slug
}

class Basket {
  lines = $state<BasketLine[]>([])
  /** A one-off message for the basket page after something was added. */
  flash = $state('')

  get count(): number {
    return this.lines.reduce((sum, line) => sum + line.quantity, 0)
  }

  get subtotal(): number {
    return this.lines.reduce((sum, line) => sum + (resolve(line)?.ticket.price ?? 0) * line.quantity, 0)
  }

  /** Called once the page is running in the browser. */
  load() {
    this.lines = read<BasketLine[]>(BASKET_KEY, [])
  }

  private save() {
    sessionStorage.setItem(BASKET_KEY, JSON.stringify(this.lines))
  }

  add(slug: string, ticket: string, quantity: number) {
    const key = `${slug}|${ticket}`
    const existing = this.lines.find((line) => line.key === key)
    if (existing) existing.quantity += quantity
    else this.lines.push({ key, slug, ticket, quantity })
    this.save()
  }

  remove(key: string) {
    this.lines = this.lines.filter((line) => line.key !== key)
    this.save()
  }

  clear() {
    this.lines = []
    this.save()
  }
}

export const basket = new Basket()

function reference(seed: string): string {
  let hash = 2166136261
  for (const char of seed) hash = Math.imul(hash ^ char.charCodeAt(0), 16777619) >>> 0
  return String(100000 + (hash % 900000))
}

export function placeBooking(
  details: Pick<Booking, 'name' | 'email' | 'phone' | 'delivery'>,
  discount: number,
): Booking {
  const lines = basket.lines.flatMap((line) => {
    const found = resolve(line)
    if (!found) return []
    return [
      {
        title: found.event.title,
        date: found.event.date,
        venue: found.event.venue,
        ticket: found.ticket.name,
        quantity: line.quantity,
        price: found.ticket.price * line.quantity,
      },
    ]
  })
  const subtotal = lines.reduce((sum, line) => sum + line.price, 0)
  const booking: Booking = {
    ...details,
    reference: reference(JSON.stringify([details.name, details.email, lines])),
    lines,
    subtotal,
    discount,
    total: subtotal - discount,
  }
  sessionStorage.setItem(BOOKING_KEY, JSON.stringify(booking))
  basket.clear()
  return booking
}

export function lastBooking(): Booking | null {
  return read<Booking | null>(BOOKING_KEY, null)
}
