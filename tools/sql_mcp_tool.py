"""
SQL MCP Tool implementation with SQLite
"""
import sqlite3
import os
from typing import Dict, Any, List
from .base_mcp_tool import BaseMCPTool
import json


class SQLMCPTool(BaseMCPTool):
    """MCP Tool for SQL database operations"""

    def _initialize(self):
        """Initialize SQL database connection and create sample tables"""
        self.db_path = os.environ.get('SQL_DB_PATH', 'data/sample.db')

        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # Initialize database with sample tables
        self._create_sample_tables()

    def _create_sample_tables(self):
        """Create sample tables for demonstration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Create customers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    country TEXT,
                    registration_date DATE,
                    total_purchases DECIMAL(10,2) DEFAULT 0
                )
            ''')

            # Create products table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_name TEXT NOT NULL,
                    category TEXT,
                    price DECIMAL(10,2),
                    stock_quantity INTEGER,
                    supplier TEXT
                )
            ''')

            # Insert sample data if tables are empty
            cursor.execute("SELECT COUNT(*) FROM customers")
            if cursor.fetchone()[0] == 0:
                sample_customers = [
                    ('John Doe', 'john.doe@email.com', 'USA', '2023-01-15', 1250.50),
                    ('Jane Smith', 'jane.smith@email.com', 'Canada', '2023-02-20', 890.75),
                    ('Bob Johnson', 'bob.j@email.com', 'UK', '2023-03-10', 2100.00),
                    ('Alice Brown', 'alice.b@email.com', 'Australia', '2023-04-05', 650.25),
                    ('Charlie Wilson', 'charlie.w@email.com', 'Germany', '2023-05-12', 1500.00)
                ]

                cursor.executemany('''
                    INSERT INTO customers (name, email, country, registration_date, total_purchases)
                    VALUES (?, ?, ?, ?, ?)
                ''', sample_customers)

            cursor.execute("SELECT COUNT(*) FROM products")
            if cursor.fetchone()[0] == 0:
                sample_products = [
                    ('Laptop Pro', 'Electronics', 1299.99, 50, 'TechCorp'),
                    ('Wireless Mouse', 'Electronics', 29.99, 200, 'TechCorp'),
                    ('Office Chair', 'Furniture', 249.99, 75, 'FurniturePlus'),
                    ('Standing Desk', 'Furniture', 599.99, 30, 'FurniturePlus'),
                    ('Notebook Set', 'Stationery', 15.99, 500, 'OfficeSupply'),
                    ('Pen Pack', 'Stationery', 9.99, 1000, 'OfficeSupply'),
                    ('Monitor 27"', 'Electronics', 399.99, 100, 'TechCorp'),
                    ('Keyboard Mechanical', 'Electronics', 89.99, 150, 'TechCorp')
                ]

                cursor.executemany('''
                    INSERT INTO products (product_name, category, price, stock_quantity, supplier)
                    VALUES (?, ?, ?, ?, ?)
                ''', sample_products)

            conn.commit()

        except Exception as e:
            print(f"Error creating sample tables: {e}")
        finally:
            conn.close()

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle SQL tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            tool_methods = {
                "execute_query": self._execute_query,
                "get_table_schema": self._get_table_schema,
                "list_tables": self._list_tables,
                "get_table_info": self._get_table_info,
                "search_customers": self._search_customers,
                "search_products": self._search_products,
                "get_statistics": self._get_statistics,
                "insert_record": self._insert_record,
                "update_record": self._update_record,
                "delete_record": self._delete_record
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
        """Execute a SQL query"""
        query = params.get('query', '')

        if not query:
            return {"error": "Query is required"}

        # Basic safety check (in production, use proper parameterization)
        dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER']
        if any(keyword in query.upper() for keyword in dangerous_keywords):
            if not params.get('allow_dangerous', False):
                return {"error": "Dangerous operation not allowed. Set allow_dangerous=True to proceed."}

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(query)

            # Check if it's a SELECT query
            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                results = [dict(row) for row in rows]

                return {
                    "query": query,
                    "results": results,
                    "row_count": len(results)
                }
            else:
                conn.commit()
                return {
                    "query": query,
                    "rows_affected": cursor.rowcount,
                    "message": "Query executed successfully"
                }

        except Exception as e:
            return {"error": str(e), "query": query}
        finally:
            conn.close()

    def _get_table_schema(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get schema information for a table"""
        table_name = params.get('table_name', '')

        if not table_name:
            return {"error": "Table name is required"}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            schema = []
            for col in columns:
                schema.append({
                    "column_id": col[0],
                    "name": col[1],
                    "type": col[2],
                    "not_null": bool(col[3]),
                    "default_value": col[4],
                    "is_primary_key": bool(col[5])
                })

            return {
                "table_name": table_name,
                "schema": schema,
                "column_count": len(schema)
            }

        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

    def _list_tables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all tables in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            return {
                "database": self.db_path,
                "tables": tables,
                "table_count": len(tables)
            }

        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

    def _get_table_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a table"""
        table_name = params.get('table_name', '')

        if not table_name:
            return {"error": "Table name is required"}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Get schema
            schema_result = self._get_table_schema(params)

            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]

            # Get sample rows
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
            conn.row_factory = sqlite3.Row
            cursor.row_factory = sqlite3.Row
            sample_rows = [dict(row) for row in cursor.fetchall()]

            return {
                "table_name": table_name,
                "schema": schema_result.get('schema', []),
                "row_count": row_count,
                "sample_rows": sample_rows
            }

        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

    def _search_customers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for customers"""
        search_term = params.get('search_term', '')
        country = params.get('country', '')

        query = "SELECT * FROM customers WHERE 1=1"
        query_params = []

        if search_term:
            query += " AND (name LIKE ? OR email LIKE ?)"
            query_params.extend([f"%{search_term}%", f"%{search_term}%"])

        if country:
            query += " AND country = ?"
            query_params.append(country)

        return self._execute_query({
            'query': query,
            'params': query_params
        })

    def _search_products(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for products"""
        category = params.get('category', '')
        min_price = params.get('min_price', 0)
        max_price = params.get('max_price', 999999)

        query = "SELECT * FROM products WHERE price >= ? AND price <= ?"
        query_params = [min_price, max_price]

        if category:
            query += " AND category = ?"
            query_params.append(category)

        query += " ORDER BY price"

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(query, query_params)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]

            return {
                "results": results,
                "count": len(results),
                "filters": {
                    "category": category,
                    "min_price": min_price,
                    "max_price": max_price
                }
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

    def _get_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            stats = {}

            # Customer statistics
            cursor.execute("SELECT COUNT(*), AVG(total_purchases), SUM(total_purchases) FROM customers")
            cust_stats = cursor.fetchone()
            stats['customers'] = {
                'total_count': cust_stats[0],
                'avg_purchases': round(cust_stats[1], 2) if cust_stats[1] else 0,
                'total_revenue': round(cust_stats[2], 2) if cust_stats[2] else 0
            }

            # Product statistics
            cursor.execute("SELECT COUNT(*), AVG(price), SUM(stock_quantity * price) FROM products")
            prod_stats = cursor.fetchone()
            stats['products'] = {
                'total_count': prod_stats[0],
                'avg_price': round(prod_stats[1], 2) if prod_stats[1] else 0,
                'total_inventory_value': round(prod_stats[2], 2) if prod_stats[2] else 0
            }

            # Category breakdown
            cursor.execute("SELECT category, COUNT(*), AVG(price) FROM products GROUP BY category")
            categories = []
            for row in cursor.fetchall():
                categories.append({
                    'category': row[0],
                    'product_count': row[1],
                    'avg_price': round(row[2], 2) if row[2] else 0
                })
            stats['categories'] = categories

            return {"statistics": stats}

        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

    def _insert_record(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new record"""
        table = params.get('table', '')
        data = params.get('data', {})

        if not table or not data:
            return {"error": "Table and data are required"}

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        values = list(data.values())

        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(query, values)
            conn.commit()

            return {
                "message": "Record inserted successfully",
                "table": table,
                "inserted_id": cursor.lastrowid
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

    def _update_record(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record"""
        table = params.get('table', '')
        data = params.get('data', {})
        where = params.get('where', {})

        if not table or not data or not where:
            return {"error": "Table, data, and where clause are required"}

        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])

        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        values = list(data.values()) + list(where.values())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(query, values)
            conn.commit()

            return {
                "message": "Record updated successfully",
                "table": table,
                "rows_affected": cursor.rowcount
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()

    def _delete_record(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a record"""
        table = params.get('table', '')
        where = params.get('where', {})

        if not table or not where:
            return {"error": "Table and where clause are required"}

        where_clause = ' AND '.join([f"{k} = ?" for k in where.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        values = list(where.values())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(query, values)
            conn.commit()

            return {
                "message": "Record deleted successfully",
                "table": table,
                "rows_affected": cursor.rowcount
            }
        except Exception as e:
            return {"error": str(e)}
        finally:
            conn.close()