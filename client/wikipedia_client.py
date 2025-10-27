"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Wikipedia Tool Client - Standalone Python client for Wikipedia MCP tool
"""

import json
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional


class WikipediaClient:
    """
    Standalone client for Wikipedia MCP tool
    """
    
    def __init__(self, base_url: str = "http://localhost:5000", api_token: Optional[str] = None):
        """
        Initialize Wikipedia client
        
        Args:
            base_url: Base URL of the MCP server
            api_token: Optional API authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.tool_name = "wikipedia"
    
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
    
    def search(self, query: str, limit: int = 5) -> Dict:
        """
        Search Wikipedia for articles matching the query
        
        Args:
            query: Search query string
            limit: Maximum number of results (1-20, default: 5)
            
        Returns:
            Dictionary containing search results
            
        Example:
            >>> client = WikipediaClient()
            >>> results = client.search("Python programming", limit=3)
            >>> print(results['count'])
            3
        """
        arguments = {
            "action": "search",
            "query": query,
            "limit": limit
        }
        
        return self._execute_tool(arguments)
    
    def get_page(self, title: str) -> Dict:
        """
        Get full Wikipedia page content
        
        Args:
            title: Wikipedia page title
            
        Returns:
            Dictionary containing full page content
            
        Example:
            >>> client = WikipediaClient()
            >>> page = client.get_page("Python (programming language)")
            >>> print(page['title'])
            >>> print(page['content'][:500])
        """
        arguments = {
            "action": "get_page",
            "query": title
        }
        
        return self._execute_tool(arguments)
    
    def get_summary(self, title: str) -> Dict:
        """
        Get Wikipedia page summary (first few sentences)
        
        Args:
            title: Wikipedia page title
            
        Returns:
            Dictionary containing page summary
            
        Example:
            >>> client = WikipediaClient()
            >>> summary = client.get_summary("Artificial Intelligence")
            >>> print(summary['summary'])
        """
        arguments = {
            "action": "get_summary",
            "query": title
        }
        
        return self._execute_tool(arguments)
    
    def search_and_get_summary(self, query: str) -> Dict:
        """
        Convenience method: Search and get summary of first result
        
        Args:
            query: Search query string
            
        Returns:
            Dictionary containing summary of first search result
            
        Example:
            >>> client = WikipediaClient()
            >>> result = client.search_and_get_summary("Machine Learning")
            >>> print(result['summary'])
        """
        # First search
        search_results = self.search(query, limit=1)
        
        if search_results.get('count', 0) > 0:
            first_result = search_results['results'][0]
            title = first_result['title']
            
            # Get summary of first result
            return self.get_summary(title)
        else:
            raise Exception(f"No results found for query: {query}")


def main():
    """
    Main function demonstrating Wikipedia client usage
    """
    print("=" * 80)
    print("Wikipedia MCP Tool Client - Demo")
    print("=" * 80)
    print()
    
    # Initialize client
    # For local testing without authentication
    client = WikipediaClient(base_url="http://localhost:5000")
    
    # For production with authentication
    # client = WikipediaClient(base_url="https://your-mcp-server.com", api_token="your-token")
    
    try:
        # Example 1: Search for articles
        print("Example 1: Searching Wikipedia")
        print("-" * 80)
        query = "Python programming"
        print(f"Query: {query}")
        print()
        
        search_results = client.search(query, limit=5)
        print(f"Found {search_results['count']} results:")
        print()
        
        for i, result in enumerate(search_results['results'], 1):
            print(f"{i}. {result['title']}")
            print(f"   Description: {result['description']}")
            print(f"   URL: {result['url']}")
            print()
        
        # Example 2: Get page summary
        print("\n" + "=" * 80)
        print("Example 2: Getting Page Summary")
        print("-" * 80)
        title = "Artificial Intelligence"
        print(f"Title: {title}")
        print()
        
        summary = client.get_summary(title)
        print(f"Page ID: {summary['pageid']}")
        print(f"Title: {summary['title']}")
        print(f"URL: {summary['url']}")
        print()
        print("Summary:")
        print(summary['summary'])
        
        # Example 3: Get full page content
        print("\n" + "=" * 80)
        print("Example 3: Getting Full Page Content")
        print("-" * 80)
        title = "Machine Learning"
        print(f"Title: {title}")
        print()
        
        page = client.get_page(title)
        print(f"Page ID: {page['pageid']}")
        print(f"Title: {page['title']}")
        print(f"URL: {page['url']}")
        print()
        print("Content (first 500 characters):")
        print(page['content'][:500] + "...")
        
        # Example 4: Search and get summary (convenience method)
        print("\n" + "=" * 80)
        print("Example 4: Search and Get Summary (Convenience Method)")
        print("-" * 80)
        query = "Quantum Computing"
        print(f"Query: {query}")
        print()
        
        result = client.search_and_get_summary(query)
        print(f"Title: {result['title']}")
        print(f"Summary: {result['summary']}")
        
        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nNote: Make sure the MCP server is running at the specified URL")


if __name__ == "__main__":
    main()
