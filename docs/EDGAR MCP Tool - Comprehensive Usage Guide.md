# EDGAR MCP Tool - Comprehensive Usage Guide

## Overview
The EDGAR MCP Tool provides comprehensive access to the SEC's EDGAR database, enabling retrieval and analysis of corporate filings, financial data, insider transactions, and regulatory documents.

## Key Features

### 1. Company Information
- **get_company_info**: Retrieve comprehensive company details including business addresses, SIC codes, fiscal year ends, and corporate structure
- **get_cik_lookup**: Convert between various identifiers (ticker, company name, CUSIP, LEI) and CIK
- **get_company_tickers**: Browse all available company tickers with filtering options

### 2. Filing Retrieval
- **get_company_filings**: Fetch company filings with date and type filtering
- **get_filing_documents**: Access detailed documents and exhibits from specific filings
- **get_recent_filings**: Monitor real-time filing submissions across all companies
- **search_filings**: Full-text search across EDGAR database

### 3. Financial Analysis
- **get_company_financials**: Extract structured financial statements from XBRL data
- **get_xbrl_facts**: Access detailed XBRL taxonomy facts and metrics
- **get_historical_data**: Retrieve historical trends for specific financial metrics
- **get_peer_comparison**: Compare company metrics with industry peers

### 4. Ownership & Trading
- **get_insider_transactions**: Track insider trading from Forms 3, 4, and 5
- **get_institutional_holdings**: Analyze institutional positions from 13F filings
- **get_beneficial_ownership**: Monitor major shareholders via Schedule 13D/G

### 5. Corporate Actions
- **get_proxy_statements**: Access proxy statements and executive compensation
- **get_merger_filings**: Track M&A activity and related filings
- **get_ipo_registrations**: Monitor IPO registration statements
- **get_comment_letters**: Review SEC correspondence

### 6. Fund Data
- **get_fund_data**: Retrieve mutual fund and ETF filings and holdings

### 7. Validation
- **validate_filing**: Validate EDGAR filing format and compliance

## Usage Examples

### Basic Company Lookup
```python
# Get company info by ticker
result = tool.handle_tool_call("get_company_info", {
    "ticker": "AAPL"
})

# Get company info by CIK
result = tool.handle_tool_call("get_company_info", {
    "cik": "0000320193"
})
```

### Retrieve Recent Filings
```python
# Get latest 10-K and 10-Q filings
result = tool.handle_tool_call("get_company_filings", {
    "ticker": "MSFT",
    "filing_type": "10-K",
    "limit": 5
})

# Get filings within date range
result = tool.handle_tool_call("get_company_filings", {
    "ticker": "GOOGL",
    "date_from": "2024-01-01",
    "date_to": "2024-12-31",
    "limit": 20
})
```

### Financial Analysis
```python
# Get income statement data
result = tool.handle_tool_call("get_company_financials", {
    "ticker": "TSLA",
    "statement_type": "income",
    "period": "quarterly",
    "fiscal_year": 2024
})

# Get historical revenue trend
result = tool.handle_tool_call("get_historical_data", {
    "ticker": "AMZN",
    "metric": "Revenues",
    "years": 10,
    "frequency": "annual"
})
```

### Insider Trading Analysis
```python
# Get recent insider transactions
result = tool.handle_tool_call("get_insider_transactions", {
    "ticker": "META",
    "transaction_type": "P",  # Purchases only
    "date_from": "2024-01-01",
    "limit": 50
})
```

### Institutional Holdings
```python
# Get 13F filings for an institution
result = tool.handle_tool_call("get_institutional_holdings", {
    "institution_name": "Berkshire Hathaway",
    "quarter": "2024Q3"
})
```

### M&A Activity
```python
# Track merger-related filings
result = tool.handle_tool_call("get_merger_filings", {
    "ticker": "TGT",
    "transaction_type": "merger",
    "date_from": "2023-01-01"
})
```

### Fund Analysis
```python
# Get fund data and holdings
result = tool.handle_tool_call("get_fund_data", {
    "ticker": "SPY",
    "include_holdings": True
})
```

### Peer Comparison
```python
# Compare with industry peers
result = tool.handle_tool_call("get_peer_comparison", {
    "ticker": "NVDA",
    "use_sic_peers": True,
    "metrics": ["Assets", "Revenues", "NetIncomeLoss", "ResearchAndDevelopmentExpense"]
})
```

## Configuration

### Environment Variables
```bash
# Required: Set your user agent with contact information
export SEC_USER_AGENT="YourCompany/1.0 (your-email@example.com)"
```

### Rate Limiting
The SEC enforces a rate limit of 10 requests per second. The tool automatically manages this through the `check_rate_limit()` method.

## Data Formats

### CIK (Central Index Key)
- 10-digit identifier for companies
- Can be provided with or without leading zeros
- Example: "0000320193" or "320193"

### Filing Types
Common filing types include:
- **10-K**: Annual report
- **10-Q**: Quarterly report
- **8-K**: Current report
- **DEF 14A**: Proxy statement
- **S-1**: IPO registration
- **4**: Insider trading
- **13F-HR**: Institutional holdings
- **SC 13D/G**: Beneficial ownership

### Date Formats
- Use ISO format: "YYYY-MM-DD"
- Example: "2024-03-15"

## Response Structure

All responses follow a consistent structure:
```json
{
    "status": 200,  // HTTP status code
    "data": {},     // Response data
    "error": null   // Error message if applicable
}
```

## Error Handling

The tool provides detailed error messages:
- Rate limit exceeded (429)
- Invalid parameters (400)
- Resource not found (404)
- Server errors (500)

## Best Practices

1. **Use CIK when possible**: CIK lookups are faster than ticker searches
2. **Cache frequently used data**: Store company info and ticker mappings
3. **Batch requests efficiently**: Group related queries to minimize API calls
4. **Respect rate limits**: Allow time between requests
5. **Filter at source**: Use date ranges and filing type filters to reduce data volume
6. **Parse incrementally**: For large datasets, process in chunks

## Advanced Features

### XBRL Processing
The tool can extract structured data from XBRL filings:
- Financial statements
- Company facts
- Custom metrics
- Multi-period comparisons

### Real-time Monitoring
Monitor filings as they're submitted:
- Set up polling for recent filings
- Track specific companies or filing types
- Alert on material events (8-K)

### Compliance Validation
Validate filing formats before submission:
- Check required tags and structure
- Verify XBRL compliance
- Ensure proper formatting

## Limitations

1. **Full-text search**: Requires special EDGAR access credentials
2. **Real-time feeds**: RSS/websocket feeds need additional integration
3. **Historical data**: Some older filings may not have structured data
4. **Document parsing**: Full document text extraction requires additional processing

## Support & Resources

- [SEC EDGAR Homepage](https://www.sec.gov/edgar)
- [EDGAR API Documentation](https://www.sec.gov/edgar/sec-api-documentation)
- [Company Search](https://www.sec.gov/edgar/searchedgar/companysearch)
- [Filing Types Reference](https://www.sec.gov/info/edgar/forms/edgform.pdf)