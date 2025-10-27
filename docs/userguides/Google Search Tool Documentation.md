# Google Search Tool Documentation

**Copyright All Rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com**

## Table of Contents

1. [Overview](#overview)
2. [Configuration](#configuration)
3. [Setup Requirements](#setup-requirements)
4. [Parameters](#parameters)
5. [Python Client Usage](#python-client-usage)
6. [Web UI Usage](#web-ui-usage)
7. [Examples](#examples)
8. [Error Handling](#error-handling)

---

## Overview

The Google Search Tool provides programmatic access to Google's web search capabilities through the Custom Search JSON API. It supports web search, image search, and advanced filtering options.

### Features

- **Web Search**: Comprehensive web search results
- **Image Search**: Search for images with metadata
- **Safe Search**: Configurable content filtering
- **Site Restriction**: Limit search to specific domains
- **Pagination**: Navigate through multiple result pages
- **Demo Mode**: Test without API credentials

### Specifications

- **Tool Name**: `google_search`
- **Category**: Web Search
- **API**: Google Custom Search JSON API
- **Rate Limit**: 100 requests/hour (configurable)
- **Cache TTL**: 3600 seconds (1 hour)
- **Authentication**: API Key + Search Engine ID required

---

## Configuration

### Configuration File

Location: `config/tools/google_search.json`

```json
{
  "name": "google_search",
  "type": "google_search",
  "description": "Search the web using Google",
  "version": "1.0.0",
  "enabled": true,
  "api_key": "",
  "search_engine_id": "",
  "inputSchema": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query"
      },
      "num_results": {
        "type": "integer",
        "description": "Number of results to return",
        "default": 10,
        "minimum": 1,
        "maximum": 10
      },
      "start": {
        "type": "integer",
        "description": "Starting index for results (for pagination)",
        "default": 1,
        "minimum": 1
      },
      "safe_search": {
        "type": "string",
        "description": "Safe search level",
        "enum": ["off", "medium", "high"],
        "default": "medium"
      },
      "search_type": {
        "type": "string",
        "description": "Type of search",
        "enum": ["web", "image", "video"],
        "default": "web"
      },
      "site": {
        "type": "string",
        "description": "Restrict search to specific site (e.g., wikipedia.org)"
      }
    },
    "required": ["query"]
  },
  "metadata": {
    "author": "Ashutosh Sinha",
    "category": "Web Search",
    "tags": ["search", "google", "web"],
    "rateLimit": 100,
    "cacheTTL": 3600,
    "note": "Requires Google Custom Search API key and Search Engine ID for production use"
  }
}
```

---

## Setup Requirements

### 1. Google Cloud Console Setup

#### Step 1: Create a Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Custom Search API

#### Step 2: Get API Key
1. Navigate to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **API Key**
3. Copy the API key
4. (Optional) Restrict the key to Custom Search API only

#### Step 3: Create Search Engine
1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click **Add** to create a new search engine
3. Configure settings:
   - **Search entire web**: Enable
   - **Image search**: Enable (if needed)
   - **Safe search**: Configure as desired
4. Get your **Search Engine ID** (cx parameter)

### 2. Configuration

Update `config/tools/google_search.json`:

```json
{
  "api_key": "YOUR_API_KEY_HERE",
  "search_engine_id": "YOUR_SEARCH_ENGINE_ID_HERE"
}
```

### 3. API Quotas

**Free Tier:**
- 100 queries per day
- No cost

**Paid Tier:**
- First 100 queries/day: Free
- Additional queries: $5 per 1000 queries
- Maximum: 10,000 queries per day

### Demo Mode

If no API credentials are provided, the tool operates in demo mode with mock results. This is useful for testing but does not provide real search data.

---

## Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| query | string | Search query string |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| num_results | integer | 10 | Number of results (1-10) |
| start | integer | 1 | Starting result index for pagination |
| safe_search | string | "medium" | Safe search level: "off", "medium", "high" |
| search_type | string | "web" | Type of search: "web", "image", "video" |
| site | string | null | Restrict to specific site (e.g., "reddit.com") |

### Response Format

**Web Search:**
```json
{
  "query": "search query",
  "totalResults": "1000000",
  "searchTime": 0.45,
  "count": 10,
  "results": [
    {
      "title": "Page Title",
      "link": "https://example.com/page",
      "snippet": "Brief description of the page...",
      "displayLink": "example.com"
    }
  ]
}
```

**Image Search:**
```json
{
  "query": "search query",
  "totalResults": "50000",
  "searchTime": 0.35,
  "count": 10,
  "results": [
    {
      "title": "Image Title",
      "link": "https://example.com/image.jpg",
      "snippet": "Image description",
      "displayLink": "example.com",
      "image": {
        "thumbnailLink": "https://...",
        "contextLink": "https://...",
        "height": 800,
        "width": 600
      }
    }
  ]
}
```

---

## Python Client Usage

### Basic Setup

```python
from tools.tools_registry import ToolsRegistry

# Initialize registry
registry = ToolsRegistry()

# Get Google Search tool
search_tool = registry.get_tool('google_search')

# Check if tool is available
if search_tool is None:
    print("Google Search tool not found")
    exit(1)

# Check if tool is enabled
if not search_tool.enabled:
    print("Google Search tool is disabled")
    exit(1)
```

### Example 1: Basic Web Search

```python
from tools.tools_registry import ToolsRegistry
import json

registry = ToolsRegistry()
search_tool = registry.get_tool('google_search')

# Perform search
arguments = {
    'query': 'Python programming tutorials',
    'num_results': 5
}

try:
    result = search_tool.execute_with_tracking(arguments)
    print(json.dumps(result, indent=2))
    
    # Process results
    print(f"\nFound {result['totalResults']} results in {result['searchTime']}s")
    print(f"Showing {result['count']} results:\n")
    
    for i, item in enumerate(result['results'], 1):
        print(f"{i}. {item['title']}")
        print(f"   {item['link']}")
        print(f"   {item['snippet']}\n")
        
except Exception as e:
    print(f"Error: {e}")
```

**Sample Output:**
```
Found 1,240,000 results in 0.45s
Showing 5 results:

1. Python Tutorial - W3Schools
   https://www.w3schools.com/python/
   Well organized and easy to understand Web building tutorials...

2. The Python Tutorial — Python 3.12 Documentation
   https://docs.python.org/3/tutorial/
   This tutorial introduces the reader informally to the basic concepts...
```

### Example 2: Site-Specific Search

```python
from tools.tools_registry import ToolsRegistry

registry = ToolsRegistry()
search_tool = registry.get_tool('google_search')

# Search within a specific site
arguments = {
    'query': 'machine learning',
    'site': 'wikipedia.org',
    'num_results': 5
}

try:
    result = search_tool.execute_with_tracking(arguments)
    
    print(f"Searching Wikipedia for: {arguments['query']}\n")
    
    for item in result['results']:
        print(f"Title: {item['title']}")
        print(f"URL: {item['link']}")
        print(f"Snippet: {item['snippet'][:100]}...")
        print()
        
except Exception as e:
    print(f"Error: {e}")
```

### Example 3: Image Search

```python
from tools.tools_registry import ToolsRegistry

registry = ToolsRegistry()
search_tool = registry.get_tool('google_search')

# Search for images
arguments = {
    'query': 'sunset landscape',
    'search_type': 'image',
    'num_results': 10,
    'safe_search': 'high'
}

try:
    result = search_tool.execute_with_tracking(arguments)
    
    print(f"Image search: {arguments['query']}")
    print(f"Found {result['count']} images\n")
    
    for i, item in enumerate(result['results'], 1):
        if 'image' in item:
            print(f"{i}. {item['title']}")
            print(f"   Image URL: {item['link']}")
            print(f"   Thumbnail: {item['image']['thumbnailLink']}")
            print(f"   Size: {item['image']['width']}x{item['image']['height']}")
            print()
            
except Exception as e:
    print(f"Error: {e}")
```

### Example 4: Paginated Search

```python
from tools.tools_registry import ToolsRegistry
import time

def paginated_search(query, total_pages=3):
    """Perform paginated search"""
    registry = ToolsRegistry()
    search_tool = registry.get_tool('google_search')
    
    all_results = []
    
    for page in range(total_pages):
        start_index = (page * 10) + 1
        
        try:
            result = search_tool.execute_with_tracking({
                'query': query,
                'num_results': 10,
                'start': start_index
            })
            
            all_results.extend(result['results'])
            print(f"Page {page + 1}: Retrieved {len(result['results'])} results")
            
            # Rate limiting - be respectful
            if page < total_pages - 1:
                time.sleep(2)
                
        except Exception as e:
            print(f"Error on page {page + 1}: {e}")
            break
    
    return all_results

# Usage
results = paginated_search('artificial intelligence', total_pages=3)
print(f"\nTotal results collected: {len(results)}")
```

### Example 5: Search with Filtering

```python
from tools.tools_registry import ToolsRegistry

def filtered_search(query, filters):
    """
    Perform search with custom filters
    
    Args:
        query: Base search query
        filters: Dict of filter parameters
    """
    registry = ToolsRegistry()
    search_tool = registry.get_tool('google_search')
    
    # Build search parameters
    arguments = {
        'query': query,
        'num_results': filters.get('limit', 10),
        'safe_search': filters.get('safe_search', 'medium'),
        'search_type': filters.get('type', 'web')
    }
    
    # Add site restriction if specified
    if 'site' in filters:
        arguments['site'] = filters['site']
    
    try:
        result = search_tool.execute_with_tracking(arguments)
        
        # Apply additional filtering
        filtered_results = []
        for item in result['results']:
            # Filter by domain if specified
            if 'include_domains' in filters:
                if any(domain in item['displayLink'] for domain in filters['include_domains']):
                    filtered_results.append(item)
            # Filter by keywords in title
            elif 'title_keywords' in filters:
                if any(kw.lower() in item['title'].lower() for kw in filters['title_keywords']):
                    filtered_results.append(item)
            else:
                filtered_results.append(item)
        
        return {
            'query': query,
            'filters_applied': filters,
            'total_found': result['totalResults'],
            'count': len(filtered_results),
            'results': filtered_results
        }
        
    except Exception as e:
        return {'error': str(e)}

# Usage examples

# Search within educational sites
result = filtered_search('quantum computing', {
    'include_domains': ['.edu', 'wikipedia.org'],
    'limit': 10
})

# Search with title filtering
result = filtered_search('python tutorial', {
    'title_keywords': ['beginner', 'learn', 'guide'],
    'limit': 10
})
```

### Example 6: Research Assistant

```python
from tools.tools_registry import ToolsRegistry
import time

class ResearchAssistant:
    def __init__(self):
        registry = ToolsRegistry()
        self.search_tool = registry.get_tool('google_search')
    
    def comprehensive_search(self, topic, sources=None):
        """
        Perform comprehensive research on a topic
        
        Args:
            topic: Research topic
            sources: List of preferred sources (domains)
        """
        print(f"Researching: {topic}")
        print("=" * 60)
        
        research_data = {
            'topic': topic,
            'general_results': [],
            'academic_results': [],
            'news_results': []
        }
        
        # General web search
        print("\n1. General web search...")
        try:
            result = self.search_tool.execute_with_tracking({
                'query': topic,
                'num_results': 10
            })
            research_data['general_results'] = result['results']
            print(f"   Found {len(result['results'])} general results")
        except Exception as e:
            print(f"   Error: {e}")
        
        time.sleep(2)
        
        # Academic sources
        print("\n2. Academic sources...")
        academic_sites = ['scholar.google.com', '.edu', 'arxiv.org']
        for site in academic_sites:
            try:
                result = self.search_tool.execute_with_tracking({
                    'query': topic,
                    'site': site,
                    'num_results': 5
                })
                research_data['academic_results'].extend(result['results'])
                print(f"   Found {len(result['results'])} results from {site}")
                time.sleep(2)
            except Exception as e:
                print(f"   Error searching {site}: {e}")
        
        # News articles
        print("\n3. Recent news...")
        try:
            result = self.search_tool.execute_with_tracking({
                'query': f"{topic} news",
                'num_results': 10
            })
            research_data['news_results'] = result['results']
            print(f"   Found {len(result['results'])} news articles")
        except Exception as e:
            print(f"   Error: {e}")
        
        return research_data
    
    def generate_report(self, research_data):
        """Generate research report"""
        print("\n" + "=" * 60)
        print(f"RESEARCH REPORT: {research_data['topic']}")
        print("=" * 60)
        
        print("\nGENERAL SOURCES:")
        for i, item in enumerate(research_data['general_results'][:5], 1):
            print(f"{i}. {item['title']}")
            print(f"   {item['link']}")
        
        print("\nACADEMIC SOURCES:")
        for i, item in enumerate(research_data['academic_results'][:5], 1):
            print(f"{i}. {item['title']}")
            print(f"   {item['link']}")
        
        print("\nRECENT NEWS:")
        for i, item in enumerate(research_data['news_results'][:5], 1):
            print(f"{i}. {item['title']}")
            print(f"   {item['link']}")

# Usage
assistant = ResearchAssistant()
data = assistant.comprehensive_search('climate change solutions')
assistant.generate_report(data)
```

### Example 7: Competitive Intelligence

```python
from tools.tools_registry import ToolsRegistry

def analyze_competitor_presence(company_name, competitors):
    """Analyze online presence of competitors"""
    registry = ToolsRegistry()
    search_tool = registry.get_tool('google_search')
    
    analysis = {}
    
    for competitor in competitors:
        try:
            # Search for competitor
            result = search_tool.execute_with_tracking({
                'query': competitor,
                'num_results': 10
            })
            
            # Count different types of results
            owned_domains = 0
            social_media = 0
            news_mentions = 0
            
            for item in result['results']:
                link_lower = item['displayLink'].lower()
                
                if competitor.lower().replace(' ', '') in link_lower:
                    owned_domains += 1
                elif any(social in link_lower for social in ['facebook', 'twitter', 'linkedin', 'instagram']):
                    social_media += 1
                elif any(news in link_lower for news in ['news', 'techcrunch', 'reuters', 'bloomberg']):
                    news_mentions += 1
            
            analysis[competitor] = {
                'total_results': result['totalResults'],
                'owned_domains': owned_domains,
                'social_media': social_media,
                'news_mentions': news_mentions,
                'top_result': result['results'][0] if result['results'] else None
            }
            
        except Exception as e:
            analysis[competitor] = {'error': str(e)}
    
    return analysis

# Usage
competitors = ['OpenAI', 'Anthropic', 'Google DeepMind']
analysis = analyze_competitor_presence('AI Companies', competitors)

for company, data in analysis.items():
    print(f"\n{company}:")
    if 'error' not in data:
        print(f"  Total Results: {data['total_results']}")
        print(f"  Owned Domains: {data['owned_domains']}")
        print(f"  Social Media: {data['social_media']}")
        print(f"  News Mentions: {data['news_mentions']}")
    else:
        print(f"  Error: {data['error']}")
```

---

## Web UI Usage

### Accessing the Tool

1. **Navigate to Tools Page**
   ```
   http://localhost:5000/tools
   ```

2. **Select Google Search Tool**
   - Find "google_search" in the tools list
   - Click "Execute" button

3. **Execute Tool Page**
   ```
   http://localhost:5000/tools/execute/google_search
   ```

### Using the Web Interface

#### Basic Web Search

1. **Enter Query**: Type your search query
2. **Set Results**: Choose number of results (1-10)
3. **Safe Search**: Select filtering level
4. **Execute**: Click "Execute Tool" button

**Example Input:**
```
Query: artificial intelligence ethics
Num Results: 10
Start: 1
Safe Search: medium
Search Type: web
```

#### Site-Restricted Search

1. **Enter Query**: Your search terms
2. **Enter Site**: Domain to search within (e.g., "reddit.com")
3. **Execute**: Click "Execute Tool"

**Example Input:**
```
Query: best programming languages
Site: stackoverflow.com
Num Results: 5
```

#### Image Search

1. **Enter Query**: Image search terms
2. **Select Type**: Choose "image" from dropdown
3. **Safe Search**: Recommended "high" for images
4. **Execute**: Click "Execute Tool"

**Example Input:**
```
Query: data visualization examples
Search Type: image
Num Results: 10
Safe Search: high
```

#### Paginated Results

1. **First Page**: Leave start at 1
2. **View Results**: Click execute
3. **Next Page**: Set start to 11, click execute
4. **Continue**: Increment by 10 for each page

### Web UI Features

- **Auto-validation**: Form validates before submission
- **Result Links**: Clickable links to search results
- **Snippet Preview**: Shows page descriptions
- **Search Time**: Displays query execution time
- **Total Results**: Shows approximate total matches
- **Demo Mode Indicator**: Shows when using demo data

---

## Examples

### Complete Working Examples

#### Example 1: Content Aggregator

```python
from tools.tools_registry import ToolsRegistry
import json
import time

class ContentAggregator:
    def __init__(self):
        registry = ToolsRegistry()
        self.search_tool = registry.get_tool('google_search')
    
    def aggregate_content(self, topic, sources_config):
        """
        Aggregate content from multiple sources
        
        Args:
            topic: Search topic
            sources_config: List of {name, site, limit} dicts
        """
        aggregated = {
            'topic': topic,
            'sources': []
        }
        
        for config in sources_config:
            print(f"Searching {config['name']}...")
            
            try:
                result = self.search_tool.execute_with_tracking({
                    'query': topic,
                    'site': config.get('site'),
                    'num_results': config.get('limit', 10)
                })
                
                aggregated['sources'].append({
                    'name': config['name'],
                    'site': config.get('site'),
                    'count': len(result['results']),
                    'results': result['results']
                })
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error: {e}")
        
        return aggregated
    
    def export_to_json(self, data, filename):
        """Export aggregated data to JSON"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Exported to {filename}")

# Usage
aggregator = ContentAggregator()

sources = [
    {'name': 'General Web', 'limit': 10},
    {'name': 'Wikipedia', 'site': 'wikipedia.org', 'limit': 5},
    {'name': 'Academic', 'site': '.edu', 'limit': 5},
    {'name': 'GitHub', 'site': 'github.com', 'limit': 5}
]

data = aggregator.aggregate_content('machine learning frameworks', sources)
aggregator.export_to_json(data, 'ml_frameworks_research.json')
```

#### Example 2: SEO Analysis Tool

```python
from tools.tools_registry import ToolsRegistry

class SEOAnalyzer:
    def __init__(self):
        registry = ToolsRegistry()
        self.search_tool = registry.get_tool('google_search')
    
    def analyze_rankings(self, keyword, target_domain, num_pages=3):
        """
        Analyze search rankings for a keyword
        
        Args:
            keyword: Search keyword
            target_domain: Domain to track
            num_pages: Number of pages to check
        """
        print(f"Analyzing rankings for: {keyword}")
        print(f"Target domain: {target_domain}\n")
        
        rankings = []
        found_position = None
        
        for page in range(num_pages):
            start = (page * 10) + 1
            
            try:
                result = self.search_tool.execute_with_tracking({
                    'query': keyword,
                    'num_results': 10,
                    'start': start
                })
                
                for i, item in enumerate(result['results'], start):
                    if target_domain in item['displayLink']:
                        found_position = i
                        rankings.append({
                            'position': i,
                            'page': page + 1,
                            'title': item['title'],
                            'url': item['link'],
                            'snippet': item['snippet']
                        })
                
                time.sleep(2)
                
            except Exception as e:
                print(f"Error on page {page + 1}: {e}")
                break
        
        # Display results
        if rankings:
            print(f"✓ Found {len(rankings)} ranking(s):\n")
            for rank in rankings:
                print(f"Position #{rank['position']} (Page {rank['page']})")
                print(f"Title: {rank['title']}")
                print(f"URL: {rank['url']}\n")
        else:
            print(f"✗ {target_domain} not found in top {num_pages * 10} results")
        
        return rankings

# Usage
analyzer = SEOAnalyzer()
analyzer.analyze_rankings(
    'python web framework',
    'flask.palletsprojects.com',
    num_pages=3
)
```

---

## Error Handling

### Common Errors

#### 1. API Key Invalid

**Error:**
```
ValueError: API key invalid or quota exceeded
```

**Solutions:**
- Verify API key is correct
- Check API is enabled in Google Cloud Console
- Verify billing is set up (for usage beyond free tier)
- Check daily quota hasn't been exceeded

#### 2. Search Engine ID Invalid

**Error:**
```
ValueError: Invalid search parameters
```

**Solutions:**
- Verify Search Engine ID (cx parameter)
- Ensure search engine is properly configured
- Check search engine hasn't been deleted

#### 3. Quota Exceeded

**Error:**
```
ValueError: API key invalid or quota exceeded (HTTP 403)
```

**Solutions:**
- Wait until quota resets (usually midnight Pacific Time)
- Upgrade to paid tier for higher quotas
- Implement caching to reduce API calls
- Use alternative search methods

#### 4. Demo Mode Limitations

**Note:** Demo mode returns mock data and displays a note in results

**Solution:**
- Configure valid API credentials
- See [Setup Requirements](#setup-requirements)

### Comprehensive Error Handling

```python
from tools.tools_registry import ToolsRegistry
import time

def safe_search(query, max_retries=3, **kwargs):
    """Perform search with comprehensive error handling"""
    registry = ToolsRegistry()
    search_tool = registry.get_tool('google_search')
    
    if search_tool is None:
        return {'error': 'Search tool not available'}
    
    arguments = {'query': query}
    arguments.update(kwargs)
    
    for attempt in range(max_retries):
        try:
            result = search_tool.execute_with_tracking(arguments)
            
            # Check if demo mode
            if 'note' in result and 'demo' in result['note'].lower():
                print("Warning: Running in demo mode")
            
            return {'success': True, 'data': result}
            
        except ValueError as e:
            error_msg = str(e)
            
            if 'quota exceeded' in error_msg.lower():
                return {'error': 'API quota exceeded. Try again later.'}
            elif 'invalid' in error_msg.lower() and 'key' in error_msg.lower():
                return {'error': 'Invalid API credentials'}
            elif attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return {'error': f'Failed after {max_retries} attempts: {error_msg}'}
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return {'error': f'Unexpected error: {str(e)}'}
    
    return {'error': 'Failed after retries'}

# Usage
result = safe_search('python tutorials', num_results=5)
if result.get('success'):
    for item in result['data']['results']:
        print(item['title'])
else:
    print(f"Error: {result['error']}")
```

---

## Best Practices

### 1. Respect Rate Limits

```python
import time

# Add delays between searches
queries = ['query1', 'query2', 'query3']
for query in queries:
    result = search_tool.execute_with_tracking({'query': query})
    time.sleep(1)  # 1 second delay
```

### 2. Implement Caching

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_search(query, num_results=10):
    registry = ToolsRegistry()
    search_tool = registry.get_tool('google_search')
    return search_tool.execute_with_tracking({
        'query': query,
        'num_results': num_results
    })
```

### 3. Use Specific Queries

```python
# ✗ Too broad
result = search('python')

# ✓ More specific
result = search('python web development best practices 2025')
```

### 4. Handle Demo Mode

```python
def check_demo_mode(result):
    """Check if running in demo mode"""
    if 'note' in result and 'demo' in result['note'].lower():
        print("⚠️  Running in demo mode - configure API credentials for real results")
        return True
    return False
```

---

## Troubleshooting

### Issue: No Results Returned

**Solutions:**
1. Try different search terms
2. Remove site restrictions
3. Check safe search settings
4. Verify API credentials

### Issue: Results Not Relevant

**Solutions:**
1. Use more specific keywords
2. Add site restrictions
3. Use quoted phrases for exact matches
4. Filter results programmatically

### Issue: Slow Performance

**Solutions:**
1. Reduce num_results
2. Implement caching
3. Use async requests for multiple queries
4. Check network latency

---

## Additional Resources

- [Google Custom Search API Documentation](https://developers.google.com/custom-search)
- [MCP Tools Overview](MCP_TOOLS_OVERVIEW.md)
- [API Console](https://console.cloud.google.com/)

---

## Support

For issues or questions, contact:
**Ashutosh Sinha** - ajsinha@gmail.com

---

*Last Updated: October 26, 2025*