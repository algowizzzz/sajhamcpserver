# Wikipedia Tool Documentation

**Copyright All Rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com**

## Table of Contents

1. [Overview](#overview)
2. [Configuration](#configuration)
3. [Actions](#actions)
4. [Python Client Usage](#python-client-usage)
5. [Web UI Usage](#web-ui-usage)
6. [Examples](#examples)
7. [Error Handling](#error-handling)

---

## Overview

The Wikipedia Tool provides programmatic access to Wikipedia's vast knowledge base. It allows you to search for articles, retrieve full page content, and get article summaries.

### Features

- **Article Search**: Find Wikipedia articles by keywords
- **Full Page Content**: Retrieve complete article text
- **Article Summaries**: Get concise article introductions
- **No API Key Required**: Uses Wikipedia's free public API
- **Multi-language Support**: Can be extended for different Wikipedia languages

### Specifications

- **Tool Name**: `wikipedia`
- **Category**: Information Retrieval
- **API Endpoint**: `https://en.wikipedia.org/w/api.php`
- **Rate Limit**: 100 requests/hour (configurable)
- **Cache TTL**: 3600 seconds (1 hour)
- **Authentication**: Not required

---

## Configuration

### Configuration File

Location: `config/tools/wikipedia.json`

```json
{
  "name": "wikipedia",
  "type": "wikipedia",
  "description": "Search and retrieve information from Wikipedia",
  "version": "1.0.0",
  "enabled": true,
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "description": "Action to perform",
        "enum": ["search", "get_page", "get_summary"]
      },
      "query": {
        "type": "string",
        "description": "Search query or page title"
      },
      "limit": {
        "type": "integer",
        "description": "Maximum number of results (for search)",
        "default": 5,
        "minimum": 1,
        "maximum": 20
      }
    },
    "required": ["action", "query"]
  },
  "metadata": {
    "author": "Ashutosh Sinha",
    "category": "Information Retrieval",
    "tags": ["wikipedia", "search", "knowledge"],
    "rateLimit": 100,
    "cacheTTL": 3600
  }
}
```

### Configuration Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| name | string | Yes | Tool identifier |
| type | string | Yes | Must be "wikipedia" |
| enabled | boolean | No | Enable/disable tool (default: true) |
| version | string | No | Tool version |

---

## Actions

### 1. search

Search Wikipedia for articles matching a query.

**Parameters:**
- `action`: "search" (required)
- `query`: Search keywords (required)
- `limit`: Number of results to return (optional, default: 5, max: 20)

**Returns:**
```json
{
  "query": "search query",
  "count": 5,
  "results": [
    {
      "title": "Article Title",
      "description": "Brief description",
      "url": "https://en.wikipedia.org/wiki/Article_Title"
    }
  ]
}
```

### 2. get_page

Retrieve the full content of a Wikipedia page.

**Parameters:**
- `action`: "get_page" (required)
- `query`: Page title (required)

**Returns:**
```json
{
  "title": "Page Title",
  "pageid": 12345,
  "content": "Full article text...",
  "url": "https://en.wikipedia.org/wiki/Page_Title"
}
```

### 3. get_summary

Get a summary (first 5 sentences) of a Wikipedia page.

**Parameters:**
- `action`: "get_summary" (required)
- `query`: Page title (required)

**Returns:**
```json
{
  "title": "Page Title",
  "pageid": 12345,
  "summary": "Summary text (first 5 sentences)...",
  "url": "https://en.wikipedia.org/wiki/Page_Title"
}
```

---

## Python Client Usage

### Basic Setup

```python
from tools.tools_registry import ToolsRegistry

# Initialize registry
registry = ToolsRegistry()

# Get Wikipedia tool
wiki_tool = registry.get_tool('wikipedia')

# Check if tool is available
if wiki_tool is None:
    print("Wikipedia tool not found")
    exit(1)

# Check if tool is enabled
if not wiki_tool.enabled:
    print("Wikipedia tool is disabled")
    exit(1)
```

### Example 1: Search for Articles

```python
from tools.tools_registry import ToolsRegistry
import json

# Get tool
registry = ToolsRegistry()
wiki_tool = registry.get_tool('wikipedia')

# Search for articles
arguments = {
    'action': 'search',
    'query': 'Python programming',
    'limit': 5
}

try:
    result = wiki_tool.execute_with_tracking(arguments)
    print(json.dumps(result, indent=2))
    
    # Process results
    for article in result['results']:
        print(f"\nTitle: {article['title']}")
        print(f"Description: {article['description']}")
        print(f"URL: {article['url']}")
        
except Exception as e:
    print(f"Error: {e}")
```

**Sample Output:**
```json
{
  "query": "Python programming",
  "count": 5,
  "results": [
    {
      "title": "Python (programming language)",
      "description": "High-level programming language",
      "url": "https://en.wikipedia.org/wiki/Python_(programming_language)"
    },
    {
      "title": "History of Python",
      "description": "History of the Python programming language",
      "url": "https://en.wikipedia.org/wiki/History_of_Python"
    }
  ]
}
```

### Example 2: Get Page Content

```python
from tools.tools_registry import ToolsRegistry
import json

registry = ToolsRegistry()
wiki_tool = registry.get_tool('wikipedia')

# Get full page content
arguments = {
    'action': 'get_page',
    'query': 'Artificial intelligence'
}

try:
    result = wiki_tool.execute_with_tracking(arguments)
    
    print(f"Title: {result['title']}")
    print(f"Page ID: {result['pageid']}")
    print(f"URL: {result['url']}")
    print(f"\nContent ({len(result['content'])} characters):")
    print(result['content'][:500] + "...")
    
except ValueError as e:
    print(f"Page not found: {e}")
except Exception as e:
    print(f"Error: {e}")
```

### Example 3: Get Page Summary

```python
from tools.tools_registry import ToolsRegistry

registry = ToolsRegistry()
wiki_tool = registry.get_tool('wikipedia')

# Get page summary
arguments = {
    'action': 'get_summary',
    'query': 'Machine Learning'
}

try:
    result = wiki_tool.execute_with_tracking(arguments)
    
    print(f"Title: {result['title']}")
    print(f"\nSummary:")
    print(result['summary'])
    print(f"\nRead more: {result['url']}")
    
except Exception as e:
    print(f"Error: {e}")
```

**Sample Output:**
```
Title: Machine Learning

Summary:
Machine learning (ML) is a field of study in artificial intelligence 
concerned with the development and study of statistical algorithms that 
can learn from data and generalize to unseen data. Machine learning 
algorithms build a model based on sample data, known as training data, 
in order to make predictions or decisions without being explicitly 
programmed to do so.

Read more: https://en.wikipedia.org/wiki/Machine_Learning
```

### Example 4: Batch Processing

```python
from tools.tools_registry import ToolsRegistry

registry = ToolsRegistry()
wiki_tool = registry.get_tool('wikipedia')

# List of topics to search
topics = ['Quantum Computing', 'Blockchain', 'Neural Networks']

summaries = {}

for topic in topics:
    try:
        result = wiki_tool.execute_with_tracking({
            'action': 'get_summary',
            'query': topic
        })
        summaries[topic] = result['summary']
        print(f"✓ Retrieved: {topic}")
    except Exception as e:
        print(f"✗ Failed: {topic} - {e}")

# Display summaries
for topic, summary in summaries.items():
    print(f"\n{topic}:")
    print(summary[:200] + "...")
```

### Example 5: Error Handling

```python
from tools.tools_registry import ToolsRegistry

registry = ToolsRegistry()
wiki_tool = registry.get_tool('wikipedia')

def search_wikipedia(query, action='search', limit=5):
    """
    Safe Wikipedia search with comprehensive error handling
    """
    try:
        # Validate action
        valid_actions = ['search', 'get_page', 'get_summary']
        if action not in valid_actions:
            return {
                'success': False,
                'error': f'Invalid action. Must be one of: {valid_actions}'
            }
        
        # Prepare arguments
        arguments = {
            'action': action,
            'query': query
        }
        
        if action == 'search':
            arguments['limit'] = limit
        
        # Execute tool
        result = wiki_tool.execute_with_tracking(arguments)
        
        return {
            'success': True,
            'data': result
        }
        
    except ValueError as e:
        # Page not found or validation error
        return {
            'success': False,
            'error': f'Validation error: {str(e)}'
        }
    except RuntimeError as e:
        # Tool disabled or execution error
        return {
            'success': False,
            'error': f'Execution error: {str(e)}'
        }
    except Exception as e:
        # Unexpected error
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }

# Usage
result = search_wikipedia('Python programming', action='search', limit=3)
if result['success']:
    print(result['data'])
else:
    print(f"Error: {result['error']}")
```

---

## Web UI Usage

### Accessing the Tool

1. **Navigate to Tools Page**
   ```
   http://localhost:5000/tools
   ```

2. **Select Wikipedia Tool**
   - Find "wikipedia" in the tools list
   - Click "Execute" button or tool name

3. **Execute Tool Page**
   ```
   http://localhost:5000/tools/execute/wikipedia
   ```

### Using the Web Interface

#### Search for Articles

1. **Select Action**: Choose "search" from dropdown
2. **Enter Query**: Type your search keywords
3. **Set Limit**: Choose number of results (1-20)
4. **Execute**: Click "Execute Tool" button

**Example Input:**
```
Action: search
Query: Artificial Intelligence
Limit: 10
```

**Result Display:**
```json
{
  "query": "Artificial Intelligence",
  "count": 10,
  "results": [
    {
      "title": "Artificial intelligence",
      "description": "Intelligence of machines or software",
      "url": "https://en.wikipedia.org/wiki/Artificial_intelligence"
    },
    ...
  ]
}
```

#### Get Full Page Content

1. **Select Action**: Choose "get_page"
2. **Enter Query**: Type exact page title
3. **Execute**: Click "Execute Tool" button

**Example Input:**
```
Action: get_page
Query: Machine Learning
```

#### Get Page Summary

1. **Select Action**: Choose "get_summary"
2. **Enter Query**: Type page title
3. **Execute**: Click "Execute Tool" button

**Example Input:**
```
Action: get_summary
Query: Deep Learning
```

### Web UI Features

- **Dynamic Form**: Form fields adjust based on selected action
- **Validation**: Required fields are marked with red asterisk (*)
- **Real-time Results**: Results appear immediately after execution
- **Execution History**: Last 5 executions shown in sidebar
- **Clear Button**: Reset form to start fresh
- **JSON Formatting**: Results displayed with syntax highlighting

---

## Examples

### Complete Working Examples

#### Example 1: Research Assistant

```python
from tools.tools_registry import ToolsRegistry
import time

class WikipediaResearchAssistant:
    def __init__(self):
        registry = ToolsRegistry()
        self.wiki_tool = registry.get_tool('wikipedia')
    
    def research_topic(self, topic):
        """
        Comprehensive research on a topic
        """
        print(f"Researching: {topic}")
        print("=" * 50)
        
        # Step 1: Search for related articles
        print("\n1. Searching for articles...")
        search_result = self.wiki_tool.execute_with_tracking({
            'action': 'search',
            'query': topic,
            'limit': 5
        })
        
        print(f"Found {search_result['count']} articles")
        for i, article in enumerate(search_result['results'], 1):
            print(f"  {i}. {article['title']}")
        
        # Step 2: Get summary of main article
        if search_result['results']:
            main_article = search_result['results'][0]['title']
            print(f"\n2. Getting summary of '{main_article}'...")
            
            time.sleep(1)  # Respectful delay
            
            summary_result = self.wiki_tool.execute_with_tracking({
                'action': 'get_summary',
                'query': main_article
            })
            
            print("\nSummary:")
            print(summary_result['summary'])
            print(f"\nRead more: {summary_result['url']}")
        
        return search_result

# Usage
assistant = WikipediaResearchAssistant()
assistant.research_topic('Climate Change')
```

#### Example 2: Content Comparison

```python
from tools.tools_registry import ToolsRegistry

def compare_topics(topic1, topic2):
    """
    Compare two topics by their Wikipedia summaries
    """
    registry = ToolsRegistry()
    wiki_tool = registry.get_tool('wikipedia')
    
    topics = [topic1, topic2]
    summaries = {}
    
    for topic in topics:
        try:
            result = wiki_tool.execute_with_tracking({
                'action': 'get_summary',
                'query': topic
            })
            summaries[topic] = {
                'summary': result['summary'],
                'length': len(result['summary']),
                'url': result['url']
            }
        except Exception as e:
            print(f"Error getting {topic}: {e}")
            return None
    
    # Display comparison
    print(f"Comparing: {topic1} vs {topic2}")
    print("=" * 60)
    
    for topic, data in summaries.items():
        print(f"\n{topic}:")
        print(f"Length: {data['length']} characters")
        print(f"Summary: {data['summary'][:150]}...")
        print(f"URL: {data['url']}")
    
    return summaries

# Usage
compare_topics('Python (programming language)', 'JavaScript')
```

#### Example 3: Knowledge Graph Builder

```python
from tools.tools_registry import ToolsRegistry
import re

def build_knowledge_graph(starting_topic, depth=2):
    """
    Build a simple knowledge graph by following Wikipedia links
    """
    registry = ToolsRegistry()
    wiki_tool = registry.get_tool('wikipedia')
    
    graph = {
        'nodes': [],
        'edges': []
    }
    
    def extract_links(text):
        """Extract potential Wikipedia page names from text"""
        # Simple extraction - in production use more sophisticated parsing
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        return list(set(words))[:5]  # Limit to 5 links
    
    def explore_topic(topic, current_depth):
        if current_depth >= depth or topic in graph['nodes']:
            return
        
        print(f"Exploring: {topic} (depth: {current_depth})")
        
        try:
            result = wiki_tool.execute_with_tracking({
                'action': 'get_summary',
                'query': topic
            })
            
            graph['nodes'].append(topic)
            
            # Extract related topics
            related_topics = extract_links(result['summary'])
            
            for related in related_topics:
                graph['edges'].append((topic, related))
                explore_topic(related, current_depth + 1)
        
        except Exception as e:
            print(f"Error exploring {topic}: {e}")
    
    explore_topic(starting_topic, 0)
    
    return graph

# Usage
graph = build_knowledge_graph('Artificial Intelligence', depth=2)
print(f"\nKnowledge Graph:")
print(f"Nodes: {len(graph['nodes'])}")
print(f"Edges: {len(graph['edges'])}")
```

---

## Error Handling

### Common Errors

#### 1. Page Not Found

**Error:**
```
ValueError: Page not found: Invalid Page Name
```

**Cause:** The specified page title doesn't exist on Wikipedia

**Solution:**
- Use the search action first to find exact titles
- Check spelling and capitalization
- Try variations of the page name

#### 2. Missing Required Parameters

**Error:**
```
ValueError: Missing required parameter: query
```

**Cause:** Required parameter not provided in arguments

**Solution:**
```python
# ✗ Wrong
arguments = {'action': 'search'}

# ✓ Correct
arguments = {'action': 'search', 'query': 'Python'}
```

#### 3. Network Errors

**Error:**
```
ValueError: Failed to search Wikipedia: Network connection failed
```

**Cause:** Network connectivity issues

**Solution:**
- Check internet connection
- Verify firewall settings
- Implement retry logic

#### 4. Tool Disabled

**Error:**
```
RuntimeError: Tool is disabled: wikipedia
```

**Cause:** Tool is disabled in configuration

**Solution:**
```python
# Enable the tool
registry = ToolsRegistry()
registry.enable_tool('wikipedia')
```

### Comprehensive Error Handling Pattern

```python
from tools.tools_registry import ToolsRegistry
import time

def safe_wikipedia_query(query, action='search', max_retries=3):
    """
    Execute Wikipedia query with retry logic and error handling
    """
    registry = ToolsRegistry()
    wiki_tool = registry.get_tool('wikipedia')
    
    if wiki_tool is None:
        return {'error': 'Wikipedia tool not available'}
    
    if not wiki_tool.enabled:
        return {'error': 'Wikipedia tool is disabled'}
    
    for attempt in range(max_retries):
        try:
            result = wiki_tool.execute_with_tracking({
                'action': action,
                'query': query
            })
            return {'success': True, 'data': result}
            
        except ValueError as e:
            # Validation or page not found error - don't retry
            return {'error': f'Validation error: {str(e)}'}
            
        except Exception as e:
            # Network or other error - retry
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return {'error': f'Failed after {max_retries} attempts: {str(e)}'}
    
    return {'error': 'Unknown error'}

# Usage
result = safe_wikipedia_query('Machine Learning', action='get_summary')
if 'error' in result:
    print(f"Error: {result['error']}")
else:
    print(result['data']['summary'])
```

---

## Best Practices

### 1. Respectful Usage

```python
import time

# Add delays between requests
for topic in topics:
    result = wiki_tool.execute_with_tracking({'action': 'search', 'query': topic})
    time.sleep(1)  # 1 second delay
```

### 2. Use Search Before Get Page

```python
# ✓ Best practice: Search first to find exact title
search_result = wiki_tool.execute_with_tracking({
    'action': 'search',
    'query': 'artificial intelligence',
    'limit': 1
})

if search_result['results']:
    exact_title = search_result['results'][0]['title']
    
    # Then get the page using exact title
    page_result = wiki_tool.execute_with_tracking({
        'action': 'get_page',
        'query': exact_title
    })
```

### 3. Cache Results

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_summary(topic):
    registry = ToolsRegistry()
    wiki_tool = registry.get_tool('wikipedia')
    return wiki_tool.execute_with_tracking({
        'action': 'get_summary',
        'query': topic
    })
```

### 4. Input Validation

```python
def validate_query(query):
    """Validate query before sending to Wikipedia"""
    if not query or not isinstance(query, str):
        raise ValueError("Query must be a non-empty string")
    
    if len(query) > 300:
        raise ValueError("Query too long (max 300 characters)")
    
    return query.strip()

# Usage
try:
    query = validate_query(user_input)
    result = wiki_tool.execute_with_tracking({
        'action': 'search',
        'query': query
    })
except ValueError as e:
    print(f"Invalid input: {e}")
```

---

## Performance Considerations

### Typical Response Times

- **Search**: 200-500ms
- **Get Summary**: 300-700ms
- **Get Full Page**: 500-1500ms

### Optimization Tips

1. **Use Summaries**: Faster than full page content
2. **Limit Search Results**: Lower limits = faster response
3. **Implement Caching**: Reduce redundant API calls
4. **Batch Requests**: Group related queries
5. **Async Processing**: Use for multiple requests

---

## Troubleshooting

### Issue: Tool Not Found

**Symptoms:** `registry.get_tool('wikipedia')` returns `None`

**Solutions:**
1. Check configuration file exists: `config/tools/wikipedia.json`
2. Verify file has correct JSON syntax
3. Check tool name matches exactly
4. Review registry logs for loading errors

### Issue: Empty Results

**Symptoms:** Search returns `count: 0`

**Solutions:**
1. Try different search terms
2. Check for typos
3. Use broader search terms
4. Verify Wikipedia is accessible

### Issue: Slow Response

**Symptoms:** Queries take >2 seconds

**Solutions:**
1. Check network latency
2. Use summaries instead of full pages
3. Implement caching
4. Reduce search result limits

---

## Additional Resources

- [Wikipedia API Documentation](https://www.mediawiki.org/wiki/API:Main_page)
- [MCP Tools Overview](MCP_TOOLS_OVERVIEW.md)
- [Tool Registry Documentation](MCP_TOOLS_OVERVIEW.md#tool-registry)

---

## Support

For issues or questions, contact:
**Ashutosh Sinha** - ajsinha@gmail.com

---

*Last Updated: October 26, 2025*