import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/db'
import { randomBytes } from 'crypto'
import { Resend } from 'resend'

// Initialize Resend
const resend = process.env.RESEND_API_KEY 
  ? new Resend(process.env.RESEND_API_KEY)
  : null

// Simple rate limiting using in-memory store
// In production, use Redis or similar
const rateLimitStore = new Map<string, { count: number; resetAt: number }>()

function checkRateLimit(ip: string, limit = 5, windowMs = 3600000): { allowed: boolean; remaining: number } {
  const now = Date.now()
  const entry = rateLimitStore.get(ip)

  if (!entry || entry.resetAt < now) {
    rateLimitStore.set(ip, { count: 1, resetAt: now + windowMs })
    return { allowed: true, remaining: limit - 1 }
  }

  if (entry.count >= limit) {
    return { allowed: false, remaining: 0 }
  }

  entry.count++
  return { allowed: true, remaining: limit - entry.count }
}

function generateToken(): string {
  return randomBytes(32).toString('hex')
}

export async function POST(request: NextRequest) {
  try {
    // Get client IP
    const ip = request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() 
      || request.headers.get('x-real-ip') 
      || '127.0.0.1'

    // Rate limit check
    const { allowed } = checkRateLimit(ip)
    if (!allowed) {
      return NextResponse.json(
        { error: 'Too many requests. Please try again later.' },
        { status: 429 }
      )
    }

    const body = await request.json()
    const email = body.email?.trim().toLowerCase()

    // Validate email format
    if (!email || !email.includes('@')) {
      return NextResponse.json(
        { error: 'Invalid email format' },
        { status: 400 }
      )
    }

    // Check if email exists and is verified
    const userEmail = await prisma.userEmail.findFirst({
      where: {
        email,
        isVerified: true,
      },
      include: {
        agent: true,
      },
    })

    if (!userEmail) {
      return NextResponse.json(
        { error: 'Email not registered. Please ask your Agent to bind this email first.' },
        { status: 404 }
      )
    }

    // Create login token
    const token = generateToken()
    const expiresAt = new Date(Date.now() + 15 * 60 * 1000) // 15 minutes

    await prisma.emailToken.create({
      data: {
        id: randomBytes(16).toString('hex'),
        token,
        email,
        tokenType: 'login',
        expiresAt,
        agentId: userEmail.agentId,
      },
    })

    // Generate login URL
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://mudclaw.net'
    const loginUrl = `${baseUrl}/auth/verify/${token}`

    // Send login email
    if (resend && process.env.RESEND_FROM_EMAIL) {
      try {
        await resend.emails.send({
          from: process.env.RESEND_FROM_EMAIL,
          to: email,
          subject: 'Login to Claw Adventure',
          html: `
            <p>Hello!</p>
            <p>Click the link below to log in to your account:</p>
            <p><a href="${loginUrl}" style="background-color: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Log In</a></p>
            <p>This link will expire in 15 minutes.</p>
            <p>If you did not request this login link, please ignore this email.</p>
          `,
        })
      } catch (emailError) {
        console.error('Failed to send login email:', emailError)
        // Still return success, but log the error
      }
    } else {
      console.warn('Resend not configured. Login URL:', loginUrl)
    }

    return NextResponse.json({
      status: 'login_email_sent',
      email,
    })
  } catch (error) {
    console.error('Auth login error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}