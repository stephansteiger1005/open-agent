# open-agent
## Project: Multi-Agent OpenWebUI Instance (MCP + REST)

Build a production-ready multi-agent system inside/alongside OpenWebUI that orchestrates specialized agents via the Model Context Protocol (MCP) and exposes a clean REST API for external integrations. The system must support routing, tool access, memory, and streaming responses, and run locally with Docker.

---

## Goals

- Provide multi-agent orchestration for OpenWebUI chats (planner/router + specialist agents).
- Use MCP servers as the standard way to expose tools/capabilities (DB, web, files, calendar, etc.).
- Offer a REST API to:
  - start conversations
  - send messages
  - stream tokens/events
  - inspect runs, steps, tool calls
  - manage agent registry and policies
- Be ready to run: docker-compose, env templates, sensible defaults, test suite.

---

## Core Concepts

### Agents
Each agent is a stateless service with:
- id, name, role
- system_prompt
- model (or model selector)
- allowed_tools (MCP tool allowlist)
- optional policies (data redaction, SQL safety, etc.)

Required agents:
1. Router/Planner – decides which agent(s) should act, creates a plan, delegates tasks.
2. General Assistant – default conversational agent.
3. Tool Agent – executes MCP tool calls safely (optionally separated for security).
4. Domain Specialists – e.g. sql-agent, devops-agent, docs-agent.

### MCP Integration
- Connect to one or more MCP servers (stdio or HTTP transport).
- Discover tools dynamically via MCP and map them into a unified tool registry.
- Enforce per-agent allowlists and argument validation.

### Orchestration
Run loop:
1. receive user message
2. router produces plan (single-agent or multi-step)
3. execute steps:
   - model calls
   - tool calls via MCP
   - intermediate state updates
4. stream events and finalize response

### Persistence
Store:
- conversations
- messages
- runs
- steps
- tool_calls  
SQLite by default, Postgres optional.

---

## System Architecture

### Services (Docker)
- api (FastAPI or similar)
  - REST endpoints
  - SSE/WebSocket streaming
  - auth middleware
- orchestrator
  - routing/planning
  - agent execution
  - MCP tool invocation
- mcp-gateway (optional)
  - manages MCP server connections
  - caches tool schemas
  - applies security controls
- db (sqlite volume or postgres)

OpenWebUI integration:
- Plugin/Pipe: OpenWebUI calls this REST API as backend agent runtime
- Sidecar: OpenWebUI unchanged, accessed via separate endpoint/client

---

## REST API (v1)

### Conversations
- POST /v1/conversations
- GET /v1/conversations/{conversation_id}
- POST /v1/conversations/{conversation_id}/messages  
  body: { "role": "user", "content": "...", "attachments": [] }

### Runs
- POST /v1/conversations/{conversation_id}/runs  
  body: { "agent_id": "router", "stream": true, "metadata": {} }
- GET /v1/runs/{run_id}
- GET /v1/runs/{run_id}/steps

### Streaming
- GET /v1/runs/{run_id}/events (SSE)  
Events:
- run.started
- step.started
- model.delta
- tool.call.started
- tool.call.result
- run.completed
- run.failed

### Agents
- GET /v1/agents
- POST /v1/agents (admin)
- GET /v1/agents/{agent_id}
- PATCH /v1/agents/{agent_id} (admin)

### Tools
- GET /v1/tools
- GET /v1/tools/{tool_name}
- POST /v1/tools/{tool_name}/invoke (admin/testing)

---

## Security

- API key (dev), JWT (prod)
- Per-agent tool allowlists
- JSON schema validation for MCP arguments
- Secret redaction in logs
- Rate limiting for tool calls
- Optional sandbox mode for dangerous tools

---

## Configuration

Environment:
- DATABASE_URL=sqlite:///data/app.db
- AUTH_MODE=apikey|jwt
- API_KEYS=...
- MODEL_PROVIDER=openai|ollama|azure|...
- MCP_SERVERS=...
- DEFAULT_MODEL=...

Files:
- .env.example
- docker-compose.yml
- config/agents.yaml
- config/tool_policies.yaml

---

## Repository Layout

- apps/api/
- apps/orchestrator/
- apps/mcp_gateway/
- packages/core/
- packages/clients/
- config/
- tests/
- deploy/

---

## Implementation Notes

- Typed event model for streaming (SSE)
- Support single-agent and router→specialist flows
- MCP flow:
  1. discover tools + schemas
  2. model emits tool call
  3. validate args
  4. invoke MCP
  5. persist and optionally feed result back

---

## Definition of Done

- docker compose up starts a working system
- Conversations + streaming responses work
- At least one MCP tool works end-to-end
- Runs and steps are persisted and inspectable
- Core routing and tool tests pass

---

## Deliverables

- Working codebase
- curl examples
- OpenWebUI pipe/plugin example
- Minimal README with setup and extension guide
