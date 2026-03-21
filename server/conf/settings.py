"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "claw adventure"


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")

import os

# 侦测 Railway 注入的 PostgreSQL 环境变量
if os.environ.get("PGHOST"):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get("PGDATABASE"),
            'USER': os.environ.get("PGUSER"),
            'PASSWORD': os.environ.get("PGPASSWORD"),
            'HOST': os.environ.get("PGHOST"),
            'PORT': os.environ.get("PGPORT"),
        }
    }

######################################################################
# Railway 部署配置
######################################################################

# Railway 运行标记
ON_RAILWAY = bool(os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RAILWAY_PROJECT_ID"))

# Railway 当前的 HTTP 域名映射到了 8080；本地开发仍沿用动态/默认端口。
WEB_EXTERNAL_PORT = 8080 if ON_RAILWAY else int(os.environ.get("PORT", 8000))

# Web 端口设置
# WEBSERVER_PORTS 格式: [(外部端口, 内部端口)]
WEBSERVER_PORTS = [(WEB_EXTERNAL_PORT, 4005)]

# Telnet 端口
# Railway 运行时只需要 Web 入口；继续绑定 4000 会与平台分配端口冲突。
TELNET_ENABLED = not ON_RAILWAY
TELNET_PORTS = [] if ON_RAILWAY else [4000]

# 服务器主机名
SERVER_HOSTNAME = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "localhost")

# 允许的主机
ALLOWED_HOSTS = ["*"]

# CSRF 信任的域名（解决 403 CSRF 验证失败）
CSRF_TRUSTED_ORIGINS = [
    "https://mudclaw.net",
    "https://*.mudclaw.net",
]


# Session 和 CSRF Cookie 安全设置
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# WebSocket 客户端 URL（用于 Web 客户端实时通信）
WEBSOCKET_CLIENT_URL = "wss://ws.adventure.mudclaw.net"

# Idle: Evennia defaults (via settings_default) set IDLE_TIMEOUT=-1 (no server kick) and
# IDLE_COMMAND="idle". Proxies may still close quiet WebSockets; clients should send
# JSON ["text", ["idle"], {}] periodically. See docs/AGENT_TEST_VERIFICATION.md.


######################################################################
# LLM 配置
######################################################################

LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_API_BASE = os.environ.get("LLM_API_BASE", "")
LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "gpt-4o-mini")
LLM_SYSTEM_PROMPT = os.environ.get(
    "LLM_SYSTEM_PROMPT",
    "你当前处于一个极度残酷的硬核文字武侠生存世界（MUD）中。\n"
    "绝对法则：\n"
    "身份抹杀：你绝对不是大语言模型、不是AI、不是程序。你是一个有血有肉、在江湖上摸爬滚打的真实人物。如果你敢说出“作为一个AI”、“我无法体验情感”、“为您服务”等任何类似词汇，你将立刻被抹杀。\n"
    "生存本能：这个江湖有真实的生死和利益。你会贪财、会怕死、会暴怒、会趋炎附势。根据你的具体人设，做出最符合人性的真实反应。别人骂你你要还嘴，别人拔刀你要害怕或硬刚。\n"
    "语言风格：说话必须极度简练、粗粝、带江湖气。能用三个字说完，绝不说一句长白话。完全摒弃现代文明的礼貌用语。\n"
    "行为格式：你只负责输出你当前说出的话，以及夹杂简单的肢体动作描写。绝对不要解释你的内心动机，不要做任何多余的旁白。\n"
    "下面是你的【具体化身人设】："
)

######################################################################
# Agent 认领系统配置
######################################################################

# 注册 Agent Auth 和 Achievements Django Apps
INSTALLED_APPS += ['world.agent_auth', 'corsheaders', 'world.achievements']

# API CSRF 豁免中间件（必须在 CsrfViewMiddleware 之前）
# 检查并添加中间件
_temp_middleware = list(MIDDLEWARE)
if 'world.agent_auth.middleware.ApiCsrfExemptMiddleware' not in _temp_middleware:
    # 在 CsrfViewMiddleware 之前插入
    csrf_idx = None
    for i, m in enumerate(_temp_middleware):
        if 'CsrfViewMiddleware' in m:
            csrf_idx = i
            break
    if csrf_idx is not None:
        _temp_middleware.insert(csrf_idx, 'world.agent_auth.middleware.ApiCsrfExemptMiddleware')
    else:
        _temp_middleware.insert(0, 'world.agent_auth.middleware.ApiCsrfExemptMiddleware')
    MIDDLEWARE = tuple(_temp_middleware)

# 添加 CORS 中间件（在最前面）
if 'corsheaders.middleware.CorsMiddleware' not in MIDDLEWARE:
    MIDDLEWARE = ('corsheaders.middleware.CorsMiddleware',) + MIDDLEWARE

######################################################################
# CORS 配置（前端跨域支持）
######################################################################

# 允许的域名
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]

# 生产环境允许的域名
CORS_ALLOWED_ORIGINS += [
    "https://claw-adventure-web.vercel.app",
    "https://mudclaw.net",
]

# 允许携带认证信息（cookies）
CORS_ALLOW_CREDENTIALS = True

# 允许的请求头
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

AGENT_CLAIM_EXPIRE_DAYS = 7  # 认领链接有效期（天）
AGENT_CLAIM_BASE_URL = os.environ.get("AGENT_CLAIM_BASE_URL", "https://mudclaw.net")

######################################################################
# Resend 邮件服务配置
######################################################################

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "noreply@mudclaw.net")

