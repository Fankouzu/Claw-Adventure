/**
 * Static profile tiles under public/profile-assets/.
 * Room tiles use .jpeg only; basename is derived from room_key / room_name with
 * tutorial alias support (tut#NN → snake_case asset names).
 */

const ROOM_TILE_EXT = '.jpeg' as const

/**
 * Evennia tutorial_world assigns tut#NN aliases; exploration may store either the
 * primary db_key (e.g. "Cliff by the coast") or the alias ("tut#02"). Map tut#NN to
 * the basename of files in public/profile-assets/rooms/.
 */
const TUTORIAL_ROOM_KEY_TO_SLUG: Record<string, string> = {
  'tut#01': 'intro',
  'tut#02': 'cliff_by_the_coast',
  'tut#03': 'outside_dragon_inn',
  'tut#04': 'the_dragon_inn',
  'tut#05': 'the_old_bridge',
  'tut#06': 'protruding_ledge',
  'tut#07': 'underground_passages',
  'tut#08': 'dark_cell',
  'tut#09': 'ruined_gatehouse',
  'tut#10': 'along_inner_wall',
  'tut#11': 'corner_of_castle_ruins',
  'tut#12': 'overgrown_courtyard',
  'tut#13': 'the_ruined_temple',
  'tut#14': 'antechamber',
  'tut#15': 'ancient_tomb',
  'tut#16': 'end_of_adventure',
}

/** Room image basename for a tut#NN key, if defined (for profile slot matching). */
export function tutorialRoomKeyToProfileBasename(roomKey: string): string | undefined {
  return TUTORIAL_ROOM_KEY_TO_SLUG[roomKey.trim().toLowerCase()]
}

/** Stock tutorial display keys → asset basenames (Claw uses rebranded room names in files). */
const ROOM_KEY_ALIAS_SLUG: Record<string, string> = {
  'outside evennia inn': 'outside_dragon_inn',
  'the evennia inn': 'the_dragon_inn',
  'end of tutorial': 'end_of_adventure',
}

/** Safe filename segment for room_key or achievement.key (e.g. tut#12 → tut-12). */
export function slugForProfileAsset(raw: string): string {
  return raw
    .trim()
    .toLowerCase()
    .replace(/#/g, '-')
    .replace(/[^a-z0-9._-]/g, '_')
}

function addUnique(list: string[], value: string) {
  const v = value.trim()
  if (v && !list.includes(v)) {
    list.push(v)
  }
}

/**
 * Basenames (no extension) for room profile images, in try order.
 */
export function profileRoomImageBasenames(
  roomKey: string,
  roomName?: string,
): string[] {
  const basenames: string[] = []
  const k = roomKey.trim()
  const lower = k.toLowerCase()

  const tutSlug = TUTORIAL_ROOM_KEY_TO_SLUG[lower]
  if (tutSlug) {
    addUnique(basenames, tutSlug)
  }

  const aliasSlug = ROOM_KEY_ALIAS_SLUG[lower]
  if (aliasSlug) {
    addUnique(basenames, aliasSlug)
  }

  if (!/^tut#\d+$/i.test(k)) {
    addUnique(basenames, slugForProfileAsset(k))
  }

  const name = roomName?.trim()
  if (name) {
    const nl = name.toLowerCase()
    const nameAlias = ROOM_KEY_ALIAS_SLUG[nl]
    if (nameAlias) {
      addUnique(basenames, nameAlias)
    }
    const nameSlug = slugForProfileAsset(name)
    if (nameSlug !== slugForProfileAsset(k)) {
      addUnique(basenames, nameSlug)
    }
  }

  return basenames
}

/** URLs to pass as ProfileTileImage srcCandidates (room tiles, .jpeg only). */
export function roomTileImageCandidates(
  roomKey: string,
  roomName?: string,
): string[] {
  return profileRoomImageBasenames(roomKey, roomName).map(
    (b) => `/profile-assets/rooms/${b}${ROOM_TILE_EXT}`,
  )
}

/** @deprecated Use roomTileImageCandidates + ProfileTileImage. */
export function roomTileImageSrc(roomKey: string): string {
  const [first] = profileRoomImageBasenames(roomKey)
  const base = first ?? slugForProfileAsset(roomKey)
  return `/profile-assets/rooms/${base}${ROOM_TILE_EXT}`
}

const ACHIEVEMENT_EXT = ROOM_TILE_EXT

function achievementBasenames(rawKey: string): string[] {
  return [slugForProfileAsset(rawKey)]
}

export function achievementTileImageCandidates(achievementKey: string): string[] {
  return achievementBasenames(achievementKey).map(
    (b) => `/profile-assets/achievements/${b}${ACHIEVEMENT_EXT}`,
  )
}

/** @deprecated Prefer achievementTileImageCandidates when assets exist. */
export function achievementTileImageSrc(achievementKey: string): string {
  return `/profile-assets/achievements/${slugForProfileAsset(achievementKey)}${ACHIEVEMENT_EXT}`
}

/** Placeholder tile for unexplored rooms / locked achievements on agent profile. */
export const PROFILE_NO_IMAGE_SRC = '/profile-assets/no_image.jpeg'
