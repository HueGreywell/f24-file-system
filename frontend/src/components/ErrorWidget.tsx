interface ErrorWidgetProps {
  message: string
  onRetry: () => void
}

export function ErrorWidget({ message, onRetry }: ErrorWidgetProps) {
  return (
    <div className="error-widget">
      <p>{message}</p>
      <button type="button" onClick={onRetry}>
        Retry
      </button>
    </div>
  )
}
