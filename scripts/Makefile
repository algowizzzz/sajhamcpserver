# Makefile for MCP Server
# © 2025-2030 Ashutosh Sinha

.PHONY: help install run test clean docker-build docker-run docker-stop setup dev prod

# Default target
help:
	@echo "MCP Server - Available Commands:"
	@echo "================================"
	@echo "  make install      - Install Python dependencies"
	@echo "  make setup        - Set up the development environment"
	@echo "  make run          - Run the server locally"
	@echo "  make dev          - Run in development mode with auto-reload"
	@echo "  make test         - Run tests"
	@echo "  make clean        - Clean temporary files and caches"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run server in Docker container"
	@echo "  make docker-stop  - Stop Docker containers"
	@echo "  make prod         - Run in production mode with Docker Compose"
	@echo ""

# Install dependencies
install:
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

# Setup development environment
setup: install
	mkdir -p config config/tools data data/office_files logs instance
	@echo "✓ Directories created"

	# Create example configuration files if they don't exist
	@if [ ! -f config/users.json ]; then \
		echo '{"users": [{"id": "admin", "password": "admin123", "full_name": "Administrator", "roles": ["admin", "user"]}]}' > config/users.json; \
		echo "✓ Created default users.json"; \
	fi

	@if [ ! -f config/application.properties ]; then \
		cp config/application.properties.example config/application.properties 2>/dev/null || \
		echo "# MCP Server Configuration\nserver.host=0.0.0.0\nserver.port=5000\nserver.debug=False" > config/application.properties; \
		echo "✓ Created default application.properties"; \
	fi

	@echo "✓ Development environment ready"

# Run the server
run:
	python run_server.py

# Run in development mode
dev:
	FLASK_ENV=development FLASK_DEBUG=1 python run_server.py

# Run tests
test:
	pytest tests/ -v --cov=core --cov=tools --cov=web --cov-report=html

# Clean temporary files
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type f -name '*.log' -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	@echo "✓ Cleaned temporary files"

# Docker commands
docker-build:
	docker build -t mcp-server:latest .
	@echo "✓ Docker image built"

docker-run:
	docker run -d \
		--name mcp-server \
		-p 5000:5000 \
		-v $(PWD)/config:/app/config \
		-v $(PWD)/data:/app/data \
		-v $(PWD)/logs:/app/logs \
		mcp-server:latest
	@echo "✓ Docker container started"
	@echo "Access the server at http://localhost:5000"

docker-stop:
	docker stop mcp-server || true
	docker rm mcp-server || true
	@echo "✓ Docker container stopped"

# Production deployment with Docker Compose
prod:
	docker-compose --profile production up -d
	@echo "✓ Production environment started"
	@echo "Access the server at http://localhost"

# Development with Docker Compose
docker-dev:
	docker-compose up

# Stop all Docker Compose services
docker-down:
	docker-compose --profile production down
	docker-compose --profile cache down
	@echo "✓ All services stopped"

# View logs
logs:
	tail -f logs/mcp_server.log

# Database operations
db-reset:
	rm -f data/*.db data/*.duckdb
	@echo "✓ Databases reset"

# Create distribution package
dist: clean
	python setup.py sdist bdist_wheel
	@echo "✓ Distribution packages created"

# Install in development mode
install-dev:
	pip install -e .
	@echo "✓ Installed in development mode"

# Format code
format:
	black core/ tools/ web/ tests/
	isort core/ tools/ web/ tests/
	@echo "✓ Code formatted"

# Lint code
lint:
	pylint core/ tools/ web/
	flake8 core/ tools/ web/
	@echo "✓ Code linted"

# Security check
security:
	bandit -r core/ tools/ web/
	safety check
	@echo "✓ Security check complete"

# Full check before commit
pre-commit: format lint test security
	@echo "✓ Pre-commit checks passed"

# Generate documentation
docs:
	sphinx-build -b html docs/ docs/_build/html
	@echo "✓ Documentation generated"
	@echo "Open docs/_build/html/index.html to view"

# Show current configuration
show-config:
	@echo "Current Configuration:"
	@echo "====================="
	@cat config/application.properties 2>/dev/null || echo "No configuration file found"
	@echo ""

# Monitor server (requires tmux)
monitor:
	tmux new-session -d -s mcp-monitor 'make logs'
	tmux split-window -h 'watch -n 1 "curl -s http://localhost:5000/api/stats | python -m json.tool"'
	tmux attach -t mcp-monitor

# Backup data
backup:
	mkdir -p backups
	tar -czf backups/backup-$(shell date +%Y%m%d-%H%M%S).tar.gz config/ data/
	@echo "✓ Backup created in backups/"

# Restore from backup
restore:
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Usage: make restore BACKUP_FILE=backups/backup-YYYYMMDD-HHMMSS.tar.gz"; \
	else \
		tar -xzf $(BACKUP_FILE); \
		echo "✓ Restored from $(BACKUP_FILE)"; \
	fi