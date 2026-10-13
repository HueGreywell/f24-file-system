import { useCallback, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import type { Toast, ToastVariant } from '../../types/toast'
import { ToastContext, type ToastContextValue } from './ToastContext'
import { ToastViewport } from './ToastViewport'

const TOAST_DURATION_MS = 5000

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const nextIdRef = useRef(0)

  const dismiss = useCallback((id: number) => {
    setToasts((current) => current.filter((toast) => toast.id !== id))
  }, [])

  const push = useCallback(
    (variant: ToastVariant, message: string) => {
      const id = ++nextIdRef.current
      setToasts((current) => [...current, { id, message, variant }])
      setTimeout(() => dismiss(id), TOAST_DURATION_MS)
    },
    [dismiss],
  )

  const value = useMemo<ToastContextValue>(
    () => ({
      error: (message: string) => push('error', message),
      info: (message: string) => push('info', message),
      success: (message: string) => push('success', message),
    }),
    [push],
  )

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastViewport toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  )
}
