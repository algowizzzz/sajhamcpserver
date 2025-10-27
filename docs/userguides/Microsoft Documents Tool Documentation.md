# Microsoft Documents Tool Documentation

**Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com**

## Overview

The Microsoft Documents Tool (msdoc_tools) provides comprehensive functionality for working with Microsoft Word (.docx) and Excel (.xlsx, .xlsm) files stored in a designated directory. This tool enables reading, searching, and extracting information from Office documents programmatically.

## Features

- **File Management**: List and browse Word and Excel files
- **Word Documents**: Read paragraphs, tables, and extract text
- **Excel Files**: Read sheets, cells, and extract data
- **Search Functionality**: Search for text in both Word and Excel files
- **Metadata Extraction**: Get document properties and statistics
- **Multi-Sheet Support**: Work with Excel workbooks containing multiple sheets
- **Formula Support**: Optionally include Excel cell formulas

## Installation

### Prerequisites

- Python 3.8 or higher
- python-docx library (for Word documents)
- openpyxl library (for Excel files)

### Setup

1. **Install Required Libraries:**
   ```bash
   pip install python-docx openpyxl
   ```

2. **Copy Tool Files:**
   ```bash
   # Copy tool implementation
   cp msdoc_tools_tool.py /path/to/project/tools/impl/
   
   # Copy configuration
   cp msdoc_tools.json /path/to/project/config/tools/
   ```

3. **Create Documents Directory:**
   ```bash
   # Create the directory for MS documents
   mkdir -p data/msdocs
   
   # Copy your Word and Excel files there
   cp *.docx data/msdocs/
   cp *.xlsx data/msdocs/
   ```

4. **Update Registry:**
   
   Add to `tools_registry.py`:
   ```python
   self.builtin_tools = {
       ...
       'msdoc_tools': 'tools.impl.msdoc_tools_tool.MsDocToolsTool'
   }
   ```

5. **Restart Server:**
   ```bash
   python app.py
   ```

## Configuration

### JSON Configuration File (`msdoc_tools.json`)

```json
{
  "name": "msdoc_tools",
  "type": "msdoc_tools",
  "description": "Work with Microsoft Word and Excel documents",
  "version": "1.0.0",
  "enabled": true,
  "docs_directory": "data/msdocs",
  "metadata": {
    "author": "Ashutosh Sinha",
    "category": "Document Processing",
    "tags": ["microsoft", "word", "excel", "documents"],
    "rateLimit": 60,
    "cacheTTL": 300
  }
}
```

### Configuration Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `name` | string | Tool name | Yes |
| `docs_directory` | string | Path to documents folder | Yes |
| `enabled` | boolean | Enable/disable tool | No (default: true) |
| `rateLimit` | integer | Max requests per minute | No |
| `cacheTTL` | integer | Cache time in seconds | No |

## Usage

### Input Schema

```json
{
  "action": "string (required)",
  "filename": "string",
  "file_type": "all|word|excel",
  "search_term": "string",
  "sheet_name": "string",
  "sheet_index": "integer",
  "max_rows": "integer (1-10000, default: 100)",
  "include_formulas": "boolean (default: false)"
}
```

### Available Actions

1. **list_files** - List all documents in directory
2. **read_word** - Read Word document content
3. **read_excel** - Read Excel file data
4. **search_word** - Search for text in Word document
5. **search_excel** - Search for text in Excel file
6. **get_word_metadata** - Get Word document metadata
7. **get_excel_metadata** - Get Excel file metadata
8. **extract_text** - Extract all text from document
9. **get_excel_sheets** - List sheets in Excel workbook
10. **read_excel_sheet** - Read specific Excel sheet

## Programmatic Usage (Python)

### Method 1: List Files

```python
from tools.impl.msdoc_tools_tool import MsDocToolsTool

# Initialize tool
config = {
    'name': 'msdoc_tools',
    'docs_directory': 'data/msdocs',
    'enabled': True
}

tool = MsDocToolsTool(config)

# Example 1: List all files
arguments = {
    'action': 'list_files',
    'file_type': 'all'
}

result = tool.execute_with_tracking(arguments)

print(f"Documents in {result['directory']}:")
print(f"Total files: {result['count']}\n")

for file in result['files']:
    print(f"- {file['filename']}")
    print(f"  Type: {file['type']}")
    print(f"  Size: {file['size_mb']} MB")
    print(f"  Modified: {file['modified']}")
    print()
```

**Output:**
```
Documents in data/msdocs:
Total files: 5

- report.docx
  Type: word
  Size: 0.25 MB
  Modified: 2024-10-25T14:30:00

- budget.xlsx
  Type: excel
  Size: 0.52 MB
  Modified: 2024-10-24T16:45:00
...
```

### Method 2: Read Word Document

```python
# Example 2: Read Word document
arguments = {
    'action': 'read_word',
    'filename': 'report.docx'
}

result = tool.execute_with_tracking(arguments)

print(f"Document: {result['filename']}")
print(f"Paragraphs: {result['paragraph_count']}")
print(f"Tables: {result['table_count']}\n")

# Display first few paragraphs
print("Content Preview:")
for i, para in enumerate(result['paragraphs'][:3], 1):
    print(f"{i}. {para['text'][:100]}...")
    print(f"   Style: {para['style']}\n")

# Display metadata
metadata = result['metadata']
print(f"Author: {metadata['author']}")
print(f"Created: {metadata['created']}")
```

**Output:**
```
Document: report.docx
Paragraphs: 25
Tables: 3

Content Preview:
1. Executive Summary...
   Style: Heading 1

2. This report provides an overview of the quarterly results...
   Style: Normal

Author: John Doe
Created: 2024-10-20T10:00:00
```

### Method 3: Read Excel File

```python
# Example 3: Read Excel file
arguments = {
    'action': 'read_excel',
    'filename': 'budget.xlsx',
    'max_rows': 10
}

result = tool.execute_with_tracking(arguments)

print(f"Excel File: {result['filename']}")
print(f"Sheets: {result['sheet_count']}")
print(f"Sheet Names: {', '.join(result['sheet_names'])}\n")

# Display data from first sheet
first_sheet = list(result['sheets'].keys())[0]
sheet_data = result['sheets'][first_sheet]

print(f"Sheet: {first_sheet}")
print(f"Rows: {sheet_data['row_count']}/{sheet_data['total_rows']}")
print(f"Columns: {sheet_data['column_count']}\n")

# Display first few rows
print("Data Preview:")
for i, row in enumerate(sheet_data['rows'][:5], 1):
    print(f"Row {i}: {row}")
```

**Output:**
```
Excel File: budget.xlsx
Sheets: 3
Sheet Names: Summary, Q1, Q2

Sheet: Summary
Rows: 10/50
Columns: 5

Data Preview:
Row 1: ['Category', 'Budget', 'Actual', 'Variance', 'Status']
Row 2: ['Marketing', 50000, 48500, 1500, 'Under']
Row 3: ['Operations', 120000, 125000, -5000, 'Over']
...
```

### Method 4: Search in Word Document

```python
# Example 4: Search Word document
arguments = {
    'action': 'search_word',
    'filename': 'report.docx',
    'search_term': 'revenue'
}

result = tool.execute_with_tracking(arguments)

print(f"Searching '{result['search_term']}' in {result['filename']}")
print(f"Matches found: {result['match_count']}\n")

for match in result['matches'][:5]:
    if match['type'] == 'paragraph':
        print(f"Paragraph {match['index']}:")
        print(f"  ...{match['context']}...")
    elif match['type'] == 'table':
        print(f"Table {match['table_index']}, Row {match['row']}, Col {match['column']}:")
        print(f"  {match['text']}")
    print()
```

### Method 5: Search in Excel File

```python
# Example 5: Search Excel file
arguments = {
    'action': 'search_excel',
    'filename': 'budget.xlsx',
    'search_term': 'marketing'
}

result = tool.execute_with_tracking(arguments)

print(f"Searching '{result['search_term']}' in {result['filename']}")
print(f"Matches found: {result['match_count']}\n")

for match in result['matches'][:10]:
    print(f"Sheet: {match['sheet']}")
    print(f"Cell: {match['cell']} (Row {match['row']}, Col {match['column']})")
    print(f"Value: {match['value']}")
    print()
```

### Method 6: Get Document Metadata

```python
# Example 6: Get Word metadata
arguments = {
    'action': 'get_word_metadata',
    'filename': 'report.docx'
}

result = tool.execute_with_tracking(arguments)

print(f"Document: {result['filename']}")
print("\nMetadata:")
for key, value in result['metadata'].items():
    print(f"  {key}: {value}")

print("\nStatistics:")
for key, value in result['statistics'].items():
    print(f"  {key}: {value}")
```

```python
# Example 6b: Get Excel metadata
arguments = {
    'action': 'get_excel_metadata',
    'filename': 'budget.xlsx'
}

result = tool.execute_with_tracking(arguments)

print(f"File: {result['filename']}")
print("\nMetadata:")
for key, value in result['metadata'].items():
    print(f"  {key}: {value}")

print("\nSheets:")
for sheet in result['statistics']['sheets']:
    print(f"  {sheet['name']}: {sheet['rows']} rows x {sheet['columns']} cols")
```

### Method 7: Extract Text

```python
# Example 7: Extract all text
arguments = {
    'action': 'extract_text',
    'filename': 'report.docx'
}

result = tool.execute_with_tracking(arguments)

print(f"Document: {result['filename']}")
print(f"Characters: {result['character_count']}")
print(f"Words: {result['word_count']}")
print(f"Paragraphs: {result['paragraph_count']}\n")

# Display first 500 characters
print("Text Preview:")
print(result['text'][:500])
print("...")
```

### Method 8: Get Excel Sheets

```python
# Example 8: List Excel sheets
arguments = {
    'action': 'get_excel_sheets',
    'filename': 'budget.xlsx'
}

result = tool.execute_with_tracking(arguments)

print(f"Workbook: {result['filename']}")
print(f"Total Sheets: {result['sheet_count']}\n")

for sheet in result['sheets']:
    print(f"Sheet {sheet['index']}: {sheet['name']}")
    print(f"  Dimensions: {sheet['rows']} rows x {sheet['columns']} columns")
```

### Method 9: Read Specific Sheet

```python
# Example 9: Read specific sheet by name
arguments = {
    'action': 'read_excel_sheet',
    'filename': 'budget.xlsx',
    'sheet_name': 'Q1',
    'max_rows': 20
}

result = tool.execute_with_tracking(arguments)

print(f"Sheet: {result['sheet_name']} (index {result['sheet_index']})")
print(f"Showing {result['row_count']} of {result['total_rows']} rows\n")

# Display header and first few rows
if result['rows']:
    print("Headers:", result['rows'][0])
    print("\nData:")
    for row in result['rows'][1:6]:
        print(row)
```

```python
# Example 9b: Read sheet by index
arguments = {
    'action': 'read_excel_sheet',
    'filename': 'budget.xlsx',
    'sheet_index': 0,
    'max_rows': 50
}

result = tool.execute_with_tracking(arguments)
```

### Method 10: Using Tools Registry

```python
from tools.tools_registry import ToolsRegistry

# Get registry instance
registry = ToolsRegistry('config/tools')

# Get the tool
msdoc_tool = registry.get_tool('msdoc_tools')

# List Word documents only
arguments = {
    'action': 'list_files',
    'file_type': 'word'
}

result = msdoc_tool.execute_with_tracking(arguments)

print("Word Documents:")
for file in result['files']:
    print(f"- {file['filename']} ({file['size_mb']} MB)")
```

### Error Handling

```python
try:
    result = tool.execute_with_tracking(arguments)
    
    # Check for errors (when libraries are missing)
    if 'error' in result:
        print(f"Warning: {result['error']}")
        print(f"Note: {result['note']}")
    else:
        # Process results
        pass
        
except ValueError as e:
    print(f"Validation error: {e}")
except RuntimeError as e:
    print(f"Tool execution error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Web UI Usage

### Accessing the Tool

1. **Navigate to Tools List:**
   - Open web browser
   - Go to `http://your-server:port/tools`
   - Find "msdoc_tools" in the tools list

2. **Click "Execute" button**

### Example 1: List Files via Web UI

**Form Input:**
```
Action: list_files
File Type: all
```

**Click "Execute Tool"**

**Expected Output:**
```json
{
  "directory": "data/msdocs",
  "file_type": "all",
  "count": 5,
  "files": [
    {
      "filename": "report.docx",
      "type": "word",
      "size": 256000,
      "size_mb": 0.25,
      "modified": "2024-10-25T14:30:00"
    },
    ...
  ]
}
```

### Example 2: Read Word Document via Web UI

**Form Input:**
```
Action: read_word
Filename: report.docx
```

**Expected Output:**
- Document paragraphs with styles
- Tables data
- Metadata (author, title, dates)
- Paragraph and table counts

### Example 3: Read Excel File via Web UI

**Form Input:**
```
Action: read_excel
Filename: budget.xlsx
Max Rows: 50
Include Formulas: false
```

**Expected Output:**
- Sheet names
- Data from multiple sheets
- Row and column counts

### Example 4: Search Word Document via Web UI

**Form Input:**
```
Action: search_word
Filename: report.docx
Search Term: revenue
```

**Expected Output:**
- Match count
- Context for each match
- Paragraph indices
- Table locations if found

### Example 5: Search Excel File via Web UI

**Form Input:**
```
Action: search_excel
Filename: budget.xlsx
Search Term: marketing
```

**Expected Output:**
- Match count
- Sheet names
- Cell references (A1, B2, etc.)
- Cell values

### Example 6: Get Metadata via Web UI

**Form Input:**
```
Action: get_word_metadata
Filename: report.docx
```

**Expected Output:**
- Author, title, subject
- Creation and modification dates
- Document statistics

### Example 7: Extract Text via Web UI

**Form Input:**
```
Action: extract_text
Filename: report.docx
```

**Expected Output:**
- Full text content
- Character count
- Word count
- Paragraph count

### Example 8: Get Excel Sheets via Web UI

**Form Input:**
```
Action: get_excel_sheets
Filename: budget.xlsx
```

**Expected Output:**
- List of sheet names
- Dimensions for each sheet
- Sheet indices

### Example 9: Read Specific Sheet via Web UI

**Form Input:**
```
Action: read_excel_sheet
Filename: budget.xlsx
Sheet Name: Q1
Max Rows: 100
```

**Expected Output:**
- Sheet data
- Row count (shown vs total)
- Column count

## API Endpoint Usage

### REST API Call

```bash
# List files
curl -X POST http://your-server:port/api/tools/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "tool": "msdoc_tools",
    "arguments": {
      "action": "list_files",
      "file_type": "all"
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

# Example 1: Read Word document
payload = {
    "tool": "msdoc_tools",
    "arguments": {
        "action": "read_word",
        "filename": "report.docx"
    }
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    result = response.json()
    
    if result['success']:
        data = result['result']
        print(f"Document: {data['filename']}")
        print(f"Paragraphs: {data['paragraph_count']}")
        print(f"Tables: {data['table_count']}")
    else:
        print(f"Error: {result['error']}")
```

```python
# Example 2: Search Excel file
payload = {
    "tool": "msdoc_tools",
    "arguments": {
        "action": "search_excel",
        "filename": "budget.xlsx",
        "search_term": "marketing"
    }
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()['result']

print(f"Found {data['match_count']} matches")
for match in data['matches'][:5]:
    print(f"{match['sheet']}: {match['cell']} = {match['value']}")
```

```python
# Example 3: Read specific Excel sheet
payload = {
    "tool": "msdoc_tools",
    "arguments": {
        "action": "read_excel_sheet",
        "filename": "budget.xlsx",
        "sheet_name": "Q1",
        "max_rows": 25
    }
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()['result']

print(f"Sheet: {data['sheet_name']}")
print(f"Rows: {data['row_count']}")

# Display as table
for row in data['rows'][:10]:
    print(" | ".join(str(cell) for cell in row))
```

## Response Formats

### List Files Response

```json
{
  "directory": "data/msdocs",
  "file_type": "all",
  "count": 5,
  "files": [
    {
      "filename": "report.docx",
      "type": "word",
      "size": 256000,
      "size_mb": 0.25,
      "modified": "2024-10-25T14:30:00",
      "path": "data/msdocs/report.docx"
    }
  ]
}
```

### Read Word Response

```json
{
  "filename": "report.docx",
  "type": "word",
  "paragraph_count": 25,
  "table_count": 3,
  "paragraphs": [
    {
      "text": "Executive Summary",
      "style": "Heading 1"
    }
  ],
  "tables": [
    [
      ["Header 1", "Header 2"],
      ["Data 1", "Data 2"]
    ]
  ],
  "metadata": {
    "author": "John Doe",
    "title": "Quarterly Report",
    "created": "2024-10-20T10:00:00"
  }
}
```

### Read Excel Response

```json
{
  "filename": "budget.xlsx",
  "type": "excel",
  "sheet_count": 3,
  "sheet_names": ["Summary", "Q1", "Q2"],
  "sheets": {
    "Summary": {
      "rows": [[...], [...]],
      "row_count": 10,
      "column_count": 5,
      "total_rows": 50
    }
  }
}
```

### Search Response

```json
{
  "filename": "report.docx",
  "search_term": "revenue",
  "match_count": 5,
  "matches": [
    {
      "type": "paragraph",
      "index": 3,
      "context": "...total revenue increased by 15%...",
      "position": 45
    }
  ]
}
```

## Best Practices

### 1. Organize Your Documents

```bash
# Create organized structure
data/msdocs/
├── reports/
│   ├── monthly/
│   └── quarterly/
├── budgets/
└── presentations/
```

### 2. Handle Large Files

```python
# For large Excel files, limit rows
arguments = {
    'action': 'read_excel',
    'filename': 'large_data.xlsx',
    'max_rows': 100  # Limit to avoid memory issues
}
```

### 3. Check Library Availability

```python
result = tool.execute_with_tracking(arguments)

if 'error' in result:
    print(f"Library missing: {result['error']}")
    print("Install required libraries:")
    print("  pip install python-docx openpyxl")
```

### 4. Search Efficiently

```python
# Use specific search terms
result = tool.execute_with_tracking({
    'action': 'search_word',
    'filename': 'report.docx',
    'search_term': 'Q4 revenue'  # Specific term
})
```

### 5. Process Multiple Files

```python
# Get all files first
files_result = tool.execute_with_tracking({
    'action': 'list_files',
    'file_type': 'word'
})

# Process each file
for file_info in files_result['files']:
    try:
        result = tool.execute_with_tracking({
            'action': 'extract_text',
            'filename': file_info['filename']
        })
        print(f"{file_info['filename']}: {result['word_count']} words")
    except Exception as e:
        print(f"Error processing {file_info['filename']}: {e}")
```

## Troubleshooting

### Issue: "python-docx library not available"

**Solution:**
```bash
pip install python-docx
```

### Issue: "openpyxl library not available"

**Solution:**
```bash
pip install openpyxl
```

### Issue: "File not found"

**Solution:**
1. Check file exists in `data/msdocs/`
2. Verify filename spelling
3. Ensure file has correct extension (.docx, .xlsx)
4. Check file permissions

### Issue: Excel file takes too long

**Solution:**
```python
# Reduce max_rows
arguments = {
    'action': 'read_excel',
    'filename': 'large.xlsx',
    'max_rows': 50  # Reduce from default 100
}
```

### Issue: Cannot read certain Excel features

**Solution:**
- Tool supports basic Excel features
- Macros and advanced features may not be supported
- Use `include_formulas: true` to see formulas

### Issue: Special characters not displaying correctly

**Solution:**
- Ensure files are saved in UTF-8 encoding
- Check Python environment encoding settings

## Limitations

1. **Protected Documents**: Password-protected files cannot be read
2. **Macros**: Excel macros are not executed
3. **Complex Formatting**: Some advanced formatting may be lost
4. **Large Files**: Very large files (>100MB) may cause performance issues
5. **File Types**: Only supports .docx, .xlsx, and .xlsm formats

## Support and Resources

- **python-docx Documentation**: https://python-docx.readthedocs.io/
- **openpyxl Documentation**: https://openpyxl.readthedocs.io/
- **Tool Support**: ajsinha@gmail.com

## License

Copyright All rights Reserved 2025-2030, Ashutosh Sinha

## Version History

- **v1.0.0** (2024-10-26): Initial release
  - List files functionality
  - Read Word documents
  - Read Excel files
  - Search in documents
  - Metadata extraction
  - Text extraction
  - Multi-sheet Excel support

---

**End of Documentation**