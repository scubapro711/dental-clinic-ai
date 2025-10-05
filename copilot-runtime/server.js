import express from 'express';
import cors from 'cors';
import { 
  CopilotRuntime, 
  copilotRuntimeNodeHttpEndpoint,
  ExperimentalEmptyAdapter 
} from '@copilotkit/runtime';

const app = express();
const PORT = 3001;

app.use(cors({ origin: 'http://localhost:5173', credentials: true }));
app.use(express.json());

const runtime = new CopilotRuntime({
  remoteEndpoints: [
    {
      uri: "http://localhost:8000/copilotkit",
    }
  ]
});

const serviceAdapter = new ExperimentalEmptyAdapter();

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.post('/api/copilotkit', async (req, res) => {
  const handler = copilotRuntimeNodeHttpEndpoint({
    runtime,
    serviceAdapter,
    endpoint: '/api/copilotkit'
  });
  
  await handler(req, res);
});

app.listen(PORT, () => {
  console.log(`✅ Copilot Runtime on http://localhost:${PORT}`);
});
