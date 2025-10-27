"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Federal Reserve Tool Client - Standalone Python client for FRED MCP tool
"""

import json
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class FedReserveClient:
    """
    Standalone client for Federal Reserve Economic Data (FRED) MCP tool
    """
    
    def __init__(self, base_url: str = "http://localhost:5000", api_token: Optional[str] = None):
        """
        Initialize Federal Reserve client
        
        Args:
            base_url: Base URL of the MCP server
            api_token: Optional API authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.tool_name = "fed_reserve"
        
        # Common economic indicators
        self.indicators = {
            'gdp': 'Gross Domestic Product',
            'unemployment': 'Unemployment Rate',
            'inflation': 'Consumer Price Index',
            'fed_rate': 'Federal Funds Rate',
            'treasury_10y': '10-Year Treasury Rate',
            'treasury_2y': '2-Year Treasury Rate',
            'sp500': 'S&P 500 Index',
            'housing': 'Housing Starts',
            'retail': 'Retail Sales',
            'industrial': 'Industrial Production Index',
            'm2': 'M2 Money Supply',
            'pce': 'Personal Consumption Expenditures Price Index'
        }
    
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
    
    def get_series(self, 
                   series_id: Optional[str] = None,
                   indicator: Optional[str] = None,
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None,
                   limit: int = 100) -> Dict:
        """
        Get time series data from FRED
        
        Args:
            series_id: FRED series ID (e.g., GDP, UNRATE)
            indicator: Common indicator name (alternative to series_id)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Number of observations to return
            
        Returns:
            Dictionary containing time series data
            
        Example:
            >>> client = FedReserveClient()
            >>> data = client.get_series(indicator="gdp", limit=20)
            >>> print(f"Series: {data['title']}")
            >>> for obs in data['observations'][-5:]:
            ...     print(f"{obs['date']}: {obs['value']}")
        """
        arguments = {
            "action": "get_series",
            "limit": limit
        }
        
        if series_id:
            arguments["series_id"] = series_id
        elif indicator:
            arguments["indicator"] = indicator
        else:
            raise ValueError("Either series_id or indicator must be provided")
        
        if start_date:
            arguments["start_date"] = start_date
        if end_date:
            arguments["end_date"] = end_date
        
        return self._execute_tool(arguments)
    
    def get_latest(self, 
                   series_id: Optional[str] = None,
                   indicator: Optional[str] = None) -> Dict:
        """
        Get latest observation for a series
        
        Args:
            series_id: FRED series ID
            indicator: Common indicator name (alternative to series_id)
            
        Returns:
            Dictionary containing latest observation
            
        Example:
            >>> client = FedReserveClient()
            >>> data = client.get_latest(indicator="unemployment")
            >>> print(f"Latest unemployment rate: {data['value']}% as of {data['date']}")
        """
        arguments = {
            "action": "get_latest"
        }
        
        if series_id:
            arguments["series_id"] = series_id
        elif indicator:
            arguments["indicator"] = indicator
        else:
            raise ValueError("Either series_id or indicator must be provided")
        
        return self._execute_tool(arguments)
    
    def search_series(self, query: str) -> Dict:
        """
        Search for FRED series
        
        Args:
            query: Search query string
            
        Returns:
            Dictionary containing search results
            
        Example:
            >>> client = FedReserveClient()
            >>> results = client.search_series("employment")
            >>> for result in results['results'][:5]:
            ...     print(f"{result['id']}: {result['title']}")
        """
        arguments = {
            "action": "search_series",
            "query": query
        }
        
        return self._execute_tool(arguments)
    
    def get_common_indicators(self) -> Dict:
        """
        Get all common economic indicators with their latest values
        
        Returns:
            Dictionary containing all common indicators
            
        Example:
            >>> client = FedReserveClient()
            >>> indicators = client.get_common_indicators()
            >>> for name, data in indicators['indicators'].items():
            ...     if 'value' in data:
            ...         print(f"{name}: {data['value']} {data['units']}")
        """
        arguments = {
            "action": "get_common_indicators"
        }
        
        return self._execute_tool(arguments)
    
    def get_series_by_date_range(self,
                                  indicator: str,
                                  months_back: int = 12) -> Dict:
        """
        Get series data for a specific number of months back
        
        Args:
            indicator: Common indicator name
            months_back: Number of months to look back
            
        Returns:
            Dictionary containing time series data
            
        Example:
            >>> client = FedReserveClient()
            >>> data = client.get_series_by_date_range("inflation", months_back=24)
            >>> print(f"2-year inflation data: {data['observation_count']} observations")
        """
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=months_back*30)).strftime('%Y-%m-%d')
        
        return self.get_series(
            indicator=indicator,
            start_date=start_date,
            end_date=end_date,
            limit=1000
        )
    
    def compare_indicators(self, indicators: List[str]) -> Dict:
        """
        Compare multiple indicators with their latest values
        
        Args:
            indicators: List of indicator names
            
        Returns:
            Dictionary mapping indicators to their latest values
            
        Example:
            >>> client = FedReserveClient()
            >>> comparison = client.compare_indicators(["unemployment", "inflation", "fed_rate"])
            >>> for indicator, data in comparison.items():
            ...     print(f"{indicator}: {data['value']} ({data['date']})")
        """
        results = {}
        
        for indicator in indicators:
            try:
                latest = self.get_latest(indicator=indicator)
                results[indicator] = {
                    "title": latest.get('title'),
                    "value": latest.get('value'),
                    "date": latest.get('date'),
                    "units": latest.get('units')
                }
            except Exception as e:
                results[indicator] = {"error": str(e)}
        
        return results
    
    def get_economic_dashboard(self) -> Dict:
        """
        Get a comprehensive economic dashboard with key indicators
        
        Returns:
            Dictionary containing key economic metrics
            
        Example:
            >>> client = FedReserveClient()
            >>> dashboard = client.get_economic_dashboard()
            >>> print("Economic Dashboard:")
            >>> for category, indicators in dashboard.items():
            ...     print(f"\n{category}:")
            ...     for name, data in indicators.items():
            ...         print(f"  {name}: {data}")
        """
        key_indicators = ['gdp', 'unemployment', 'inflation', 'fed_rate']
        
        dashboard = {
            "employment": {},
            "prices": {},
            "rates": {},
            "growth": {}
        }
        
        comparison = self.compare_indicators(key_indicators)
        
        # Categorize indicators
        if 'unemployment' in comparison:
            dashboard['employment']['unemployment'] = comparison['unemployment']
        
        if 'inflation' in comparison:
            dashboard['prices']['inflation'] = comparison['inflation']
        
        if 'fed_rate' in comparison:
            dashboard['rates']['fed_funds_rate'] = comparison['fed_rate']
        
        if 'gdp' in comparison:
            dashboard['growth']['gdp'] = comparison['gdp']
        
        return dashboard
    
    def list_available_indicators(self) -> Dict[str, str]:
        """
        List all available common indicators
        
        Returns:
            Dictionary mapping indicator codes to descriptions
            
        Example:
            >>> client = FedReserveClient()
            >>> indicators = client.list_available_indicators()
            >>> for code, description in indicators.items():
            ...     print(f"{code}: {description}")
        """
        return self.indicators.copy()


def main():
    """
    Main function demonstrating Federal Reserve client usage
    """
    print("=" * 80)
    print("Federal Reserve (FRED) MCP Tool Client - Demo")
    print("=" * 80)
    print()
    
    # Initialize client
    # For local testing without authentication
    client = FedReserveClient(base_url="http://localhost:5000")
    
    # For production with authentication
    # client = FedReserveClient(base_url="https://your-mcp-server.com", api_token="your-token")
    
    try:
        # Example 1: List available indicators
        print("Example 1: Available Economic Indicators")
        print("-" * 80)
        indicators = client.list_available_indicators()
        print(f"Total available indicators: {len(indicators)}")
        print()
        
        for code, description in indicators.items():
            print(f"  {code:15} - {description}")
        
        # Example 2: Get latest value for an indicator
        print("\n" + "=" * 80)
        print("Example 2: Get Latest Economic Data")
        print("-" * 80)
        indicator = "unemployment"
        print(f"Indicator: {indicator}")
        print()
        
        latest = client.get_latest(indicator=indicator)
        print(f"Series: {latest['title']}")
        print(f"Latest Value: {latest['value']} {latest['units']}")
        print(f"Date: {latest['date']}")
        print(f"Frequency: {latest['frequency']}")
        print(f"Last Updated: {latest['last_updated']}")
        
        # Example 3: Get time series data
        print("\n" + "=" * 80)
        print("Example 3: Get Time Series Data")
        print("-" * 80)
        indicator = "gdp"
        limit = 10
        print(f"Indicator: {indicator}")
        print(f"Observations: Last {limit}")
        print()
        
        series = client.get_series(indicator=indicator, limit=limit)
        print(f"Series: {series['title']}")
        print(f"Units: {series['units']}")
        print(f"Frequency: {series['frequency']}")
        print(f"Total Observations: {series['observation_count']}")
        print()
        print("Recent values:")
        
        for obs in series['observations'][-5:]:
            if obs['value'] is not None:
                print(f"  {obs['date']}: {obs['value']:,.2f} {series['units']}")
        
        # Example 4: Search for series
        print("\n" + "=" * 80)
        print("Example 4: Search for FRED Series")
        print("-" * 80)
        query = "employment"
        print(f"Query: {query}")
        print()
        
        search_results = client.search_series(query)
        print(f"Found {search_results['count']} results:")
        print()
        
        for i, result in enumerate(search_results['results'][:5], 1):
            print(f"{i}. {result['id']}")
            print(f"   Title: {result['title']}")
            print(f"   Units: {result['units']}")
            print(f"   Frequency: {result['frequency']}")
            print(f"   Popularity: {result['popularity']}")
            print()
        
        # Example 5: Get all common indicators
        print("=" * 80)
        print("Example 5: Get All Common Economic Indicators")
        print("-" * 80)
        print()
        
        all_indicators = client.get_common_indicators()
        print(f"Last Updated: {all_indicators['last_updated']}")
        print()
        
        for name, data in all_indicators['indicators'].items():
            if 'value' in data:
                print(f"{name:15} {data['value']:>10} {data['units']:20} ({data['date']})")
            elif 'error' in data:
                print(f"{name:15} ERROR: {data['error']}")
        
        # Example 6: Compare multiple indicators
        print("\n" + "=" * 80)
        print("Example 6: Compare Multiple Indicators")
        print("-" * 80)
        indicators_to_compare = ["unemployment", "inflation", "fed_rate"]
        print(f"Comparing: {', '.join(indicators_to_compare)}")
        print()
        
        comparison = client.compare_indicators(indicators_to_compare)
        
        print(f"{'Indicator':<15} {'Value':<12} {'Date':<12} {'Units':<20}")
        print("-" * 65)
        
        for indicator, data in comparison.items():
            if 'error' not in data:
                print(f"{indicator:<15} {str(data['value']):<12} {data['date']:<12} {data['units']:<20}")
            else:
                print(f"{indicator:<15} Error: {data['error']}")
        
        # Example 7: Get series by date range
        print("\n" + "=" * 80)
        print("Example 7: Get Series Data by Date Range")
        print("-" * 80)
        indicator = "inflation"
        months = 12
        print(f"Indicator: {indicator}")
        print(f"Period: Last {months} months")
        print()
        
        range_data = client.get_series_by_date_range(indicator, months_back=months)
        print(f"Series: {range_data['title']}")
        print(f"Observations: {range_data['observation_count']}")
        print()
        print("Recent trend:")
        
        for obs in range_data['observations'][-6:]:
            if obs['value'] is not None:
                print(f"  {obs['date']}: {obs['value']:.2f}%")
        
        # Example 8: Economic dashboard
        print("\n" + "=" * 80)
        print("Example 8: Economic Dashboard")
        print("-" * 80)
        print()
        
        dashboard = client.get_economic_dashboard()
        
        for category, indicators in dashboard.items():
            print(f"\n{category.upper()}:")
            for name, data in indicators.items():
                if data and 'value' in data:
                    print(f"  {name}: {data['value']} {data.get('units', '')} (as of {data['date']})")
        
        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nNote: Make sure the MCP server is running at the specified URL")
        print("      FRED API may be in demo mode - configure API key for real data")


if __name__ == "__main__":
    main()
