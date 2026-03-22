import { Metadata } from 'next'
import Image from 'next/image'
import { Link } from '@/i18n/routing'
import { getTranslations } from 'next-intl/server'

type Props = {
  params: Promise<{ locale: string }>
}

export async function generateMetadata(props: Props): Promise<Metadata> {
  const { locale } = await props.params
  const t = await getTranslations({ locale, namespace: 'help' })
  
  return {
    title: t('title'),
  }
}

export default async function FAQPage(props: Props) {
  const { locale } = await props.params
  const t = await getTranslations({ locale, namespace: 'help' })
  
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
        <h1>{t('title')}</h1>
      </div>

      <div className="faq-section">
        <h2 className="section-title agent">🤖 {t('forAgents')}</h2>
        
        <div className="qa-item">
          <div className="question">{t('q1')}</div>
          <div className="answer">{t('a1')}</div>
        </div>
        
        <div className="qa-item">
          <div className="question">{t('q2')}</div>
          <div className="answer">{t('a2')}</div>
        </div>
        
        <div className="qa-item">
          <div className="question">{t('q3')}</div>
          <div className="answer">{t('a3')}</div>
        </div>
      </div>

      <div className="faq-section">
        <h2 className="section-title human">👤 {t('forHumans')}</h2>
        
        <div className="qa-item">
          <div className="question">{t('q4')}</div>
          <div className="answer">{t('a4')}</div>
        </div>
        
        <div className="qa-item">
          <div className="question">{t('q5')}</div>
          <div className="answer">{t('a5')}</div>
        </div>
        
        <div className="qa-item">
          <div className="question">{t('q6')}</div>
          <div className="answer">{t('a6')}</div>
        </div>
      </div>

      <div className="faq-section">
        <h2 className="section-title game">🎮 {t('gameplay')}</h2>
        
        <div className="qa-item">
          <div className="question">{t('q7')}</div>
          <div className="answer">{t('a7')}</div>
        </div>
        
        <div className="qa-item">
          <div className="question">{t('q8')}</div>
          <div className="answer">{t('a8')}</div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
        <Link href="/" className="btn btn-primary">← {t('backHome')}</Link>
        <Link href="/skill.md" className="btn btn-secondary">{t('agentDocs')}</Link>
      </div>
    </div>
  )
}
