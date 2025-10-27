# Bank of Canada Tool Documentation

**Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com**

## Overview

The Bank of Canada Tool provides access to Canadian economic and financial data through the Bank of Canada's Valet API. This tool enables retrieval of exchange rates, interest rates, bond yields, and various economic indicators without requiring an API key.

## Features

- **Exchange Rates**: Access daily exchange rates for major currencies
- **Interest Rates**: Retrieve policy rates, overnight rates, and prime rates
- **Bond Yields**: Get Government of Canada bond yields (2Y, 5Y, 10Y, 30Y)
- **Economic Indicators**: Access CPI, GDP, and other economic data
- **Historical Data**: Retrieve time series data with flexible date ranges
- **No API Key Required**: Free access to public data
- **High Data Quality**: Official data from Bank of Canada

## Installation

### Prerequisites

- Python 3.8 or higher
- No API key required (public data access)

### Setup

1. **Copy the tool files to your project:**
   ```bash
   # Copy tool implementation
   cp bank_of_canada_tool.py /path/to/your/project/tools/impl/
   
   # Copy configuration
   cp bank_of_canada.json /path/to/your/project/config/tools/
   ```

2. **Update Registry:**
   
   Add to `tools_registry.py`:
   ```python
   self.builtin_tools = {
       ...
       'bank_of_canada': 'tools.impl.bank_of_canada_tool.BankOfCanadaTool'
   }
   ```

3. **Restart Server:**
   ```bash
   python app.py
   ```

## Configuration

### JSON Configuration File (`bank_of_canada.json`)

```json
{
  "name": "bank_of_canada",
  "type": "bank_of_canada",
  "description": "Retrieve economic and financial data from Bank of Canada",
  "version": "1.0.0",
  "enabled": true,
  "inputSchema": { ... },
  "metadata": {
    "author": "Ashutosh Sinha",
    "category": "Economic Data",
    "tags": ["economics", "bank of canada", "canada", "financial"],
    "rateLimit": 120,
    "cacheTTL": 3600
  }
}
```

### Configuration Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `name` | string | Tool name | Yes |
| `type` | string | Tool type identifier | Yes |
| `enabled` | boolean | Enable/disable tool | No (default: true) |
| `rateLimit` | integer | Max requests per minute | No |
| `cacheTTL` | integer | Cache time in seconds | No |

## Usage

### Input Schema

```json
{
  "action": "string (required)",
  "series_name": "string",
  "indicator": "string",
  "currency_pair": "string",
  "rate_type": "string",
  "bond_term": "string",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "recent_periods": "integer (1-100, default: 10)"
}
```

### Actions

1. **get_series** - Get time series data
2. **get_exchange_rate** - Get currency exchange rates
3. **get_interest_rate** - Get interest rates
4. **get_bond_yield** - Get bond yields
5. **search_series** - List available series
6. **get_latest** - Get latest observation
7. **get_common_indicators** - Get key indicators

### Available Indicators

#### Exchange Rates
- `usd_cad` - US Dollar to Canadian Dollar
- `eur_cad` - Euro to Canadian Dollar
- `gbp_cad` - British Pound to Canadian Dollar
- `jpy_cad` - Japanese Yen to Canadian Dollar
- `cny_cad` - Chinese Yuan to Canadian Dollar

#### Interest Rates
- `policy_rate` - BoC Policy Interest Rate
- `overnight_rate` - Canadian Overnight Repo Rate Average (CORRA)
- `prime_rate` - Prime Business Rate

#### Bond Yields
- `bond_2y` - 2-Year Government Bond Yield
- `bond_5y` - 5-Year Government Bond Yield
- `bond_10y` - 10-Year Government Bond Yield
- `bond_30y` - 30-Year Government Bond Yield

#### Economic Indicators
- `cpi` - Consumer Price Index
- `core_cpi` - CPI Common (Core Inflation)
- `gdp` - Gross Domestic Product

## Programmatic Usage (Python)

### Method 1: Get Exchange Rates

```python
from tools.impl.bank_of_canada_tool import BankOfCanadaTool

# Initialize tool
config = {
    'name': 'bank_of_canada',
    'enabled': True
}

tool = BankOfCanadaTool(config)

# Example 1: Get USD/CAD exchange rate
arguments = {
    'action': 'get_exchange_rate',
    'indicator': 'usd_cad',
    'recent_periods': 10
}

result = tool.execute_with_tracking(arguments)
print(f"USD/CAD Exchange Rate Data:")
print(f"Series: {result['label']}")
print(f"Latest {len(result['observations'])} observations:")

for obs in result['observations']:
    print(f"  {obs['date']}: {obs['value']:.4f}")
```

**Output:**
```
USD/CAD Exchange Rate Data:
Series: US dollar, noon spot rate, CAD
Latest 10 observations:
  2024-10-25: 1.3845
  2024-10-24: 1.3820
  2024-10-23: 1.3795
  ...
```

### Method 2: Get Interest Rates

```python
# Example 2: Get Bank of Canada Policy Rate
arguments = {
    'action': 'get_interest_rate',
    'rate_type': 'policy_rate',
    'recent_periods': 5
}

result = tool.execute_with_tracking(arguments)

print(f"\nBank of Canada Policy Rate:")
print(f"Description: {result['description']}")

for obs in result['observations']:
    print(f"  {obs['date']}: {obs['value']:.2f}%")
```

**Output:**
```
Bank of Canada Policy Rate:
Description: Bank of Canada Policy Interest Rate
  2024-10-01: 4.25%
  2024-09-01: 4.50%
  2024-08-01: 4.50%
  2024-07-01: 4.75%
  2024-06-01: 4.75%
```

### Method 3: Get Bond Yields

```python
# Example 3: Get 10-Year Bond Yield
arguments = {
    'action': 'get_bond_yield',
    'bond_term': '10y',
    'recent_periods': 20
}

result = tool.execute_with_tracking(arguments)

print(f"\n10-Year Government of Canada Bond Yield:")
print(f"Total observations: {result['observation_count']}")

# Calculate average
values = [obs['value'] for obs in result['observations'] if obs['value']]
avg_yield = sum(values) / len(values)
print(f"Average yield: {avg_yield:.2f}%")

# Show recent values
print("\nRecent values:")
for obs in result['observations'][-5:]:
    print(f"  {obs['date']}: {obs['value']:.2f}%")
```

### Method 4: Get Historical Data with Date Range

```python
# Example 4: Get historical USD/CAD data
arguments = {
    'action': 'get_series',
    'indicator': 'usd_cad',
    'start_date': '2024-01-01',
    'end_date': '2024-03-31'
}

result = tool.execute_with_tracking(arguments)

print(f"\nUSD/CAD Q1 2024 Data:")
print(f"Series: {result['label']}")
print(f"Observations: {result['observation_count']}")

# Find min and max
rates = [obs['value'] for obs in result['observations'] if obs['value']]
print(f"High: {max(rates):.4f}")
print(f"Low: {min(rates):.4f}")
print(f"Average: {sum(rates)/len(rates):.4f}")
```

### Method 5: Get Common Indicators

```python
# Example 5: Get key economic indicators
arguments = {
    'action': 'get_common_indicators'
}

result = tool.execute_with_tracking(arguments)

print(f"\nKey Canadian Economic Indicators:")
print(f"Last Updated: {result['last_updated']}\n")

for indicator_name, data in result['indicators'].items():
    if 'value' in data:
        print(f"{data['description']}:")
        print(f"  Value: {data['value']}")
        print(f"  Date: {data['date']}")
        print()
```

**Output:**
```
Key Canadian Economic Indicators:
Last Updated: 2024-10-26T15:30:00

US Dollar to Canadian Dollar Exchange Rate:
  Value: 1.3845
  Date: 2024-10-25

Bank of Canada Policy Interest Rate:
  Value: 4.25
  Date: 2024-10-01

10-Year Government of Canada Bond Yield:
  Value: 3.15
  Date: 2024-10-25

Consumer Price Index:
  Value: 162.4
  Date: 2024-09-01
```

### Method 6: Get Latest Value for Any Series

```python
# Example 6: Get latest CPI value
arguments = {
    'action': 'get_latest',
    'indicator': 'cpi'
}

result = tool.execute_with_tracking(arguments)

print(f"\nLatest {result['label']}:")
print(f"Date: {result['date']}")
print(f"Value: {result['value']}")
print(f"Description: {result['description']}")
```

### Method 7: Using Tools Registry

```python
from tools.tools_registry import ToolsRegistry

# Get registry instance
registry = ToolsRegistry('config/tools')

# Get the tool
boc_tool = registry.get_tool('bank_of_canada')

# Get multiple exchange rates
currencies = ['usd_cad', 'eur_cad', 'gbp_cad']

print("Current Exchange Rates to CAD:")
for currency in currencies:
    arguments = {
        'action': 'get_latest',
        'indicator': currency
    }
    
    result = boc_tool.execute_with_tracking(arguments)
    print(f"{currency.upper()}: {result['value']:.4f} ({result['date']})")
```

### Error Handling

```python
try:
    result = tool.execute_with_tracking(arguments)
    
    if result['observation_count'] == 0:
        print("No data available for the specified period")
    else:
        # Process results
        pass
        
except ValueError as e:
    print(f"Validation error: {e}")
except RuntimeError as e:
    print(f"Tool execution error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Web UI Usage

### Accessing the Tool

1. **Navigate to Tools List:**
   - Open your web browser
   - Go to `http://your-server:port/tools`
   - Find "bank_of_canada" in the tools list

2. **Click "Execute" button** next to the Bank of Canada tool

### Example 1: Get Exchange Rate via Web UI

**Step 1: Fill in the form**

```
Action: get_exchange_rate
Indicator: usd_cad
Recent Periods: 10
```

**Step 2: Click "Execute Tool" button**

**Step 3: View Results**

Results will display:
```json
{
  "series_name": "FXUSDCAD",
  "label": "US dollar, noon spot rate, CAD",
  "description": "...",
  "observation_count": 10,
  "observations": [
    {
      "date": "2024-10-25",
      "value": 1.3845
    },
    ...
  ]
}
```

### Example 2: Get Interest Rate via Web UI

**Form Input:**
```
Action: get_interest_rate
Rate Type: policy_rate
Recent Periods: 5
```

**Expected Output:**
- Series name and description
- Historical policy rate changes
- Latest rate value and date

### Example 3: Get Bond Yields via Web UI

**Form Input:**
```
Action: get_bond_yield
Bond Term: 10y
Recent Periods: 20
```

**Expected Output:**
- 10-year bond yield time series
- Recent 20 observations
- Dates and yield values

### Example 4: Get Historical Data via Web UI

**Form Input:**
```
Action: get_series
Indicator: usd_cad
Start Date: 2024-01-01
End Date: 2024-03-31
```

**Expected Output:**
- Q1 2024 exchange rate data
- All observations in the date range
- Series information

### Example 5: Get Common Indicators via Web UI

**Form Input:**
```
Action: get_common_indicators
```

**Expected Output:**
- Key economic indicators
- Latest values for each
- Dates of observation
- Descriptions

### Example 6: Search Available Series via Web UI

**Form Input:**
```
Action: search_series
```

**Expected Output:**
- List of available series by category
- Exchange Rates
- Interest Rates
- Bond Yields
- Economic Indicators

## API Endpoint Usage

### REST API Call

```bash
# Using curl to get USD/CAD exchange rate
curl -X POST http://your-server:port/api/tools/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN" \
  -d '{
    "tool": "bank_of_canada",
    "arguments": {
      "action": "get_exchange_rate",
      "indicator": "usd_cad",
      "recent_periods": 10
    }
  }'
```

### Python Requests

```python
import requests
import json

# API endpoint
url = "http://your-server:port/api/tools/execute"

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_SESSION_TOKEN"
}

# Example 1: Get Policy Rate
payload = {
    "tool": "bank_of_canada",
    "arguments": {
        "action": "get_interest_rate",
        "rate_type": "policy_rate",
        "recent_periods": 5
    }
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    result = response.json()
    
    if result['success']:
        data = result['result']
        print(f"Policy Rate Data:")
        print(f"Series: {data['label']}")
        
        for obs in data['observations']:
            print(f"  {obs['date']}: {obs['value']}%")
    else:
        print(f"Error: {result['error']}")
else:
    print(f"HTTP Error: {response.status_code}")
```

```python
# Example 2: Get Bond Yields
payload = {
    "tool": "bank_of_canada",
    "arguments": {
        "action": "get_bond_yield",
        "bond_term": "10y",
        "recent_periods": 10
    }
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()['result']

print("10-Year Bond Yields:")
for obs in data['observations']:
    print(f"{obs['date']}: {obs['value']:.2f}%")
```

```python
# Example 3: Get Multiple Indicators
indicators = ['usd_cad', 'policy_rate', 'bond_10y']

for indicator in indicators:
    payload = {
        "tool": "bank_of_canada",
        "arguments": {
            "action": "get_latest",
            "indicator": indicator
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()['result']
        print(f"{data['label']}: {data['value']} ({data['date']})")
```

## Response Format

### Successful Response - Time Series

```json
{
  "series_name": "FXUSDCAD",
  "label": "US dollar, noon spot rate, CAD",
  "description": "Description of the series",
  "dimension": {
    "key": "value"
  },
  "observation_count": 10,
  "observations": [
    {
      "date": "2024-10-25",
      "value": 1.3845
    },
    {
      "date": "2024-10-24",
      "value": 1.3820
    }
  ]
}
```

### Successful Response - Latest Observation

```json
{
  "series_name": "POLICY_RATE",
  "label": "Bank of Canada Policy Interest Rate",
  "description": "Official policy rate",
  "date": "2024-10-01",
  "value": 4.25
}
```

### Successful Response - Common Indicators

```json
{
  "indicators": {
    "usd_cad": {
      "series_name": "FXUSDCAD",
      "label": "US dollar, noon spot rate, CAD",
      "value": 1.3845,
      "date": "2024-10-25",
      "description": "US Dollar to Canadian Dollar Exchange Rate"
    },
    "policy_rate": {
      "series_name": "POLICY_RATE",
      "label": "Bank of Canada Policy Interest Rate",
      "value": 4.25,
      "date": "2024-10-01",
      "description": "Bank of Canada Policy Interest Rate"
    }
  },
  "last_updated": "2024-10-26T15:30:00"
}
```

## Rate Limiting

- **Default Rate Limit**: 120 requests per minute
- **Configurable**: Adjust in `bank_of_canada.json`
- **Bank of Canada API**: No official rate limits for public data

## Caching

- **Default Cache TTL**: 3600 seconds (1 hour)
- **Configurable**: Adjust `cacheTTL` in configuration
- **Benefits**: Reduces API calls and improves response time

## Best Practices

### 1. Use Appropriate Date Ranges

```python
# For recent data, use recent_periods
arguments = {
    'action': 'get_series',
    'indicator': 'usd_cad',
    'recent_periods': 30  # Last 30 observations
}

# For specific periods, use date ranges
arguments = {
    'action': 'get_series',
    'indicator': 'usd_cad',
    'start_date': '2024-01-01',
    'end_date': '2024-12-31'
}
```

### 2. Use Indicator Names for Convenience

```python
# Easier to use
arguments = {'action': 'get_latest', 'indicator': 'usd_cad'}

# vs. using series names
arguments = {'action': 'get_latest', 'series_name': 'FXUSDCAD'}
```

### 3. Handle Missing Data

```python
result = tool.execute_with_tracking(arguments)

for obs in result['observations']:
    if obs['value'] is not None:
        # Process value
        print(f"{obs['date']}: {obs['value']}")
    else:
        print(f"{obs['date']}: No data")
```

### 4. Cache Results for Performance

```python
from datetime import datetime, timedelta

cache = {}
cache_duration = timedelta(hours=1)

def get_exchange_rate_cached(currency):
    cache_key = f"exchange_{currency}"
    
    if cache_key in cache:
        cached_data, timestamp = cache[cache_key]
        if datetime.now() - timestamp < cache_duration:
            return cached_data
    
    # Fetch fresh data
    result = tool.execute_with_tracking({
        'action': 'get_latest',
        'indicator': currency
    })
    
    cache[cache_key] = (result, datetime.now())
    return result
```

### 5. Batch Requests for Efficiency

```python
# Get multiple related indicators
indicators = {
    'Exchange Rates': ['usd_cad', 'eur_cad', 'gbp_cad'],
    'Interest Rates': ['policy_rate', 'overnight_rate', 'prime_rate'],
    'Bond Yields': ['bond_2y', 'bond_5y', 'bond_10y']
}

results = {}

for category, indicator_list in indicators.items():
    results[category] = {}
    for indicator in indicator_list:
        try:
            data = tool.execute_with_tracking({
                'action': 'get_latest',
                'indicator': indicator
            })
            results[category][indicator] = data['value']
        except Exception as e:
            print(f"Error fetching {indicator}: {e}")
```

## Troubleshooting

### Issue: "Series not found" error

**Solution:**
1. Check series name spelling
2. Use `search_series` action to list available series
3. Use indicator names instead of series names
4. Verify series exists on Bank of Canada website

### Issue: No data for specific date range

**Solution:**
1. Check if data is published for that period
2. Verify date format: YYYY-MM-DD
3. Ensure start_date is before end_date
4. Try using recent_periods instead

### Issue: Connection timeout

**Solution:**
1. Check internet connectivity
2. Verify Bank of Canada API is accessible
3. Increase timeout in configuration
4. Try again later (temporary API issues)

### Issue: Unexpected data values

**Solution:**
1. Verify correct series/indicator
2. Check units in series description
3. Some series may have null values
4. Confirm data frequency (daily, monthly, etc.)

## Tool Metrics

Access tool metrics programmatically:

```python
# Get tool metrics
metrics = tool.get_metrics()

print(f"Tool: {metrics['name']}")
print(f"Version: {metrics['version']}")
print(f"Enabled: {metrics['enabled']}")
print(f"Executions: {metrics['execution_count']}")
print(f"Last execution: {metrics['last_execution']}")
print(f"Avg time: {metrics['average_execution_time']:.2f}s")
```

## Data Sources

All data is sourced from:
- **Bank of Canada Valet API**: Official public API
- **Website**: https://www.bankofcanada.ca
- **API Documentation**: https://www.bankofcanada.ca/valet/docs

## Support and Resources

- **Bank of Canada API Docs**: https://www.bankofcanada.ca/valet/docs
- **Data Portal**: https://www.bankofcanada.ca/rates/
- **Tool Support**: ajsinha@gmail.com

## License

Copyright All rights Reserved 2025-2030, Ashutosh Sinha

## Version History

- **v1.0.0** (2024-10-26): Initial release
  - Exchange rate retrieval
  - Interest rate data
  - Bond yield data
  - Economic indicators
  - Historical data access
  - No API key required

## Examples Summary

### Quick Reference

```python
# 1. USD/CAD exchange rate
tool.execute_with_tracking({
    'action': 'get_exchange_rate',
    'indicator': 'usd_cad'
})

# 2. Policy interest rate
tool.execute_with_tracking({
    'action': 'get_interest_rate',
    'rate_type': 'policy_rate'
})

# 3. 10-year bond yield
tool.execute_with_tracking({
    'action': 'get_bond_yield',
    'bond_term': '10y'
})

# 4. Historical data
tool.execute_with_tracking({
    'action': 'get_series',
    'indicator': 'usd_cad',
    'start_date': '2024-01-01',
    'end_date': '2024-12-31'
})

# 5. Common indicators
tool.execute_with_tracking({
    'action': 'get_common_indicators'
})
```

---

**End of Documentation**