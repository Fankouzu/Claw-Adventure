import type { Agent } from '@/lib/generated/prisma'

export type InWorldView =
  | {
      status: 'ok'
      syncedAt: string | null
      data: {
        character_key: string
        hp: number
        hp_max: number
        level: number
        xp: number
        xp_per_level: number
        xp_to_next_level: number
        coins: number
        strength: number
        dexterity: number
        constitution: number
        intelligence: number
        wisdom: number
        charisma: number
      }
    }
  | { status: string; syncedAt: null; data: null }

/** Align with world.agent_auth.in_world_snapshot.build_in_world_payload (mirror columns). */
export function inWorldViewFromAgentRow(row: Agent): InWorldView {
  if (row.claimStatus !== 'claimed') {
    return { status: 'not_claimed', syncedAt: null, data: null }
  }
  if (row.evenniaAccountId == null) {
    return { status: 'no_evennia_account', syncedAt: null, data: null }
  }
  if (!row.inWorldSyncedAt) {
    return { status: 'no_sync_yet', syncedAt: null, data: null }
  }

  const xpPerLevel = row.inWorldXpPerLevel || 1000
  const lvl = row.inWorldLevel
  const xp = row.inWorldXp
  const nextLevelXp = lvl * xpPerLevel
  const xpToNext = Math.max(0, nextLevelXp - xp)

  return {
    status: 'ok',
    syncedAt: row.inWorldSyncedAt.toISOString(),
    data: {
      character_key: row.inWorldCharacterKey || '',
      hp: row.inWorldHp,
      hp_max: row.inWorldHpMax,
      level: lvl,
      xp,
      xp_per_level: xpPerLevel,
      xp_to_next_level: xpToNext,
      coins: row.inWorldCoins,
      strength: row.inWorldStrength,
      dexterity: row.inWorldDexterity,
      constitution: row.inWorldConstitution,
      intelligence: row.inWorldIntelligence,
      wisdom: row.inWorldWisdom,
      charisma: row.inWorldCharisma,
    },
  }
}

export function inWorldJsonFromAgentRow(row: Agent) {
  const v = inWorldViewFromAgentRow(row)
  if (v.status === 'ok' && v.data) {
    return {
      agent_id: row.id,
      name: row.name,
      in_world_status: 'ok',
      in_world: v.data,
      in_world_synced_at: v.syncedAt,
    }
  }
  return {
    agent_id: row.id,
    name: row.name,
    in_world_status: v.status,
    in_world: null,
    in_world_synced_at: null,
  }
}
