"""
Twitter / X URL handling for Agent claim.

Default: weak server-side verification (URL shape + handle). Strong checks
(oEmbed + claim_token in text) are optional for deployments that can reach
publish.twitter.com and want extra assurance.

Product expectation: richer verification can be implemented in the frontend;
this backend stays compatible with Railway-style game stacks without relying
on server-side Twitter access for the default path.
"""
import logging
import re

import requests
from django.conf import settings
from django.utils import timezone

from .models import Agent

logger = logging.getLogger(__name__)

OEMBED_URL = "https://publish.twitter.com/oembed"


def extract_tweet_id(tweet_url: str) -> str | None:
    """Extract tweet_id from URL (twitter.com or x.com)."""
    if not tweet_url:
        return None

    pattern = r"(?:twitter\.com|x\.com)/\w+/status/(\d+)"
    match = re.search(pattern, tweet_url)

    if match:
        return match.group(1)

    return None


def extract_twitter_handle(tweet_url: str) -> str | None:
    """Extract Twitter username from tweet URL."""
    if not tweet_url:
        return None

    pattern = r"(?:twitter\.com|x\.com)/(\w+)/status/\d+"
    match = re.search(pattern, tweet_url)

    if match:
        return match.group(1)

    return None


def verify_tweet_exists_best_effort(tweet_id: str) -> None:
    """
    Optional HEAD check; failures are ignored (weak path).

    Does not block claim; logs at debug only.
    """
    try:
        url = f"https://x.com/i/status/{tweet_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ClawAdventure/1.0; +claim-weak)",
        }
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        logger.debug("claim weak HEAD %s -> %s", tweet_id, response.status_code)
    except Exception as exc:
        logger.debug("claim weak HEAD skipped: %s", exc)


def fetch_tweet_visible_text_oembed(tweet_url: str) -> str | None:
    """Used only when AGENT_CLAIM_SERVER_STRICT_VERIFY is enabled."""
    try:
        response = requests.get(
            OEMBED_URL,
            params={"url": tweet_url.strip(), "omit_script": "true"},
            timeout=15,
            headers={"User-Agent": "ClawAdventure/1.0 (claim-verify-strict)"},
        )
        if response.status_code != 200:
            logger.info("oEmbed HTTP %s for strict claim verify", response.status_code)
            return None
        payload = response.json()
        html = payload.get("html") or ""
        text = re.sub(r"<[^>]+>", " ", html)
        return " ".join(text.split())
    except Exception:
        logger.exception("oEmbed request failed for strict claim verify")
        return None


def _tweet_contains_claim_proof(visible_text: str, agent: Agent) -> tuple[bool, str | None]:
    """Strict mode: visible text must include claim_token and optional substring."""
    if agent.claim_token not in visible_text:
        return (
            False,
            "Could not confirm your tweet contains the claim link or token. "
            "Post using the share button on the claim page (public account), then try again.",
        )
    extra = (getattr(settings, "AGENT_CLAIM_REQUIRED_SUBSTRING", None) or "").strip()
    if extra and extra not in visible_text:
        return (
            False,
            "Tweet must include the required phrase from the claim instructions.",
        )
    return True, None


def complete_agent_claim(agent: Agent, tweet_url: str, twitter_handle: str) -> bool:
    """Persist claim completion."""
    try:
        agent.tweet_url = tweet_url
        agent.twitter_handle = twitter_handle
        agent.claim_status = Agent.ClaimStatus.CLAIMED
        agent.claimed_at = timezone.now()
        agent.save()

        logger.info("Agent %s claimed by @%s", agent.name, twitter_handle)
        return True

    except Exception:
        logger.exception("Failed to complete agent claim")
        return False


def verify_and_claim_agent(agent: Agent, tweet_url: str) -> dict:
    """
    Complete claim after basic URL checks.

    - Default (weak): valid x.com/twitter status URL + handle; optional best-effort HEAD.
    - Strict (AGENT_CLAIM_SERVER_STRICT_VERIFY): oEmbed must return text containing
      claim_token and optional AGENT_CLAIM_REQUIRED_SUBSTRING.
    """
    tweet_id = extract_tweet_id(tweet_url)
    if not tweet_id:
        return {
            "success": False,
            "error": (
                "Invalid tweet URL format. Expected: "
                "https://x.com/username/status/1234567890123456789"
            ),
        }

    twitter_handle = extract_twitter_handle(tweet_url)
    if not twitter_handle:
        return {
            "success": False,
            "error": "Could not extract Twitter handle from URL",
        }

    strict = getattr(settings, "AGENT_CLAIM_SERVER_STRICT_VERIFY", False)

    if strict:
        visible = fetch_tweet_visible_text_oembed(tweet_url)
        if visible is None:
            return {
                "success": False,
                "error": (
                    "Could not load tweet content (deleted, private, or network error). "
                    "Ensure the post is public and retry."
                ),
            }

        ok, err = _tweet_contains_claim_proof(visible, agent)
        if not ok:
            return {"success": False, "error": err}
    else:
        verify_tweet_exists_best_effort(tweet_id)

    if complete_agent_claim(agent, tweet_url, twitter_handle):
        return {
            "success": True,
            "message": f"Agent claimed by @{twitter_handle}",
        }
    return {
        "success": False,
        "error": "Failed to update agent status",
    }
