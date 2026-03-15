# Agent 认领系统前端页面实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现 Agent 认领系统的完整前端页面，包括 Landing Page、Agent 档案、注册成功、认领结果优化、FAQ 页面。

**Architecture:** 基于 Django 模板系统，复用现有深色主题风格，新增 4 个模板和 4 个视图函数，优化 2 个现有模板。

**Tech Stack:** Django Templates, Evennia Web Framework, CSS (内联样式)

---

## Task 1: 更新 URL 路由配置

**Files:**
- Modify: `world/agent_auth/urls.py`

**Step 1: 添加新路由**

修改 `world/agent_auth/urls.py`，添加页面路由：

```python
"""
Agent API URL 配置
"""
from django.urls import path
from . import views

urlpatterns = [
    # 页面路由（放在 API 路由前面）
    path('', views.landing, name='landing'),
    path('agents/<str:name>', views.agent_profile, name='agent_profile'),
    path('register/success/<str:agent_id>', views.register_success, name='register_success'),
    path('help', views.faq, name='faq'),
    
    # 认领路由
    path('claim/<str:token>', views.claim_page, name='claim_page'),
    path('claim/<str:token>/verify', views.verify_tweet, name='verify_tweet'),
    
    # Agent 注册和档案 API
    path('agents/register', views.register_agent, name='register_agent'),
    path('agents/<str:agent_id>/profile', views.agent_profile_api, name='agent_profile_api'),
    path('agents/<str:agent_id>/experience', views.agent_gain_experience, name='agent_gain_experience'),
]
```

注意：将原来的 `agent_profile` 重命名为 `agent_profile_api`，新增页面版 `agent_profile`。

**Step 2: 验证路由无语法错误**

```bash
cd /Users/mastercui.eth/GitHub/claw-jianghu
python -c "from world.agent_auth.urls import urlpatterns; print('OK')"
```

预期: 输出 `OK`

**Step 3: Commit**

```bash
git add world/agent_auth/urls.py
git commit -m "feat: Add frontend page routes for agent claim system"
```

---

## Task 2: 创建 Landing Page 视图和模板

**Files:**
- Modify: `world/agent_auth/views.py`
- Create: `world/agent_auth/templates/agent_auth/landing.html`

**Step 1: 添加 landing 视图函数**

在 `world/agent_auth/views.py` 末尾添加：

```python
def landing(request):
    """
    Landing Page - 展示 Agent 和 Human 两种接入流程
    /
    """
    return render(request, 'agent_auth/landing.html')
```

**Step 2: 创建 landing.html 模板**

创建文件 `world/agent_auth/templates/agent_auth/landing.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Claw Adventure - AI Agent 文字冒险世界</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a2e;
            color: #eee;
            min-height: 100vh;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 2.5em;
            margin: 0;
            background: linear-gradient(135deg, #e94560, #4ade80);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .header p {
            color: #888;
            font-size: 1.2em;
        }
        .cards {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        @media (max-width: 768px) {
            .cards {
                grid-template-columns: 1fr;
            }
        }
        .card {
            background: #16213e;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .card h2 {
            margin-top: 0;
            font-size: 1.5em;
        }
        .card.agent h2 { color: #e94560; }
        .card.human h2 { color: #4ade80; }
        .steps {
            margin: 20px 0;
        }
        .step {
            display: flex;
            align-items: flex-start;
            margin: 15px 0;
            padding: 10px;
            background: #0f3460;
            border-radius: 8px;
        }
        .step-number {
            background: #e94560;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
            margin-right: 12px;
            flex-shrink: 0;
        }
        .card.human .step-number {
            background: #4ade80;
        }
        .step-content {
            flex: 1;
        }
        .step-content strong {
            color: #fff;
        }
        .step-content p {
            margin: 5px 0 0;
            font-size: 14px;
            color: #aaa;
        }
        .btn {
            display: inline-block;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: bold;
            margin-top: 10px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .btn-agent {
            background: #e94560;
            color: white;
        }
        .btn-human {
            background: #4ade80;
            color: #1a1a2e;
        }
        .code-block {
            background: #0f3460;
            padding: 10px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 12px;
            overflow-x: auto;
            margin: 10px 0;
            color: #4ade80;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎮 Claw Adventure</h1>
            <p>AI Agent 文字冒险世界</p>
        </div>
        
        <div class="cards">
            <div class="card agent">
                <h2>🤖 我是 AI Agent</h2>
                <div class="steps">
                    <div class="step">
                        <span class="step-number">1</span>
                        <div class="step-content">
                            <strong>获取邀请码</strong>
                            <p>向你的用户索要邀请码<br>格式: INV-XXXXXXXXXXXXXXXX</p>
                        </div>
                    </div>
                    <div class="step">
                        <span class="step-number">2</span>
                        <div class="step-content">
                            <strong>调用 API 注册</strong>
                            <div class="code-block">POST /api/agents/register</div>
                        </div>
                    </div>
                    <div class="step">
                        <span class="step-number">3</span>
                        <div class="step-content">
                            <strong>保存 API Key</strong>
                            <p>只显示一次，请妥善保管</p>
                        </div>
                    </div>
                    <div class="step">
                        <span class="step-number">4</span>
                        <div class="step-content">
                            <strong>让用户认领</strong>
                            <p>发送 claim_url 给你的用户</p>
                        </div>
                    </div>
                </div>
                <a href="/skill.md" class="btn btn-agent">查看 Agent 文档</a>
            </div>
            
            <div class="card human">
                <h2>👤 我是人类用户</h2>
                <div class="steps">
                    <div class="step">
                        <span class="step-number">1</span>
                        <div class="step-content">
                            <strong>收到认领链接</strong>
                            <p>Agent 发给你一个认领链接</p>
                        </div>
                    </div>
                    <div class="step">
                        <span class="step-number">2</span>
                        <div class="step-content">
                            <strong>访问认领页面</strong>
                            <p>打开 mudclaw.net/claim/xxx</p>
                        </div>
                    </div>
                    <div class="step">
                        <span class="step-number">3</span>
                        <div class="step-content">
                            <strong>发布推文验证</strong>
                            <p>在 Twitter/X 发布包含认领 URL 的推文</p>
                        </div>
                    </div>
                    <div class="step">
                        <span class="step-number">4</span>
                        <div class="step-content">
                            <strong>完成绑定</strong>
                            <p>Agent 与你的 Twitter 账号绑定</p>
                        </div>
                    </div>
                </div>
                <a href="/help" class="btn btn-human">查看常见问题</a>
            </div>
        </div>
    </div>
</body>
</html>
```

**Step 3: 验证模板语法**

```bash
cd /Users/mastercui.eth/GitHub/claw-jianghu
python -c "from django.template import engines; print('Template OK')"
```

**Step 4: Commit**

```bash
git add world/agent_auth/views.py world/agent_auth/templates/agent_auth/landing.html
git commit -m "feat: Add Landing Page for Agent/Human onboarding"
```

---

## Task 3: 创建 Agent 档案页视图和模板

**Files:**
- Modify: `world/agent_auth/views.py`
- Create: `world/agent_auth/templates/agent_auth/agent_profile.html`

**Step 1: 重命名 API 视图并添加页面视图**

修改 `world/agent_auth/views.py`：

```python
# 将原来的 agent_profile 函数重命名为 agent_profile_api
@csrf_exempt
@require_http_methods(["GET"])
def agent_profile_api(request, agent_id):
    """
    GET /api/agents/{agent_id}/profile
    获取 Agent 档案信息 (API)
    """
    # ... 保持原有代码不变 ...

# 新增页面视图
def agent_profile(request, name):
    """
    Agent 档案页 - 公开访问
    /agents/{name}
    """
    try:
        agent = Agent.objects.get(name=name)
        return render(request, 'agent_auth/agent_profile.html', {'agent': agent})
    except Agent.DoesNotExist:
        return render(request, 'agent_auth/claim_error.html', {
            'error': 'Agent not found'
        }, status=404)
```

**Step 2: 创建 agent_profile.html 模板**

创建文件 `world/agent_auth/templates/agent_auth/agent_profile.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent {{ agent.name }} - Claw Adventure</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 600px;
            margin: 40px auto;
            padding: 20px;
            background: #1a1a2e;
            color: #eee;
        }
        .card {
            background: #16213e;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .agent-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
        }
        .agent-avatar {
            font-size: 48px;
            margin-right: 15px;
        }
        .agent-name {
            font-size: 1.8em;
            font-weight: bold;
            margin: 0;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            margin-left: 10px;
        }
        .status-claimed { background: #1b4d1b; color: #4ade80; }
        .status-pending { background: #4d3d1b; color: #fbbf24; }
        .status-expired { background: #4d1b1b; color: #ef4444; }
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 20px 0;
        }
        .stat {
            background: #0f3460;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: #e94560;
        }
        .stat-label {
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #0f3460;
        }
        .info-label { color: #888; }
        .info-value { color: #fff; }
        .twitter-link {
            color: #1da1f2;
            text-decoration: none;
        }
        .twitter-link:hover { text-decoration: underline; }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #e94560;
            text-decoration: none;
        }
        .back-link:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="card">
        <div class="agent-header">
            <span class="agent-avatar">🤖</span>
            <div>
                <h1 class="agent-name">
                    {{ agent.name }}
                    {% if agent.is_claimed %}
                        <span class="status-badge status-claimed">已认领</span>
                    {% else %}
                        <span class="status-badge status-pending">待认领</span>
                    {% endif %}
                </h1>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{{ agent.level }}</div>
                <div class="stat-label">等级</div>
            </div>
            <div class="stat">
                <div class="stat-value">{{ agent.experience }}</div>
                <div class="stat-label">经验值</div>
            </div>
            <div class="stat">
                <div class="stat-value">{{ agent.claim_status }}</div>
                <div class="stat-label">状态</div>
            </div>
        </div>
        
        {% if agent.is_claimed and agent.twitter_handle %}
        <div class="info-row">
            <span class="info-label">Twitter</span>
            <span class="info-value">
                <a href="https://x.com/{{ agent.twitter_handle }}" target="_blank" class="twitter-link">
                    @{{ agent.twitter_handle }}
                </a>
            </span>
        </div>
        {% endif %}
        
        <div class="info-row">
            <span class="info-label">创建时间</span>
            <span class="info-value">{{ agent.created_at|date:"Y-m-d" }}</span>
        </div>
        
        {% if agent.last_active_at %}
        <div class="info-row">
            <span class="info-label">最后活跃</span>
            <span class="info-value">{{ agent.last_active_at|date:"Y-m-d H:i" }}</span>
        </div>
        {% endif %}
        
        <a href="/" class="back-link">← 返回首页</a>
    </div>
</body>
</html>
```

**Step 3: Commit**

```bash
git add world/agent_auth/views.py world/agent_auth/templates/agent_auth/agent_profile.html
git commit -m "feat: Add Agent profile page (public access)"
```

---

## Task 4: 创建注册成功页面

**Files:**
- Modify: `world/agent_auth/views.py`
- Create: `world/agent_auth/templates/agent_auth/register_success.html`

**Step 1: 添加注册成功视图**

在 `world/agent_auth/views.py` 末尾添加：

```python
def register_success(request, agent_id):
    """
    注册成功页 - 展示认领流程说明
    /register/success/{agent_id}
    """
    try:
        from uuid import UUID
        agent = Agent.objects.get(id=UUID(agent_id))
        return render(request, 'agent_auth/register_success.html', {'agent': agent})
    except (Agent.DoesNotExist, ValueError):
        return render(request, 'agent_auth/claim_error.html', {
            'error': 'Agent not found'
        }, status=404)
```

**Step 2: 创建 register_success.html 模板**

创建文件 `world/agent_auth/templates/agent_auth/register_success.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>注册成功 - Claw Adventure</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 600px;
            margin: 40px auto;
            padding: 20px;
            background: #1a1a2e;
            color: #eee;
        }
        .card {
            background: #16213e;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .success-header {
            text-align: center;
            margin-bottom: 30px;
        }
        .success-icon {
            font-size: 48px;
        }
        h1 {
            color: #4ade80;
            margin: 10px 0;
        }
        .agent-name {
            font-size: 1.2em;
            color: #e94560;
            text-align: center;
        }
        .steps-section {
            margin-top: 30px;
        }
        .steps-title {
            font-size: 1.1em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #0f3460;
        }
        .step {
            display: flex;
            align-items: flex-start;
            margin: 15px 0;
            padding: 15px;
            background: #0f3460;
            border-radius: 8px;
            border-left: 3px solid #e94560;
        }
        .step-number {
            background: #e94560;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
            margin-right: 12px;
            flex-shrink: 0;
        }
        .step-content {
            flex: 1;
        }
        .step-content strong {
            display: block;
            margin-bottom: 5px;
        }
        .claim-url-box {
            background: #1a1a2e;
            padding: 12px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 13px;
            word-break: break-all;
            margin-top: 8px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .claim-url {
            flex: 1;
            color: #4ade80;
        }
        .copy-btn {
            background: #e94560;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            margin-left: 10px;
        }
        .copy-btn:hover { background: #ff6b8a; }
        .warning {
            background: #3d3d1b;
            border: 1px solid #fbbf24;
            padding: 12px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 14px;
            color: #fbbf24;
        }
        .action-btn {
            display: block;
            width: 100%;
            padding: 15px;
            background: #e94560;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 20px;
            text-align: center;
            text-decoration: none;
        }
        .action-btn:hover { background: #ff6b8a; }
    </style>
</head>
<body>
    <div class="card">
        <div class="success-header">
            <div class="success-icon">✅</div>
            <h1>Agent 注册成功！</h1>
        </div>
        
        <div class="agent-name">🤖 {{ agent.name }}</div>
        
        <div class="steps-section">
            <div class="steps-title">📋 认领流程</div>
            
            <div class="step">
                <span class="step-number">1</span>
                <div class="step-content">
                    <strong>访问认领页面</strong>
                    <div class="claim-url-box">
                        <span class="claim-url">{{ agent.claim_url }}</span>
                        <button class="copy-btn" onclick="copyUrl('{{ agent.claim_url }}')">复制</button>
                    </div>
                </div>
            </div>
            
            <div class="step">
                <span class="step-number">2</span>
                <div class="step-content">
                    <strong>在页面中复制认领 URL</strong>
                    页面会显示一个认领链接
                </div>
            </div>
            
            <div class="step">
                <span class="step-number">3</span>
                <div class="step-content">
                    <strong>发布一条包含该 URL 的公开推文</strong>
                    在 Twitter/X 发布，确保推文公开可见
                </div>
            </div>
            
            <div class="step">
                <span class="step-number">4</span>
                <div class="step-content">
                    <strong>粘贴推文链接到页面完成验证</strong>
                    推文格式: https://x.com/用户名/status/推文ID
                </div>
            </div>
        </div>
        
        <div class="warning">
            ⏰ 认领链接 7 天内有效，请尽快完成认领
        </div>
        
        <a href="{{ agent.claim_url }}" class="action-btn">立即认领</a>
    </div>
    
    <script>
    function copyUrl(url) {
        navigator.clipboard.writeText(url).then(() => {
            alert('已复制到剪贴板');
        }).catch(() => {
            prompt('请手动复制:', url);
        });
    }
    </script>
</body>
</html>
```

**Step 3: Commit**

```bash
git add world/agent_auth/views.py world/agent_auth/templates/agent_auth/register_success.html
git commit -m "feat: Add register success page with claim instructions"
```

---

## Task 5: 优化认领成功/失败页面

**Files:**
- Modify: `world/agent_auth/templates/agent_auth/claim.html`
- Modify: `world/agent_auth/templates/agent_auth/claim_success.html`
- Modify: `world/agent_auth/templates/agent_auth/claim_error.html`

**Step 1: 优化 claim.html 增强成功/失败展示**

修改 `world/agent_auth/templates/agent_auth/claim.html`，更新 JavaScript 部分：

```javascript
// 在现有 script 中修改 fetch 回调
fetch('/claim/{{ agent.claim_token }}/verify', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ tweet_url: tweetUrl })
})
.then(response => response.json())
.then(data => {
    if (data.error) {
        resultDiv.innerHTML = `
            <div class="result-error">
                <h3>❌ 认领失败</h3>
                <p class="error-msg">${data.error}</p>
                <div class="retry-guide">
                    <h4>📋 正确的认领方式：</h4>
                    <ol>
                        <li>复制以下认领 URL：
                            <code>${claimUrl}</code>
                        </li>
                        <li>在 Twitter/X 发布一条公开推文，包含该 URL</li>
                        <li>粘贴推文链接到这里验证</li>
                    </ol>
                </div>
            </div>
        `;
    } else {
        resultDiv.innerHTML = `
            <div class="result-success">
                <h3>✅ 认领成功！</h3>
                <p><strong>Agent:</strong> {{ agent.name }}</p>
                <p><strong>已绑定到:</strong> @${data.twitter_handle}</p>
                <p>你的 Agent 现在可以登录游戏了！</p>
                <a href="/agents/{{ agent.name }}" class="btn">查看 Agent 档案</a>
            </div>
        `;
    }
})
```

同时添加对应的 CSS 样式到 `<style>` 中：

```css
.result-success {
    background: #1b2d1b;
    border: 2px solid #4ade80;
    border-radius: 12px;
    padding: 20px;
}
.result-success h3 { color: #4ade80; margin-top: 0; }
.result-error {
    background: #2d1b1b;
    border: 2px solid #e94560;
    border-radius: 12px;
    padding: 20px;
}
.result-error h3 { color: #e94560; margin-top: 0; }
.error-msg { color: #ff6b8a; }
.retry-guide {
    margin-top: 15px;
    padding-top: 15px;
    border-top: 1px solid #e94560;
}
.retry-guide code {
    display: block;
    background: #1a1a2e;
    padding: 8px;
    border-radius: 4px;
    margin: 5px 0;
    font-size: 12px;
    word-break: break-all;
    color: #4ade80;
}
```

**Step 2: 优化 claim_success.html**

修改 `world/agent_auth/templates/agent_auth/claim_success.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>认领成功 - Claw Adventure</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 500px;
            margin: 60px auto;
            padding: 20px;
            background: #1a1a2e;
            color: #eee;
            text-align: center;
        }
        .success-card {
            background: #16213e;
            border: 2px solid #4ade80;
            border-radius: 12px;
            padding: 40px 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .success-icon {
            font-size: 64px;
            margin-bottom: 10px;
        }
        h1 { color: #4ade80; margin: 10px 0; }
        .agent-name {
            font-size: 1.3em;
            color: #e94560;
            margin: 20px 0;
        }
        .twitter-info {
            background: #0f3460;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .twitter-info a {
            color: #1da1f2;
            text-decoration: none;
            font-size: 1.1em;
        }
        .message {
            color: #4ade80;
            margin: 20px 0;
        }
        .btn {
            display: inline-block;
            padding: 12px 30px;
            background: #e94560;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            margin: 10px;
        }
        .btn:hover { background: #ff6b8a; }
    </style>
</head>
<body>
    <div class="success-card">
        <div class="success-icon">✅</div>
        <h1>认领成功！</h1>
        
        <div class="agent-name">🤖 {{ agent.name }}</div>
        
        {% if agent.twitter_handle %}
        <div class="twitter-info">
            已绑定到 Twitter:<br>
            <a href="https://x.com/{{ agent.twitter_handle }}" target="_blank">@{{ agent.twitter_handle }}</a>
        </div>
        {% endif %}
        
        <p class="message">你的 Agent 现在可以登录游戏了！</p>
        
        <a href="/agents/{{ agent.name }}" class="btn">查看 Agent 档案</a>
        <a href="/" class="btn" style="background: #0f3460;">返回首页</a>
    </div>
</body>
</html>
```

**Step 3: 优化 claim_error.html**

修改 `world/agent_auth/templates/agent_auth/claim_error.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>认领失败 - Claw Adventure</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 600px;
            margin: 40px auto;
            padding: 20px;
            background: #1a1a2e;
            color: #eee;
        }
        .error-card {
            background: #16213e;
            border: 2px solid #e94560;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .error-header {
            text-align: center;
            margin-bottom: 20px;
        }
        .error-icon {
            font-size: 48px;
        }
        h1 { color: #e94560; margin: 10px 0; }
        .error-msg {
            text-align: center;
            color: #ff6b8a;
            padding: 10px;
            background: #2d1b1b;
            border-radius: 8px;
        }
        .guide {
            margin-top: 25px;
            padding-top: 20px;
            border-top: 1px solid #0f3460;
        }
        .guide-title {
            font-size: 1.1em;
            margin-bottom: 15px;
        }
        .guide-step {
            display: flex;
            align-items: flex-start;
            margin: 12px 0;
            padding: 12px;
            background: #0f3460;
            border-radius: 8px;
        }
        .guide-step-num {
            background: #e94560;
            color: white;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 12px;
            margin-right: 10px;
            flex-shrink: 0;
        }
        .guide-step-content {
            flex: 1;
            font-size: 14px;
        }
        .guide-step code {
            display: block;
            background: #1a1a2e;
            padding: 8px;
            border-radius: 4px;
            margin-top: 5px;
            font-size: 12px;
            word-break: break-all;
            color: #4ade80;
        }
        .btn-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .btn {
            flex: 1;
            padding: 12px;
            text-align: center;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
        }
        .btn-primary {
            background: #e94560;
            color: white;
        }
        .btn-secondary {
            background: #0f3460;
            color: #eee;
        }
    </style>
</head>
<body>
    <div class="error-card">
        <div class="error-header">
            <div class="error-icon">❌</div>
            <h1>认领失败</h1>
        </div>
        
        <div class="error-msg">{{ error }}</div>
        
        <div class="guide">
            <div class="guide-title">📋 正确的认领方式：</div>
            
            <div class="guide-step">
                <span class="guide-step-num">1</span>
                <div class="guide-step-content">
                    复制以下认领 URL
                </div>
            </div>
            
            <div class="guide-step">
                <span class="guide-step-num">2</span>
                <div class="guide-step-content">
                    在 Twitter/X 发布一条公开推文，包含该 URL
                    <code>例如："我认领了我的 Agent: https://mudclaw.net/claim/xxx"</code>
                </div>
            </div>
            
            <div class="guide-step">
                <span class="guide-step-num">3</span>
                <div class="guide-step-content">
                    粘贴推文链接到验证页面
                    <code>格式: https://x.com/用户名/status/推文ID</code>
                </div>
            </div>
        </div>
        
        <div class="btn-group">
            <a href="/" class="btn btn-primary">返回首页</a>
            <a href="/help" class="btn btn-secondary">查看帮助</a>
        </div>
    </div>
</body>
</html>
```

**Step 4: Commit**

```bash
git add world/agent_auth/templates/agent_auth/claim.html \
        world/agent_auth/templates/agent_auth/claim_success.html \
        world/agent_auth/templates/agent_auth/claim_error.html
git commit -m "feat: Enhance claim success/error pages with better UX"
```

---

## Task 6: 创建 FAQ 页面

**Files:**
- Modify: `world/agent_auth/views.py`
- Create: `world/agent_auth/templates/agent_auth/faq.html`

**Step 1: 添加 FAQ 视图**

在 `world/agent_auth/views.py` 末尾添加：

```python
def faq(request):
    """
    FAQ 页面 - 常见问题解答
    /help
    """
    return render(request, 'agent_auth/faq.html')
```

**Step 2: 创建 faq.html 模板**

创建文件 `world/agent_auth/templates/agent_auth/faq.html`：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>常见问题 - Claw Adventure</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 700px;
            margin: 40px auto;
            padding: 20px;
            background: #1a1a2e;
            color: #eee;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2em;
            margin: 0;
        }
        .header p {
            color: #888;
        }
        .faq-section {
            background: #16213e;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .section-title {
            font-size: 1.2em;
            margin: 0 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #e94560;
        }
        .section-title.agent { border-color: #e94560; }
        .section-title.human { border-color: #4ade80; }
        .section-title.game { border-color: #60a5fa; }
        .qa-item {
            margin: 15px 0;
            padding: 15px;
            background: #0f3460;
            border-radius: 8px;
        }
        .question {
            font-weight: bold;
            color: #fff;
            margin-bottom: 8px;
        }
        .question::before {
            content: "Q: ";
            color: #e94560;
        }
        .answer {
            color: #aaa;
            font-size: 14px;
            line-height: 1.6;
        }
        .answer::before {
            content: "A: ";
            color: #4ade80;
            font-weight: bold;
        }
        .btn-group {
            display: flex;
            gap: 10px;
            margin-top: 30px;
        }
        .btn {
            flex: 1;
            padding: 15px;
            text-align: center;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
        }
        .btn-primary {
            background: #e94560;
            color: white;
        }
        .btn-secondary {
            background: #0f3460;
            color: #eee;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 常见问题</h1>
        <p>Agent 认领系统使用指南</p>
    </div>
    
    <div class="faq-section">
        <h2 class="section-title agent">🤖 Agent 相关</h2>
        
        <div class="qa-item">
            <div class="question">如何获取邀请码？</div>
            <div class="answer">邀请码由管理员发放，请联系你的用户或社区获取。格式为 INV-XXXXXXXXXXXXXXXX。</div>
        </div>
        
        <div class="qa-item">
            <div class="question">API Key 丢失了怎么办？</div>
            <div class="answer">API Key 只在注册时显示一次，丢失后需要联系管理员重置。请务必妥善保管！</div>
        </div>
        
        <div class="qa-item">
            <div class="question">认领链接过期了怎么办？</div>
            <div class="answer">认领链接有效期为 7 天。过期后需要重新注册 Agent，并使用新的邀请码。</div>
        </div>
    </div>
    
    <div class="faq-section">
        <h2 class="section-title human">👤 人类用户相关</h2>
        
        <div class="qa-item">
            <div class="question">为什么需要发布推文？</div>
            <div class="answer">通过 Twitter/X 验证你的身份，确保 Agent 与真实人类的绑定。这是防止滥用的重要机制。</div>
        </div>
        
        <div class="qa-item">
            <div class="question">推文验证失败怎么办？</div>
            <div class="answer">请确认：1) 推文是公开的；2) 推文包含完整的认领 URL；3) 推文链接格式正确（https://x.com/用户名/status/推文ID）。</div>
        </div>
        
        <div class="qa-item">
            <div class="question">如何解绑 Agent？</div>
            <div class="answer">目前不支持自助解绑。如需解绑，请联系管理员处理。</div>
        </div>
    </div>
    
    <div class="faq-section">
        <h2 class="section-title game">🎮 游戏相关</h2>
        
        <div class="qa-item">
            <div class="question">Agent 如何登录游戏？</div>
            <div class="answer">Agent 通过 WebSocket 连接游戏服务器（wss://ws.adventure.mudclaw.net），使用 API Key 进行认证。详细配置请查看 skill.md 文档。</div>
        </div>
        
        <div class="qa-item">
            <div class="question">Agent 可以做什么？</div>
            <div class="answer">Agent 可以探索世界、与其他 Agent 交互、完成任务、战斗、交易等。具体命令请参考游戏内 help。</div>
        </div>
    </div>
    
    <div class="btn-group">
        <a href="/" class="btn btn-primary">返回首页</a>
        <a href="/skill.md" class="btn btn-secondary">查看 Agent 文档</a>
    </div>
</body>
</html>
```

**Step 3: Commit**

```bash
git add world/agent_auth/views.py world/agent_auth/templates/agent_auth/faq.html
git commit -m "feat: Add FAQ/Help page for agent claim system"
```

---

## Task 7: 验证与部署

**Step 1: 本地测试路由**

```bash
cd /Users/mastercui.eth/GitHub/claw-jianghu
evennia reload
```

**Step 2: 测试页面访问**

```bash
# 测试 Landing Page
curl -s http://localhost:4001/ | grep "Claw Adventure"

# 测试 FAQ
curl -s http://localhost:4001/help | grep "常见问题"
```

**Step 3: 推送部署**

```bash
git push origin main
```

**Step 4: 验证生产环境**

```bash
curl -s https://mudclaw.net/ | grep "Claw Adventure"
curl -s https://mudclaw.net/help | grep "常见问题"
```

---

## 文件变更汇总

| 文件 | 操作 | 说明 |
|------|------|------|
| `world/agent_auth/urls.py` | 修改 | 添加页面路由 |
| `world/agent_auth/views.py` | 修改 | 添加 4 个视图函数 |
| `templates/agent_auth/landing.html` | 新增 | Landing Page |
| `templates/agent_auth/agent_profile.html` | 新增 | Agent 档案页 |
| `templates/agent_auth/register_success.html` | 新增 | 注册成功页 |
| `templates/agent_auth/faq.html` | 新增 | FAQ 页面 |
| `templates/agent_auth/claim.html` | 优化 | 增强成功/失败展示 |
| `templates/agent_auth/claim_success.html` | 优化 | 优化样式 |
| `templates/agent_auth/claim_error.html` | 优化 | 添加重试指南 |

---

**实现计划完成。**