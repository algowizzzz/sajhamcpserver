"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Bank of Canada Tool - Standalone Client

This client provides easy-to-use methods for interacting with the Bank of Canada tool.
It can be used independently or integrated into larger applications.
"""

import json
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class BankOfCanadaClient:
    """
    Standalone client for Bank of Canada Tool
    
    This client provides a convenient interface for accessing Canadian economic
    and financial data through the MCP server API.
    """
    
    def __init__(self, base_url: str, api_token: Optional[str] = None):
        """
        Initialize Bank of Canada client
        
        Args:
            base_url: Base URL of the MCP server (e.g., 'http://localhost:5000')
            api_token: Optional authentication token for the MCP server
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.tool_name = 'bank_of_canada'
        
    def _make_request(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make API request to execute tool
        
        Args:
            arguments: Tool arguments
            
        Returns:
            Tool execution result
            
        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}/api/tools/execute"
        
        payload = {
            'tool': self.tool_name,
            'arguments': arguments
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.api_token:
            headers['Authorization'] = f'Bearer {self.api_token}'
        
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers)
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if result.get('success'):
                    return result.get('result', {})
                else:
                    raise Exception(f"Tool execution failed: {result.get('error', 'Unknown error')}")
                    
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8') if e.fp else str(e)
            raise Exception(f"HTTP error {e.code}: {error_msg}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_exchange_rate(
        self,
        currency_pair: str,
        recent_periods: int = 10
    ) -> Dict[str, Any]:
        """
        Get exchange rate for a currency pair
        
        Args:
            currency_pair: Currency pair (e.g., 'USD/CAD', 'EUR/CAD') or indicator name
            recent_periods: Number of recent observations
            
        Returns:
            Exchange rate data
        """
        # Check if it's an indicator name or currency pair
        if '/' in currency_pair:
            arguments = {
                'action': 'get_exchange_rate',
                'currency_pair': currency_pair,
                'recent_periods': recent_periods
            }
        else:
            arguments = {
                'action': 'get_exchange_rate',
                'indicator': currency_pair,
                'recent_periods': recent_periods
            }
        
        return self._make_request(arguments)
    
    def get_latest_exchange_rate(self, currency_pair: str) -> Dict[str, Any]:
        """
        Get latest exchange rate for a currency pair
        
        Args:
            currency_pair: Currency pair or indicator name
            
        Returns:
            Latest exchange rate
        """
        if '/' in currency_pair:
            arguments = {
                'action': 'get_exchange_rate',
                'currency_pair': currency_pair,
                'recent_periods': 1
            }
        else:
            arguments = {
                'action': 'get_latest',
                'indicator': currency_pair
            }
        
        result = self._make_request(arguments)
        
        # Return just the latest if using get_exchange_rate
        if 'observations' in result and result['observations']:
            latest = result['observations'][-1]
            return {
                'series_name': result.get('series_name'),
                'label': result.get('label'),
                'date': latest['date'],
                'value': latest['value']
            }
        
        return result
    
    def get_interest_rate(
        self,
        rate_type: str = 'policy_rate',
        recent_periods: int = 10
    ) -> Dict[str, Any]:
        """
        Get interest rate data
        
        Args:
            rate_type: Type of rate ('policy_rate', 'overnight_rate', 'prime_rate')
            recent_periods: Number of recent observations
            
        Returns:
            Interest rate data
        """
        arguments = {
            'action': 'get_interest_rate',
            'rate_type': rate_type,
            'recent_periods': recent_periods
        }
        
        return self._make_request(arguments)
    
    def get_latest_interest_rate(self, rate_type: str = 'policy_rate') -> Dict[str, Any]:
        """
        Get latest interest rate
        
        Args:
            rate_type: Type of rate
            
        Returns:
            Latest interest rate
        """
        result = self.get_interest_rate(rate_type, recent_periods=1)
        
        if 'observations' in result and result['observations']:
            latest = result['observations'][-1]
            return {
                'series_name': result.get('series_name'),
                'label': result.get('label'),
                'rate_type': rate_type,
                'date': latest['date'],
                'value': latest['value']
            }
        
        return result
    
    def get_bond_yield(
        self,
        term: str = '10y',
        recent_periods: int = 10
    ) -> Dict[str, Any]:
        """
        Get bond yield data
        
        Args:
            term: Bond term ('2y', '5y', '10y', '30y')
            recent_periods: Number of recent observations
            
        Returns:
            Bond yield data
        """
        arguments = {
            'action': 'get_bond_yield',
            'bond_term': term,
            'recent_periods': recent_periods
        }
        
        return self._make_request(arguments)
    
    def get_latest_bond_yield(self, term: str = '10y') -> Dict[str, Any]:
        """
        Get latest bond yield
        
        Args:
            term: Bond term
            
        Returns:
            Latest bond yield
        """
        result = self.get_bond_yield(term, recent_periods=1)
        
        if 'observations' in result and result['observations']:
            latest = result['observations'][-1]
            return {
                'series_name': result.get('series_name'),
                'label': result.get('label'),
                'term': term,
                'date': latest['date'],
                'value': latest['value']
            }
        
        return result
    
    def get_historical_data(
        self,
        indicator: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Get historical data for a specific date range
        
        Args:
            indicator: Indicator name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Historical data
        """
        arguments = {
            'action': 'get_series',
            'indicator': indicator,
            'start_date': start_date,
            'end_date': end_date
        }
        
        return self._make_request(arguments)
    
    def get_common_indicators(self) -> Dict[str, Any]:
        """
        Get key Canadian economic indicators
        
        Returns:
            Common indicators with latest values
        """
        arguments = {
            'action': 'get_common_indicators'
        }
        
        return self._make_request(arguments)
    
    def search_available_series(self) -> Dict[str, Any]:
        """
        Get list of available data series
        
        Returns:
            Available series by category
        """
        arguments = {
            'action': 'search_series'
        }
        
        return self._make_request(arguments)
    
    def get_yield_curve(self) -> Dict[str, Any]:
        """
        Get current yield curve (all bond terms)
        
        Returns:
            Yield curve data
        """
        terms = ['2y', '5y', '10y', '30y']
        yield_curve = {
            'date': None,
            'yields': {}
        }
        
        for term in terms:
            try:
                data = self.get_latest_bond_yield(term)
                yield_curve['yields'][term] = data['value']
                if not yield_curve['date']:
                    yield_curve['date'] = data['date']
            except Exception as e:
                print(f"Warning: Could not fetch {term} yield: {e}")
                yield_curve['yields'][term] = None
        
        return yield_curve
    
    def get_all_exchange_rates(self) -> Dict[str, Any]:
        """
        Get latest exchange rates for all major currencies
        
        Returns:
            Dictionary of exchange rates
        """
        currencies = ['usd_cad', 'eur_cad', 'gbp_cad', 'jpy_cad', 'cny_cad']
        rates = {
            'date': None,
            'rates': {}
        }
        
        for currency in currencies:
            try:
                data = self.get_latest_exchange_rate(currency)
                rates['rates'][currency] = data['value']
                if not rates['date']:
                    rates['date'] = data['date']
            except Exception as e:
                print(f"Warning: Could not fetch {currency}: {e}")
                rates['rates'][currency] = None
        
        return rates
    
    def calculate_rate_change(
        self,
        indicator: str,
        periods: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate rate change over specified periods
        
        Args:
            indicator: Indicator name
            periods: Number of periods to analyze
            
        Returns:
            Rate change analysis
        """
        data = self._make_request({
            'action': 'get_series',
            'indicator': indicator,
            'recent_periods': periods
        })
        
        observations = data.get('observations', [])
        if len(observations) < 2:
            return {'error': 'Insufficient data for analysis'}
        
        # Get first and last values
        first = observations[0]
        last = observations[-1]
        
        if first['value'] is None or last['value'] is None:
            return {'error': 'Missing values in data'}
        
        change = last['value'] - first['value']
        change_percent = (change / first['value']) * 100 if first['value'] != 0 else 0
        
        return {
            'indicator': indicator,
            'label': data.get('label'),
            'start_date': first['date'],
            'end_date': last['date'],
            'start_value': first['value'],
            'end_value': last['value'],
            'absolute_change': change,
            'percent_change': change_percent,
            'periods_analyzed': len(observations)
        }
    
    def print_results(self, results: Dict[str, Any], title: str = "Results"):
        """
        Pretty print results
        
        Args:
            results: Results dictionary
            title: Title for the output
        """
        print(f"\n{'='*80}")
        print(f"{title}")
        print(f"{'='*80}\n")
        
        # Check for observations
        if 'observations' in results:
            print(f"Series: {results.get('label', 'N/A')}")
            print(f"Series Name: {results.get('series_name', 'N/A')}")
            if results.get('description'):
                print(f"Description: {results['description']}")
            print(f"Observations: {results.get('observation_count', 0)}\n")
            
            # Print observations
            for obs in results['observations']:
                value = obs['value']
                if value is not None:
                    print(f"  {obs['date']}: {value}")
                else:
                    print(f"  {obs['date']}: No data")
        
        # Check for indicators
        elif 'indicators' in results:
            print("Canadian Economic Indicators:")
            print(f"Last Updated: {results.get('last_updated', 'N/A')}\n")
            
            for indicator_name, data in results['indicators'].items():
                if 'value' in data:
                    print(f"{data.get('description', indicator_name)}:")
                    print(f"  Value: {data['value']}")
                    print(f"  Date: {data['date']}")
                else:
                    print(f"{indicator_name}: {data.get('error', 'Error')}")
                print()
        
        # Check for categories (search results)
        elif 'categories' in results:
            print(f"Available Series ({results.get('total_series', 0)} total):\n")
            
            for category, series_list in results['categories'].items():
                print(f"{category}:")
                for series in series_list:
                    print(f"  - {series['indicator']}: {series['description']}")
                print()
        
        # Single value result
        elif 'value' in results:
            print(f"Series: {results.get('label', 'N/A')}")
            if results.get('description'):
                print(f"Description: {results['description']}")
            print(f"Date: {results['date']}")
            print(f"Value: {results['value']}")
        
        # Generic result
        else:
            print(json.dumps(results, indent=2))
        
        print()


def main():
    """
    Main function with usage examples
    """
    # Initialize client
    BASE_URL = 'http://localhost:5000'
    API_TOKEN = None  # Set your token if required
    
    client = BankOfCanadaClient(BASE_URL, API_TOKEN)
    
    print("="*80)
    print("BANK OF CANADA TOOL - CLIENT EXAMPLES")
    print("="*80)
    
    # Example 1: Get USD/CAD Exchange Rate
    print("\n" + "="*80)
    print("EXAMPLE 1: USD/CAD Exchange Rate (Last 10 Days)")
    print("="*80)
    
    try:
        result = client.get_exchange_rate('usd_cad', recent_periods=10)
        client.print_results(result, "USD/CAD Exchange Rate")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Get Latest Exchange Rate
    print("\n" + "="*80)
    print("EXAMPLE 2: Latest USD/CAD Exchange Rate")
    print("="*80)
    
    try:
        result = client.get_latest_exchange_rate('usd_cad')
        print(f"\nLatest USD/CAD Rate:")
        print(f"Date: {result['date']}")
        print(f"Rate: {result['value']:.4f}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Get Policy Interest Rate
    print("\n" + "="*80)
    print("EXAMPLE 3: Bank of Canada Policy Rate History")
    print("="*80)
    
    try:
        result = client.get_interest_rate('policy_rate', recent_periods=5)
        client.print_results(result, "BoC Policy Rate")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Get Latest Policy Rate
    print("\n" + "="*80)
    print("EXAMPLE 4: Current Policy Interest Rate")
    print("="*80)
    
    try:
        result = client.get_latest_interest_rate('policy_rate')
        print(f"\nCurrent BoC Policy Rate:")
        print(f"Date: {result['date']}")
        print(f"Rate: {result['value']:.2f}%")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 5: Get 10-Year Bond Yield
    print("\n" + "="*80)
    print("EXAMPLE 5: 10-Year Government Bond Yield")
    print("="*80)
    
    try:
        result = client.get_bond_yield('10y', recent_periods=20)
        client.print_results(result, "10-Year Bond Yield")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 6: Get Historical Data
    print("\n" + "="*80)
    print("EXAMPLE 6: Historical USD/CAD (Q1 2024)")
    print("="*80)
    
    try:
        result = client.get_historical_data(
            'usd_cad',
            '2024-01-01',
            '2024-03-31'
        )
        
        print(f"\nUSD/CAD Q1 2024 Analysis:")
        print(f"Total observations: {result['observation_count']}")
        
        if result['observations']:
            rates = [obs['value'] for obs in result['observations'] if obs['value']]
            if rates:
                print(f"High: {max(rates):.4f}")
                print(f"Low: {min(rates):.4f}")
                print(f"Average: {sum(rates)/len(rates):.4f}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 7: Get Common Indicators
    print("\n" + "="*80)
    print("EXAMPLE 7: Key Canadian Economic Indicators")
    print("="*80)
    
    try:
        result = client.get_common_indicators()
        client.print_results(result, "Common Economic Indicators")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 8: Search Available Series
    print("\n" + "="*80)
    print("EXAMPLE 8: Available Data Series")
    print("="*80)
    
    try:
        result = client.search_available_series()
        client.print_results(result, "Available Series")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 9: Get Yield Curve
    print("\n" + "="*80)
    print("EXAMPLE 9: Government Bond Yield Curve")
    print("="*80)
    
    try:
        result = client.get_yield_curve()
        print(f"\nYield Curve as of {result['date']}:")
        for term, yield_value in result['yields'].items():
            if yield_value:
                print(f"  {term.upper()}: {yield_value:.2f}%")
            else:
                print(f"  {term.upper()}: N/A")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 10: Get All Exchange Rates
    print("\n" + "="*80)
    print("EXAMPLE 10: All Major Exchange Rates to CAD")
    print("="*80)
    
    try:
        result = client.get_all_exchange_rates()
        print(f"\nExchange Rates as of {result['date']}:")
        for currency, rate in result['rates'].items():
            if rate:
                print(f"  {currency.upper()}: {rate:.4f}")
            else:
                print(f"  {currency.upper()}: N/A")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 11: Calculate Rate Change
    print("\n" + "="*80)
    print("EXAMPLE 11: Policy Rate Change Analysis (Last 30 Days)")
    print("="*80)
    
    try:
        result = client.calculate_rate_change('policy_rate', periods=30)
        
        if 'error' not in result:
            print(f"\n{result['label']} Analysis:")
            print(f"Period: {result['start_date']} to {result['end_date']}")
            print(f"Starting Rate: {result['start_value']:.2f}%")
            print(f"Ending Rate: {result['end_value']:.2f}%")
            print(f"Absolute Change: {result['absolute_change']:+.2f}%")
            print(f"Percent Change: {result['percent_change']:+.2f}%")
            print(f"Periods Analyzed: {result['periods_analyzed']}")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 12: Compare Multiple Exchange Rates
    print("\n" + "="*80)
    print("EXAMPLE 12: Compare Multiple Exchange Rates")
    print("="*80)
    
    try:
        currencies = ['usd_cad', 'eur_cad', 'gbp_cad']
        
        print("\nLatest Exchange Rates:")
        for currency in currencies:
            result = client.get_latest_exchange_rate(currency)
            print(f"{currency.upper()}: {result['value']:.4f} (as of {result['date']})")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)
    print("ALL EXAMPLES COMPLETED")
    print("="*80)


if __name__ == "__main__":
    """
    Run the client examples
    
    Usage:
        python bank_of_canada_client.py
    
    Configuration:
        Update BASE_URL and API_TOKEN in main() function
    """
    main()
