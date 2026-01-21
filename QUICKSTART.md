# OpenWebUI Quick Start Guide

## 🚀 Getting Started

1. **Start the system:**
   ```bash
   docker compose up --build
   ```

2. **Wait for services to start** (usually 30-60 seconds)

3. **Open OpenWebUI:**
   ```
   http://localhost:3000
   ```

## 💬 Using the Interface

### Select an Agent

Click the model dropdown at the top of the chat and choose from:

- **Router/Planner** - Smart routing to the right specialist agent
- **General Assistant** - General conversation and questions
- **SQL Agent** - Database queries and analysis
- **DevOps Agent** - Infrastructure and deployment help
- **Documentation Agent** - Documentation search and creation
- **Tool Agent** - Execute MCP tools

### Chat

Simply type your message and press Enter. The agent will respond in real-time using OpenAI.

## 🔧 Configuration

All configuration is in `.env`:

```bash
# Required - Your OpenAI API key
OPENAI_API_KEY=sk-your-key-here

# Optional - Change the model
DEFAULT_MODEL=gpt-4

# Optional - Enable debug logging
LOG_LEVEL=DEBUG
```

## 🧪 Testing

Run the integration test:
```bash
./test_openwebui.sh
```

## 📚 Documentation

- **[OPENWEBUI.md](OPENWEBUI.md)** - Detailed usage guide
- **[SETUP.md](SETUP.md)** - Complete setup instructions
- **[README.md](README.md)** - Project overview

## ⚡ Troubleshooting

**OpenWebUI not loading?**
```bash
docker compose logs openwebui
```

**Agents not showing up?**
```bash
# Check API is running
curl http://localhost:8000/health

# Check agents are configured
curl -H "Authorization: Bearer dev_key_123456789" \
     http://localhost:8000/v1/agents
```

**Slow responses?**
- Check your OpenAI API key is valid
- Increase timeout: `OPENAI_TIMEOUT=120` in `.env`
- Check logs: `docker compose logs orchestrator`

## 🎯 Quick Examples

### Example 1: General Question
1. Select "General Assistant"
2. Ask: "What is the capital of France?"
3. Get instant AI response via OpenAI

### Example 2: Router Agent
1. Select "Router/Planner"
2. Ask: "I need to query the database for user statistics"
3. Router analyzes and delegates to SQL Agent

### Example 3: SQL Query
1. Select "SQL Agent"
2. Ask: "Show me all users created in the last 30 days"
3. Get SQL-specific assistance

## 🔐 Security Note

The default setup has authentication disabled (`WEBUI_AUTH=false`) for easy testing. For production:

1. Enable authentication in docker-compose.yml
2. Set up user accounts in OpenWebUI
3. Configure JWT authentication for the API

## 🌐 Accessing Services

- OpenWebUI: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📝 Next Steps

1. Try different agents
2. Customize system prompts in `config/agents.yaml`
3. Add your own specialized agents
4. Configure MCP tools for enhanced capabilities
5. Deploy to production (see SETUP.md)
