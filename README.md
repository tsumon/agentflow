# AgentFlow — Enterprise Multi-Agent Collaboration Platform

A production-ready enterprise platform for orchestrating multiple AI agents in a **Plan → Execute → Review** pipeline.

## Architecture

```
User Request
     │
     ▼
┌──────────┐    ┌───────────┐    ┌──────────┐
│ Planner  │───▶│ Executor  │───▶│ Reviewer │
│ (规划)   │    │ (执行)    │    │ (审查)   │
└──────────┘    └───────────┘    └──────────┘
     │               │                │
     ▼               ▼                ▼
  Task Plan     Tool Calls       Quality Report
  (JSON)        (6 tools)        (Pass/Revise)
```

## Features

- **Multi-Agent Pipeline**: Planner → Executor → Reviewer with automatic orchestration
- **Built-in Tools**: Calculator, Search, File R/W, Web Fetch, JSON Parse
- **Knowledge Base**: Document store for RAG-powered context injection
- **REST API**: FastAPI backend with async support and streaming
- **Web UI**: React dashboard with task playground and knowledge management
- **Persistent Storage**: SQLite with SQLAlchemy async ORM

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY=sk-your-key
export OPENAI_BASE_URL=https://api.openai.com/v1  # or custom endpoint

python run.py
# Server starts at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:3000
```

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Your OpenAI API key |
| `OPENAI_BASE_URL` | `https://api.openai.com/v1` | API base URL (supports compatible providers) |
| `AGENTFLOW_LLM_MODEL` | `gpt-4o-mini` | Model to use |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/agents/` | List available agents |
| `POST` | `/api/agents/run` | Execute pipeline task |
| `POST` | `/api/agents/chat` | Direct chat with agent |
| `GET` | `/api/agents/tools` | List available tools |
| `GET` | `/api/tasks/` | List task history |
| `POST` | `/api/tasks/` | Create task record |
| `GET` | `/api/knowledge/` | List knowledge docs |
| `POST` | `/api/knowledge/` | Add knowledge doc |
| `POST` | `/api/knowledge/search` | Search knowledge base |

## Project Structure

```
agentflow/
├── backend/
│   ├── app/
│   │   ├── agents/        # Planner, Executor, Reviewer, Orchestrator
│   │   ├── core/           # LLM client, Memory, Tools, Knowledge
│   │   ├── api/            # FastAPI route handlers
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   ├── config.py       # Settings
│   │   └── main.py         # FastAPI app
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── pages/          # Agents, Playground, Knowledge
│   │   ├── services/       # API client
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## License

MIT
