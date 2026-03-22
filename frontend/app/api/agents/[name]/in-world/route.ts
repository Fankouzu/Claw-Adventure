import { NextRequest, NextResponse } from 'next/server'
import { prisma } from '@/lib/db'
import { inWorldJsonFromAgentRow } from '@/lib/in-world-from-agent'

/** Same JSON as Evennia GET /api/agents/name/{name}/in-world (Prisma reads mirror columns). */
export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ name: string }> },
) {
  const { name } = await params
  const decoded = decodeURIComponent(name)
  const row = await prisma.agent.findUnique({ where: { name: decoded } })
  if (!row) {
    return NextResponse.json({ error: 'Agent not found' }, { status: 404 })
  }
  return NextResponse.json(inWorldJsonFromAgentRow(row))
}
