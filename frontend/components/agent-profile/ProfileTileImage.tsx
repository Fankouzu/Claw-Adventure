'use client'

import Image from 'next/image'
import { useState } from 'react'

type ProfileTileImageProps = {
  src: string
  alt: string
  /** Shown inside the placeholder when the image file is missing */
  fallbackLabel?: string
}

const TILE = 100

/**
 * 100×100 tile; on missing asset shows a neutral placeholder (add PNG under public/ later).
 */
export function ProfileTileImage({ src, alt, fallbackLabel }: ProfileTileImageProps) {
  const [failed, setFailed] = useState(false)

  if (failed) {
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

  return (
    <Image
      src={src}
      alt={alt}
      width={TILE}
      height={TILE}
      className="profile-tile-image"
      style={{
        width: TILE,
        height: TILE,
        objectFit: 'cover',
        borderRadius: 8,
        border: '1px solid #3f3f46',
      }}
      unoptimized
      onError={() => setFailed(true)}
    />
  )
}
