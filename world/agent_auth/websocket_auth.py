"""
WebSocket 认证处理模块

实现 Agent 通过 API Key 认证连接到 Evennia 的握手流程。
"""
import hashlib
import hmac
import secrets
import time
import logging
from django.core.cache import cache
from django.utils import timezone
from .models import Agent

logger = logging.getLogger(__name__)

# 配置参数
CHALLENGE_EXPIRE_SECONDS = 30
NONCE_CACHE_SECONDS = 300
MAX_ATTEMPTS_PER_IP = 10
MAX_ATTEMPTS_PER_AGENT = 5
RATE_LIMIT_WINDOW = 60  # seconds


def generate_nonce() -> str:
    """生成随机 nonce"""
    return secrets.token_urlsafe(32)


def generate_challenge() -> dict:
    """
    生成认证挑战
    
    Returns:
        挑战字典，包含 nonce、timestamp 和 expires_in
    """
    nonce = generate_nonce()
    timestamp = int(time.time())
    
    # 缓存 nonce 用于后续验证
    cache_key = f"auth_nonce_{nonce}"
    cache.set(cache_key, timestamp, NONCE_CACHE_SECONDS)
    
    return {
        "type": "auth_challenge",
        "nonce": nonce,
        "timestamp": timestamp,
        "expires_in": CHALLENGE_EXPIRE_SECONDS
    }


def calculate_signature(nonce: str, api_key: str) -> str:
    """
    计算 HMAC-SHA256 签名
    
    Args:
        nonce: 服务器发送的 nonce
        api_key: 客户端的 API Key
        
    Returns:
        十六进制编码的签名
    """
    return hmac.new(
        api_key.encode('utf-8'),
        nonce.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def verify_signature(nonce: str, api_key: str, signature: str) -> bool:
    """
    验证签名
    
    Args:
        nonce: 服务器发送的 nonce
        api_key: Agent 的 API Key
        signature: 客户端发送的签名
        
    Returns:
        True 如果签名有效
    """
    expected = calculate_signature(nonce, api_key)
    return hmac.compare_digest(expected, signature)


def check_nonce_valid(nonce: str) -> bool:
    """
    检查 nonce 是否有效（未过期且未被使用）
    
    Args:
        nonce: 要检查的 nonce
        
    Returns:
        True 如果 nonce 有效
    """
    cache_key = f"auth_nonce_{nonce}"
    timestamp = cache.get(cache_key)
    
    if timestamp is None:
        return False
    
    # 检查是否过期
    if time.time() - timestamp > CHALLENGE_EXPIRE_SECONDS:
        cache.delete(cache_key)
        return False
    
    return True


def consume_nonce(nonce: str) -> bool:
    """
    消费 nonce（使其失效）
    
    Args:
        nonce: 要消费的 nonce
        
    Returns:
        True 如果成功消费
    """
    cache_key = f"auth_nonce_{nonce}"
    if cache.get(cache_key) is None:
        return False
    cache.delete(cache_key)
    return True


def check_rate_limit_ip(ip_address: str) -> bool:
    """
    检查 IP 速率限制
    
    Args:
        ip_address: 客户端 IP 地址
        
    Returns:
        True 如果允许请求
    """
    cache_key = f"auth_rate_ip_{ip_address}"
    current = cache.get(cache_key, 0)
    
    if current >= MAX_ATTEMPTS_PER_IP:
        return False
    
    cache.set(cache_key, current + 1, RATE_LIMIT_WINDOW)
    return True


def check_rate_limit_agent(agent_id: str) -> bool:
    """
    检查 Agent 速率限制
    
    Args:
        agent_id: Agent ID
        
    Returns:
        True 如果允许请求
    """
    cache_key = f"auth_rate_agent_{agent_id}"
    current = cache.get(cache_key, 0)
    
    if current >= MAX_ATTEMPTS_PER_AGENT:
        return False
    
    cache.set(cache_key, current + 1, RATE_LIMIT_WINDOW)
    return True


def verify_auth_response(
    nonce: str,
    api_key_prefix: str | None = None,
    signature: str | None = None,
    ip_address: str | None = None,
    api_key: str | None = None,
) -> dict:
    """
    Verify WebSocket auth_response: full api_key (over WSS) + HMAC-SHA256(nonce, key).

    Prefix-only auth is disabled: without the secret key material the server cannot
    verify an HMAC while storing only api_key_hash.
    """
    if ip_address and not check_rate_limit_ip(ip_address):
        return {
            "success": False,
            "error_code": "RATE_LIMITED",
            "message": "Too many authentication attempts from this IP",
        }

    if not check_nonce_valid(nonce):
        return {
            "success": False,
            "error_code": "CHALLENGE_EXPIRED",
            "message": "Challenge has expired or is invalid",
        }

    if not api_key or not api_key.startswith("claw_"):
        return {
            "success": False,
            "error_code": "UNSUPPORTED_AUTH_SCHEME",
            "message": (
                "Send api_key (over WSS) and signature. "
                "Prefix-only authentication is not supported."
            ),
        }

    if not signature:
        return {
            "success": False,
            "error_code": "SIGNATURE_REQUIRED",
            "message": "signature is required",
        }

    api_key_hash = Agent.hash_api_key(api_key)
    try:
        agent = Agent.objects.get(api_key_hash=api_key_hash)
    except Agent.DoesNotExist:
        return {
            "success": False,
            "error_code": "INVALID_API_KEY",
            "message": "Invalid API key",
        }

    if api_key_prefix is not None and not api_key.startswith(api_key_prefix):
        return {
            "success": False,
            "error_code": "PREFIX_MISMATCH",
            "message": "api_key_prefix does not match api_key",
        }

    if not verify_signature(nonce, api_key, signature):
        return {
            "success": False,
            "error_code": "SIGNATURE_MISMATCH",
            "message": "Invalid signature",
        }

    if not check_rate_limit_agent(str(agent.id)):
        return {
            "success": False,
            "error_code": "RATE_LIMITED",
            "message": "Too many authentication attempts for this agent",
        }

    if not agent.is_claimed:
        return {
            "success": False,
            "error_code": "AGENT_NOT_CLAIMED",
            "message": "Agent has not been claimed by a human",
        }

    consume_nonce(nonce)
    agent.update_last_active()

    return {
        "success": True,
        "agent": agent,
        "agent_id": str(agent.id),
        "agent_name": agent.name,
        "message": "Authentication successful",
    }


def verify_auth_with_api_key(nonce: str, api_key: str, ip_address: str = None) -> dict:
    """
    使用完整 API Key 验证认证（简化方案）
    
    客户端发送完整的 API Key，服务器验证后不存储。
    这是最简单的实现方式，适用于 MVP。
    
    Args:
        nonce: 客户端返回的 nonce
        api_key: 完整的 API Key
        ip_address: 客户端 IP
        
    Returns:
        结果字典
    """
    # 检查 IP 速率限制
    if ip_address and not check_rate_limit_ip(ip_address):
        return {
            "success": False,
            "error_code": "RATE_LIMITED",
            "message": "Too many authentication attempts from this IP"
        }
    
    # 检查 nonce 有效性
    if not check_nonce_valid(nonce):
        return {
            "success": False,
            "error_code": "CHALLENGE_EXPIRED",
            "message": "Challenge has expired or is invalid"
        }
    
    # 验证 API Key 格式
    if not api_key or not api_key.startswith('claw_'):
        return {
            "success": False,
            "error_code": "INVALID_API_KEY",
            "message": "Invalid API key format"
        }
    
    # 计算 hash 并查找 Agent
    api_key_hash = Agent.hash_api_key(api_key)
    try:
        agent = Agent.objects.get(api_key_hash=api_key_hash)
    except Agent.DoesNotExist:
        return {
            "success": False,
            "error_code": "INVALID_API_KEY",
            "message": "Invalid API key"
        }
    
    # 检查 Agent 速率限制
    if not check_rate_limit_agent(str(agent.id)):
        return {
            "success": False,
            "error_code": "RATE_LIMITED",
            "message": "Too many authentication attempts for this agent"
        }
    
    # 检查 Agent 是否已认领
    if not agent.is_claimed:
        return {
            "success": False,
            "error_code": "AGENT_NOT_CLAIMED",
            "message": "Agent has not been claimed by a human"
        }
    
    # 消费 nonce
    consume_nonce(nonce)
    
    # 更新最后活动时间
    agent.update_last_active()
    
    logger.info(f"Agent {agent.name} authenticated successfully")
    
    return {
        "success": True,
        "agent": agent,
        "agent_id": str(agent.id),
        "agent_name": agent.name,
        "message": "Authentication successful"
    }


def create_auth_result(success: bool, agent=None, error_code=None, message=None) -> dict:
    """
    创建认证结果消息
    
    Args:
        success: 是否成功
        agent: Agent 实例（成功时）
        error_code: 错误码（失败时）
        message: 消息
        
    Returns:
        结果字典
    """
    result = {
        "type": "auth_result",
        "status": "success" if success else "failed"
    }
    
    if success and agent:
        result["agent_id"] = str(agent.id)
        result["agent_name"] = agent.name
    
    if error_code:
        result["error_code"] = error_code
    
    if message:
        result["message"] = message
    
    return result