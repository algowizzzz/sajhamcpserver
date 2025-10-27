"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Google Search Tool Client - Standalone Python client for Google Search MCP tool
"""

import json
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional


class GoogleSearchClient:
    """
    Standalone client for Google Search MCP tool
    """
    
    def __init__(self, base_url: str = "http://localhost:5000", api_token: Optional[str] = None):
        """
        Initialize Google Search client
        
        Args:
            base_url: Base URL of the MCP server
            api_token: Optional API authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.tool_name = "google_search"
    
    def _execute_tool(self, arguments: Dict[str, Any]) -> Dict:
        """
        Execute tool via MCP server API
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        url = f"{self.base_url}/api/tools/execute"
        
        payload = {
            "tool": self.tool_name,
            "arguments": arguments
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('success'):
                    return result.get('result', {})
                else:
                    raise Exception(f"Tool execution failed: {result.get('error')}")
                    
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            raise Exception(f"HTTP Error {e.code}: {error_msg}")
        except Exception as e:
            raise Exception(f"Failed to execute tool: {str(e)}")
    
    def search(self, 
               query: str, 
               num_results: int = 10, 
               start: int = 1,
               safe_search: str = "medium",
               search_type: str = "web") -> Dict:
        """
        Perform a web search
        
        Args:
            query: Search query string
            num_results: Number of results to return (1-10)
            start: Starting index for pagination
            safe_search: Safe search level (off, medium, high)
            search_type: Type of search (web, image, video)
            
        Returns:
            Dictionary containing search results
            
        Example:
            >>> client = GoogleSearchClient()
            >>> results = client.search("Python programming", num_results=5)
            >>> for result in results['results']:
            ...     print(f"{result['title']}: {result['link']}")
        """
        arguments = {
            "query": query,
            "num_results": num_results,
            "start": start,
            "safe_search": safe_search,
            "search_type": search_type
        }
        
        return self._execute_tool(arguments)
    
    def search_site(self, query: str, site: str, num_results: int = 10) -> Dict:
        """
        Search within a specific site
        
        Args:
            query: Search query string
            site: Site to restrict search to (e.g., wikipedia.org)
            num_results: Number of results to return
            
        Returns:
            Dictionary containing search results
            
        Example:
            >>> client = GoogleSearchClient()
            >>> results = client.search_site("artificial intelligence", "wikipedia.org")
            >>> print(results['count'])
        """
        arguments = {
            "query": query,
            "site": site,
            "num_results": num_results
        }
        
        return self._execute_tool(arguments)
    
    def image_search(self, query: str, num_results: int = 10) -> Dict:
        """
        Search for images
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            Dictionary containing image search results
            
        Example:
            >>> client = GoogleSearchClient()
            >>> results = client.image_search("sunset photography")
            >>> for result in results['results']:
            ...     if 'image' in result:
            ...         print(f"Image: {result['image']['thumbnailLink']}")
        """
        arguments = {
            "query": query,
            "num_results": num_results,
            "search_type": "image"
        }
        
        return self._execute_tool(arguments)
    
    def paginated_search(self, query: str, total_results: int = 20) -> List[Dict]:
        """
        Perform paginated search to get more than 10 results
        
        Args:
            query: Search query string
            total_results: Total number of results to retrieve
            
        Returns:
            List of all search results
            
        Example:
            >>> client = GoogleSearchClient()
            >>> all_results = client.paginated_search("machine learning", total_results=25)
            >>> print(f"Retrieved {len(all_results)} results")
        """
        all_results = []
        start = 1
        
        while len(all_results) < total_results:
            # Calculate how many results to fetch in this batch
            remaining = total_results - len(all_results)
            num_results = min(remaining, 10)
            
            try:
                results = self.search(query, num_results=num_results, start=start)
                
                if results.get('count', 0) == 0:
                    break
                
                all_results.extend(results['results'])
                start += num_results
                
            except Exception as e:
                print(f"Error fetching results at start={start}: {e}")
                break
        
        return all_results
    
    def safe_search_strict(self, query: str, num_results: int = 10) -> Dict:
        """
        Perform search with strict safe search enabled
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            Dictionary containing filtered search results
            
        Example:
            >>> client = GoogleSearchClient()
            >>> results = client.safe_search_strict("education resources")
        """
        return self.search(query, num_results=num_results, safe_search="high")
    
    def search_news(self, query: str, num_results: int = 10) -> Dict:
        """
        Search for news articles (using site restriction)
        
        Args:
            query: Search query string
            num_results: Number of results to return
            
        Returns:
            Dictionary containing news search results
            
        Example:
            >>> client = GoogleSearchClient()
            >>> results = client.search_news("technology trends 2025")
        """
        # This uses site restriction as a workaround for news search
        # In production, you might want to use Google News API
        news_sites = "news.google.com OR cnn.com OR bbc.com OR reuters.com"
        modified_query = f"{query} ({news_sites})"
        
        return self.search(modified_query, num_results=num_results)


def main():
    """
    Main function demonstrating Google Search client usage
    """
    print("=" * 80)
    print("Google Search MCP Tool Client - Demo")
    print("=" * 80)
    print()
    
    # Initialize client
    # For local testing without authentication
    client = GoogleSearchClient(base_url="http://localhost:5000")
    
    # For production with authentication
    # client = GoogleSearchClient(base_url="https://your-mcp-server.com", api_token="your-token")
    
    try:
        # Example 1: Basic web search
        print("Example 1: Basic Web Search")
        print("-" * 80)
        query = "Python programming language"
        print(f"Query: {query}")
        print()
        
        results = client.search(query, num_results=5)
        print(f"Total Results: {results['totalResults']}")
        print(f"Search Time: {results['searchTime']} seconds")
        print(f"Returned: {results['count']} results")
        print()
        
        for i, result in enumerate(results['results'], 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['link']}")
            print(f"   Domain: {result['displayLink']}")
            print(f"   Snippet: {result['snippet']}")
            print()
        
        # Example 2: Site-specific search
        print("=" * 80)
        print("Example 2: Site-Specific Search")
        print("-" * 80)
        query = "machine learning"
        site = "wikipedia.org"
        print(f"Query: {query}")
        print(f"Site: {site}")
        print()
        
        results = client.search_site(query, site, num_results=5)
        print(f"Found {results['count']} results on {site}:")
        print()
        
        for i, result in enumerate(results['results'], 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['link']}")
            print(f"   Snippet: {result['snippet'][:100]}...")
            print()
        
        # Example 3: Image search
        print("=" * 80)
        print("Example 3: Image Search")
        print("-" * 80)
        query = "mountain landscape"
        print(f"Query: {query}")
        print()
        
        results = client.image_search(query, num_results=5)
        print(f"Found {results['count']} image results:")
        print()
        
        for i, result in enumerate(results['results'], 1):
            print(f"{i}. {result['title']}")
            if 'image' in result:
                print(f"   Thumbnail: {result['image']['thumbnailLink']}")
                print(f"   Size: {result['image']['width']}x{result['image']['height']}")
                print(f"   Context: {result['image']['contextLink']}")
            else:
                print(f"   Link: {result['link']}")
            print()
        
        # Example 4: Paginated search
        print("=" * 80)
        print("Example 4: Paginated Search (Multiple Pages)")
        print("-" * 80)
        query = "artificial intelligence"
        total = 15
        print(f"Query: {query}")
        print(f"Fetching {total} results...")
        print()
        
        all_results = client.paginated_search(query, total_results=total)
        print(f"Retrieved {len(all_results)} total results:")
        print()
        
        for i, result in enumerate(all_results[:10], 1):
            print(f"{i}. {result['title'][:60]}...")
            print(f"   {result['displayLink']}")
        
        if len(all_results) > 10:
            print(f"\n... and {len(all_results) - 10} more results")
        
        # Example 5: Safe search
        print("\n" + "=" * 80)
        print("Example 5: Safe Search (Strict Mode)")
        print("-" * 80)
        query = "educational resources"
        print(f"Query: {query}")
        print(f"Safe Search: High")
        print()
        
        results = client.safe_search_strict(query, num_results=3)
        print(f"Found {results['count']} family-friendly results:")
        print()
        
        for i, result in enumerate(results['results'], 1):
            print(f"{i}. {result['title']}")
            print(f"   {result['link']}")
            print()
        
        # Example 6: News search
        print("=" * 80)
        print("Example 6: News Search")
        print("-" * 80)
        query = "technology news 2025"
        print(f"Query: {query}")
        print()
        
        results = client.search_news(query, num_results=5)
        print(f"Found {results['count']} news results:")
        print()
        
        for i, result in enumerate(results['results'], 1):
            print(f"{i}. {result['title']}")
            print(f"   Source: {result['displayLink']}")
            print(f"   URL: {result['link']}")
            print(f"   Snippet: {result['snippet'][:100]}...")
            print()
        
        print("=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)
        
        # Check for demo mode note
        if 'note' in results:
            print("\n" + "!" * 80)
            print("NOTE: " + results['note'])
            print("!" * 80)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nNote: Make sure the MCP server is running at the specified URL")
        print("      and that you have configured Google Search API credentials")


if __name__ == "__main__":
    main()
