"""
Federal Reserve MCP Tool implementation
"""
import os
import requests
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .base_mcp_tool import BaseMCPTool


class FedReserveMCPTool(BaseMCPTool):
    """MCP Tool for Federal Reserve data operations"""

    def _initialize(self):
        """Initialize Fed Reserve specific components"""
        self.api_key = os.environ.get('FRED_API_KEY', '')  # Federal Reserve Economic Data API
        self.fred_base_url = "https://api.stlouisfed.org/fred"

        if not self.api_key:
            print("Warning: FRED_API_KEY not set. Limited functionality available.")

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Federal Reserve tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            tool_methods = {
                "get_interest_rates": self._get_interest_rates,
                "get_economic_series": self._get_economic_series,
                "get_gdp_data": self._get_gdp_data,
                "get_inflation_data": self._get_inflation_data,
                "get_unemployment_data": self._get_unemployment_data,
                "get_money_supply": self._get_money_supply,
                "get_treasury_yields": self._get_treasury_yields,
                "search_series": self._search_series,
                "get_fomc_statements": self._get_fomc_statements,
                "get_banking_statistics": self._get_banking_statistics
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

    def _get_interest_rates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Federal interest rates"""
        rate_type = params.get('rate_type', 'federal_funds')  # federal_funds, prime, discount

        series_map = {
            'federal_funds': 'DFF',  # Federal Funds Rate
            'prime': 'DPRIME',  # Bank Prime Loan Rate
            'discount': 'INTDSRUSM193N'  # Discount Rate
        }

        series_id = series_map.get(rate_type, 'DFF')

        if self.api_key:
            try:
                url = f"{self.fred_base_url}/series/observations"
                api_params = {
                    'series_id': series_id,
                    'api_key': self.api_key,
                    'file_type': 'json',
                    'limit': params.get('limit', 30),
                    'sort_order': 'desc'
                }

                response = requests.get(url, params=api_params)
                if response.status_code == 200:
                    data = response.json()
                    observations = data.get('observations', [])

                    return {
                        "rate_type": rate_type,
                        "series_id": series_id,
                        "unit": data.get('units', 'Percent'),
                        "latest_rate": observations[0].get('value') if observations else None,
                        "latest_date": observations[0].get('date') if observations else None,
                        "observations": observations[:10]  # Last 10 observations
                    }
            except Exception as e:
                return {"error": str(e)}

        return {"error": "FRED API key required for this operation"}

    def _get_economic_series(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get any economic series data"""
        series_id = params.get('series_id', '')
        start_date = params.get('start_date', '')
        end_date = params.get('end_date', '')

        if not series_id:
            return {"error": "Series ID is required"}

        if self.api_key:
            try:
                url = f"{self.fred_base_url}/series/observations"
                api_params = {
                    'series_id': series_id,
                    'api_key': self.api_key,
                    'file_type': 'json',
                    'observation_start': start_date,
                    'observation_end': end_date
                }

                response = requests.get(url, params=api_params)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "series_id": series_id,
                        "observations": data.get('observations', []),
                        "count": data.get('count', 0)
                    }
            except Exception as e:
                return {"error": str(e)}

        return {"error": "FRED API key required"}

    def _get_gdp_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get GDP data"""
        gdp_type = params.get('gdp_type', 'real')  # real or nominal

        series_id = 'GDPC1' if gdp_type == 'real' else 'GDP'

        return self._get_economic_series({
            'series_id': series_id,
            'start_date': params.get('start_date', ''),
            'end_date': params.get('end_date', '')
        })

    def _get_inflation_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get inflation data (CPI)"""
        inflation_type = params.get('inflation_type', 'cpi')  # cpi, pce, core_cpi

        series_map = {
            'cpi': 'CPIAUCSL',  # Consumer Price Index
            'pce': 'PCEPI',  # PCE Price Index
            'core_cpi': 'CPILFESL'  # Core CPI
        }

        series_id = series_map.get(inflation_type, 'CPIAUCSL')

        return self._get_economic_series({
            'series_id': series_id,
            'start_date': params.get('start_date', ''),
            'end_date': params.get('end_date', '')
        })

    def _get_unemployment_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get unemployment data"""
        return self._get_economic_series({
            'series_id': 'UNRATE',  # Unemployment Rate
            'start_date': params.get('start_date', ''),
            'end_date': params.get('end_date', '')
        })

    def _get_money_supply(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get money supply data"""
        supply_type = params.get('supply_type', 'm2')  # m1, m2

        series_id = 'M2SL' if supply_type == 'm2' else 'M1SL'

        return self._get_economic_series({
            'series_id': series_id,
            'start_date': params.get('start_date', ''),
            'end_date': params.get('end_date', '')
        })

    def _get_treasury_yields(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Treasury yield curve data"""
        maturity = params.get('maturity', '10Y')  # 3M, 2Y, 5Y, 10Y, 30Y

        series_map = {
            '3M': 'DGS3MO',
            '2Y': 'DGS2',
            '5Y': 'DGS5',
            '10Y': 'DGS10',
            '30Y': 'DGS30'
        }

        series_id = series_map.get(maturity, 'DGS10')

        return self._get_economic_series({
            'series_id': series_id,
            'start_date': params.get('start_date', ''),
            'end_date': params.get('end_date', '')
        })

    def _search_series(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for economic series"""
        search_text = params.get('search_text', '')

        if not search_text:
            return {"error": "Search text is required"}

        if self.api_key:
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
                            'popularity': s.get('popularity')
                        })

                    return {
                        "search_text": search_text,
                        "results": results,
                        "count": len(results)
                    }
            except Exception as e:
                return {"error": str(e)}

        return {"error": "FRED API key required"}

    def _get_fomc_statements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get FOMC statements (placeholder)"""
        # This would require scraping or additional API access
        return {
            "statements": [],
            "message": "FOMC statements require web scraping implementation"
        }

    def _get_banking_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get banking statistics"""
        stat_type = params.get('stat_type', 'reserves')  # reserves, loans, deposits

        series_map = {
            'reserves': 'TOTRESNS',  # Total Reserves
            'loans': 'TOTLL',  # Total Loans and Leases
            'deposits': 'DPSACBW027SBOG'  # Deposits
        }

        series_id = series_map.get(stat_type, 'TOTRESNS')

        return self._get_economic_series({
            'series_id': series_id,
            'start_date': params.get('start_date', ''),
            'end_date': params.get('end_date', '')
        })