# MCP Workflows

This folder contains example workflow scripts that demonstrate how to chain multiple MCP tool calls together.

## Available Workflows

### 1. Wikipedia Research Workflow (`wikipedia_workflow.py`)

A simple educational workflow that demonstrates:
- Searching for Wikipedia articles
- Getting article summaries
- Extracting article links
- Exploring related articles

**What it does:**
1. Searches Wikipedia for a topic
2. Gets the summary of the first result
3. Extracts all links from that article
4. Gets summaries of the top 3 related articles
5. Saves all results to a JSON file

## How to Run

### Prerequisites
1. Make sure the MCP server is running:
   ```bash
   cd /Users/saadahmed/MCP\ server/sajhamcpserver
   source venv/bin/activate
   python run_server.py
   ```

2. Server should be accessible at `http://localhost:5002`

### Running the Wikipedia Workflow

**Basic usage (default topic: "Artificial Intelligence"):**
```bash
cd /Users/saadahmed/MCP\ server/sajhamcpserver
source venv/bin/activate
python workflows/wikipedia_workflow.py
```

**Search for a custom topic:**
```bash
python workflows/wikipedia_workflow.py "Machine Learning"
```

```bash
python workflows/wikipedia_workflow.py "Python programming language"
```

```bash
python workflows/wikipedia_workflow.py "Climate Change"
```

### Output

The workflow will:
- Print progress for each step
- Show results in the terminal
- Save complete results to `workflows/workflow_results.json`

### Example Output
```
============================================================
WIKIPEDIA RESEARCH WORKFLOW
============================================================

🔐 Logging in as 'admin'...
✅ Login successful!

🔍 Research Topic: Artificial Intelligence

============================================================
STEP 1: SEARCH FOR ARTICLES
============================================================
🔧 Calling: search_articles
   Arguments: {
      "query": "Artificial Intelligence",
      "limit": 5
   }
✅ Success!

📚 Found 5 articles:
   1. Artificial intelligence
   2. History of artificial intelligence
   3. AI effect
   ...
```

## Creating Your Own Workflows

To create a new workflow:

1. Create a new Python file in this folder
2. Copy the structure from `wikipedia_workflow.py`
3. Modify the steps to use different tools
4. Add your custom logic

### Basic Workflow Template
```python
import requests
import json

class MyWorkflow:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "http://localhost:5002"
        
    def login(self):
        self.session.post(f"{self.base_url}/login", 
                         data={"username": "admin", "password": "admin123"})
    
    def call_tool(self, tool_name, method, arguments):
        response = self.session.post(
            f"{self.base_url}/api/tool/{tool_name}/call",
            json={"method": method, "arguments": arguments}
        )
        return response.json()
    
    def run(self):
        self.login()
        # Add your workflow steps here
        result = self.call_tool("wikipedia_tool", "search_articles", 
                               {"query": "AI", "limit": 5})
        print(result)

if __name__ == "__main__":
    workflow = MyWorkflow()
    workflow.run()
```

## Tips

1. **Always login first** - The API requires authentication
2. **Check for errors** - Each result may contain an `"error"` field
3. **Chain results** - Use output from one call as input to the next
4. **Save results** - Store important data to files for later analysis
5. **Handle exceptions** - Use try/except blocks for robust workflows

## Next Steps

Try modifying the Wikipedia workflow to:
- Search for multiple topics
- Go deeper into the article tree
- Export results to different formats (CSV, Markdown, etc.)
- Combine with other tools (Yahoo Finance, SEC, etc.)

Happy workflow building! 🚀

