# OpenWebUI Integration Fixes

This document describes the fixes applied to resolve OpenWebUI integration issues.

## Issues Fixed

### 1. Pipeline Interface Compatibility ✅

**Problem:** Agents were showing "Pipe.pipe() missing 3 required positional arguments" error

**Root Cause:** The class was named `Pipe` instead of `Pipeline`, and used `pipes()` method instead of `pipelines` property

**Solution:**
- Renamed class from `Pipe` to `Pipeline`
- Changed `pipes()` method to `pipelines` property (list of dicts)
- Added `on_startup()` and `on_shutdown()` lifecycle methods
- File renamed to `multi_agent_pipeline.py` following OpenWebUI naming convention

**Files Changed:**
- `apps/openwebui_pipe.py` → `apps/multi_agent_pipeline.py`
- `docker-compose.yml` (updated volume mount path)

### 2. Missing Auto Router Agent ✅

**Problem:** No automatic routing agent available - users had to manually select specialist agents

**Root Cause:** Only manual Router/Planner agent existed, no automatic routing

**Solution:**
- Added new "Auto Router" agent that automatically classifies requests
- Auto Router analyzes user input and routes to the best specialist agent
- Positioned as first agent in the list for easy access
- Router/Planner still available for advanced manual coordination

**Files Changed:**
- `config/agents.yaml` (added auto_router agent)
- `apps/multi_agent_pipeline.py` (included in fallback list)

### 3. Pipeline Auto-Loading ✅

**Problem:** Pipeline was not automatically showing up in OpenWebUI

**Root Cause:** Class naming and interface mismatch prevented proper loading

**Solution:**
- Fixed Pipeline class to match OpenWebUI's expected interface
- Pipeline now properly auto-loads from mounted volume
- Fallback agents ensure pipeline works even if API is unavailable

**Files Changed:**
- `apps/multi_agent_pipeline.py` (interface fixes)
- `OPENWEBUI.md` (updated troubleshooting guide)

## Available Agents

After the fix, the following agents are available in OpenWebUI:

1. **Auto Router** (NEW ⭐) - Automatically routes to the best specialist agent
2. **Router/Planner** - Manual task coordination and planning
3. **General Assistant** - General-purpose conversational AI
4. **Tool Agent** - Executes MCP tool calls
5. **SQL Agent** - Database queries and analysis
6. **DevOps Agent** - Infrastructure and deployment tasks
7. **Documentation Agent** - Documentation search and creation

## Testing

Run the validation tests:

```bash
# Validate configuration
python3 -c "import yaml; yaml.safe_load(open('config/agents.yaml'))"

# Validate pipeline syntax
python3 -m py_compile apps/multi_agent_pipeline.py

# Validate docker-compose
docker compose config > /dev/null

# Run pipeline tests (requires pydantic and requests)
pip install pydantic requests
python3 /tmp/test_pipeline.py
```

## Usage

### Quick Start

1. Set your OpenAI API key in `.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
```

2. Start the services:
```bash
docker compose up --build
```

3. Open OpenWebUI:
```
http://localhost:3000
```

4. Select "Auto Router" from the model dropdown

5. Start chatting!

### Recommended Agent Selection

- **For most users**: Use "Auto Router" - it automatically picks the right specialist
- **For complex tasks**: Use "Router/Planner" for manual coordination
- **For specific needs**: Select the specialist agent directly

## Verification

To verify the fixes are working:

1. **Check agents are loaded:**
```bash
# Should show 7 agents including auto_router
curl -H "Authorization: Bearer dev_key_123456789" \
     http://localhost:8000/v1/agents | jq '.[] | {id, name}'
```

2. **Check pipeline is mounted:**
```bash
docker compose exec openwebui ls -la /app/backend/data/functions/
# Should show multi_agent_pipeline.py
```

3. **Check pipeline loads in OpenWebUI:**
- Open http://localhost:3000
- Click model dropdown
- Should see "Multi-Agent System" with all 7 agents

4. **Test auto router:**
- Select "Auto Router" agent
- Ask: "What's the weather like?"
- Should get a response (routed to General Assistant)
- Ask: "How do I query users table?"
- Should get a response (routed to SQL Agent)

## Troubleshooting

If agents still don't show up:

1. **Clear Docker volumes:**
```bash
docker compose down -v
docker compose up --build
```

2. **Check OpenWebUI logs:**
```bash
docker compose logs openwebui | grep -i pipeline
docker compose logs openwebui | grep -i error
```

3. **Verify file is mounted:**
```bash
docker compose exec openwebui cat /app/backend/data/functions/multi_agent_pipeline.py | head -20
```

4. **Check API is accessible from OpenWebUI:**
```bash
docker compose exec openwebui curl http://api:8000/health
```

## Technical Details

### Pipeline Interface

The pipeline now follows OpenWebUI's expected interface:

```python
class Pipeline:
    def __init__(self):
        self.type = "manifold"  # Indicates multiple models
        self.id = "multi_agent_system"
        self.name = "Multi-Agent System"
        self.pipelines = [...]  # List of available models
    
    async def on_startup(self):
        # Called when pipeline loads
        pass
    
    async def on_shutdown(self):
        # Called when pipeline unloads
        pass
    
    def pipe(self, user_message, model_id, messages, body):
        # Process chat requests
        pass
```

### Auto Router Logic

The Auto Router agent uses this system prompt:

```
You are an intelligent auto-routing agent. Your job is to:
1. Analyze the user's request
2. Automatically determine which specialized agent is BEST suited
3. Route the request to that agent and return its response

Available specialist agents:
- general: General conversational assistant
- tool: Tool executor
- sql: SQL specialist
- devops: DevOps specialist
- docs: Documentation specialist

IMPORTANT: Route to exactly ONE agent that best fits the request.
```

## Migration Guide

If you were using the old pipeline:

1. **No action needed** - the changes are backward compatible
2. **Rebuild containers** to get the latest pipeline:
```bash
docker compose up --build
```

3. **New "Auto Router" agent** will appear automatically
4. **Existing conversations** will continue to work

## Future Improvements

Potential enhancements for future versions:

1. **Conversation persistence** - Reuse conversations across sessions
2. **Multi-agent workflows** - Chain multiple agents in one request
3. **Agent performance metrics** - Track which agents are used most
4. **Custom routing rules** - User-defined routing logic
5. **Tool call visualization** - Show which tools agents are using

## Related Documentation

- [OPENWEBUI.md](./OPENWEBUI.md) - Full OpenWebUI usage guide
- [config/agents.yaml](./config/agents.yaml) - Agent configurations
- [apps/multi_agent_pipeline.py](./apps/multi_agent_pipeline.py) - Pipeline implementation
