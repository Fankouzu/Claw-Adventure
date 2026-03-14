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

async function main() {
  const config = {
    ws_url: 'ws://127.0.0.1:4010',
    auto_login_command: 'connect test secret'
  };
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));

  const mock = spawn('node', ['scripts/mock-evennia-ws.js'], {
    cwd: pkgDir,
    env: { ...process.env, MOCK_WS_PORT: '4010' },
    stdio: ['ignore', 'ignore', 'pipe']
  });

  const transport = new StdioClientTransport({
    command: 'node',
    args: ['index.js'],
    cwd: pkgDir,
    stderr: 'pipe'
  });

  const client = new Client({ name: 'evennia-mcp-smoke', version: '1.0.0' });
  await client.connect(transport);
  await wait(1000);

  const tools = await client.listTools();
  const names = tools.tools.map((tool) => tool.name).sort();
  if (!names.includes('mud_action') || !names.includes('mud_read') || !names.includes('mud_status')) {
    throw new Error(`Missing tools: ${names.join(',')}`);
  }

  const status = await client.callTool({ name: 'mud_status', arguments: {} });
  const statusText = status.content?.[0]?.text || '';
  if (!statusText.includes('STATE: READY')) {
    throw new Error(`Server not ready: ${statusText}`);
  }

  const action = await client.callTool({ name: 'mud_action', arguments: { command: 'look' } });
  const actionText = action.content?.[0]?.text || '';
  if (actionText !== 'Command sent.') {
    throw new Error(`Unexpected mud_action response: ${actionText}`);
  }

  await wait(500);
  const read = await client.callTool({ name: 'mud_read', arguments: {} });
  const readText = read.content?.[0]?.text || '';
  if (!readText.includes('hello from mock')) {
    throw new Error(`Unexpected mud_read response: ${readText}`);
  }

  const readAgain = await client.callTool({ name: 'mud_read', arguments: {} });
  const readAgainText = readAgain.content?.[0]?.text || '';
  if (readAgainText !== 'No new events since last read.') {
    throw new Error(`Buffer was not cleared: ${readAgainText}`);
  }

  await transport.close();
  mock.kill('SIGTERM');
  fs.unlinkSync(configPath);
  process.stderr.write('[smoke] OK\n');
}

main().catch((error) => {
  process.stderr.write(`[smoke] ${error.stack || error.message}\n`);
  process.exitCode = 1;
});
