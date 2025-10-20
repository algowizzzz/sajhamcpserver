# DuckDB OLAP MCP Tool Documentation

## Overview
The DuckDB OLAP MCP Tool provides analytical database capabilities with OLAP operations, data aggregation, and advanced SQL analytics using DuckDB. **Enhanced with automatic file discovery, intelligent table management, and auto-refresh capabilities.**

## Key Features

### Automatic File Discovery
- **Auto-detects CSV and Parquet files** in the data folder upon instantiation
- **Recursive scanning** - discovers files in subdirectories
- **Smart table naming** - converts filenames to lowercase table names (e.g., `Sales_Data.csv` → `sales_data`)
- **Schema inference** - automatically detects column types and structure

### Intelligent Table Management
- **Automatic table creation** from discovered files
- **Change detection** - monitors file modifications (size and timestamp)
- **Auto-refresh** - periodically checks for new, modified, or deleted files
- **Synchronized operations** - thread-safe table updates

### Dynamic Refresh System
- **Configurable refresh interval** (default: 10 minutes)
- **Background refresh thread** for continuous monitoring
- **Manual refresh trigger** available via API
- **Change tracking** - reports new, updated, and deleted files

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DUCKDB_DATA_FOLDER` | Path to data folder containing CSV/Parquet files | `data` |
| `DUCKDB_REFRESH_INTERVAL` | Auto-refresh interval in minutes | `10` |
| `DUCKDB_AUTO_REFRESH` | Enable automatic table refresh (true/false) | `true` |

### Example Configuration
```bash
export DUCKDB_DATA_FOLDER=/path/to/data
export DUCKDB_REFRESH_INTERVAL=5
export DUCKDB_AUTO_REFRESH=true
```

## How It Works

### Initialization Process
1. **Scan data folder** for `.csv` and `.parquet` files
2. **Generate table names** from filenames (lowercase, sanitized)
3. **Create tables** with auto-detected schemas
4. **Track file metadata** (modification time, size)
5. **Create default views** (sales_summary, customer_sales if applicable)
6. **Start background refresh** (if auto-refresh enabled)

### Refresh Cycle
Every N minutes (configurable), the system:
1. **Scans for new files** → Creates new tables
2. **Checks for modifications** → Refreshes changed tables
3. **Detects deletions** → Removes corresponding tables
4. **Updates metadata** → Records changes and timestamps

### Table Naming Convention
Files are converted to table names using these rules:
- Convert to lowercase
- Replace spaces and hyphens with underscores
- Remove special characters
- Keep only alphanumeric and underscores

**Examples:**
- `Sales Data.csv` → `sales_data`
- `Customer-Info.parquet` → `customer_info`
- `Q4_Report_2024.csv` → `q4_report_2024`

## Sample Data

### Sales Data Table (`sales_data.csv`)
- 1000 sample records
- Products: Laptop, Phone, Tablet, Monitor, Keyboard
- Regions: North, South, East, West, Central
- Fields: order_id, date, product, region, quantity, unit_price, customer_id, discount, total_amount

### Customer Data Table (`customer_data.csv`)
- 200 sample customers
- Countries: USA, Canada, UK, Germany, France, Japan
- Segments: Enterprise, SMB, Consumer, Government
- Fields: customer_id, company_name, country, segment, registration_date, credit_limit, status

### Pre-built Views
- `sales_summary`: Aggregated sales by date, product, region
- `customer_sales`: Customer purchase analytics

## Available Methods

### New Methods

#### 14. get_loaded_files
Get information about currently loaded files and refresh status.

**Parameters:** None

**Returns:**
- List of loaded files with metadata
- Table names and row counts
- Refresh interval and auto-refresh status
- File sizes and load timestamps

**Example:**
```python
result = duckdb_tool.handle_tool_call('get_loaded_files', {})
```

**Response:**
```json
{
  "loaded_files": [
    {
      "file_path": "/path/to/sales_data.csv",
      "table_name": "sales_data",
      "row_count": 1000,
      "loaded_at": "2025-10-20T10:30:00",
      "size_bytes": 245678
    }
  ],
  "count": 1,
  "refresh_interval_minutes": 10,
  "auto_refresh_enabled": true
}
```

#### 15. refresh_tables
Manually trigger table refresh to discover new, modified, or deleted files.

**Parameters:** None

**Returns:**
- Changes detected (new, updated, deleted files)
- Total tables count
- Success confirmation

**Example:**
```python
result = duckdb_tool.handle_tool_call('refresh_tables', {})
```

**Response:**
```json
{
  "message": "Tables refreshed successfully",
  "changes": {
    "new_files": ["/path/to/new_data.csv"],
    "updated_files": ["/path/to/sales_data.csv"],
    "deleted_files": [],
    "total_tables": 5
  }
}
```

### Core Methods

#### 1. execute_query
Execute a DuckDB SQL query.

**Parameters:**
- `query`: SQL query string (required)

**Returns:**
- Query results (limited to 100 rows)
- Row count
- Column names

#### 2. list_tables
List all tables and views in DuckDB **with source file information**.

**Returns:**
- Table names and types
- Row counts
- **Source file paths** (for auto-discovered tables)

**Enhanced Response:**
```json
{
  "tables": [
    {
      "name": "sales_data",
      "type": "TABLE",
      "row_count": 1000,
      "source_file": "/path/to/sales_data.csv"
    }
  ],
  "count": 1
}
```

#### 3. get_table_schema
Get schema information for a table.

**Parameters:**
- `table_name`: Name of table (required)

**Returns:**
- Column details (name, type, nullable, default)
- Sample data (5 rows)

#### 4. aggregate_data
Perform aggregation operations.

**Parameters:**
- `table` (default: 'sales_data'): Table to aggregate
- `group_by`: List of grouping columns (required)
- `aggregations`: Dictionary of column: function pairs
- `filters` (optional): Filter conditions

#### 5. pivot_data
Create pivot table.

**Parameters:**
- `table` (default: 'sales_data'): Source table
- `rows`: Row dimension columns (required)
- `columns`: Column dimension columns (required)
- `values`: Value column (required)
- `agg_func` (default: 'SUM'): Aggregation function

#### 6. time_series_analysis
Perform time series analysis.

**Parameters:**
- `table` (default: 'sales_data'): Source table
- `date_column` (default: 'date'): Date column
- `value_column` (default: 'total_amount'): Value to analyze
- `granularity` (default: 'month'): Time period

#### 7. top_n_analysis
Get top N records by a metric.

**Parameters:**
- `table` (default: 'sales_data'): Source table
- `group_by` (default: 'product'): Grouping column
- `metric` (default: 'total_amount'): Metric column
- `n` (default: 10): Number of results

#### 8. window_functions
Apply window functions for advanced analytics.

**Parameters:**
- `table` (default: 'sales_data'): Source table
- `partition_by` (optional): Partition column
- `order_by` (default: 'date'): Order column
- `window_type`: row_number, rank, dense_rank, lag, lead, cumsum

#### 9. join_tables
Join multiple tables.

**Parameters:**
- `left_table` (default: 'sales_data'): Left table
- `right_table` (default: 'customer_data'): Right table
- `join_type` (default: 'INNER'): Join type
- `join_key` (default: 'customer_id'): Join column

#### 10. load_csv
Load a new CSV/Parquet file into DuckDB.

**Parameters:**
- `file_path`: File path (required)
- `table_name`: Target table name (optional - **auto-generated from filename**)

**Enhanced Behavior:**
- Table name now optional
- Auto-generates lowercase table name from filename
- Supports both CSV and Parquet formats
- Automatically tracks file in loaded files registry

#### 11. export_results
Export query results to CSV.

**Parameters:**
- `query`: SQL query (required)
- `output_file` (default: 'export.csv'): Output filename

#### 12. create_materialized_view
Create a materialized view for performance.

**Parameters:**
- `view_name`: View name (required)
- `query`: SQL query for view (required)

#### 13. analyze_performance
Analyze query performance.

**Parameters:**
- `query`: SQL query to analyze (required)

## Usage Examples

### Auto-Discovery Workflow

```python
# 1. Drop CSV/Parquet files in data folder
# /data/sales_2024.csv
# /data/products.parquet
# /data/regions.csv

# 2. Tool automatically discovers and loads on initialization
# Tables created: sales_2024, products, regions

# 3. Check loaded files
result = duckdb_tool.handle_tool_call('get_loaded_files', {})

# 4. Query auto-discovered tables
result = duckdb_tool.handle_tool_call('execute_query', {
    'query': 'SELECT * FROM sales_2024 LIMIT 10'
})

# 5. Modify a file (e.g., add more rows to sales_2024.csv)
# Wait for auto-refresh or trigger manually

# 6. Manual refresh
result = duckdb_tool.handle_tool_call('refresh_tables', {})
# Returns: {"changes": {"updated_files": ["sales_2024.csv"], ...}}
```

### Working with Dynamic Tables

```python
# List all tables (includes auto-discovered)
result = duckdb_tool.handle_tool_call('list_tables', {})

# Query any discovered table
result = duckdb_tool.handle_tool_call('execute_query', {
    'query': '''
        SELECT product, SUM(quantity) as total
        FROM sales_2024
        GROUP BY product
    '''
})

# Join auto-discovered tables
result = duckdb_tool.handle_tool_call('join_tables', {
    'left_table': 'sales_2024',
    'right_table': 'products',
    'join_key': 'product_id'
})
```

### Traditional Usage (Still Supported)

```python
# Aggregate data
result = duckdb_tool.handle_tool_call('aggregate_data', {
    'table': 'sales_data',
    'group_by': ['product', 'region'],
    'aggregations': {
        'total_amount': 'SUM',
        'quantity': 'AVG'
    }
})

# Time series analysis
result = duckdb_tool.handle_tool_call('time_series_analysis', {
    'table': 'sales_data',
    'date_column': 'date',
    'value_column': 'total_amount',
    'granularity': 'month'
})

# Top N analysis
result = duckdb_tool.handle_tool_call('top_n_analysis', {
    'table': 'sales_data',
    'group_by': 'customer_id',
    'metric': 'total_amount',
    'n': 10
})
```

## File Format Support

### CSV Files
- Automatic delimiter detection
- Header row detection
- Type inference
- Encoding handling (UTF-8)

### Parquet Files
- Native DuckDB support
- Efficient columnar reading
- Schema preservation
- Compression support

## Advanced Features

### Change Detection Algorithm
```python
# File is considered "changed" if:
# 1. Modification time (mtime) differs
# 2. File size differs
# 3. File is new (not in registry)
```

### Thread Safety
- All table operations are protected by locks
- Background refresh runs in daemon thread
- Safe concurrent access to DuckDB connection

### Performance Optimization
- **Lazy loading** - only loads when accessed
- **Incremental updates** - only refreshes changed tables
- **Columnar storage** - efficient DuckDB storage
- **Vectorized execution** - fast query processing

## Monitoring and Debugging

### Check Refresh Status
```python
result = duckdb_tool.handle_tool_call('get_loaded_files', {})
print(f"Auto-refresh: {result['auto_refresh_enabled']}")
print(f"Interval: {result['refresh_interval_minutes']} minutes")
```

### Monitor File Changes
```python
result = duckdb_tool.handle_tool_call('refresh_tables', {})
print(f"New files: {result['changes']['new_files']}")
print(f"Updated: {result['changes']['updated_files']}")
print(f"Deleted: {result['changes']['deleted_files']}")
```

### Verify Table Sources
```python
result = duckdb_tool.handle_tool_call('list_tables', {})
for table in result['tables']:
    print(f"{table['name']}: {table['source_file']}")
```

## Best Practices

1. **File Naming**: Use descriptive, lowercase names with underscores
2. **Refresh Interval**: Set based on data update frequency (default 10 min is good for most cases)
3. **File Size**: DuckDB handles large files efficiently, but consider partitioning very large datasets
4. **Schema Stability**: Avoid changing column names/types in existing files
5. **Manual Refresh**: Use when you need immediate updates before auto-refresh cycle

## Troubleshooting

### Table Not Appearing
```python
# 1. Check if file is in data folder
# 2. Verify file extension (.csv or .parquet)
# 3. Trigger manual refresh
result = duckdb_tool.handle_tool_call('refresh_tables', {})
```

### Table Not Updating
```python
# 1. Check file modification time
# 2. Verify auto-refresh is enabled
result = duckdb_tool.handle_tool_call('get_loaded_files', {})
# 3. Trigger manual refresh
```

### Performance Issues
```python
# 1. Analyze query performance
result = duckdb_tool.handle_tool_call('analyze_performance', {
    'query': 'YOUR_SLOW_QUERY'
})
# 2. Consider creating materialized views for frequent queries
```

## Migration Guide

### From Previous Version
The enhanced version is **fully backward compatible**. Existing code continues to work without changes.

**What's New:**
- Tables auto-load from files (no need for `_load_data_sources`)
- Table names follow file names (e.g., `sales_data.csv` → `sales_data`)
- Auto-refresh keeps tables synchronized
- New methods: `get_loaded_files`, `refresh_tables`
- Enhanced `list_tables` includes source file information

**No Breaking Changes:**
- All existing methods work as before
- Sample data still created if files don't exist
- Default table names (`sales_data`, `customer_data`) unchanged

## Copyright Notice

© 2025 - 2030 Ashutosh Sinha.

All rights reserved. No part of this publication may be reproduced, distributed, or transmitted in any form or by any means, including photocopying, recording, or other electronic or mechanical methods, without the prior written permission of the publisher, except in the case of brief quotations embodied in critical reviews and certain other noncommercial uses permitted by copyright law.