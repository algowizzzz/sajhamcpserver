"""
Wikipedia MCP Tool implementation
"""
import wikipedia
from typing import Dict, Any, List
from .base_mcp_tool import BaseMCPTool


class WikipediaMCPTool(BaseMCPTool):
    """MCP Tool for Wikipedia operations"""

    def _initialize(self):
        """Initialize Wikipedia specific components"""
        wikipedia.set_lang('en')  # Default to English

    def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Wikipedia tool calls"""
        try:
            if self.check_rate_limit():
                error_msg = "Rate limit exceeded"
                self.record_call(tool_name, arguments, error=error_msg)
                return {"error": error_msg, "status": 429}

            result = None

            tool_methods = {
                "search_articles": self._search_articles,
                "get_article_summary": self._get_article_summary,
                "get_article_content": self._get_article_content,
                "get_article_sections": self._get_article_sections,
                "get_random_article": self._get_random_article,
                "get_article_links": self._get_article_links,
                "get_article_categories": self._get_article_categories,
                "get_article_images": self._get_article_images
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

    def _search_articles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for Wikipedia articles"""
        query = params.get('query', '')
        limit = params.get('limit', 10)

        if not query:
            return {"error": "Query is required"}

        try:
            results = wikipedia.search(query, results=limit)
            return {
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_article_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get article summary"""
        title = params.get('title', '')
        sentences = params.get('sentences', 5)

        if not title:
            return {"error": "Title is required"}

        try:
            summary = wikipedia.summary(title, sentences=sentences)
            page = wikipedia.page(title)

            return {
                "title": page.title,
                "summary": summary,
                "url": page.url,
                "page_id": page.pageid
            }
        except wikipedia.exceptions.DisambiguationError as e:
            return {
                "error": "Disambiguation page",
                "options": e.options[:10]
            }
        except wikipedia.exceptions.PageError:
            return {"error": f"Page '{title}' not found"}
        except Exception as e:
            return {"error": str(e)}

    def _get_article_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get full article content"""
        title = params.get('title', '')

        if not title:
            return {"error": "Title is required"}

        try:
            page = wikipedia.page(title)
            return {
                "title": page.title,
                "content": page.content[:5000],  # Limit content length
                "url": page.url,
                "page_id": page.pageid,
                "revision_id": page.revision_id
            }
        except wikipedia.exceptions.PageError:
            return {"error": f"Page '{title}' not found"}
        except Exception as e:
            return {"error": str(e)}

    def _get_article_sections(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get article sections"""
        title = params.get('title', '')

        if not title:
            return {"error": "Title is required"}

        try:
            page = wikipedia.page(title)
            sections = page.sections

            return {
                "title": page.title,
                "sections": sections,
                "section_count": len(sections)
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_random_article(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get a random Wikipedia article"""
        try:
            title = wikipedia.random()
            return self._get_article_summary({'title': title, 'sentences': 3})
        except Exception as e:
            return {"error": str(e)}

    def _get_article_links(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get links from an article"""
        title = params.get('title', '')
        limit = params.get('limit', 20)

        if not title:
            return {"error": "Title is required"}

        try:
            page = wikipedia.page(title)
            links = page.links[:limit]

            return {
                "title": page.title,
                "links": links,
                "link_count": len(links)
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_article_categories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get article categories"""
        title = params.get('title', '')

        if not title:
            return {"error": "Title is required"}

        try:
            page = wikipedia.page(title)
            categories = page.categories

            return {
                "title": page.title,
                "categories": categories,
                "category_count": len(categories)
            }
        except Exception as e:
            return {"error": str(e)}

    def _get_article_images(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get images from an article"""
        title = params.get('title', '')
        limit = params.get('limit', 10)

        if not title:
            return {"error": "Title is required"}

        try:
            page = wikipedia.page(title)
            images = page.images[:limit]

            return {
                "title": page.title,
                "images": images,
                "image_count": len(images)
            }
        except Exception as e:
            return {"error": str(e)}