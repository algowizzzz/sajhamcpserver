"""
Zillow MCP Tool implementation
"""
import requests
from typing import Dict, Any, List, Optional
from .base_mcp_tool import BaseMCPTool


class ZillowMCPTool(BaseMCPTool):
    """MCP Tool for Zillow real estate operations"""

    def _initialize(self):
        """Initialize Zillow specific components"""
        self.api_key = self.config.get('api_key', '')
        self.base_url = self.config.get('base_url', 'https://zillow-com1.p.rapidapi.com')
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'zillow-com1.p.rapidapi.com'
        }
        self.timeout = 30

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Zillow tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            tool_methods = {
                "search_properties": self._search_properties,
                "get_property_details": self._get_property_details,
                "get_property_by_zpid": self._get_property_by_zpid,
                "get_zestimate": self._get_zestimate,
                "search_by_address": self._search_by_address,
                "get_similar_properties": self._get_similar_properties,
                "get_property_images": self._get_property_images,
                "get_market_trends": self._get_market_trends,
                "get_school_info": self._get_school_info,
                "get_mortgage_calculator": self._get_mortgage_calculator,
                "search_agents": self._search_agents,
                "get_rent_estimate": self._get_rent_estimate
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

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make API request to Zillow"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)

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

    def _search_properties(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for properties"""
        location = params.get('location', '')
        status = params.get('status', 'forSale')  # forSale, forRent, recentlySold
        home_type = params.get('home_type', '')  # Houses, Townhomes, Condos, Apartments
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        bedrooms = params.get('bedrooms')
        bathrooms = params.get('bathrooms')
        sort = params.get('sort', 'Homes_for_You')  # Price_High_Low, Price_Low_High, Newest, etc.
        page = params.get('page', 1)

        if not location:
            return {"error": "Location is required"}

        search_params = {
            'location': location,
            'status': status,
            'page': page,
            'sort': sort
        }

        if home_type:
            search_params['home_type'] = home_type
        if min_price:
            search_params['minPrice'] = min_price
        if max_price:
            search_params['maxPrice'] = max_price
        if bedrooms:
            search_params['beds'] = bedrooms
        if bathrooms:
            search_params['baths'] = bathrooms

        result = self._make_request('/propertyExtendedSearch', search_params)

        if 'error' not in result:
            return {
                "location": location,
                "status": status,
                "properties": result.get('props', []),
                "total_results": result.get('totalResultCount', 0),
                "page": page
            }
        return result

    def _get_property_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed property information"""
        property_url = params.get('property_url', '')

        if not property_url:
            return {"error": "Property URL is required"}

        result = self._make_request('/property', {'property_url': property_url})

        if 'error' not in result:
            property_data = result
            return {
                "zpid": property_data.get('zpid'),
                "address": property_data.get('address'),
                "price": property_data.get('price'),
                "bedrooms": property_data.get('bedrooms'),
                "bathrooms": property_data.get('bathrooms'),
                "living_area": property_data.get('livingArea'),
                "lot_size": property_data.get('lotSize'),
                "year_built": property_data.get('yearBuilt'),
                "property_type": property_data.get('homeType'),
                "description": property_data.get('description'),
                "zestimate": property_data.get('zestimate'),
                "rent_zestimate": property_data.get('rentZestimate'),
                "tax_assessed_value": property_data.get('taxAssessedValue'),
                "images": property_data.get('photos', []),
                "url": property_url
            }
        return result

    def _get_property_by_zpid(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get property by Zillow Property ID (ZPID)"""
        zpid = params.get('zpid', '')

        if not zpid:
            return {"error": "ZPID is required"}

        result = self._make_request('/propertyByZpid', {'zpid': zpid})

        if 'error' not in result:
            return {
                "zpid": zpid,
                "property_data": result
            }
        return result

    def _get_zestimate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Zestimate (Zillow's estimated market value)"""
        zpid = params.get('zpid', '')
        property_url = params.get('property_url', '')

        if not zpid and not property_url:
            return {"error": "ZPID or property URL is required"}

        if zpid:
            result = self._make_request('/zestimate', {'zpid': zpid})
        else:
            result = self._make_request('/zestimate', {'property_url': property_url})

        if 'error' not in result:
            return {
                "zestimate": result.get('zestimate'),
                "value_change": result.get('valueChange'),
                "valuation_range": result.get('valuationRange'),
                "last_updated": result.get('lastUpdated')
            }
        return result

    def _search_by_address(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for property by specific address"""
        address = params.get('address', '')
        city = params.get('city', '')
        state = params.get('state', '')
        zipcode = params.get('zipcode', '')

        if not address:
            return {"error": "Address is required"}

        full_address = f"{address}, {city}, {state} {zipcode}".strip(', ')

        result = self._make_request('/searchByAddress', {'address': full_address})

        if 'error' not in result:
            return {
                "address": full_address,
                "properties": result.get('results', []),
                "match_count": len(result.get('results', []))
            }
        return result

    def _get_similar_properties(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get similar properties (comparables)"""
        zpid = params.get('zpid', '')

        if not zpid:
            return {"error": "ZPID is required"}

        result = self._make_request('/similarProperties', {'zpid': zpid})

        if 'error' not in result:
            return {
                "zpid": zpid,
                "similar_properties": result.get('comparables', []),
                "count": len(result.get('comparables', []))
            }
        return result

    def _get_property_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get property images"""
        zpid = params.get('zpid', '')

        if not zpid:
            return {"error": "ZPID is required"}

        result = self._make_request('/images', {'zpid': zpid})

        if 'error' not in result:
            return {
                "zpid": zpid,
                "images": result.get('images', []),
                "count": len(result.get('images', []))
            }
        return result

    def _get_market_trends(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get market trends for a location"""
        location = params.get('location', '')
        region_type = params.get('region_type', 'city')  # city, county, zip, neighborhood

        if not location:
            return {"error": "Location is required"}

        result = self._make_request('/marketTrends', {
            'location': location,
            'regionType': region_type
        })

        if 'error' not in result:
            return {
                "location": location,
                "median_home_value": result.get('medianHomeValue'),
                "median_rent": result.get('medianRent'),
                "value_change": result.get('valueChange'),
                "price_per_sqft": result.get('pricePerSqft'),
                "inventory": result.get('inventory'),
                "data_date": result.get('dataDate')
            }
        return result

    def _get_school_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get school information for a property"""
        zpid = params.get('zpid', '')

        if not zpid:
            return {"error": "ZPID is required"}

        result = self._make_request('/schools', {'zpid': zpid})

        if 'error' not in result:
            return {
                "zpid": zpid,
                "schools": result.get('schools', []),
                "count": len(result.get('schools', []))
            }
        return result

    def _get_mortgage_calculator(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate mortgage payment"""
        price = params.get('price', 0)
        down_payment = params.get('down_payment', 0)
        interest_rate = params.get('interest_rate', 0)
        loan_term = params.get('loan_term', 30)  # years

        if not price or not interest_rate:
            return {"error": "Price and interest rate are required"}

        loan_amount = price - down_payment
        monthly_rate = interest_rate / 100 / 12
        num_payments = loan_term * 12

        # Calculate monthly payment using mortgage formula
        if monthly_rate > 0:
            monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                              ((1 + monthly_rate) ** num_payments - 1)
        else:
            monthly_payment = loan_amount / num_payments

        total_paid = monthly_payment * num_payments
        total_interest = total_paid - loan_amount

        return {
            "price": price,
            "down_payment": down_payment,
            "loan_amount": loan_amount,
            "interest_rate": interest_rate,
            "loan_term_years": loan_term,
            "monthly_payment": round(monthly_payment, 2),
            "total_interest": round(total_interest, 2),
            "total_paid": round(total_paid, 2)
        }

    def _search_agents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for real estate agents"""
        location = params.get('location', '')
        specialty = params.get('specialty', '')  # buyer, seller, rental

        if not location:
            return {"error": "Location is required"}

        search_params = {'location': location}
        if specialty:
            search_params['specialty'] = specialty

        result = self._make_request('/agents', search_params)

        if 'error' not in result:
            return {
                "location": location,
                "agents": result.get('agents', []),
                "count": len(result.get('agents', []))
            }
        return result

    def _get_rent_estimate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get rent estimate (Rent Zestimate)"""
        zpid = params.get('zpid', '')

        if not zpid:
            return {"error": "ZPID is required"}

        result = self._make_request('/rentEstimate', {'zpid': zpid})

        if 'error' not in result:
            return {
                "zpid": zpid,
                "rent_zestimate": result.get('rentZestimate'),
                "rent_range": result.get('rentRange'),
                "last_updated": result.get('lastUpdated')
            }
        return result