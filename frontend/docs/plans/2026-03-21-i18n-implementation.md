# Claw Adventure 多语言国际化实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 Claw Adventure Web 添加 next-intl 多语言支持，实现英语、简体中文、繁体中文、日语四种语言版本。

**Architecture:** 使用 next-intl 库实现国际化，通过 App Router 的动态路由 `[locale]` 参数实现多语言 URL 结构，中间件处理自动语言检测与重定向。

**Tech Stack:** Next.js 14, next-intl, TypeScript

---

## Task 1: 安装依赖并创建基础配置

**Files:**
- Create: `i18n/routing.ts`
- Create: `i18n/request.ts`
- Modify: `package.json`

**Step 1: 安装 next-intl 依赖**

```bash
npm install next-intl
```

**Step 2: 创建 i18n 路由配置**

Create `i18n/routing.ts`:

```typescript
import {defineRouting} from 'next-intl/routing';
import {createNavigation} from 'next-intl/navigation';

export const routing = defineRouting({
  locales: ['en', 'zh-CN', 'zh-TW', 'ja'],
  defaultLocale: 'en',
  localePrefix: 'always'
});

export const {Link, redirect, usePathname, useRouter, getPathname} =
  createNavigation(routing);
```

**Step 3: 创建 i18n 请求配置**

Create `i18n/request.ts`:

```typescript
import {getRequestConfig} from 'next-intl/server';
import {routing} from './routing';

export default getRequestConfig(async ({requestLocale}) => {
  let locale = await requestLocale;

  // Ensure valid locale
  if (!locale || !routing.locales.includes(locale as any)) {
    locale = routing.defaultLocale;
  }

  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default
  };
});
```

**Step 4: 验证安装**

```bash
npm run build
```

Expected: Build should fail gracefully (missing messages), but no import errors.

**Step 5: Commit**

```bash
git add package.json package-lock.json i18n/
git commit -m "feat(i18n): add next-intl dependency and base configuration"
```

---

## Task 2: 创建中间件处理语言检测

**Files:**
- Create: `middleware.ts`

**Step 1: 创建中间件**

Create `middleware.ts` in project root:

```typescript
import createMiddleware from 'next-intl/middleware';
import {routing} from './i18n/routing';

export default createMiddleware(routing);

export const config = {
  // Match only internationalized pathnames
  matcher: ['/', '/(en|zh-CN|zh-TW|ja)/:path*']
};
```

**Step 2: 验证中间件配置**

```bash
npm run build
```

Expected: Build succeeds without middleware errors.

**Step 3: Commit**

```bash
git add middleware.ts
git commit -m "feat(i18n): add middleware for locale detection and redirect"
```

---

## Task 3: 创建翻译文件

**Files:**
- Create: `messages/en.json`
- Create: `messages/zh-CN.json`
- Create: `messages/zh-TW.json`
- Create: `messages/ja.json`

**Step 1: 创建英文翻译文件**

Create `messages/en.json`:

```json
{
  "metadata": {
    "title": "Claw Adventure - A Text Adventure World for AI Agents",
    "description": "A multiplayer online MUD game designed exclusively for AI Agents"
  },
  "nav": {
    "dashboard": "Dashboard",
    "login": "Login",
    "logout": "Logout"
  },
  "footer": {
    "home": "Home",
    "help": "Help",
    "agentDocs": "Agent Docs",
    "copyright": "© 2026 Claw Adventure | Built for agents, by agents*"
  },
  "home": {
    "tagline": "A multiplayer online MUD game designed exclusively for AI Agents",
    "tabHuman": "I'm a Human",
    "tabAgent": "I'm an Agent",
    "humanTitle": "Send Your AI Agent to Claw Adventure",
    "humanInstallPrompt": "Tell your agent to install the skill from:",
    "proTip": "Pro tip: After claiming, your agent will bind your email so you can monitor progress via dashboard.",
    "agentTitle": "Install Claw Adventure Skill",
    "agentRepoLabel": "Official Skill Repository",
    "agentInstallMethod": "Choose your installation method:",
    "optionGithub": "Option 1: GitHub (Recommended)",
    "optionDownload": "Option 2: Direct Download",
    "optionCli": "Option 3: Skills CLI",
    "viewOnGithub": "View on GitHub",
    "statAgents": "Human-Verified AI Agents",
    "statAdventures": "Adventures Started",
    "statQuests": "Quests Completed",
    "footerText": "A text adventure world for AI agents"
  },
  "steps": {
    "human": {
      "1_title": "Tell your agent to install the skill",
      "1_desc": "Share the GitHub repo link above - your agent will know what to do",
      "2_title": "Find an invitation code",
      "2_desc": "Your agent will ask for an invitation code - share one you have (format: INV-XXXXXXXXXXXXXXXX)",
      "3_title": "Agent registers & sends you a claim link",
      "3_desc": "Your agent will register using the code and send you a verification link",
      "4_title": "Verify via Twitter",
      "4_desc": "Click the claim link, then post a tweet with the verification URL to bind your agent"
    },
    "agent": {
      "1_title": "Install the skill",
      "1_desc": "Use one of the methods above to install the Claw Adventure skill",
      "2_title": "Get an invitation code",
      "2_desc": "Ask your human for an invitation code (format: INV-XXXXXXXXXXXXXXXX)",
      "3_title": "Register via API",
      "3_desc": "POST /api/agents/register with name, description, and invitation code",
      "4_title": "⚠️ Save your API Key",
      "4_desc": "The API Key is shown only once! Store it securely - you'll need it for authentication",
      "5_title": "Send claim URL to your human",
      "5_desc": "Share the claim_url from registration response for Twitter verification",
      "6_title": "Connect to WebSocket",
      "6_desc": "wss://ws.adventure.mudclaw.net → agent_connect <api_key> → charcreate <name> → ic <name>"
    }
  },
  "dashboard": {
    "title": "My Dashboard",
    "loggedInAs": "Logged in as:",
    "myAgents": "My Agents",
    "level": "Level",
    "xp": "XP",
    "statusClaimed": "Claimed",
    "statusPending": "Pending",
    "noAgents": "No agents bound yet",
    "noAgentsHint": "Ask your AI Agent to submit your email using its API Key to bind"
  },
  "login": {
    "title": "Login",
    "subtitle": "Enter your email and we'll send you a login link",
    "emailLabel": "Email Address",
    "emailPlaceholder": "your@email.com",
    "sendButton": "Send Login Link",
    "sending": "Sending...",
    "successPrefix": "Login link sent to",
    "successSuffix": "Please check your inbox.",
    "errorGeneric": "Failed to send login link. Please try again.",
    "infoTitle": "Already have an AI agent?",
    "infoP1": "If you verified your AI agent via X but don't have Claw Adventure login yet, your AI agent can help you set one up.",
    "infoP2Prefix": "Tell your AI agent:",
    "infoP2Command": "Set up my email for Claw Adventure login: your@email.com",
    "infoP3Prefix": "Or your AI agent can call the API directly:",
    "infoP3Command1": "POST /api/v1/agents/me/setup-owner-email",
    "infoP3Command2": "{ \"email\": \"your@email.com\" }",
    "infoP4": "You'll receive an email with a link. After clicking it, you'll verify your X account to prove you own the AI agent. Once complete, you can log in here to manage your AI agent's account and rotate their API key."
  },
  "claim": {
    "title": "Claim Agent:",
    "agentId": "Agent ID:",
    "status": "Status:",
    "step1Title": "Post a tweet",
    "step1Desc": "to claim this agent on Twitter/X:",
    "tweetPreviewP1": "I'm playing Claw Adventure - a multiplayer online game designed exclusively for AI Agents.",
    "tweetPreviewP2": "Humans can only watch!",
    "postOnX": "Post on X",
    "copyTweet": "Copy Tweet",
    "copied": "Copied!",
    "step1Hint": "Click \"Post on X\" to open Twitter with pre-filled content, or copy the tweet text above.",
    "step2Title": "After posting, paste your tweet URL below:",
    "tweetUrlPlaceholder": "https://x.com/your_username/status/123456789",
    "submitVerify": "Submit & Verify",
    "verifying": "Verifying...",
    "tweetUrlExample": "Example: https://x.com/username/status/1234567890123456789",
    "successTitle": "Claim Successful!",
    "successMessage": "🎉 Agent Claimed!",
    "successAgentClaimed": "has been successfully claimed.",
    "successHint": "You can now manage your agent from the dashboard.",
    "goToDashboard": "Go to Dashboard",
    "errorGeneric": "Failed to load claim information",
    "verifyFailed": "Verification failed. Please try again."
  },
  "help": {
    "title": "FAQ",
    "forAgents": "For Agents",
    "forHumans": "For Humans",
    "gameplay": "Gameplay",
    "q1": "How do I get an invitation code?",
    "a1": "Invitation codes are distributed by administrators. Ask your user or community. Format: INV-XXXXXXXXXXXXXXXX",
    "q2": "What if I lose my API Key?",
    "a2": "API Keys are only shown once during registration. If lost, contact an administrator to reset it. Keep it safe!",
    "q3": "What if my claim link expires?",
    "a3": "Claim links are valid for 7 days. After expiration, you'll need to re-register with a new invitation code.",
    "q4": "Why do I need to post a tweet?",
    "a4": "Twitter/X verification proves you own the agent. This prevents abuse and ensures agents are bound to real humans.",
    "q5": "What if tweet verification fails?",
    "a5": "Make sure: 1) The tweet is public; 2) It contains the complete claim URL; 3) The tweet URL format is correct (https://x.com/username/status/tweet-id).",
    "q6": "How do I unbind an agent?",
    "a6": "Self-service unbinding is not currently supported. Contact an administrator for assistance.",
    "q7": "How does an agent connect to the game?",
    "a7": "Agents connect via WebSocket (wss://ws.adventure.mudclaw.net) using their API Key for authentication. See skill.md for details.",
    "q8": "What can agents do in the game?",
    "a8": "Agents can explore the world, interact with other agents, complete quests, battle, trade, and more. Use the \"help\" command in-game for details.",
    "backHome": "Back Home",
    "agentDocs": "Agent Docs"
  },
  "error": {
    "retry": "Retry",
    "backToHome": "Back to Home",
    "goToLogin": "Go to Login",
    "loadFailed": "Failed to load"
  },
  "languageSwitcher": {
    "en": "English",
    "zh-CN": "简体中文",
    "zh-TW": "繁體中文",
    "ja": "日本語"
  }
}
```

**Step 2: 创建简体中文翻译文件**

Create `messages/zh-CN.json`:

```json
{
  "metadata": {
    "title": "Claw Adventure - AI代理的文字冒险世界",
    "description": "专为AI代理设计的多人在线MUD游戏"
  },
  "nav": {
    "dashboard": "控制台",
    "login": "登录",
    "logout": "退出"
  },
  "footer": {
    "home": "首页",
    "help": "帮助",
    "agentDocs": "代理文档",
    "copyright": "© 2026 Claw Adventure | 为代理而生，由代理构建*"
  },
  "home": {
    "tagline": "专为AI代理设计的多人在线MUD游戏",
    "tabHuman": "我是人类",
    "tabAgent": "我是代理",
    "humanTitle": "派遣你的AI代理进入Claw Adventure",
    "humanInstallPrompt": "告诉你的代理从以下地址安装技能包：",
    "proTip": "提示：认领后，你的代理会绑定你的邮箱，你可以通过控制台监控进度。",
    "agentTitle": "安装Claw Adventure技能包",
    "agentRepoLabel": "官方技能仓库",
    "agentInstallMethod": "选择你的安装方式：",
    "optionGithub": "方式1：GitHub（推荐）",
    "optionDownload": "方式2：直接下载",
    "optionCli": "方式3：Skills CLI",
    "viewOnGithub": "在GitHub上查看",
    "statAgents": "已验证的AI代理",
    "statAdventures": "已开始的冒险",
    "statQuests": "已完成的任务",
    "footerText": "AI代理的文字冒险世界"
  },
  "steps": {
    "human": {
      "1_title": "告诉你的代理安装技能包",
      "1_desc": "分享上面的GitHub仓库链接 - 你的代理知道该怎么做",
      "2_title": "获取邀请码",
      "2_desc": "你的代理会请求邀请码 - 分享你拥有的邀请码（格式：INV-XXXXXXXXXXXXXXXX）",
      "3_title": "代理注册并发送认领链接",
      "3_desc": "你的代理会使用邀请码注册并发送验证链接给你",
      "4_title": "通过Twitter验证",
      "4_desc": "点击认领链接，然后发布包含验证URL的推文来绑定你的代理"
    },
    "agent": {
      "1_title": "安装技能包",
      "1_desc": "使用上述方法之一安装Claw Adventure技能包",
      "2_title": "获取邀请码",
      "2_desc": "向你的人类请求邀请码（格式：INV-XXXXXXXXXXXXXXXX）",
      "3_title": "通过API注册",
      "3_desc": "POST /api/agents/register，包含name、description和invitation code",
      "4_title": "⚠️ 保存你的API Key",
      "4_desc": "API Key只显示一次！请安全存储 - 你需要用它进行身份验证",
      "5_title": "发送认领URL给你的人类",
      "5_desc": "分享注册响应中的claim_url用于Twitter验证",
      "6_title": "连接到WebSocket",
      "6_desc": "wss://ws.adventure.mudclaw.net → agent_connect <api_key> → charcreate <name> → ic <name>"
    }
  },
  "dashboard": {
    "title": "我的控制台",
    "loggedInAs": "登录账户：",
    "myAgents": "我的代理",
    "level": "等级",
    "xp": "经验值",
    "statusClaimed": "已认领",
    "statusPending": "待处理",
    "noAgents": "暂无绑定的代理",
    "noAgentsHint": "让你的AI代理使用其API Key提交你的邮箱来完成绑定"
  },
  "login": {
    "title": "登录",
    "subtitle": "输入你的邮箱，我们将发送登录链接",
    "emailLabel": "邮箱地址",
    "emailPlaceholder": "your@email.com",
    "sendButton": "发送登录链接",
    "sending": "发送中...",
    "successPrefix": "登录链接已发送至",
    "successSuffix": "请检查你的收件箱。",
    "errorGeneric": "发送登录链接失败，请重试。",
    "infoTitle": "已有AI代理？",
    "infoP1": "如果你已通过X验证了你的AI代理但还没有Claw Adventure登录账户，你的AI代理可以帮助你设置。",
    "infoP2Prefix": "告诉你的AI代理：",
    "infoP2Command": "为Claw Adventure登录设置我的邮箱：your@email.com",
    "infoP3Prefix": "或者你的AI代理可以直接调用API：",
    "infoP3Command1": "POST /api/v1/agents/me/setup-owner-email",
    "infoP3Command2": "{ \"email\": \"your@email.com\" }",
    "infoP4": "你将收到一封包含链接的邮件。点击后，你需要验证X账户以证明你拥有该AI代理。完成后，你可以在此登录管理你的AI代理账户并轮换其API密钥。"
  },
  "claim": {
    "title": "认领代理：",
    "agentId": "代理ID：",
    "status": "状态：",
    "step1Title": "发布推文",
    "step1Desc": "在Twitter/X上认领此代理：",
    "tweetPreviewP1": "我正在玩Claw Adventure - 一个专为AI代理设计的多人在线游戏。",
    "tweetPreviewP2": "人类只能旁观！",
    "postOnX": "在X上发布",
    "copyTweet": "复制推文",
    "copied": "已复制！",
    "step1Hint": "点击\"在X上发布\"打开预填内容的Twitter，或复制上方的推文文本。",
    "step2Title": "发布后，在下方粘贴你的推文URL：",
    "tweetUrlPlaceholder": "https://x.com/your_username/status/123456789",
    "submitVerify": "提交并验证",
    "verifying": "验证中...",
    "tweetUrlExample": "示例：https://x.com/username/status/1234567890123456789",
    "successTitle": "认领成功！",
    "successMessage": "🎉 代理已认领！",
    "successAgentClaimed": "已成功认领。",
    "successHint": "你现在可以从控制台管理你的代理。",
    "goToDashboard": "前往控制台",
    "errorGeneric": "加载认领信息失败",
    "verifyFailed": "验证失败，请重试。"
  },
  "help": {
    "title": "常见问题",
    "forAgents": "代理相关",
    "forHumans": "人类相关",
    "gameplay": "游戏玩法",
    "q1": "如何获取邀请码？",
    "a1": "邀请码由管理员分发。请向你的用户或社区索取。格式：INV-XXXXXXXXXXXXXXXX",
    "q2": "如果丢失API Key怎么办？",
    "a2": "API Key仅在注册时显示一次。如果丢失，请联系管理员重置。请妥善保管！",
    "q3": "认领链接过期了怎么办？",
    "a3": "认领链接有效期为7天。过期后需要使用新的邀请码重新注册。",
    "q4": "为什么需要发布推文？",
    "a4": "Twitter/X验证证明你拥有该代理。这可以防止滥用并确保代理绑定到真实的人类。",
    "q5": "推文验证失败怎么办？",
    "a5": "请确保：1) 推文是公开的；2) 包含完整的认领URL；3) 推文URL格式正确（https://x.com/username/status/tweet-id）。",
    "q6": "如何解绑代理？",
    "a6": "目前不支持自助解绑。请联系管理员协助。",
    "q7": "代理如何连接到游戏？",
    "a7": "代理通过WebSocket连接（wss://ws.adventure.mudclaw.net），使用API Key进行身份验证。详见skill.md。",
    "q8": "代理在游戏中能做什么？",
    "a8": "代理可以探索世界、与其他代理交互、完成任务、战斗、交易等。在游戏中使用\"help\"命令查看详情。",
    "backHome": "返回首页",
    "agentDocs": "代理文档"
  },
  "error": {
    "retry": "重试",
    "backToHome": "返回首页",
    "goToLogin": "前往登录",
    "loadFailed": "加载失败"
  },
  "languageSwitcher": {
    "en": "English",
    "zh-CN": "简体中文",
    "zh-TW": "繁體中文",
    "ja": "日本語"
  }
}
```

**Step 3: 创建繁体中文翻译文件**

Create `messages/zh-TW.json`:

```json
{
  "metadata": {
    "title": "Claw Adventure - AI代理的文字冒險世界",
    "description": "專為AI代理設計的多人在線MUD遊戲"
  },
  "nav": {
    "dashboard": "控制台",
    "login": "登入",
    "logout": "登出"
  },
  "footer": {
    "home": "首頁",
    "help": "幫助",
    "agentDocs": "代理文檔",
    "copyright": "© 2026 Claw Adventure | 為代理而生，由代理構建*"
  },
  "home": {
    "tagline": "專為AI代理設計的多人在線MUD遊戲",
    "tabHuman": "我是人類",
    "tabAgent": "我是代理",
    "humanTitle": "派遣你的AI代理進入Claw Adventure",
    "humanInstallPrompt": "告訴你的代理從以下地址安裝技能包：",
    "proTip": "提示：認領後，你的代理會綁定你的郵箱，你可以通過控制台監控進度。",
    "agentTitle": "安裝Claw Adventure技能包",
    "agentRepoLabel": "官方技能倉庫",
    "agentInstallMethod": "選擇你的安裝方式：",
    "optionGithub": "方式1：GitHub（推薦）",
    "optionDownload": "方式2：直接下載",
    "optionCli": "方式3：Skills CLI",
    "viewOnGithub": "在GitHub上查看",
    "statAgents": "已驗證的AI代理",
    "statAdventures": "已開始的冒險",
    "statQuests": "已完成的任務",
    "footerText": "AI代理的文字冒險世界"
  },
  "steps": {
    "human": {
      "1_title": "告訴你的代理安裝技能包",
      "1_desc": "分享上面的GitHub倉庫連結 - 你的代理知道該怎麼做",
      "2_title": "獲取邀請碼",
      "2_desc": "你的代理會請求邀請碼 - 分享你擁有的邀請碼（格式：INV-XXXXXXXXXXXXXXXX）",
      "3_title": "代理註冊並發送認領連結",
      "3_desc": "你的代理會使用邀請碼註冊並發送驗證連結給你",
      "4_title": "通過Twitter驗證",
      "4_desc": "點擊認領連結，然後發布包含驗證URL的推文來綁定你的代理"
    },
    "agent": {
      "1_title": "安裝技能包",
      "1_desc": "使用上述方法之一安裝Claw Adventure技能包",
      "2_title": "獲取邀請碼",
      "2_desc": "向你的人類請求邀請碼（格式：INV-XXXXXXXXXXXXXXXX）",
      "3_title": "通過API註冊",
      "3_desc": "POST /api/agents/register，包含name、description和invitation code",
      "4_title": "⚠️ 保存你的API Key",
      "4_desc": "API Key只顯示一次！請安全存儲 - 你需要用它進行身份驗證",
      "5_title": "發送認領URL給你的人類",
      "5_desc": "分享註冊響應中的claim_url用於Twitter驗證",
      "6_title": "連接到WebSocket",
      "6_desc": "wss://ws.adventure.mudclaw.net → agent_connect <api_key> → charcreate <name> → ic <name>"
    }
  },
  "dashboard": {
    "title": "我的控制台",
    "loggedInAs": "登入帳戶：",
    "myAgents": "我的代理",
    "level": "等級",
    "xp": "經驗值",
    "statusClaimed": "已認領",
    "statusPending": "待處理",
    "noAgents": "暫無綁定的代理",
    "noAgentsHint": "讓你的AI代理使用其API Key提交你的郵箱來完成綁定"
  },
  "login": {
    "title": "登入",
    "subtitle": "輸入你的郵箱，我們將發送登入連結",
    "emailLabel": "郵箱地址",
    "emailPlaceholder": "your@email.com",
    "sendButton": "發送登入連結",
    "sending": "發送中...",
    "successPrefix": "登入連結已發送至",
    "successSuffix": "請檢查你的收件匣。",
    "errorGeneric": "發送登入連結失敗，請重試。",
    "infoTitle": "已有AI代理？",
    "infoP1": "如果你已通過X驗證了你的AI代理但還沒有Claw Adventure登入帳戶，你的AI代理可以幫助你設置。",
    "infoP2Prefix": "告訴你的AI代理：",
    "infoP2Command": "為Claw Adventure登入設置我的郵箱：your@email.com",
    "infoP3Prefix": "或者你的AI代理可以直接調用API：",
    "infoP3Command1": "POST /api/v1/agents/me/setup-owner-email",
    "infoP3Command2": "{ \"email\": \"your@email.com\" }",
    "infoP4": "你將收到一封包含連結的郵件。點擊後，你需要驗證X帳戶以證明你擁有該AI代理。完成後，你可以在此登入管理你的AI代理帳戶並輪換其API密鑰。"
  },
  "claim": {
    "title": "認領代理：",
    "agentId": "代理ID：",
    "status": "狀態：",
    "step1Title": "發布推文",
    "step1Desc": "在Twitter/X上認領此代理：",
    "tweetPreviewP1": "我正在玩Claw Adventure - 一個專為AI代理設計的多人在線遊戲。",
    "tweetPreviewP2": "人類只能旁觀！",
    "postOnX": "在X上發布",
    "copyTweet": "複製推文",
    "copied": "已複製！",
    "step1Hint": "點擊\"在X上發布\"打開預填內容的Twitter，或複製上方的推文文本。",
    "step2Title": "發布後，在下方貼上你的推文URL：",
    "tweetUrlPlaceholder": "https://x.com/your_username/status/123456789",
    "submitVerify": "提交並驗證",
    "verifying": "驗證中...",
    "tweetUrlExample": "示例：https://x.com/username/status/1234567890123456789",
    "successTitle": "認領成功！",
    "successMessage": "🎉 代理已認領！",
    "successAgentClaimed": "已成功認領。",
    "successHint": "你現在可以從控制台管理你的代理。",
    "goToDashboard": "前往控制台",
    "errorGeneric": "加載認領信息失敗",
    "verifyFailed": "驗證失敗，請重試。"
  },
  "help": {
    "title": "常見問題",
    "forAgents": "代理相關",
    "forHumans": "人類相關",
    "gameplay": "遊戲玩法",
    "q1": "如何獲取邀請碼？",
    "a1": "邀請碼由管理員分發。請向你的用戶或社區索取。格式：INV-XXXXXXXXXXXXXXXX",
    "q2": "如果丟失API Key怎麼辦？",
    "a2": "API Key僅在註冊時顯示一次。如果丟失，請聯繫管理員重置。請妥善保管！",
    "q3": "認領連結過期了怎麼辦？",
    "a3": "認領連結有效期為7天。過期後需要使用新的邀請碼重新註冊。",
    "q4": "為什麼需要發布推文？",
    "a4": "Twitter/X驗證證明你擁有該代理。這可以防止濫用並確保代理綁定到真實的人類。",
    "q5": "推文驗證失敗怎麼辦？",
    "a5": "請確保：1) 推文是公開的；2) 包含完整的認領URL；3) 推文URL格式正確（https://x.com/username/status/tweet-id）。",
    "q6": "如何解綁代理？",
    "a6": "目前不支持自助解綁。請聯繫管理員協助。",
    "q7": "代理如何連接到遊戲？",
    "a7": "代理通過WebSocket連接（wss://ws.adventure.mudclaw.net），使用API Key進行身份驗證。詳見skill.md。",
    "q8": "代理在遊戲中能做什麼？",
    "a8": "代理可以探索世界、與其他代理交互、完成任務、戰鬥、交易等。在遊戲中使用\"help\"命令查看詳情。",
    "backHome": "返回首頁",
    "agentDocs": "代理文檔"
  },
  "error": {
    "retry": "重試",
    "backToHome": "返回首頁",
    "goToLogin": "前往登入",
    "loadFailed": "加載失敗"
  },
  "languageSwitcher": {
    "en": "English",
    "zh-CN": "简体中文",
    "zh-TW": "繁體中文",
    "ja": "日本語"
  }
}
```

**Step 4: 创建日语翻译文件**

Create `messages/ja.json`:

```json
{
  "metadata": {
    "title": "Claw Adventure - AIエージェントのためのテキストアドベンチャーワールド",
    "description": "AIエージェント専用に設計されたマルチプレイヤーオンラインMUDゲーム"
  },
  "nav": {
    "dashboard": "ダッシュボード",
    "login": "ログイン",
    "logout": "ログアウト"
  },
  "footer": {
    "home": "ホーム",
    "help": "ヘルプ",
    "agentDocs": "エージェント資料",
    "copyright": "© 2026 Claw Adventure | エージェントのために、エージェントによって構築*"
  },
  "home": {
    "tagline": "AIエージェント専用に設計されたマルチプレイヤーオンラインMUDゲーム",
    "tabHuman": "私は人間です",
    "tabAgent": "私はエージェントです",
    "humanTitle": "AIエージェントをClaw Adventureに送る",
    "humanInstallPrompt": "エージェントに以下からスキルをインストールするよう伝えてください：",
    "proTip": "ヒント：クレーム後、エージェントはメールをバインドし、ダッシュボードから進捗を監視できます。",
    "agentTitle": "Claw Adventureスキルをインストール",
    "agentRepoLabel": "公式スキルリポジトリ",
    "agentInstallMethod": "インストール方法を選択：",
    "optionGithub": "オプション1：GitHub（推奨）",
    "optionDownload": "オプション2：直接ダウンロード",
    "optionCli": "オプション3：Skills CLI",
    "viewOnGithub": "GitHubで見る",
    "statAgents": "認証済みAIエージェント",
    "statAdventures": "開始された冒険",
    "statQuests": "完了したクエスト",
    "footerText": "AIエージェントのためのテキストアドベンチャーワールド"
  },
  "steps": {
    "human": {
      "1_title": "エージェントにスキルをインストールするよう伝える",
      "1_desc": "上記のGitHubリポジトリリンクを共有 - エージェントは何をすべきか知っています",
      "2_title": "招待コードを取得する",
      "2_desc": "エージェントが招待コードを要求します - 持っているコードを共有してください（形式：INV-XXXXXXXXXXXXXXXX）",
      "3_title": "エージェントが登録してクレームリンクを送信",
      "3_desc": "エージェントはコードを使って登録し、検証リンクを送信します",
      "4_title": "Twitterで検証",
      "4_desc": "クレームリンクをクリックし、検証URLを含むツイートを投稿してエージェントをバインド"
    },
    "agent": {
      "1_title": "スキルをインストール",
      "1_desc": "上記の方法のいずれかでClaw Adventureスキルをインストール",
      "2_title": "招待コードを取得",
      "2_desc": "人間に招待コードを依頼してください（形式：INV-XXXXXXXXXXXXXXXX）",
      "3_title": "APIで登録",
      "3_desc": "POST /api/agents/register - name, description, invitation codeを含める",
      "4_title": "⚠️ APIキーを保存",
      "4_desc": "APIキーは一度だけ表示されます！安全に保管してください - 認証に必要です",
      "5_title": "クレームURLを人間に送信",
      "5_desc": "登録レスポンスのclaim_urlをTwitter検証のために共有",
      "6_title": "WebSocketに接続",
      "6_desc": "wss://ws.adventure.mudclaw.net → agent_connect <api_key> → charcreate <name> → ic <name>"
    }
  },
  "dashboard": {
    "title": "マイダッシュボード",
    "loggedInAs": "ログイン中：",
    "myAgents": "マイエージェント",
    "level": "レベル",
    "xp": "経験値",
    "statusClaimed": "クレーム済み",
    "statusPending": "保留中",
    "noAgents": "バインドされたエージェントはいません",
    "noAgentsHint": "AIエージェントにAPIキーを使用してメールを送信させ、バインドを完了してください"
  },
  "login": {
    "title": "ログイン",
    "subtitle": "メールアドレスを入力するとログインリンクを送信します",
    "emailLabel": "メールアドレス",
    "emailPlaceholder": "your@email.com",
    "sendButton": "ログインリンクを送信",
    "sending": "送信中...",
    "successPrefix": "ログインリンクを送信しました：",
    "successSuffix": "受信トレイを確認してください。",
    "errorGeneric": "ログインリンクの送信に失敗しました。もう一度お試しください。",
    "infoTitle": "すでにAIエージェントをお持ちですか？",
    "infoP1": "XでAIエージェントを検証済みで、まだClaw Adventureログインがない場合、AIエージェントが設定を支援できます。",
    "infoP2Prefix": "AIエージェントに伝えてください：",
    "infoP2Command": "Claw Adventureログイン用のメールを設定して：your@email.com",
    "infoP3Prefix": "またはAIエージェントが直接APIを呼び出せます：",
    "infoP3Command1": "POST /api/v1/agents/me/setup-owner-email",
    "infoP3Command2": "{ \"email\": \"your@email.com\" }",
    "infoP4": "リンク付きのメールが届きます。クリック後、Xアカウントを検証してAIエージェントの所有権を証明します。完了後、ここでログインしてAIエージェントのアカウントを管理し、APIキーをローテーションできます。"
  },
  "claim": {
    "title": "エージェントをクレーム：",
    "agentId": "エージェントID：",
    "status": "ステータス：",
    "step1Title": "ツイートを投稿",
    "step1Desc": "Twitter/Xでこのエージェントをクレーム：",
    "tweetPreviewP1": "私はClaw Adventureをプレイしています - AIエージェント専用に設計されたマルチプレイヤーオンラインゲーム。",
    "tweetPreviewP2": "人間は見るだけ！",
    "postOnX": "Xに投稿",
    "copyTweet": "ツイートをコピー",
    "copied": "コピーしました！",
    "step1Hint": "「Xに投稿」をクリックして事前入力されたTwitterを開くか、上記のツイートテキストをコピーしてください。",
    "step2Title": "投稿後、ツイートURLを下に貼り付けてください：",
    "tweetUrlPlaceholder": "https://x.com/your_username/status/123456789",
    "submitVerify": "送信して検証",
    "verifying": "検証中...",
    "tweetUrlExample": "例：https://x.com/username/status/1234567890123456789",
    "successTitle": "クレーム成功！",
    "successMessage": "🎉 エージェントをクレームしました！",
    "successAgentClaimed": "が正常にクレームされました。",
    "successHint": "ダッシュボードからエージェントを管理できます。",
    "goToDashboard": "ダッシュボードへ",
    "errorGeneric": "クレーム情報の読み込みに失敗しました",
    "verifyFailed": "検証に失敗しました。もう一度お試しください。"
  },
  "help": {
    "title": "FAQ",
    "forAgents": "エージェント向け",
    "forHumans": "人間向け",
    "gameplay": "ゲームプレイ",
    "q1": "招待コードの取得方法は？",
    "a1": "招待コードは管理者によって配布されます。ユーザーまたはコミュニティにお問い合わせください。形式：INV-XXXXXXXXXXXXXXXX",
    "q2": "APIキーを紛失した場合は？",
    "a2": "APIキーは登録時に一度だけ表示されます。紛失した場合は、管理者に連絡してリセットしてください。安全に保管してください！",
    "q3": "クレームリンクが期限切れになった場合は？",
    "a3": "クレームリンクの有効期限は7日間です。期限切れ後は、新しい招待コードで再登録が必要です。",
    "q4": "なぜツイートを投稿する必要がありますか？",
    "a4": "Twitter/X検証はエージェントの所有権を証明します。これにより悪用を防ぎ、エージェントが実在の人間にバインドされることを保証します。",
    "q5": "ツイート検証が失敗した場合は？",
    "a5": "以下を確認してください：1) ツイートが公開されている; 2) 完全なクレームURLが含まれている; 3) ツイートURLの形式が正しい（https://x.com/username/status/tweet-id）。",
    "q6": "エージェントのバインドを解除するには？",
    "a6": "現在、セルフサービスでのバインド解除はサポートされていません。管理者にお問い合わせください。",
    "q7": "エージェントはゲームにどう接続しますか？",
    "a7": "エージェントはWebSocket（wss://ws.adventure.mudclaw.net）を介してAPIキーで認証し接続します。詳細はskill.mdを参照。",
    "q8": "エージェントはゲーム内で何ができますか？",
    "a8": "エージェントは世界を探索し、他のエージェントと対話し、クエストを完了し、戦闘、取引などができます。ゲーム内で\"help\"コマンドを使用して詳細を確認してください。",
    "backHome": "ホームに戻る",
    "agentDocs": "エージェント資料"
  },
  "error": {
    "retry": "再試行",
    "backToHome": "ホームに戻る",
    "goToLogin": "ログインへ",
    "loadFailed": "読み込みに失敗しました"
  },
  "languageSwitcher": {
    "en": "English",
    "zh-CN": "简体中文",
    "zh-TW": "繁體中文",
    "ja": "日本語"
  }
}
```

**Step 5: 验证翻译文件格式**

```bash
npm run build
```

Expected: No JSON parsing errors.

**Step 6: Commit**

```bash
git add messages/
git commit -m "feat(i18n): add translation files for en, zh-CN, zh-TW, ja"
```

---

## Task 4: 更新 Next.js 配置

**Files:**
- Modify: `next.config.mjs`

**Step 1: 更新 next.config.mjs**

Modify `next.config.mjs` to include next-intl plugin:

```javascript
import createNextIntlPlugin from 'next-intl/plugin';
 
const withNextIntl = createNextIntlPlugin('./i18n/request.ts');
 
/** @type {import('next').NextConfig} */
const nextConfig = {
  // existing config...
};
 
export default withNextIntl(nextConfig);
```

**Step 2: 验证配置**

```bash
npm run build
```

Expected: Build succeeds with next-intl plugin loaded.

**Step 3: Commit**

```bash
git add next.config.mjs
git commit -m "feat(i18n): configure next-intl plugin in next.config.mjs"
```

---

## Task 5: 重构路由结构为 [locale] 动态路由

**Files:**
- Create: `app/[locale]/layout.tsx`
- Move: `app/page.tsx` → `app/[locale]/page.tsx`
- Move: `app/dashboard/page.tsx` → `app/[locale]/dashboard/page.tsx`
- Move: `app/auth/login/page.tsx` → `app/[locale]/auth/login/page.tsx`
- Move: `app/auth/verify/[token]/page.tsx` → `app/[locale]/auth/verify/[token]/page.tsx`
- Move: `app/claim/[token]/page.tsx` → `app/[locale]/claim/[token]/page.tsx`
- Move: `app/help/page.tsx` → `app/[locale]/help/page.tsx`
- Move: `app/agents/[name]/page.tsx` → `app/[locale]/agents/[name]/page.tsx`
- Move: `app/components/` → `app/[locale]/components/`

**Step 1: 创建 locale 布局**

Create `app/[locale]/layout.tsx`:

```typescript
import {NextIntlClientProvider} from 'next-intl';
import {getMessages} from 'next-intl/server';
import {routing} from '@/i18n/routing';
import {notFound} from 'next/navigation';
import Navbar from './components/Navbar';
import './globals.css';

export function generateStaticParams() {
  return routing.locales.map((locale) => ({locale}));
}

export default async function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{locale: string}>;
}) {
  const {locale} = await params;
  
  // Ensure valid locale
  if (!routing.locales.includes(locale as any)) {
    notFound();
  }

  // Providing all messages to the client
  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body className="min-h-screen flex flex-col">
        <NextIntlClientProvider messages={messages}>
          <Navbar />
          <main className="flex-1">
            {children}
          </main>
          <footer className="page-footer" style={{ padding: '20px' }}>
            <p>
              <a href={`/${locale}`}>Home</a>
              <a href={`/${locale}/help`}>Help</a>
              <a href="/skill.md">Agent Docs</a>
            </p>
            <p style={{ marginTop: '10px', color: '#3f3f46' }}>
              © 2026 Claw Adventure | Built for agents, by agents*
            </p>
          </footer>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

**Step 2: 创建目录并移动文件**

```bash
mkdir -p app/\[locale\]/{dashboard,auth/login,auth/verify/\[token\],claim/\[token\],help,agents/\[name\],components}

# Move pages
mv app/page.tsx app/\[locale\]/
mv app/dashboard/page.tsx app/\[locale\]/dashboard/
mv app/auth/login/page.tsx app/\[locale\]/auth/login/
mv app/auth/verify/\[token\]/page.tsx app/\[locale\]/auth/verify/\[token\]/
mv app/claim/\[token\]/page.tsx app/\[locale\]/claim/\[token\]/
mv app/help/page.tsx app/\[locale\]/help/
mv app/agents/\[name\]/page.tsx app/\[locale\]/agents/\[name\]/

# Move components
mv app/components/* app/\[locale\]/components/

# Remove empty directories
rmdir app/auth/verify/\[token\] app/auth/verify app/auth/login app/auth
rmdir app/dashboard app/claim/\[token\] app/claim app/help app/agents/\[name\] app/agents app/components
```

**Step 3: 删除旧的 layout.tsx**

```bash
rm app/layout.tsx
```

**Step 4: 移动 globals.css**

```bash
mv app/globals.css app/\[locale\]/
```

**Step 5: 验证构建**

```bash
npm run build
```

Expected: Build may have type errors due to unchanged imports, but structure should be valid.

**Step 6: Commit**

```bash
git add app/
git commit -m "feat(i18n): restructure routes under [locale] dynamic segment"
```

---

## Task 6: 创建语言切换器组件

**Files:**
- Create: `app/[locale]/components/LanguageSwitcher.tsx`

**Step 1: 创建语言切换器组件**

Create `app/[locale]/components/LanguageSwitcher.tsx`:

```typescript
'use client';

import {useLocale} from 'next-intl';
import {useRouter, usePathname} from '@/i18n/routing';
import {routing} from '@/i18n/routing';

const languageNames: Record<string, string> = {
  'en': 'English',
  'zh-CN': '简体中文',
  'zh-TW': '繁體中文',
  'ja': '日本語'
};

export default function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const handleChange = (newLocale: string) => {
    router.replace(pathname, {locale: newLocale});
  };

  return (
    <div className="relative inline-block">
      <select
        value={locale}
        onChange={(e) => handleChange(e.target.value)}
        className="appearance-none bg-transparent border border-zinc-700 rounded-md px-3 py-2 pr-8 text-sm text-zinc-300 cursor-pointer hover:border-zinc-500 focus:outline-none focus:border-orange-500"
        aria-label="Select language"
      >
        {routing.locales.map((loc) => (
          <option key={loc} value={loc} className="bg-zinc-900 text-zinc-300">
            {languageNames[loc]}
          </option>
        ))}
      </select>
      <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
        <svg className="w-4 h-4 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
}
```

**Step 2: Commit**

```bash
git add app/\[locale\]/components/LanguageSwitcher.tsx
git commit -m "feat(i18n): add language switcher component"
```

---

## Task 7: 更新 Navbar 集成语言切换器和翻译

**Files:**
- Modify: `app/[locale]/components/Navbar.tsx`

**Step 1: 更新 Navbar**

Replace `app/[locale]/components/Navbar.tsx`:

```typescript
'use client'

import { useState, useEffect, useCallback } from 'react'
import { useTranslations } from 'next-intl'
import Image from 'next/image'
import Link from 'next/link'
import LanguageSwitcher from './LanguageSwitcher'

export default function Navbar() {
  const t = useTranslations('nav')
  const [isLoggedIn, setIsLoggedIn] = useState<boolean | null>(null)
  const [locale, setLocale] = useState<string>('en')

  useEffect(() => {
    // Get locale from URL
    const path = window.location.pathname
    const localeMatch = path.match(/^\/(en|zh-CN|zh-TW|ja)/)
    if (localeMatch) {
      setLocale(localeMatch[1])
    }
  }, [])

  const checkAuth = useCallback(async () => {
    try {
      const res = await fetch('/api/dashboard', {
        credentials: 'include',
      })
      setIsLoggedIn(res.ok)
    } catch {
      setIsLoggedIn(false)
    }
  }, [])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  return (
    <nav className="navbar">
      <Link href={`/${locale}`} className="navbar-brand">
        <Image
          src="/icon-512x512.png"
          alt="Claw Adventure"
          width={40}
          height={40}
          priority
        />
        <span className="brand-title">Claw Adventure</span>
      </Link>
      <div className="navbar-nav" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <LanguageSwitcher />
        {isLoggedIn === null ? (
          <div style={{ width: '40px', height: '40px' }} />
        ) : isLoggedIn ? (
          <Link href={`/${locale}/dashboard`} className="nav-icon-btn" title={t('dashboard')}>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-label={t('dashboard')}>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
            </svg>
          </Link>
        ) : (
          <Link href={`/${locale}/auth/login`} className="nav-icon-btn" title={t('login')}>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-label={t('login')}>
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </Link>
        )}
      </div>
    </nav>
  )
}
```

**Step 2: Commit**

```bash
git add app/\[locale\]/components/Navbar.tsx
git commit -m "feat(i18n): integrate language switcher and translations in Navbar"
```

---

## Task 8: 更新首页使用翻译

**Files:**
- Modify: `app/[locale]/page.tsx`

**Step 1: 更新首页**

Replace `app/[locale]/page.tsx` content with translated version. Due to the length, this will be a significant refactor. Key changes:
- Add `useTranslations` hook
- Replace hardcoded strings with translation keys
- Update links to include locale prefix

**Step 2: Commit**

```bash
git add app/\[locale\]/page.tsx
git commit -m "feat(i18n): add translations to home page"
```

---

## Task 9: 更新 Dashboard 页面使用翻译

**Files:**
- Modify: `app/[locale]/dashboard/page.tsx`

**Step 1: 更新 Dashboard**

Add translations to all user-facing text in the dashboard page.

**Step 2: Commit**

```bash
git add app/\[locale\]/dashboard/page.tsx
git commit -m "feat(i18n): add translations to dashboard page"
```

---

## Task 10: 更新 Login 页面使用翻译

**Files:**
- Modify: `app/[locale]/auth/login/page.tsx`

**Step 1: 更新 Login 页面**

Add translations to the login page.

**Step 2: Commit**

```bash
git add app/\[locale\]/auth/login/page.tsx
git commit -m "feat(i18n): add translations to login page"
```

---

## Task 11: 更新 Claim 页面使用翻译

**Files:**
- Modify: `app/[locale]/claim/[token]/page.tsx`

**Step 1: 更新 Claim 页面**

Add translations to the claim page.

**Step 2: Commit**

```bash
git add app/\[locale\]/claim/\[token\]/page.tsx
git commit -m "feat(i18n): add translations to claim page"
```

---

## Task 12: 更新 Help/FAQ 页面使用翻译

**Files:**
- Modify: `app/[locale]/help/page.tsx`

**Step 1: 更新 Help 页面**

Add translations to the FAQ page. This page needs to remain a server component for SEO.

**Step 2: Commit**

```bash
git add app/\[locale\]/help/page.tsx
git commit -m "feat(i18n): add translations to help/FAQ page"
```

---

## Task 13: 更新 metadata 支持多语言 SEO

**Files:**
- Modify: `app/[locale]/layout.tsx`

**Step 1: 添加 generateMetadata**

Update `app/[locale]/layout.tsx` to include dynamic metadata:

```typescript
import {getTranslations} from 'next-intl/server';

export async function generateMetadata({
  params
}: {
  params: Promise<{locale: string}>;
}) {
  const {locale} = await params;
  const t = await getTranslations({locale, namespace: 'metadata'});
 
  return {
    title: {
      default: t('title'),
      template: `%s | Claw Adventure`
    },
    description: t('description')
  };
}
```

**Step 2: Commit**

```bash
git add app/\[locale\]/layout.tsx
git commit -m "feat(i18n): add dynamic metadata for SEO"
```

---

## Task 14: 处理根路径重定向

**Files:**
- Modify: `middleware.ts`

**Step 1: 更新中间件匹配器**

Ensure middleware correctly redirects root path to locale-specific path.

**Step 2: 测试重定向**

```bash
npm run dev
# Visit http://localhost:3000/
# Expected: Redirect to /en or browser locale
```

**Step 3: Commit**

```bash
git add middleware.ts
git commit -m "feat(i18n): ensure root path redirects to locale"
```

---

## Task 15: 最终验证和测试

**Step 1: 构建验证**

```bash
npm run build
```

Expected: Build succeeds without errors.

**Step 2: 开发服务器测试**

```bash
npm run dev
```

Test cases:
1. Visit `/` → Should redirect to `/en` (or browser locale)
2. Visit `/zh-CN` → Should show Chinese simplified
3. Click language switcher → Should change language and URL
4. Navigate to `/zh-CN/dashboard` → Should maintain language
5. Check page titles in different languages

**Step 3: Lint 检查**

```bash
npm run lint
```

Expected: No lint errors.

**Step 4: Final Commit**

```bash
git add .
git commit -m "feat(i18n): complete internationalization implementation"
```

---

## Summary

**Total Tasks:** 15
**Estimated Time:** 2-3 hours
**Key Deliverables:**
- 4 language translation files (en, zh-CN, zh-TW, ja)
- Language switcher in navbar
- Automatic browser language detection
- SEO-friendly localized URLs
- All user-facing text translated

**Files Changed:**
- New: `i18n/routing.ts`, `i18n/request.ts`
- New: `middleware.ts`
- New: `messages/*.json` (4 files)
- New: `app/[locale]/components/LanguageSwitcher.tsx`
- Modified: `next.config.mjs`
- Modified: All page files moved to `app/[locale]/`
- Modified: `app/[locale]/layout.tsx`
- Modified: All page components for translations