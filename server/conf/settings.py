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
SERVERNAME = "claw-jianghu"


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

# Railway 端口配置
PORT = int(os.environ.get("PORT", 8000))

# Web 端口设置（Railway 使用动态端口）
# WEBSERVER_PORTS 格式: [(外部端口, 内部端口)]
WEBSERVER_PORTS = [(PORT, 4005)]
PORT = os.environ.get("PORT", 8000)

# Web 端口设置（Railway 使用动态端口）
WEBSERVER_ENABLED = True
WEBCLIENT_PORT = int(PORT)  # Web 界面端口

# Telnet 端口（可选，Railway 可能不支持）
TELNET_ENABLED = True
TELNET_PORTS = [4000]

# 服务器主机名
SERVER_HOSTNAME = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "localhost")

# 允许的主机
ALLOWED_HOSTS = ["*"]