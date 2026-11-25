import { type RefObject, useEffect } from 'react'

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'

/**
 * While `active`, keeps Tab and Shift+Tab inside `container`, closes on Escape, stops the
 * page behind from scrolling and, when it closes, returns focus to where it was (or to
 * `fallback()` when that element has gone).
 */
export function useFocusTrap(
  container: RefObject<HTMLElement | null>,
  active: boolean,
  onClose: () => void,
  fallback?: () => HTMLElement | null,
) {
  useEffect(() => {
    if (!active) return
    const before = document.activeElement as HTMLElement | null
    const node = container.current
    const first = node?.querySelector<HTMLElement>('[data-autofocus]') ?? node
    first?.focus()
    document.body.classList.add('is-locked')

    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault()
        onClose()
        return
      }
      if (event.key !== 'Tab' || !node) return
      const items = Array.from(node.querySelectorAll<HTMLElement>(FOCUSABLE)).filter(
        (item) => item.offsetParent !== null,
      )
      if (!items.length) return
      const firstItem = items[0]
      const lastItem = items[items.length - 1]
      if (event.shiftKey && (document.activeElement === firstItem || document.activeElement === node)) {
        event.preventDefault()
        lastItem.focus()
      } else if (!event.shiftKey && document.activeElement === lastItem) {
        event.preventDefault()
        firstItem.focus()
      }
    }
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.classList.remove('is-locked')
      const target = before && before !== document.body && before.isConnected ? before : fallback?.()
      target?.focus({ preventScroll: true })
    }
    // onClose and fallback are read when the trap opens.
  }, [active])
}
