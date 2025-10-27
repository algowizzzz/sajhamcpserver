# Yahoo Finance Tool Documentation

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

The Yahoo Finance Tool provides real-time and historical stock market data, including quotes, price history, and symbol search. It uses Yahoo Finance's free API endpoints for reliable financial data access.

### Features

- **Real-time Quotes**: Get current stock prices and market data
- **Historical Data**: Retrieve price history with various time periods
- **Symbol Search**: Find stock symbols by company name
- **No API Key Required**: Uses free Yahoo Finance endpoints
- **Multiple Intervals**: Support for various data granularities
- **Market Metrics**: Includes volume, market cap, 52-week highs/lows

### Specifications

- **Tool Name**: `yahoo_finance`
- **Category**: Financial Data
- **API Endpoint**: `query1.finance.yahoo.com`
- **Rate Limit**: 60 requests/hour (configurable)
- **Cache TTL**: 300 seconds (5 minutes)
- **Authentication**: Not required

---

## Configuration

### Configuration File

Location: `config/tools/yahoo_finance.json`

```json
{
  "name": "yahoo_finance",
  "type": "yahoo_finance",
  "description": "Retrieve stock market data from Yahoo Finance",
  "version": "1.0.0",
  "enabled": true,
  "inputSchema": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "description": "Action to perform",
        "enum": ["get_quote", "get_history", "search_symbols"]
      },
      "symbol": {
        "type": "string",
        "description": "Stock symbol (e.g., AAPL, GOOGL)"
      },
      "query": {
        "type": "string",
        "description": "Search query (for search_symbols)"
      },
      "period": {
        "type": "string",
        "description": "Time period for historical data",
        "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"],
        "default": "1mo"
      },
      "interval": {
        "type": "string",
        "description": "Data interval",
        "enum": ["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"],
        "default": "1d"
      }
    },
    "required": ["action"]
  },
  "metadata": {
    "author": "Ashutosh Sinha",
    "category": "Financial Data",
    "tags": ["finance", "stocks", "market"],
    "rateLimit": 60,
    "cacheTTL": 300
  }
}
```

---

## Actions

### 1. get_quote

Get current stock quote with real-time pricing and market data.

**Parameters:**
- `action`: "get_quote" (required)
- `symbol`: Stock symbol (required) - e.g., "AAPL", "GOOGL", "MSFT"

**Returns:**
```json
{
  "symbol": "AAPL",
  "currency": "USD",
  "exchange": "NMS",
  "regularMarketPrice": 178.45,
  "previousClose": 175.80,
  "regularMarketOpen": 176.20,
  "regularMarketDayHigh": 179.10,
  "regularMarketDayLow": 175.90,
  "regularMarketVolume": 52478900,
  "marketCap": 2789000000000,
  "fiftyTwoWeekHigh": 199.62,
  "fiftyTwoWeekLow": 164.08,
  "change": 2.65,
  "changePercent": 1.51,
  "timestamp": "2025-10-26T16:00:00"
}
```

### 2. get_history

Retrieve historical stock price data for a specified time period.

**Parameters:**
- `action`: "get_history" (required)
- `symbol`: Stock symbol (required)
- `period`: Time period (optional, default: "1mo")
  - Options: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"
- `interval`: Data interval (optional, default: "1d")
  - Options: "1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"

**Returns:**
```json
{
  "symbol": "AAPL",
  "currency": "USD",
  "exchange": "NMS",
  "period": "1mo",
  "interval": "1d",
  "dataPoints": 21,
  "history": [
    {
      "date": "2025-09-26T00:00:00",
      "open": 175.50,
      "high": 177.20,
      "low": 174.80,
      "close": 176.45,
      "volume": 48392100
    }
  ]
}
```

### 3. search_symbols

Search for stock symbols by company name or keyword.

**Parameters:**
- `action`: "search_symbols" (required)
- `query`: Search query (required) - company name or keyword

**Returns:**
```json
{
  "query": "apple",
  "count": 10,
  "results": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "type": "Equity",
      "exchange": "NASDAQ",
      "score": 10000
    },
    {
      "symbol": "AAPL.MX",
      "name": "Apple Inc.",
      "type": "Equity",
      "exchange": "Mexico",
      "score": 9500
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

# Get Yahoo Finance tool
finance_tool = registry.get_tool('yahoo_finance')

# Check if tool is available
if finance_tool is None:
    print("Yahoo Finance tool not found")
    exit(1)

# Check if tool is enabled
if not finance_tool.enabled:
    print("Yahoo Finance tool is disabled")
    exit(1)
```

### Example 1: Get Real-time Stock Quote

```python
from tools.tools_registry import ToolsRegistry
import json

registry = ToolsRegistry()
finance_tool = registry.get_tool('yahoo_finance')

# Get quote for Apple stock
arguments = {
    'action': 'get_quote',
    'symbol': 'AAPL'
}

try:
    result = finance_tool.execute_with_tracking(arguments)
    print(json.dumps(result, indent=2))
    
    # Display key metrics
    print(f"\n{result['symbol']} - {result['exchange']}")
    print(f"Current Price: ${result['regularMarketPrice']:.2f} {result['currency']}")
    print(f"Change: {result['change']:+.2f} ({result['changePercent']:+.2f}%)")
    print(f"Day Range: ${result['regularMarketDayLow']:.2f} - ${result['regularMarketDayHigh']:.2f}")
    print(f"52 Week Range: ${result['fiftyTwoWeekLow']:.2f} - ${result['fiftyTwoWeekHigh']:.2f}")
    print(f"Volume: {result['regularMarketVolume']:,}")
    print(f"Market Cap: ${result['marketCap']:,}")
    
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

**Sample Output:**
```
AAPL - NMS
Current Price: $178.45 USD
Change: +2.65 (+1.51%)
Day Range: $175.90 - $179.10
52 Week Range: $164.08 - $199.62
Volume: 52,478,900
Market Cap: $2,789,000,000,000
```

### Example 2: Get Historical Data

```python
from tools.tools_registry import ToolsRegistry
import json

registry = ToolsRegistry()
finance_tool = registry.get_tool('yahoo_finance')

# Get 1 year of daily data for Microsoft
arguments = {
    'action': 'get_history',
    'symbol': 'MSFT',
    'period': '1y',
    'interval': '1d'
}

try:
    result = finance_tool.execute_with_tracking(arguments)
    
    print(f"Symbol: {result['symbol']}")
    print(f"Period: {result['period']}")
    print(f"Interval: {result['interval']}")
    print(f"Data Points: {result['dataPoints']}")
    
    # Display first and last data points
    if result['history']:
        first = result['history'][0]
        last = result['history'][-1]
        
        print(f"\nFirst Trading Day:")
        print(f"  Date: {first['date']}")
        print(f"  Close: ${first['close']:.2f}")
        
        print(f"\nLast Trading Day:")
        print(f"  Date: {last['date']}")
        print(f"  Close: ${last['close']:.2f}")
        
        # Calculate return
        if first['close'] and last['close']:
            return_pct = ((last['close'] - first['close']) / first['close']) * 100
            print(f"\nTotal Return: {return_pct:+.2f}%")
    
except Exception as e:
    print(f"Error: {e}")
```

### Example 3: Search for Stock Symbols

```python
from tools.tools_registry import ToolsRegistry

registry = ToolsRegistry()
finance_tool = registry.get_tool('yahoo_finance')

# Search for Tesla
arguments = {
    'action': 'search_symbols',
    'query': 'Tesla'
}

try:
    result = finance_tool.execute_with_tracking(arguments)
    
    print(f"Search query: '{result['query']}'")
    print(f"Found {result['count']} results:\n")
    
    for i, stock in enumerate(result['results'][:5], 1):
        print(f"{i}. {stock['symbol']:10} - {stock['name']}")
        print(f"   Type: {stock['type']:10} Exchange: {stock['exchange']}")
        print()
    
except Exception as e:
    print(f"Error: {e}")
```

**Sample Output:**
```
Search query: 'Tesla'
Found 10 results:

1. TSLA       - Tesla, Inc.
   Type: Equity      Exchange: NASDAQ

2. TSLA.MX    - Tesla, Inc.
   Type: Equity      Exchange: Mexico

3. TL0.F      - Tesla, Inc.
   Type: Equity      Exchange: Frankfurt
```

### Example 4: Multi-Symbol Portfolio Tracker

```python
from tools.tools_registry import ToolsRegistry
import time

class PortfolioTracker:
    def __init__(self):
        registry = ToolsRegistry()
        self.finance_tool = registry.get_tool('yahoo_finance')
        
    def get_portfolio_value(self, holdings):
        """
        Calculate total portfolio value
        
        Args:
            holdings: dict of {symbol: shares}
        """
        total_value = 0
        portfolio_data = []
        
        for symbol, shares in holdings.items():
            try:
                result = self.finance_tool.execute_with_tracking({
                    'action': 'get_quote',
                    'symbol': symbol
                })
                
                current_price = result['regularMarketPrice']
                position_value = current_price * shares
                total_value += position_value
                
                portfolio_data.append({
                    'symbol': symbol,
                    'shares': shares,
                    'price': current_price,
                    'value': position_value,
                    'change_pct': result['changePercent']
                })
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"Error getting {symbol}: {e}")
        
        return {
            'total_value': total_value,
            'positions': portfolio_data
        }
    
    def display_portfolio(self, holdings):
        """Display portfolio summary"""
        portfolio = self.get_portfolio_value(holdings)
        
        print("Portfolio Summary")
        print("=" * 70)
        print(f"{'Symbol':<8} {'Shares':>8} {'Price':>12} {'Value':>15} {'Change':>10}")
        print("-" * 70)
        
        for position in portfolio['positions']:
            print(f"{position['symbol']:<8} "
                  f"{position['shares']:>8} "
                  f"${position['price']:>11.2f} "
                  f"${position['value']:>14.2f} "
                  f"{position['change_pct']:>9.2f}%")
        
        print("-" * 70)
        print(f"{'TOTAL':<8} {'':<8} {'':<12} ${portfolio['total_value']:>14.2f}")

# Usage
tracker = PortfolioTracker()
holdings = {
    'AAPL': 100,
    'GOOGL': 50,
    'MSFT': 75,
    'TSLA': 25
}
tracker.display_portfolio(holdings)
```

### Example 5: Technical Analysis Helper

```python
from tools.tools_registry import ToolsRegistry

def calculate_moving_average(history, period=20):
    """Calculate simple moving average"""
    if len(history) < period:
        return None
    
    prices = [day['close'] for day in history[-period:] if day['close']]
    return sum(prices) / len(prices)

def analyze_stock(symbol, period='3mo'):
    """Perform basic technical analysis"""
    registry = ToolsRegistry()
    finance_tool = registry.get_tool('yahoo_finance')
    
    # Get historical data
    result = finance_tool.execute_with_tracking({
        'action': 'get_history',
        'symbol': symbol,
        'period': period,
        'interval': '1d'
    })
    
    history = result['history']
    
    if not history:
        return None
    
    # Calculate metrics
    current_price = history[-1]['close']
    ma_20 = calculate_moving_average(history, 20)
    ma_50 = calculate_moving_average(history, 50)
    
    # Find highest and lowest prices
    prices = [day['close'] for day in history if day['close']]
    highest = max(prices)
    lowest = min(prices)
    
    # Analysis
    analysis = {
        'symbol': symbol,
        'current_price': current_price,
        'ma_20': ma_20,
        'ma_50': ma_50,
        'period_high': highest,
        'period_low': lowest,
        'distance_from_high': ((current_price - highest) / highest) * 100,
        'distance_from_low': ((current_price - lowest) / lowest) * 100
    }
    
    # Determine trend
    if ma_20 and ma_50:
        if current_price > ma_20 > ma_50:
            analysis['trend'] = 'Strong Uptrend'
        elif current_price > ma_20:
            analysis['trend'] = 'Uptrend'
        elif current_price < ma_20 < ma_50:
            analysis['trend'] = 'Strong Downtrend'
        elif current_price < ma_20:
            analysis['trend'] = 'Downtrend'
        else:
            analysis['trend'] = 'Sideways'
    
    return analysis

# Usage
analysis = analyze_stock('NVDA', period='6mo')
if analysis:
    print(f"\nTechnical Analysis: {analysis['symbol']}")
    print(f"Current Price: ${analysis['current_price']:.2f}")
    print(f"20-day MA: ${analysis['ma_20']:.2f}")
    print(f"50-day MA: ${analysis['ma_50']:.2f}")
    print(f"Trend: {analysis['trend']}")
    print(f"Distance from Period High: {analysis['distance_from_high']:.2f}%")
    print(f"Distance from Period Low: {analysis['distance_from_low']:.2f}%")
```

### Example 6: Stock Comparison Tool

```python
from tools.tools_registry import ToolsRegistry

def compare_stocks(symbols):
    """Compare multiple stocks side by side"""
    registry = ToolsRegistry()
    finance_tool = registry.get_tool('yahoo_finance')
    
    comparison = []
    
    for symbol in symbols:
        try:
            quote = finance_tool.execute_with_tracking({
                'action': 'get_quote',
                'symbol': symbol
            })
            
            comparison.append({
                'symbol': symbol,
                'price': quote['regularMarketPrice'],
                'change_pct': quote['changePercent'],
                'volume': quote['regularMarketVolume'],
                'market_cap': quote['marketCap'],
                '52w_high': quote['fiftyTwoWeekHigh'],
                '52w_low': quote['fiftyTwoWeekLow']
            })
            
        except Exception as e:
            print(f"Error getting {symbol}: {e}")
    
    # Display comparison
    print("\nStock Comparison")
    print("=" * 100)
    print(f"{'Symbol':<8} {'Price':>10} {'Change %':>10} {'Volume':>15} "
          f"{'Market Cap':>15} {'52W Range':>20}")
    print("-" * 100)
    
    for stock in comparison:
        range_str = f"${stock['52w_low']:.0f}-${stock['52w_high']:.0f}"
        print(f"{stock['symbol']:<8} "
              f"${stock['price']:>9.2f} "
              f"{stock['change_pct']:>9.2f}% "
              f"{stock['volume']:>14,} "
              f"${stock['market_cap']:>14,.0f} "
              f"{range_str:>20}")
    
    return comparison

# Usage
tech_stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META']
compare_stocks(tech_stocks)
```

---

## Web UI Usage

### Accessing the Tool

1. **Navigate to Tools Page**
   ```
   http://localhost:5000/tools
   ```

2. **Select Yahoo Finance Tool**
   - Find "yahoo_finance" in the tools list
   - Click "Execute" button

3. **Execute Tool Page**
   ```
   http://localhost:5000/tools/execute/yahoo_finance
   ```

### Using the Web Interface

#### Get Stock Quote

1. **Select Action**: Choose "get_quote" from dropdown
2. **Enter Symbol**: Type stock symbol (e.g., AAPL)
3. **Execute**: Click "Execute Tool" button

**Example Input:**
```
Action: get_quote
Symbol: TSLA
```

**Result Display:**
```json
{
  "symbol": "TSLA",
  "currency": "USD",
  "regularMarketPrice": 242.84,
  "change": 5.23,
  "changePercent": 2.20,
  "regularMarketVolume": 89234567,
  "marketCap": 768900000000
}
```

#### Get Historical Data

1. **Select Action**: Choose "get_history"
2. **Enter Symbol**: Type stock symbol
3. **Select Period**: Choose time range (e.g., "1y")
4. **Select Interval**: Choose data frequency (e.g., "1d")
5. **Execute**: Click "Execute Tool"

**Example Input:**
```
Action: get_history
Symbol: NVDA
Period: 6mo
Interval: 1d
```

#### Search Symbols

1. **Select Action**: Choose "search_symbols"
2. **Enter Query**: Type company name or keyword
3. **Execute**: Click "Execute Tool"

**Example Input:**
```
Action: search_symbols
Query: Microsoft
```

### Web UI Features

- **Real-time Data**: Live stock quotes when markets are open
- **Historical Charts**: Visual representation of price history
- **Symbol Validation**: Immediate feedback for invalid symbols
- **Currency Display**: Shows prices in appropriate currency
- **Formatted Numbers**: Easy-to-read formatting for large numbers
- **Execution History**: Track your recent queries

---

## Examples

### Complete Working Examples

#### Example 1: Daily Market Monitor

```python
from tools.tools_registry import ToolsRegistry
from datetime import datetime
import time

class MarketMonitor:
    def __init__(self, watchlist):
        registry = ToolsRegistry()
        self.finance_tool = registry.get_tool('yahoo_finance')
        self.watchlist = watchlist
    
    def get_market_snapshot(self):
        """Get current snapshot of watchlist"""
        print(f"\n{'='*70}")
        print(f"Market Snapshot - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        print(f"{'Symbol':<8} {'Price':>10} {'Change':>10} {'% Change':>12} {'Volume':>15}")
        print(f"{'-'*70}")
        
        for symbol in self.watchlist:
            try:
                quote = self.finance_tool.execute_with_tracking({
                    'action': 'get_quote',
                    'symbol': symbol
                })
                
                change_color = '+' if quote['change'] >= 0 else ''
                print(f"{symbol:<8} "
                      f"${quote['regularMarketPrice']:>9.2f} "
                      f"{change_color}{quote['change']:>9.2f} "
                      f"{change_color}{quote['changePercent']:>11.2f}% "
                      f"{quote['regularMarketVolume']:>14,}")
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                print(f"{symbol:<8} Error: {e}")
        
        print(f"{'='*70}\n")
    
    def monitor(self, interval=60):
        """Continuously monitor market (interval in seconds)"""
        try:
            while True:
                self.get_market_snapshot()
                print(f"Refreshing in {interval} seconds... (Ctrl+C to stop)")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")

# Usage
watchlist = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA']
monitor = MarketMonitor(watchlist)
monitor.get_market_snapshot()  # Single snapshot
# monitor.monitor(300)  # Continuous monitoring every 5 minutes
```

#### Example 2: Stock Alerts System

```python
from tools.tools_registry import ToolsRegistry
import time

class StockAlerts:
    def __init__(self):
        registry = ToolsRegistry()
        self.finance_tool = registry.get_tool('yahoo_finance')
        self.alerts = []
    
    def add_alert(self, symbol, condition, target_price):
        """
        Add price alert
        
        Args:
            symbol: Stock symbol
            condition: 'above' or 'below'
            target_price: Price threshold
        """
        self.alerts.append({
            'symbol': symbol,
            'condition': condition,
            'target_price': target_price,
            'triggered': False
        })
        print(f"Alert added: {symbol} {condition} ${target_price}")
    
    def check_alerts(self):
        """Check all alerts and trigger if conditions met"""
        for alert in self.alerts:
            if alert['triggered']:
                continue
            
            try:
                quote = self.finance_tool.execute_with_tracking({
                    'action': 'get_quote',
                    'symbol': alert['symbol']
                })
                
                current_price = quote['regularMarketPrice']
                
                if alert['condition'] == 'above' and current_price >= alert['target_price']:
                    self.trigger_alert(alert, current_price)
                elif alert['condition'] == 'below' and current_price <= alert['target_price']:
                    self.trigger_alert(alert, current_price)
                
            except Exception as e:
                print(f"Error checking {alert['symbol']}: {e}")
    
    def trigger_alert(self, alert, current_price):
        """Trigger an alert"""
        alert['triggered'] = True
        print(f"\n🔔 ALERT TRIGGERED! 🔔")
        print(f"{alert['symbol']} is now {alert['condition']} ${alert['target_price']}")
        print(f"Current price: ${current_price:.2f}")
        print()
    
    def monitor_alerts(self, check_interval=60):
        """Continuously monitor alerts"""
        print(f"Monitoring {len(self.alerts)} alerts...")
        try:
            while any(not a['triggered'] for a in self.alerts):
                self.check_alerts()
                active_alerts = sum(1 for a in self.alerts if not a['triggered'])
                if active_alerts > 0:
                    print(f"Checking again in {check_interval} seconds... "
                          f"({active_alerts} alerts active)")
                    time.sleep(check_interval)
                else:
                    print("All alerts triggered!")
                    break
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")

# Usage
alerts = StockAlerts()
alerts.add_alert('AAPL', 'above', 180.00)
alerts.add_alert('TSLA', 'below', 240.00)
alerts.add_alert('NVDA', 'above', 500.00)
# alerts.monitor_alerts(check_interval=300)
```

#### Example 3: Performance Report Generator

```python
from tools.tools_registry import ToolsRegistry
from datetime import datetime

def generate_performance_report(symbol, period='1y'):
    """Generate comprehensive performance report"""
    registry = ToolsRegistry()
    finance_tool = registry.get_tool('yahoo_finance')
    
    # Get current quote
    quote = finance_tool.execute_with_tracking({
        'action': 'get_quote',
        'symbol': symbol
    })
    
    # Get historical data
    history = finance_tool.execute_with_tracking({
        'action': 'get_history',
        'symbol': symbol,
        'period': period,
        'interval': '1d'
    })
    
    # Calculate metrics
    prices = [day['close'] for day in history['history'] if day['close']]
    volumes = [day['volume'] for day in history['history'] if day['volume']]
    
    first_price = prices[0]
    last_price = prices[-1]
    highest = max(prices)
    lowest = min(prices)
    avg_volume = sum(volumes) / len(volumes)
    
    total_return = ((last_price - first_price) / first_price) * 100
    
    # Generate report
    report = f"""
{'='*70}
PERFORMANCE REPORT: {symbol}
{'='*70}

Report Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Period: {period}

CURRENT METRICS
{'-'*70}
Current Price:        ${quote['regularMarketPrice']:.2f}
Day's Change:         {quote['change']:+.2f} ({quote['changePercent']:+.2f}%)
Day's Range:          ${quote['regularMarketDayLow']:.2f} - ${quote['regularMarketDayHigh']:.2f}
Volume:               {quote['regularMarketVolume']:,}
Market Cap:           ${quote['marketCap']:,.0f}

PERIOD PERFORMANCE
{'-'*70}
Starting Price:       ${first_price:.2f}
Ending Price:         ${last_price:.2f}
Total Return:         {total_return:+.2f}%
Period High:          ${highest:.2f}
Period Low:           ${lowest:.2f}
Average Volume:       {avg_volume:,.0f}

52-WEEK METRICS
{'-'*70}
52-Week High:         ${quote['fiftyTwoWeekHigh']:.2f}
52-Week Low:          ${quote['fiftyTwoWeekLow']:.2f}
From 52W High:        {((quote['regularMarketPrice'] - quote['fiftyTwoWeekHigh']) / quote['fiftyTwoWeekHigh'] * 100):.2f}%
From 52W Low:         {((quote['regularMarketPrice'] - quote['fiftyTwoWeekLow']) / quote['fiftyTwoWeekLow'] * 100):.2f}%

{'='*70}
    """
    
    print(report)
    return report

# Usage
generate_performance_report('AAPL', period='1y')
```

---

## Error Handling

### Common Errors

#### 1. Symbol Not Found

**Error:**
```
ValueError: Symbol not found: INVALID
```

**Solution:**
- Use search_symbols to find correct symbol
- Verify symbol spelling and exchange

```python
# Find correct symbol first
search_result = finance_tool.execute_with_tracking({
    'action': 'search_symbols',
    'query': 'Apple'
})
# Use exact symbol from search results
```

#### 2. Invalid Period/Interval Combination

**Error:**
```
ValueError: Invalid period/interval combination
```

**Solution:**
- Intraday intervals (1m, 5m, etc.) only work with short periods (1d, 5d)
- Use daily or weekly intervals for longer periods

```python
# ✗ Wrong
{'period': '1y', 'interval': '1m'}  # Too much data

# ✓ Correct
{'period': '1y', 'interval': '1d'}  # Daily data for 1 year
{'period': '1d', 'interval': '5m'}  # 5-min data for 1 day
```

#### 3. Rate Limiting

**Error:**
```
ValueError: Failed to get quote: HTTP 429
```

**Solution:**
- Implement delays between requests
- Cache results when possible
- Reduce request frequency

```python
import time

for symbol in symbols:
    quote = finance_tool.execute_with_tracking({
        'action': 'get_quote',
        'symbol': symbol
    })
    time.sleep(0.5)  # 500ms delay
```

#### 4. Market Closed Data

**Situation:** Getting stale data when markets are closed

**Solution:**
- Check timestamp in response
- Use previousClose for after-hours reference
- Consider extended hours data if needed

```python
quote = finance_tool.execute_with_tracking({
    'action': 'get_quote',
    'symbol': 'AAPL'
})

from datetime import datetime
quote_time = datetime.fromisoformat(quote['timestamp'])
now = datetime.now()

if (now - quote_time).seconds > 900:  # 15 minutes
    print("Warning: Data may be delayed")
```

### Comprehensive Error Handling

```python
from tools.tools_registry import ToolsRegistry
import time

def safe_get_quote(symbol, max_retries=3):
    """Get stock quote with retry logic"""
    registry = ToolsRegistry()
    finance_tool = registry.get_tool('yahoo_finance')
    
    for attempt in range(max_retries):
        try:
            result = finance_tool.execute_with_tracking({
                'action': 'get_quote',
                'symbol': symbol
            })
            return {'success': True, 'data': result}
            
        except ValueError as e:
            error_msg = str(e)
            if 'not found' in error_msg.lower():
                # Symbol doesn't exist - don't retry
                return {'success': False, 'error': f'Symbol not found: {symbol}'}
            elif attempt < max_retries - 1:
                # Network or temporary error - retry
                wait_time = 2 ** attempt
                print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return {'success': False, 'error': str(e)}
                
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return {'success': False, 'error': f'Unexpected error: {str(e)}'}
    
    return {'success': False, 'error': 'Failed after retries'}

# Usage
result = safe_get_quote('AAPL')
if result['success']:
    print(f"Price: ${result['data']['regularMarketPrice']:.2f}")
else:
    print(f"Error: {result['error']}")
```

---

## Best Practices

### 1. Symbol Validation

Always validate symbols before getting quotes:

```python
def validate_and_get_quote(query):
    """Search for symbol, then get quote"""
    # Search first
    search = finance_tool.execute_with_tracking({
        'action': 'search_symbols',
        'query': query
    })
    
    if search['results']:
        symbol = search['results'][0]['symbol']
        # Get quote with validated symbol
        return finance_tool.execute_with_tracking({
            'action': 'get_quote',
            'symbol': symbol
        })
    else:
        raise ValueError(f"No symbols found for: {query}")
```

### 2. Implement Caching

Cache quotes to reduce API calls:

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedFinance:
    def __init__(self, cache_seconds=300):
        registry = ToolsRegistry()
        self.finance_tool = registry.get_tool('yahoo_finance')
        self.cache = {}
        self.cache_seconds = cache_seconds
    
    def get_quote(self, symbol):
        """Get quote with caching"""
        now = datetime.now()
        
        if symbol in self.cache:
            cached_time, cached_data = self.cache[symbol]
            if (now - cached_time).seconds < self.cache_seconds:
                return cached_data
        
        # Cache miss or expired
        quote = self.finance_tool.execute_with_tracking({
            'action': 'get_quote',
            'symbol': symbol
        })
        
        self.cache[symbol] = (now, quote)
        return quote
```

### 3. Batch Operations with Rate Limiting

```python
def batch_get_quotes(symbols, delay=0.5):
    """Get multiple quotes with rate limiting"""
    registry = ToolsRegistry()
    finance_tool = registry.get_tool('yahoo_finance')
    
    results = {}
    for symbol in symbols:
        try:
            quote = finance_tool.execute_with_tracking({
                'action': 'get_quote',
                'symbol': symbol
            })
            results[symbol] = quote
            time.sleep(delay)
        except Exception as e:
            results[symbol] = {'error': str(e)}
    
    return results
```

### 4. Data Validation

Validate received data before use:

```python
def validate_quote_data(quote):
    """Validate quote data completeness"""
    required_fields = ['symbol', 'regularMarketPrice', 'previousClose']
    
    for field in required_fields:
        if field not in quote:
            raise ValueError(f"Missing required field: {field}")
        if quote[field] is None or quote[field] == 0:
            raise ValueError(f"Invalid value for {field}")
    
    return True
```

---

## Troubleshooting

### Issue: Incorrect Prices

**Symptoms:** Prices seem wrong or outdated

**Solutions:**
1. Check if markets are currently open
2. Verify timestamp in response
3. Consider using different symbol (e.g., .L for London)
4. Check for stock splits or corporate actions

### Issue: Missing Historical Data

**Symptoms:** History has gaps or null values

**Solutions:**
1. Filter out null values in processing
2. Use longer intervals for older data
3. Check if symbol existed during entire period
4. Consider adjusted close prices for splits

### Issue: Search Returns Wrong Results

**Symptoms:** Symbol search returns unexpected results

**Solutions:**
1. Use more specific search terms
2. Include exchange suffix (e.g., AAPL.L)
3. Filter results by exchange or type
4. Check score field for relevance

---

## Additional Resources

- [Yahoo Finance API Documentation](https://finance.yahoo.com)
- [MCP Tools Overview](MCP_TOOLS_OVERVIEW.md)
- [Stock Symbol Conventions](https://finance.yahoo.com/lookup)

---

## Support

For issues or questions, contact:
**Ashutosh Sinha** - ajsinha@gmail.com

---

*Last Updated: October 26, 2025*