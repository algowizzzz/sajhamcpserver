"""
US Food and Drug Administration (FDA) MCP Tool implementation
"""
import requests
from typing import Dict, Any, List, Optional
from .base_mcp_tool import BaseMCPTool


class FDAMCPTool(BaseMCPTool):
    """MCP Tool for FDA data including drugs, devices, and food safety"""

    def _initialize(self):
        """Initialize FDA specific components"""
        self.api_key = self.config.get('api_key', '')
        self.base_url = 'https://api.fda.gov'
        self.timeout = 30

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle FDA tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            tool_methods = {
                "search_drugs": self._search_drugs,
                "get_drug_label": self._get_drug_label,
                "get_drug_adverse_events": self._get_drug_adverse_events,
                "search_medical_devices": self._search_medical_devices,
                "get_device_recalls": self._get_device_recalls,
                "get_device_adverse_events": self._get_device_adverse_events,
                "search_food_recalls": self._search_food_recalls,
                "get_food_enforcement": self._get_food_enforcement,
                "search_ndc_directory": self._search_ndc_directory,
                "get_drug_approvals": self._get_drug_approvals,
                "search_clinical_trials": self._search_clinical_trials,
                "get_generic_drugs": self._get_generic_drugs,
                "search_510k_devices": self._search_510k_devices,
                "get_drug_shortages": self._get_drug_shortages
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
        """Make API request to FDA"""
        try:
            url = f"{self.base_url}{endpoint}"
            if params is None:
                params = {}
            if self.api_key:
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

    def _search_drugs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for drugs by name or active ingredient"""
        query = params.get('query', '')
        limit = params.get('limit', 10)

        if not query:
            return {"error": "Query is required"}

        search_params = {
            'search': f'openfda.brand_name:"{query}" OR openfda.generic_name:"{query}"',
            'limit': limit
        }

        result = self._make_request('/drug/label.json', search_params)

        if 'error' not in result:
            results = result.get('results', [])

            return {
                "query": query,
                "drugs": [
                    {
                        "brand_name": drug.get('openfda', {}).get('brand_name', ['N/A'])[0],
                        "generic_name": drug.get('openfda', {}).get('generic_name', ['N/A'])[0],
                        "manufacturer": drug.get('openfda', {}).get('manufacturer_name', ['N/A'])[0],
                        "product_type": drug.get('openfda', {}).get('product_type', ['N/A'])[0],
                        "route": drug.get('openfda', {}).get('route', []),
                        "substance_name": drug.get('openfda', {}).get('substance_name', [])
                    }
                    for drug in results
                ],
                "total": result.get('meta', {}).get('results', {}).get('total', 0),
                "count": len(results)
            }
        return result

    def _get_drug_label(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed drug label information"""
        drug_name = params.get('drug_name', '')

        if not drug_name:
            return {"error": "Drug name is required"}

        search_params = {
            'search': f'openfda.brand_name:"{drug_name}"',
            'limit': 1
        }

        result = self._make_request('/drug/label.json', search_params)

        if 'error' not in result:
            results = result.get('results', [])
            if not results:
                return {"error": "Drug not found"}

            drug = results[0]

            return {
                "drug_name": drug_name,
                "brand_name": drug.get('openfda', {}).get('brand_name', []),
                "generic_name": drug.get('openfda', {}).get('generic_name', []),
                "manufacturer": drug.get('openfda', {}).get('manufacturer_name', []),
                "purpose": drug.get('purpose', []),
                "indications_and_usage": drug.get('indications_and_usage', []),
                "dosage_and_administration": drug.get('dosage_and_administration', []),
                "warnings": drug.get('warnings', []),
                "adverse_reactions": drug.get('adverse_reactions', []),
                "drug_interactions": drug.get('drug_interactions', []),
                "active_ingredient": drug.get('active_ingredient', []),
                "inactive_ingredient": drug.get('inactive_ingredient', []),
                "when_using": drug.get('when_using', []),
                "stop_use": drug.get('stop_use', []),
                "pregnancy_category": drug.get('pregnancy', [])
            }
        return result

    def _get_drug_adverse_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get adverse event reports for a drug"""
        drug_name = params.get('drug_name', '')
        limit = params.get('limit', 100)

        if not drug_name:
            return {"error": "Drug name is required"}

        search_params = {
            'search': f'patient.drug.medicinalproduct:"{drug_name}"',
            'limit': limit,
            'count': 'patient.reaction.reactionmeddrapt.exact'
        }

        result = self._make_request('/drug/event.json', search_params)

        if 'error' not in result:
            reactions = result.get('results', [])

            return {
                "drug_name": drug_name,
                "adverse_events": [
                    {
                        "reaction": reaction.get('term'),
                        "count": reaction.get('count')
                    }
                    for reaction in reactions[:20]  # Top 20 reactions
                ],
                "total_reports": sum(r.get('count', 0) for r in reactions)
            }
        return result

    def _search_medical_devices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for medical devices"""
        query = params.get('query', '')
        device_class = params.get('device_class', '')  # 1, 2, or 3
        limit = params.get('limit', 10)

        if not query:
            return {"error": "Query is required"}

        search_query = f'device_name:"{query}"'
        if device_class:
            search_query += f' AND device_class:{device_class}'

        search_params = {
            'search': search_query,
            'limit': limit
        }

        result = self._make_request('/device/510k.json', search_params)

        if 'error' not in result:
            results = result.get('results', [])

            return {
                "query": query,
                "device_class": device_class,
                "devices": [
                    {
                        "device_name": device.get('device_name'),
                        "applicant": device.get('applicant'),
                        "k_number": device.get('k_number'),
                        "device_class": device.get('device_class'),
                        "decision_date": device.get('decision_date'),
                        "decision_description": device.get('decision_description')
                    }
                    for device in results
                ],
                "count": len(results)
            }
        return result

    def _get_device_recalls(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get medical device recalls"""
        device_name = params.get('device_name', '')
        classification = params.get('classification', '')  # Class I, II, or III
        start_date = params.get('start_date', '')
        limit = params.get('limit', 50)

        search_parts = []
        if device_name:
            search_parts.append(f'product_description:"{device_name}"')
        if classification:
            search_parts.append(f'classification:"{classification}"')
        if start_date:
            search_parts.append(f'recall_initiation_date:[{start_date} TO 20991231]')

        search_query = ' AND '.join(search_parts) if search_parts else '*'

        search_params = {
            'search': search_query,
            'limit': limit
        }

        result = self._make_request('/device/recall.json', search_params)

        if 'error' not in result:
            results = result.get('results', [])

            return {
                "device_name": device_name,
                "classification": classification,
                "recalls": [
                    {
                        "product_description": recall.get('product_description'),
                        "reason_for_recall": recall.get('reason_for_recall'),
                        "classification": recall.get('classification'),
                        "recall_number": recall.get('recall_number'),
                        "recall_initiation_date": recall.get('recall_initiation_date'),
                        "firm_name": recall.get('firm_fei_number')
                    }
                    for recall in results
                ],
                "count": len(results)
            }
        return result

    def _get_device_adverse_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get adverse event reports for medical devices"""
        device_name = params.get('device_name', '')
        limit = params.get('limit', 100)

        if not device_name:
            return {"error": "Device name is required"}

        search_params = {
            'search': f'device.brand_name:"{device_name}"',
            'limit': limit,
            'count': 'device.generic_name.exact'
        }

        result = self._make_request('/device/event.json', search_params)

        if 'error' not in result:
            events = result.get('results', [])

            return {
                "device_name": device_name,
                "adverse_events": events,
                "count": len(events)
            }
        return result

    def _search_food_recalls(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search food recalls"""
        product = params.get('product', '')
        reason = params.get('reason', '')
        classification = params.get('classification', '')  # Class I, II, III
        start_date = params.get('start_date', '')
        limit = params.get('limit', 50)

        search_parts = []
        if product:
            search_parts.append(f'product_description:"{product}"')
        if reason:
            search_parts.append(f'reason_for_recall:"{reason}"')
        if classification:
            search_parts.append(f'classification:"{classification}"')
        if start_date:
            search_parts.append(f'recall_initiation_date:[{start_date} TO 20991231]')

        search_query = ' AND '.join(search_parts) if search_parts else '*'

        search_params = {
            'search': search_query,
            'limit': limit,
            'sort': 'recall_initiation_date:desc'
        }

        result = self._make_request('/food/recall.json', search_params)

        if 'error' not in result:
            results = result.get('results', [])

            return {
                "product": product,
                "reason": reason,
                "recalls": [
                    {
                        "product_description": recall.get('product_description'),
                        "reason_for_recall": recall.get('reason_for_recall'),
                        "classification": recall.get('classification'),
                        "recall_number": recall.get('recall_number'),
                        "recall_initiation_date": recall.get('recall_initiation_date'),
                        "distribution_pattern": recall.get('distribution_pattern'),
                        "recalling_firm": recall.get('recalling_firm')
                    }
                    for recall in results
                ],
                "count": len(results)
            }
        return result

    def _get_food_enforcement(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get food enforcement actions"""
        product_type = params.get('product_type', '')
        state = params.get('state', '')
        limit = params.get('limit', 50)

        search_parts = []
        if product_type:
            search_parts.append(f'product_type:"{product_type}"')
        if state:
            search_parts.append(f'state:"{state}"')

        search_query = ' AND '.join(search_parts) if search_parts else 'product_type:"Food"'

        search_params = {
            'search': search_query,
            'limit': limit,
            'sort': 'report_date:desc'
        }

        result = self._make_request('/food/enforcement.json', search_params)

        if 'error' not in result:
            results = result.get('results', [])

            return {
                "product_type": product_type,
                "state": state,
                "enforcement_actions": [
                    {
                        "product_description": action.get('product_description'),
                        "reason_for_recall": action.get('reason_for_recall'),
                        "status": action.get('status'),
                        "report_date": action.get('report_date'),
                        "recall_number": action.get('recall_number'),
                        "recalling_firm": action.get('recalling_firm')
                    }
                    for action in results
                ],
                "count": len(results)
            }
        return result

    def _search_ndc_directory(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search National Drug Code (NDC) directory"""
        ndc_code = params.get('ndc_code', '')
        brand_name = params.get('brand_name', '')
        limit = params.get('limit', 10)

        if not ndc_code and not brand_name:
            return {"error": "NDC code or brand name is required"}

        if ndc_code:
            search_query = f'product_ndc:"{ndc_code}"'
        else:
            search_query = f'brand_name:"{brand_name}"'

        search_params = {
            'search': search_query,
            'limit': limit
        }

        result = self._make_request('/drug/ndc.json', search_params)

        if 'error' not in result:
            results = result.get('results', [])

            return {
                "ndc_code": ndc_code,
                "brand_name": brand_name,
                "products": [
                    {
                        "product_ndc": product.get('product_ndc'),
                        "brand_name": product.get('brand_name'),
                        "generic_name": product.get('generic_name'),
                        "dosage_form": product.get('dosage_form'),
                        "route": product.get('route'),
                        "product_type": product.get('product_type'),
                        "labeler_name": product.get('labeler_name'),
                        "marketing_category": product.get('marketing_category')
                    }
                    for product in results
                ],
                "count": len(results)
            }
        return result

    def _get_drug_approvals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get drug approval applications"""
        application_number = params.get('application_number', '')
        sponsor_name = params.get('sponsor_name', '')
        limit = params.get('limit', 10)

        search_parts = []
        if application_number:
            search_parts.append(f'application_number:"{application_number}"')
        if sponsor_name:
            search_parts.append(f'sponsor_name:"{sponsor_name}"')

        search_query = ' AND '.join(search_parts) if search_parts else '*'

        search_params = {
            'search': search_query,
            'limit': limit
        }

        result = self._make_request('/drug/drugsfda.json', search_params)

        if 'error' not in result:
            results = result.get('results', [])

            return {
                "application_number": application_number,
                "sponsor_name": sponsor_name,
                "approvals": [
                    {
                        "application_number": app.get('application_number'),
                        "sponsor_name": app.get('sponsor_name'),
                        "products": [
                            {
                                "brand_name": prod.get('brand_name'),
                                "active_ingredients": prod.get('active_ingredients'),
                                "dosage_form": prod.get('dosage_form'),
                                "route": prod.get('route')
                            }
                            for prod in app.get('products', [])
                        ]
                    }
                    for app in results
                ],
                "count": len(results)
            }
        return result

    def _search_clinical_trials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search clinical trials (placeholder - would integrate with ClinicalTrials.gov)"""
        condition = params.get('condition', '')
        intervention = params.get('intervention', '')
        status = params.get('status', '')

        return {
            "condition": condition,
            "intervention": intervention,
            "status": status,
            "info": "Clinical trials data available through ClinicalTrials.gov API",
            "source": "https://clinicaltrials.gov/api/"
        }

    def _get_generic_drugs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get generic drug equivalents"""
        brand_name = params.get('brand_name', '')

        if not brand_name:
            return {"error": "Brand name is required"}

        # Search for the brand name drug
        search_params = {
            'search': f'openfda.brand_name:"{brand_name}"',
            'limit': 10
        }

        result = self._make_request('/drug/label.json', search_params)

        if 'error' not in result:
            results = result.get('results', [])

            generic_equivalents = []
            for drug in results:
                generic_names = drug.get('openfda', {}).get('generic_name', [])
                if generic_names:
                    generic_equivalents.extend(generic_names)

            return {
                "brand_name": brand_name,
                "generic_equivalents": list(set(generic_equivalents)),
                "count": len(set(generic_equivalents))
            }
        return result

    def _search_510k_devices(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search 510(k) premarket notifications for medical devices"""
        device_name = params.get('device_name', '')
        applicant = params.get('applicant', '')
        year = params.get('year', '')
        limit = params.get('limit', 20)

        search_parts = []
        if device_name:
            search_parts.append(f'device_name:"{device_name}"')
        if applicant:
            search_parts.append(f'applicant:"{applicant}"')
        if year:
            search_parts.append(f'decision_date:[{year}0101 TO {year}1231]')

        search_query = ' AND '.join(search_parts) if search_parts else '*'

        search_params = {
            'search': search_query,
            'limit': limit,
            'sort': 'decision_date:desc'
        }

        result = self._make_request('/device/510k.json', search_params)

        if 'error' not in result:
            results = result.get('results', [])

            return {
                "device_name": device_name,
                "applicant": applicant,
                "year": year,
                "clearances": [
                    {
                        "k_number": device.get('k_number'),
                        "device_name": device.get('device_name'),
                        "applicant": device.get('applicant'),
                        "decision_date": device.get('decision_date'),
                        "decision_description": device.get('decision_description'),
                        "product_code": device.get('product_code'),
                        "device_class": device.get('device_class')
                    }
                    for device in results
                ],
                "count": len(results)
            }
        return result

    def _get_drug_shortages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current drug shortage information (placeholder)"""
        drug_name = params.get('drug_name', '')

        return {
            "drug_name": drug_name,
            "info": "Drug shortage information available through FDA Drug Shortages database",
            "source": "https://www.accessdata.fda.gov/scripts/drugshortages/"
        }