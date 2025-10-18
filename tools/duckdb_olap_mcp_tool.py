"""
DuckDB OLAP MCP Tool implementation
"""
import os
import duckdb
import pandas as pd
from typing import Dict, Any, List
from .base_mcp_tool import BaseMCPTool
from datetime import datetime
import csv
import random


class DuckDBOlapMCPTool(BaseMCPTool):
    """MCP Tool for DuckDB OLAP operations"""

    def _initialize(self):
        """Initialize DuckDB and create sample data"""
        self.data_folder = os.environ.get('DUCKDB_DATA_FOLDER', 'data')
        self.db_path = os.path.join(self.data_folder, 'olap.duckdb')

        # Create data directory if it doesn't exist
        os.makedirs(self.data_folder, exist_ok=True)

        # Create sample CSV files if they don't exist
        self._create_sample_data()

        # Initialize DuckDB connection
        self.conn = duckdb.connect(self.db_path)

        # Load CSV files into DuckDB
        self._load_data_sources()

    def _create_sample_data(self):
        """Create sample CSV files for demonstration"""
        # Create sales data CSV
        sales_file = os.path.join(self.data_folder, 'sales_data.csv')
        if not os.path.exists(sales_file):
            sales_data = []
            products = ['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard']
            regions = ['North', 'South', 'East', 'West', 'Central']

            for i in range(1000):
                sales_data.append({
                    'order_id': f'ORD{i:04d}',
                    'date': f'2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                    'product': random.choice(products),
                    'region': random.choice(regions),
                    'quantity': random.randint(1, 10),
                    'unit_price': random.uniform(100, 2000),
                    'customer_id': f'CUST{random.randint(1, 200):03d}',
                    'discount': random.uniform(0, 0.3)
                })

            df = pd.DataFrame(sales_data)
            df['total_amount'] = df['quantity'] * df['unit_price'] * (1 - df['discount'])
            df.to_csv(sales_file, index=False)

        # Create customer data CSV
        customer_file = os.path.join(self.data_folder, 'customer_data.csv')
        if not os.path.exists(customer_file):
            customer_data = []
            countries = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Japan']
            segments = ['Enterprise', 'SMB', 'Consumer', 'Government']

            for i in range(1, 201):
                customer_data.append({
                    'customer_id': f'CUST{i:03d}',
                    'company_name': f'Company {i}',
                    'country': random.choice(countries),
                    'segment': random.choice(segments),
                    'registration_date': f'2023-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}',
                    'credit_limit': random.randint(5000, 100000),
                    'status': random.choice(['Active', 'Inactive', 'Pending'])
                })

            df = pd.DataFrame(customer_data)
            df.to_csv(customer_file, index=False)

    def _load_data_sources(self):
        """Load CSV files into DuckDB"""
        try:
            # Load sales data
            sales_file = os.path.join(self.data_folder, 'sales_data.csv')
            if os.path.exists(sales_file):
                self.conn.execute(f"""
                    CREATE OR REPLACE TABLE sales AS
                    SELECT * FROM read_csv_auto('{sales_file}')
                """)

            # Load customer data
            customer_file = os.path.join(self.data_folder, 'customer_data.csv')
            if os.path.exists(customer_file):
                self.conn.execute(f"""
                    CREATE OR REPLACE TABLE customers AS
                    SELECT * FROM read_csv_auto('{customer_file}')
                """)

            # Create additional views for OLAP operations
            self.conn.execute("""
                CREATE OR REPLACE VIEW sales_summary AS
                SELECT 
                    date,
                    product,
                    region,
                    SUM(quantity) as total_quantity,
                    SUM(total_amount) as total_revenue,
                    AVG(unit_price) as avg_price,
                    COUNT(*) as order_count
                FROM sales
                GROUP BY date, product, region
            """)

            self.conn.execute("""
                CREATE OR REPLACE VIEW customer_sales AS
                SELECT 
                    c.customer_id,
                    c.company_name,
                    c.country,
                    c.segment,
                    SUM(s.total_amount) as total_purchases,
                    COUNT(s.order_id) as order_count,
                    AVG(s.total_amount) as avg_order_value
                FROM customers c
                LEFT JOIN sales s ON c.customer_id = s.customer_id
                GROUP BY c.customer_id, c.company_name, c.country, c.segment
            """)

        except Exception as e:
            print(f"Error loading data sources: {e}")

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle DuckDB OLAP tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            tool_methods = {
                "execute_query": self._execute_query,
                "list_tables": self._list_tables,
                "get_table_schema": self._get_table_schema,
                "aggregate_data": self._aggregate_data,
                "pivot_data": self._pivot_data,
                "time_series_analysis": self._time_series_analysis,
                "top_n_analysis": self._top_n_analysis,
                "window_functions": self._window_functions,
                "join_tables": self._join_tables,
                "load_csv": self._load_csv,
                "export_results": self._export_results,
                "create_materialized_view": self._create_materialized_view,
                "analyze_performance": self._analyze_performance
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

    def _execute_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a DuckDB SQL query"""
        query = params.get('query', '')

        if not query:
            return {"error": "Query is required"}

        try:
            result = self.conn.execute(query).fetchdf()

            return {
                "query": query,
                "results": result.head(100).to_dict('records'),
                "row_count": len(result),
                "columns": result.columns.tolist()
            }

        except Exception as e:
            return {"error": str(e), "query": query}

    def _list_tables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all tables and views in DuckDB"""
        try:
            # Get tables
            tables = self.conn.execute("""
                SELECT table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema = 'main'
            """).fetchall()

            table_list = []
            for table_name, table_type in tables:
                # Get row count
                row_count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

                table_list.append({
                    'name': table_name,
                    'type': table_type,
                    'row_count': row_count
                })

            return {
                "tables": table_list,
                "count": len(table_list)
            }

        except Exception as e:
            return {"error": str(e)}

    def _get_table_schema(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get schema information for a table"""
        table_name = params.get('table_name', '')

        if not table_name:
            return {"error": "Table name is required"}

        try:
            schema = self.conn.execute(f"""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """).fetchall()

            columns = []
            for col_name, data_type, is_nullable, default in schema:
                columns.append({
                    'name': col_name,
                    'type': data_type,
                    'nullable': is_nullable == 'YES',
                    'default': default
                })

            # Get sample data
            sample = self.conn.execute(f"SELECT * FROM {table_name} LIMIT 5").fetchdf()

            return {
                "table_name": table_name,
                "columns": columns,
                "sample_data": sample.to_dict('records')
            }

        except Exception as e:
            return {"error": str(e)}

    def _aggregate_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform aggregation operations"""
        table = params.get('table', 'sales')
        group_by = params.get('group_by', [])
        aggregations = params.get('aggregations', {})  # column: function pairs
        filters = params.get('filters', {})

        if not group_by:
            return {"error": "Group by columns required"}

        try:
            # Build query
            select_parts = group_by.copy()

            for column, func in aggregations.items():
                select_parts.append(f"{func}({column}) as {func.lower()}_{column}")

            query = f"SELECT {', '.join(select_parts)} FROM {table}"

            # Add filters
            if filters:
                where_conditions = []
                for col, val in filters.items():
                    if isinstance(val, str):
                        where_conditions.append(f"{col} = '{val}'")
                    else:
                        where_conditions.append(f"{col} = {val}")
                query += f" WHERE {' AND '.join(where_conditions)}"

            query += f" GROUP BY {', '.join(group_by)}"
            query += " ORDER BY 1"

            result = self.conn.execute(query).fetchdf()

            return {
                "query": query,
                "results": result.to_dict('records'),
                "row_count": len(result)
            }

        except Exception as e:
            return {"error": str(e)}

    def _pivot_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create pivot table"""
        table = params.get('table', 'sales')
        rows = params.get('rows', [])
        columns = params.get('columns', [])
        values = params.get('values', '')
        agg_func = params.get('agg_func', 'SUM')

        if not rows or not columns or not values:
            return {"error": "Rows, columns, and values are required"}

        try:
            # Build pivot query
            query = f"""
                PIVOT (
                    SELECT {', '.join(rows + columns)}, {values}
                    FROM {table}
                )
                ON {', '.join(columns)}
                USING {agg_func}({values})
            """

            result = self.conn.execute(query).fetchdf()

            return {
                "query": query,
                "results": result.to_dict('records'),
                "shape": {
                    'rows': len(result),
                    'columns': len(result.columns)
                }
            }

        except Exception as e:
            return {"error": str(e)}

    def _time_series_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform time series analysis"""
        table = params.get('table', 'sales')
        date_column = params.get('date_column', 'date')
        value_column = params.get('value_column', 'total_amount')
        granularity = params.get('granularity', 'month')  # day, week, month, quarter, year

        try:
            # Date truncation based on granularity
            date_trunc_map = {
                'day': 'day',
                'week': 'week',
                'month': 'month',
                'quarter': 'quarter',
                'year': 'year'
            }

            date_trunc = date_trunc_map.get(granularity, 'month')

            query = f"""
                SELECT 
                    DATE_TRUNC('{date_trunc}', {date_column}::DATE) as period,
                    COUNT(*) as count,
                    SUM({value_column}) as total,
                    AVG({value_column}) as average,
                    MIN({value_column}) as minimum,
                    MAX({value_column}) as maximum
                FROM {table}
                GROUP BY 1
                ORDER BY 1
            """

            result = self.conn.execute(query).fetchdf()

            return {
                "granularity": granularity,
                "results": result.to_dict('records'),
                "row_count": len(result)
            }

        except Exception as e:
            return {"error": str(e)}

    def _top_n_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get top N records by a metric"""
        table = params.get('table', 'sales')
        group_by = params.get('group_by', 'product')
        metric = params.get('metric', 'total_amount')
        agg_func = params.get('agg_func', 'SUM')
        n = params.get('n', 10)
        order = params.get('order', 'DESC')

        try:
            query = f"""
                SELECT 
                    {group_by},
                    {agg_func}({metric}) as metric_value
                FROM {table}
                GROUP BY {group_by}
                ORDER BY metric_value {order}
                LIMIT {n}
            """

            result = self.conn.execute(query).fetchdf()

            return {
                "top_n": n,
                "results": result.to_dict('records')
            }

        except Exception as e:
            return {"error": str(e)}

    def _window_functions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Apply window functions for advanced analytics"""
        table = params.get('table', 'sales')
        partition_by = params.get('partition_by', '')
        order_by = params.get('order_by', 'date')
        window_type = params.get('window_type', 'row_number')  # row_number, rank, lag, lead, cumsum

        try:
            # Build window function query
            window_func_map = {
                'row_number': 'ROW_NUMBER()',
                'rank': 'RANK()',
                'dense_rank': 'DENSE_RANK()',
                'lag': 'LAG(total_amount)',
                'lead': 'LEAD(total_amount)',
                'cumsum': 'SUM(total_amount)'
            }

            window_func = window_func_map.get(window_type, 'ROW_NUMBER()')

            partition_clause = f"PARTITION BY {partition_by}" if partition_by else ""

            query = f"""
                SELECT 
                    *,
                    {window_func} OVER ({partition_clause} ORDER BY {order_by}) as window_result
                FROM {table}
                LIMIT 100
            """

            result = self.conn.execute(query).fetchdf()

            return {
                "window_type": window_type,
                "results": result.to_dict('records'),
                "row_count": len(result)
            }

        except Exception as e:
            return {"error": str(e)}

    def _join_tables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Join multiple tables"""
        left_table = params.get('left_table', 'sales')
        right_table = params.get('right_table', 'customers')
        join_type = params.get('join_type', 'INNER')  # INNER, LEFT, RIGHT, FULL
        join_key = params.get('join_key', 'customer_id')

        try:
            query = f"""
                SELECT *
                FROM {left_table} l
                {join_type} JOIN {right_table} r
                ON l.{join_key} = r.{join_key}
                LIMIT 100
            """

            result = self.conn.execute(query).fetchdf()

            return {
                "join_type": join_type,
                "results": result.to_dict('records'),
                "row_count": len(result)
            }

        except Exception as e:
            return {"error": str(e)}

    def _load_csv(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Load a new CSV file into DuckDB"""
        file_path = params.get('file_path', '')
        table_name = params.get('table_name', '')

        if not file_path or not table_name:
            return {"error": "File path and table name are required"}

        full_path = os.path.join(self.data_folder, file_path)

        if not os.path.exists(full_path):
            return {"error": f"File '{file_path}' not found"}

        try:
            # Load CSV into DuckDB
            self.conn.execute(f"""
                CREATE OR REPLACE TABLE {table_name} AS
                SELECT * FROM read_csv_auto('{full_path}')
            """)

            # Get row count
            row_count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]

            return {
                "table_name": table_name,
                "file_path": file_path,
                "row_count": row_count,
                "message": "CSV loaded successfully"
            }

        except Exception as e:
            return {"error": str(e)}

    def _export_results(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Export query results to CSV"""
        query = params.get('query', '')
        output_file = params.get('output_file', 'export.csv')

        if not query:
            return {"error": "Query is required"}

        output_path = os.path.join(self.data_folder, output_file)

        try:
            # Execute query and export to CSV
            self.conn.execute(f"""
                COPY ({query})
                TO '{output_path}'
                WITH (HEADER, DELIMITER ',')
            """)

            return {
                "output_file": output_file,
                "path": output_path,
                "message": "Results exported successfully"
            }

        except Exception as e:
            return {"error": str(e)}

    def _create_materialized_view(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a materialized view for performance"""
        view_name = params.get('view_name', '')
        query = params.get('query', '')

        if not view_name or not query:
            return {"error": "View name and query are required"}

        try:
            # Create table as materialized view
            self.conn.execute(f"""
                CREATE OR REPLACE TABLE {view_name} AS
                {query}
            """)

            row_count = self.conn.execute(f"SELECT COUNT(*) FROM {view_name}").fetchone()[0]

            return {
                "view_name": view_name,
                "row_count": row_count,
                "message": "Materialized view created successfully"
            }

        except Exception as e:
            return {"error": str(e)}

    def _analyze_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query performance"""
        query = params.get('query', '')

        if not query:
            return {"error": "Query is required"}

        try:
            # Use EXPLAIN ANALYZE to get query plan
            explain_result = self.conn.execute(f"EXPLAIN ANALYZE {query}").fetchall()

            # Parse explain output
            plan_details = []
            for row in explain_result:
                plan_details.append(row[0])

            return {
                "query": query,
                "execution_plan": plan_details
            }

        except Exception as e:
            return {"error": str(e)}