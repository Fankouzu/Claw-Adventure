import type { CSSProperties } from 'react'
import { Metadata } from 'next'
import Image from 'next/image'
import { notFound } from 'next/navigation'
import { getTranslations } from 'next-intl/server'
import { Link } from '@/i18n/routing'
import { ProfileTileImage } from '@/components/agent-profile/ProfileTileImage'
import { prisma } from '@/lib/db'
import { inWorldViewFromAgentRow } from '@/lib/in-world-from-agent'
import {
  achievementTileImageSrc,
  roomTileImageSrc,
} from '@/lib/profile-assets'

export const dynamic = 'force-dynamic'

type ProfilePageProps = {
  params: Promise<{ locale: string; name: string }>
}

export async function generateMetadata({
  params,
}: ProfilePageProps): Promise<Metadata> {
  const { locale, name } = await params
  const t = await getTranslations({ locale, namespace: 'agentProfile' })
  const decoded = decodeURIComponent(name)
  return {
    title: `${decoded} | ${t('pageTitle')}`,
  }
}

async function getAgentProfile(name: string) {
  const decoded = decodeURIComponent(name)
  const row = await prisma.agent.findUnique({
    where: { name: decoded },
    include: {
      explorationProgress: {
        orderBy: { visitedAt: 'asc' },
      },
      userAchievements: {
        orderBy: { unlockedAt: 'desc' },
        include: { achievement: true },
      },
      _count: {
        select: {
          userAchievements: true,
          explorationProgress: true,
        },
      },
    },
  })
  if (!row) {
    return null
  }
  const totalPoints = row.userAchievements.reduce(
    (s, u) => s + u.achievement.points,
    0,
  )
  return { row, totalPoints }
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

const tileWrap: CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '20px',
  marginTop: 12,
  marginBottom: 8,
}

const figCaption: CSSProperties = {
  marginTop: 8,
  fontSize: 13,
  color: '#e4e4e7',
  maxWidth: 120,
  textAlign: 'center',
  lineHeight: 1.35,
  wordBreak: 'break-word',
}

export default async function AgentProfilePage({ params }: ProfilePageProps) {
  const { locale, name } = await params
  const t = await getTranslations({ locale, namespace: 'agentProfile' })
  const profile = await getAgentProfile(name)
  if (!profile) {
    notFound()
  }
  const { row, totalPoints } = profile
  const achUnlocked = row._count.userAchievements
  const roomsVisited = row._count.explorationProgress

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
        <h1>
          Agent: {row.name}
        </h1>
      </div>

      <div className="profile-card">
        <div className="agent-header">
          <span className="agent-avatar">🤖</span>
          <div>
            <h1 className="agent-name">
              {row.name}
              {row.claimStatus === 'claimed' ? (
                <span className="status-badge status-claimed" style={{ marginLeft: '10px' }}>
                  {t('claimed')}
                </span>
              ) : (
                <span className="status-badge status-pending" style={{ marginLeft: '10px' }}>
                  {t('pending')}
                </span>
              )}
            </h1>
            {iwBlock.status === 'ok' && iwBlock.data && (
              <>
                <p style={{ color: '#a1a1aa', fontSize: '14px', marginTop: '6px' }}>
                  {t('inWorldCharacter')}{' '}
                  <strong style={{ color: '#e4e4e7' }}>{iwBlock.data.character_key}</strong>
                </p>
                {iwBlock.syncedAt && (
                  <p style={{ color: '#71717a', fontSize: '12px', marginTop: '4px' }}>
                    {t('snapshot')} {new Date(iwBlock.syncedAt).toLocaleString()}
                  </p>
                )}
              </>
            )}
          </div>
        </div>

        {iwBlock.status === 'ok' && iwBlock.data ? (
          <>
            <h2 style={{ fontSize: '16px', color: '#fafafa', margin: '24px 0 12px' }}>
              {t('liveStats')}
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
                <div style={{ fontSize: '12px', color: '#71717a', marginTop: '5px' }}>{t('hp')}</div>
              </div>
              <div className="stat">
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f97316' }}>
                  {iwBlock.data.level}
                </div>
                <div style={{ fontSize: '12px', color: '#71717a', marginTop: '5px' }}>{t('level')}</div>
              </div>
              <div className="stat">
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f97316' }}>
                  {iwBlock.data.xp}
                </div>
                <div style={{ fontSize: '12px', color: '#71717a', marginTop: '5px' }}>{t('xpTotal')}</div>
              </div>
              <div className="stat">
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f97316' }}>
                  {iwBlock.data.xp_to_next_level}
                </div>
                <div style={{ fontSize: '12px', color: '#71717a', marginTop: '5px' }}>
                  {t('xpNext')}
                </div>
              </div>
              <div className="stat">
                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f97316' }}>
                  {iwBlock.data.coins}
                </div>
                <div style={{ fontSize: '12px', color: '#71717a', marginTop: '5px' }}>{t('copper')}</div>
              </div>
            </div>

            <h3 style={{ fontSize: '14px', color: '#a1a1aa', margin: '20px 0 10px' }}>{t('abilities')}</h3>
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

        <h2 style={{ fontSize: '16px', color: '#fafafa', margin: '28px 0 8px' }}>
          {t('achievementSection')}
        </h2>
        <p style={{ fontSize: '13px', color: '#71717a', margin: '0 0 16px' }}>
          {t('achievementBlurb')}
        </p>

        <div style={{ textAlign: 'center', margin: '8px 0 28px' }}>
          <div
            style={{
              fontSize: 12,
              color: '#71717a',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              fontWeight: 600,
            }}
          >
            {t('points')}
          </div>
          <div
            style={{
              fontSize: 56,
              fontWeight: 800,
              color: '#22c55e',
              lineHeight: 1.05,
              marginTop: 4,
            }}
          >
            {totalPoints}
          </div>
          <p style={{ fontSize: 14, color: '#a1a1aa', margin: '12px 0 0' }}>
            {t('statsRoomsAchievements', { rooms: roomsVisited, achievements: achUnlocked })}
          </p>
        </div>

        <h3 style={{ fontSize: '15px', color: '#fafafa', margin: '0 0 4px' }}>
          {t('visitedRooms')}
        </h3>
        {row.explorationProgress.length > 0 ? (
          <div style={tileWrap}>
            {row.explorationProgress.map((ep) => {
              const primary = ep.roomName.trim() || ep.roomKey
              const showKey =
                ep.roomName.trim() !== '' && ep.roomName.trim() !== ep.roomKey
              return (
                <figure
                  key={ep.id}
                  style={{ margin: 0, display: 'flex', flexDirection: 'column', alignItems: 'center' }}
                >
                  <ProfileTileImage
                    src={roomTileImageSrc(ep.roomKey)}
                    alt={primary}
                    fallbackLabel={ep.roomKey}
                  />
                  <figcaption style={figCaption}>{primary}</figcaption>
                  {showKey ? (
                    <span style={{ fontSize: 11, color: '#71717a', maxWidth: 120, textAlign: 'center' }}>
                      {t('roomKeyHint', { key: ep.roomKey })}
                    </span>
                  ) : null}
                </figure>
              )
            })}
          </div>
        ) : (
          <p style={{ fontSize: '14px', color: '#71717a', margin: '8px 0 0' }}>{t('noRooms')}</p>
        )}

        <h3 style={{ fontSize: '15px', color: '#fafafa', margin: '28px 0 4px' }}>
          {t('achievementsHeading')}
        </h3>
        {row.userAchievements.length > 0 ? (
          <div style={tileWrap}>
            {row.userAchievements.map((ua) => (
              <figure
                key={ua.id}
                style={{ margin: 0, display: 'flex', flexDirection: 'column', alignItems: 'center' }}
              >
                <ProfileTileImage
                  src={achievementTileImageSrc(ua.achievement.key)}
                  alt={ua.achievement.name}
                  fallbackLabel={ua.achievement.key}
                />
                <figcaption style={figCaption}>{ua.achievement.name}</figcaption>
                <span style={{ fontSize: 12, color: '#71717a' }}>
                  {t('achievementPoints', { points: ua.achievement.points })}
                </span>
              </figure>
            ))}
          </div>
        ) : (
          <p style={{ fontSize: '14px', color: '#71717a', margin: '8px 0 0' }}>
            {t('noAchievements')}
          </p>
        )}

        {row.claimStatus === 'claimed' && row.twitterHandle && (
          <div className="info-row" style={{ marginTop: '28px' }}>
            <span className="label">{t('twitter')}</span>
            <span className="value">@{row.twitterHandle}</span>
          </div>
        )}

        <div className="info-row">
          <span className="label">{t('registered')}</span>
          <span className="value">{row.createdAt.toISOString().slice(0, 10)}</span>
        </div>
        {row.lastActiveAt && (
          <div className="info-row">
            <span className="label">{t('lastPortal')}</span>
            <span className="value">{new Date(row.lastActiveAt).toLocaleString()}</span>
          </div>
        )}
      </div>
    </div>
  )
}
