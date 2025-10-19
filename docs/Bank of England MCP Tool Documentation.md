# Bank of England MCP Tool Documentation

## Overview
The Bank of England MCP Tool provides comprehensive access to UK economic data, monetary policy information, financial statistics, and market indicators from the Bank of England's Statistical Interactive Database.

## Configuration
- **Base URL**: Bank of England Interactive Database API
- No API key required
- Automatic CSV parsing and data formatting

## Available Methods

### Monetary Policy & Interest Rates

#### 1. get_bank_rate
Retrieves Bank of England Bank Rate (policy rate).

**Parameters:**
- `datefrom` (optional): Start date
- `dateto` (optional): End date
- `recent` (optional): Number of recent observations

**Returns:**
- Current and historical bank rate
- Date of changes
- Rate trends

#### 2. get_sonia
Gets Sterling Overnight Index Average (SONIA).

**Parameters:**
- Standard date parameters

**Returns:**
- Daily SONIA rates
- Volume-weighted average

#### 3. get_term_sonia
Gets Term SONIA reference rates.

**Parameters:**
- `term` (default: '3M'): '1M', '3M', '6M', or '12M'
- Standard date parameters

#### 4. get_swap_rates
Gets interest rate swap rates.

**Parameters:**
- `maturity` (default: '5Y'): '1Y', '2Y', '3Y', '5Y', '7Y', '10Y'

#### 5. get_overnight_index_swaps
Gets Overnight Index Swap rates.

#### 6. get_forward_rates
Gets forward interest rates.

**Parameters:**
- `horizon` (default: '1Y'): '1Y', '2Y', '5Y'

#### 7. get_real_interest_rates
Gets real (inflation-adjusted) interest rates.

### Economic Indicators

#### 8. get_inflation_data
Gets UK inflation data.

**Parameters:**
- `measure` (default: 'cpi'): 'cpi', 'cpih', 'rpi', 'core_cpi'

#### 9. get_cpi_data
Gets Consumer Price Index data.

#### 10. get_rpi_data
Gets Retail Price Index data.

#### 11. get_gdp_data
Gets UK GDP data.

**Parameters:**
- `gdp_type` (default: 'growth'): 'growth', 'level', 'per_capita'

#### 12. get_unemployment
Gets UK unemployment rate.

#### 13. get_wage_growth
Gets wage growth data.

**Parameters:**
- `measure` (default: 'average_weekly'): 'average_weekly', 'regular_pay', 'total_pay'

#### 14. get_productivity
Gets productivity data.

#### 15. get_retail_sales
Gets retail sales data.

### Exchange Rates

#### 16. get_sterling_exchange_rates
Gets Sterling exchange rates.

**Parameters:**
- `currency` (default: 'USD'): 'USD', 'EUR', 'JPY', 'CHF', 'CAD', 'AUD', 'CNY'

#### 17. get_effective_exchange_rates
Gets Sterling effective exchange rates.

**Parameters:**
- `eer_type` (default: 'nominal'): 'nominal' or 'real'

#### 18. get_forward_exchange_rates
Gets forward exchange rates.

**Parameters:**
- `currency` (default: 'USD')
- `tenor` (default: '1M'): Forward period

#### 19. get_currency_volatility
Gets currency volatility measures.

**Parameters:**
- `currency` (default: 'USD')

### Government Securities & Gilts

#### 20. get_gilt_yields
Gets UK government bond (gilt) yields.

**Parameters:**
- `maturity` (default: '10Y'): '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y'

#### 21. get_gilt_prices
Gets gilt prices.

#### 22. get_index_linked_gilts
Gets index-linked gilt yields.

**Parameters:**
- `maturity` (default: '10Y'): '5Y', '10Y', '20Y'

#### 23. get_gilt_issuance
Gets gilt issuance data.

#### 24. get_yield_curve
Gets complete UK yield curve.

**Returns:**
- Yields from 1Y to 30Y
- Yield curve spreads (10Y2Y, 10Y1Y)
- Curve shape analysis

#### 25. get_treasury_bills
Gets Treasury Bill rates.

### Banking & Financial System

#### 26. get_bank_lending
Gets bank lending data.

#### 27. get_mortgage_lending
Gets mortgage lending data.

#### 28. get_consumer_credit
Gets consumer credit data.

#### 29. get_deposit_rates
Gets deposit interest rates.

**Parameters:**
- `deposit_type` (default: 'household'): 'household', 'corporate', 'instant_access', 'fixed_rate'

#### 30. get_lending_rates
Gets lending interest rates.

**Parameters:**
- `loan_type` (default: 'mortgage'): 'mortgage', 'personal_loan', 'credit_card', 'overdraft'

#### 31. get_bank_capital_ratios
Gets bank capital ratios.

**Parameters:**
- `ratio_type` (default: 'tier1'): 'tier1', 'cet1', 'total_capital'

#### 32. get_bank_stress_tests
Gets bank stress test results information.

### Money Supply & Credit

#### 33. get_money_supply
Gets money supply data.

**Parameters:**
- `aggregate` (default: 'M4'): 'M0', 'M4', 'M4_lending'

#### 34. get_broad_money
Gets broad money (M4) growth.

#### 35. get_credit_growth
Gets credit growth to private sector.

#### 36. get_sectoral_lending
Gets lending by sector.

**Parameters:**
- `sector` (default: 'household'): 'household', 'pnfc', 'financial', 'real_estate'

#### 37. get_lending_to_smes
Gets lending to small and medium enterprises.

### Financial Markets

#### 38. get_ftse_indices
Gets FTSE index data.

**Parameters:**
- `index` (default: 'ftse100'): 'ftse100', 'ftse250', 'ftse_all_share'

#### 39. get_equity_prices
Gets equity price indices.

#### 40. get_corporate_bond_spreads
Gets corporate bond spreads.

**Parameters:**
- `rating` (default: 'investment_grade'): 'investment_grade', 'high_yield', 'aaa'

#### 41. get_sterling_money_markets
Gets sterling money market data.

### Housing Market

#### 42. get_house_prices
Gets UK house price indices.

**Parameters:**
- `index_type` (default: 'nationwide'): 'nationwide', 'halifax', 'land_registry'

#### 43. get_mortgage_approvals
Gets mortgage approval numbers.

#### 44. get_mortgage_rates
Gets mortgage interest rates.

**Parameters:**
- `mortgage_type` (default: 'variable'): 'variable', 'fixed_2y', 'fixed_3y', 'fixed_5y'

#### 45. get_buy_to_let
Gets buy-to-let mortgage data.

#### 46. get_housing_transactions
Gets housing transaction volumes.

### External Sector

#### 47. get_current_account
Gets current account balance.

#### 48. get_trade_balance
Gets trade balance.

#### 49. get_exports
Gets export data.

#### 50. get_imports
Gets import data.

#### 51. get_foreign_investment
Gets foreign direct investment data.

#### 52. get_uk_investment_abroad
Gets UK investment abroad data.

### Regional Data

#### 53. get_regional_gdp
Gets regional GDP data.

**Parameters:**
- `region` (default: 'london')

#### 54. get_regional_unemployment
Gets regional unemployment rates.

**Parameters:**
- `region`: Region name (london, southeast, southwest, etc.)

#### 55. get_regional_house_prices
Gets regional house price data.

**Parameters:**
- `region`: Region name

### Business Conditions

#### 56. get_agents_scores
Gets Bank of England Agents' summary scores.

**Parameters:**
- `indicator` (default: 'demand'): Economic indicator

#### 57. get_business_investment
Gets business investment data.

#### 58. get_corporate_profitability
Gets corporate profitability indicators.

#### 59. get_company_liquidations
Gets company liquidation statistics.

### Financial Stability

#### 60. get_systemic_risk_survey
Gets Systemic Risk Survey results information.

#### 61. get_financial_stability_indicators
Gets financial stability indicators.

#### 62. get_countercyclical_buffer
Gets countercyclical capital buffer rate.

#### 63. get_leverage_ratio
Gets leverage ratio requirements.

#### 64. get_liquidity_coverage
Gets liquidity coverage ratio data.

### Surveys & Expectations

#### 65. get_inflation_expectations
Gets inflation expectations from various sources.

**Parameters:**
- `source` (default: 'market'): 'market', 'survey', 'professional'

#### 66. get_inflation_attitudes_survey
Gets Inflation Attitudes Survey results.

#### 67. get_credit_conditions_survey
Gets Credit Conditions Survey results.

#### 68. get_bank_liabilities_survey
Gets Bank Liabilities Survey results.

#### 69. get_mpc_minutes
Gets Monetary Policy Committee meeting information.

### Quantitative Easing & Balance Sheet

#### 70. get_asset_purchase_facility
Gets Asset Purchase Facility data.

#### 71. get_qe_holdings
Gets quantitative easing holdings.

**Parameters:**
- `asset_type` (default: 'gilts'): 'gilts' or 'corporate_bonds'

#### 72. get_bank_reserves
Gets bank reserves at Bank of England.

#### 73. get_balance_sheet
Gets Bank of England balance sheet.

**Parameters:**
- `item` (default: 'total_assets'): 'total_assets', 'liabilities', 'notes_in_circulation', 'reserve_balances'

#### 74. get_term_funding_scheme
Gets Term Funding Scheme data.

### Historical Data

#### 75. get_historical_bank_rate
Gets historical Bank Rate from 1694.

**Parameters:**
- `datefrom` (default: '1694-01-01'): Start date

#### 76. get_historical_exchange_rates
Gets historical exchange rates.

**Parameters:**
- `datefrom` (default: '1975-01-01'): Start date

#### 77. get_historical_inflation
Gets historical inflation data.

**Parameters:**
- `datefrom` (default: '1988-01-01'): Start date

#### 78. get_long_run_data
Gets long-run economic data (centuries).

**Parameters:**
- `dataset` (default: 'interest_rates'): 'interest_rates', 'prices', 'gdp', 'money_supply'
- `datefrom` (default: '1694-01-01'): Start date

### Payment Systems

#### 79. get_chaps_volumes
Gets CHAPS payment system volumes.

#### 80. get_faster_payments
Gets Faster Payments Service statistics.

#### 81. get_rtgs_statistics
Gets RTGS (Real-Time Gross Settlement) statistics.

#### 82. get_payment_statistics
Gets payment system statistics.

**Parameters:**
- `system` (default: 'all'): 'all', 'chaps', 'faster_payments', 'rtgs'

### Brexit & EU

#### 83. get_brexit_uncertainty_index
Gets Brexit uncertainty index information.

#### 84. get_eu_trade_statistics
Gets EU trade statistics.

#### 85. get_financial_services_trade
Gets financial services trade statistics.

### Climate & ESG

#### 86. get_climate_risk_indicators
Gets climate-related financial risk indicators.

#### 87. get_green_bonds
Gets green bond issuance and holdings.

#### 88. get_transition_indicators
Gets climate transition risk indicators.

### Search & Metadata

#### 89. search_series
Searches for Bank of England data series.

**Parameters:**
- `search_term`: Search query

#### 90. get_series_metadata
Gets metadata for specific series.

**Parameters:**
- `series_code`: Series identifier

#### 91. get_data_availability
Gets information about data availability.

## Series Code Examples

Common series codes:
- IUDBEDR: Bank Rate
- IUDSOIA: SONIA
- XUDLUSS: GBP/USD exchange rate
- D7BT: CPI inflation
- IHYQ: GDP growth
- MGSX: Unemployment rate

## Example Usage
```python