'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import Image from 'next/image'
import { useTranslations, useLocale } from 'next-intl'
import { Link } from '@/i18n/routing'
import { getClaimInfo, verifyTweet, ApiError } from '@/lib/api'
import { ClaimSkeleton } from '@/components/Skeleton'
import ErrorMessage from '@/components/ErrorMessage'

interface ClaimInfo {
  agent_id: string
  name: string
  claim_token: string
  claim_status: string
  share_url: string
  expires_at?: string
}

export default function ClaimPage({ params }: { params: Promise<{ token: string }> }) {
  const t = useTranslations('claim')
  const tError = useTranslations('error')
  const locale = useLocale()
  
  const [agent, setAgent] = useState<ClaimInfo | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [tweetUrl, setTweetUrl] = useState('')
  const [copied, setCopied] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [success, setSuccess] = useState(false)
  const [token, setToken] = useState<string>('')

  useEffect(() => {
    params.then(p => setToken(p.token))
  }, [params])

  useEffect(() => {
    if (!token) return

    const controller = new AbortController()

    const fetchAgent = async () => {
      try {
        const data = await getClaimInfo(token)
        setAgent(data)
      } catch (err) {
        if (err instanceof ApiError) {
          setError(err.message)
        } else {
          setError(t('errorGeneric'))
        }
      } finally {
        setLoading(false)
      }
    }

    fetchAgent()

    return () => {
      controller.abort()
    }
  }, [token, t])

  const shareUrl = useMemo(() => {
    return agent?.share_url || `https://mudclaw.net/claim/${token}`
  }, [agent?.share_url, token])

  const tweetText = useMemo(() => {
    return `${t('tweetPreviewP1')}\n${t('tweetPreviewP2')}\n\n${shareUrl}`
  }, [shareUrl, t])

  const tweetIntentUrl = useMemo(() => {
    return `https://twitter.com/intent/tweet?text=${encodeURIComponent(tweetText)}`
  }, [tweetText])

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(tweetText)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }, [tweetText])

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setSubmitError('')

    try {
      const result = await verifyTweet(token, tweetUrl)
      if (result.status === 'claimed') {
        setSuccess(true)
      }
    } catch (err) {
      if (err instanceof ApiError) {
        setSubmitError(err.message)
      } else {
        setSubmitError(t('verifyFailed'))
      }
    } finally {
      setSubmitting(false)
    }
  }, [token, tweetUrl, t])

  const handleRetry = useCallback(() => {
    setLoading(true)
    setError('')
    window.location.reload()
  }, [])

  if (loading) {
    return <ClaimSkeleton />
  }

  if (error) {
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
          <h1>Error</h1>
        </div>
        <div className="card">
          <ErrorMessage
            message={error}
            onRetry={handleRetry}
            backLink={{ href: '/', text: tError('backToHome') }}
          />
        </div>
      </div>
    )
  }

  if (success) {
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
          <h1>{t('successTitle')}</h1>
        </div>
        <div className="card">
          <div style={{
            background: 'rgba(34, 197, 94, 0.1)',
            border: '1px solid #22c55e',
            borderRadius: '8px',
            padding: '24px',
            textAlign: 'center',
          }}>
            <h2 style={{ color: '#22c55e', marginBottom: '16px' }}>{t('successMessage')}</h2>
            <p style={{ marginBottom: '16px' }}>
              <strong>{agent?.name}</strong> {t('successAgentClaimed')}
            </p>
            <p style={{ color: '#a1a1aa', marginBottom: '24px' }}>
              {t('successHint')}
            </p>
            <Link href="/dashboard" className="btn btn-primary">
              {t('goToDashboard')}
            </Link>
          </div>
        </div>
      </div>
    )
  }

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
        <h1>{t('title')} {agent?.name}</h1>
      </div>

      <div className="card">
        <div style={{
          background: 'rgba(0, 0, 0, 0.6)',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #27272a',
        }}>
          <strong>{t('agentId')}</strong> {agent?.agent_id}<br />
          <strong>{t('status')}</strong> {agent?.claim_status}
        </div>

        <div style={{
          margin: '20px 0',
          padding: '15px',
          background: 'rgba(249, 115, 22, 0.1)',
          borderRadius: '8px',
          borderLeft: '4px solid #f97316',
        }}>
          <span style={{
            background: '#f97316',
            color: 'white',
            padding: '2px 8px',
            borderRadius: '4px',
            fontWeight: 'bold',
          }}>
            Step 1
          </span>
          <p style={{ marginTop: '10px' }}><strong>{t('step1Title')}</strong> {t('step1Desc')}</p>

          <div className="tweet-preview">
            {t('tweetPreviewP1')}<br />
            {t('tweetPreviewP2')}<br /><br />
            <span className="url">{shareUrl}</span>
          </div>

          <div className="button-group">
            <a href={tweetIntentUrl} target="_blank" rel="noopener noreferrer" className="btn btn-twitter">
              🐦 {t('postOnX')}
            </a>
            <button 
              type="button"
              className={`btn ${copied ? 'btn-success' : 'btn-secondary'}`}
              onClick={handleCopy}
            >
              {copied ? `✓ ${t('copied')}` : `📋 ${t('copyTweet')}`}
            </button>
          </div>

          <p style={{ fontSize: '14px', color: '#71717a', marginTop: '10px' }}>
            {t('step1Hint')}
          </p>
        </div>

        <div style={{
          margin: '20px 0',
          padding: '15px',
          background: 'rgba(249, 115, 22, 0.1)',
          borderRadius: '8px',
          borderLeft: '4px solid #f97316',
        }}>
          <span style={{
            background: '#f97316',
            color: 'white',
            padding: '2px 8px',
            borderRadius: '4px',
            fontWeight: 'bold',
          }}>
            Step 2
          </span>
          <p style={{ marginTop: '10px' }}>{t('step2Title')}</p>
          
          {submitError && (
            <div style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid #ef4444',
              borderRadius: '8px',
              padding: '12px',
              marginBottom: '12px',
              color: '#ef4444',
            }}>
              {submitError}
            </div>
          )}
          
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <input 
                type="text" 
                id="tweet_url"
                name="tweet_url"
                placeholder={t('tweetUrlPlaceholder')}
                value={tweetUrl}
                onChange={(e) => setTweetUrl(e.target.value)}
                disabled={submitting}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '2px solid #27272a',
                  borderRadius: '8px',
                  fontSize: '16px',
                  background: 'rgba(0, 0, 0, 0.6)',
                  color: '#e4e4e7',
                  margin: '10px 0',
                }}
              />
            </div>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={submitting || !tweetUrl.trim()}
            >
              {submitting ? t('verifying') : t('submitVerify')}
            </button>
          </form>
          
          <p style={{ fontSize: '14px', color: '#71717a', marginTop: '10px' }}>
            {t('tweetUrlExample')}
          </p>
        </div>
      </div>
    </div>
  )
}