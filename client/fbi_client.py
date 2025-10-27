"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
FBI Crime Data Explorer Standalone Client

This is a standalone client for interacting with the FBI Crime Data Explorer tool.
It can be used independently of the MCP server for direct API access.
"""

import json
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional
from datetime import datetime


class FBIClient:
    """
    Standalone client for FBI Crime Data Explorer API
    
    This client provides direct access to FBI crime statistics without requiring
    the MCP server infrastructure.
    """
    
    def __init__(self, api_url: str = "https://api.usa.gov/crime/fbi/cde"):
        """
        Initialize FBI client
        
        Args:
            api_url: Base URL for FBI API (default: official FBI API)
        """
        self.api_url = api_url
        
        # Crime offense types
        self.offense_types = {
            'violent_crime': 'violent-crime',
            'homicide': 'homicide',
            'rape': 'rape',
            'robbery': 'robbery',
            'aggravated_assault': 'aggravated-assault',
            'property_crime': 'property-crime',
            'burglary': 'burglary',
            'larceny': 'larceny',
            'motor_vehicle_theft': 'motor-vehicle-theft',
            'arson': 'arson'
        }
        
        # US State abbreviations
        self.states = {
            'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
            'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
            'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
            'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
            'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
            'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
            'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
            'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
            'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
            'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
            'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
            'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
            'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
        }
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make HTTP request to FBI API
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response data
            
        Raises:
            Exception: If request fails
        """
        url = f"{self.api_url}/{endpoint}"
        
        if params:
            url += '?' + urllib.parse.urlencode(params)
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/json'
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
                
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise Exception(f"Resource not found: {endpoint}")
            else:
                raise Exception(f"Failed to fetch data: HTTP {e.code}")
        except Exception as e:
            raise Exception(f"Failed to fetch data: {str(e)}")
    
    def _get_latest_year(self) -> int:
        """Get the latest available year (typically current year - 2)"""
        return datetime.now().year - 2
    
    def get_national_statistics(
        self,
        year: Optional[int] = None,
        offense_type: str = 'violent_crime',
        per_capita: bool = False
    ) -> Dict:
        """
        Get national crime statistics
        
        Args:
            year: Year for statistics (defaults to latest available)
            offense_type: Type of crime (default: 'violent_crime')
            per_capita: Return per capita statistics
            
        Returns:
            National crime statistics
            
        Example:
            >>> client = FBIClient()
            >>> stats = client.get_national_statistics(year=2022, offense_type='homicide')
            >>> print(stats['data'])
        """
        if year is None:
            year = self._get_latest_year()
        
        offense = self.offense_types.get(offense_type, offense_type)
        endpoint = f"summarized/national/{offense}/{year}"
        
        data = self._make_request(endpoint)
        
        return {
            'year': year,
            'offense_type': offense_type,
            'offense_category': offense,
            'per_capita': per_capita,
            'data': data,
            'source': 'FBI Crime Data Explorer',
            'retrieved_at': datetime.now().isoformat()
        }
    
    def get_state_statistics(
        self,
        state: str,
        year: Optional[int] = None,
        offense_type: str = 'violent_crime',
        per_capita: bool = False
    ) -> Dict:
        """
        Get state crime statistics
        
        Args:
            state: US state abbreviation (e.g., 'CA', 'NY', 'TX')
            year: Year for statistics (defaults to latest available)
            offense_type: Type of crime (default: 'violent_crime')
            per_capita: Return per capita statistics
            
        Returns:
            State crime statistics
            
        Example:
            >>> client = FBIClient()
            >>> stats = client.get_state_statistics('CA', year=2022, offense_type='robbery')
            >>> print(f"Robberies in California: {stats['data']['actual']}")
        """
        if year is None:
            year = self._get_latest_year()
        
        state = state.upper()
        if state not in self.states:
            raise ValueError(f"Invalid state abbreviation: {state}")
        
        offense = self.offense_types.get(offense_type, offense_type)
        endpoint = f"summarized/state/{state}/{offense}/{year}"
        
        data = self._make_request(endpoint)
        
        return {
            'state': state,
            'state_name': self.states[state],
            'year': year,
            'offense_type': offense_type,
            'offense_category': offense,
            'per_capita': per_capita,
            'data': data,
            'source': 'FBI Crime Data Explorer',
            'retrieved_at': datetime.now().isoformat()
        }
    
    def get_agency_statistics(
        self,
        ori: str,
        year: Optional[int] = None,
        offense_type: str = 'violent_crime'
    ) -> Dict:
        """
        Get agency crime statistics
        
        Args:
            ori: Originating Agency Identifier (ORI) code
            year: Year for statistics (defaults to latest available)
            offense_type: Type of crime (default: 'violent_crime')
            
        Returns:
            Agency crime statistics
            
        Example:
            >>> client = FBIClient()
            >>> stats = client.get_agency_statistics('CA01942', year=2022)
            >>> print(stats['data'])
        """
        if year is None:
            year = self._get_latest_year()
        
        offense = self.offense_types.get(offense_type, offense_type)
        endpoint = f"summarized/agency/{ori}/{offense}/{year}"
        
        data = self._make_request(endpoint)
        
        return {
            'ori': ori,
            'year': year,
            'offense_type': offense_type,
            'offense_category': offense,
            'data': data,
            'source': 'FBI Crime Data Explorer',
            'retrieved_at': datetime.now().isoformat()
        }
    
    def search_agencies(
        self,
        state: Optional[str] = None,
        agency_name: Optional[str] = None
    ) -> Dict:
        """
        Search for law enforcement agencies
        
        Args:
            state: Filter by US state abbreviation
            agency_name: Filter by agency name
            
        Returns:
            List of matching agencies
            
        Example:
            >>> client = FBIClient()
            >>> agencies = client.search_agencies(state='NY', agency_name='Police')
            >>> for agency in agencies['agencies']:
            ...     print(f"{agency['agency_name']} - {agency['ori']}")
        """
        endpoint = "agencies"
        params = {}
        
        if state:
            state = state.upper()
            if state not in self.states:
                raise ValueError(f"Invalid state abbreviation: {state}")
            params['state'] = state
        
        if agency_name:
            params['name'] = agency_name
        
        data = self._make_request(endpoint, params)
        
        return {
            'search_criteria': {
                'state': state,
                'agency_name': agency_name
            },
            'agencies': data.get('results', []),
            'total_count': len(data.get('results', [])),
            'source': 'FBI Crime Data Explorer',
            'retrieved_at': datetime.now().isoformat()
        }
    
    def get_agency_details(self, ori: str) -> Dict:
        """
        Get detailed information about an agency
        
        Args:
            ori: Originating Agency Identifier (ORI) code
            
        Returns:
            Agency details
            
        Example:
            >>> client = FBIClient()
            >>> details = client.get_agency_details('CA01942')
            >>> print(f"Agency: {details['agency_details']['agency_name']}")
        """
        endpoint = f"agencies/{ori}"
        
        data = self._make_request(endpoint)
        
        return {
            'ori': ori,
            'agency_details': data,
            'source': 'FBI Crime Data Explorer',
            'retrieved_at': datetime.now().isoformat()
        }
    
    def get_offense_data(
        self,
        year: Optional[int] = None,
        state: Optional[str] = None
    ) -> Dict:
        """
        Get detailed offense data for all crime types
        
        Args:
            year: Year for statistics (defaults to latest available)
            state: Optional state filter
            
        Returns:
            Offense data for all crime types
            
        Example:
            >>> client = FBIClient()
            >>> offenses = client.get_offense_data(year=2022, state='FL')
            >>> for offense, data in offenses['offenses'].items():
            ...     print(f"{offense}: {data}")
        """
        if year is None:
            year = self._get_latest_year()
        
        results = {}
        
        for offense_name, offense_code in self.offense_types.items():
            try:
                if state:
                    endpoint = f"summarized/state/{state.upper()}/{offense_code}/{year}"
                else:
                    endpoint = f"summarized/national/{offense_code}/{year}"
                
                data = self._make_request(endpoint)
                results[offense_name] = data
            except Exception as e:
                results[offense_name] = {'error': str(e)}
        
        return {
            'year': year,
            'state': state,
            'offenses': results,
            'source': 'FBI Crime Data Explorer',
            'retrieved_at': datetime.now().isoformat()
        }
    
    def get_participation_rate(
        self,
        year: Optional[int] = None,
        state: Optional[str] = None
    ) -> Dict:
        """
        Get UCR program participation rate
        
        Args:
            year: Year for statistics (defaults to latest available)
            state: Optional state filter
            
        Returns:
            Participation rate data
            
        Example:
            >>> client = FBIClient()
            >>> participation = client.get_participation_rate(year=2022, state='CA')
            >>> print(f"Participation: {participation['participation_data']}")
        """
        if year is None:
            year = self._get_latest_year()
        
        if state:
            state = state.upper()
            if state not in self.states:
                raise ValueError(f"Invalid state abbreviation: {state}")
            endpoint = f"participation/state/{state}/{year}"
        else:
            endpoint = f"participation/national/{year}"
        
        data = self._make_request(endpoint)
        
        return {
            'year': year,
            'state': state,
            'state_name': self.states.get(state) if state else 'National',
            'participation_data': data,
            'source': 'FBI Crime Data Explorer',
            'retrieved_at': datetime.now().isoformat()
        }
    
    def get_crime_trend(
        self,
        state: Optional[str] = None,
        offense_type: str = 'violent_crime',
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        per_capita: bool = False
    ) -> Dict:
        """
        Get crime trend over multiple years
        
        Args:
            state: Optional state filter (omit for national trends)
            offense_type: Type of crime (default: 'violent_crime')
            start_year: Start year (defaults to 5 years ago)
            end_year: End year (defaults to latest available)
            per_capita: Return per capita statistics
            
        Returns:
            Crime trend data
            
        Example:
            >>> client = FBIClient()
            >>> trend = client.get_crime_trend('TX', 'homicide', 2018, 2022)
            >>> for year_data in trend['trend']:
            ...     print(f"{year_data['year']}: {year_data['data']}")
        """
        if end_year is None:
            end_year = self._get_latest_year()
        if start_year is None:
            start_year = end_year - 5
        
        offense = self.offense_types.get(offense_type, offense_type)
        trend_data = []
        
        for year in range(start_year, end_year + 1):
            try:
                if state:
                    state = state.upper()
                    if state not in self.states:
                        raise ValueError(f"Invalid state abbreviation: {state}")
                    endpoint = f"summarized/state/{state}/{offense}/{year}"
                else:
                    endpoint = f"summarized/national/{offense}/{year}"
                
                data = self._make_request(endpoint)
                trend_data.append({
                    'year': year,
                    'data': data
                })
            except Exception as e:
                trend_data.append({
                    'year': year,
                    'error': str(e)
                })
        
        return {
            'state': state,
            'state_name': self.states.get(state) if state else 'National',
            'offense_type': offense_type,
            'offense_category': offense,
            'start_year': start_year,
            'end_year': end_year,
            'per_capita': per_capita,
            'trend': trend_data,
            'source': 'FBI Crime Data Explorer',
            'retrieved_at': datetime.now().isoformat()
        }
    
    def compare_states(
        self,
        states: List[str],
        year: Optional[int] = None,
        offense_type: str = 'violent_crime',
        per_capita: bool = True
    ) -> Dict:
        """
        Compare crime statistics across multiple states
        
        Args:
            states: List of state abbreviations (minimum 2)
            year: Year for comparison (defaults to latest available)
            offense_type: Type of crime (default: 'violent_crime')
            per_capita: Return per capita statistics (default: True)
            
        Returns:
            Comparison data for all states
            
        Example:
            >>> client = FBIClient()
            >>> comparison = client.compare_states(['CA', 'TX', 'FL', 'NY'], year=2022)
            >>> for state, data in comparison['states'].items():
            ...     print(f"{data['state_name']}: {data['data']}")
        """
        if year is None:
            year = self._get_latest_year()
        
        if len(states) < 2:
            raise ValueError("At least 2 states required for comparison")
        
        offense = self.offense_types.get(offense_type, offense_type)
        comparison_data = {}
        
        for state in states:
            state = state.upper()
            if state not in self.states:
                print(f"Warning: Invalid state abbreviation: {state}")
                continue
            
            try:
                endpoint = f"summarized/state/{state}/{offense}/{year}"
                data = self._make_request(endpoint)
                comparison_data[state] = {
                    'state_name': self.states[state],
                    'data': data
                }
            except Exception as e:
                comparison_data[state] = {
                    'state_name': self.states[state],
                    'error': str(e)
                }
        
        return {
            'year': year,
            'offense_type': offense_type,
            'offense_category': offense,
            'per_capita': per_capita,
            'states': comparison_data,
            'source': 'FBI Crime Data Explorer',
            'retrieved_at': datetime.now().isoformat()
        }


def main():
    """
    Main function with sample usage examples
    """
    print("=" * 80)
    print("FBI Crime Data Explorer Client - Sample Usage")
    print("Copyright All rights Reserved 2025-2030, Ashutosh Sinha")
    print("=" * 80)
    print()
    
    # Initialize client
    client = FBIClient()
    
    # Example 1: Get National Statistics
    print("Example 1: National Violent Crime Statistics")
    print("-" * 80)
    try:
        national_stats = client.get_national_statistics(
            year=2022,
            offense_type='violent_crime',
            per_capita=True
        )
        print(f"Year: {national_stats['year']}")
        print(f"Offense: {national_stats['offense_type']}")
        print(f"Data: {json.dumps(national_stats['data'], indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Example 2: Get State Statistics
    print("Example 2: California Homicide Statistics")
    print("-" * 80)
    try:
        state_stats = client.get_state_statistics(
            state='CA',
            year=2022,
            offense_type='homicide',
            per_capita=True
        )
        print(f"State: {state_stats['state_name']}")
        print(f"Year: {state_stats['year']}")
        print(f"Offense: {state_stats['offense_type']}")
        print(f"Data: {json.dumps(state_stats['data'], indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Example 3: Search Agencies
    print("Example 3: Search for Police Agencies in New York")
    print("-" * 80)
    try:
        agencies = client.search_agencies(
            state='NY',
            agency_name='Police'
        )
        print(f"Found {agencies['total_count']} agencies")
        for agency in agencies['agencies'][:5]:  # Show first 5
            print(f"  - {agency.get('agency_name', 'N/A')} (ORI: {agency.get('ori', 'N/A')})")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Example 4: Get Crime Trend
    print("Example 4: Texas Violent Crime Trend (2018-2022)")
    print("-" * 80)
    try:
        trend = client.get_crime_trend(
            state='TX',
            offense_type='violent_crime',
            start_year=2018,
            end_year=2022,
            per_capita=True
        )
        print(f"State: {trend['state_name']}")
        print(f"Offense: {trend['offense_type']}")
        print("Trend:")
        for year_data in trend['trend']:
            if 'error' not in year_data:
                print(f"  {year_data['year']}: {year_data['data']}")
            else:
                print(f"  {year_data['year']}: Error - {year_data['error']}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Example 5: Compare States
    print("Example 5: Compare Violent Crime Across States (2022)")
    print("-" * 80)
    try:
        comparison = client.compare_states(
            states=['CA', 'TX', 'FL', 'NY'],
            year=2022,
            offense_type='violent_crime',
            per_capita=True
        )
        print(f"Year: {comparison['year']}")
        print(f"Offense: {comparison['offense_type']}")
        print("Comparison:")
        for state, data in comparison['states'].items():
            if 'error' not in data:
                print(f"  {data['state_name']}: {data['data']}")
            else:
                print(f"  {data['state_name']}: Error - {data['error']}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Example 6: Get Offense Data
    print("Example 6: All Offense Types for Florida (2022)")
    print("-" * 80)
    try:
        offenses = client.get_offense_data(year=2022, state='FL')
        print(f"State: Florida")
        print(f"Year: {offenses['year']}")
        print("Offenses:")
        for offense, data in offenses['offenses'].items():
            if 'error' not in data:
                print(f"  {offense}: {data}")
            else:
                print(f"  {offense}: Error - {data['error']}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Example 7: Get Participation Rate
    print("Example 7: UCR Participation Rate for California (2022)")
    print("-" * 80)
    try:
        participation = client.get_participation_rate(year=2022, state='CA')
        print(f"State: {participation['state_name']}")
        print(f"Year: {participation['year']}")
        print(f"Participation Data: {json.dumps(participation['participation_data'], indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    print("=" * 80)
    print("Sample execution completed")
    print("=" * 80)


if __name__ == '__main__':
    main()
