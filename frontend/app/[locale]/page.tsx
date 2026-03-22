import { getLandingPageStats } from '@/lib/public-stats'
import { HomePageClient } from './home-page-client'

/** Live counts from PostgreSQL; cannot be statically baked at build time. */
export const dynamic = 'force-dynamic'

export default async function LocaleHomePage() {
  const stats = await getLandingPageStats()
  return <HomePageClient stats={stats} />
}
