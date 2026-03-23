/**
 * Fixed grid of explorable rooms (20) and achievements (16) on the public agent profile.
 * Matches world tutorial rooms excluding Limbo / Intro / Leaving Adventure, and
 * world/achievements/data.py ALL_ACHIEVEMENTS order.
 */

import { slugForProfileAsset, tutorialRoomKeyToProfileBasename } from '@/lib/profile-assets'

/** Canonical Evennia db_key strings for the 20 tutorial rooms shown on the profile grid. */
export const AGENT_PROFILE_ROOM_ORDER = [
  'Cliff by the coast',
  'Outside Dragon Inn',
  'The Dragon Inn',
  'The old bridge',
  'Protruding ledge',
  'Underground passages',
  'Dark cell',
  'Ruined gatehouse',
  'Along inner wall',
  'Corner of castle ruins',
  'Overgrown courtyard',
  'The ruined temple',
  'Antechamber',
  'Blue bird tomb',
  'Tomb of woman on horse',
  'Tomb of the crowned queen',
  'Tomb of the shield',
  'Tomb of the hero',
  'Ancient tomb',
  'End of adventure',
] as const

export const AGENT_PROFILE_ROOM_TOTAL = AGENT_PROFILE_ROOM_ORDER.length

const VISIT_KEY_TO_CANONICAL: Record<string, (typeof AGENT_PROFILE_ROOM_ORDER)[number]> = {
  'outside evennia inn': 'Outside Dragon Inn',
  'the evennia inn': 'The Dragon Inn',
  'end of tutorial': 'End of adventure',
}

export type ExplorationRow = {
  id: string
  roomKey: string
  roomName: string
  visitedAt?: Date
}

/**
 * Map a DB exploration row to one of AGENT_PROFILE_ROOM_ORDER, or null if outside the grid.
 */
export function resolveExplorationToProfileCanonicalRoom(
  roomKey: string,
  roomName: string,
): (typeof AGENT_PROFILE_ROOM_ORDER)[number] | null {
  const k = roomKey.trim()
  const n = roomName.trim()
  const kl = k.toLowerCase()
  const nl = n.toLowerCase()

  const tutBasename = tutorialRoomKeyToProfileBasename(k)
  if (tutBasename) {
    const hit = AGENT_PROFILE_ROOM_ORDER.find(
      (c) => slugForProfileAsset(c) === tutBasename,
    )
    if (hit) {
      return hit
    }
  }

  const aliasK = VISIT_KEY_TO_CANONICAL[kl]
  if (aliasK) {
    return aliasK
  }
  const aliasN = VISIT_KEY_TO_CANONICAL[nl]
  if (aliasN) {
    return aliasN
  }

  const directK = AGENT_PROFILE_ROOM_ORDER.find((c) => c.toLowerCase() === kl)
  if (directK) {
    return directK
  }
  const directN = AGENT_PROFILE_ROOM_ORDER.find((c) => c.toLowerCase() === nl)
  if (directN) {
    return directN
  }

  return null
}

export type RoomSlotVisited<T extends ExplorationRow> = {
  kind: 'visited'
  canonical: (typeof AGENT_PROFILE_ROOM_ORDER)[number]
  row: T
}

export type RoomSlotLocked = {
  kind: 'locked'
  canonical: (typeof AGENT_PROFILE_ROOM_ORDER)[number]
}

export function buildAgentProfileRoomSlots<T extends ExplorationRow>(
  visitsFiltered: T[],
): { slots: Array<RoomSlotVisited<T> | RoomSlotLocked>; orphans: T[] } {
  const sorted = [...visitsFiltered].sort((a, b) => {
    const ta = a.visitedAt ? new Date(a.visitedAt).getTime() : 0
    const tb = b.visitedAt ? new Date(b.visitedAt).getTime() : 0
    return ta - tb
  })
  const pool = [...sorted]

  const slots: Array<RoomSlotVisited<T> | RoomSlotLocked> = AGENT_PROFILE_ROOM_ORDER.map(
    (canonical) => {
      const idx = pool.findIndex(
        (v) =>
          resolveExplorationToProfileCanonicalRoom(v.roomKey, v.roomName) ===
          canonical,
      )
      if (idx >= 0) {
        const [row] = pool.splice(idx, 1)
        return { kind: 'visited', canonical, row }
      }
      return { kind: 'locked', canonical }
    },
  )

  return { slots, orphans: pool }
}

/** Achievement keys in load order (QUEST_ACHIEVEMENTS + HIDDEN + COMBAT). */
export const AGENT_PROFILE_ACHIEVEMENT_KEY_ORDER = [
  'first_steps',
  'cliff_explorer',
  'bridge_crosser',
  'dark_survivor',
  'gatehouse_visitor',
  'temple_visitor',
  'puzzle_solver',
  'tomb_finder',
  'ghost_slayer',
  'adventure_complete',
  'explorer_master',
  'secret_finder',
  'speedrunner',
  'first_blood',
  'monster_hunter',
  'ghostbane',
] as const

export const AGENT_PROFILE_ACHIEVEMENT_TOTAL =
  AGENT_PROFILE_ACHIEVEMENT_KEY_ORDER.length

export type AchievementRow = {
  id: string
  key: string
  name: string
  points: number
  isHidden: boolean
}

export type UserAchievementRow = {
  id: string
  achievementId: string
  achievement: AchievementRow
}

export type AchievementSlotUnlocked = {
  kind: 'unlocked'
  ua: UserAchievementRow
}

export type AchievementSlotLocked = {
  kind: 'locked'
  achievementKey: string
}

export function buildAgentProfileAchievementSlots(
  allAchievements: AchievementRow[],
  userAchievements: UserAchievementRow[],
): Array<AchievementSlotUnlocked | AchievementSlotLocked> {
  const uaByKey = new Map(
    userAchievements.map((ua) => [ua.achievement.key, ua]),
  )

  const orderedKeys = new Set<string>(AGENT_PROFILE_ACHIEVEMENT_KEY_ORDER)
  const extraKeys = allAchievements
    .map((a) => a.key)
    .filter((k) => !orderedKeys.has(k))
    .sort((a, b) => a.localeCompare(b))

  const keys = [...AGENT_PROFILE_ACHIEVEMENT_KEY_ORDER, ...extraKeys]

  return keys.map((achievementKey) => {
    const ua = uaByKey.get(achievementKey)
    if (ua) {
      return { kind: 'unlocked' as const, ua }
    }
    return { kind: 'locked' as const, achievementKey }
  })
}
