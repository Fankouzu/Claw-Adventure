import {defineRouting} from 'next-intl/routing';
import {createNavigation} from 'next-intl/navigation';

export const routing = defineRouting({
  locales: ['en', 'zh-CN', 'zh-TW', 'ja'],
  defaultLocale: 'en',
  // Emails and APIs use paths without /en/ (e.g. /auth/verify/:token, /claim/:token).
  // 'as-needed' keeps default-locale URLs unprefixed while other locales stay prefixed.
  localePrefix: 'as-needed',
});

export const {Link, redirect, usePathname, useRouter, getPathname} =
  createNavigation(routing);