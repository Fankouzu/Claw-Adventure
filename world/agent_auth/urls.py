"""
Agent API URL 配置
"""
from django.urls import path
from . import views

urlpatterns = [
    # Agent 注册和档案
    path('agents/register', views.register_agent, name='register_agent'),
    path('agents/<str:agent_id>/profile', views.agent_profile, name='agent_profile'),
    path('agents/<str:agent_id>/experience', views.agent_gain_experience, name='agent_gain_experience'),
    
    # 测试端点（生产环境移除）
    path('test/agents/<str:agent_id>/claim', views.test_claim_agent, name='test_claim_agent'),
]
    # Agent 注册和档案
    path('agents/register', views.register_agent, name='register_agent'),
    path('agents/<str:agent_id>/profile', views.agent_profile, name='agent_profile'),
    path('agents/<str:agent_id>/experience', views.agent_gain_experience, name='agent_gain_experience'),
]