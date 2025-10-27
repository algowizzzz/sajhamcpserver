"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
DuckDB OLAP Tools - Standalone Client

This client provides easy-to-use methods for interacting with DuckDB OLAP Tools.
It can be used independently or integrated into larger applications.
"""

import json
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional


class DuckDbOlapToolsClient:
    """
    Standalone client for DuckDB OLAP Tools
    
    This client provides a convenient interface for analytical operations
    on CSV, Parquet, and JSON files using DuckDB.
    """
    
    def __init__(self, base_url: str, api_token: Optional[str] = None):
        """
        Initialize DuckDB OLAP Tools client
        
        Args:
            base_url: Base URL of the MCP server (e.g., 'http://localhost:5000')
            api_token: Optional authentication token for the MCP server
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.tool_name = 'duckdb_olap_tools'
        
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
    
    def list_tables(self) -> Dict[str, Any]:
        """
        List all available tables/views
        
        Returns:
            List of tables with row counts
        """
        arguments = {
            'action': 'list_tables'
        }
        
        return self._make_request(arguments)
    
    def describe_table(self, table_name: str) -> Dict[str, Any]:
        """
        Get schema and sample data for a table
        
        Args:
            table_name: Name of table/view
            
        Returns:
            Table schema and sample data
        """
        arguments = {
            'action': 'describe_table',
            'table_name': table_name
        }
        
        return self._make_request(arguments)
    
    def query(self, sql_query: str, limit: int = 100) -> Dict[str, Any]:
        """
        Execute SQL query
        
        Args:
            sql_query: SQL query string
            limit: Maximum rows to return
            
        Returns:
            Query results
        """
        arguments = {
            'action': 'query',
            'sql_query': sql_query,
            'limit': limit
        }
        
        return self._make_request(arguments)
    
    def refresh_views(self) -> Dict[str, Any]:
        """
        Refresh file views (detect new/removed files)
        
        Returns:
            Refresh status
        """
        arguments = {
            'action': 'refresh_views'
        }
        
        return self._make_request(arguments)
    
    def get_stats(self, table_name: str) -> Dict[str, Any]:
        """
        Get statistics for a table
        
        Args:
            table_name: Name of table/view
            
        Returns:
            Table statistics
        """
        arguments = {
            'action': 'get_stats',
            'table_name': table_name
        }
        
        return self._make_request(arguments)
    
    def aggregate(
        self,
        table_name: str,
        aggregations: Dict[str, str],
        group_by: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform aggregations on a table
        
        Args:
            table_name: Name of table/view
            aggregations: Dict of column: function (e.g., {'price': 'sum'})
            group_by: Columns to group by
            
        Returns:
            Aggregation results
        """
        arguments = {
            'action': 'aggregate',
            'table_name': table_name,
            'aggregations': aggregations
        }
        
        if group_by:
            arguments['group_by'] = group_by
        
        return self._make_request(arguments)
    
    def list_files(self) -> Dict[str, Any]:
        """
        List data files in directory
        
        Returns:
            List of data files
        """
        arguments = {
            'action': 'list_files'
        }
        
        return self._make_request(arguments)
    
    def get_table_names(self) -> List[str]:
        """
        Get list of table names
        
        Returns:
            List of table name strings
        """
        result = self.list_tables()
        return [table['name'] for table in result.get('tables', [])]
    
    def execute_analytics(
        self,
        table_name: str,
        metrics: List[str],
        dimensions: List[str]
    ) -> Dict[str, Any]:
        """
        Execute analytics query with metrics and dimensions
        
        Args:
            table_name: Name of table
            metrics: Columns to aggregate (with functions)
            dimensions: Columns to group by
            
        Returns:
            Analytics results
        """
        # Build aggregations from metrics
        aggs = {}
        for metric in metrics:
            if ':' in metric:
                col, func = metric.split(':')
                aggs[col.strip()] = func.strip()
            else:
                aggs[metric] = 'sum'
        
        return self.aggregate(table_name, aggs, dimensions)
    
    def get_top_n(
        self,
        table_name: str,
        column: str,
        n: int = 10,
        order: str = 'desc'
    ) -> Dict[str, Any]:
        """
        Get top N records by column value
        
        Args:
            table_name: Name of table
            column: Column to order by
            n: Number of records
            order: 'asc' or 'desc'
            
        Returns:
            Query results
        """
        order_clause = 'DESC' if order.lower() == 'desc' else 'ASC'
        query = f"SELECT * FROM {table_name} ORDER BY {column} {order_clause} LIMIT {n}"
        
        return self.query(query, limit=n)
    
    def print_tables(self):
        """Pretty print available tables"""
        result = self.list_tables()
        
        print(f"\n{'='*80}")
        print(f"Available Tables in {result['data_directory']}")
        print(f"Total: {result['table_count']} tables")
        print(f"{'='*80}\n")
        
        for table in result['tables']:
            print(f"📊 {table['name']}")
            print(f"   Rows: {table['row_count']:,}")
            print()
    
    def print_schema(self, table_name: str):
        """
        Pretty print table schema
        
        Args:
            table_name: Name of table
        """
        result = self.describe_table(table_name)
        
        print(f"\n{'='*80}")
        print(f"Table: {result['table_name']}")
        print(f"Columns: {result['column_count']}")
        print(f"{'='*80}\n")
        
        for col in result['columns']:
            null_str = 'NULL' if col.get('null') == 'YES' else 'NOT NULL'
            print(f"  {col['name']:<20} {col['type']:<15} {null_str}")
        
        print(f"\n{'-'*80}")
        print("Sample Data:")
        print(f"{'-'*80}\n")
        
        for i, row in enumerate(result['sample_data'][:5], 1):
            print(f"Row {i}: {row}")
    
    def print_query_results(self, result: Dict[str, Any], max_rows: int = 20):
        """
        Pretty print query results
        
        Args:
            result: Query result dictionary
            max_rows: Maximum rows to display
        """
        print(f"\n{'='*80}")
        print(f"Query Results")
        print(f"Rows: {result['row_count']}")
        print(f"{'='*80}\n")
        
        # Print column headers
        headers = result['columns']
        print(" | ".join(str(h)[:15] for h in headers))
        print("-" * 80)
        
        # Print rows
        for row in result['rows'][:max_rows]:
            print(" | ".join(str(v)[:15] for v in row))
        
        if result['row_count'] > max_rows:
            print(f"\n... ({result['row_count'] - max_rows} more rows)")


def main():
    """
    Main function with usage examples
    """
    # Initialize client
    BASE_URL = 'http://localhost:5000'
    API_TOKEN = None
    
    client = DuckDbOlapToolsClient(BASE_URL, API_TOKEN)
    
    print("="*80)
    print("DUCKDB OLAP TOOLS - CLIENT EXAMPLES")
    print("="*80)
    
    # Example 1: List Tables
    print("\n" + "="*80)
    print("EXAMPLE 1: List All Tables")
    print("="*80)
    
    try:
        client.print_tables()
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: Make sure:")
        print("1. Server is running")
        print("2. DuckDB is installed (pip install duckdb)")
        print("3. Sample data files are in data/duckdb/")
        return
    
    # Example 2: Describe Table
    print("\n" + "="*80)
    print("EXAMPLE 2: Describe Table Schema")
    print("="*80)
    
    try:
        tables = client.get_table_names()
        if tables:
            client.print_schema(tables[0])
        else:
            print("No tables available")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Simple Query
    print("\n" + "="*80)
    print("EXAMPLE 3: Execute Simple Query")
    print("="*80)
    
    try:
        tables = client.get_table_names()
        if tables:
            table_name = tables[0]
            result = client.query(f"SELECT * FROM {table_name} LIMIT 5")
            client.print_query_results(result)
        else:
            print("No tables available")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Aggregation
    print("\n" + "="*80)
    print("EXAMPLE 4: Perform Aggregation")
    print("="*80)
    
    try:
        # Aggregate sales data
        result = client.aggregate(
            table_name='sample_sales_data',
            aggregations={
                'quantity': 'sum',
                'price': 'avg',
                'order_id': 'count'
            },
            group_by=['category']
        )
        
        print("\nSales by Category:\n")
        print(f"Columns: {result['columns']}\n")
        
        for row in result['rows']:
            print(f"Category: {row[0]}")
            print(f"  Total Quantity: {row[1]}")
            print(f"  Avg Price: ${row[2]:.2f}")
            print(f"  Order Count: {row[3]}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 5: Regional Analysis
    print("\n" + "="*80)
    print("EXAMPLE 5: Regional Sales Analysis")
    print("="*80)
    
    try:
        result = client.query("""
            SELECT 
                region,
                COUNT(*) as orders,
                SUM(price * quantity) as revenue,
                AVG(price * quantity) as avg_order_value
            FROM sample_sales_data
            GROUP BY region
            ORDER BY revenue DESC
        """)
        
        print("\nRegional Performance:\n")
        
        for row in result['rows']:
            print(f"{row[0]}:")
            print(f"  Orders: {row[1]}")
            print(f"  Revenue: ${row[2]:,.2f}")
            print(f"  Avg Order: ${row[3]:.2f}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 6: Get Statistics
    print("\n" + "="*80)
    print("EXAMPLE 6: Get Table Statistics")
    print("="*80)
    
    try:
        result = client.get_stats('sample_sales_data')
        
        print(f"\nTable: {result['table_name']}")
        print(f"Rows: {result['row_count']:,}")
        print(f"Columns: {result['column_count']}\n")
        
        print("Column Statistics:")
        for col, stats in list(result['statistics'].items())[:5]:
            print(f"\n{col}:")
            for stat_name, value in stats.items():
                if isinstance(value, float):
                    print(f"  {stat_name}: {value:.2f}")
                else:
                    print(f"  {stat_name}: {value}")
                    
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 7: JOIN Query
    print("\n" + "="*80)
    print("EXAMPLE 7: JOIN Multiple Tables")
    print("="*80)
    
    try:
        result = client.query("""
            SELECT 
                c.customer_name,
                c.customer_tier,
                COUNT(s.order_id) as order_count,
                SUM(s.price * s.quantity) as total_spent
            FROM sample_sales_data s
            JOIN sample_customer_data c ON s.customer_id = c.customer_id
            GROUP BY c.customer_name, c.customer_tier
            ORDER BY total_spent DESC
            LIMIT 5
        """)
        
        print("\nTop Customers:\n")
        
        for row in result['rows']:
            print(f"{row[0]} ({row[1]}):")
            print(f"  Orders: {row[2]}")
            print(f"  Total Spent: ${row[3]:,.2f}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 8: Time Series Analysis
    print("\n" + "="*80)
    print("EXAMPLE 8: Time Series Analysis")
    print("="*80)
    
    try:
        result = client.query("""
            SELECT 
                DATE_TRUNC('week', order_date) as week,
                COUNT(*) as orders,
                SUM(price * quantity) as revenue
            FROM sample_sales_data
            GROUP BY week
            ORDER BY week
        """)
        
        print("\nWeekly Sales Trend:\n")
        
        for row in result['rows']:
            print(f"Week {row[0]}: {row[1]} orders, ${row[2]:,.2f}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 9: Top Products
    print("\n" + "="*80)
    print("EXAMPLE 9: Top Products by Revenue")
    print("="*80)
    
    try:
        result = client.query("""
            SELECT 
                product,
                COUNT(*) as times_ordered,
                SUM(quantity) as units_sold,
                SUM(price * quantity) as revenue
            FROM sample_sales_data
            GROUP BY product
            ORDER BY revenue DESC
            LIMIT 5
        """)
        
        print("\nTop 5 Products:\n")
        
        for i, row in enumerate(result['rows'], 1):
            print(f"{i}. {row[0]}")
            print(f"   Orders: {row[1]}, Units: {row[2]}, Revenue: ${row[3]:,.2f}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 10: Refresh Views
    print("\n" + "="*80)
    print("EXAMPLE 10: Refresh Views")
    print("="*80)
    
    try:
        result = client.refresh_views()
        
        print(f"\nRefresh Status: {result['status']}")
        print(f"Previous Files: {result['previous_files']}")
        print(f"Current Files: {result['current_files']}")
        print(f"Files Added: {result['files_added']}")
        print(f"Files Removed: {result['files_removed']}")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 11: List Files
    print("\n" + "="*80)
    print("EXAMPLE 11: List Data Files")
    print("="*80)
    
    try:
        result = client.list_files()
        
        print(f"\nData Directory: {result['directory']}")
        print(f"Files: {result['file_count']}\n")
        
        for file in result['files']:
            print(f"📄 {file['filename']}")
            print(f"   View: {file['view_name']}")
            print(f"   Size: {file['size_mb']} MB")
            print(f"   Type: {file['extension']}")
            print(f"   Modified: {file['modified']}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 12: Complex Analytics
    print("\n" + "="*80)
    print("EXAMPLE 12: Complex Analytics Query")
    print("="*80)
    
    try:
        result = client.query("""
            WITH monthly_sales AS (
                SELECT 
                    DATE_TRUNC('month', order_date) as month,
                    category,
                    SUM(price * quantity) as revenue
                FROM sample_sales_data
                GROUP BY month, category
            )
            SELECT 
                month,
                category,
                revenue,
                SUM(revenue) OVER (PARTITION BY category ORDER BY month) as cumulative_revenue
            FROM monthly_sales
            ORDER BY category, month
        """)
        
        print("\nCumulative Revenue by Category:\n")
        client.print_query_results(result, max_rows=15)
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)
    print("ALL EXAMPLES COMPLETED")
    print("="*80)


if __name__ == "__main__":
    """
    Run the client examples
    
    Usage:
        python duckdb_olap_tools_client.py
    
    Prerequisites:
        - Server running
        - DuckDB installed (pip install duckdb)
        - Sample data in data/duckdb/
    
    Configuration:
        Update BASE_URL and API_TOKEN in main() function
    """
    main()
