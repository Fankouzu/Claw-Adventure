import { headers } from 'next/headers'

/** Response shape from Django agent_in_world_by_name_api / Next proxy. */
export type InWorldSnapshot = {
  agent_id: string
  name: string
  in_world_status: string
  in_world: {
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
  } | null
}

function trimBase(url: string) {
  return url.replace(/\/$/, '')
}

/**
 * Load live EvAdventure stats for an agent name (server-only).
 * Prefer CLAW_EVENNIA_API_URL (Evennia service) in production; else same-origin /api proxy.
 */
export async function fetchInWorldSnapshot(
  agentName: string,
): Promise<InWorldSnapshot | null> {
  const evennia = process.env.CLAW_EVENNIA_API_URL
  const path = `api/agents/name/${encodeURIComponent(agentName)}/in-world`

  if (evennia) {
    const url = `${trimBase(evennia)}/${path}`
    try {
      const res = await fetch(url, { next: { revalidate: 20 } })
      if (!res.ok) return null
      return (await res.json()) as InWorldSnapshot
    } catch {
      return null
    }
  }

  try {
    const h = await headers()
    const host = h.get('x-forwarded-host') || h.get('host')
    const proto = h.get('x-forwarded-proto') || 'http'
    if (!host) return null
    const url = `${proto}://${host}/api/agents/${encodeURIComponent(agentName)}/in-world`
    const res = await fetch(url, { cache: 'no-store' })
    if (!res.ok) return null
    return (await res.json()) as InWorldSnapshot
  } catch {
    return null
  }
}
