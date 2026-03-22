'use client'

import { useState, useEffect, useCallback } from 'react'
import { useTranslations, useLocale } from 'next-intl'
import Image from 'next/image'
import { Link } from '@/i18n/routing'
import LanguageSwitcher from './LanguageSwitcher'

export default function Navbar() {
  const t = useTranslations('nav')
  const locale = useLocale()
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null)

  const checkAuth = useCallback(async () => {
    try {
      const res = await fetch('/api/dashboard', {
        credentials: 'include',
      })
      setIsLoggedIn(res.ok)
    } catch {
      setIsLoggedIn(false)
    }
  }, [])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  return (
    <nav className="navbar">
      <Link href="/" className="navbar-brand">
        <Image
          src="/icon-512x512.png"
          alt="Claw Adventure"
          width={40}
          height={40}
          priority
        />
        <span className="brand-title">Claw Adventure</span>
      </Link>
      <div className="navbar-nav" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <LanguageSwitcher />
        {isLoggedIn === null ? (
          <div style={{ width: '40px', height: '40px' }} />
        ) : isLoggedIn ? (
          <Link href="/dashboard" className="nav-icon-btn" title={t('dashboard')}>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-label={t('dashboard')}>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </Link>
        ) : (
          <Link href="/auth/login" className="nav-icon-btn" title={t('login')}>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-label={t('login')}>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </Link>
        )}
      </div>
    </nav>
  )
}