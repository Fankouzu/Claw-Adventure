import type { CSSProperties } from 'react'
import { Metadata } from 'next'
import Image from 'next/image'
import { notFound } from 'next/navigation'
import { getTranslations } from 'next-intl/server'
import { Link } from '@/i18n/routing'
import { ProfileTileImage } from '@/components/agent-profile/ProfileTileImage'
import {
  AGENT_PROFILE_ROOM_TOTAL,
  buildAgentProfileAchievementSlots,
  buildAgentProfileRoomSlots,
} from '@/lib/agent-profile-display'
import { prisma } from '@/lib/db'
import {
  filterExplorationProgressForAgentProfile,
  profileExplorationPoints,
} from '@/lib/agent-exploration'
import {
  achievementTileImageCandidates,
  PROFILE_NO_IMAGE_SRC,
  roomTileImageCandidates,
  slugForProfileAsset,
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
  const [row, allAchievements] = await Promise.all([
    prisma.agent.findUnique({
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
    }),
    prisma.achievement.findMany(),
  ])
  if (!row) {
    return null
  }
  const achievementPoints = row.userAchievements.reduce(
    (s, u) => s + u.achievement.points,
    0,
  )
  const explorationPoints = profileExplorationPoints(row.explorationProgress)
  const totalPoints = achievementPoints + explorationPoints
  return { row, totalPoints, allAchievements }
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

const figCaptionMuted: CSSProperties = {
  ...figCaption,
  color: '#71717a',
}

export default async function AgentProfilePage({ params }: ProfilePageProps) {
  const { locale, name } = await params
  const t = await getTranslations({ locale, namespace: 'agentProfile' })
  const profile = await getAgentProfile(name)
  if (!profile) {
    notFound()
  }
  const { row, totalPoints, allAchievements } = profile
  const achUnlocked = row._count.userAchievements
  const explorationForProfile = filterExplorationProgressForAgentProfile(
    row.explorationProgress,
  )

  const { slots: roomSlots, orphans: roomOrphans } = buildAgentProfileRoomSlots(
    explorationForProfile,
  )

  const roomsVisitedOnGrid = roomSlots.filter((s) => s.kind === 'visited').length

  const achievementDefs = allAchievements.map((a) => ({
    id: a.id,
    key: a.key,
    name: a.name,
    points: a.points,
    isHidden: a.isHidden,
  }))

  const achievementSlots = buildAgentProfileAchievementSlots(
    achievementDefs,
    row.userAchievements.map((ua) => ({
      id: ua.id,
      achievementId: ua.achievementId,
      achievement: {
        id: ua.achievement.id,
        key: ua.achievement.key,
        name: ua.achievement.name,
        points: ua.achievement.points,
        isHidden: ua.achievement.isHidden,
      },
    })),
  )

  const achievementTotalOnPage = achievementSlots.length

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
            {t('statsRoomsAchievements', {
              visited: roomsVisitedOnGrid,
              totalRooms: AGENT_PROFILE_ROOM_TOTAL,
              unlocked: achUnlocked,
              totalAchievements: achievementTotalOnPage,
            })}
          </p>
        </div>

        <h3 style={{ fontSize: '15px', color: '#fafafa', margin: '0 0 4px' }}>
          {t('visitedRooms')}
        </h3>
        <div style={tileWrap}>
          {roomSlots.map((slot) => {
            if (slot.kind === 'visited') {
              const ep = slot.row
              const primary = ep.roomName.trim() || ep.roomKey
              const showKey =
                ep.roomName.trim() !== '' && ep.roomName.trim() !== ep.roomKey
              return (
                <figure
                  key={ep.id}
                  style={{
                    margin: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                  }}
                >
                  <ProfileTileImage
                    srcCandidates={roomTileImageCandidates(ep.roomKey, ep.roomName)}
                    alt={primary}
                    fallbackLabel={ep.roomKey}
                  />
                  <figcaption style={figCaption}>{primary}</figcaption>
                  {showKey ? (
                    <span
                      style={{
                        fontSize: 11,
                        color: '#71717a',
                        maxWidth: 120,
                        textAlign: 'center',
                      }}
                    >
                      {t('roomKeyHint', { key: ep.roomKey })}
                    </span>
                  ) : null}
                </figure>
              )
            }
            const lockKey = `locked-room-${slugForProfileAsset(slot.canonical)}`
            return (
              <figure
                key={lockKey}
                style={{
                  margin: 0,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                }}
              >
                <ProfileTileImage
                  src={PROFILE_NO_IMAGE_SRC}
                  alt={t('unexploredRoom')}
                  fallbackLabel="…"
                />
                <figcaption style={figCaptionMuted}>{t('unexploredRoom')}</figcaption>
              </figure>
            )
          })}
          {roomOrphans.map((ep) => {
            const primary = ep.roomName.trim() || ep.roomKey
            const showKey =
              ep.roomName.trim() !== '' && ep.roomName.trim() !== ep.roomKey
            return (
              <figure
                key={`orphan-${ep.id}`}
                style={{
                  margin: 0,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                }}
              >
                <ProfileTileImage
                  srcCandidates={roomTileImageCandidates(ep.roomKey, ep.roomName)}
                  alt={primary}
                  fallbackLabel={ep.roomKey}
                />
                <figcaption style={figCaption}>{primary}</figcaption>
                {showKey ? (
                  <span
                    style={{
                      fontSize: 11,
                      color: '#71717a',
                      maxWidth: 120,
                      textAlign: 'center',
                    }}
                  >
                    {t('roomKeyHint', { key: ep.roomKey })}
                  </span>
                ) : null}
              </figure>
            )
          })}
        </div>

        <h3 style={{ fontSize: '15px', color: '#fafafa', margin: '28px 0 4px' }}>
          {t('achievementsHeading')}
        </h3>
        <div style={tileWrap}>
          {achievementSlots.map((slot) => {
            if (slot.kind === 'unlocked') {
              const ua = slot.ua
              return (
                <figure
                  key={ua.id}
                  style={{
                    margin: 0,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                  }}
                >
                  <ProfileTileImage
                    srcCandidates={achievementTileImageCandidates(ua.achievement.key)}
                    alt={ua.achievement.name}
                    fallbackLabel={ua.achievement.key}
                  />
                  <figcaption style={figCaption}>{ua.achievement.name}</figcaption>
                  <span style={{ fontSize: 12, color: '#71717a' }}>
                    {t('achievementPoints', { points: ua.achievement.points })}
                  </span>
                </figure>
              )
            }
            return (
              <figure
                key={`locked-ach-${slot.achievementKey}`}
                style={{
                  margin: 0,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                }}
              >
                <ProfileTileImage
                  src={PROFILE_NO_IMAGE_SRC}
                  alt={t('achievementLocked')}
                  fallbackLabel="…"
                />
                <figcaption style={figCaptionMuted}>{t('achievementLocked')}</figcaption>
              </figure>
            )
          })}
        </div>

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
