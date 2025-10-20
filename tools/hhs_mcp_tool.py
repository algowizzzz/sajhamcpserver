"""
US Health and Human Services (HHS) MCP Tool implementation
"""
import requests
from typing import Dict, Any, List, Optional
from .base_mcp_tool import BaseMCPTool


class HHSMCPTool(BaseMCPTool):
    """MCP Tool for US Health and Human Services data"""

    def _initialize(self):
        """Initialize HHS specific components"""
        self.api_key = self.config.get('api_key', '')
        self.base_url = self.config.get('base_url', 'https://healthdata.gov/api/3')
        self.timeout = 30
        self.headers = {}
        if self.api_key:
            self.headers['X-API-Key'] = self.api_key

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HHS tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            tool_methods = {
                "search_datasets": self._search_datasets,
                "get_dataset": self._get_dataset,
                "search_hospitals": self._search_hospitals,
                "get_hospital_quality": self._get_hospital_quality,
                "get_medicare_data": self._get_medicare_data,
                "get_public_health_stats": self._get_public_health_stats,
                "search_health_indicators": self._search_health_indicators,
                "get_disease_surveillance": self._get_disease_surveillance,
                "get_healthcare_spending": self._get_healthcare_spending,
                "search_nursing_homes": self._search_nursing_homes,
                "get_vaccination_data": self._get_vaccination_data,
                "get_opioid_data": self._get_opioid_data,
                "search_community_health": self._search_community_health,
                "get_health_disparities": self._get_health_disparities
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
        """Make API request to HHS"""
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

    def _search_datasets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search HHS datasets"""
        query = params.get('query', '')
        limit = params.get('limit', 20)
        offset = params.get('offset', 0)

        if not query:
            return {"error": "Query is required"}

        result = self._make_request('/action/package_search', {
            'q': query,
            'rows': limit,
            'start': offset
        })

        if 'error' not in result:
            return {
                "query": query,
                "datasets": result.get('result', {}).get('results', []),
                "count": result.get('result', {}).get('count', 0)
            }
        return result

    def _get_dataset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get specific dataset by ID"""
        dataset_id = params.get('dataset_id', '')

        if not dataset_id:
            return {"error": "Dataset ID is required"}

        result = self._make_request('/action/package_show', {
            'id': dataset_id
        })

        if 'error' not in result:
            dataset = result.get('result', {})
            return {
                "id": dataset.get('id'),
                "name": dataset.get('name'),
                "title": dataset.get('title'),
                "description": dataset.get('notes'),
                "organization": dataset.get('organization', {}).get('title'),
                "resources": dataset.get('resources', []),
                "tags": [tag.get('name') for tag in dataset.get('tags', [])],
                "metadata_created": dataset.get('metadata_created'),
                "metadata_modified": dataset.get('metadata_modified')
            }
        return result

    def _search_hospitals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for hospitals"""
        state = params.get('state', '')
        city = params.get('city', '')
        hospital_type = params.get('hospital_type', '')
        limit = params.get('limit', 50)

        search_params = {'limit': limit}

        filters = []
        if state:
            filters.append(f"state='{state}'")
        if city:
            filters.append(f"city='{city}'")
        if hospital_type:
            filters.append(f"hospital_type='{hospital_type}'")

        if filters:
            search_params['where'] = ' AND '.join(filters)

        # Using Hospital General Information dataset
        result = self._make_request('/action/datastore_search', {
            'resource_id': 'hospital-general-information',
            **search_params
        })

        if 'error' not in result:
            records = result.get('result', {}).get('records', [])
            return {
                "hospitals": records,
                "count": len(records),
                "filters": {"state": state, "city": city, "type": hospital_type}
            }
        return result

    def _get_hospital_quality(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get hospital quality ratings and measures"""
        hospital_id = params.get('hospital_id', '')
        measure_type = params.get('measure_type', 'all')  # mortality, safety, readmission, patient_experience

        if not hospital_id:
            return {"error": "Hospital ID is required"}

        result = self._make_request('/action/datastore_search', {
            'resource_id': 'hospital-quality-measures',
            'filters': {'provider_id': hospital_id}
        })

        if 'error' not in result:
            measures = result.get('result', {}).get('records', [])

            if measure_type != 'all':
                measures = [m for m in measures if m.get('measure_category') == measure_type]

            return {
                "hospital_id": hospital_id,
                "measure_type": measure_type,
                "quality_measures": measures,
                "count": len(measures)
            }
        return result

    def _get_medicare_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get Medicare spending and utilization data"""
        state = params.get('state', '')
        year = params.get('year', '')
        category = params.get('category', '')  # inpatient, outpatient, prescription

        search_params = {}

        if state:
            search_params['state'] = state
        if year:
            search_params['year'] = year
        if category:
            search_params['category'] = category

        result = self._make_request('/action/datastore_search', {
            'resource_id': 'medicare-spending',
            'filters': search_params,
            'limit': 100
        })

        if 'error' not in result:
            records = result.get('result', {}).get('records', [])

            # Calculate aggregates
            total_spending = sum(float(r.get('amount', 0)) for r in records if r.get('amount'))

            return {
                "state": state,
                "year": year,
                "category": category,
                "records": records,
                "total_spending": total_spending,
                "count": len(records)
            }
        return result

    def _get_public_health_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get public health statistics"""
        indicator = params.get('indicator', '')
        state = params.get('state', '')
        year_start = params.get('year_start', '')
        year_end = params.get('year_end', '')

        search_params = {}

        if indicator:
            search_params['indicator'] = indicator
        if state:
            search_params['state'] = state

        result = self._make_request('/action/datastore_search', {
            'resource_id': 'public-health-indicators',
            'filters': search_params,
            'limit': 200
        })

        if 'error' not in result:
            records = result.get('result', {}).get('records', [])

            # Filter by year range if provided
            if year_start or year_end:
                filtered_records = []
                for r in records:
                    year = int(r.get('year', 0))
                    if year_start and year < int(year_start):
                        continue
                    if year_end and year > int(year_end):
                        continue
                    filtered_records.append(r)
                records = filtered_records

            return {
                "indicator": indicator,
                "state": state,
                "year_range": f"{year_start or 'all'} to {year_end or 'present'}",
                "statistics": records,
                "count": len(records)
            }
        return result

    def _search_health_indicators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search health indicators by category"""
        category = params.get('category', '')  # chronic_disease, maternal_health, mental_health, etc.
        location = params.get('location', '')

        if not category:
            return {"error": "Category is required"}

        result = self._make_request('/action/datastore_search', {
            'resource_id': 'health-indicators',
            'q': category,
            'limit': 100
        })

        if 'error' not in result:
            indicators = result.get('result', {}).get('records', [])

            if location:
                indicators = [i for i in indicators if location.lower() in i.get('location', '').lower()]

            return {
                "category": category,
                "location": location,
                "indicators": indicators,
                "count": len(indicators)
            }
        return result

    def _get_disease_surveillance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get disease surveillance data"""
        disease = params.get('disease', '')
        state = params.get('state', '')
        start_date = params.get('start_date', '')
        end_date = params.get('end_date', '')

        if not disease:
            return {"error": "Disease name is required"}

        search_params = {'disease': disease}

        if state:
            search_params['state'] = state

        result = self._make_request('/action/datastore_search', {
            'resource_id': 'disease-surveillance',
            'filters': search_params,
            'limit': 500
        })

        if 'error' not in result:
            records = result.get('result', {}).get('records', [])

            # Calculate statistics
            total_cases = sum(int(r.get('case_count', 0)) for r in records)

            return {
                "disease": disease,
                "state": state,
                "date_range": f"{start_date or 'all'} to {end_date or 'present'}",
                "surveillance_data": records,
                "total_cases": total_cases,
                "count": len(records)
            }
        return result

    def _get_healthcare_spending(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get healthcare spending data"""
        state = params.get('state', '')
        year = params.get('year', '')
        spending_type = params.get('spending_type', '')  # hospital, physician, prescription, etc.

        search_params = {}

        if state:
            search_params['state'] = state
        if year:
            search_params['year'] = year
        if spending_type:
            search_params['type'] = spending_type

        result = self._make_request('/action/datastore_search', {
            'resource_id': 'healthcare-spending',
            'filters': search_params,
            'limit': 100
        })

        if 'error' not in result:
            records = result.get('result', {}).get('records', [])

            total_spending = sum(float(r.get('spending', 0)) for r in records if r.get('spending'))
            per_capita = total_spending / float(records[0].get('population', 1)) if records else 0

            return {
                "state": state,
                "year": year,
                "spending_type": spending_type,
                "spending_data": records,
                "total_spending": total_spending,
                "per_capita_spending": per_capita,
                "count": len(records)
            }
        return result

    def _search_nursing_homes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search nursing homes and quality ratings"""
        state = params.get('state', '')
        city = params.get('city', '')
        min_rating = params.get('min_rating', 1)
        limit = params.get('limit', 50)

        search_params = {'limit': limit}

        filters = []
        if state:
            filters.append(f"state='{state}'")
        if city:
            filters.append(f"city='{city}'")
        if min_rating:
            filters.append(f"overall_rating>={min_rating}")

        if filters:
            search_params['where'] = ' AND '.join(filters)

        result = self._make_request('/action/datastore_search', {
            'resource_id': 'nursing-home-compare',
            **search_params
        })

        if 'error' not in result:
            facilities = result.get('result', {}).get('records', [])

            return {
                "state": state,
                "city": city,
                "min_rating": min_rating,
                "nursing_homes": facilities,
                "count": len(facilities)
            }
        return result

    def _get_vaccination_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get vaccination coverage data"""
        vaccine_type = params.get('vaccine_type', '')
        state = params.get('state', '')
        age_group = params.get('age_group', '')
        year = params.get('year', '')

        search_params = {}

        if vaccine_type:
            search_params['vaccine'] = vaccine_type
        if state:
            search_params['state'] = state
        if age_group:
            search_params['age_group'] = age_group
        if year:
            search_params['year'] = year

        result = self._make_request('/action/datastore_search', {
            'resource_id': 'vaccination-coverage',
            'filters': search_params,
            'limit': 200
        })

        if 'error' not in result:
            records = result.get('result', {}).get('records', [])

            # Calculate coverage statistics
            avg_coverage = sum(float(r.get('coverage_rate', 0)) for r in records) / len(records) if records else 0

            return {
                "vaccine_type": vaccine_type,
                "state": state,
                "age_group": age_group,
                "year": year,
                "vaccination_data": records,
                "average_coverage": avg_coverage,
                "count": len(records)
            }
        return result

    def _get_opioid_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get opioid prescription and overdose data"""
        state = params.get('state', '')
        year = params.get('year', '')
        data_type = params.get('data_type', 'all')  # prescriptions, overdoses, treatment

        search_params = {}

        if state:
            search_params['state'] = state
        if year:
            search_params['year'] = year
        if data_type != 'all':
            search_params['data_type'] = data_type

        result = self._make_request('/action/datastore_search', {
            'resource_id': 'opioid-data',
            'filters': search_params,
            'limit': 200
        })

        if 'error' not in result:
            records = result.get('result', {}).get('records', [])

            return {
                "state": state,
                "year": year,
                "data_type": data_type,
                "opioid_data": records,
                "count": len(records)
            }
        return result

    def _search_community_health(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search community health centers"""
        state = params.get('state', '')
        county = params.get('county', '')
        service_type = params.get('service_type', '')
        limit = params.get('limit', 50)

        search_params = {'limit': limit}

        filters = []
        if state:
            filters.append(f"state='{state}'")
        if county:
            filters.append(f"county='{county}'")
        if service_type:
            filters.append(f"services LIKE '%{service_type}%'")

        if filters:
            search_params['where'] = ' AND '.join(filters)

        result = self._make_request('/action/datastore_search', {
            'resource_id': 'community-health-centers',
            **search_params
        })

        if 'error' not in result:
            centers = result.get('result', {}).get('records', [])

            return {
                "state": state,
                "county": county,
                "service_type": service_type,
                "health_centers": centers,
                "count": len(centers)
            }
        return result

    def _get_health_disparities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get health disparity data"""
        indicator = params.get('indicator', '')
        demographic = params.get('demographic', '')  # race, income, education
        state = params.get('state', '')

        if not indicator:
            return {"error": "Health indicator is required"}

        search_params = {'indicator': indicator}

        if demographic:
            search_params['demographic'] = demographic
        if state:
            search_params['state'] = state

        result = self._make_request('/action/datastore_search', {
            'resource_id': 'health-disparities',
            'filters': search_params,
            'limit': 200
        })

        if 'error' not in result:
            records = result.get('result', {}).get('records', [])

            return {
                "indicator": indicator,
                "demographic": demographic,
                "state": state,
                "disparity_data": records,
                "count": len(records)
            }
        return result