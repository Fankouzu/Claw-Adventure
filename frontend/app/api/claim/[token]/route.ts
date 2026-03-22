import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/db'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ token: string }> }
) {
  try {
    const { token } = await params

    if (!token) {
      return NextResponse.json(
        { error: 'Missing claim token' },
        { status: 400 }
      )
    }

    // Validate token format (should be base64url, min 20 chars)
    if (token.length < 20 || !/^[A-Za-z0-9_-]+$/.test(token)) {
      return NextResponse.json(
        { error: 'Invalid claim token format' },
        { status: 400 }
      )
    }

    const agent = await prisma.agent.findUnique({
      where: { claimToken: token },
    })

    if (!agent) {
      return NextResponse.json(
        { error: 'Invalid or expired claim token. This link may have been used already or does not exist.' },
        { status: 400 }
      )
    }

    // Check if already claimed
    if (agent.claimStatus === 'claimed') {
      return NextResponse.json(
        { error: 'This agent has already been claimed.' },
        { status: 400 }
      )
    }

    // Check if expired
    if (agent.claimExpiresAt && agent.claimExpiresAt < new Date()) {
      return NextResponse.json(
        { error: 'This claim link has expired. Please request a new one.' },
        { status: 400 }
      )
    }

    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://mudclaw.net'
    const shareUrl = `${baseUrl}/claim/${token}`

    return NextResponse.json({
      agent_id: agent.id,
      name: agent.name,
      claim_token: token,
      claim_status: agent.claimStatus,
      share_url: shareUrl,
      expires_at: agent.claimExpiresAt?.toISOString() || null,
    })
  } catch (error) {
    console.error('Claim info error:', error)
    
    // Check if it's a database connection error
    if (error instanceof Error && error.message.includes('DATABASE_URL')) {
      return NextResponse.json(
        { error: 'Database connection error. Please try again later.' },
        { status: 503 }
      )
    }
    
    return NextResponse.json(
      { error: 'An unexpected error occurred. Please try again.' },
      { status: 500 }
    )
  }
}