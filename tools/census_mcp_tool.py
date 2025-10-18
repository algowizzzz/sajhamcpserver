"""
Census.gov MCP Tool implementation
"""
import os
import requests
from typing import Dict, Any, List
from .base_mcp_tool import BaseMCPTool


class CensusMCPTool(BaseMCPTool):
    """MCP Tool for Census.gov data operations"""

    def _initialize(self):
        """Initialize Census specific components"""
        self.api_key = os.environ.get('CENSUS_API_KEY', '')
        self.base_url = "https://api.census.gov/data"

        if not self.api_key:
            print("Warning: CENSUS_API_KEY not set. Limited functionality available.")

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Census tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            tool_methods = {
                "get_population_data": self._get_population_data,
                "get_demographic_data": self._get_demographic_data,
                "get_economic_data": self._get_economic_data,
                "get_housing_data": self._get_housing_data,
                "get_education_data": self._get_education_data,
                "get_state_data": self._get_state_data,
                "get_county_data": self._get_county_data,
                "search_datasets": self._search_datasets
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

    def _get_population_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get population data"""
        year = params.get('year', 2021)
        geography = params.get('geography', 'state')  # state, county, place
        state = params.get('state', '*')  # FIPS code or * for all

        if not self.api_key:
            return {"error": "Census API key required"}

        try:
            # American Community Survey 5-Year Estimates
            url = f"{self.base_url}/{year}/acs/acs5"

            # Build parameters
            api_params = {
                'get': 'NAME,B01001_001E',  # Total population
                'for': f'{geography}:{state}',
                'key': self.api_key
            }

            response = requests.get(url, params=api_params)
            if response.status_code == 200:
                data = response.json()

                # Parse results
                results = []
                headers = data[0]

                for row in data[1:]:
                    result_dict = dict(zip(headers, row))
                    results.append({
                        'name': result_dict.get('NAME', ''),
                        'population': int(result_dict.get('B01001_001E', 0)) if result_dict.get('B01001_001E') else 0,
                        'state': result_dict.get('state', ''),
                        'county': result_dict.get('county', '')
                    })

                return {
                    "year": year,
                    "geography": geography,
                    "data": results,
                    "count": len(results)
                }
            else:
                return {"error": f"API request failed: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_demographic_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get demographic data including age, race, ethnicity"""
        year = params.get('year', 2021)
        state = params.get('state', '06')  # California as default

        if not self.api_key:
            return {"error": "Census API key required"}

        try:
            url = f"{self.base_url}/{year}/acs/acs5"

            # Variables for demographics
            variables = [
                'B01001_001E',  # Total population
                'B01001_002E',  # Male
                'B01001_026E',  # Female
                'B01002_001E',  # Median age
                'B02001_002E',  # White alone
                'B02001_003E',  # Black or African American alone
                'B02001_005E',  # Asian alone
                'B03002_012E'  # Hispanic or Latino
            ]

            api_params = {
                'get': f"NAME,{','.join(variables)}",
                'for': f'state:{state}',
                'key': self.api_key
            }

            response = requests.get(url, params=api_params)
            if response.status_code == 200:
                data = response.json()

                if len(data) > 1:
                    headers = data[0]
                    values = data[1]
                    result = dict(zip(headers, values))

                    return {
                        "year": year,
                        "state": result.get('NAME', ''),
                        "demographics": {
                            "total_population": int(result.get('B01001_001E', 0)) if result.get('B01001_001E') else 0,
                            "male_population": int(result.get('B01001_002E', 0)) if result.get('B01001_002E') else 0,
                            "female_population": int(result.get('B01001_026E', 0)) if result.get('B01001_026E') else 0,
                            "median_age": float(result.get('B01002_001E', 0)) if result.get('B01002_001E') else 0,
                            "white_alone": int(result.get('B02001_002E', 0)) if result.get('B02001_002E') else 0,
                            "black_alone": int(result.get('B02001_003E', 0)) if result.get('B02001_003E') else 0,
                            "asian_alone": int(result.get('B02001_005E', 0)) if result.get('B02001_005E') else 0,
                            "hispanic_latino": int(result.get('B03002_012E', 0)) if result.get('B03002_012E') else 0
                        }
                    }

            return {"error": f"API request failed: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_economic_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get economic data including income, poverty, employment"""
        year = params.get('year', 2021)
        state = params.get('state', '06')

        if not self.api_key:
            return {"error": "Census API key required"}

        try:
            url = f"{self.base_url}/{year}/acs/acs5"

            # Economic variables
            variables = [
                'B19013_001E',  # Median household income
                'B17001_002E',  # Below poverty level
                'B23025_002E',  # Labor force
                'B23025_005E',  # Unemployed
                'B25077_001E'  # Median home value
            ]

            api_params = {
                'get': f"NAME,{','.join(variables)}",
                'for': f'state:{state}',
                'key': self.api_key
            }

            response = requests.get(url, params=api_params)
            if response.status_code == 200:
                data = response.json()

                if len(data) > 1:
                    headers = data[0]
                    values = data[1]
                    result = dict(zip(headers, values))

                    return {
                        "year": year,
                        "state": result.get('NAME', ''),
                        "economic_data": {
                            "median_household_income": int(result.get('B19013_001E', 0)) if result.get(
                                'B19013_001E') else 0,
                            "below_poverty_level": int(result.get('B17001_002E', 0)) if result.get(
                                'B17001_002E') else 0,
                            "labor_force": int(result.get('B23025_002E', 0)) if result.get('B23025_002E') else 0,
                            "unemployed": int(result.get('B23025_005E', 0)) if result.get('B23025_005E') else 0,
                            "median_home_value": int(result.get('B25077_001E', 0)) if result.get('B25077_001E') else 0
                        }
                    }

            return {"error": f"API request failed: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_housing_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get housing data"""
        year = params.get('year', 2021)
        state = params.get('state', '06')

        if not self.api_key:
            return {"error": "Census API key required"}

        try:
            url = f"{self.base_url}/{year}/acs/acs5"

            # Housing variables
            variables = [
                'B25001_001E',  # Total housing units
                'B25002_002E',  # Occupied units
                'B25002_003E',  # Vacant units
                'B25003_002E',  # Owner occupied
                'B25003_003E',  # Renter occupied
                'B25064_001E'  # Median gross rent
            ]

            api_params = {
                'get': f"NAME,{','.join(variables)}",
                'for': f'state:{state}',
                'key': self.api_key
            }

            response = requests.get(url, params=api_params)
            if response.status_code == 200:
                data = response.json()

                if len(data) > 1:
                    headers = data[0]
                    values = data[1]
                    result = dict(zip(headers, values))

                    return {
                        "year": year,
                        "state": result.get('NAME', ''),
                        "housing_data": {
                            "total_housing_units": int(result.get('B25001_001E', 0)) if result.get(
                                'B25001_001E') else 0,
                            "occupied_units": int(result.get('B25002_002E', 0)) if result.get('B25002_002E') else 0,
                            "vacant_units": int(result.get('B25002_003E', 0)) if result.get('B25002_003E') else 0,
                            "owner_occupied": int(result.get('B25003_002E', 0)) if result.get('B25003_002E') else 0,
                            "renter_occupied": int(result.get('B25003_003E', 0)) if result.get('B25003_003E') else 0,
                            "median_gross_rent": int(result.get('B25064_001E', 0)) if result.get('B25064_001E') else 0
                        }
                    }

            return {"error": f"API request failed: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_education_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get education data"""
        year = params.get('year', 2021)
        state = params.get('state', '06')

        if not self.api_key:
            return {"error": "Census API key required"}

        try:
            url = f"{self.base_url}/{year}/acs/acs5"

            # Education variables
            variables = [
                'B15003_001E',  # Total population 25 years and over
                'B15003_017E',  # High school graduate
                'B15003_021E',  # Associate's degree
                'B15003_022E',  # Bachelor's degree
                'B15003_023E',  # Master's degree
                'B15003_025E'  # Doctorate degree
            ]

            api_params = {
                'get': f"NAME,{','.join(variables)}",
                'for': f'state:{state}',
                'key': self.api_key
            }

            response = requests.get(url, params=api_params)
            if response.status_code == 200:
                data = response.json()

                if len(data) > 1:
                    headers = data[0]
                    values = data[1]
                    result = dict(zip(headers, values))

                    return {
                        "year": year,
                        "state": result.get('NAME', ''),
                        "education_data": {
                            "population_25_plus": int(result.get('B15003_001E', 0)) if result.get('B15003_001E') else 0,
                            "high_school_graduate": int(result.get('B15003_017E', 0)) if result.get(
                                'B15003_017E') else 0,
                            "associates_degree": int(result.get('B15003_021E', 0)) if result.get('B15003_021E') else 0,
                            "bachelors_degree": int(result.get('B15003_022E', 0)) if result.get('B15003_022E') else 0,
                            "masters_degree": int(result.get('B15003_023E', 0)) if result.get('B15003_023E') else 0,
                            "doctorate_degree": int(result.get('B15003_025E', 0)) if result.get('B15003_025E') else 0
                        }
                    }

            return {"error": f"API request failed: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_state_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive data for all states"""
        year = params.get('year', 2021)

        return self._get_population_data({
            'year': year,
            'geography': 'state',
            'state': '*'
        })

    def _get_county_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get data for counties"""
        year = params.get('year', 2021)
        state = params.get('state', '06')  # California

        return self._get_population_data({
            'year': year,
            'geography': 'county',
            'state': f'*&in=state:{state}'
        })

    def _search_datasets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search available Census datasets"""
        keyword = params.get('keyword', '')

        # List of common datasets
        datasets = [
            {
                "name": "American Community Survey 5-Year",
                "code": "acs/acs5",
                "description": "Detailed demographic and economic data",
                "years": "2009-2021"
            },
            {
                "name": "Decennial Census",
                "code": "dec",
                "description": "Complete count of population",
                "years": "2000, 2010, 2020"
            },
            {
                "name": "Economic Census",
                "code": "ecn",
                "description": "Business and economic statistics",
                "years": "2017"
            },
            {
                "name": "Population Estimates",
                "code": "pep",
                "description": "Annual population estimates",
                "years": "2010-2021"
            }
        ]

        if keyword:
            datasets = [d for d in datasets if
                        keyword.lower() in d['name'].lower() or keyword.lower() in d['description'].lower()]

        return {
            "keyword": keyword,
            "datasets": datasets,
            "count": len(datasets)
        }