/**
 * Static profile tiles under public/profile-assets/.
 * Drop PNGs named from slugs (see slugForProfileAsset) — no bundler import required.
 */

/** Safe filename segment for room_key or achievement.key (e.g. tut#12 → tut-12). */
export function slugForProfileAsset(raw: string): string {
  return raw
    .trim()
    .toLowerCase()
    .replace(/#/g, '-')
    .replace(/[^a-z0-9._-]/g, '_')
}

export function roomTileImageSrc(roomKey: string): string {
  return `/profile-assets/rooms/${slugForProfileAsset(roomKey)}.png`
}

export function achievementTileImageSrc(achievementKey: string): string {
  return `/profile-assets/achievements/${slugForProfileAsset(achievementKey)}.png`
}
