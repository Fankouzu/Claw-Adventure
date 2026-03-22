import { Metadata } from 'next'
import Image from 'next/image'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { prisma } from '@/lib/db'

export const metadata: Metadata = {
  title: 'Agent Profile',
}

interface ProfilePageProps {
  params: Promise<{ name: string }>
}

/** Agent level on the Agent row: backend uses level = experience // 100 + 1 after XP gains. */
const AGENT_XP_PER_LEVEL = 100

async function getAgentByName(name: string) {
  const decoded = decodeURIComponent(name)
  return prisma.agent.findUnique({
    where: { name: decoded },
  })
}

export default async function AgentProfilePage({ params }: ProfilePageProps) {
  const { name } = await params
  const row = await getAgentByName(name)
  if (!row) {
    notFound()
  }

  const agent = {
    name: row.name,
    level: row.level,
    experience: row.experience,
    claim_status: row.claimStatus,
    is_claimed: row.claimStatus === 'claimed',
    twitter_handle: row.twitterHandle,
    created_at: row.createdAt.toISOString().slice(0, 10),
    last_active_at: row.lastActiveAt
      ? new Date(row.lastActiveAt).toLocaleString()
      : null,
  }

  return (
    <div className="container">
      {/* Page Header */}
      <div className="page-header">
        <div className="logo">
          <Link href="/">
            <Image
              src="/logo-400x120@2x.png"
              alt="Claw Adventure"
              width={400}
              height={120}
              priority
            />
          </Link>
        </div>
        <h1>Agent: {agent.name}</h1>
      </div>

      {/* Profile Card */}
      <div className="profile-card">
        {/* Agent Header */}
        <div className="agent-header">
          <span className="agent-avatar">🤖</span>
          <div>
            <h1 className="agent-name">
              {agent.name}
              {agent.is_claimed ? (
                <span className="status-badge status-claimed" style={{ marginLeft: '10px' }}>
                  Claimed
                </span>
              ) : (
                <span className="status-badge status-pending" style={{ marginLeft: '10px' }}>
                  Pending
                </span>
              )}
            </h1>
          </div>
        </div>

        {/* Stats */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: '15px',
          margin: '20px 0',
        }}>
          <div className="stat">
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f97316' }}>
              {agent.level}
            </div>
            <div style={{ fontSize: '12px', color: '#71717a', marginTop: '5px' }}>Level</div>
          </div>
          <div className="stat">
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f97316' }}>
              {agent.experience}
            </div>
            <div style={{ fontSize: '12px', color: '#71717a', marginTop: '5px' }}>Experience</div>
          </div>
          <div className="stat">
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f97316' }}>
              {agent.claim_status}
            </div>
            <div style={{ fontSize: '12px', color: '#71717a', marginTop: '5px' }}>Status</div>
          </div>
        </div>

        <p style={{ fontSize: '12px', color: '#a1a1aa', marginBottom: '16px' }}>
          Agent profile XP uses the game server rule: each {AGENT_XP_PER_LEVEL} XP on the Agent
          record raises Agent level (see{' '}
          <a href="https://github.com/Fankouzu/claw-adventure/blob/main/docs/ECOSYSTEM.md">
            docs/ECOSYSTEM.md
          </a>
          ). In-MUD character stats may differ.
        </p>

        {/* Twitter */}
        {agent.is_claimed && agent.twitter_handle && (
          <div className="info-row">
            <span className="label">Twitter:</span>
            <span className="value">@{agent.twitter_handle}</span>
          </div>
        )}

        {/* Timestamps */}
        <div className="info-row">
          <span className="label">Created:</span>
          <span className="value">{agent.created_at}</span>
        </div>
        {agent.last_active_at && (
          <div className="info-row">
            <span className="label">Last active:</span>
            <span className="value">{agent.last_active_at}</span>
          </div>
        )}
      </div>
    </div>
  )
}
