import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/db'

// Extract tweet_id from Twitter URL
function extractTweetId(tweetUrl: string): string | null {
  const pattern = /(?:twitter\.com|x\.com)\/\w+\/status\/(\d+)/
  const match = tweetUrl.match(pattern)
  return match ? match[1] : null
}

// Extract Twitter handle from URL
function extractTwitterHandle(tweetUrl: string): string | null {
  const pattern = /(?:twitter\.com|x\.com)\/(\w+)\/status\/\d+/
  const match = tweetUrl.match(pattern)
  return match ? match[1] : null
}

export async function POST(
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

    const agent = await prisma.agent.findUnique({
      where: { claimToken: token },
    })

    if (!agent) {
      return NextResponse.json(
        { error: 'Invalid claim token' },
        { status: 400 }
      )
    }

    if (agent.claimStatus === 'claimed') {
      return NextResponse.json(
        { error: 'Agent already claimed' },
        { status: 400 }
      )
    }

    const body = await request.json()
    const tweetUrl = body.tweet_url?.trim()

    if (!tweetUrl) {
      return NextResponse.json(
        { error: 'Tweet URL is required' },
        { status: 400 }
      )
    }

    // Validate tweet URL format
    if (!tweetUrl.includes('twitter.com') && !tweetUrl.includes('x.com')) {
      return NextResponse.json(
        { error: 'Invalid tweet URL format' },
        { status: 400 }
      )
    }

    // Extract Twitter handle
    const twitterHandle = extractTwitterHandle(tweetUrl)
    if (!twitterHandle) {
      return NextResponse.json(
        { error: 'Could not extract Twitter handle from URL' },
        { status: 400 }
      )
    }

    // Update agent - claim completed
    const updatedAgent = await prisma.agent.update({
      where: { id: agent.id },
      data: {
        claimStatus: 'claimed',
        claimedAt: new Date(),
        twitterHandle,
        tweetUrl,
      },
    })

    return NextResponse.json({
      status: 'claimed',
      message: `Agent claimed by @${twitterHandle}`,
      twitter_handle: twitterHandle,
      agent: {
        id: updatedAgent.id,
        name: updatedAgent.name,
      },
    })
  } catch (error) {
    console.error('Claim verify error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}