"""
Setup script for MCP Server
© 2025-2030 Ashutosh Sinha
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sajhamcpserver",
    version="1.0.0",
    author="Ashutosh Sinha",
    author_email="ashutosh.sinha@example.com",
    description="A comprehensive MCP (Model Context Protocol) server with multiple data source integrations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sajhamcpserver",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mcp-server=run_server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.properties", "*.html", "*.css", "*.js"],
        "config": ["*.json", "*.properties", "tools/*.json"],
        "web": ["templates/*.html", "static/*"],
    },
    zip_safe=False,
    keywords="mcp server api tools integration",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/sajhamcpserver/issues",
        "Source": "https://github.com/yourusername/sajhamcpserver",
    },
)