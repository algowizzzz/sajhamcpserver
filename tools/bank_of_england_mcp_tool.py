"""
Bank of England MCP Tool implementation with comprehensive capabilities
"""
import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base_mcp_tool import BaseMCPTool


class BankOfEnglandMCPTool(BaseMCPTool):
    """Comprehensive MCP Tool for Bank of England data operations"""

    def _initialize(self):
        """Initialize Bank of England specific components"""
        # Bank of England Statistical Interactive Database API
        self.boe_base_url = "https://www.bankofengland.co.uk/boeapps/iadb"
        # Bank of England API
        self.api_base_url = "https://api.bankofengland.co.uk/api"

        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Bank of England tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            # Comprehensive tool method mapping
            tool_methods = {
                # Monetary Policy & Interest Rates
                "get_bank_rate": self._get_bank_rate,
                "get_sonia": self._get_sonia,
                "get_repo_rate": self._get_repo_rate,
                "get_term_sonia": self._get_term_sonia,
                "get_libor_rates": self._get_libor_rates,
                "get_swap_rates": self._get_swap_rates,
                "get_overnight_index_swaps": self._get_overnight_index_swaps,
                "get_forward_rates": self._get_forward_rates,
                "get_real_interest_rates": self._get_real_interest_rates,

                # Economic Indicators
                "get_inflation_data": self._get_inflation_data,
                "get_cpi_data": self._get_cpi_data,
                "get_rpi_data": self._get_rpi_data,
                "get_gdp_data": self._get_gdp_data,
                "get_unemployment": self._get_unemployment,
                "get_wage_growth": self._get_wage_growth,
                "get_productivity": self._get_productivity,
                "get_output_gap": self._get_output_gap,
                "get_retail_sales": self._get_retail_sales,

                # Exchange Rates
                "get_sterling_exchange_rates": self._get_sterling_exchange_rates,
                "get_effective_exchange_rates": self._get_effective_exchange_rates,
                "get_spot_rates": self._get_spot_rates,
                "get_forward_exchange_rates": self._get_forward_exchange_rates,
                "get_currency_volatility": self._get_currency_volatility,

                # Government Securities & Gilts
                "get_gilt_yields": self._get_gilt_yields,
                "get_gilt_prices": self._get_gilt_prices,
                "get_index_linked_gilts": self._get_index_linked_gilts,
                "get_gilt_issuance": self._get_gilt_issuance,
                "get_yield_curve": self._get_yield_curve,
                "get_treasury_bills": self._get_treasury_bills,

                # Banking & Financial System
                "get_bank_lending": self._get_bank_lending,
                "get_mortgage_lending": self._get_mortgage_lending,
                "get_consumer_credit": self._get_consumer_credit,
                "get_deposit_rates": self._get_deposit_rates,
                "get_lending_rates": self._get_lending_rates,
                "get_credit_conditions": self._get_credit_conditions,
                "get_bank_capital_ratios": self._get_bank_capital_ratios,
                "get_bank_stress_tests": self._get_bank_stress_tests,

                # Money Supply & Credit
                "get_money_supply": self._get_money_supply,
                "get_broad_money": self._get_broad_money,
                "get_credit_growth": self._get_credit_growth,
                "get_sectoral_lending": self._get_sectoral_lending,
                "get_lending_to_smes": self._get_lending_to_smes,

                # Financial Markets
                "get_ftse_indices": self._get_ftse_indices,
                "get_equity_prices": self._get_equity_prices,
                "get_corporate_bond_spreads": self._get_corporate_bond_spreads,
                "get_sterling_money_markets": self._get_sterling_money_markets,
                "get_derivatives_data": self._get_derivatives_data,

                # Housing Market
                "get_house_prices": self._get_house_prices,
                "get_mortgage_approvals": self._get_mortgage_approvals,
                "get_mortgage_rates": self._get_mortgage_rates,
                "get_buy_to_let": self._get_buy_to_let,
                "get_housing_transactions": self._get_housing_transactions,
                "get_rental_yields": self._get_rental_yields,

                # External Sector
                "get_current_account": self._get_current_account,
                "get_trade_balance": self._get_trade_balance,
                "get_exports": self._get_exports,
                "get_imports": self._get_imports,
                "get_foreign_investment": self._get_foreign_investment,
                "get_uk_investment_abroad": self._get_uk_investment_abroad,

                # Regional Data
                "get_regional_gdp": self._get_regional_gdp,
                "get_regional_unemployment": self._get_regional_unemployment,
                "get_regional_house_prices": self._get_regional_house_prices,
                "get_regional_lending": self._get_regional_lending,

                # Business Conditions
                "get_agents_scores": self._get_agents_scores,
                "get_business_investment": self._get_business_investment,
                "get_corporate_profitability": self._get_corporate_profitability,
                "get_company_liquidations": self._get_company_liquidations,
                "get_credit_availability": self._get_credit_availability,

                # Financial Stability
                "get_systemic_risk_survey": self._get_systemic_risk_survey,
                "get_financial_stability_indicators": self._get_financial_stability_indicators,
                "get_countercyclical_buffer": self._get_countercyclical_buffer,
                "get_leverage_ratio": self._get_leverage_ratio,
                "get_liquidity_coverage": self._get_liquidity_coverage,

                # Surveys & Expectations
                "get_inflation_expectations": self._get_inflation_expectations,
                "get_inflation_attitudes_survey": self._get_inflation_attitudes_survey,
                "get_credit_conditions_survey": self._get_credit_conditions_survey,
                "get_bank_liabilities_survey": self._get_bank_liabilities_survey,
                "get_mpc_minutes": self._get_mpc_minutes,

                # Quantitative Easing & Balance Sheet
                "get_asset_purchase_facility": self._get_asset_purchase_facility,
                "get_qe_holdings": self._get_qe_holdings,
                "get_bank_reserves": self._get_bank_reserves,
                "get_balance_sheet": self._get_balance_sheet,
                "get_term_funding_scheme": self._get_term_funding_scheme,

                # Historical Data
                "get_historical_bank_rate": self._get_historical_bank_rate,
                "get_historical_exchange_rates": self._get_historical_exchange_rates,
                "get_historical_inflation": self._get_historical_inflation,
                "get_long_run_data": self._get_long_run_data,

                # Payment Systems
                "get_chaps_volumes": self._get_chaps_volumes,
                "get_faster_payments": self._get_faster_payments,
                "get_rtgs_statistics": self._get_rtgs_statistics,
                "get_payment_statistics": self._get_payment_statistics,

                # Brexit-related
                "get_brexit_uncertainty_index": self._get_brexit_uncertainty_index,
                "get_eu_trade_statistics": self._get_eu_trade_statistics,
                "get_financial_services_trade": self._get_financial_services_trade,

                # Climate & ESG
                "get_climate_risk_indicators": self._get_climate_risk_indicators,
                "get_green_bonds": self._get_green_bonds,
                "get_transition_indicators": self._get_transition_indicators,

                # Search & Metadata
                "search_series": self._search_series,
                "get_series_metadata": self._get_series_metadata,
                "get_data_availability": self._get_data_availability
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

    def _fetch_boe_data(self, series_code: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Centralized Bank of England data fetching"""
        try:
            # Build URL for data retrieval
            url = f"{self.boe_base_url}/export.aspx"

            # Build query parameters
            query_params = {
                'SeriesCodes': series_code,
                'CSVF': 'TN',
                'UsingCodes': 'Y',
                'VPD': 'Y',
                'VFD': 'N'
            }

            if params.get('datefrom'):
                query_params['Datefrom'] = params['datefrom']
            if params.get('dateto'):
                query_params['Dateto'] = params['dateto']

            response = requests.get(url, params=query_params, headers=self.headers)

            if response.status_code != 200:
                return {"error": f"API request failed with status {response.status_code}"}

            # Parse CSV response
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                return {"error": "No data returned"}

            # Parse header and data
            headers = lines[0].split(',')
            observations = []

            for line in lines[1:]:
                values = line.split(',')
                if len(values) >= 2:
                    observations.append({
                        'date': values[0],
                        'value': values[1] if len(values) > 1 else None
                    })

            # Sort observations by date
            observations.sort(key=lambda x: x['date'], reverse=True)

            # Calculate changes
            changes = []
            if len(observations) > 1:
                for i in range(len(observations) - 1):
                    if observations[i]['value'] and observations[i+1]['value']:
                        try:
                            current = float(observations[i]['value'])
                            previous = float(observations[i+1]['value'])
                            if previous != 0:
                                change = ((current - previous) / previous) * 100
                                changes.append({
                                    'date': observations[i]['date'],
                                    'change_pct': round(change, 2)
                                })
                        except:
                            pass

            return {
                "series_code": series_code,
                "latest_value": observations[0]['value'] if observations else None,
                "latest_date": observations[0]['date'] if observations else None,
                "observations": observations[:params.get('limit', 30)],
                "changes": changes[:5] if changes else [],
                "count": len(observations)
            }

        except Exception as e:
            return {"error": str(e)}

    # ==================== MONETARY POLICY & INTEREST RATES ====================

    def _get_bank_rate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Bank of England Bank Rate (policy rate)"""
        return self._fetch_boe_data('IUDBEDR', params)

    def _get_sonia(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Sterling Overnight Index Average (SONIA)"""
        return self._fetch_boe_data('IUDSOIA', params)

    def _get_repo_rate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get repo rate"""
        return self._fetch_boe_data('IUDRPOR', params)

    def _get_term_sonia(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Term SONIA reference rates"""
        term = params.get('term', '3M')

        term_map = {
            '1M': 'IUDTSRM1',
            '3M': 'IUDTSRM3',
            '6M': 'IUDTSRM6',
            '12M': 'IUDTSRM12'
        }

        series_code = term_map.get(term, 'IUDTSRM3')
        return self._fetch_boe_data(series_code, params)

    def _get_libor_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get LIBOR rates (discontinued but historical data available)"""
        return {
            "message": "LIBOR discontinued end-2021, replaced by SONIA",
            "alternative": "Use get_sonia() or get_term_sonia() for current rates"
        }

    def _get_swap_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get interest rate swap rates"""
        maturity = params.get('maturity', '5Y')

        maturity_map = {
            '1Y': 'IUDSW1Y',
            '2Y': 'IUDSW2Y',
            '3Y': 'IUDSW3Y',
            '5Y': 'IUDSW5Y',
            '7Y': 'IUDSW7Y',
            '10Y': 'IUDSW10Y'
        }

        series_code = maturity_map.get(maturity, 'IUDSW5Y')
        return self._fetch_boe_data(series_code, params)

    def _get_overnight_index_swaps(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Overnight Index Swap rates"""
        return self._fetch_boe_data('IUDOIS', params)

    def _get_forward_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get forward interest rates"""
        horizon = params.get('horizon', '1Y')

        horizon_map = {
            '1Y': 'IUDFWD1Y',
            '2Y': 'IUDFWD2Y',
            '5Y': 'IUDFWD5Y'
        }

        series_code = horizon_map.get(horizon, 'IUDFWD1Y')
        return self._fetch_boe_data(series_code, params)

    def _get_real_interest_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get real interest rates"""
        return self._fetch_boe_data('IUDREAL', params)

    # ==================== ECONOMIC INDICATORS ====================

    def _get_inflation_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get UK inflation data"""
        measure = params.get('measure', 'cpi')

        measure_map = {
            'cpi': 'D7BT',
            'cpih': 'L522',
            'rpi': 'CZBH',
            'core_cpi': 'D7G8'
        }

        series_code = measure_map.get(measure, 'D7BT')
        return self._fetch_boe_data(series_code, params)

    def _get_cpi_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Consumer Price Index data"""
        return self._fetch_boe_data('D7BT', params)

    def _get_rpi_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Retail Price Index data"""
        return self._fetch_boe_data('CZBH', params)

    def _get_gdp_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get UK GDP data"""
        gdp_type = params.get('gdp_type', 'growth')

        gdp_map = {
            'growth': 'IHYQ',
            'level': 'ABMI',
            'per_capita': 'IHXW'
        }

        series_code = gdp_map.get(gdp_type, 'IHYQ')
        return self._fetch_boe_data(series_code, params)

    def _get_unemployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get UK unemployment rate"""
        return self._fetch_boe_data('MGSX', params)

    def _get_wage_growth(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get wage growth data"""
        measure = params.get('measure', 'average_weekly')

        measure_map = {
            'average_weekly': 'KAB9',
            'regular_pay': 'KAI7',
            'total_pay': 'KAI8'
        }

        series_code = measure_map.get(measure, 'KAB9')
        return self._fetch_boe_data(series_code, params)

    def _get_productivity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get productivity data"""
        return self._fetch_boe_data('LZVB', params)

    def _get_output_gap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get output gap estimates"""
        return {
            "message": "Output gap estimates available in Monetary Policy Report",
            "source": "Bank of England staff estimates"
        }

    def _get_retail_sales(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get retail sales data"""
        return self._fetch_boe_data('J5EK', params)

    # ==================== EXCHANGE RATES ====================

    def _get_sterling_exchange_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Sterling exchange rates"""
        currency = params.get('currency', 'USD')

        currency_map = {
            'USD': 'XUDLUSS',
            'EUR': 'XUDLERS',
            'JPY': 'XUDLJYS',
            'CHF': 'XUDLSFS',
            'CAD': 'XUDLCDS',
            'AUD': 'XUDLADS',
            'CNY': 'XUDLBK73'
        }

        series_code = currency_map.get(currency, 'XUDLUSS')
        return self._fetch_boe_data(series_code, params)

    def _get_effective_exchange_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Sterling effective exchange rates"""
        eer_type = params.get('eer_type', 'nominal')

        eer_map = {
            'nominal': 'XUDLBK67',
            'real': 'XUDLBK68'
        }

        series_code = eer_map.get(eer_type, 'XUDLBK67')
        return self._fetch_boe_data(series_code, params)

    def _get_spot_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get spot exchange rates"""
        return self._get_sterling_exchange_rates(params)

    def _get_forward_exchange_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get forward exchange rates"""
        currency = params.get('currency', 'USD')
        tenor = params.get('tenor', '1M')

        # Forward rates series codes
        series_code = f'XUDF{currency}{tenor}'
        return self._fetch_boe_data(series_code, params)

    def _get_currency_volatility(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get currency volatility measures"""
        currency = params.get('currency', 'USD')

        # Implied volatility series
        series_code = f'XUDVOL{currency}'
        return self._fetch_boe_data(series_code, params)

    # ==================== GOVERNMENT SECURITIES & GILTS ====================

    def _get_gilt_yields(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get UK government bond (gilt) yields"""
        maturity = params.get('maturity', '10Y')

        maturity_map = {
            '2Y': 'IUDMNPY2',
            '3Y': 'IUDMNPY3',
            '5Y': 'IUDMNPY5',
            '7Y': 'IUDMNPY7',
            '10Y': 'IUDMNPY10',
            '20Y': 'IUDMNPY20',
            '30Y': 'IUDMNPY30'
        }

        series_code = maturity_map.get(maturity, 'IUDMNPY10')
        return self._fetch_boe_data(series_code, params)

    def _get_gilt_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get gilt prices"""
        return self._fetch_boe_data('IUDGPRC', params)

    def _get_index_linked_gilts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get index-linked gilt yields"""
        maturity = params.get('maturity', '10Y')

        maturity_map = {
            '5Y': 'IUDMIRY5',
            '10Y': 'IUDMIRY10',
            '20Y': 'IUDMIRY20'
        }

        series_code = maturity_map.get(maturity, 'IUDMIRY10')
        return self._fetch_boe_data(series_code, params)

    def _get_gilt_issuance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get gilt issuance data"""
        return self._fetch_boe_data('LPMBATP', params)

    def _get_yield_curve(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get UK yield curve"""
        maturities = {
            '1Y': 'IUDMNPY1',
            '2Y': 'IUDMNPY2',
            '3Y': 'IUDMNPY3',
            '5Y': 'IUDMNPY5',
            '7Y': 'IUDMNPY7',
            '10Y': 'IUDMNPY10',
            '20Y': 'IUDMNPY20',
            '30Y': 'IUDMNPY30'
        }

        yields = {}
        for maturity, series_code in maturities.items():
            result = self._fetch_boe_data(series_code, {'limit': 1})
            if 'latest_value' in result:
                yields[maturity] = float(result['latest_value'])

        # Calculate spreads
        spreads = {}
        if '10Y' in yields and '2Y' in yields:
            spreads['10Y2Y'] = round(yields['10Y'] - yields['2Y'], 2)
        if '10Y' in yields and '1Y' in yields:
            spreads['10Y1Y'] = round(yields['10Y'] - yields['1Y'], 2)

        return {
            "yield_curve": yields,
            "spreads": spreads,
            "date": datetime.now().strftime('%Y-%m-%d')
        }

    def _get_treasury_bills(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Treasury Bill rates"""
        return self._fetch_boe_data('IUDTBR', params)

    # ==================== BANKING & FINANCIAL SYSTEM ====================

    def _get_bank_lending(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get bank lending data"""
        return self._fetch_boe_data('LPMVTXK', params)

    def _get_mortgage_lending(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get mortgage lending data"""
        return self._fetch_boe_data('LPMVTVX', params)

    def _get_consumer_credit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get consumer credit data"""
        return self._fetch_boe_data('LPMVZRJ', params)

    def _get_deposit_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get deposit interest rates"""
        deposit_type = params.get('deposit_type', 'household')

        deposit_map = {
            'household': 'IUMBV34',
            'corporate': 'IUMBV37',
            'instant_access': 'IUMBV54',
            'fixed_rate': 'IUMBV56'
        }

        series_code = deposit_map.get(deposit_type, 'IUMBV34')
        return self._fetch_boe_data(series_code, params)

    def _get_lending_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get lending interest rates"""
        loan_type = params.get('loan_type', 'mortgage')

        loan_map = {
            'mortgage': 'IUMBV45',
            'personal_loan': 'IUMBV48',
            'credit_card': 'IUMBV49',
            'overdraft': 'IUMBV50'
        }

        series_code = loan_map.get(loan_type, 'IUMBV45')
        return self._fetch_boe_data(series_code, params)

    def _get_credit_conditions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get credit conditions from surveys"""
        return {
            "message": "Credit Conditions Survey available quarterly",
            "source": "Bank of England Credit Conditions Survey"
        }

    def _get_bank_capital_ratios(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get bank capital ratios"""
        ratio_type = params.get('ratio_type', 'tier1')

        ratio_map = {
            'tier1': 'RPQB762',
            'cet1': 'RPQB763',
            'total_capital': 'RPQB764'
        }

        series_code = ratio_map.get(ratio_type, 'RPQB762')
        return self._fetch_boe_data(series_code, params)

    def _get_bank_stress_tests(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get bank stress test results"""
        return {
            "message": "Annual stress test results available",
            "source": "Bank of England Financial Stability Report"
        }

    # ==================== MONEY SUPPLY & CREDIT ====================

    def _get_money_supply(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get money supply data"""
        aggregate = params.get('aggregate', 'M4')

        aggregate_map = {
            'M0': 'LPMAUYM',
            'M4': 'LPMVQJW',
            'M4_lending': 'LPMVQLU'
        }

        series_code = aggregate_map.get(aggregate, 'LPMVQJW')
        return self._fetch_boe_data(series_code, params)

    def _get_broad_money(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get broad money (M4) growth"""
        return self._fetch_boe_data('LPMVQJW', params)

    def _get_credit_growth(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get credit growth to private sector"""
        return self._fetch_boe_data('LPMVWYL', params)

    def _get_sectoral_lending(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get lending by sector"""
        sector = params.get('sector', 'household')

        sector_map = {
            'household': 'LPMVTVR',
            'pnfc': 'LPMVWNV',  # Private non-financial corporations
            'financial': 'LPMB6J3',
            'real_estate': 'LPMBC57'
        }

        series_code = sector_map.get(sector, 'LPMVTVR')
        return self._fetch_boe_data(series_code, params)

    def _get_lending_to_smes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get lending to small and medium enterprises"""
        return self._fetch_boe_data('LPMB3E2', params)

    # ==================== FINANCIAL MARKETS ====================

    def _get_ftse_indices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get FTSE index data"""
        index = params.get('index', 'ftse100')

        index_map = {
            'ftse100': 'LMIAFF',
            'ftse250': 'LMIAFL',
            'ftse_all_share': 'LMIAFD'
        }

        series_code = index_map.get(index, 'LMIAFF')
        return self._fetch_boe_data(series_code, params)

    def _get_equity_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get equity price indices"""
        return self._fetch_boe_data('LMIAFD', params)

    def _get_corporate_bond_spreads(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get corporate bond spreads"""
        rating = params.get('rating', 'investment_grade')

        rating_map = {
            'investment_grade': 'IUMSCIG',
            'high_yield': 'IUMSCHY',
            'aaa': 'IUMSCAAA'
        }

        series_code = rating_map.get(rating, 'IUMSCIG')
        return self._fetch_boe_data(series_code, params)

    def _get_sterling_money_markets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get sterling money market data"""
        return self._fetch_boe_data('IUDSMMR', params)

    def _get_derivatives_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get derivatives market data"""
        return {
            "message": "Derivatives data available from ICE Futures Europe",
            "source": "Exchange data providers"
        }

    # ==================== HOUSING MARKET ====================

    def _get_house_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get UK house price indices"""
        index_type = params.get('index_type', 'nationwide')

        index_map = {
            'nationwide': 'AMWZ',
            'halifax': 'AMVJ',
            'land_registry': 'AMSJ'
        }

        series_code = index_map.get(index_type, 'AMWZ')
        return self._fetch_boe_data(series_code, params)

    def _get_mortgage_approvals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get mortgage approval numbers"""
        return self._fetch_boe_data('LPMVTVR', params)

    def _get_mortgage_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get mortgage interest rates"""
        mortgage_type = params.get('mortgage_type', 'variable')

        mortgage_map = {
            'variable': 'IUMBV45',
            'fixed_2y': 'IUMB2Y75',
            'fixed_3y': 'IUMB3Y75',
            'fixed_5y': 'IUMB5Y75'
        }

        series_code = mortgage_map.get(mortgage_type, 'IUMBV45')
        return self._fetch_boe_data(series_code, params)

    def _get_buy_to_let(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get buy-to-let mortgage data"""
        return self._fetch_boe_data('LPMB3F8', params)

    def _get_housing_transactions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get housing transaction volumes"""
        return self._fetch_boe_data('LPMB2WF', params)

    def _get_rental_yields(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get rental yield data"""
        return {
            "message": "Rental yield data from private sector sources",
            "sources": ["Zoopla", "Rightmove", "ONS"]
        }

    # ==================== EXTERNAL SECTOR ====================

    def _get_current_account(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current account balance"""
        return self._fetch_boe_data('HBOP', params)

    def _get_trade_balance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get trade balance"""
        return self._fetch_boe_data('IKBJ', params)

    def _get_exports(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get export data"""
        return self._fetch_boe_data('IKBH', params)

    def _get_imports(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get import data"""
        return self._fetch_boe_data('IKBI', params)

    def _get_foreign_investment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get foreign direct investment data"""
        return self._fetch_boe_data('HBQA', params)

    def _get_uk_investment_abroad(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get UK investment abroad data"""
        return self._fetch_boe_data('HBQB', params)

    # ==================== REGIONAL DATA ====================

    def _get_regional_gdp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get regional GDP data"""
        region = params.get('region', 'london')

        # Regional data typically from ONS
        return {
            "region": region,
            "message": "Regional data available from ONS",
            "source": "Office for National Statistics"
        }

    def _get_regional_unemployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get regional unemployment rates"""
        region = params.get('region', 'london')

        region_map = {
            'london': 'YCNB',
            'southeast': 'YCNC',
            'southwest': 'YCND',
            'eastanglia': 'YCNE',
            'eastmidlands': 'YCNF',
            'westmidlands': 'YCNG',
            'yorkshire': 'YCNH',
            'northwest': 'YCNI',
            'north': 'YCNJ',
            'wales': 'YCNK',
            'scotland': 'YCNL',
            'ni': 'YCNM'
        }

        series_code = region_map.get(region.lower().replace(' ', ''), 'YCNB')
        return self._fetch_boe_data(series_code, params)

    def _get_regional_house_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get regional house price data"""
        region = params.get('region', 'london')

        region_map = {
            'london': 'WQAL',
            'southeast': 'WQAM',
            'southwest': 'WQAN',
            'eastanglia': 'WQAO',
            'eastmidlands': 'WQAP',
            'westmidlands': 'WQAQ',
            'yorkshire': 'WQAR',
            'northwest': 'WQAS',
            'north': 'WQAT',
            'wales': 'WQAU',
            'scotland': 'WQAV',
            'ni': 'WQAW'
        }

        series_code = region_map.get(region.lower().replace(' ', ''), 'WQAL')
        return self._fetch_boe_data(series_code, params)

    def _get_regional_lending(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get regional lending data"""
        region = params.get('region', 'london')

        return {
            "region": region,
            "message": "Regional lending data from mortgage approvals",
            "source": "Bank of England regional statistics"
        }

    # ==================== BUSINESS CONDITIONS ====================

    def _get_agents_scores(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Bank of England Agents' summary scores"""
        indicator = params.get('indicator', 'demand')

        # Agents' scores are published in the Agents' Summary
        return {
            "message": "Agents' scores available in quarterly Agents' Summary",
            "indicator": indicator,
            "source": "Bank of England Agents"
        }

    def _get_business_investment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get business investment data"""
        return self._fetch_boe_data('NPQT', params)

    def _get_corporate_profitability(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get corporate profitability indicators"""
        return self._fetch_boe_data('LPMB8G6', params)

    def _get_company_liquidations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get company liquidation statistics"""
        return self._fetch_boe_data('LPMB8G7', params)

    def _get_credit_availability(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get credit availability indicators"""
        return {
            "message": "Credit availability from Credit Conditions Survey",
            "source": "Bank of England surveys"
        }

    # ==================== FINANCIAL STABILITY ====================

    def _get_systemic_risk_survey(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Systemic Risk Survey results"""
        return {
            "message": "Systemic Risk Survey published semi-annually",
            "source": "Bank of England Systemic Risk Survey"
        }

    def _get_financial_stability_indicators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get financial stability indicators"""
        return {
            "indicators": [
                "Credit-to-GDP gap",
                "Household debt-to-income",
                "Corporate leverage",
                "Property price growth"
            ],
            "source": "Bank of England Financial Stability Report"
        }

    def _get_countercyclical_buffer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get countercyclical capital buffer rate"""
        return self._fetch_boe_data('RPQB886', params)

    def _get_leverage_ratio(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get leverage ratio requirements"""
        return self._fetch_boe_data('RPQB887', params)

    def _get_liquidity_coverage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get liquidity coverage ratio data"""
        return self._fetch_boe_data('RPQB889', params)

    # ==================== SURVEYS & EXPECTATIONS ====================

    def _get_inflation_expectations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get inflation expectations from various sources"""
        source = params.get('source', 'market')

        source_map = {
            'market': 'IUDINFEX5',
            'survey': 'IUDINFEX1',
            'professional': 'IUDINFEX2'
        }

        series_code = source_map.get(source, 'IUDINFEX5')
        return self._fetch_boe_data(series_code, params)

    def _get_inflation_attitudes_survey(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Inflation Attitudes Survey results"""
        return {
            "message": "Inflation Attitudes Survey published quarterly",
            "source": "Bank of England/TNS survey"
        }

    def _get_credit_conditions_survey(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Credit Conditions Survey results"""
        return {
            "message": "Credit Conditions Survey published quarterly",
            "source": "Bank of England"
        }

    def _get_bank_liabilities_survey(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Bank Liabilities Survey results"""
        return {
            "message": "Bank Liabilities Survey published quarterly",
            "source": "Bank of England"
        }

    def _get_mpc_minutes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Monetary Policy Committee meeting minutes"""
        return {
            "frequency": "8 times per year",
            "content": "Policy decisions and voting records",
            "source": "Bank of England Monetary Policy Committee"
        }

    # ==================== QUANTITATIVE EASING & BALANCE SHEET ====================

    def _get_asset_purchase_facility(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Asset Purchase Facility data"""
        return self._fetch_boe_data('RPQB550', params)

    def _get_qe_holdings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get quantitative easing holdings"""
        asset_type = params.get('asset_type', 'gilts')

        asset_map = {
            'gilts': 'RPQB551',
            'corporate_bonds': 'RPQB552'
        }

        series_code = asset_map.get(asset_type, 'RPQB551')
        return self._fetch_boe_data(series_code, params)

    def _get_bank_reserves(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get bank reserves at Bank of England"""
        return self._fetch_boe_data('RPQB545', params)

    def _get_balance_sheet(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Bank of England balance sheet"""
        item = params.get('item', 'total_assets')

        item_map = {
            'total_assets': 'RPQB500',
            'liabilities': 'RPQB501',
            'notes_in_circulation': 'RPQB502',
            'reserve_balances': 'RPQB503'
        }

        series_code = item_map.get(item, 'RPQB500')
        return self._fetch_boe_data(series_code, params)

    def _get_term_funding_scheme(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Term Funding Scheme data"""
        return self._fetch_boe_data('RPQB775', params)

    # ==================== HISTORICAL DATA ====================

    def _get_historical_bank_rate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical Bank Rate from 1694"""
        params['datefrom'] = params.get('datefrom', '1694-01-01')
        return self._fetch_boe_data('IUDBEDR', params)

    def _get_historical_exchange_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical exchange rates"""
        params['datefrom'] = params.get('datefrom', '1975-01-01')
        return self._get_sterling_exchange_rates(params)

    def _get_historical_inflation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical inflation data"""
        params['datefrom'] = params.get('datefrom', '1988-01-01')
        return self._get_inflation_data(params)

    def _get_long_run_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get long-run economic data (centuries)"""
        dataset = params.get('dataset', 'interest_rates')

        dataset_map = {
            'interest_rates': 'IUDBEDR',
            'prices': 'CDKO',
            'gdp': 'ABMI',
            'money_supply': 'LPMAUYM'
        }

        series_code = dataset_map.get(dataset, 'IUDBEDR')
        historical_params = params.copy()
        historical_params['datefrom'] = params.get('datefrom', '1694-01-01')

        return self._fetch_boe_data(series_code, historical_params)

    # ==================== PAYMENT SYSTEMS ====================

    def _get_chaps_volumes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get CHAPS payment system volumes"""
        return self._fetch_boe_data('RPQZ3GA', params)

    def _get_faster_payments(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Faster Payments Service statistics"""
        return self._fetch_boe_data('RPQZ3GC', params)

    def _get_rtgs_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get RTGS (Real-Time Gross Settlement) statistics"""
        return self._fetch_boe_data('RPQZ3GB', params)

    def _get_payment_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get payment system statistics"""
        system = params.get('system', 'all')

        if system == 'all':
            return {
                "chaps": self._fetch_boe_data('RPQZ3GA', {'limit': 1}),
                "faster_payments": self._fetch_boe_data('RPQZ3GC', {'limit': 1}),
                "rtgs": self._fetch_boe_data('RPQZ3GB', {'limit': 1})
            }
        elif system == 'chaps':
            return self._get_chaps_volumes(params)
        elif system == 'faster_payments':
            return self._get_faster_payments(params)
        else:
            return self._get_rtgs_statistics(params)

    # ==================== BREXIT & EU ====================

    def _get_brexit_uncertainty_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Brexit uncertainty index"""
        return {
            "message": "Brexit uncertainty indicators available",
            "source": "Bank of England analysis and external indices"
        }

    def _get_eu_trade_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get EU trade statistics"""
        return self._fetch_boe_data('LPMB9T4', params)

    def _get_financial_services_trade(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get financial services trade statistics"""
        return self._fetch_boe_data('IKBD', params)

    # ==================== CLIMATE & ESG ====================

    def _get_climate_risk_indicators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get climate-related financial risk indicators"""
        return {
            "message": "Climate risk indicators under development",
            "source": "Bank of England climate stress testing"
        }

    def _get_green_bonds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get green bond issuance and holdings"""
        return {
            "message": "Green bond data available",
            "source": "Bank of England and market sources"
        }

    def _get_transition_indicators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get climate transition risk indicators"""
        return {
            "message": "Climate transition indicators in development",
            "source": "Bank of England climate scenario analysis"
        }

    # ==================== SEARCH & METADATA ====================

    def _search_series(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for Bank of England data series"""
        search_term = params.get('search_term', '')

        return {
            "message": "Search Bank of England Interactive Database",
            "search_term": search_term,
            "url": "https://www.bankofengland.co.uk/boeapps/database/"
        }

    def _get_series_metadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get metadata for specific series"""
        series_code = params.get('series_code', '')

        if not series_code:
            return {"error": "Series code required"}

        return self._fetch_boe_data(series_code, {'limit': 1})

    def _get_data_availability(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about data availability"""
        return {
            "database": "Bank of England Interactive Database",
            "url": "https://www.bankofengland.co.uk/boeapps/database/",
            "update_frequency": "Various (daily to annual)",
            "historical_data": "Some series available from 1694",
            "real_time": "Key rates and market data updated daily"
        }