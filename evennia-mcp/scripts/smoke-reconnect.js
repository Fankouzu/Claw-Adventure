import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const pkgDir = path.dirname(__dirname);
const configPath = path.join(pkgDir, 'mcp-config.json');

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function spawnMock(extraEnv = {}) {
  return spawn('node', ['scripts/mock-evennia-ws.js'], {
    cwd: pkgDir,
    env: { ...process.env, MOCK_WS_PORT: '4010', ...extraEnv },
    stdio: ['ignore', 'ignore', 'pipe']
  });
}

async function main() {
  fs.writeFileSync(
    configPath,
    JSON.stringify({ ws_url: 'ws://127.0.0.1:4010', auto_login_command: 'connect test secret' }, null, 2)
  );

  let mock = spawnMock({ MOCK_CLOSE_AFTER_FIRST_MESSAGE: '1' });

  const transport = new StdioClientTransport({
    command: 'node',
    args: ['index.js'],
    cwd: pkgDir,
    env: { ...process.env, MUD_KEEPALIVE_MS: '5000' },
    stderr: 'pipe'
  });
  const client = new Client({ name: 'evennia-mcp-reconnect-smoke', version: '1.0.0' });
  await client.connect(transport);
  await wait(2000);

  let status = await client.callTool({ name: 'mud_status', arguments: {} });
  let text = status.content?.[0]?.text || '';
  if (!text.includes('STATE: READY') && !text.includes('STATE: RECONNECTING')) {
    throw new Error(`Unexpected early state: ${text}`);
  }

  mock.kill('SIGTERM');
  await wait(1000);
  mock = spawnMock();
  await wait(8000);
  status = await client.callTool({ name: 'mud_status', arguments: {} });
  text = status.content?.[0]?.text || '';
  if (!text.includes('STATE: READY')) {
    throw new Error(`Reconnect did not recover to READY: ${text}`);
  }

  await transport.close();
  mock.kill('SIGTERM');
  if (fs.existsSync(configPath)) {
    fs.unlinkSync(configPath);
  }
  process.stderr.write('[smoke-reconnect] OK\n');
}

main().catch((error) => {
  process.stderr.write(`[smoke-reconnect] ${error.stack || error.message}\n`);
  process.exitCode = 1;
});
