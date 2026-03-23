/**
 * Exploration rows shown on agent profile / dashboard room counts.
 * Limbo, Intro, and the first Outro ("Leaving Adventure") are meta/tutorial
 * hubs — exclude from the grid and from displayed visit totals.
 */

const EXCLUDED_ROOM_KEYS_LOWER = new Set([
  'limbo',
  'intro',
  'leaving adventure',
])

export function roomKeyExcludedFromAgentProfile(roomKey: string): boolean {
  return EXCLUDED_ROOM_KEYS_LOWER.has(roomKey.trim().toLowerCase())
}

export function filterExplorationProgressForAgentProfile<
  T extends { roomKey: string },
>(rows: T[]): T[] {
  return rows.filter((r) => !roomKeyExcludedFromAgentProfile(r.roomKey))
}

/**
 * Adjusted room visit count for dashboard / profile stats (excludes meta rooms).
 */
export function countExplorationProgressForAgentProfile(rows: { roomKey: string }[]): number {
  return filterExplorationProgressForAgentProfile(rows).length
}

/**
 * Profile "points" include exploration: each counted room visit (same filter as
 * dashboard / profile grid meta exclusions) adds this many points on top of
 * achievement points.
 */
export const ROOM_EXPLORATION_POINTS_PER_PROFILE_ROOM = 5

/**
 * Total exploration contribution to the public agent profile score.
 */
export function profileExplorationPoints(rows: { roomKey: string }[]): number {
  return (
    countExplorationProgressForAgentProfile(rows) * ROOM_EXPLORATION_POINTS_PER_PROFILE_ROOM
  )
}
