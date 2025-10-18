"""
European Central Bank MCP Tool implementation with comprehensive capabilities
"""
import os
import requests
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base_mcp_tool import BaseMCPTool


class ECBMCPTool(BaseMCPTool):
    """Comprehensive MCP Tool for European Central Bank data operations"""

    def _initialize(self):
        """Initialize ECB specific components"""
        # ECB Statistical Data Warehouse API
        self.sdw_base_url = "https://sdw-wsrest.ecb.europa.eu/service"
        # ECB Data Portal API
        self.data_base_url = "https://data.ecb.europa.eu/api/v1"

        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ECB tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            # Comprehensive tool method mapping
            tool_methods = {
                # Monetary Policy & Interest Rates
                "get_key_interest_rates": self._get_key_interest_rates,
                "get_deposit_facility_rate": self._get_deposit_facility_rate,
                "get_main_refinancing_rate": self._get_main_refinancing_rate,
                "get_marginal_lending_rate": self._get_marginal_lending_rate,
                "get_euribor": self._get_euribor,
                "get_eonia": self._get_eonia,
                "get_ester": self._get_ester,
                "get_money_market_rates": self._get_money_market_rates,
                "get_yield_curves": self._get_yield_curves,
                "get_forward_rates": self._get_forward_rates,

                # Economic Indicators
                "get_hicp_inflation": self._get_hicp_inflation,
                "get_core_inflation": self._get_core_inflation,
                "get_gdp_data": self._get_gdp_data,
                "get_unemployment": self._get_unemployment,
                "get_industrial_production": self._get_industrial_production,
                "get_retail_sales": self._get_retail_sales,
                "get_confidence_indicators": self._get_confidence_indicators,
                "get_pmi_data": self._get_pmi_data,
                "get_economic_sentiment": self._get_economic_sentiment,

                # Exchange Rates
                "get_euro_exchange_rates": self._get_euro_exchange_rates,
                "get_effective_exchange_rates": self._get_effective_exchange_rates,
                "get_reference_rates": self._get_reference_rates,
                "get_currency_cross_rates": self._get_currency_cross_rates,
                "get_exchange_rate_statistics": self._get_exchange_rate_statistics,

                # Government Securities & Bonds
                "get_government_bond_yields": self._get_government_bond_yields,
                "get_sovereign_spreads": self._get_sovereign_spreads,
                "get_yield_curve_euro_area": self._get_yield_curve_euro_area,
                "get_aaa_rated_bonds": self._get_aaa_rated_bonds,
                "get_corporate_bond_yields": self._get_corporate_bond_yields,
                "get_covered_bonds": self._get_covered_bonds,

                # Banking & Financial System
                "get_bank_balance_sheets": self._get_bank_balance_sheets,
                "get_bank_lending_rates": self._get_bank_lending_rates,
                "get_bank_deposit_rates": self._get_bank_deposit_rates,
                "get_bank_lending_survey": self._get_bank_lending_survey,
                "get_monetary_aggregates": self._get_monetary_aggregates,
                "get_credit_growth": self._get_credit_growth,
                "get_npl_ratios": self._get_npl_ratios,
                "get_bank_profitability": self._get_bank_profitability,

                # Financial Markets
                "get_equity_indices": self._get_equity_indices,
                "get_stock_market_data": self._get_stock_market_data,
                "get_volatility_indices": self._get_volatility_indices,
                "get_derivatives_statistics": self._get_derivatives_statistics,
                "get_securities_issues": self._get_securities_issues,

                # Payment Systems & Market Infrastructure
                "get_target2_statistics": self._get_target2_statistics,
                "get_payment_statistics": self._get_payment_statistics,
                "get_securities_settlement": self._get_securities_settlement,
                "get_money_market_turnover": self._get_money_market_turnover,

                # Country-Specific Data
                "get_country_inflation": self._get_country_inflation,
                "get_country_gdp": self._get_country_gdp,
                "get_country_unemployment": self._get_country_unemployment,
                "get_country_debt": self._get_country_debt,
                "get_country_deficit": self._get_country_deficit,
                "get_country_current_account": self._get_country_current_account,

                # Labor Market
                "get_employment_data": self._get_employment_data,
                "get_wage_growth": self._get_wage_growth,
                "get_unit_labor_costs": self._get_unit_labor_costs,
                "get_productivity": self._get_productivity,
                "get_job_vacancies": self._get_job_vacancies,

                # Trade & Balance of Payments
                "get_trade_balance": self._get_trade_balance,
                "get_exports": self._get_exports,
                "get_imports": self._get_imports,
                "get_current_account": self._get_current_account,
                "get_foreign_direct_investment": self._get_foreign_direct_investment,
                "get_portfolio_investment": self._get_portfolio_investment,

                # Housing & Real Estate
                "get_house_prices": self._get_house_prices,
                "get_residential_property": self._get_residential_property,
                "get_commercial_property": self._get_commercial_property,
                "get_construction_output": self._get_construction_output,
                "get_building_permits": self._get_building_permits,

                # Fiscal Policy
                "get_government_debt": self._get_government_debt,
                "get_budget_balance": self._get_budget_balance,
                "get_government_expenditure": self._get_government_expenditure,
                "get_tax_revenue": self._get_tax_revenue,

                # Financial Stability
                "get_systemic_risk_indicators": self._get_systemic_risk_indicators,
                "get_financial_stress_index": self._get_financial_stress_index,
                "get_macroprudential_measures": self._get_macroprudential_measures,
                "get_banking_supervision_data": self._get_banking_supervision_data,

                # Surveys & Expectations
                "get_survey_of_professional_forecasters": self._get_survey_of_professional_forecasters,
                "get_consumer_expectations": self._get_consumer_expectations,
                "get_inflation_expectations": self._get_inflation_expectations,
                "get_business_expectations": self._get_business_expectations,

                # Climate & Sustainable Finance
                "get_green_bonds": self._get_green_bonds,
                "get_climate_indicators": self._get_climate_indicators,
                "get_sustainable_finance_data": self._get_sustainable_finance_data,

                # Historical Data & Research
                "get_historical_statistics": self._get_historical_statistics,
                "get_long_term_statistics": self._get_long_term_statistics,
                "search_series": self._search_series,
                "get_series_metadata": self._get_series_metadata
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

    def _fetch_ecb_data(self, dataset: str, series_key: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Centralized ECB Statistical Data Warehouse fetching"""
        try:
            # Build URL for data retrieval
            url = f"{self.sdw_base_url}/data/{dataset}/{series_key}"

            # Build query parameters
            query_params = {
                'format': 'jsondata',
                'detail': params.get('detail', 'dataonly')
            }

            if params.get('startPeriod'):
                query_params['startPeriod'] = params['startPeriod']
            if params.get('endPeriod'):
                query_params['endPeriod'] = params['endPeriod']
            if params.get('lastNObservations'):
                query_params['lastNObservations'] = params['lastNObservations']

            response = requests.get(url, params=query_params, headers=self.headers)

            if response.status_code != 200:
                return {"error": f"API request failed with status {response.status_code}"}

            data = response.json()

            # Parse observations
            observations = []
            if 'dataSets' in data and data['dataSets']:
                dataset_data = data['dataSets'][0]
                if 'series' in dataset_data:
                    for series_data in dataset_data['series'].values():
                        if 'observations' in series_data:
                            for obs_key, obs_values in series_data['observations'].items():
                                observations.append({
                                    'period': self._get_period_from_index(obs_key, data),
                                    'value': obs_values[0] if obs_values else None
                                })

            # Sort observations by date
            observations.sort(key=lambda x: x['period'], reverse=True)

            # Get metadata
            metadata = {}
            if 'structure' in data:
                structure = data['structure']
                if 'name' in structure:
                    metadata['name'] = structure['name']
                if 'dimensions' in structure:
                    metadata['dimensions'] = structure['dimensions']

            # Calculate changes
            changes = []
            if len(observations) > 1:
                for i in range(len(observations) - 1):
                    if observations[i]['value'] and observations[i+1]['value']:
                        current = float(observations[i]['value'])
                        previous = float(observations[i+1]['value'])
                        if previous != 0:
                            change = ((current - previous) / previous) * 100
                            changes.append({
                                'period': observations[i]['period'],
                                'change_pct': round(change, 2)
                            })

            return {
                "dataset": dataset,
                "series_key": series_key,
                "metadata": metadata,
                "latest_value": observations[0]['value'] if observations else None,
                "latest_period": observations[0]['period'] if observations else None,
                "observations": observations[:params.get('limit', 30)],
                "changes": changes[:5] if changes else [],
                "count": len(observations)
            }

        except Exception as e:
            return {"error": str(e)}

    def _get_period_from_index(self, index: str, data: Dict) -> str:
        """Convert observation index to period string"""
        try:
            if 'structure' in data and 'dimensions' in data['structure']:
                dimensions = data['structure']['dimensions']
                if 'observation' in dimensions:
                    for dim in dimensions['observation']:
                        if dim['id'] == 'TIME_PERIOD' and 'values' in dim:
                            idx = int(index)
                            if idx < len(dim['values']):
                                return dim['values'][idx]['id']
            return index
        except:
            return index

    # ==================== MONETARY POLICY & INTEREST RATES ====================

    def _get_key_interest_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get ECB key interest rates"""
        # Fetch all three key rates
        rates = {}

        # Main refinancing operations
        mro = self._fetch_ecb_data('FM', 'B.U2.EUR.4F.KR.MRR_RT.LEV', {'lastNObservations': 1})
        if 'latest_value' in mro:
            rates['main_refinancing'] = mro['latest_value']

        # Deposit facility
        df = self._fetch_ecb_data('FM', 'B.U2.EUR.4F.KR.DFR.LEV', {'lastNObservations': 1})
        if 'latest_value' in df:
            rates['deposit_facility'] = df['latest_value']

        # Marginal lending facility
        mlf = self._fetch_ecb_data('FM', 'B.U2.EUR.4F.KR.MLFR.LEV', {'lastNObservations': 1})
        if 'latest_value' in mlf:
            rates['marginal_lending'] = mlf['latest_value']

        return {
            "key_rates": rates,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "description": "ECB key interest rates"
        }

    def _get_deposit_facility_rate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get ECB deposit facility rate"""
        return self._fetch_ecb_data('FM', 'B.U2.EUR.4F.KR.DFR.LEV', params)

    def _get_main_refinancing_rate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get ECB main refinancing operations rate"""
        return self._fetch_ecb_data('FM', 'B.U2.EUR.4F.KR.MRR_RT.LEV', params)

    def _get_marginal_lending_rate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get ECB marginal lending facility rate"""
        return self._fetch_ecb_data('FM', 'B.U2.EUR.4F.KR.MLFR.LEV', params)

    def _get_euribor(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get EURIBOR rates"""
        tenor = params.get('tenor', '3M')

        tenor_map = {
            '1W': 'FM.M.U2.EUR.RT.MM.EURIBOR1WD_.HSTA',
            '1M': 'FM.M.U2.EUR.RT.MM.EURIBOR1MD_.HSTA',
            '3M': 'FM.M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA',
            '6M': 'FM.M.U2.EUR.RT.MM.EURIBOR6MD_.HSTA',
            '12M': 'FM.M.U2.EUR.RT.MM.EURIBOR12MD_.HSTA'
        }

        series = tenor_map.get(tenor, 'FM.M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA')
        return self._fetch_ecb_data('FM', series, params)

    def _get_eonia(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get EONIA rate (discontinued, replaced by €STR)"""
        return {
            "message": "EONIA discontinued in January 2022, replaced by €STR",
            "alternative": "Use get_ester() for Euro short-term rate"
        }

    def _get_ester(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get €STR (Euro short-term rate)"""
        return self._fetch_ecb_data('MM', 'D.EUR.EONIAED_', params)

    def _get_money_market_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get various money market rates"""
        rate_type = params.get('rate_type', 'overnight')

        rate_map = {
            'overnight': 'D.EUR.EONIAED_',
            'tom_next': 'D.EUR.EURTND_',
            'spot_next': 'D.EUR.EURSND_',
            '1_week': 'D.EUR.EUR1WD_',
            '1_month': 'D.EUR.EUR1MD_'
        }

        series = rate_map.get(rate_type, 'D.EUR.EONIAED_')
        return self._fetch_ecb_data('MM', series, params)

    def _get_yield_curves(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Euro area yield curves"""
        curve_type = params.get('curve_type', 'spot')

        curve_map = {
            'spot': 'YC.B.U2.EUR.4F.G_N_A.SV_C_YM',
            'forward': 'YC.B.U2.EUR.4F.G_N_A.FWD_C_YM',
            'par': 'YC.B.U2.EUR.4F.G_N_A.PAR_YLD'
        }

        base_series = curve_map.get(curve_type, 'YC.B.U2.EUR.4F.G_N_A.SV_C_YM')

        # Get yields for various maturities
        maturities = ['1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']
        yields = {}

        for maturity in maturities:
            series = f"{base_series}.{maturity}"
            result = self._fetch_ecb_data('YC', series, {'lastNObservations': 1})
            if 'latest_value' in result:
                yields[maturity] = result['latest_value']

        return {
            "curve_type": curve_type,
            "yields": yields,
            "date": datetime.now().strftime('%Y-%m-%d')
        }

    def _get_forward_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get forward rates"""
        return self._get_yield_curves({**params, 'curve_type': 'forward'})

    # ==================== ECONOMIC INDICATORS ====================

    def _get_hicp_inflation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Harmonised Index of Consumer Prices (HICP)"""
        component = params.get('component', 'all_items')

        component_map = {
            'all_items': 'ICP.M.U2.N.000000.4.ANR',
            'energy': 'ICP.M.U2.N.NRG000.4.ANR',
            'food': 'ICP.M.U2.N.FOOD00.4.ANR',
            'core': 'ICP.M.U2.N.XEFOOD.4.ANR',
            'services': 'ICP.M.U2.N.SERV00.4.ANR'
        }

        series = component_map.get(component, 'ICP.M.U2.N.000000.4.ANR')
        return self._fetch_ecb_data('ICP', series, params)

    def _get_core_inflation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get core inflation (excluding energy and unprocessed food)"""
        return self._fetch_ecb_data('ICP', 'ICP.M.U2.N.XEF000.4.ANR', params)

    def _get_gdp_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Euro area GDP data"""
        gdp_type = params.get('gdp_type', 'growth_rate')

        gdp_map = {
            'growth_rate': 'MNA.Q.Y.I8.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.GY',
            'level': 'MNA.Q.Y.I8.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.V.N',
            'per_capita': 'MNA.A.N.I8.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.PS.V.N'
        }

        series = gdp_map.get(gdp_type, 'MNA.Q.Y.I8.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.GY')
        return self._fetch_ecb_data('MNA', series, params)

    def _get_unemployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Euro area unemployment rate"""
        demographic = params.get('demographic', 'total')

        demographic_map = {
            'total': 'STS.M.I8.S.UNEH.RTT000.4.000',
            'youth': 'STS.M.I8.S.UNEY.RTT000.4.000',
            'male': 'STS.M.I8.S.UNEM.RTT000.4.000',
            'female': 'STS.M.I8.S.UNEF.RTT000.4.000'
        }

        series = demographic_map.get(demographic, 'STS.M.I8.S.UNEH.RTT000.4.000')
        return self._fetch_ecb_data('STS', series, params)

    def _get_industrial_production(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get industrial production index"""
        sector = params.get('sector', 'total')

        sector_map = {
            'total': 'STS.M.I8.Y.PROD.NS0010.4.000',
            'manufacturing': 'STS.M.I8.Y.PROD.NS0020.4.000',
            'energy': 'STS.M.I8.Y.PROD.NS0030.4.000',
            'construction': 'STS.M.I8.Y.PROD.NS0040.4.000'
        }

        series = sector_map.get(sector, 'STS.M.I8.Y.PROD.NS0010.4.000')
        return self._fetch_ecb_data('STS', series, params)

    def _get_retail_sales(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get retail sales data"""
        return self._fetch_ecb_data('STS', 'STS.M.I8.Y.TOVT.NS0060.4.000', params)

    def _get_confidence_indicators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get confidence indicators"""
        indicator = params.get('indicator', 'consumer')

        indicator_map = {
            'consumer': 'BCS.M.I8.BAL.CONS.TOT.OVRL.SA',
            'business': 'BCS.M.I8.BAL.BSCI.OVRL.SA',
            'economic_sentiment': 'BCS.M.I8.IDX.ESI.OVRL.SA'
        }

        series = indicator_map.get(indicator, 'BCS.M.I8.BAL.CONS.TOT.OVRL.SA')
        return self._fetch_ecb_data('BCS', series, params)

    def _get_pmi_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Purchasing Managers' Index data"""
        pmi_type = params.get('pmi_type', 'composite')

        # Note: PMI data typically requires external data provider
        return {
            "message": "PMI data requires subscription to IHS Markit",
            "pmi_type": pmi_type,
            "alternatives": "Use confidence indicators or industrial production"
        }

    def _get_economic_sentiment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Economic Sentiment Indicator"""
        return self._fetch_ecb_data('BCS', 'BCS.M.I8.IDX.ESI.OVRL.SA', params)

    # ==================== EXCHANGE RATES ====================

    def _get_euro_exchange_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get EUR exchange rates"""
        currency = params.get('currency', 'USD')

        currency_map = {
            'USD': 'D.USD.EUR.SP00.A',
            'GBP': 'D.GBP.EUR.SP00.A',
            'JPY': 'D.JPY.EUR.SP00.A',
            'CHF': 'D.CHF.EUR.SP00.A',
            'CNY': 'D.CNY.EUR.SP00.A',
            'AUD': 'D.AUD.EUR.SP00.A',
            'CAD': 'D.CAD.EUR.SP00.A'
        }

        series = currency_map.get(currency, 'D.USD.EUR.SP00.A')
        return self._fetch_ecb_data('EXR', series, params)

    def _get_effective_exchange_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Euro effective exchange rates"""
        eer_type = params.get('eer_type', 'nominal')

        eer_map = {
            'nominal': 'M.I8.N.EN00.EUE.A',
            'real_cpi': 'M.I8.R.RC00.EUE.A',
            'real_ppi': 'M.I8.R.RP00.EUE.A'
        }

        series = eer_map.get(eer_type, 'M.I8.N.EN00.EUE.A')
        return self._fetch_ecb_data('EXR', series, params)

    def _get_reference_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get ECB reference exchange rates"""
        # Get multiple reference rates
        currencies = ['USD', 'GBP', 'JPY', 'CHF']
        rates = {}

        for currency in currencies:
            series = f'D.{currency}.EUR.SP00.A'
            result = self._fetch_ecb_data('EXR', series, {'lastNObservations': 1})
            if 'latest_value' in result:
                rates[currency] = result['latest_value']

        return {
            "reference_rates": rates,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "description": "ECB reference exchange rates"
        }

    def _get_currency_cross_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get cross rates between major currencies"""
        cross = params.get('cross', 'GBP_USD')

        # ECB provides some cross rates directly
        cross_map = {
            'GBP_USD': 'D.USD.GBP.SP00.A',
            'USD_JPY': 'D.JPY.USD.SP00.A',
            'GBP_JPY': 'D.JPY.GBP.SP00.A'
        }

        series = cross_map.get(cross, 'D.USD.GBP.SP00.A')
        return self._fetch_ecb_data('EXR', series, params)

    def _get_exchange_rate_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get exchange rate statistics and volatility"""
        currency = params.get('currency', 'USD')

        # Get historical data for volatility calculation
        series = f'D.{currency}.EUR.SP00.A'
        return self._fetch_ecb_data('EXR', series, params)

    # ==================== GOVERNMENT SECURITIES & BONDS ====================

    def _get_government_bond_yields(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get government bond yields for Euro area countries"""
        country = params.get('country', 'DE')
        maturity = params.get('maturity', '10Y')

        # Map country and maturity to series
        series = f'IRS.M.{country}.L.L40.CI.{maturity}.EUR.N.Z'
        return self._fetch_ecb_data('IRS', series, params)

    def _get_sovereign_spreads(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get sovereign spreads vs German Bunds"""
        country = params.get('country', 'IT')

        # Get German and other country yields
        de_yield = self._fetch_ecb_data('IRS', 'IRS.M.DE.L.L40.CI.10Y.EUR.N.Z', {'lastNObservations': 1})
        country_yield = self._fetch_ecb_data('IRS', f'IRS.M.{country}.L.L40.CI.10Y.EUR.N.Z', {'lastNObservations': 1})

        spread = None
        if 'latest_value' in de_yield and 'latest_value' in country_yield:
            spread = float(country_yield['latest_value']) - float(de_yield['latest_value'])

        return {
            "country": country,
            "spread_vs_bund": spread,
            "german_yield": de_yield.get('latest_value'),
            "country_yield": country_yield.get('latest_value'),
            "date": de_yield.get('latest_period')
        }

    def _get_yield_curve_euro_area(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Euro area AAA-rated yield curve"""
        maturities = ['3M', '6M', '1Y', '2Y', '3Y', '5Y', '7Y', '10Y', '20Y', '30Y']
        yields = {}

        for maturity in maturities:
            series = f'YC.B.U2.EUR.4F.G_N_A.SV_C_YM.{maturity}'
            result = self._fetch_ecb_data('YC', series, {'lastNObservations': 1})
            if 'latest_value' in result:
                yields[maturity] = result['latest_value']

        return {
            "yield_curve": yields,
            "rating": "AAA",
            "date": datetime.now().strftime('%Y-%m-%d')
        }

    def _get_aaa_rated_bonds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get AAA-rated Euro area government bonds"""
        maturity = params.get('maturity', '10Y')
        series = f'YC.B.U2.EUR.4F.G_N_A.SV_C_YM.{maturity}'
        return self._fetch_ecb_data('YC', series, params)

    def _get_corporate_bond_yields(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get corporate bond yields"""
        rating = params.get('rating', 'AA')

        rating_map = {
            'AAA': 'FM.M.U2.EUR.4F.BB.AAA.DEI',
            'AA': 'FM.M.U2.EUR.4F.BB.AA.DEI',
            'A': 'FM.M.U2.EUR.4F.BB.A.DEI',
            'BBB': 'FM.M.U2.EUR.4F.BB.BBB.DEI'
        }

        series = rating_map.get(rating, 'FM.M.U2.EUR.4F.BB.AA.DEI')
        return self._fetch_ecb_data('FM', series, params)

    def _get_covered_bonds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get covered bond yields"""
        return self._fetch_ecb_data('FM', 'FM.M.U2.EUR.4F.CB.DFR.LEV', params)

    # ==================== BANKING & FINANCIAL SYSTEM ====================

    def _get_bank_balance_sheets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get aggregated bank balance sheet data"""
        item = params.get('item', 'total_assets')

        item_map = {
            'total_assets': 'BSI.M.U2.N.A.A20.A.1.U2.2100.Z01.E',
            'loans': 'BSI.M.U2.N.A.A20.A.4.U2.2100.Z01.E',
            'deposits': 'BSI.M.U2.N.A.L20.L.1.U2.2100.Z01.E',
            'equity': 'BSI.M.U2.N.A.L30.F.1.U2.2100.Z01.E'
        }

        series = item_map.get(item, 'BSI.M.U2.N.A.A20.A.1.U2.2100.Z01.E')
        return self._fetch_ecb_data('BSI', series, params)

    def _get_bank_lending_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get bank lending rates"""
        loan_type = params.get('loan_type', 'corporate')

        loan_map = {
            'corporate': 'MIR.M.U2.B.L22.F.R.A.2240.EUR.N',
            'household_mortgage': 'MIR.M.U2.B.L23.F.R.A.2250.EUR.N',
            'consumer': 'MIR.M.U2.B.L23.F.R.A.2255.EUR.N'
        }

        series = loan_map.get(loan_type, 'MIR.M.U2.B.L22.F.R.A.2240.EUR.N')
        return self._fetch_ecb_data('MIR', series, params)

    def _get_bank_deposit_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get bank deposit rates"""
        deposit_type = params.get('deposit_type', 'household')

        deposit_map = {
            'household': 'MIR.M.U2.B.L21.F.R.A.2230.EUR.N',
            'corporate': 'MIR.M.U2.B.L22.F.R.A.2240.EUR.N',
            'overnight': 'MIR.M.U2.B.L21.D.R.A.2210.EUR.N'
        }

        series = deposit_map.get(deposit_type, 'MIR.M.U2.B.L21.F.R.A.2230.EUR.N')
        return self._fetch_ecb_data('MIR', series, params)

    def _get_bank_lending_survey(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Bank Lending Survey results"""
        indicator = params.get('indicator', 'credit_standards')

        indicator_map = {
            'credit_standards': 'BLS.Q.U2.ALL.Z.H.H.C.E.Z.B3.ST.S.BWNET',
            'demand': 'BLS.Q.U2.ALL.Z.H.H.C.E.Z.B3.DM.S.BWNET',
            'terms_conditions': 'BLS.Q.U2.ALL.Z.H.H.C.E.Z.B3.TC.S.BWNET'
        }

        series = indicator_map.get(indicator, 'BLS.Q.U2.ALL.Z.H.H.C.E.Z.B3.ST.S.BWNET')
        return self._fetch_ecb_data('BLS', series, params)

    def _get_monetary_aggregates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get monetary aggregates (M1, M2, M3)"""
        aggregate = params.get('aggregate', 'M3')

        aggregate_map = {
            'M1': 'BSI.M.U2.Y.V.M10.X.I.U2.2100.Z01.A',
            'M2': 'BSI.M.U2.Y.V.M20.X.I.U2.2100.Z01.A',
            'M3': 'BSI.M.U2.Y.V.M30.X.I.U2.2100.Z01.A'
        }

        series = aggregate_map.get(aggregate, 'BSI.M.U2.Y.V.M30.X.I.U2.2100.Z01.A')
        return self._fetch_ecb_data('BSI', series, params)

    def _get_credit_growth(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get credit growth to private sector"""
        sector = params.get('sector', 'total')

        sector_map = {
            'total': 'BSI.M.U2.N.A.A20.A.I.U2.2100.Z01.A',
            'households': 'BSI.M.U2.N.A.A20.A.I.U2.2250.Z01.A',
            'corporations': 'BSI.M.U2.N.A.A20.A.I.U2.2240.Z01.A'
        }

        series = sector_map.get(sector, 'BSI.M.U2.N.A.A20.A.I.U2.2100.Z01.A')
        return self._fetch_ecb_data('BSI', series, params)

    def _get_npl_ratios(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get non-performing loans ratios"""
        return self._fetch_ecb_data('CBD2', 'CBD2.Q.U2.W0.67._T._T.A.F.R.F._T.F._T.F.Q.P', params)

    def _get_bank_profitability(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get bank profitability indicators"""
        indicator = params.get('indicator', 'roe')

        indicator_map = {
            'roe': 'CBD2.A.U2.W0.67._T._T.A.F.R310._T.F._T.F.Q.P',
            'roa': 'CBD2.A.U2.W0.67._T._T.A.F.R320._T.F._T.F.Q.P',
            'cost_income': 'CBD2.A.U2.W0.67._T._T.A.F.R420._T.F._T.F.Q.P'
        }

        series = indicator_map.get(indicator, 'CBD2.A.U2.W0.67._T._T.A.F.R310._T.F._T.F.Q.P')
        return self._fetch_ecb_data('CBD2', series, params)

    # ==================== FINANCIAL MARKETS ====================

    def _get_equity_indices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Euro area equity indices"""
        index = params.get('index', 'eurostoxx50')

        index_map = {
            'eurostoxx50': 'FM.M.U2.EUR.DS.EI.DJEUTOT.HSTA',
            'eurostoxx600': 'FM.M.U2.EUR.DS.EI.DJES600.HSTA',
            'dax': 'FM.M.DE.EUR.DS.EI.DAXINDX.HSTA',
            'cac40': 'FM.M.FR.EUR.DS.EI.FRCAC40.HSTA',
            'ftse_mib': 'FM.M.IT.EUR.DS.EI.FTMIB.HSTA'
        }

        series = index_map.get(index, 'FM.M.U2.EUR.DS.EI.DJEUTOT.HSTA')
        return self._fetch_ecb_data('FM', series, params)

    def _get_stock_market_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get stock market data"""
        market = params.get('market', 'euro_area')

        market_map = {
            'euro_area': 'FM.M.U2.EUR.DS.EI.DJES600.HSTA',
            'germany': 'FM.M.DE.EUR.DS.EI.DAXINDX.HSTA',
            'france': 'FM.M.FR.EUR.DS.EI.FRCAC40.HSTA',
            'italy': 'FM.M.IT.EUR.DS.EI.FTMIB.HSTA',
            'spain': 'FM.M.ES.EUR.DS.EI.IBEX35.HSTA'
        }

        series = market_map.get(market, 'FM.M.U2.EUR.DS.EI.DJES600.HSTA')
        return self._fetch_ecb_data('FM', series, params)

    def _get_volatility_indices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get volatility indices"""
        index = params.get('index', 'vstoxx')

        # VSTOXX is the European volatility index
        return {
            "index": index,
            "message": "VSTOXX and other volatility indices available from market data providers",
            "alternative": "Use equity market data for volatility calculations"
        }

    def _get_derivatives_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get derivatives market statistics"""
        return self._fetch_ecb_data('SEC', 'SEC.M.U2.THS.A.A.A.A.Z.Z.Z.Z.Z', params)

    def _get_securities_issues(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get securities issuance data"""
        security_type = params.get('security_type', 'bonds')

        security_map = {
            'bonds': 'SEC.M.U2.THS.A.A.A.A.Z.Z.Z.Z.Z',
            'equities': 'SEC.M.U2.THS.E.A.A.A.Z.Z.Z.Z.Z',
            'short_term': 'SEC.M.U2.THS.S.A.A.A.Z.Z.Z.Z.Z'
        }

        series = security_map.get(security_type, 'SEC.M.U2.THS.A.A.A.A.Z.Z.Z.Z.Z')
        return self._fetch_ecb_data('SEC', series, params)

    # ==================== PAYMENT SYSTEMS & MARKET INFRASTRUCTURE ====================

    def _get_target2_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get TARGET2 payment system statistics"""
        return self._fetch_ecb_data('PSS', 'PSS.A.I8.T2.N.V.Z01.X', params)

    def _get_payment_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get payment system statistics"""
        return self._fetch_ecb_data('PSS', 'PSS.A.I8.LVPS.N.T.Z01.X', params)

    def _get_securities_settlement(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get securities settlement statistics"""
        return self._fetch_ecb_data('SSS', 'SSS.A.I8.T2S.N.V.Z01.X', params)

    def _get_money_market_turnover(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get money market turnover data"""
        return self._fetch_ecb_data('MM', 'MM.M.U2.EUR.V.M.MMTO', params)

    # ==================== COUNTRY-SPECIFIC DATA ====================

    def _get_country_inflation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get inflation data for specific Euro area country"""
        country = params.get('country', 'DE')
        series = f'ICP.M.{country}.N.000000.4.ANR'
        return self._fetch_ecb_data('ICP', series, params)

    def _get_country_gdp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get GDP data for specific Euro area country"""
        country = params.get('country', 'DE')
        series = f'MNA.Q.Y.{country}.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.GY'
        return self._fetch_ecb_data('MNA', series, params)

    def _get_country_unemployment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get unemployment rate for specific Euro area country"""
        country = params.get('country', 'DE')
        series = f'STS.M.{country}.S.UNEH.RTT000.4.000'
        return self._fetch_ecb_data('STS', series, params)

    def _get_country_debt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get government debt for specific Euro area country"""
        country = params.get('country', 'DE')
        series = f'GFS.Q.N.{country}.W0.S13.S1.N.D.D._Z._Z._Z.XDC_R_B1GQ_CY._Z.S.V.CY._T'
        return self._fetch_ecb_data('GFS', series, params)

    def _get_country_deficit(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get government deficit for specific Euro area country"""
        country = params.get('country', 'DE')
        series = f'GFS.Q.N.{country}.W0.S13.S1.N.B.B9._Z._Z._Z.XDC_R_B1GQ_CY._Z.S.V.CY._T'
        return self._fetch_ecb_data('GFS', series, params)

    def _get_country_current_account(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current account for specific Euro area country"""
        country = params.get('country', 'DE')
        series = f'BP6.M.N.{country}.W1.S1.S1.T.B.CA._Z._Z._Z.EUR._T._X.N'
        return self._fetch_ecb_data('BP6', series, params)

    # ==================== LABOR MARKET ====================

    def _get_employment_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Euro area employment data"""
        return self._fetch_ecb_data('LFSI', 'LFSI.M.I8.S.UNEHRT.TOTAL.TOTAL', params)

    def _get_wage_growth(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get wage growth data"""
        return self._fetch_ecb_data('MNA', 'MNA.Q.Y.I8.W0.S1.S1.D.D1._Z._T._Z.EUR_HW.LR.N', params)

    def _get_unit_labor_costs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get unit labor costs"""
        return self._fetch_ecb_data('MNA', 'MNA.Q.Y.I8.W2.S1.S1.D.TULC._Z._T._Z.IX.LR.N', params)

    def _get_productivity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get labor productivity data"""
        return self._fetch_ecb_data('MNA', 'MNA.Q.Y.I8.W2.S1.S1._Z.LPR_HW._Z._T._Z.EUR_HW.LR.N', params)

    def _get_job_vacancies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get job vacancy rate"""
        return self._fetch_ecb_data('LFSI', 'LFSI.Q.I8.S.JOBVAC.RT.TOTAL', params)

    # ==================== TRADE & BALANCE OF PAYMENTS ====================

    def _get_trade_balance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get trade balance data"""
        return self._fetch_ecb_data('BP6', 'BP6.M.N.I8.W1.S1.S1.T.B.G._Z._Z._Z.EUR._T._X.N', params)

    def _get_exports(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get export data"""
        return self._fetch_ecb_data('BP6', 'BP6.M.N.I8.W1.S1.S1.T.C.G._Z._Z._Z.EUR._T._X.N', params)

    def _get_imports(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get import data"""
        return self._fetch_ecb_data('BP6', 'BP6.M.N.I8.W1.S1.S1.T.D.G._Z._Z._Z.EUR._T._X.N', params)

    def _get_current_account(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current account balance"""
        return self._fetch_ecb_data('BP6', 'BP6.M.N.I8.W1.S1.S1.T.B.CA._Z._Z._Z.EUR._T._X.N', params)

    def _get_foreign_direct_investment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get foreign direct investment data"""
        return self._fetch_ecb_data('BP6', 'BP6.M.N.I8.W1.S1.S1.T.A.FA.D.F._Z._Z._Z.EUR._T._X.N', params)

    def _get_portfolio_investment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get portfolio investment data"""
        return self._fetch_ecb_data('BP6', 'BP6.M.N.I8.W1.S1.S1.T.A.FA.P.F._Z._Z._Z.EUR._T._X.N', params)

    # ==================== HOUSING & REAL ESTATE ====================

    def _get_house_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get house price indices"""
        return self._fetch_ecb_data('RPP', 'RPP.Q.I8.N.TD.00.3.00', params)

    def _get_residential_property(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get residential property price indices"""
        return self._fetch_ecb_data('RPP', 'RPP.Q.I8.N.TD.RE.3.00', params)

    def _get_commercial_property(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get commercial property price indices"""
        return self._fetch_ecb_data('CPP', 'CPP.Q.I8.N.IT.RE.3.00', params)

    def _get_construction_output(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get construction output data"""
        return self._fetch_ecb_data('STS', 'STS.M.I8.Y.PROD.2C3000.4.000', params)

    def _get_building_permits(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get building permits data"""
        return self._fetch_ecb_data('STS', 'STS.Q.I8.Y.BPEM.2C3000.4.000', params)

    # ==================== FISCAL POLICY ====================

    def _get_government_debt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get government debt statistics"""
        return self._fetch_ecb_data('GFS', 'GFS.Q.N.I8.W0.S13.S1.N.D.D._Z._Z._Z.XDC_R_B1GQ_CY._Z.S.V.CY._T', params)

    def _get_budget_balance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get government budget balance"""
        return self._fetch_ecb_data('GFS', 'GFS.Q.N.I8.W0.S13.S1.N.B.B9._Z._Z._Z.XDC_R_B1GQ_CY._Z.S.V.CY._T', params)

    def _get_government_expenditure(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get government expenditure data"""
        return self._fetch_ecb_data('GFS', 'GFS.Q.N.I8.W0.S13.S1.P.D.D._Z._Z._T.XDC_R_B1GQ_CY._Z.S.V.CY._T', params)

    def _get_tax_revenue(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get tax revenue data"""
        return self._fetch_ecb_data('GFS', 'GFS.Q.N.I8.W0.S13.S1.N.R.D2._Z._Z._Z.XDC_R_B1GQ_CY._Z.S.V.CY._T', params)

    # ==================== FINANCIAL STABILITY ====================

    def _get_systemic_risk_indicators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get systemic risk indicators"""
        return {
            "indicators": [
                "Credit-to-GDP gap",
                "House price gaps",
                "Bank leverage",
                "Interconnectedness"
            ],
            "source": "ECB Financial Stability Review"
        }

    def _get_financial_stress_index(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get financial stress index"""
        return self._fetch_ecb_data('CISS', 'CISS.D.U2.Z0Z.4F.EC.SS_CI.IDX', params)

    def _get_macroprudential_measures(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get macroprudential policy measures"""
        return {
            "measures": [
                "Countercyclical capital buffer",
                "Systemic risk buffer",
                "O-SII buffers"
            ],
            "source": "ECB Macroprudential Database"
        }

    def _get_banking_supervision_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get banking supervision statistics"""
        return {
            "message": "Banking supervision data available from SSM",
            "source": "ECB Single Supervisory Mechanism"
        }

    # ==================== SURVEYS & EXPECTATIONS ====================

    def _get_survey_of_professional_forecasters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Survey of Professional Forecasters results"""
        variable = params.get('variable', 'inflation')

        variable_map = {
            'inflation': 'SPF.Q.U2.HICP.POINT.1Y.GROWTH',
            'gdp': 'SPF.Q.U2.RGDP.POINT.1Y.GROWTH',
            'unemployment': 'SPF.Q.U2.UNEM.POINT.1Y.LEVEL'
        }

        series = variable_map.get(variable, 'SPF.Q.U2.HICP.POINT.1Y.GROWTH')
        return self._fetch_ecb_data('SPF', series, params)

    def _get_consumer_expectations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get consumer expectations survey data"""
        return self._fetch_ecb_data('CES', 'CES.M.I8.HICP.EXP_12M.MEDIAN', params)

    def _get_inflation_expectations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get inflation expectations from various sources"""
        source = params.get('source', 'market')

        if source == 'market':
            # Market-based inflation expectations (5y5y forward)
            return self._fetch_ecb_data('ILS', 'ILS.M.U2.C.L0502.CP.E5Y5Y', params)
        else:
            # Survey-based expectations
            return self._get_survey_of_professional_forecasters({'variable': 'inflation'})

    def _get_business_expectations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get business expectations data"""
        return self._fetch_ecb_data('BCS', 'BCS.M.I8.BAL.EMP.EX3M.OVRL.SA', params)

    # ==================== CLIMATE & SUSTAINABLE FINANCE ====================

    def _get_green_bonds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get green bond statistics"""
        return {
            "message": "Green bond data available from ECB Data Portal",
            "source": "ECB Sustainable Finance Statistics"
        }

    def _get_climate_indicators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get climate-related financial indicators"""
        return {
            "indicators": [
                "Carbon intensity",
                "Green bond issuance",
                "Climate stress test results"
            ],
            "source": "ECB Climate Change Centre"
        }

    def _get_sustainable_finance_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get sustainable finance data"""
        return {
            "message": "Sustainable finance statistics under development",
            "source": "ECB Sustainable Finance initiatives"
        }

    # ==================== HISTORICAL DATA & RESEARCH ====================

    def _get_historical_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical economic statistics"""
        series = params.get('series', '')
        dataset = params.get('dataset', '')

        if not series or not dataset:
            return {"error": "Series and dataset required"}

        # Add historical data retrieval
        historical_params = params.copy()
        if 'startPeriod' not in historical_params:
            historical_params['startPeriod'] = '1999-01'  # Euro introduction

        return self._fetch_ecb_data(dataset, series, historical_params)

    def _get_long_term_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get long-term statistical series"""
        series_type = params.get('series_type', 'interest_rates')

        series_map = {
            'interest_rates': ('FM', 'B.U2.EUR.4F.KR.MRR_RT.LEV'),
            'inflation': ('ICP', 'ICP.M.U2.N.000000.4.ANR'),
            'gdp': ('MNA', 'MNA.Q.Y.I8.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.V.N'),
            'unemployment': ('STS', 'STS.M.I8.S.UNEH.RTT000.4.000')
        }

        if series_type in series_map:
            dataset, series = series_map[series_type]
            params['startPeriod'] = params.get('startPeriod', '1999-01')
            return self._fetch_ecb_data(dataset, series, params)

        return {"error": f"Unknown series type: {series_type}"}

    def _search_series(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for ECB data series"""
        search_term = params.get('search_term', '')

        return {
            "message": "Search ECB Statistical Data Warehouse",
            "search_term": search_term,
            "url": "https://sdw.ecb.europa.eu/"
        }

    def _get_series_metadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get metadata for specific series"""
        dataset = params.get('dataset', '')
        series_key = params.get('series_key', '')

        if not dataset or not series_key:
            return {"error": "Dataset and series_key required"}

        # Get metadata by fetching with detail parameter
        params_with_metadata = params.copy()
        params_with_metadata['detail'] = 'full'
        params_with_metadata['lastNObservations'] = 1

        return self._fetch_ecb_data(dataset, series_key, params_with_metadata)