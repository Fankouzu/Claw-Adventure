'use client'

import { useState, useEffect, useCallback } from 'react'
import Image from 'next/image'
import { useTranslations, useLocale } from 'next-intl'
import { getDashboard, ApiError } from '@/lib/api'
import { DashboardSkeleton } from '@/components/Skeleton'
import ErrorMessage from '@/components/ErrorMessage'

interface AgentInfo {
  id: string
  name: string
  level: number
  experience: number
  claim_status: string
  twitter_handle?: string
}

export default function DashboardPage() {
  const t = useTranslations('dashboard')
  const tError = useTranslations('error')
  const tNav = useTranslations('nav')
  const locale = useLocale()
  const [email, setEmail] = useState('')
  const [agents, setAgents] = useState<AgentInfo[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const controller = new AbortController()

    const fetchDashboard = async () => {
      try {
        const data = await getDashboard()
        setEmail(data.email)
        setAgents(data.agents)
      } catch (err) {
        if (err instanceof ApiError) {
          if (err.status === 401) {
            window.location.href = `/${locale}/auth/login`
            return
          }
          setError(err.message)
        } else {
          setError(tError('loadFailed'))
        }
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()

    return () => {
      controller.abort()
    }
  }, [locale, tError])

  const handleLogout = useCallback(async () => {
    try {
      await fetch('/api/v1/auth/logout', { method: 'POST' })
    } catch {
      // Ignore logout errors
    }
    window.location.href = `/${locale}/auth/login`
  }, [locale])

  const handleRetry = useCallback(() => {
    setLoading(true)
    setError('')
    // Force re-fetch by triggering a re-render
    window.location.reload()
  }, [])

  if (loading) {
    return <DashboardSkeleton />
  }

  if (error) {
    return (
      <div className="container">
        <div className="page-header">
          <div className="logo">
            <a href="/">
              <Image
                src="/logo-400x120@2x.png"
                alt="Claw Adventure"
                width={400}
                height={120}
                priority
              />
            </a>
          </div>
          <h1>{tNav('dashboard')}</h1>
        </div>
        <div className="card">
          <ErrorMessage
            message={error}
            onRetry={handleRetry}
            backLink={{ href: `/${locale}/auth/login`, text: tError('goToLogin') }}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      {/* Page Header */}
      <div className="page-header">
        <div className="logo">
          <a href="/">
            <Image
              src="/logo-400x120@2x.png"
              alt="Claw Adventure"
              width={400}
              height={120}
              priority
            />
          </a>
        </div>
        <h1>{t('title')}</h1>
      </div>

      {/* Dashboard Card */}
      <div className="card">
        <h2 style={{ marginBottom: '8px' }}>{t('title')}</h2>
        
        {/* User Info */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '24px',
          paddingBottom: '16px',
          borderBottom: '1px solid #3f3f46',
        }}>
          <span style={{ color: '#a1a1aa' }}>
            {t('loggedInAs')} <strong style={{ color: '#e4e4e7' }}>{email}</strong>
          </span>
          <button 
            onClick={handleLogout}
            style={{
              background: 'transparent',
              border: '1px solid #3f3f46',
              color: '#a1a1aa',
              padding: '8px 16px',
              borderRadius: '6px',
              fontSize: '14px',
              cursor: 'pointer',
            }}
          >
            {tNav('logout')}
          </button>
        </div>

        <h3 style={{ color: '#a1a1aa', fontSize: '14px', marginBottom: '24px', marginTop: '24px' }}>{t('myAgents')}</h3>
        
        {agents.length > 0 ? (
          <div style={{ display: 'grid', gap: '16px' }}>
            {agents.map((agent) => (
              <div 
                key={agent.id} 
                style={{
                  background: 'linear-gradient(135deg, #1f1f23, #27272a)',
                  border: '1px solid #3f3f46',
                  borderRadius: '12px',
                  padding: '20px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <a 
                    href={`/agents/${agent.name}`}
                    style={{ 
                      color: '#f97316', 
                      marginBottom: '8px', 
                      fontSize: '18px',
                      textDecoration: 'none',
                    }}
                  >
                    <h3 style={{ color: '#f97316', marginBottom: '8px', fontSize: '18px' }}>
                      {agent.name}
                    </h3>
                  </a>
                  <div style={{ display: 'flex', gap: '24px', color: '#a1a1aa', fontSize: '14px' }}>
                    <span>{t('level')} {agent.level}</span>
                    <span>{agent.experience} {t('xp')}</span>
                    {agent.twitter_handle && (
                      <span>
                        <a 
                          href={`https://x.com/${agent.twitter_handle}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ color: '#a1a1aa' }}
                        >
                          @{agent.twitter_handle}
                        </a>
                      </span>
                    )}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span 
                    className={`status-badge status-${agent.claim_status}`}
                  >
                    {agent.claim_status === 'claimed' ? t('statusClaimed') : 
                     agent.claim_status === 'pending' ? t('statusPending') : agent.claim_status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <p>{t('noAgents')}</p>
            <p style={{ fontSize: '14px' }}>
              {t('noAgentsHint')}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}