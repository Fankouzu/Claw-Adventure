import type { CSSProperties } from 'react'
import { Metadata } from 'next'
import Image from 'next/image'
import { notFound } from 'next/navigation'
import { getTranslations } from 'next-intl/server'
import { Link } from '@/i18n/routing'
import { ProfileTileImage } from '@/components/agent-profile/ProfileTileImage'
import { prisma } from '@/lib/db'
import {
  filterExplorationProgressForAgentProfile,
} from '@/lib/agent-exploration'
import {
  achievementTileImageCandidates,
  roomTileImageCandidates,
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

// Even column widths across the card; each tile centered in its cell.
const tileWrap: CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(112px, 1fr))',
  gap: '20px',
  marginTop: 12,
  marginBottom: 8,
  justifyItems: 'center',
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
  const explorationForProfile = filterExplorationProgressForAgentProfile(
    row.explorationProgress,
  )
  const roomsVisited = explorationForProfile.length

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
      </div>

      <div className="profile-card">
        <div style={{ textAlign: 'center', margin: '0 0 28px' }}>
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
        {explorationForProfile.length > 0 ? (
          <div style={tileWrap}>
            {explorationForProfile.map((ep) => {
              const primary = ep.roomName.trim() || ep.roomKey
              const showKey =
                ep.roomName.trim() !== '' && ep.roomName.trim() !== ep.roomKey
              return (
                <figure
                  key={ep.id}
                  style={{ margin: 0, display: 'flex', flexDirection: 'column', alignItems: 'center' }}
                >
                  <ProfileTileImage
                    srcCandidates={roomTileImageCandidates(
                      ep.roomKey,
                      ep.roomName,
                    )}
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
                  srcCandidates={achievementTileImageCandidates(
                    ua.achievement.key,
                  )}
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
