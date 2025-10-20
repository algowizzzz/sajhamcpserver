"""
Trulia MCP Tool implementation
"""
import requests
from typing import Dict, Any, List, Optional
from .base_mcp_tool import BaseMCPTool


class TruliaMCPTool(BaseMCPTool):
    """MCP Tool for Trulia real estate operations"""

    def _initialize(self):
        """Initialize Trulia specific components"""
        self.api_key = self.config.get('api_key', '')
        self.base_url = self.config.get('base_url', 'https://trulia-com-data.p.rapidapi.com')
        self.headers = {
            'X-RapidAPI-Key': self.api_key,
            'X-RapidAPI-Host': 'trulia-com-data.p.rapidapi.com'
        }
        self.timeout = 30

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Trulia tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            tool_methods = {
                "search_properties": self._search_properties,
                "get_property_details": self._get_property_details,
                "search_by_coordinates": self._search_by_coordinates,
                "get_neighborhood_info": self._get_neighborhood_info,
                "get_crime_data": self._get_crime_data,
                "get_school_ratings": self._get_school_ratings,
                "get_commute_time": self._get_commute_time,
                "search_rentals": self._search_rentals,
                "get_local_amenities": self._get_local_amenities,
                "get_price_history": self._get_price_history,
                "get_tax_history": self._get_tax_history,
                "search_new_homes": self._search_new_homes,
                "get_open_houses": self._get_open_houses,
                "get_saved_searches": self._get_saved_searches
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
        """Make API request to Trulia"""
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
        property_type = params.get('property_type', 'for_sale')  # for_sale, for_rent
        home_type = params.get('home_type', [])  # Single_Family_Home, Condo, Townhome, etc.
        min_price = params.get('min_price')
        max_price = params.get('max_price')
        min_beds = params.get('min_beds')
        max_beds = params.get('max_beds')
        min_baths = params.get('min_baths')
        max_baths = params.get('max_baths')
        min_sqft = params.get('min_sqft')
        max_sqft = params.get('max_sqft')
        sort_by = params.get('sort_by', 'relevance')  # relevance, price_low, price_high, newest
        page = params.get('page', 1)

        if not location:
            return {"error": "Location is required"}

        search_params = {
            'location': location,
            'propertyType': property_type,
            'page': page,
            'sortBy': sort_by
        }

        if home_type:
            search_params['homeType'] = home_type
        if min_price:
            search_params['minPrice'] = min_price
        if max_price:
            search_params['maxPrice'] = max_price
        if min_beds:
            search_params['minBeds'] = min_beds
        if max_beds:
            search_params['maxBeds'] = max_beds
        if min_baths:
            search_params['minBaths'] = min_baths
        if max_baths:
            search_params['maxBaths'] = max_baths
        if min_sqft:
            search_params['minSqft'] = min_sqft
        if max_sqft:
            search_params['maxSqft'] = max_sqft

        result = self._make_request('/search', search_params)

        if 'error' not in result:
            return {
                "location": location,
                "property_type": property_type,
                "properties": result.get('listings', []),
                "total_count": result.get('totalCount', 0),
                "page": page
            }
        return result

    def _get_property_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed property information"""
        property_id = params.get('property_id', '')
        property_url = params.get('property_url', '')

        if not property_id and not property_url:
            return {"error": "Property ID or URL is required"}

        search_param = {'propertyId': property_id} if property_id else {'propertyUrl': property_url}
        result = self._make_request('/property/details', search_param)

        if 'error' not in result:
            property_data = result.get('property', {})
            return {
                "property_id": property_data.get('id'),
                "address": property_data.get('address'),
                "price": property_data.get('price'),
                "bedrooms": property_data.get('bedrooms'),
                "bathrooms": property_data.get('bathrooms'),
                "square_feet": property_data.get('squareFeet'),
                "lot_size": property_data.get('lotSize'),
                "year_built": property_data.get('yearBuilt'),
                "property_type": property_data.get('propertyType'),
                "description": property_data.get('description'),
                "features": property_data.get('features', []),
                "hoa_fee": property_data.get('hoaFee'),
                "parking": property_data.get('parking'),
                "heating": property_data.get('heating'),
                "cooling": property_data.get('cooling'),
                "images": property_data.get('photos', []),
                "virtual_tour": property_data.get('virtualTour'),
                "listing_date": property_data.get('listingDate'),
                "days_on_market": property_data.get('daysOnMarket')
            }
        return result

    def _search_by_coordinates(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for properties by geographic coordinates"""
        latitude = params.get('latitude')
        longitude = params.get('longitude')
        radius = params.get('radius', 5)  # miles
        property_type = params.get('property_type', 'for_sale')

        if latitude is None or longitude is None:
            return {"error": "Latitude and longitude are required"}

        result = self._make_request('/search/coordinates', {
            'lat': latitude,
            'lon': longitude,
            'radius': radius,
            'propertyType': property_type
        })

        if 'error' not in result:
            return {
                "coordinates": {"latitude": latitude, "longitude": longitude},
                "radius_miles": radius,
                "properties": result.get('listings', []),
                "count": len(result.get('listings', []))
            }
        return result

    def _get_neighborhood_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get neighborhood information"""
        location = params.get('location', '')

        if not location:
            return {"error": "Location is required"}

        result = self._make_request('/neighborhood', {'location': location})

        if 'error' not in result:
            neighborhood = result.get('neighborhood', {})
            return {
                "location": location,
                "name": neighborhood.get('name'),
                "description": neighborhood.get('description'),
                "median_home_value": neighborhood.get('medianHomeValue'),
                "median_rent": neighborhood.get('medianRent'),
                "population": neighborhood.get('population'),
                "demographics": neighborhood.get('demographics', {}),
                "walkability_score": neighborhood.get('walkScore'),
                "transit_score": neighborhood.get('transitScore'),
                "bike_score": neighborhood.get('bikeScore'),
                "nearby_neighborhoods": neighborhood.get('nearbyNeighborhoods', [])
            }
        return result

    def _get_crime_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get crime statistics for an area"""
        location = params.get('location', '')

        if not location:
            return {"error": "Location is required"}

        result = self._make_request('/crime', {'location': location})

        if 'error' not in result:
            crime_data = result.get('crimeData', {})
            return {
                "location": location,
                "overall_crime_grade": crime_data.get('overallGrade'),
                "violent_crime": crime_data.get('violentCrime'),
                "property_crime": crime_data.get('propertyCrime'),
                "crime_rate": crime_data.get('crimeRate'),
                "comparison_to_national": crime_data.get('comparisonToNational'),
                "yearly_trends": crime_data.get('yearlyTrends', [])
            }
        return result

    def _get_school_ratings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get school ratings and information"""
        location = params.get('location', '')
        property_id = params.get('property_id', '')

        if not location and not property_id:
            return {"error": "Location or property ID is required"}

        search_param = {'propertyId': property_id} if property_id else {'location': location}
        result = self._make_request('/schools', search_param)

        if 'error' not in result:
            return {
                "elementary_schools": result.get('elementarySchools', []),
                "middle_schools": result.get('middleSchools', []),
                "high_schools": result.get('highSchools', []),
                "private_schools": result.get('privateSchools', []),
                "district_rating": result.get('districtRating')
            }
        return result

    def _get_commute_time(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate commute time from property"""
        property_location = params.get('property_location', '')
        destination = params.get('destination', '')
        travel_mode = params.get('travel_mode', 'driving')  # driving, transit, walking, bicycling

        if not property_location or not destination:
            return {"error": "Property location and destination are required"}

        result = self._make_request('/commute', {
            'from': property_location,
            'to': destination,
            'mode': travel_mode
        })

        if 'error' not in result:
            return {
                "from": property_location,
                "to": destination,
                "travel_mode": travel_mode,
                "duration_minutes": result.get('duration'),
                "distance_miles": result.get('distance'),
                "traffic_condition": result.get('trafficCondition')
            }
        return result

    def _search_rentals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search specifically for rental properties"""
        location = params.get('location', '')
        min_rent = params.get('min_rent')
        max_rent = params.get('max_rent')
        bedrooms = params.get('bedrooms')
        bathrooms = params.get('bathrooms')
        pets_allowed = params.get('pets_allowed')

        if not location:
            return {"error": "Location is required"}

        search_params = {
            'location': location,
            'propertyType': 'for_rent'
        }

        if min_rent:
            search_params['minRent'] = min_rent
        if max_rent:
            search_params['maxRent'] = max_rent
        if bedrooms:
            search_params['beds'] = bedrooms
        if bathrooms:
            search_params['baths'] = bathrooms
        if pets_allowed is not None:
            search_params['petsAllowed'] = pets_allowed

        result = self._make_request('/rentals', search_params)

        if 'error' not in result:
            return {
                "location": location,
                "rentals": result.get('listings', []),
                "total_count": result.get('totalCount', 0)
            }
        return result

    def _get_local_amenities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get local amenities near a property"""
        location = params.get('location', '')
        amenity_type = params.get('amenity_type', 'all')  # all, restaurants, shopping, parks, etc.
        radius = params.get('radius', 1)  # miles

        if not location:
            return {"error": "Location is required"}

        result = self._make_request('/amenities', {
            'location': location,
            'type': amenity_type,
            'radius': radius
        })

        if 'error' not in result:
            return {
                "location": location,
                "amenity_type": amenity_type,
                "radius_miles": radius,
                "restaurants": result.get('restaurants', []),
                "shopping": result.get('shopping', []),
                "parks": result.get('parks', []),
                "entertainment": result.get('entertainment', []),
                "healthcare": result.get('healthcare', [])
            }
        return result

    def _get_price_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get price history for a property"""
        property_id = params.get('property_id', '')

        if not property_id:
            return {"error": "Property ID is required"}

        result = self._make_request('/property/priceHistory', {'propertyId': property_id})

        if 'error' not in result:
            return {
                "property_id": property_id,
                "price_history": result.get('priceHistory', []),
                "current_price": result.get('currentPrice'),
                "original_list_price": result.get('originalListPrice'),
                "price_changes": result.get('priceChanges', [])
            }
        return result

    def _get_tax_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get tax history for a property"""
        property_id = params.get('property_id', '')

        if not property_id:
            return {"error": "Property ID is required"}

        result = self._make_request('/property/taxHistory', {'propertyId': property_id})

        if 'error' not in result:
            return {
                "property_id": property_id,
                "tax_history": result.get('taxHistory', []),
                "current_tax_amount": result.get('currentTaxAmount'),
                "tax_assessment": result.get('taxAssessment')
            }
        return result

    def _search_new_homes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for new construction homes"""
        location = params.get('location', '')
        builder = params.get('builder', '')
        min_price = params.get('min_price')
        max_price = params.get('max_price')

        if not location:
            return {"error": "Location is required"}

        search_params = {'location': location, 'newConstruction': True}

        if builder:
            search_params['builder'] = builder
        if min_price:
            search_params['minPrice'] = min_price
        if max_price:
            search_params['maxPrice'] = max_price

        result = self._make_request('/newHomes', search_params)

        if 'error' not in result:
            return {
                "location": location,
                "new_homes": result.get('listings', []),
                "builders": result.get('builders', []),
                "count": len(result.get('listings', []))
            }
        return result

    def _get_open_houses(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get open house listings"""
        location = params.get('location', '')
        date = params.get('date', '')  # YYYY-MM-DD format

        if not location:
            return {"error": "Location is required"}

        search_params = {'location': location}
        if date:
            search_params['date'] = date

        result = self._make_request('/openHouses', search_params)

        if 'error' not in result:
            return {
                "location": location,
                "date": date if date else "all upcoming",
                "open_houses": result.get('openHouses', []),
                "count": len(result.get('openHouses', []))
            }
        return result

    def _get_saved_searches(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get saved search criteria (for authenticated users)"""
        user_id = params.get('user_id', '')

        if not user_id:
            return {"error": "User ID is required"}

        result = self._make_request('/savedSearches', {'userId': user_id})

        if 'error' not in result:
            return {
                "user_id": user_id,
                "saved_searches": result.get('searches', []),
                "count": len(result.get('searches', []))
            }
        return result