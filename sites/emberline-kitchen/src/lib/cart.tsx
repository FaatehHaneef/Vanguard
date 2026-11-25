import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { dishBySlug, sizes, type SizeId } from '../data/menu'

export interface OrderLine {
  key: string
  slug: string
  size?: SizeId
  spice?: string
  extras: string[]
  quantity: number
  unitPrice: number // pence, size and extras included
}

const STORAGE_KEY = 'emberline-order'
export const MAX_QUANTITY = 20

function load(): OrderLine[] {
  try {
    const saved = JSON.parse(sessionStorage.getItem(STORAGE_KEY) ?? '[]')
    return Array.isArray(saved) ? saved : []
  } catch {
    return []
  }
}

/** "Chicken Karahi · Large · Hot": the dish with its size and spice level. */
export function lineTitle(line: OrderLine): string {
  const dish = dishBySlug(line.slug)
  if (!dish) return line.slug
  const parts = [dish.name]
  if (dish.sizes && line.size) parts.push(sizes.find((s) => s.id === line.size)?.name ?? '')
  if (line.spice) parts.push(line.spice)
  return parts.filter(Boolean).join(' · ')
}

/** "With cucumber raita and fried green chillies", or an empty string. */
export function lineExtras(line: OrderLine): string {
  const dish = dishBySlug(line.slug)
  const names = line.extras
    .map((id) => dish?.extras?.find((extra) => extra.id === id)?.name.toLowerCase())
    .filter(Boolean) as string[]
  if (!names.length) return ''
  const list = names.length > 1 ? `${names.slice(0, -1).join(', ')} and ${names.at(-1)}` : names[0]
  return `With ${list}`
}

interface CartValue {
  lines: OrderLine[]
  count: number
  subtotal: number
  add: (line: Omit<OrderLine, 'key'>) => void
  setQuantity: (key: string, quantity: number) => void
  remove: (key: string) => void
  clear: () => void
  drawerOpen: boolean
  openDrawer: () => void
  closeDrawer: () => void
}

const CartContext = createContext<CartValue | null>(null)

export function CartProvider({ children }: { children: ReactNode }) {
  const [lines, setLines] = useState<OrderLine[]>(load)
  const [drawerOpen, setDrawerOpen] = useState(false)

  useEffect(() => {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(lines))
  }, [lines])

  const add = useCallback((line: Omit<OrderLine, 'key'>) => {
    const key = [line.slug, line.size ?? '', line.spice ?? '', [...line.extras].sort().join('+')].join('|')
    setLines((current) => {
      const existing = current.find((item) => item.key === key)
      if (existing) {
        return current.map((item) =>
          item.key === key
            ? { ...item, quantity: Math.min(MAX_QUANTITY, item.quantity + line.quantity) }
            : item,
        )
      }
      return [...current, { ...line, key }]
    })
  }, [])

  const setQuantity = useCallback((key: string, quantity: number) => {
    setLines((current) =>
      quantity <= 0
        ? current.filter((item) => item.key !== key)
        : current.map((item) =>
            item.key === key ? { ...item, quantity: Math.min(MAX_QUANTITY, quantity) } : item,
          ),
    )
  }, [])

  const openDrawer = useCallback(() => setDrawerOpen(true), [])
  const closeDrawer = useCallback(() => setDrawerOpen(false), [])

  const value = useMemo<CartValue>(
    () => ({
      lines,
      count: lines.reduce((sum, line) => sum + line.quantity, 0),
      subtotal: lines.reduce((sum, line) => sum + line.quantity * line.unitPrice, 0),
      add,
      setQuantity,
      remove: (key) => setLines((current) => current.filter((item) => item.key !== key)),
      clear: () => setLines([]),
      drawerOpen,
      openDrawer,
      closeDrawer,
    }),
    [lines, add, setQuantity, drawerOpen, openDrawer, closeDrawer],
  )

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}

export function useCart(): CartValue {
  const value = useContext(CartContext)
  if (!value) throw new Error('useCart outside CartProvider')
  return value
}
