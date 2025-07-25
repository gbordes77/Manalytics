# Manalytics Professional Makefile
# ================================

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PROJECT := manalytics
SRC_DIR := src
TEST_DIR := tests
DOCS_DIR := docs

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

# Phony targets
.PHONY: help install install-dev test lint format clean docker run migrate docs

# Help target
help: ## Show this help message
	@echo "$(BLUE)Manalytics - Professional MTG Analysis Platform$(NC)"
	@echo "=============================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "Quick start: make install && make test"

# Installation
install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e .
	@echo "$(GREEN)✓ Installation complete!$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e ".[dev,test,docs]"
	pre-commit install
	@echo "$(GREEN)✓ Development setup complete!$(NC)"

# Testing
test: ## Run all tests with coverage
	@echo "$(BLUE)Running tests...$(NC)"
	$(PYTHON) -m pytest -v --cov=$(PROJECT) --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Tests complete! Coverage report: htmlcov/index.html$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(PYTHON) -m pytest tests/unit -v -m "unit"

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(PYTHON) -m pytest tests/integration -v -m "integration"

# Code quality
lint: ## Run all linters
	@echo "$(BLUE)Running linters...$(NC)"
	@echo "→ Black (formatter check)..."
	$(PYTHON) -m black --check $(SRC_DIR) $(TEST_DIR)
	@echo "→ isort (import sort check)..."
	$(PYTHON) -m isort --check-only $(SRC_DIR) $(TEST_DIR)
	@echo "→ Flake8 (style guide)..."
	$(PYTHON) -m flake8 $(SRC_DIR) $(TEST_DIR)
	@echo "→ MyPy (type checking)..."
	$(PYTHON) -m mypy $(SRC_DIR)
	@echo "$(GREEN)✓ All linters passed!$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	$(PYTHON) -m black $(SRC_DIR) $(TEST_DIR) scripts/
	$(PYTHON) -m isort $(SRC_DIR) $(TEST_DIR) scripts/
	@echo "$(GREEN)✓ Code formatted!$(NC)"

# Database
migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	$(PYTHON) -m alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete!$(NC)"

# Scrapers
scrape-mtgo: ## Run MTGO scraper (usage: make scrape-mtgo format=standard days=7)
	@echo "$(BLUE)Running MTGO scraper...$(NC)"
	$(PYTHON) -m manalytics.scrapers.mtgo.scraper --format $(format) --days $(days)

scrape-melee: ## Run Melee scraper (usage: make scrape-melee format=standard days=7)
	@echo "$(BLUE)Running Melee scraper...$(NC)"
	$(PYTHON) -m manalytics.scrapers.melee.scraper --format $(format) --days $(days)

scrape-all: ## Run all scrapers
	@echo "$(BLUE)Running all scrapers...$(NC)"
	$(PYTHON) scripts/scrape_all_platforms.py --format standard --days 7

# API
run: ## Run the API server
	@echo "$(BLUE)Starting Manalytics API...$(NC)"
	$(PYTHON) -m uvicorn manalytics.api.app:app --reload --host 0.0.0.0 --port 8000

# Docker
docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Docker build complete!$(NC)"

docker-up: ## Start Docker containers
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started!$(NC)"

docker-down: ## Stop Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped!$(NC)"

# Documentation
docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	cd $(DOCS_DIR) && $(MAKE) clean html
	@echo "$(GREEN)✓ Documentation built! Open docs/_build/html/index.html$(NC)"

# Maintenance
clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	rm -rf build/ dist/ *.egg-info .coverage htmlcov/ .pytest_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "$(GREEN)✓ Cleanup complete!$(NC)"

# Development shortcuts
dev: install-dev ## Full development setup
	@echo "$(GREEN)✓ Development environment ready!$(NC)"

check: lint test ## Run all checks (lint + test)
	@echo "$(GREEN)✓ All checks passed!$(NC)"

# Utilities
shell: ## Open Python shell with project context
	@echo "$(BLUE)Opening Python shell...$(NC)"
	$(PYTHON) -i -c "from manalytics import *; print('Manalytics shell ready!')"

version: ## Show version
	@echo "$(BLUE)Manalytics version:$(NC)"
	@$(PYTHON) -c "import manalytics; print(f'  v{manalytics.__version__}')"