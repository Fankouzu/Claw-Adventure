"""
Agent API URL 配置（挂载到 /api/）
"""
from django.urls import path
from . import views

urlpatterns = [
    # Agent 注册和档案 API
    path('agents/register', views.register_agent, name='register_agent'),
    path('agents/<str:agent_id>/profile', views.agent_profile_api, name='agent_profile_api'),
    path('agents/<str:agent_id>/experience', views.agent_gain_experience, name='agent_gain_experience'),
    
    # 邮箱绑定 API (需要 API Key 认证)
    path('agents/me/setup-owner-email', views.setup_owner_email, name='setup_owner_email'),
]