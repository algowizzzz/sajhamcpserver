"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
European Central Bank (ECB) Tool - Standalone Client
"""

import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta


class EuropeanCentralBankClient:
    """
    Standalone client for interacting with the European Central Bank MCP Tool
    
    This client provides a convenient Python interface for making requests to the
    ECB tool API endpoint.
    """
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 30):
        """
        Initialize the ECB client
        
        Args:
            base_url: Base URL of the MCP server (default: http://localhost:5000)
            timeout: Request timeout in seconds (default: 30)
        """
        self.base_url = base_url.rstrip('/')
        self.api_endpoint = f"{self.base_url}/api/tools/execute"
        self.timeout = timeout
        self.tool_name = "european_central_bank"
    
    def _execute_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the ECB tool with given arguments
        
        Args:
            arguments: Tool arguments dictionary
            
        Returns:
            Tool execution result
            
        Raises:
            requests.exceptions.RequestException: On HTTP errors
            ValueError: On tool execution errors
        """
        payload = {
            "tool_name": self.tool_name,
            "arguments": arguments
        }
        
        try:
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get('status') == 'error':
                raise ValueError(f"Tool error: {result.get('error')}")
            
            return result.get('result', {})
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP request failed: {e}")
    
    def get_series(
        self,
        flow: Optional[str] = None,
        key: Optional[str] = None,
        indicator: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        recent_periods: int = 10
    ) -> Dict[str, Any]:
        """
        Get time series data from ECB
        
        Args:
            flow: ECB data flow identifier (e.g., 'EXR', 'FM')
            key: ECB series key
            indicator: Common indicator name (alternative to flow/key)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            recent_periods: Number of recent periods to retrieve
            
        Returns:
            Time series data dictionary
        """
        arguments = {
            "action": "get_series",
            "recent_periods": recent_periods
        }
        
        if flow:
            arguments["flow"] = flow
        if key:
            arguments["key"] = key
        if indicator:
            arguments["indicator"] = indicator
        if start_date:
            arguments["start_date"] = start_date
        if end_date:
            arguments["end_date"] = end_date
        
        return self._execute_tool(arguments)
    
    def get_exchange_rate(
        self,
        currency_pair: Optional[str] = None,
        indicator: Optional[str] = None,
        recent_periods: int = 10
    ) -> Dict[str, Any]:
        """
        Get exchange rate data
        
        Args:
            currency_pair: Currency pair (e.g., 'EUR/USD')
            indicator: Common indicator name (e.g., 'eur_usd')
            recent_periods: Number of recent periods to retrieve
            
        Returns:
            Exchange rate data dictionary
        """
        arguments = {
            "action": "get_exchange_rate",
            "recent_periods": recent_periods
        }
        
        if currency_pair:
            arguments["currency_pair"] = currency_pair
        if indicator:
            arguments["indicator"] = indicator
        
        return self._execute_tool(arguments)
    
    def get_interest_rate(
        self,
        rate_type: str = "main_refinancing_rate",
        recent_periods: int = 10
    ) -> Dict[str, Any]:
        """
        Get ECB interest rate data
        
        Args:
            rate_type: Type of interest rate
                - 'main_refinancing_rate'
                - 'deposit_facility_rate'
                - 'marginal_lending_rate'
                - 'eonia'
                - 'ester'
            recent_periods: Number of recent periods to retrieve
            
        Returns:
            Interest rate data dictionary
        """
        arguments = {
            "action": "get_interest_rate",
            "rate_type": rate_type,
            "recent_periods": recent_periods
        }
        
        return self._execute_tool(arguments)
    
    def get_bond_yield(
        self,
        bond_term: str = "10y",
        recent_periods: int = 10
    ) -> Dict[str, Any]:
        """
        Get Euro Area government bond yield data
        
        Args:
            bond_term: Bond maturity ('2y', '5y', '10y')
            recent_periods: Number of recent periods to retrieve
            
        Returns:
            Bond yield data dictionary
        """
        arguments = {
            "action": "get_bond_yield",
            "bond_term": bond_term,
            "recent_periods": recent_periods
        }
        
        return self._execute_tool(arguments)
    
    def get_inflation(
        self,
        inflation_type: str = "overall",
        recent_periods: int = 10
    ) -> Dict[str, Any]:
        """
        Get HICP inflation data
        
        Args:
            inflation_type: Type of inflation measure
                - 'overall': Overall HICP
                - 'core': Core HICP (excluding energy and food)
                - 'energy': Energy HICP
            recent_periods: Number of recent periods to retrieve
            
        Returns:
            Inflation data dictionary
        """
        arguments = {
            "action": "get_inflation",
            "inflation_type": inflation_type,
            "recent_periods": recent_periods
        }
        
        return self._execute_tool(arguments)
    
    def get_latest(
        self,
        flow: Optional[str] = None,
        key: Optional[str] = None,
        indicator: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the latest observation for a series
        
        Args:
            flow: ECB data flow identifier
            key: ECB series key
            indicator: Common indicator name (alternative to flow/key)
            
        Returns:
            Latest observation dictionary
        """
        arguments = {
            "action": "get_latest"
        }
        
        if flow:
            arguments["flow"] = flow
        if key:
            arguments["key"] = key
        if indicator:
            arguments["indicator"] = indicator
        
        return self._execute_tool(arguments)
    
    def get_common_indicators(self) -> Dict[str, Any]:
        """
        Get latest values for common economic indicators
        
        Returns:
            Dictionary of common indicators with latest values
        """
        arguments = {
            "action": "get_common_indicators"
        }
        
        return self._execute_tool(arguments)
    
    def search_series(self) -> Dict[str, Any]:
        """
        List all available common series organized by category
        
        Returns:
            Dictionary of available series by category
        """
        arguments = {
            "action": "search_series"
        }
        
        return self._execute_tool(arguments)
    
    def get_unemployment_rate(self, recent_periods: int = 12) -> Dict[str, Any]:
        """
        Get Eurozone unemployment rate
        
        Args:
            recent_periods: Number of recent periods to retrieve
            
        Returns:
            Unemployment rate data dictionary
        """
        return self.get_series(
            indicator="unemployment_rate",
            recent_periods=recent_periods
        )
    
    def get_gdp(self, recent_periods: int = 8) -> Dict[str, Any]:
        """
        Get Eurozone GDP data
        
        Args:
            recent_periods: Number of recent periods to retrieve
            
        Returns:
            GDP data dictionary
        """
        return self.get_series(
            indicator="gdp",
            recent_periods=recent_periods
        )
    
    def get_money_supply(
        self,
        aggregate: str = "m3",
        recent_periods: int = 12
    ) -> Dict[str, Any]:
        """
        Get monetary aggregate data
        
        Args:
            aggregate: Monetary aggregate ('m1', 'm2', 'm3')
            recent_periods: Number of recent periods to retrieve
            
        Returns:
            Money supply data dictionary
        """
        return self.get_series(
            indicator=aggregate,
            recent_periods=recent_periods
        )
    
    def print_series_data(self, data: Dict[str, Any], max_rows: int = 10) -> None:
        """
        Pretty print series data
        
        Args:
            data: Series data dictionary
            max_rows: Maximum number of observations to display
        """
        print(f"\n{'=' * 80}")
        print(f"Series: {data.get('description', data.get('series_name', 'Unknown'))}")
        print(f"Flow: {data.get('flow', 'N/A')} | Key: {data.get('key', 'N/A')}")
        print(f"Observation Count: {data.get('observation_count', 0)}")
        print(f"{'=' * 80}\n")
        
        observations = data.get('observations', [])
        display_obs = observations[-max_rows:] if len(observations) > max_rows else observations
        
        if display_obs:
            print(f"{'Date':<15} {'Value':>15}")
            print(f"{'-' * 15} {'-' * 15}")
            for obs in display_obs:
                value = obs.get('value')
                value_str = f"{value:.4f}" if value is not None else "N/A"
                print(f"{obs.get('date', 'N/A'):<15} {value_str:>15}")
        else:
            print("No observations available")
        
        print(f"\n{'=' * 80}\n")
    
    def print_indicators(self, indicators: Dict[str, Any]) -> None:
        """
        Pretty print common indicators
        
        Args:
            indicators: Indicators dictionary from get_common_indicators()
        """
        print(f"\n{'=' * 80}")
        print("Common Economic Indicators")
        print(f"Last Updated: {indicators.get('last_updated', 'N/A')}")
        print(f"{'=' * 80}\n")
        
        indicator_data = indicators.get('indicators', {})
        
        for name, data in indicator_data.items():
            if 'value' in data:
                print(f"{name.replace('_', ' ').title():<40}")
                print(f"  Value: {data.get('value', 'N/A')}")
                print(f"  Date:  {data.get('date', 'N/A')}")
                print(f"  Desc:  {data.get('description', 'N/A')}")
                print()
            elif 'error' in data:
                print(f"{name.replace('_', ' ').title():<40}")
                print(f"  Error: {data.get('error', 'N/A')}")
                print()
        
        print(f"{'=' * 80}\n")


def main():
    """
    Main function with comprehensive examples of using the ECB client
    """
    print("\n" + "=" * 80)
    print("European Central Bank (ECB) Tool - Client Examples")
    print("Copyright All rights Reserved 2025-2030, Ashutosh Sinha")
    print("=" * 80 + "\n")
    
    # Initialize client
    client = EuropeanCentralBankClient(base_url="http://localhost:5000")
    
    try:
        # Example 1: Get EUR/USD Exchange Rate
        print("\n### Example 1: EUR/USD Exchange Rate (Last 5 Days)")
        eur_usd = client.get_exchange_rate(indicator="eur_usd", recent_periods=5)
        client.print_series_data(eur_usd, max_rows=5)
        
        # Example 2: Get Main Refinancing Rate
        print("\n### Example 2: ECB Main Refinancing Rate")
        mrr = client.get_interest_rate(rate_type="main_refinancing_rate", recent_periods=10)
        client.print_series_data(mrr, max_rows=10)
        
        # Example 3: Get 10-Year Bond Yield
        print("\n### Example 3: 10-Year Euro Area Bond Yield")
        bond_10y = client.get_bond_yield(bond_term="10y", recent_periods=10)
        client.print_series_data(bond_10y, max_rows=10)
        
        # Example 4: Get Overall Inflation (HICP)
        print("\n### Example 4: Overall Inflation (HICP)")
        hicp = client.get_inflation(inflation_type="overall", recent_periods=12)
        client.print_series_data(hicp, max_rows=12)
        
        # Example 5: Get Latest EUR/GBP Rate
        print("\n### Example 5: Latest EUR/GBP Exchange Rate")
        latest_gbp = client.get_latest(indicator="eur_gbp")
        print(f"EUR/GBP Rate: {latest_gbp.get('value', 'N/A')}")
        print(f"Date: {latest_gbp.get('date', 'N/A')}")
        
        # Example 6: Get Unemployment Rate
        print("\n### Example 6: Eurozone Unemployment Rate")
        unemployment = client.get_unemployment_rate(recent_periods=6)
        client.print_series_data(unemployment, max_rows=6)
        
        # Example 7: Get M3 Money Supply
        print("\n### Example 7: M3 Monetary Aggregate")
        m3 = client.get_money_supply(aggregate="m3", recent_periods=12)
        client.print_series_data(m3, max_rows=12)
        
        # Example 8: Get GDP
        print("\n### Example 8: Eurozone GDP")
        gdp = client.get_gdp(recent_periods=4)
        client.print_series_data(gdp, max_rows=4)
        
        # Example 9: Get €STR (Euro Short-Term Rate)
        print("\n### Example 9: €STR (Euro Short-Term Rate)")
        ester = client.get_interest_rate(rate_type="ester", recent_periods=10)
        client.print_series_data(ester, max_rows=10)
        
        # Example 10: Get Common Indicators Dashboard
        print("\n### Example 10: Common Indicators Dashboard")
        indicators = client.get_common_indicators()
        client.print_indicators(indicators)
        
        # Example 11: Search Available Series
        print("\n### Example 11: Available Series by Category")
        series_list = client.search_series()
        categories = series_list.get('categories', {})
        print(f"Total Series Available: {series_list.get('total_series', 0)}\n")
        
        for category, series in categories.items():
            print(f"\n{category}:")
            for s in series:
                print(f"  - {s.get('indicator', 'N/A')}: {s.get('description', 'N/A')}")
        
        # Example 12: Get Core Inflation
        print("\n### Example 12: Core Inflation (Excluding Energy & Food)")
        core_hicp = client.get_inflation(inflation_type="core", recent_periods=12)
        client.print_series_data(core_hicp, max_rows=12)
        
        # Example 13: Get EUR/JPY with Date Range
        print("\n### Example 13: EUR/JPY Exchange Rate (Date Range)")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        eur_jpy = client.get_series(
            indicator="eur_jpy",
            start_date=start_date,
            end_date=end_date
        )
        client.print_series_data(eur_jpy, max_rows=10)
        
        # Example 14: Get Deposit Facility Rate
        print("\n### Example 14: ECB Deposit Facility Rate")
        dfr = client.get_interest_rate(rate_type="deposit_facility_rate", recent_periods=10)
        client.print_series_data(dfr, max_rows=10)
        
        # Example 15: Get 2-Year and 5-Year Bond Yields Comparison
        print("\n### Example 15: Bond Yield Curve Comparison")
        bond_2y = client.get_bond_yield(bond_term="2y", recent_periods=5)
        bond_5y = client.get_bond_yield(bond_term="5y", recent_periods=5)
        
        print("\nBond Yield Curve:")
        print(f"{'Date':<15} {'2Y Yield':>12} {'5Y Yield':>12} {'Spread':>12}")
        print(f"{'-' * 15} {'-' * 12} {'-' * 12} {'-' * 12}")
        
        obs_2y = bond_2y.get('observations', [])
        obs_5y = bond_5y.get('observations', [])
        
        for i in range(min(len(obs_2y), len(obs_5y))):
            date = obs_2y[i].get('date', 'N/A')
            yield_2y = obs_2y[i].get('value')
            yield_5y = obs_5y[i].get('value')
            
            if yield_2y is not None and yield_5y is not None:
                spread = yield_5y - yield_2y
                print(f"{date:<15} {yield_2y:>12.4f} {yield_5y:>12.4f} {spread:>12.4f}")
        
        print("\n" + "=" * 80)
        print("All examples completed successfully!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\nError occurred: {e}")
        print("\nMake sure the MCP server is running at http://localhost:5000")
        print("and the european_central_bank tool is properly configured.\n")


if __name__ == "__main__":
    main()
