# Web Crawler MCP Tool Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [API Reference](#api-reference)
5. [Usage Examples](#usage-examples)
6. [Best Practices](#best-practices)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The **WebCrawlerMCPTool** is a comprehensive Model Context Protocol (MCP) tool designed for web scraping and crawling operations. It provides a robust set of features for extracting content, links, metadata, and structured data from websites.

### Key Features

- **Multi-level crawling** (up to 3 levels deep)
- **Document link extraction** (PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT)
- **Intelligent link management** with duplicate detection
- **Content extraction** (text, images, tables, headings)
- **Metadata extraction** (title, description, keywords, Open Graph tags)
- **Search functionality** within pages
- **Sitemap and robots.txt parsing**
- **Built-in rate limiting** and error handling
- **URL normalization** and validation

### Technical Specifications

- **Maximum crawl depth**: 3 levels
- **Maximum pages per crawl**: 100 pages
- **Rate limit**: 100 requests per 10-second window
- **Request timeout**: 10 seconds
- **Supported protocols**: HTTP, HTTPS

---

## Installation

### Prerequisites

```bash
python >= 3.8
```

### Required Dependencies

```bash
pip install requests beautifulsoup4 lxml
```

### Installation Steps

1. **Copy the tool files** to your MCP tools directory:
   ```bash
   tools/
   ├── base_mcp_tool.py
   ├── web_crawler_mcp_tool.py
   └── web_crawler_mcp_tool.json
   ```

2. **Import the tool** in your application:
   ```python
   from tools.web_crawler_mcp_tool import WebCrawlerMCPTool
   
   crawler = WebCrawlerMCPTool()
   ```

---

## Configuration

### Basic Configuration

```python
from tools.web_crawler_mcp_tool import WebCrawlerMCPTool

# Initialize the tool
crawler = WebCrawlerMCPTool()

# Configure custom headers (optional)
crawler.headers['User-Agent'] = 'MyCustomBot/1.0'

# Set custom timeout (optional)
crawler.request_timeout = 15  # seconds
```

### Rate Limiting Configuration

The tool has built-in rate limiting to prevent overwhelming target servers:

- **Default**: 100 requests per 10-second window
- **Configurable** via `max_hits` and `max_hit_interval` in JSON schema

```json
{
  "max_hits": 100,
  "max_hit_interval": 10
}
```

---

## API Reference

### 1. crawl_website

Crawl a website starting from a given URL, exploring up to 3 levels deep.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | Starting URL to crawl |
| `max_depth` | integer | No | 3 | Maximum depth to crawl (1-3) |
| `max_pages` | integer | No | 50 | Maximum number of pages to crawl (1-100) |
| `same_domain_only` | boolean | No | true | Only crawl pages within the same domain |
| `include_external_links` | boolean | No | false | Include external links in results |
| `extract_metadata` | boolean | No | true | Extract page metadata |

#### Response Format

```json
{
  "start_url": "https://example.com",
  "crawl_date": "2025-10-20T10:30:00",
  "max_depth": 3,
  "pages_crawled": 42,
  "total_internal_links": 156,
  "total_external_links": 23,
  "pages": [
    {
      "url": "https://example.com/page1",
      "depth": 1,
      "status": 200,
      "text_length": 3456,
      "text_content": "Page content...",
      "metadata": {
        "title": "Page Title",
        "description": "Page description"
      },
      "links_found": 12,
      "internal_links": ["https://example.com/page2", "..."]
    }
  ],
  "external_links": ["https://external.com", "..."]
}
```

#### Example Usage

```python
result = crawler.handle_tool_call("crawl_website", {
    "url": "https://example.com",
    "max_depth": 2,
    "max_pages": 25,
    "same_domain_only": True
})

print(f"Crawled {result['pages_crawled']} pages")
```

---

### 2. crawl_single_page

Crawl a single page and extract its content and links.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL of the page to crawl |
| `extract_links` | boolean | No | true | Extract all links from the page |
| `extract_metadata` | boolean | No | true | Extract page metadata |

#### Response Format

```json
{
  "url": "https://example.com/page",
  "status": 200,
  "text_length": 5678,
  "text_content": "Full page text content...",
  "metadata": {
    "title": "Page Title",
    "description": "Meta description",
    "keywords": "keyword1, keyword2"
  },
  "links": [
    {
      "url": "https://example.com/link1",
      "text": "Link text",
      "title": "Link title"
    }
  ],
  "link_count": 23
}
```

#### Example Usage

```python
result = crawler.handle_tool_call("crawl_single_page", {
    "url": "https://example.com/article",
    "extract_metadata": True
})

print(result['text_content'])
```

---

### 3. extract_all_links

Extract all hyperlinks from a given page.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL to extract links from |
| `absolute_urls` | boolean | No | true | Convert relative URLs to absolute |
| `filter_domain` | string | No | null | Filter links by specific domain |

#### Response Format

```json
{
  "url": "https://example.com",
  "status": 200,
  "total_links": 45,
  "links": [
    {
      "url": "https://example.com/page1",
      "text": "Link text",
      "title": "Link title attribute"
    }
  ]
}
```

#### Example Usage

```python
# Extract all links
result = crawler.handle_tool_call("extract_all_links", {
    "url": "https://example.com",
    "absolute_urls": True
})

# Extract links for specific domain
result = crawler.handle_tool_call("extract_all_links", {
    "url": "https://example.com",
    "filter_domain": "example.com"
})
```

---

### 4. extract_all_document_links

Extract links to documents (PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT).

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL to extract document links from |
| `document_types` | array | No | all | Filter by specific document types |
| `absolute_urls` | boolean | No | true | Return absolute URLs |

#### Response Format

```json
{
  "url": "https://example.com/resources",
  "status": 200,
  "total_documents": 12,
  "documents": [
    {
      "url": "https://example.com/files/report.pdf",
      "type": "pdf",
      "text": "Annual Report 2024",
      "title": "Download Report"
    }
  ],
  "by_type": {
    "pdf": [/* PDF documents */],
    "xlsx": [/* Excel documents */],
    "docx": [/* Word documents */]
  }
}
```

#### Example Usage

```python
# Extract all document types
result = crawler.handle_tool_call("extract_all_document_links", {
    "url": "https://example.com/downloads"
})

# Extract only PDFs and Excel files
result = crawler.handle_tool_call("extract_all_document_links", {
    "url": "https://example.com/downloads",
    "document_types": ["pdf", "xlsx"]
})

# Access documents by type
pdfs = result['by_type']['pdf']
for pdf in pdfs:
    print(f"PDF: {pdf['text']} - {pdf['url']}")
```

---

### 5. extract_images

Extract all images from a page with their attributes.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL to extract images from |
| `include_alt_text` | boolean | No | true | Include alt text for images |

#### Response Format

```json
{
  "url": "https://example.com",
  "status": 200,
  "total_images": 15,
  "images": [
    {
      "url": "https://example.com/images/photo.jpg",
      "alt": "Photo description",
      "title": "Photo title",
      "width": "800",
      "height": "600"
    }
  ]
}
```

#### Example Usage

```python
result = crawler.handle_tool_call("extract_images", {
    "url": "https://example.com/gallery",
    "include_alt_text": True
})

for image in result['images']:
    print(f"{image['alt']}: {image['url']}")
```

---

### 6. extract_headings

Extract all headings (H1-H6) from a page.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL to extract headings from |
| `include_hierarchy` | boolean | No | true | Organize headings by hierarchy |

#### Response Format

```json
{
  "url": "https://example.com",
  "status": 200,
  "total_headings": 18,
  "headings": [
    {
      "level": 1,
      "text": "Main Title",
      "id": "main-title"
    }
  ],
  "hierarchy": {
    "h1": ["Main Title"],
    "h2": ["Section 1", "Section 2"],
    "h3": ["Subsection 1.1", "Subsection 1.2"]
  }
}
```

#### Example Usage

```python
result = crawler.handle_tool_call("extract_headings", {
    "url": "https://example.com/article",
    "include_hierarchy": True
})

# Print document structure
for level, headings in result['hierarchy'].items():
    if headings:
        print(f"\n{level.upper()}:")
        for heading in headings:
            print(f"  - {heading}")
```

---

### 7. extract_tables

Extract all tables from a page as structured data.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL to extract tables from |
| `format` | string | No | json | Output format: json, csv, or text |

#### Response Format

**JSON Format:**
```json
{
  "url": "https://example.com",
  "status": 200,
  "total_tables": 3,
  "tables": [
    {
      "table_index": 0,
      "headers": ["Name", "Age", "City"],
      "data": [
        {"Name": "John", "Age": "30", "City": "NYC"},
        {"Name": "Jane", "Age": "25", "City": "LA"}
      ],
      "row_count": 2
    }
  ]
}
```

**CSV Format:**
```json
{
  "tables": [
    {
      "table_index": 0,
      "csv": "Name,Age,City\nJohn,30,NYC\nJane,25,LA\n"
    }
  ]
}
```

#### Example Usage

```python
# Extract as JSON
result = crawler.handle_tool_call("extract_tables", {
    "url": "https://example.com/data",
    "format": "json"
})

# Extract as CSV
result = crawler.handle_tool_call("extract_tables", {
    "url": "https://example.com/data",
    "format": "csv"
})

# Process table data
for table in result['tables']:
    print(f"Table {table['table_index']}:")
    for row in table['data']:
        print(row)
```

---

### 8. get_page_metadata

Extract metadata from a page (title, description, keywords, Open Graph tags).

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL to extract metadata from |

#### Response Format

```json
{
  "url": "https://example.com",
  "status": 200,
  "metadata": {
    "title": "Page Title",
    "description": "Page description",
    "keywords": "keyword1, keyword2, keyword3",
    "author": "John Doe",
    "og:title": "Open Graph Title",
    "og:description": "Open Graph Description",
    "og:image": "https://example.com/image.jpg",
    "twitter:card": "summary_large_image",
    "viewport": "width=device-width, initial-scale=1"
  }
}
```

#### Example Usage

```python
result = crawler.handle_tool_call("get_page_metadata", {
    "url": "https://example.com"
})

metadata = result['metadata']
print(f"Title: {metadata.get('title')}")
print(f"Description: {metadata.get('description')}")
print(f"OG Image: {metadata.get('og:image')}")
```

---

### 9. search_text_in_page

Search for specific text or patterns within a page.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL to search in |
| `search_term` | string | Yes | - | Text or pattern to search for |
| `case_sensitive` | boolean | No | false | Case sensitive search |
| `context_chars` | integer | No | 100 | Characters of context around matches |

#### Response Format

```json
{
  "url": "https://example.com",
  "status": 200,
  "search_term": "python programming",
  "total_matches": 5,
  "matches": [
    {
      "position": 1234,
      "context": "...learn python programming with our comprehensive...",
      "match": "python programming"
    }
  ]
}
```

#### Example Usage

```python
result = crawler.handle_tool_call("search_text_in_page", {
    "url": "https://example.com/article",
    "search_term": "machine learning",
    "case_sensitive": False,
    "context_chars": 150
})

print(f"Found {result['total_matches']} matches")
for match in result['matches']:
    print(f"\n{match['context']}")
```

---

### 10. get_sitemap

Fetch and parse the sitemap.xml of a website.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | Base URL of the website |
| `sitemap_url` | string | No | null | Specific sitemap URL (optional) |

#### Response Format

```json
{
  "sitemap_url": "https://example.com/sitemap.xml",
  "status": 200,
  "total_urls": 250,
  "urls": [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/blog/article1"
  ]
}
```

#### Example Usage

```python
# Auto-detect sitemap
result = crawler.handle_tool_call("get_sitemap", {
    "url": "https://example.com"
})

# Specific sitemap URL
result = crawler.handle_tool_call("get_sitemap", {
    "url": "https://example.com",
    "sitemap_url": "https://example.com/sitemap_index.xml"
})

print(f"Found {result['total_urls']} URLs in sitemap")
```

---

### 11. get_robots_txt

Fetch and parse the robots.txt file of a website.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | Base URL of the website |

#### Response Format

```json
{
  "robots_url": "https://example.com/robots.txt",
  "status": 200,
  "content": "User-agent: *\nDisallow: /admin/\nAllow: /\n...",
  "rules": {
    "user_agents": ["*", "Googlebot"],
    "disallowed": ["/admin/", "/private/"],
    "allowed": ["/"],
    "sitemaps": ["https://example.com/sitemap.xml"],
    "crawl_delay": "1"
  }
}
```

#### Example Usage

```python
result = crawler.handle_tool_call("get_robots_txt", {
    "url": "https://example.com"
})

rules = result['rules']
print(f"Disallowed paths: {rules['disallowed']}")
print(f"Sitemaps: {rules['sitemaps']}")
print(f"Crawl delay: {rules['crawl_delay']} seconds")
```

---

### 12. check_url_accessibility

Check if a URL is accessible and get response information.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `url` | string | Yes | - | URL to check |
| `follow_redirects` | boolean | No | true | Follow redirects |

#### Response Format

```json
{
  "url": "https://example.com/page",
  "accessible": true,
  "status_code": 200,
  "status_text": "OK",
  "headers": {
    "Content-Type": "text/html; charset=utf-8",
    "Content-Length": "12345",
    "Server": "nginx"
  },
  "final_url": "https://example.com/page",
  "redirect": false
}
```

#### Example Usage

```python
result = crawler.handle_tool_call("check_url_accessibility", {
    "url": "https://example.com/page",
    "follow_redirects": True
})

if result['accessible']:
    print(f"URL is accessible: {result['status_code']}")
else:
    print(f"URL not accessible: {result.get('error')}")
```

---

## Usage Examples

### Example 1: Complete Website Analysis

```python
from tools.web_crawler_mcp_tool import WebCrawlerMCPTool

crawler = WebCrawlerMCPTool()

# Step 1: Check robots.txt
robots = crawler.handle_tool_call("get_robots_txt", {
    "url": "https://example.com"
})
print("Crawl rules:", robots['rules'])

# Step 2: Get sitemap for structured crawling
sitemap = crawler.handle_tool_call("get_sitemap", {
    "url": "https://example.com"
})
print(f"Sitemap contains {sitemap['total_urls']} URLs")

# Step 3: Crawl the website
crawl_result = crawler.handle_tool_call("crawl_website", {
    "url": "https://example.com",
    "max_depth": 2,
    "max_pages": 30,
    "same_domain_only": True
})

print(f"Crawled {crawl_result['pages_crawled']} pages")
for page in crawl_result['pages']:
    print(f"  - {page['url']} (depth: {page['depth']})")
```

### Example 2: Document Harvesting

```python
# Extract all downloadable documents
documents = crawler.handle_tool_call("extract_all_document_links", {
    "url": "https://example.com/resources",
    "document_types": ["pdf", "docx", "xlsx"]
})

# Organize by type
for doc_type, docs in documents['by_type'].items():
    print(f"\n{doc_type.upper()} Documents:")
    for doc in docs:
        print(f"  - {doc['text']}")
        print(f"    URL: {doc['url']}")
```

### Example 3: Content Analysis

```python
# Get page content
page = crawler.handle_tool_call("crawl_single_page", {
    "url": "https://example.com/article",
    "extract_metadata": True
})

# Extract structure
headings = crawler.handle_tool_call("extract_headings", {
    "url": "https://example.com/article",
    "include_hierarchy": True
})

# Extract data tables
tables = crawler.handle_tool_call("extract_tables", {
    "url": "https://example.com/article",
    "format": "json"
})

# Search for specific content
results = crawler.handle_tool_call("search_text_in_page", {
    "url": "https://example.com/article",
    "search_term": "machine learning",
    "context_chars": 200
})

print(f"Article: {page['metadata']['title']}")
print(f"Headings: {headings['total_headings']}")
print(f"Tables: {tables['total_tables']}")
print(f"ML mentions: {results['total_matches']}")
```

### Example 4: Link Validation

```python
# Get all links from a page
links_result = crawler.handle_tool_call("extract_all_links", {
    "url": "https://example.com"
})

# Check each link
broken_links = []
for link in links_result['links']:
    check = crawler.handle_tool_call("check_url_accessibility", {
        "url": link['url'],
        "follow_redirects": True
    })
    
    if not check['accessible']:
        broken_links.append({
            'url': link['url'],
            'status': check.get('status_code', 'N/A'),
            'text': link['text']
        })

print(f"Found {len(broken_links)} broken links:")
for broken in broken_links:
    print(f"  - {broken['text']}: {broken['url']} ({broken['status']})")
```

### Example 5: Competitive Analysis

```python
competitors = [
    "https://competitor1.com",
    "https://competitor2.com",
    "https://competitor3.com"
]

analysis = []
for url in competitors:
    # Get metadata
    metadata = crawler.handle_tool_call("get_page_metadata", {
        "url": url
    })
    
    # Get structure
    headings = crawler.handle_tool_call("extract_headings", {
        "url": url
    })
    
    # Get internal links
    links = crawler.handle_tool_call("extract_all_links", {
        "url": url,
        "filter_domain": urlparse(url).netloc
    })
    
    analysis.append({
        'url': url,
        'title': metadata['metadata'].get('title'),
        'description': metadata['metadata'].get('description'),
        'heading_count': headings['total_headings'],
        'internal_links': links['total_links']
    })

# Compare results
for comp in analysis:
    print(f"\n{comp['url']}:")
    print(f"  Title: {comp['title']}")
    print(f"  Headings: {comp['heading_count']}")
    print(f"  Internal links: {comp['internal_links']}")
```

---

## Best Practices

### 1. Respect robots.txt

Always check and respect robots.txt rules before crawling:

```python
# Check robots.txt first
robots = crawler.handle_tool_call("get_robots_txt", {
    "url": "https://example.com"
})

# Review disallowed paths
if '/admin/' in robots['rules']['disallowed']:
    print("Admin section is disallowed for crawling")
```

### 2. Use Appropriate Crawl Depth

- **Depth 1**: For quick surveys or single-level analysis
- **Depth 2**: For moderate exploration of site structure
- **Depth 3**: For comprehensive crawling (use sparingly)

```python
# Light crawl
crawler.handle_tool_call("crawl_website", {
    "url": "https://example.com",
    "max_depth": 1,
    "max_pages": 10
})

# Deep crawl (use with caution)
crawler.handle_tool_call("crawl_website", {
    "url": "https://example.com",
    "max_depth": 3,
    "max_pages": 100
})
```

### 3. Handle Rate Limiting

The tool has built-in rate limiting, but you should also add delays for large crawls:

```python
import time

urls = ["url1", "url2", "url3", ...]

for url in urls:
    result = crawler.handle_tool_call("crawl_single_page", {"url": url})
    time.sleep(1)  # 1 second delay between requests
```

### 4. Error Handling

Always check for errors in responses:

```python
result = crawler.handle_tool_call("crawl_website", {
    "url": "https://example.com"
})

if 'error' in result:
    print(f"Error occurred: {result['error']}")
    if result.get('status') == 429:
        print("Rate limit exceeded - wait before retrying")
else:
    # Process successful result
    print(f"Successfully crawled {result['pages_crawled']} pages")
```

### 5. Filter Content Effectively

Use domain filtering to stay focused:

```python
# Only get links from the same domain
links = crawler.handle_tool_call("extract_all_links", {
    "url": "https://example.com/page",
    "filter_domain": "example.com"
})

# Only crawl same domain
crawl = crawler.handle_tool_call("crawl_website", {
    "url": "https://example.com",
    "same_domain_only": True
})
```

### 6. Optimize Data Extraction

Extract only what you need to reduce processing time:

```python
# Minimal extraction
result = crawler.handle_tool_call("crawl_single_page", {
    "url": "https://example.com",
    "extract_links": False,
    "extract_metadata": False
})

# Targeted extraction
documents = crawler.handle_tool_call("extract_all_document_links", {
    "url": "https://example.com",
    "document_types": ["pdf"]  # Only PDFs
})
```

### 7. Use Sitemap for Efficiency

When available, use sitemaps for more efficient crawling:

```python
# Get sitemap URLs
sitemap = crawler.handle_tool_call("get_sitemap", {
    "url": "https://example.com"
})

# Crawl specific URLs from sitemap
for url in sitemap['urls'][:50]:  # First 50 URLs
    page = crawler.handle_tool_call("crawl_single_page", {
        "url": url
    })
    # Process page...
```

---

## Error Handling

### Common Errors

#### 1. Rate Limit Exceeded (429)

```json
{
  "error": "Rate limit exceeded",
  "status": 429
}
```

**Solution**: Wait before making additional requests. The tool limits to 100 requests per 10 seconds.

#### 2. Invalid URL

```json
{
  "error": "Invalid URL format"
}
```

**Solution**: Ensure URLs include protocol (http:// or https://)

```python
# Wrong
crawler.handle_tool_call("crawl_website", {"url": "example.com"})

# Correct
crawler.handle_tool_call("crawl_website", {"url": "https://example.com"})
```

#### 3. Failed to Fetch Page

```json
{
  "url": "https://example.com/page",
  "status": 404,
  "error": "Failed to fetch page"
}
```

**Solution**: Check URL validity, network connection, or server availability.

#### 4. Timeout Error

**Solution**: The default timeout is 10 seconds. Increase if needed:

```python
crawler.request_timeout = 20  # 20 seconds
```

### Error Handling Pattern

```python
def safe_crawl(crawler, url):
    try:
        result = crawler.handle_tool_call("crawl_website", {
            "url": url,
            "max_depth": 2,
            "max_pages": 25
        })
        
        if 'error' in result:
            if result.get('status') == 429:
                print("Rate limited - waiting 10 seconds")
                time.sleep(10)
                return safe_crawl(crawler, url)  # Retry
            else:
                print(f"Error: {result['error']}")
                return None
        
        return result
        
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None

# Usage
result = safe_crawl(crawler, "https://example.com")
if result:
    print(f"Successfully crawled {result['pages_crawled']} pages")
```

---

## Rate Limiting

### Built-in Rate Limiting

The tool implements automatic rate limiting to prevent abuse:

- **Limit**: 100 requests per 10-second window
- **Automatic**: No manual configuration needed
- **Blocking**: Exceeding the limit returns a 429 error

### Rate Limit Strategy

```python
from collections import deque
from time import time, sleep

class RateLimiter:
    def __init__(self, max_requests=100, time_window=10):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    def wait_if_needed(self):
        now = time()
        
        # Remove old requests
        while self.requests and self.requests[0] < now - self.time_window:
            self.requests.popleft()
        
        # Check if we need to wait
        if len(self.requests) >= self.max_requests:
            sleep_time = self.requests[0] + self.time_window - now
            if sleep_time > 0:
                print(f"Rate limit reached - sleeping {sleep_time:.2f}s")
                sleep(sleep_time)
                return self.wait_if_needed()
        
        self.requests.append(now)

# Usage
limiter = RateLimiter()

urls = [...]  # List of URLs
for url in urls:
    limiter.wait_if_needed()
    result = crawler.handle_tool_call("crawl_single_page", {"url": url})
```

### Distributed Crawling

For large-scale crawling, consider:

1. **Multiple instances** with different rate limits
2. **Queue-based system** with delay management
3. **Distributed workers** across different IPs

---

## Troubleshooting

### Issue: Pages Not Being Crawled

**Symptoms**: Fewer pages crawled than expected

**Possible Causes**:
1. Max depth reached
2. Max pages limit reached
3. URLs not on same domain (with `same_domain_only=True`)
4. Pages blocked by robots.txt

**Solution**:
```python
# Check robots.txt
robots = crawler.handle_tool_call("get_robots_txt", {
    "url": "https://example.com"
})

# Adjust settings
result = crawler.handle_tool_call("crawl_website", {
    "url": "https://example.com",
    "max_depth": 3,
    "max_pages": 100,
    "same_domain_only": False
})
```

### Issue: Incomplete Text Content

**Symptoms**: Text extraction missing content

**Possible Causes**:
1. JavaScript-rendered content (not supported)
2. Content in iframes
3. CSS-hidden elements

**Solution**:
- Use browser automation (Selenium/Playwright) for JavaScript sites
- The tool extracts static HTML only

### Issue: Document Links Not Found

**Symptoms**: `extract_all_document_links` returns empty

**Possible Causes**:
1. Links are JavaScript-generated
2. Links use different file extensions
3. Links are in iframes

**Solution**:
```python
# Try extracting all links first
all_links = crawler.handle_tool_call("extract_all_links", {
    "url": "https://example.com"
})

# Manually filter for documents
for link in all_links['links']:
    if any(ext in link['url'].lower() for ext in ['.pdf', '.doc', '.xls']):
        print(link)
```

### Issue: Slow Performance

**Symptoms**: Crawling takes too long

**Possible Causes**:
1. Network latency
2. Server response time
3. Too many pages

**Solution**:
```python
# Reduce scope
result = crawler.handle_tool_call("crawl_website", {
    "url": "https://example.com",
    "max_depth": 1,  # Reduce depth
    "max_pages": 20   # Reduce pages
})

# Increase timeout if needed
crawler.request_timeout = 15
```

### Issue: Memory Usage

**Symptoms**: High memory consumption

**Possible Causes**:
1. Large pages
2. Too many pages in memory

**Solution**:
- Process pages in batches
- Clear results after processing
- Use pagination

```python
# Process in batches
def crawl_in_batches(url, batch_size=25):
    results = []
    
    for i in range(0, 100, batch_size):
        batch_result = crawler.handle_tool_call("crawl_website", {
            "url": url,
            "max_pages": batch_size
        })
        
        # Process batch
        results.extend(batch_result['pages'])
        
        # Clear to free memory
        del batch_result
    
    return results
```

---

## Advanced Usage

### Custom User Agent

```python
crawler.headers['User-Agent'] = 'MyCompanyBot/1.0 (+https://mycompany.com/bot)'
```

### Custom Headers

```python
crawler.headers.update({
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://example.com',
    'Custom-Header': 'value'
})
```

### Connection Pooling

The tool uses `requests.Session` for connection pooling automatically:

```python
# Session is automatically reused
# Improves performance for multiple requests to same domain
```

### Parallel Crawling

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def crawl_url(url):
    return crawler.handle_tool_call("crawl_single_page", {"url": url})

urls = ["url1", "url2", "url3", ...]

with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_url = {executor.submit(crawl_url, url): url for url in urls}
    
    for future in as_completed(future_to_url):
        url = future_to_url[future]
        try:
            result = future.result()
            print(f"Crawled: {url}")
        except Exception as e:
            print(f"Error crawling {url}: {e}")
```

---

## API Versioning

**Current Version**: 1.0.0

### Changelog

#### Version 1.0.0 (2025-10-20)
- Initial release
- 12 core tools
- Support for up to 3-level crawling
- Document link extraction
- Table parsing
- Metadata extraction
- Rate limiting

---

## Support & Contributing

### Getting Help

- Check this documentation
- Review code examples
- Test with simple URLs first

### Reporting Issues

When reporting issues, include:
1. Tool name and parameters used
2. Full error message
3. URL being crawled (if not sensitive)
4. Expected vs actual behavior

### Best Practices for Production

1. **Always respect robots.txt**
2. **Implement exponential backoff** for retries
3. **Log all requests** for debugging
4. **Monitor rate limits** proactively
5. **Cache results** when possible
6. **Use appropriate timeouts**
7. **Handle all error cases**
8. **Test on small samples** first

---

## License

This tool is provided as-is for web crawling and data extraction purposes. Users are responsible for ensuring their use complies with applicable laws and website terms of service.

---

## Additional Resources

- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests Library Documentation](https://docs.python-requests.org/)
- [robots.txt Specification](https://www.robotstxt.org/)
- [Sitemap Protocol](https://www.sitemaps.org/)

---

**Last Updated**: October 20, 2025  
**Version**: 1.0.0  
**Maintainer**: MCP Tools Team


## Copyright Notice

© 2025 - 2030 Ashutosh Sinha.

All rights reserved. No part of this publication may be reproduced, distributed, or transmitted in any form or by any means, including photocopying, recording, or other electronic or mechanical methods, without the prior written permission of the publisher, except in the case of brief quotations embodied in critical reviews and certain other noncommercial uses permitted by copyright law.