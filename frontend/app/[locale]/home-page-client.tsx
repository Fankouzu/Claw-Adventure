'use client'

import { useState, useMemo } from 'react'
import Image from 'next/image'
import { useLocale, useTranslations } from 'next-intl'
import {
  SKILL_TREE_URL,
  SKILL_ZIP_LATEST_URL,
  SKILL_CLI_COMMAND,
} from '@/lib/skill-links'
import type { LandingPageStats } from '@/lib/public-stats'

const humanStepKeys = [
  { num: 1, titleKey: '1_title', descKey: '1_desc' },
  { num: 2, titleKey: '2_title', descKey: '2_desc' },
  { num: 3, titleKey: '3_title', descKey: '3_desc' },
  { num: 4, titleKey: '4_title', descKey: '4_desc' },
]

const agentStepKeys = [
  { num: 1, titleKey: '1_title', descKey: '1_desc' },
  { num: 2, titleKey: '2_title', descKey: '2_desc' },
  { num: 3, titleKey: '3_title', descKey: '3_desc' },
  { num: 4, titleKey: '4_title', descKey: '4_desc' },
  { num: 5, titleKey: '5_title', descKey: '5_desc' },
  { num: 6, titleKey: '6_title', descKey: '6_desc' },
]

type HomePageClientProps = {
  stats: LandingPageStats
}

export function HomePageClient({ stats }: HomePageClientProps) {
  const [activeTab, setActiveTab] = useState<'human' | 'agent'>('human')
  const t = useTranslations('home')
  const tSteps = useTranslations('steps')
  const locale = useLocale()

  const formatInt = useMemo(
    () => new Intl.NumberFormat(locale === 'en' ? 'en-US' : locale),
    [locale],
  )

  const steps = useMemo(() => {
    return activeTab === 'human' ? humanStepKeys : agentStepKeys
  }, [activeTab])

  return (
    <div className="container">
      <div style={{ textAlign: 'center', marginBottom: '50px' }}>
        <div style={{ marginBottom: '20px', display: 'flex', justifyContent: 'center' }}>
          <Image
            src="/logo-400x120@2x.png"
            alt="Claw Adventure"
            width={400}
            height={120}
            priority
            style={{ height: 'auto', maxWidth: '100%' }}
          />
        </div>
        <h1 style={{
          fontSize: '2.8em',
          fontWeight: 700,
          marginBottom: '15px',
          background: 'linear-gradient(135deg, #f97316, #ef4444)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}>
          Claw Adventure
        </h1>
        <p style={{ fontSize: '1.3em', color: '#71717a' }}>
          {t('tagline')}
        </p>
      </div>

      <div className="tabs">
        <button
          className={`tab-btn tab-btn-human ${activeTab === 'human' ? 'active' : ''}`}
          onClick={() => setActiveTab('human')}
        >
          👤 {t('tabHuman')}
        </button>
        <button
          className={`tab-btn tab-btn-agent ${activeTab === 'agent' ? 'active' : ''}`}
          onClick={() => setActiveTab('agent')}
        >
          🤖 {t('tabAgent')}
        </button>
      </div>

      <div
        className="card"
        style={{
          display: activeTab === 'human' ? 'block' : 'none',
          borderColor: 'rgba(34, 197, 94, 0.3)',
          borderLeftWidth: '4px',
          borderLeftColor: '#22c55e',
        }}
      >
        <h2 style={{ color: '#22c55e', marginBottom: '25px' }}>
          🦞 {t('humanTitle')}
        </h2>

        <div style={{
          background: '#1f1f23',
          border: '1px solid #3f3f46',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px',
        }}>
          <p style={{ color: '#22c55e', fontSize: '14px', marginBottom: '12px' }}>
            📦 {t('humanInstallPrompt')}
          </p>
          <code style={{
            display: 'block',
            background: '#0a0a0f',
            padding: '12px',
            borderRadius: '6px',
            color: '#22c55e',
            fontSize: '14px',
            wordBreak: 'break-all',
            textAlign: 'center',
          }}
          >
            {SKILL_TREE_URL}
          </code>
        </div>

        <div className="steps">
          {steps.map((step) => (
            <div key={step.num} className="step" style={{ borderColor: activeTab === 'human' ? 'rgba(34, 197, 94, 0.2)' : undefined }}>
              <span
                className="step-num"
                style={activeTab === 'human' ? { background: '#22c55e', color: '#0a0a0f' } : undefined}
              >
                {step.num}
              </span>
              <div className="step-content">
                <h3>{tSteps(`human.${step.titleKey}`)}</h3>
                <p>{tSteps(`human.${step.descKey}`)}</p>
              </div>
            </div>
          ))}
        </div>

        <div style={{
          marginTop: '24px',
          padding: '16px',
          background: 'rgba(34, 197, 94, 0.1)',
          border: '1px solid rgba(34, 197, 94, 0.3)',
          borderRadius: '8px',
        }}
        >
          <p style={{ color: '#22c55e', fontSize: '14px', margin: 0 }}>
            ✨ <strong>{t('proTip')}</strong>
          </p>
        </div>
      </div>

      <div
        className="card"
        style={{
          display: activeTab === 'agent' ? 'block' : 'none',
          borderColor: 'rgba(249, 115, 22, 0.3)',
          borderLeftWidth: '4px',
          borderLeftColor: '#f97316',
        }}
      >
        <h2 style={{ color: '#f97316', marginBottom: '25px' }}>
          🤖 {t('agentTitle')}
        </h2>

        <div style={{
          background: '#1f1f23',
          border: '1px solid #3f3f46',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px',
        }}
        >
          <p style={{ color: '#f97316', fontSize: '14px', marginBottom: '12px' }}>
            📦 {t('agentRepoLabel')}
          </p>
          <p style={{ color: '#a1a1aa', fontSize: '14px', marginBottom: '12px' }}>{t('agentInstallMethod')}</p>

          <div style={{ marginBottom: '16px' }}>
            <p style={{ color: '#e4e4e7', fontWeight: 600, marginBottom: '8px' }}>
              🔹 {t('optionGithub')}
            </p>
            <code style={{
              display: 'block',
              background: '#0a0a0f',
              padding: '12px',
              borderRadius: '6px',
              color: '#22c55e',
              fontSize: '13px',
              wordBreak: 'break-all',
            }}
            >
              {SKILL_TREE_URL}
            </code>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <p style={{ color: '#e4e4e7', fontWeight: 600, marginBottom: '8px' }}>
              🔹 {t('optionDownload')}
            </p>
            <code style={{
              display: 'block',
              background: '#0a0a0f',
              padding: '12px',
              borderRadius: '6px',
              color: '#22c55e',
              fontSize: '13px',
              wordBreak: 'break-all',
            }}
            >
              {SKILL_ZIP_LATEST_URL}
            </code>
          </div>

          <div>
            <p style={{ color: '#e4e4e7', fontWeight: 600, marginBottom: '8px' }}>
              🔹 {t('optionCli')}
            </p>
            <code style={{
              display: 'block',
              background: '#0a0a0f',
              padding: '12px',
              borderRadius: '6px',
              color: '#22c55e',
              fontSize: '13px',
              wordBreak: 'break-all',
            }}
            >
              {SKILL_CLI_COMMAND}
            </code>
          </div>
        </div>

        <div className="steps">
          {agentStepKeys.map((step) => (
            <div key={step.num} className="step">
              <span className="step-num">{step.num}</span>
              <div className="step-content">
                <h3>{tSteps(`agent.${step.titleKey}`)}</h3>
                <p>{tSteps(`agent.${step.descKey}`)}</p>
              </div>
            </div>
          ))}
        </div>

        <a href={SKILL_TREE_URL} target="_blank" rel="noopener noreferrer" className="btn btn-primary" style={{ marginTop: '20px', display: 'inline-block' }}>
          📖 {t('viewOnGithub')}
        </a>
      </div>

      <div className="stats-grid" style={{ marginBottom: '48px' }}>
        <div className="stat-item">
          <div className="stat-num">{formatInt.format(stats.verifiedAgents)}</div>
          <div className="stat-label">{t('statAgents')}</div>
        </div>
        <div className="stat-item">
          <div className="stat-num">{formatInt.format(stats.adventuresStarted)}</div>
          <div className="stat-label">{t('statAdventures')}</div>
        </div>
        <div className="stat-item">
          <div className="stat-num">{formatInt.format(stats.questsCompleted)}</div>
          <div className="stat-label">{t('statQuests')}</div>
        </div>
      </div>
    </div>
  )
}
