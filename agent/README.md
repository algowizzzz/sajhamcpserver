# Agent System

**Config-driven AI agents with MCP tools integration**

## Quick Start

```bash
# List available agents
python run_agent.py --list-agents

# Execute query
python run_agent.py "Check limits for AC001"

# Use specific agent
python run_agent.py --agent risk_analyst_agent "Analyze risk for Northbridge Capital"

# Interactive mode
python run_agent.py --interactive
```

## Python Usage

```python
from agent import AgentExecutor, AgentConfig

# Load agent
config = AgentConfig().load_agent_config('risk_analyst_agent')
agent = AgentExecutor(config)

# Execute query
result = agent.run("Check limits for AC001")
print(result['final_answer'])
```

## Available Agents

1. **default_agent** - General purpose assistant (all tools)
2. **risk_analyst_agent** - Credit risk specialist (risk tools)
3. **data_analyst_agent** - Data exploration expert (data tools)

## Creating Custom Agents

1. Create JSON file in `config/agents/my_agent.json`
2. Define name, tools, and prompt template
3. Use with `--agent my_agent`

See `docs/userguides/Agent System Documentation.md` for full documentation.

## Architecture

```
agent/
├── __init__.py          # Package initialization
├── state.py             # Agent state (LangGraph-ready)
├── tools_adapter.py     # MCP tools integration
├── agent_config.py      # Config management
├── prompts.py           # System prompts
└── agent_executor.py    # Main execution engine
```

## Features

- ✅ Config-driven architecture
- ✅ Multiple agent personalities
- ✅ Pattern-based query routing
- ✅ Smart entity extraction
- ✅ Formatted responses
- ✅ CLI + Python API
- ✅ LangGraph-ready structure

---

Copyright All rights Reserved 2025-2030, Ashutosh Sinha

