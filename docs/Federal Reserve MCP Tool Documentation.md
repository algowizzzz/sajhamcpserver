# Federal Reserve MCP Tool Documentation

## Overview
The Federal Reserve MCP Tool provides comprehensive access to US economic data, monetary policy information, and financial statistics through the FRED (Federal Reserve Economic Data) API.

## Configuration
- **Environment Variables:**
  - `FRED_API_KEY`: Required API key from FRED
- **Base URL**: FRED API (api.stlouisfed.org)

## Available Methods

### Interest Rates & Monetary Policy

#### 1. get_interest_rates
Gets comprehensive Federal interest rates.

**Parameters:**
- `rate_type` (default: 'federal_funds'): 
  - 'federal_funds': Federal funds rate
  - 'federal_funds_target': Target rate
  - 'effective_federal_funds': EFFR
  - 'prime': Prime rate
  - 'sofr': SOFR
  - 'obfr': OBFR
  - 'iorb': Interest on reserve balances

#### 2. get_real_interest_rates
Gets real (inflation-adjusted) interest rates.

**Parameters:**
- `rate_type` (default: '10Y'): '5Y', '10Y', 'federal_funds'

#### 3. get_term_spreads
Gets term spreads (yield curve indicators).

**Parameters:**
- `spread_type` (default: '10Y2Y'): '10Y2Y', '10Y3M', '5Y2Y', '30Y5Y'

#### 4. get_fomc_projections
Gets FOMC economic projections.

**Parameters:**
- `projection_type` (default: 'federal_funds')

#### 5. get_fomc_statements
Gets FOMC statements and minutes information.

#### 6. get_policy_tools
Gets Fed policy tools data.

**Parameters:**
- `tool_type` (default: 'balance_sheet'): 'balance_sheet', 'reserve_balances', 'securities_held'

#### 7. get_reverse_repo
Gets reverse repo operations data.

**Parameters:**
- `data_type` (default: 'volume'): 'volume', 'rate', 'counterparties'

#### 8. get_standing_repo
Gets standing repo facility data.

### Economic Indicators

#### 9. get_economic_series
Gets any economic series data.

**Parameters:**
- `series_id` (required): FRED series identifier

#### 10. get_gdp_data
Gets GDP data.

**Parameters:**
- `gdp_type` (default: 'real'): 'real' or 'nominal'

#### 11. get_gdp_components
Gets GDP components breakdown.

**Parameters:**
- `component_type` (default: 'all'): 'all', 'consumption', 'investment', 'government', 'net_exports'

#### 12. get_inflation_data
Gets inflation data.

**Parameters:**
- `inflation_type` (default: 'cpi'): 'cpi', 'cpi_yoy', 'pce', 'core_cpi', 'core_pce'

#### 13. get_inflation_expectations
Gets inflation expectations.

**Parameters:**
- `horizon` (default: '5Y'): '1Y', '5Y', '10Y', 'michigan_1Y', 'michigan_5Y'

#### 14. get_pce_components
Gets PCE inflation components.

**Parameters:**
- `component` (default: 'core'): 'headline', 'core', 'goods', 'services', 'energy', 'food'

### Labor Market

#### 15. get_unemployment_data
Gets unemployment data.

#### 16. get_employment_data
Gets employment data by sector.

**Parameters:**
- `employment_type` (default: 'nonfarm'): Multiple sector options

#### 17. get_labor_force_participation
Gets labor force participation rates.

**Parameters:**
- `demographic` (default: 'total'): 'total', 'prime_age', 'women', 'men', 'teens', 'over_55'

#### 18. get_job_openings
Gets JOLTS job openings data.

**Parameters:**
- `data_type` (default: 'openings'): 'openings', 'hires', 'quits', 'layoffs'

#### 19. get_wage_growth
Gets wage growth data.

**Parameters:**
- `wage_type` (default: 'average_hourly'): Multiple wage measures

#### 20. get_initial_claims
Gets unemployment claims data.

**Parameters:**
- `claims_type` (default: 'initial'): 'initial', 'continuing', '4week_average'

#### 21. get_productivity_data
Gets labor productivity data.

**Parameters:**
- `measure` (default: 'productivity'): 'productivity', 'unit_labor_costs'

### Financial Markets

#### 22. get_treasury_yields
Gets Treasury yields.

**Parameters:**
- `maturity` (default: '10Y'): '3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y'

#### 23. get_yield_curve
Gets complete yield curve.

**Returns:**
- All maturities from 1M to 30Y
- Key spreads
- Inversion status

#### 24. get_tips_spreads
Gets TIPS breakeven inflation rates.

**Parameters:**
- `maturity` (default: '10Y'): '5Y', '10Y', '30Y'

#### 25. get_co