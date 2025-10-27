"""
SQL Select Tool Client
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com

Standalone client for interacting with the SQL Select Tool via the MCP Server API.
Includes support for BaseMCPTool features (metrics, enable/disable, etc.)
"""

import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


class SqlSelectClient:
    """
    Client for interacting with the SQL Select Tool.
    
    This client provides methods to:
    - List available data sources
    - Execute SQL SELECT queries
    - Get schema information
    - Retrieve sample data
    - Count rows with filtering
    - Get tool metrics (BaseMCPTool feature)
    - Enable/disable tool (BaseMCPTool feature)
    """
    
    def __init__(self, base_url: str, api_token: str):
        """
        Initialize the SQL Select Tool client.
        
        Args:
            base_url: Base URL of the MCP Server (e.g., "http://localhost:5000")
            api_token: API authentication token
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.tool_name = "sqlselect"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
    
    def _execute_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with given arguments.
        
        Args:
            arguments: Tool arguments dictionary
            
        Returns:
            Tool execution result
        """
        payload = {
            "tool": self.tool_name,
            "arguments": arguments
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/tools/execute",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"API request failed: {str(e)}"
            }
    
    # ========== Tool Actions ==========
    
    def list_sources(self) -> Dict[str, Any]:
        """
        List all available data sources.
        
        Returns:
            Dictionary containing list of data sources
        """
        return self._execute_tool({"action": "list_sources"})
    
    def describe_source(self, source_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific data source.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            Dictionary containing source details including schema and row count
        """
        return self._execute_tool({
            "action": "describe_source",
            "source_name": source_name
        })
    
    def execute_query(self, query: str, limit: int = 100) -> Dict[str, Any]:
        """
        Execute a SQL SELECT query.
        
        Args:
            query: SQL SELECT query to execute
            limit: Maximum number of rows to return (default: 100, max: 10000)
            
        Returns:
            Dictionary containing query results
        """
        return self._execute_tool({
            "action": "execute_query",
            "query": query,
            "limit": limit
        })
    
    def sample_data(self, source_name: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get sample data from a data source.
        
        Args:
            source_name: Name of the data source
            limit: Number of sample rows to return (default: 10)
            
        Returns:
            Dictionary containing sample data
        """
        return self._execute_tool({
            "action": "sample_data",
            "source_name": source_name,
            "limit": limit
        })
    
    def get_schema(self, source_name: str) -> Dict[str, Any]:
        """
        Get schema information for a data source.
        
        Args:
            source_name: Name of the data source
            
        Returns:
            Dictionary containing schema information
        """
        return self._execute_tool({
            "action": "get_schema",
            "source_name": source_name
        })
    
    def count_rows(self, source_name: str, where_clause: Optional[str] = None) -> Dict[str, Any]:
        """
        Count rows in a data source with optional filtering.
        
        Args:
            source_name: Name of the data source
            where_clause: Optional WHERE clause for filtering
            
        Returns:
            Dictionary containing row count
        """
        arguments = {
            "action": "count_rows",
            "source_name": source_name
        }
        
        if where_clause:
            arguments["where_clause"] = where_clause
        
        return self._execute_tool(arguments)
    
    # ========== BaseMCPTool Features ==========
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get tool execution metrics.
        
        Inherited from BaseMCPTool, provides:
        - execution_count: Total number of executions
        - last_execution: Timestamp of last execution
        - total_execution_time: Total time spent executing
        - average_execution_time: Average execution time per call
        
        Returns:
            Dictionary containing tool metrics
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tools/{self.tool_name}/metrics",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to get metrics: {str(e)}"
            }
    
    def enable_tool(self) -> Dict[str, Any]:
        """
        Enable the SQL Select Tool.
        
        Uses BaseMCPTool.enable() method
        
        Returns:
            Dictionary containing operation result
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/admin/tools/{self.tool_name}/enable",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to enable tool: {str(e)}"
            }
    
    def disable_tool(self) -> Dict[str, Any]:
        """
        Disable the SQL Select Tool.
        
        Uses BaseMCPTool.disable() method
        
        Returns:
            Dictionary containing operation result
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/admin/tools/{self.tool_name}/disable",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to disable tool: {str(e)}"
            }
    
    def get_tool_info(self) -> Dict[str, Any]:
        """
        Get tool information in MCP format.
        
        Uses BaseMCPTool.to_mcp_format() method
        
        Returns:
            Dictionary containing tool information
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tools/{self.tool_name}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to get tool info: {str(e)}"
            }
    
    # ========== Convenience Methods ==========
    
    def get_customers_by_state(self, state: str, limit: int = 100) -> Dict[str, Any]:
        """Get customers filtered by state."""
        query = f"SELECT * FROM customers WHERE state = '{state}'"
        return self.execute_query(query, limit)
    
    def get_active_customers(self, limit: int = 100) -> Dict[str, Any]:
        """Get all active customers."""
        query = "SELECT * FROM customers WHERE status = 'Active'"
        return self.execute_query(query, limit)
    
    def get_products_by_category(self, category: str, limit: int = 100) -> Dict[str, Any]:
        """Get products filtered by category."""
        query = f"SELECT * FROM products WHERE category = '{category}' ORDER BY price DESC"
        return self.execute_query(query, limit)
    
    def get_top_customers(self, limit: int = 10) -> Dict[str, Any]:
        """Get top customers by total order amount."""
        query = f"""
            SELECT 
                c.customer_id,
                c.customer_name,
                c.email,
                COUNT(o.order_id) as order_count,
                SUM(o.total_amount) as total_spent
            FROM customers c
            INNER JOIN orders o ON c.customer_id = o.customer_id
            GROUP BY c.customer_id, c.customer_name, c.email
            ORDER BY total_spent DESC
            LIMIT {limit}
        """
        return self.execute_query(query, limit)
    
    def get_sales_by_region(self, limit: int = 100) -> Dict[str, Any]:
        """Get sales summary by region."""
        query = """
            SELECT 
                region,
                COUNT(*) as sale_count,
                SUM(total_price) as total_revenue,
                AVG(total_price) as avg_sale_value
            FROM sales
            GROUP BY region
            ORDER BY total_revenue DESC
        """
        return self.execute_query(query, limit)
    
    def get_product_sales_summary(self, limit: int = 20) -> Dict[str, Any]:
        """Get product sales summary with totals."""
        query = f"""
            SELECT 
                product_name,
                category,
                COUNT(*) as times_sold,
                SUM(quantity) as total_quantity,
                SUM(total_price) as total_revenue,
                AVG(unit_price) as avg_price
            FROM sales
            GROUP BY product_name, category
            ORDER BY total_revenue DESC
            LIMIT {limit}
        """
        return self.execute_query(query, limit)
    
    # ========== Utility Methods ==========
    
    def print_results(self, result: Dict[str, Any], max_rows: int = 10):
        """Pretty print query results."""
        if not result.get("success"):
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
            return
        
        data = result.get("data", {})
        
        # Handle list_sources
        if "sources" in data:
            print("\n📊 Available Data Sources")
            print("=" * 70)
            for source in data["sources"]:
                print(f"\n🔹 {source['name']}")
                print(f"   File: {source['file']}")
                print(f"   Type: {source['type']}")
                print(f"   Description: {source.get('description', 'N/A')}")
            print(f"\n✅ Total sources: {data['count']}")
            return
        
        # Handle schema
        if "schema" in data:
            print(f"\n📋 Schema for {data['source_name']}")
            print("=" * 70)
            print(f"{'Column Name':<30} {'Data Type':<15} {'Nullable':<10}")
            print("-" * 70)
            for col in data["schema"]:
                print(f"{col['column_name']:<30} {col['data_type']:<15} {col['nullable']:<10}")
            print(f"\n✅ Total columns: {data['column_count']}")
            return
        
        # Handle row count
        if "row_count" in data and "rows" not in data:
            print(f"\n🔢 Row Count for {data['source_name']}")
            print("=" * 70)
            print(f"Count: {data['row_count']}")
            if data.get("where_clause"):
                print(f"Filter: {data['where_clause']}")
            return
        
        # Handle query results
        if "rows" in data:
            rows = data["rows"]
            columns = data.get("columns", [])
            
            print(f"\n📊 Query Results")
            print("=" * 70)
            print(f"Rows returned: {data['row_count']}")
            
            if not rows:
                print("No data returned")
                return
            
            # Display up to max_rows
            display_rows = rows[:max_rows]
            
            # Print header
            if columns:
                print("\n" + " | ".join(f"{col:<15}" for col in columns))
                print("-" * (len(columns) * 17))
            
            # Print rows
            for row in display_rows:
                if isinstance(row, dict):
                    values = [str(row.get(col, ''))[:15] for col in columns]
                    print(" | ".join(f"{val:<15}" for val in values))
            
            if len(rows) > max_rows:
                print(f"\n... and {len(rows) - max_rows} more rows")
        
        print()
    
    def print_metrics(self, metrics: Dict[str, Any]):
        """Pretty print tool metrics."""
        if not metrics.get("success", True):
            print(f"❌ Error: {metrics.get('error', 'Unknown error')}")
            return
        
        print("\n📈 Tool Metrics")
        print("=" * 70)
        print(f"Tool Name: {metrics.get('name', 'N/A')}")
        print(f"Version: {metrics.get('version', 'N/A')}")
        print(f"Status: {'✅ Enabled' if metrics.get('enabled') else '❌ Disabled'}")
        print(f"\nExecution Statistics:")
        print(f"  Total Executions: {metrics.get('execution_count', 0)}")
        print(f"  Last Execution: {metrics.get('last_execution', 'Never')}")
        print(f"  Total Time: {metrics.get('total_execution_time', 0):.2f}s")
        print(f"  Average Time: {metrics.get('average_execution_time', 0):.3f}s")
        print()


def main():
    """
    Main function with example usage of SqlSelectClient.
    """
    # Configuration
    BASE_URL = "http://localhost:5000"
    API_TOKEN = "your_api_token_here"  # Replace with actual token
    
    # Initialize client
    client = SqlSelectClient(BASE_URL, API_TOKEN)
    
    print("=" * 80)
    print("SQL Select Tool Client - Example Usage")
    print("Copyright All rights Reserved 2025-2030, Ashutosh Sinha")
    print("=" * 80)
    
    # Example 1: Get tool information
    print("\n" + "=" * 80)
    print("Example 1: Get tool information (BaseMCPTool feature)")
    print("=" * 80)
    tool_info = client.get_tool_info()
    print(json.dumps(tool_info, indent=2))
    
    # Example 2: Get tool metrics
    print("\n" + "=" * 80)
    print("Example 2: Get tool metrics (BaseMCPTool feature)")
    print("=" * 80)
    metrics = client.get_metrics()
    client.print_metrics(metrics)
    
    # Example 3: List all data sources
    print("\n" + "=" * 80)
    print("Example 3: List all available data sources")
    print("=" * 80)
    result = client.list_sources()
    client.print_results(result)
    
    # Example 4: Describe a data source
    print("\n" + "=" * 80)
    print("Example 4: Describe the 'customers' data source")
    print("=" * 80)
    result = client.describe_source("customers")
    client.print_results(result)
    
    # Example 5: Get sample data
    print("\n" + "=" * 80)
    print("Example 5: Get sample data from 'products'")
    print("=" * 80)
    result = client.sample_data("products", limit=5)
    client.print_results(result)
    
    # Example 6: Get schema
    print("\n" + "=" * 80)
    print("Example 6: Get schema for 'orders'")
    print("=" * 80)
    result = client.get_schema("orders")
    client.print_results(result)
    
    # Example 7: Count rows
    print("\n" + "=" * 80)
    print("Example 7: Count active customers")
    print("=" * 80)
    result = client.count_rows("customers", "status = 'Active'")
    client.print_results(result)
    
    # Example 8: Execute a simple query
    print("\n" + "=" * 80)
    print("Example 8: Get customers from California")
    print("=" * 80)
    result = client.get_customers_by_state("CA")
    client.print_results(result)
    
    # Example 9: Get top customers
    print("\n" + "=" * 80)
    print("Example 9: Get top 5 customers by spending")
    print("=" * 80)
    result = client.get_top_customers(limit=5)
    client.print_results(result)
    
    # Example 10: Get sales by region
    print("\n" + "=" * 80)
    print("Example 10: Get sales summary by region")
    print("=" * 80)
    result = client.get_sales_by_region()
    client.print_results(result)
    
    # Example 11: Get product sales summary
    print("\n" + "=" * 80)
    print("Example 11: Get top 10 products by revenue")
    print("=" * 80)
    result = client.get_product_sales_summary(limit=10)
    client.print_results(result)
    
    # Example 12: Custom complex query
    print("\n" + "=" * 80)
    print("Example 12: Custom query - Customer order statistics")
    print("=" * 80)
    query = """
        SELECT 
            c.customer_name,
            c.city,
            c.state,
            COUNT(o.order_id) as total_orders,
            SUM(o.total_amount) as total_spent,
            AVG(o.total_amount) as avg_order_value
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.customer_id
        WHERE c.status = 'Active'
        GROUP BY c.customer_name, c.city, c.state
        HAVING COUNT(o.order_id) > 0
        ORDER BY total_spent DESC
        LIMIT 10
    """
    result = client.execute_query(query)
    client.print_results(result)
    
    # Example 13: Tool management - Enable/Disable (requires admin access)
    print("\n" + "=" * 80)
    print("Example 13: Tool management (BaseMCPTool features)")
    print("=" * 80)
    print("Note: These operations require admin privileges")
    
    # Check current metrics
    metrics = client.get_metrics()
    print(f"\nCurrent status: {'Enabled' if metrics.get('enabled') else 'Disabled'}")
    print(f"Total executions so far: {metrics.get('execution_count', 0)}")
    
    # Example 14: Final metrics check
    print("\n" + "=" * 80)
    print("Example 14: Final metrics check")
    print("=" * 80)
    final_metrics = client.get_metrics()
    client.print_metrics(final_metrics)
    
    print("\n" + "=" * 80)
    print("✅ All examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
