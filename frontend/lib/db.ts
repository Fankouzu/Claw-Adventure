import 'dotenv/config'
import { PrismaClient } from './generated/prisma'
import { PrismaPg } from '@prisma/adapter-pg'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

function createPrismaClient() {
  const dbUrl = process.env.DATABASE_URL
  
  if (!dbUrl) {
    throw new Error('DATABASE_URL is not set')
  }
  
  const adapter = new PrismaPg({ connectionString: dbUrl })
  
  return new PrismaClient({ adapter })
}

export const prisma = globalForPrisma.prisma ?? createPrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma