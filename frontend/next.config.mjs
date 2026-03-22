import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./i18n/request.ts');

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable gzip compression
  compress: true,
  // Remove X-Powered-By header for security
  poweredByHeader: false,
  images: {
    domains: ['pbs.twimg.com', 'abs.twimg.com'],
    // Enable modern image formats
    formats: ['image/avif', 'image/webp'],
    // Image optimization settings
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
  },
  // 修复开发模式下的 chunk 缓存问题
  experimental: {
    // 使用更稳定的 webpack 配置
    optimizePackageImports: ['react-markdown', 'remark-gfm'],
  },
  // 强制使用稳定的 chunk ID
  webpack: (config, { dev }) => {
    if (dev) {
      config.optimization = {
        ...config.optimization,
        chunkIds: 'named', // 使用命名 chunk ID，避免数字 ID 不一致
      }
    }
    return config
  },
  // Static asset caching headers
  async headers() {
    return [
      {
        source: '/:all*(svg|jpg|jpeg|png|webp|avif|ico)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ]
  },
}

export default withNextIntl(nextConfig)