"""
Twitter 推文验证服务

用于验证用户提交的推文 URL 是否包含正确的 claim_url。
采用网页抓取方式（方案 B），后续可升级为 Twitter API v2。
"""
import re
import logging
from django.utils import timezone
from .models import Agent

logger = logging.getLogger(__name__)


def extract_tweet_id(tweet_url: str) -> str | None:
    """
    从推文 URL 提取 tweet_id
    
    支持的 URL 格式：
    - https://twitter.com/username/status/123456789
    - https://x.com/username/status/123456789
    
    Args:
        tweet_url: 推文 URL
        
    Returns:
        tweet_id 字符串，或 None（如果 URL 无效）
    """
    if not tweet_url:
        return None
    
    # 匹配 twitter.com 或 x.com 的推文 URL
    pattern = r'(?:twitter\.com|x\.com)/\w+/status/(\d+)'
    match = re.search(pattern, tweet_url)
    
    if match:
        return match.group(1)
    
    return None


def extract_twitter_handle(tweet_url: str) -> str | None:
    """
    从推文 URL 提取 Twitter 用户名
    
    Args:
        tweet_url: 推文 URL
        
    Returns:
        Twitter 用户名（不带 @），或 None
    """
    if not tweet_url:
        return None
    
    pattern = r'(?:twitter\.com|x\.com)/(\w+)/status/\d+'
    match = re.search(pattern, tweet_url)
    
    if match:
        return match.group(1)
    
    return None


def fetch_tweet_content(tweet_id: str) -> dict | None:
    """
    获取推文内容（网页抓取方式）
    
    注意：这是简化版本，使用网页抓取。
    生产环境建议使用 Twitter API v2 获取更稳定的结果。
    
    Args:
        tweet_id: 推文 ID
        
    Returns:
        包含推文信息的字典，或 None（如果获取失败）
    """
    try:
        import requests
        from urllib.parse import quote
        
        # 构建推文 URL
        url = f"https://x.com/i/status/{tweet_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # 从 HTML 中提取推文文本（简化版）
            # 注意：实际生产中可能需要更复杂的解析
            html_content = response.text
            
            # 尝试从 meta 标签提取
            title_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]*)"', html_content)
            desc_match = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', html_content)
            
            text = ""
            if desc_match:
                text = desc_match.group(1)
            elif title_match:
                text = title_match.group(1)
            
            return {
                'tweet_id': tweet_id,
                'text': text,
                'url': url,
            }
        
        logger.warning(f"Failed to fetch tweet {tweet_id}: HTTP {response.status_code}")
        return None
        
    except requests.RequestException as e:
        logger.error(f"Request error fetching tweet {tweet_id}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching tweet {tweet_id}: {e}")
        return None


def verify_tweet_contains_claim_url(tweet_content: str, claim_url: str) -> bool:
    """
    检查推文是否包含正确的 claim_url
    
    Args:
        tweet_content: 推文文本内容
        claim_url: 期望的 claim URL
        
    Returns:
        True 如果推文包含 claim_url，否则 False
    """
    if not tweet_content or not claim_url:
        return False
    
    # 直接检查 claim_url 是否在推文中
    if claim_url in tweet_content:
        return True
    
    # 也检查 claim_token（以防 URL 被截断）
    # claim_url 格式: https://mudclaw.net/claim/{token}
    token_match = re.search(r'/claim/([a-zA-Z0-9_-]+)', claim_url)
    if token_match:
        token = token_match.group(1)
        if token in tweet_content:
            return True
    
    return False


def complete_agent_claim(agent: Agent, tweet_url: str, twitter_handle: str) -> bool:
    """
    完成 Agent 认领流程
    
    Args:
        agent: Agent 实例
        tweet_url: 验证通过的推文 URL
        twitter_handle: 推文作者的 Twitter 用户名
        
    Returns:
        True 如果成功更新，否则 False
    """
    try:
        agent.tweet_url = tweet_url
        agent.twitter_handle = twitter_handle
        agent.claim_status = Agent.ClaimStatus.CLAIMED
        agent.claimed_at = timezone.now()
        agent.save()
        
        logger.info(f"Agent {agent.name} claimed by @{twitter_handle}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to complete agent claim: {e}")
        return False


def verify_and_claim_agent(agent: Agent, tweet_url: str) -> dict:
    """
    完整的验证和认领流程
    
    Args:
        agent: Agent 实例
        tweet_url: 用户提交的推文 URL
        
    Returns:
        结果字典，包含 success 和 message
    """
    # 提取 tweet_id
    tweet_id = extract_tweet_id(tweet_url)
    if not tweet_id:
        return {
            'success': False,
            'error': 'Invalid tweet URL format'
        }
    
    # 提取 twitter_handle
    twitter_handle = extract_twitter_handle(tweet_url)
    if not twitter_handle:
        return {
            'success': False,
            'error': 'Could not extract Twitter handle from URL'
        }
    
    # 获取推文内容
    tweet_data = fetch_tweet_content(tweet_id)
    if not tweet_data:
        # 如果无法获取推文内容，记录日志但允许继续（测试环境）
        logger.warning(f"Could not fetch tweet content for {tweet_id}, proceeding with URL validation only")
        # 只验证 URL 中的 token 是否匹配
        if agent.claim_token in tweet_url or agent.claim_url in tweet_url:
            complete_agent_claim(agent, tweet_url, twitter_handle)
            return {
                'success': True,
                'message': f'Agent claimed by @{twitter_handle}'
            }
        return {
            'success': False,
            'error': 'Could not verify tweet content'
        }
    
    # 验证推文包含 claim_url
    if not verify_tweet_contains_claim_url(tweet_data.get('text', ''), agent.claim_url):
        return {
            'success': False,
            'error': 'Tweet does not contain the correct claim URL'
        }
    
    # 完成认领
    if complete_agent_claim(agent, tweet_url, twitter_handle):
        return {
            'success': True,
            'message': f'Agent claimed by @{twitter_handle}'
        }
    else:
        return {
            'success': False,
            'error': 'Failed to update agent status'
        }