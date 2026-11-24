import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { useLocation } from 'react-router'
import { Icon } from '../components/Icon'

export interface Toast {
  id: number
  title: string
  message: string
  tone: 'info' | 'error'
}

interface ToastValue {
  show: (toast: Omit<Toast, 'id'>) => void
  clear: () => void
}

const ToastContext = createContext<ToastValue | null>(null)
let nextId = 1

/** Notifications in the bottom-right corner. They stay until dismissed or the page changes. */
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const { pathname } = useLocation()

  const show = useCallback(
    (toast: Omit<Toast, 'id'>) => setToasts((current) => [...current.slice(-2), { ...toast, id: nextId++ }]),
    [],
  )
  const clear = useCallback(() => setToasts([]), [])
  useEffect(() => clear(), [pathname, clear])

  const value = useMemo(() => ({ show, clear }), [show, clear])
  return (
    <ToastContext.Provider value={value}>
      {children}
      <ol className="toasts">
        {toasts.map((toast) => (
          <li
            key={toast.id}
            className={`toast toast--${toast.tone}`}
            role={toast.tone === 'error' ? 'alert' : 'status'}
          >
            <p>
              <strong>{toast.title}</strong>
              {toast.message}
            </p>
            <button
              type="button"
              className="icon-btn"
              aria-label="Dismiss"
              onClick={() => setToasts((current) => current.filter((item) => item.id !== toast.id))}
            >
              <Icon name="close" />
            </button>
          </li>
        ))}
      </ol>
    </ToastContext.Provider>
  )
}

export function useToast(): ToastValue {
  const value = useContext(ToastContext)
  if (!value) throw new Error('useToast outside ToastProvider')
  return value
}
