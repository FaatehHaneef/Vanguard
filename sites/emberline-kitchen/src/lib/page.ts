import { useEffect, useRef } from 'react'

const SITE = 'Emberline Kitchen'
let firstPage = true

/**
 * Sets the document title and, after client-side navigation, moves keyboard focus
 * to the page's main heading, as a fresh page load starts at the top of the page.
 */
export function usePage(title: string, keepFocus = false) {
  const heading = useRef<HTMLHeadingElement>(null)
  useEffect(() => {
    document.title = title ? `${title} · ${SITE}` : `${SITE} · Pickup from the coals`
    if (firstPage) {
      firstPage = false
      return
    }
    if (!keepFocus) heading.current?.focus({ preventScroll: true })
  }, [title])
  return heading
}
