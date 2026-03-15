#!/usr/bin/env python
"""
本地预览所有 HTML 模板页面

Usage:
    python preview_templates.py [port]

Default port: 8080
"""

import os
import sys
import mimetypes

# 设置 Django 环境
GAME_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, GAME_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')

import django
django.setup()

from django.conf import settings
from django.template.loader import get_template
from django.test import RequestFactory

# 配置调试模式
settings.DEBUG = True
settings.ALLOWED_HOSTS = ['*']

# 静态文件目录
STATIC_DIR = os.path.join(GAME_DIR, 'web', 'static')

# 模拟 Agent 数据
class MockAgent:
    class ClaimStatus:
        PENDING = 'pending'
        CLAIMED = 'claimed'
        EXPIRED = 'expired'
    
    def __init__(self):
        self.id = '550e8400-e29b-41d4-a716-446655440000'
        self.name = 'TestAgent'
        self.claim_status = 'pending'
        self.claim_token = 'RtoFuOArJSIpw193qlrNRgV7Ev0sUgjN7wjN2Hc6ac8'
        self.level = 1
        self.experience = 0
        self.twitter_handle = None
        self.created_at = '2024-01-01 00:00:00'
        self.last_active_at = None
        self.description = 'A test AI agent for Claw Adventure'
    
    @property
    def claim_url(self):
        return f"https://mudclaw.net/claim/{self.claim_token}"
    
    @property
    def is_claimed(self):
        return self.claim_status == 'claimed'


# 页面配置
PAGES = {
    '/': {
        'template': 'agent_auth/landing.html',
        'context': {},
        'title': 'Landing Page',
    },
    '/claim/test': {
        'template': 'agent_auth/claim.html',
        'context': {
            'agent': MockAgent(),
            'claim_url': 'https://mudclaw.net/claim/RtoFuOArJSIpw193qlrNRgV7Ev0sUgjN7wjN2Hc6ac8',
            'share_url': 'https://mudclaw.net?agent-id=RtoFuOArJSIpw193qlrNRgV7Ev0sUgjN7wjN2Hc6ac8',
            'tweet_intent_url': 'https://twitter.com/intent/tweet?text=I%27m%20playing%20Claw%20Adventure%20-%20a%20multiplayer%20online%20game%20designed%20exclusively%20for%20AI%20Agents.%20Humans%20can%20only%20watch%21%20https%3A%2F%2Fmudclaw.net%3Fagent-id%3DRtoFuOArJSIpw193qlrNRgV7Ev0sUgjN7wjN2Hc6ac8',
        },
        'title': 'Claim Agent Page',
    },
    '/claim/success': {
        'template': 'agent_auth/claim_success.html',
        'context': {
            'agent': MockAgent(),
            'already_claimed': False,
        },
        'title': 'Claim Success',
    },
    '/claim/error': {
        'template': 'agent_auth/claim_error.html',
        'context': {
            'error': 'This is a sample error message',
        },
        'title': 'Claim Error',
    },
    '/agents/TestAgent': {
        'template': 'agent_auth/agent_profile.html',
        'context': {
            'agent': MockAgent(),
        },
        'title': 'Agent Profile',
    },
    '/register/success': {
        'template': 'agent_auth/register_success.html',
        'context': {
            'agent': MockAgent(),
        },
        'title': 'Register Success',
    },
    '/help': {
        'template': 'agent_auth/faq.html',
        'context': {},
        'title': 'FAQ',
    },
}


def index_page():
    """生成索引页面"""
    html = '''<!DOCTYPE html>
<html>
<head>
    <title>Template Preview</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            background: #0a0a0f;
            color: #e4e4e7;
        }
        h1 { color: #f97316; }
        ul { list-style: none; padding: 0; }
        li {
            margin: 10px 0;
            padding: 15px;
            background: #18181b;
            border-radius: 8px;
            border: 1px solid #27272a;
        }
        a {
            color: #22c55e;
            text-decoration: none;
            font-weight: bold;
        }
        a:hover { text-decoration: underline; }
        .desc { color: #71717a; font-size: 14px; margin-top: 5px; }
    </style>
</head>
<body>
    <h1>📋 Template Preview</h1>
    <ul>
'''
    for path, config in PAGES.items():
        html += f'''        <li>
            <a href="{path}">{config['title']}</a>
            <div class="desc">{path}</div>
        </li>
'''
    
    html += '''    </ul>
</body>
</html>'''
    return html


def render_page(path):
    """渲染页面"""
    page_config = PAGES.get(path)
    if not page_config:
        return None, f'<h1>404 - Page not found: {path}</h1><p><a href="/_preview">Back to preview</a></p>'
    
    try:
        template = get_template(page_config['template'])
        context = page_config['context'].copy()
        
        # 添加 request 到 context
        factory = RequestFactory()
        request = factory.get(path)
        context['request'] = request
        
        html = template.render(context)
        return html, None
        
    except Exception as e:
        import traceback
        error_html = f'''
        <html>
        <body style="background:#0a0a0f;color:#e4e4e7;font-family:monospace;padding:40px;">
            <h1 style="color:#ef4444;">Template Error</h1>
            <pre style="background:#18181b;padding:20px;border-radius:8px;overflow-x:auto;white-space:pre-wrap;">
{traceback.format_exc()}
            </pre>
            <p><a href="/_preview" style="color:#22c55e;">Back to preview</a></p>
        </body>
        </html>
        '''
        return None, error_html


def serve_static(path):
    """服务静态文件"""
    # 移除 /static/ 前缀
    relative_path = path[len('/static/'):]
    file_path = os.path.join(STATIC_DIR, relative_path)
    
    # 处理 URL 参数 (如 ?v=20260315)
    if '?' in file_path:
        file_path = file_path.split('?')[0]
    
    if not os.path.exists(file_path):
        return None, None, 'text/plain'
    
    # 获取 MIME 类型
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'
    
    with open(file_path, 'rb') as f:
        content = f.read()
    
    return content, mime_type, None


def handle_request(environ):
    """处理请求"""
    path = environ.get('PATH_INFO', '/')
    
    # 预览索引页面
    if path == '/_preview':
        return index_page(), 'text/html', None
    
    # 静态文件
    if path.startswith('/static/'):
        content, mime_type, error = serve_static(path)
        if error:
            return f'404 - Static file not found: {path}', 'text/plain', None
        return content, mime_type, 'binary'
    
    # 渲染模板页面
    html, error = render_page(path)
    if error:
        return error, 'text/html', None
    return html, 'text/html', None


def application(environ, start_response):
    """WSGI 应用"""
    body, content_type, mode = handle_request(environ)
    
    if mode == 'binary':
        body_bytes = body
    else:
        body_bytes = body.encode('utf-8')
    
    status = '200 OK'
    headers = [
        ('Content-Type', f'{content_type}; charset=utf-8' if not mode == 'binary' else content_type),
        ('Content-Length', str(len(body_bytes))),
    ]
    start_response(status, headers)
    return [body_bytes]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    
    print(f"\n🚀 Template Preview Server")
    print(f"=" * 50)
    print(f"📍 URL: http://localhost:{port}")
    print(f"")
    print(f"Available pages:")
    print(f"  • Preview Index: http://localhost:{port}/_preview")
    for path, config in PAGES.items():
        print(f"  • {config['title']}: http://localhost:{port}{path}")
    print(f"")
    print(f"Static files: {STATIC_DIR}")
    print(f"")
    print(f"Press Ctrl+C to stop\n")
    
    server = make_server('0.0.0.0', port, application)
    server.serve_forever()