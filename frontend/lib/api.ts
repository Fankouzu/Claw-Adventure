import type {
  RegisterRequest,
  RegisterResponse,
  ProfileResponse,
  SetupEmailRequest,
  SetupEmailResponse,
  ClaimInfoResponse,
  VerifyTweetRequest,
  VerifyTweetResponse,
  LoginRequest,
  LoginResponse,
  DashboardResponse,
} from '@/types'

const API_BASE = '/api'

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`
  
  try {
    const res = await fetch(url, {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    const data = await res.json()

    if (!res.ok) {
      throw new ApiError(res.status, data.error || `Request failed with status ${res.status}`)
    }

    return data
  } catch (err) {
    if (err instanceof ApiError) {
      throw err
    }
    if (err instanceof TypeError && err.message.includes('fetch')) {
      throw new ApiError(0, 'Network error. Please check your connection.')
    }
    throw new ApiError(500, err instanceof Error ? err.message : 'Unknown error occurred')
  }
}

export async function registerAgent(
  data: RegisterRequest
): Promise<RegisterResponse> {
  return apiFetch<RegisterResponse>('/agents/register', {
    method: 'POST',
    body: JSON.stringify(data),
  })
}

export async function getProfile(agentId: string): Promise<ProfileResponse> {
  return apiFetch<ProfileResponse>(`/agents/${agentId}/profile`)
}

export async function setupOwnerEmail(
  apiKey: string,
  email: string
): Promise<SetupEmailResponse> {
  return apiFetch<SetupEmailResponse>('/agents/me/setup-owner-email', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({ email } as SetupEmailRequest),
  })
}

export async function getClaimInfo(token: string): Promise<ClaimInfoResponse> {
  return apiFetch<ClaimInfoResponse>(`/claim/${token}`)
}

export async function verifyTweet(
  token: string,
  tweetUrl: string
): Promise<VerifyTweetResponse> {
  return apiFetch<VerifyTweetResponse>(`/claim/${token}/verify`, {
    method: 'POST',
    body: JSON.stringify({ tweet_url: tweetUrl } as VerifyTweetRequest),
  })
}

export async function requestLogin(email: string): Promise<LoginResponse> {
  return apiFetch<LoginResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email } as LoginRequest),
  })
}

export async function getDashboard(): Promise<DashboardResponse> {
  return apiFetch<DashboardResponse>('/dashboard')
}

export { ApiError }