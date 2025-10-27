# Tavily Search Tool Documentation

**Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com**

## Overview

The Tavily Search Tool is an AI-powered web search tool that provides intelligent search results with optional AI-generated summaries. It leverages the Tavily API to deliver high-quality, relevant search results optimized for AI applications and research.

## Features

- **AI-Powered Search**: Advanced search capabilities optimized for AI agents
- **Intelligent Summarization**: Optional AI-generated answer summaries
- **Flexible Search Depth**: Choose between basic (fast) and advanced (comprehensive) search
- **Topic Categorization**: Filter results by topic (general, news, finance, science)
- **Domain Filtering**: Include or exclude specific domains
- **Image Search**: Optionally retrieve relevant images
- **Raw Content Access**: Get full HTML content when needed

## Installation

### Prerequisites

- Python 3.8 or higher
- Tavily API key (get one at [https://tavily.com](https://tavily.com))

### Setup

1. **Copy the tool files to your project:**
   ```bash
   # Copy tool implementation
   cp tavily_tool.py /path/to/your/project/tools/impl/
   
   # Copy configuration
   cp tavily.json /path/to/your/project/config/tools/
   ```

2. **Configure API Key:**
   
   Edit `config/tools/tavily.json` and add your API key:
   ```json
   {
     "api_key": "tvly-YOUR_API_KEY_HERE",
     ...
   }
   ```

3. **Update Registry:**
   
   Add to `tools_registry.py`:
   ```python
   self.builtin_tools = {
       ...
       'tavily': 'tools.impl.tavily_tool.TavilyTool'
   }
   ```

## Configuration

### JSON Configuration File (`tavily.json`)

```json
{
  "name": "tavily",
  "type": "tavily",
  "description": "AI-powered web search using Tavily API",
  "version": "1.0.0",
  "enabled": true,
  "api_key": "tvly-YOUR_API_KEY_HERE",
  "inputSchema": { ... },
  "metadata": {
    "author": "Ashutosh Sinha",
    "category": "Web Search",
    "tags": ["search", "tavily", "ai", "web"],
    "rateLimit": 100,
    "cacheTTL": 3600
  }
}
```

### Configuration Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `name` | string | Tool name | Yes |
| `type` | string | Tool type identifier | Yes |
| `api_key` | string | Tavily API key | Yes (for production) |
| `enabled` | boolean | Enable/disable tool | No (default: true) |
| `rateLimit` | integer | Max requests per minute | No |
| `cacheTTL` | integer | Cache time in seconds | No |

## Usage

### Input Schema

```json
{
  "query": "string (required)",
  "search_depth": "basic|advanced (default: basic)",
  "topic": "general|news|finance|science (default: general)",
  "max_results": "integer (1-20, default: 5)",
  "include_answer": "boolean (default: true)",
  "include_raw_content": "boolean (default: false)",
  "include_images": "boolean (default: false)",
  "include_domains": ["array of strings"],
  "exclude_domains": ["array of strings"]
}
```

### Parameters Description

- **query** (required): The search query string
- **search_depth**: 
  - `basic`: Fast, returns top results quickly
  - `advanced`: Comprehensive search with deeper analysis
- **topic**: Category filter for specialized searches
- **max_results**: Number of results to return (1-20)
- **include_answer**: Get AI-generated summary of results
- **include_raw_content**: Include full HTML content of pages
- **include_images**: Retrieve relevant images
- **include_domains**: Restrict search to specific domains
- **exclude_domains**: Exclude specific domains from search

## Programmatic Usage (Python)

### Method 1: Direct Tool Invocation

```python
from tools.impl.tavily_tool import TavilyTool

# Initialize tool with configuration
config = {
    'name': 'tavily',
    'api_key': 'tvly-YOUR_API_KEY_HERE',
    'enabled': True
}

tool = TavilyTool(config)

# Example 1: Basic Search
arguments = {
    'query': 'artificial intelligence trends 2024',
    'max_results': 5
}

result = tool.execute_with_tracking(arguments)
print(result)
```

**Output:**
```json
{
  "query": "artificial intelligence trends 2024",
  "search_depth": "basic",
  "topic": "general",
  "results_count": 5,
  "results": [
    {
      "title": "Top AI Trends to Watch in 2024",
      "url": "https://example.com/ai-trends-2024",
      "content": "The artificial intelligence landscape is...",
      "score": 0.95,
      "published_date": "2024-10-15"
    },
    ...
  ],
  "answer": "In 2024, key AI trends include..."
}
```

### Method 2: Advanced Search with Filters

```python
# Example 2: Advanced Search with Domain Filtering
arguments = {
    'query': 'climate change research',
    'search_depth': 'advanced',
    'topic': 'science',
    'max_results': 10,
    'include_answer': True,
    'include_images': True,
    'include_domains': ['nature.com', 'science.org', 'nasa.gov']
}

result = tool.execute_with_tracking(arguments)

# Access AI-generated answer
print(f"AI Summary: {result['answer']}")

# Access search results
for item in result['results']:
    print(f"Title: {item['title']}")
    print(f"URL: {item['url']}")
    print(f"Score: {item['score']}")
    print(f"Content: {item['content'][:200]}...")
    print("---")

# Access images if included
if 'images' in result:
    for img in result['images']:
        print(f"Image: {img['url']}")
```

### Method 3: Using Tools Registry

```python
from tools.tools_registry import ToolsRegistry

# Get registry instance
registry = ToolsRegistry('config/tools')

# Get the tool
tavily_tool = registry.get_tool('tavily')

# Execute search
arguments = {
    'query': 'stock market analysis',
    'topic': 'finance',
    'max_results': 7,
    'include_answer': True
}

result = tavily_tool.execute_with_tracking(arguments)
```

### Method 4: News Search Example

```python
# Example 3: News Search
arguments = {
    'query': 'technology breakthroughs',
    'search_depth': 'basic',
    'topic': 'news',
    'max_results': 5,
    'include_answer': True,
    'exclude_domains': ['reddit.com', 'twitter.com']  # Exclude social media
}

result = tool.execute_with_tracking(arguments)

print(f"Query: {result['query']}")
print(f"AI Answer: {result['answer']}")
print(f"\nTop {result['results_count']} News Results:")

for idx, item in enumerate(result['results'], 1):
    print(f"\n{idx}. {item['title']}")
    print(f"   Published: {item['published_date']}")
    print(f"   Relevance: {item['score']}")
    print(f"   {item['content'][:150]}...")
```

### Method 5: Raw Content Extraction

```python
# Example 4: Get Raw Content for Web Scraping
arguments = {
    'query': 'machine learning tutorials',
    'max_results': 3,
    'include_raw_content': True,
    'include_answer': False
}

result = tool.execute_with_tracking(arguments)

for item in result['results']:
    print(f"Extracting content from: {item['url']}")
    
    # Access raw HTML if needed
    if 'raw_content' in item:
        raw_html = item['raw_content']
        # Process raw HTML as needed
        print(f"Raw content length: {len(raw_html)} characters")
```

### Error Handling

```python
try:
    result = tool.execute_with_tracking(arguments)
    
    if result['results_count'] == 0:
        print("No results found")
    else:
        # Process results
        pass
        
except ValueError as e:
    print(f"Validation error: {e}")
except RuntimeError as e:
    print(f"Tool execution error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Web UI Usage

### Accessing the Tool

1. **Navigate to Tools List:**
   - Open your web browser
   - Go to `http://your-server:port/tools`
   - Find "tavily" in the tools list

2. **Click "Execute" button** next to the Tavily tool

### Basic Search via Web UI

**Step 1: Fill in the form**

```
Query: artificial intelligence applications
Search Depth: basic
Topic: general
Max Results: 5
Include Answer: ✓ (checked)
Include Raw Content: ☐ (unchecked)
Include Images: ☐ (unchecked)
```

**Step 2: Click "Execute Tool" button**

**Step 3: View Results**

The results will display in the right panel:
```json
{
  "query": "artificial intelligence applications",
  "search_depth": "basic",
  "topic": "general",
  "results_count": 5,
  "results": [
    {
      "title": "Top AI Applications in 2024",
      "url": "https://example.com/ai-apps",
      "content": "Artificial intelligence is being applied...",
      "score": 0.93,
      "published_date": "2024-10-20"
    }
  ],
  "answer": "AI applications span multiple industries..."
}
```

### Advanced Search with Filters via Web UI

**Step 1: Configure Advanced Parameters**

```
Query: renewable energy innovations
Search Depth: advanced
Topic: science
Max Results: 10
Include Answer: ✓
Include Raw Content: ☐
Include Images: ✓
Include Domains: nature.com,science.org (comma-separated)
Exclude Domains: (leave empty)
```

**Step 2: Execute and Review**

The Web UI will display:
- AI-generated answer summary
- List of search results with titles, URLs, and snippets
- Relevance scores
- Published dates
- Image results (if requested)

### News Search via Web UI

**Sample Input:**
```
Query: latest tech news
Search Depth: basic
Topic: news
Max Results: 7
Include Answer: ✓
Include Raw Content: ☐
Include Images: ☐
Include Domains: (leave empty)
Exclude Domains: reddit.com,twitter.com
```

### Finance Search via Web UI

**Sample Input:**
```
Query: cryptocurrency market analysis
Search Depth: advanced
Topic: finance
Max Results: 8
Include Answer: ✓
Include Raw Content: ☐
Include Images: ☐
Include Domains: bloomberg.com,reuters.com,coindesk.com
Exclude Domains: (leave empty)
```

## API Endpoint Usage

### REST API Call

```bash
# Using curl
curl -X POST http://your-server:port/api/tools/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -d '{
    "tool": "tavily",
    "arguments": {
      "query": "quantum computing advances",
      "search_depth": "advanced",
      "topic": "science",
      "max_results": 5,
      "include_answer": true
    }
  }'
```

### Python Requests

```python
import requests
import json

# API endpoint
url = "http://your-server:port/api/tools/execute"

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_SESSION_TOKEN"
}

# Request payload
payload = {
    "tool": "tavily",
    "arguments": {
        "query": "space exploration missions",
        "search_depth": "basic",
        "topic": "science",
        "max_results": 5,
        "include_answer": True,
        "include_images": True
    }
}

# Make request
response = requests.post(url, headers=headers, json=payload)

# Process response
if response.status_code == 200:
    result = response.json()
    
    if result['success']:
        data = result['result']
        print(f"Answer: {data.get('answer', 'N/A')}")
        print(f"\nResults ({data['results_count']}):")
        
        for item in data['results']:
            print(f"- {item['title']}")
            print(f"  {item['url']}")
    else:
        print(f"Error: {result['error']}")
else:
    print(f"HTTP Error: {response.status_code}")
```

## Response Format

### Successful Response

```json
{
  "query": "search query",
  "search_depth": "basic|advanced",
  "topic": "general|news|finance|science",
  "results_count": 5,
  "results": [
    {
      "title": "Result Title",
      "url": "https://example.com/page",
      "content": "Snippet of the content...",
      "score": 0.95,
      "published_date": "2024-10-15"
    }
  ],
  "answer": "AI-generated summary (if requested)",
  "images": [
    {
      "url": "https://example.com/image.jpg",
      "description": "Image description"
    }
  ]
}
```

### Field Descriptions

- **query**: Original search query
- **search_depth**: Depth of search performed
- **topic**: Topic category used
- **results_count**: Number of results returned
- **results**: Array of search results
  - **title**: Page title
  - **url**: Page URL
  - **content**: Content snippet
  - **score**: Relevance score (0-1)
  - **published_date**: Publication date (if available)
- **answer**: AI-generated summary (optional)
- **images**: Relevant images (optional)

## Demo Mode

If no API key is configured, the tool operates in demo mode:

```python
# Demo mode automatically activated without API key
config = {
    'name': 'tavily',
    'api_key': '',  # Empty = demo mode
    'enabled': True
}

tool = TavilyTool(config)

# Execute in demo mode
result = tool.execute_with_tracking({
    'query': 'machine learning',
    'max_results': 3
})

# Result will include note about demo mode
print(result['note'])  # "Demo mode - Configure Tavily API key..."
```

Demo mode returns realistic sample data for testing without API access.

## Rate Limiting

- **Default Rate Limit**: 100 requests per minute
- **Configurable**: Adjust in `tavily.json`
- **Tavily API Limits**: Depend on your subscription plan

## Caching

- **Default Cache TTL**: 3600 seconds (1 hour)
- **Configurable**: Adjust `cacheTTL` in configuration
- **Benefits**: Reduces API calls for repeated queries

## Best Practices

### 1. Choose Appropriate Search Depth

```python
# Use 'basic' for quick lookups
arguments = {'query': 'Python tutorial', 'search_depth': 'basic'}

# Use 'advanced' for research
arguments = {'query': 'climate change impacts', 'search_depth': 'advanced'}
```

### 2. Use Topic Filters

```python
# Categorize searches for better results
arguments = {
    'query': 'stock market crash',
    'topic': 'finance'  # More relevant results
}
```

### 3. Implement Domain Filtering

```python
# Academic research
arguments = {
    'query': 'peer-reviewed AI studies',
    'include_domains': ['.edu', '.gov', 'nature.com', 'science.org']
}

# Exclude unreliable sources
arguments = {
    'query': 'health information',
    'exclude_domains': ['reddit.com', 'quora.com']
}
```

### 4. Handle Errors Gracefully

```python
def safe_search(query, **kwargs):
    try:
        result = tool.execute_with_tracking({
            'query': query,
            **kwargs
        })
        return result
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        return None
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return None
```

## Troubleshooting

### Issue: "Invalid API key" error

**Solution:**
1. Verify API key in `tavily.json`
2. Check key format: `tvly-...`
3. Ensure key is active on Tavily dashboard

### Issue: "Rate limit exceeded" error

**Solution:**
1. Reduce request frequency
2. Implement caching
3. Upgrade Tavily plan

### Issue: No results returned

**Solution:**
1. Broaden search query
2. Try different topic categories
3. Remove restrictive domain filters
4. Use 'advanced' search depth

### Issue: Low-quality results

**Solution:**
1. Refine search query
2. Use domain filtering
3. Increase `max_results`
4. Try different topic categories

## Tool Metrics

Access tool metrics programmatically:

```python
# Get tool metrics
metrics = tool.get_metrics()

print(f"Execution count: {metrics['execution_count']}")
print(f"Last execution: {metrics['last_execution']}")
print(f"Average time: {metrics['average_execution_time']:.2f}s")
```

## Support and Resources

- **Tavily API Documentation**: [https://docs.tavily.com](https://docs.tavily.com)
- **Get API Key**: [https://tavily.com](https://tavily.com)
- **Tool Support**: ajsinha@gmail.com

## License

Copyright All rights Reserved 2025-2030, Ashutosh Sinha

## Version History

- **v1.0.0** (2024-10-26): Initial release
  - Basic and advanced search
  - AI-powered summaries
  - Domain filtering
  - Image search support
  - Multiple topic categories

## Examples Summary

### Quick Reference

```python
# 1. Basic search
tool.execute_with_tracking({'query': 'AI trends'})

# 2. Advanced with answer
tool.execute_with_tracking({
    'query': 'quantum computing',
    'search_depth': 'advanced',
    'include_answer': True
})

# 3. News search
tool.execute_with_tracking({
    'query': 'tech news',
    'topic': 'news',
    'max_results': 10
})

# 4. Domain-filtered research
tool.execute_with_tracking({
    'query': 'scientific studies',
    'include_domains': ['.edu', '.gov'],
    'search_depth': 'advanced'
})

# 5. With images
tool.execute_with_tracking({
    'query': 'data visualization',
    'include_images': True,
    'max_results': 5
})
```

---

**End of Documentation**