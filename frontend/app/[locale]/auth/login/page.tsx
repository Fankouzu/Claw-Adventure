'use client'

import { useState, useCallback } from 'react'
import Image from 'next/image'
import { Link } from '@/i18n/routing'
import { useTranslations } from 'next-intl'
import { requestLogin, ApiError } from '@/lib/api'

export default function LoginPage() {
  const t = useTranslations('login')
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      const result = await requestLogin(email)
      setSuccess(`${t('successPrefix')} ${result.email}. ${t('successSuffix')}`)
      setEmail('')
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message)
      } else {
        setError(t('errorGeneric'))
      }
    } finally {
      setLoading(false)
    }
  }, [email, t])

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
          <h1>{t('title')}</h1>
        </div>

      {/* Login Card */}
          <div style={{ maxWidth: '480px', margin: '0 auto' }}>
            <div className="card">
              <h2 style={{ textAlign: 'center', marginBottom: '8px' }}>{t('title')}</h2>
              <p style={{ textAlign: 'center', color: '#71717a', marginBottom: '24px' }}>
                {t('subtitle')}
              </p>

          {success && (
            <div style={{
              background: 'rgba(34, 197, 94, 0.1)',
              border: '1px solid #22c55e',
              borderRadius: '8px',
              padding: '12px',
              marginBottom: '16px',
              color: '#22c55e',
            }}>
              {success}
            </div>
          )}

          {error && (
            <div style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid #ef4444',
              borderRadius: '8px',
              padding: '12px',
              marginBottom: '16px',
              color: '#ef4444',
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="email">{t('emailLabel')}</label>
              <input 
                type="email" 
                id="email" 
                name="email" 
                placeholder={t('emailPlaceholder')}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                required 
              />
            </div>
            <button 
              type="submit" 
              className="btn btn-primary" 
              style={{ width: '100%' }}
              disabled={loading}
            >
              {loading ? t('sending') : t('sendButton')}
            </button>
          </form>

          <div className="info-box">
            <h3>{t('infoTitle')}</h3>
            <p>{t('infoP1')}</p>
            <p style={{ marginTop: '12px' }}>
              <strong>{t('infoP2Prefix')}</strong><br />
              <code style={{ 
                display: 'block', 
                marginTop: '4px', 
                padding: '8px', 
                background: 'rgba(0,0,0,0.4)', 
                borderRadius: '4px',
                fontSize: '13px',
              }}>
                {t('infoP2Command')}
              </code>
            </p>
            <p style={{ marginTop: '12px' }}>
              {t('infoP3Prefix')}<br />
              <code style={{ 
                display: 'block', 
                marginTop: '4px', 
                padding: '8px', 
                background: 'rgba(0,0,0,0.4)', 
                borderRadius: '4px',
                fontSize: '13px',
              }}>
                {t('infoP3Command1')}<br />
                {t('infoP3Command2')}
              </code>
            </p>
            <p style={{ marginTop: '12px', fontSize: '13px', color: '#71717a' }}>
              {t('infoP4')}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}