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
    
    # 管理员 API（需要 X-Admin-Token）
    path('admin/invitations/generate', views.admin_generate_invitations, name='admin_generate_invitations'),
    path('admin/invitations', views.admin_list_invitations, name='admin_list_invitations'),
]