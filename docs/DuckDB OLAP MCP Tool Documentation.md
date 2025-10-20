# DuckDB OLAP MCP Tool Documentation

## Overview
The DuckDB OLAP MCP Tool provides analytical database capabilities with OLAP operations, data aggregation, and advanced SQL analytics using DuckDB.

## Configuration
- **Environment Variables:**
  - `DUCKDB_DATA_FOLDER` (default: 'data'): Data folder path
- Automatic sample data generation
- In-memory and persistent database options
- CSV file integration

## Sample Data

### Sales Data Table
- 1000 sample records
- Products: Laptop, Phone, Tablet, Monitor, Keyboard
- Regions: North, South, East, West, Central
- Fields: order_id, date, product, region, quantity, unit_price, customer_id, discount, total_amount

### Customer Data Table
- 200 sample customers
- Countries: USA, Canada, UK, Germany, France, Japan
- Segments: Enterprise, SMB, Consumer, Government
- Fields: customer_id, company_name, country, segment, registration_date, credit_limit, status

### Pre-built Views
- `sales_summary`: Aggregated sales by date, product, region
- `customer_sales`: Customer purchase analytics

## Available Methods

### 1. execute_query
Execute a DuckDB SQL query.

**Parameters:**
- `query`: SQL query string (required)

**Returns:**
- Query results (limited to 100 rows)
- Row count
- Column names

**Supports:**
- All DuckDB SQL syntax
- Window functions
- CTEs
- Advanced analytics

### 2. list_tables
List all tables and views in DuckDB.

**Returns:**
- Table names
- Table types (TABLE or VIEW)
- Row counts

### 3. get_table_schema
Get schema information for a table.

**Parameters:**
- `table_name`: Name of table (required)

**Returns:**
- Column details (name, type, nullable, default)
- Sample data (5 rows)

### 4. aggregate_data
Perform aggregation operations.

**Parameters:**
- `table` (default: 'sales'): Table to aggregate
- `group_by`: List of grouping columns (required)
- `aggregations`: Dictionary of column: function pairs
- `filters` (optional): Filter conditions

**Aggregation Functions:**
- SUM, AVG, COUNT, MIN, MAX
- STDDEV, VARIANCE
- Any DuckDB aggregate function

**Returns:**
- Aggregated results
- Applied query

### 5. pivot_data
Create pivot table.

**Parameters:**
- `table` (default: 'sales'): Source table
- `rows`: Row dimension columns (required)
- `columns`: Column dimension columns (required)
- `values`: Value column (required)
- `agg_func` (default: 'SUM'): Aggregation function

**Returns:**
- Pivoted data
- Result dimensions

### 6. time_series_analysis
Perform time series analysis.

**Parameters:**
- `table` (default: 'sales'): Source table
- `date_column` (default: 'date'): Date column
- `value_column` (default: 'total_amount'): Value to analyze
- `granularity` (default: 'month'): 'day', 'week', 'month', 'quarter', 'year'

**Returns:**
- Time series aggregations
- Period statistics (count, total, average, min, max)

### 7. top_n_analysis
Get top N records by a metric.

**Parameters:**
- `table` (default: 'sales'): Source table
- `group_by` (default: 'product'): Grouping column
- `metric` (default: 'total_amount'): Metric column
- `agg_func` (default: 'SUM'): Aggregation function
- `n` (default: 10): Number of results
- `order` (default: 'DESC'): Sort order

**Returns:**
- Top N results
- Metric values

### 8. window_functions
Apply window functions for advanced analytics.

**Parameters:**
- `table` (default: 'sales'): Source table
- `partition_by` (optional): Partition column
- `order_by` (default: 'date'): Order column
- `window_type` (default: 'row_number'): Window function type

**Window Types:**
- row_number
- rank
- dense_rank
- lag
- lead
- cumsum

**Returns:**
- Data with window function results

### 9. join_tables
Join multiple tables.

**Parameters:**
- `left_table` (default: 'sales'): Left table
- `right_table` (default: 'customers'): Right table
- `join_type` (default: 'INNER'): 'INNER', 'LEFT', 'RIGHT', 'FULL'
- `join_key` (default: 'customer_id'): Join column

**Returns:**
- Joined data (limited to 100 rows)

### 10. load_csv
Load a new CSV file into DuckDB.

**Parameters:**
- `file_path`: CSV file path (required)
- `table_name`: Target table name (required)

**Returns:**
- Table creation confirmation
- Row count

### 11. export_results
Export query results to CSV.

**Parameters:**
- `query`: SQL query (required)
- `output_file` (default: 'export.csv'): Output filename

**Returns:**
- Export confirmation
- File path

### 12. create_materialized_view
Create a materialized view for performance.

**Parameters:**
- `view_name`: View name (required)
- `query`: SQL query for view (required)

**Returns:**
- View creation confirmation
- Row count

### 13. analyze_performance
Analyze query performance.

**Parameters:**
- `query`: SQL query to analyze (required)

**Returns:**
- Execution plan
- Performance metrics

## SQL Examples

### Aggregation Query
```sql
SELECT 
    product,
    region,
    SUM(total_amount) as revenue,
    COUNT(*) as orders
FROM sales
WHERE date >= '2024-01-01'
GROUP BY product, region
ORDER BY revenue DESC
```

### Window Function Query
```sql
SELECT 
    *,
    ROW_NUMBER() OVER (PARTITION BY region ORDER BY total_amount DESC) as rank
FROM sales
```

### Time Series Query
```sql
SELECT 
    DATE_TRUNC('month', date) as month,
    SUM(total_amount) as monthly_revenue,
    COUNT(DISTINCT customer_id) as unique_customers
FROM sales
GROUP BY 1
ORDER BY 1
```

## Example Usage
```python
# Execute custom query
result = duckdb_tool.handle_tool_call('execute_query', {
    'query': 'SELECT * FROM sales LIMIT 10'
})

# Aggregate data
result = duckdb_tool.handle_tool_call('aggregate_data', {
    'table': 'sales',
    'group_by': ['product', 'region'],
    'aggregations': {
        'total_amount': 'SUM',
        'quantity': 'AVG'
    }
})

# Create pivot table
result = duckdb_tool.handle_tool_call('pivot_data', {
    'table': 'sales',
    'rows': ['product'],
    'columns': ['region'],
    'values': 'total_amount',
    'agg_func': 'SUM'
})

# Time series analysis
result = duckdb_tool.handle_tool_call('time_series_analysis', {
    'table': 'sales',
    'date_column': 'date',
    'value_column': 'total_amount',
    'granularity': 'month'
})

# Top N analysis
result = duckdb_tool.handle_tool_call('top_n_analysis', {
    'table': 'sales',
    'group_by': 'customer_id',
    'metric': 'total_amount',
    'n': 10
})

# Window functions
result = duckdb_tool.handle_tool_call('window_functions', {
    'table': 'sales',
    'partition_by': 'region',
    'order_by': 'total_amount',
    'window_type': 'rank'
})

# Load CSV file
result = duckdb_tool.handle_tool_call('load_csv', {
    'file_path': 'new_data.csv',
    'table_name': 'new_table'
})

# Export results
result = duckdb_tool.handle_tool_call('export_results', {
    'query': 'SELECT * FROM sales WHERE region = "North"',
    'output_file': 'north_sales.csv'
})
```

## Advanced Features

### Performance Optimization
- Automatic query optimization
- Columnar storage
- Vectorized execution
- Parallel processing

### Supported Data Types
- Numeric: INTEGER, BIGINT, DECIMAL, DOUBLE
- String: VARCHAR, TEXT
- Date/Time: DATE, TIME, TIMESTAMP
- Boolean: BOOLEAN
- Arrays and Structs

### OLAP Capabilities
- Roll-up and drill-down
- Slice and dice operations
- Complex aggregations
- Window analytics
- Pivot operations

## Copyright Notice

© 2025 - 2030 Ashutosh Sinha.

All rights reserved. No part of this publication may be reproduced, distributed, or transmitted in any form or by any means, including photocopying, recording, or other electronic or mechanical methods, without the prior written permission of the publisher, except in the case of brief quotations embodied in critical reviews and certain other noncommercial uses permitted by copyright law.