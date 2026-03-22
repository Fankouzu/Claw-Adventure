#!/usr/bin/env bash
# Smoke test: unprefixed paths must hit next-intl + [locale] routes (not app-wide 404).
# Regression: narrow middleware matcher + localePrefix always caused /auth/*, /agents/* 404.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TMP_BODY="$(mktemp)"
PID=""

cleanup() {
  rm -f "$TMP_BODY" 2>/dev/null || true
  if [[ -n "$PID" ]]; then
    kill "$PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

echo "==> npm run build"
npm run build

PORT="${VERIFY_PORT:-43123}"
echo "==> next start on port $PORT"

npm run start -- -p "$PORT" &
PID=$!

READY=""
for _ in $(seq 1 60); do
  if curl -sf "http://127.0.0.1:${PORT}/" >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 1
done

if [[ -z "${READY}" ]]; then
  echo "ERROR: server did not become ready on port ${PORT}"
  exit 1
fi

expect_200() {
  local path="$1"
  local code
  code="$(curl -sS -o "$TMP_BODY" -w "%{http_code}" "http://127.0.0.1:${PORT}${path}")"
  if [[ "$code" != "200" ]]; then
    echo "FAIL ${path}: expected HTTP 200, got ${code}"
    head -c 800 "$TMP_BODY" || true
    echo
    exit 1
  fi
  echo "OK  ${path} -> 200"
}

echo "==> Checking unprefixed routes (default locale, no /en/)"
expect_200 "/auth/verify/smoke-verify-token"
expect_200 "/claim/smoke-claim-token"
expect_200 "/help"

echo "==> Checking prefixed non-default locale"
expect_200 "/zh-CN/help"

# /agents/[name] hits Prisma; without a reachable DB the page returns 500 (not a routing 404).
if [[ "${VERIFY_INCLUDE_AGENTS:-}" == "1" ]]; then
  echo "==> Checking /agents/* (VERIFY_INCLUDE_AGENTS=1, needs DATABASE_URL)"
  code="$(curl -sS -o "$TMP_BODY" -w "%{http_code}" "http://127.0.0.1:${PORT}/agents/__verify_no_such_agent__")"
  if [[ "$code" != "200" && "$code" != "404" ]]; then
    echo "FAIL /agents/__verify_no_such_agent__: expected HTTP 200 or 404, got ${code}"
    head -c 800 "$TMP_BODY" || true
    echo
    exit 1
  fi
  echo "OK  /agents/__verify_no_such_agent__ -> ${code}"
fi

echo "==> All unprefixed-route checks passed."
