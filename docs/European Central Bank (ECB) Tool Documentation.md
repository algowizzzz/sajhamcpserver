# European Central Bank (ECB) Tool Documentation

**Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com**

## Overview

The European Central Bank (ECB) Tool provides seamless access to economic and financial data from the European Central Bank's Statistical Data Warehouse. This tool enables retrieval of exchange rates, interest rates, bond yields, inflation indicators, GDP, money supply, and unemployment data for the Eurozone.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Web UI Examples](#web-ui-examples)
- [Available Indicators](#available-indicators)
- [Error Handling](#error-handling)
- [Rate Limits](#rate-limits)

## Features

- **Exchange Rates**: EUR/USD, EUR/GBP, EUR/JPY, EUR/CNY, EUR/CHF
- **Interest Rates**: Main Refinancing Rate, Deposit Facility Rate, Marginal Lending Rate, EONIA, €STR
- **Bond Yields**: 2-year, 5-year, 10-year Euro Area Government Bonds
- **Inflation Metrics**: HICP Overall, Core HICP, Energy HICP
- **Economic Indicators**: GDP, Unemployment Rate
- **Monetary Aggregates**: M1, M2, M3
- **Historical Data**: Retrieve time series with custom date ranges
- **Latest Values**: Get most recent observations
- **No API Key Required**: Access public ECB data freely

## Installation

### Prerequisites

- Python 3.7 or higher
- Required packages (see requirements.txt)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Package Requirements

```
Flask>=3.0.0
requests>=2.31.0
jsonschema>=4.19.0
python-dotenv>=1.0.0
```

## Configuration

### JSON Configuration File

The `european_central_bank.json` file defines the tool configuration:

```json
{
  "name": "european_central_bank",
  "implementation": "tools.impl.european_central_bank_tool.EuropeanCentralBankTool",
  "description": "Retrieve economic and financial data from European Central Bank",
  "version": "1.0.0",
  "enabled": true,
  "metadata": {
    "author": "Ashutosh Sinha",
    "category": "Economic Data",
    "rateLimit": 120,
    "cacheTTL": 3600
  }
}
```

### Environment Variables (Optional)

Create a `.env` file for custom configurations:

```env
ECB_API_TIMEOUT=30
ECB_CACHE_ENABLED=true
ECB_CACHE_TTL=3600
```

## API Reference

### Actions

The tool supports the following actions:

#### 1. `get_series`

Retrieve time series data for a specific ECB series.

**Parameters:**
- `flow` (string, optional): ECB data flow identifier (e.g., "EXR", "FM", "ICP")
- `key` (string, optional): ECB series key
- `indicator` (string, optional): Common indicator name
- `start_date` (string, optional): Start date in YYYY-MM-DD format
- `end_date` (string, optional): End date in YYYY-MM-DD format
- `recent_periods` (integer, optional): Number of recent observations (default: 10)

**Note:** Either (`flow` and `key`) or `indicator` must be provided.

#### 2. `get_exchange_rate`

Get exchange rate data for a currency pair.

**Parameters:**
- `currency_pair` (string, optional): Currency pair (e.g., "EUR/USD")
- `indicator` (string, optional): Predefined indicator (e.g., "eur_usd")
- `recent_periods` (integer, optional): Number of recent observations (default: 10)

#### 3. `get_interest_rate`

Retrieve ECB interest rate data.

**Parameters:**
- `rate_type` (string): Type of rate
  - `main_refinancing_rate`
  - `deposit_facility_rate`
  - `marginal_lending_rate`
  - `eonia`
  - `ester`
- `recent_periods` (integer, optional): Number of recent observations (default: 10)

#### 4. `get_bond_yield`

Get Euro Area government bond yield data.

**Parameters:**
- `bond_term` (string): Bond maturity
  - `2y` - 2-Year bonds
  - `5y` - 5-Year bonds
  - `10y` - 10-Year bonds
- `recent_periods` (integer, optional): Number of recent observations (default: 10)

#### 5. `get_inflation`

Retrieve HICP (inflation) data.

**Parameters:**
- `inflation_type` (string): Type of inflation measure
  - `overall` - Overall HICP
  - `core` - Core HICP (excluding energy and food)
  - `energy` - Energy HICP
- `recent_periods` (integer, optional): Number of recent observations (default: 10)

#### 6. `get_latest`

Get the most recent observation for a series.

**Parameters:**
- `flow` (string, optional): ECB data flow identifier
- `key` (string, optional): ECB series key
- `indicator` (string, optional): Common indicator name

#### 7. `get_common_indicators`

Retrieve latest values for key economic indicators.

**Parameters:** None

**Returns:** Latest values for EUR/USD, Main Refinancing Rate, 10-Year Bond Yield, Overall HICP, and Unemployment Rate.

#### 8. `search_series`

List all available common series organized by category.

**Parameters:** None

## Usage Examples

### Programmatic API Calls

#### Example 1: Get EUR/USD Exchange Rate

```python
import requests
import json

# API endpoint
url = "http://localhost:5000/api/tools/execute"

# Request payload
payload = {
    "tool_name": "european_central_bank",
    "arguments": {
        "action": "get_exchange_rate",
        "indicator": "eur_usd",
        "recent_periods": 5
    }
}

# Execute request
response = requests.post(url, json=payload)
result = response.json()

print(json.dumps(result, indent=2))
```

**Response:**
```json
{
  "status": "success",
  "result": {
    "flow": "EXR",
    "key": "D.USD.EUR.SP00.A",
    "series_name": "D.USD.EUR.SP00.A",
    "description": "EUR/USD Exchange Rate Daily",
    "observation_count": 5,
    "observations": [
      {"date": "2025-10-20", "value": 1.0823},
      {"date": "2025-10-21", "value": 1.0835},
      {"date": "2025-10-22", "value": 1.0845},
      {"date": "2025-10-23", "value": 1.0830},
      {"date": "2025-10-24", "value": 1.0850}
    ]
  }
}
```

#### Example 2: Get ECB Main Refinancing Rate

```python
payload = {
    "tool_name": "european_central_bank",
    "arguments": {
        "action": "get_interest_rate",
        "rate_type": "main_refinancing_rate",
        "recent_periods": 10
    }
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
```

#### Example 3: Get 10-Year Bond Yield with Date Range

```python
payload = {
    "tool_name": "european_central_bank",
    "arguments": {
        "action": "get_bond_yield",
        "bond_term": "10y",
        "start_date": "2025-01-01",
        "end_date": "2025-03-31"
    }
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
```

#### Example 4: Get Overall Inflation (HICP)

```python
payload = {
    "tool_name": "european_central_bank",
    "arguments": {
        "action": "get_inflation",
        "inflation_type": "overall",
        "recent_periods": 12
    }
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
```

#### Example 5: Get Latest Common Indicators

```python
payload = {
    "tool_name": "european_central_bank",
    "arguments": {
        "action": "get_common_indicators"
    }
}

response = requests.post(url, json=payload)
result = response.json()

# Display key indicators
indicators = result['result']['indicators']
for name, data in indicators.items():
    if 'value' in data:
        print(f"{name}: {data['value']} (as of {data['date']})")
```

#### Example 6: Get Unemployment Rate

```python
payload = {
    "tool_name": "european_central_bank",
    "arguments": {
        "action": "get_series",
        "indicator": "unemployment_rate",
        "recent_periods": 6
    }
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
```

#### Example 7: Get M3 Money Supply

```python
payload = {
    "tool_name": "european_central_bank",
    "arguments": {
        "action": "get_series",
        "indicator": "m3",
        "recent_periods": 12
    }
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
```

#### Example 8: Get Latest EUR/GBP Exchange Rate

```python
payload = {
    "tool_name": "european_central_bank",
    "arguments": {
        "action": "get_latest",
        "indicator": "eur_gbp"
    }
}

response = requests.post(url, json=payload)
result = response.json()

latest = result['result']
print(f"EUR/GBP: {latest['value']} (as of {latest['date']})")
```

#### Example 9: Search Available Series

```python
payload = {
    "tool_name": "european_central_bank",
    "arguments": {
        "action": "search_series"
    }
}

response = requests.post(url, json=payload)
result = response.json()

# Display available categories
categories = result['result']['categories']
for category, series_list in categories.items():
    print(f"\n{category}:")
    for series in series_list:
        print(f"  - {series['indicator']}: {series['description']}")
```

#### Example 10: Get €STR (Euro Short-Term Rate)

```python
payload = {
    "tool_name": "european_central_bank",
    "arguments": {
        "action": "get_interest_rate",
        "rate_type": "ester",
        "recent_periods": 30
    }
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))
```

### Using the Standalone Client

```python
from european_central_bank_client import EuropeanCentralBankClient

# Initialize client
client = EuropeanCentralBankClient(base_url="http://localhost:5000")

# Get EUR/USD exchange rate
eur_usd = client.get_exchange_rate(indicator="eur_usd", recent_periods=5)
print(f"EUR/USD observations: {len(eur_usd['observations'])}")

# Get Main Refinancing Rate
rate = client.get_interest_rate(rate_type="main_refinancing_rate")
print(f"Latest rate: {rate['observations'][-1]['value']}%")

# Get 10-year bond yield
bond_yield = client.get_bond_yield(bond_term="10y", recent_periods=10)
print(f"10Y Yield: {bond_yield['observations'][-1]['value']}%")

# Get overall inflation
inflation = client.get_inflation(inflation_type="overall", recent_periods=12)
print(f"Latest HICP: {inflation['observations'][-1]['value']}%")

# Get latest common indicators
indicators = client.get_common_indicators()
for name, data in indicators['indicators'].items():
    if 'value' in data:
        print(f"{name}: {data['value']}")
```

## Web UI Examples

### Example 1: EUR/USD Exchange Rate via Web UI

1. Navigate to the MCP Server Web Interface
2. Select "European Central Bank" from the tools dropdown
3. Fill in the form:
   - **Action**: `get_exchange_rate`
   - **Indicator**: `eur_usd`
   - **Recent Periods**: `10`
4. Click "Execute Tool"
5. View the results displaying the last 10 EUR/USD exchange rates

### Example 2: Get Bond Yields via Web UI

1. Open the Web UI
2. Select "European Central Bank" tool
3. Configure:
   - **Action**: `get_bond_yield`
   - **Bond Term**: `10y`
   - **Recent Periods**: `20`
4. Click "Execute Tool"
5. Results show 10-year Euro Area bond yields

### Example 3: Monitor Inflation via Web UI

1. Access the tool interface
2. Select "European Central Bank"
3. Set parameters:
   - **Action**: `get_inflation`
   - **Inflation Type**: `overall`
   - **Recent Periods**: `12`
4. Execute to view 12 months of HICP data

### Example 4: Dashboard View of Common Indicators

1. Open Web UI
2. Select "European Central Bank" tool
3. Choose:
   - **Action**: `get_common_indicators`
4. Click "Execute Tool"
5. View dashboard with latest values for:
   - EUR/USD exchange rate
   - Main Refinancing Rate
   - 10-Year Bond Yield
   - Overall HICP
   - Unemployment Rate

## Available Indicators

### Exchange Rates

| Indicator | Description | Flow | Key |
|-----------|-------------|------|-----|
| `eur_usd` | EUR/USD Exchange Rate | EXR | D.USD.EUR.SP00.A |
| `eur_gbp` | EUR/GBP Exchange Rate | EXR | D.GBP.EUR.SP00.A |
| `eur_jpy` | EUR/JPY Exchange Rate | EXR | D.JPY.EUR.SP00.A |
| `eur_cny` | EUR/CNY Exchange Rate | EXR | D.CNY.EUR.SP00.A |
| `eur_chf` | EUR/CHF Exchange Rate | EXR | D.CHF.EUR.SP00.A |

### Interest Rates

| Indicator | Description | Flow | Key |
|-----------|-------------|------|-----|
| `main_refinancing_rate` | Main Refinancing Operations Rate | FM | B.U2.EUR.4F.KR.MRR_FR.LEV |
| `deposit_facility_rate` | Deposit Facility Rate | FM | B.U2.EUR.4F.KR.DFR.LEV |
| `marginal_lending_rate` | Marginal Lending Facility Rate | FM | B.U2.EUR.4F.KR.MLFR.LEV |
| `eonia` | Euro OverNight Index Average | FM | D.U2.EUR.4F.KR.EON.LEV |
| `ester` | Euro Short-Term Rate (€STR) | FM | D.U2.EUR.4F.KR.ESTER.LEV |

### Bond Yields

| Indicator | Description | Flow | Key |
|-----------|-------------|------|-----|
| `bond_2y` | 2-Year Euro Area Government Bond Yield | YC | B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y |
| `bond_5y` | 5-Year Euro Area Government Bond Yield | YC | B.U2.EUR.4F.G_N_A.SV_C_YM.SR_5Y |
| `bond_10y` | 10-Year Euro Area Government Bond Yield | YC | B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y |

### Inflation (HICP)

| Indicator | Description | Flow | Key |
|-----------|-------------|------|-----|
| `hicp_overall` | HICP - Overall Index | ICP | M.U2.N.000000.4.ANR |
| `hicp_core` | HICP - Excluding Energy and Food | ICP | M.U2.N.XEF000.4.ANR |
| `hicp_energy` | HICP - Energy | ICP | M.U2.N.NRG000.4.ANR |

### Economic Indicators

| Indicator | Description | Flow | Key |
|-----------|-------------|------|-----|
| `gdp` | GDP at Market Prices | MNA | Q.Y.I8.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.N |
| `unemployment_rate` | Unemployment Rate - Total | LFSI | M.U2.N.S.UNEH.RTT000.4.AV3 |

### Monetary Aggregates

| Indicator | Description | Flow | Key |
|-----------|-------------|------|-----|
| `m1` | Monetary Aggregate M1 | BSI | M.U2.Y.V.M10.X.1.U2.2300.Z01.E |
| `m2` | Monetary Aggregate M2 | BSI | M.U2.Y.V.M20.X.1.U2.2300.Z01.E |
| `m3` | Monetary Aggregate M3 | BSI | M.U2.Y.V.M30.X.1.U2.2300.Z01.E |

## Error Handling

### Common Errors

#### 1. Series Not Found (404)

```python
# Error response
{
  "status": "error",
  "error": "Series not found: EXR/D.XXX.EUR.SP00.A"
}
```

**Solution:** Verify the flow and key are correct or use a predefined indicator.

#### 2. Invalid Action

```python
# Error response
{
  "status": "error",
  "error": "Unknown action: invalid_action"
}
```

**Solution:** Use one of the supported actions listed in the API Reference.

#### 3. Missing Required Parameters

```python
# Error response
{
  "status": "error",
  "error": "Either 'flow' and 'key', or 'indicator' is required"
}
```

**Solution:** Provide either the flow/key combination or a predefined indicator.

#### 4. Invalid Date Format

```python
# Error response
{
  "status": "error",
  "error": "Invalid date format. Use YYYY-MM-DD"
}
```

**Solution:** Ensure dates are in YYYY-MM-DD format (e.g., "2025-01-15").

### Error Handling in Code

```python
import requests

try:
    response = requests.post(url, json=payload)
    response.raise_for_status()
    result = response.json()
    
    if result.get('status') == 'error':
        print(f"Tool Error: {result.get('error')}")
    else:
        # Process successful result
        data = result['result']
        
except requests.exceptions.RequestException as e:
    print(f"HTTP Error: {e}")
except json.JSONDecodeError as e:
    print(f"JSON Parse Error: {e}")
```

## Rate Limits

- **Rate Limit**: 120 requests per minute
- **Cache TTL**: 3600 seconds (1 hour)
- **Timeout**: 30 seconds per request

### Best Practices

1. **Use Caching**: Results are cached for 1 hour to improve performance
2. **Batch Requests**: Use `get_common_indicators` instead of multiple individual requests
3. **Handle Errors Gracefully**: Implement retry logic with exponential backoff
4. **Specify Date Ranges**: Request only the data you need to reduce response size

## Data Sources

- **Primary Source**: ECB Statistical Data Warehouse
- **API Documentation**: https://data.ecb.europa.eu/help/api/overview
- **Data Coverage**: Varies by series, generally from 1999 onwards for Eurozone data
- **Update Frequency**: Varies by series (daily, monthly, quarterly)

## Support and Contact

For questions or issues regarding this tool:

- **Author**: Ashutosh Sinha
- **Email**: ajsinha@gmail.com
- **Version**: 1.0.0

## License

Copyright All rights Reserved 2025-2030, Ashutosh Sinha

All rights reserved. Unauthorized copying, modification, distribution, or use of this software is strictly prohibited.

## Changelog

### Version 1.0.0 (2025)
- Initial release
- Support for exchange rates, interest rates, bond yields
- HICP inflation indicators
- GDP and unemployment data
- Monetary aggregates (M1, M2, M3)
- Common indicators dashboard
- Series search functionality

---

**Last Updated**: October 2025