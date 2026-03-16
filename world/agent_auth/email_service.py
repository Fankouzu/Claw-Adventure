"""
邮件发送服务 - 使用 Resend API
"""
import resend
from django.conf import settings
from typing import Tuple, Optional


def send_verification_email(email: str, verify_url: str, agent_name: str) -> Tuple[bool, Optional[str]]:
    """
    发送邮箱验证邮件
    
    Args:
        email: 收件人邮箱
        verify_url: 验证链接 URL
        agent_name: Agent 名称
        
    Returns:
        (success, error_message) - 成功时 error_message 为 None
    """
    if not settings.RESEND_API_KEY:
        return (False, "RESEND_API_KEY not configured")
    
    resend.api_key = settings.RESEND_API_KEY
    
    try:
        resend.Emails.send({
            "from": settings.RESEND_FROM_EMAIL,
            "to": email,
            "subject": f"验证您的邮箱 - {agent_name} 正在为您设置账户",
            "html": f"""
<p>您好！</p>
<p>Agent <strong>{agent_name}</strong> 正在为您设置 Claw Adventure 账户。</p>
<p>请点击下方链接验证您的邮箱地址：</p>
<p><a href="{verify_url}" style="background-color: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">验证邮箱</a></p>
<p>此链接将在 24 小时后过期。</p>
<p>如果您没有请求此验证，请忽略此邮件。</p>
"""
        })
        return (True, None)
    except Exception as e:
        return (False, str(e))


def send_login_email(email: str, login_url: str) -> Tuple[bool, Optional[str]]:
    """
    发送登录链接邮件
    
    Args:
        email: 收件人邮箱
        login_url: 登录链接 URL
        
    Returns:
        (success, error_message) - 成功时 error_message 为 None
    """
    if not settings.RESEND_API_KEY:
        return (False, "RESEND_API_KEY not configured")
    
    resend.api_key = settings.RESEND_API_KEY
    
    try:
        resend.Emails.send({
            "from": settings.RESEND_FROM_EMAIL,
            "to": email,
            "subject": "登录 Claw Adventure",
            "html": f"""
<p>您好！</p>
<p>请点击下方链接登录您的账户：</p>
<p><a href="{login_url}" style="background-color: #3b82f6; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">登录</a></p>
<p>此链接将在 15 分钟后过期。</p>
<p>如果您没有请求此登录链接，请忽略此邮件。</p>
"""
        })
        return (True, None)
    except Exception as e:
        return (False, str(e))


def send_confirmation_email(email: str, agent_name: str) -> Tuple[bool, Optional[str]]:
    """
    发送邮箱验证成功确认邮件
    
    Args:
        email: 收件人邮箱
        agent_name: Agent 名称
        
    Returns:
        (success, error_message) - 成功时 error_message 为 None
    """
    if not settings.RESEND_API_KEY:
        return (False, "RESEND_API_KEY not configured")
    
    resend.api_key = settings.RESEND_API_KEY
    
    try:
        resend.Emails.send({
            "from": settings.RESEND_FROM_EMAIL,
            "to": email,
            "subject": "邮箱验证成功",
            "html": f"""
<p>您好！</p>
<p>您的邮箱已成功绑定到 Agent <strong>{agent_name}</strong>。</p>
<p>您现在可以登录了！</p>
"""
        })
        return (True, None)
    except Exception as e:
        return (False, str(e))