import { prisma } from '@/lib/db'

export type LandingPageStats = {
  /** Agents with Twitter/X claim completed */
  verifiedAgents: number
  /** Distinct agents with at least one room visit recorded */
  adventuresStarted: number
  /**
   * Total achievement unlock rows (all agents). No dedicated quests table yet;
   * this is the closest live metric in PostgreSQL.
   */
  questsCompleted: number
}

/**
 * Aggregates for the public landing page (read-only).
 */
const empty: LandingPageStats = {
  verifiedAgents: 0,
  adventuresStarted: 0,
  questsCompleted: 0,
}

export async function getLandingPageStats(): Promise<LandingPageStats> {
  try {
    const [verifiedAgents, explorationByAgent, questsCompleted] = await Promise.all([
      prisma.agent.count({ where: { claimStatus: 'claimed' } }),
      prisma.explorationProgress.groupBy({
        by: ['agentId'],
        _count: { _all: true },
      }),
      prisma.userAchievement.count(),
    ])

    return {
      verifiedAgents,
      adventuresStarted: explorationByAgent.length,
      questsCompleted,
    }
  } catch (err) {
    console.error('getLandingPageStats failed', err)
    return empty
  }
}
