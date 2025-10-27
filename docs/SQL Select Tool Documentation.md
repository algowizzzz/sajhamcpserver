# SQL Select Tool Documentation

**Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com**

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Available Actions](#available-actions)
7. [Usage Examples](#usage-examples)
   - [Using Web UI](#using-web-ui)
   - [Using API Programmatically](#using-api-programmatically)
8. [Data Sources](#data-sources)
9. [Query Examples](#query-examples)
10. [Security Considerations](#security-considerations)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The **SQL Select Tool** is a powerful data query tool that allows users to execute SQL SELECT queries on configured data sources. It extends the `BaseMCPTool` class and supports CSV, Parquet, and JSON files through an in-memory DuckDB database, providing fast and efficient data analysis capabilities.

### Key Capabilities

- Execute SQL SELECT queries on multiple data sources
- List and describe available data sources
- Get schema information for tables
- Retrieve sample data
- Count rows with optional filtering
- Support for complex SQL queries with JOINs, aggregations, and filtering
- Built-in execution tracking and metrics (inherited from BaseMCPTool)

---

## Architecture

### Class Hierarchy

```
BaseMCPTool (Abstract Base Class)
    ├── Properties: name, description, version, enabled
    ├── Methods: execute_with_tracking(), get_metrics(), validate_arguments()
    └── Abstract Methods: execute(), get_input_schema()
         
         └── SqlSelectTool (Extends BaseMCPTool)
              ├── DuckDB Integration
              ├── Data Source Management
              └── Query Execution
```

### Design Benefits

By extending `BaseMCPTool`, the SQL Select Tool automatically gains:

- **Execution Tracking**: Automatic tracking of execution count, time, and last execution
- **Metrics Collection**: Built-in metrics for monitoring and performance analysis
- **Validation**: Argument validation against input schema
- **Enable/Disable**: Tool can be enabled or disabled dynamically
- **Logging**: Integrated logging with proper log levels
- **MCP Format**: Automatic conversion to MCP protocol format
- **Configuration Management**: Standardized configuration loading

---

## Features

- **Multi-format Support**: Works with CSV, Parquet, and JSON files
- **Fast In-Memory Processing**: Uses DuckDB for high-performance SQL execution
- **Security Built-in**: Only SELECT queries allowed, dangerous operations blocked
- **Easy Configuration**: Simple JSON-based data source configuration
- **Schema Discovery**: Automatic schema detection and column type inference
- **Result Limiting**: Automatic result limiting to prevent memory issues
- **RESTful API**: Easy integration with existing applications
- **Execution Metrics**: Built-in performance tracking and monitoring
- **Tool Management**: Enable/disable, metrics, and configuration management

---

## Installation

### Prerequisites

- Python 3.8 or higher
- DuckDB library
- BaseMCPTool class (from MCP Server)

### Install Dependencies

```bash
pip install duckdb
```

### Setup Data Directory

1. Create the data directory structure:
```bash
mkdir -p data/sqlselect
```

2. Copy sample data files to the data directory:
```bash
cp customers.csv data/sqlselect/
cp products.csv data/sqlselect/
cp orders.csv data/sqlselect/
cp sales.csv data/sqlselect/
```

3. Place the tool files:
```
tools/
├── impl/
│   ├── base_mcp_tool.py      (Base class)
│   └── sqlselect_tool.py     (SQL Select implementation)
└── configs/
    └── sqlselect.json         (Configuration)
```

---

## Configuration

The tool is configured using a JSON file (`sqlselect.json`):

```json
{
  "name": "sqlselect",
  "implementation": "tools.impl.sqlselect_tool.SqlSelectTool",
  "description": "SQL SELECT query tool for configured data sources",
  "version": "1.0.0",
  "enabled": true,
  "data_directory": "data/sqlselect",
  "data_sources": {
    "customers": {
      "file": "customers.csv",
      "type": "csv",
      "description": "Customer master data"
    },
    "orders": {
      "file": "orders.csv",
      "type": "csv",
      "description": "Order transactions"
    },
    "products": {
      "file": "products.csv",
      "type": "csv",
      "description": "Product catalog"
    },
    "sales": {
      "file": "sales.csv",
      "type": "csv",
      "description": "Sales data"
    }
  }
}
```

### Configuration Parameters

| Parameter | Description | Required | Default |
|-----------|-------------|----------|---------|
| `name` | Tool name | Yes | - |
| `implementation` | Python class path | Yes | - |
| `description` | Tool description | Yes | - |
| `version` | Tool version | Yes | "1.0.0" |
| `enabled` | Enable/disable tool | No | true |
| `data_directory` | Path to data files | Yes | - |
| `data_sources` | Data source configurations | Yes | - |

---

## Available Actions

### 1. list_sources

List all available data sources.

**Parameters**: None

**Example Request**:
```json
{
  "action": "list_sources"
}
```

**Example Response**:
```json
{
  "success": true,
  "action": "list_sources",
  "data": {
    "sources": [
      {
        "name": "customers",
        "file": "customers.csv",
        "type": "csv",
        "description": "Customer master data"
      }
    ],
    "count": 4
  },
  "timestamp": "2024-10-26T10:30:00"
}
```

---

### 2. describe_source

Get detailed information about a specific data source.

**Parameters**:
- `source_name` (required): Name of the data source

**Example Request**:
```json
{
  "action": "describe_source",
  "source_name": "customers"
}
```

**Example Response**:
```json
{
  "success": true,
  "action": "describe_source",
  "data": {
    "source_name": "customers",
    "file": "customers.csv",
    "type": "csv",
    "description": "Customer master data",
    "row_count": 20,
    "columns": [
      {
        "name": "customer_id",
        "type": "VARCHAR",
        "null": "YES",
        "key": null
      }
    ]
  },
  "timestamp": "2024-10-26T10:30:00"
}
```

---

### 3. execute_query

Execute a SQL SELECT query.

**Parameters**:
- `query` (required): SQL SELECT query
- `limit` (optional): Maximum rows to return (default: 100, max: 10000)

**Example Request**:
```json
{
  "action": "execute_query",
  "query": "SELECT customer_name, city FROM customers WHERE state = 'CA'",
  "limit": 50
}
```

**Example Response**:
```json
{
  "success": true,
  "action": "execute_query",
  "data": {
    "columns": ["customer_name", "city"],
    "rows": [
      {
        "customer_name": "Emma Johnson",
        "city": "Los Angeles"
      }
    ],
    "row_count": 4,
    "query": "SELECT customer_name, city FROM customers WHERE state = 'CA' LIMIT 50"
  },
  "timestamp": "2024-10-26T10:30:00"
}
```

---

### 4. sample_data

Get sample data from a data source.

**Parameters**:
- `source_name` (required): Name of the data source
- `limit` (optional): Number of sample rows (default: 10)

**Example Request**:
```json
{
  "action": "sample_data",
  "source_name": "products",
  "limit": 5
}
```

---

### 5. get_schema

Get schema information for a data source.

**Parameters**:
- `source_name` (required): Name of the data source

**Example Request**:
```json
{
  "action": "get_schema",
  "source_name": "orders"
}
```

---

### 6. count_rows

Count rows in a data source with optional filtering.

**Parameters**:
- `source_name` (required): Name of the data source
- `where_clause` (optional): WHERE clause for filtering

**Example Request**:
```json
{
  "action": "count_rows",
  "source_name": "customers",
  "where_clause": "status = 'Active'"
}
```

---

## Usage Examples

### Using Web UI

#### Step 1: Navigate to Tools Page

1. Log in to the SAJHA MCP Server
2. Click on **Tools** in the navigation menu
3. Find **sqlselect** in the tools list
4. Click **Execute** button

#### Step 2: List Available Data Sources

1. Select action: `list_sources`
2. Click **Execute Tool**
3. View the list of available data sources

#### Step 3: Execute a Query

1. Select action: `execute_query`
2. Enter query:
   ```sql
   SELECT customer_name, email, city 
   FROM customers 
   WHERE state = 'CA' AND status = 'Active'
   ```
3. Set limit: `50`
4. Click **Execute Tool**
5. View results in the output panel

---

### Using API Programmatically

#### Python Example with BaseMCPTool Features

```python
import requests
import json

# API Configuration
BASE_URL = "http://localhost:5000"
API_TOKEN = "your_api_token_here"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

# Example 1: Execute query using execute_with_tracking
def execute_query_tracked(query, limit=100):
    """
    Execute query with automatic tracking
    Uses execute_with_tracking from BaseMCPTool
    """
    payload = {
        "tool": "sqlselect",
        "arguments": {
            "action": "execute_query",
            "query": query,
            "limit": limit
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/tools/execute",
        headers=headers,
        json=payload
    )
    
    return response.json()

# Example 2: Get tool metrics
def get_tool_metrics():
    """
    Get execution metrics for the SQL Select Tool
    Inherited from BaseMCPTool.get_metrics()
    """
    response = requests.get(
        f"{BASE_URL}/api/tools/sqlselect/metrics",
        headers=headers
    )
    
    return response.json()

# Example 3: Enable/Disable tool
def toggle_tool(enabled: bool):
    """
    Enable or disable the tool
    Uses BaseMCPTool.enable() or BaseMCPTool.disable()
    """
    action = "enable" if enabled else "disable"
    response = requests.post(
        f"{BASE_URL}/api/admin/tools/sqlselect/{action}",
        headers=headers
    )
    
    return response.json()

# Example 4: Complex query with tracking
def analyze_sales_by_region():
    query = """
        SELECT 
            region,
            COUNT(*) as sale_count,
            SUM(total_price) as total_revenue
        FROM sales
        GROUP BY region
        ORDER BY total_revenue DESC
    """
    
    result = execute_query_tracked(query)
    print(json.dumps(result, indent=2))
    
    # Get metrics to see execution stats
    metrics = get_tool_metrics()
    print("\nTool Metrics:")
    print(f"  Executions: {metrics['execution_count']}")
    print(f"  Avg Time: {metrics['average_execution_time']:.3f}s")
    
if __name__ == "__main__":
    # Run examples
    analyze_sales_by_region()
```

#### cURL Examples

**Execute Query**:
```bash
curl -X POST http://localhost:5000/api/tools/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "tool": "sqlselect",
    "arguments": {
      "action": "execute_query",
      "query": "SELECT * FROM customers LIMIT 10"
    }
  }'
```

**Get Tool Metrics**:
```bash
curl -X GET http://localhost:5000/api/tools/sqlselect/metrics \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Enable/Disable Tool**:
```bash
# Disable tool
curl -X POST http://localhost:5000/api/admin/tools/sqlselect/disable \
  -H "Authorization: Bearer YOUR_TOKEN"

# Enable tool
curl -X POST http://localhost:5000/api/admin/tools/sqlselect/enable \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Data Sources

### Customers Table
- **Records**: 20 customers
- **Columns**: customer_id, customer_name, email, phone, city, state, country, registration_date, status

### Products Table
- **Records**: 20 products  
- **Columns**: product_id, product_name, category, brand, price, cost, stock_quantity, reorder_level, supplier, status

### Orders Table
- **Records**: 25 orders
- **Columns**: order_id, customer_id, order_date, ship_date, status, payment_method, total_amount, shipping_cost, discount_amount, tax_amount

### Sales Table
- **Records**: 44 sales
- **Columns**: sale_id, order_id, customer_id, customer_name, product_id, product_name, category, quantity, unit_price, total_price, sale_date, region

---

## Query Examples

### Basic Queries

```sql
-- Select all active customers
SELECT * FROM customers WHERE status = 'Active'

-- Get products by category
SELECT product_name, price 
FROM products 
WHERE category = 'Electronics' 
ORDER BY price DESC

-- Count orders by status
SELECT status, COUNT(*) as order_count 
FROM orders 
GROUP BY status
```

### Advanced Queries with JOINs

```sql
-- Customer orders with totals
SELECT 
    c.customer_name,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_name
ORDER BY total_spent DESC

-- Product sales summary
SELECT 
    p.product_name,
    SUM(s.quantity) as total_sold,
    SUM(s.total_price) as revenue
FROM products p
INNER JOIN sales s ON p.product_id = s.product_id
GROUP BY p.product_name
ORDER BY revenue DESC
LIMIT 10
```

---

## Security Considerations

### Query Restrictions

1. **Only SELECT queries allowed**: INSERT, UPDATE, DELETE, DROP operations are blocked
2. **Keyword filtering**: Dangerous SQL keywords are filtered
3. **Automatic LIMIT**: Queries without LIMIT get an automatic limit
4. **Result size control**: Maximum 10,000 rows

### Best Practices

1. Use parameterized queries when building queries programmatically
2. Validate user input before constructing queries
3. Set appropriate limits to prevent large result sets
4. Monitor query performance using tool metrics
5. Regular security audits of query patterns

### Access Control

- Tool access controlled by MCP server's user management
- Users need appropriate permissions to execute the tool
- Admin users can enable/disable tools and monitor metrics
- BaseMCPTool provides built-in execution tracking

---

## Troubleshooting

### Common Issues

**Issue**: "Tool is disabled"
- **Solution**: Enable the tool using admin API or web UI
- Use: `POST /api/admin/tools/sqlselect/enable`

**Issue**: "Data source not found"
- **Solution**: Verify data source name matches configuration
- Check that data files exist in configured directory

**Issue**: "Query execution failed"
- **Solution**: Check SQL syntax
- Verify column names using `get_schema` action
- Review tool logs for detailed error messages

### Debug Tips

1. **Check tool metrics** to see if tool is being executed
2. **Review logs** - BaseMCPTool provides detailed logging
3. **Use sample_data action** to verify data is loaded
4. **Test with simple queries** before complex ones
5. **Monitor execution time** using metrics endpoint

### Performance Tips

1. Use LIMIT clause to restrict result sets
2. Filter early with WHERE clauses
3. Monitor metrics for slow queries
4. Check average_execution_time in metrics
5. Use appropriate indexes for large datasets

---

## Tool Metrics

The SQL Select Tool inherits metrics tracking from BaseMCPTool:

```json
{
  "name": "sqlselect",
  "version": "1.0.0",
  "enabled": true,
  "execution_count": 150,
  "last_execution": "2024-10-26T14:30:00Z",
  "total_execution_time": 45.2,
  "average_execution_time": 0.301
}
```

### Metrics Explanation

- **execution_count**: Total number of executions
- **last_execution**: ISO timestamp of last execution
- **total_execution_time**: Total time spent executing (seconds)
- **average_execution_time**: Average execution time per call (seconds)

---

## Support

For issues, questions, or feature requests:

- **Email**: ajsinha@gmail.com
- **Documentation**: Refer to this guide
- **Version**: 1.0.0

---

**Copyright All rights Reserved 2025-2030, Ashutosh Sinha**