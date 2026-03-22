import { NextResponse } from 'next/server'
import { prisma } from '@/lib/db'
import { getSession } from '@/lib/session'

interface AgentData {
  id: string
  name: string
  level: number
  experience: number
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

    const agents: AgentData[] = []
    
    for (const ue of userEmails) {
      if (ue.agent) {
        agents.push({
          id: ue.agent.id,
          name: ue.agent.name,
          level: ue.agent.level,
          experience: ue.agent.experience,
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