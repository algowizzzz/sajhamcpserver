"""
US Department of Agriculture (USDA) MCP Tool implementation
"""
import requests
from typing import Dict, Any, List, Optional
from .base_mcp_tool import BaseMCPTool


class USDAMCPTool(BaseMCPTool):
    """MCP Tool for USDA data including nutrition and agriculture"""

    def _initialize(self):
        """Initialize USDA specific components"""
        self.api_key = self.config.get('api_key', 'DEMO_KEY')
        self.food_data_url = 'https://api.nal.usda.gov/fdc/v1'
        self.nass_url = 'https://quickstats.nass.usda.gov/api'
        self.timeout = 30

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle USDA tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            tool_methods = {
                "search_foods": self._search_foods,
                "get_food_details": self._get_food_details,
                "get_nutrients": self._get_nutrients,
                "search_farmers_markets": self._search_farmers_markets,
                "get_crop_data": self._get_crop_data,
                "get_livestock_data": self._get_livestock_data,
                "search_organic_data": self._search_organic_data,
                "get_food_prices": self._get_food_prices,
                "search_nutrition_programs": self._search_nutrition_programs,
                "get_dietary_guidelines": self._get_dietary_guidelines,
                "search_food_recalls": self._search_food_recalls,
                "get_commodity_prices": self._get_commodity_prices,
                "search_agricultural_census": self._search_agricultural_census,
                "get_soil_survey_data": self._get_soil_survey_data
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

    def _make_fdc_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make request to FoodData Central API"""
        try:
            url = f"{self.food_data_url}{endpoint}"
            if params is None:
                params = {}
            params['api_key'] = self.api_key

            response = requests.get(url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "status_code": response.status_code
                }
        except requests.exceptions.Timeout:
            return {"error": "Request timeout"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def _make_nass_request(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make request to NASS QuickStats API"""
        try:
            url = f"{self.nass_url}/api_GET"
            if params is None:
                params = {}
            params['key'] = self.api_key
            params['format'] = 'JSON'

            response = requests.get(url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "status_code": response.status_code
                }
        except requests.exceptions.Timeout:
            return {"error": "Request timeout"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def _search_foods(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for foods in the USDA database"""
        query = params.get('query', '')
        data_type = params.get('data_type', '')  # Foundation, SR Legacy, Branded
        page_size = params.get('page_size', 50)
        page_number = params.get('page_number', 1)

        if not query:
            return {"error": "Query is required"}

        search_params = {
            'query': query,
            'pageSize': page_size,
            'pageNumber': page_number
        }

        if data_type:
            search_params['dataType'] = data_type

        result = self._make_fdc_request('/foods/search', search_params)

        if 'error' not in result:
            foods = result.get('foods', [])

            return {
                "query": query,
                "data_type": data_type,
                "foods": [
                    {
                        "fdc_id": food.get('fdcId'),
                        "description": food.get('description'),
                        "brand_owner": food.get('brandOwner'),
                        "data_type": food.get('dataType'),
                        "published_date": food.get('publishedDate')
                    }
                    for food in foods
                ],
                "total_hits": result.get('totalHits', 0),
                "current_page": result.get('currentPage', 1),
                "total_pages": result.get('totalPages', 1)
            }
        return result

    def _get_food_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed nutrition information for a specific food"""
        fdc_id = params.get('fdc_id', '')

        if not fdc_id:
            return {"error": "FDC ID is required"}

        result = self._make_fdc_request(f'/food/{fdc_id}')

        if 'error' not in result:
            nutrients = result.get('foodNutrients', [])

            return {
                "fdc_id": result.get('fdcId'),
                "description": result.get('description'),
                "data_type": result.get('dataType'),
                "brand_owner": result.get('brandOwner'),
                "ingredients": result.get('ingredients'),
                "serving_size": result.get('servingSize'),
                "serving_size_unit": result.get('servingSizeUnit'),
                "nutrients": [
                    {
                        "name": n.get('nutrient', {}).get('name'),
                        "amount": n.get('amount'),
                        "unit": n.get('nutrient', {}).get('unitName')
                    }
                    for n in nutrients
                ],
                "category": result.get('foodCategory', {}).get('description'),
                "publication_date": result.get('publicationDate')
            }
        return result

    def _get_nutrients(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific nutrients for foods"""
        fdc_ids = params.get('fdc_ids', [])
        nutrients = params.get('nutrients', [])  # List of nutrient IDs or names

        if not fdc_ids:
            return {"error": "FDC IDs are required"}

        results = []
        for fdc_id in fdc_ids:
            food_data = self._make_fdc_request(f'/food/{fdc_id}')

            if 'error' not in food_data:
                food_nutrients = food_data.get('foodNutrients', [])

                if nutrients:
                    food_nutrients = [
                        n for n in food_nutrients
                        if n.get('nutrient', {}).get('name') in nutrients
                    ]

                results.append({
                    "fdc_id": fdc_id,
                    "description": food_data.get('description'),
                    "nutrients": [
                        {
                            "name": n.get('nutrient', {}).get('name'),
                            "amount": n.get('amount'),
                            "unit": n.get('nutrient', {}).get('unitName')
                        }
                        for n in food_nutrients
                    ]
                })

        return {
            "foods": results,
            "count": len(results)
        }

    def _search_farmers_markets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for farmers markets"""
        location = params.get('location', '')
        zipcode = params.get('zipcode', '')

        if not location and not zipcode:
            return {"error": "Location or zipcode is required"}

        # Using USDA Farmers Market API
        try:
            if zipcode:
                url = f"https://search.ams.usda.gov/farmersmarkets/v1/data.svc/zipSearch?zip={zipcode}"
            else:
                url = f"https://search.ams.usda.gov/farmersmarkets/v1/data.svc/locSearch?location={location}"

            response = requests.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])

                return {
                    "search_location": location or zipcode,
                    "farmers_markets": [
                        {
                            "id": market.get('id'),
                            "name": market.get('marketname')
                        }
                        for market in results
                    ],
                    "count": len(results)
                }
            else:
                return {"error": f"Request failed with status {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def _get_crop_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get crop production and yield data"""
        commodity = params.get('commodity', '')
        state = params.get('state', '')
        year = params.get('year', '')

        if not commodity:
            return {"error": "Commodity name is required"}

        nass_params = {
            'commodity_desc': commodity.upper(),
            'statisticcat_desc': 'PRODUCTION'
        }

        if state:
            nass_params['state_name'] = state.upper()
        if year:
            nass_params['year'] = year

        result = self._make_nass_request(nass_params)

        if 'error' not in result:
            data = result.get('data', [])

            return {
                "commodity": commodity,
                "state": state,
                "year": year,
                "crop_data": [
                    {
                        "year": item.get('year'),
                        "state": item.get('state_name'),
                        "value": item.get('Value'),
                        "unit": item.get('unit_desc')
                    }
                    for item in data
                ],
                "count": len(data)
            }
        return result

    def _get_livestock_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get livestock inventory and production data"""
        animal_type = params.get('animal_type', '')
        state = params.get('state', '')
        year = params.get('year', '')

        if not animal_type:
            return {"error": "Animal type is required (e.g., CATTLE, HOGS, CHICKENS)"}

        nass_params = {
            'commodity_desc': animal_type.upper(),
            'statisticcat_desc': 'INVENTORY'
        }

        if state:
            nass_params['state_name'] = state.upper()
        if year:
            nass_params['year'] = year

        result = self._make_nass_request(nass_params)

        if 'error' not in result:
            data = result.get('data', [])

            return {
                "animal_type": animal_type,
                "state": state,
                "year": year,
                "livestock_data": [
                    {
                        "year": item.get('year'),
                        "state": item.get('state_name'),
                        "count": item.get('Value'),
                        "unit": item.get('unit_desc')
                    }
                    for item in data
                ],
                "count": len(data)
            }
        return result

    def _search_organic_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get organic agriculture data"""
        commodity = params.get('commodity', '')
        state = params.get('state', '')
        year = params.get('year', '')

        nass_params = {
            'util_practice_desc': 'ORGANIC',
            'statisticcat_desc': 'PRODUCTION'
        }

        if commodity:
            nass_params['commodity_desc'] = commodity.upper()
        if state:
            nass_params['state_name'] = state.upper()
        if year:
            nass_params['year'] = year

        result = self._make_nass_request(nass_params)

        if 'error' not in result:
            data = result.get('data', [])

            return {
                "commodity": commodity,
                "state": state,
                "year": year,
                "organic_data": [
                    {
                        "commodity": item.get('commodity_desc'),
                        "year": item.get('year'),
                        "state": item.get('state_name'),
                        "value": item.get('Value'),
                        "unit": item.get('unit_desc')
                    }
                    for item in data
                ],
                "count": len(data)
            }
        return result

    def _get_food_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get food price data"""
        commodity = params.get('commodity', '')
        year = params.get('year', '')

        if not commodity:
            return {"error": "Commodity is required"}

        nass_params = {
            'commodity_desc': commodity.upper(),
            'statisticcat_desc': 'PRICE RECEIVED'
        }

        if year:
            nass_params['year'] = year

        result = self._make_nass_request(nass_params)

        if 'error' not in result:
            data = result.get('data', [])

            # Calculate average price
            prices = [float(item.get('Value', 0)) for item in data if item.get('Value')]
            avg_price = sum(prices) / len(prices) if prices else 0

            return {
                "commodity": commodity,
                "year": year,
                "price_data": [
                    {
                        "year": item.get('year'),
                        "period": item.get('period_desc'),
                        "price": item.get('Value'),
                        "unit": item.get('unit_desc')
                    }
                    for item in data
                ],
                "average_price": avg_price,
                "count": len(data)
            }
        return result

    def _search_nutrition_programs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search USDA nutrition assistance programs"""
        program_type = params.get('program_type', '')  # SNAP, WIC, School Lunch
        state = params.get('state', '')
        year = params.get('year', '')

        # This would integrate with USDA FNS data
        # Placeholder for demonstration
        return {
            "program_type": program_type,
            "state": state,
            "year": year,
            "info": "Nutrition program data available through USDA Food and Nutrition Service",
            "programs": [
                {"name": "SNAP", "description": "Supplemental Nutrition Assistance Program"},
                {"name": "WIC", "description": "Women, Infants, and Children"},
                {"name": "NSLP", "description": "National School Lunch Program"},
                {"name": "SBP", "description": "School Breakfast Program"}
            ]
        }

    def _get_dietary_guidelines(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get USDA dietary guidelines"""
        category = params.get('category', '')  # vegetables, fruits, grains, protein, dairy
        age_group = params.get('age_group', '')

        guidelines = {
            "vegetables": "2-3 cups per day",
            "fruits": "1.5-2 cups per day",
            "grains": "6-8 ounces per day",
            "protein": "5-6.5 ounces per day",
            "dairy": "3 cups per day"
        }

        if category:
            return {
                "category": category,
                "age_group": age_group,
                "guideline": guidelines.get(category.lower(), "Category not found"),
                "source": "USDA Dietary Guidelines 2020-2025"
            }
        else:
            return {
                "age_group": age_group,
                "guidelines": guidelines,
                "source": "USDA Dietary Guidelines 2020-2025"
            }

    def _search_food_recalls(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search food recalls"""
        keyword = params.get('keyword', '')
        start_date = params.get('start_date', '')
        end_date = params.get('end_date', '')

        # This would integrate with FSIS recall data
        return {
            "keyword": keyword,
            "date_range": f"{start_date} to {end_date}",
            "info": "Food recall data available through USDA FSIS",
            "source": "https://www.fsis.usda.gov/recalls"
        }

    def _get_commodity_prices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get agricultural commodity prices"""
        commodity = params.get('commodity', '')
        market_type = params.get('market_type', 'CASH')
        year = params.get('year', '')

        if not commodity:
            return {"error": "Commodity is required"}

        nass_params = {
            'commodity_desc': commodity.upper(),
            'statisticcat_desc': 'PRICE RECEIVED',
            'agg_level_desc': 'NATIONAL'
        }

        if year:
            nass_params['year'] = year

        result = self._make_nass_request(nass_params)

        if 'error' not in result:
            data = result.get('data', [])

            return {
                "commodity": commodity,
                "market_type": market_type,
                "year": year,
                "prices": [
                    {
                        "date": f"{item.get('year')}-{item.get('period_desc')}",
                        "price": item.get('Value'),
                        "unit": item.get('unit_desc')
                    }
                    for item in data
                ],
                "count": len(data)
            }
        return result

    def _search_agricultural_census(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search agricultural census data"""
        state = params.get('state', '')
        sector = params.get('sector', '')  # CROPS, ANIMALS, ECONOMICS
        year = params.get('year', '2017')

        nass_params = {
            'source_desc': 'CENSUS',
            'census_year': year
        }

        if state:
            nass_params['state_name'] = state.upper()
        if sector:
            nass_params['sector_desc'] = sector.upper()

        result = self._make_nass_request(nass_params)

        if 'error' not in result:
            data = result.get('data', [])

            return {
                "state": state,
                "sector": sector,
                "year": year,
                "census_data": [
                    {
                        "category": item.get('short_desc'),
                        "value": item.get('Value'),
                        "unit": item.get('unit_desc')
                    }
                    for item in data[:100]  # Limit results
                ],
                "count": len(data)
            }
        return result

    def _get_soil_survey_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get soil survey data"""
        state = params.get('state', '')
        county = params.get('county', '')

        # This would integrate with NRCS Soil Data Access
        return {
            "state": state,
            "county": county,
            "info": "Soil survey data available through USDA NRCS Web Soil Survey",
            "source": "https://websoilsurvey.nrcs.usda.gov/"
        }