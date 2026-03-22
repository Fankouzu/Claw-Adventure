import createMiddleware from 'next-intl/middleware';
import {routing} from './i18n/routing';

export default createMiddleware(routing);

// Match all non-static routes so unprefixed paths (e.g. /auth/verify/..., /agents/...)
// are handled by next-intl and mapped to [locale] segments. Previously only `/` and
// `/{locale}/*` matched, so `/auth/*` never hit the middleware and returned 404.
export const config = {
  matcher: ['/((?!api|_next|_next/static|_next/image|_vercel|.*\\..*).*)'],
};