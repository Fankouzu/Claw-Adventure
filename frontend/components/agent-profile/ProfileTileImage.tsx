'use client'

import { useMemo, useState } from 'react'

type ProfileTileImageProps = {
  /** Single URL (e.g. achievements). */
  src?: string
  /** Try each URL in order until one loads (e.g. room tile alias fallbacks). */
  srcCandidates?: string[]
  alt: string
  /** Shown inside the placeholder when no image loads */
  fallbackLabel?: string
}

const TILE = 100

function normalizeCandidates(
  src: string | undefined,
  srcCandidates: string[] | undefined,
): string[] {
  if (srcCandidates?.length) {
    return srcCandidates
  }
  if (src) {
    return [src]
  }
  return []
}

/**
 * 100×100 tile; cycles through srcCandidates on error until one works or shows placeholder.
 */
export function ProfileTileImage({
  src,
  srcCandidates,
  alt,
  fallbackLabel,
}: ProfileTileImageProps) {
  const candidates = useMemo(
    () => normalizeCandidates(src, srcCandidates),
    [src, srcCandidates],
  )
  const [attempt, setAttempt] = useState(0)
  const [dead, setDead] = useState(candidates.length === 0)

  if (dead || attempt >= candidates.length) {
    return (
      <div
        className="profile-tile-placeholder"
        style={{
          width: TILE,
          height: TILE,
          borderRadius: 8,
          background: 'linear-gradient(145deg, #3f3f46 0%, #27272a 100%)',
          border: '1px solid #52525b',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#a1a1aa',
          fontSize: 11,
          textAlign: 'center',
          padding: 6,
          lineHeight: 1.2,
          wordBreak: 'break-word',
        }}
        aria-label={alt}
      >
        {fallbackLabel ?? '…'}
      </div>
    )
  }

  const currentSrc = candidates[attempt]

  return (
    // eslint-disable-next-line @next/next/no-img-element -- public static tiles; avoid next/image quirks
    <img
      key={currentSrc}
      src={currentSrc}
      alt={alt}
      width={TILE}
      height={TILE}
      className="profile-tile-image"
      loading="lazy"
      decoding="async"
      style={{
        width: TILE,
        height: TILE,
        objectFit: 'cover',
        borderRadius: 8,
        border: '1px solid #3f3f46',
      }}
      onError={() => {
        if (attempt + 1 < candidates.length) {
          setAttempt((a) => a + 1)
        } else {
          setDead(true)
        }
      }}
    />
  )
}
