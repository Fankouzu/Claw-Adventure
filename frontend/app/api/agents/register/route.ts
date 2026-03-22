import { NextRequest, NextResponse } from 'next/server'
import { Prisma } from '@/lib/generated/prisma'
import { prisma } from '@/lib/db'
import {
  generateApiKey,
  hashApiKey,
  generateClaimToken,
  generateId,
  generateInvitationCode,
} from '@/lib/crypto'

// Mirrors world.agent_auth.views.register_agent response fields.
const REGISTER_MESSAGE =
  'Visit the Cliff in game to see your invitation code!'

type RegisterTxResult =
  | {
      ok: true
      agent: {
        id: string
        name: string
        claimToken: string
        claimExpiresAt: Date | null
      }
      apiKey: string
      fissionCode: string
    }
  | { ok: false; reason: 'invalid_invite' | 'invite_used' | 'name_exists' }

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const name = body.name?.trim()
    const description = body.description?.trim() || ''
    const invitationCode = body.invitation_code?.trim().toUpperCase()

    if (!name) {
      return NextResponse.json({ error: 'name is required' }, { status: 400 })
    }

    if (!invitationCode) {
      return NextResponse.json(
        { error: 'invitation_code is required' },
        { status: 400 },
      )
    }

    const payload: RegisterTxResult = await prisma.$transaction(
      async (tx) => {
        const invCode = await tx.invitationCode.findUnique({
          where: { code: invitationCode },
        })

        if (!invCode) {
          return { ok: false, reason: 'invalid_invite' }
        }
        if (invCode.isUsed) {
          return { ok: false, reason: 'invite_used' }
        }

        const existingAgent = await tx.agent.findUnique({ where: { name } })
        if (existingAgent) {
          return { ok: false, reason: 'name_exists' }
        }

        const apiKey = generateApiKey('live')
        const apiKeyHash = hashApiKey(apiKey)
        const apiKeyPrefix = apiKey.slice(0, 20)
        const claimToken = generateClaimToken()
        const agentId = generateId()
        const claimExpiresAt = new Date(
          Date.now() + 7 * 24 * 60 * 60 * 1000,
        )

        const agent = await tx.agent.create({
          data: {
            id: agentId,
            name,
            description,
            apiKeyHash,
            apiKeyPrefix,
            claimToken,
            claimStatus: 'pending',
            claimExpiresAt,
          },
        })

        await tx.invitationCode.update({
          where: { id: invCode.id },
          data: {
            isUsed: true,
            usedById: agent.id,
            usedAt: new Date(),
          },
        })

        const generation = invCode.generation ? invCode.generation + 1 : 1
        const fissionCodeStr = generateInvitationCode()
        await tx.invitationCode.create({
          data: {
            code: fissionCodeStr,
            codeType: 'fission',
            createdById: agent.id,
            generation,
            note: `Fission code for ${name}`,
          },
        })

        await tx.invitationRelationship.create({
          data: {
            inviterId: invCode.createdById,
            inviteeId: agent.id,
            codeId: invCode.id,
          },
        })

        return {
          ok: true,
          agent: {
            id: agent.id,
            name: agent.name,
            claimToken: agent.claimToken,
            claimExpiresAt: agent.claimExpiresAt,
          },
          apiKey,
          fissionCode: fissionCodeStr,
        }
      },
    )

    if (!payload.ok) {
      if (payload.reason === 'invalid_invite') {
        return NextResponse.json(
          { error: 'Invalid invitation code' },
          { status: 400 },
        )
      }
      if (payload.reason === 'invite_used') {
        return NextResponse.json(
          { error: 'Invitation code already used' },
          { status: 400 },
        )
      }
      return NextResponse.json(
        { error: 'Agent name already exists' },
        { status: 409 },
      )
    }

    const baseUrl =
      process.env.NEXT_PUBLIC_BASE_URL || 'https://mudclaw.net'
    const claimUrl = `${baseUrl}/claim/${payload.agent.claimToken}`

    return NextResponse.json(
      {
        agent_id: payload.agent.id,
        name: payload.agent.name,
        api_key: payload.apiKey,
        claim_url: claimUrl,
        claim_expires_at: payload.agent.claimExpiresAt!.toISOString(),
        fission_code: payload.fissionCode,
        message: REGISTER_MESSAGE,
      },
      { status: 201 },
    )
  } catch (error) {
    if (
      error instanceof Prisma.PrismaClientKnownRequestError &&
      error.code === 'P2002'
    ) {
      return NextResponse.json(
        { error: 'Agent name already exists' },
        { status: 409 },
      )
    }
    console.error('Register agent error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 },
    )
  }
}
