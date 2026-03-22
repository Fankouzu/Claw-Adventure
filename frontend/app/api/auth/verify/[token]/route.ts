import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/db'
import { getSession } from '@/lib/session'

export async function GET(
  request: NextRequest,
  { params }: { params: { token: string } }
) {
  try {
    const token = params.token

    // Find and verify the login token
    const emailToken = await prisma.emailToken.findUnique({
      where: { token },
      include: {
        agent: true,
      },
    })

    if (!emailToken) {
      return NextResponse.json(
        { error: 'Invalid token' },
        { status: 400 }
      )
    }

    // Check if token is expired
    if (emailToken.expiresAt < new Date()) {
      // Delete expired token
      await prisma.emailToken.delete({
        where: { id: emailToken.id },
      })
      return NextResponse.json(
        { error: 'Token expired. Please request a new login link.' },
        { status: 400 }
      )
    }

    // Verify token type
    if (emailToken.tokenType !== 'login') {
      return NextResponse.json(
        { error: 'Invalid token type' },
        { status: 400 }
      )
    }

    // Verify the email is associated with the agent
    const userEmail = await prisma.userEmail.findFirst({
      where: {
        email: emailToken.email,
        isVerified: true,
      },
      include: {
        agent: true,
      },
    })

    if (!userEmail) {
      return NextResponse.json(
        { error: 'Email not found or not verified' },
        { status: 400 }
      )
    }

    // Create session with verified email
    const session = await getSession()
    session.email = emailToken.email
    await session.save()

    // Delete the used token
    await prisma.emailToken.delete({
      where: { id: emailToken.id },
    })

    return NextResponse.json({
      status: 'verified',
      email: emailToken.email,
    })
  } catch (error) {
    console.error('Auth verify error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
