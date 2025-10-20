"""
Web Crawler MCP Tool implementation with comprehensive crawling capabilities
Enhanced with redirect handling
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
    """Comprehensive MCP Tool for web crawling operations with redirect handling"""

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

        # Max redirects to follow
        self.max_redirects = 10

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.max_redirects = self.max_redirects

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
                "trace_redirects": self._trace_redirects,
                "get_redirect_chain": self._get_redirect_chain,
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

    def _fetch_page(self, url: str, follow_redirects: bool = True,
                   max_redirects: Optional[int] = None) -> Tuple[Optional[str], Optional[BeautifulSoup], int, Dict[str, Any]]:
        """
        Fetch a page and return its content, BeautifulSoup object, status code, and redirect info

        Returns:
            Tuple of (html_content, soup, status_code, redirect_info)
        """
        try:
            # Set max redirects if specified
            if max_redirects is not None:
                original_max = self.session.max_redirects
                self.session.max_redirects = max_redirects

            response = self.session.get(
                url,
                timeout=self.request_timeout,
                allow_redirects=follow_redirects
            )

            # Reset max redirects
            if max_redirects is not None:
                self.session.max_redirects = original_max

            status_code = response.status_code

            # Build redirect information
            redirect_info = self._build_redirect_info(response)

            if status_code == 200:
                # Try to detect encoding
                response.encoding = response.apparent_encoding
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                return html_content, soup, status_code, redirect_info
            else:
                return None, None, status_code, redirect_info

        except requests.exceptions.TooManyRedirects as e:
            redirect_info = {
                'was_redirected': True,
                'redirect_count': max_redirects or self.max_redirects,
                'error': 'Too many redirects',
                'redirect_loop': True
            }
            return None, None, 0, redirect_info

        except requests.exceptions.RequestException as e:
            redirect_info = {
                'was_redirected': False,
                'error': str(e)
            }
            return None, None, 0, redirect_info

    def _build_redirect_info(self, response: requests.Response) -> Dict[str, Any]:
        """Build comprehensive redirect information from response"""
        redirect_info = {
            'was_redirected': False,
            'redirect_count': 0,
            'final_url': response.url,
            'redirect_chain': [],
            'redirect_types': [],
            'permanent_redirect': False
        }

        # Check if there were redirects
        if response.history:
            redirect_info['was_redirected'] = True
            redirect_info['redirect_count'] = len(response.history)

            # Build redirect chain
            for i, hist_response in enumerate(response.history):
                redirect_type = self._get_redirect_type(hist_response.status_code)

                redirect_step = {
                    'step': i + 1,
                    'from_url': hist_response.url,
                    'to_url': hist_response.headers.get('Location', ''),
                    'status_code': hist_response.status_code,
                    'redirect_type': redirect_type,
                    'is_permanent': hist_response.status_code in [301, 308]
                }

                redirect_info['redirect_chain'].append(redirect_step)
                redirect_info['redirect_types'].append(redirect_type)

                # Check for permanent redirects
                if hist_response.status_code in [301, 308]:
                    redirect_info['permanent_redirect'] = True

            # Add final destination
            redirect_info['original_url'] = response.history[0].url
            redirect_info['final_url'] = response.url

            # Detect redirect patterns
            redirect_info['redirect_pattern'] = self._detect_redirect_pattern(
                redirect_info['redirect_chain']
            )

        return redirect_info

    def _get_redirect_type(self, status_code: int) -> str:
        """Get human-readable redirect type from status code"""
        redirect_types = {
            301: 'Moved Permanently',
            302: 'Found (Temporary)',
            303: 'See Other',
            307: 'Temporary Redirect',
            308: 'Permanent Redirect'
        }
        return redirect_types.get(status_code, f'Redirect {status_code}')

    def _detect_redirect_pattern(self, redirect_chain: List[Dict[str, Any]]) -> str:
        """Detect common redirect patterns"""
        if not redirect_chain:
            return 'none'

        if len(redirect_chain) == 1:
            return 'simple'

        # Check for redirect loop
        urls = [step['from_url'] for step in redirect_chain]
        if len(urls) != len(set(urls)):
            return 'loop_detected'

        # Check for protocol redirect (http -> https)
        if redirect_chain[0]['from_url'].startswith('http://') and \
           redirect_chain[-1].get('to_url', '').startswith('https://'):
            return 'http_to_https'

        # Check for www redirect
        from_domain = urlparse(redirect_chain[0]['from_url']).netloc
        to_domain = urlparse(redirect_chain[-1].get('to_url', '')).netloc
        if from_domain.replace('www.', '') == to_domain.replace('www.', ''):
            if 'www.' in to_domain and 'www.' not in from_domain:
                return 'add_www'
            elif 'www.' not in to_domain and 'www.' in from_domain:
                return 'remove_www'

        # Multiple redirects
        if len(redirect_chain) > 2:
            return 'chain'

        return 'multiple'

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
        """Crawl a website starting from a URL with redirect handling"""
        start_url = params.get('url', '')
        max_depth = min(params.get('max_depth', 3), 3)  # Cap at 3
        max_pages = min(params.get('max_pages', 50), 100)  # Cap at 100
        same_domain_only = params.get('same_domain_only', True)
        include_external_links = params.get('include_external_links', False)
        extract_metadata = params.get('extract_metadata', True)
        follow_redirects = params.get('follow_redirects', True)
        track_redirects = params.get('track_redirects', True)

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
        redirect_summary: Dict[str, Any] = {
            'total_redirects': 0,
            'permanent_redirects': 0,
            'temporary_redirects': 0,
            'redirect_chains': [],
            'redirect_loops': []
        }

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

            # Fetch page with redirect tracking
            html_content, soup, status_code, redirect_info = self._fetch_page(
                current_url,
                follow_redirects=follow_redirects
            )

            if soup is None:
                page_result = {
                    'url': current_url,
                    'depth': depth,
                    'status': status_code,
                    'error': 'Failed to fetch page'
                }

                # Add redirect info if available
                if track_redirects and redirect_info:
                    page_result['redirect_info'] = redirect_info
                    if redirect_info.get('redirect_loop'):
                        redirect_summary['redirect_loops'].append(current_url)

                results.append(page_result)
                continue

            # Extract text content
            text_content = self._extract_text_from_soup(soup)

            # Use final URL after redirects for link extraction
            final_url = redirect_info.get('final_url', current_url)

            # Prepare page result
            page_result = {
                'url': current_url,
                'final_url': final_url,
                'depth': depth,
                'status': status_code,
                'text_length': len(text_content),
                'text_content': text_content[:5000] if text_content else '',
            }

            # Add redirect information
            if track_redirects and redirect_info['was_redirected']:
                page_result['redirect_info'] = redirect_info
                redirect_summary['total_redirects'] += redirect_info['redirect_count']

                if redirect_info.get('permanent_redirect'):
                    redirect_summary['permanent_redirects'] += 1
                else:
                    redirect_summary['temporary_redirects'] += 1

                # Store significant redirect chains
                if redirect_info['redirect_count'] > 1:
                    redirect_summary['redirect_chains'].append({
                        'original': current_url,
                        'final': final_url,
                        'steps': redirect_info['redirect_count'],
                        'pattern': redirect_info['redirect_pattern']
                    })

            # Extract metadata if requested
            if extract_metadata:
                metadata = self._extract_metadata(soup)
                page_result['metadata'] = metadata

            # Extract links from final page
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = self._get_absolute_url(final_url, href)

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
            'redirect_summary': redirect_summary,
            'pages': results
        }

        if include_external_links:
            final_result['external_links'] = list(external_links)[:100]

        return final_result

    def _crawl_single_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crawl a single page and extract its content with redirect tracking"""
        url = params.get('url', '')
        extract_links = params.get('extract_links', True)
        extract_metadata = params.get('extract_metadata', True)
        follow_redirects = params.get('follow_redirects', True)
        track_redirects = params.get('track_redirects', True)

        if not url:
            return {"error": "URL is required"}

        if not self._is_valid_url(url):
            return {"error": "Invalid URL format"}

        # Fetch page with redirect tracking
        html_content, soup, status_code, redirect_info = self._fetch_page(
            url,
            follow_redirects=follow_redirects
        )

        if soup is None:
            result = {
                'url': url,
                'status': status_code,
                'error': 'Failed to fetch page'
            }
            if track_redirects and redirect_info:
                result['redirect_info'] = redirect_info
            return result

        # Extract text content
        text_content = self._extract_text_from_soup(soup)

        # Get final URL after redirects
        final_url = redirect_info.get('final_url', url)

        result = {
            'url': url,
            'final_url': final_url,
            'status': status_code,
            'text_length': len(text_content),
            'text_content': text_content,
        }

        # Add redirect information
        if track_redirects and redirect_info['was_redirected']:
            result['redirect_info'] = redirect_info

        # Extract metadata
        if extract_metadata:
            metadata = self._extract_metadata(soup)
            result['metadata'] = metadata

        # Extract links using final URL
        if extract_links:
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = self._get_absolute_url(final_url, href)
                if self._is_valid_url(absolute_url):
                    links.append({
                        'url': absolute_url,
                        'text': link.get_text(strip=True),
                        'title': link.get('title', '')
                    })
            result['links'] = links
            result['link_count'] = len(links)

        return result

    # ==================== REDIRECT-SPECIFIC METHODS ====================

    def _trace_redirects(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trace all redirects for a URL without fetching content
        Dedicated tool for redirect analysis
        """
        url = params.get('url', '')
        max_redirects = params.get('max_redirects', self.max_redirects)

        if not url:
            return {"error": "URL is required"}

        if not self._is_valid_url(url):
            return {"error": "Invalid URL format"}

        try:
            # Use HEAD request for faster redirect tracing
            response = self.session.head(
                url,
                timeout=self.request_timeout,
                allow_redirects=True
            )

            redirect_info = self._build_redirect_info(response)

            result = {
                'original_url': url,
                'final_url': response.url,
                'status_code': response.status_code,
                'redirect_info': redirect_info,
                'total_time_ms': int(response.elapsed.total_seconds() * 1000)
            }

            # Add analysis
            if redirect_info['was_redirected']:
                result['analysis'] = {
                    'redirect_count': redirect_info['redirect_count'],
                    'redirect_pattern': redirect_info['redirect_pattern'],
                    'has_permanent_redirect': redirect_info['permanent_redirect'],
                    'redirect_types': redirect_info['redirect_types']
                }

                # Recommendations
                recommendations = []
                if redirect_info['redirect_count'] > 3:
                    recommendations.append('Consider reducing redirect chain length')
                if redirect_info['redirect_pattern'] == 'http_to_https':
                    recommendations.append('Good: HTTPS redirect is in place')
                if redirect_info['redirect_pattern'] == 'loop_detected':
                    recommendations.append('Warning: Redirect loop detected')
                if redirect_info['permanent_redirect']:
                    recommendations.append('Update links to point to final URL')

                result['recommendations'] = recommendations
            else:
                result['analysis'] = {
                    'message': 'No redirects detected'
                }

            return result

        except requests.exceptions.TooManyRedirects:
            return {
                'original_url': url,
                'error': 'Too many redirects (possible redirect loop)',
                'max_redirects': max_redirects
            }
        except Exception as e:
            return {
                'original_url': url,
                'error': str(e)
            }

    def _get_redirect_chain(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed redirect chain information
        Shows each step in the redirect process
        """
        url = params.get('url', '')
        include_headers = params.get('include_headers', False)
        max_redirects = params.get('max_redirects', self.max_redirects)

        if not url:
            return {"error": "URL is required"}

        if not self._is_valid_url(url):
            return {"error": "Invalid URL format"}

        try:
            response = self.session.get(
                url,
                timeout=self.request_timeout,
                allow_redirects=True
            )

            redirect_chain = []

            # Process each redirect in history
            for i, hist_response in enumerate(response.history):
                step = {
                    'step': i + 1,
                    'url': hist_response.url,
                    'status_code': hist_response.status_code,
                    'status_text': hist_response.reason,
                    'redirect_type': self._get_redirect_type(hist_response.status_code),
                    'location': hist_response.headers.get('Location', ''),
                    'is_permanent': hist_response.status_code in [301, 308]
                }

                if include_headers:
                    step['headers'] = dict(hist_response.headers)

                redirect_chain.append(step)

            # Add final destination
            final_step = {
                'step': len(redirect_chain) + 1,
                'url': response.url,
                'status_code': response.status_code,
                'status_text': response.reason,
                'is_final': True
            }

            if include_headers:
                final_step['headers'] = dict(response.headers)

            redirect_chain.append(final_step)

            return {
                'original_url': url,
                'final_url': response.url,
                'total_redirects': len(response.history),
                'redirect_chain': redirect_chain,
                'total_time_ms': int(response.elapsed.total_seconds() * 1000)
            }

        except requests.exceptions.TooManyRedirects:
            return {
                'original_url': url,
                'error': 'Too many redirects',
                'max_redirects_exceeded': True
            }
        except Exception as e:
            return {
                'original_url': url,
                'error': str(e)
            }

    # ==================== LINK EXTRACTION METHODS ====================

    def _extract_all_links(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all links from a page"""
        url = params.get('url', '')
        absolute_urls = params.get('absolute_urls', True)
        filter_domain = params.get('filter_domain')
        follow_redirects = params.get('follow_redirects', True)

        if not url:
            return {"error": "URL is required"}

        # Fetch page
        html_content, soup, status_code, redirect_info = self._fetch_page(
            url,
            follow_redirects=follow_redirects
        )

        if soup is None:
            result = {
                'url': url,
                'status': status_code,
                'error': 'Failed to fetch page'
            }
            if redirect_info:
                result['redirect_info'] = redirect_info
            return result

        # Use final URL after redirects for link resolution
        final_url = redirect_info.get('final_url', url)

        # Extract links
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']

            if absolute_urls:
                link_url = self._get_absolute_url(final_url, href)
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

        result = {
            'url': url,
            'final_url': final_url,
            'status': status_code,
            'total_links': len(unique_links),
            'links': unique_links
        }

        if redirect_info['was_redirected']:
            result['redirect_info'] = redirect_info

        return result

    def _extract_all_document_links(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all document links from a page"""
        url = params.get('url', '')
        document_types = params.get('document_types')
        absolute_urls = params.get('absolute_urls', True)
        follow_redirects = params.get('follow_redirects', True)

        if not url:
            return {"error": "URL is required"}

        # Fetch page
        html_content, soup, status_code, redirect_info = self._fetch_page(
            url,
            follow_redirects=follow_redirects
        )

        if soup is None:
            result = {
                'url': url,
                'status': status_code,
                'error': 'Failed to fetch page'
            }
            if redirect_info:
                result['redirect_info'] = redirect_info
            return result

        # Use final URL for link resolution
        final_url = redirect_info.get('final_url', url)

        # Extract document links
        document_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']

            if absolute_urls:
                link_url = self._get_absolute_url(final_url, href)
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

        result = {
            'url': url,
            'final_url': final_url,
            'status': status_code,
            'total_documents': len(unique_docs),
            'documents': unique_docs,
            'by_type': by_type
        }

        if redirect_info['was_redirected']:
            result['redirect_info'] = redirect_info

        return result

    # ==================== EXTRACTION METHODS ====================

    def _extract_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all images from a page"""
        url = params.get('url', '')
        include_alt_text = params.get('include_alt_text', True)
        follow_redirects = params.get('follow_redirects', True)

        if not url:
            return {"error": "URL is required"}

        # Fetch page
        html_content, soup, status_code, redirect_info = self._fetch_page(
            url,
            follow_redirects=follow_redirects
        )

        if soup is None:
            return {
                'url': url,
                'status': status_code,
                'error': 'Failed to fetch page'
            }

        final_url = redirect_info.get('final_url', url)

        # Extract images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                image_url = self._get_absolute_url(final_url, src)
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
            'final_url': final_url,
            'status': status_code,
            'total_images': len(images),
            'images': images
        }

    def _extract_headings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all headings from a page"""
        url = params.get('url', '')
        include_hierarchy = params.get('include_hierarchy', True)
        follow_redirects = params.get('follow_redirects', True)

        if not url:
            return {"error": "URL is required"}

        # Fetch page
        html_content, soup, status_code, redirect_info = self._fetch_page(
            url,
            follow_redirects=follow_redirects
        )

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
        follow_redirects = params.get('follow_redirects', True)

        if not url:
            return {"error": "URL is required"}

        # Fetch page
        html_content, soup, status_code, redirect_info = self._fetch_page(
            url,
            follow_redirects=follow_redirects
        )

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
                    if row_data:
                        table_data.append(row_data)

            # Format based on output format
            if output_format == 'json':
                if headers:
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
        follow_redirects = params.get('follow_redirects', True)

        if not url:
            return {"error": "URL is required"}

        # Fetch page
        html_content, soup, status_code, redirect_info = self._fetch_page(
            url,
            follow_redirects=follow_redirects
        )

        if soup is None:
            return {
                'url': url,
                'status': status_code,
                'error': 'Failed to fetch page'
            }

        metadata = self._extract_metadata(soup)

        result = {
            'url': url,
            'status': status_code,
            'metadata': metadata
        }

        if redirect_info['was_redirected']:
            result['redirect_info'] = redirect_info

        return result

    # ==================== SEARCH AND UTILITY METHODS ====================

    def _search_text_in_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for text in a page"""
        url = params.get('url', '')
        search_term = params.get('search_term', '')
        case_sensitive = params.get('case_sensitive', False)
        context_chars = params.get('context_chars', 100)
        follow_redirects = params.get('follow_redirects', True)

        if not url:
            return {"error": "URL is required"}

        if not search_term:
            return {"error": "Search term is required"}

        # Fetch page
        html_content, soup, status_code, redirect_info = self._fetch_page(
            url,
            follow_redirects=follow_redirects
        )

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
            'matches': matches[:50]
        }

    def _get_sitemap(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get and parse sitemap.xml"""
        url = params.get('url', '')
        sitemap_url = params.get('sitemap_url')
        follow_redirects = params.get('follow_redirects', True)

        if not url and not sitemap_url:
            return {"error": "URL is required"}

        # Construct sitemap URL
        if not sitemap_url:
            parsed = urlparse(url)
            sitemap_url = f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"

        # Fetch sitemap
        try:
            response = self.session.get(
                sitemap_url,
                timeout=self.request_timeout,
                allow_redirects=follow_redirects
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')

                # Extract URLs from sitemap
                urls = []
                for loc in soup.find_all('loc'):
                    urls.append(loc.get_text(strip=True))

                result = {
                    'sitemap_url': sitemap_url,
                    'final_url': response.url,
                    'status': response.status_code,
                    'total_urls': len(urls),
                    'urls': urls
                }

                # Add redirect info if redirected
                if response.history:
                    redirect_info = self._build_redirect_info(response)
                    result['redirect_info'] = redirect_info

                return result
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
        follow_redirects = params.get('follow_redirects', True)

        if not url:
            return {"error": "URL is required"}

        # Construct robots.txt URL
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        # Fetch robots.txt
        try:
            response = self.session.get(
                robots_url,
                timeout=self.request_timeout,
                allow_redirects=follow_redirects
            )

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

                result = {
                    'robots_url': robots_url,
                    'final_url': response.url,
                    'status': response.status_code,
                    'content': content,
                    'rules': rules
                }

                # Add redirect info if redirected
                if response.history:
                    redirect_info = self._build_redirect_info(response)
                    result['redirect_info'] = redirect_info

                return result
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
        """Check if URL is accessible with enhanced redirect tracking"""
        url = params.get('url', '')
        follow_redirects = params.get('follow_redirects', True)
        max_redirects = params.get('max_redirects', self.max_redirects)

        if not url:
            return {"error": "URL is required"}

        try:
            # Set max redirects
            original_max = self.session.max_redirects
            self.session.max_redirects = max_redirects

            response = self.session.head(
                url,
                timeout=self.request_timeout,
                allow_redirects=follow_redirects
            )

            # Reset max redirects
            self.session.max_redirects = original_max

            result = {
                'url': url,
                'accessible': response.status_code < 400,
                'status_code': response.status_code,
                'status_text': response.reason,
                'headers': dict(response.headers),
                'final_url': response.url if follow_redirects else url
            }

            # Add comprehensive redirect info
            if follow_redirects and response.history:
                redirect_info = self._build_redirect_info(response)
                result['redirect_info'] = redirect_info
                result['was_redirected'] = True
                result['redirect_count'] = redirect_info['redirect_count']
            else:
                result['was_redirected'] = False

            # Add redirect-specific flags
            if response.status_code >= 300 and response.status_code < 400:
                result['is_redirect'] = True
                result['redirect_location'] = response.headers.get('Location', '')
                result['redirect_type'] = self._get_redirect_type(response.status_code)
            else:
                result['is_redirect'] = False

            return result

        except requests.exceptions.TooManyRedirects:
            return {
                'url': url,
                'accessible': False,
                'error': 'Too many redirects (possible redirect loop)',
                'max_redirects_exceeded': True,
                'max_redirects': max_redirects
            }
        except Exception as e:
            return {
                'url': url,
                'accessible': False,
                'error': str(e)
            }