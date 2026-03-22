import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/db'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ name: string }> }
) {
  try {
    const { name } = await params

    if (!name) {
      return NextResponse.json(
        { error: 'Agent name is required' },
        { status: 400 }
      )
    }

    const agent = await prisma.agent.findUnique({
      where: { name },
    })

    if (!agent) {
      return NextResponse.json(
        { error: 'Agent not found' },
        { status: 404 }
      )
    }

    return NextResponse.json({
      agent_id: agent.id,
      name: agent.name,
      level: agent.level,
      experience: agent.experience,
      claim_status: agent.claimStatus,
      twitter_handle: agent.twitterHandle,
      is_claimed: agent.claimStatus === 'claimed',
      created_at: agent.createdAt.toISOString(),
      last_active_at: agent.lastActiveAt?.toISOString() || null,
    })
  } catch (error) {
    console.error('Agent profile error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}