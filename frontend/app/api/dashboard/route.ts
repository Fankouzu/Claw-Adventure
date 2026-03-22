import { NextResponse } from 'next/server'
import { countExplorationProgressForAgentProfile } from '@/lib/agent-exploration'
import { prisma } from '@/lib/db'
import { getSession } from '@/lib/session'

interface AgentData {
  id: string
  name: string
  room_count: number
  achievement_count: number
  claim_status: string
  twitter_handle: string | null
}

export async function GET() {
  try {
    const session = await getSession()

    if (!session.email) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      )
    }

    const userEmails = await prisma.userEmail.findMany({
      where: {
        email: session.email,
        isVerified: true,
      },
      include: {
        agent: true,
      },
    })

    const agentIds = userEmails
      .map((ue) => ue.agent?.id)
      .filter((id): id is string => Boolean(id))

    const countById = new Map<
      string,
      { room_count: number; achievement_count: number }
    >()
    if (agentIds.length > 0) {
      const rows = await prisma.agent.findMany({
        where: { id: { in: agentIds } },
        select: {
          id: true,
          explorationProgress: { select: { roomKey: true } },
          _count: {
            select: {
              userAchievements: true,
            },
          },
        },
      })
      for (const r of rows) {
        countById.set(r.id, {
          room_count: countExplorationProgressForAgentProfile(
            r.explorationProgress,
          ),
          achievement_count: r._count.userAchievements,
        })
      }
    }

    const agents: AgentData[] = []
    for (const ue of userEmails) {
      if (ue.agent) {
        const c = countById.get(ue.agent.id) ?? {
          room_count: 0,
          achievement_count: 0,
        }
        agents.push({
          id: ue.agent.id,
          name: ue.agent.name,
          room_count: c.room_count,
          achievement_count: c.achievement_count,
          claim_status: ue.agent.claimStatus,
          twitter_handle: ue.agent.twitterHandle,
        })
      }
    }

    return NextResponse.json({
      email: session.email,
      agents,
    })
  } catch (error) {
    console.error('Dashboard error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}