"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Microsoft Documents Tool - Standalone Client

This client provides easy-to-use methods for interacting with the MS Doc Tools.
It can be used independently or integrated into larger applications.
"""

import json
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional


class MsDocToolsClient:
    """
    Standalone client for Microsoft Documents Tool
    
    This client provides a convenient interface for working with Word and Excel
    documents through the MCP server API.
    """
    
    def __init__(self, base_url: str, api_token: Optional[str] = None):
        """
        Initialize MS Doc Tools client
        
        Args:
            base_url: Base URL of the MCP server (e.g., 'http://localhost:5000')
            api_token: Optional authentication token for the MCP server
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.tool_name = 'msdoc_tools'
        
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
    
    def list_files(self, file_type: str = 'all') -> Dict[str, Any]:
        """
        List files in the documents directory
        
        Args:
            file_type: Type of files ('all', 'word', 'excel')
            
        Returns:
            List of files with metadata
        """
        arguments = {
            'action': 'list_files',
            'file_type': file_type
        }
        
        return self._make_request(arguments)
    
    def read_word_document(self, filename: str) -> Dict[str, Any]:
        """
        Read Word document content
        
        Args:
            filename: Name of Word file
            
        Returns:
            Document content and metadata
        """
        arguments = {
            'action': 'read_word',
            'filename': filename
        }
        
        return self._make_request(arguments)
    
    def read_excel_file(
        self,
        filename: str,
        max_rows: int = 100,
        include_formulas: bool = False
    ) -> Dict[str, Any]:
        """
        Read Excel file content
        
        Args:
            filename: Name of Excel file
            max_rows: Maximum rows to return
            include_formulas: Include cell formulas
            
        Returns:
            Excel data and metadata
        """
        arguments = {
            'action': 'read_excel',
            'filename': filename,
            'max_rows': max_rows,
            'include_formulas': include_formulas
        }
        
        return self._make_request(arguments)
    
    def search_word(self, filename: str, search_term: str) -> Dict[str, Any]:
        """
        Search for text in Word document
        
        Args:
            filename: Name of Word file
            search_term: Text to search for
            
        Returns:
            Search results
        """
        arguments = {
            'action': 'search_word',
            'filename': filename,
            'search_term': search_term
        }
        
        return self._make_request(arguments)
    
    def search_excel(self, filename: str, search_term: str) -> Dict[str, Any]:
        """
        Search for text in Excel file
        
        Args:
            filename: Name of Excel file
            search_term: Text to search for
            
        Returns:
            Search results
        """
        arguments = {
            'action': 'search_excel',
            'filename': filename,
            'search_term': search_term
        }
        
        return self._make_request(arguments)
    
    def get_word_metadata(self, filename: str) -> Dict[str, Any]:
        """
        Get Word document metadata
        
        Args:
            filename: Name of Word file
            
        Returns:
            Document metadata
        """
        arguments = {
            'action': 'get_word_metadata',
            'filename': filename
        }
        
        return self._make_request(arguments)
    
    def get_excel_metadata(self, filename: str) -> Dict[str, Any]:
        """
        Get Excel file metadata
        
        Args:
            filename: Name of Excel file
            
        Returns:
            File metadata
        """
        arguments = {
            'action': 'get_excel_metadata',
            'filename': filename
        }
        
        return self._make_request(arguments)
    
    def extract_text(self, filename: str) -> Dict[str, Any]:
        """
        Extract all text from document
        
        Args:
            filename: Name of file
            
        Returns:
            Extracted text
        """
        arguments = {
            'action': 'extract_text',
            'filename': filename
        }
        
        return self._make_request(arguments)
    
    def get_excel_sheets(self, filename: str) -> Dict[str, Any]:
        """
        Get list of sheets in Excel file
        
        Args:
            filename: Name of Excel file
            
        Returns:
            List of sheets
        """
        arguments = {
            'action': 'get_excel_sheets',
            'filename': filename
        }
        
        return self._make_request(arguments)
    
    def read_excel_sheet(
        self,
        filename: str,
        sheet_name: Optional[str] = None,
        sheet_index: Optional[int] = None,
        max_rows: int = 100
    ) -> Dict[str, Any]:
        """
        Read specific Excel sheet
        
        Args:
            filename: Name of Excel file
            sheet_name: Name of sheet (optional)
            sheet_index: Index of sheet (optional)
            max_rows: Maximum rows to return
            
        Returns:
            Sheet data
        """
        arguments = {
            'action': 'read_excel_sheet',
            'filename': filename,
            'max_rows': max_rows
        }
        
        if sheet_name:
            arguments['sheet_name'] = sheet_name
        elif sheet_index is not None:
            arguments['sheet_index'] = sheet_index
        else:
            raise ValueError("Either sheet_name or sheet_index must be provided")
        
        return self._make_request(arguments)
    
    def get_all_word_files(self) -> List[Dict]:
        """
        Get list of all Word files
        
        Returns:
            List of Word files
        """
        result = self.list_files('word')
        return result.get('files', [])
    
    def get_all_excel_files(self) -> List[Dict]:
        """
        Get list of all Excel files
        
        Returns:
            List of Excel files
        """
        result = self.list_files('excel')
        return result.get('files', [])
    
    def search_all_word_files(self, search_term: str) -> Dict[str, List]:
        """
        Search for term in all Word files
        
        Args:
            search_term: Text to search for
            
        Returns:
            Dictionary of filename to matches
        """
        word_files = self.get_all_word_files()
        results = {}
        
        for file_info in word_files:
            try:
                search_result = self.search_word(file_info['filename'], search_term)
                if search_result['match_count'] > 0:
                    results[file_info['filename']] = search_result['matches']
            except Exception as e:
                print(f"Error searching {file_info['filename']}: {e}")
        
        return results
    
    def get_document_summary(self, filename: str) -> Dict[str, Any]:
        """
        Get comprehensive summary of document
        
        Args:
            filename: Name of file
            
        Returns:
            Document summary
        """
        if filename.endswith('.docx'):
            metadata = self.get_word_metadata(filename)
            text = self.extract_text(filename)
            
            return {
                'filename': filename,
                'type': 'word',
                'metadata': metadata.get('metadata', {}),
                'statistics': metadata.get('statistics', {}),
                'text_stats': {
                    'characters': text.get('character_count', 0),
                    'words': text.get('word_count', 0),
                    'paragraphs': text.get('paragraph_count', 0)
                }
            }
        elif filename.endswith('.xlsx') or filename.endswith('.xlsm'):
            metadata = self.get_excel_metadata(filename)
            sheets = self.get_excel_sheets(filename)
            
            return {
                'filename': filename,
                'type': 'excel',
                'metadata': metadata.get('metadata', {}),
                'statistics': metadata.get('statistics', {}),
                'sheets': sheets.get('sheets', [])
            }
        else:
            raise ValueError("Unsupported file type")
    
    def print_file_list(self, file_type: str = 'all'):
        """
        Pretty print file list
        
        Args:
            file_type: Type of files to list
        """
        result = self.list_files(file_type)
        
        print(f"\n{'='*80}")
        print(f"Documents in {result['directory']}")
        print(f"Type: {result['file_type']}")
        print(f"Total: {result['count']} files")
        print(f"{'='*80}\n")
        
        for file in result['files']:
            print(f"📄 {file['filename']}")
            print(f"   Type: {file['type']}")
            print(f"   Size: {file['size_mb']} MB")
            print(f"   Modified: {file['modified']}")
            print()
    
    def print_word_content(self, filename: str, max_paragraphs: int = 5):
        """
        Pretty print Word document content
        
        Args:
            filename: Name of Word file
            max_paragraphs: Maximum paragraphs to display
        """
        result = self.read_word_document(filename)
        
        print(f"\n{'='*80}")
        print(f"Word Document: {result['filename']}")
        print(f"{'='*80}\n")
        
        print(f"Paragraphs: {result['paragraph_count']}")
        print(f"Tables: {result['table_count']}")
        
        if 'metadata' in result:
            print(f"\nAuthor: {result['metadata'].get('author', 'Unknown')}")
            print(f"Created: {result['metadata'].get('created', 'Unknown')}")
        
        print(f"\n{'-'*80}")
        print("Content Preview:")
        print(f"{'-'*80}\n")
        
        for i, para in enumerate(result['paragraphs'][:max_paragraphs], 1):
            print(f"{i}. [{para['style']}]")
            print(f"   {para['text'][:200]}")
            if len(para['text']) > 200:
                print("   ...")
            print()
    
    def print_excel_content(self, filename: str, max_rows: int = 10):
        """
        Pretty print Excel file content
        
        Args:
            filename: Name of Excel file
            max_rows: Maximum rows to display
        """
        result = self.read_excel_file(filename, max_rows=max_rows)
        
        print(f"\n{'='*80}")
        print(f"Excel File: {result['filename']}")
        print(f"{'='*80}\n")
        
        print(f"Sheets: {result['sheet_count']}")
        print(f"Sheet Names: {', '.join(result['sheet_names'])}\n")
        
        for sheet_name, sheet_data in result['sheets'].items():
            print(f"{'-'*80}")
            print(f"Sheet: {sheet_name}")
            print(f"Rows: {sheet_data['row_count']}/{sheet_data['total_rows']}")
            print(f"Columns: {sheet_data['column_count']}")
            print(f"{'-'*80}\n")
            
            # Print rows
            for i, row in enumerate(sheet_data['rows'][:5], 1):
                print(f"Row {i}: {' | '.join(str(cell)[:20] for cell in row)}")
            print()


def main():
    """
    Main function with usage examples
    """
    # Initialize client
    BASE_URL = 'http://localhost:5000'
    API_TOKEN = None
    
    client = MsDocToolsClient(BASE_URL, API_TOKEN)
    
    print("="*80)
    print("MICROSOFT DOCUMENTS TOOL - CLIENT EXAMPLES")
    print("="*80)
    
    # Example 1: List All Files
    print("\n" + "="*80)
    print("EXAMPLE 1: List All Documents")
    print("="*80)
    
    try:
        client.print_file_list('all')
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: List Word Documents Only
    print("\n" + "="*80)
    print("EXAMPLE 2: List Word Documents")
    print("="*80)
    
    try:
        word_files = client.get_all_word_files()
        print(f"\nFound {len(word_files)} Word documents:\n")
        for file in word_files:
            print(f"- {file['filename']} ({file['size_mb']} MB)")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Read Word Document
    print("\n" + "="*80)
    print("EXAMPLE 3: Read Word Document")
    print("="*80)
    
    try:
        # Get first Word file
        word_files = client.get_all_word_files()
        if word_files:
            filename = word_files[0]['filename']
            client.print_word_content(filename, max_paragraphs=3)
        else:
            print("\nNo Word documents found in data/msdocs/")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Read Excel File
    print("\n" + "="*80)
    print("EXAMPLE 4: Read Excel File")
    print("="*80)
    
    try:
        excel_files = client.get_all_excel_files()
        if excel_files:
            filename = excel_files[0]['filename']
            client.print_excel_content(filename, max_rows=10)
        else:
            print("\nNo Excel files found in data/msdocs/")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 5: Get Excel Sheets
    print("\n" + "="*80)
    print("EXAMPLE 5: List Excel Sheets")
    print("="*80)
    
    try:
        excel_files = client.get_all_excel_files()
        if excel_files:
            filename = excel_files[0]['filename']
            result = client.get_excel_sheets(filename)
            
            print(f"\nWorkbook: {result['filename']}")
            print(f"Total Sheets: {result['sheet_count']}\n")
            
            for sheet in result['sheets']:
                print(f"Sheet {sheet['index']}: {sheet['name']}")
                print(f"  {sheet['rows']} rows x {sheet['columns']} columns")
        else:
            print("\nNo Excel files found")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 6: Read Specific Excel Sheet
    print("\n" + "="*80)
    print("EXAMPLE 6: Read Specific Excel Sheet")
    print("="*80)
    
    try:
        excel_files = client.get_all_excel_files()
        if excel_files:
            filename = excel_files[0]['filename']
            result = client.read_excel_sheet(filename, sheet_index=0, max_rows=5)
            
            print(f"\nSheet: {result['sheet_name']}")
            print(f"Showing {result['row_count']} rows:\n")
            
            for i, row in enumerate(result['rows'], 1):
                print(f"Row {i}: {' | '.join(str(cell)[:15] for cell in row)}")
        else:
            print("\nNo Excel files found")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 7: Search Word Document
    print("\n" + "="*80)
    print("EXAMPLE 7: Search in Word Document")
    print("="*80)
    
    try:
        word_files = client.get_all_word_files()
        if word_files:
            filename = word_files[0]['filename']
            search_term = "the"  # Common word
            
            result = client.search_word(filename, search_term)
            
            print(f"\nSearching for '{search_term}' in {filename}")
            print(f"Matches found: {result['match_count']}\n")
            
            for i, match in enumerate(result['matches'][:3], 1):
                print(f"Match {i}:")
                if match['type'] == 'paragraph':
                    print(f"  Paragraph {match['index']}")
                    print(f"  ...{match['context']}...")
                print()
        else:
            print("\nNo Word documents found")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 8: Search Excel File
    print("\n" + "="*80)
    print("EXAMPLE 8: Search in Excel File")
    print("="*80)
    
    try:
        excel_files = client.get_all_excel_files()
        if excel_files:
            filename = excel_files[0]['filename']
            search_term = "total"  # Common term
            
            result = client.search_excel(filename, search_term)
            
            print(f"\nSearching for '{search_term}' in {filename}")
            print(f"Matches found: {result['match_count']}\n")
            
            for i, match in enumerate(result['matches'][:5], 1):
                print(f"Match {i}:")
                print(f"  Sheet: {match['sheet']}")
                print(f"  Cell: {match['cell']}")
                print(f"  Value: {match['value']}")
                print()
        else:
            print("\nNo Excel files found")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 9: Get Document Metadata
    print("\n" + "="*80)
    print("EXAMPLE 9: Get Document Metadata")
    print("="*80)
    
    try:
        word_files = client.get_all_word_files()
        if word_files:
            filename = word_files[0]['filename']
            result = client.get_word_metadata(filename)
            
            print(f"\nDocument: {result['filename']}")
            print("\nMetadata:")
            for key, value in result['metadata'].items():
                print(f"  {key}: {value}")
            
            print("\nStatistics:")
            for key, value in result['statistics'].items():
                print(f"  {key}: {value}")
        else:
            print("\nNo Word documents found")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 10: Extract Text
    print("\n" + "="*80)
    print("EXAMPLE 10: Extract Text from Document")
    print("="*80)
    
    try:
        word_files = client.get_all_word_files()
        if word_files:
            filename = word_files[0]['filename']
            result = client.extract_text(filename)
            
            print(f"\nDocument: {result['filename']}")
            print(f"Characters: {result['character_count']}")
            print(f"Words: {result['word_count']}")
            print(f"Paragraphs: {result.get('paragraph_count', 'N/A')}")
            
            print("\nText Preview (first 300 characters):")
            print(result['text'][:300])
            print("...")
        else:
            print("\nNo Word documents found")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 11: Get Document Summary
    print("\n" + "="*80)
    print("EXAMPLE 11: Get Comprehensive Document Summary")
    print("="*80)
    
    try:
        word_files = client.get_all_word_files()
        if word_files:
            filename = word_files[0]['filename']
            summary = client.get_document_summary(filename)
            
            print(f"\nDocument: {summary['filename']}")
            print(f"Type: {summary['type']}")
            
            if 'text_stats' in summary:
                print("\nText Statistics:")
                for key, value in summary['text_stats'].items():
                    print(f"  {key}: {value}")
        else:
            print("\nNo documents found")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 12: Search All Word Files
    print("\n" + "="*80)
    print("EXAMPLE 12: Search Across All Word Documents")
    print("="*80)
    
    try:
        search_term = "report"
        results = client.search_all_word_files(search_term)
        
        print(f"\nSearching for '{search_term}' across all Word documents")
        print(f"Files with matches: {len(results)}\n")
        
        for filename, matches in results.items():
            print(f"{filename}: {len(matches)} matches")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)
    print("ALL EXAMPLES COMPLETED")
    print("="*80)
    print("\nNote: Place your .docx and .xlsx files in data/msdocs/ to test")


if __name__ == "__main__":
    """
    Run the client examples
    
    Usage:
        python msdoc_tools_client.py
    
    Configuration:
        Update BASE_URL and API_TOKEN in main() function
    
    Requirements:
        - Server must be running
        - python-docx and openpyxl installed on server
        - Documents in data/msdocs/ directory
    """
    main()
