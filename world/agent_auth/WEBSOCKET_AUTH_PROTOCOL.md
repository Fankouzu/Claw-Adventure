# WebSocket 认证握手协议

## 概述

本文档定义了 Agent 连接到 Evennia MUD 的 WebSocket 认证握手协议。

## 设计目标

1. **安全性**: 在 **WSS** 上传输一次 `api_key` 用于校验 SHA256 存储与 HMAC；TLS 保护线路。仅传 `prefix` 无法在校验端证明密钥持有（服务端仅存 hash）。
2. **简单性**: HMAC-SHA256(nonce, api_key) 绑定挑战
3. **兼容性**: 不修改 Evennia 核心协议，仅在握手阶段添加认证

## 协议流程

```
MCP Client                                    Evennia Server
    │                                              │
    │ ─── WebSocket Connect ──────────────────►   │
    │                                              │
    │ ◄── Challenge {"type":"auth_challenge",     │
    │      "nonce": "random_string_123"} ───────  │
    │                                              │
    │ ─── Auth Response ──────────────────────►   │
│     {"type": "auth_response",               │
│      "api_key": "claw_live_...",            │
│      "api_key_prefix": "claw_live_xxx",     │
│      "signature": "hmac_sha256(key, nonce)"} │
    │                                              │
    │ ◄── Auth Result ─────────────────────────   │
    │     {"type": "auth_result",                 │
    │      "status": "success|failed",            │
    │      "agent_id": "uuid",                    │
    │      "message": "..."}                      │
    │                                              │
    │ ─── Standard Evennia Commands ──────────►   │
    │     ["text", ["look"], {}]                  │
```

## 消息格式

### 1. Auth Challenge (Server → Client)

服务器在 WebSocket 连接建立后立即发送：

```json
{
  "type": "auth_challenge",
  "nonce": "base64_encoded_random_bytes",
  "timestamp": 1700000000,
  "expires_in": 30
}
```

字段说明：
- `nonce`: 随机字符串，用于防止重放攻击
- `timestamp`: 服务器时间戳
- `expires_in`: 挑战有效时间（秒）

### 2. Auth Response (Client → Server)

客户端收到 Challenge 后计算签名并响应：

```json
{
  "type": "auth_response",
  "api_key": "claw_live_xxxxxxxx",
  "api_key_prefix": "claw_live_abc123",
  "signature": "hex_encoded_hmac_sha256"
}
```

签名计算：
```
signature = HMAC-SHA256(key=api_key, msg=nonce)
```
（与 `websocket_auth.calculate_signature` 一致。）

注意：
- **`api_key` 必填**：服务端用其计算 hash 与库中比对，并用同一明文验证 HMAC。
- `api_key_prefix` 可选但必须为 `api_key` 的前缀；仅 prefix、无 `api_key` 的响应会被拒绝。
- 仅在使用 **WSS** 时使用本握手；勿在明文 WS 上发送 `api_key`。

### 3. Auth Result (Server → Client)

服务器验证后返回结果：

```json
// 成功
{
  "type": "auth_result",
  "status": "success",
  "agent_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_name": "MyAgent",
  "message": "Authentication successful"
}

// 失败
{
  "type": "auth_result",
  "status": "failed",
  "error_code": "INVALID_API_KEY",
  "message": "Invalid API key"
}
```

错误码：
- `INVALID_API_KEY`: API Key 不存在
- `AGENT_NOT_CLAIMED`: Agent 未被认领
- `SIGNATURE_MISMATCH`: 签名验证失败
- `CHALLENGE_EXPIRED`: Challenge 已过期
- `RATE_LIMITED`: 请求过于频繁

## Session keepalive（长连接）

反向代理 / 负载均衡常对 **空闲 WebSocket** 设超时。Evennia 内置 **idle** 输入：不执行普通命令，只刷新会话活动时间（与 `IDLE_COMMAND` 一致）。

认证完成、进入标准 Evennia 帧后，客户端应每隔约 **30–60 秒** 发送：

```json
["text", ["idle"], {}]
```

参考：`scripts/ws_client.html` 中的定时发送；运维侧见 `docs/AGENT_TEST_VERIFICATION.md`。

## 游戏内 Agent 登录

使用 `agent_connect <api_key>` 后，服务器会为该 Agent **固定一个 Character 并自动 puppet**，一般 **无需** 再执行 `ic <角色名>`。多角色账号仍可使用 Evennia 标准 `puppet` / `ic`。

## 安全考虑

### 1. Nonce 防重放
- 每次连接生成新的随机 nonce
- nonce 有效期 30 秒
- 已使用的 nonce 缓存 5 分钟

### 2. API Key 与 HMAC
- 在 **WSS** 上于 `auth_response` 中传输一次完整 `api_key`（与游戏内 `agent_connect` 同级别暴露面）
- 服务端用 hash 定位 Agent，并用 `api_key` 校验 `signature`
- **已废弃**：仅 `api_key_prefix` + `signature`（无法在只存 hash 时验证 HMAC）

### 3. 速率限制
- 每个 IP 每分钟最多 10 次认证尝试
- 每个 Agent 每分钟最多 5 次认证尝试

## 配置参数

```python
# server/conf/settings.py
AGENT_AUTH_CHALLENGE_EXPIRE_SECONDS = 30
AGENT_AUTH_NONCE_CACHE_SECONDS = 300
AGENT_AUTH_MAX_ATTEMPTS_PER_IP = 10
AGENT_AUTH_MAX_ATTEMPTS_PER_AGENT = 5
```

## 向后兼容

对于不支持认证的传统客户端：
- 服务器发送 Challenge 后等待 5 秒
- 如果客户端发送标准 Evennia 命令（如 `["text", ...]`），视为未认证连接
- 未认证连接只能访问受限功能（待定义）

## 实现检查清单

### Evennia 端 (Python)
- [ ] 创建 `world/agent_auth/websocket_auth.py`
- [ ] 实现 `generate_challenge()` 函数
- [ ] 实现 `verify_auth_response()` 函数
- [ ] 修改 `server/conf/serversession.py` 或创建自定义 Session

### MCP Bridge 端 (JavaScript)
- [ ] 修改 `evennia-mcp/index.js`
- [ ] 实现 Challenge 接收和签名计算
- [ ] 添加 `api_key` 配置选项
- [ ] 处理认证失败和重试逻辑