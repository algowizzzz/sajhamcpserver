# Single-File Configuration Refactoring

**Date:** October 27, 2025  
**Version:** 2.0.0  
**Status:** ✅ Complete

## Overview

Refactored the agent system from scattered configuration (multiple files, hardcoded prompts) to a **single JSON file per agent** containing ALL configuration.

## What Changed

### Before (v1.0.0) - Scattered Config
```
config/agents/risk_analyst_agent.json  → name, model, tools only
agent/prompts.py                       → HARDCODED prompts
                                       → system_prompt_template reference
```

**Issues:**
- ❌ Prompts hardcoded in Python
- ❌ Multiple files to modify
- ❌ Not truly config-driven
- ❌ Can't customize prompts without code changes

### After (v2.0.0) - Single File Config
```
config/agents/risk_analyst_agent.json  → EVERYTHING!
  - name, description
  - model (name, temperature, max_tokens)
  - execution (max_iterations, timeout)
  - tools (enabled list)
  - prompt (system prompt with variables)
  - response (format, style)
  - metadata

agent/prompts.py                       → FALLBACK only (backward compat)
```

**Benefits:**
- ✅ Fully config-driven
- ✅ One file to modify
- ✅ Customize prompts without code
- ✅ Version control friendly
- ✅ Easy deployment
- ✅ Backward compatible

## New Config Structure

### Complete Example

```json
{
  "name": "risk_analyst_agent",
  "description": "Specialized risk analysis agent",
  
  "model": {
    "name": "gpt-4",
    "temperature": 0.3,
    "max_tokens": 2000
  },
  
  "execution": {
    "max_iterations": 5,
    "timeout_seconds": 30
  },
  
  "tools": {
    "enabled": [
      "limits_exposure_analysis",
      "duckdb_olap_tools",
      "tavily"
    ]
  },
  
  "prompt": {
    "system": "You are a Risk Analysis Agent...\n\nAvailable Tools:\n{tools_description}\n\nMax iterations: {max_iterations}",
    
    "variables": {
      "tools_description": "auto_generated",
      "max_iterations": "from_execution"
    }
  },
  
  "response": {
    "format": "markdown",
    "style": "executive_summary",
    "include_metadata": true
  },
  
  "metadata": {
    "version": "2.0.0",
    "author": "Ashutosh Sinha",
    "tags": ["risk", "credit"]
  }
}
```

### Config Sections

| Section | Purpose | Required |
|---------|---------|----------|
| `name` | Agent identifier | ✅ Yes |
| `description` | Human-readable description | ✅ Yes |
| `model` | LLM configuration | No (defaults) |
| `execution` | Execution parameters | No (defaults) |
| `tools` | Enabled tools list | No (all if empty) |
| `prompt` | System prompt definition | ✅ Yes |
| `response` | Response formatting | No (defaults) |
| `metadata` | Versioning, tags, etc. | No |

### Prompt Variables

The prompt can include variables that get auto-replaced:

| Variable | Replaced With | Example |
|----------|---------------|---------|
| `{tools_description}` | Auto-generated tools list | "- limits_exposure_analysis: Analyze..." |
| `{max_iterations}` | From execution config | "5" |

## Implementation Details

### Updated Files

1. **config/agents/*.json** - All 3 agent configs updated
   - Added full `prompt` section
   - Added `model`, `execution`, `tools` structure
   - Version bumped to 2.0.0

2. **agent/agent_executor.py** - Added prompt loading logic
   - `_build_system_prompt()` - Loads from config or falls back
   - `_get_max_iterations()` - Reads from execution config
   - Updated `__init__` to handle new structure

3. **agent/prompts.py** - Marked as fallback
   - Added deprecation notice
   - Kept for backward compatibility

### Backward Compatibility

Old-style configs still work:

```json
{
  "name": "old_agent",
  "system_prompt_template": "default",
  "max_iterations": 5
}
```

Agent executor will:
1. Check for `prompt.system` in config
2. If not found, fall back to `system_prompt_template`
3. Use prompts.py templates

## Migration Guide

### For Existing Agents

**Option 1: Do Nothing** (backward compatible)
- Keep using `system_prompt_template`
- Will continue to work

**Option 2: Migrate to New Format**

1. Copy prompt from `agent/prompts.py`
2. Add to config JSON:
```json
{
  "prompt": {
    "system": "Your prompt here with\n{tools_description}\n{max_iterations}"
  }
}
```

3. Remove `system_prompt_template` field

### For New Agents

Just create one JSON file with all sections. See examples in `config/agents/`.

## Testing

### Tests Performed

✅ Load new config structure  
✅ Initialize agent with new config  
✅ Execute queries  
✅ All 3 agents work  
✅ CLI works  
✅ Backward compatibility  
✅ Prompt variables replaced correctly  

### Test Results

```bash
# Test new config
python run_agent.py --agent risk_analyst_agent "Check limits for AC001"
✅ Works - uses prompt from config

# Test old config (if any remain)
✅ Works - falls back to prompts.py
```

## Benefits Achieved

### 1. True Config-Driven Architecture

**Before:**
```bash
# To change prompt: Edit Python code
vim agent/prompts.py
# To change agent: Edit JSON
vim config/agents/risk_analyst_agent.json
```

**After:**
```bash
# To change anything: Edit one JSON
vim config/agents/risk_analyst_agent.json
```

### 2. No Code Deployments

Change prompts in production without code deploy:
```bash
# Update prompt
vim config/agents/risk_analyst_agent.json

# Restart service (picks up new config)
systemctl restart agent-service
```

### 3. A/B Testing

Easy to test different prompts:
```bash
cp risk_analyst_agent.json risk_analyst_agent_v2.json
# Edit v2 prompt
python run_agent.py --agent risk_analyst_agent_v2 "test"
```

### 4. Version Control

```bash
git diff config/agents/risk_analyst_agent.json
# See exactly what changed (prompt, config, everything)
```

### 5. Non-Developer Friendly

Product managers can modify prompts without touching code.

## Files Changed

### Modified
- `config/agents/default_agent.json` (v1.0.0 → v2.0.0)
- `config/agents/risk_analyst_agent.json` (v1.0.0 → v2.0.0)
- `config/agents/data_analyst_agent.json` (v1.0.0 → v2.0.0)
- `agent/agent_executor.py` (added prompt loading logic)
- `agent/prompts.py` (marked as fallback)

### Created
- `SINGLE_FILE_CONFIG_REFACTOR.md` (this file)

## Usage Examples

### Create New Agent

```json
{
  "name": "compliance_agent",
  "description": "Regulatory compliance specialist",
  
  "model": {
    "temperature": 0.2
  },
  
  "execution": {
    "max_iterations": 3
  },
  
  "tools": {
    "enabled": ["limits_exposure_analysis", "tavily"]
  },
  
  "prompt": {
    "system": "You are a Compliance Officer.\n\nMission:\n- Ensure regulatory compliance\n- Flag violations\n- Recommend actions\n\nTools:\n{tools_description}\n\nMax: {max_iterations} iterations"
  }
}
```

Save as `config/agents/compliance_agent.json` and use immediately!

### Customize Existing Agent

```bash
# Copy existing agent
cp config/agents/risk_analyst_agent.json config/agents/my_risk_agent.json

# Edit prompt section
vim config/agents/my_risk_agent.json
# Change: "prompt.system" to your custom prompt

# Use it
python run_agent.py --agent my_risk_agent "query"
```

## Future Enhancements

Possible additions to config:

```json
{
  "prompt": {
    "system": "...",
    "user_prefix": "User:",
    "assistant_prefix": "Assistant:",
    "examples": [
      {"user": "...", "assistant": "..."}
    ]
  },
  
  "memory": {
    "enabled": true,
    "max_messages": 10,
    "summarize_after": 5
  },
  
  "guardrails": {
    "max_cost_per_query": 0.50,
    "disallowed_tools": ["dangerous_tool"],
    "require_approval_for": ["sensitive_tool"]
  }
}
```

## Conclusion

Successfully refactored from scattered configuration to **single-file config**.

**Impact:**
- ✅ Truly config-driven
- ✅ Easier to manage
- ✅ Faster to customize
- ✅ Production-friendly
- ✅ Backward compatible

All agents now follow the **"everything in one JSON"** principle, matching the tools configuration pattern.

---

**Refactored by:** Ashutosh Sinha  
**Date:** October 27, 2025  
**Status:** Production Ready ✅

