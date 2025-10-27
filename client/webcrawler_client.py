"""
Copyright All rights Reserved 2025-2030, Ashutosh Sinha, Email: ajsinha@gmail.com
Web Crawler Standalone Client

This is a standalone client for interacting with web pages and crawling websites.
It can be used independently of the MCP server for direct web crawling.
"""

import json
import re
import time
import urllib.parse
import urllib.request
import urllib.robotparser
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from html.parser import HTMLParser
from collections import deque


class LinkExtractor(HTMLParser):
    """HTML parser to extract links and metadata"""
    
    def __init__(self):
        super().__init__()
        self.links = []
        self.images = []
        self.title = None
        self.meta_description = None
        self.meta_keywords = None
        self.headings = {'h1': [], 'h2': [], 'h3': []}
        self.current_tag = None
        self.current_data = []
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'a' and 'href' in attrs_dict:
            self.links.append(attrs_dict['href'])
        
        elif tag == 'img' and 'src' in attrs_dict:
            self.images.append({
                'src': attrs_dict['src'],
                'alt': attrs_dict.get('alt', ''),
                'title': attrs_dict.get('title', '')
            })
        
        elif tag == 'meta':
            name = attrs_dict.get('name', '').lower()
            content = attrs_dict.get('content', '')
            
            if name == 'description':
                self.meta_description = content
            elif name == 'keywords':
                self.meta_keywords = content
        
        elif tag in ['h1', 'h2', 'h3']:
            self.current_tag = tag
            self.current_data = []
        
        elif tag == 'title':
            self.current_tag = 'title'
            self.current_data = []
    
    def handle_data(self, data):
        if self.current_tag:
            self.current_data.append(data)
    
    def handle_endtag(self, tag):
        if tag == self.current_tag:
            text = ''.join(self.current_data).strip()
            if text:
                if tag == 'title':
                    self.title = text
                elif tag in self.headings:
                    self.headings[tag].append(text)
            self.current_tag = None
            self.current_data = []


class WebCrawlerClient:
    """
    Standalone client for web crawling and content extraction
    
    This client provides direct access to web crawling capabilities without requiring
    the MCP server infrastructure. Maximum crawl depth is 3 levels.
    """
    
    def __init__(self, user_agent: str = None):
        """
        Initialize Web Crawler client
        
        Args:
            user_agent: Custom user agent string (optional)
        """
        self.max_depth = 3  # Maximum crawl depth
        self.default_timeout = 10
        self.default_delay = 1.0
        self.user_agent = user_agent or 'Mozilla/5.0 (compatible; WebCrawlerClient/1.0)'
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except:
            return False
    
    def _normalize_url(self, url: str, base_url: str) -> Optional[str]:
        """Normalize and resolve relative URLs"""
        try:
            if not url.startswith(('http://', 'https://', '//')):
                url = urllib.parse.urljoin(base_url, url)
            
            parsed = urllib.parse.urlparse(url)
            url = urllib.parse.urlunparse((
                parsed.scheme, parsed.netloc, parsed.path,
                parsed.params, parsed.query, ''
            ))
            
            return url if self._is_valid_url(url) else None
        except:
            return None
    
    def _is_same_domain(self, url1: str, url2: str) -> bool:
        """Check if two URLs are from the same domain"""
        try:
            domain1 = urllib.parse.urlparse(url1).netloc
            domain2 = urllib.parse.urlparse(url2).netloc
            return domain1 == domain2
        except:
            return False
    
    def _fetch_url(self, url: str, timeout: int = None) -> tuple:
        """
        Fetch URL content
        
        Returns:
            Tuple of (content, content_type, status_code)
        """
        if timeout is None:
            timeout = self.default_timeout
        
        try:
            headers = {
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode('utf-8', errors='ignore')
                content_type = response.headers.get('Content-Type', '')
                status_code = response.status
                
                return content, content_type, status_code
                
        except Exception as e:
            raise Exception(f"Failed to fetch URL: {str(e)}")
    
    def check_robots_txt(self, url: str) -> Dict:
        """
        Check robots.txt for the domain
        
        Args:
            url: URL to check
            
        Returns:
            Robots.txt information
            
        Example:
            >>> client = WebCrawlerClient()
            >>> robots = client.check_robots_txt('https://example.com')
            >>> if robots['can_fetch']:
            ...     print("Crawling allowed")
        """
        try:
            parsed = urllib.parse.urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            can_fetch = rp.can_fetch(self.user_agent, url)
            
            return {
                'robots_url': robots_url,
                'can_fetch': can_fetch,
                'user_agent': self.user_agent,
                'url': url,
                'checked_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'robots_url': None,
                'can_fetch': True,
                'error': str(e),
                'url': url,
                'checked_at': datetime.now().isoformat()
            }
    
    def extract_links(self, url: str) -> Dict:
        """
        Extract all links from a URL
        
        Args:
            url: URL to extract links from
            
        Returns:
            Dictionary with extracted links
            
        Example:
            >>> client = WebCrawlerClient()
            >>> links = client.extract_links('https://example.com')
            >>> print(f"Found {links['total_links']} links")
            >>> for link in links['internal_links']:
            ...     print(link)
        """
        content, content_type, status_code = self._fetch_url(url)
        
        parser = LinkExtractor()
        parser.feed(content)
        
        internal_links = []
        external_links = []
        
        for link in parser.links:
            normalized = self._normalize_url(link, url)
            if normalized:
                if self._is_same_domain(url, normalized):
                    internal_links.append(normalized)
                else:
                    external_links.append(normalized)
        
        internal_links = list(set(internal_links))
        external_links = list(set(external_links))
        
        return {
            'url': url,
            'status_code': status_code,
            'internal_links': internal_links,
            'external_links': external_links,
            'internal_count': len(internal_links),
            'external_count': len(external_links),
            'total_links': len(internal_links) + len(external_links),
            'extracted_at': datetime.now().isoformat()
        }
    
    def extract_content(
        self,
        url: str,
        extract_images: bool = True,
        extract_text: bool = True
    ) -> Dict:
        """
        Extract content from a URL
        
        Args:
            url: URL to extract content from
            extract_images: Extract image URLs
            extract_text: Extract text content
            
        Returns:
            Dictionary with extracted content
            
        Example:
            >>> client = WebCrawlerClient()
            >>> content = client.extract_content('https://example.com')
            >>> print(f"Title: {content['title']}")
            >>> print(f"Images: {content['image_count']}")
        """
        content, content_type, status_code = self._fetch_url(url)
        
        parser = LinkExtractor()
        parser.feed(content)
        
        result = {
            'url': url,
            'status_code': status_code,
            'content_type': content_type,
            'title': parser.title,
            'headings': parser.headings,
            'extracted_at': datetime.now().isoformat()
        }
        
        if extract_images:
            normalized_images = []
            for img in parser.images:
                img_copy = img.copy()
                img_copy['src'] = self._normalize_url(img['src'], url)
                normalized_images.append(img_copy)
            
            result['images'] = normalized_images
            result['image_count'] = len(normalized_images)
        
        if extract_text:
            text = re.sub(r'<[^>]+>', '', content)
            text = re.sub(r'\s+', ' ', text).strip()
            
            result['text_content'] = text[:5000]
            result['text_length'] = len(text)
        
        return result
    
    def extract_metadata(self, url: str) -> Dict:
        """
        Extract metadata from a URL
        
        Args:
            url: URL to extract metadata from
            
        Returns:
            Dictionary with page metadata
            
        Example:
            >>> client = WebCrawlerClient()
            >>> metadata = client.extract_metadata('https://example.com')
            >>> print(f"Title: {metadata['title']}")
            >>> print(f"Description: {metadata['meta_description']}")
        """
        content, content_type, status_code = self._fetch_url(url)
        
        parser = LinkExtractor()
        parser.feed(content)
        
        return {
            'url': url,
            'status_code': status_code,
            'content_type': content_type,
            'title': parser.title,
            'meta_description': parser.meta_description,
            'meta_keywords': parser.meta_keywords,
            'headings': parser.headings,
            'content_length': len(content),
            'extracted_at': datetime.now().isoformat()
        }
    
    def get_page_info(self, url: str) -> Dict:
        """
        Get comprehensive page information
        
        Args:
            url: URL to analyze
            
        Returns:
            Dictionary with page information
            
        Example:
            >>> client = WebCrawlerClient()
            >>> info = client.get_page_info('https://example.com')
            >>> print(f"Links: {info['link_count']}")
            >>> print(f"Images: {info['image_count']}")
        """
        content, content_type, status_code = self._fetch_url(url)
        
        parser = LinkExtractor()
        parser.feed(content)
        
        link_count = len(parser.links)
        image_count = len(parser.images)
        
        return {
            'url': url,
            'status_code': status_code,
            'content_type': content_type,
            'title': parser.title,
            'meta_description': parser.meta_description,
            'meta_keywords': parser.meta_keywords,
            'headings': {
                'h1_count': len(parser.headings['h1']),
                'h2_count': len(parser.headings['h2']),
                'h3_count': len(parser.headings['h3']),
                'h1': parser.headings['h1'][:5],
                'h2': parser.headings['h2'][:5],
                'h3': parser.headings['h3'][:5]
            },
            'link_count': link_count,
            'image_count': image_count,
            'content_length': len(content),
            'retrieved_at': datetime.now().isoformat()
        }
    
    def crawl_sitemap(self, url: str) -> Dict:
        """
        Crawl sitemap.xml
        
        Args:
            url: URL of sitemap or base URL
            
        Returns:
            Dictionary with sitemap URLs
            
        Example:
            >>> client = WebCrawlerClient()
            >>> sitemap = client.crawl_sitemap('https://example.com')
            >>> print(f"Found {sitemap['url_count']} URLs")
            >>> for url in sitemap['urls'][:5]:
            ...     print(url)
        """
        try:
            parsed = urllib.parse.urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            sitemap_urls = [
                url if url.endswith('sitemap.xml') else None,
                f"{base_url}/sitemap.xml",
                f"{base_url}/sitemap_index.xml",
                f"{base_url}/sitemap1.xml"
            ]
            
            sitemap_urls = [u for u in sitemap_urls if u]
            
            for sitemap_url in sitemap_urls:
                try:
                    content, content_type, status_code = self._fetch_url(sitemap_url)
                    
                    urls = re.findall(r'<loc>(.*?)</loc>', content)
                    
                    if urls:
                        return {
                            'sitemap_url': sitemap_url,
                            'status_code': status_code,
                            'url_count': len(urls),
                            'urls': urls,
                            'retrieved_at': datetime.now().isoformat()
                        }
                except:
                    continue
            
            return {
                'error': 'No sitemap found',
                'attempted_urls': sitemap_urls,
                'base_url': base_url
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'url': url
            }
    
    def crawl_url(
        self,
        start_url: str,
        max_depth: int = 1,
        max_pages: int = 10,
        follow_external: bool = False,
        respect_robots: bool = True,
        extract_images: bool = True,
        extract_text: bool = True,
        delay: float = 1.0,
        timeout: int = 10
    ) -> Dict:
        """
        Crawl a URL and its links up to max_depth (maximum 3)
        
        Args:
            start_url: URL to start crawling from
            max_depth: Maximum crawl depth (0-3)
            max_pages: Maximum number of pages to crawl
            follow_external: Follow external links
            respect_robots: Respect robots.txt rules
            extract_images: Extract image URLs
            extract_text: Extract text content
            delay: Delay between requests in seconds
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with crawl results
            
        Example:
            >>> client = WebCrawlerClient()
            >>> result = client.crawl_url(
            ...     'https://example.com',
            ...     max_depth=2,
            ...     max_pages=20
            ... )
            >>> print(f"Crawled {result['pages_crawled']} pages")
            >>> for page in result['pages']:
            ...     print(f"{page['url']} (depth {page['depth']})")
        """
        # Enforce maximum depth
        max_depth = min(max_depth, self.max_depth)
        
        # Check robots.txt if required
        if respect_robots:
            robots_check = self.check_robots_txt(start_url)
            if not robots_check['can_fetch']:
                return {
                    'error': 'Crawling not allowed by robots.txt',
                    'robots_check': robots_check,
                    'url': start_url
                }
        
        visited: Set[str] = set()
        to_visit = deque([(start_url, 0)])
        pages = []
        
        start_time = time.time()
        
        while to_visit and len(visited) < max_pages:
            if len(visited) >= max_pages:
                break
            
            current_url, depth = to_visit.popleft()
            
            if current_url in visited:
                continue
            
            if depth > max_depth:
                continue
            
            if not follow_external and not self._is_same_domain(start_url, current_url):
                continue
            
            try:
                if visited:
                    time.sleep(delay)
                
                content, content_type, status_code = self._fetch_url(current_url, timeout)
                
                parser = LinkExtractor()
                parser.feed(content)
                
                page_info = {
                    'url': current_url,
                    'depth': depth,
                    'status_code': status_code,
                    'content_type': content_type,
                    'title': parser.title,
                    'meta_description': parser.meta_description,
                    'link_count': len(parser.links),
                    'crawled_at': datetime.now().isoformat()
                }
                
                if extract_images:
                    page_info['image_count'] = len(parser.images)
                    page_info['images'] = [self._normalize_url(img['src'], current_url) for img in parser.images[:10]]
                
                if extract_text:
                    text = re.sub(r'<[^>]+>', '', content)
                    text = re.sub(r'\s+', ' ', text).strip()
                    page_info['text_preview'] = text[:500]
                
                pages.append(page_info)
                visited.add(current_url)
                
                if depth < max_depth:
                    for link in parser.links:
                        normalized = self._normalize_url(link, current_url)
                        if normalized and normalized not in visited:
                            if follow_external or self._is_same_domain(start_url, normalized):
                                to_visit.append((normalized, depth + 1))
                
            except Exception as e:
                print(f"Warning: Error crawling {current_url}: {e}")
                pages.append({
                    'url': current_url,
                    'depth': depth,
                    'error': str(e),
                    'crawled_at': datetime.now().isoformat()
                })
                visited.add(current_url)
        
        end_time = time.time()
        
        return {
            'start_url': start_url,
            'max_depth': max_depth,
            'max_pages': max_pages,
            'pages_crawled': len(visited),
            'pages': pages,
            'follow_external': follow_external,
            'respect_robots': respect_robots,
            'crawl_duration': round(end_time - start_time, 2),
            'completed_at': datetime.now().isoformat()
        }


def main():
    """
    Main function with sample usage examples
    """
    print("=" * 80)
    print("Web Crawler Client - Sample Usage")
    print("Copyright All rights Reserved 2025-2030, Ashutosh Sinha")
    print("=" * 80)
    print()
    
    # Initialize client
    client = WebCrawlerClient()
    
    # Example URL (using example.com which allows crawling)
    example_url = "http://example.com"
    
    # Example 1: Check Robots.txt
    print("Example 1: Check Robots.txt")
    print("-" * 80)
    try:
        robots = client.check_robots_txt(example_url)
        print(f"URL: {robots['url']}")
        print(f"Can Fetch: {robots['can_fetch']}")
        print(f"Robots URL: {robots.get('robots_url', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Example 2: Extract Links
    print("Example 2: Extract Links")
    print("-" * 80)
    try:
        links = client.extract_links(example_url)
        print(f"URL: {links['url']}")
        print(f"Total Links: {links['total_links']}")
        print(f"Internal Links: {links['internal_count']}")
        print(f"External Links: {links['external_count']}")
        if links['internal_links']:
            print("Sample Internal Links:")
            for link in links['internal_links'][:3]:
                print(f"  - {link}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Example 3: Extract Metadata
    print("Example 3: Extract Metadata")
    print("-" * 80)
    try:
        metadata = client.extract_metadata(example_url)
        print(f"URL: {metadata['url']}")
        print(f"Title: {metadata['title']}")
        print(f"Description: {metadata['meta_description']}")
        print(f"Keywords: {metadata['meta_keywords']}")
        print(f"H1 Headings: {metadata['headings']['h1']}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Example 4: Extract Content
    print("Example 4: Extract Content")
    print("-" * 80)
    try:
        content = client.extract_content(example_url, extract_images=True, extract_text=True)
        print(f"URL: {content['url']}")
        print(f"Title: {content['title']}")
        print(f"Image Count: {content.get('image_count', 0)}")
        print(f"Text Length: {content.get('text_length', 0)} characters")
        if content.get('text_content'):
            print(f"Text Preview: {content['text_content'][:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Example 5: Get Page Info
    print("Example 5: Get Page Info")
    print("-" * 80)
    try:
        info = client.get_page_info(example_url)
        print(f"URL: {info['url']}")
        print(f"Status Code: {info['status_code']}")
        print(f"Title: {info['title']}")
        print(f"Links: {info['link_count']}")
        print(f"Images: {info['image_count']}")
        print(f"H1 Count: {info['headings']['h1_count']}")
        print(f"H2 Count: {info['headings']['h2_count']}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Example 6: Simple Crawl (Depth 1)
    print("Example 6: Simple Crawl (Depth 1)")
    print("-" * 80)
    try:
        result = client.crawl_url(
            start_url=example_url,
            max_depth=1,
            max_pages=5,
            follow_external=False,
            delay=1.0
        )
        print(f"Start URL: {result['start_url']}")
        print(f"Max Depth: {result['max_depth']}")
        print(f"Pages Crawled: {result['pages_crawled']}")
        print(f"Duration: {result['crawl_duration']} seconds")
        print("Pages:")
        for page in result['pages']:
            if 'error' not in page:
                print(f"  - {page['url']} (depth {page['depth']}) - {page.get('title', 'No title')}")
            else:
                print(f"  - {page['url']} (depth {page['depth']}) - Error: {page['error']}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # Example 7: Crawl Sitemap
    print("Example 7: Crawl Sitemap")
    print("-" * 80)
    try:
        sitemap = client.crawl_sitemap(example_url)
        if 'error' in sitemap:
            print(f"Error: {sitemap['error']}")
        else:
            print(f"Sitemap URL: {sitemap['sitemap_url']}")
            print(f"URLs Found: {sitemap['url_count']}")
            if sitemap['urls']:
                print("Sample URLs:")
                for url in sitemap['urls'][:5]:
                    print(f"  - {url}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    print("=" * 80)
    print("Sample execution completed")
    print("=" * 80)
    print()
    print("Note: To test deeper crawls (depth 2-3), use a website with more pages:")
    print("  result = client.crawl_url('https://your-website.com', max_depth=2, max_pages=20)")


if __name__ == '__main__':
    main()
