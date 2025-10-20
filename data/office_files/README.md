# MS Office Test Files

This folder contains sample Microsoft Office files for testing the MS Office MCP Tool.

## Created Files

### 📝 Word Documents

#### 1. **Q3_2025_Business_Report.docx** (37 KB)
A comprehensive quarterly business report with:
- **Executive Summary** with bullet points
- **Financial Performance** section with narrative
- **Key Metrics Table** (5 rows x 3 columns)
  - Revenue, Gross Profit, Net Income, Customer Count
  - Q2 vs Q3 comparison
- **Product Performance** analysis
- **Customer Insights** 
- **Market Analysis**
- **Challenges and Opportunities** (with sub-sections)
- **Q4 Outlook**
- **Conclusion**

**Total:** ~1,200 words, 20+ paragraphs, 1 table

**Search Keywords:** revenue, quarterly results, Innovation Suite, customer acquisition, market share

---

#### 2. **Product_Roadmap_2025.docx** (36 KB)
A product development roadmap document with:
- **Overview** of product strategy
- **Q4 2025 Priorities** with feature list
- **Technical Specifications**
- Bullet-pointed feature lists
- AI analytics, collaboration tools, security features

**Total:** ~400 words, 10+ paragraphs

**Search Keywords:** AI-powered analytics, cloud platforms, mobile app, roadmap

---

### 📊 Excel Spreadsheet

#### 3. **Sales_Data_Q3_2025.xlsx** (16 KB)
A multi-sheet workbook with realistic sales data:

**Sheet 1: Sales_Data** (150 rows)
| Column | Type | Description |
|--------|------|-------------|
| Date | Date | Transaction dates (Jul-Sep 2025) |
| Region | Text | North America, Europe, Asia, South America |
| Product | Text | 5 different products |
| Sales_Rep | Text | 6 sales representatives |
| Units_Sold | Number | 1-50 units |
| Unit_Price | Number | $299 - $2,499 |
| Total_Revenue | Number | Calculated (Units × Price) |
| Customer_Type | Text | Enterprise, SMB, Startup, Government |

**Sheet 2: Customer_Database** (50 rows)
| Column | Type | Description |
|--------|------|-------------|
| Customer_ID | Text | CUST1000-CUST1049 |
| Company_Name | Text | Various company names |
| Industry | Text | 6 different industries |
| Contact_Name | Text | Contact person |
| Email | Text | Email addresses |
| Phone | Text | Phone numbers |
| Status | Text | Active, Prospect, Inactive |
| Annual_Revenue | Number | $500K - $25M |
| Employees | Number | 10 - 2,500 |

**Sheet 3: Monthly_Summary** (3 rows)
| Column | Type | Description |
|--------|------|-------------|
| Month | Text | July, August, September 2025 |
| Total_Sales | Number | Monthly revenue totals |
| Units_Sold | Number | Total units per month |
| Avg_Order_Value | Number | Average order size |
| Customers | Number | Customer count |
| Growth_% | Number | Month-over-month growth |

---

## Test Scenarios

### Word Document Tests:
1. ✅ **Read document** - Extract paragraphs and tables
2. ✅ **Search text** - Find "quarterly results", "revenue", "AI"
3. ✅ **Get metadata** - Author, dates, properties
4. ✅ **Extract tables** - Read metrics table from Q3 report
5. ✅ **List all documents** - Enumerate files

### Excel Tests:
1. ✅ **List sheets** - Should return 3 sheets
2. ✅ **Read sheet** - Get Sales_Data rows
3. ✅ **Query with filters** - Filter by Region="North America"
4. ✅ **Calculate statistics** - Sum revenue, average units sold
5. ✅ **Search values** - Find specific customer or product
6. ✅ **Multi-sheet analysis** - Compare data across sheets

### Combined Tests:
1. ✅ **Extract Excel data** → Create Word report
2. ✅ **Search across all files** for specific terms
3. ✅ **Generate summary** from Excel statistics

---

## Data Characteristics

### Sales Data Statistics:
- **Date Range:** July 1 - September 30, 2025 (Q3)
- **Total Transactions:** 150
- **Regions:** 4 (North America, Europe, Asia, South America)
- **Products:** 5 (Innovation Suite, Business Pro, Enterprise Plus, Starter Pack, Premium Edition)
- **Sales Reps:** 6 people
- **Price Range:** $299 - $2,499
- **Expected Total Revenue:** ~$150K - $200K

### Customer Database:
- **Total Customers:** 50
- **Industries:** 6 (Technology, Finance, Healthcare, Retail, Manufacturing, Education)
- **Revenue Range:** $500K - $25M annual
- **Employee Range:** 10 - 2,500 employees

---

## File Generation

Files were created using:
- `python-docx` for Word documents
- `openpyxl` for Excel files
- Realistic business data and formatting
- Proper headers, styles, and structure

**Script:** `create_sample_office_files.py` (root directory)

---

## Usage with MS Office Tool

### Example API Calls:

**List all files:**
```json
{
  "method": "list_files",
  "arguments": {"file_type": "all"}
}
```

**Read Word document:**
```json
{
  "method": "read_word_document",
  "arguments": {
    "filename": "Q3_2025_Business_Report.docx",
    "max_paragraphs": 20
  }
}
```

**Read Excel sheet:**
```json
{
  "method": "read_excel_sheet",
  "arguments": {
    "filename": "Sales_Data_Q3_2025.xlsx",
    "sheet_name": "Sales_Data",
    "max_rows": 50
  }
}
```

**Query Excel data:**
```json
{
  "method": "query_excel_data",
  "arguments": {
    "filename": "Sales_Data_Q3_2025.xlsx",
    "sheet_name": "Sales_Data",
    "filters": {"Region": "North America"},
    "columns": ["Date", "Product", "Total_Revenue"]
  }
}
```

**Search for text:**
```json
{
  "method": "search_word_documents",
  "arguments": {
    "search_term": "revenue",
    "case_sensitive": false
  }
}
```

---

**Created:** October 20, 2025  
**Purpose:** Testing MS Office MCP Tool functionality  
**Status:** Ready for testing

