const BASE = '/api';

export interface Agent {
  name: string;
  role: string;
  description: string;
  tools: string[];
}

export interface TaskResult {
  task: string;
  plan: any;
  execution_result: string;
  review: any;
  final_output: string;
  status: string;
}

export interface KnowledgeDoc {
  id: string;
  title: string;
  content_preview: string;
  metadata: Record<string, any>;
}

export const api = {
  // Agents
  async listAgents(): Promise<Agent[]> {
    const res = await fetch(`${BASE}/agents/`);
    const data = await res.json();
    return data.agents;
  },

  async runTask(task: string, kbQuery: string = ''): Promise<TaskResult> {
    const res = await fetch(`${BASE}/agents/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ task, kb_query: kbQuery }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async chat(message: string, stream: boolean = false): Promise<string | ReadableStream> {
    const res = await fetch(`${BASE}/agents/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, stream }),
    });
    if (stream) return res.body!;
    const data = await res.json();
    return data.response;
  },

  async listTools(): Promise<any[]> {
    const res = await fetch(`${BASE}/agents/tools`);
    const data = await res.json();
    return data.tools;
  },

  // Knowledge
  async listKnowledge(): Promise<KnowledgeDoc[]> {
    const res = await fetch(`${BASE}/knowledge/`);
    const data = await res.json();
    return data.documents;
  },

  async addKnowledge(docId: string, title: string, content: string, metadata: Record<string, any> = {}): Promise<any> {
    const res = await fetch(`${BASE}/knowledge/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ docId, title, content, metadata }),
    });
    return res.json();
  },

  async deleteKnowledge(docId: string): Promise<any> {
    const res = await fetch(`${BASE}/knowledge/${docId}`, { method: 'DELETE' });
    return res.json();
  },

  async searchKnowledge(query: string, topK: number = 5): Promise<any> {
    const res = await fetch(`${BASE}/knowledge/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, topK }),
    });
    return res.json();
  },

  // Tasks
  async listTasks(): Promise<any[]> {
    const res = await fetch(`${BASE}/tasks/`);
    const data = await res.json();
    return data.tasks;
  },
};
