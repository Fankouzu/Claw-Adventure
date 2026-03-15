"""
Agent Claim 页面视图
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from .models import Agent, InvitationCode
from .auth import verify_claim_token
from .twitter_verify import verify_and_claim_agent

# Agent Profile API endpoints
@csrf_exempt
@require_http_methods(["GET"])
def agent_profile(request, agent_id):
    """
    GET /api/agents/{agent_id}/profile
    获取 Agent 档案信息
    """
    try:
        from uuid import UUID
        agent = Agent.objects.get(id=UUID(agent_id))
        
        return JsonResponse({
            'agent_id': str(agent.id),
            'name': agent.name,
            'level': agent.level,
            'experience': agent.experience,
            'claim_status': agent.claim_status,
            'twitter_handle': agent.twitter_handle,
            'created_at': agent.created_at.isoformat(),
            'last_active_at': agent.last_active_at.isoformat() if agent.last_active_at else None,
        })
    except (Agent.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Agent not found'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def agent_gain_experience(request, agent_id):
    """
    POST /api/agents/{agent_id}/experience
    增加 Agent 经验值（游戏内部调用）
    """
    try:
        from uuid import UUID
        import json
        
        agent = Agent.objects.get(id=UUID(agent_id))
        
        data = json.loads(request.body)
        exp_gain = data.get('experience', 0)
        
        if exp_gain <= 0:
            return JsonResponse({'error': 'experience must be positive'}, status=400)
        
        agent.experience += exp_gain
        
        # 简单的升级逻辑（每 100 经验升一级）
        new_level = agent.experience // 100 + 1
        if new_level > agent.level:
            agent.level = new_level
        
        agent.save()
        
        return JsonResponse({
            'agent_id': str(agent.id),
            'level': agent.level,
            'experience': agent.experience,
            'level_up': new_level > agent.level - (agent.experience - exp_gain) // 100
        })
        
    except (Agent.DoesNotExist, ValueError):
        return JsonResponse({'error': 'Agent not found'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def register_agent(request):
    """
    POST /api/agents/register
    注册新 Agent，返回 API Key 和 Claim URL
    
    需要 invitation_code 参数（邀请码）
    """
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        description = data.get('description', '')
        invitation_code = data.get('invitation_code', '').strip().upper()
        
        if not name:
            return JsonResponse({'error': 'name is required'}, status=400)
        
        if not invitation_code:
            return JsonResponse({'error': 'invitation_code is required'}, status=400)
        
        # 验证邀请码
        try:
            inv_code = InvitationCode.objects.get(code=invitation_code)
        except InvitationCode.DoesNotExist:
            return JsonResponse({'error': 'Invalid invitation code'}, status=400)
        
        if inv_code.is_used:
            return JsonResponse({'error': 'Invitation code already used'}, status=400)
        
        # 检查名称是否已存在
        if Agent.objects.filter(name=name).exists():
            return JsonResponse({'error': 'Agent name already exists'}, status=409)
        
        # 创建 Agent
        agent, api_key = Agent.create_agent(name=name, description=description)
        
        # 标记邀请码为已使用
        inv_code.mark_used(agent)
        
        return JsonResponse({
            'agent_id': str(agent.id),
            'name': agent.name,
            'api_key': api_key,
            'claim_url': agent.claim_url,
            'claim_expires_at': agent.claim_expires_at.isoformat()
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def claim_page(request, token):
    """
    Claim 页面 - GET 请求显示表单
    /claim/{token}
    """
    # 验证 token
    agent = verify_claim_token(token)
    
    if not agent:
        return render(request, 'agent_auth/claim_error.html', {
            'error': 'Invalid or expired claim link'
        })
    
    # 检查是否已认领
    if agent.is_claimed:
        return render(request, 'agent_auth/claim_success.html', {
            'agent': agent,
            'already_claimed': True
        })
    
    # 检查是否过期
    if agent.claim_expires_at and agent.claim_expires_at < timezone.now():
        return render(request, 'agent_auth/claim_error.html', {
            'error': 'Claim link has expired'
        })
    
    return render(request, 'agent_auth/claim.html', {
        'agent': agent,
        'claim_url': agent.claim_url,
    })


@csrf_exempt
@require_http_methods(["POST"])
def verify_tweet(request, token):
    """
    验证推文 URL - POST 请求
    /claim/{token}/verify
    """
    agent = verify_claim_token(token)
    
    if not agent:
        return JsonResponse({'error': 'Invalid claim token'}, status=400)
    
    if agent.is_claimed:
        return JsonResponse({'error': 'Agent already claimed'}, status=400)
    
    try:
        data = json.loads(request.body)
        tweet_url = data.get('tweet_url', '').strip()
        
        if not tweet_url:
            return JsonResponse({'error': 'Tweet URL is required'}, status=400)
        
        # 验证推文 URL 格式（基本检查）
        if not ('twitter.com' in tweet_url or 'x.com' in tweet_url):
            return JsonResponse({'error': 'Invalid tweet URL format'}, status=400)
        
        # 执行完整的验证和认领流程
        result = verify_and_claim_agent(agent, tweet_url)
        
        if result['success']:
            return JsonResponse({
                'status': 'claimed',
                'message': result['message'],
                'twitter_handle': agent.twitter_handle
            })
        else:
            return JsonResponse({'error': result.get('error', 'Verification failed')}, status=400)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)