"""
Web Crawler MCP Tool implementation with comprehensive crawling capabilities
"""
import os
import re
import requests
import csv
import json
from typing import Dict, Any, List, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from collections import deque
from datetime import datetime
from .base_mcp_tool import BaseMCPTool


class WebCrawlerMCPTool(BaseMCPTool):
    """Comprehensive MCP Tool for web crawling operations"""

    def _initialize(self):
        """Initialize Web Crawler specific components"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; MCPWebCrawler/1.0)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }

        # Document file extensions
        self.document_extensions = {
            'pdf': '.pdf',
            'doc': '.doc',
            'docx': '.docx',
            'xls': '.xls',
            'xlsx': '.xlsx',
            'ppt': '.ppt',
            'pptx': '.pptx',
            'txt': '.txt'
        }

        # Timeout for requests
        self.request_timeout = 10

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Web Crawler tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            # Tool method mapping
            tool_methods = {
                "crawl_website": self._crawl_website,
                "crawl_single_page": self._crawl_single_page,
                "extract_all_links": self._extract_all_links,
                "extract_all_document_links": self._extract_all_document_links,
                "extract_images": self._extract_images,
                "extract_headings": self._extract_headings,
                "extract_tables": self._extract_tables,
                "get_page_metadata": self._get_page_metadata,
                "search_text_in_page": self._search_text_in_page,
                "get_sitemap": self._get_sitemap,
                "get_robots_txt": self._get_robots_txt,
                "check_url_accessibility": self._check_url_accessibility,
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

    # ==================== HELPER METHODS ====================

    def _fetch_page(self, url: str) -> Tuple[Optional[str], Optional[BeautifulSoup], int]:
        """Fetch a page and return its content and BeautifulSoup object"""
        try:
            response = self.session.get(url, timeout=self.request_timeout, allow_redirects=True)
            status_code = response.status_code

            if status_code == 200:
                # Try to detect encoding
                response.encoding = response.apparent_encoding
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                return html_content, soup, status_code
            else:
                return None, None, status_code

        except requests.exceptions.RequestException as e:
            return None, None, 0

    def _normalize_url(self, url: str) -> str:
        """Normalize URL by removing fragments and standardizing format"""
        parsed = urlparse(url)
        # Remove fragment
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            ''  # No fragment
        ))
        # Remove trailing slash for consistency (except for root)
        if normalized.endswith('/') and parsed.path != '/':
            normalized = normalized[:-1]
        return normalized

    def _is_same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs are from the same domain"""
        domain1 = urlparse(url1).netloc
        domain2 = urlparse(url2).netloc
        return domain1 == domain2

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid"""
        parsed = urlparse(url)
        return bool(parsed.scheme) and bool(parsed.netloc)

    def _extract_text_from_soup(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from BeautifulSoup object"""
        # Remove script and style elements
        for script in soup(["script", "style", "meta", "noscript"]):
            script.decompose()

        # Get text
        text = soup.get_text(separator='\n')

        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)

        return text

    def _get_absolute_url(self, base_url: str, relative_url: str) -> str:
        """Convert relative URL to absolute URL"""
        return urljoin(base_url, relative_url)

    def _is_document_link(self, url: str, doc_types: Optional[List[str]] = None) -> bool:
        """Check if URL points to a document"""
        url_lower = url.lower()

        if doc_types is None:
            doc_types = list(self.document_extensions.keys())

        for doc_type in doc_types:
            ext = self.document_extensions.get(doc_type, f'.{doc_type}')
            if url_lower.endswith(ext):
                return True

        return False

    # ==================== MAIN CRAWLING METHODS ====================

    def _crawl_website(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crawl a website starting from a URL"""
        start_url = params.get('url', '')
        max_depth = min(params.get('max_depth', 3), 3)  # Cap at 3
        max_pages = min(params.get('max_pages', 50), 100)  # Cap at 100
        same_domain_only = params.get('same_domain_only', True)
        include_external_links = params.get('include_external_links', False)
        extract_metadata = params.get('extract_metadata', True)

        if not start_url:
            return {"error": "URL is required"}

        if not self._is_valid_url(start_url):
            return {"error": "Invalid URL format"}

        # Initialize crawling data structures
        visited: Set[str] = set()
        to_visit: deque = deque([(start_url, 0)])  # (url, depth)
        results: List[Dict[str, Any]] = []
        all_links: Set[str] = set()
        external_links: Set[str] = set()

        start_domain = urlparse(start_url).netloc

        while to_visit and len(visited) < max_pages:
            current_url, depth = to_visit.popleft()

            # Normalize URL
            current_url = self._normalize_url(current_url)

            # Skip if already visited
            if current_url in visited:
                continue

            # Skip if depth exceeded
            if depth > max_depth:
                continue

            visited.add(current_url)

            # Fetch page
            html_content, soup, status_code = self._fetch_page(current_url)

            if soup is None:
                results.append({
                    'url': current_url,
                    'depth': depth,
                    'status': status_code,
                    'error': 'Failed to fetch page'
                })
                continue

            # Extract text content
            text_content = self._extract_text_from_soup(soup)

            # Prepare page result
            page_result = {
                'url': current_url,
                'depth': depth,
                'status': status_code,
                'text_length': len(text_content),
                'text_content': text_content[:5000] if text_content else '',  # Limit text
            }

            # Extract metadata if requested
            if extract_metadata:
                metadata = self._extract_metadata(soup)
                page_result['metadata'] = metadata

            # Extract links
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = self._get_absolute_url(current_url, href)

                # Validate URL
                if not self._is_valid_url(absolute_url):
                    continue

                normalized_link = self._normalize_url(absolute_url)

                # Check if same domain
                is_same_domain = self._is_same_domain(start_url, normalized_link)

                if is_same_domain:
                    all_links.add(normalized_link)
                    links.append(normalized_link)

                    # Add to queue if not visited and within depth
                    if normalized_link not in visited and depth < max_depth:
                        if same_domain_only or not same_domain_only:
                            to_visit.append((normalized_link, depth + 1))
                else:
                    external_links.add(normalized_link)
                    if not same_domain_only:
                        # Only add external links if explicitly allowed
                        if depth < max_depth and normalized_link not in visited:
                            pass  # Don't crawl external by default

            page_result['links_found'] = len(links)
            page_result['internal_links'] = links[:20]  # Limit for response size

            results.append(page_result)

        # Compile final result
        final_result = {
            'start_url': start_url,
            'crawl_date': datetime.now().isoformat(),
            'max_depth': max_depth,
            'pages_crawled': len(visited),
            'total_internal_links': len(all_links),
            'total_external_links': len(external_links),
            'pages': results
        }

        if include_external_links:
            final_result['external_links'] = list(external_links)[:100]  # Limit for response

        return final_result

    def _crawl_single_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crawl a single page and extract its content"""
        url = params.get('url', '')
        extract_links = params.get('extract_links', True)
        extract_metadata = params.get('extract_metadata', True)

        if not url:
            return {"error": "URL is required"}

        if not self._is_valid_url(url):
            return {"error": "Invalid URL format"}

        # Fetch page
        html_content, soup, status_code = self._fetch_page(url)

        if soup is None:
            return {
                'url': url,
                'status': status_code,
                'error': 'Failed to fetch page'
            }

        # Extract text content
        text_content = self._extract_text_from_soup(soup)

        result = {
            'url': url,
            'status': status_code,
            'text_length': len(text_content),
            'text_content': text_content,
        }

        # Extract metadata
        if extract_metadata:
            metadata = self._extract_metadata(soup)
            result['metadata'] = metadata

        # Extract links
        if extract_links:
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = self._get_absolute_url(url, href)
                if self._is_valid_url(absolute_url):
                    links.append({
                        'url': absolute_url,
                        'text': link.get_text(strip=True),
                        'title': link.get('title', '')
                    })
            result['links'] = links
            result['link_count'] = len(links)

        return result

    # ==================== LINK EXTRACTION METHODS ====================

    def _extract_all_links(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all links from a page"""
        url = params.get('url', '')
        absolute_urls = params.get('absolute_urls', True)
        filter_domain = params.get('filter_domain')

        if not url:
            return {"error": "URL is required"}

        # Fetch page
        html_content, soup, status_code = self._fetch_page(url)

        if soup is None:
            return {
                'url': url,
                'status': status_code,
                'error': 'Failed to fetch page'
            }

        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']

            if absolute_urls:
                link_url = self._get_absolute_url(url, href)
            else:
                link_url = href

            # Validate URL
            if absolute_urls and not self._is_valid_url(link_url):
                continue

            # Filter by domain if specified
            if filter_domain:
                if urlparse(link_url).netloc != filter_domain:
                    continue

            links.append({
                'url': link_url,
                'text': link.get_text(strip=True),
                'title': link.get('title', '')
            })

        # Remove duplicates
        unique_links = []
        seen_urls = set()
        for link in links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)

        return {
            'url': url,
            'status': status_code,
            'total_links': len(unique_links),
            'links': unique_links
        }

    def _extract_all_document_links(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all document links from a page"""
        url = params.get('url', '')
        document_types = params.get('document_types')
        absolute_urls = params.get('absolute_urls', True)

        if not url:
            return {"error": "URL is required"}

        # Fetch page
        html_content, soup, status_code = self._fetch_page(url)

        if soup is None:
            return {
                'url': url,
                'status': status_code,
                'error': 'Failed to fetch page'
            }

        # Extract document links
        document_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']

            if absolute_urls:
                link_url = self._get_absolute_url(url, href)
            else:
                link_url = href

            # Check if it's a document
            if self._is_document_link(link_url, document_types):
                # Determine document type
                doc_type = None
                for dtype, ext in self.document_extensions.items():
                    if link_url.lower().endswith(ext):
                        doc_type = dtype
                        break

                document_links.append({
                    'url': link_url,
                    'type': doc_type,
                    'text': link.get_text(strip=True),
                    'title': link.get('title', '')
                })

        # Remove duplicates
        unique_docs = []
        seen_urls = set()
        for doc in document_links:
            if doc['url'] not in seen_urls:
                seen_urls.add(doc['url'])
                unique_docs.append(doc)

        # Group by type
        by_type = {}
        for doc in unique_docs:
            dtype = doc['type']
            if dtype not in by_type:
                by_type[dtype] = []
            by_type[dtype].append(doc)

        return {
            'url': url,
            'status': status_code,
            'total_documents': len(unique_docs),
            'documents': unique_docs,
            'by_type': by_type
        }

    # ==================== EXTRACTION METHODS ====================

    def _extract_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all images from a page"""
        url = params.get('url', '')
        include_alt_text = params.get('include_alt_text', True)

        if not url:
            return {"error": "URL is required"}

        # Fetch page
        html_content, soup, status_code = self._fetch_page(url)

        if soup is None:
            return {
                'url': url,
                'status': status_code,
                'error': 'Failed to fetch page'
            }

        # Extract images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                image_url = self._get_absolute_url(url, src)
                image_data = {
                    'url': image_url,
                    'alt': img.get('alt', '') if include_alt_text else None,
                    'title': img.get('title', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', '')
                }
                images.append(image_data)

        return {
            'url': url,
            'status': status_code,
            'total_images': len(images),
            'images': images
        }

    def _extract_headings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all headings from a page"""
        url = params.get('url', '')
        include_hierarchy = params.get('include_hierarchy', True)

        if not url:
            return {"error": "URL is required"}

        # Fetch page
        html_content, soup, status_code = self._fetch_page(url)

        if soup is None:
            return {
                'url': url,
                'status': status_code,
                'error': 'Failed to fetch page'
            }

        # Extract headings
        headings = []
        for level in range(1, 7):
            tag = f'h{level}'
            for heading in soup.find_all(tag):
                headings.append({
                    'level': level,
                    'text': heading.get_text(strip=True),
                    'id': heading.get('id', '')
                })

        # Organize by hierarchy if requested
        if include_hierarchy:
            hierarchy = {
                'h1': [],
                'h2': [],
                'h3': [],
                'h4': [],
                'h5': [],
                'h6': []
            }
            for heading in headings:
                hierarchy[f"h{heading['level']}"].append(heading['text'])

            return {
                'url': url,
                'status': status_code,
                'total_headings': len(headings),
                'headings': headings,
                'hierarchy': hierarchy
            }

        return {
            'url': url,
            'status': status_code,
            'total_headings': len(headings),
            'headings': headings
        }

    def _extract_tables(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all tables from a page"""
        url = params.get('url', '')
        output_format = params.get('format', 'json')

        if not url:
            return {"error": "URL is required"}

        # Fetch page
        html_content, soup, status_code = self._fetch_page(url)

        if soup is None:
            return {
                'url': url,
                'status': status_code,
                'error': 'Failed to fetch page'
            }

        # Extract tables
        tables = []
        for idx, table in enumerate(soup.find_all('table')):
            table_data = []

            # Get headers
            headers = []
            header_row = table.find('thead')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            elif table.find('tr'):
                first_row = table.find('tr')
                if first_row.find('th'):
                    headers = [th.get_text(strip=True) for th in first_row.find_all('th')]

            # Get rows
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    if row_data:  # Skip empty rows
                        table_data.append(row_data)

            # Format based on output format
            if output_format == 'json':
                if headers:
                    # Convert to list of dicts
                    json_table = []
                    for row in table_data[1:] if not header_row else table_data:
                        if len(row) >= len(headers):
                            json_table.append(dict(zip(headers, row)))
                    tables.append({
                        'table_index': idx,
                        'headers': headers,
                        'data': json_table,
                        'row_count': len(json_table)
                    })
                else:
                    tables.append({
                        'table_index': idx,
                        'data': table_data,
                        'row_count': len(table_data)
                    })
            elif output_format == 'csv':
                # Convert to CSV string
                import io
                output = io.StringIO()
                writer = csv.writer(output)
                if headers:
                    writer.writerow(headers)
                for row in table_data:
                    writer.writerow(row)
                tables.append({
                    'table_index': idx,
                    'csv': output.getvalue()
                })
            else:  # text
                text_output = []
                if headers:
                    text_output.append(' | '.join(headers))
                    text_output.append('-' * 50)
                for row in table_data:
                    text_output.append(' | '.join(row))
                tables.append({
                    'table_index': idx,
                    'text': '\n'.join(text_output)
                })

        return {
            'url': url,
            'status': status_code,
            'total_tables': len(tables),
            'tables': tables
        }

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata from a page"""
        metadata = {}

        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)

        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            content = meta.get('content', '')

            if name and content:
                metadata[name] = content

        return metadata

    def _get_page_metadata(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get page metadata"""
        url = params.get('url', '')

        if not url:
            return {"error": "URL is required"}

        # Fetch page
        html_content, soup, status_code = self._fetch_page(url)

        if soup is None:
            return {
                'url': url,
                'status': status_code,
                'error': 'Failed to fetch page'
            }

        metadata = self._extract_metadata(soup)

        return {
            'url': url,
            'status': status_code,
            'metadata': metadata
        }

    # ==================== SEARCH AND UTILITY METHODS ====================

    def _search_text_in_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for text in a page"""
        url = params.get('url', '')
        search_term = params.get('search_term', '')
        case_sensitive = params.get('case_sensitive', False)
        context_chars = params.get('context_chars', 100)

        if not url:
            return {"error": "URL is required"}

        if not search_term:
            return {"error": "Search term is required"}

        # Fetch page
        html_content, soup, status_code = self._fetch_page(url)

        if soup is None:
            return {
                'url': url,
                'status': status_code,
                'error': 'Failed to fetch page'
            }

        # Extract text
        text_content = self._extract_text_from_soup(soup)

        # Search
        matches = []
        search_flags = 0 if case_sensitive else re.IGNORECASE

        for match in re.finditer(re.escape(search_term), text_content, search_flags):
            start = max(0, match.start() - context_chars)
            end = min(len(text_content), match.end() + context_chars)
            context = text_content[start:end]

            matches.append({
                'position': match.start(),
                'context': context,
                'match': match.group()
            })

        return {
            'url': url,
            'status': status_code,
            'search_term': search_term,
            'total_matches': len(matches),
            'matches': matches[:50]  # Limit results
        }

    def _get_sitemap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get and parse sitemap.xml"""
        url = params.get('url', '')
        sitemap_url = params.get('sitemap_url')

        if not url and not sitemap_url:
            return {"error": "URL is required"}

        # Construct sitemap URL
        if not sitemap_url:
            parsed = urlparse(url)
            sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"

        # Fetch sitemap
        try:
            response = self.session.get(sitemap_url, timeout=self.request_timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')

                # Extract URLs from sitemap
                urls = []
                for loc in soup.find_all('loc'):
                    urls.append(loc.get_text(strip=True))

                return {
                    'sitemap_url': sitemap_url,
                    'status': response.status_code,
                    'total_urls': len(urls),
                    'urls': urls
                }
            else:
                return {
                    'sitemap_url': sitemap_url,
                    'status': response.status_code,
                    'error': 'Sitemap not found'
                }
        except Exception as e:
            return {
                'sitemap_url': sitemap_url,
                'error': str(e)
            }

    def _get_robots_txt(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get and parse robots.txt"""
        url = params.get('url', '')

        if not url:
            return {"error": "URL is required"}

        # Construct robots.txt URL
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        # Fetch robots.txt
        try:
            response = self.session.get(robots_url, timeout=self.request_timeout)
            if response.status_code == 200:
                content = response.text

                # Parse rules
                lines = content.split('\n')
                rules = {
                    'user_agents': [],
                    'disallowed': [],
                    'allowed': [],
                    'sitemaps': [],
                    'crawl_delay': None
                }

                current_agent = None
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    if line.lower().startswith('user-agent:'):
                        current_agent = line.split(':', 1)[1].strip()
                        rules['user_agents'].append(current_agent)
                    elif line.lower().startswith('disallow:'):
                        path = line.split(':', 1)[1].strip()
                        rules['disallowed'].append(path)
                    elif line.lower().startswith('allow:'):
                        path = line.split(':', 1)[1].strip()
                        rules['allowed'].append(path)
                    elif line.lower().startswith('sitemap:'):
                        sitemap = line.split(':', 1)[1].strip()
                        rules['sitemaps'].append(sitemap)
                    elif line.lower().startswith('crawl-delay:'):
                        delay = line.split(':', 1)[1].strip()
                        rules['crawl_delay'] = delay

                return {
                    'robots_url': robots_url,
                    'status': response.status_code,
                    'content': content,
                    'rules': rules
                }
            else:
                return {
                    'robots_url': robots_url,
                    'status': response.status_code,
                    'error': 'robots.txt not found'
                }
        except Exception as e:
            return {
                'robots_url': robots_url,
                'error': str(e)
            }

    def _check_url_accessibility(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check if URL is accessible"""
        url = params.get('url', '')
        follow_redirects = params.get('follow_redirects', True)

        if not url:
            return {"error": "URL is required"}

        try:
            response = self.session.head(
                url,
                timeout=self.request_timeout,
                allow_redirects=follow_redirects
            )

            result = {
                'url': url,
                'accessible': response.status_code < 400,
                'status_code': response.status_code,
                'status_text': response.reason,
                'headers': dict(response.headers),
                'final_url': response.url if follow_redirects else url
            }

            if response.status_code >= 300 and response.status_code < 400:
                result['redirect'] = True
                result['redirect_url'] = response.headers.get('Location', '')

            return result

        except Exception as e:
            return {
                'url': url,
                'accessible': False,
                'error': str(e)
            }