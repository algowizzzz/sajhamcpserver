# Limits vs Exposure Analysis Tool Documentation

**Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com**

## Overview

The Limits vs Exposure Analysis Tool provides comprehensive counterparty risk assessment by combining credit limit data with trading exposure data. This tool executes 16 different analytical queries to give a complete 360-degree view of counterparty risk, making it ideal for risk officers, credit analysts, and AI/LLM-based risk assessment systems.

## Features

- **Comprehensive Analysis**: 16 different analysis sections covering all aspects of counterparty risk
- **Flexible Input**: Accept either customer name or Adaptiv code as identifier
- **Selective Reporting**: Option to run only specific sections
- **Executive Summary**: Auto-generated summary with key risk indicators
- **LLM-Optimized**: Output format designed for AI consumption and natural language reporting
- **Real-Time**: Queries live data from DuckDB tables
- **Breach Detection**: Automatic identification of limit breaches and warnings

## Installation

### Prerequisites

- Python 3.8 or higher
- DuckDB OLAP Tools (must be configured and working)
- Data files: `trades.parquet` and `ccr_limits.parquet` in `data/duckdb/`

### Setup

1. **Copy Tool Files:**
   ```bash
   # Copy tool implementation
   cp limits_exposure_analysis_tool.py /path/to/project/tools/impl/
   
   # Copy configuration
   cp limits_exposure_analysis.json /path/to/project/config/tools/
   ```

2. **Verify DuckDB Tool:**
   ```bash
   # Ensure DuckDB tool is working
   python -c "from tools.impl.duckdb_olap_tools_tool import DuckDbOlapToolsTool; print('OK')"
   ```

3. **Restart Server:**
   ```bash
   python run_server.py
   ```

The tool will be automatically registered by the tools registry.

## Configuration

### JSON Configuration File

```json
{
  "name": "limits_exposure_analysis",
  "implementation": "tools.impl.limits_exposure_analysis_tool.LimitsExposureAnalysisTool",
  "enabled": true,
  "rateLimit": 30,
  "cacheTTL": 60
}
```

## Usage

### Input Schema

```json
{
  "counterparty_identifier": "string (required)",
  "include_sections": ["string (optional)"]
}
```

#### Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `counterparty_identifier` | string | Customer name or Adaptiv code | Yes |
| `include_sections` | array | Specific sections to include | No |

#### Available Sections

1. **overview** - Counterparty identity and credit info
2. **limit_status** - Current limit utilization and breach status
3. **trade_summary** - Trade count and notional summary
4. **mtm_pnl** - Mark-to-market and P&L analysis
5. **asset_class_breakdown** - Breakdown by asset class
6. **product_breakdown** - Breakdown by product type
7. **collateral_status** - Collateral and netting analysis
8. **desk_distribution** - Distribution across desks/books
9. **maturity_profile** - Maturity timeline analysis
10. **risk_greeks** - Delta, Gamma, Vega analysis
11. **failed_trades** - List of failed trades
12. **recent_activity** - Recent trading activity
13. **currency_exposure** - Currency breakdown
14. **risk_factors** - Top risk factors
15. **combined_view** - Trades vs limits comparison
16. **historical_limits** - Historical limit utilization

## Programmatic Usage (Python)

### Example 1: Full Analysis

```python
from tools.impl.limits_exposure_analysis_tool import LimitsExposureAnalysisTool

# Initialize tool
config = {
    'name': 'limits_exposure_analysis',
    'enabled': True
}

tool = LimitsExposureAnalysisTool(config)

# Run full analysis
result = tool.execute({
    'counterparty_identifier': 'Northbridge Capital'
})

# Access executive summary
summary = result['summary']
print(f"Customer: {summary['customer_name']}")
print(f"Limit Status: {summary['limit_status']}")
print(f"Utilization: {summary['limit_utilization_pct']}%")
print(f"Total Trades: {summary['total_trades']}")
print(f"Total Notional: ${summary['total_notional']:,.2f}")
print(f"Failed Trades: {summary['failed_trades_count']}")
```

**Output:**
```
Customer: Northbridge Capital
Limit Status: BREACH
Utilization: 113.81%
Total Trades: 16
Total Notional: $172,400,755.39
Failed Trades: 1
```

### Example 2: Analysis by Adaptiv Code

```python
# Use Adaptiv code instead of name
result = tool.execute({
    'counterparty_identifier': 'AC003'
})

# Check limit status
limit_status = result['sections']['limit_status']
print(f"Customer: {limit_status['customer_name']}")
print(f"Limit: ${limit_status['limit_ccr']:,}")
print(f"Exposure (EPE): ${limit_status['exposure_epe']:,.2f}")
print(f"Utilization: {limit_status['limit_utilization_pct']:.2f}%")
print(f"Status: {limit_status['limit_status']}")
```

**Output:**
```
Customer: Aurora Metals
Limit: $10,000,000
Exposure (EPE): $11,913,149.77
Utilization: 119.13%
Status: BREACH
```

### Example 3: Selective Sections

```python
# Request only specific sections
result = tool.execute({
    'counterparty_identifier': 'Lakeview Partners',
    'include_sections': [
        'limit_status',
        'trade_summary',
        'asset_class_breakdown',
        'failed_trades'
    ]
})

# Access specific sections
trade_summary = result['sections']['trade_summary']
print(f"Total Trades: {trade_summary['total_trades']}")
print(f"Total Notional: ${trade_summary['total_notional']:,.2f}")
print(f"Unique Products: {trade_summary['unique_products']}")

asset_breakdown = result['sections']['asset_class_breakdown']
for asset in asset_breakdown['breakdown']:
    print(f"{asset['asset_class']}: {asset['trade_count']} trades")
```

### Example 4: Monitoring All Counterparties

```python
# Check all counterparties for breaches
counterparties = ['AC001', 'AC002', 'AC003', 'AC004', 'AC005', 'AC006']

breaches = []
warnings = []
ok_list = []

for cp_id in counterparties:
    result = tool.execute({
        'counterparty_identifier': cp_id,
        'include_sections': ['overview', 'limit_status']
    })
    
    summary = result['summary']
    limit_status = summary['limit_status']
    
    cp_info = {
        'code': cp_id,
        'name': summary['customer_name'],
        'rating': summary['rating'],
        'utilization': summary['limit_utilization_pct']
    }
    
    if limit_status == 'BREACH':
        breaches.append(cp_info)
    elif limit_status == 'WARNING':
        warnings.append(cp_info)
    else:
        ok_list.append(cp_info)

print(f"🔴 Breaches: {len(breaches)}")
for cp in breaches:
    print(f"  - {cp['name']} ({cp['code']}): {cp['utilization']:.2f}%")

print(f"\n🟡 Warnings: {len(warnings)}")
for cp in warnings:
    print(f"  - {cp['name']} ({cp['code']}): {cp['utilization']:.2f}%")

print(f"\n🟢 OK: {len(ok_list)}")
```

**Output:**
```
🔴 Breaches: 2
  - Northbridge Capital (AC001): 113.81%
  - Aurora Metals (AC003): 119.13%

🟡 Warnings: 1
  - Pacific Energy (AC005): 90.99%

🟢 OK: 3
```

### Example 5: Asset Class Analysis

```python
result = tool.execute({
    'counterparty_identifier': 'Northbridge Capital',
    'include_sections': ['asset_class_breakdown', 'product_breakdown']
})

# Asset class breakdown
print("Asset Class Distribution:")
for asset in result['sections']['asset_class_breakdown']['breakdown']:
    pct = (asset['total_notional'] / result['summary']['total_notional']) * 100
    print(f"  {asset['asset_class']}: {asset['trade_count']} trades, "
          f"${asset['total_notional']:,.2f} ({pct:.1f}%)")

# Product breakdown
print("\nProduct Distribution:")
for product in result['sections']['product_breakdown']['breakdown']:
    print(f"  {product['product']} ({product['asset_class']}): "
          f"{product['trade_count']} trades, "
          f"${product['total_notional']:,.2f}")
```

### Example 6: Risk Greeks Analysis

```python
result = tool.execute({
    'counterparty_identifier': 'AC001',
    'include_sections': ['risk_greeks']
})

greeks = result['sections']['risk_greeks']['breakdown']

print("Risk Greeks by Asset Class:")
for item in greeks:
    print(f"\n{item['asset_class']}:")
    print(f"  Total Delta: {item['total_delta']:.4f}")
    print(f"  Total Gamma: {item['total_gamma']:.4f}")
    print(f"  Total Vega: {item['total_vega']:,.2f}")
    print(f"  Avg Delta: {item['avg_delta']:.4f}")
```

### Example 7: Failed Trades Investigation

```python
result = tool.execute({
    'counterparty_identifier': 'Northbridge Capital',
    'include_sections': ['failed_trades']
})

failed = result['sections']['failed_trades']
print(f"Failed Trades: {failed['count']}\n")

for trade in failed['failed_trades']:
    print(f"Trade ID: {trade['trade_id']}")
    print(f"  Product: {trade['product']}")
    print(f"  Notional: ${trade['notional']:,.2f}")
    print(f"  MTM: ${trade['mtm']:,.2f}")
    print(f"  Trade Date: {trade['trade_date']}")
    print(f"  Maturity: {trade['maturity_date']}")
    print()
```

### Example 8: Historical Trend Analysis

```python
result = tool.execute({
    'counterparty_identifier': 'AC001',
    'include_sections': ['historical_limits']
})

history = result['sections']['historical_limits']['history']

print("Historical Limit Utilization:")
print(f"{'Date':<12} {'EPE':>15} {'Limit':>15} {'Utilization':>12}")
print("-" * 60)

for record in history[:10]:  # Last 10 records
    print(f"{record['as_of_date']:<12} "
          f"${record['exposure_epe']:>14,.0f} "
          f"${record['limit_ccr']:>14,} "
          f"{record['limit_utilization_pct']:>11.2f}%")
```

## Web UI Usage

### Via MCP Server Web Interface

1. **Navigate to Tools Page:**
   - Go to `http://your-server:port/tools`
   - Find "limits_exposure_analysis"
   - Click "Execute"

2. **Full Analysis Example:**
   ```json
   {
     "counterparty_identifier": "Northbridge Capital"
   }
   ```

3. **Selective Sections Example:**
   ```json
   {
     "counterparty_identifier": "AC003",
     "include_sections": [
       "limit_status",
       "trade_summary",
       "asset_class_breakdown"
     ]
   }
   ```

## API Endpoint Usage

### REST API Call

```bash
curl -X POST http://your-server:port/api/tools/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "tool": "limits_exposure_analysis",
    "arguments": {
      "counterparty_identifier": "Northbridge Capital"
    }
  }'
```

### Python Requests

```python
import requests

url = "http://your-server:port/api/tools/execute"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_TOKEN"
}

payload = {
    "tool": "limits_exposure_analysis",
    "arguments": {
        "counterparty_identifier": "Aurora Metals",
        "include_sections": ["limit_status", "trade_summary"]
    }
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    result = response.json()
    summary = result['result']['summary']
    print(f"Status: {summary['limit_status']}")
    print(f"Utilization: {summary['limit_utilization_pct']}%")
```

## Output Format

### Structure

```json
{
  "counterparty_identifier": "string",
  "analysis_timestamp": "ISO-8601 timestamp",
  "sections": {
    "overview": {...},
    "limit_status": {...},
    "trade_summary": {...},
    ...
  },
  "summary": {
    "customer_name": "string",
    "rating": "string",
    "sector": "string",
    "limit_status": "BREACH|WARNING|OK",
    "limit_utilization_pct": number,
    "exposure_epe": number,
    "total_trades": number,
    "total_notional": number,
    "total_mtm": number,
    "total_pnl": number,
    "failed_trades_count": number
  }
}
```

### Example Output

```json
{
  "counterparty_identifier": "Northbridge Capital",
  "analysis_timestamp": "2025-10-27T22:06:49.287069",
  "summary": {
    "customer_name": "Northbridge Capital",
    "rating": "A-",
    "sector": "Financial Services",
    "limit_status": "BREACH",
    "limit_utilization_pct": 113.81,
    "exposure_epe": 13543220.92,
    "total_trades": 16,
    "total_notional": 172400755.39,
    "total_mtm": 2711178.10,
    "total_pnl": 271117.81,
    "failed_trades_count": 1
  },
  "sections": {
    "overview": {
      "customer_name": "Northbridge Capital",
      "adaptiv_code": "AC001",
      "sector": "Financial Services",
      "rating": "A-",
      "country": "Canada",
      "region": "North America",
      "portfolio": "FX-Derivs",
      "booking_location": "TOR",
      "risk_owner": "Desk A"
    },
    "limit_status": {
      "limit_ccr": 17000000,
      "exposure_epe": 13543220.92,
      "exposure_pfe": 19347458.46,
      "limit_utilization_pct": 113.81,
      "limit_status": "BREACH"
    }
  }
}
```

## Use Cases

### 1. Credit Risk Monitoring

Monitor all counterparties for limit breaches:

```python
# Daily breach check
for counterparty in get_all_counterparties():
    result = tool.execute({
        'counterparty_identifier': counterparty,
        'include_sections': ['limit_status']
    })
    
    if result['summary']['limit_status'] == 'BREACH':
        send_alert(result)
```

### 2. Pre-Trade Credit Check

Before executing a new trade:

```python
# Check current exposure
result = tool.execute({
    'counterparty_identifier': proposed_trade.counterparty,
    'include_sections': ['limit_status', 'trade_summary']
})

available_capacity = (
    result['sections']['limit_status']['limit_ccr'] -
    result['sections']['limit_status']['exposure_epe']
)

if proposed_trade.notional > available_capacity:
    reject_trade("Exceeds credit limit")
```

### 3. Risk Reporting

Generate daily risk report:

```python
# Generate comprehensive report
report = []
for cp in high_risk_counterparties:
    result = tool.execute({
        'counterparty_identifier': cp
    })
    report.append(result['summary'])

# Create executive summary
generate_pdf_report(report)
```

### 4. LLM-Based Risk Analysis

Feed data to LLM for natural language insights:

```python
# Get comprehensive data
result = tool.execute({
    'counterparty_identifier': 'Northbridge Capital'
})

# Send to LLM
prompt = f"""
Analyze the following counterparty risk profile and provide insights:

{json.dumps(result, indent=2)}

Provide:
1. Risk assessment summary
2. Key concerns
3. Recommendations
"""

llm_analysis = llm.generate(prompt)
```

## Best Practices

### 1. Use Selective Sections for Performance

```python
# Good: Request only what you need
result = tool.execute({
    'counterparty_identifier': 'AC001',
    'include_sections': ['limit_status', 'failed_trades']
})

# Avoid: Full analysis when not needed
# (unless you truly need all 16 sections)
```

### 2. Cache Results

```python
# Cache full analysis results
cache_key = f"limits_analysis_{counterparty}_{date}"
result = cache.get(cache_key)

if not result:
    result = tool.execute({
        'counterparty_identifier': counterparty
    })
    cache.set(cache_key, result, ttl=3600)
```

### 3. Handle Errors Gracefully

```python
try:
    result = tool.execute({
        'counterparty_identifier': 'Unknown CP'
    })
except Exception as e:
    logger.error(f"Analysis failed: {e}")
    # Fall back to basic query
    result = get_basic_counterparty_info('Unknown CP')
```

## Troubleshooting

### Issue: "Counterparty not found"

**Solutions:**
1. Verify the identifier spelling
2. Check if counterparty exists in ccr_limits table
3. Try alternate identifier (name vs code)

### Issue: "No trade data found"

**Cause:** Counterparty exists in limits but has no trades

**Solution:** This is expected for counterparties with no active positions

### Issue: "DuckDB tool not available"

**Solutions:**
1. Verify DuckDB tool is installed and configured
2. Check data files exist in `data/duckdb/`
3. Restart the server

## Performance Considerations

- **Full Analysis:** ~500ms for typical counterparty
- **Selective Sections:** ~100-200ms depending on sections
- **Concurrent Requests:** Tool is thread-safe
- **Caching:** Recommended for frequently accessed counterparties

## Dependencies

- DuckDB OLAP Tools
- Data files: `trades.parquet`, `ccr_limits.parquet`
- Python 3.8+

## Version History

- **v1.0.0** (2025-10-27): Initial release
  - 16 comprehensive analysis sections
  - Executive summary generation
  - Support for customer name and Adaptiv code
  - LLM-optimized output format

## Support

- **Tool Support:** ajsinha@gmail.com
- **Documentation:** See MCP Tools Documentation

## License

Copyright All rights Reserved 2025-2030, Ashutosh Sinha

---

**End of Documentation**

