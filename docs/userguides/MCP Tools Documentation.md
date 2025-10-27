# MCP Tools Documentation

**Copyright All Rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com**

## Welcome

This comprehensive documentation package covers the Model Context Protocol (MCP) Tools framework and its built-in tools. Each tool is documented with detailed usage examples, configuration instructions, and best practices for both Python client and Web UI usage.

---

## Documentation Index

### 📋 Overview

**[MCP Tools Overview](MCP_TOOLS_OVERVIEW.md)**
- System architecture and components
- Tool registry management
- General usage patterns
- Configuration guidelines
- API integration
- Performance metrics
- Best practices and troubleshooting

### 🔧 Individual Tool Documentation

#### 1. **[Wikipedia Tool](WIKIPEDIA_TOOL.md)**
**Category:** Information Retrieval  
**API Required:** No

**Features:**
- Article search
- Full page content retrieval
- Article summaries
- No authentication needed

**Use Cases:**
- Knowledge base queries
- Research assistance
- Content aggregation
- Educational applications

---

#### 2. **[Yahoo Finance Tool](YAHOO_FINANCE_TOOL.md)**
**Category:** Financial Data  
**API Required:** No

**Features:**
- Real-time stock quotes
- Historical price data
- Symbol search
- Market metrics

**Use Cases:**
- Portfolio tracking
- Market analysis
- Stock screening
- Technical analysis
- Financial reporting

---

#### 3. **[Google Search Tool](GOOGLE_SEARCH_TOOL.md)**
**Category:** Web Search  
**API Required:** Yes (Google Custom Search API)

**Features:**
- Web search
- Image search
- Site-restricted search
- Safe search filtering
- Pagination support

**Use Cases:**
- Content discovery
- Research and analysis
- Competitive intelligence
- SEO analysis
- Market research

**Setup Required:**
- Google Cloud Console API Key
- Custom Search Engine ID
- [Setup Instructions](GOOGLE_SEARCH_TOOL.md#setup-requirements)

---

#### 4. **[Federal Reserve Tool](FED_RESERVE_TOOL.md)**
**Category:** Economic Data  
**API Required:** Yes (FRED API - Free)

**Features:**
- Economic indicators (GDP, unemployment, inflation, etc.)
- Historical time series data
- Series search
- Common indicators dashboard

**Use Cases:**
- Economic analysis
- Market research
- Policy analysis
- Financial forecasting
- Academic research

**Setup Required:**
- FRED API Key (free)
- [Setup Instructions](FED_RESERVE_TOOL.md#setup-requirements)

---

## Quick Start Guide

### Installation

1. **Clone or download the repository**
   ```bash
   git clone <repository-url>
   cd mcp-tools
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure tools**
   - Edit configuration files in `config/tools/`
   - Add API keys where required
   - See individual tool documentation for setup details

### Basic Python Usage

```python
from tools.tools_registry import ToolsRegistry

# Initialize registry (singleton)
registry = ToolsRegistry()

# Get a tool
tool = registry.get_tool('wikipedia')

# Execute tool
result = tool.execute_with_tracking({
    'action': 'search',
    'query': 'Python programming'
})

print(result)
```

### Web UI Access

1. **Start the server**
   ```bash
   python app.py
   ```

2. **Open browser**
   ```
   http://localhost:5000
   ```

3. **Navigate to Tools**
   ```
   http://localhost:5000/tools
   ```

4. **Select and execute a tool**

---

## Tool Comparison Matrix

| Feature | Wikipedia | Yahoo Finance | Google Search | Federal Reserve |
|---------|-----------|---------------|---------------|-----------------|
| **API Key Required** | ❌ No | ❌ No | ✅ Yes | ✅ Yes (free) |
| **Rate Limit** | 100/hour | 60/hour | 100/day (free) | 120/min |
| **Cache TTL** | 1 hour | 5 minutes | 1 hour | 1 hour |
| **Demo Mode** | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| **Real-time Data** | ❌ No | ✅ Yes | ✅ Yes | ❌ No |
| **Historical Data** | ❌ No | ✅ Yes | ❌ No | ✅ Yes |
| **Search Capability** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |

---

## Common Use Cases

### 1. Research Assistant

**Tools Used:** Wikipedia, Google Search, Federal Reserve

```python
# Search Wikipedia for overview
wiki_result = wiki_tool.execute_with_tracking({
    'action': 'get_summary',
    'query': 'Artificial Intelligence'
})

# Get detailed web search results
search_result = search_tool.execute_with_tracking({
    'query': 'artificial intelligence applications 2025',
    'num_results': 10
})

# Get relevant economic data
fred_result = fred_tool.execute_with_tracking({
    'action': 'search_series',
    'query': 'technology investment'
})
```

### 2. Financial Analysis

**Tools Used:** Yahoo Finance, Federal Reserve

```python
# Get stock data
stock_quote = finance_tool.execute_with_tracking({
    'action': 'get_quote',
    'symbol': 'AAPL'
})

# Get economic context
fed_rate = fred_tool.execute_with_tracking({
    'action': 'get_latest',
    'indicator': 'fed_rate'
})
```

### 3. Market Intelligence

**Tools Used:** Google Search, Yahoo Finance, Wikipedia

```python
# Search for company information
company_search = search_tool.execute_with_tracking({
    'query': 'Tesla inc',
    'num_results': 10
})

# Get stock performance
stock_data = finance_tool.execute_with_tracking({
    'action': 'get_history',
    'symbol': 'TSLA',
    'period': '1y'
})

# Get company background
company_info = wiki_tool.execute_with_tracking({
    'action': 'get_summary',
    'query': 'Tesla, Inc.'
})
```

---

## Configuration

### Tool Configuration Files

All tools are configured via JSON files in `config/tools/`:

```
config/tools/
├── wikipedia.json
├── yahoo_finance.json
├── google_search.json
└── fed_reserve.json
```

### Configuration Structure

```json
{
  "name": "tool_name",
  "type": "tool_type",
  "description": "Tool description",
  "version": "1.0.0",
  "enabled": true,
  "api_key": "YOUR_API_KEY",
  "inputSchema": { ... },
  "metadata": { ... }
}
```

### Hot Reloading

The tool registry monitors configuration files and automatically reloads tools when:
- New configuration file is added
- Existing configuration is modified
- Configuration file is deleted

---

## API Integration

### REST API Endpoints

```python
# List all tools
GET /api/tools/list

# Get tool details
GET /api/tools/<tool_name>

# Execute tool
POST /api/tools/execute
{
  "tool": "tool_name",
  "arguments": { ... }
}

# Get metrics
GET /api/tools/metrics
```

### Example API Call

```python
import requests

response = requests.post(
    'http://localhost:5000/api/tools/execute',
    json={
        'tool': 'wikipedia',
        'arguments': {
            'action': 'search',
            'query': 'Python programming'
        }
    }
)

result = response.json()
```

---

## Best Practices

### 1. Error Handling

Always wrap tool execution in try-except blocks:

```python
try:
    result = tool.execute_with_tracking(arguments)
    # Process result
except ValueError as e:
    # Handle validation errors
    print(f"Validation error: {e}")
except RuntimeError as e:
    # Handle execution errors
    print(f"Execution error: {e}")
except Exception as e:
    # Handle unexpected errors
    print(f"Unexpected error: {e}")
```

### 2. Rate Limiting

Implement delays between requests:

```python
import time

for query in queries:
    result = tool.execute_with_tracking({'query': query})
    time.sleep(1)  # 1 second delay
```

### 3. Caching

Use caching for frequently accessed data:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_data(query):
    return tool.execute_with_tracking({'query': query})
```

### 4. Input Validation

Validate inputs before execution:

```python
def validate_arguments(arguments, schema):
    required = schema.get('required', [])
    for param in required:
        if param not in arguments:
            raise ValueError(f"Missing required parameter: {param}")
    return True
```

---

## Troubleshooting

### Common Issues

#### Tool Not Loading

**Symptoms:** Tool not appearing in registry

**Solutions:**
1. Check configuration file syntax (valid JSON)
2. Verify file is in `config/tools/` directory
3. Check tool type matches builtin_tools mapping
4. Review application logs for errors

#### API Authentication Failures

**Symptoms:** HTTP 401/403 errors

**Solutions:**
1. Verify API key is correct
2. Check API key permissions
3. Ensure API is enabled in provider console
4. Check rate limits haven't been exceeded

#### Slow Performance

**Symptoms:** Long execution times

**Solutions:**
1. Implement caching
2. Reduce number of results requested
3. Use pagination for large datasets
4. Check network latency
5. Review rate limiting configuration

#### Demo Mode Not Working

**Symptoms:** Errors even without API key

**Solutions:**
1. Ensure tool implements demo mode
2. Check configuration has demo mode enabled
3. Review tool-specific documentation

---

## Performance Optimization

### Metrics Monitoring

```python
# Get tool metrics
registry = ToolsRegistry()
metrics = registry.get_tool_metrics()

for metric in metrics:
    print(f"Tool: {metric['name']}")
    print(f"  Executions: {metric['execution_count']}")
    print(f"  Avg Time: {metric['average_execution_time']:.2f}s")
```

### Optimization Strategies

1. **Implement Caching**
   - Cache frequently accessed data
   - Use appropriate cache TTL
   - Clear cache when data becomes stale

2. **Batch Operations**
   - Group related requests
   - Use async processing for multiple tools
   - Implement request queuing

3. **Resource Management**
   - Close connections properly
   - Limit concurrent requests
   - Monitor memory usage

4. **Query Optimization**
   - Use specific queries
   - Limit result sets
   - Filter data server-side when possible

---

## Development

### Creating Custom Tools

1. **Create tool class**
   ```python
   from tools.base_mcp_tool import BaseMCPTool
   
   class MyCustomTool(BaseMCPTool):
       def get_input_schema(self):
           return { ... }
       
       def execute(self, arguments):
           # Implementation
           pass
   ```

2. **Create configuration file**
   ```json
   {
     "name": "my_custom_tool",
     "type": "custom",
     "implementation": "tools.impl.my_custom_tool.MyCustomTool",
     ...
   }
   ```

3. **Place configuration in `config/tools/`**

4. **Tool will be auto-loaded by registry**

---

## Testing

### Unit Testing

```python
import unittest
from tools.tools_registry import ToolsRegistry

class TestWikipediaTool(unittest.TestCase):
    def setUp(self):
        self.registry = ToolsRegistry()
        self.tool = self.registry.get_tool('wikipedia')
    
    def test_search(self):
        result = self.tool.execute_with_tracking({
            'action': 'search',
            'query': 'Python programming',
            'limit': 5
        })
        self.assertIn('results', result)
        self.assertGreater(len(result['results']), 0)
```

### Integration Testing

```python
def test_multi_tool_workflow():
    registry = ToolsRegistry()
    
    # Test tool chaining
    wiki_result = registry.get_tool('wikipedia').execute_with_tracking({
        'action': 'search',
        'query': 'Apple Inc'
    })
    
    # Use result to search for stock
    if wiki_result['results']:
        finance_result = registry.get_tool('yahoo_finance').execute_with_tracking({
            'action': 'search_symbols',
            'query': 'Apple'
        })
```

---

## Security Considerations

### API Key Management

1. **Never commit API keys to version control**
   - Use environment variables
   - Use secure key storage
   - Rotate keys regularly

2. **Restrict API key permissions**
   - Use minimum required permissions
   - Enable IP restrictions where available
   - Monitor API key usage

3. **Implement rate limiting**
   - Prevent abuse
   - Protect against attacks
   - Control costs

### Input Validation

1. **Sanitize user inputs**
2. **Validate against schema**
3. **Prevent injection attacks**
4. **Limit input size**

---

## Support and Resources

### Documentation

- [MCP Tools Overview](MCP_TOOLS_OVERVIEW.md)
- [Wikipedia Tool](WIKIPEDIA_TOOL.md)
- [Yahoo Finance Tool](YAHOO_FINANCE_TOOL.md)
- [Google Search Tool](GOOGLE_SEARCH_TOOL.md)
- [Federal Reserve Tool](FED_RESERVE_TOOL.md)

### External Resources

- **Wikipedia API:** https://www.mediawiki.org/wiki/API:Main_page
- **Yahoo Finance:** https://finance.yahoo.com
- **Google Custom Search:** https://developers.google.com/custom-search
- **FRED API:** https://fred.stlouisfed.org/docs/api/

### Support Contact

For questions, issues, or contributions:

**Ashutosh Sinha**  
Email: ajsinha@gmail.com

---

## License

Copyright All Rights Reserved 2025-2030  
Ashutosh Sinha  
Email: ajsinha@gmail.com

---

## Version History

- **v1.0.0** (October 2025)
  - Initial release
  - Four built-in tools (Wikipedia, Yahoo Finance, Google Search, Federal Reserve)
  - Web UI interface
  - Tool registry with hot reloading
  - Comprehensive documentation

---

## Acknowledgments

This project uses the following external APIs:
- Wikipedia API
- Yahoo Finance API
- Google Custom Search API
- Federal Reserve Economic Data (FRED) API

Special thanks to all API providers for making their data accessible.

---

*Last Updated: October 26, 2025*