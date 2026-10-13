import { createContext } from 'react'

export interface ToastContextValue {
  error: (message: string) => void
  info: (message: string) => void
  success: (message: string) => void
}

export const ToastContext = createContext<ToastContextValue | null>(null)
