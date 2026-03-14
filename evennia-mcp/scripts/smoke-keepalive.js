import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const pkgDir = path.dirname(__dirname);
const configPath = path.join(pkgDir, 'mcp-config.json');
const mockLogPath = '/tmp/evennia-mcp-keepalive-mock.log';
const mockPort = '4011';

function wait(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  fs.writeFileSync(
    configPath,
    JSON.stringify({ ws_url: `ws://127.0.0.1:${mockPort}`, auto_login_command: 'connect test secret' }, null, 2)
  );

  const mockOut = fs.openSync(mockLogPath, 'w');
  const mock = spawn('node', ['scripts/mock-evennia-ws.js'], {
    cwd: pkgDir,
    env: { ...process.env, MOCK_WS_PORT: mockPort },
    stdio: ['ignore', mockOut, mockOut]
  });

  const server = spawn('node', ['index.js'], {
    cwd: pkgDir,
    env: { ...process.env, MUD_KEEPALIVE_MS: '1500' },
    stdio: ['ignore', 'ignore', 'pipe']
  });

  await wait(3500);

  server.kill('SIGTERM');
  mock.kill('SIGTERM');
  fs.closeSync(mockOut);

  const log = fs.readFileSync(mockLogPath, 'utf8');
  fs.unlinkSync(mockLogPath);
  if (fs.existsSync(configPath)) {
    fs.unlinkSync(configPath);
  }

  if (!log.includes('["text",["idle"],{}]')) {
    throw new Error(`Keepalive frame not observed in mock log:\n${log}`);
  }

  process.stderr.write('[smoke-keepalive] OK\n');
}

main().catch((error) => {
  process.stderr.write(`[smoke-keepalive] ${error.stack || error.message}\n`);
  process.exitCode = 1;
});
