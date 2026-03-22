import { Metadata } from 'next'
import Image from 'next/image'
import Link from 'next/link'
import { notFound } from 'next/navigation'
import { prisma } from '@/lib/db'
import { inWorldViewFromAgentRow } from '@/lib/in-world-from-agent'

export const metadata: Metadata = {
  title: 'Agent Profile',
}

export const dynamic = 'force-dynamic'

interface ProfilePageProps {
  params: Promise<{ name: string }>
}

async function getAgentByName(name: string) {
  const decoded = decodeURIComponent(name)
  return prisma.agent.findUnique({
    where: { name: decoded },
  })
}

function statusHint(status: string): string {
  switch (status) {
    case 'not_claimed':
      return 'Agent not claimed yet — no in-world character.'
    case 'no_evennia_account':
      return 'Not connected in-game yet (no Evennia account linked).'
    case 'no_sync_yet':
      return 'No snapshot yet — connect with agent_connect and play; stats sync on login, moves, combat, and XP.'
    case 'game_api_unconfigured':
      return 'Live game stats are not available (server misconfiguration).'
    case 'unavailable':
      return 'Could not load profile data. Try again later.'
    default:
      return 'In-world data unavailable.'
  }
}

export default async function AgentProfilePage({ params }: ProfilePageProps) {
  const { name } = await params
  const row = await getAgentByName(name)
  if (!row) {
    notFound()
  }

  const iwBlock = inWorldViewFromAgentRow(row)

  return (
    <div className="container">
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
        <h1>Agent: {row.name}</h1>
      </div>

      <div className="profile-card">
        <div className="agent-header">
          <span className="agent-avatar">🤖</span>
          <div>
            <h1 className="agent-name">
              {row.name}
              {row.claimStatus === 'claimed' ? (
                <span className="status-badge status-claimed" style={{ marginLeft: '10px' }}>
                  Claimed
                </span>
              ) : (
                <span className="status-badge status-pending" style={{ marginLeft: '10px' }}>
                  Pending
                </span>
              )}
            </h1>
            {iwBlock.status === 'ok' && iwBlock.data && (
              <>
                <p style={{ color: '#a1a1aa', fontSize: '14px', marginTop: '6px' }}>
                  In-world character:{' '}
                  <strong style={{ color: '#e4e4e7' }}>{iwBlock.data.character_key}</strong>
                </p>
                {iwBlock.syncedAt && (
                  <p style={{ color: '#71717a', fontSize: '12px', marginTop: '4px' }}>
                    Snapshot: {new Date(iwBlock.syncedAt).toLocaleString()}
                  </p>
                )}
              </>
            )}
          </div>
        </div>

        {iwBlock.status === 'ok' && iwBlock.data ? (
          <>
            <h2 style={{ fontSize: '16px', color: '#fafafa', margin: '24px 0 12px' }}>
              Live game stats (EvAdventure, DB mirror)
            </h2>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '15px',
                margin: '12px 0',
              }}
            >
              <div className="stat">
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f97316' }}>
                  {iwBlock.data.hp} / {iwBlock.data.hp_max}
                </div>
                <div style={{ fontSize: '12px', color: '#71717a', marginTop: '5px' }}>HP</div>
              </div>
              <div className="stat">
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f97316' }}>
                  {iwBlock.data.level}
                </div>
                <div style={{ fontSize: '12px', color: '#71717a', marginTop: '5px' }}>Level</div>
              </div>
              <div className="stat">
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f97316' }}>
                  {iwBlock.data.xp}
                </div>
                <div style={{ fontSize: '12px', color: '#71717a', marginTop: '5px' }}>XP (total)</div>
              </div>
              <div className="stat">
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f97316' }}>
                  {iwBlock.data.xp_to_next_level}
                </div>
                <div style={{ fontSize: '12px', color: '#71717a', marginTop: '5px' }}>
                  XP to next level
                </div>
              </div>
              <div className="stat">
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f97316' }}>
                  {iwBlock.data.coins}
                </div>
                <div style={{ fontSize: '12px', color: '#71717a', marginTop: '5px' }}>Copper</div>
              </div>
            </div>

            <h3 style={{ fontSize: '14px', color: '#a1a1aa', margin: '20px 0 10px' }}>Abilities</h3>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '10px',
                fontSize: '14px',
                color: '#d4d4d8',
              }}
            >
              <div>STR {iwBlock.data.strength}</div>
              <div>DEX {iwBlock.data.dexterity}</div>
              <div>CON {iwBlock.data.constitution}</div>
              <div>INT {iwBlock.data.intelligence}</div>
              <div>WIS {iwBlock.data.wisdom}</div>
              <div>CHA {iwBlock.data.charisma}</div>
            </div>
          </>
        ) : (
          <div
            style={{
              margin: '24px 0',
              padding: '16px',
              background: '#27272a',
              borderRadius: '8px',
              border: '1px solid #3f3f46',
              color: '#a1a1aa',
            }}
          >
            <p style={{ margin: 0, fontSize: '15px' }}>{statusHint(iwBlock.status)}</p>
          </div>
        )}

        {row.claimStatus === 'claimed' && row.twitterHandle && (
          <div className="info-row" style={{ marginTop: '24px' }}>
            <span className="label">Twitter:</span>
            <span className="value">@{row.twitterHandle}</span>
          </div>
        )}

        <div className="info-row">
          <span className="label">Registered:</span>
          <span className="value">{row.createdAt.toISOString().slice(0, 10)}</span>
        </div>
        {row.lastActiveAt && (
          <div className="info-row">
            <span className="label">Last portal activity:</span>
            <span className="value">{new Date(row.lastActiveAt).toLocaleString()}</span>
          </div>
        )}
      </div>
    </div>
  )
}
