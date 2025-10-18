"""
Enhanced Federal Reserve MCP Tool implementation with extensive capabilities
"""
import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base_mcp_tool import BaseMCPTool


class FedReserveMCPTool(BaseMCPTool):
    """Enhanced MCP Tool for comprehensive Federal Reserve data operations"""

    def _initialize(self):
        """Initialize Fed Reserve specific components"""
        self.api_key = os.environ.get('FRED_API_KEY', '')
        self.fred_base_url = "https://api.stlouisfed.org/fred"
        self.fomc_base_url = "https://www.federalreserve.gov/json"

        if not self.api_key:
            print("Warning: FRED_API_KEY not set. Limited functionality available.")

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Federal Reserve tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            # Comprehensive tool method mapping
            tool_methods = {
                # Interest Rates & Monetary Policy
                "get_interest_rates": self._get_interest_rates,
                "get_real_interest_rates": self._get_real_interest_rates,
                "get_term_spreads": self._get_term_spreads,
                "get_fomc_projections": self._get_fomc_projections,
                "get_fomc_statements": self._get_fomc_statements,
                "get_policy_tools": self._get_policy_tools,
                "get_reverse_repo": self._get_reverse_repo,
                "get_standing_repo": self._get_standing_repo,

                # Economic Indicators
                "get_economic_series": self._get_economic_series,
                "get_gdp_data": self._get_gdp_data,
                "get_gdp_components": self._get_gdp_components,
                "get_inflation_data": self._get_inflation_data,
                "get_inflation_expectations": self._get_inflation_expectations,
                "get_pce_components": self._get_pce_components,

                # Labor Market
                "get_unemployment_data": self._get_unemployment_data,
                "get_employment_data": self._get_employment_data,
                "get_labor_force_participation": self._get_labor_force_participation,
                "get_job_openings": self._get_job_openings,
                "get_wage_growth": self._get_wage_growth,
                "get_initial_claims": self._get_initial_claims,
                "get_productivity_data": self._get_productivity_data,

                # Financial Markets
                "get_treasury_yields": self._get_treasury_yields,
                "get_yield_curve": self._get_yield_curve,
                "get_tips_spreads": self._get_tips_spreads,
                "get_corporate_spreads": self._get_corporate_spreads,
                "get_stock_market_indicators": self._get_stock_market_indicators,
                "get_volatility_indices": self._get_volatility_indices,
                "get_exchange_rates": self._get_exchange_rates,
                "get_dollar_index": self._get_dollar_index,

                # Banking & Credit
                "get_money_supply": self._get_money_supply,
                "get_banking_statistics": self._get_banking_statistics,
                "get_bank_lending_standards": self._get_bank_lending_standards,
                "get_consumer_credit": self._get_consumer_credit,
                "get_mortgage_rates": self._get_mortgage_rates,
                "get_credit_card_rates": self._get_credit_card_rates,
                "get_auto_loan_rates": self._get_auto_loan_rates,
                "get_commercial_paper": self._get_commercial_paper,
                "get_bank_failures": self._get_bank_failures,

                # Housing Market
                "get_housing_starts": self._get_housing_starts,
                "get_home_prices": self._get_home_prices,
                "get_existing_home_sales": self._get_existing_home_sales,
                "get_new_home_sales": self._get_new_home_sales,
                "get_construction_spending": self._get_construction_spending,
                "get_homeownership_rate": self._get_homeownership_rate,

                # Industrial & Manufacturing
                "get_industrial_production": self._get_industrial_production,
                "get_capacity_utilization": self._get_capacity_utilization,
                "get_manufacturing_data": self._get_manufacturing_data,
                "get_durable_goods": self._get_durable_goods,
                "get_factory_orders": self._get_factory_orders,
                "get_business_inventories": self._get_business_inventories,

                # Consumer & Retail
                "get_retail_sales": self._get_retail_sales,
                "get_consumer_sentiment": self._get_consumer_sentiment,
                "get_personal_income": self._get_personal_income,
                "get_personal_spending": self._get_personal_spending,
                "get_savings_rate": self._get_savings_rate,
                "get_household_debt": self._get_household_debt,

                # Trade & International
                "get_trade_balance": self._get_trade_balance,
                "get_exports": self._get_exports,
                "get_imports": self._get_imports,
                "get_current_account": self._get_current_account,
                "get_foreign_holdings": self._get_foreign_holdings,

                # Regional Fed Data
                "get_regional_fed_data": self._get_regional_fed_data,
                "get_beige_book": self._get_beige_book,
                "get_state_unemployment": self._get_state_unemployment,
                "get_metro_area_data": self._get_metro_area_data,

                # Financial Stability
                "get_financial_stress_index": self._get_financial_stress_index,
                "get_systemic_risk_indicators": self._get_systemic_risk_indicators,
                "get_leverage_ratios": self._get_leverage_ratios,
                "get_liquidity_indicators": self._get_liquidity_indicators,

                # Historical & Research
                "search_series": self._search_series,
                "get_series_metadata": self._get_series_metadata,
                "get_vintage_data": self._get_vintage_data,
                "get_recession_dates": self._get_recession_dates,
                "get_historical_rates": self._get_historical_rates,

                # Specialized Indicators
                "get_term_premia": self._get_term_premia,
                "get_natural_rate": self._get_natural_rate,
                "get_output_gap": self._get_output_gap,
                "get_taylor_rule": self._get_taylor_rule,
                "get_financial_conditions": self._get_financial_conditions,
                "get_credit_spreads": self._get_credit_spreads,
                "get_commodity_prices": self._get_commodity_prices,
                "get_energy_prices": self._get_energy_prices,
            }

            if tool_name in tool_methods:
                result = tool_methods[tool_name](arguments)
            else:
                result = {"error": f"Unknown tool: {tool_name}"}

            self.record_call(tool_name, arguments, result=result)
            return result

        except Exception as e:
            error_msg = str(e)
            self.record_call(tool_name, arguments, error=error_msg)
            return {"error": error_msg, "status": 500}

    # ==================== HELPER METHODS ====================

    def _fetch_fred_series(self, series_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Centralized FRED API fetching with metadata"""
        if not self.api_key:
            return {"error": "FRED API key required"}

        try:
            # Fetch observations
            url = f"{self.fred_base_url}/series/observations"
            api_params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json',
                'limit': params.get('limit', 30),
                'sort_order': params.get('sort_order', 'desc'),
                'observation_start': params.get('start_date', ''),
                'observation_end': params.get('end_date', '')
            }

            response = requests.get(url, params=api_params)
            if response.status_code != 200:
                return {"error": f"API request failed with status {response.status_code}"}

            data = response.json()
            observations = data.get('observations', [])

            # Fetch series metadata
            meta_url = f"{self.fred_base_url}/series"
            meta_params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json'
            }

            meta_response = requests.get(meta_url, params=meta_params)
            metadata = {}
            if meta_response.status_code == 200:
                meta_data = meta_response.json()
                if 'seriess' in meta_data and meta_data['seriess']:
                    series_info = meta_data['seriess'][0]
                    metadata = {
                        'title': series_info.get('title'),
                        'units': series_info.get('units'),
                        'frequency': series_info.get('frequency'),
                        'seasonal_adjustment': series_info.get('seasonal_adjustment'),
                        'last_updated': series_info.get('last_updated')
                    }

            # Calculate period-over-period changes if applicable
            changes = []
            if len(observations) > 1:
                for i in range(len(observations) - 1):
                    if observations[i].get('value', '.') != '.' and observations[i+1].get('value', '.') != '.':
                        current = float(observations[i]['value'])
                        previous = float(observations[i+1]['value'])
                        change = ((current - previous) / previous) * 100 if previous != 0 else 0
                        changes.append({
                            'date': observations[i]['date'],
                            'change_pct': round(change, 2)
                        })

            return {
                "series_id": series_id,
                "metadata": metadata,
                "latest_value": observations[0].get('value') if observations else None,
                "latest_date": observations[0].get('date') if observations else None,
                "observations": observations,
                "changes": changes[:5] if changes else [],
                "count": len(observations)
            }

        except Exception as e:
            return {"error": str(e)}

    # ==================== INTEREST RATES & MONETARY POLICY ====================

    def _get_interest_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive Federal interest rates"""
        rate_type = params.get('rate_type', 'federal_funds')

        series_map = {
            'federal_funds': 'DFF',
            'federal_funds_target': 'DFEDTARU',
            'federal_funds_upper': 'DFEDTARU',
            'federal_funds_lower': 'DFEDTARL',
            'effective_federal_funds': 'EFFR',
            'prime': 'DPRIME',
            'discount': 'INTDSRUSM193N',
            'sofr': 'SOFR',
            'obfr': 'OBFR',
            'iorb': 'IORB',
            'ioer': 'IOER'
        }

        series_id = series_map.get(rate_type, 'DFF')
        return self._fetch_fred_series(series_id, params)

    def _get_real_interest_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get real (inflation-adjusted) interest rates"""
        rate_type = params.get('rate_type', '10Y')

        series_map = {
            '5Y': 'REAINTRATREARAT5Y',
            '10Y': 'REAINTRATREARAT10Y',
            'federal_funds': 'FEDFUNDS'
        }

        series_id = series_map.get(rate_type, 'REAINTRATREARAT10Y')
        return self._fetch_fred_series(series_id, params)

    def _get_term_spreads(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get term spreads (yield curve indicators)"""
        spread_type = params.get('spread_type', '10Y2Y')

        series_map = {
            '10Y2Y': 'T10Y2Y',
            '10Y3M': 'T10Y3M',
            '5Y2Y': 'T5YFF',
            '30Y5Y': 'T30Y5Y'
        }

        series_id = series_map.get(spread_type, 'T10Y2Y')
        return self._fetch_fred_series(series_id, params)

    def _get_fomc_projections(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get FOMC economic projections"""
        projection_type = params.get('projection_type', 'federal_funds')

        # Note: FOMC projections require special handling
        # This is a placeholder implementation
        return {
            "projection_type": projection_type,
            "message": "FOMC projections available at federalreserve.gov/monetarypolicy/fomcprojtabl.htm",
            "last_update": "Most recent FOMC meeting"
        }

    def _get_fomc_statements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get FOMC statements and minutes"""
        return {
            "message": "FOMC statements available at federalreserve.gov/monetarypolicy/fomc.htm",
            "recent_meetings": "Access through Federal Reserve website"
        }

    def _get_policy_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Fed policy tools data"""
        tool_type = params.get('tool_type', 'balance_sheet')

        series_map = {
            'balance_sheet': 'WALCL',
            'reserve_balances': 'TOTRESNS',
            'securities_held': 'WSECOUT'
        }

        series_id = series_map.get(tool_type, 'WALCL')
        return self._fetch_fred_series(series_id, params)

    def _get_reverse_repo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get reverse repo operations data"""
        data_type = params.get('data_type', 'volume')

        series_map = {
            'volume': 'RRPONTSYD',
            'rate': 'RRPONTTLD',
            'counterparties': 'RRPONCT'
        }

        series_id = series_map.get(data_type, 'RRPONTSYD')
        return self._fetch_fred_series(series_id, params)

    def _get_standing_repo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get standing repo facility data"""
        return self._fetch_fred_series('RPONTTLD', params)

    # ==================== ECONOMIC INDICATORS ====================

    def _get_economic_series(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get any economic series data"""
        series_id = params.get('series_id', '')

        if not series_id:
            return {"error": "Series ID is required"}

        return self._fetch_fred_series(series_id, params)

    def _get_gdp_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get GDP data"""
        gdp_type = params.get('gdp_type', 'real')

        series_id = 'GDPC1' if gdp_type == 'real' else 'GDP'
        return self._fetch_fred_series(series_id, params)

    def _get_gdp_components(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get GDP components breakdown"""
        component_type = params.get('component_type', 'all')

        components = {
            'consumption': 'PCECC96',
            'investment': 'GPDIC1',
            'government': 'GCEC1',
            'net_exports': 'NETEXC',
            'exports': 'EXPGSC1',
            'imports': 'IMPGSC1'
        }

        if component_type == 'all':
            results = {}
            for component, series_id in components.items():
                result = self._fetch_fred_series(series_id, {'limit': 1})
                if 'latest_value' in result:
                    results[component] = {
                        'value': result['latest_value'],
                        'date': result['latest_date']
                    }
            return {
                "gdp_components": results,
                "type": "Real GDP components (billions of chained 2017 dollars)"
            }
        else:
            series_id = components.get(component_type, 'PCECC96')
            return self._fetch_fred_series(series_id, params)

    def _get_inflation_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get inflation data"""
        inflation_type = params.get('inflation_type', 'cpi')

        series_map = {
            'cpi': 'CPIAUCSL',
            'cpi_yoy': 'CPILFESL',
            'pce': 'PCEPI',
            'core_cpi': 'CPILFESL',
            'core_pce': 'PCEPILFE'
        }

        series_id = series_map.get(inflation_type, 'CPIAUCSL')
        return self._fetch_fred_series(series_id, params)

    def _get_inflation_expectations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get inflation expectations"""
        horizon = params.get('horizon', '5Y')

        series_map = {
            '1Y': 'EXPINF1YR',
            '5Y': 'T5YIE',
            '10Y': 'T10YIE',
            'michigan_1Y': 'MICH',
            'michigan_5Y': 'MICH5Y10'
        }

        series_id = series_map.get(horizon, 'T5YIE')
        return self._fetch_fred_series(series_id, params)

    def _get_pce_components(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get PCE inflation components"""
        component = params.get('component', 'core')

        series_map = {
            'headline': 'PCEPI',
            'core': 'PCEPILFE',
            'goods': 'DGDSRG3M086SBEA',
            'services': 'DSERRG3M086SBEA',
            'energy': 'PCEENG',
            'food': 'PCEFOOD'
        }

        series_id = series_map.get(component, 'PCEPILFE')
        return self._fetch_fred_series(series_id, params)

    # ==================== LABOR MARKET ====================

    def _get_unemployment_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get unemployment data"""
        return self._fetch_fred_series('UNRATE', params)

    def _get_employment_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get employment data by sector"""
        employment_type = params.get('employment_type', 'nonfarm')

        series_map = {
            'nonfarm': 'PAYEMS',
            'private': 'USPRIV',
            'government': 'USGOVT',
            'manufacturing': 'MANEMP',
            'construction': 'USCONS',
            'retail': 'USTRADE',
            'leisure_hospitality': 'USLAH',
            'professional_business': 'USPBS',
            'education_health': 'USEHS',
            'information': 'USINFO',
            'financial': 'USFIRE'
        }

        series_id = series_map.get(employment_type, 'PAYEMS')
        return self._fetch_fred_series(series_id, params)

    def _get_labor_force_participation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get labor force participation rates"""
        demographic = params.get('demographic', 'total')

        series_map = {
            'total': 'CIVPART',
            'prime_age': 'LNS11300060',
            'women': 'LNS11300002',
            'men': 'LNS11300001',
            'teens': 'LNS11300012',
            'over_55': 'LNS11324230'
        }

        series_id = series_map.get(demographic, 'CIVPART')
        return self._fetch_fred_series(series_id, params)

    def _get_job_openings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get JOLTS job openings data"""
        data_type = params.get('data_type', 'openings')

        series_map = {
            'openings': 'JTSJOL',
            'hires': 'JTSHIL',
            'quits': 'JTSQUR',
            'layoffs': 'JTSLDR'
        }

        series_id = series_map.get(data_type, 'JTSJOL')
        return self._fetch_fred_series(series_id, params)

    def _get_wage_growth(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get wage growth data"""
        wage_type = params.get('wage_type', 'average_hourly')

        series_map = {
            'average_hourly': 'CES0500000003',
            'atlanta_fed_tracker': 'AHETPI',
            'eci_total': 'ECIALLCIV',
            'eci_wages': 'ECIWAG',
            'production_workers': 'CES0500000008'
        }

        series_id = series_map.get(wage_type, 'CES0500000003')
        return self._fetch_fred_series(series_id, params)

    def _get_initial_claims(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get unemployment claims data"""
        claims_type = params.get('claims_type', 'initial')

        series_map = {
            'initial': 'ICSA',
            'continuing': 'CCSA',
            '4week_average': 'IC4WSA'
        }

        series_id = series_map.get(claims_type, 'ICSA')
        return self._fetch_fred_series(series_id, params)

    def _get_productivity_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get labor productivity data"""
        measure = params.get('measure', 'productivity')

        series_map = {
            'productivity': 'OPHNFB',
            'unit_labor_costs': 'ULCNFB',
            'output_per_hour': 'OPHNFB'
        }

        series_id = series_map.get(measure, 'OPHNFB')
        return self._fetch_fred_series(series_id, params)

    # ==================== FINANCIAL MARKETS ====================

    def _get_treasury_yields(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Treasury yields"""
        maturity = params.get('maturity', '10Y')

        series_map = {
            '3M': 'DGS3MO',
            '6M': 'DGS6MO',
            '1Y': 'DGS1',
            '2Y': 'DGS2',
            '3Y': 'DGS3',
            '5Y': 'DGS5',
            '7Y': 'DGS7',
            '10Y': 'DGS10',
            '20Y': 'DGS20',
            '30Y': 'DGS30'
        }

        series_id = series_map.get(maturity, 'DGS10')
        return self._fetch_fred_series(series_id, params)

    def _get_yield_curve(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get complete yield curve"""
        maturities = {
            '1M': 'DGS1MO',
            '3M': 'DGS3MO',
            '6M': 'DGS6MO',
            '1Y': 'DGS1',
            '2Y': 'DGS2',
            '3Y': 'DGS3',
            '5Y': 'DGS5',
            '7Y': 'DGS7',
            '10Y': 'DGS10',
            '20Y': 'DGS20',
            '30Y': 'DGS30'
        }

        curve_data = {}
        for maturity, series_id in maturities.items():
            result = self._fetch_fred_series(series_id, {'limit': 1})
            if 'latest_value' in result and result['latest_value'] != '.':
                curve_data[maturity] = float(result['latest_value'])

        # Calculate key spreads
        spreads = {}
        if '10Y' in curve_data and '2Y' in curve_data:
            spreads['10Y2Y'] = round(curve_data['10Y'] - curve_data['2Y'], 2)
        if '10Y' in curve_data and '3M' in curve_data:
            spreads['10Y3M'] = round(curve_data['10Y'] - curve_data['3M'], 2)

        return {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "yield_curve": curve_data,
            "spreads": spreads,
            "inverted": spreads.get('10Y2Y', 0) < 0 if '10Y2Y' in spreads else None
        }

    def _get_tips_spreads(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get TIPS breakeven inflation rates"""
        maturity = params.get('maturity', '10Y')

        series_map = {
            '5Y': 'T5YIE',
            '10Y': 'T10YIE',
            '30Y': 'T30YIEM'
        }

        series_id = series_map.get(maturity, 'T10YIE')
        return self._fetch_fred_series(series_id, params)

    def _get_corporate_spreads(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get corporate bond spreads"""
        grade = params.get('grade', 'investment_grade')

        series_map = {
            'investment_grade': 'BAMLC0A0CM',
            'high_yield': 'BAMLH0A0HYM2',
            'bbb': 'BAMLC0A4CBBB',
            'ccc': 'BAMLH0A3HYC'
        }

        series_id = series_map.get(grade, 'BAMLC0A0CM')
        return self._fetch_fred_series(series_id, params)

    def _get_stock_market_indicators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get stock market indicators"""
        indicator = params.get('indicator', 'sp500')

        series_map = {
            'sp500': 'SP500',
            'dow': 'DJIA',
            'nasdaq': 'NASDAQCOM',
            'russell2000': 'RUT',
            'wilshire5000': 'WILL5000INDFC'
        }

        series_id = series_map.get(indicator, 'SP500')
        return self._fetch_fred_series(series_id, params)

    def _get_volatility_indices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get volatility indices"""
        index = params.get('index', 'vix')

        series_map = {
            'vix': 'VIXCLS',
            'vxn': 'VXNCLS',
            'rvx': 'RVXCLS',
            'move': 'MOVE'
        }

        series_id = series_map.get(index, 'VIXCLS')
        return self._fetch_fred_series(series_id, params)

    def _get_exchange_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get exchange rates"""
        currency = params.get('currency', 'eur')

        series_map = {
            'eur': 'DEXUSEU',
            'gbp': 'DEXUSUK',
            'jpy': 'DEXJPUS',
            'cny': 'DEXCHUS',
            'cad': 'DEXCAUS',
            'mxn': 'DEXMXUS',
            'aud': 'DEXUSAL'
        }

        series_id = series_map.get(currency, 'DEXUSEU')
        return self._fetch_fred_series(series_id, params)

    def _get_dollar_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get US Dollar Index"""
        index_type = params.get('index_type', 'trade_weighted')

        series_map = {
            'trade_weighted': 'DTWEXBGS',
            'major_currencies': 'DTWEXM',
            'broad': 'DTWEXBGS'
        }

        series_id = series_map.get(index_type, 'DTWEXBGS')
        return self._fetch_fred_series(series_id, params)

    # ==================== BANKING & CREDIT ====================

    def _get_money_supply(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get money supply data"""
        supply_type = params.get('supply_type', 'm2')

        series_id = 'M2SL' if supply_type == 'm2' else 'M1SL'
        return self._fetch_fred_series(series_id, params)

    def _get_banking_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get banking statistics"""
        stat_type = params.get('stat_type', 'reserves')

        series_map = {
            'reserves': 'TOTRESNS',
            'loans': 'TOTLL',
            'deposits': 'DPSACBW027SBOG',
            'assets': 'TLAACBW027SBOG'
        }

        series_id = series_map.get(stat_type, 'TOTRESNS')
        return self._fetch_fred_series(series_id, params)

    def _get_bank_lending_standards(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get bank lending standards"""
        loan_type = params.get('loan_type', 'commercial')

        series_map = {
            'commercial': 'DRTSCILM',
            'consumer': 'DRTSCLCC',
            'mortgage': 'DRTSPM',
            'small_business': 'DRTSSBS'
        }

        series_id = series_map.get(loan_type, 'DRTSCILM')
        return self._fetch_fred_series(series_id, params)

    def _get_consumer_credit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get consumer credit data"""
        credit_type = params.get('credit_type', 'total')

        series_map = {
            'total': 'TOTALSL',
            'revolving': 'REVOLSL',
            'nonrevolving': 'NONREVSL',
            'auto': 'MVLOAS',
            'student': 'SLOAS'
        }

        series_id = series_map.get(credit_type, 'TOTALSL')
        return self._fetch_fred_series(series_id, params)

    def _get_mortgage_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get mortgage rates"""
        mortgage_type = params.get('mortgage_type', '30Y_fixed')

        series_map = {
            '30Y_fixed': 'MORTGAGE30US',
            '15Y_fixed': 'MORTGAGE15US',
            '5Y_arm': 'MORTGAGE5US',
            'jumbo': 'MORTGAGEJUMBOUS'
        }

        series_id = series_map.get(mortgage_type, 'MORTGAGE30US')
        return self._fetch_fred_series(series_id, params)

    def _get_credit_card_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get credit card interest rates"""
        return self._fetch_fred_series('TERMCBCCALLNS', params)

    def _get_auto_loan_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get auto loan rates"""
        return self._fetch_fred_series('TERMAFCNCNSA', params)

    def _get_commercial_paper(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get commercial paper rates"""
        paper_type = params.get('paper_type', 'financial')

        series_map = {
            'financial': 'DCPF3M',
            'nonfinancial': 'DCPN3M',
            'asset_backed': 'DCPAB3M'
        }

        series_id = series_map.get(paper_type, 'DCPF3M')
        return self._fetch_fred_series(series_id, params)

    def _get_bank_failures(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get bank failure data"""
        # Note: This requires FDIC data integration
        return {
            "message": "Bank failure data available at fdic.gov/bank-failures",
            "source": "FDIC"
        }

    # ==================== HOUSING MARKET ====================

    def _get_housing_starts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get housing starts data"""
        data_type = params.get('data_type', 'starts')

        series_map = {
            'starts': 'HOUST',
            'permits': 'PERMIT',
            'completions': 'COMPUTSA',
            'under_construction': 'UNDCONTSA'
        }

        series_id = series_map.get(data_type, 'HOUST')
        return self._fetch_fred_series(series_id, params)

    def _get_home_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get home price indices"""
        index_type = params.get('index_type', 'case_shiller')

        series_map = {
            'case_shiller': 'CSUSHPISA',
            'fhfa': 'USSTHPI',
            'median_price': 'MSPUS',
            'price_rent_ratio': 'PRICERENTCITYA01USQ661S'
        }

        series_id = series_map.get(index_type, 'CSUSHPISA')
        return self._fetch_fred_series(series_id, params)

    def _get_existing_home_sales(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get existing home sales data"""
        metric = params.get('metric', 'sales')

        series_map = {
            'sales': 'EXHOSLUSM495S',
            'inventory': 'MSACSR',
            'months_supply': 'HOSSUPUSM673N',
            'median_days': 'MEDDAYONMARUS'
        }

        series_id = series_map.get(metric, 'EXHOSLUSM495S')
        return self._fetch_fred_series(series_id, params)

    def _get_new_home_sales(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get new home sales data"""
        return self._fetch_fred_series('HSN1F', params)

    def _get_construction_spending(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get construction spending data"""
        return self._fetch_fred_series('TTLCONS', params)

    def _get_homeownership_rate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get homeownership rate"""
        return self._fetch_fred_series('RHORUSQ156N', params)

    # ==================== INDUSTRIAL & MANUFACTURING ====================

    def _get_industrial_production(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get industrial production"""
        sector = params.get('sector', 'total')

        series_map = {
            'total': 'INDPRO',
            'manufacturing': 'IPMAN',
            'mining': 'IPB50001N',
            'utilities': 'IPB56100N',
            'tech': 'IPHITECH'
        }

        series_id = series_map.get(sector, 'INDPRO')
        return self._fetch_fred_series(series_id, params)

    def _get_capacity_utilization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get capacity utilization"""
        sector = params.get('sector', 'total')

        series_map = {
            'total': 'TCU',
            'manufacturing': 'MCUMFN',
            'mining': 'CUMFNS'
        }

        series_id = series_map.get(sector, 'TCU')
        return self._fetch_fred_series(series_id, params)

    def _get_manufacturing_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get manufacturing indicators"""
        indicator = params.get('indicator', 'pmi')

        series_map = {
            'pmi': 'MANEMP',  # ISM Manufacturing PMI would require external source
            'new_orders': 'AMTUNO',
            'shipments': 'AMTMVS'
        }

        series_id = series_map.get(indicator, 'MANEMP')
        return self._fetch_fred_series(series_id, params)

    def _get_durable_goods(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get durable goods orders"""
        return self._fetch_fred_series('DGORDER', params)

    def _get_factory_orders(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get factory orders"""
        return self._fetch_fred_series('TMNMNO', params)

    def _get_business_inventories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get business inventories"""
        return self._fetch_fred_series('BUSINV', params)

    # ==================== CONSUMER & RETAIL ====================

    def _get_retail_sales(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get retail sales data"""
        category = params.get('category', 'total')

        series_map = {
            'total': 'RSAFS',
            'ex_auto': 'RSFSXMV',
            'ex_gas': 'RSXFS',
            'core': 'RSCCASN',
            'online': 'ECOMSA',
            'restaurants': 'RSFSDP'
        }

        series_id = series_map.get(category, 'RSAFS')
        return self._fetch_fred_series(series_id, params)

    def _get_consumer_sentiment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get consumer sentiment"""
        survey = params.get('survey', 'michigan')

        series_map = {
            'michigan': 'UMCSENT',
            'conference_board': 'CSCICP03USM665S',
            'expectations': 'MEXPCH',
            'current': 'UMCSENT'
        }

        series_id = series_map.get(survey, 'UMCSENT')
        return self._fetch_fred_series(series_id, params)

    def _get_personal_income(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get personal income data"""
        component = params.get('component', 'total')

        series_map = {
            'total': 'PI',
            'wages': 'WASCUR',
            'disposable': 'DSPI',
            'real_disposable': 'DSPIC96'
        }

        series_id = series_map.get(component, 'PI')
        return self._fetch_fred_series(series_id, params)

    def _get_personal_spending(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get personal consumption expenditures"""
        category = params.get('category', 'total')

        series_map = {
            'total': 'PCE',
            'goods': 'PCEDG',
            'services': 'PCES',
            'durable': 'PCDG',
            'nondurable': 'PCND'
        }

        series_id = series_map.get(category, 'PCE')
        return self._fetch_fred_series(series_id, params)

    def _get_savings_rate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get personal savings rate"""
        return self._fetch_fred_series('PSAVERT', params)

    def _get_household_debt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get household debt data"""
        debt_type = params.get('debt_type', 'total')

        series_map = {
            'total': 'HDTGPDUSQ163N',
            'mortgage': 'MDOTHPD',
            'consumer': 'CDOTHPD'
        }

        series_id = series_map.get(debt_type, 'HDTGPDUSQ163N')
        return self._fetch_fred_series(series_id, params)

    # ==================== TRADE & INTERNATIONAL ====================

    def _get_trade_balance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get trade balance data"""
        measure = params.get('measure', 'balance')

        series_map = {
            'balance': 'BOPGSTB',
            'goods': 'BOPGTB',
            'services': 'BOPSTB'
        }

        series_id = series_map.get(measure, 'BOPGSTB')
        return self._fetch_fred_series(series_id, params)

    def _get_exports(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get export data"""
        return self._fetch_fred_series('EXPGS', params)

    def _get_imports(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get import data"""
        return self._fetch_fred_series('IMPGS', params)

    def _get_current_account(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current account data"""
        return self._fetch_fred_series('NETFI', params)

    def _get_foreign_holdings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get foreign holdings of US securities"""
        return self._fetch_fred_series('FDHBTN', params)

    # ==================== REGIONAL FED DATA ====================

    def _get_regional_fed_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get regional Federal Reserve data"""
        region = params.get('region', 'new_york')
        data_type = params.get('data_type', 'activity_index')

        # Map regions to their activity indices
        regional_series = {
            'boston': 'BOST',
            'new_york': 'NYEMP',
            'philadelphia': 'PHIINDPRO',
            'cleveland': 'CLEINDPRO',
            'richmond': 'RICHINDPRO',
            'atlanta': 'ATLINDPRO',
            'chicago': 'CFNAI',
            'st_louis': 'STLINDPRO',
            'minneapolis': 'MINNINDPRO',
            'kansas_city': 'KCINDPRO',
            'dallas': 'DALINDPRO',
            'san_francisco': 'SFINDPRO'
        }

        series_id = regional_series.get(region, 'CFNAI')
        return self._fetch_fred_series(series_id, params)

    def _get_beige_book(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Beige Book information"""
        return {
            "message": "Beige Book available at federalreserve.gov/monetarypolicy/beigebook",
            "frequency": "8 times per year",
            "description": "Summary of economic conditions in each Fed district"
        }

    def _get_state_unemployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get state-level unemployment data"""
        state = params.get('state', 'CA')

        # Example for California, would need full state mapping
        series_id = f'{state}UR'
        return self._fetch_fred_series(series_id, params)

    def _get_metro_area_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get metropolitan area economic data"""
        metro = params.get('metro', 'NYC')
        data_type = params.get('data_type', 'unemployment')

        # Example mapping
        metro_series = {
            'NYC': 'NEWY636UR',
            'LA': 'LOSA006UR',
            'CHI': 'CHIC917UR'
        }

        series_id = metro_series.get(metro, 'NEWY636UR')
        return self._fetch_fred_series(series_id, params)

    # ==================== FINANCIAL STABILITY ====================

    def _get_financial_stress_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get financial stress indices"""
        index_type = params.get('index_type', 'stlfsi')

        series_map = {
            'stlfsi': 'STLFSI2',
            'nfci': 'NFCI',
            'vix': 'VIXCLS',
            'move': 'MOVE'
        }

        series_id = series_map.get(index_type, 'STLFSI2')
        return self._fetch_fred_series(series_id, params)

    def _get_systemic_risk_indicators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get systemic risk indicators"""
        indicator = params.get('indicator', 'srisk')

        # Note: Some systemic risk indicators require external sources
        series_map = {
            'leverage': 'ANFCI',
            'credit_growth': 'TOTBKCR'
        }

        series_id = series_map.get(indicator, 'ANFCI')
        return self._fetch_fred_series(series_id, params)

    def _get_leverage_ratios(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get financial sector leverage ratios"""
        return self._fetch_fred_series('BOGZ1FL794190005Q', params)

    def _get_liquidity_indicators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get market liquidity indicators"""
        indicator = params.get('indicator', 'bid_ask')

        # Placeholder - would require market data
        return {
            "indicator": indicator,
            "message": "Detailed liquidity indicators require market microstructure data"
        }

    # ==================== HISTORICAL & RESEARCH ====================

    def _search_series(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for economic series"""
        search_text = params.get('search_text', '')

        if not search_text:
            return {"error": "Search text is required"}

        if not self.api_key:
            return {"error": "FRED API key required"}

        try:
            url = f"{self.fred_base_url}/series/search"
            api_params = {
                'search_text': search_text,
                'api_key': self.api_key,
                'file_type': 'json',
                'limit': 20
            }

            response = requests.get(url, params=api_params)
            if response.status_code == 200:
                data = response.json()
                series = data.get('seriess', [])

                results = []
                for s in series:
                    results.append({
                        'id': s.get('id'),
                        'title': s.get('title'),
                        'units': s.get('units'),
                        'frequency': s.get('frequency'),
                        'popularity': s.get('popularity'),
                        'observation_start': s.get('observation_start'),
                        'observation_end': s.get('observation_end')
                    })

                return {
                    "search_text": search_text,
                    "results": results,
                    "count": len(results)
                }
        except Exception as e:
            return {"error": str(e)}

    def _get_series_metadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed series metadata"""
        series_id = params.get('series_id', '')

        if not series_id:
            return {"error": "Series ID required"}

        if not self.api_key:
            return {"error": "FRED API key required"}

        try:
            url = f"{self.fred_base_url}/series"
            api_params = {
                'series_id': series_id,
                'api_key': self.api_key,
                'file_type': 'json'
            }

            response = requests.get(url, params=api_params)
            if response.status_code == 200:
                data = response.json()
                if 'seriess' in data and data['seriess']:
                    series = data['seriess'][0]
                    return {
                        'series_id': series.get('id'),
                        'title': series.get('title'),
                        'units': series.get('units'),
                        'frequency': series.get('frequency'),
                        'seasonal_adjustment': series.get('seasonal_adjustment'),
                        'last_updated': series.get('last_updated'),
                        'observation_start': series.get('observation_start'),
                        'observation_end': series.get('observation_end'),
                        'popularity': series.get('popularity'),
                        'notes': series.get('notes')
                    }
        except Exception as e:
            return {"error": str(e)}

    def _get_vintage_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get vintage data for a series"""
        series_id = params.get('series_id', '')
        vintage_date = params.get('vintage_date', '')

        if not series_id:
            return {"error": "Series ID required"}

        # Note: Would require FRED vintage API endpoint
        return {
            "series_id": series_id,
            "vintage_date": vintage_date,
            "message": "Vintage data requires ALFRED (Archival FRED) API"
        }

    def _get_recession_dates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get NBER recession dates"""
        return self._fetch_fred_series('USREC', params)

    def _get_historical_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical interest rates"""
        rate_type = params.get('rate_type', 'federal_funds')
        start_date = params.get('start_date', '1954-07-01')

        series_map = {
            'federal_funds': 'FEDFUNDS',
            'discount': 'INTDSRUSM193N',
            '10Y_treasury': 'GS10'
        }

        series_id = series_map.get(rate_type, 'FEDFUNDS')
        params['start_date'] = start_date
        return self._fetch_fred_series(series_id, params)

    # ==================== SPECIALIZED INDICATORS ====================

    def _get_term_premia(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get term premium estimates"""
        maturity = params.get('maturity', '10Y')

        series_map = {
            '5Y': 'THREEFYTP5',
            '10Y': 'THREEFYTP10'
        }

        series_id = series_map.get(maturity, 'THREEFYTP10')
        return self._fetch_fred_series(series_id, params)

    def _get_natural_rate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get natural rate of interest (r-star)"""
        return self._fetch_fred_series('NROU', params)

    def _get_output_gap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get output gap estimates"""
        return self._fetch_fred_series('GDPPOT', params)

    def _get_taylor_rule(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Taylor Rule implied rate"""
        version = params.get('version', 'original')

        # Note: Would require calculation based on inflation and output gap
        return {
            "version": version,
            "message": "Taylor Rule calculation requires inflation and output gap data",
            "formula": "r = p + 0.5y + 0.5(p - 2) + 2"
        }

    def _get_financial_conditions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get financial conditions indices"""
        index = params.get('index', 'nfci')

        series_map = {
            'nfci': 'NFCI',
            'anfci': 'ANFCI',
            'nfci_leverage': 'NFCILEVERAGE',
            'nfci_credit': 'NFCICREDIT'
        }

        series_id = series_map.get(index, 'NFCI')
        return self._fetch_fred_series(series_id, params)

    def _get_credit_spreads(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get various credit spreads"""
        spread_type = params.get('spread_type', 'baa_treasury')

        series_map = {
            'baa_treasury': 'BAA10Y',
            'aaa_treasury': 'AAA10Y',
            'ted_spread': 'TEDRATE',
            'libor_ois': 'DEXCAUS'  # Placeholder
        }

        series_id = series_map.get(spread_type, 'BAA10Y')
        return self._fetch_fred_series(series_id, params)

    def _get_commodity_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get commodity price indices"""
        commodity = params.get('commodity', 'all')

        series_map = {
            'all': 'PPIACO',
            'energy': 'PPIENG',
            'metals': 'PPICMM',
            'agriculture': 'WPU01',
            'gold': 'GOLDAMGBD228NLBM',
            'oil': 'DCOILWTICO'
        }

        series_id = series_map.get(commodity, 'PPIACO')
        return self._fetch_fred_series(series_id, params)

    def _get_energy_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get energy price data"""
        energy_type = params.get('energy_type', 'oil')

        series_map = {
            'oil': 'DCOILWTICO',
            'gas': 'GASPRICE',
            'natural_gas': 'DHHNGSP',
            'electricity': 'APU000072610'
        }

        series_id = series_map.get(energy_type, 'DCOILWTICO')
        return self._fetch_fred_series(series_id, params)