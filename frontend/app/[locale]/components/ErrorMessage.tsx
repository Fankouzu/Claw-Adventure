'use client'

interface ErrorMessageProps {
  message: string
  onRetry?: () => void
  retryText?: string
  backLink?: {
    href: string
    text: string
  }
}

export default function ErrorMessage({
  message,
  onRetry,
  retryText = 'Retry',
  backLink,
}: ErrorMessageProps) {
  return (
    <div
      role="alert"
      style={{
        background: 'rgba(239, 68, 68, 0.1)',
        border: '1px solid #ef4444',
        borderRadius: '8px',
        padding: '16px',
        color: '#fca5a5',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          style={{ width: '20px', height: '20px', flexShrink: 0, marginTop: '2px' }}
          aria-label="Error"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
        <div style={{ flex: 1 }}>
          <p style={{ margin: 0, fontWeight: 500 }}>{message}</p>
          {(onRetry || backLink) && (
            <div style={{ marginTop: '12px', display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              {onRetry && (
                <button
                  onClick={onRetry}
                  style={{
                    background: 'transparent',
                    border: '1px solid #ef4444',
                    color: '#fca5a5',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    fontSize: '14px',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                  }}
                >
                  {retryText}
                </button>
              )}
              {backLink && (
                <a
                  href={backLink.href}
                  style={{
                    color: '#a1a1aa',
                    textDecoration: 'none',
                    fontSize: '14px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  ← {backLink.text}
                </a>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}