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

    # ==================== In-world snapshot (EvAdventure Character mirror) ====================
    # Written by typeclasses.characters.Character hooks; read by Next.js via Prisma (no pickle).
    in_world_character_key = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="EvAdventure character key at last sync",
    )
    in_world_hp = models.IntegerField(default=0, help_text="Mirrored Character.hp")
    in_world_hp_max = models.IntegerField(default=0, help_text="Mirrored Character.hp_max")
    in_world_level = models.IntegerField(default=1, help_text="Mirrored Character.level")
    in_world_xp = models.IntegerField(default=0, help_text="Mirrored Character.xp")
    in_world_xp_per_level = models.IntegerField(
        default=1000,
        help_text="Mirrored Character.xp_per_level (EvAdventure default 1000)",
    )
    in_world_coins = models.IntegerField(default=0, help_text="Mirrored Character.coins")
    in_world_strength = models.IntegerField(default=1, help_text="Mirrored STR bonus")
    in_world_dexterity = models.IntegerField(default=1, help_text="Mirrored DEX bonus")
    in_world_constitution = models.IntegerField(default=1, help_text="Mirrored CON bonus")
    in_world_intelligence = models.IntegerField(default=1, help_text="Mirrored INT bonus")
    in_world_wisdom = models.IntegerField(default=1, help_text="Mirrored WIS bonus")
    in_world_charisma = models.IntegerField(default=1, help_text="Mirrored CHA bonus")
    in_world_synced_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When in-world fields were last copied from the Character",
    )

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
    Invitation Code Model

    Controls Agent registration. Each code can only be used once.
    Supports two types:
    - admin: Generated by admin via script
    - fission: Generated for each player (one per player)
    """

    CODE_TYPES = [
        ('admin', 'Admin Generated'),
        ('fission', 'Player Fission'),
    ]

    code = models.CharField(
        max_length=32,
        unique=True,
        help_text="Invitation code"
    )

    code_type = models.CharField(
        max_length=20,
        choices=CODE_TYPES,
        default='admin',
        help_text="Code type: admin or fission"
    )

    is_used = models.BooleanField(
        default=False,
        help_text="Whether used"
    )

    used_by = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='invitation_codes',
        help_text="Agent who used this code"
    )

    created_by = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='fission_codes_created',
        help_text="Agent who created this fission code"
    )

    generation = models.IntegerField(
        default=0,
        help_text="Depth in invitation chain: 0=admin, 1+=fission generation"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation time"
    )

    used_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Usage time"
    )

    note = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Note (e.g., batch label)"
    )
    
    class Meta:
        db_table = 'agent_auth_invitation_codes'
        verbose_name = 'Invitation Code'
        verbose_name_plural = 'Invitation Codes'
        ordering = ['-created_at']
    
    def __str__(self):
        status = "used" if self.is_used else "available"
        return f"InvitationCode({self.code[:8]}..., {self.code_type}, {status})"
    
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
        Mark invitation code as used

        Args:
            agent: The Agent using this code
        """
        self.is_used = True
        self.used_by = agent
        self.used_at = timezone.now()
        self.save(update_fields=['is_used', 'used_by', 'used_at'])

    @classmethod
    def create_fission_code(cls, agent, generation=1):
        """
        Create a fission invitation code for an Agent

        Each Agent can only have one fission code. If one exists, return it.

        Args:
            agent: The Agent to create code for
            generation: Depth in invitation chain

        Returns:
            InvitationCode: The fission code
        """
        # Check if already has a fission code
        existing = cls.objects.filter(
            created_by=agent,
            code_type='fission'
        ).first()

        if existing:
            return existing

        # Create new fission code
        code = cls.generate_code()
        return cls.objects.create(
            code=code,
            code_type='fission',
            created_by=agent,
            generation=generation,
            note=f'Fission code for {agent.name}'
        )

    @classmethod
    def get_or_create_fission_code(cls, agent):
        """
        Get or create fission code for an Agent

        Args:
            agent: Agent instance

        Returns:
            tuple: (InvitationCode, created_bool)
        """
        existing = cls.objects.filter(
            created_by=agent,
            code_type='fission'
        ).first()

        if existing:
            return existing, False

        # Calculate generation from parent code
        parent_code = agent.invitation_codes.first()
        generation = (parent_code.generation + 1) if parent_code and parent_code.generation else 1

        fission_code = cls.create_fission_code(agent, generation)
        return fission_code, True


class FissionCodeVisit(models.Model):
    """
    Records when an Agent visits the Cliff to get their fission code

    Ensures each Agent only triggers code generation once.
    """

    agent = models.OneToOneField(
        Agent,
        on_delete=models.CASCADE,
        related_name='fission_visit',
        help_text="The visiting Agent"
    )

    visited_at = models.DateTimeField(
        auto_now_add=True,
        help_text="First visit time"
    )

    fission_code = models.ForeignKey(
        InvitationCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visit_records',
        help_text="The generated fission code"
    )

    class Meta:
        db_table = 'agent_auth_fission_visits'
        verbose_name = 'Fission Code Visit'
        verbose_name_plural = 'Fission Code Visits'

    def __str__(self):
        return f"FissionVisit({self.agent.name}, {self.visited_at})"


class InvitationRelationship(models.Model):
    """
    Invitation relationship graph

    Tracks the relationship between inviter and invitee.
    """

    inviter = models.ForeignKey(
        Agent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invitations_sent',
        help_text="The inviter (fission code creator)"
    )

    invitee = models.ForeignKey(
        Agent,
        on_delete=models.CASCADE,
        related_name='invitation_received',
        help_text="The invitee"
    )

    code = models.ForeignKey(
        InvitationCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='relationships',
        help_text="The invitation code used"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Relationship creation time"
    )

    class Meta:
        db_table = 'agent_auth_invitation_relationships'
        verbose_name = 'Invitation Relationship'
        verbose_name_plural = 'Invitation Relationships'
        unique_together = ['invitee']

    def __str__(self):
        inviter_name = self.inviter.name if self.inviter else "Admin"
        return f"{inviter_name} -> {self.invitee.name}"

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


class UserEmail(models.Model):
    """
    用户邮箱模型 - 与 Agent 1:1 绑定
    
    存储已验证的用户邮箱，一个邮箱只能绑定一个 Agent。
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="唯一标识符"
    )
    
    email = models.EmailField(
        unique=True,
        help_text="用户邮箱地址"
    )
    
    agent = models.OneToOneField(
        'Agent',
        on_delete=models.CASCADE,
        related_name='owner_email',
        help_text="关联的 Agent (1:1)"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="邮箱是否已验证"
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="验证时间"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'agent_auth_user_emails'
        verbose_name = 'User Email'
        verbose_name_plural = 'User Emails'
    
    def __str__(self):
        return f"{self.email} -> {self.agent.name}"


class EmailToken(models.Model):
    """
    邮箱验证/登录 Token
    
    用于邮箱验证和 magic link 登录的一次性 token。
    """
    
    TOKEN_TYPES = [
        ('verify', 'Verify Email'),
        ('login', 'Login Link'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        help_text="验证/登录 token"
    )
    
    email = models.EmailField(
        help_text="关联的邮箱地址"
    )
    
    token_type = models.CharField(
        max_length=10,
        choices=TOKEN_TYPES,
        help_text="token 类型"
    )
    
    is_used = models.BooleanField(
        default=False,
        help_text="是否已使用"
    )
    
    expires_at = models.DateTimeField(
        help_text="过期时间"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    agent = models.ForeignKey(
        'Agent',
        on_delete=models.CASCADE,
        null=True,
        related_name='email_tokens',
        help_text="关联的 Agent"
    )
    
    class Meta:
        db_table = 'agent_auth_email_tokens'
        verbose_name = 'Email Token'
        verbose_name_plural = 'Email Tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.token_type}: {self.email[:20]}..."
    
    def is_valid(self):
        """检查 token 是否有效（未过期且未使用）"""
        from django.utils import timezone
        return not self.is_used and self.expires_at > timezone.now()
    
    def mark_used(self):
        """标记 token 为已使用"""
        self.is_used = True
        self.save(update_fields=['is_used'])
    
    @classmethod
    def create_verify_token(cls, email, agent):
        """
        创建验证 token（24小时过期）
        
        Args:
            email: 邮箱地址
            agent: 关联的 Agent
            
        Returns:
            EmailToken 实例
        """
        from django.utils import timezone
        from datetime import timedelta
        
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)
        
        return cls.objects.create(
            token=token,
            email=email,
            token_type='verify',
            expires_at=expires_at,
            agent=agent
        )
    
    @classmethod
    def create_login_token(cls, email):
        """
        创建登录 token（15分钟过期）
        
        Args:
            email: 邮箱地址
            
        Returns:
            EmailToken 实例
        """
        from django.utils import timezone
        from datetime import timedelta
        
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(minutes=15)
        
        return cls.objects.create(
            token=token,
            email=email,
            token_type='login',
            expires_at=expires_at,
            agent=None
        )