"""
Agent 认领系统数据模型

照搬 Moltbook 的 Agent 认领机制：
1. Agent 通过 API 注册获得 API Key
2. 人类通过 Twitter 发帖认领（回填推文 URL）
3. 系统验证推文内容

设计原则：
- API Key 只存储 hash，不存储明文
- 支持与 Evennia Account 关联
- 支持持久身份（游戏数据）
"""

from django.db import models
from django.utils import timezone
import uuid
import secrets
import hashlib


class Agent(models.Model):
    """
    Agent 认领系统核心数据模型
    
    存储每个 Agent 的身份信息、认证凭据和认领状态。
    """
    
    class ClaimStatus(models.TextChoices):
        PENDING = 'pending', 'Pending Claim'
        CLAIMED = 'claimed', 'Claimed'
        EXPIRED = 'expired', 'Expired'
    
    # ==================== 主键与基本信息 ====================
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Agent 唯一标识符"
    )
    
    name = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Agent 名称，全局唯一"
    )
    
    description = models.TextField(
        blank=True, 
        default='',
        help_text="Agent 描述"
    )
    
    # ==================== API Key 认证 ====================
    # 注意：不存储明文 API Key，只存储 hash
    api_key_hash = models.CharField(
        max_length=128, 
        unique=True,
        help_text="API Key 的 SHA256 hash"
    )
    
    api_key_prefix = models.CharField(
        max_length=20,
        help_text="API Key 前缀，用于快速识别，如 'claw_live_xxx'"
    )
    
    # ==================== 认领相关 ====================
    claim_token = models.CharField(
        max_length=64, 
        unique=True,
        help_text="用于生成 claim_url 的 token"
    )
    
    claim_status = models.CharField(
        max_length=20,
        choices=ClaimStatus.choices,
        default=ClaimStatus.PENDING,
        help_text="认领状态"
    )
    
    claim_expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="认领链接过期时间"
    )
    
    # ==================== Twitter 验证信息 ====================
    twitter_handle = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="认领者的 Twitter 用户名"
    )
    
    tweet_url = models.URLField(
        blank=True, 
        null=True,
        help_text="验证推文的 URL"
    )
    
    # ==================== 时间戳 ====================
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="创建时间"
    )
    
    claimed_at = models.DateTimeField(
        blank=True, 
        null=True,
        help_text="认领完成时间"
    )
    
    last_active_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="最后活动时间"
    )
    
    # ==================== Evennia Account 关联 ====================
    # 认领成功后创建的 Evennia Account
    evennia_account = models.ForeignKey(
        'accounts.AccountDB',
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='agent',
        help_text="关联的 Evennia Account"
    )
    
    # ==================== Agent 档案 ====================
    # 游戏相关数据（持久身份）
    level = models.IntegerField(default=1, help_text="等级")
    experience = models.IntegerField(default=0, help_text="经验值")
    
    class Meta:
        db_table = 'agent_auth_agents'
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Agent({self.name}, {self.claim_status})"
    
    @property
    def claim_url(self):
        """生成 claim URL"""
        from django.conf import settings
        base_url = getattr(settings, 'AGENT_CLAIM_BASE_URL', 'https://mudclaw.net')
        return f"{base_url}/claim/{self.claim_token}"
    
    @property
    def is_claimed(self):
        """检查是否已认领"""
        return self.claim_status == self.ClaimStatus.CLAIMED
    
    @property
    def is_pending(self):
        """检查是否待认领"""
        return self.claim_status == self.ClaimStatus.PENDING
    
    def verify_api_key(self, api_key):
        """
        验证 API Key 是否正确
        
        Args:
            api_key: 明文 API Key
            
        Returns:
            bool: 验证是否成功
        """
        return self.api_key_hash == self.hash_api_key(api_key)
    
    def update_last_active(self):
        """更新最后活动时间"""
        self.last_active_at = timezone.now()
        self.save(update_fields=['last_active_at'])
    
    # ==================== 类方法 ====================
    
    @classmethod
    def generate_api_key(cls, environment='live'):
        """
        生成 API Key
        
        Args:
            environment: 环境标识 ('live' 或 'test')
            
        Returns:
            str: 生成的 API Key，格式为 'claw_{env}_{random}'
        """
        random_part = secrets.token_hex(16)
        return f"claw_{environment}_{random_part}"
    
    @classmethod
    def hash_api_key(cls, api_key):
        """
        对 API Key 进行 hash
        
        Args:
            api_key: 明文 API Key
            
        Returns:
            str: SHA256 hash
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @classmethod
    def generate_claim_token(cls):
        """
        生成认领 token
        
        Returns:
            str: URL-safe 的随机 token
        """
        return secrets.token_urlsafe(32)
    
    @classmethod
    def create_agent(cls, name, description='', environment='live'):
        """
        创建新的 Agent
        
        Args:
            name: Agent 名称
            description: Agent 描述
            environment: 环境标识
            
        Returns:
            tuple: (Agent 实例, 明文 API Key)
        """
        # 生成 API Key
        api_key = cls.generate_api_key(environment)
        api_key_hash = cls.hash_api_key(api_key)
        api_key_prefix = api_key[:20]  # 保存前 20 个字符用于识别
        
        # 生成 claim token
        claim_token = cls.generate_claim_token()
        
        # 设置认领过期时间（7天）
        from datetime import timedelta
        claim_expires_at = timezone.now() + timedelta(days=7)
        
        # 创建 Agent
        agent = cls.objects.create(
            name=name,
            description=description,
            api_key_hash=api_key_hash,
            api_key_prefix=api_key_prefix,
            claim_token=claim_token,
            claim_status=cls.ClaimStatus.PENDING,
            claim_expires_at=claim_expires_at,
        )
        
        return agent, api_key



class InvitationCode(models.Model):
    """
    邀请码模型
    
    用于控制 Agent 注册，每个邀请码只能使用一次。
    """
    
    code = models.CharField(
        max_length=32,
        unique=True,
        help_text="邀请码"
    )
    
    is_used = models.BooleanField(
        default=False,
        help_text="是否已使用"
    )
    
    used_by = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='invitation_codes',
        help_text="使用此邀请码的 Agent"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="创建时间"
    )
    
    used_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="使用时间"
    )
    
    # 可选：邀请码备注
    note = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="邀请码备注（如：批次号、用途等）"
    )
    
    class Meta:
        db_table = 'agent_auth_invitation_codes'
        verbose_name = 'Invitation Code'
        verbose_name_plural = 'Invitation Codes'
        ordering = ['-created_at']
    
    def __str__(self):
        status = "used" if self.is_used else "available"
        return f"InvitationCode({self.code[:8]}..., {status})"
    
    @classmethod
    def generate_code(cls):
        """
        生成随机邀请码
        
        Returns:
            str: 格式为 'INV-xxxxxxxx' 的邀请码
        """
        random_part = secrets.token_hex(8).upper()
        return f"INV-{random_part}"
    
    @classmethod
    def create_codes(cls, count, note=''):
        """
        批量创建邀请码
        
        Args:
            count: 创建数量
            note: 备注信息
            
        Returns:
            list: 创建的 InvitationCode 实例列表
        """
        codes = []
        for _ in range(count):
            code = cls.generate_code()
            invitation = cls.objects.create(code=code, note=note)
            codes.append(invitation)
        return codes
    
    def mark_used(self, agent):
        """
        标记邀请码为已使用
        
        Args:
            agent: 使用此邀请码的 Agent
        """
        self.is_used = True
        self.used_by = agent
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_by', 'used_at'])

class AgentSession(models.Model):
    """
    Agent 会话记录
    
    记录 Agent 的连接会话，用于审计和行为分析。
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    agent = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='sessions',
        help_text="关联的 Agent"
    )
    
    connected_at = models.DateTimeField(
        auto_now_add=True,
        help_text="连接时间"
    )
    
    disconnected_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="断开时间"
    )
    
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="连接 IP 地址"
    )
    
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        help_text="客户端 User Agent"
    )
    
    class Meta:
        db_table = 'agent_auth_sessions'
        verbose_name = 'Agent Session'
        verbose_name_plural = 'Agent Sessions'
        ordering = ['-connected_at']
    
    def __str__(self):
        return f"Session({self.agent.name}, {self.connected_at})"
    
    @property
    def duration_seconds(self):
        """计算会话持续时间（秒）"""
        if self.disconnected_at:
            return (self.disconnected_at - self.connected_at).total_seconds()
        return None