# DuckDB OLAP Tools Documentation

**Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com**

## Overview

The DuckDB OLAP Tools provides a powerful analytical interface for CSV, Parquet, and JSON files using DuckDB's high-performance analytical engine. The tool automatically detects files in the designated directory and creates views for instant SQL querying and OLAP operations.

## Features

- **Automatic File Detection**: Monitors directory for new/removed files
- **Auto-View Creation**: Each file becomes a queryable view
- **SQL Queries**: Execute standard SQL queries
- **OLAP Operations**: Aggregations, grouping, statistics
- **Multi-Format Support**: CSV, Parquet, JSON
- **Schema Inspection**: View table structures
- **Performance**: Leverages DuckDB's columnar engine

## Installation

### Prerequisites

- Python 3.8 or higher
- DuckDB library

### Setup

1. **Install DuckDB:**
   ```bash
   pip install duckdb
   ```

2. **Copy Tool Files:**
   ```bash
   # Copy tool implementation
   cp duckdb_olap_tools_tool.py /path/to/project/tools/impl/
   
   # Copy configuration
   cp duckdb_olap_tools.json /path/to/project/config/tools/
   ```

3. **Create Data Directory:**
   ```bash
   # Create the directory for data files
   mkdir -p data/duckdb
   
   # Copy sample data files
   cp sample_sales_data.csv data/duckdb/
   cp sample_customer_data.csv data/duckdb/
   cp sample_inventory_data.csv data/duckdb/
   ```

4. **Update Registry:**
   
   Add to `tools_registry.py`:
   ```python
   self.builtin_tools = {
       ...
       'duckdb_olap_tools': 'tools.impl.duckdb_olap_tools_tool.DuckDbOlapToolsTool'
   }
   ```

5. **Restart Server:**
   ```bash
   python app.py
   ```

## Configuration

### JSON Configuration File

```json
{
  "name": "duckdb_olap_tools",
  "data_directory": "data/duckdb",
  "enabled": true,
  "rateLimit": 60,
  "cacheTTL": 60
}
```

### Configuration Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `name` | string | Tool name | Yes |
| `data_directory` | string | Path to data files | Yes |
| `enabled` | boolean | Enable/disable tool | No (default: true) |
| `rateLimit` | integer | Max requests per minute | No |

## Usage

### Input Schema

```json
{
  "action": "string (required)",
  "table_name": "string",
  "sql_query": "string",
  "columns": ["string"],
  "group_by": ["string"],
  "aggregations": {"column": "function"},
  "limit": "integer (1-10000, default: 100)"
}
```

### Available Actions

1. **list_tables** - List all available tables/views
2. **describe_table** - Get schema of a table
3. **query** - Execute SQL query
4. **refresh_views** - Refresh file views
5. **get_stats** - Get table statistics
6. **aggregate** - Perform aggregations
7. **list_files** - List data files

## Programmatic Usage (Python)

### Method 1: List Tables

```python
from tools.impl.duckdb_olap_tools_tool import DuckDbOlapToolsTool

# Initialize tool
config = {
    'name': 'duckdb_olap_tools',
    'data_directory': 'data/duckdb',
    'enabled': True
}

tool = DuckDbOlapToolsTool(config)

# Example 1: List all tables
arguments = {
    'action': 'list_tables'
}

result = tool.execute_with_tracking(arguments)

print(f"Available Tables: {result['table_count']}")
for table in result['tables']:
    print(f"- {table['name']}: {table['row_count']} rows")
```

**Output:**
```
Available Tables: 3
- sample_sales_data: 20 rows
- sample_customer_data: 10 rows
- sample_inventory_data: 10 rows
```

### Method 2: Describe Table Schema

```python
# Example 2: Describe table
arguments = {
    'action': 'describe_table',
    'table_name': 'sample_sales_data'
}

result = tool.execute_with_tracking(arguments)

print(f"Table: {result['table_name']}")
print(f"Columns: {result['column_count']}\n")

for col in result['columns']:
    print(f"- {col['name']}: {col['type']}")

print(f"\nSample Data:")
for row in result['sample_data'][:3]:
    print(row)
```

**Output:**
```
Table: sample_sales_data
Columns: 8

- order_id: BIGINT
- customer_id: VARCHAR
- product: VARCHAR
- category: VARCHAR
- quantity: BIGINT
- price: DOUBLE
- order_date: DATE
- region: VARCHAR

Sample Data:
(1001, 'C001', 'Laptop', 'Electronics', 1, 1200.0, ...)
(1002, 'C002', 'Mouse', 'Electronics', 2, 25.5, ...)
(1003, 'C001', 'Keyboard', 'Electronics', 1, 75.0, ...)
```

### Method 3: Execute SQL Query

```python
# Example 3: Execute SQL query
arguments = {
    'action': 'query',
    'sql_query': 'SELECT region, COUNT(*) as orders, SUM(price * quantity) as revenue FROM sample_sales_data GROUP BY region ORDER BY revenue DESC',
    'limit': 10
}

result = tool.execute_with_tracking(arguments)

print(f"Query Results: {result['row_count']} rows\n")
print(f"Columns: {result['columns']}\n")

for row in result['rows']:
    print(f"{row[0]}: {row[1]} orders, ${row[2]:.2f} revenue")
```

**Output:**
```
Query Results: 4 rows

Columns: ['region', 'orders', 'revenue']

North: 6 orders, $4330.00 revenue
South: 5 orders, $3401.00 revenue
East: 5 orders, $1801.50 revenue
West: 4 orders, $1683.00 revenue
```

### Method 4: Get Table Statistics

```python
# Example 4: Get statistics
arguments = {
    'action': 'get_stats',
    'table_name': 'sample_sales_data'
}

result = tool.execute_with_tracking(arguments)

print(f"Table: {result['table_name']}")
print(f"Rows: {result['row_count']}")
print(f"Columns: {result['column_count']}\n")

print("Statistics:")
for col, stats in result['statistics'].items():
    print(f"\n{col}:")
    for stat_name, value in stats.items():
        print(f"  {stat_name}: {value}")
```

**Output:**
```
Table: sample_sales_data
Rows: 20
Columns: 8

Statistics:

order_id:
  min: 1001
  max: 1020
  avg: 1010.5
  distinct: 20

quantity:
  min: 1
  max: 4
  avg: 1.65
  distinct: 4

price:
  min: 25.5
  max: 1400.0
  avg: 397.75
  distinct: 13
```

### Method 5: Perform Aggregations

```python
# Example 5: Aggregate data
arguments = {
    'action': 'aggregate',
    'table_name': 'sample_sales_data',
    'aggregations': {
        'quantity': 'sum',
        'price': 'avg',
        'order_id': 'count'
    },
    'group_by': ['category']
}

result = tool.execute_with_tracking(arguments)

print(f"Aggregation Results:\n")
print(f"Columns: {result['columns']}\n")

for row in result['rows']:
    print(f"Category: {row[0]}")
    print(f"  Total Quantity: {row[1]}")
    print(f"  Avg Price: ${row[2]:.2f}")
    print(f"  Order Count: {row[3]}")
    print()
```

**Output:**
```
Aggregation Results:

Columns: ['category', 'quantity_sum', 'price_avg', 'order_id_count']

Category: Electronics
  Total Quantity: 24
  Avg Price: $483.13
  Order Count: 14

Category: Furniture
  Total Quantity: 11
  Avg Price: $333.33
  Order Count: 6
```

### Method 6: Refresh Views

```python
# Example 6: Refresh views (after adding new files)
arguments = {
    'action': 'refresh_views'
}

result = tool.execute_with_tracking(arguments)

print(f"Status: {result['status']}")
print(f"Previous Files: {result['previous_files']}")
print(f"Current Files: {result['current_files']}")
print(f"Files Added: {result['files_added']}")
print(f"Files Removed: {result['files_removed']}")
```

### Method 7: Complex Analytics Query

```python
# Example 7: Complex JOIN query
arguments = {
    'action': 'query',
    'sql_query': '''
        SELECT 
            c.customer_name,
            c.customer_tier,
            COUNT(s.order_id) as order_count,
            SUM(s.price * s.quantity) as total_spent
        FROM sample_sales_data s
        JOIN sample_customer_data c ON s.customer_id = c.customer_id
        GROUP BY c.customer_name, c.customer_tier
        ORDER BY total_spent DESC
    ''',
    'limit': 10
}

result = tool.execute_with_tracking(arguments)

print("Top Customers:\n")
for row in result['rows']:
    print(f"{row[0]} ({row[1]}): {row[2]} orders, ${row[3]:.2f}")
```

### Method 8: Window Functions

```python
# Example 8: Use window functions
arguments = {
    'action': 'query',
    'sql_query': '''
        SELECT 
            order_date,
            region,
            price * quantity as revenue,
            SUM(price * quantity) OVER (PARTITION BY region ORDER BY order_date) as running_total
        FROM sample_sales_data
        ORDER BY region, order_date
    ''',
    'limit': 20
}

result = tool.execute_with_tracking(arguments)
```

### Method 9: List Files

```python
# Example 9: List data files
arguments = {
    'action': 'list_files'
}

result = tool.execute_with_tracking(arguments)

print(f"Data Directory: {result['directory']}")
print(f"Files: {result['file_count']}\n")

for file in result['files']:
    print(f"File: {file['filename']}")
    print(f"  View Name: {file['view_name']}")
    print(f"  Size: {file['size_mb']} MB")
    print(f"  Modified: {file['modified']}")
    print()
```

### Error Handling

```python
try:
    result = tool.execute_with_tracking(arguments)
    
    # Check for DuckDB availability
    if 'error' in result:
        print(f"Error: {result['error']}")
        print(f"Note: {result['note']}")
    else:
        # Process results
        pass
        
except ValueError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Web UI Usage

### Example 1: List Tables via Web UI

**Step 1: Navigate to tools**
- Go to `http://your-server:port/tools`
- Find "duckdb_olap_tools"

**Step 2: Fill form**
```
Action: list_tables
```

**Step 3: Execute**
- Click "Execute Tool"

**Expected Output:**
```json
{
  "table_count": 3,
  "tables": [
    {"name": "sample_sales_data", "row_count": 20},
    {"name": "sample_customer_data", "row_count": 10},
    {"name": "sample_inventory_data", "row_count": 10}
  ],
  "data_directory": "data/duckdb"
}
```

### Example 2: Execute Query via Web UI

**Form Input:**
```
Action: query
SQL Query: SELECT category, COUNT(*) as count, SUM(price * quantity) as total FROM sample_sales_data GROUP BY category
Limit: 100
```

**Expected Output:**
- Query results with columns
- Row count
- Data rows

### Example 3: Describe Table via Web UI

**Form Input:**
```
Action: describe_table
Table Name: sample_sales_data
```

**Expected Output:**
- Column names and types
- Sample data rows

### Example 4: Get Statistics via Web UI

**Form Input:**
```
Action: get_stats
Table Name: sample_customer_data
```

**Expected Output:**
- Row count
- Column statistics
- Min/max/avg values

### Example 5: Aggregate Data via Web UI

**Form Input:**
```
Action: aggregate
Table Name: sample_sales_data
Aggregations: {"quantity": "sum", "price": "avg"}
Group By: ["region"]
```

**Expected Output:**
- Aggregated results by region
- Sum of quantities
- Average prices

## API Endpoint Usage

### REST API Call

```bash
# List tables
curl -X POST http://your-server:port/api/tools/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "tool": "duckdb_olap_tools",
    "arguments": {
      "action": "list_tables"
    }
  }'
```

### Python Requests

```python
import requests
import json

url = "http://your-server:port/api/tools/execute"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_TOKEN"
}

# Example 1: Execute query
payload = {
    "tool": "duckdb_olap_tools",
    "arguments": {
        "action": "query",
        "sql_query": "SELECT * FROM sample_sales_data WHERE category = 'Electronics'",
        "limit": 20
    }
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    result = response.json()
    
    if result['success']:
        data = result['result']
        print(f"Query returned {data['row_count']} rows")
        for row in data['rows']:
            print(row)
```

```python
# Example 2: Get aggregations
payload = {
    "tool": "duckdb_olap_tools",
    "arguments": {
        "action": "aggregate",
        "table_name": "sample_sales_data",
        "aggregations": {
            "quantity": "sum",
            "price": "avg"
        },
        "group_by": ["category", "region"]
    }
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()['result']

print("Aggregation Results:")
for row in data['rows']:
    print(f"{row[0]} - {row[1]}: Sum={row[2]}, Avg=${row[3]:.2f}")
```

## Sample Data Files

### sample_sales_data.csv

Contains 20 sales orders with:
- order_id, customer_id, product, category
- quantity, price, order_date, region

### sample_customer_data.csv

Contains 10 customers with:
- customer_id, customer_name, email, country
- signup_date, total_purchases, customer_tier

### sample_inventory_data.csv

Contains 10 products with:
- product_id, product_name, category
- stock_quantity, reorder_level
- unit_cost, unit_price, supplier

## Automatic View Management

### How It Works

1. **Initialization**: Tool scans `data/duckdb` directory
2. **View Creation**: Each file becomes a view with sanitized name
3. **Monitoring**: Registry tracks files and modification times
4. **Auto-Update**: New files automatically registered on access
5. **Auto-Cleanup**: Deleted files removed from views

### View Naming

Files are converted to view names:
- `sample_sales_data.csv` → `sample_sales_data`
- `my-file.csv` → `my_file`
- `Data 2024.csv` → `data_2024`

### Adding New Files

```bash
# Simply copy files to data directory
cp new_data.csv data/duckdb/

# Views refresh automatically on next query
# Or force refresh:
# action: refresh_views
```

### Removing Files

```bash
# Delete file
rm data/duckdb/old_data.csv

# Views refresh automatically
# Or force refresh with refresh_views action
```

## Response Formats

### List Tables Response

```json
{
  "table_count": 3,
  "tables": [
    {
      "name": "sample_sales_data",
      "row_count": 20
    }
  ],
  "data_directory": "data/duckdb"
}
```

### Query Response

```json
{
  "query": "SELECT * FROM sample_sales_data LIMIT 10",
  "columns": ["order_id", "customer_id", ...],
  "row_count": 10,
  "rows": [[1001, "C001", ...], ...],
  "limited": true
}
```

### Statistics Response

```json
{
  "table_name": "sample_sales_data",
  "row_count": 20,
  "column_count": 8,
  "columns": ["order_id", ...],
  "statistics": {
    "price": {
      "min": 25.5,
      "max": 1400.0,
      "avg": 397.75,
      "distinct": 13
    }
  }
}
```

## Best Practices

### 1. File Organization

```bash
# Organize by date or category
data/duckdb/
├── 2024/
│   ├── sales_q1.csv
│   └── sales_q2.csv
├── customers/
│   └── active_customers.csv
└── inventory/
    └── current_stock.csv
```

### 2. Query Optimization

```python
# Use limits for large datasets
arguments = {
    'action': 'query',
    'sql_query': 'SELECT * FROM large_table',
    'limit': 1000  # Prevent memory issues
}

# Use aggregations instead of fetching all rows
arguments = {
    'action': 'aggregate',
    'table_name': 'large_table',
    'aggregations': {'revenue': 'sum'},
    'group_by': ['category']
}
```

### 3. Refresh Views After File Changes

```python
# After adding/removing files
result = tool.execute_with_tracking({
    'action': 'refresh_views'
})

# Then query new data
result = tool.execute_with_tracking({
    'action': 'list_tables'
})
```

### 4. Use Appropriate Aggregations

```python
# Good: Specific aggregations
aggregations = {
    'revenue': 'sum',
    'quantity': 'avg',
    'order_id': 'count'
}

# Efficient: Group by low-cardinality columns
group_by = ['category', 'region']  # Good
# group_by = ['customer_id']  # May create many groups
```

## Troubleshooting

### Issue: "DuckDB not available"

**Solution:**
```bash
pip install duckdb
```

Verify installation:
```bash
python -c "import duckdb; print('DuckDB installed')"
```

### Issue: "Table not found"

**Solutions:**
1. Check file exists in `data/duckdb/`
2. Refresh views:
   ```python
   tool.execute_with_tracking({'action': 'refresh_views'})
   ```
3. List available tables:
   ```python
   tool.execute_with_tracking({'action': 'list_tables'})
   ```

### Issue: Query performance slow

**Solutions:**
1. Use LIMIT clause
2. Add WHERE conditions to filter data
3. Use aggregations instead of raw data
4. Consider converting CSV to Parquet for better performance

### Issue: File not appearing as view

**Solutions:**
1. Check file extension (.csv, .parquet, .json)
2. Verify file is not corrupted
3. Check file permissions
4. Force refresh views

## Supported File Formats

### CSV Files
- Auto-detected delimiter
- Header row required
- UTF-8 encoding recommended

### Parquet Files
- Columnar format
- Best performance
- Compressed by default

### JSON Files
- JSON Lines (JSONL) format
- One JSON object per line
- Auto-schema detection

## Limitations

1. **In-Memory**: Database is in-memory (data not persisted)
2. **File Size**: Large files (>1GB) may cause memory issues
3. **Concurrent Access**: Single connection per tool instance
4. **File Locking**: Files being written may cause errors
5. **View Names**: Must be valid SQL identifiers

## Support

- **DuckDB Documentation**: https://duckdb.org/docs/
- **Tool Support**: ajsinha@gmail.com

## License

Copyright All rights Reserved 2025-2030, Ashutosh Sinha

## Version History

- **v1.0.0** (2024-10-26): Initial release
  - Automatic file detection
  - Auto-view creation
  - SQL queries
  - OLAP operations
  - Statistics and aggregations
  - Multi-format support

---

**End of Documentation**