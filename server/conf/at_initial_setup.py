"""
At_initial_setup module template

Custom at_initial_setup method. This allows you to hook special
modifications to the initial server startup process. Note that this
will only be run once - when the server starts up for the very first
time! It is called last in the startup process and can thus be used to
overload things that happened before it.

The module must contain a global function at_initial_setup().  This
will be called without arguments. Note that tracebacks in this module
will be QUIETLY ignored, so make sure to check it well to make sure it
does what you expect it to.

"""

def at_initial_setup():
    """
    服务器首次启动时自动创建超级管理员
    从环境变量读取配置，支持Railway部署
    """
    import os
    from evennia.accounts.accounts import DefaultAccount
    
    # 从环境变量获取管理员信息，设置默认值
    username = os.environ.get("EVENNIA_SUPERUSER_NAME", "admin")
    password = os.environ.get("EVENNIA_SUPERUSER_PASSWORD", "admin123")
    email = os.environ.get("EVENNIA_SUPERUSER_EMAIL", "admin@localhost")
    
    # 检查账号是否已存在
    from evennia.accounts.models import AccountDB
    
    if not AccountDB.objects.filter(username=username).exists():
        # 使用AccountDB.create创建账号并设置权限
        account = AccountDB.objects.create_account(
            username=username,
            email=email,
            password=password,
            typeclass=DefaultAccount
        )
        # 设置为超级管理员权限
        account.permissions.add("Developer")
        account.permissions.add("Admin")
        print(f"[at_initial_setup] 超级管理员 '{username}' 创建成功!")
    else:
        print(f"[at_initial_setup] 管理员 '{username}' 已存在，跳过创建")
