/**
 * Static profile tiles under public/profile-assets/.
 * Files use slugForProfileAsset(room_key) as basename; extension may be .png, .jpeg, .jpg, or .webp.
 */

/** Safe filename segment for room_key or achievement.key (e.g. tut#12 → tut-12). */
export function slugForProfileAsset(raw: string): string {
  return raw
    .trim()
    .toLowerCase()
    .replace(/#/g, '-')
    .replace(/[^a-z0-9._-]/g, '_')
}

const TILE_EXTENSIONS = ['.png', '.jpeg', '.jpg', '.webp'] as const

function tileCandidates(
  folder: 'rooms' | 'achievements',
  rawKey: string,
): string[] {
  const slug = slugForProfileAsset(rawKey)
  const base = `/profile-assets/${folder}/${slug}`
  return TILE_EXTENSIONS.map((ext) => `${base}${ext}`)
}

/** Ordered URLs to pass as ProfileTileImage srcCandidates (room tiles). */
export function roomTileImageCandidates(roomKey: string): string[] {
  return tileCandidates('rooms', roomKey)
}

/** @deprecated Prefer roomTileImageCandidates + ProfileTileImage for multi-extension support. */
export function roomTileImageSrc(roomKey: string): string {
  return `/profile-assets/rooms/${slugForProfileAsset(roomKey)}.png`
}

export function achievementTileImageCandidates(achievementKey: string): string[] {
  return tileCandidates('achievements', achievementKey)
}

/** @deprecated Prefer achievementTileImageCandidates when assets may not be PNG-only. */
export function achievementTileImageSrc(achievementKey: string): string {
  return `/profile-assets/achievements/${slugForProfileAsset(achievementKey)}.png`
}
