#!/usr/bin/env python3
"""
Wikipedia Research Workflow
============================

This script demonstrates a simple workflow using the Wikipedia MCP Tool.

Workflow Steps:
1. Search for a topic
2. Get summary of the first result
3. Get links from that article
4. Get summaries of related articles

Author: Learning Example
Date: 2025-10-19
"""

import requests
import json
import sys


class WikipediaWorkflow:
    """Simple workflow for Wikipedia research"""
    
    def __init__(self, base_url="http://localhost:5002"):
        """Initialize the workflow with server URL"""
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {}
    
    def login(self, username="admin", password="admin123"):
        """Login to the MCP server"""
        print(f"🔐 Logging in as '{username}'...")
        
        response = self.session.post(
            f"{self.base_url}/login",
            data={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            print("✅ Login successful!\n")
            return True
        else:
            print("❌ Login failed!")
            return False
    
    def call_tool(self, method, arguments):
        """Call a Wikipedia tool method"""
        print(f"🔧 Calling: {method}")
        print(f"   Arguments: {json.dumps(arguments, indent=6)}")
        
        response = self.session.post(
            f"{self.base_url}/api/tool/wikipedia_tool/call",
            json={
                "method": method,
                "arguments": arguments
            }
        )
        
        result = response.json()
        
        if "error" in result:
            print(f"❌ Error: {result['error']}\n")
            return None
        else:
            print(f"✅ Success!\n")
            return result
    
    def step1_search(self, query, limit=5):
        """Step 1: Search for articles on a topic"""
        print("=" * 60)
        print("STEP 1: SEARCH FOR ARTICLES")
        print("=" * 60)
        
        result = self.call_tool("search_articles", {
            "query": query,
            "limit": limit
        })
        
        if result:
            self.results['search'] = result
            print(f"📚 Found {result.get('count', 0)} articles:")
            for i, title in enumerate(result.get('results', []), 1):
                print(f"   {i}. {title}")
            print()
        
        return result
    
    def step2_get_summary(self, title, sentences=3):
        """Step 2: Get summary of an article"""
        print("=" * 60)
        print("STEP 2: GET ARTICLE SUMMARY")
        print("=" * 60)
        
        result = self.call_tool("get_article_summary", {
            "title": title,
            "sentences": sentences
        })
        
        if result:
            self.results['summary'] = result
            print(f"📄 Article: {result.get('title', title)}")
            print(f"🔗 URL: {result.get('url', 'N/A')}")
            print(f"\n📝 Summary:\n{result.get('summary', 'No summary available')}\n")
        
        return result
    
    def step3_get_links(self, title, limit=10):
        """Step 3: Get links from the article"""
        print("=" * 60)
        print("STEP 3: GET ARTICLE LINKS")
        print("=" * 60)
        
        result = self.call_tool("get_article_links", {
            "title": title,
            "limit": limit
        })
        
        if result:
            self.results['links'] = result
            print(f"🔗 Found {result.get('count', 0)} links:")
            for i, link in enumerate(result.get('links', []), 1):
                print(f"   {i}. {link}")
            print()
        
        return result
    
    def step4_explore_related(self, links, max_articles=3):
        """Step 4: Get summaries of related articles"""
        print("=" * 60)
        print("STEP 4: EXPLORE RELATED ARTICLES")
        print("=" * 60)
        
        related_summaries = []
        
        for i, link in enumerate(links[:max_articles], 1):
            print(f"\n📖 Exploring article {i}/{max_articles}: {link}")
            print("-" * 60)
            
            result = self.call_tool("get_article_summary", {
                "title": link,
                "sentences": 2
            })
            
            if result:
                related_summaries.append(result)
                print(f"   Summary: {result.get('summary', 'No summary')[:100]}...")
        
        self.results['related'] = related_summaries
        print()
        return related_summaries
    
    def print_final_report(self):
        """Print a final summary report"""
        print("\n" + "=" * 60)
        print("WORKFLOW COMPLETE - FINAL REPORT")
        print("=" * 60)
        
        print(f"\n✅ Steps Completed:")
        print(f"   - Searched articles: {len(self.results.get('search', {}).get('results', []))} found")
        print(f"   - Main article summary: {self.results.get('summary', {}).get('title', 'N/A')}")
        print(f"   - Article links found: {len(self.results.get('links', {}).get('links', []))}")
        print(f"   - Related articles explored: {len(self.results.get('related', []))}")
        
        print(f"\n📊 Total API calls made: {len(self.results)}")
        print(f"\n🎉 Workflow executed successfully!")
    
    def save_results(self, filename="workflow_results.json"):
        """Save workflow results to a JSON file"""
        filepath = f"/Users/saadahmed/MCP server/sajhamcpserver/workflows/{filename}"
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")


def main():
    """Main workflow execution"""
    print("\n" + "=" * 60)
    print("WIKIPEDIA RESEARCH WORKFLOW")
    print("=" * 60)
    print()
    
    # Initialize workflow
    workflow = WikipediaWorkflow()
    
    # Login
    if not workflow.login():
        print("Cannot continue without login. Exiting.")
        sys.exit(1)
    
    # Get search topic from user or use default
    if len(sys.argv) > 1:
        search_topic = " ".join(sys.argv[1:])
    else:
        search_topic = "Artificial Intelligence"
    
    print(f"🔍 Research Topic: {search_topic}\n")
    
    # Execute workflow steps
    try:
        # Step 1: Search for articles
        search_results = workflow.step1_search(search_topic, limit=5)
        if not search_results or not search_results.get('results'):
            print("No articles found. Exiting.")
            sys.exit(1)
        
        # Get the first article title
        first_article = search_results['results'][0]
        
        # Step 2: Get summary of first article
        summary = workflow.step2_get_summary(first_article, sentences=3)
        if not summary:
            print("Could not get summary. Exiting.")
            sys.exit(1)
        
        # Step 3: Get links from the article
        links = workflow.step3_get_links(first_article, limit=10)
        if not links or not links.get('links'):
            print("No links found. Exiting.")
            sys.exit(1)
        
        # Step 4: Explore related articles
        workflow.step4_explore_related(links['links'], max_articles=3)
        
        # Print final report
        workflow.print_final_report()
        
        # Save results
        workflow.save_results()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during workflow execution: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

