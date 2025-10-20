"""
Parquet Analytics MCP Tool implementation
Generic tool for analyzing and querying Parquet files
"""
import os
import pandas as pd
import pyarrow.parquet as pq
from typing import Dict, Any, List, Optional
from .base_mcp_tool import BaseMCPTool
from pathlib import Path
import json


class ParquetMCPTool(BaseMCPTool):
    """MCP Tool for Parquet file analytics and data extraction"""

    def _initialize(self):
        """Initialize Parquet tool"""
        self.data_folder = os.environ.get('PARQUET_DATA_FOLDER', 'data')
        self.parquet_folders = []
        
        # Discover parquet files in data folder and subfolders
        self._discover_parquet_files()

    def _discover_parquet_files(self):
        """Discover all parquet files in the data folder"""
        self.parquet_files = {}
        
        for root, dirs, files in os.walk(self.data_folder):
            for file in files:
                if file.endswith('.parquet'):
                    file_path = os.path.join(root, file)
                    # Use relative path as key
                    rel_path = os.path.relpath(file_path, self.data_folder)
                    self.parquet_files[rel_path] = file_path

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Parquet tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            tool_methods = {
                "list_parquet_files": self._list_parquet_files,
                "get_file_info": self._get_file_info,
                "list_columns": self._list_columns,
                "get_column_stats": self._get_column_stats,
                "get_unique_values": self._get_unique_values,
                "filter_data": self._filter_data,
                "aggregate_data": self._aggregate_data,
                "query_data": self._query_data,
                "get_sample": self._get_sample,
                "get_value_counts": self._get_value_counts,
                "get_data_summary": self._get_data_summary,
                "export_filtered_data": self._export_filtered_data,
                "join_files": self._join_files
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

    def _get_file_path(self, file_name: str) -> Optional[str]:
        """Get full path for a parquet file"""
        # Refresh file list
        self._discover_parquet_files()
        
        # Try exact match first
        if file_name in self.parquet_files:
            return self.parquet_files[file_name]
        
        # Try finding by basename
        for rel_path, full_path in self.parquet_files.items():
            if os.path.basename(rel_path) == file_name:
                return full_path
        
        return None

    def _list_parquet_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all available parquet files"""
        self._discover_parquet_files()
        
        files_info = []
        for rel_path, full_path in self.parquet_files.items():
            try:
                # Get file size
                size_bytes = os.path.getsize(full_path)
                size_mb = size_bytes / (1024 * 1024)
                
                # Get row count
                parquet_file = pq.ParquetFile(full_path)
                row_count = parquet_file.metadata.num_rows
                num_columns = parquet_file.metadata.num_columns
                
                files_info.append({
                    'file_name': rel_path,
                    'full_path': full_path,
                    'size_mb': round(size_mb, 2),
                    'row_count': row_count,
                    'column_count': num_columns
                })
            except Exception as e:
                files_info.append({
                    'file_name': rel_path,
                    'full_path': full_path,
                    'error': str(e)
                })
        
        return {
            "files": files_info,
            "total_files": len(files_info)
        }

    def _get_file_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a parquet file"""
        file_name = params.get('file_name', '')
        
        if not file_name:
            return {"error": "file_name is required"}
        
        file_path = self._get_file_path(file_name)
        if not file_path:
            return {"error": f"File '{file_name}' not found"}
        
        try:
            parquet_file = pq.ParquetFile(file_path)
            metadata = parquet_file.metadata
            
            # Get schema information
            schema = parquet_file.schema
            columns = []
            for i in range(len(schema)):
                field = schema[i]
                columns.append({
                    'name': field.name,
                    'type': str(field.physical_type)
                })
            
            return {
                "file_name": file_name,
                "row_count": metadata.num_rows,
                "column_count": metadata.num_columns,
                "columns": columns,
                "size_bytes": os.path.getsize(file_path),
                "num_row_groups": metadata.num_row_groups
            }
        
        except Exception as e:
            return {"error": str(e)}

    def _list_columns(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all columns in a parquet file with their data types"""
        file_name = params.get('file_name', '')
        
        if not file_name:
            return {"error": "file_name is required"}
        
        file_path = self._get_file_path(file_name)
        if not file_path:
            return {"error": f"File '{file_name}' not found"}
        
        try:
            df = pd.read_parquet(file_path)
            
            columns_info = []
            for col in df.columns:
                columns_info.append({
                    'name': col,
                    'dtype': str(df[col].dtype),
                    'null_count': int(df[col].isna().sum()),
                    'null_percentage': round(float(df[col].isna().sum() / len(df) * 100), 2)
                })
            
            return {
                "file_name": file_name,
                "columns": columns_info,
                "total_columns": len(columns_info),
                "total_rows": len(df)
            }
        
        except Exception as e:
            return {"error": str(e)}

    def _get_column_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get statistics for specific columns"""
        file_name = params.get('file_name', '')
        columns = params.get('columns', [])
        
        if not file_name:
            return {"error": "file_name is required"}
        
        file_path = self._get_file_path(file_name)
        if not file_path:
            return {"error": f"File '{file_name}' not found"}
        
        try:
            df = pd.read_parquet(file_path)
            
            if not columns:
                columns = df.columns.tolist()
            
            stats = {}
            for col in columns:
                if col not in df.columns:
                    stats[col] = {"error": "Column not found"}
                    continue
                
                col_stats = {
                    'count': int(df[col].count()),
                    'null_count': int(df[col].isna().sum()),
                    'unique_count': int(df[col].nunique())
                }
                
                # Add numeric statistics if applicable
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_stats.update({
                        'mean': float(df[col].mean()) if not df[col].isna().all() else None,
                        'std': float(df[col].std()) if not df[col].isna().all() else None,
                        'min': float(df[col].min()) if not df[col].isna().all() else None,
                        'max': float(df[col].max()) if not df[col].isna().all() else None,
                        'median': float(df[col].median()) if not df[col].isna().all() else None
                    })
                
                stats[col] = col_stats
            
            return {
                "file_name": file_name,
                "statistics": stats
            }
        
        except Exception as e:
            return {"error": str(e)}

    def _get_unique_values(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get unique values for a column"""
        file_name = params.get('file_name', '')
        column = params.get('column', '')
        limit = params.get('limit', 100)
        
        if not file_name:
            return {"error": "file_name is required"}
        if not column:
            return {"error": "column is required"}
        
        file_path = self._get_file_path(file_name)
        if not file_path:
            return {"error": f"File '{file_name}' not found"}
        
        try:
            df = pd.read_parquet(file_path)
            
            if column not in df.columns:
                return {"error": f"Column '{column}' not found"}
            
            unique_values = df[column].dropna().unique().tolist()[:limit]
            
            return {
                "file_name": file_name,
                "column": column,
                "unique_values": unique_values,
                "total_unique": int(df[column].nunique()),
                "returned_count": len(unique_values)
            }
        
        except Exception as e:
            return {"error": str(e)}

    def _filter_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Filter data by column conditions"""
        file_name = params.get('file_name', '')
        filters = params.get('filters', {})
        columns = params.get('columns', None)  # Columns to return
        limit = params.get('limit', 100)
        
        if not file_name:
            return {"error": "file_name is required"}
        
        file_path = self._get_file_path(file_name)
        if not file_path:
            return {"error": f"File '{file_name}' not found"}
        
        try:
            df = pd.read_parquet(file_path)
            
            # Apply filters
            filtered_df = df.copy()
            for col, value in filters.items():
                if col not in df.columns:
                    return {"error": f"Column '{col}' not found"}
                
                if isinstance(value, dict):
                    # Handle operators like gt, lt, gte, lte, in, contains
                    if 'gt' in value:
                        filtered_df = filtered_df[filtered_df[col] > value['gt']]
                    if 'lt' in value:
                        filtered_df = filtered_df[filtered_df[col] < value['lt']]
                    if 'gte' in value:
                        filtered_df = filtered_df[filtered_df[col] >= value['gte']]
                    if 'lte' in value:
                        filtered_df = filtered_df[filtered_df[col] <= value['lte']]
                    if 'in' in value:
                        filtered_df = filtered_df[filtered_df[col].isin(value['in'])]
                    if 'contains' in value:
                        filtered_df = filtered_df[filtered_df[col].str.contains(value['contains'], na=False)]
                else:
                    # Exact match
                    filtered_df = filtered_df[filtered_df[col] == value]
            
            # Select columns
            if columns:
                missing_cols = [c for c in columns if c not in filtered_df.columns]
                if missing_cols:
                    return {"error": f"Columns not found: {missing_cols}"}
                filtered_df = filtered_df[columns]
            
            # Limit results
            result_df = filtered_df.head(limit)
            
            return {
                "file_name": file_name,
                "filters_applied": filters,
                "total_matches": len(filtered_df),
                "returned_rows": len(result_df),
                "data": result_df.to_dict('records')
            }
        
        except Exception as e:
            return {"error": str(e)}

    def _aggregate_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate data by grouping columns"""
        file_name = params.get('file_name', '')
        group_by = params.get('group_by', [])
        aggregations = params.get('aggregations', {})
        filters = params.get('filters', {})
        
        if not file_name:
            return {"error": "file_name is required"}
        if not group_by:
            return {"error": "group_by columns are required"}
        if not aggregations:
            return {"error": "aggregations are required"}
        
        file_path = self._get_file_path(file_name)
        if not file_path:
            return {"error": f"File '{file_name}' not found"}
        
        try:
            df = pd.read_parquet(file_path)
            
            # Apply filters first
            for col, value in filters.items():
                if col in df.columns:
                    df = df[df[col] == value]
            
            # Perform aggregation
            agg_dict = {}
            for col, func in aggregations.items():
                if col not in df.columns:
                    return {"error": f"Column '{col}' not found"}
                agg_dict[col] = func
            
            result_df = df.groupby(group_by).agg(agg_dict).reset_index()
            
            return {
                "file_name": file_name,
                "group_by": group_by,
                "aggregations": aggregations,
                "result_count": len(result_df),
                "data": result_df.to_dict('records')
            }
        
        except Exception as e:
            return {"error": str(e)}

    def _query_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query data using pandas query syntax"""
        file_name = params.get('file_name', '')
        query = params.get('query', '')
        limit = params.get('limit', 100)
        
        if not file_name:
            return {"error": "file_name is required"}
        if not query:
            return {"error": "query is required"}
        
        file_path = self._get_file_path(file_name)
        if not file_path:
            return {"error": f"File '{file_name}' not found"}
        
        try:
            df = pd.read_parquet(file_path)
            result_df = df.query(query).head(limit)
            
            return {
                "file_name": file_name,
                "query": query,
                "result_count": len(result_df),
                "data": result_df.to_dict('records')
            }
        
        except Exception as e:
            return {"error": str(e)}

    def _get_sample(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a sample of data from the parquet file"""
        file_name = params.get('file_name', '')
        n = params.get('n', 10)
        random = params.get('random', False)
        
        if not file_name:
            return {"error": "file_name is required"}
        
        file_path = self._get_file_path(file_name)
        if not file_path:
            return {"error": f"File '{file_name}' not found"}
        
        try:
            df = pd.read_parquet(file_path)
            
            if random:
                sample_df = df.sample(n=min(n, len(df)))
            else:
                sample_df = df.head(n)
            
            return {
                "file_name": file_name,
                "sample_size": len(sample_df),
                "total_rows": len(df),
                "data": sample_df.to_dict('records')
            }
        
        except Exception as e:
            return {"error": str(e)}

    def _get_value_counts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get value counts for a column"""
        file_name = params.get('file_name', '')
        column = params.get('column', '')
        limit = params.get('limit', 20)
        
        if not file_name:
            return {"error": "file_name is required"}
        if not column:
            return {"error": "column is required"}
        
        file_path = self._get_file_path(file_name)
        if not file_path:
            return {"error": f"File '{file_name}' not found"}
        
        try:
            df = pd.read_parquet(file_path)
            
            if column not in df.columns:
                return {"error": f"Column '{column}' not found"}
            
            value_counts = df[column].value_counts().head(limit)
            
            return {
                "file_name": file_name,
                "column": column,
                "value_counts": {str(k): int(v) for k, v in value_counts.items()},
                "total_unique": int(df[column].nunique())
            }
        
        except Exception as e:
            return {"error": str(e)}

    def _get_data_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive summary of the parquet file"""
        file_name = params.get('file_name', '')
        
        if not file_name:
            return {"error": "file_name is required"}
        
        file_path = self._get_file_path(file_name)
        if not file_path:
            return {"error": f"File '{file_name}' not found"}
        
        try:
            df = pd.read_parquet(file_path)
            
            summary = {
                "file_name": file_name,
                "shape": {
                    "rows": len(df),
                    "columns": len(df.columns)
                },
                "columns": df.columns.tolist(),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "memory_usage_mb": round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
                "null_counts": {col: int(df[col].isna().sum()) for col in df.columns},
                "numeric_summary": df.describe().to_dict() if len(df.select_dtypes(include=['number']).columns) > 0 else {}
            }
            
            return summary
        
        except Exception as e:
            return {"error": str(e)}

    def _export_filtered_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Export filtered data to a new parquet file"""
        file_name = params.get('file_name', '')
        output_name = params.get('output_name', 'filtered_output.parquet')
        filters = params.get('filters', {})
        columns = params.get('columns', None)
        
        if not file_name:
            return {"error": "file_name is required"}
        
        file_path = self._get_file_path(file_name)
        if not file_path:
            return {"error": f"File '{file_name}' not found"}
        
        try:
            df = pd.read_parquet(file_path)
            
            # Apply filters
            filtered_df = df.copy()
            for col, value in filters.items():
                if col in df.columns:
                    filtered_df = filtered_df[filtered_df[col] == value]
            
            # Select columns
            if columns:
                filtered_df = filtered_df[columns]
            
            # Save to new file
            output_path = os.path.join(self.data_folder, output_name)
            filtered_df.to_parquet(output_path)
            
            return {
                "file_name": file_name,
                "output_file": output_name,
                "output_path": output_path,
                "rows_exported": len(filtered_df),
                "columns_exported": len(filtered_df.columns)
            }
        
        except Exception as e:
            return {"error": str(e)}

    def _join_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Join two parquet files"""
        left_file = params.get('left_file', '')
        right_file = params.get('right_file', '')
        on = params.get('on', [])
        how = params.get('how', 'inner')
        limit = params.get('limit', 100)
        
        if not left_file or not right_file:
            return {"error": "left_file and right_file are required"}
        if not on:
            return {"error": "join column(s) 'on' is required"}
        
        left_path = self._get_file_path(left_file)
        right_path = self._get_file_path(right_file)
        
        if not left_path:
            return {"error": f"File '{left_file}' not found"}
        if not right_path:
            return {"error": f"File '{right_file}' not found"}
        
        try:
            df_left = pd.read_parquet(left_path)
            df_right = pd.read_parquet(right_path)
            
            merged_df = pd.merge(df_left, df_right, on=on, how=how)
            result_df = merged_df.head(limit)
            
            return {
                "left_file": left_file,
                "right_file": right_file,
                "join_type": how,
                "join_columns": on,
                "result_count": len(merged_df),
                "returned_rows": len(result_df),
                "data": result_df.to_dict('records')
            }
        
        except Exception as e:
            return {"error": str(e)}

