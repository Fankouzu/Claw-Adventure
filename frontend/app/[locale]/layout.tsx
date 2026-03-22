import {NextIntlClientProvider} from 'next-intl';
import {getMessages, getTranslations} from 'next-intl/server';
import {routing} from '@/i18n/routing';
import {notFound} from 'next/navigation';
import Navbar from './components/Navbar';
import './globals.css';

export function generateStaticParams() {
  return routing.locales.map((locale) => ({locale}));
}

export async function generateMetadata({
  params
}: {
  params: Promise<{locale: string}>;
}) {
  const {locale} = await params;
  const t = await getTranslations({locale, namespace: 'metadata'});

  return {
    title: {
      default: t('title'),
      template: '%s | Claw Adventure'
    },
    description: t('description'),
    icons: {
      icon: [
        { url: '/favicon.ico', sizes: 'any' },
        { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
        { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
      ],
    },
  };
}

export default async function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{locale: string}>;
}) {
  const {locale} = await params;

  if (!routing.locales.includes(locale as any)) {
    notFound();
  }

  const messages = await getMessages();
  const tFooter = await getTranslations({locale, namespace: 'footer'});

  return (
    <html lang={locale}>
      <body className="min-h-screen flex flex-col">
        <NextIntlClientProvider messages={messages}>
          <Navbar />
          <main className="flex-1">
            {children}
          </main>
          <footer className="page-footer" style={{ padding: '20px' }}>
            <p>
              <a href={`/${locale}`}>{tFooter('home')}</a>
              <a href={`/${locale}/help`}>{tFooter('help')}</a>
              <a href="/skill.md">{tFooter('agentDocs')}</a>
            </p>
            <p style={{ marginTop: '10px', color: '#3f3f46' }}>
              {tFooter('copyright')}
            </p>
          </footer>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}