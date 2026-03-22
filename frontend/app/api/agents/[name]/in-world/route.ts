import { NextRequest, NextResponse } from 'next/server'

function trimBase(url: string) {
  return url.replace(/\/$/, '')
}

/**
 * Proxies to Evennia Django: GET /api/agents/name/{name}/in-world
 * Used when the browser or SSR cannot reach Evennia directly.
 */
export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ name: string }> },
) {
  const { name } = await params
  const decoded = decodeURIComponent(name)
  const evennia = process.env.CLAW_EVENNIA_API_URL

  if (!evennia) {
    return NextResponse.json(
      {
        agent_id: '',
        name: decoded,
        in_world_status: 'game_api_unconfigured',
        in_world: null,
      },
      { status: 200 },
    )
  }

  const url = `${trimBase(evennia)}/api/agents/name/${encodeURIComponent(decoded)}/in-world`
  try {
    const res = await fetch(url, { next: { revalidate: 20 } })
    const body = await res.text()
    return new NextResponse(body, {
      status: res.status,
      headers: { 'Content-Type': 'application/json' },
    })
  } catch (e) {
    console.error('in-world proxy:', e)
    return NextResponse.json(
      { error: 'Upstream game API unreachable' },
      { status: 502 },
    )
  }
}
