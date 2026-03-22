'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

interface PageProps {
  params: { token: string }
}

export default function VerifyPage({ params }: PageProps) {
  const router = useRouter()
  const { token } = params
  const [error, setError] = useState('')

  useEffect(() => {
    const verifyToken = async () => {
      try {
        const response = await fetch(`/api/auth/verify/${token}`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
        })

        const data = await response.json()

        if (!response.ok) {
          setError(data.error || 'Verification failed')
          return
        }

        // Successfully verified, redirect to dashboard
        router.push('/dashboard')
      } catch (err) {
        setError('Network error. Please try again.')
      }
    }

    verifyToken()
  }, [token, router])

  if (error) {
    return (
      <div className="max-w-md mx-auto px-4 py-16">
        <div className="bg-gray-800 border border-red-700 rounded-lg p-6 text-center">
          <h1 className="text-xl font-semibold text-red-500 mb-2">Verification Failed</h1>
          <p className="text-gray-400 mb-4">{error}</p>
          <a
            href="/auth/login"
            className="inline-block bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg transition-colors"
          >
            Back to Login
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-md mx-auto px-4 py-16">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 text-center">
        <div className="mb-4">
          <div className="w-12 h-12 mx-auto border-4 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
        <h1 className="text-xl font-semibold text-white mb-2">Verifying...</h1>
        <p className="text-gray-400">
          Please wait while we verify your login token.
        </p>
      </div>
    </div>
  )
}
