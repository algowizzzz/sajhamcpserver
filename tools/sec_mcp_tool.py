"""
SEC MCP Tool implementation including EDGAR database access
"""
import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base_mcp_tool import BaseMCPTool
import xml.etree.ElementTree as ET


class SECMCPTool(BaseMCPTool):
    """MCP Tool for SEC and EDGAR database operations"""

    def _initialize(self):
        """Initialize SEC specific components"""
        self.base_url = "https://data.sec.gov"
        self.edgar_url = "https://www.sec.gov/Archives/edgar"
        self.user_agent = os.environ.get('SEC_USER_AGENT', 'YourApp/1.0 (your-email@example.com)')

        # SEC requires a user agent with contact info
        self.headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json'
        }

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle SEC tool calls

        Args:
            tool_name: Name of the tool being called
            arguments: Arguments for the tool

        Returns:
            Result of the tool call
        """
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            # Map tool names to methods
            tool_methods = {
                "get_company_info": self._get_company_info,
                "get_company_filings": self._get_company_filings,
                "get_filing_details": self._get_filing_details,
                "search_filings": self._search_filings,
                "get_insider_transactions": self._get_insider_transactions,
                "get_company_facts": self._get_company_facts,
                "get_cik_lookup": self._get_cik_lookup,
                "get_recent_filings": self._get_recent_filings,
                "get_financial_statements": self._get_financial_statements,
                "get_company_tickers": self._get_company_tickers
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

    def _get_company_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get company information from SEC"""
        cik = params.get('cik', '')
        ticker = params.get('ticker', '')

        if not cik and not ticker:
            return {"error": "Either CIK or ticker is required"}

        # Convert ticker to CIK if needed
        if ticker and not cik:
            cik_result = self._get_cik_lookup({'ticker': ticker})
            if 'error' in cik_result:
                return cik_result
            cik = cik_result.get('cik', '')

        # Pad CIK with zeros to 10 digits
        cik = str(cik).zfill(10)

        try:
            # Get company submissions
            url = f"{self.base_url}/submissions/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()

                return {
                    "cik": cik,
                    "name": data.get('name', ''),
                    "ticker": data.get('tickers', []),
                    "exchanges": data.get('exchanges', []),
                    "sic": data.get('sic', ''),
                    "sic_description": data.get('sicDescription', ''),
                    "category": data.get('category', ''),
                    "fiscal_year_end": data.get('fiscalYearEnd', ''),
                    "state_of_incorporation": data.get('stateOfIncorporation', ''),
                    "business_address": data.get('addresses', {}).get('business', {}),
                    "mailing_address": data.get('addresses', {}).get('mailing', {}),
                    "former_names": data.get('formerNames', []),
                    "ein": data.get('ein', ''),
                    "entity_type": data.get('entityType', ''),
                    "website": data.get('website', '')
                }
            else:
                return {"error": f"Failed to fetch company info: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_company_filings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get company filings from SEC"""
        cik = params.get('cik', '')
        ticker = params.get('ticker', '')
        filing_type = params.get('filing_type', '')  # e.g., '10-K', '10-Q', '8-K'
        limit = params.get('limit', 20)

        if not cik and not ticker:
            return {"error": "Either CIK or ticker is required"}

        # Convert ticker to CIK if needed
        if ticker and not cik:
            cik_result = self._get_cik_lookup({'ticker': ticker})
            if 'error' in cik_result:
                return cik_result
            cik = cik_result.get('cik', '')

        # Pad CIK with zeros to 10 digits
        cik = str(cik).zfill(10)

        try:
            url = f"{self.base_url}/submissions/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                filings = data.get('filings', {}).get('recent', {})

                # Process filings
                filing_list = []
                accession_numbers = filings.get('accessionNumber', [])
                filing_dates = filings.get('filingDate', [])
                report_dates = filings.get('reportDate', [])
                forms = filings.get('form', [])
                primary_documents = filings.get('primaryDocument', [])
                primary_doc_descriptions = filings.get('primaryDocDescription', [])

                for i in range(min(len(accession_numbers), limit)):
                    # Filter by filing type if specified
                    if filing_type and forms[i] != filing_type:
                        continue

                    filing_list.append({
                        "accession_number": accession_numbers[i],
                        "filing_date": filing_dates[i],
                        "report_date": report_dates[i],
                        "form": forms[i],
                        "primary_document": primary_documents[i],
                        "document_description": primary_doc_descriptions[i],
                        "edgar_url": f"{self.edgar_url}/data/{cik.lstrip('0')}/{accession_numbers[i].replace('-', '')}/{accession_numbers[i]}-index.htm"
                    })

                return {
                    "cik": cik,
                    "company_name": data.get('name', ''),
                    "filings": filing_list,
                    "count": len(filing_list)
                }
            else:
                return {"error": f"Failed to fetch filings: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_filing_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a specific filing"""
        cik = params.get('cik', '')
        accession_number = params.get('accession_number', '')

        if not cik or not accession_number:
            return {"error": "Both CIK and accession number are required"}

        # Format CIK and accession number
        cik = str(cik).zfill(10).lstrip('0')
        accession_clean = accession_number.replace('-', '')

        try:
            # Get filing index
            index_url = f"{self.edgar_url}/data/{cik}/{accession_clean}/{accession_number}-index.json"
            response = requests.get(index_url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()

                # Get document list
                documents = []
                for item in data.get('directory', {}).get('item', []):
                    documents.append({
                        "name": item.get('name', ''),
                        "type": item.get('type', ''),
                        "size": item.get('size', ''),
                        "last_modified": item.get('lastmod', ''),
                        "url": f"{self.edgar_url}/data/{cik}/{accession_clean}/{item.get('name', '')}"
                    })

                return {
                    "cik": cik,
                    "accession_number": accession_number,
                    "filing_date": data.get('filing_date', ''),
                    "accepted_date": data.get('accepted_date', ''),
                    "documents": documents,
                    "document_count": len(documents)
                }
            else:
                return {"error": f"Failed to fetch filing details: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _search_filings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for filings across all companies"""
        query = params.get('query', '')
        filing_type = params.get('filing_type', '')
        date_from = params.get('date_from', '')
        date_to = params.get('date_to', '')

        # Note: SEC's full-text search API is limited
        # This is a simplified implementation

        search_params = {
            "q": query,
            "dateRange": "custom" if date_from or date_to else "all",
            "startdt": date_from,
            "enddt": date_to,
            "forms": filing_type
        }

        # Remove empty parameters
        search_params = {k: v for k, v in search_params.items() if v}

        return {
            "query": query,
            "results": [],
            "message": "Full-text search requires EDGAR full-text search API access"
        }

    def _get_insider_transactions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get insider transactions (Forms 3, 4, 5)"""
        cik = params.get('cik', '')
        ticker = params.get('ticker', '')

        if not cik and not ticker:
            return {"error": "Either CIK or ticker is required"}

        # Get Form 4 filings (insider transactions)
        filings_result = self._get_company_filings({
            'cik': cik,
            'ticker': ticker,
            'filing_type': '4',
            'limit': 50
        })

        if 'error' in filings_result:
            return filings_result

        # Also get Forms 3 and 5
        form3_result = self._get_company_filings({
            'cik': cik,
            'ticker': ticker,
            'filing_type': '3',
            'limit': 10
        })

        form5_result = self._get_company_filings({
            'cik': cik,
            'ticker': ticker,
            'filing_type': '5',
            'limit': 10
        })

        all_transactions = {
            "cik": cik,
            "form_4_transactions": filings_result.get('filings', []),
            "form_3_holdings": form3_result.get('filings', []) if 'filings' in form3_result else [],
            "form_5_annual": form5_result.get('filings', []) if 'filings' in form5_result else [],
            "total_transactions": len(filings_result.get('filings', [])) +
                                  len(form3_result.get('filings', [])) if 'filings' in form3_result else 0 +
                                                                                                         len(form5_result.get(
                                                                                                             'filings',
                                                                                                             [])) if 'filings' in form5_result else 0
        }

        return all_transactions

    def _get_company_facts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get company financial facts from XBRL data"""
        cik = params.get('cik', '')
        ticker = params.get('ticker', '')

        if not cik and not ticker:
            return {"error": "Either CIK or ticker is required"}

        # Convert ticker to CIK if needed
        if ticker and not cik:
            cik_result = self._get_cik_lookup({'ticker': ticker})
            if 'error' in cik_result:
                return cik_result
            cik = cik_result.get('cik', '')

        # Pad CIK with zeros to 10 digits
        cik = str(cik).zfill(10)

        try:
            url = f"{self.base_url}/api/xbrl/companyfacts/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()

                # Extract key financial metrics
                facts = data.get('facts', {})

                # Process US-GAAP facts
                us_gaap = facts.get('us-gaap', {})

                # Extract common financial metrics
                metrics = {}
                common_items = [
                    'Assets', 'Liabilities', 'StockholdersEquity',
                    'Revenues', 'NetIncomeLoss', 'EarningsPerShareBasic',
                    'CommonStockSharesOutstanding', 'CashAndCashEquivalentsAtCarryingValue'
                ]

                for item in common_items:
                    if item in us_gaap:
                        item_data = us_gaap[item]
                        units = item_data.get('units', {})

                        # Get the most recent value
                        recent_values = []
                        for unit_type, values in units.items():
                            if isinstance(values, list) and values:
                                # Sort by end date and get most recent
                                sorted_values = sorted(values, key=lambda x: x.get('end', ''), reverse=True)
                                if sorted_values:
                                    recent_values.append({
                                        'value': sorted_values[0].get('val'),
                                        'unit': unit_type,
                                        'end_date': sorted_values[0].get('end', ''),
                                        'form': sorted_values[0].get('form', '')
                                    })

                        if recent_values:
                            metrics[item] = recent_values[0]

                return {
                    "cik": cik,
                    "entity_name": data.get('entityName', ''),
                    "financial_metrics": metrics,
                    "fact_count": len(us_gaap)
                }
            else:
                return {"error": f"Failed to fetch company facts: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_cik_lookup(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Look up CIK by ticker symbol"""
        ticker = params.get('ticker', '').upper()

        if not ticker:
            return {"error": "Ticker is required"}

        try:
            # Get company tickers file
            url = f"{self.base_url}/files/company_tickers.json"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()

                # Search for ticker
                for key, company in data.items():
                    if company.get('ticker', '') == ticker:
                        return {
                            "ticker": ticker,
                            "cik": str(company.get('cik_str', '')),
                            "company_name": company.get('title', '')
                        }

                return {"error": f"Ticker {ticker} not found"}
            else:
                return {"error": f"Failed to fetch tickers: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_recent_filings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent filings across all companies"""
        filing_type = params.get('filing_type', '')
        limit = params.get('limit', 20)

        # Note: This would require accessing SEC's RSS feeds or recent filings endpoint
        # Simplified implementation

        return {
            "filing_type": filing_type,
            "recent_filings": [],
            "message": "Recent filings requires RSS feed parsing or additional API access"
        }

    def _get_financial_statements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get parsed financial statements from XBRL filings"""
        cik = params.get('cik', '')
        ticker = params.get('ticker', '')
        statement_type = params.get('statement_type', '')  # 'income', 'balance', 'cash_flow'
        period = params.get('period', 'annual')  # 'annual' or 'quarterly'

        if not cik and not ticker:
            return {"error": "Either CIK or ticker is required"}

        # This would require parsing XBRL documents
        # Providing structure for implementation

        return {
            "cik": cik,
            "statement_type": statement_type,
            "period": period,
            "data": {},
            "message": "Financial statement parsing requires XBRL processing implementation"
        }

    def _get_company_tickers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of all company tickers"""
        exchange = params.get('exchange', '')  # NYSE, NASDAQ, etc.

        try:
            url = f"{self.base_url}/files/company_tickers.json"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()

                tickers = []
                for key, company in data.items():
                    ticker_info = {
                        "ticker": company.get('ticker', ''),
                        "cik": str(company.get('cik_str', '')),
                        "name": company.get('title', '')
                    }

                    # Filter by exchange if specified
                    if not exchange or exchange.upper() in ticker_info['ticker']:
                        tickers.append(ticker_info)

                return {
                    "tickers": tickers[:100],  # Limit to first 100
                    "total_count": len(tickers)
                }
            else:
                return {"error": f"Failed to fetch tickers: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}