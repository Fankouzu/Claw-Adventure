"""
Internal / server-to-server API helpers (experience, future hooks).
"""
import hmac
import ipaddress
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def client_ip(request) -> str:
    """Best-effort client IP (honors X-Forwarded-For first hop)."""
    xff = (request.META.get("HTTP_X_FORWARDED_FOR") or "").strip()
    if xff:
        return xff.split(",")[0].strip()
    return (request.META.get("REMOTE_ADDR") or "").strip() or ""


def _is_private_or_loopback(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        return addr.is_private or addr.is_loopback
    except ValueError:
        return False


def experience_request_authorized(request) -> bool:
    """
    True if the caller may use POST .../experience.

    - Prefer shared secret: HTTP_X_CLAW_INTERNAL_KEY or Authorization: Bearer <secret>
      matching settings.AGENT_INTERNAL_API_SECRET (non-empty).
    - If secret is not configured, allow only when AGENT_EXPERIENCE_ALLOW_PRIVATE_IP
      and the client IP is loopback/private (dev / same-host game server).
    """
    secret = (getattr(settings, "AGENT_INTERNAL_API_SECRET", None) or "").strip()
    if secret:
        header = (request.META.get("HTTP_X_CLAW_INTERNAL_KEY") or "").strip()
        if header and hmac.compare_digest(header, secret):
            return True
        auth = (request.META.get("HTTP_AUTHORIZATION") or "").strip()
        if auth.lower().startswith("bearer "):
            token = auth[7:].strip()
            if token and hmac.compare_digest(token, secret):
                return True
        logger.warning("Experience API: rejected request (invalid internal secret)")
        return False

    if getattr(settings, "AGENT_EXPERIENCE_ALLOW_PRIVATE_IP", False):
        ip = client_ip(request)
        if _is_private_or_loopback(ip):
            return True
        logger.warning("Experience API: rejected request (no secret; IP not private: %s)", ip)
        return False

    logger.error(
        "Experience API: AGENT_INTERNAL_API_SECRET unset and private-IP bypass disabled; denying all"
    )
    return False
