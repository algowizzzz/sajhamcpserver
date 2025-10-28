# Agent System Documentation

**Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com**

## Overview

The Agent System is a config-driven, LangGraph-ready AI agent framework that provides an "Agent as a Service" capability. It integrates seamlessly with the existing MCP tools infrastructure to create specialized AI agents that can reason about queries and execute appropriate tools to fulfill user requests.

## Key Features

- **Config-Driven**: All agents defined via JSON configuration files
- **Tool Integration**: Seamless integration with all MCP tools
- **Multiple Agent Types**: Pre-built agent personalities (default, risk analyst, data analyst)
- **Simple Architecture**: Easy to understand and extend
- **CLI Interface**: Command-line interface for direct interaction
- **API Ready**: Structured for easy REST API integration
- **LangGraph Compatible**: Architecture ready for LangGraph enhancement

## Architecture

```
┌─────────────────────────────────────┐
│         User Query                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     Agent Executor                  │
│  - Load Config                      │
│  - Parse Query                      │
│  - Select Tool                      │
│  - Execute & Format                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     MCP Tools Adapter               │
│  - Tool Discovery                   │
│  - Tool Execution                   │
│  - Result Formatting                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     MCP Tools Registry              │
│  - 13+ Available Tools              │
└─────────────────────────────────────┘
```

## Directory Structure

```
agent/
├── __init__.py              # Package initialization
├── state.py                 # Agent state management
├── tools_adapter.py         # MCP tools integration
├── agent_config.py          # Configuration management
├── prompts.py              # System prompts for different agents
└── agent_executor.py        # Main agent execution logic

config/agents/
├── default_agent.json       # General purpose agent
├── risk_analyst_agent.json  # Risk-focused agent
└── data_analyst_agent.json  # Data analysis agent

run_agent.py                 # CLI runner script
```

## Installation

### Prerequisites

- Python 3.8+
- All MCP tools configured
- Virtual environment activated

### Setup

The agent system is already installed if you have the MCP server running. No additional installation required.

## Configuration

### Agent Configuration File Structure

```json
{
  "name": "agent_name",
  "description": "Agent description",
  "model": "gpt-4",
  "temperature": 0.7,
  "max_iterations": 5,
  "enabled_tools": [],
  "system_prompt_template": "default",
  "response_format": "natural",
  "streaming": false,
  "metadata": {
    "version": "1.0.0",
    "author": "Your Name",
    "tags": ["tag1", "tag2"]
  }
}
```

### Configuration Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `name` | string | Unique agent identifier | required |
| `description` | string | Human-readable description | required |
| `model` | string | LLM model to use | "gpt-4" |
| `temperature` | float | LLM temperature (0-1) | 0.7 |
| `max_iterations` | int | Max tool executions | 5 |
| `enabled_tools` | array | Tool whitelist (empty = all) | [] |
| `system_prompt_template` | string | Prompt template name | "default" |
| `response_format` | string | Output format style | "natural" |
| `streaming` | boolean | Enable streaming (future) | false |

### Available Prompt Templates

1. **default** - General purpose assistant
2. **risk_analyst** - Specialized for risk analysis
3. **data_analyst** - Optimized for data exploration

## Usage

### Command Line Interface

#### Basic Usage

```bash
# Single query execution
python run_agent.py "Your query here"

# Use specific agent
python run_agent.py --agent risk_analyst_agent "Check limits for AC001"

# List available agents
python run_agent.py --list-agents

# Interactive mode
python run_agent.py --interactive

# Verbose logging
python run_agent.py --verbose "Your query"
```

#### CLI Examples

**Example 1: Risk Analysis**
```bash
python run_agent.py --agent risk_analyst_agent "Analyze risk for Northbridge Capital"
```

**Output:**
```
# Risk Analysis: Northbridge Capital

## Executive Summary
- **Rating**: A-
- **Sector**: Financial Services
- **Limit Status**: BREACH
- **Utilization**: 113.81%

## Exposure Metrics
- **Exposure (EPE)**: $13,543,220.92
- **Total Trades**: 16
- **Total Notional**: $172,400,755.39
...
```

**Example 2: Data Query**
```bash
python run_agent.py "List all available tables"
```

**Output:**
```
# Available Data Tables

- **ccr_limits**: 30 rows
- **trades**: 90 rows

Total: 2 tables
```

**Example 3: Interactive Mode**
```bash
python run_agent.py --interactive --agent risk_analyst_agent
```

```
🤖 > Check limits for AC001
Thinking...
------------------------------------------------------------
# Risk Analysis: Northbridge Capital
...
------------------------------------------------------------

🤖 > switch default_agent
✓ Switched to agent: default_agent

🤖 > List all tables
...
```

### Programmatic Usage (Python)

#### Example 1: Simple Query Execution

```python
from agent import AgentExecutor, AgentConfig

# Load agent configuration
config_manager = AgentConfig()
config = config_manager.load_agent_config('default_agent')

# Create agent
agent = AgentExecutor(config)

# Execute query
result = agent.run("Analyze risk for Northbridge Capital")

# Access results
print(result['final_answer'])
print(f"Iterations: {result['iterations']}")
print(f"Tools used: {result['tools_used']}")
```

#### Example 2: Risk Analyst Agent

```python
from agent import AgentExecutor, AgentConfig

config_manager = AgentConfig()
risk_config = config_manager.load_agent_config('risk_analyst_agent')
agent = AgentExecutor(risk_config)

# Check multiple counterparties
counterparties = ['AC001', 'AC002', 'AC003', 'AC004', 'AC005', 'AC006']
results = []

for cp in counterparties:
    result = agent.run(f"Check limits for {cp}")
    results.append(result)

# Process results
for result in results:
    if 'BREACH' in result['final_answer']:
        print(f"⚠️  Breach detected: {result['query']}")
```

#### Example 3: Custom Agent Configuration

```python
from agent import AgentExecutor

# Create custom agent config
custom_config = {
    'name': 'custom_agent',
    'description': 'My custom agent',
    'model': 'gpt-4',
    'temperature': 0.5,
    'max_iterations': 3,
    'enabled_tools': ['limits_exposure_analysis', 'duckdb_olap_tools'],
    'system_prompt_template': 'risk_analyst'
}

agent = AgentExecutor(custom_config)
result = agent.run("Your query")
```

## Pre-Built Agents

### 1. Default Agent

**Configuration:** `config/agents/default_agent.json`

- **Purpose**: General purpose assistant
- **Tools**: All available tools
- **Temperature**: 0.7
- **Use Cases**: 
  - General queries
  - Multi-domain questions
  - Exploratory analysis

**Example Queries:**
- "What can you help me with?"
- "List all available tables"
- "Analyze risk for AC001"

### 2. Risk Analyst Agent

**Configuration:** `config/agents/risk_analyst_agent.json`

- **Purpose**: Counterparty credit risk analysis
- **Tools**: 
  - `limits_exposure_analysis`
  - `duckdb_olap_tools`
  - `tavily`
- **Temperature**: 0.3 (more precise)
- **Use Cases**:
  - Credit risk assessment
  - Limit breach detection
  - Exposure analysis
  - Risk reporting

**Example Queries:**
- "Analyze risk for Northbridge Capital"
- "Check limits for AC003"
- "Show me all limit breaches"
- "What is the exposure for Aurora Metals?"

### 3. Data Analyst Agent

**Configuration:** `config/agents/data_analyst_agent.json`

- **Purpose**: Data exploration and analysis
- **Tools**:
  - `duckdb_olap_tools`
  - `sqlselect`
- **Temperature**: 0.5 (balanced)
- **Use Cases**:
  - Data exploration
  - SQL queries
  - Statistical analysis
  - Data quality checks

**Example Queries:**
- "List all tables"
- "Show me sample data from trades"
- "Query all trades for AC001"
- "Describe the ccr_limits table"

## Creating Custom Agents

### Step 1: Create Configuration File

Create a new JSON file in `config/agents/`:

```json
{
  "name": "my_custom_agent",
  "description": "Custom agent for specific use case",
  "model": "gpt-4",
  "temperature": 0.7,
  "max_iterations": 5,
  "enabled_tools": [
    "tool1",
    "tool2"
  ],
  "system_prompt_template": "default",
  "metadata": {
    "version": "1.0.0",
    "author": "Your Name"
  }
}
```

### Step 2: Test Your Agent

```bash
python run_agent.py --agent my_custom_agent "Test query"
```

### Step 3: Create Custom Prompt (Optional)

If you need a custom system prompt, edit `agent/prompts.py`:

```python
MY_CUSTOM_PROMPT = """You are a specialized agent for...

Available Tools:
{tools_description}

[Your custom instructions]
"""

PROMPT_TEMPLATES = {
    'default': DEFAULT_SYSTEM_PROMPT,
    'risk_analyst': RISK_ANALYST_PROMPT,
    'my_custom': MY_CUSTOM_PROMPT  # Add your prompt
}
```

Then use it in your config:
```json
{
  "system_prompt_template": "my_custom"
}
```

## Query Pattern Recognition

The agent uses pattern matching to identify user intent:

### Risk Analysis Patterns
- Keywords: "limit", "breach", "exposure", "counterparty", "risk"
- Extracts: Counterparty names or Adaptiv codes (AC###)
- Action: Executes `limits_exposure_analysis` tool

### Data Query Patterns
- Keywords: "list", "table", "data", "file"
- Action: Executes `duckdb_olap_tools` with `list_tables`

### SQL Query Patterns
- Keywords: "query", "select", "sql"
- Extracts: SQL SELECT statements
- Action: Executes `duckdb_olap_tools` with `query` action

### Search Patterns
- Keywords: "search", "google"
- Action: Executes `tavily` or `google_search` tool

### Wikipedia Patterns
- Keywords: "wikipedia", "wiki"
- Action: Executes `wikipedia` tool

## Response Formatting

The agent automatically formats responses based on tool type:

### Risk Analysis Format
```markdown
# Risk Analysis: [Counterparty Name]

## Executive Summary
- **Rating**: A-
- **Sector**: Financial Services
- **Limit Status**: BREACH
- **Utilization**: 113.81%

## Exposure Metrics
- **Exposure (EPE)**: $13,543,220.92
- **Total Trades**: 16
...
```

### Data Query Format
```markdown
# Available Data Tables

- **table1**: 100 rows
- **table2**: 200 rows

Total: 2 tables
```

### Search Results Format
```markdown
# Search Results

## 1. Title
Description...
Source: URL

## 2. Title
...
```

## API Integration

### Flask Endpoint Example

```python
from flask import Flask, request, jsonify
from agent import AgentExecutor, AgentConfig

app = Flask(__name__)
config_manager = AgentConfig()

@app.route('/api/agent/query', methods=['POST'])
def agent_query():
    data = request.json
    query = data.get('query')
    agent_name = data.get('agent', 'default_agent')
    
    try:
        config = config_manager.load_agent_config(agent_name)
        agent = AgentExecutor(config)
        result = agent.run(query)
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agent/list', methods=['GET'])
def list_agents():
    agents = config_manager.list_available_agents()
    return jsonify({
        'success': True,
        'agents': agents
    })
```

### API Usage Example

```bash
# Execute query
curl -X POST http://localhost:5000/api/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze risk for AC001",
    "agent": "risk_analyst_agent"
  }'

# List agents
curl http://localhost:5000/api/agent/list
```

## Best Practices

### 1. Agent Selection

- Use **risk_analyst_agent** for credit/risk queries
- Use **data_analyst_agent** for data exploration
- Use **default_agent** for general queries

### 2. Query Formulation

**Good queries:**
- "Analyze risk for Northbridge Capital"
- "Check limits for AC001"
- "List all available tables"

**Less optimal:**
- "Tell me about AC001" (too vague)
- "Risk" (insufficient context)

### 3. Tool Configuration

- Limit tools for specialized agents (better performance)
- Use all tools for general purpose agents
- Test with verbose mode during development

### 4. Performance Optimization

- Set appropriate `max_iterations` (lower = faster)
- Use selective tool lists
- Cache results when possible

## Troubleshooting

### Issue: Agent doesn't select correct tool

**Solution:** Check query phrasing, use keywords like "limit", "risk", "query"

### Issue: "Tool not found" error

**Solution:** Verify tool is enabled in agent config's `enabled_tools` array

### Issue: Timeout or slow response

**Solution:** Reduce `max_iterations`, check tool performance, use specific queries

### Issue: Incorrect results

**Solution:** Try different agent (e.g., risk_analyst vs default), adjust temperature

## Future Enhancements

### Planned Features

1. **Full LangGraph Integration**
   - Multi-step reasoning
   - Memory and context management
   - Complex workflow support

2. **Streaming Responses**
   - Real-time output streaming
   - Progress indicators

3. **Multi-Tool Execution**
   - Parallel tool execution
   - Tool chaining
   - Conditional execution

4. **Enhanced Pattern Matching**
   - LLM-based query understanding
   - Intent classification
   - Entity extraction

5. **Web UI**
   - Dedicated agent interface
   - Visual workflow builder
   - Result visualization

## Examples Library

### Example 1: Daily Risk Report

```python
from agent import AgentExecutor, AgentConfig

config = AgentConfig().load_agent_config('risk_analyst_agent')
agent = AgentExecutor(config)

# Get all counterparties with limit breaches
counterparties = ['AC001', 'AC002', 'AC003', 'AC004', 'AC005', 'AC006']

report = "# Daily Risk Report\n\n"
breaches = []

for cp in counterparties:
    result = agent.run(f"Check limits for {cp}")
    if 'BREACH' in result['final_answer']:
        breaches.append(result['final_answer'])

report += f"## Breaches Detected: {len(breaches)}\n\n"
for breach in breaches:
    report += breach + "\n\n"

print(report)
```

### Example 2: Interactive Risk Session

```bash
# Start interactive mode with risk analyst
python run_agent.py -i -a risk_analyst_agent

# Run queries
🤖 > Check all counterparties for breaches
🤖 > Analyze AC001 in detail
🤖 > Show failed trades for Aurora Metals
```

### Example 3: Automated Monitoring

```python
import schedule
import time
from agent import AgentExecutor, AgentConfig

def check_limits():
    config = AgentConfig().load_agent_config('risk_analyst_agent')
    agent = AgentExecutor(config)
    
    counterparties = ['AC001', 'AC003', 'AC005']
    
    for cp in counterparties:
        result = agent.run(f"Check limits for {cp}")
        if 'BREACH' in result['final_answer']:
            send_alert(cp, result['final_answer'])

# Schedule check every hour
schedule.every().hour.do(check_limits)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Support

- **Documentation**: See this file
- **Issues**: Check logs with `--verbose` flag
- **Custom Agents**: Follow "Creating Custom Agents" section

## Version History

- **v1.0.0** (2025-10-27): Initial release
  - Config-driven agent system
  - 3 pre-built agents
  - CLI interface
  - Pattern-based query routing
  - MCP tools integration

---

**End of Documentation**

