"""
Tavily MCP Tool implementation for news and entity search
"""
import os
import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_mcp_tool import BaseMCPTool


class TavilyMCPTool(BaseMCPTool):
    """MCP Tool for Tavily news and entity search operations"""

    def _initialize(self):
        """Initialize Tavily specific components"""
        self.api_key = os.environ.get('TAVILY_API_KEY', '')
        self.base_url = "https://api.tavily.com"

        if not self.api_key:
            print("Warning: TAVILY_API_KEY not set in environment variables")

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Tavily tool calls

        Args:
            tool_name: Name of the tool being called
            arguments: Arguments for the tool

        Returns:
            Result of the tool call
        """
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            if tool_name == "tavily_search":
                result = self._search(arguments)
            elif tool_name == "tavily_news_search":
                result = self._news_search(arguments)
            elif tool_name == "tavily_entity_search":
                result = self._entity_search(arguments)
            elif tool_name == "tavily_context_search":
                result = self._context_search(arguments)
            elif tool_name == "tavily_extract":
                result = self._extract_content(arguments)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            self.record_call(tool_name, arguments, result=result)
            return result

        except Exception as e:
            error_msg = str(e)
            self.record_call(tool_name, arguments, error=error_msg)
            return {"error": error_msg, "status": 500}

    def _search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a Tavily search

        Args:
            params: Search parameters

        Returns:
            Search results
        """
        if not self.api_key:
            return {"error": "Tavily API key not configured", "results": []}

        query = params.get('query', '')
        search_depth = params.get('search_depth', 'basic')  # basic or advanced
        max_results = params.get('max_results', 10)
        include_images = params.get('include_images', False)
        include_answer = params.get('include_answer', False)
        include_raw_content = params.get('include_raw_content', False)
        include_domains = params.get('include_domains', [])
        exclude_domains = params.get('exclude_domains', [])

        try:
            response = requests.post(
                f"{self.base_url}/search",
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "search_depth": search_depth,
                    "max_results": max_results,
                    "include_images": include_images,
                    "include_answer": include_answer,
                    "include_raw_content": include_raw_content,
                    "include_domains": include_domains,
                    "exclude_domains": exclude_domains
                },
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "query": query,
                    "results": data.get('results', []),
                    "answer": data.get('answer', ''),
                    "images": data.get('images', []),
                    "count": len(data.get('results', []))
                }
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "results": []
                }

        except Exception as e:
            return {"error": str(e), "results": []}

    def _news_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for news articles about entities or topics

        Args:
            params: Search parameters

        Returns:
            News search results
        """
        query = params.get('query', '')
        days_back = params.get('days_back', 7)
        topic = params.get('topic', '')  # e.g., 'technology', 'politics', 'business'

        # Add time restriction to query
        date_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        search_query = query
        if topic:
            search_query = f"{query} {topic} news"

        search_params = {
            'query': search_query,
            'search_depth': 'advanced',
            'max_results': params.get('max_results', 20),
            'include_answer': True
        }

        # Add news-focused domains if not specified
        if not params.get('include_domains'):
            search_params['include_domains'] = [
                'reuters.com', 'bloomberg.com', 'wsj.com', 'nytimes.com',
                'washingtonpost.com', 'bbc.com', 'cnn.com', 'apnews.com',
                'theguardian.com', 'forbes.com', 'businessinsider.com'
            ]

        results = self._search(search_params)

        # Filter results by date if possible
        if 'results' in results:
            filtered_results = []
            for result in results['results']:
                # Check if result has a date field and filter
                if 'published_date' in result:
                    try:
                        pub_date = datetime.strptime(result['published_date'], '%Y-%m-%d')
                        if pub_date >= datetime.strptime(date_from, '%Y-%m-%d'):
                            filtered_results.append(result)
                    except:
                        filtered_results.append(result)  # Keep if can't parse date
                else:
                    filtered_results.append(result)  # Keep if no date field

            results['results'] = filtered_results
            results['count'] = len(filtered_results)
            results['date_filter'] = f"Last {days_back} days"

        return results

    def _entity_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for information about specific entities (companies, people, places)

        Args:
            params: Search parameters

        Returns:
            Entity search results
        """
        entity_name = params.get('entity_name', '')
        entity_type = params.get('entity_type', '')  # 'company', 'person', 'place', 'organization'
        include_social = params.get('include_social', False)
        include_financial = params.get('include_financial', False)

        if not entity_name:
            return {"error": "Entity name is required", "results": []}

        # Build specialized query based on entity type
        query_parts = [entity_name]

        if entity_type == 'company':
            query_parts.extend(['company', 'corporation', 'business'])
            if include_financial:
                query_parts.extend(['revenue', 'earnings', 'stock', 'market cap'])
        elif entity_type == 'person':
            query_parts.extend(['biography', 'profile'])
            if include_social:
                query_parts.extend(['twitter', 'linkedin', 'social media'])
        elif entity_type == 'place':
            query_parts.extend(['location', 'geography', 'city', 'country'])
        elif entity_type == 'organization':
            query_parts.extend(['organization', 'institution', 'association'])

        search_query = ' '.join(query_parts)

        # Perform deep search for entities
        return self._search({
            'query': search_query,
            'search_depth': 'advanced',
            'max_results': params.get('max_results', 15),
            'include_answer': True,
            'include_raw_content': True
        })

    def _context_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search with context for more relevant results

        Args:
            params: Search parameters with context

        Returns:
            Contextual search results
        """
        query = params.get('query', '')
        context = params.get('context', '')  # Additional context for the search
        previous_queries = params.get('previous_queries', [])

        # Build enhanced query with context
        enhanced_query = query

        if context:
            enhanced_query = f"{context} {query}"

        # Add related terms from previous queries if available
        if previous_queries and len(previous_queries) > 0:
            related_terms = ' '.join(previous_queries[-3:])  # Use last 3 queries
            enhanced_query = f"{enhanced_query} related to {related_terms}"

        return self._search({
            'query': enhanced_query,
            'search_depth': 'advanced',
            'max_results': params.get('max_results', 10),
            'include_answer': True
        })

    def _extract_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract content from specific URLs

        Args:
            params: Extraction parameters

        Returns:
            Extracted content
        """
        urls = params.get('urls', [])

        if not urls:
            return {"error": "URLs are required", "results": []}

        if not self.api_key:
            return {"error": "Tavily API key not configured", "results": []}

        results = []

        for url in urls[:5]:  # Limit to 5 URLs
            try:
                response = requests.post(
                    f"{self.base_url}/extract",
                    json={
                        "api_key": self.api_key,
                        "url": url
                    },
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    data = response.json()
                    results.append({
                        'url': url,
                        'title': data.get('title', ''),
                        'content': data.get('content', ''),
                        'author': data.get('author', ''),
                        'published_date': data.get('published_date', ''),
                        'extracted': True
                    })
                else:
                    results.append({
                        'url': url,
                        'error': f"Failed to extract: status {response.status_code}",
                        'extracted': False
                    })

            except Exception as e:
                results.append({
                    'url': url,
                    'error': str(e),
                    'extracted': False
                })

        return {
            "urls_processed": len(urls),
            "results": results
        }