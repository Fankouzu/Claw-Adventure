// API Types

export interface RegisterRequest {
  name: string
  description?: string
  invitation_code: string
}

export interface RegisterResponse {
  agent_id: string
  name: string
  api_key: string
  claim_url: string
  claim_expires_at: string
}

export interface ProfileResponse {
  agent_id: string
  name: string
  level: number
  experience: number
  claim_status: string
  twitter_handle?: string
  is_claimed?: boolean
  created_at: string
  last_active_at?: string
}

export interface SetupEmailRequest {
  email: string
}

export interface SetupEmailResponse {
  status: string
  email: string
}

export interface ClaimInfoResponse {
  agent_id: string
  name: string
  claim_token: string
  claim_status: string
  share_url: string
  expires_at?: string
}

export interface VerifyTweetRequest {
  tweet_url: string
}

export interface VerifyTweetResponse {
  status: string
  message: string
  twitter_handle: string
  agent: {
    id: string
    name: string
  }
}

export interface LoginRequest {
  email: string
}

export interface LoginResponse {
  status: string
  email: string
}

export interface DashboardResponse {
  email: string
  agents: Array<{
    id: string
    name: string
    level: number
    experience: number
    claim_status: string
    twitter_handle?: string
  }>
}