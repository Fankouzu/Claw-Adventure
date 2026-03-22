interface SkeletonProps {
  variant?: 'text' | 'card' | 'avatar' | 'button'
  width?: string | number
  height?: string | number
  className?: string
  style?: React.CSSProperties
}

export default function Skeleton({
  variant = 'text',
  width,
  height,
  className = '',
  style,
}: SkeletonProps) {
  const baseStyles: React.CSSProperties = {
    background: 'linear-gradient(90deg, #27272a 25%, #3f3f46 50%, #27272a 75%)',
    backgroundSize: '200% 100%',
    animation: 'skeleton-loading 1.5s infinite',
    borderRadius: '4px',
  }

  const variantStyles: Record<string, React.CSSProperties> = {
    text: { height: height || '1em', width: width || '100%' },
    card: { height: height || '120px', width: width || '100%', borderRadius: '12px' },
    avatar: { height: height || '40px', width: width || '40px', borderRadius: '50%' },
    button: { height: height || '40px', width: width || '100px', borderRadius: '8px' },
  }

  return (
    <div
      className={`skeleton ${className}`}
      style={{ ...baseStyles, ...variantStyles[variant], ...style }}
      aria-busy="true"
      aria-live="polite"
    />
  )
}

// Dashboard specific skeleton components
export function DashboardSkeleton() {
  return (
    <div className="container">
      <div className="card" style={{ padding: '30px' }}>
        {/* Header skeleton */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
          <Skeleton variant="text" width="200px" height="24px" />
          <Skeleton variant="button" width="80px" />
        </div>

        {/* User info skeleton */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '24px',
          paddingBottom: '16px',
          borderBottom: '1px solid #3f3f46',
        }}>
          <Skeleton variant="text" width="250px" height="20px" />
          <Skeleton variant="button" width="80px" />
        </div>

        {/* Agents list skeleton */}
        <div style={{ display: 'grid', gap: '16px', marginTop: '24px' }}>
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              style={{
                background: 'linear-gradient(135deg, #1f1f23, #27272a)',
                border: '1px solid #3f3f46',
                borderRadius: '12px',
                padding: '20px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div>
                <Skeleton variant="text" width="150px" height="20px" />
                <div style={{ display: 'flex', gap: '24px', marginTop: '12px' }}>
                  <Skeleton variant="text" width="60px" height="16px" />
                  <Skeleton variant="text" width="60px" height="16px" />
                </div>
              </div>
              <Skeleton variant="button" width="80px" height="24px" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Claim page skeleton
export function ClaimSkeleton() {
  return (
    <div className="container">
      <div className="card" style={{ padding: '30px' }}>
        {/* Header skeleton */}
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <Skeleton variant="text" width="200px" height="28px" style={{ margin: '0 auto' }} />
        </div>

        {/* Agent info box skeleton */}
        <div style={{
          background: 'rgba(0, 0, 0, 0.6)',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #27272a',
        }}>
          <Skeleton variant="text" width="300px" height="16px" />
          <div style={{ marginTop: '8px' }}>
            <Skeleton variant="text" width="200px" height="16px" />
          </div>
        </div>

        {/* Steps skeleton */}
        {[1, 2].map((i) => (
          <div
            key={i}
            style={{
              margin: '20px 0',
              padding: '15px',
              background: 'rgba(249, 115, 22, 0.1)',
              borderRadius: '8px',
              borderLeft: '4px solid #f97316',
            }}
          >
            <Skeleton variant="button" width="60px" height="24px" />
            <div style={{ marginTop: '10px' }}>
              <Skeleton variant="text" width="100%" height="16px" />
              <Skeleton variant="text" width="80%" height="16px" style={{ marginTop: '8px' }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}