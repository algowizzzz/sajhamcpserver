"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Tavily Search Tool - Standalone Client

This client provides easy-to-use methods for interacting with the Tavily search tool.
It can be used independently or integrated into larger applications.
"""

import json
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional
from datetime import datetime


class TavilyClient:
    """
    Standalone client for Tavily Search Tool
    
    This client provides a convenient interface for executing searches
    using the Tavily tool through the MCP server API.
    """
    
    def __init__(self, base_url: str, api_token: Optional[str] = None):
        """
        Initialize Tavily client
        
        Args:
            base_url: Base URL of the MCP server (e.g., 'http://localhost:5000')
            api_token: Optional authentication token for the MCP server
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.tool_name = 'tavily'
        
    def _make_request(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make API request to execute tool
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Tool execution result
            
        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}/api/tools/execute"
        
        payload = {
            'tool': self.tool_name,
            'arguments': arguments
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.api_token:
            headers['Authorization'] = f'Bearer {self.api_token}'
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('success'):
                    return result.get('result', {})
                else:
                    raise Exception(f"Tool execution failed: {result.get('error', 'Unknown error')}")
                    
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8') if e.fp else str(e)
            raise Exception(f"HTTP error {e.code}: {error_msg}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = 'basic',
        topic: str = 'general',
        include_answer: bool = True
    ) -> Dict[str, Any]:
        """
        Perform a basic search
        
        Args:
            query: Search query
            max_results: Maximum number of results (1-20)
            search_depth: 'basic' or 'advanced'
            topic: 'general', 'news', 'finance', or 'science'
            include_answer: Include AI-generated answer
            
        Returns:
            Search results
        """
        arguments = {
            'query': query,
            'max_results': max_results,
            'search_depth': search_depth,
            'topic': topic,
            'include_answer': include_answer
        }
        
        return self._make_request(arguments)
    
    def advanced_search(
        self,
        query: str,
        max_results: int = 10,
        topic: str = 'general',
        include_answer: bool = True,
        include_images: bool = False,
        include_raw_content: bool = False,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform an advanced search with more options
        
        Args:
            query: Search query
            max_results: Maximum number of results (1-20)
            topic: Search topic category
            include_answer: Include AI-generated answer
            include_images: Include relevant images
            include_raw_content: Include raw HTML content
            include_domains: List of domains to include
            exclude_domains: List of domains to exclude
            
        Returns:
            Search results
        """
        arguments = {
            'query': query,
            'max_results': max_results,
            'search_depth': 'advanced',
            'topic': topic,
            'include_answer': include_answer,
            'include_images': include_images,
            'include_raw_content': include_raw_content
        }
        
        if include_domains:
            arguments['include_domains'] = include_domains
        if exclude_domains:
            arguments['exclude_domains'] = exclude_domains
        
        return self._make_request(arguments)
    
    def news_search(
        self,
        query: str,
        max_results: int = 7,
        include_answer: bool = True
    ) -> Dict[str, Any]:
        """
        Search for news articles
        
        Args:
            query: Search query
            max_results: Maximum number of results
            include_answer: Include AI-generated summary
            
        Returns:
            News search results
        """
        return self.search(
            query=query,
            max_results=max_results,
            search_depth='basic',
            topic='news',
            include_answer=include_answer
        )
    
    def finance_search(
        self,
        query: str,
        max_results: int = 5,
        include_answer: bool = True
    ) -> Dict[str, Any]:
        """
        Search for financial information
        
        Args:
            query: Search query
            max_results: Maximum number of results
            include_answer: Include AI-generated summary
            
        Returns:
            Finance search results
        """
        return self.search(
            query=query,
            max_results=max_results,
            search_depth='basic',
            topic='finance',
            include_answer=include_answer
        )
    
    def science_search(
        self,
        query: str,
        max_results: int = 5,
        search_depth: str = 'advanced',
        include_answer: bool = True
    ) -> Dict[str, Any]:
        """
        Search for scientific information
        
        Args:
            query: Search query
            max_results: Maximum number of results
            search_depth: Search depth
            include_answer: Include AI-generated summary
            
        Returns:
            Science search results
        """
        return self.search(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            topic='science',
            include_answer=include_answer
        )
    
    def academic_search(
        self,
        query: str,
        max_results: int = 10,
        include_answer: bool = True
    ) -> Dict[str, Any]:
        """
        Search academic sources (filters for .edu, .gov, academic publishers)
        
        Args:
            query: Search query
            max_results: Maximum number of results
            include_answer: Include AI-generated summary
            
        Returns:
            Academic search results
        """
        academic_domains = [
            'scholar.google.com',
            'nature.com',
            'science.org',
            'ieee.org',
            'acm.org',
            'arxiv.org'
        ]
        
        return self.advanced_search(
            query=query,
            max_results=max_results,
            topic='science',
            include_answer=include_answer,
            include_domains=academic_domains
        )
    
    def image_search(
        self,
        query: str,
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Search with images included
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            Search results with images
        """
        arguments = {
            'query': query,
            'max_results': max_results,
            'search_depth': 'basic',
            'topic': 'general',
            'include_answer': False,
            'include_images': True
        }
        
        return self._make_request(arguments)
    
    def quick_answer(self, query: str) -> str:
        """
        Get a quick AI-generated answer without full results
        
        Args:
            query: Search query
            
        Returns:
            AI-generated answer string
        """
        result = self.search(
            query=query,
            max_results=3,
            search_depth='basic',
            include_answer=True
        )
        
        return result.get('answer', 'No answer available')
    
    def print_results(self, results: Dict[str, Any], show_content: bool = True):
        """
        Pretty print search results
        
        Args:
            results: Search results dictionary
            show_content: Whether to show content snippets
        """
        print(f"\n{'='*80}")
        print(f"Query: {results.get('query', 'N/A')}")
        print(f"Results: {results.get('results_count', 0)}")
        print(f"Search Depth: {results.get('search_depth', 'N/A')}")
        print(f"Topic: {results.get('topic', 'N/A')}")
        print(f"{'='*80}\n")
        
        # Print AI answer if available
        if 'answer' in results:
            print("AI-GENERATED ANSWER:")
            print("-" * 80)
            print(results['answer'])
            print("-" * 80)
            print()
        
        # Print results
        for idx, item in enumerate(results.get('results', []), 1):
            print(f"{idx}. {item.get('title', 'Untitled')}")
            print(f"   URL: {item.get('url', 'N/A')}")
            print(f"   Score: {item.get('score', 0):.2f}")
            
            if item.get('published_date'):
                print(f"   Published: {item['published_date']}")
            
            if show_content and item.get('content'):
                content = item['content']
                # Truncate if too long
                if len(content) > 200:
                    content = content[:200] + "..."
                print(f"   {content}")
            
            print()
        
        # Print images if available
        if 'images' in results and results['images']:
            print("RELATED IMAGES:")
            print("-" * 80)
            for idx, img in enumerate(results['images'], 1):
                print(f"{idx}. {img.get('url', 'N/A')}")
                if img.get('description'):
                    print(f"   {img['description']}")
            print()
        
        # Print note if in demo mode
        if 'note' in results:
            print(f"Note: {results['note']}")
            print()


def main():
    """
    Main function with usage examples
    """
    # Initialize client
    # Replace with your actual server URL and token
    BASE_URL = 'http://localhost:5000'
    API_TOKEN = None  # Set your token if required
    
    client = TavilyClient(BASE_URL, API_TOKEN)
    
    print("="*80)
    print("TAVILY SEARCH TOOL - CLIENT EXAMPLES")
    print("="*80)
    
    # Example 1: Basic Search
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Search")
    print("="*80)
    
    try:
        results = client.search(
            query="artificial intelligence trends 2024",
            max_results=5
        )
        client.print_results(results)
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Advanced Search with Domain Filtering
    print("\n" + "="*80)
    print("EXAMPLE 2: Advanced Search with Domain Filtering")
    print("="*80)
    
    try:
        results = client.advanced_search(
            query="climate change impacts",
            max_results=7,
            topic="science",
            include_answer=True,
            include_domains=["nature.com", "science.org", "nasa.gov"]
        )
        client.print_results(results)
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: News Search
    print("\n" + "="*80)
    print("EXAMPLE 3: News Search")
    print("="*80)
    
    try:
        results = client.news_search(
            query="technology breakthroughs",
            max_results=5
        )
        client.print_results(results)
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Finance Search
    print("\n" + "="*80)
    print("EXAMPLE 4: Finance Search")
    print("="*80)
    
    try:
        results = client.finance_search(
            query="cryptocurrency market analysis",
            max_results=5
        )
        client.print_results(results)
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 5: Science Search
    print("\n" + "="*80)
    print("EXAMPLE 5: Science Search")
    print("="*80)
    
    try:
        results = client.science_search(
            query="quantum computing breakthroughs",
            max_results=5,
            search_depth="advanced"
        )
        client.print_results(results)
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 6: Academic Search
    print("\n" + "="*80)
    print("EXAMPLE 6: Academic Search")
    print("="*80)
    
    try:
        results = client.academic_search(
            query="machine learning algorithms",
            max_results=7
        )
        client.print_results(results)
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 7: Image Search
    print("\n" + "="*80)
    print("EXAMPLE 7: Image Search")
    print("="*80)
    
    try:
        results = client.image_search(
            query="data visualization examples",
            max_results=5
        )
        client.print_results(results)
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 8: Quick Answer
    print("\n" + "="*80)
    print("EXAMPLE 8: Quick Answer")
    print("="*80)
    
    try:
        question = "What is machine learning?"
        answer = client.quick_answer(question)
        print(f"Question: {question}")
        print(f"Answer: {answer}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 9: Search with Excluded Domains
    print("\n" + "="*80)
    print("EXAMPLE 9: Search with Excluded Domains")
    print("="*80)
    
    try:
        results = client.advanced_search(
            query="programming tutorials",
            max_results=5,
            exclude_domains=["reddit.com", "stackoverflow.com"]
        )
        client.print_results(results)
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 10: Custom Search Parameters
    print("\n" + "="*80)
    print("EXAMPLE 10: Custom Search Parameters")
    print("="*80)
    
    try:
        results = client.advanced_search(
            query="renewable energy innovations",
            max_results=8,
            topic="science",
            include_answer=True,
            include_images=True,
            search_depth="advanced"
        )
        client.print_results(results, show_content=True)
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)
    print("ALL EXAMPLES COMPLETED")
    print("="*80)


if __name__ == "__main__":
    """
    Run the client examples
    
    Usage:
        python tavily_client.py
    
    Configuration:
        Update BASE_URL and API_TOKEN in main() function
    """
    main()
