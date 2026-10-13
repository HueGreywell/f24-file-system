export type ToastVariant = 'error' | 'info' | 'success'

export interface Toast {
  id: number
  message: string
  variant: ToastVariant
}
