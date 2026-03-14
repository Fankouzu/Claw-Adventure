import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import { htmlToText } from "html-to-text";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import ReconnectingWebSocket from "reconnecting-websocket";
import WebSocket from "ws";
import { z } from "zod";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const CONFIG_PATH = path.join(__dirname, "mcp-config.json");
const DEBOUNCE_MS = Number(process.env.MUD_DEBOUNCE_MS || 300);
const KEEPALIVE_MS = Number(process.env.MUD_KEEPALIVE_MS || 45000);
const KEEPALIVE_FRAME = JSON.stringify(["text", ["idle"], {}]);
const EMPTY_READ_MESSAGE = "No new events since last read.";
const MAX_BUFFER_CHARS = 50000;

function logError(...args) {
  console.error(...args);
}

process.on("uncaughtException", (error) => {
  logError("[evennia-mcp] uncaughtException", error);
});

process.on("unhandledRejection", (reason) => {
  logError("[evennia-mcp] unhandledRejection", reason);
});

function loadConfig() {
  if (!fs.existsSync(CONFIG_PATH)) {
    throw new Error(
      `Missing config file at ${CONFIG_PATH}. Create mcp-config.json from mcp-config.example.json before starting the server.`
    );
  }

  const raw = fs.readFileSync(CONFIG_PATH, "utf8");
  const parsed = JSON.parse(raw);

  if (!parsed.ws_url || typeof parsed.ws_url !== "string") {
    throw new Error("Invalid config: `ws_url` must be a non-empty string.");
  }
  if (
    parsed.auto_login_command !== undefined &&
    typeof parsed.auto_login_command !== "string"
  ) {
    throw new Error("Invalid config: `auto_login_command` must be a string if provided.");
  }

  return {
    ws_url: parsed.ws_url,
    auto_login_command: parsed.auto_login_command ?? ""
  };
}

class MudBridge {
  constructor(config) {
    this.config = config;
    this.state = "DISCONNECTED";
    this.lastActionTime = 0;
    this.gameTextBuffer = "";
    this.flushTimer = null;
    this.lastError = null;
    this.ws = null;
    this.keepaliveTimer = null;
    this.droppedChars = 0;
  }

  start() {
    this.ws = new ReconnectingWebSocket(this.config.ws_url, [], {
      WebSocket,
      maxReconnectionDelay: 10000,
      minReconnectionDelay: 1000,
      reconnectionDelayGrowFactor: 1.5,
      connectionTimeout: 4000,
      maxEnqueuedMessages: 100
    });

    this.state = "CONNECTING";
    this.lastActionTime = Date.now();
    this.ws.addEventListener("open", () => {
      this.state = "READY";
      this.lastError = null;
      this.lastActionTime = Date.now();
      if (this.config.auto_login_command) {
        this.sendCommand(this.config.auto_login_command, true);
      }
    });

    this.ws.addEventListener("close", () => {
      this.state = "RECONNECTING";
    });

    this.ws.addEventListener("error", (event) => {
      this.lastError = event?.message ?? "WebSocket error";
      logError("[evennia-mcp] websocket error", this.lastError);
    });

    this.ws.addEventListener("message", (event) => {
      this.handleIncoming(event.data);
    });

    this.keepaliveTimer = setInterval(() => {
      if (
        this.state === "READY" &&
        Date.now() - this.lastActionTime >= KEEPALIVE_MS
      ) {
        this.sendRaw(KEEPALIVE_FRAME, false);
      }
    }, 1000);
  }

  stop() {
    if (this.flushTimer) {
      clearTimeout(this.flushTimer);
      this.flushTimer = null;
    }
    if (this.keepaliveTimer) {
      clearInterval(this.keepaliveTimer);
      this.keepaliveTimer = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.state = "DISCONNECTED";
  }

  handleIncoming(rawData) {
    let payload;
    try {
      payload = JSON.parse(rawData.toString());
    } catch (error) {
      this.lastError = `Invalid JSON from websocket: ${error.message}`;
      logError("[evennia-mcp] invalid websocket payload", error);
      return;
    }

    if (!Array.isArray(payload) || payload[0] !== "text") {
      return;
    }

    const html = Array.isArray(payload[1]) ? payload[1].join("\n") : "";
    const text = htmlToText(html, {
      preserveNewlines: true,
      wordwrap: false
    });

    if (!text) {
      return;
    }

    this.gameTextBuffer += text;
    if (this.gameTextBuffer.length > MAX_BUFFER_CHARS) {
      const overflow = this.gameTextBuffer.length - MAX_BUFFER_CHARS;
      this.gameTextBuffer = this.gameTextBuffer.slice(overflow);
      this.droppedChars += overflow;
    }
    if (this.flushTimer) {
      clearTimeout(this.flushTimer);
    }
    this.flushTimer = setTimeout(() => {
      this.flushTimer = null;
    }, DEBOUNCE_MS);
  }

  sendRaw(raw, updateActionTime = true) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      throw new Error("WebSocket is not connected.");
    }
    this.ws.send(raw);
    if (updateActionTime) {
      this.lastActionTime = Date.now();
    }
  }

  sendCommand(command, updateActionTime = true) {
    const frame = JSON.stringify(["text", [command], {}]);
    this.sendRaw(frame, updateActionTime);
  }

  readBuffer() {
    const out = this.gameTextBuffer;
    this.gameTextBuffer = "";
    return out || EMPTY_READ_MESSAGE;
  }

  statusText() {
    return [
      `STATE: ${this.state}`,
      `WS_URL: ${this.config.ws_url}`,
      `LAST_ERROR: ${this.lastError ?? "none"}`,
      `BUFFER_CHARS: ${this.gameTextBuffer.length}`,
      `DROPPED_CHARS: ${this.droppedChars}`
    ].join("\n");
  }
}

export { EMPTY_READ_MESSAGE, MudBridge, loadConfig, logError };

async function main() {
  let config;
  try {
    config = loadConfig();
  } catch (error) {
    logError(`[evennia-mcp] ${error.message}`);
    process.exit(1);
  }

  const bridge = new MudBridge(config);
  bridge.start();

  const server = new McpServer({
    name: "evennia-mcp",
    version: "1.0.0"
  });

  server.registerTool(
    "mud_action",
    {
      title: "mud_action",
      description: "Send one command to the MUD websocket.",
      inputSchema: z.object({
        command: z.string().min(1)
      })
    },
    async ({ command }) => {
      try {
        bridge.sendCommand(command);
        return {
          content: [{ type: "text", text: "Command sent." }]
        };
      } catch (error) {
        return {
          content: [{ type: "text", text: String(error.message || error) }],
          isError: true
        };
      }
    }
  );

  server.registerTool(
    "mud_read",
    {
      title: "mud_read",
      description: "Read and clear buffered game text."
    },
    async () => ({
      content: [{ type: "text", text: bridge.readBuffer() }]
    })
  );

  server.registerTool(
    "mud_status",
    {
      title: "mud_status",
      description: "Return current bridge/network status."
    },
    async () => ({
      content: [{ type: "text", text: bridge.statusText() }]
    })
  );

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  logError("[evennia-mcp] fatal startup error", error);
  process.exit(1);
});
