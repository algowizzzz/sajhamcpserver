"""
US Data.gov MCP Tool implementation
Access to US Government open data catalog
"""
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_mcp_tool import BaseMCPTool


class USDataMCPTool(BaseMCPTool):
    """Comprehensive MCP Tool for US Government Data.gov operations"""

    def _initialize(self):
        """Initialize US Data.gov specific components"""
        self.api_base_url = "https://catalog.data.gov/api/3"

        # HTTP headers
        self.headers = {
            'User-Agent': 'USDataMCPTool/1.0',
            'Accept': 'application/json'
        }

        # Request timeout
        self.request_timeout = 30

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle US Data.gov tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            # Tool method mapping
            tool_methods = {
                "search_datasets": self._search_datasets,
                "get_dataset": self._get_dataset,
                "get_dataset_resources": self._get_dataset_resources,
                "list_organizations": self._list_organizations,
                "get_organization": self._get_organization,
                "search_by_organization": self._search_by_organization,
                "list_groups": self._list_groups,
                "get_group": self._get_group,
                "get_recent_datasets": self._get_recent_datasets,
                "get_popular_datasets": self._get_popular_datasets,
                "search_by_tag": self._search_by_tag,
                "get_dataset_statistics": self._get_dataset_statistics,
                "search_by_format": self._search_by_format,
                "get_dataset_metadata": self._get_dataset_metadata,
                "list_tags": self._list_tags,
                "search_by_date_range": self._search_by_date_range,
                "advanced_search": self._advanced_search,
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

    # ==================== HELPER METHODS ====================

    def _make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request to data.gov API"""
        try:
            url = f"{self.api_base_url}/{endpoint}"
            response = self.session.get(url, params=params, timeout=self.request_timeout)

            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API request failed with status {response.status_code}",
                    "status": response.status_code
                }
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def _format_dataset(self, dataset: Dict[str, Any]) -> Dict[str, Any]:
        """Format dataset for response"""
        return {
            "id": dataset.get("id"),
            "name": dataset.get("name"),
            "title": dataset.get("title"),
            "notes": dataset.get("notes", "")[:500],  # Limit description
            "organization": dataset.get("organization", {}).get("title"),
            "organization_id": dataset.get("organization", {}).get("name"),
            "metadata_created": dataset.get("metadata_created"),
            "metadata_modified": dataset.get("metadata_modified"),
            "author": dataset.get("author"),
            "maintainer": dataset.get("maintainer"),
            "license_title": dataset.get("license_title"),
            "tags": [tag.get("display_name") for tag in dataset.get("tags", [])],
            "num_resources": dataset.get("num_resources", 0),
            "num_tags": dataset.get("num_tags", 0),
            "url": f"https://catalog.data.gov/dataset/{dataset.get('name')}",
        }

    # ==================== DATASET SEARCH METHODS ====================

    def _search_datasets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search datasets on data.gov"""
        query = params.get("query", "")
        rows = min(params.get("rows", 10), 1000)
        start = params.get("start", 0)
        sort = params.get("sort", "score desc")

        api_params = {
            "q": query,
            "rows": rows,
            "start": start,
            "sort": sort
        }

        result = self._make_request("action/package_search", api_params)

        if "error" in result:
            return result

        search_result = result.get("result", {})
        datasets = search_result.get("results", [])

        return {
            "query": query,
            "count": search_result.get("count", 0),
            "results_returned": len(datasets),
            "datasets": [self._format_dataset(ds) for ds in datasets]
        }

    def _get_dataset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a dataset"""
        dataset_id = params.get("dataset_id", "")

        if not dataset_id:
            return {"error": "dataset_id is required"}

        result = self._make_request("action/package_show", {"id": dataset_id})

        if "error" in result:
            return result

        dataset = result.get("result", {})

        return {
            "id": dataset.get("id"),
            "name": dataset.get("name"),
            "title": dataset.get("title"),
            "notes": dataset.get("notes"),
            "organization": {
                "title": dataset.get("organization", {}).get("title"),
                "name": dataset.get("organization", {}).get("name"),
                "description": dataset.get("organization", {}).get("description"),
            },
            "author": dataset.get("author"),
            "author_email": dataset.get("author_email"),
            "maintainer": dataset.get("maintainer"),
            "maintainer_email": dataset.get("maintainer_email"),
            "license_title": dataset.get("license_title"),
            "license_url": dataset.get("license_url"),
            "metadata_created": dataset.get("metadata_created"),
            "metadata_modified": dataset.get("metadata_modified"),
            "tags": [tag.get("display_name") for tag in dataset.get("tags", [])],
            "groups": [group.get("display_name") for group in dataset.get("groups", [])],
            "resources": [{
                "id": res.get("id"),
                "name": res.get("name"),
                "description": res.get("description"),
                "format": res.get("format"),
                "url": res.get("url"),
                "created": res.get("created"),
                "size": res.get("size")
            } for res in dataset.get("resources", [])],
            "num_resources": len(dataset.get("resources", [])),
            "url": f"https://catalog.data.gov/dataset/{dataset.get('name')}",
        }

    def _get_dataset_resources(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get all resources for a dataset"""
        dataset_id = params.get("dataset_id", "")

        if not dataset_id:
            return {"error": "dataset_id is required"}

        result = self._make_request("action/package_show", {"id": dataset_id})

        if "error" in result:
            return result

        dataset = result.get("result", {})
        resources = dataset.get("resources", [])

        return {
            "dataset_id": dataset.get("id"),
            "dataset_name": dataset.get("name"),
            "dataset_title": dataset.get("title"),
            "total_resources": len(resources),
            "resources": [{
                "id": res.get("id"),
                "name": res.get("name"),
                "description": res.get("description", ""),
                "format": res.get("format"),
                "mimetype": res.get("mimetype"),
                "url": res.get("url"),
                "size": res.get("size"),
                "created": res.get("created"),
                "last_modified": res.get("last_modified"),
                "hash": res.get("hash"),
            } for res in resources]
        }

    # ==================== ORGANIZATION METHODS ====================

    def _list_organizations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all organizations/agencies"""
        all_fields = params.get("all_fields", False)
        limit = params.get("limit", 100)

        api_params = {
            "all_fields": all_fields,
            "limit": limit
        }

        result = self._make_request("action/organization_list", api_params)

        if "error" in result:
            return result

        organizations = result.get("result", [])

        if all_fields:
            return {
                "count": len(organizations),
                "organizations": [{
                    "id": org.get("id"),
                    "name": org.get("name"),
                    "title": org.get("display_name") or org.get("title"),
                    "description": org.get("description", "")[:500],
                    "image_url": org.get("image_url"),
                    "package_count": org.get("package_count", 0),
                    "created": org.get("created"),
                } for org in organizations]
            }
        else:
            return {
                "count": len(organizations),
                "organizations": organizations
            }

    def _get_organization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about an organization"""
        org_id = params.get("org_id", "")
        include_datasets = params.get("include_datasets", False)

        if not org_id:
            return {"error": "org_id is required"}

        api_params = {
            "id": org_id,
            "include_datasets": include_datasets
        }

        result = self._make_request("action/organization_show", api_params)

        if "error" in result:
            return result

        org = result.get("result", {})

        response = {
            "id": org.get("id"),
            "name": org.get("name"),
            "title": org.get("display_name") or org.get("title"),
            "description": org.get("description"),
            "image_url": org.get("image_url"),
            "created": org.get("created"),
            "package_count": org.get("package_count", 0),
            "approval_status": org.get("approval_status"),
        }

        if include_datasets:
            response["datasets"] = [
                self._format_dataset(ds) for ds in org.get("packages", [])
            ]

        return response

    def _search_by_organization(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search datasets by organization"""
        org_name = params.get("org_name", "")
        rows = params.get("rows", 10)

        if not org_name:
            return {"error": "org_name is required"}

        api_params = {
            "fq": f"organization:{org_name}",
            "rows": rows
        }

        result = self._make_request("action/package_search", api_params)

        if "error" in result:
            return result

        search_result = result.get("result", {})
        datasets = search_result.get("results", [])

        return {
            "organization": org_name,
            "count": search_result.get("count", 0),
            "results_returned": len(datasets),
            "datasets": [self._format_dataset(ds) for ds in datasets]
        }

    # ==================== GROUP/CATEGORY METHODS ====================

    def _list_groups(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all groups/categories"""
        all_fields = params.get("all_fields", False)

        api_params = {
            "all_fields": all_fields
        }

        result = self._make_request("action/group_list", api_params)

        if "error" in result:
            return result

        groups = result.get("result", [])

        if all_fields:
            return {
                "count": len(groups),
                "groups": [{
                    "id": grp.get("id"),
                    "name": grp.get("name"),
                    "title": grp.get("display_name") or grp.get("title"),
                    "description": grp.get("description", "")[:500],
                    "package_count": grp.get("package_count", 0),
                } for grp in groups]
            }
        else:
            return {
                "count": len(groups),
                "groups": groups
            }

    def _get_group(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get information about a group"""
        group_id = params.get("group_id", "")

        if not group_id:
            return {"error": "group_id is required"}

        result = self._make_request("action/group_show", {"id": group_id})

        if "error" in result:
            return result

        group = result.get("result", {})

        return {
            "id": group.get("id"),
            "name": group.get("name"),
            "title": group.get("display_name") or group.get("title"),
            "description": group.get("description"),
            "image_url": group.get("image_url"),
            "created": group.get("created"),
            "package_count": group.get("package_count", 0),
        }

    # ==================== SPECIALIZED SEARCH METHODS ====================

    def _get_recent_datasets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get recently updated datasets"""
        rows = params.get("rows", 10)

        api_params = {
            "rows": rows,
            "sort": "metadata_modified desc"
        }

        result = self._make_request("action/package_search", api_params)

        if "error" in result:
            return result

        search_result = result.get("result", {})
        datasets = search_result.get("results", [])

        return {
            "count": len(datasets),
            "datasets": [self._format_dataset(ds) for ds in datasets]
        }

    def _get_popular_datasets(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get most popular datasets"""
        rows = params.get("rows", 10)

        api_params = {
            "rows": rows,
            "sort": "views_recent desc"
        }

        result = self._make_request("action/package_search", api_params)

        if "error" in result:
            return result

        search_result = result.get("result", {})
        datasets = search_result.get("results", [])

        return {
            "count": len(datasets),
            "datasets": [self._format_dataset(ds) for ds in datasets]
        }

    def _search_by_tag(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search datasets by tag"""
        tag = params.get("tag", "")
        rows = params.get("rows", 10)

        if not tag:
            return {"error": "tag is required"}

        api_params = {
            "fq": f"tags:{tag}",
            "rows": rows
        }

        result = self._make_request("action/package_search", api_params)

        if "error" in result:
            return result

        search_result = result.get("result", {})
        datasets = search_result.get("results", [])

        return {
            "tag": tag,
            "count": search_result.get("count", 0),
            "results_returned": len(datasets),
            "datasets": [self._format_dataset(ds) for ds in datasets]
        }

    def _search_by_format(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search datasets by format"""
        format_type = params.get("format", "")
        rows = params.get("rows", 10)

        if not format_type:
            return {"error": "format is required"}

        api_params = {
            "fq": f"res_format:{format_type.upper()}",
            "rows": rows
        }

        result = self._make_request("action/package_search", api_params)

        if "error" in result:
            return result

        search_result = result.get("result", {})
        datasets = search_result.get("results", [])

        return {
            "format": format_type,
            "count": search_result.get("count", 0),
            "results_returned": len(datasets),
            "datasets": [self._format_dataset(ds) for ds in datasets]
        }

    def _search_by_date_range(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search datasets by date range"""
        start_date = params.get("start_date", "")
        end_date = params.get("end_date", "")
        rows = params.get("rows", 10)

        if not start_date or not end_date:
            return {"error": "start_date and end_date are required"}

        api_params = {
            "fq": f"metadata_modified:[{start_date}T00:00:00Z TO {end_date}T23:59:59Z]",
            "rows": rows,
            "sort": "metadata_modified desc"
        }

        result = self._make_request("action/package_search", api_params)

        if "error" in result:
            return result

        search_result = result.get("result", {})
        datasets = search_result.get("results", [])

        return {
            "start_date": start_date,
            "end_date": end_date,
            "count": search_result.get("count", 0),
            "results_returned": len(datasets),
            "datasets": [self._format_dataset(ds) for ds in datasets]
        }

    def _advanced_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced search with multiple filters"""
        query = params.get("query", "*:*")
        organization = params.get("organization")
        tags = params.get("tags", [])
        format_type = params.get("format")
        rows = params.get("rows", 10)

        # Build filter query
        fq_parts = []

        if organization:
            fq_parts.append(f"organization:{organization}")

        if tags:
            tag_query = " AND ".join([f"tags:{tag}" for tag in tags])
            fq_parts.append(f"({tag_query})")

        if format_type:
            fq_parts.append(f"res_format:{format_type.upper()}")

        api_params = {
            "q": query,
            "rows": rows
        }

        if fq_parts:
            api_params["fq"] = " AND ".join(fq_parts)

        result = self._make_request("action/package_search", api_params)

        if "error" in result:
            return result

        search_result = result.get("result", {})
        datasets = search_result.get("results", [])

        return {
            "query": query,
            "filters": {
                "organization": organization,
                "tags": tags,
                "format": format_type
            },
            "count": search_result.get("count", 0),
            "results_returned": len(datasets),
            "datasets": [self._format_dataset(ds) for ds in datasets]
        }

    # ==================== METADATA AND STATISTICS ====================

    def _get_dataset_metadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive metadata for a dataset"""
        dataset_id = params.get("dataset_id", "")

        if not dataset_id:
            return {"error": "dataset_id is required"}

        result = self._make_request("action/package_show", {"id": dataset_id})

        if "error" in result:
            return result

        dataset = result.get("result", {})

        return {
            "basic_info": {
                "id": dataset.get("id"),
                "name": dataset.get("name"),
                "title": dataset.get("title"),
                "type": dataset.get("type"),
                "state": dataset.get("state"),
                "private": dataset.get("private"),
            },
            "content": {
                "notes": dataset.get("notes"),
                "url": dataset.get("url"),
            },
            "ownership": {
                "author": dataset.get("author"),
                "author_email": dataset.get("author_email"),
                "maintainer": dataset.get("maintainer"),
                "maintainer_email": dataset.get("maintainer_email"),
                "organization": dataset.get("organization", {}).get("title"),
            },
            "licensing": {
                "license_id": dataset.get("license_id"),
                "license_title": dataset.get("license_title"),
                "license_url": dataset.get("license_url"),
            },
            "temporal": {
                "metadata_created": dataset.get("metadata_created"),
                "metadata_modified": dataset.get("metadata_modified"),
            },
            "classification": {
                "tags": [tag.get("display_name") for tag in dataset.get("tags", [])],
                "groups": [grp.get("display_name") for grp in dataset.get("groups", [])],
            },
            "resources_summary": {
                "count": len(dataset.get("resources", [])),
                "formats": list(set([res.get("format") for res in dataset.get("resources", []) if res.get("format")])),
            }
        }

    def _list_tags(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all available tags"""
        limit = params.get("limit", 100)

        api_params = {
            "all_fields": True,
            "limit": limit
        }

        result = self._make_request("action/tag_list", api_params)

        if "error" in result:
            return result

        tags = result.get("result", [])

        return {
            "count": len(tags),
            "tags": [{
                "id": tag.get("id"),
                "name": tag.get("name"),
                "display_name": tag.get("display_name"),
            } for tag in tags] if isinstance(tags[0], dict) else tags
        }

    def _get_dataset_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics about data.gov datasets"""
        # Get total count
        count_result = self._make_request("action/package_search", {"rows": 0})

        if "error" in count_result:
            return count_result

        total_count = count_result.get("result", {}).get("count", 0)

        # Get organizations count
        org_result = self._make_request("action/organization_list")
        org_count = len(org_result.get("result", [])) if "result" in org_result else 0

        # Get groups count
        group_result = self._make_request("action/group_list")
        group_count = len(group_result.get("result", [])) if "result" in group_result else 0

        return {
            "total_datasets": total_count,
            "total_organizations": org_count,
            "total_groups": group_count,
            "data_source": "data.gov",
            "api_version": "3",
            "timestamp": datetime.now().isoformat()
        }