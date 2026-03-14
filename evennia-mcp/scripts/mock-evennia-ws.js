import process from 'node:process';
import { WebSocketServer } from 'ws';

const port = Number(process.env.MOCK_WS_PORT || 4010);
const CLOSE_AFTER_FIRST_MESSAGE = process.env.MOCK_CLOSE_AFTER_FIRST_MESSAGE === '1';
let seenMessages = 0;
const wss = new WebSocketServer({ port });

wss.on('connection', (ws) => {
  ws.on('message', (data) => {
    const text = data.toString();
    process.stderr.write(`[mock-ws] ${text}\n`);
    seenMessages += 1;
    ws.send(JSON.stringify(['text', ['<p>hello from mock</p>'], {}]));
    if (CLOSE_AFTER_FIRST_MESSAGE && seenMessages === 1) {
      ws.close();
    }
  });
});

process.stderr.write(`[mock-ws] listening on ${port}\n`);
