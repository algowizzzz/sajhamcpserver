"""
EDGAR MCP Tool - Comprehensive SEC EDGAR database access implementation
"""
import os
import requests
import json
import time
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlencode, quote
from .base_mcp_tool import BaseMCPTool
import re
import csv
from io import StringIO


class EDGARMCPTool(BaseMCPTool):
    """Comprehensive MCP Tool for SEC EDGAR database operations"""

    def _initialize(self):
        """Initialize EDGAR specific components"""
        # API endpoints
        self.data_url = "https://data.sec.gov"
        self.edgar_url = "https://www.sec.gov/Archives/edgar"
        self.efts_url = "https://efts.sec.gov/LATEST"

        # User agent required by SEC
        self.user_agent = os.environ.get(
            'SEC_USER_AGENT',
            'CompanyName/1.0 (contact@example.com)'
        )

        self.headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json,application/xml,text/html,text/plain'
        }

        # Cache for frequently accessed data
        self.ticker_cache = {}
        self.cik_cache = {}
        self.last_ticker_update = None

        # Filing type mappings
        self.filing_categories = {
            'annual': ['10-K', '10-K/A', '20-F', '20-F/A', '40-F', '40-F/A'],
            'quarterly': ['10-Q', '10-Q/A'],
            'current': ['8-K', '8-K/A', '6-K'],
            'proxy': ['DEF 14A', 'DEFM14A', 'DEF 14C', 'PRE 14A'],
            'registration': ['S-1', 'S-3', 'S-4', 'S-8', 'S-11', 'F-1', 'F-3', 'F-4'],
            'insider': ['3', '4', '5', '144'],
            'institutional': ['13F-HR', '13F-HR/A', '13D', '13G', '13D/A', '13G/A'],
            'fund': ['N-Q', 'N-CSR', 'N-CSR/A', 'N-PX', '485BPOS', '485APOS']
        }

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle EDGAR tool calls

        Args:
            tool_name: Name of the tool being called
            arguments: Arguments for the tool

        Returns:
            Result of the tool call
        """
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded. SEC limits requests to 10 per second"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            # Map tool names to methods
            tool_methods = {
                "get_company_info": self._get_company_info,
                "get_company_filings": self._get_company_filings,
                "get_filing_documents": self._get_filing_documents,
                "get_insider_transactions": self._get_insider_transactions,
                "get_institutional_holdings": self._get_institutional_holdings,
                "get_beneficial_ownership": self._get_beneficial_ownership,
                "get_proxy_statements": self._get_proxy_statements,
                "get_company_financials": self._get_company_financials,
                "get_fund_data": self._get_fund_data,
                "search_filings": self._search_filings,
                "get_recent_filings": self._get_recent_filings,
                "get_ipo_registrations": self._get_ipo_registrations,
                "get_merger_filings": self._get_merger_filings,
                "get_comment_letters": self._get_comment_letters,
                "get_xbrl_facts": self._get_xbrl_facts,
                "get_peer_comparison": self._get_peer_comparison,
                "get_cik_lookup": self._get_cik_lookup,
                "get_company_tickers": self._get_company_tickers,
                "get_historical_data": self._get_historical_data,
                "validate_filing": self._validate_filing
            }

            if tool_name not in tool_methods:
                result = {"error": f"Unknown tool: {tool_name}"}
            else:
                result = tool_methods[tool_name](arguments)

            self.record_call(tool_name, arguments, result=result)
            return result

        except Exception as e:
            error_msg = str(e)
            self.record_call(tool_name, arguments, error=error_msg)
            return {"error": error_msg, "status": 500}

    def _ensure_ticker_cache(self):
        """Ensure ticker cache is loaded and up to date"""
        if not self.ticker_cache or not self.last_ticker_update or \
           (datetime.now() - self.last_ticker_update).days > 1:
            self._load_ticker_cache()

    def _load_ticker_cache(self):
        """Load ticker to CIK mapping cache"""
        try:
            url = f"{self.data_url}/files/company_tickers.json"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                self.ticker_cache = {}
                self.cik_cache = {}

                for key, company in data.items():
                    ticker = company.get('ticker', '')
                    cik = str(company.get('cik_str', '')).zfill(10)
                    name = company.get('title', '')

                    if ticker:
                        self.ticker_cache[ticker] = {
                            'cik': cik,
                            'name': name
                        }
                    if cik:
                        self.cik_cache[cik] = {
                            'ticker': ticker,
                            'name': name
                        }

                self.last_ticker_update = datetime.now()
                return True
        except requests.exceptions.RequestException as e:
            # Network error - cache remains empty but don't crash
            print(f"Warning: Could not load ticker cache: {e}")
        except Exception as e:
            # Other errors - cache remains empty but don't crash
            print(f"Warning: Error processing ticker cache: {e}")

        return False

    def _normalize_cik(self, cik: str) -> str:
        """Normalize CIK to 10-digit format"""
        return str(cik).zfill(10)

    def _resolve_identifier(self, params: Dict[str, Any]) -> Optional[str]:
        """Resolve company identifier to CIK"""
        cik = params.get('cik', '')
        ticker = params.get('ticker', '')

        if cik:
            return self._normalize_cik(cik)

        if ticker:
            # First try cache
            self._ensure_ticker_cache()
            ticker_upper = ticker.upper()
            if ticker_upper in self.ticker_cache:
                return self.ticker_cache[ticker_upper]['cik']

            # If cache failed or ticker not found, try direct lookup
            cik_result = self._get_cik_lookup_direct(ticker_upper)
            if cik_result:
                return cik_result

        return None

    def _get_cik_lookup_direct(self, ticker: str) -> Optional[str]:
        """Direct CIK lookup without cache"""
        try:
            url = f"{self.data_url}/submissions/CIK{ticker}.json"
            # Try ticker-based search endpoint
            tickers_url = f"{self.data_url}/files/company_tickers.json"
            response = requests.get(tickers_url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                for key, company in data.items():
                    if company.get('ticker', '') == ticker:
                        return str(company.get('cik_str', '')).zfill(10)
        except Exception as e:
            # Log error but don't raise
            pass

        return None

    def _get_company_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive company information from EDGAR"""
        cik = params.get('cik', '')
        ticker = params.get('ticker', '')

        # Try to resolve identifier
        resolved_cik = self._resolve_identifier(params)

        if not resolved_cik:
            if ticker:
                # Try alternative lookup method for ticker
                ticker_upper = ticker.upper()
                try:
                    # Use CIK lookup tool directly
                    lookup_result = self._get_cik_lookup({'ticker': ticker_upper})
                    if 'results' in lookup_result and lookup_result['results']:
                        resolved_cik = lookup_result['results'][0].get('cik')
                except:
                    pass

                if not resolved_cik:
                    return {
                        "error": f"Ticker '{ticker}' not found. Please verify the ticker symbol or use CIK instead.",
                        "suggestion": "You can find the CIK at https://www.sec.gov/edgar/searchedgar/companysearch"
                    }
            else:
                return {"error": "Either CIK or ticker is required"}

        cik = resolved_cik

        try:
            # Get company submissions
            url = f"{self.data_url}/submissions/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()

                # Get additional company facts
                facts_url = f"{self.data_url}/api/xbrl/companyfacts/CIK{cik}.json"
                facts_response = requests.get(facts_url, headers=self.headers)

                entity_info = {}
                if facts_response.status_code == 200:
                    facts_data = facts_response.json()
                    entity_info = {
                        "entity_name": facts_data.get('entityName', ''),
                        "fact_count": len(facts_data.get('facts', {}).get('us-gaap', {}))
                    }

                # Extract insider roster if available
                insiders = []
                if 'insiders' in data:
                    for insider in data.get('insiders', []):
                        insiders.append({
                            "name": insider.get('name', ''),
                            "title": insider.get('title', ''),
                            "cik": insider.get('cik', '')
                        })

                return {
                    "cik": cik,
                    "name": data.get('name', ''),
                    "tickers": data.get('tickers', []),
                    "exchanges": data.get('exchanges', []),
                    "sic": data.get('sic', ''),
                    "sic_description": data.get('sicDescription', ''),
                    "category": data.get('category', ''),
                    "fiscal_year_end": data.get('fiscalYearEnd', ''),
                    "state_of_incorporation": data.get('stateOfIncorporation', ''),
                    "state_location": data.get('stateOfLocation', ''),
                    "business_address": data.get('addresses', {}).get('business', {}),
                    "mailing_address": data.get('addresses', {}).get('mailing', {}),
                    "phone": data.get('phone', ''),
                    "former_names": data.get('formerNames', []),
                    "ein": data.get('ein', ''),
                    "entity_type": data.get('entityType', ''),
                    "website": data.get('website', ''),
                    "investor_website": data.get('investorWebsite', ''),
                    "insiders": insiders[:10] if insiders else [],
                    "flags": data.get('flags', ''),
                    **entity_info
                }
            else:
                return {"error": f"Failed to fetch company info: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_company_filings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get company filings with advanced filtering"""
        cik = self._resolve_identifier(params)

        if not cik:
            return {"error": "Either CIK or ticker is required"}

        filing_type = params.get('filing_type', '')
        date_from = params.get('date_from', '')
        date_to = params.get('date_to', '')
        limit = params.get('limit', 20)

        try:
            url = f"{self.data_url}/submissions/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                filings = data.get('filings', {}).get('recent', {})

                # Process filings with filtering
                filing_list = []
                accession_numbers = filings.get('accessionNumber', [])
                filing_dates = filings.get('filingDate', [])
                report_dates = filings.get('reportDate', [])
                forms = filings.get('form', [])
                primary_documents = filings.get('primaryDocument', [])
                primary_doc_descriptions = filings.get('primaryDocDescription', [])
                file_numbers = filings.get('fileNumber', [])
                film_numbers = filings.get('filmNumber', [])
                item_values = filings.get('items', [])
                sizes = filings.get('size', [])
                is_xbrl = filings.get('isXBRL', [])
                is_inline_xbrl = filings.get('isInlineXBRL', [])

                for i in range(min(len(accession_numbers), 1000)):
                    # Filter by filing type
                    if filing_type and forms[i] != filing_type:
                        continue

                    # Filter by date range
                    if date_from and filing_dates[i] < date_from:
                        continue
                    if date_to and filing_dates[i] > date_to:
                        continue

                    filing_entry = {
                        "accession_number": accession_numbers[i],
                        "filing_date": filing_dates[i],
                        "report_date": report_dates[i] if i < len(report_dates) else '',
                        "form": forms[i],
                        "primary_document": primary_documents[i] if i < len(primary_documents) else '',
                        "document_description": primary_doc_descriptions[i] if i < len(primary_doc_descriptions) else '',
                        "file_number": file_numbers[i] if i < len(file_numbers) else '',
                        "film_number": film_numbers[i] if i < len(film_numbers) else '',
                        "items": item_values[i] if i < len(item_values) else '',
                        "size": sizes[i] if i < len(sizes) else 0,
                        "is_xbrl": is_xbrl[i] if i < len(is_xbrl) else 0,
                        "is_inline_xbrl": is_inline_xbrl[i] if i < len(is_inline_xbrl) else 0,
                        "edgar_url": f"{self.edgar_url}/data/{cik.lstrip('0')}/{accession_numbers[i].replace('-', '')}/{accession_numbers[i]}-index.htm"
                    }

                    filing_list.append(filing_entry)

                    if len(filing_list) >= limit:
                        break

                # Get filing statistics
                form_counts = {}
                for form in forms[:1000]:
                    form_counts[form] = form_counts.get(form, 0) + 1

                return {
                    "cik": cik,
                    "company_name": data.get('name', ''),
                    "filings": filing_list,
                    "count": len(filing_list),
                    "total_filings": len(accession_numbers),
                    "filing_types": sorted(form_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                }
            else:
                return {"error": f"Failed to fetch filings: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_filing_documents(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed documents and exhibits from a specific filing"""
        cik = params.get('cik', '')
        accession_number = params.get('accession_number', '')
        include_exhibits = params.get('include_exhibits', True)

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

                # Categorize documents
                primary_docs = []
                exhibits = []
                graphics = []
                xbrl_docs = []
                other_docs = []

                for item in data.get('directory', {}).get('item', []):
                    doc_info = {
                        "name": item.get('name', ''),
                        "type": item.get('type', ''),
                        "size": item.get('size', ''),
                        "last_modified": item.get('lastmod', ''),
                        "description": item.get('description', ''),
                        "url": f"{self.edgar_url}/data/{cik}/{accession_clean}/{item.get('name', '')}"
                    }

                    name = item.get('name', '').lower()

                    # Categorize by document type
                    if name.endswith('.htm') and not 'ex-' in name and not 'exhibit' in name:
                        primary_docs.append(doc_info)
                    elif 'ex-' in name or 'exhibit' in name:
                        if include_exhibits:
                            exhibits.append(doc_info)
                    elif name.endswith(('.jpg', '.gif', '.png', '.pdf')):
                        graphics.append(doc_info)
                    elif name.endswith(('.xml', '.xsd', '.xbrl')):
                        xbrl_docs.append(doc_info)
                    else:
                        other_docs.append(doc_info)

                return {
                    "cik": cik,
                    "accession_number": accession_number,
                    "filing_date": data.get('filing_date', ''),
                    "accepted_date": data.get('accepted_date', ''),
                    "period_of_report": data.get('period_of_report', ''),
                    "form_type": data.get('form_type', ''),
                    "primary_documents": primary_docs,
                    "exhibits": exhibits,
                    "graphics": graphics[:5],  # Limit graphics to avoid large responses
                    "xbrl_documents": xbrl_docs,
                    "other_documents": other_docs[:5],
                    "document_count": len(primary_docs) + len(exhibits) + len(graphics) + len(xbrl_docs) + len(other_docs),
                    "index_url": f"{self.edgar_url}/data/{cik}/{accession_clean}/{accession_number}-index.htm"
                }
            else:
                return {"error": f"Failed to fetch filing documents: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_insider_transactions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get insider trading transactions with detailed analysis"""
        cik = self._resolve_identifier(params)

        if not cik:
            return {"error": "Either CIK or ticker is required"}

        insider_cik = params.get('insider_cik', '')
        transaction_type = params.get('transaction_type', '')
        date_from = params.get('date_from', '')
        date_to = params.get('date_to', '')
        limit = params.get('limit', 50)

        # Get Form 4 filings
        filings_params = {
            'cik': cik,
            'filing_type': '4',
            'date_from': date_from,
            'date_to': date_to,
            'limit': limit
        }

        form4_result = self._get_company_filings(filings_params)

        if 'error' in form4_result:
            return form4_result

        # Also get Forms 3 and 5 for complete picture
        form3_params = {**filings_params, 'filing_type': '3', 'limit': 10}
        form5_params = {**filings_params, 'filing_type': '5', 'limit': 10}

        form3_result = self._get_company_filings(form3_params)
        form5_result = self._get_company_filings(form5_params)

        # Process transactions (would need to parse actual Form 4 XML for full details)
        transactions = []
        for filing in form4_result.get('filings', []):
            transactions.append({
                "accession_number": filing['accession_number'],
                "filing_date": filing['filing_date'],
                "form_type": "4",
                "document_url": filing['edgar_url'],
                "reporting_owner": "Parse from document",  # Would need to fetch and parse
                "transaction_type": "Parse from document",
                "securities_transacted": "Parse from document"
            })

        # Calculate summary statistics
        summary = {
            "total_form4": len(form4_result.get('filings', [])),
            "total_form3": len(form3_result.get('filings', [])) if 'filings' in form3_result else 0,
            "total_form5": len(form5_result.get('filings', [])) if 'filings' in form5_result else 0,
            "date_range": f"{date_from or 'earliest'} to {date_to or 'latest'}"
        }

        return {
            "cik": cik,
            "company_name": form4_result.get('company_name', ''),
            "transactions": transactions[:limit],
            "form3_initial_holdings": form3_result.get('filings', [])[:5] if 'filings' in form3_result else [],
            "form5_annual_statement": form5_result.get('filings', [])[:5] if 'filings' in form5_result else [],
            "summary": summary
        }

    def _get_institutional_holdings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get institutional holdings from 13F filings"""
        cik = params.get('cik', '')
        institution_name = params.get('institution_name', '')
        quarter = params.get('quarter', '')
        cusip = params.get('cusip', '')

        if not cik and not institution_name:
            return {"error": "Either institution CIK or name is required"}

        # Get 13F-HR filings
        filings_params = {
            'cik': cik,
            'filing_type': '13F-HR',
            'limit': 10
        }

        if quarter:
            # Convert quarter to date range
            year = int(quarter[:4])
            qtr = int(quarter[5:6])
            if qtr == 1:
                filings_params['date_from'] = f"{year}-01-01"
                filings_params['date_to'] = f"{year}-03-31"
            elif qtr == 2:
                filings_params['date_from'] = f"{year}-04-01"
                filings_params['date_to'] = f"{year}-06-30"
            elif qtr == 3:
                filings_params['date_from'] = f"{year}-07-01"
                filings_params['date_to'] = f"{year}-09-30"
            elif qtr == 4:
                filings_params['date_from'] = f"{year}-10-01"
                filings_params['date_to'] = f"{year}-12-31"

        filings_result = self._get_company_filings(filings_params)

        if 'error' in filings_result:
            return filings_result

        # Process holdings (would need to parse actual 13F XML for full details)
        holdings_summary = {
            "institution_cik": cik,
            "institution_name": filings_result.get('company_name', ''),
            "recent_filings": filings_result.get('filings', [])[:5],
            "filing_count": len(filings_result.get('filings', [])),
            "message": "Full holdings details would require parsing the 13F-HR XML documents"
        }

        if cusip:
            holdings_summary["cusip_filter"] = cusip

        return holdings_summary

    def _get_beneficial_ownership(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get beneficial ownership from Schedule 13D/G filings"""
        cik = self._resolve_identifier(params)

        if not cik:
            return {"error": "Either CIK or ticker is required"}

        owner_name = params.get('owner_name', '')
        ownership_threshold = params.get('ownership_threshold', 5.0)

        # Get 13D and 13G filings
        filings_13d = self._get_company_filings({
            'cik': cik,
            'filing_type': 'SC 13D',
            'limit': 20
        })

        filings_13g = self._get_company_filings({
            'cik': cik,
            'filing_type': 'SC 13G',
            'limit': 20
        })

        # Combine and process ownership filings
        all_filings = []

        if 'filings' in filings_13d:
            for filing in filings_13d['filings']:
                filing['schedule_type'] = '13D (Active)'
                all_filings.append(filing)

        if 'filings' in filings_13g:
            for filing in filings_13g['filings']:
                filing['schedule_type'] = '13G (Passive)'
                all_filings.append(filing)

        # Sort by filing date
        all_filings.sort(key=lambda x: x['filing_date'], reverse=True)

        return {
            "cik": cik,
            "company_name": filings_13d.get('company_name', ''),
            "ownership_threshold": ownership_threshold,
            "beneficial_ownership_filings": all_filings[:20],
            "total_13d": len(filings_13d.get('filings', [])) if 'filings' in filings_13d else 0,
            "total_13g": len(filings_13g.get('filings', [])) if 'filings' in filings_13g else 0,
            "message": "Full ownership percentages would require parsing the Schedule 13D/G documents"
        }

    def _get_proxy_statements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get proxy statements and executive compensation data"""
        cik = self._resolve_identifier(params)

        if not cik:
            return {"error": "Either CIK or ticker is required"}

        year = params.get('year', datetime.now().year)
        include_compensation = params.get('include_compensation', True)

        # Get DEF 14A (definitive proxy) filings
        filings_result = self._get_company_filings({
            'cik': cik,
            'filing_type': 'DEF 14A',
            'date_from': f"{year-1}-01-01",
            'date_to': f"{year}-12-31",
            'limit': 5
        })

        if 'error' in filings_result:
            return filings_result

        proxy_data = {
            "cik": cik,
            "company_name": filings_result.get('company_name', ''),
            "fiscal_year": year,
            "proxy_statements": filings_result.get('filings', [])
        }

        if include_compensation:
            # Note: Actual compensation data would require parsing the proxy statement
            proxy_data["executive_compensation"] = {
                "message": "Executive compensation details would require parsing the DEF 14A document",
                "typical_sections": [
                    "Compensation Discussion and Analysis (CD&A)",
                    "Summary Compensation Table",
                    "Grants of Plan-Based Awards",
                    "Outstanding Equity Awards",
                    "Option Exercises and Stock Vested",
                    "Pension Benefits",
                    "Non-Qualified Deferred Compensation",
                    "Director Compensation"
                ]
            }

        return proxy_data

    def _get_company_financials(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get structured financial data from XBRL filings"""
        cik = self._resolve_identifier(params)

        if not cik:
            return {"error": "Either CIK or ticker is required"}

        statement_type = params.get('statement_type', 'all')
        period = params.get('period', 'all')
        fiscal_year = params.get('fiscal_year')
        fiscal_quarter = params.get('fiscal_quarter')

        try:
            # Get company facts from XBRL data
            url = f"{self.data_url}/api/xbrl/companyfacts/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                facts = data.get('facts', {})
                us_gaap = facts.get('us-gaap', {})

                # Define financial statement components
                statement_items = {
                    'balance': [
                        'Assets', 'AssetsCurrent', 'AssetsNoncurrent',
                        'Liabilities', 'LiabilitiesCurrent', 'LiabilitiesNoncurrent',
                        'StockholdersEquity', 'CommonStockSharesOutstanding',
                        'CashAndCashEquivalentsAtCarryingValue', 'Investments',
                        'AccountsReceivableNet', 'Inventory', 'PropertyPlantAndEquipmentNet'
                    ],
                    'income': [
                        'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax',
                        'CostOfRevenue', 'GrossProfit', 'OperatingExpenses',
                        'OperatingIncomeLoss', 'NonoperatingIncomeExpense',
                        'IncomeTaxExpenseBenefit', 'NetIncomeLoss',
                        'EarningsPerShareBasic', 'EarningsPerShareDiluted'
                    ],
                    'cash_flow': [
                        'NetCashProvidedByUsedInOperatingActivities',
                        'NetCashProvidedByUsedInInvestingActivities',
                        'NetCashProvidedByUsedInFinancingActivities',
                        'CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect'
                    ],
                    'comprehensive_income': [
                        'ComprehensiveIncomeNetOfTax',
                        'OtherComprehensiveIncomeLossNetOfTax',
                        'ComprehensiveIncomeNetOfTaxAttributableToNoncontrollingInterest'
                    ]
                }

                # Select items based on statement type
                if statement_type == 'all':
                    items_to_extract = sum(statement_items.values(), [])
                else:
                    items_to_extract = statement_items.get(statement_type, [])

                # Extract financial metrics
                financials = {}
                for item in items_to_extract:
                    if item in us_gaap:
                        item_data = us_gaap[item]
                        units = item_data.get('units', {})

                        values = []
                        for unit_type, unit_values in units.items():
                            if isinstance(unit_values, list):
                                for val in unit_values:
                                    # Filter by period if specified
                                    if period != 'all':
                                        form = val.get('form', '')
                                        if period == 'annual' and '10-K' not in form:
                                            continue
                                        if period == 'quarterly' and '10-Q' not in form:
                                            continue

                                    # Filter by fiscal year/quarter if specified
                                    if fiscal_year:
                                        end_date = val.get('end', '')
                                        if not end_date.startswith(str(fiscal_year)):
                                            continue

                                    values.append({
                                        'value': val.get('val'),
                                        'unit': unit_type,
                                        'end_date': val.get('end', ''),
                                        'start_date': val.get('start', ''),
                                        'form': val.get('form', ''),
                                        'filed': val.get('filed', '')
                                    })

                        if values:
                            # Sort by end date and get recent values
                            values.sort(key=lambda x: x['end_date'], reverse=True)
                            financials[item] = values[:5]  # Keep last 5 periods

                return {
                    "cik": cik,
                    "entity_name": data.get('entityName', ''),
                    "statement_type": statement_type,
                    "period": period,
                    "financials": financials,
                    "metrics_found": len(financials),
                    "data_points": sum(len(v) for v in financials.values())
                }
            else:
                return {"error": f"Failed to fetch financial data: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_fund_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get mutual fund and ETF data"""
        cik = self._resolve_identifier(params)

        if not cik:
            return {"error": "Either CIK or ticker is required"}

        series_id = params.get('series_id', '')
        include_holdings = params.get('include_holdings', True)

        # Get fund-specific filings
        fund_filings = {}
        fund_forms = ['N-Q', 'N-CSR', 'N-PX', '485BPOS', '485APOS']

        for form in fund_forms:
            result = self._get_company_filings({
                'cik': cik,
                'filing_type': form,
                'limit': 5
            })
            if 'filings' in result and result['filings']:
                fund_filings[form] = result['filings']

        fund_info = {
            "cik": cik,
            "series_id": series_id,
            "fund_filings": fund_filings,
            "filing_types_found": list(fund_filings.keys())
        }

        if include_holdings:
            fund_info["holdings"] = {
                "message": "Portfolio holdings would require parsing N-Q and N-CSR filings",
                "recent_holdings_filings": fund_filings.get('N-Q', [])[:3]
            }

        return fund_info

    def _search_filings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Full-text search across EDGAR filings"""
        query = params.get('query', '')
        filing_types = params.get('filing_type', [])
        ciks = params.get('cik', [])
        date_from = params.get('date_from', '')
        date_to = params.get('date_to', '')
        sic_code = params.get('sic_code', '')
        limit = params.get('limit', 50)

        if not query:
            return {"error": "Search query is required"}

        # Build search parameters
        search_params = {
            "q": query,
            "dateRange": "custom" if date_from or date_to else "all",
            "category": "all-public-filings"
        }

        if date_from:
            search_params["from"] = date_from.replace('-', '')
        if date_to:
            search_params["to"] = date_to.replace('-', '')

        if filing_types:
            search_params["forms"] = ",".join(filing_types)

        if ciks:
            search_params["ciks"] = ",".join(ciks)

        if sic_code:
            search_params["sic"] = sic_code

        # Note: SEC's full-text search requires special access
        # This is a simplified response structure
        return {
            "query": query,
            "parameters": search_params,
            "results": [],
            "message": "Full-text search requires EDGAR full-text search API access. Consider using specific filing searches instead.",
            "alternative": "Use get_company_filings with filing_type filter for targeted searches"
        }

    def _get_recent_filings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get most recent filings with real-time updates"""
        filing_types = params.get('filing_type', [])
        minutes_ago = params.get('minutes_ago', 60)
        limit = params.get('limit', 100)

        # Calculate time window
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=minutes_ago)

        # Note: Real-time feed would require RSS or websocket access
        return {
            "time_window": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "minutes": minutes_ago
            },
            "filing_types": filing_types,
            "recent_filings": [],
            "message": "Real-time filing feed requires RSS feed parsing or EDGAR FTP access",
            "rss_feeds": {
                "all_filings": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent",
                "company_filings": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany"
            }
        }

    def _get_ipo_registrations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get IPO registration statements"""
        status = params.get('status', 'all')
        date_from = params.get('date_from', '')
        date_to = params.get('date_to', '')
        industry = params.get('industry', '')

        # Search for registration statements
        registration_forms = ['S-1', 'S-11', 'F-1', 'F-3']
        results = {}

        for form in registration_forms:
            # This would need to search across all companies
            results[form] = {
                "message": f"Would search for {form} filings",
                "date_range": f"{date_from or 'any'} to {date_to or 'any'}"
            }

        return {
            "registration_status": status,
            "date_range": f"{date_from or 'any'} to {date_to or 'any'}",
            "industry_filter": industry,
            "registration_types": registration_forms,
            "results": results,
            "message": "IPO registration search requires cross-company filing search capability"
        }

    def _get_merger_filings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get merger and acquisition related filings"""
        cik = self._resolve_identifier(params)

        if not cik:
            return {"error": "Either CIK or ticker is required"}

        transaction_type = params.get('transaction_type', 'all')
        date_from = params.get('date_from', '')

        # Get M&A related filings
        ma_forms = {
            'merger': ['DEFM14A', 'S-4', 'S-4/A', '425'],
            'acquisition': ['8-K', 'SC 13D', 'SC TO-T'],
            'tender_offer': ['SC TO-C', 'SC TO-I', 'SC TO-T']
        }

        results = {}

        if transaction_type == 'all':
            forms_to_search = sum(ma_forms.values(), [])
        else:
            forms_to_search = ma_forms.get(transaction_type, [])

        for form in set(forms_to_search):
            filing_result = self._get_company_filings({
                'cik': cik,
                'filing_type': form,
                'date_from': date_from,
                'limit': 10
            })

            if 'filings' in filing_result and filing_result['filings']:
                results[form] = filing_result['filings']

        # Look for 8-K items related to M&A
        eight_k_result = self._get_company_filings({
            'cik': cik,
            'filing_type': '8-K',
            'date_from': date_from,
            'limit': 20
        })

        ma_eight_ks = []
        if 'filings' in eight_k_result:
            for filing in eight_k_result['filings']:
                items = filing.get('items', '')
                # Items 1.01, 1.02, 2.01 are M&A related
                if any(item in str(items) for item in ['1.01', '1.02', '2.01']):
                    ma_eight_ks.append(filing)

        return {
            "cik": cik,
            "transaction_type": transaction_type,
            "merger_acquisition_filings": results,
            "relevant_8k_filings": ma_eight_ks[:10],
            "total_filings": sum(len(v) for v in results.values()) + len(ma_eight_ks)
        }

    def _get_comment_letters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get SEC comment letters and company responses"""
        cik = self._resolve_identifier(params)

        if not cik:
            return {"error": "Either CIK or ticker is required"}

        date_from = params.get('date_from', '')
        include_responses = params.get('include_responses', True)

        # Get correspondence filings
        corresp_result = self._get_company_filings({
            'cik': cik,
            'filing_type': 'CORRESP',
            'date_from': date_from,
            'limit': 20
        })

        upload_result = self._get_company_filings({
            'cik': cik,
            'filing_type': 'UPLOAD',
            'date_from': date_from,
            'limit': 20
        })

        comment_letters = {
            "cik": cik,
            "correspondence_filings": corresp_result.get('filings', []) if 'filings' in corresp_result else [],
            "upload_filings": upload_result.get('filings', []) if 'filings' in upload_result else [],
            "total_letters": (len(corresp_result.get('filings', [])) if 'filings' in corresp_result else 0) +
                           (len(upload_result.get('filings', [])) if 'filings' in upload_result else 0)
        }

        if include_responses:
            comment_letters["note"] = "Company responses are typically included in CORRESP filings"

        return comment_letters

    def _get_xbrl_facts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get structured XBRL company facts"""
        cik = self._resolve_identifier(params)

        if not cik:
            return {"error": "Either CIK or ticker is required"}

        concept = params.get('concept', '')
        taxonomy = params.get('taxonomy', 'us-gaap')

        try:
            url = f"{self.data_url}/api/xbrl/companyfacts/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                facts = data.get('facts', {})

                result = {
                    "cik": cik,
                    "entity_name": data.get('entityName', ''),
                    "taxonomies": list(facts.keys())
                }

                # Get specific taxonomy or all
                if taxonomy == 'all':
                    result["facts"] = {}
                    for tax_name, tax_facts in facts.items():
                        result["facts"][tax_name] = {
                            "concept_count": len(tax_facts) if isinstance(tax_facts, dict) else 0,
                            "concepts": list(tax_facts.keys())[:20] if isinstance(tax_facts, dict) else []
                        }
                else:
                    taxonomy_facts = facts.get(taxonomy, {})

                    if concept:
                        # Get specific concept
                        if concept in taxonomy_facts:
                            concept_data = taxonomy_facts[concept]
                            result["concept"] = {
                                "name": concept,
                                "label": concept_data.get('label', ''),
                                "description": concept_data.get('description', ''),
                                "units": list(concept_data.get('units', {}).keys()),
                                "data_points": sum(
                                    len(v) if isinstance(v, list) else 0
                                    for v in concept_data.get('units', {}).values()
                                )
                            }
                        else:
                            result["error"] = f"Concept '{concept}' not found in {taxonomy}"
                    else:
                        # List all concepts in taxonomy
                        result["concepts"] = {}
                        for concept_name in list(taxonomy_facts.keys())[:50]:
                            concept_data = taxonomy_facts[concept_name]
                            result["concepts"][concept_name] = {
                                "label": concept_data.get('label', ''),
                                "units": list(concept_data.get('units', {}).keys())
                            }

                return result
            else:
                return {"error": f"Failed to fetch XBRL facts: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_peer_comparison(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Compare company metrics with industry peers"""
        cik = self._resolve_identifier(params)

        if not cik:
            return {"error": "Either CIK or ticker is required"}

        peer_ciks = params.get('peer_ciks', [])
        use_sic_peers = params.get('use_sic_peers', False)
        metrics = params.get('metrics', ['Assets', 'Revenues', 'NetIncomeLoss', 'EarningsPerShareBasic'])

        # Get primary company info
        company_info = self._get_company_info({'cik': cik})
        if 'error' in company_info:
            return company_info

        # Get peer companies
        if use_sic_peers and not peer_ciks:
            # Would need to search for companies with same SIC code
            sic_code = company_info.get('sic', '')
            peer_ciks = []  # Would populate with SIC peers

        # Get metrics for primary company
        primary_metrics = self._get_xbrl_facts({
            'cik': cik,
            'taxonomy': 'us-gaap'
        })

        comparison_data = {
            "primary_company": {
                "cik": cik,
                "name": company_info.get('name', ''),
                "sic": company_info.get('sic', ''),
                "sic_description": company_info.get('sic_description', '')
            },
            "peers": [],
            "metrics_compared": metrics
        }

        # Get metrics for peer companies
        for peer_cik in peer_ciks[:5]:  # Limit to 5 peers
            peer_data = self._get_xbrl_facts({
                'cik': peer_cik,
                'taxonomy': 'us-gaap'
            })

            if 'error' not in peer_data:
                comparison_data["peers"].append({
                    "cik": peer_cik,
                    "name": peer_data.get('entity_name', ''),
                    "data_available": True
                })

        comparison_data["note"] = "Full metric comparison would require extracting and normalizing XBRL values"

        return comparison_data

    def _get_cik_lookup(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Look up CIK by various identifiers"""
        ticker = params.get('ticker', '')
        company_name = params.get('company_name', '')
        cusip = params.get('cusip', '')
        lei = params.get('lei', '')

        results = []

        # Direct ticker lookup if provided
        if ticker:
            ticker_upper = ticker.upper()

            # Try to get fresh data directly from SEC
            try:
                url = f"{self.data_url}/files/company_tickers.json"
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()

                    # Direct ticker match
                    for key, company in data.items():
                        if company.get('ticker', '') == ticker_upper:
                            results.append({
                                "ticker": ticker_upper,
                                "cik": str(company.get('cik_str', '')).zfill(10),
                                "name": company.get('title', ''),
                                "match_type": "ticker_exact"
                            })
                            break

                    # If no exact match, try partial match
                    if not results:
                        for key, company in data.items():
                            if ticker_upper in company.get('ticker', ''):
                                results.append({
                                    "ticker": company.get('ticker', ''),
                                    "cik": str(company.get('cik_str', '')).zfill(10),
                                    "name": company.get('title', ''),
                                    "match_type": "ticker_partial"
                                })
                                if len(results) >= 5:
                                    break

            except Exception as e:
                # If online lookup fails, try cache
                self._ensure_ticker_cache()
                if ticker_upper in self.ticker_cache:
                    results.append({
                        "ticker": ticker_upper,
                        "cik": self.ticker_cache[ticker_upper]['cik'],
                        "name": self.ticker_cache[ticker_upper]['name'],
                        "match_type": "ticker_exact_cached"
                    })

        # Search by company name (partial match)
        if company_name:
            name_lower = company_name.lower()
            for ticker_symbol, ticker_data in self.ticker_cache.items():
                if name_lower in ticker_data['name'].lower():
                    results.append({
                        "cik": ticker_data['cik'],
                        "ticker": ticker_symbol,
                        "name": ticker_data['name'],
                        "match_type": "name_partial"
                    })
                    if len(results) >= 10:
                        break

        # CUSIP and LEI lookups would require additional data sources
        if cusip:
            results.append({
                "message": "CUSIP lookup requires additional data source integration"
            })

        if lei:
            results.append({
                "message": "LEI lookup requires GLEIF database integration"
            })

        return {
            "search_criteria": {
                "ticker": ticker,
                "company_name": company_name,
                "cusip": cusip,
                "lei": lei
            },
            "results": results[:10],  # Limit to 10 results
            "result_count": len(results)
        }

    def _get_company_tickers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive list of company tickers"""
        exchange = params.get('exchange', '')
        sic_code = params.get('sic_code', '')
        state = params.get('state', '')
        country = params.get('country', '')
        status = params.get('status', 'active')

        try:
            # Get all tickers
            url = f"{self.data_url}/files/company_tickers.json"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()

                # Get additional exchange data if available
                exchange_url = f"{self.data_url}/files/company_tickers_exchange.json"
                exchange_data = {}
                try:
                    exchange_response = requests.get(exchange_url, headers=self.headers)
                    if exchange_response.status_code == 200:
                        exchange_data = exchange_response.json()
                except:
                    pass

                tickers = []
                for key, company in data.items():
                    ticker_info = {
                        "ticker": company.get('ticker', ''),
                        "cik": str(company.get('cik_str', '')).zfill(10),
                        "name": company.get('title', ''),
                        "exchange": exchange_data.get(company.get('ticker', ''), {}).get('exchange', '')
                    }

                    # Apply filters
                    if exchange and exchange.upper() not in ticker_info.get('exchange', '').upper():
                        continue

                    tickers.append(ticker_info)

                    if len(tickers) >= 500:  # Limit response size
                        break

                # Sort by ticker
                tickers.sort(key=lambda x: x['ticker'])

                return {
                    "filters": {
                        "exchange": exchange,
                        "sic_code": sic_code,
                        "state": state,
                        "country": country,
                        "status": status
                    },
                    "tickers": tickers[:200],  # Return first 200
                    "total_count": len(tickers),
                    "truncated": len(tickers) > 200
                }
            else:
                return {"error": f"Failed to fetch tickers: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_historical_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get historical filing data for trend analysis"""
        cik = self._resolve_identifier(params)

        if not cik:
            return {"error": "Either CIK or ticker is required"}

        metric = params.get('metric', '')
        years = params.get('years', 5)
        frequency = params.get('frequency', 'annual')

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)

        try:
            # Get XBRL facts for the metric
            url = f"{self.data_url}/api/xbrl/companyfacts/CIK{cik}.json"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                facts = data.get('facts', {}).get('us-gaap', {})

                historical_data = {
                    "cik": cik,
                    "entity_name": data.get('entityName', ''),
                    "metric": metric,
                    "years_requested": years,
                    "frequency": frequency,
                    "data_points": []
                }

                if metric and metric in facts:
                    metric_data = facts[metric]
                    units = metric_data.get('units', {})

                    all_values = []
                    for unit_type, values in units.items():
                        if isinstance(values, list):
                            for val in values:
                                # Filter by frequency
                                form = val.get('form', '')
                                if frequency == 'annual' and '10-K' not in form:
                                    continue
                                if frequency == 'quarterly' and '10-Q' not in form:
                                    continue

                                # Filter by date range
                                end = val.get('end', '')
                                if end and start_date.isoformat() <= end <= end_date.isoformat():
                                    all_values.append({
                                        'value': val.get('val'),
                                        'unit': unit_type,
                                        'period_end': end,
                                        'period_start': val.get('start', ''),
                                        'form': form,
                                        'filed': val.get('filed', '')
                                    })

                    # Sort by period end date
                    all_values.sort(key=lambda x: x['period_end'])
                    historical_data["data_points"] = all_values

                    # Calculate basic statistics
                    if all_values:
                        values_only = [v['value'] for v in all_values if isinstance(v['value'], (int, float))]
                        if values_only:
                            historical_data["statistics"] = {
                                "min": min(values_only),
                                "max": max(values_only),
                                "average": sum(values_only) / len(values_only),
                                "data_count": len(values_only),
                                "earliest_date": all_values[0]['period_end'],
                                "latest_date": all_values[-1]['period_end']
                            }
                else:
                    historical_data["available_metrics"] = list(facts.keys())[:50]

                return historical_data
            else:
                return {"error": f"Failed to fetch historical data: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _validate_filing(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate EDGAR filing format and compliance"""
        filing_content = params.get('filing_content', '')
        filing_type = params.get('filing_type', '')
        check_xbrl = params.get('check_xbrl', True)

        if not filing_content or not filing_type:
            return {"error": "Both filing content and filing type are required"}

        validation_results = {
            "filing_type": filing_type,
            "content_length": len(filing_content),
            "validations": []
        }

        # Basic validations
        validations = []

        # Check for required headers
        if filing_type in ['10-K', '10-Q', '8-K']:
            required_tags = ['<SEC-DOCUMENT>', '<SEC-HEADER>', '<DOCUMENT>']
            for tag in required_tags:
                if tag in filing_content:
                    validations.append({
                        "check": f"Required tag {tag}",
                        "status": "PASS"
                    })
                else:
                    validations.append({
                        "check": f"Required tag {tag}",
                        "status": "FAIL",
                        "message": f"Missing required tag: {tag}"
                    })

        # Check XBRL structure if requested
        if check_xbrl and '<xbrl' in filing_content.lower():
            try:
                # Basic XML validation
                ET.fromstring(filing_content)
                validations.append({
                    "check": "XML structure",
                    "status": "PASS"
                })
            except ET.ParseError as e:
                validations.append({
                    "check": "XML structure",
                    "status": "FAIL",
                    "message": f"Invalid XML: {str(e)}"
                })

        # Check filing type specific requirements
        filing_requirements = {
            '10-K': ['Item 1', 'Item 7', 'Item 8'],
            '10-Q': ['Item 1', 'Item 2'],
            '8-K': ['Item '],
            'DEF 14A': ['PROXY STATEMENT']
        }

        if filing_type in filing_requirements:
            for requirement in filing_requirements[filing_type]:
                if requirement in filing_content:
                    validations.append({
                        "check": f"Required section: {requirement}",
                        "status": "PASS"
                    })
                else:
                    validations.append({
                        "check": f"Required section: {requirement}",
                        "status": "WARNING",
                        "message": f"Could not find expected section: {requirement}"
                    })

        validation_results["validations"] = validations
        validation_results["overall_status"] = "PASS" if all(
            v["status"] == "PASS" for v in validations
        ) else "FAIL" if any(
            v["status"] == "FAIL" for v in validations
        ) else "WARNING"

        return validation_results