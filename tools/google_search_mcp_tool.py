"""
Google Search MCP Tool implementation
"""
import os
from typing import Dict, Any, List
from .base_mcp_tool import BaseMCPTool
from googlesearch import search as google_search
import requests
from bs4 import BeautifulSoup


class GoogleSearchMCPTool(BaseMCPTool):
    """MCP Tool for Google Search operations"""

    def _initialize(self):
        """Initialize Google Search specific components"""
        self.api_key = os.environ.get('GOOGLE_API_KEY', '')
        self.custom_search_engine_id = os.environ.get('GOOGLE_CSE_ID', '')

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Google Search tool calls

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

            if tool_name == "google_search":
                result = self._search(arguments)
            elif tool_name == "google_image_search":
                result = self._image_search(arguments)
            elif tool_name == "google_news_search":
                result = self._news_search(arguments)
            elif tool_name == "google_scholar_search":
                result = self._scholar_search(arguments)
            elif tool_name == "google_site_search":
                result = self._site_search(arguments)
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
        Perform a standard Google search

        Args:
            params: Search parameters

        Returns:
            Search results
        """
        query = params.get('query', '')
        num_results = params.get('num_results', 10)
        language = params.get('language', 'en')
        safe = params.get('safe', 'off')

        results = []

        try:
            # Use Google Custom Search API if available
            if self.api_key and self.custom_search_engine_id:
                url = "https://www.googleapis.com/customsearch/v1"
                api_params = {
                    'key': self.api_key,
                    'cx': self.custom_search_engine_id,
                    'q': query,
                    'num': min(num_results, 10),  # API limit
                    'hl': language,
                    'safe': safe
                }

                response = requests.get(url, params=api_params)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', []):
                        results.append({
                            'title': item.get('title', ''),
                            'url': item.get('link', ''),
                            'snippet': item.get('snippet', '')
                        })
            else:
                # Fallback to web scraping (limited functionality)
                for url in google_search(query, num_results=num_results, lang=language, safe=safe):
                    results.append({
                        'url': url,
                        'title': self._get_page_title(url),
                        'snippet': ''
                    })

        except Exception as e:
            return {"error": str(e), "results": []}

        return {
            "query": query,
            "results": results,
            "count": len(results)
        }

    def _image_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform Google Image search

        Args:
            params: Search parameters

        Returns:
            Image search results
        """
        query = params.get('query', '')
        num_results = params.get('num_results', 10)
        size = params.get('size', 'medium')  # icon, small, medium, large, xlarge, xxlarge, huge
        image_type = params.get('type', 'photo')  # clipart, face, lineart, stock, photo, animated

        results = []

        if self.api_key and self.custom_search_engine_id:
            url = "https://www.googleapis.com/customsearch/v1"
            api_params = {
                'key': self.api_key,
                'cx': self.custom_search_engine_id,
                'q': query,
                'searchType': 'image',
                'num': min(num_results, 10),
                'imgSize': size,
                'imgType': image_type
            }

            try:
                response = requests.get(url, params=api_params)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', []):
                        results.append({
                            'title': item.get('title', ''),
                            'url': item.get('link', ''),
                            'thumbnail': item.get('image', {}).get('thumbnailLink', ''),
                            'context': item.get('displayLink', ''),
                            'width': item.get('image', {}).get('width', 0),
                            'height': item.get('image', {}).get('height', 0)
                        })
            except Exception as e:
                return {"error": str(e), "results": []}

        return {
            "query": query,
            "type": "image",
            "results": results,
            "count": len(results)
        }

    def _news_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform Google News search

        Args:
            params: Search parameters

        Returns:
            News search results
        """
        query = params.get('query', '')
        num_results = params.get('num_results', 10)
        date_restrict = params.get('date_restrict', 'd7')  # d[number] = days, w[number] = weeks, m[number] = months

        results = []

        # Add news search parameter to query
        news_query = f"{query} site:news.google.com OR news"

        if self.api_key and self.custom_search_engine_id:
            url = "https://www.googleapis.com/customsearch/v1"
            api_params = {
                'key': self.api_key,
                'cx': self.custom_search_engine_id,
                'q': news_query,
                'num': min(num_results, 10),
                'dateRestrict': date_restrict,
                'tbm': 'nws'  # News search
            }

            try:
                response = requests.get(url, params=api_params)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', []):
                        results.append({
                            'title': item.get('title', ''),
                            'url': item.get('link', ''),
                            'snippet': item.get('snippet', ''),
                            'source': item.get('displayLink', ''),
                            'published': item.get('pagemap', {}).get('metatags', [{}])[0].get('article:published_time',
                                                                                              '')
                        })
            except Exception as e:
                return {"error": str(e), "results": []}

        return {
            "query": query,
            "type": "news",
            "results": results,
            "count": len(results)
        }

    def _scholar_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform Google Scholar search (limited without official API)

        Args:
            params: Search parameters

        Returns:
            Scholar search results
        """
        query = params.get('query', '')
        year_from = params.get('year_from', '')
        year_to = params.get('year_to', '')

        # Note: Google Scholar doesn't have an official API
        # This is a basic implementation
        scholar_query = query
        if year_from:
            scholar_query += f" after:{year_from}"
        if year_to:
            scholar_query += f" before:{year_to}"

        results = []

        # Use regular search with scholar site restriction
        search_results = self._search({
            'query': f'site:scholar.google.com {scholar_query}',
            'num_results': 10
        })

        return {
            "query": query,
            "type": "scholar",
            "results": search_results.get('results', []),
            "count": search_results.get('count', 0),
            "note": "Limited functionality - Google Scholar API not available"
        }

    def _site_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform site-specific Google search

        Args:
            params: Search parameters

        Returns:
            Site-specific search results
        """
        query = params.get('query', '')
        site = params.get('site', '')
        num_results = params.get('num_results', 10)

        if not site:
            return {"error": "Site parameter is required", "results": []}

        # Modify query to include site restriction
        site_query = f"site:{site} {query}"

        return self._search({
            'query': site_query,
            'num_results': num_results
        })

    def _get_page_title(self, url: str) -> str:
        """
        Get the title of a web page

        Args:
            url: URL of the page

        Returns:
            Page title or empty string
        """
        try:
            response = requests.get(url, timeout=5, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.find('title')
                return title.text if title else ''
        except:
            pass
        return ''