"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Yahoo Finance Tool Client - Standalone Python client for Yahoo Finance MCP tool
"""

import json
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional
from datetime import datetime


class YahooFinanceClient:
    """
    Standalone client for Yahoo Finance MCP tool
    """
    
    def __init__(self, base_url: str = "http://localhost:5000", api_token: Optional[str] = None):
        """
        Initialize Yahoo Finance client
        
        Args:
            base_url: Base URL of the MCP server
            api_token: Optional API authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.tool_name = "yahoo_finance"
    
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
    
    def get_quote(self, symbol: str) -> Dict:
        """
        Get current stock quote for a symbol
        
        Args:
            symbol: Stock symbol (e.g., AAPL, GOOGL, TSLA)
            
        Returns:
            Dictionary containing current quote data
            
        Example:
            >>> client = YahooFinanceClient()
            >>> quote = client.get_quote("AAPL")
            >>> print(f"Price: ${quote['regularMarketPrice']}")
            >>> print(f"Change: {quote['change']} ({quote['changePercent']}%)")
        """
        arguments = {
            "action": "get_quote",
            "symbol": symbol.upper()
        }
        
        return self._execute_tool(arguments)
    
    def get_history(self, symbol: str, period: str = "1mo", interval: str = "1d") -> Dict:
        """
        Get historical stock data
        
        Args:
            symbol: Stock symbol (e.g., AAPL, GOOGL, TSLA)
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            Dictionary containing historical data
            
        Example:
            >>> client = YahooFinanceClient()
            >>> history = client.get_history("AAPL", period="1y", interval="1d")
            >>> print(f"Data points: {history['dataPoints']}")
            >>> for point in history['history'][:5]:
            ...     print(f"{point['date']}: ${point['close']}")
        """
        arguments = {
            "action": "get_history",
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval
        }
        
        return self._execute_tool(arguments)
    
    def search_symbols(self, query: str) -> Dict:
        """
        Search for stock symbols
        
        Args:
            query: Search query (company name or symbol)
            
        Returns:
            Dictionary containing search results
            
        Example:
            >>> client = YahooFinanceClient()
            >>> results = client.search_symbols("Apple")
            >>> for result in results['results']:
            ...     print(f"{result['symbol']}: {result['name']}")
        """
        arguments = {
            "action": "search_symbols",
            "query": query
        }
        
        return self._execute_tool(arguments)
    
    def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Get quotes for multiple symbols
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary mapping symbols to quote data
            
        Example:
            >>> client = YahooFinanceClient()
            >>> quotes = client.get_multiple_quotes(["AAPL", "GOOGL", "MSFT"])
            >>> for symbol, quote in quotes.items():
            ...     print(f"{symbol}: ${quote['regularMarketPrice']}")
        """
        results = {}
        
        for symbol in symbols:
            try:
                results[symbol] = self.get_quote(symbol)
            except Exception as e:
                results[symbol] = {"error": str(e)}
        
        return results
    
    def get_price_change(self, symbol: str, period: str = "1mo") -> Dict:
        """
        Calculate price change over a period
        
        Args:
            symbol: Stock symbol
            period: Time period
            
        Returns:
            Dictionary with price change information
            
        Example:
            >>> client = YahooFinanceClient()
            >>> change = client.get_price_change("AAPL", period="1y")
            >>> print(f"Change: {change['price_change']} ({change['percent_change']}%)")
        """
        history = self.get_history(symbol, period=period, interval="1d")
        
        if history['dataPoints'] > 0:
            first_price = None
            last_price = None
            
            # Find first valid price
            for point in history['history']:
                if point['close'] is not None:
                    first_price = point['close']
                    first_date = point['date']
                    break
            
            # Find last valid price
            for point in reversed(history['history']):
                if point['close'] is not None:
                    last_price = point['close']
                    last_date = point['date']
                    break
            
            if first_price and last_price:
                price_change = last_price - first_price
                percent_change = (price_change / first_price) * 100
                
                return {
                    "symbol": symbol,
                    "period": period,
                    "start_date": first_date,
                    "end_date": last_date,
                    "start_price": first_price,
                    "end_price": last_price,
                    "price_change": round(price_change, 2),
                    "percent_change": round(percent_change, 2)
                }
        
        raise Exception(f"Unable to calculate price change for {symbol}")


def main():
    """
    Main function demonstrating Yahoo Finance client usage
    """
    print("=" * 80)
    print("Yahoo Finance MCP Tool Client - Demo")
    print("=" * 80)
    print()
    
    # Initialize client
    # For local testing without authentication
    client = YahooFinanceClient(base_url="http://localhost:5000")
    
    # For production with authentication
    # client = YahooFinanceClient(base_url="https://your-mcp-server.com", api_token="your-token")
    
    try:
        # Example 1: Get current stock quote
        print("Example 1: Getting Current Stock Quote")
        print("-" * 80)
        symbol = "AAPL"
        print(f"Symbol: {symbol}")
        print()
        
        quote = client.get_quote(symbol)
        print(f"Company: {quote['symbol']}")
        print(f"Exchange: {quote['exchange']}")
        print(f"Currency: {quote['currency']}")
        print(f"Current Price: ${quote['regularMarketPrice']:.2f}")
        print(f"Change: ${quote['change']:.2f} ({quote['changePercent']:.2f}%)")
        print(f"Open: ${quote['regularMarketOpen']:.2f}")
        print(f"Day High: ${quote['regularMarketDayHigh']:.2f}")
        print(f"Day Low: ${quote['regularMarketDayLow']:.2f}")
        print(f"Volume: {quote['regularMarketVolume']:,}")
        print(f"52 Week High: ${quote['fiftyTwoWeekHigh']:.2f}")
        print(f"52 Week Low: ${quote['fiftyTwoWeekLow']:.2f}")
        print(f"Last Updated: {quote['timestamp']}")
        
        # Example 2: Get historical data
        print("\n" + "=" * 80)
        print("Example 2: Getting Historical Data")
        print("-" * 80)
        symbol = "GOOGL"
        period = "1mo"
        interval = "1d"
        print(f"Symbol: {symbol}, Period: {period}, Interval: {interval}")
        print()
        
        history = client.get_history(symbol, period=period, interval=interval)
        print(f"Currency: {history['currency']}")
        print(f"Data Points: {history['dataPoints']}")
        print()
        print("Last 5 trading days:")
        for point in history['history'][-5:]:
            if point['close'] is not None:
                print(f"  {point['date'][:10]}: Open=${point['open']:.2f}, "
                      f"High=${point['high']:.2f}, Low=${point['low']:.2f}, "
                      f"Close=${point['close']:.2f}, Volume={point['volume']:,}")
        
        # Example 3: Search for symbols
        print("\n" + "=" * 80)
        print("Example 3: Searching for Stock Symbols")
        print("-" * 80)
        query = "Tesla"
        print(f"Query: {query}")
        print()
        
        search_results = client.search_symbols(query)
        print(f"Found {search_results['count']} results:")
        print()
        
        for result in search_results['results'][:5]:
            print(f"  {result['symbol']:10} {result['name']}")
            print(f"  {'':10} Type: {result['type']}, Exchange: {result['exchange']}")
            print()
        
        # Example 4: Get multiple quotes
        print("=" * 80)
        print("Example 4: Getting Multiple Quotes")
        print("-" * 80)
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        print(f"Symbols: {', '.join(symbols)}")
        print()
        
        quotes = client.get_multiple_quotes(symbols)
        print(f"{'Symbol':<10} {'Price':<12} {'Change':<12} {'Change %':<12}")
        print("-" * 50)
        
        for symbol, quote in quotes.items():
            if 'error' not in quote:
                print(f"{symbol:<10} ${quote['regularMarketPrice']:<11.2f} "
                      f"${quote['change']:<11.2f} {quote['changePercent']:<11.2f}%")
            else:
                print(f"{symbol:<10} Error: {quote['error']}")
        
        # Example 5: Calculate price change
        print("\n" + "=" * 80)
        print("Example 5: Calculating Price Change Over Period")
        print("-" * 80)
        symbol = "AAPL"
        period = "1y"
        print(f"Symbol: {symbol}, Period: {period}")
        print()
        
        change = client.get_price_change(symbol, period=period)
        print(f"Period: {change['start_date'][:10]} to {change['end_date'][:10]}")
        print(f"Start Price: ${change['start_price']:.2f}")
        print(f"End Price: ${change['end_price']:.2f}")
        print(f"Price Change: ${change['price_change']:.2f}")
        print(f"Percent Change: {change['percent_change']:.2f}%")
        
        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("\nNote: Make sure the MCP server is running at the specified URL")


if __name__ == "__main__":
    main()
